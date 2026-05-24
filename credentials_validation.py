import re


def is_email_valid(email):
    regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.fullmatch(regex, email))


def is_name_valid(name):
    regex = r"^[a-zA-Z0-9]+$"
    return bool(re.fullmatch(regex, name))
