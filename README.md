# notionGPT

This project provides a chatbot with a knowledge base built from user-provided Notion data. It utilizes the langchain library and OpenAI's API to process Notion documents, split the text, embed the text, and store it in a vectorstore for efficient access and retrieval.

## Installation

Clone the repository:

```
git clone https://github.com/kevin19930919/notionGPT.git
```

## How to Start

Follow the steps below to use notionGPT:

1. Start by downloading the data from your desired Notion page. [ref](https://www.notion.so/help/export-your-content)
2. Next, create a file called `secret.ini`. This file should include your `OPENAI_API_KEY` and the `DATA_RESOURCE_NAME`.
   Looks like this:
   ![Alt text](/material/img/img1.png)
3. Download all required Python packages

```
pip3 install -r requirement.txt
``` 

4. Once you have the data and secrets ready, ingest the data you provide:

```makefile
make ingest-data
```

5. Run app:

```makefile
make chat
```
or 
```python
python3 main.py
```

## Note

Every chat will contain the history content(previous questions and answers), until you input keyword "end".
Entering "end" will clear history data, and start with a new conversation.
