import sqlite3

# create a connection to sqlite db from the disk, creates it if now already present
con = sqlite3.connect("users.db")
# con.row_factory = sqlite3.Row
cursor = con.cursor()

cursor.execute("""
    CREATE TABLE if not exists users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT UNIQUE NOT NULL
    )
""")

# data = [
#     ("Legolas Greenleaf", "legolas.greenleaf@mirkwood.net", "Lg7@Mirkwood"),
#     ("Tyrion Lannister", "tyrion.lannister@casterly.com", "L1on@Drinks4ever"),
#     ("Frodo Baggins", "frodo.baggins@theshire.net", "R1ngB3ar3r@Shire"),
#     ("Rand alThor", "rand.althor@tworivers.net", "Dr4g0nR3b0rn@Light"),
# ]

# cursor.executemany(
#     "INSERT OR IGNORE INTO users (name, email, password) VALUES (?, ?, ?)", data
# )
# con.commit()

result = cursor.execute("SELECT * FROM users")
print(result.fetchall())
# con.close()

# new_con = sqlite3.connect("users.db")
# new_cursor = new_con.cursor()
# result = new_cursor.execute("SELECT * FROM users")
# print(result.fetchall())
# new_con.close()
