# N+1 Query Problem

Fetching 100 books, then each book's author one by one, runs 1 + 100 = 101 queries.

| Approach | Queries |
|---|---|
| N+1 (loop) | 101 |
| JOIN | 1 |
| Batch with IN | 2 |

Tests count every SQL statement with SQLite's trace callback and check that all three
approaches return identical data.

Run: `python n_plus_one_fix.py`