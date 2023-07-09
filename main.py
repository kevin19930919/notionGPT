"""
Main script
"""
import pickle
import configparser
from langchain.llms import OpenAI
from adapter.query import QAChain
from domain.conversation import Conversation

# from adapter.notion.notion_server import NotionDB



secrets = configparser.ConfigParser()
secrets.read('secret.ini')

OPENAI_API_KEY = secrets['DEFAULT']['OPENAI_API_KEY']
NOTION_API_KEY = secrets['DEFAULT']['NOTION_API_KEY']
NOTION_ROOT_DB_ID = secrets['DEFAULT']['NOTION_ROOT_DB_ID']

if __name__ == "__main__":
    # loading embedding vector data
    with open("vectorstore.pkl", "rb") as f:
        vectorstore = pickle.load(f)

    # initial llm
    llm = OpenAI(
        # limit it's diversity of answer
        temperature = 0,
        openai_api_key = OPENAI_API_KEY,
        model_name = 'gpt-3.5-turbo',
        max_tokens = 512,
    )
    chain = QAChain(vectorstore, llm)
    chat_history = []
    while True:
        print("Question:")
        content = input()
        # end a conversation
        if content == "end":
            chat_history = []
            continue
        conv = Conversation(content=content, chat_history=chat_history)
        if not conv.is_all_content_exceed():
            print("conversation too long!")
            continue
        result = chain.query(question=conv.content, chat_history=conv.chat_history)
        chat_history.append((conv.content, result))
        print("Answer:")
        print(result)
