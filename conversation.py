"""
This module contains the Conversation class.
"""
import tiktoken

tokenizer = tiktoken.get_encoding("cl100k_base")

class Conversation:
    """
    This class represents a conversation.
   
    Attributes:
        content (str): The content of the conversation.
        chat_history (list[tuple]): The chat history of the conversation.
    """

    def __init__(self, content: str, chat_history: list[tuple]):
        self.content = content
        self.chat_history = chat_history
        self.token_number = self.get_token_number()

    def get_token_number(self):
        """
        Get the token number of the content and chat history.

        Returns:
            int: The token number of the content and chat history.
        """
        total_token_num = 0

        for content_tuple in self.chat_history:
            q_token = tokenizer.encode(content_tuple[0], disallowed_special=())
            a_token = tokenizer.encode(content_tuple[1], disallowed_special=())
            total_token_num += len(q_token)
            total_token_num += len(a_token)
        current_content_token = tokenizer.encode(self.content, disallowed_special=())
        total_token_num += len(current_content_token)
        return total_token_num
    def is_all_content_exceed(self):
        """
        Check if the content and chat history exceed the token limit.

        Returns:
            bool: True if the content and chat history exceed the token limit, False otherwise.
        """
        return self.token_number < 1024
    