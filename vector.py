import os
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

# Define the folder containing your .txt files
FOLDER_PATH = "Data"

# Load all .txt files from the folder
documents = []
for filename in os.listdir(FOLDER_PATH):
    if filename.endswith(".txt"):
        with open(os.path.join(FOLDER_PATH, filename), "r", encoding="utf-8") as file:
            text = file.read()
            documents.append(Document(page_content=text, metadata={"source": filename}))

# Create embeddings
embeddings = OllamaEmbeddings(model="mxbai-embed-large")

# Create vector store
vectorstore = Chroma.from_documents(documents, embedding=embeddings, persist_directory="chroma_store")

# Persist the vector store to disk
vectorstore.persist()

print(f"✅ Vector store created with {len(documents)} documents.")