from app.utils.utilFuncs import move_files
from app.utils.database import DBConnection
from bson import ObjectId
import os


def move_media_from_temp(media_items, user_id, dest_bucket_name, tags_to_insert={}):
    # first we move them in the database

    # then we move them in real storage
    source_folder_path = os.path.join(
        os.getcwd(), 'content', user_id, '_temp')
    dest_folder_path = os.path.join(
        os.getcwd(), 'content', user_id, dest_bucket_name)
    move_files(source_folder_path, dest_folder_path, media_items)
    return True
