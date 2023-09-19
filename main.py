import os
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferWindowMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.callbacks import get_openai_callback
from pyrogram import Client, filters
from gdown import download, download_folder
from redis import Redis
from prompt import prompt

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


chains = {}
app = Client(
    "my_account",
    api_id=os.environ["API_ID"],
    api_hash=os.environ["API_HASH"],
    phone_number=os.environ["PHONE_NUMBER"],
)

redis = Redis(
    host=os.environ["REDIS_HOST"],
    port=os.environ["REDIS_PORT"],
    password=os.environ["REDIS_PASSWORD"],
)

llm = ChatOpenAI(model_name="gpt-4", temperature=0)
download(id="1h2Txpgp4bL6BEAV59Ch2lbJzjIlz0cPv", quiet=True)
download_folder(id="1BTGO36lB-aSJRk-Ei9dAilXcJGlBIQm0", quiet=True)
vectordb = Chroma(embedding_function=OpenAIEmbeddings(), persist_directory="vectordb")
retriever = vectordb.as_retriever(search_kwargs={"k": 5})


@app.on_message(filters.private & filters.text & filters.incoming)
def handle_text(client, message):
    if message.from_user.id not in allowed_users:
        username = (
            "@" + message.from_user.username
            if message.from_user.username
            else "отсутствует"
        )
        phone_number = (
            message.from_user.phone_number
            if message.from_user.phone_number
            else "скрыт"
        )
        text = f"""Юзернейм: {username}
Номер телефона: {phone_number}
Сообщение:
{message.text}"""
        client.send_message(chat_id=-870308252, text=text)
        return

    try:
        qa = chains[message.from_user.id]
    except KeyError:
        memory = ConversationBufferWindowMemory(
            k=2,
            memory_key="chat_history",
            return_messages=True,
        )

        qa = ConversationalRetrievalChain.from_llm(
            llm,
            retriever,
            verbose=True,
            combine_docs_chain_kwargs={"prompt": prompt},
            memory=memory,
        )
        chains[message.from_user.id] = qa

    with get_openai_callback() as cb:
        question = message.text
        answer = qa.run(question)
        message.reply_text(text=answer, reply_to_message_id=message.id)
        usage = redis.get("Profi_usage")
        usage = float(usage) + cb.total_cost if usage else cb.total_cost
        redis.set("Profi_usage", usage)


if __name__ == "__main__":
    print("The bot is up and running!")
    app.run()
