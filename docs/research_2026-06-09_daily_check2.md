# Daily Trade Check (2nd run) — 2026-06-09

Automated `daily-trade-check-2` run. The primary research for today was already
written in [research_2026-06-09_optical_dispersion.md](research_2026-06-09_optical_dispersion.md).
This second run confirms the FN invalidation execution, documents the
`residual_roa_6535_paper` launch, and adds incremental observations not covered
in the first run.

---

## Confirmed: FN invalidation executed

The first-run report predicted "tonight's automated run will exit FN from the
treatment sleeve." It did:

```
llm_overlay_mom_roa_top1_paper  FN  exit=2026-06-09  pnl=-19.3%  reason=invalidation
```

FN closed at **$586.00** today — $14 below the $600 stop set on the 6/03 BUY
entry. The control sleeve (`mom_roa_top1_paper`) still holds FN open at
138.7 shares × $586 ≈ -$19.2% unrealized.

**Current experiment standings (11d since 5/29 inception):**
| Sleeve | NAV | Since Inception |
|---|---|---|
| `mom_roa_top1_paper` (control) | $81,382 | **−18.6%** (holds FN open) |
| `llm_overlay_mom_roa_top1_paper` (treatment) | $80,766 | **−19.2%** (in cash) |

The treatment is 0.6% behind the control after the stop exit — a coin-flip
difference at this point. The critical question is whether FN bounces (the
"CPO-delay denial bounce" scenario the 6/09 optical-dispersion report flagged)
or continues falling. That outcome will determine whether the stop helped or
hurt the treatment. Watch the spread over the next 2–4 weeks.

---

## New: `residual_roa_6535_paper` launched today

The 5th systematic paper sleeve went live on **2026-06-09** with 50 positions
at $99,950.07 inception NAV. Key observations from the initial position list:

**Portfolio character:**
- Heavy **Financial Services** micro-caps: FGMC, FNRN, DMAA, SSSS, EMYB,
  FMBM, CMTV, EZPW, SEZL (~8 names). Community banks + specialty finance
  with strong idiosyncratic momentum but near-zero sector/market correlation
  — exactly what residual momentum selects for.
- **Energy** overweight: APA, DINO, INSW, PARR, PBR, NRT, TEN (~7 names).
  Energy had strong idiosyncratic upward moves decoupled from the tech
  selloff narrative.
- **Large-cap defensives**: JNJ, PM, CAT, GLW, CBOE — none of which appear
  in mom_v1/v2/roa_6535. This is the ROA filter working as intended: profitable
  incumbents with steady residual momentum score highly.
- **Zero optical-transceiver exposure**: AAOI, COHR, FN, MXL, CIEN are ALL
  absent. The idiosyncratic signal stripped out the factor that hurt the other
  sleeves on 6/05 and 6/09.

**Potential issue — GOOG/GOOGL double-count:**
The portfolio holds BOTH `GOOG` (5.5 shares, $362.47 entry) AND `GOOGL`
(5.5 shares, $364.44 entry), representing ~2% exposure each to the SAME
company (Alphabet Inc). Total Alphabet weight is ~4% of book. This isn't
portfolio-breaking, but the universe filter should de-duplicate dual-class
shares. Flag for next maintenance session: add a `GOOG→GOOGL` canonical
ticker map in `universe.py`, keeping the more liquid share class (GOOGL) and
dropping the other. *No action taken this run — sleeve is live, surgical fix
should wait for next rebalance cycle.*

---

## Portfolio scorecard (all sleeves, corrected returns)

Benchmarks since 2026-05-01 (39 trading days):
- **SPY**: $720.65 → $737.05 = **+2.28%**
- **QQQ**: $674.15 → $707.83 = **+5.00%**

| Sleeve | Days | Return | vs SPY | vs QQQ |
|---|---|---|---|---|
| `mom_roa_6535_paper` | 39 | **+2.71%** | +0.43pp | −2.29pp |
| `sector_top4_paper` | 39 | **+2.40%** | +0.12pp | −2.60pp |
| `mom_v1_paper` | 39 | **−2.00%** | −4.28pp | −7.00pp |
| `mom_v2_paper` | 39 | **−3.65%** | −5.93pp | −8.65pp |
| `residual_roa_6535_paper` | 0 | $0.00 (inception today) | — | — |
| `llm_overlay_sector_top4_paper` | 4 | $0.00 (unseeded) | — | — |

The chip crash on 6/05 (−5.5% single day) and the CPO-optics selloff today
have turned the 39-day race negative for the pure-momentum books. The ROA
filter and sector diversification in `mom_roa_6535` are the only systematic
sleeves beating SPY.

---

## Entry-timing dissection: May 1 vs June 3 entries within `mom_roa_6535`

The most important pattern in today's data — not covered in the optical report —
is how dramatically **entry vintage matters** within the SAME strategy:

**May 1 entries (39d holding):**
| Name | P&L |
|---|---|
| MU (Micron) | **+72.5%** |
| DOCN (DigitalOcean) | **+63.6%** |
| LRCX (Lam Research) | +27.4% |
| STX (Seagate) | +16.3% |
| TTMI, TER, VICR, POWL | +5–9% |
| VSAT, FIX, ARWR, BELFB | −1 to −3% |
| SATS, BE, AAOI | −5 to −11% |
| PRAX | **−22.8%** |

**June 3 entries (6d holding):**
| Name | P&L |
|---|---|
| GOLF, MCK, VCEL, IDT, GWW | +4–7% |
| AAPL, ATEN, BLD, CALX, FTI, GOOGL, RBC | ±2% |
| FORM, INTC, LRN, MTZ, NEGG, SE | −2 to −6% |
| FN, FLEX, OSIS | −9 to −19% |
| RMBS | **−14.0%** |
| WDC | **−12.9%** |
| MXL | **−20.6%** |
| CIEN | **−29.2%** |

**Pattern:** The June 3 rebalance entered names that were already deep
mid-parabola by the time of rebalance. CIEN went from $569 on 6/01 → $627
on 6/02 → $620 on 6/03 (entry) → $535 on 6/04 (−14% the NEXT DAY, before
the 6/05 macro shock). This is consistent with the 6/08 report's
"momentum rotated into an already-extended theme" observation, and with the
**extension-filter idea** (reject entries trading >X% above 20-day MA).

**The CIEN case in particular**: CIEN peaked at $627 on 6/02, the strategy
bought the day after at $620.68, and then it crashed −13.7% on 6/04 alone.
This is almost certainly a post-earnings-catalyst entry — the prior spike
was the earnings gap, and the rebalance caught it the day the pop faded.
A simple rule: *"do not enter a position in the 5 days after a >10%
single-session gap"* would have excluded CIEN on 6/03.

---

## Strategy ideas (incremental — not in the 6/09 optical report)

**1. Post-spike entry blackout (easy to implement, addresses CIEN/WDC/MXL/FN).**
At rebalance time, exclude any name that gapped >10% up in the prior 5
trading days. This is a lightweight extension filter focused on the extreme
case (parabolic tops from earnings, not generic overbought). Backtest
on both windows; hypothesis is it saves the CIEN/FN category of losses while
not cutting much of the MU/DOCN/STX type of winner (those names did NOT have
a recent gap-up — their momentum was smooth over many months).

**2. GOOG/GOOGL canonical deduplication in `universe.py`.**
Low-effort code fix. Drop GOOG, keep GOOGL as canonical for Alphabet. Also
check for other dual-class pairs (FOXA/FOX, BRK.A/BRK.B, etc.) that could
similarly double-count in factor rankings.

**3. Seed `llm_overlay_sector_top4_paper`.**
This has been flagged in every recent report. The sleeve is in cash with 0
decisions at 4 days old. Rate-hike bets, tech derating, and the SOX crash
are exactly the regime this macro overlay is meant to handle. Seeding it now
gives forward test data during a live stress period.

---

## What this run did NOT do

- No trades, rebalances, or stop executions. All automated via scheduled tasks.
- Did not implement any of the strategy ideas above — they require backtesting.
- Did not update `record_*` / `state_*` docs. The CLAUDE.md cadence reminder
  applies; these may be 1–2 prompts overdue for a catch-up in the next
  interactive session.

---

*Run by: `daily-trade-check-2` scheduled task, 2026-06-09.*
