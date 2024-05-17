
from app.utils.database import DBConnectionStatic
from numpy import array, float32


def load_global_embeddings():
    global_embeddings = {}
    with DBConnectionStatic('mongodb://127.0.0.1:27017/', 'tagfolio') as db:
        documents = list(db['facial_embeddings'].find())
        for item in documents:
            global_embeddings[item['personId']] = {
                'first': array(item['first'], dtype=float32), 'second': array(item['second'], dtype=float32)}
    return global_embeddings


# if __name__ == '__main__':
#    known_embeddings = load_embeddings('known_embeddings.json')
#    test_embedding = get_embedding(cv2.imread('kajol.jpg'))
#    similarity = 1 - cosine(test_embedding, known_embeddings['imranKhan'])
#    print(similarity)
