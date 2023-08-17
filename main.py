import os
import subprocess
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferWindowMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.chains.conversational_retrieval.prompts import PromptTemplate
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

subprocess.run(
    [
        "gdown",
        "1RJXnuu-2th0-KnffLyqE0FctfEN-uVx3",
        "--output",
        "./vectordb/chroma.sqlite3",
    ]
)


prompt_prefix = """You are a very polite and helpful assistant of a company called Profi Training.
Use the following pieces of context to answer the question at the end. Respond in {}.
If you don't know the answer, just say that you don't know, don't try to make up an answer. 
Greet back if the user greets you.
"""

prompt_suffix = """
{context}

{chat_history}
Human: {question}
Assistant:"""

prompt = {
    "ru": PromptTemplate(
        template=prompt_prefix.format("Russian") + prompt_suffix,
        input_variables=["context", "chat_history", "question"],
    ),
    "uz_lat": PromptTemplate(
        template=prompt_prefix.format("Uzbek (Latin)") + prompt_suffix,
        input_variables=["context", "chat_history", "question"],
    ),
    "uz_cyr": PromptTemplate(
        template=prompt_prefix.format("Uzbek (Cyrillic)") + prompt_suffix,
        input_variables=["context", "chat_history", "question"],
    ),
}


chains = {}
app = Client(
    "my_account",
    api_id=os.environ["API_ID"],
    api_hash=os.environ["API_HASH"],
    bot_token=os.environ["BOT_TOKEN"],
)


@app.on_message(filters.private & filters.text)
def handle_text(client, message):
    if message.text == "/start":
        start(message)
    else:
        try:
            qa = chains[message.from_user.id]
        except KeyError:
            start(message)
        else:
            question = message.text
            answer = qa.run(question)
            message.reply_text(answer)


language_text = """Выберите свой язык:

O'z tilingizni tanlang:

Уз тилингизни танланг:"""

language_keyboard = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton("🇷🇺 Русский 🇷🇺", callback_data="ru")],
        [InlineKeyboardButton("🇺🇿 O'zbekcha 🇺🇿", callback_data="uz_lat")],
        [InlineKeyboardButton("🇺🇿 Узбекча 🇺🇿", callback_data="uz_cyr")],
    ]
)


# Adding three inline buttons
def start(message):
    message.reply_text(text=language_text, reply_markup=language_keyboard)


llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)
vectordb = Chroma(embedding_function=OpenAIEmbeddings(), persist_directory="vectordb")


# Processing callbacks from the buttons
@app.on_callback_query()
def handle_callback(client, query: CallbackQuery):
    if query.data.startswith(("ru", "uz_lat", "uz_cyr")):
        retriever = vectordb.as_retriever(
            search_kwargs={
                "k": 5,
                "filter": {"category": query.data},
            }
        )

        memory = ConversationBufferWindowMemory(
            k=2,
            memory_key="chat_history",
            return_messages=True,
        )

        chains[query.from_user.id] = ConversationalRetrievalChain.from_llm(
            llm,
            retriever=retriever,
            memory=memory,
            combine_docs_chain_kwargs={"prompt": prompt[query.data]},
            verbose=True,
        )

        match query.data:
            case "ru":
                query.answer("Выбран русский язык")
                client.send_message(query.from_user.id, "Выбран русский язык")
            case "uz_lat":
                query.answer("O'zbek tili tanlandi")
                client.send_message(query.from_user.id, "O'zbek tili tanlandi")
            case "uz_cyr":
                query.answer("Узбек тили танланди")
                client.send_message(query.from_user.id, "Узбек тили танланди")
    else:
        query.answer("Нажата неверная кнопка")
        client.send_message(query.from_user.id, "Нажата неверная кнопка")


if __name__ == "__main__":
    print("The bot is up and running!")
    app.run()
