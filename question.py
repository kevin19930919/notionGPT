import tiktoken

tokenizer = tiktoken.get_encoding("cl100k_base")

class Question():
    def __init__(self, content):
        self.content = content
        self.tokens = tokenizer.encode(self.content, disallowed_special=())
    def is_token_exceeded(self):   
        return len(self.tokens) < 50