"""
This script is used to embedding your notion data, and store as file.
"""
import pickle
import configparser
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import DirectoryLoader
from langchain.vectorstores.faiss import FAISS

from langchain.embeddings import OpenAIEmbeddings


secrets = configparser.ConfigParser()
secrets.read('../secret.ini')

OPENAI_API_KEY = secrets['DEFAULT']['OPENAI_API_KEY']
DATA_RESOURCE_NAME = secrets['DEFAULT']['DATA_RESOURCE_NAME']

# Load Data
loader  = DirectoryLoader('../data', glob='*.pdf')
raw_documents = loader.load()

# Split text
text_splitter = RecursiveCharacterTextSplitter()
documents = text_splitter.split_documents(raw_documents)


embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
# # Load Data to vectorstore
vectorstore = FAISS.from_documents(documents, embeddings)


# Save vectorstore
with open("../vectorstore_unstruct.pkl", "wb") as f:
    pickle.dump(vectorstore, f)
    