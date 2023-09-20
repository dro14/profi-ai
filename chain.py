from langchain.memory import ConversationBufferWindowMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.vectorstores import Chroma
from gdown import download_folder
from prompt import prompt


download_folder(
    id="1BTGO36lB-aSJRk-Ei9dAilXcJGlBIQm0",
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

