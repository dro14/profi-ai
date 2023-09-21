from users import users
import re


def format_message_to_forward(message):
    username = (
        "@" + message.from_user.username
        if message.from_user.username
        else "отсутствует"
    )

    phone_number = (
        message.from_user.phone_number if message.from_user.phone_number else "скрыт"
    )

    return f"""\
Юзернейм: {username}
Номер телефона: {phone_number}
Сообщение:
{message.text}"""


def user_id_from_message(message):
    result = re.search(r"Вам пишет (.+)\n", message.text)
    name = result.group(1)
    try:
        user = users[name]
    except KeyError:
        print("no user found with this name:", name)
    else:
        if len(user) == 1:
            return user[0]["id"]
        else:
            print("multiple users found with this name:", name, user)
