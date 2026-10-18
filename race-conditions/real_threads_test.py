# 50 users buy the last phone at the SAME time, using real threads.
import os
import sqlite3
import threading
import time

DB = "shop_threads.db"
USERS = 50

def setup():
    if os.path.exists(DB):
        os.remove(DB)
    conn = sqlite3.connect(DB)
    conn.execute("CREATE TABLE products (id INTEGER PRIMARY KEY, stock INTEGER)")
    conn.execute("CREATE TABLE orders (buyer TEXT)")
    conn.execute("INSERT INTO products VALUES (1, 1)") # 1 phone
    conn.commit()
    conn.close()

def buy_unsafe(name):
    conn = sqlite3.connect(DB, isolation_level=None, timeout=10)
    stock = conn.execute("SELECT stock FROM products WHERE id = 1").fetchone()[0]
    time.sleep(0.01) # tiny delay, like a real app doing work
    if stock > 0:
        conn.execute("UPDATE products SET stock = ? WHERE id = 1", (stock - 1,))
        conn.execute("INSERT INTO orders VALUES (?)", (name,))
    conn.close()

def buy_atomic(name):
    conn = sqlite3.connect(DB, isolation_level=None, timeout=10)
    cur = conn.execute("UPDATE products SET stock = stock - 1 WHERE id = 1 AND stock > 0")
    if cur.rowcount == 1:
        conn.execute("INSERT INTO orders VALUES (?)", (name,))
    conn.close()

for fn in (buy_unsafe, buy_atomic):
    setup()
    threads = [threading.Thread(target=fn, args=(f"user{i}",)) for i in range(USERS)]
    for t in threads:
        t.start() # all 50 start together
    for t in threads:
        t.join() # wait for all to finish

    conn = sqlite3.connect(DB)
    orders = conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
    stock = conn.execute("SELECT stock FROM products").fetchone()[0]
    conn.close()
    print(f"{fn.__name__:<12} {USERS} users, 1 phone -> orders: {orders}, stock left: {stock}")

os.remove(DB)

"""
buy_unsafe   50 users, 1 phone -> orders: 46, stock left: 0
buy_atomic   50 users, 1 phone -> orders: 1, stock left: 0
"""