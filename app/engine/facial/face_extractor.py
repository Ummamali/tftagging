import cv2
from mtcnn.mtcnn import MTCNN


def extract_faces(image, extra_width=0.1, extra_height=0.1):
    # Load the image

    # Initialize the MTCNN face detection model with tuned parameters
    detector = MTCNN(min_face_size=20, scale_factor=0.72)

    # Detect faces in the image
    faces = detector.detect_faces(image)

    image_height, image_width, chnl = image.shape

    face_images = []
    # Extract and save each detected face
    extra_vertical = int((image_height * extra_height) / 2)
    extra_horizontal = int((image_width * extra_width) / 2)
    for face in faces:
        x, y, w, h = face['box']

        vertical_start = y - extra_vertical if y - extra_vertical > 0 else y
        vertical_end = vertical_start + h + extra_vertical if vertical_start + \
            h + extra_vertical < image_height else vertical_start + h

        horizontal_start = x - extra_horizontal if x - extra_horizontal > 0 else x
        horizontal_end = horizontal_start + w + \
            extra_horizontal if horizontal_start + \
            w + extra_horizontal < image_width else horizontal_start + w
        face_img = image[vertical_start:vertical_end,
                         horizontal_start:horizontal_end]
        face_images.append(face_img)
    return face_images
