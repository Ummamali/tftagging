import os
from app.utils.database import DBConnectionStatic
import cv2
import numpy as np
from facenet_pytorch import MTCNN, InceptionResnetV1
import json
from bson import ObjectId

# Initialize MTCNN and Inception Resnet V1 models
mtcnn = MTCNN()
resnet = InceptionResnetV1(pretrained='vggface2').eval()

known_faces = {"imranKhan": {"face_img": "imranKhan.jpg", "embedding": None}}


def get_embedding(image):
    # Detect face and return the embedding
    face = mtcnn(image)
    if face is not None:
        face = face.unsqueeze(0)
        embedding = resnet(face)
        return embedding.detach().numpy().flatten()
    else:
        return None


def migrate_global_embeddings():
    global_faces_path = os.path.join(
        os.getcwd(), 'app', 'engine', 'facial', 'global_known_faces')
    persosnalities = [d for d in os.listdir(
        global_faces_path) if os.path.isdir(os.path.join(global_faces_path, d))]
    new_embeddings = {}
    for person_id in persosnalities:
        emb_obj = {}
        first_emb = get_embedding(cv2.imread(
            os.path.join(global_faces_path, person_id, 'first.jpg')))
        emb_obj['first'] = first_emb.tolist(
        ) if first_emb is not None else None
        if os.path.exists(os.path.join(global_faces_path, person_id, 'second.jpg')):
            second_emb = get_embedding(cv2.imread(
                os.path.join(global_faces_path, person_id, 'second.jpg')))
            emb_obj['second'] = second_emb.tolist(
            ) if second_emb is not None else None
        else:
            emb_obj['second'] = None
        new_embeddings[person_id] = emb_obj

    with DBConnectionStatic('mongodb://127.0.0.1:27017/', 'tagfolio') as db:
        embeddings_col = db['facial_embeddings']
        documents = []
        for person_id, embedding in new_embeddings.items():
            exists = embeddings_col.find_one(
                {'personId': person_id}) is not None
            if not exists:
                documents.append(
                    {'personId': person_id, 'first': embedding['first'], 'second': embedding['second']})
        embeddings_col.insert_many(documents)
        print('embeddings have been migrated to database')


# def calculate_known_face_embeddings(faces_directory_path):
#     embeddings = {}
#     for person_id, person_data in known_faces.items():
#         img = cv2.imread(os.path.join(
#             faces_directory_path, person_data['face_img']))
#         img_emb = get_embedding(img)
#         embeddings[person_id] = img_emb
#     return embeddings


# if __name__ == "__main__":
#     print('Calculating first embeddings...........')
#     first_directory = os.path.join(os.getcwd(), 'known_faces', 'first')
#     embs = calculate_known_face_embeddings(first_directory)
#     for person_id, embedding in embs.items():
#         embs[person_id] = embedding.tolist()
#     with open('known_embeddings_first.json', 'w') as f:
#         json.dump(embs, f)
#         print('First Embeddings has been dumped')

#     print('Calculating second embeddings...........')
#     second_directory = os.path.join(os.getcwd(), 'known_faces', 'second')
#     embs = calculate_known_face_embeddings(second_directory)
#     for person_id, embedding in embs.items():
#         embs[person_id] = embedding.tolist()
#     with open('known_embeddings_second.json', 'w') as f:
#         json.dump(embs, f)
#         print('Second embeddings has been dumped')
