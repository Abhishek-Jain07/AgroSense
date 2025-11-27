# rag/vector_store.py

import os
import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# Config: choose embedding model
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

class VectorStore:
    def __init__(self, json_path="rag/rag_chunks.json", index_path="rag/faiss_index.bin", embeddings_path="rag/embeddings.npy"):
        self.json_path = json_path
        self.index_path = index_path
        self.embeddings_path = embeddings_path

        # Load chunks
        with open(json_path, 'r', encoding='utf-8') as f:
            self.chunks = json.load(f)

        self.model = SentenceTransformer(EMBEDDING_MODEL)
        self._load_or_build_index()

    def _load_or_build_index(self):
        # If index and embeddings exist, load them; else build
        if os.path.exists(self.index_path) and os.path.exists(self.embeddings_path):
            # load embeddings
            self.embeddings = np.load(self.embeddings_path)
            # load index
            self.index = faiss.read_index(self.index_path)
        else:
            texts = [c.get("text", "") for c in self.chunks]
            if not texts:
                raise ValueError("No chunks found in RAG JSON.")

            embeddings = self.model.encode(texts, convert_to_numpy=True, normalize_embeddings=True).astype(np.float32)
            dim = embeddings.shape[1]

            # Create index
            self.index = faiss.IndexFlatIP(dim)  # cosine-sim via inner product
            self.index.add(embeddings)

            # Save for reuse
            os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
            faiss.write_index(self.index, self.index_path)
            np.save(self.embeddings_path, embeddings)
            self.embeddings = embeddings

    def query(self, query_text: str, top_k=5, soil_filter: str = None):
        """
        Returns list of chunk dicts: top_k most similar to the query.
        If soil_filter provided, filters chunks whose soil_tags contain the soil_filter (case insensitive).
        """
        q_emb = self.model.encode([query_text], convert_to_numpy=True, normalize_embeddings=True).astype(np.float32)
        distances, idxs = self.index.search(q_emb, top_k)
        
        results = []
        for idx in idxs[0]:
            if idx < 0 or idx >= len(self.chunks):
                continue
            chunk = self.chunks[idx]
            if soil_filter:
                tags = [t.strip().lower() for t in chunk.get("soil_tags", [])]
                if soil_filter.strip().lower() not in tags:
                    continue
            results.append(chunk)
        return results