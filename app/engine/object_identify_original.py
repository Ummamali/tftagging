import tensorflow as tf
import cv2
import numpy as np
import pprint
import tensorflow_hub as hub
from app.engine.words import find_representative_words
import os


def analyze_resnet(image):
    model = tf.keras.applications.ResNet50V2(
        weights="imagenet", input_shape=(224, 224, 3)
    )

    # Load an image
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    # Resize image to match the model's input size
    image_resized = cv2.resize(image, (224, 224))

    # Preprocess the image
    image_resized = tf.keras.applications.mobilenet_v2.preprocess_input(image_resized)

    # Expand dimensions to create a batch (required by the model)
    input_tensor = tf.expand_dims(image_resized, 0)

    # Make predictions
    predictions = model.predict(input_tensor)

    # Decode predictions
    decoded_predictions = tf.keras.applications.mobilenet_v2.decode_predictions(
        predictions
    )
    ans = []
    # Print the top predicted classes
    for imagenet_id, label, score in decoded_predictions[0]:
        ans.append((label, score))
    return ans


def analyze_densenet(image):
    model = tf.keras.applications.DenseNet201(
        weights="imagenet", input_shape=(224, 224, 3)
    )

    # Load an image
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    # Resize image to match the model's input size
    image_resized = cv2.resize(image, (224, 224))

    # Preprocess the image
    image_resized = tf.keras.applications.mobilenet_v2.preprocess_input(image_resized)

    # Expand dimensions to create a batch (required by the model)
    input_tensor = tf.expand_dims(image_resized, 0)

    # Make predictions
    predictions = model.predict(input_tensor)

    # Decode predictions
    decoded_predictions = tf.keras.applications.mobilenet_v2.decode_predictions(
        predictions
    )
    ans = []
    # Print the top predicted classes
    for imagenet_id, label, score in decoded_predictions[0]:
        ans.append((label, score))
    return ans


def get_tags_whole_object(image, network="RESNET"):
    analyzer = {"RESNET": analyze_resnet, "DENSENET": analyze_densenet}
    result = analyzer[network](image)
    tags = [item[0] for item in result[0:4]]
    reps = find_representative_words(tags)
    reps_words = [w[0] for w in reps]
    tags += reps_words
    return tags
