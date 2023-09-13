import os
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferWindowMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.chains.conversational_retrieval.prompts import PromptTemplate
from langchain.callbacks import get_openai_callback
from pyrogram import Client, filters
from gdown import download, download_folder
from redis import Redis

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

prompt_template = """You are a very polite and helpful assistant named Аймышь which belongs to a company called Profi Training.
Use the following pieces of context to answer the question at the end. Respond in the question's original language, which can be either Russian or Uzbek.
If you don't know the answer, just say that you don't know, don't try to make up an answer. 
Greet back if it is the first message of the user.

{context}

{chat_history}
Human: {question}
Assistant:"""

prompt = PromptTemplate(
    template=prompt_template,
    input_variables=["context", "chat_history", "question"],
)

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
download_folder(id="1FYaUhsRc5Ck8RHO1DRxKSd4aJn1qFOKA", quiet=True)
vectordb = Chroma(embedding_function=OpenAIEmbeddings(), persist_directory="vectordb")
retriever = vectordb.as_retriever(search_kwargs={"k": 3})


@app.on_message(filters.private & filters.text & filters.incoming)
def handle_text(client, message):
    if message.from_user.id not in allowed_users:
        text = f"""Юзернейм: {message.from_user.username}
        Номер телефона: {message.from_user.phone_number}
        Сообщение: {message.text}"""
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
