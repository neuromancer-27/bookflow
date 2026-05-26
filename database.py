import sqlite3

# create a connection to sqlite db from the disk, creates it if now already present
con = sqlite3.connect("users.db")

cursor = con.cursor()

cursor.execute("CREATE TABLE if not exists users(name TEXT, email TEXT UNIQUE)")

data = [
    ("Legolas Greenleaf", "legolas.greenleaf@mirkwood.net"),
    ("Katniss Everdeen", "katniss.everdeen@panemmail.com"),
    ("Bilbo Baggins", "bilbo.baggins@shiremail.com"),
    ("Jay Gatsby", "jay.gatsby@westegg.com"),
]

cursor.executemany("INSERT INTO users VALUES (?, ?)", data)
con.commit()

result = cursor.execute("SELECT * FROM users")
print(result.fetchall())
con.close()

# new_con = sqlite3.connect("users.db")
# new_cursor = new_con.cursor()
# result = new_cursor.execute("SELECT * FROM users")
# print(result.fetchall())
# new_con.close()
