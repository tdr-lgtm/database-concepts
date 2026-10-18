import sqlite3
import time

ROWS = 200_000

def timed(conn, sql, params=()):
    start = time.perf_counter()
    conn.execute(sql, params) if params else conn.executescript(sql)
    return (time.perf_counter() - start) * 1000

def test(indexes):
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, email TEXT, city TEXT, age INTEGER, bio TEXT)")
    for col in indexes:
        conn.execute(f"CREATE INDEX idx_{col} ON users({col})")

    rows = [(i, f"user{i}@mail.com", f"city{i % 50}", i % 90, "hello") for i in range(1, ROWS + 1)]
    start = time.perf_counter()
    conn.executemany("INSERT INTO users VALUES (?, ?, ?, ?, ?)", rows)
    insert = (time.perf_counter() - start) * 1000

    upd_email = timed(conn, "UPDATE users SET email = email || 'x' WHERE id <= 100000;")  # indexed column
    upd_bio = timed(conn, "UPDATE users SET bio = 'bye' WHERE id <= 100000;")              # NOT indexed
    delete = timed(conn, "DELETE FROM users WHERE id <= 100000;")

    return insert, upd_email, upd_bio, delete


print(f"{'indexes':<20}" + "".join(f"{h:>13}" for h in ["insert 200k", "update email", "update bio", "delete 100k"]))
for idx in ([], ["email"], ["email", "city", "age"]):
    times = test(idx)
    label = ", ".join(idx) or "none"
    print(f"{label:<20}" + "".join(f"{t:>11.0f}ms" for t in times))


"""
indexes               insert 200k update email   update bio  delete 100k
none                        171ms         30ms         23ms         15ms
email                       300ms        111ms         23ms         58ms
email, city, age            845ms        145ms         34ms        179ms
"""