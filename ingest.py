"""
This script is used to embedding your notion data, and store as file.
"""
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import NotionDirectoryLoader
from langchain.vectorstores.faiss import FAISS

from langchain.embeddings import OpenAIEmbeddings
import pickle
import configparser

secrets = configparser.ConfigParser()
secrets.read('secret.ini')

OPENAI_API_KEY = secrets['DEFAULT']['OPENAI_API_KEY']
DATA_RESOURCE_NAME = secrets['DEFAULT']['DATA_RESOURCE_NAME']

# Load Data
loader = NotionDirectoryLoader(DATA_RESOURCE_NAME)
raw_documents = loader.load()

# Split text
text_splitter = RecursiveCharacterTextSplitter()
documents = text_splitter.split_documents(raw_documents)


embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
# # Load Data to vectorstore
vectorstore = FAISS.from_documents(documents, embeddings)


# Save vectorstore
with open("vectorstore.pkl", "wb") as f:
    pickle.dump(vectorstore, f)

