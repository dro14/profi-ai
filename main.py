import os
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferWindowMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.chains.conversational_retrieval.prompts import PromptTemplate
from pyrogram import Client, filters
from gdown import download


prompt_template = """You are a very polite and helpful assistant named Profi AI which belongs to a company called Profi Training.
Use the following pieces of context to answer the question at the end. Respond in the question's original language.
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

llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)
download(id="1wMzN9Wygpo8Ml3EhnWjPa3bbOWlE6LM5", output="vectordb/chroma.sqlite3")
vectordb = Chroma(embedding_function=OpenAIEmbeddings(), persist_directory="vectordb")


@app.on_message(filters.private & filters.text)
def handle_text(client, message):
    try:
        qa = chains[message.from_user.id]
    except KeyError:
        retriever = vectordb.as_retriever(search_kwargs={"k": 5})
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

    question = message.text
    answer = qa.run(question)
    message.reply_text(answer)


if __name__ == "__main__":
    print("The bot is up and running!")
    app.run()
