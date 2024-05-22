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
from app.utils.utilFuncs import filter_comparison_scores
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
    bucket_object_emb = array([item["tags"]["objects"] for item in embeddings])
    bucket_people_emb = array([item["tags"]["people"] for item in embeddings])
    bucket_box_emb = array([item["boxes"] for item in embeddings])

    all_comparisons = [*compare_embeddings(query_embedding, bucket_object_emb), *compare_embeddings(query_embedding, bucket_people_emb), *compare_embeddings(query_embedding, bucket_box_emb)]

    all_comparisons.sort(key=lambda item: item[1], reverse=True)

    pprint.pprint(all_comparisons)
    

    filtered_scores = filter_comparison_scores(all_comparisons, 0.40)

    return jsonify({"scores": filtered_scores})
