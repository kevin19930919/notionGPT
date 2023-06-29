import pickle
from query import QAChain
from langchain.llms import OpenAI


if __name__ == "__main__":
    with open("vectorstore.pkl", "rb") as f:
        vectorstore = pickle.load(f)
    
    # initial llm
    llm = OpenAI(
        temperature=0, 
        openai_api_key="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",
        model_name='gpt-3.5-turbo'
    )
    
    chain = QAChain(vectorstore, llm)
    
    chat_history = []
    print("Chat with your docs!")
    while True:
        print("Question:")
        question = input()
        result = chain.query(question)
        # chat_history.append((question, result["answer"]))
        print("AI:")
        print(result["answer"])