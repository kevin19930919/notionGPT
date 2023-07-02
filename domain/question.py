"""
Module for question
"""
import tiktoken

tokenizer = tiktoken.get_encoding("cl100k_base")

class Question():
    """
    This class represents a question.
    """
    def __init__(self, content):
        self.content = content
        self.tokens = tokenizer.encode(self.content, disallowed_special=())
    def is_token_exceeded(self):
        """
        Check if the content exceed the token limit.
        """
        return len(self.tokens) < 50
    def get_token_number(self):
        """
        Get the token number of the content.
        """
        return len(self.tokens)
    