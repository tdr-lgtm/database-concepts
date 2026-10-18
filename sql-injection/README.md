# SQL Injection

SQL injection happens when user input is pasted into a SQL query as text.
The attacker can then add their own SQL.

## The attack

```python
# BAD: input pasted into the SQL text
sql = f"SELECT id FROM users WHERE email = '{email}' AND password = '{password}'"
```

If the attacker types this as the password:

```
' OR '1'='1
```

The query becomes:

```sql
SELECT id FROM users WHERE email = 'admin@mail.com' AND password = '' OR '1'='1'
```

`'1'='1'` is always true, so the attacker logs in without the password.

## The fix

```python
# GOOD: ? placeholders, input is sent separately as plain data
conn.execute("SELECT id FROM users WHERE email = ? AND password = ?", (email, password))
```

The input is only ever treated as a value, never as SQL. The attack becomes just a wrong password.

**Rule:** never build SQL with f-strings or `+` using user input. Always use `?`.

## Result

| Try | Unsafe | Safe |
|---|---|---|
| Correct password | Logged in | Logged in |
| Wrong password | Blocked | Blocked |
| `' OR '1'='1` | **Logged in** | Blocked |

Note: this demo stores passwords as plain text to keep it simple. Real apps store a hash.

## Run

```bash
python login_demo.py
```