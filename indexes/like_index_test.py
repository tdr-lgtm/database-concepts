import sqlite3
conn = sqlite3.connect(":memory:")
conn.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, email TEXT)")
conn.execute("CREATE INDEX idx_email ON users(email)")
 
queries = [
    "email = 'amit@gmail.com'",    # exact
    "email LIKE 'amit%'",          # starts with
    "email LIKE '%gmail.com'",     # ends with
    "email LIKE '%mit%'",          # contains
]
 
for where in queries:
    plan = conn.execute(f"EXPLAIN QUERY PLAN SELECT * FROM users WHERE {where}").fetchone()[-1]
    print(f"{where:<28} -> {plan}")

"""   
email = 'amit@gmail.com'     -> SEARCH users USING COVERING INDEX idx_email (email=?)
email LIKE 'amit%'           -> SCAN users
email LIKE '%gmail.com'      -> SCAN users
email LIKE '%mit%'           -> SCAN users
"""