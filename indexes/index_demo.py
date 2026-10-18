import sqlite3
import random
import time
 
ROWS = 200_000

def make_db():
    conn = sqlite3.connect(":memory:") # temporary in-RAM database, no file created, gone when the connection closes
    conn.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, email TEXT, city TEXT)")
    random.seed(42)
    cities = ["Ahmedabad", "Surat", "Vadodara", "Rajkot", "Gandhinagar"]
    rows = [(i, f"user{i}@mail.com", random.choice(cities)) for i in range(1, ROWS + 1)]
    conn.executemany("INSERT INTO users VALUES (?, ?, ?)", rows)
    conn.commit()
    return conn

def query_plan(conn, sql, params=()):
    # ask the database HOW it will run a query
    rows = conn.execute("EXPLAIN QUERY PLAN " + sql, params).fetchall()
    return " | ".join(row[-1] for row in rows)   # last column holds the plan text
 
def time_query(conn, sql, params, runs=200):
    start = time.perf_counter()
    for _ in range(runs):
        conn.execute(sql, params).fetchall()
    return (time.perf_counter() - start) * 1000

FIND_BY_EMAIL = "SELECT id, city FROM users WHERE email = ?"
TARGET = ("user150000@mail.com",)

def test_without_index_db_scans_whole_table():
    conn = make_db()
    plan = query_plan(conn, FIND_BY_EMAIL, TARGET)
    assert plan.startswith("SCAN"), plan

def test_with_index_db_searches_directly():
    conn = make_db()
    conn.execute("CREATE INDEX idx_users_email ON users(email)")
    plan = query_plan(conn, FIND_BY_EMAIL, TARGET)
    print(plan)
    assert "SEARCH" in plan and "idx_users_email" in plan, plan

def test_index_does_not_change_the_answer():
    conn = make_db()
    before = conn.execute(FIND_BY_EMAIL, TARGET).fetchall()
    conn.execute("CREATE INDEX idx_users_email ON users(email)")
    after = conn.execute(FIND_BY_EMAIL, TARGET).fetchall()
    assert before == after
    assert before[0][0] == 150000

def test_index_is_faster():
    conn = make_db()
    slow = time_query(conn, FIND_BY_EMAIL, TARGET)
    conn.execute("CREATE INDEX idx_users_email ON users(email)")
    fast = time_query(conn, FIND_BY_EMAIL, TARGET)
    assert fast * 10 < slow, f"without={slow:.1f}ms with={fast:.1f}ms"

if __name__ == "__main__":
    tests = [
        test_without_index_db_scans_whole_table,
        test_with_index_db_searches_directly,
        test_index_does_not_change_the_answer,
        test_index_is_faster,
    ]
    for t in tests:
        t()
        print(f"PASS  {t.__name__}")
 
    conn = make_db()
    print(f"\nTable has {ROWS:,} rows. Looking up one email, 200 times.\n")
 
    print("WITHOUT index")
    print("  plan:", query_plan(conn, FIND_BY_EMAIL, TARGET))
    print(f"  time: {time_query(conn, FIND_BY_EMAIL, TARGET):8.1f} ms")
 
    conn.execute("CREATE INDEX idx_users_email ON users(email)")
 
    print("\nWITH index")
    print("  plan:", query_plan(conn, FIND_BY_EMAIL, TARGET))
    print(f"  time: {time_query(conn, FIND_BY_EMAIL, TARGET):8.1f} ms")


"""
PASS  test_without_index_db_scans_whole_table
PASS  test_with_index_db_searches_directly
PASS  test_index_does_not_change_the_answer
PASS  test_index_is_faster

Table has 200,000 rows. Looking up one email, 200 times.

WITHOUT index
  plan: SCAN users
  time:   1661.1 ms

WITH index
  plan: SEARCH users USING INDEX idx_users_email (email=?)
  time:      0.5 ms
"""