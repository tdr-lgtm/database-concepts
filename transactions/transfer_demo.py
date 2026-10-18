import sqlite3

def make_db():
    conn = sqlite3.connect(":memory:", isolation_level=None)   # autocommit: each statement saves at once
    conn.execute("CREATE TABLE accounts (name TEXT PRIMARY KEY, balance INTEGER)")
    conn.execute("INSERT INTO accounts VALUES ('A', 1000), ('B', 0)")
    return conn


def balances(conn):
    return dict(conn.execute("SELECT name, balance FROM accounts"))

def transfer_without_transaction(conn, amount):
    conn.execute("UPDATE accounts SET balance = balance - ? WHERE name = 'A'", (amount,))
    raise RuntimeError("server crashed") # crash halfway
    conn.execute("UPDATE accounts SET balance = balance + ? WHERE name = 'B'", (amount,))

def transfer_with_transaction(conn, amount):
    conn.execute("BEGIN")                                       # start: nothing is saved yet
    try:
        conn.execute("UPDATE accounts SET balance = balance - ? WHERE name = 'A'", (amount,))
        raise RuntimeError("server crashed") # crash halfway
        conn.execute("UPDATE accounts SET balance = balance + ? WHERE name = 'B'", (amount,))
        conn.execute("COMMIT") # save both changes together
    except RuntimeError:
        conn.execute("ROLLBACK") # undo everything since BEGIN
        raise

for fn in (transfer_without_transaction, transfer_with_transaction):
    conn = make_db()
    print(f"\n=== {fn.__name__} ===")
    print("  before:", balances(conn), " total:", sum(balances(conn).values()))
    try:
        fn(conn, 500)
    except RuntimeError as e:
        print("  error: ", e)
    print("  after: ", balances(conn), " total:", sum(balances(conn).values()))

"""
=== transfer_without_transaction ===
  before: {'A': 1000, 'B': 0}  total: 1000
  error:  server crashed
  after:  {'A': 500, 'B': 0}  total: 500

=== transfer_with_transaction ===
  before: {'A': 1000, 'B': 0}  total: 1000
  error:  server crashed
  after:  {'A': 1000, 'B': 0}  total: 1000
"""