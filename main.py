import http.cookies
import http.server
import os
import re

from build_user_html import build_user_html
from credentials_validation import is_email_valid, is_name_valid, is_password_valid
from database import con, cursor

# from read_user_data import read_user_data

COOKIE_NAME = "message"
COOKIE_VALUE = "youshallpass"


# cookie check helper
def is_authenticated(self):
    cookie_headers = self.headers.get("Cookie", "")
    cookie = http.cookies.SimpleCookie()
    cookie.load(cookie_headers)

    return COOKIE_NAME in cookie and cookie[COOKIE_NAME].value == COOKIE_VALUE


# get current user id
def get_current_user_id(self):
    cookie_headers = self.headers.get("Cookie", "")
    cookie = http.cookies.SimpleCookie()
    cookie.load(cookie_headers)

    current_user_id = cookie["user_id"].value
    return int(current_user_id)


# get current user from DB
def get_current_user(self):
    user_id = get_current_user_id(self)

    # get user from DB
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user_row = cursor.fetchone()

    return user_row


# check if user is admin
def is_admin(self):
    current_user = get_current_user(self)

    role = current_user[4]

    return role == "admin"


class MyHandler(http.server.BaseHTTPRequestHandler):
    # handle all GET requests
    def do_GET(self):
        # show login page
        if self.path == "/login":
            with open("login.html", "rb") as f:
                login_page = f.read()

            final_page = login_page.decode("utf-8").replace("{message}", "")

            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(final_page.encode("utf-8"))

        # handle deleting User
        path = self.path
        regex = r"^/delete/[1-9]+$"

        if re.fullmatch(regex, path):
            # check for cookie
            if not is_authenticated(self):
                self.send_response(303)
                self.send_header("Location", "/login")
                self.end_headers()
                return

            if not is_admin(self):
                self.send_response(303)
                self.send_header("Location", "/")
                self.end_headers()
                return

            requested_user_id = int(path.split("/")[2])

            cursor.execute(
                "SELECT name, email, password FROM users WHERE id = ?",
                (requested_user_id,),
            )
            req_user_to_delete = cursor.fetchone()

            if req_user_to_delete is None:
                self.send_response(404)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                self.wfile.write(b"Index not valid OR Item already deleted")
                return

            cursor.execute("DELETE FROM users WHERE id = ?", (requested_user_id,))
            con.commit()

            self.send_response(303)
            self.send_header("Location", "/")
            self.end_headers()
            return

        # handle dynamic route
        path = self.path
        regex = r"^/edit/[1-9]+$"

        # if id matches the regex
        if re.fullmatch(regex, path):
            # check for cookie
            if not is_authenticated(self):
                self.send_response(303)
                self.send_header("Location", "/login")
                self.end_headers()
                return

            # open edit.html page
            with open("edit.html", "rb") as f:
                edit_page_data = f.read()

            # extract the id form the incoming route
            requested_user_id = int(path.split("/")[2])

            # check if users is not admin and the users id does not match with the cookie user-id
            # redirect to index page
            if (
                not is_admin(self)
                and not get_current_user_id(self) == requested_user_id
            ):
                self.send_response(303)
                self.send_header("Location", "/")
                self.end_headers()
                return

            try:
                # fetch all the data from the table
                cursor.execute("SELECT * FROM users WHERE id = ?", (requested_user_id,))

                requested_user = cursor.fetchone()
                if requested_user is None:
                    self.send_response(400)
                    self.send_header("Content/Type", "text/html")
                    self.end_headers()
                    self.wfile.write(b"ID not valid")

                req_user_name = requested_user[1]
                req_user_email = requested_user[2]
                req_user_password = requested_user[3]

                edit_page = (
                    edit_page_data.decode("utf-8")
                    .replace("{idnum}", f"Edit item with id: {requested_user_id}")
                    .replace("{id}", str(requested_user_id))
                    .replace("{name}", f"{req_user_name}")
                    .replace("{email}", f"{req_user_email}")
                    .replace("{password}", f"{req_user_password}")
                )

                self.send_response(200)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                self.wfile.write(edit_page.encode("utf-8"))
                return
            except IndexError:
                self.send_response(404)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                self.wfile.write(b"The entered Index is not valid")
                return

        # dict to handle all the different strict url routes
        routes = {
            "/": "index.html",
            "/about": "about.html",
            "/contact": "contact.html",
        }

        if self.path in routes:
            filename = routes[self.path]

            try:
                with open(filename, "rb") as f:
                    data = f.read()

                    # handle index.html
                    if filename == "index.html":
                        # check for cookie
                        if not is_authenticated(self):
                            self.send_response(303)
                            self.send_header("Location", "/login")
                            self.end_headers()
                            return

                        if not os.path.exists("users.db"):
                            self.send_response(500)
                            self.end_headers()
                            self.wfile.write(b"Not Found")
                            return

                        cursor.execute("SELECT * FROM users")
                        users_info = cursor.fetchall()
                        users_html = build_user_html(
                            users_info, is_admin(self), get_current_user_id(self)
                        )

                        role = "admin" if is_admin(self) else "user"

                        final_page = (
                            data.decode("utf-8")
                            .replace("{role}", role)
                            .replace("{content}", users_html)
                        )
                        self.send_response(200)
                        self.send_header("Content-Type", "text/html")
                        self.end_headers()
                        self.wfile.write(final_page.encode("utf-8"))
                        return
                    self.send_response(200)
                    self.send_header("Content-Type", "text/html")
                    self.end_headers()
                    self.wfile.write(data)
                    return
            except Exception as e:
                print(e)
                self.send_response(500)
                self.end_headers()
                self.wfile.write(b"Server ErrorDB")
                return
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")
            return

    def do_POST(self):

        if self.path == "/authenticate":
            # get data from incoming request
            content_length = int(self.headers.get("Content-Length", 0))
            raw_body = self.rfile.read(content_length).decode("utf-8")

            from urllib.parse import parse_qs

            parsed = parse_qs(raw_body)

            username = parsed.get("username", [""])[0]
            password = parsed.get("password", [""])[0]

            # get data from the DB
            cursor.execute("SELECT * FROM users")
            stored_users = cursor.fetchall()

            loggedin_users_id = None
            in_stored_users = False
            for user in stored_users:
                if username == user[1] and password == user[3]:
                    in_stored_users = True
                    loggedin_users_id = user[0]
                    break

            if in_stored_users:
                self.send_response(303)
                self.send_header("Location", "/")
                self.send_header(
                    "Set-Cookie", f"{COOKIE_NAME}={COOKIE_VALUE};Path=/; HttpOnly"
                )
                self.send_header(
                    "Set-Cookie", f"user_id={loggedin_users_id};Path=/; HttpOnly"
                )
                self.end_headers()
                return

            with open("login.html", "rb") as f:
                login_page = f.read()

            final_page = login_page.decode("utf-8").replace(
                "{message}", "Username or Password Incorrect"
            )

            self.send_response(400)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(final_page.encode("utf-8"))
            return

        if self.path == "/addUser":
            # check for cookie
            if not is_authenticated(self):
                self.send_response(303)
                self.send_header("Location", "/login")
                self.end_headers()
                return

            if not is_admin(self):
                self.send_response(303)
                self.send_header("Location", "/")
                self.end_headers()
                return

            # get the exact no.of bytes to read
            content_length = int(self.headers.get("Content-Length", 0))

            # .rfile input the stream of incoming request body
            # .read read exactly this many bytes from the stream
            # .decode convert those bytes into readable python string
            raw_body = self.rfile.read(content_length).decode("utf-8")

            from urllib.parse import parse_qs

            parsed = parse_qs(raw_body)

            name = parsed.get("name", [""])[0]
            email = parsed.get("email", [""])[0]
            password = parsed.get("password", [""])[0]

            if not is_email_valid(email):
                self.send_response(400)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                self.wfile.write(b"Invalid Email")
                return

            if not is_name_valid(name):
                self.send_response(400)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                self.wfile.write(b"Invalid Name")
                return

            if not is_password_valid(password):
                self.send_response(400)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                self.wfile.write(b"Invalid Password")
                return

            try:
                cursor.execute(
                    "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                    (name, email, password),
                )
                con.commit()

                self.send_response(303)
                self.send_header("Location", "/")
                self.end_headers()
                # self.wfile.write(b"<h1>User Added</h1><a href='/'>Home</a>")
                return
            except Exception:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(b"Server Error")
                return

        # handle edit username
        if self.path == "/editUser":
            # check for cookie
            if not is_authenticated(self):
                self.send_response(303)
                self.send_header("Location", "/login")
                self.end_headers()
                return

            # get edited data
            edited_content_length = int(self.headers.get("Content-Length", 0))

            raw_edited_data_body = self.rfile.read(edited_content_length).decode(
                "utf-8"
            )

            from urllib.parse import parse_qs

            parsed = parse_qs(raw_edited_data_body)

            try:
                edited_item_id = int(parsed.get("id", [""])[0])
            except ValueError:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(f"Invalid id: {parsed}".encode("utf-8"))
                return

            edited_item_name = parsed.get("name", [""])[0]
            edited_item_email = parsed.get("email", [""])[0]
            edited_item_password = parsed.get("password", [""])[0]

            if not is_email_valid(edited_item_email):
                self.send_response(400)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                self.wfile.write(b"Invalid Email")
                return

            if not is_name_valid(edited_item_name):
                self.send_response(400)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                self.wfile.write(b"Invalid Name")
                return

            if not is_password_valid(edited_item_password):
                self.send_response(400)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                self.wfile.write(b"Invalid Password")
                return

            try:
                cursor.execute(
                    "SELECT name, email, password FROM users WHERE id = ?",
                    (edited_item_id,),
                )
                user_data_from_table = cursor.fetchone()

                if user_data_from_table == (
                    edited_item_name,
                    edited_item_email,
                    edited_item_password,
                ):
                    self.send_response(200)
                    self.send_header("Content-Type", "text/html")
                    self.end_headers()
                    self.wfile.write(b"<p>No changes made</p> <a href='/'>Home</a>")
                    return

                cursor.execute(
                    "UPDATE users SET name = ?, email = ?, password = ? WHERE id = ?",
                    (
                        edited_item_name,
                        edited_item_email,
                        edited_item_password,
                        edited_item_id,
                    ),
                )
                con.commit()

                self.send_response(200)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                self.wfile.write(b"<p>Changes submitted</p> <a href='/'>Home</a>")
                return
            except IndexError:
                self.send_response(404)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                self.wfile.write(b"<p>User not found</p> <a href ='/'>Home</a>")
                return

        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")
            return

    def log_message(self, format, *args):
        pass


server = http.server.HTTPServer(("", 3000), MyHandler)
print("Server running on port 3000")
server.serve_forever()
