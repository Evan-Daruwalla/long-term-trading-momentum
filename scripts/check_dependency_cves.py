"""Dependency CVE check against OSV.dev. Stdlib only - no new dependency.

WHY NOT pip-audit: it is a convenience wrapper over the same public advisory
data. The one genuinely hard part - deciding whether an installed version falls
inside an advisory's affected range under PEP 440 - is done SERVER-SIDE by OSV's
querybatch endpoint, which takes a concrete version and returns only the
advisories affecting it. So there is nothing left to reimplement, and installing
a scanner would enlarge the very dependency surface being measured.

WHAT THIS DOES NOT TELL YOU. A hit means "a version you have is named in a
published advisory" - NOT "you are exploitable". OSV cannot know whether the
vulnerable code path is reachable from this project, and most advisories sit in
code a given project never calls. Triage by hand; the ones worth caring about
here are the packages that parse UNTRUSTED REMOTE DATA (yfinance -> curl_cffi /
requests / urllib3 / pandas, and beautifulsoup4 / lxml on scraped pages).
It also does NOT detect malicious or typosquatted packages - a different and
arguably more realistic supply-chain threat that version matching cannot see.

NETWORK: sends {name, version} pairs to https://api.osv.dev (Google-operated).
Public package names only, but it is machine inventory leaving the box.

Exit codes: 0 = no advisories, 1 = advisories found, 2 = COULD NOT DETERMINE.
An unreachable API is never reported as clean.

Usage:
    python -m scripts.check_dependency_cves
    python -m scripts.check_dependency_cves --requirements requirements.txt --json out.json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

from trading_bot.config import PROJECT_ROOT

OSV_BATCH = "https://api.osv.dev/v1/querybatch"
OSV_VULN = "https://api.osv.dev/v1/vulns/"
TIMEOUT = 30

# Packages whose job is parsing data fetched from the internet. A hit in one of
# these is reachable from untrusted input; a hit elsewhere probably is not.
UNTRUSTED_INPUT_PATH = {
    "yfinance", "curl-cffi", "requests", "urllib3", "httpx", "certifi",
    "beautifulsoup4", "lxml", "pandas", "numpy", "soupsieve", "html5lib",
}

# CANARIES: (name, version) pairs with long-standing published advisories,
# submitted alongside the real query. If a canary comes back CLEAN the pipeline
# is broken - wrong ecosystem string, name normalization off, API contract
# changed - and a "no advisories" result on the real packages would be a
# FALSE NEGATIVE. This is what turns an assumed negative into a verified one.
CANARIES = [("urllib3", "1.26.4"), ("requests", "2.19.1")]


def normalize(name: str) -> str:
    """PEP 503 normalization. OSV's PyPI ecosystem keys on the normalized name.

    Load-bearing: `pip freeze` emits `curl_cffi`, PyPI calls it `curl-cffi`, and
    querying the un-normalized form returns an empty result that is
    INDISTINGUISHABLE from 'no advisories'.
    """
    return re.sub(r"[-_.]+", "-", name).lower()


def parse_requirements(path: Path) -> list[tuple[str, str]]:
    out = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "==" not in line:
            continue
        name, _, ver = line.partition("==")
        ver = ver.split(";")[0].split()[0].strip()
        out.append((normalize(name.strip()), ver))
    return out


def osv_querybatch(pkgs: list[tuple[str, str]]) -> list[list[dict]]:
    body = json.dumps({"queries": [
        {"package": {"name": n, "ecosystem": "PyPI"}, "version": v}
        for n, v in pkgs]}).encode()
    req = urllib.request.Request(OSV_BATCH, data=body,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        data = json.loads(r.read())
    results = data.get("results", [])
    if len(results) != len(pkgs):
        raise RuntimeError(f"OSV returned {len(results)} results for {len(pkgs)} "
                           f"queries - positional alignment broken, refusing to map")
    return [res.get("vulns", []) or [] for res in results]


def vuln_detail(vid: str) -> dict:
    try:
        with urllib.request.urlopen(OSV_VULN + vid, timeout=TIMEOUT) as r:
            return json.loads(r.read())
    except Exception:
        return {}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--requirements", default=None,
                    help="Default: requirements.lock.txt, else requirements.txt")
    ap.add_argument("--json", default=None, help="Also write full findings here.")
    args = ap.parse_args()

    if args.requirements:
        req = Path(args.requirements)
    else:
        req = PROJECT_ROOT / "requirements.lock.txt"
        if not req.exists():
            req = PROJECT_ROOT / "requirements.txt"
    if not req.exists():
        print(f"COULD NOT DETERMINE: no requirements file at {req}")
        return 2

    pkgs = parse_requirements(req)
    if not pkgs:
        print(f"COULD NOT DETERMINE: no pinned (name==version) lines in {req.name}")
        return 2
    print(f"Source: {req.name} ({len(pkgs)} pinned package(s))")
    print(f"Service: {OSV_BATCH}  [sends name+version only]")

    query = pkgs + CANARIES
    try:
        vulns = osv_querybatch(query)
    except (urllib.error.URLError, TimeoutError, RuntimeError, ValueError) as e:
        # NEVER "clean" on failure. This is the whole point of the exit-2 state.
        print(f"\nCOULD NOT DETERMINE: OSV query failed ({type(e).__name__}: {e}).")
        print("Dependency vulnerability status is UNKNOWN, not clean.")
        return 2

    n = len(pkgs)
    pkg_hits, canary_hits = vulns[:n], vulns[n:]

    # Verify the pipeline BEFORE trusting any negative.
    dead = [f"{c[0]}=={c[1]}" for c, v in zip(CANARIES, canary_hits) if not v]
    if dead:
        print(f"\nCOULD NOT DETERMINE: canary package(s) {', '.join(dead)} returned "
              f"NO advisories, but they have known ones.")
        print("The query pipeline is broken (name normalization, ecosystem string, "
              "or API contract). A 'no advisories' result would be a FALSE NEGATIVE.")
        return 2
    print(f"Canaries OK: {', '.join(f'{c[0]}=={c[1]}' for c in CANARIES)} both "
          f"returned advisories, so a negative below is trustworthy.")

    findings = []
    for (name, ver), vs in zip(pkgs, pkg_hits):
        if not vs:
            continue
        ids = [v["id"] for v in vs]
        details = [vuln_detail(i) for i in ids]
        findings.append({
            "package": name, "version": ver, "ids": ids,
            "aliases": sorted({a for d in details for a in d.get("aliases", [])}),
            "summaries": [d.get("summary", "") for d in details],
            "untrusted_input_path": name in UNTRUSTED_INPUT_PATH,
        })

    print()
    if not findings:
        print(f"NO ADVISORIES: none of the {n} pinned packages match a published "
              f"OSV advisory at their pinned version.")
        print("This is version matching only - it does NOT mean the code is safe, "
              "and it cannot see malicious/typosquatted packages.")
        if args.json:
            Path(args.json).write_text(json.dumps([], indent=2), encoding="utf-8")
        return 0

    hot = [f for f in findings if f["untrusted_input_path"]]
    print(f"ADVISORIES FOUND: {len(findings)} package(s), "
          f"{len(hot)} on the untrusted-input path.")
    for f in sorted(findings, key=lambda x: (not x["untrusted_input_path"], x["package"])):
        flag = "  <-- PARSES UNTRUSTED REMOTE DATA" if f["untrusted_input_path"] else ""
        print(f"\n  {f['package']}=={f['version']}{flag}")
        for i, vid in enumerate(f["ids"]):
            alias = [a for a in f["aliases"] if a.startswith("CVE-")]
            summ = (f["summaries"][i] or "").strip().splitlines()
            print(f"     {vid}{'  (' + ', '.join(alias) + ')' if alias else ''}"
                  f"{'  ' + summ[0] if summ else ''}")
    print("\nA hit is a TRIAGE item, not proof of exploitability - OSV cannot know "
          "whether the vulnerable path is reachable here.")
    print("Do NOT bulk-upgrade: a yfinance/pandas bump can change price-adjustment "
          "behaviour and silently move every backtest number.")
    if args.json:
        Path(args.json).write_text(json.dumps(findings, indent=2), encoding="utf-8")
        print(f"Full findings -> {args.json}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
