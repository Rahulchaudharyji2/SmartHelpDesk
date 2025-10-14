from typing import List, Dict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class KBEngine:
    def __init__(self):
        self.vectorizer = None
        self.matrix = None
        self.records = []

    def build_index(self, db):
        from .models import KnowledgeBase
        self.records = db.query(KnowledgeBase).all()
        corpus = [f"{r.title}. {r.content}" for r in self.records]
        if len(corpus) == 0:
            self.vectorizer = None
            self.matrix = None
            return
        self.vectorizer = TfidfVectorizer(stop_words="english")
        self.matrix = self.vectorizer.fit_transform(corpus)

    def suggest(self, db, text: str, top_k: int = 3) -> List[Dict]:
        if self.vectorizer is None or self.matrix is None:
            self.build_index(db)
        if self.vectorizer is None or self.matrix is None:
            return []
        q = self.vectorizer.transform([text])
        sim = cosine_similarity(q, self.matrix).flatten()
        idxs = sim.argsort()[::-1][:top_k]
        out = []
        for i in idxs:
            r = self.records[i]
            out.append({"id": r.id, "title": r.title, "score": float(sim[i])})
        return out