import sqlite3

# create a connection to sqlite db from the disk, creates it if now already present
con = sqlite3.connect("users.db")
# con.row_factory = sqlite3.Row
cursor = con.cursor()

cursor.execute("""
    CREATE TABLE if not exists users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL
    )
""")

# data = [
#     ("Legolas Greenleaf", "legolas.greenleaf@mirkwood.net"),
#     ("Katniss Everdeen", "katniss.everdeen@panemmail.com"),
#     ("Bilbo Baggins", "bilbo.baggins@shiremail.com"),
#     ("Jay Gatsby", "jay.gatsby@westegg.com"),
# ]

# cursor.executemany("INSERT OR IGNORE INTO users (name, email) VALUES (?, ?)", data)
# con.commit()

result = cursor.execute("SELECT * FROM users")
print(result.fetchall())
# con.close()

# new_con = sqlite3.connect("users.db")
# new_cursor = new_con.cursor()
# result = new_cursor.execute("SELECT * FROM users")
# print(result.fetchall())
# new_con.close()
