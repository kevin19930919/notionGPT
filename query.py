"""
Module for querying data
"""
from langchain.prompts.prompt import PromptTemplate
from langchain.chains import ConversationalRetrievalChain

TEMPLATE = """
Imagine you're chatting with a human, answer question
{chat_history}
question: {question}
answer:
"""
QUESTION_PROMPT = PromptTemplate(
                    input_variables = ["chat_history", "question"],
                    template = TEMPLATE
                )

class QAChain() :
    """
    A wrapper class for langchain chain module
    """
    def __init__(self, vectorstore, llm) :
        self.vectorstore = vectorstore
        self.llm = llm
        self.chain = self.new_chain(self.vectorstore, self.llm)
    def new_chain(self, vectorstore, llm):
        """_summary_

        Args:
            vectorstore (_type_): _description_
            llm (_type_): _description_

        Returns:
            _type_: _description_
        """
        return ConversationalRetrievalChain.from_llm(
            llm = llm,
            retriever = vectorstore.as_retriever(),
            condense_question_prompt = QUESTION_PROMPT,
        )
    def query(self, question: str, chat_history: list[tuple]) :
        """_summary_
        Args:
            question (str): Text input of a question
            chat_history (list[tuple]): List of questions and their answers
        Returns:
        """
        result = self.chain({"question": question, "chat_history": chat_history})
        return result["answer"]
