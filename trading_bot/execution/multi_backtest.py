"""Sequential multi-profile backtest.

Runs the same date range three times with conservative / normal / aggressive
profiles. Each run wipes positions before starting, so to keep comparison
data we archive the full position set to a JSON file per profile.

Two archive layouts are written each invocation:
  1. Top-level `{profile}.json` — overwritten each run, used by legacy code
     and the terminal dashboard for "latest run" lookups.
  2. `runs/{run_id}/{profile}.json` — versioned snapshot tagged with a UTC
     timestamp run_id. The web dashboard reads this directory to show
     historical runs side-by-side and auto-update as new runs land.

Each `runs/{run_id}` folder also gets a `meta.json` capturing the profile
config, date range, and total wall-clock time so the dashboard can label
runs with their settings without reverse-engineering them from positions.
"""
from __future__ import annotations

import json
import logging
import time
from dataclasses import asdict, dataclass, fields
from datetime import date, datetime, timezone
from pathlib import Path

from trading_bot import profiles
from trading_bot.config import VAR_DIR
from trading_bot.db import connect
from trading_bot.execution import backtest as bt_mod


log = logging.getLogger(__name__)

ARCHIVE_DIR = VAR_DIR / "sim_archive"
RUNS_DIR = ARCHIVE_DIR / "runs"


def _profile_to_dict(p) -> dict:
    """Serialize a RiskProfile dataclass to a plain dict for meta.json."""
    return {f.name: getattr(p, f.name) for f in fields(p)}


@dataclass
class ProfileSimResult:
    profile_name: str
    since: str
    until: str
    starting_cash: float
    ending_cash: float
    open_positions_value: float
    closed_count: int
    open_count: int
    realized_pnl: float
    total_pnl: float
    total_pnl_pct: float
    closed_positions: list[dict]
    open_positions: list[dict]


def run_all(
    *, since: date, until: date, starting_cash: float = 100_000.0,
    label: str | None = None, resume_run_id: str | None = None,
) -> list[ProfileSimResult]:
    """Run all three profiles sequentially; return the result for each.

    *label* is an optional human-readable name (e.g. "R9-50DMA-tuned") stored
    in meta.json and displayed in the web dashboard run selector.  If omitted
    the run is shown by its timestamp run_id.

    *resume_run_id* picks up an existing run by run_id. Profiles whose JSON
    is already on disk get skipped (re-loaded from JSON for the final
    summary); profiles that didn't finish run from scratch. Useful when the
    process crashes mid-run — re-launching with --resume preserves
    completed profiles instead of redoing 2+ hours of Conservative.
    """
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    RUNS_DIR.mkdir(parents=True, exist_ok=True)

    if resume_run_id:
        run_id = resume_run_id
        run_dir = RUNS_DIR / run_id
        if not run_dir.exists():
            run_dir.mkdir(exist_ok=True)
            log.info("--resume %s: directory didn't exist, starting fresh", run_id)
        else:
            log.info("--resume %s: existing dir found, will skip completed profiles", run_id)
    else:
        run_id = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        run_dir = RUNS_DIR / run_id
        run_dir.mkdir(exist_ok=True)
    started_at = time.time()

    results: list[ProfileSimResult] = []
    profile_meta: dict[str, dict] = {}

    total_profiles = len(profiles.ALL_PROFILES)
    for idx, profile in enumerate(profiles.ALL_PROFILES, start=1):
        # Resume: if this profile's JSON already exists, load it and skip.
        existing_path = run_dir / f"{profile.name}.json"
        if resume_run_id and existing_path.exists():
            log.info("=== Profile %d/%d: %s SKIPPED (resume — already on disk) ===",
                     idx, total_profiles, profile.name)
            with existing_path.open() as f:
                existing = json.load(f)
            # Reconstruct ProfileSimResult from JSON for the summary
            results.append(ProfileSimResult(
                profile_name=existing["profile_name"],
                since=existing["since"],
                until=existing["until"],
                starting_cash=existing["starting_cash"],
                ending_cash=existing["ending_cash"],
                open_positions_value=existing["open_positions_value"],
                closed_count=existing["closed_count"],
                open_count=existing["open_count"],
                realized_pnl=existing["realized_pnl"],
                total_pnl=existing["total_pnl"],
                total_pnl_pct=existing["total_pnl_pct"],
                closed_positions=existing["closed_positions"],
                open_positions=existing["open_positions"],
            ))
            profile_meta[profile.name] = _profile_to_dict(profile)
            continue

        log.info("=== Profile %d/%d: %s (run_id=%s) ===",
                 idx, total_profiles, profile.name, run_id)
        with profiles.use_profile(profile):
            r = bt_mod.run_backtest(since=since, until=until, starting_cash=starting_cash)

        # Snapshot DB state before the next iteration's wipe.
        with connect() as conn:
            closed = [dict(row) for row in conn.execute(
                "SELECT * FROM positions WHERE status='closed' "
                "ORDER BY realized_pnl DESC"
            )]
            opens = [dict(row) for row in conn.execute(
                "SELECT * FROM positions WHERE status='open' "
                "ORDER BY entry_value DESC"
            )]

        result = ProfileSimResult(
            profile_name=profile.name,
            since=r.since.isoformat(),
            until=r.until.isoformat(),
            starting_cash=r.starting_cash,
            ending_cash=r.ending_cash,
            open_positions_value=r.open_positions_value,
            closed_count=r.closed_count,
            open_count=r.open_count,
            realized_pnl=r.realized_pnl,
            total_pnl=r.total_pnl,
            total_pnl_pct=r.total_pnl_pct,
            closed_positions=closed,
            open_positions=opens,
        )
        results.append(result)
        profile_meta[profile.name] = _profile_to_dict(profile)

        # Latest-run snapshot (back-compat for load_archives + terminal dash).
        latest_path = ARCHIVE_DIR / f"{profile.name}.json"
        with latest_path.open("w") as f:
            json.dump(asdict(result), f, indent=2, default=str)

        # Versioned snapshot — what the web dashboard reads.
        versioned_path = run_dir / f"{profile.name}.json"
        with versioned_path.open("w") as f:
            json.dump(asdict(result), f, indent=2, default=str)
        log.info("Archived %s -> %s (latest + run %s)", profile.name, latest_path, run_id)

    # meta.json captures profile config + run info so the dashboard can
    # show "this run was conservative thr=8 TP=30" without re-deriving.
    meta = {
        "run_id": run_id,
        "label": label or run_id,  # human-readable name; falls back to timestamp
        "started_at": datetime.fromtimestamp(started_at, timezone.utc).isoformat(),
        "elapsed_seconds": round(time.time() - started_at, 2),
        "since": since.isoformat(),
        "until": until.isoformat(),
        "starting_cash": starting_cash,
        "profiles": profile_meta,
        "summary": {
            r.profile_name: {
                "total_pnl_pct": r.total_pnl_pct,
                "closed_count": r.closed_count,
                "open_count": r.open_count,
            }
            for r in results
        },
    }
    with (run_dir / "meta.json").open("w") as f:
        json.dump(meta, f, indent=2, default=str)
    log.info("Run %s archived. P&L: %s",
             run_id,
             ", ".join(f"{r.profile_name}={r.total_pnl_pct:+.2f}%" for r in results))

    return results


def list_runs() -> list[dict]:
    """Return all archived runs newest-first, each with its meta.json."""
    if not RUNS_DIR.exists():
        return []
    out = []
    for d in sorted(RUNS_DIR.iterdir(), reverse=True):
        if not d.is_dir():
            continue
        meta_path = d / "meta.json"
        if not meta_path.exists():
            continue
        with meta_path.open() as f:
            meta = json.load(f)
        meta["_dir"] = str(d)
        out.append(meta)
    return out


def load_run(run_id: str) -> dict | None:
    """Load a specific run by run_id. Returns dict with `meta` and per-profile `results`."""
    run_dir = RUNS_DIR / run_id
    meta_path = run_dir / "meta.json"
    if not meta_path.exists():
        return None
    with meta_path.open() as f:
        meta = json.load(f)
    results: dict[str, dict] = {}
    for profile_name in ["conservative", "normal", "aggressive"]:
        p = run_dir / f"{profile_name}.json"
        if p.exists():
            with p.open() as f:
                results[profile_name] = json.load(f)
    return {"meta": meta, "results": results}


def load_archives() -> list[ProfileSimResult]:
    """Load previously-archived multi-backtest results, if any."""
    if not ARCHIVE_DIR.exists():
        return []
    out = []
    for profile in profiles.ALL_PROFILES:
        path = ARCHIVE_DIR / f"{profile.name}.json"
        if not path.exists():
            continue
        with path.open() as f:
            data = json.load(f)
        out.append(ProfileSimResult(**data))
    return out
