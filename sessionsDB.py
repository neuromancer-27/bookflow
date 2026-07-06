import sqlite3

conn_session = sqlite3.connect("sessions.db")
cursor_session = conn_session.cursor()

cursor_session.execute("""
    CREATE TABLE if not exists sessions(
    id INTEGER PRIMARY KEY,
    sessionID TEXT UNIQUE NOT NULL,
    user_ID INTEGER,
    CONSTRAINT fk_userID
        FOREIGN KEY (user_ID)
        REFERENCES users(id)
        ON DELETE RESTRICT
    );
    """)

cursor_session.execute("SELECT * FROM sessions")
result = cursor_session.fetchall()
print(result)
