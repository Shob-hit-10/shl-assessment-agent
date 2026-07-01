from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class Retriever:
    def __init__(self, assessments):
        self.assessments = assessments

        self.documents = []

        for a in assessments:
            doc = f"""
            Name: {a.get('name', '')}
            Description: {a.get('description', '')}
            Job Levels: {' '.join(a.get('job_levels', []))}
            Keys: {' '.join(a.get('keys', []))}
            Languages: {' '.join(a.get('languages', []))}
            Duration: {a.get('duration', '')}
            """
            self.documents.append(doc)

        self.vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
        self.tfidf_matrix = self.vectorizer.fit_transform(self.documents)

    def search(self, query, top_k=10):
        query_vector = self.vectorizer.transform([query])
        scores = cosine_similarity(query_vector, self.tfidf_matrix).flatten()
        top_indices = scores.argsort()[-top_k:][::-1]
        return [self.assessments[i] for i in top_indices]