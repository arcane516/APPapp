from __future__ import annotations

import argparse
from pathlib import Path

from rag import build_index, answer_query_with_rag
from settings import DATA_DIR, INDEX_DIR, DEFAULT_LLM_MODEL, TOP_K


def main() -> None:
    parser = argparse.ArgumentParser(description="Personal Local AI (Offline RAG)")
    subparsers = parser.add_subparsers(dest="command", required=True)

    p_ingest = subparsers.add_parser("ingest", help="Ingest documents and build/update the index")
    p_ingest.add_argument("--docs", type=str, default=str(DATA_DIR), help="Path to documents folder")

    p_chat = subparsers.add_parser("chat", help="Ask a question or start interactive chat")
    p_chat.add_argument("--query", type=str, default=None, help="Single question to ask")
    p_chat.add_argument("--model", type=str, default=DEFAULT_LLM_MODEL, help="LLM model to use (Ollama)")
    p_chat.add_argument("--k", type=int, default=TOP_K, help="Number of retrieved chunks")

    args = parser.parse_args()

    if args.command == "ingest":
        docs_dir = Path(args.docs).resolve()
        docs_dir.mkdir(parents=True, exist_ok=True)
        INDEX_DIR.mkdir(parents=True, exist_ok=True)
        print(f"Building index from {docs_dir} → {INDEX_DIR} ...")
        build_index(docs_dir, INDEX_DIR)
        print("Index built.")
        return

    if args.command == "chat":
        if args.query:
            answer = answer_query_with_rag(args.query, model=args.model, top_k=args.k)
            print("\nAnswer:\n" + answer)
            return
        # Interactive mode
        print("Entering interactive mode. Press Ctrl+C to exit.")
        try:
            while True:
                q = input("You: ").strip()
                if not q:
                    continue
                ans = answer_query_with_rag(q, model=args.model, top_k=args.k)
                print("AI: " + ans + "\n")
        except KeyboardInterrupt:
            print("\nBye!")
            return


if __name__ == "__main__":
    main()