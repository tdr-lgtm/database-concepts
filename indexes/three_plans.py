import sqlite3

conn = sqlite3.connect(":memory:")
conn.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, email TEXT, city TEXT)")
# an index can have multiple columns, e.g. CREATE INDEX idx_email_city ON users(email, city)
conn.execute("CREATE INDEX idx_email ON users(email)")

queries = [
    "SELECT * FROM users WHERE city = 'Surat'",              # SCAN: city has no index
    "SELECT city FROM users WHERE email = 'amit@mail.com'",  # INDEX: index finds row, table gives city
    "SELECT id FROM users WHERE email = 'amit@mail.com'",    # COVERING: index has email + id, no table trip
]

for sql in queries:
    plan = conn.execute("EXPLAIN QUERY PLAN " + sql).fetchone()[-1]
    print(f"{sql:<55} -> {plan}")


"""
SELECT * FROM users WHERE city = 'Surat'                -> SCAN users
SELECT city FROM users WHERE email = 'amit@mail.com'    -> SEARCH users USING INDEX idx_email (email=?)
SELECT id FROM users WHERE email = 'amit@mail.com'      -> SEARCH users USING COVERING INDEX idx_email (email=?)
"""