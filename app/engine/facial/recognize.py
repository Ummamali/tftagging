from scipy.spatial.distance import cosine


def recognize_faces(face_embeddings: list, local_embeddings: dict, global_embeddings: dict):
    # faces = extract_faces(image_path)

    # face_embeddings = []
    # for face_img in faces:
    #   face_embeddings.append(get_embedding(face_img))

    found = {'confident': set(), 'blurry': set()}

    # first we lookup all local embeddings
    for known_person, known_person_em in local_embeddings.items():
        for i, unknown_em in enumerate(face_embeddings):
            if unknown_em is not None:
                similarity = 1 - cosine(known_person_em['first'], unknown_em)
                second_similarity = 1 - \
                    cosine(known_person_em['second'], unknown_em)
                print(f'{known_person} <-----> face-{i} >>>> {similarity}')
                print(
                    f'   {known_person} <-----> face-{i} >>>> {second_similarity}')
                if similarity > 0.6 or second_similarity > 0.6:
                    found['confident'].add(known_person)
                elif similarity > 0.5 or second_similarity > 0.5:
                    found['blurry'].add(known_person)

  # then we lookup global embeddings
    for known_person, known_person_em in global_embeddings.items():
        for i, unknown_em in enumerate(face_embeddings):
            if unknown_em is not None:
                similarity = 1 - cosine(known_person_em['first'], unknown_em)
                second_similarity = 1 - \
                    cosine(known_person_em['second'], unknown_em)
                print(f'{known_person} <-----> face-{i} >>>> {similarity}')
                print(
                    f'   {known_person} <-----> face-{i} >>>> {second_similarity}')
                if similarity > 0.6 or second_similarity > 0.6:
                    found['confident'].add(known_person)
                elif similarity > 0.5 or second_similarity > 0.5:
                    found['blurry'].add(known_person)

    return {'confident': list(found['confident']), 'blurry': list(found['blurry'])}
