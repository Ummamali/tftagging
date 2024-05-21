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


@image_bp.route("/tags/objects/<algo>", methods=["POST"])
def ask_tags_object(algo):

    if "image" not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files["image"]

    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    # Convert uploaded image to numpy array
    file_stream = file.stream
    nparr = np.frombuffer(file_stream.read(), np.uint8)
    img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    tags = get_tags_whole_object(img_np, algo)
    return jsonify({"predictions": tags})


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
    if "image" not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files["image"]

    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    # Convert uploaded image to numpy array
    file_stream = file.stream
    nparr = np.frombuffer(file_stream.read(), np.uint8)
    img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    faces = extract_faces(img_np)
    print(f"{len(faces)} face extracted")
    embeddings = [get_embedding(face) for face in faces]
    predictions_ids = recognize_faces(
        embeddings, {}, current_app.config["global_embeddings"]
    )

    print(None)

    predictions = {"confident": [], "blurry": []}

    for prediction_type in predictions_ids.keys():
        for person_id in predictions_ids[prediction_type]:
            with DBConnection() as db:
                embeddings_col = db["facial_embeddings"]
                answer = embeddings_col.find_one(
                    {"personId": person_id}, {"_id": 0, "tags": 1}
                )
            predictions[prediction_type].extend(answer["tags"])
    return jsonify({"predictions": predictions})


@image_bp.route("/tags/facial/singleface", methods=["POST"])
def ask_tags_facial_singleface():
    if "image" not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files["image"]

    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    # Convert uploaded image to numpy array
    file_stream = file.stream
    nparr = np.frombuffer(file_stream.read(), np.uint8)
    img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    predictions_ids = recognize_faces(
        [get_embedding(img_np)], {}, current_app.config["global_embeddings"]
    )

    predictions = {"confident": [], "blurry": []}

    for prediction_type in predictions_ids.keys():
        for person_id in predictions_ids[prediction_type]:
            with DBConnection() as db:
                embeddings_col = db["facial_embeddings"]
                answer = embeddings_col.find_one(
                    {"personId": person_id}, {"_id": 0, "tags": 1}
                )
            predictions[prediction_type].extend(answer["tags"])
    return jsonify({"predictions": predictions})


@image_bp.route("/upload/multiple/data", methods=["POST"])
@jwt_required()
def upload_multiple_data():
    user_id = get_jwt_identity()
    req_obj = request.json

    bucket_name = req_obj["bucketName"]
    new_items = req_obj["newItems"]

    new_items_modified = []

    for item in new_items:
        new_items_modified.append({**item, "path": "/"})

    with DBConnection() as db:
        ocean_col = db["ocean"]
        result = ocean_col.update_one(
            {"_id": ObjectId(user_id), "buckets.name": bucket_name},
            {"$push": {"buckets.$.items": {"$each": new_items_modified}}},
        )
        if result.modified_count > 0:
            return jsonify({"dataSaved": True, "itemsCreated": new_items_modified})
        else:
            return jsonify({"dataSaved": False}), 400


@image_bp.route("/upload/multiple/files/<bucket_name>", methods=["POST"])
@jwt_required()
def upload_multpile_files(bucket_name):
    user_id = get_jwt_identity()
    # Check if files are present in the request
    if "images" not in request.files:
        return "No files uploaded", 400

    # Get the list of files from the request
    files = request.files.getlist("images")

    # Define the directory where images will be saved
    save_dir = os.path.join(os.getcwd(), "content", user_id, bucket_name)

    try:
        # Iterate over each file and save it to the specified directory
        for file in files:
            file.save(os.path.join(save_dir, file.filename))

        return jsonify({"success": True}), 200
    except Exception as e:
        image_names = [file.filename for file in files]
        with DBConnection() as db:
            ocean_col = db["ocean"]
            result = ocean_col.update_one(
                {"_id": ObjectId(user_id), "buckets.name": bucket_name},
                {"$pull": {"buckets.$.items": {"name": {"$in": image_names}}}},
            )
        return jsonify({"msg": str(e), "reverted_count": result.modified_count}), 500


@image_bp.route("/get/<path:file_path>", methods=["GET"])
def get_image(file_path):
    try:
        return send_file(os.path.join(os.getcwd(), "content", file_path))
    except FileNotFoundError:
        abort(404)
