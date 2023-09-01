import os
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferWindowMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.chains.conversational_retrieval.prompts import PromptTemplate
from pyrogram import Client, filters
from gdown import download, download_folder

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

llm = ChatOpenAI(model_name="gpt-4", temperature=0)
download(id="1h2Txpgp4bL6BEAV59Ch2lbJzjIlz0cPv", quiet=True)
download_folder(id="1FYaUhsRc5Ck8RHO1DRxKSd4aJn1qFOKA", quiet=True)
vectordb = Chroma(embedding_function=OpenAIEmbeddings(), persist_directory="vectordb")
retriever = vectordb.as_retriever(search_kwargs={"k": 3})


@app.on_message(
    filters.private & filters.text & filters.incoming & filters.user(allowed_users)
)
def handle_text(client, message):
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

    question = message.text
    answer = qa.run(question)
    message.reply_text(text=answer, reply_to_message_id=message.id)


if __name__ == "__main__":
    print("The bot is up and running!")
    app.run()
