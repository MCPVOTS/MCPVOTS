"""
Lightweight SQLite-backed vector store with cosine similarity.
Collections: identity, funding, trade (or any string label).
Embeddings stored as JSON arrays; metadata stored as JSON; simple where filters.
"""
from __future__ import annotations

import json
import math
import os
import sqlite3
import threading
import time
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple


def _ensure_dir(path: str):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)


def _cosine(a: Sequence[float], b: Sequence[float]) -> float:
    if not a or not b:
        return 0.0
    if len(a) != len(b):
        # pad/truncate
        n = min(len(a), len(b))
        a = a[:n]
        b = b[:n]
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def hash_embed(text: str, dim: int = 384) -> List[float]:
    """Deterministic hashing bag-of-words embedding with simple weighting.
    No external deps; good enough for rough similarity.
    """
    vec = [0.0] * dim
    if not text:
        return vec
    # basic tokenization
    for tok in text.lower().split():
        h = hash(tok) % dim
        vec[h] += 1.0
    # L2 normalize
    norm = math.sqrt(sum(v * v for v in vec)) or 1.0
    return [v / norm for v in vec]


@dataclass
class QueryResult:
    ids: List[str]
    metadatas: List[List[Dict[str, Any]]]
    documents: List[List[str]]
    distances: Optional[List[List[float]]] = None


class SQLiteVectorStore:
    def __init__(self, db_path: str = "data/local_vectors.db"):
        _ensure_dir(db_path)
        self.db_path = db_path
        self._lock = threading.RLock()
        self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self):
        with self._conn:
            self._conn.execute(
                """
                CREATE TABLE IF NOT EXISTS vectors (
                    id TEXT PRIMARY KEY,
                    collection TEXT NOT NULL,
                    embedding TEXT NOT NULL,
                    document TEXT,
                    metadata TEXT,
                    created_at REAL
                )
                """
            )
            self._conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_vectors_collection ON vectors(collection)"
            )
            self._conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_vectors_created ON vectors(created_at)"
            )

    # Chroma-like API
    def add(
        self,
        collection: str,
        ids: Sequence[str],
        embeddings: Sequence[Sequence[float]],
        documents: Optional[Sequence[str]] = None,
        metadatas: Optional[Sequence[Dict[str, Any]]] = None,
    ) -> None:
        ts = time.time()
        documents = documents or [None] * len(ids)
        metadatas = metadatas or [None] * len(ids)
        with self._lock, self._conn:
            for i, emb in enumerate(embeddings):
                self._conn.execute(
                    """
                    INSERT OR REPLACE INTO vectors (id, collection, embedding, document, metadata, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        ids[i],
                        collection,
                        json.dumps(list(map(float, emb))),
                        documents[i],
                        json.dumps(metadatas[i]) if metadatas[i] is not None else None,
                        ts,
                    ),
                )

    def count(self, collection: str) -> int:
        cur = self._conn.execute(
            "SELECT COUNT(*) AS c FROM vectors WHERE collection = ?", (collection,)
        )
        return int(cur.fetchone()[0])

    def query(
        self,
        collection: str,
        query_embeddings: Optional[Sequence[Sequence[float]]] = None,
        query_texts: Optional[Sequence[str]] = None,
        where: Optional[Dict[str, Any]] = None,
        n_results: int = 10,
    ) -> QueryResult:
        if query_embeddings is None and query_texts is None:
            raise ValueError("Provide query_embeddings or query_texts")
        if query_embeddings is None:
            query_embeddings = [hash_embed(t) for t in (query_texts or [])]

        # Load candidates
        where = where or {}
        rows = self._conn.execute(
            "SELECT * FROM vectors WHERE collection = ?", (collection,)
        ).fetchall()

        # Filter by metadata equality if provided
        candidates: List[sqlite3.Row] = []
        for r in rows:
            if where:
                md = json.loads(r["metadata"]) if r["metadata"] else {}
                ok = all(md.get(k) == v for k, v in where.items())
                if not ok:
                    continue
            candidates.append(r)

        # Pre-decode embeddings
        cand_embs: List[Tuple[sqlite3.Row, List[float]]] = [
            (r, list(map(float, json.loads(r["embedding"])))) for r in candidates
        ]

        results_ids: List[str] = []
        results_metas: List[List[Dict[str, Any]]] = []
        results_docs: List[List[str]] = []
        results_dists: List[List[float]] = []

        for q in query_embeddings:
            scored: List[Tuple[float, sqlite3.Row]] = []
            for r, e in cand_embs:
                sim = _cosine(q, e)
                scored.append((sim, r))
            scored.sort(key=lambda x: x[0], reverse=True)
            top = scored[:n_results]
            ids = [r["id"] for _, r in top]
            metas = [json.loads(r["metadata"]) if r["metadata"] else {} for _, r in top]
            docs = [r["document"] or "" for _, r in top]
            # distances as 1 - similarity
            dists = [1.0 - s for s, _ in top]
            results_ids.append(ids)
            results_metas.append(metas)
            results_docs.append(docs)
            results_dists.append(dists)

        return QueryResult(
            ids=results_ids,
            metadatas=results_metas,
            documents=results_docs,
            distances=results_dists,
        )

    def close(self):
        try:
            self._conn.close()
        except Exception:
            pass


__all__ = ["SQLiteVectorStore", "hash_embed", "QueryResult"]
