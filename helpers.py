from pyrogram.enums import MessageEntityType
from redis_functions import set_user, get_user
from users import users
import re


def format_message_to_forward(message):
    username = message.from_user.username
    username = "@" + username if username else "отсутствует"

    phone_number = message.from_user.phone_number
    phone_number = phone_number if phone_number else "скрыт"

    text = f"""\
Юзернейм: {username}
Номер телефона: {phone_number}
Сообщение:
{message.text}"""

    return text


def extract_email_via_entities(message):
    for entity in message.entities:
        if entity.type == MessageEntityType.EMAIL:
            begin = entity.offset
            end = entity.offset + entity.length
            email = message.text[begin:end]
            message.text = message.text[:begin] + message.text[end:]
            message.text = message.text.strip()
            return message, email
    return message, None


def user_id_from_message(message):
    name = re.search(r"Вам пишет (.+)\n", message.text).group(1)

    try:
        user_data = users[name]
    except KeyError:
        print("no user found with this name:", name)
        return message, None

    if len(user_data) == 1:
        return message, user_data[0]["id"]
    else:
        user_id = get_user(name)
        if user_id:
            return message, user_id

        print("multiple users found with this name:", name, user_data)

        message, email = extract_email_via_entities(message)
        if email:
            for user in user_data:
                if user["email"] == email:
                    set_user(name, user["id"])
                    return message, user["id"]
        return message, None
