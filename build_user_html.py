def build_user_html(userdata):
    html_parts = []

    for id, user in enumerate(userdata):
        # the route and the button need to be inside the loop bcoz they need to
        # be recreated with the updated id on each iteration of the loop
        edit_route = f"/edit/{id}"
        edit_button = f"""<a href='{edit_route}'><button>edit</button></a>"""

        delete_route = f"/delete/{id}"
        delete_button = f"""<button class = 'showModal' data-delete-route = '{delete_route}'>delete</button>"""

        name = user[0]
        email = user[1]

        html_parts.append(
            f"<p><strong>{name}</strong> - {email} {edit_button} {delete_button}</p>"
        )

    return "".join(html_parts) or "<p>No users found</p>"
