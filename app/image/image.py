from flask import jsonify, request
from app.utils.database import DBConnection
from flask_jwt_extended import get_jwt_identity, jwt_required
from http import HTTPStatus
from .routes import image_bp
from app.utils.middlewares import validate_schema
from app.engine.object_identify_original import get_tags_whole_object


tag_image_schema = schema = {
    "type": "object",
    "properties": {
        "bucketId": {"type": "string"},
        "mediaId": {"type": "string"},
        "algo": {"type": "string"},
    },
    "required": ["bucketName", "mediaName", "algo"],
}


@image_bp.route("/tags", methods=["POST"])
@validate_schema(tag_image_schema)
@jwt_required()
def login():
    user_id = get_jwt_identity()
    req_obj = request.json
    tags = get_tags_whole_object(
        user_id, req_obj["bucketName"], req_obj["mediaName"], req_obj["algo"]
    )
    return jsonify(tags=tags)


# @image_bp.route("/temp/tags", methods=['POST'])
