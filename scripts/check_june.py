import sqlite3
conn = sqlite3.connect('var/trades.db')
c = conn.cursor()

# When was each strategy last rebalanced?
c.execute("SELECT strategy_name, last_rebalanced_at FROM paper_portfolio ORDER BY strategy_name")
print("=== last_rebalanced_at per strategy ===")
for r in c.fetchall(): print(r)

# Latest nav date per strategy
c.execute("SELECT strategy_name, MAX(nav_date) FROM paper_nav GROUP BY strategy_name ORDER BY strategy_name")
print("\n=== latest nav_date per strategy ===")
for r in c.fetchall(): print(r)

conn.close()
