# Implementation-shortfall memo — Alpaca PAPER mirror, 2026-07-07 and 2026-08-03 batches

**Written 2026-08-11 ~23:15 CDT. PRD deliverable M6.3.**
**Recommendation: change nothing. `HALF_SPREAD_BPS` stays at 5.0.**

---

## The one sentence this memo exists to say

> **`HALF_SPREAD_BPS` IS NOT TO BE RECALIBRATED OFF SHORTFALL. Drift is not spread.**

M6.3's original task text says to write a memo "if measured slippage differs
materially from the 5 bps assumption." Measured shortfall differs from 5 bps by
roughly **20x**. That reads like a mandate to recalibrate, and following it would
be the single most damaging change anyone could make to this project: every
backtest, every held-out validation and every sleeve comparison prices its
transaction costs off `HALF_SPREAD_BPS`. Moving it 5 → ~100 would restate all of
them at once, on evidence that does not support the change.

The evidence does not support it because **these numbers are not a spread
measurement.** They are the gap between when the sim prices a trade and when the
mirror actually trades. Section 4 shows that with three independent measurements
rather than an argument.

---

## 1. What was measured, and what it is called now

**M6 was redefined on 2026-08-11 (Evan's decision) from execution slippage to
implementation shortfall**, because execution slippage is not measurable with the
current architecture — the mirror never fills at the price the sim books at.

    shortfall_bps = (mirror fill price / sim booked price - 1) x 10,000
                    sign flipped for sells, so positive = the mirror did WORSE

- **Sim booked price** = `paper_positions.entry_price` (buys) / `exit_price`
  (sells). Persisted at fill time, never rewritten.
- **Mirror fill price** = Alpaca's `filled_avg_price`, from
  `var/alpaca_fills_2026-07-01_2026-08-06.csv` (M6.1, record CS).
- **166 of 231 fills paired.** The 65 unpaired have no sim leg by construction:
  `alpaca_sync` reconciles each account to target *weights*, so it trims and tops
  up names the sim merely holds at a different quantity. They are reported as
  unpaired, not dropped.

**PAPER-venue fills. Indicative, not proof of real-money execution.**

---

## 2. The numbers, per batch, unrounded

Never pooled across batches — the two batches differ in fill mechanics, not in
execution quality.

| rebalance | sleeve | side | n | mean | median | p95 | min | max |
|---|---|---|---:|---:|---:|---:|---:|---:|
| 2026-07-07 | mom_roa_6535_0701_paper | buy | 50 | +156.0060 | +122.9452 | +381.8753 | −125.7624 | +1470.9289 |
| 2026-07-07 | residual_roa_6535_0701_paper | buy | 48 | +41.9696 | +39.0369 | +324.7726 | −228.0287 | +337.5104 |
| 2026-08-03 | mom_roa_6535_0701_paper | buy | 19 | +396.2302 | +463.1425 | +942.4410 | −830.9591 | +954.2990 |
| 2026-08-03 | mom_roa_6535_0701_paper | sell | 19 | −156.8307 | −285.8599 | +990.9768 | −1364.9059 | +1344.3888 |
| 2026-08-03 | residual_roa_6535_0701_paper | buy | 15 | +183.3875 | +162.0426 | +484.7587 | −74.0111 | +561.7445 |
| 2026-08-03 | residual_roa_6535_0701_paper | sell | 15 | −43.9853 | +23.0228 | +270.6131 | −945.9971 | +316.9342 |

Whole-batch:

| batch | n | mean | median | p95 | min | max | sd | fills where the mirror did BETTER |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2026-07-07 | 98 | +100.1514 | +83.5756 | +331.4848 | −228.0287 | +1470.9289 | 192.1 | 20 / 98 |
| 2026-08-03 | 68 | +97.6415 | +148.1563 | +942.4410 | −1364.9059 | +1344.3888 | 498.7 | 26 / 68 |

All figures in bps. **`spy_benchmark_0701_paper` contributes nothing to this
memo**: both of its mirror fills are unpaired. Its 08-04 sell has no sim leg (the
sim never sells a buy-and-hold benchmark — a pure mirror weight trim), and its
07-07 buy is a **date mismatch**: the sim's SPY entry is dated **2026-07-06**, the
cohort inception, while the mirror bought on 07-07. It is reported as unpaired
rather than paired across a date boundary, because loose date matching is exactly
the legacy path's defect (record CT.1).

That distinction was found while writing this memo and the tracker was corrected
for it: the unpaired bucket previously gave one canned "mirror weight adjustment"
reason to all 65 fills, which was true for 64 and false for this one. It changes
no number — the fill was unpaired either way — but a report that explains a
finding wrongly is worse than one that says less.

---

## 3. Why the two batches are not comparable to each other

| batch | sim reference | mirror actually filled | the gap is |
|---|---|---|---|
| 2026-07-07 | the 07-07 **close** | **14:20 ET, mid-session** | ~1h40m of intraday drift |
| 2026-08-03 | the 08-03 **close** | **09:30–09:36 ET on 08-04**, the next session's open | an overnight gap |

The August orders were POSTed at `2026-08-03T23:24:48Z` = **19:24 ET** (measured
from `alpaca_request_ids.log`, record CS.3) — after the close, so Alpaca held them
to the next open. Market-on-close is not an escape: Alpaca rejects MOC orders
between 15:50 and 19:00 ET and queues them to the *following* close after 19:00
ET, so the 18:03-local monthly slot cannot reach the same day's closing auction at
all. Reaching it means changing when the sim prices relative to when the mirror
submits — a live-behaviour change, and Evan's call.

---

## 4. Three measurements showing this is drift, not spread

A half-spread assumption models the cost of crossing the bid-ask at the moment of
trading. If the ~+100 bps were spread, all three of the following would look
different than they do.

**(a) The dispersion is far too large.** Cross-sectional sd is **192.1 bps**
(July) and **498.7 bps** (August) around means near +100. A half-spread is
near-constant per name and would show sd of a few bps, not hundreds. The per-name
extremes are single-stock moves, which is what drift produces and what a spread
cannot: AFJK +1470.9 bps (sim 26.1531 → mirror 30.0000), STRL sell +1344.4 bps
(sim 611.1642 → mirror 529.0000), MRAM sell −1364.9 bps (sim 15.4423 → mirror
17.5500).

**(b) The sign is not one-way.** A spread cost is one-signed by construction — you
always pay it. **20 of 98** July fills and **26 of 68** August fills came out
BETTER than the sim's price. Roughly 28% of fills having negative cost is
incompatible with a spread and entirely ordinary for drift.

**(c) Per-name shortfall tracks each name's own price move.** For the 68 paired
August fills, the correlation between a name's shortfall and that same name's
overnight close-to-close move (2026-08-03 → 2026-08-04, sign-matched to side) is
**+0.7668**. A bid-ask spread does not know which direction a stock moved; a
timing gap does, by definition. This is the decisive one.

Two honest limits on (c): the fill was at the **open** and the comparison uses the
next **close**, so the residual (mean +148.2 bps) is the open→close move, not a
spread estimate — it is not evidence of anything and is not claimed as such. And
this decomposition is only possible for August: the July reference closes were
overwritten in `price_cache` and are unrecoverable (record CU.2), so July's
shortfall is valid as a shortfall but cannot be decomposed at all.

---

## 5. What a real `HALF_SPREAD_BPS` recalibration would require

A batch where **the sim's reference price and the mirror's fill are
contemporaneous**. No such batch exists in the 231 fills (record CU.3: July has
good timing but its reference data is gone; August has intact reference data but
next-open fills). Producing one requires one of the live-behaviour changes in §3,
which are outside this PRD's scope guard and are Evan's decision.

Until such a batch exists, the honest statement about spread is: **unmeasured.**
Not "5 bps confirmed," not "100 bps." The 5.0 currently in the code is the
project's standing assumption, and this memo provides no evidence for or against
it — which is precisely why it should not be touched.

Two things now make a future measurement possible that were not possible before:

- **Fill provenance** (record CV, live 2026-08-05): `paper_positions` now stores
  `entry_ref_close`/`entry_ref_date`/`exit_ref_close`/`exit_ref_date`, so a
  rebalance stays measurable after `price_cache` moves under it. Only fills
  written **after 2026-08-05** have this; the two batches in this memo are NULL
  and always will be.
- **The redefinition itself.** Shortfall is now a named, per-batch, never-pooled
  metric with its own rows in `slippage_log`, so a future session reading those
  rows finds a metric that says what it is instead of a number labelled
  "slippage."

---

## 6. Recommendation

1. **`HALF_SPREAD_BPS` = 5.0, unchanged.** Do not recalibrate off shortfall.
2. Keep reporting shortfall **per batch, never pooled**, and keep the composition
   note attached to each batch.
3. If Evan wants a genuine execution-quality number, the blocking decision is the
   mirror's timing (MOC order type, an in-session monthly slot, or accepting that
   shortfall is the metric this design can produce). Nothing else is blocking.

---

## 7. Provenance

- Pairing + reporting: `scripts/momentum/slippage_tracker.py --alpaca-csv`
  (read-only by default; `--execute` appends to `slippage_log`).
- Fills: `var/alpaca_fills_2026-07-01_2026-08-06.csv` (M6.1, record CS).
- Tests: `scripts/momentum/test_shortfall_pairing.py` — sign convention,
  buy→`entry_price` / sell→`exit_price` pairing, unpaired-with-reason, and
  write idempotency. All pass.
- Frozen regression tests after this work: **4/4, d=±0.0000pp** — v1 +14.5547%/70
  & +1.8792%/156, v2 +14.4062%/38 & +10.2194%/87.
- Prior context in the record: CS (fetch), CT (pairing + the stop), CU (basis
  pinned, July data gone), CV (forward provenance fix).
