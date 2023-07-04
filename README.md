# notionGPT

This project provides a chat bot with a knowledge base built from user-provided Notion data. It utilizes the langchain library and OpenAI's API to process Notion documents, split the text, embed the text, and store it in a vectorstore for efficient access and retrieval.

## Installation

Clone the repository:

```
git clone https://github.com/kevin19930919/notionGPT.git
```

## How to Use

Follow the steps below to use notionGPT:

1. Start by downloading the data from your desired Notion page
2. Next, create your `secret.ini` file. This file should include your `OPENAI_API_KEY` and the `DATA_RESOURCE_NAME`
3. Once you have the data and secrets ready, ingest the data into the system using the following command:

```python
python3 ingest.py
```

4. Run app:

```python
python3 main.py
```
