import sqlite3

conn = sqlite3.connect(":memory:")
conn.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, email TEXT, password TEXT)")
conn.execute("INSERT INTO users VALUES (1, 'admin@mail.com', 'secret123')")

def login_unsafe(email, password):
    # BAD: user input is pasted straight into the SQL text
    sql = f"SELECT id FROM users WHERE email = '{email}' AND password = '{password}'"
    print("  SQL sent:", sql)
    return conn.execute(sql).fetchone() is not None

def login_safe(email, password):
    # GOOD: ? placeholders, the input is sent separately as plain data
    sql = "SELECT id FROM users WHERE email = ? AND password = ?"
    print("  SQL sent:", sql, " data:", (email, password))
    return conn.execute(sql, (email, password)).fetchone() is not None

tries = [
    ("correct password", "admin@mail.com", "secret123"),
    ("wrong password",   "admin@mail.com", "guess"),
    ("ATTACK",           "admin@mail.com", "' OR '1'='1"),
]

for fn in (login_unsafe, login_safe):
    print(f"\n=== {fn.__name__} ===")
    for label, email, password in tries:
        print(f"{label}:")
        print("  logged in:", fn(email, password))

"""
=== login_unsafe ===
correct password:
  SQL sent: SELECT id FROM users WHERE email = 'admin@mail.com' AND password = 'secret123'
  logged in: True
wrong password:
  SQL sent: SELECT id FROM users WHERE email = 'admin@mail.com' AND password = 'guess'
  logged in: False
ATTACK:
  SQL sent: SELECT id FROM users WHERE email = 'admin@mail.com' AND password = '' OR '1'='1'
  logged in: True

=== login_safe ===
correct password:
  SQL sent: SELECT id FROM users WHERE email = ? AND password = ?  data: ('admin@mail.com', 'secret123')
  logged in: True
wrong password:
  SQL sent: SELECT id FROM users WHERE email = ? AND password = ?  data: ('admin@mail.com', 'guess')
  logged in: False
ATTACK:
  SQL sent: SELECT id FROM users WHERE email = ? AND password = ?  data: ('admin@mail.com', "' OR '1'='1")
  logged in: False
"""