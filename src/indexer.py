import os
import io
import requests
from bs4 import BeautifulSoup
from markdownify import markdownify
from pypdf import PdfReader
from urllib.parse import urljoin

BASE_URL = "https://www.aefligen.ch"
SITEMAP_URL = "https://www.aefligen.ch/de/sitemap/"
OUTPUT_DIR = "aefligen_markdown"

def pdf_to_markdown(pdf_bytes):
    text = ""
    with io.BytesIO(pdf_bytes) as f:
        reader = PdfReader(f)
        for page in reader.pages:
            text += page.extract_text() or ""
    return text

def get_sitemap_links():
    r = requests.get(SITEMAP_URL, timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")
    return [urljoin(BASE_URL, a["href"]) for a in soup.find_all("a", href=True)]

def crawl():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    for link in get_sitemap_links():
        try:
            resp = requests.get(link, timeout=10)
            soup = BeautifulSoup(resp.text, "html.parser")

            # Remove header, footer, and the element with id="sidebar"
            for selector in ["header", "footer", "#sidebar"]:
                for elem in soup.select(selector):
                    elem.decompose()

            md_content = markdownify(str(soup))
            base_name = link.replace(BASE_URL, "").strip("/").replace("/", "_") or "index"
            with open(os.path.join(OUTPUT_DIR, base_name + ".md"), "w", encoding="utf-8") as f:
                f.write(md_content)

            # Convert linked PDFs to Markdown
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

if __name__ == "__main__":
    crawl()