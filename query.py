from langchain.prompts.prompt import PromptTemplate
from langchain.chains import ConversationalRetrievalChain

_template = """
Imagine you're chatting with a customer, answer question
question: {question}
"""
CONDENSE_QUESTION_PROMPT = PromptTemplate.from_template(_template)

class QAChain() :
    def __init__(self, vectorstore, llm) :
        self.vectorstore = vectorstore
        self.llm = llm
        self.chain = self.new_chain(self.vectorstore, self.llm)
    
    def new_chain(self, vectorstore, llm):
        return ConversationalRetrievalChain.from_llm(
            llm,
            vectorstore.as_retriever(),
            condense_question_prompt=CONDENSE_QUESTION_PROMPT,
        )
    
    def query(self, question) :
        # TODO: add history of question (TBD)
        result = self.chain({"question": question, "chat_history": []})
        return result["answer"]
