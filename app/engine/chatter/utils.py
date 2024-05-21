from sentence_transformers import SentenceTransformer
from app.utils.database import DBConnection
from bson import ObjectId
from numpy import array, float32

import numpy as np
from sentence_transformers import util

# Load a pre-trained sentence transformer model
model = SentenceTransformer("all-MiniLM-L6-v2")


def get_embedding(text):
    """
    Given a text string, return its embedding.

    Args:
        text (str): The input text string.

    Returns:
        numpy.ndarray: The embedding vector for the input text.
    """
    embedding = model.encode(text, convert_to_tensor=False)
    return embedding


def load_embeddings_for_bucket(bucket_name, user_id):
    with DBConnection() as db:
        tag_emb_col = db["tag_embeddings"]
        result = tag_emb_col.find_one({"_id": ObjectId(user_id)})
        media_items = result["buckets"][bucket_name]
        for i in range(len(media_items)):
            media_items[i]["tags"] = {
                "objects": array(media_items[i]["tags"]["objects"], dtype=float32),
                "people": array(media_items[i]["tags"]["people"], dtype=float32),
            }
            media_items[i]["boxes"] = array(media_items[i]["boxes"], dtype=float32)
        return media_items


def compare_embeddings(query_embedding, target_embs):
    # Compute cosine similarities between query and tags
    cosine_scores = util.pytorch_cos_sim(query_embedding, target_embs)[0]

    results = np.argsort(-cosine_scores)
    return [(int(index), cosine_scores[index].item()) for index in results]
