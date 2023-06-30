from langchain.prompts.prompt import PromptTemplate
from langchain.chains import ConversationalRetrievalChain

_template = """
Imagine you're chatting with a human, answer question
{chat_history}
question: {question}
answer:
"""
QUESTION_PROMPT = PromptTemplate(input_variables = ["chat_history", "question"], template = _template)

class QAChain() :
    def __init__(self, vectorstore, llm) :
        self.vectorstore = vectorstore
        self.llm = llm
        self.chain = self.new_chain(self.vectorstore, self.llm)
    
    def new_chain(self, vectorstore, llm):
        return ConversationalRetrievalChain.from_llm(
            llm = llm,
            retriever = vectorstore.as_retriever(),
            condense_question_prompt = QUESTION_PROMPT,
        )
    
    def query(self, question, chat_history) :
        # TODO: add history of question (TBD)
        result = self.chain({"question": question, "chat_history": chat_history})
        return result["answer"]
