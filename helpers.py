from pyrogram.enums import MessageEntityType
from redis_functions import set_user, get_user
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


def extract_email_via_entities(message):
    try:
        for entity in message.entities:
            if entity.type == MessageEntityType.EMAIL:
                email = message.text[entity.offset : entity.offset + entity.length]
                message.text = (
                    message.text[: entity.offset]
                    + message.text[entity.offset + entity.length :]
                )
                message.text = message.text.strip()
                return message, email
    except TypeError:
        return message, None


def user_id_from_message(message):
    name = re.search(r"Вам пишет (.+)\n", message.text).group(1)

    try:
        user = users[name]
    except KeyError:
        print("no user found with this name:", name)
        return message, None

    if len(user) == 1:
        return message, user[0]["id"]
    else:
        user_id = get_user(name)
        if user_id:
            return message, user_id

        print("multiple users found with this name:", name, user)
        message, email = extract_email_via_entities(message)
        if email:
            for u in user:
                if u["email"] == email:
                    set_user(name, u["id"])
                    return message, u["id"]
        return message, None
