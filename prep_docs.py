import os
import sys
import time
import csv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import PyPDFLoader
from langchain.document_loaders.csv_loader import CSVLoader
from langchain.vectorstores.base import Document
from langchain.vectorstores import Chroma
from langchain.embeddings.openai import OpenAIEmbeddings


def remove_newlines(content):
    content = content.replace("\n", " ")
    content = content.replace("\\n", " ")
    content = content.replace("  ", " ")
    content = content.replace("  ", " ")
    return content


text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=100,
    separators=["\n\n", "\n", r"(?<=\.)", " ", ""],
)


def load_pdf(file):
    pages = PyPDFLoader(file).load()
    file_content = ""
    for page in pages:
        file_content += remove_newlines(page.page_content.strip()) + " "
    document = Document(page_content=file_content, metadata={"source": file})
    return text_splitter.split_documents([document])


def load_csv(file):
    f = open(file)
    rows = csv.reader(f)
    cleaned_rows = []
    for row in rows:
        add = False
        for item in row:
            if item.strip():
                add = True
        if add:
            for i in range(len(row)):
                row[i] = row[i].strip()
            cleaned_rows.append(row)
    f.close()

    f = open(file, "w")
    writer = csv.writer(f)
    writer.writerows(cleaned_rows)
    f.close()

    return CSVLoader(file).load()


vectordb = Chroma(embedding_function=OpenAIEmbeddings(), persist_directory="chroma")

for category in os.listdir("../data"):
    if category.startswith("."):
        continue
    directory = "../data/" + category
    for file_name in os.listdir(directory):
        if file_name.startswith("."):
            continue
        file_path = directory + "/" + file_name
        if file_name.endswith(".pdf"):
            docs = load_pdf(file_path)
        elif file_name.endswith(".csv"):
            docs = load_csv(file_path)
        else:
            sys.exit(f"unknown file: {file_path}")
        for i in range(len(docs)):
            docs[i].metadata["category"] = category
        vectordb.add_documents(docs)
        time.sleep(10)

vectordb.persist()
