import pickle
from query import QAChain
from langchain.llms import OpenAI
import configparser
import tiktoken


secrets = configparser.ConfigParser()
secrets.read('secret.ini')

OPENAI_API_KEY = secrets['DEFAULT']['OPENAI_API_KEY']

tokenizer = tiktoken.get_encoding("cl100k_base")

if __name__ == "__main__":
    # loading embedding vector data
    with open("vectorstore.pkl", "rb") as f:
        vectorstore = pickle.load(f)
    
    # initial llm
    llm = OpenAI(
        # limit it's diversity of answer
        temperature=0, 
        openai_api_key=OPENAI_API_KEY,
        model_name='gpt-3.5-turbo'
    )
    
    chain = QAChain(vectorstore, llm)
    
    while True:
        print("Question:")
        question = input()
        # TODO: need limitation for token number of input in a proper way
        tokens = tokenizer.encode(question, disallowed_special=())
        if len(tokens) > 50:
            print("Question too long!")
            continue

        result = chain.query(question)
        
        print("Answer:")
        print(result)