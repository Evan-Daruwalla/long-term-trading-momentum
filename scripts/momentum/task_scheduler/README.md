# Windows Task Scheduler setup for paper-trade automation

Two XML files here that import as scheduled tasks. They run `daily.bat`
and `rebalance.bat` on the right cadence.

## Daily task — `MomentumPaperDaily.xml`
Runs `daily.bat` every weekday at 16:30 local time (post US market close).

## Monthly task — `MomentumPaperRebalance.xml`
Runs `rebalance.bat` on the 1st day of each month at 16:30 local time.
The .bat itself is idempotent — re-running on the same day is a no-op.
If the 1st is a weekend, the task will run but daily.bat will skip the
empty-trading-day refresh and rebalance will use the most recent close.

## How to install

1. Open **Task Scheduler** (Win+R → `taskschd.msc`)
2. Right-click "Task Scheduler Library" → **Import Task...**
3. Browse to one of the XML files in this directory
4. Confirm settings — you may need to:
   - Enter your Windows password (task runs under your user)
   - Adjust the trigger time if 16:30 doesn't suit you
   - Adjust the working directory if Trading is elsewhere
5. Repeat for the other XML
6. Right-click each task → **Run** to test once

## How to verify it's running

After a few days, check:
- `var/data_audit/fetch_earnings_dates.out` updated (if you re-warm earnings)
- `paper_nav` table has new rows for each strategy each weekday
- Logs go to stdout (Task Scheduler captures these in history)

## To pause / disable

Right-click the task → **Disable**. To re-enable, **Enable**.

## To uninstall

Right-click → **Delete**.
