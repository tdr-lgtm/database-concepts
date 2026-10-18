import sqlite3
import time

conn = sqlite3.connect(":memory:")
conn.execute("CREATE TABLE posts (id INTEGER PRIMARY KEY, title TEXT)")
conn.executemany("INSERT INTO posts VALUES (?, ?)",
                 [(i, f"Post {i}") for i in range(1, 1_000_001)])   # 1 million posts

PAGE_SIZE = 20

def offset_page(page):
    # skip (page-1)*20 rows, then take 20
    return conn.execute("SELECT id, title FROM posts ORDER BY id LIMIT ? OFFSET ?",
                        (PAGE_SIZE, (page - 1) * PAGE_SIZE)).fetchall()

def keyset_page(last_id):
    # start right after the last id we showed
    return conn.execute("SELECT id, title FROM posts WHERE id > ? ORDER BY id LIMIT ?",
                        (last_id, PAGE_SIZE)).fetchall()

def ms(fn, arg, runs=50):
    start = time.perf_counter()
    for _ in range(runs):
        fn(arg)
    return (time.perf_counter() - start) * 1000 / runs   # average per page

print(f"{'page':>8} {'OFFSET':>10} {'keyset':>10}")
for page in (1, 1_000, 25_000, 49_999):
    last_id = (page - 1) * PAGE_SIZE                 # last id shown on the previous page
    assert offset_page(page) == keyset_page(last_id)  # both give the same 20 posts
    print(f"{page:>8} {ms(offset_page, page):>8.2f}ms {ms(keyset_page, last_id):>8.2f}ms")

"""
    page     OFFSET     keyset
       1     0.02ms     0.02ms
    1000     0.42ms     0.02ms
   25000     7.08ms     0.02ms
   49999    18.32ms     0.02ms
"""