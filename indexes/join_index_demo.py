import sqlite3
import time

conn = sqlite3.connect(":memory:")
conn.execute("CREATE TABLE authors (id INTEGER PRIMARY KEY, name TEXT)")
conn.execute("CREATE TABLE books (id INTEGER PRIMARY KEY, title TEXT, author_id INTEGER)")

# 1,000 authors, 100,000 books (each author wrote 100 books)
conn.executemany("INSERT INTO authors VALUES (?, ?)",
                 [(i, f"Author {i}") for i in range(1, 1001)])
conn.executemany("INSERT INTO books VALUES (?, ?, ?)",
                 [(i, f"Book {i}", (i % 1000) + 1) for i in range(1, 100_001)])

# author page: one author + all their books
QUERY = """
    SELECT authors.name, books.title
    FROM authors
    JOIN books ON books.author_id = authors.id
    WHERE authors.id = ?
"""

def run(label):
    plan = [row[-1] for row in conn.execute("EXPLAIN QUERY PLAN " + QUERY, (5,))]
    start = time.perf_counter()
    for author_id in range(1, 201):                     # open 200 author pages
        rows = conn.execute(QUERY, (author_id,)).fetchall()
    ms = (time.perf_counter() - start) * 1000
    print(f"{label}")
    print(f"  plan: {plan}")
    print(f"  books per author: {len(rows)}")
    print(f"  time for 200 author pages: {ms:.1f} ms\n")
    return ms

slow = run("WITHOUT index on books.author_id")
conn.execute("CREATE INDEX idx_books_author_id ON books(author_id)")
fast = run("WITH index on books.author_id")
print(f"{slow / fast:.0f}x faster")

"""
WITHOUT index on books.author_id
  plan: ['SEARCH authors USING INTEGER PRIMARY KEY (rowid=?)', 'SCAN books']
  books per author: 100
  time for 200 author pages: 945.8 ms

WITH index on books.author_id
  plan: ['SEARCH authors USING INTEGER PRIMARY KEY (rowid=?)', 'SEARCH books USING INDEX idx_books_author_id (author_id=?)']
  books per author: 100
  time for 200 author pages: 17.8 ms

53x faster
"""
