from .routes import video_bp
from flask import request, jsonify
from app.utils.database import DBConnection
from bson import ObjectId
import os

@video_bp.route("/upload/single/data", methods=['POST'])
def save_video_data():
	req_obj = request.json
	user_id = req_obj['userId']
	video_obj = {"title": req_obj['title'], 'tags': req_obj['tags']}
	with DBConnection() as db:
		ocean_col = db['ocean']
		ocean_col.update_one({'_id': ObjectId(user_id)}, { "$push": { "videos": video_obj } })
	return jsonify({'good': True})


@video_bp.route('/upload/<user_id>', methods=['POST'])
def upload_video(user_id):
    if 'video' not in request.files:
        return jsonify({"error": "No video file part in the request"}), 400
    
    video = request.files['video']
    
    if video.filename == '':
        return jsonify({"error": "No selected video file"}), 400
    
    # Save the file
    file_path = os.path.join(os.getcwd(), 'content', user_id, '_videos', video.filename)
    video.save(file_path)
    
    return jsonify({"message": "Video uploaded successfully", "file_path": file_path}), 200


@video_bp.route("/data/<user_id>")
def get_video_data(user_id):
      print(os.path.join(os.getcwd(), '..'))
      with DBConnection() as db:
            ocean_col = db['ocean']
            result = ocean_col.find_one({'_id': ObjectId(user_id)}, {'videos': 1})['videos']
            return jsonify(result)