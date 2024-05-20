from flask import jsonify, request, current_app, send_file, abort
from app.utils.database import DBConnection
from flask_jwt_extended import get_jwt_identity, jwt_required
from http import HTTPStatus
from .routes import image_bp
from app.utils.middlewares import validate_schema
from app.engine.object_identify_original import get_tags_whole_object
from app.engine.facial.recognize import recognize_faces
from app.engine.facial.face_extractor import extract_faces
from app.engine.facial.embed_known_faces import get_embedding
import os
from werkzeug.utils import secure_filename
from app.image.utils.utils import move_media_from_temp
from bson import ObjectId
import numpy as np
import cv2


@image_bp.route("/save", methods=["POST"])
@jwt_required()
def save_media():
    user_id = get_jwt_identity()
    # Check if the POST request has the file part
    if "files" not in request.files:
        return jsonify(msg="No files!"), 400

    files = request.files.getlist("files")

    # Specify the directory where you want to save the images
    save_directory = os.path.join(os.getcwd(), "content", user_id, "_temp")

    saved_files = []

    for file in files:
        if file.filename == "":
            return "No selected file", 400
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(save_directory, filename))
            saved_files.append(filename)

    return jsonify(saved=saved_files)


ask_tags_schema = {
    "type": "object",
    "properties": {
        "filenames": {"type": "array", "items": {"type": "string"}},
        "bucketName": {"type": "string"},
        "algo": {"type": "string"},
    },
    "required": ["filenames", "bucketName", "algo"],
}


@image_bp.route("/askTags", methods=["POST"])
@jwt_required()
@validate_schema(ask_tags_schema)
def ask_tags():
    user_id = get_jwt_identity()
    req_obj = request.json
    filenames = req_obj["filenames"]
    bucket_path = os.path.join(
        current_app.config["CONTENT-DIRECTORY"], user_id, req_obj["bucketName"]
    )
    file_tags = []
    for itemName in filenames:
        item_path = os.path.join(bucket_path, itemName)
        if os.path.exists(item_path):
            tags = get_tags_whole_object(
                user_id, req_obj["bucketName"], itemName, req_obj["algo"]
            )
            file_tags.append({"filename": itemName, "tags": tags})
        else:
            file_tags.append({"filename": itemName, "tags": []})
    return jsonify(file_tags)


ask_tags_facial_schema = {
    "type": "object",
    "properties": {
        "filenames": {"type": "array", "items": {"type": "string"}},
        "bucketName": {"type": "string"},
    },
    "required": ["filenames", "bucketName"],
}


# @jwt_required()
# @validate_schema(ask_tags_facial_schema)
@image_bp.route("/tags/facial", methods=["POST"])
def ask_tags_facial():
    # # user_id = get_jwt_identity()
    # req_obj = request.json
    # # filenames = req_obj["filenames"]
    # bucket_path = os.path.join(
    #     current_app.config["CONTENT-DIRECTORY"], user_id, req_obj["bucketName"]
    # )

    # faces = tag_people_in(bucket_path, filenames, user_id)
    # return jsonify(faces)
    if 'image' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400

    file = request.files['image']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Convert uploaded image to numpy array
    file_stream = file.stream
    nparr = np.frombuffer(file_stream.read(), np.uint8)
    img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    faces = extract_faces(img_np)
    print(f'{len(faces)} face extracted')
    embeddings = [get_embedding(face) for face in faces]
    predictions_ids = recognize_faces(
        embeddings, {}, current_app.config['global_embeddings'])

    print(None)

    predictions = {'confident': [], 'blurry': []}

    for prediction_type in predictions_ids.keys():
        for person_id in predictions_ids[prediction_type]:
            with DBConnection() as db:
                embeddings_col = db['facial_embeddings']
                answer = embeddings_col.find_one(
                    {'personId': person_id}, {'_id': 0, 'tags': 1})
            predictions[prediction_type].extend(answer['tags'])
    return jsonify({'predictions': predictions})


@image_bp.route("/tags/facial/singleface", methods=["POST"])
def ask_tags_facial_singleface():
    if 'image' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400

    file = request.files['image']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Convert uploaded image to numpy array
    file_stream = file.stream
    nparr = np.frombuffer(file_stream.read(), np.uint8)
    img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    predictions_ids = recognize_faces(
        [get_embedding(img_np)], {}, current_app.config['global_embeddings'])

    predictions = {'confident': [], 'blurry': []}

    for prediction_type in predictions_ids.keys():
        for person_id in predictions_ids[prediction_type]:
            with DBConnection() as db:
                embeddings_col = db['facial_embeddings']
                answer = embeddings_col.find_one(
                    {'personId': person_id}, {'_id': 0, 'tags': 1})
            predictions[prediction_type].extend(answer['tags'])
    return jsonify({'predictions': predictions})


recognize_media_schema = schema = {
    "type": "object",
    "properties": {
        "bucketName": {"type": "string"},
        "mediaNames": {
            "type": "array",
            "items": {"type": "string"}
        },
        "tags": {
            "type": "object",
        }
    },
    "required": ["bucketName", "mediaNames", "tags"]
}


@image_bp.route("/recognize", methods=["POST"])
@jwt_required()
@validate_schema(recognize_media_schema)
def recognize_media_items():
    user_id = get_jwt_identity()
    req_obj = request.json
    bucket_name = req_obj['bucketName']
    media_names = req_obj['mediaNames']
    tags_object = req_obj['tags']
    bucket_index = req_obj['bucketIndex']
    with DBConnection() as db:
        for name in media_names:
            new_media_obj = {"title": name,
                             "path": '/', "tags": tags_object[name]}
            db['ocean'].update_one(
                {"_id": ObjectId(user_id),
                 "buckets.name": bucket_name},
                {"$push": {"buckets.$.items": new_media_obj}}
            )

    move_media_from_temp(media_names, user_id, bucket_name, tags_object)
    return jsonify(msg='recognized')


@image_bp.route("/get/<path:file_path>", methods=["GET"])
def get_image(file_path):
    try:
        return send_file(os.path.join(os.getcwd(), 'content', file_path))
    except FileNotFoundError:
        abort(404)
