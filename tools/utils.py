import streamlit as st

from langchain_chroma import Chroma
from langchain.callbacks.base import BaseCallbackHandler
from langchain_community.embeddings.openai import OpenAIEmbeddings


@st.cache_resource(ttl='1h')
def get_retriever():
    embeddings = OpenAIEmbeddings()
    vectordb = Chroma(persist_directory='db2', embedding_function=embeddings)

    retriever = vectordb.as_retriever(search_type='mmr')

    return retriever

class StreamHandler(BaseCallbackHandler):
    def __init__(self, container: st.delta_generator.DeltaGenerator, initial_text: str = ''):
        self.container = container
        self.text = initial_text

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        self.text += token
        self.container.markdown(self.text)