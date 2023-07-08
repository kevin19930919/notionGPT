"""
This module provides functionality for working with configparser
and loading documents from the langchain.document_loaders module.
"""
import configparser
from langchain.document_loaders import NotionDBLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores.faiss import FAISS

from langchain.embeddings import OpenAIEmbeddings

# since we load secret in multiple place, this may not a good practice
# tend to extract the secret loading to a single place
secrets = configparser.ConfigParser()
secrets.read('../../secret.ini')

NOTION_API_KEY = secrets['DEFAULT']['NOTION_API_KEY']
NOTION_ROOT_DB_ID = secrets['DEFAULT']['NOTION_ROOT_DB_ID']
OPENAI_API_KEY = secrets['DEFAULT']['OPENAI_API_KEY']


class NotionDB:
    """
    This class represents a NotionDB.
    """

    def __init__(self, notion_api_token: str, db_id: list[tuple]):
        self.notion_api_token = notion_api_token
        self.db_id = db_id
        self.raw_data = self._get_raw_data()
    def _get_raw_data(self):
        """
        Get the documents of the notion database.

        Returns:
            list[tuple]: The documents of the notion database.
        """
        return NotionDBLoader(
            integration_token=NOTION_API_KEY,
            database_id=NOTION_ROOT_DB_ID,
            request_timeout_sec=30,  # optional
        ).load()    
    def get_vector_data(self):
        """
        Get the vectorstore of the notion database.
        
        Returns:
            Matrix[Vector]: The Matrix of vectorstore of the notion database.
        """
        # Split text
        text_splitter = RecursiveCharacterTextSplitter()
        documents = text_splitter.split_documents(self.raw_data)


        embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
        # # Load Data to vectorstore
        vectorstore = FAISS.from_documents(documents, embeddings)
        return vectorstore
