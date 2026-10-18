# Indexes

## What is an index?

An index is a sorted copy of one column, kept next to the table.
Each value points to its row. The table itself does not change.

| Table (insert order) | Index on email (sorted) |
|---|---|
| 1 · zara@mail.com | amit@mail.com → 2 |
| 2 · amit@mail.com | kiran@mail.com → 5 |
| 3 · meet@mail.com | meet@mail.com → 3 |
| 4 · neha@mail.com | neha@mail.com → 4 |
| 5 · kiran@mail.com | zara@mail.com → 1 |

## Why is it fast?

Like the index at the back of a book.

- **No index:** check every row. 200,000 rows = 200,000 checks.
- **With index:** the list is sorted, so cut it in half each step.
  200,000 rows = about 17 steps.

## How to create one

```sql
CREATE INDEX idx_users_email ON users(email);
```

- Create it once. Before or after adding data, both work.
- Your queries don't change. The database uses the index by itself.
- `PRIMARY KEY` and `UNIQUE` columns get one automatically.

## How to check

Put `EXPLAIN QUERY PLAN` before your query:

| You see | Meaning |
|---|---|
| `SCAN` | Reads every row. Slow. |
| `SEARCH ... USING INDEX` | Finds the row in the index, then opens the table for the other columns. |
| `USING COVERING INDEX` | Gets everything from the index. Never opens the table. |

## Covering index

The index only holds its columns plus the row id. If you ask for another column,
the database has to open the table.

```sql
SELECT id   FROM users WHERE email = ...   -- covering: index has id
SELECT city FROM users WHERE email = ...   -- opens the table for city
```

An index can hold more than one column. Then that query becomes covering too:

```sql
CREATE INDEX idx_email_city ON users(email, city);
```

More columns make the index bigger, so only do this for queries you run a lot.

## When the index is not used

| Search | Uses index? |
|---|---|
| `email = 'amit@gmail.com'` | Yes |
| `email LIKE 'amit%'` | No (in SQLite, by default) |
| `email LIKE '%gmail.com'` | No |
| `email LIKE '%mit%'` | No |
| `LOWER(email) = ...` | No |

The index is sorted by the exact value, from the first letter. If you change the value
or search the end or the middle, the sort order can't help.

## Index for JOIN

In `JOIN books ON books.author_id = authors.id`, the database must find books by
`author_id`. Without an index, it reads every book. So add one:

```sql
CREATE INDEX idx_books_author_id ON books(author_id);
```

`authors.id` already has an index because it's the primary key.

## The cost

Every index must be kept up to date when the data changes:

- **Insert:** the new row goes into every index.
- **Delete:** the row is removed from every index.
- **Update:** only the indexes on the changed columns are updated.

Measured on 200,000 rows (times slower than no index):

| Indexes | Insert | Update indexed column | Update other column | Delete |
|---|---|---|---|---|
| 1 | 1.8x | 3.7x | about the same | 3.9x |
| 3 | 4.9x | 4.8x | about the same | 11.9x |

Only index columns you often search or join on.

---

## Files

| File | What it shows |
|---|---|
| `index_demo.py` | Finding one user, 200 times, in 200,000 rows. Includes tests. |
| `join_index_demo.py` | Loading 200 author pages from 100,000 books |
| `three_plans.py` | `SCAN`, `USING INDEX` and `USING COVERING INDEX` side by side |
| `like_index_test.py` | Which searches use the index and which don't |
| `write_cost_test.py` | How indexes slow down insert, update and delete |

## Results

| Demo | No index | With index |
|---|---|---|
| `index_demo.py` | ~1661 ms (`SCAN`) | ~0.5 ms (`SEARCH`) |
| `join_index_demo.py` | ~946 ms (`SCAN books`) | ~18 ms (`SEARCH books`) |

## Run

```bash
python index_demo.py
python join_index_demo.py
python three_plans.py
python like_index_test.py
python write_cost_test.py
```

Python 3 only. Nothing to install. Times change from machine to machine.