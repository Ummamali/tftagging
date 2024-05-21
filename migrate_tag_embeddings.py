from app.engine.chatter.utils import get_embedding
from app.utils.database import DBConnectionStatic
from bson import ObjectId


if __name__ == "__main__":
    with DBConnectionStatic("mongodb://127.0.0.1:27017", "tagfolio") as db:
        ocean_col = db["ocean"]
        users = list(ocean_col.find({}, {"_id": 1, "buckets": 1}))
        for user in users:
            doc_for_collection = {"_id": ObjectId(user["_id"]), "buckets": {}}
            for bucket in user["buckets"]:
                print("Workign on bucket", bucket["name"])
                doc_for_collection["buckets"][bucket["name"]] = []
                for media in bucket["items"]:
                    tags_emb = {"objects": None, "people": None}
                    tags_emb["objects"] = get_embedding(
                        " ".join(media["tags"]["objects"])
                    ).tolist()
                    tags_emb["people"] = get_embedding(
                        " ".join(media["tags"]["people"])
                    ).tolist()

                    box_emb = get_embedding(
                        " ".join([" ".join(item["tags"]) for item in media["boxes"]])
                    ).tolist()
                    doc_for_collection["buckets"][bucket["name"]].append(
                        {"title": media["title"], "tags": tags_emb, "boxes": box_emb}
                    )

            db["tag_embeddings"].insert_one(doc_for_collection)
    print("tags embeddings have been calculated")
