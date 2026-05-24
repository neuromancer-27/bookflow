def read_user_data(num):
    with open("userdata.txt", "r") as f:
        user_content = f.read()

    if not user_content:
        return print("No content yet")

    split_by_line = user_content.split("\n")

    user_list = []

    for line in split_by_line:
        if not line:
            continue

        user_dict = {}

        split_by_seperator = line.split("|")

        for item in split_by_seperator:
            split_by_colon = item.split(":")

            user_dict[split_by_colon[0]] = split_by_colon[1]

        user_list.append(user_dict)

    if num > len(user_list) - 1:
        raise IndexError("Index could not be found")

    return user_list[num]
