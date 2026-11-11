import os
import re
from typing import List, Dict, Any
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KB_DIR = os.path.join(BASE_DIR, "knowledge_base")

class RAGRetriever:
    def __init__(self, kb_dir: str = KB_DIR):
        self.kb_dir = kb_dir
        self.chunks: List[Dict[str, Any]] = []
        self.vectorizer: TfidfVectorizer = None
        self.doc_vectors = None
        self.build_index()

    def _chunk_markdown(self, filepath: str) -> List[Dict[str, Any]]:
        filename = os.path.basename(filepath)
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # Split by markdown headers (# or ##)
        raw_sections = re.split(r'\n(?=#{1,3}\s)', content)
        chunks = []
        
        current_doc_title = filename.replace(".md", "").replace("_", " ").title()

        for section in raw_sections:
            section = section.strip()
            if not section:
                continue
            
            lines = section.split("\n")
            first_line = lines[0].strip()
            if first_line.startswith("#"):
                header = first_line.lstrip("#").strip()
                body = "\n".join(lines[1:]).strip()
            else:
                header = current_doc_title
                body = section

            if not body:
                body = header

            chunks.append({
                "source": filename,
                "title": header,
                "content": f"Document: {current_doc_title}\nSection: {header}\n{body}",
                "raw_text": f"{header}. {body}"
            })
            
        return chunks

    def build_index(self):
        self.chunks = []
        if not os.path.exists(self.kb_dir):
            print(f"Knowledge base directory not found at: {self.kb_dir}")
            return

        for fname in os.listdir(self.kb_dir):
            if fname.endswith(".md") or fname.endswith(".txt"):
                fpath = os.path.join(self.kb_dir, fname)
                file_chunks = self._chunk_markdown(fpath)
                self.chunks.extend(file_chunks)

        if not self.chunks:
            print("No chunks found in knowledge base.")
            return

        corpus = [c["raw_text"] for c in self.chunks]
        self.vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2),
            sublinear_tf=True
        )
        self.doc_vectors = self.vectorizer.fit_transform(corpus)
        print(f"RAG Index built successfully: {len(self.chunks)} chunks indexed across knowledge base.")

    def search(self, query: str, top_k: int = 3, threshold: float = 0.05) -> List[Dict[str, Any]]:
        if not self.chunks or self.vectorizer is None:
            return []

        query_vec = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vec, self.doc_vectors)[0]

        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            score = float(similarities[idx])
            if score >= threshold:
                chunk = self.chunks[idx].copy()
                chunk["score"] = round(score, 4)
                results.append(chunk)

        return results

# Singleton instance for application
rag_retriever = RAGRetriever()

