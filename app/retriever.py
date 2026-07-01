from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


class Retriever:
    def __init__(self, assessments):
        self.assessments = assessments

        print("Loading embedding model...")
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

        self.documents = []

        for a in assessments:
            doc = f"""
            Name: {a.get('name', '')}
            Description: {a.get('description', '')}
            Job Levels: {' '.join(a.get('job_levels', []))}
            Keys: {' '.join(a.get('keys', []))}
            Test Type: {a.get('test_type', '')}
            Languages: {' '.join(a.get('languages', []))}
            Duration: {a.get('duration', '')}
            """
            self.documents.append(doc)

        print("Creating embeddings...")
        self.embeddings = self.model.encode(
            self.documents,
            convert_to_numpy=True,
            show_progress_bar=True
        )

        print("Creating TF-IDF index...")
        self.vectorizer = TfidfVectorizer(stop_words="english")
        self.tfidf_matrix = self.vectorizer.fit_transform(self.documents)

    def search(self, query, top_k=5):

        # ---------- Semantic Search ----------
        query_embedding = self.model.encode(
            query,
            convert_to_numpy=True
        )

        semantic_scores = np.dot(self.embeddings, query_embedding)

        # ---------- Keyword Search ----------
        query_vector = self.vectorizer.transform([query])

        keyword_scores = cosine_similarity(
            query_vector,
            self.tfidf_matrix
        ).flatten()

        # ---------- Hybrid Score ----------
        final_scores = (
            0.7 * semantic_scores +
            0.3 * keyword_scores
        )

        top_indices = final_scores.argsort()[-top_k:][::-1]

        return [self.assessments[i] for i in top_indices]