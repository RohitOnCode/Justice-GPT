import pathlib, os, dotenv
from src.loaders.ipc_loader import prepare_chunks
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_community.vectorstores import FAISS

dotenv.load_dotenv()
ROOT = pathlib.Path(__file__).parents[2]
CHROMA_DIR = ROOT / "chroma_db"
FAISS_DIR  = ROOT / "faiss_db"
CHROMA_DIR.mkdir(exist_ok=True)
FAISS_DIR.mkdir(exist_ok=True)

emb = OpenAIEmbeddings()

def _build_chroma(chunks):
    vs = Chroma(
        collection_name="ipc_part1",
        embedding_function=emb,
        persist_directory=str(CHROMA_DIR / "ipc_part1"),
    )
    docs, metas = zip(*chunks)
    vs.add_texts(list(docs), metadatas=list(metas))
    print(f" Chroma built ({len(docs)} chunks).")

def _build_faiss(chunks):
    docs, metas = zip(*chunks)
    vs = FAISS.from_texts(list(docs), embedding=emb, metadatas=list(metas))
    vs.save_local(str(FAISS_DIR / "ipc_part2"))
    print(f"FAISS built ({len(docs)} chunks).")

def ensure_vectorstores():
    if (CHROMA_DIR / "ipc_part1").exists() and (FAISS_DIR / "ipc_part2").exists():
        print("🔹 Vector stores exist – skipping build.")
        return
    print("🚧  Vector stores missing – building now …")
    part1, part2 = prepare_chunks(ROOT / "docs")
    _build_chroma(part1)
    _build_faiss(part2)
    print(" Vector stores ready.")

ensure_vectorstores()
