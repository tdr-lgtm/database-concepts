# Pagination

Pagination means showing a big list in small pages, like 20 posts at a time.

## OFFSET

```sql
SELECT id, title FROM posts ORDER BY id LIMIT 20 OFFSET 40   -- ids 41 to 60
```

Skips 40 rows, then takes 20. The database reads every skipped row, so deep pages get slow.

## Keyset

```sql
SELECT id, title FROM posts WHERE id > 40 ORDER BY id LIMIT 20   -- ids 41 to 60
```

Starts after the last id shown. `id` has an index, so every page is fast.
The catch: you can only go to the next page, not jump to page 500.

## Result

1 million posts, 20 per page:

| Page | OFFSET | Keyset |
|---|---|---|
| 1 | 0.02 ms | 0.02 ms |
| 1,000 | 0.42 ms | 0.02 ms |
| 25,000 | 7.08 ms | 0.02 ms |
| 49,999 | 18.32 ms | 0.02 ms |

## Run

```bash
python offset_vs_keyset.py
```