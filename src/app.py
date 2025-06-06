import os
from dotenv import load_dotenv
import gradio as gr
from langchain_mistralai import ChatMistralAI, MistralAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain.chains import RetrievalQA

load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
if not MISTRAL_API_KEY:
    raise RuntimeError("Missing MISTRAL_API_KEY")
if not PINECONE_API_KEY:
    raise RuntimeError("Missing PINECONE_API_KEY")
llm_model = "mistral-large-latest"
PINECONE_INDEX = "helvetia-aefligen-dev"

# Initialize embeddings + vector store
embedding_model = "mistral-embed"
embeddings = MistralAIEmbeddings(api_key=MISTRAL_API_KEY, model=embedding_model)
vectorstore = PineconeVectorStore(index_name=PINECONE_INDEX, embedding=embeddings)

# Build LLM
llm = ChatMistralAI(
    api_key=MISTRAL_API_KEY,
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

if __name__ == '__main__':
    with gr.Blocks() as qa_app:
        with gr.Row():
            with gr.Column():
                query_input = gr.Textbox(label="What are you looking for?")
                response_output = gr.Textbox(label="Answer")
                query_button = gr.Button("Submit")
            with gr.Column():
                chat_history_output = gr.Textbox(label="Chat History", interactive=False)
        
        query_button.click(fn=qa_manager, inputs=query_input, outputs=response_output)
        query_button.click(fn=get_chat_history, inputs=None, outputs=chat_history_output)
        
    qa_app.launch()
