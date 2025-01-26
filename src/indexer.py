# --- Imports ---
import os
import io
import time
import requests
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from markdownify import markdownify
from pypdf import PdfReader
from urllib.parse import urljoin
from uuid import uuid4

# Pinecone + Embeddings
from pinecone import Pinecone, ServerlessSpec
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore

# LangChain core
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

# --- Load environment variables from .env ---
load_dotenv()
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# --- Pinecone index setup ---
pc = Pinecone(api_key=PINECONE_API_KEY)
index_name = "helvetia-aefligen-dev"
existing_indexes = [idx["name"] for idx in pc.list_indexes()]
if index_name not in existing_indexes:
    pc.create_index(
        name=index_name,
        dimension=3072,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1"),
    )
    while not pc.describe_index(index_name).status["ready"]:
        time.sleep(1)
index = pc.Index(index_name)

# --- Embeddings & VectorStore ---
embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
vector_store = PineconeVectorStore(index=index, embedding=embeddings)

# --- Crawler configuration ---
BASE_URL = "https://www.aefligen.ch"
SITEMAP_URL = "https://www.aefligen.ch/de/sitemap/"
OUTPUT_DIR = "../aefligen_markdown"

def pdf_to_markdown(pdf_bytes):
    text = ""
    reader = PdfReader(io.BytesIO(pdf_bytes))
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

def get_sitemap_links():
    resp = requests.get(SITEMAP_URL, timeout=10)
    soup = BeautifulSoup(resp.text, "html.parser")
    return [urljoin(BASE_URL, a["href"]) for a in soup.find_all("a", href=True)]

def crawl():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    for link in get_sitemap_links():
        try:
            r = requests.get(link, timeout=10)
            soup = BeautifulSoup(r.text, "html.parser")
            for selector in ["header", "footer", "#sidebar"]:
                for elem in soup.select(selector):
                    elem.decompose()

            md_content = markdownify(str(soup))
            base_name = link.replace(BASE_URL, "").strip("/").replace("/", "_") or "index"
            with open(os.path.join(OUTPUT_DIR, base_name + ".md"), "w", encoding="utf-8") as f:
                f.write(md_content)

            # PDFs -> .md
            for a in soup.find_all("a", href=True):
                if a["href"].lower().endswith(".pdf"):
                    pdf_url = urljoin(link, a["href"])
                    pdf_resp = requests.get(pdf_url, timeout=10)
                    if pdf_resp.status_code == 200:
                        pdf_md = pdf_to_markdown(pdf_resp.content)
                        pdf_name = os.path.splitext(pdf_url.split("/")[-1])[0] + ".md"
                        with open(os.path.join(OUTPUT_DIR, pdf_name), "w", encoding="utf-8") as f:
                            f.write(pdf_md)
        except Exception as e:
            print(f"Skipping {link} => {e}")

def index_markdown_files():
    # We'll chunk each .md file to keep documents under metadata limits
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=3000,   # Adjust chunk size to your needs
        chunk_overlap=200  # Overlap between chunks
    )

    all_docs = []
    for fname in os.listdir(OUTPUT_DIR):
        if fname.endswith(".md"):
            with open(os.path.join(OUTPUT_DIR, fname), "r", encoding="utf-8") as f:
                text = f.read()

            # Split into smaller text chunks
            for chunk in splitter.split_text(text):
                doc = Document(page_content=chunk, metadata={"filename": fname})
                all_docs.append(doc)

    # Add to Pinecone
    vector_store.add_documents(all_docs, ids=[str(uuid4()) for _ in all_docs])

if __name__ == "__main__":
    #crawl()
    index_markdown_files()