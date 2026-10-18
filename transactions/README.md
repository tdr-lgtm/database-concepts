# Transactions

A transaction is a group of steps that either **all happen or none happen**. Never half.

## The problem

Sending 500 from A to B is 2 steps:

1. take 500 from A
2. give 500 to B

If the server crashes between step 1 and step 2, A loses 500 and B gets nothing.
The money is gone.

## The fix

```sql
BEGIN      -- start: nothing is saved yet
...steps...
COMMIT     -- save all steps together
ROLLBACK   -- or undo everything since BEGIN
```

If anything fails before `COMMIT`, `ROLLBACK` undoes every step. If the power goes off,
the database undoes it by itself when it restarts.

## Result

The demo crashes after step 1:

| | Before | After | Total |
|---|---|---|---|
| Without transaction | A 1000, B 0 | A 500, B 0 | **500** (money lost) |
| With transaction | A 1000, B 0 | A 1000, B 0 | 1000 |

## Run

```bash
python transfer_demo.py
```