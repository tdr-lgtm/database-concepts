import sqlite3
import time

def make_db():
    conn = sqlite3.connect(":memory:") # temporary in-RAM database, no file created, gone when the connection closes
    conn.executescript("""
        CREATE TABLE authors (id INTEGER PRIMARY KEY, name TEXT);
        CREATE TABLE books   (id INTEGER PRIMARY KEY, title TEXT, author_id INTEGER);
    """)
    for a in range(1, 11):
        conn.execute("INSERT INTO authors VALUES (?, ?)", (a, f"Author {a}"))
    for b in range(1, 101):
        author_id = (b % 10) + 1
        conn.execute("INSERT INTO books VALUES (?, ?, ?)", (b, f"Book {b}", author_id))
    conn.commit()
    return conn

class QueryCounter:
    def __init__(self, conn):
        self.conn = conn
        self.queries = []
 
    def __enter__(self):
        self.queries.clear()
        self.conn.set_trace_callback(self.queries.append)
        return self
 
    def __exit__(self, *exc):
        self.conn.set_trace_callback(None)
 
    @property
    def count(self):
        return len(self.queries)

def books_n_plus_one(conn):
    # 1 query for books + 1 query per book for its author.
    result = []
    books = conn.execute("SELECT id, title, author_id FROM books ORDER BY id").fetchall()
    for _, title, author_id in books:
        name = conn.execute("SELECT name FROM authors WHERE id = ?", (author_id,)).fetchone()[0]
        result.append((title, name))
    return result

def books_join(conn):
    # FIX 2: let the database combine both tables -> 1 query.
    return conn.execute("""
        SELECT books.title, authors.name
        FROM books
        JOIN authors ON authors.id = books.author_id
        ORDER BY books.id
    """).fetchall()

def books_batch(conn):
    # FIX 2: fetch books, then ALL needed authors in one go -> 2 queries.
    books = conn.execute("SELECT id, title, author_id FROM books ORDER BY id").fetchall()
 
    author_ids = sorted({author_id for _, _, author_id in books})
    placeholders = ",".join("?" * len(author_ids))
    rows = conn.execute(
        f"SELECT id, name FROM authors WHERE id IN ({placeholders})", author_ids
    ).fetchall()
 
    names = dict(rows)
    return [(title, names[author_id]) for _, title, author_id in books]

def test_n_plus_one_runs_101_queries():
    conn = make_db()
    with QueryCounter(conn) as qc:
        books_n_plus_one(conn)
    assert qc.count == 101, f"expected 101, got {qc.count}"

def test_join_runs_1_query():
    conn = make_db()
    with QueryCounter(conn) as qc:
        books_join(conn)
    assert qc.count == 1, f"expected 1, got {qc.count}"

def test_batch_runs_2_queries():
    conn = make_db()
    with QueryCounter(conn) as qc:
        books_batch(conn)
    assert qc.count == 2, f"expected 2, got {qc.count}"

def test_all_three_return_same_data():
    conn = make_db()
    slow = books_n_plus_one(conn)
    assert books_join(conn) == slow
    assert books_batch(conn) == slow
    assert len(slow) == 100
    assert slow[0] == ("Book 1", "Author 2")


def test_batch_fetches_each_author_once():
    # 10 authors are shared across 100 books -> IN list should hold 10 ids, not 100.
    conn = make_db()
    with QueryCounter(conn) as qc:
        books_batch(conn)
    author_query = qc.queries[1]
    in_list = author_query[author_query.index("IN (") + 4 : author_query.rindex(")")]
    ids = in_list.split(",")
    assert len(ids) == 10, author_query

if __name__ == "__main__":
    tests = [
        test_n_plus_one_runs_101_queries,
        test_join_runs_1_query,
        test_batch_runs_2_queries,
        test_all_three_return_same_data,
        test_batch_fetches_each_author_once,
    ]
    for t in tests:
        t()
        print(f"PASS  {t.__name__}")
 
    print("\nTiming (1000 runs each, in-memory DB):")
    conn = make_db()
    for fn in (books_n_plus_one, books_join, books_batch):
        start = time.perf_counter()
        for _ in range(1000):
            fn(conn)
        ms = (time.perf_counter() - start) * 1000
        print(f"  {fn.__name__:<18} {ms:8.1f} ms")
 
"""
PASS  test_n_plus_one_runs_101_queries
PASS  test_join_runs_1_query
PASS  test_batch_runs_2_queries
PASS  test_all_three_return_same_data
PASS  test_batch_fetches_each_author_once

Timing (1000 runs each, in-memory DB):
  books_n_plus_one      254.0 ms
  books_join             61.1 ms
  books_batch            88.0 ms
"""