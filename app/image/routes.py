from flask import Blueprint

image_bp = Blueprint("image", __name__)

from . import image
