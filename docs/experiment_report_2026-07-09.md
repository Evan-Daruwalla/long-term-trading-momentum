# LLM-overlay experiment report - 2026-07-09
Read-only; forward returns are unrealized/interim.

## stock overlay  (log: llm_overlay_log)
sleeves: control=mom_roa_top1_paper | cash-veto=llm_overlay_mom_roa_top1_paper | cascade=llm_cascade_top1_paper
kill-switch: decisions=8/30  rebalance-dates=5  months=1.3/12  (first 2026-05-29, latest 2026-07-07)  approve=3 veto=5
  score-vs-forward-return (UNREALIZED/INTERIM: decision close -> latest close):
    date       ticker score verdict  fwd_ret     entry->latest
    2026-05-29 BE         5 VETO       -9.8%    285.00->257.02
    2026-06-03 FN         6 BUY       -33.4%    725.00->482.78
    2026-06-12 AAOI       4 VETO      -27.7%    169.05->122.21
    2026-07-01 BE         4 VETO      -11.2%    289.50->257.02
    2026-07-01 SLGL       3 VETO       +6.1%      71.99->76.36
    2026-07-01 WDC        7 BUY        -3.4%    598.37->578.05
    2026-07-07 BE         4 VETO       -4.7%    269.57->257.02
    2026-07-07 WDC        6 BUY        +8.6%    532.10->578.05
  mean forward return: approve(BUY)=-9.4% (n=3)  veto=-9.5% (n=5)
  [reading: a working stock BUY signal wants approve>veto; a working veto wants veto names to UNDERperform. n is tiny - noise, not proof.]

## sector overlay  (log: sector_overlay_log)
sleeves: control=sector_top4_paper | cash-veto=llm_overlay_sector_top4_paper | cascade=llm_cascade_sector4_paper
kill-switch: decisions=15/30  rebalance-dates=3  months=0.9/12  (first 2026-06-12, latest 2026-07-07)  approve=11 veto=4
  score-vs-forward-return (UNREALIZED/INTERIM: decision close -> latest close):
    date       ticker score verdict  fwd_ret     entry->latest
    2026-06-12 XLB        5 HOLD       -3.7%      52.18->50.26
    2026-06-12 XLE        3 VETO       -4.7%      57.55->54.82
    2026-06-12 XLI        8 HOLD       +2.8%    176.18->181.11
    2026-06-12 XLK        7 HOLD       +0.3%    184.80->185.35
    2026-07-01 XLB        5 HOLD       -1.5%      51.02->50.26
    2026-07-01 XLE        3 VETO       +3.8%      52.81->54.82
    2026-07-01 XLI        7 HOLD       -1.2%    183.36->181.11
    2026-07-01 XLK        7 HOLD       -0.1%    185.62->185.35
    2026-07-01 XLV        6 HOLD       +1.6%    159.54->162.17
    2026-07-01 XLY        4 VETO       -1.1%    118.09->116.85
    2026-07-07 XLB        5 HOLD       -2.4%      51.51->50.26
    2026-07-07 XLE        3 VETO       +0.3%      54.64->54.82
    2026-07-07 XLI        8 HOLD       -0.7%    182.38->181.11
    2026-07-07 XLK        6 HOLD       +3.4%    179.18->185.35
    2026-07-07 XLV        7 HOLD       -1.4%    164.44->162.17
  mean forward return: approve(HOLD)=-0.3% (n=11)  veto=-0.4% (n=4)
  [reading: a working stock BUY signal wants approve>veto; a working veto wants veto names to UNDERperform. n is tiny - noise, not proof.]

