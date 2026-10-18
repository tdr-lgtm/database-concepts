import os
import sqlite3

DB = "shop.db"

def setup():
    if os.path.exists(DB):
        os.remove(DB)
    conn = sqlite3.connect(DB)
    conn.execute("CREATE TABLE products (id INTEGER PRIMARY KEY, name TEXT, stock INTEGER)")
    conn.execute("CREATE TABLE orders (buyer TEXT)")
    conn.execute("INSERT INTO products VALUES (1, 'Phone', 1)") # only 1 left
    conn.commit()
    conn.close()

def user():
    # each user gets their own connection, like two different people
    return sqlite3.connect(DB, isolation_level=None, timeout=0)

def result(conn):
    stock = conn.execute("SELECT stock FROM products WHERE id = 1").fetchone()[0]
    buyers = [r[0] for r in conn.execute("SELECT buyer FROM orders")]
    print(f"  stock left: {stock}   orders: {buyers}")

# 1. RACE: read, check, then write
print("=== 1. Read, check, write (race condition) ===")
setup()
amit, neha = user(), user()

amit_stock = amit.execute("SELECT stock FROM products WHERE id = 1").fetchone()[0]
neha_stock = neha.execute("SELECT stock FROM products WHERE id = 1").fetchone()[0]
print(f"  Amit sees stock {amit_stock}, Neha sees stock {neha_stock}")   # both see 1

if amit_stock > 0:
    amit.execute("UPDATE products SET stock = ? WHERE id = 1", (amit_stock - 1,))
    amit.execute("INSERT INTO orders VALUES ('Amit')")
if neha_stock > 0:
    neha.execute("UPDATE products SET stock = ? WHERE id = 1", (neha_stock - 1,))
    neha.execute("INSERT INTO orders VALUES ('Neha')")
result(amit)
amit.close() # Windows can't delete an open file
neha.close()

# 2. FIX: check and write in ONE statement
print("\n=== 2. Fix: one atomic UPDATE ===")
setup()
amit, neha = user(), user()

for name, conn in (("Amit", amit), ("Neha", neha)):
    cur = conn.execute("UPDATE products SET stock = stock - 1 WHERE id = 1 AND stock > 0")
    if cur.rowcount == 1: # 1 row changed = we got the item
        conn.execute("INSERT INTO orders VALUES (?)", (name,))
        print(f"  {name}: bought it")
    else: # 0 rows changed = someone was faster
        print(f"  {name}: sold out")
result(amit)
amit.close()
neha.close()

# ---------- 3. FIX: lock first, then read, check, write ----------
print("\n=== 3. Fix: lock with BEGIN IMMEDIATE ===")
setup()
amit, neha = user(), user()

amit.execute("BEGIN IMMEDIATE") # Amit takes the write lock
try:
    neha.execute("BEGIN IMMEDIATE") # Neha tries while Amit holds it
except sqlite3.OperationalError as e:
    print(f"  Neha blocked: {e}")

stock = amit.execute("SELECT stock FROM products WHERE id = 1").fetchone()[0]
if stock > 0:
    amit.execute("UPDATE products SET stock = ? WHERE id = 1", (stock - 1,))
    amit.execute("INSERT INTO orders VALUES ('Amit')")
amit.execute("COMMIT") # lock released
print("  Amit: bought it, lock released")

neha.execute("BEGIN IMMEDIATE") # Neha tries again, now it works
stock = neha.execute("SELECT stock FROM products WHERE id = 1").fetchone()[0]
print(f"  Neha now sees stock {stock}: {'bought it' if stock > 0 else 'sold out'}")
neha.execute("COMMIT")
result(amit)

amit.close()
neha.close()
os.remove(DB)

"""
=== 1. Read, check, write (race condition) ===
  Amit sees stock 1, Neha sees stock 1
  stock left: 0   orders: ['Amit', 'Neha']

=== 2. Fix: one atomic UPDATE ===
  Amit: bought it
  Neha: sold out
  stock left: 0   orders: ['Amit']

=== 3. Fix: lock with BEGIN IMMEDIATE ===
  Neha blocked: database is locked
  Amit: bought it, lock released
  Neha now sees stock 0: sold out
  stock left: 0   orders: ['Amit']
"""