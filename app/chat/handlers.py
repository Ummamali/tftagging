from .routes import chat_bp
from flask import jsonify, request
from app.engine.chatter.utils import (
    get_embedding,
    load_embeddings_for_bucket,
    compare_embeddings,
)
from app.utils.database import DBConnection
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId
from numpy import array, float32
import numpy as np
from sentence_transformers import util
import pprint


@chat_bp.route("/search", methods=["POST"])
@jwt_required()
def find_media():
    user_id = get_jwt_identity()
    req_obj = request.json
    bucket_name = req_obj["bucketName"]
    query = req_obj["query"]
    query_embedding = get_embedding(query)
    embeddings = load_embeddings_for_bucket(bucket_name, user_id)
    media_titles = [item["title"] for item in embeddings]
    bucket_object_emb = array([item["tags"]["objects"] for item in embeddings])
    bucket_people_emb = array([item["tags"]["people"] for item in embeddings])
    bucket_box_emb = array([item["boxes"] for item in embeddings])

    object_comparison_idx = compare_embeddings(query_embedding, bucket_object_emb)
    object_comparison_names = [
        (media_titles[idx], score) for (idx, score) in object_comparison_idx
    ]

    print(object_comparison_names)
    # Compute cosine similarities between query and tags
    # cosine_scores = util.pytorch_cos_sim(query_embedding, emb_items)[0]

    # # Get the top N most similar tags
    # top_n = 5
    # top_results = np.argsort(-cosine_scores)[:top_n]
    # top_titles = [
    #     (media_titles[index], cosine_scores[index].item()) for index in top_results
    # ]
    # print(top_titles)

    return jsonify({"msg": "Good"})
