import tiktoken

tokenizer = tiktoken.get_encoding("cl100k_base")

class Conversation():
    def __init__(self, content: str, chat_history: list[tuple]):
        self.content = content
        self.chat_history = chat_history


    def is_all_content_exceed(self,):
        # TODO: check if self.content and self.chat_history is exceed token limit
        total_token_num = 0
        for content_tuple in self.chat_history:
            q_token = tokenizer.encode(content_tuple[0], disallowed_special=())
            a_token = tokenizer.encode(content_tuple[1], disallowed_special=())
            total_token_num += len(q_token)
            total_token_num += len(a_token)
            
        current_content_token = tokenizer.encode(self.content, disallowed_special=())
        total_token_num += len(current_content_token)
        
        return total_token_num < 256
            
            

    def end_conversation(self):
        pass