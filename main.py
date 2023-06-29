import pickle
from query import QAChain
from langchain.llms import OpenAI
import configparser

secrets = configparser.ConfigParser()
secrets.read('secret.ini')

OPENAI_API_KEY = secrets['DEFAULT']['OPENAI_API_KEY']


if __name__ == "__main__":
    # loading embedding vector data
    with open("vectorstore.pkl", "rb") as f:
        vectorstore = pickle.load(f)
    
    # initial llm
    llm = OpenAI(
        temperature=0, 
        openai_api_key=OPENAI_API_KEY,
        model_name='gpt-3.5-turbo'
    )
    
    chain = QAChain(vectorstore, llm)
    
    print("Chat with your docs!")
    while True:
        print("Question:")
        question = input()
        
        # TODO: need limitation for token number of input.
        result = chain.query(question)
        
        print("Answer:")
        print(result)