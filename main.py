from langchain.callbacks import get_openai_callback
from helpers import format_message_to_forward
from redis_functions import save_usage
from pyrogram import Client, filters
from gdown import download
from chain import qa_chain
import os


allowed_users = [
    5582454518,
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


download(
    id="1h2Txpgp4bL6BEAV59Ch2lbJzjIlz0cPv",
    output="my_account.session",
    quiet=True,
)

app = Client(
    "my_account",
    api_id=os.environ["API_ID"],
    api_hash=os.environ["API_HASH"],
    phone_number=os.environ["PHONE_NUMBER"],
)

chains = {}


@app.on_message(filters.private & filters.text & filters.incoming)
def handle_text(client, message):
    if message.from_user.id in allowed_users:
        try:
            qa = chains[message.from_user.id]
        except KeyError:
            qa = qa_chain()
            chains[message.from_user.id] = qa

        with get_openai_callback() as cb:
            answer = qa.run(message.text)
            message.reply_text(text=answer, reply_to_message_id=message.id)
            save_usage(cb)
    else:
        text = format_message_to_forward(message)
        client.send_message(chat_id=-870308252, text=text)


if __name__ == "__main__":
    print("The bot is up and running!")
    app.run()
