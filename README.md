# Database Concepts

Small, runnable demos of database and SQL concepts. Each one shows the behavior
with real output or tests, not just theory.

| Topic | What it shows |
|---|---|
| [n-plus-one](n-plus-one/) | The N+1 query problem and two fixes (JOIN, batch IN), with query-count tests |
| [indexes](indexes/) | How indexes make lookups and JOINs fast, when they're not used, and what they cost on writes |
| [pagination](pagination/) | Why OFFSET gets slow on deep pages, and how keyset pagination stays fast |
| [sql-injection](sql-injection/) | How a login can be bypassed with pasted-in input, and how `?` placeholders stop it |
| [transactions](transactions/) | A money transfer that crashes halfway, and how a transaction stops money from disappearing |
| [race-conditions](race-conditions/) | Two users buy the last item at once, fixed with an atomic UPDATE or a lock |

Run any demo: `python <folder>/<file>.py` (Python 3, SQLite built in, nothing to install).