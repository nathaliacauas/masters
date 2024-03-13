# -*- coding: utf-8 -*-
"""RAG-Masters.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1V_CNtEYbf_Bl6n5WNJ0iwHfEFBU4xsTp
"""

!pip install langchain openai weaviate-client

!pip install pyttsx3
import pyttsx3

!pip install espeak
import espeak

def speak_move(move):
  engine = pyttsx3.init()
  engine.say(move)
  engine.runAndWait()

import os

# Defina a sua chave da API do OpenAI
openai_api_key = ""

# Configure a variável de ambiente OPENAI_API_KEY
os.environ["OPENAI_API_KEY"] = openai_api_key

#loading extra data
import requests
from langchain.document_loaders import TextLoader

#get the data from a repo
url = "https://github.com/nathaliacauas/masters/blob/main/Chef'sHat.txt"
res = requests.get(url)
with open("ChefsHat.txt", "w") as f:
    f.write(res.text)

loader = TextLoader('./ChefsHat.txt')
documents = loader.load()

from langchain.text_splitter import CharacterTextSplitter
text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = text_splitter.split_documents(documents)

!pip install tiktoken

from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Weaviate
import weaviate
from weaviate.embedded import EmbeddedOptions

client = weaviate.Client(
  embedded_options = EmbeddedOptions()
)

vectorstore = Weaviate.from_documents(
    client = client,
    documents = chunks,
    embedding = OpenAIEmbeddings(),
    by_text = False
)

retriever = vectorstore.as_retriever()

from langchain.prompts import ChatPromptTemplate

template = """You are a sports commentator. Use the following pieces of retrieved context to elaborate exciting comments about the player's moves.
Keep the answer small and concise.
Question: {question}
Context: {context}
Answer:
"""
prompt = ChatPromptTemplate.from_template(template)

print(prompt)

from langchain.chat_models import ChatOpenAI
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser

llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)

rag_chain = (
    {"context": retriever,  "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

def new_move (move):
  query = move
  return rag_chain.invoke(query)

answer = new_move("Describe the Sous-chef behaviour in chef's hat")

speak_move(answer)