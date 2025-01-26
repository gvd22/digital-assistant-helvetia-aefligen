import os
from dotenv import load_dotenv
import gradio as gr
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain_pinecone import PineconeVectorStore
from langchain.chains import RetrievalQA

load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
llm_model = "gpt-4o"
PINECONE_INDEX = "helvetia-aefligen-dev"

# Initialize embeddings + vector store
embedding_model = "text-embedding-3-large"
embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY, model=embedding_model)
vectorstore = PineconeVectorStore(index_name=PINECONE_INDEX, embedding=embeddings)

# Build LLM
llm = ChatOpenAI(
    openai_api_key=OPENAI_API_KEY,
    model_name=llm_model,
)

qa = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=vectorstore.as_retriever()
)

def qa_manager(query):
    """Single function Gradio calls to get the answer from the chain."""
    return qa.invoke(query)

if __name__ == '__main__':
    qa_app = gr.Interface(
        fn=qa_manager,
        inputs=[gr.Textbox(label="What are you looking for?")],
        outputs=[gr.Textbox(label="Answer")],
        title="Aefligen t",
        description="Ask questions about Aefligen's website content."
    )
    qa_app.launch()