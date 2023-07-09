"""
This module provides functionality for working with configparser
and loading documents from the langchain.document_loaders module.
"""
from langchain.document_loaders import NotionDBLoader
from langchain.vectorstores.faiss import FAISS

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
        print("start querying database data...")
        raw_data = NotionDBLoader(
            integration_token = self.notion_api_token,
            database_id = self.db_id,
            request_timeout_sec = 30,  # optional
        ).load()
        print("finish querying database data...")
        return raw_data
    def get_vector_data(self, embeddings):
        """
        Get the vectorstore of the notion database.
        
        Returns:
            Matrix[Vector]: The Matrix of vectorstore of the notion database.
        """
        # # Load Data to vectorstore
        vectorstore = FAISS.from_documents(self.raw_data, embeddings)
        return vectorstore
