def format_message_to_forward(message):
    username = (
        "@" + message.from_user.username
        if message.from_user.username
        else "отсутствует"
    )

    phone_number = (
        message.from_user.phone_number if message.from_user.phone_number else "скрыт"
    )

    return f"""Юзернейм: {username}
    Номер телефона: {phone_number}
    Сообщение:
    {message.text}"""
