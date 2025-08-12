from pathlib import Path

# Core models (Ollama)
DEFAULT_LLM_MODEL: str = "llama3.1:8b"
EMBEDDING_MODEL: str = "nomic-embed-text"

# Paths
PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR: Path = PROJECT_ROOT / "data"
INDEX_DIR: Path = PROJECT_ROOT / "index"

# Chunking and retrieval
CHUNK_SIZE_CHARS: int = 1200
CHUNK_OVERLAP_CHARS: int = 200
TOP_K: int = 5

# Misc
SEED: int = 42