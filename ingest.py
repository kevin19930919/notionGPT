from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import NotionDirectoryLoader
from langchain.vectorstores.faiss import FAISS

from langchain.embeddings import OpenAIEmbeddings
import pickle

# Load Data
loader = NotionDirectoryLoader("NotionDB")
raw_documents = loader.load()

# Split text
text_splitter = RecursiveCharacterTextSplitter()
documents = text_splitter.split_documents(raw_documents)


embeddings = OpenAIEmbeddings(openai_api_key="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")
# # Load Data to vectorstore
vectorstore = FAISS.from_documents(documents, embeddings)


# Save vectorstore
with open("vectorstore.pkl", "wb") as f:
    pickle.dump(vectorstore, f)
