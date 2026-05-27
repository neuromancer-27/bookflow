import http.server
import os
import re

from build_user_html import build_user_html
from credentials_validation import is_email_valid, is_name_valid
from database import con, cursor
from read_user_data import read_user_data


class MyHandler(http.server.BaseHTTPRequestHandler):
    # handle all GET requests
    def do_GET(self):
        # handle deleting User
        path = self.path
        regex = r"^/delete/[0-9]+$"

        if re.fullmatch(regex, path):
            with open("userdata.txt", "r") as f:
                stored_user_data = f.read().strip().split("\n")

            item_id = int(path.split("/")[2])

            if (
                item_id < 0
                or item_id >= len(stored_user_data)
                or stored_user_data == ""
            ):
                self.send_response(404)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                self.wfile.write(b"Index not valid OR Item already deleted")
                return

            stored_user_data.remove(stored_user_data[item_id])

            with open("userdata.txt", "w") as f:
                f.write("\n".join(stored_user_data) + "\n")

            self.send_response(303)
            self.send_header("Location", "/")
            self.end_headers()
            # self.wfile.write(
            #     "<p><strong>User Deleted</strong></p> <a href='/'>Home</a>".encode(
            #         "utf-8"
            #     )
            # )
            return

        # handle dynamic route
        path = self.path
        regex = r"^/edit/[0-9]+$"

        if re.fullmatch(regex, path):
            with open("edit.html", "rb") as f:
                edit_page_data = f.read()

            item_id = int(path.split("/")[2])

            try:
                requested_user = read_user_data(item_id)
                req_user_name = requested_user["name"]
                req_user_email = requested_user["email"]

                edit_page = (
                    edit_page_data.decode("utf-8")
                    .replace("{idnum}", f"Edit item with id: {item_id}")
                    .replace("{id}", str(item_id))
                    .replace("{name}", f"{req_user_name}")
                    .replace("{email}", f"{req_user_email}")
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
                        if not os.path.exists("users.db"):
                            self.send_response(500)
                            self.end_headers()
                            self.wfile.write(b"Not Found")
                            return

                        # with open("userdata.txt", "r") as f:
                        #     users_info = f.read()

                        cursor.execute("SELECT * FROM users")
                        users_info = cursor.fetchall()

                        users_html = build_user_html(users_info)
                        final_page = data.decode("utf-8").replace(
                            "{content}", users_html
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
            except Exception:
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

        if self.path == "/addUser":
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

            # user_data = f"name:{name}|email:{email}\n"

            try:
                # with open("userdata.txt", "a") as f:
                #     f.write(user_data)

                cursor.execute(
                    "INSERT INTO users (name, email) VALUES (?, ?)", (name, email)
                )
                con.commit()

                self.send_response(200)
                # self.send_header("Content-Type", "text/html")
                self.end_headers()
                self.wfile.write(b"<h1>User Added</h1><a href='/'>Home</a>")
                return
            except Exception:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(b"Server Error")
                return

        # handle edit username
        if self.path == "/editUser":
            # get stored data
            with open("userdata.txt", "r") as f:
                stored_user_data = f.read().strip().split("\n")

            # get edited data
            edited_content_length = int(self.headers.get("Content-Length", 0))

            raw_edited_data_body = self.rfile.read(edited_content_length).decode(
                "utf-8"
            )

            from urllib.parse import parse_qs

            parsed = parse_qs(raw_edited_data_body)

            try:
                selected_item_id = int(parsed.get("id", [""])[0])
            except ValueError:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(f"Invalid id: {parsed}".encode("utf-8"))
                return

            selected_item_name = parsed.get("name", [""])[0]
            selected_item_email = parsed.get("email", [""])[0]

            if not is_email_valid(selected_item_email):
                self.send_response(400)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                self.wfile.write(b"Invalid Email")
                return

            if not is_name_valid(selected_item_name):
                self.send_response(400)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                self.wfile.write(b"Invalid Name")
                return

            try:
                if (
                    stored_user_data[selected_item_id]
                    == f"name:{selected_item_name}|email:{selected_item_email}"
                ):
                    self.send_response(200)
                    self.send_header("Content-Type", "text/html")
                    self.end_headers()
                    self.wfile.write(b"<p>No changes made</p> <a href='/'>Home</a>")
                    return

                stored_user_data[selected_item_id] = (
                    f"name:{selected_item_name}|email:{selected_item_email}"
                )

                with open("userdata.txt", "w") as f:
                    f.write("\n".join(stored_user_data) + "\n")

                self.send_response(200)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                self.wfile.write(b"<p>Submitted</p> <a href='/'>Home</a>")
                return
            except IndexError:
                self.send_response(404)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                self.wfile.write(b"<p>User not found</p> <a href ='/'>Home</a>")

        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")

    def log_message(self, format, *args):
        pass


server = http.server.HTTPServer(("", 3000), MyHandler)
print("Server running on port 3000")
server.serve_forever()
