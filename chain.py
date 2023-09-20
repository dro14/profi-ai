from langchain.memory import ConversationBufferWindowMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.vectorstores import Chroma
from gdown import download
from prompt import prompt
import time


download(
    id="1O1emN8RMJ9CtYur0LwmuaGwGFQZ_Q55s",
    output="vectordb/dbd9c861-7cb7-485f-9698-89f8ea05acf6/data_level0.bin",
    quiet=True,
)

time.sleep(5)

download(
    id="1JJXubJkHMyDyZSj9FPkLQTnxJPl6MLAd",
    output="vectordb/chroma.sqlite3",
    quiet=True,
)

vectordb = Chroma(
    embedding_function=OpenAIEmbeddings(),
    persist_directory="vectordb",
)

retriever = vectordb.as_retriever(
    search_kwargs={"k": 5},
)

llm = ChatOpenAI(
    model_name="gpt-4",
    temperature=0,
)


def qa_chain():
    memory = ConversationBufferWindowMemory(
        k=2,
        memory_key="chat_history",
        return_messages=True,
    )

    return ConversationalRetrievalChain.from_llm(
        llm,
        retriever,
        verbose=True,
        combine_docs_chain_kwargs={"prompt": prompt},
        memory=memory,
    )
