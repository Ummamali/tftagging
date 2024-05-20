from app.engine.facial.embed_known_faces import migrate_global_embeddings
import json
from app.utils.database import DBConnectionStatic

if __name__ == '__main__':
    if input('Calculate facial embeddings again? ') == 'y':
        migrate_global_embeddings()
    if input('Also load related tags? ') == 'y':
        with open('./people_tags.json') as f:
            data = json.load(f)
            for person_id, tags in data.items():
                with DBConnectionStatic('mongodb://127.0.0.1:27017/', 'tagfolio') as db:
                    embeddings_col = db['facial_embeddings']
                    embeddings_col.update_one({'personId': person_id}, {
                                              '$set': {'tags': tags}})
            print('Associated tags have been added')
