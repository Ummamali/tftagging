from flask import jsonify, request, current_app
from app.utils.database import DBConnection
from flask_jwt_extended import get_jwt_identity, jwt_required
from http import HTTPStatus
from .routes import image_bp
from app.utils.middlewares import validate_schema
from app.engine.object_identify_original import get_tags_whole_object
import os
from werkzeug.utils import secure_filename




@image_bp.route("/save", methods=["POST"])
@jwt_required()
def login():
    user_id = get_jwt_identity()
    # Check if the POST request has the file part
    if 'files' not in request.files:
        return jsonify(msg='No files!'), 400

    files = request.files.getlist('files')

    # Specify the directory where you want to save the images
    save_directory = os.path.join(os.getcwd(), "content", user_id, '_temp')

    saved_files = []

    # checking if any already exists
    for file in files:
        filename = secure_filename(file.filename)
        if os.path.exists(os.path.join(save_directory, filename)):
            return jsonify('File already exists'), 400

    for file in files:
        if file.filename == '':
            return 'No selected file', 400
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(save_directory, filename))
            saved_files.append(filename)

    return jsonify(saved=saved_files)
    


ask_tags_schema =  {
    "type": "object",
    "properties": {
        "filenames": {
            "type": "array",
            "items": {"type": "string"}
        },
        "bucketName": {"type": "string"},
        "algo": {"type": "string"}
    },
    "required": ["filenames", "bucketName", 'algo']
}

@image_bp.route("/askTags", methods=['POST'])
@jwt_required()
@validate_schema(ask_tags_schema)
def ask_tags():
    user_id = get_jwt_identity()
    req_obj = request.json
    filenames = req_obj['filenames']
    bucket_path = os.path.join(current_app.config['CONTENT-DIRECTORY'], user_id, req_obj['bucketName'])
    file_tags = []
    for itemName in filenames:
        item_path = os.path.join(bucket_path, itemName)
        if os.path.exists(item_path):
            tags = get_tags_whole_object(user_id, req_obj['bucketName'], itemName, req_obj['algo'])
            file_tags.append({'filename': itemName, 'tags': tags})
        else:
            file_tags.append({'filename': itemName, 'tags': []})
    return jsonify(file_tags)

