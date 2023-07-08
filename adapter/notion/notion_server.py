"""
This module provides functionality for working with configparser
and loading documents from the langchain.document_loaders module.
"""
import configparser
from langchain.document_loaders import NotionDBLoader

# since we load secret in multiple place, this may not a good practice
# tend to extract the secret loading to a single place
secrets = configparser.ConfigParser()
secrets.read('../../secret.ini')

NOTION_API_KEY = secrets['DEFAULT']['NOTION_API_KEY']
NOTION_ROOT_DB_ID = secrets['DEFAULT']['NOTION_ROOT_DB_ID']


class NotionDB:
    """
    This class represents a NotionDB.
    """

    def __init__(self, notion_api_token: str, db_id: list[tuple]):
        self.notion_api_token = notion_api_token
        self.db_id = db_id
        self.loader = NotionDBLoader(
            integration_token=NOTION_API_KEY,
            database_id=NOTION_ROOT_DB_ID,
            request_timeout_sec=30,  # optional
        )   
    def get_docs(self):
        """
        Get the documents of the notion database.

        Returns:
            list[tuple]: The documents of the notion database.
        """
        return self.loader.load()
