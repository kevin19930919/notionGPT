from langchain.prompts.prompt import PromptTemplate
from langchain.llms import OpenAI
from langchain.chains import ChatVectorDBChain
from langchain.chains import ConversationalRetrievalChain

_template = """
Given the following conversation and a follow up question, rephrase the follow up question to be a standalone question.
Follow Up Input: {question}
Standalone question:"""
CONDENSE_QUESTION_PROMPT = PromptTemplate.from_template(_template)
print(CONDENSE_QUESTION_PROMPT)

def get_chain(vectorstore):
    llm = OpenAI(
        temperature=0, 
        openai_api_key="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",
        model_name='gpt-3.5-turbo'
    )
    
    print(llm.model_name)
    qa_chain = ConversationalRetrievalChain.from_llm(
        llm,
        vectorstore.as_retriever(),
        condense_question_prompt=CONDENSE_QUESTION_PROMPT,
    )
    return qa_chain