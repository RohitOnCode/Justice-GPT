import pathlib, requests
from pypdf import PdfReader
from pydantic import BaseModel, Field
from langchain.text_splitter import RecursiveCharacterTextSplitter

IPC_URLS = [
    "https://www.indiacode.nic.in/bitstream/123456789/4219/1/THE-INDIAN-PENAL-CODE-1860.pdf",
    "https://www.iitk.ac.in/wc/data/IPC_186045.pdf",
    "https://thc.nic.in/Central%20Governmental%20Acts/Indian%20Penal%20Code%2C%201860%20.pdf",
]

class IPCSection(BaseModel):
    page: int = Field(...)
    text: str = Field(...)

def download_pdf(dest: pathlib.Path) -> pathlib.Path:
    if dest.exists():
        return dest
    for url in IPC_URLS:
        try:
            print(f"⏬  Trying {url} …")
            r = requests.get(url, timeout=30)
            r.raise_for_status()
            dest.write_bytes(r.content)
            print("✅  Downloaded IPC PDF.")
            return dest
        except requests.HTTPError as e:
            print(f"⚠️  {e} – trying next mirror.")
    raise RuntimeError("All IPC PDF mirrors failed. Please download manually to docs/ipc_1860.pdf")

def load_pages(pdf_path: pathlib.Path):
    reader = PdfReader(str(pdf_path))
    out = []
    for i, page in enumerate(reader.pages):
        txt = page.extract_text() or ""
        if txt.strip():
            out.append(IPCSection(page=i+1, text=txt.strip()))
    return out

def split_chunks(sections, size=1500, overlap=200):
    splitter = RecursiveCharacterTextSplitter(chunk_size=size, chunk_overlap=overlap)
    chunks = []
    for sec in sections:
        for chunk in splitter.split_text(sec.text):
            chunks.append((chunk, {"page": sec.page}))
    return chunks

def prepare_chunks(doc_root: pathlib.Path):
    doc_root.mkdir(parents=True, exist_ok=True)
    pdf_path = download_pdf(doc_root / "ipc_1860.pdf")
    pages = load_pages(pdf_path)
    chunks = split_chunks(pages)
    mid = len(chunks)//2 or 1
    return chunks[:mid], chunks[mid:]
