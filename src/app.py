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

# Global variable to store chat history
chat_history = []

def qa_manager(query):
    """Single function Gradio calls to get the answer from the chain."""
    response = qa.invoke(query)
    chat_history.append({"query": query, "response": response})
    return response

def get_chat_history():
    """Function to return the chat history."""
    return "\n".join([f"User: {entry['query']}\nBot: {entry['response']}" for entry in chat_history])

def clear_chat_history():
    """Clear the stored chat history."""
    chat_history.clear()
    return ""

if __name__ == '__main__':
    with gr.Blocks() as qa_app:
        with gr.Row():
            with gr.Column():
                query_input = gr.Textbox(label="What are you looking for?")
                response_output = gr.Textbox(label="Answer")
                query_button = gr.Button("Submit")
                clear_button = gr.Button("Clear History")
            with gr.Column():
                chat_history_output = gr.Textbox(label="Chat History", interactive=False)

        query_button.click(fn=qa_manager, inputs=query_input, outputs=response_output)
        query_button.click(fn=get_chat_history, inputs=None, outputs=chat_history_output)
        clear_button.click(fn=clear_chat_history, inputs=None, outputs=chat_history_output)
        
    qa_app.launch()
