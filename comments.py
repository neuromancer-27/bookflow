import sqlite3

con_comments = sqlite3.connect("users.db")
cursor_comments = con_comments.cursor()

cursor_comments.execute("""
    CREATE TABLE if not exists comments_table(
    id INTEGER PRIMARY KEY,
    receiver_id INTEGER NOT NULL,
    sender_id INTEGER NOT NULL,
    content TEXT NOT NULL CHECK (
        length(content) <= 100
        AND length(trim(content)) > 0
        ),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """);

result = cursor_comments.execute("SELECT * FROM comments_table")
print(result.fetchall())
