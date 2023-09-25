from helpers import format_message_to_forward, user_id_from_message
from langchain.callbacks import get_openai_callback
from redis_functions import save_usage
from pyrogram import Client, filters
from users import update_users
from chain import qa_chain
import os


allowed_users = [
    1331278972,
    49698050,
    616231064,
    229142482,
    1175641280,
    3167087,
    653012968,
    85696477,
    2780467,
    786096786,
    657149280,
]


app = Client(
    "my_account",
    api_id=os.environ["API_ID"],
    api_hash=os.environ["API_HASH"],
    phone_number=os.environ["PHONE_NUMBER"],
)

chains = {}


@app.on_message(filters.private & filters.text & filters.incoming)
def handle_text(client, message):
    if message.from_user.id == 5582454518:
        message, user_id = user_id_from_message(message)
        if not user_id:
            message.reply_text("Пожалуйста предоставьте свой адрес электронной почты")
            return
    elif message.from_user.id in allowed_users:
        user_id = message.from_user.id
    else:
        text = format_message_to_forward(message)
        client.send_message(chat_id=-870308252, text=text)
        return

    try:
        qa = chains[user_id]
    except KeyError:
        qa = qa_chain()
        chains[user_id] = qa

    with get_openai_callback() as cb:
        answer = qa.run(message.text)
        message.reply_text(answer)
        save_usage(cb)


async def main():
    async with app:
        await update_users()


if __name__ == "__main__":
    print("The bot is up and running!")
    app.run(main())
