import sqlite3

from salt_hashing import hash_password

# create a connection to sqlite db from the disk, creates it if not already present
con = sqlite3.connect("users.db")
# con.row_factory = sqlite3.Row
cursor = con.cursor()

cursor.execute("""
    CREATE TABLE if not exists users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT UNIQUE NOT NULL,
        role TEXT NOT NULL DEFAULT 'user'
            CHECK(role IN('user', 'admin'))
    )
""")

salt, passwordhash = hash_password("Admin@Pass1")
stored_password = f"{salt.hex()}:{passwordhash.hex()}"

# cursor.execute("""
#     INSERT OR IGNORE INTO users (name, email, password, role)
#     VALUES (?, ?, ?, ?)
# """,
# ('admin', 'admin@example.com', stored_password, 'admin'),
# )
# con.commit()

# data = [
#     ("Legolas Greenleaf", "legolas.greenleaf@mirkwood.net", "Lg7@Mirkwood"),
#     ("Tyrion Lannister", "tyrion.lannister@casterly.com", "L1on@Drinks4ever"),
#     ("Frodo Baggins", "frodo.baggins@theshire.net", "R1ngB3ar3r@Shire"),
#     ("Rand alThor", "rand.althor@tworivers.net", "DragonR3born@Light"),
# ]

# cursor.executemany(
#     "INSERT OR IGNORE INTO users (name, email, password) VALUES (?, ?, ?)", data
# )
# con.commit()

result = cursor.execute("SELECT * FROM users")
print(result.fetchall())
