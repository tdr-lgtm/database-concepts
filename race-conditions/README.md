# Race Conditions and Locks

A race condition happens when two users change the same data at the same time,
and one of them acts on an old value.

## The problem

1 phone left. Amit and Neha click "Buy" at the same time.

```
Amit reads stock → 1
Neha reads stock → 1      (Amit hasn't saved yet)
Amit saves stock = 0, makes order
Neha saves stock = 0, makes order
```

Result: stock is 0, but there are **2 orders for 1 phone**.

The gap between reading and writing lets the other user sneak in.

## Fix 1: one atomic UPDATE

Check and change in a single statement, so there is no gap:

```sql
UPDATE products SET stock = stock - 1 WHERE id = 1 AND stock > 0
```

If 1 row changed, you got the item. If 0 rows changed, it's sold out.
The database checks the **current** stock, not the number the user saw earlier.

## Fix 2: lock first

```sql
BEGIN IMMEDIATE
```

Takes the lock before reading. Others must wait until `COMMIT`, then they see the fresh stock.
(PostgreSQL uses `SELECT ... FOR UPDATE` for the same idea.)

Use Fix 1 when the check and change fit in one statement. Use a lock when they don't.

## Demo 1: `last_item_demo.py`

Two users, steps run in a fixed order so the result is easy to follow.

| Case | Orders | Correct? |
|---|---|---|
| Read, check, write | Amit, Neha | No, 1 phone sold twice |
| One atomic UPDATE | Amit | Yes |
| BEGIN IMMEDIATE | Amit | Yes |

## Demo 2: `real_threads_test.py`

50 users click "Buy" at the same moment, using real threads.

| Method | Orders for 1 phone |
|---|---|
| Read, check, write | **46** |
| One atomic UPDATE | 1 |

The unsafe count changes every run. The atomic one is always 1.

## Run

```bash
python last_item_demo.py
python real_threads_test.py
```

Both create a temporary `.db` file and delete it at the end.