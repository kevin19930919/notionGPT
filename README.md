# notionGPT

This project provides a chat bot with a knowledge base built from user-provided Notion data. It utilizes the langchain library and OpenAI's API to process Notion documents, split the text, embed the text, and store it in a vectorstore for efficient access and retrieval.

## Installation
Clone the repository:
```
git clone https://github.com/kevin19930919/notionGPT.git
```

## Usage

###
1. Download data from your Notion page
2. Create your own secret file, file name should be `secret.ini`. Also need value for `OPENAI_API_KEY`, `DATA_RESOURCE_NAME`
3. Ingest data:
```
python3 ingest.py
```
4. run app:
```
python3 main.py
```

