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

import numpy as np
from sentence_transformers import util


@chat_bp.route("/search", methods=["POST"])
@jwt_required()
def find_media():
    user_id = get_jwt_identity()
    req_obj = request.json
    bucket_name = req_obj["bucketName"]
    query = req_obj["query"].lower()

    query_embedding = get_embedding(query)

    with DBConnection() as db:
        ocean_col = db["ocean"]
        buckets = ocean_col.find_one({"_id": ObjectId(user_id)}, {"buckets": 1})[
            "buckets"
        ]

        bucket_index = -1
        for i in range(len(buckets)):
            if buckets[i]["name"] == bucket_name:
                bucket_index = i
                break

        media_items = buckets[bucket_index]["items"]
        scores = [0 for _ in media_items]

        for item_idx, item in enumerate(media_items):
            all_box_tags = []
            for box in item["boxes"]:
                box_tags = box["tags"]
                for tag in box_tags:
                    all_box_tags.append(tag)
            all_tags = [
                *item["tags"]["objects"],
                *item["tags"]["people"],
                *all_box_tags,
            ]

            for tag_text in all_tags:
                if tag_text.lower() == query:
                    scores[item_idx] += 1
                else:
                    cosine_score = float(
                        util.pytorch_cos_sim(
                            query_embedding, np.array([get_embedding(tag_text)])
                        )[0]
                    )
                    if cosine_score > 0.6:
                        scores[item_idx] += 1

        indexed_scores = [(i, score) for i, score in enumerate(scores)]
        indexed_scores.sort(key=lambda j: j[1], reverse=True)

        filtered_scores = []

        for index, score in indexed_scores:
            if score == 0:
                break
            filtered_scores.append((index, score))

        print(filtered_scores)

    return jsonify({"scores": filtered_scores})
