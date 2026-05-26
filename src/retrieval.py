"""RAG retrieval utilities using simple similarity search."""

import pandas as pd
from pathlib import Path


def load_knowledge_base(path: str = "data/techcorp_knowledge_base.csv") -> pd.DataFrame:
    """Load the knowledge base CSV."""
    return pd.read_csv(path)


def retrieve_documents(query: str, kb_df: pd.DataFrame = None, top_k: int = 3) -> list[str]:
    """Simple keyword-based retrieval from knowledge base.

    For production, replace with vector similarity search (e.g., FAISS, Chroma).
    """
    if kb_df is None:
        kb_df = load_knowledge_base()

    query_lower = query.lower()
    scores = []
    for _, row in kb_df.iterrows():
        content = row["content"].lower()
        title = row["title"].lower()
        # Simple keyword overlap scoring
        query_words = set(query_lower.split())
        content_words = set(content.split())
        title_words = set(title.split())
        score = len(query_words & content_words) + 2 * len(query_words & title_words)
        scores.append(score)

    kb_df = kb_df.copy()
    kb_df["score"] = scores
    top_docs = kb_df.nlargest(top_k, "score")
    return [f"[{row['title']}] {row['content']}" for _, row in top_docs.iterrows()]
