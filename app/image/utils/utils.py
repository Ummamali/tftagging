from app.utils.utilFuncs import move_files
from app.utils.database import DBConnection
from bson import ObjectId
import os


def move_media_from_temp(media_items, user_id, dest_bucket_name, tags_to_insert={}):
    # first we move them in the database
    with DBConnection() as db:
        col_ocean = db['ocean']
        new_item_for_bucket = []
        for item_title in media_items:
            media_object = {'path': '/', 'title': item_title,
                            'tags': tags_to_insert.get(item_title, {'object': [], 'person': []})}
            new_item_for_bucket.append(media_object)

        db.ocean.update_one(
            {"_id": ObjectId(user_id), "buckets.name": dest_bucket_name},
            {"$push": {"buckets.$.items": {'$each': new_item_for_bucket}}}
        )

        # then we move them in real storage
        source_folder_path = os.path.join(
            os.getcwd(), 'content', user_id, '_temp')
        dest_folder_path = os.path.join(
            os.getcwd(), 'content', user_id, dest_bucket_name)
        move_files(source_folder_path, dest_folder_path, media_items)
    return True
