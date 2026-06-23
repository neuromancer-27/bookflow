def build_user_html(userdata, is_admin, current_user_id):
    html_parts = []

    for user in userdata:
        # the route and the button need to be inside the loop bcoz they need to
        # be recreated with the updated id on each iteration of the loop

        id = user[0]
        name = user[1]
        email = user[2]

        edit_button = ""
        delete_button = ""

        if is_admin or id == current_user_id:
            edit_route = f"/edit/{id}"
            edit_button = f"<a href='{edit_route}'><button>edit</button></a>"

        if is_admin:
            delete_route = f"/delete/{id}"
            delete_button = f"<button class='showModal' data-delete-route='{delete_route}'>delete</button>"

        html_parts.append(
            f"<p><strong>{name}</strong> - {email} {edit_button} {delete_button}</p>"
        )

    return "".join(html_parts) or "<p>No users found</p>"
