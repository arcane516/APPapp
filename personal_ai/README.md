# Personal Local AI (Offline RAG)

A private, fully local AI assistant using [Ollama](`https://ollama.com`) to run both a chat LLM and an embedding model. No external APIs.

## Features
- Local chat with `llama3.1:8b` (modifiable)
- Local embeddings via `nomic-embed-text`
- Simple RAG over your `data/` folder (`.txt`, `.md`, `.pdf`)

## Setup
```bash
# 1) Ensure Ollama is installed and models are pulled
#    (already handled by setup script; manual steps if needed)
ollama serve &
ollama pull llama3.1:8b
ollama pull nomic-embed-text

# 2) Create venv and install deps
cd /workspace/personal_ai
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 3) Add your files into data/
mkdir -p data
# copy your .txt/.md/.pdf files into data/

# 4) Build the local index
python app.py ingest --docs ./data

# 5) Ask questions
python app.py chat --query "What do my notes say about X?"
# or start an interactive session
python app.py chat
```

## Model settings
Edit `settings.py` to change:
- `DEFAULT_LLM_MODEL` (e.g., `llama3.1:8b` → `llama3.2:1b`)
- `EMBEDDING_MODEL` (default: `nomic-embed-text`)
- Chunking and retrieval params

## Notes
- All computation is local. Performance depends on your CPU/GPU.
- PDF parsing is best-effort via `pypdf`. For complex PDFs, consider converting to text.