"""Hybrid retrieval module combining dense vector search and sparse BM25 with Reciprocal Rank Fusion (RRF)."""

import os
import math
import re
from typing import List, Dict, Any


def tokenize(text: str) -> List[str]:
    """Tokenize text into lowercase alphanumeric tokens."""
    return re.findall(r"\b[a-zA-Z0-9_]+\b", text.lower())


class SimpleBM25:
    """Lightweight in-memory BM25 implementation for robust keyword search."""

    def __init__(self, corpus: List[str], k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.corpus = corpus
        self.tokenized_corpus = [tokenize(doc) for doc in corpus]
        self.doc_lengths = [len(doc) for doc in self.tokenized_corpus]
        self.avg_doc_len = sum(self.doc_lengths) / max(len(self.doc_lengths), 1)
        self.doc_freqs = []
        self.idf = {}
        self._calc_idf()

    def _calc_idf(self):
        df = {}
        for doc in self.tokenized_corpus:
            unique_terms = set(doc)
            for term in unique_terms:
                df[term] = df.get(term, 0) + 1
        n = len(self.corpus)
        for term, freq in df.items():
            self.idf[term] = math.log(1 + (n - freq + 0.5) / (freq + 0.5))

    def get_scores(self, query: str) -> List[float]:
        query_tokens = tokenize(query)
        scores = [0.0] * len(self.corpus)
        for i, doc in enumerate(self.tokenized_corpus):
            doc_len = self.doc_lengths[i]
            if doc_len == 0:
                continue
            tf_dict = {}
            for t in doc:
                tf_dict[t] = tf_dict.get(t, 0) + 1

            doc_score = 0.0
            for qt in query_tokens:
                if qt in self.idf:
                    tf = tf_dict.get(qt, 0)
                    numerator = tf * (self.k1 + 1)
                    denominator = tf + self.k1 * (1 - self.b + self.b * (doc_len / max(self.avg_doc_len, 1e-6)))
                    doc_score += self.idf[qt] * (numerator / max(denominator, 1e-6))
            scores[i] = doc_score
        return scores


class HybridRetriever:
    """Combines dense vector retrieval and BM25 using Reciprocal Rank Fusion (RRF)."""

    def __init__(self, rrf_k: int = 60):
        self.rrf_k = rrf_k

    def reciprocal_rank_fusion(
        self, dense_results: List[Dict[str, Any]], bm25_results: List[Dict[str, Any]], top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Combine dense and BM25 ranked lists using Reciprocal Rank Fusion."""
        # Key by chunk_id or unique identifier
        scores: Dict[str, float] = {}
        items: Dict[str, Dict[str, Any]] = {}

        # Process dense results
        for rank, item in enumerate(dense_results):
            cid = item.get("id") or item.get("chunk_id") or str(hash(item.get("text", "")))
            scores[cid] = scores.get(cid, 0.0) + (1.0 / (self.rrf_k + rank + 1))
            if cid not in items:
                items[cid] = dict(item)
            items[cid]["dense_rank"] = rank + 1

        # Process BM25 results
        for rank, item in enumerate(bm25_results):
            cid = item.get("id") or item.get("chunk_id") or str(hash(item.get("text", "")))
            scores[cid] = scores.get(cid, 0.0) + (1.0 / (self.rrf_k + rank + 1))
            if cid not in items:
                items[cid] = dict(item)
            items[cid]["bm25_rank"] = rank + 1

        # Sort items by RRF score descending
        sorted_keys = sorted(scores.keys(), key=lambda k: scores[k], reverse=True)
        final_results = []
        for cid in sorted_keys[:top_k]:
            merged = items[cid]
            merged["rrf_score"] = round(scores[cid], 5)
            final_results.append(merged)

        return final_results
