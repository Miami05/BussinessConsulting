import json
import cohere
import numpy as np
import os
from sklearn.metrics.pairwise import cosine_similarity

api_key = os.getenv("COHERE_API_KEY")
co = cohere.Client(api_key)
FAQ_PATH = "faq.json"


def load_faq():
    with open(FAQ_PATH, "r") as f:
        return json.load(f)


def build_faq_index():
    faq = load_faq()
    texts = [item["question"] for item in faq]
    embeddings = co.embed(texts=texts).embeddings
    vectors = np.array(embeddings).astype("float32")
    return faq, vectors


def search_similiar_faq(faq, vectors, query, k=1):
    query_vec = np.array(co.embed(texts=[query]).embeddings).astype("float32")
    if query_vec.ndim == 1:
        query_vec = query_vec.reshape(1, -1)
    scores = cosine_similarity(query_vec, vectors)[0]
    top_indices = np.argsort(scores)[::-1][:k]
    return [faq[i] for i in top_indices]
