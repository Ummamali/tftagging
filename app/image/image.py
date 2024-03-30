from flask import Blueprint, jsonify, request, make_response
from app.utils.database import DBConnection
from flask_jwt_extended import get_jwt_identity, jwt_required, create_access_token
from http import HTTPStatus
from .routes import user_bp
from app.utils.middlewares import validate_schema


tag_image_schema = schema = {
    "type": "object",
    "properties": {
        "bucketId": {"type": "string"},
        "mediaId": {"type": "string"},
        "algo": {"type": "string"}
    },
    "required": ["bucketId", "mediaId", "algo"]
}


@user_bp.route("/tag", methods=["POST"])
@validate_schema(tag_image_schema)
@jwt_required()
def login():
    user_id = get_jwt_identity()
    req_obj = request.json
    with DBConnection() as db:
        col_media = ''
