from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Tuple, Dict

import numpy as np
import ollama  # type: ignore
from pypdf import PdfReader

from settings import (
    DEFAULT_LLM_MODEL,
    EMBEDDING_MODEL,
    DATA_DIR,
    INDEX_DIR,
    CHUNK_SIZE_CHARS,
    CHUNK_OVERLAP_CHARS,
    TOP_K,
)


@dataclass
class RetrievedChunk:
    text: str
    source: str
    score: float


def read_text_from_file(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in {".txt", ".md", ".markdown"}:
        return path.read_text(encoding="utf-8", errors="ignore")
    if suffix == ".pdf":
        reader = PdfReader(str(path))
        pages_text = []
        for page in reader.pages:
            try:
                pages_text.append(page.extract_text() or "")
            except Exception:
                pages_text.append("")
        return "\n".join(pages_text)
    return ""


def iter_documents(docs_dir: Path) -> Iterable[Tuple[str, str]]:
    for path in docs_dir.rglob("*"):
        if path.is_file() and path.suffix.lower() in {".txt", ".md", ".markdown", ".pdf"}:
            text = read_text_from_file(path)
            if text.strip():
                yield (str(path), text)


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE_CHARS, overlap: int = CHUNK_OVERLAP_CHARS) -> List[str]:
    chunks: List[str] = []
    start = 0
    length = len(text)
    while start < length:
        end = min(start + chunk_size, length)
        chunk = text[start:end]
        chunks.append(chunk)
        if end == length:
            break
        start = end - overlap
        if start < 0:
            start = 0
    return chunks


def embed_texts(texts: List[str]) -> np.ndarray:
    vectors: List[List[float]] = []
    for t in texts:
        resp = ollama.embeddings(model=EMBEDDING_MODEL, prompt=t)
        vectors.append(resp["embedding"])  # type: ignore
    arr = np.array(vectors, dtype=np.float32)
    norms = np.linalg.norm(arr, axis=1, keepdims=True) + 1e-12
    arr = arr / norms
    return arr


def build_index(docs_dir: Path = DATA_DIR, index_dir: Path = INDEX_DIR) -> None:
    index_dir.mkdir(parents=True, exist_ok=True)

    all_chunks: List[str] = []
    metadatas: List[Dict[str, str]] = []

    for source, text in iter_documents(docs_dir):
        chunks = chunk_text(text)
        for i, chunk in enumerate(chunks):
            all_chunks.append(chunk)
            metadatas.append({"source": source, "chunk_index": str(i)})

    if not all_chunks:
        raise RuntimeError(f"No documents found in {docs_dir}. Add .txt/.md/.pdf files and retry.")

    embeddings = embed_texts(all_chunks)

    np.save(index_dir / "embeddings.npy", embeddings)
    with (index_dir / "chunks.jsonl").open("w", encoding="utf-8") as f:
        for meta, chunk in zip(metadatas, all_chunks):
            record = {"text": chunk, **meta}
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


def load_index(index_dir: Path = INDEX_DIR) -> Tuple[np.ndarray, List[Dict[str, str]]]:
    emb_path = index_dir / "embeddings.npy"
    meta_path = index_dir / "chunks.jsonl"
    if not emb_path.exists() or not meta_path.exists():
        raise RuntimeError("Index not found. Run ingestion first: python app.py ingest")

    embeddings = np.load(emb_path)
    metadatas: List[Dict[str, str]] = []
    with meta_path.open("r", encoding="utf-8") as f:
        for line in f:
            metadatas.append(json.loads(line))

    return embeddings, metadatas


def retrieve(query: str, top_k: int = TOP_K, index_dir: Path = INDEX_DIR) -> List[RetrievedChunk]:
    embeddings, metadatas = load_index(index_dir)
    q_vec = embed_texts([query])[0]
    scores = embeddings @ q_vec  # cosine similarity due to normalization
    if top_k <= 0:
        top_k = 1
    top_k = min(top_k, embeddings.shape[0])
    top_indices = np.argpartition(-scores, top_k - 1)[:top_k]
    top_indices = top_indices[np.argsort(-scores[top_indices])]

    results: List[RetrievedChunk] = []
    for idx in top_indices.tolist():
        meta = metadatas[idx]
        results.append(
            RetrievedChunk(text=meta["text"], source=meta["source"], score=float(scores[idx]))
        )
    return results


def build_context(chunks: List[RetrievedChunk]) -> str:
    parts = []
    for c in chunks:
        parts.append(f"Source: {c.source}\n---\n{c.text}\n")
    return "\n\n".join(parts)


def answer_query_with_rag(query: str, model: str = DEFAULT_LLM_MODEL, top_k: int = TOP_K) -> str:
    retrieved = retrieve(query, top_k=top_k)
    context = build_context(retrieved)

    system_prompt = (
        "You are a private local assistant. Use the provided CONTEXT to answer the user's question. "
        "If the answer is not in the context, say you don't know based on the provided documents."
    )
    user_prompt = f"CONTEXT:\n{context}\n\nQUESTION:\n{query}"

    resp = ollama.chat(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    return resp["message"]["content"]  # type: ignore