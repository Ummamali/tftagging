# app/__init__.py

import os
from flask_jwt_extended import JWTManager
from datetime import timedelta

from flask import Flask, jsonify
from colorama import Fore, Style
from flask_cors import CORS

from app.utils.database import db_alive
from app.engine.object_identify_original import get_tags_whole_object


def create_app():

    app = Flask(__name__)
    CORS(app)

    jwt = JWTManager(app)

    # Connections with database
    app.config["DB_USER"] = "application"
    app.config["DB_PASSWORD"] = "tf123"
    app.config["DB_URI"] = (
        f'mongodb://{app.config["DB_USER"]
                     }:{app.config["DB_PASSWORD"]}@127.0.0.1:9000/'
    )
    app.config["DB_NAME"] = "tagfolio"
    # JWT and other stuff
    app.config["JWT_SECRET_KEY"] = "super-secret"
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=6)
    app.config['CONTENT-DIRECTORY'] = os.path.join(os.getcwd(), "content")

    # Monitoring the environment variable (No env variables yet so comment it)
    # if any(
    #     item is None for item in (app.config["MAIL_EMAIL"], app.config["MAIL_PASSWORD"])
    # ):
    #     print(
    #         Fore.RED
    #         + "WARNING! Environment variables not set properly!"
    #         + Style.RESET_ALL
    #     )

    # Monitoring the database
    if not db_alive(app.config["DB_URI"]):
        print(Fore.RED + "WARNING! Unable to ping the database!" + Style.RESET_ALL)

    # The main / route to ping the whole server
    @app.route("/", methods=("GET",))
    def home():
        print(get_tags_whole_object('603f5b40872f4f94a26d027e',
              'bucketone', 'car.jpg', network='DENSENET'))
        return jsonify(
            {
                "status": 200,
                "msg": "Tagfolio Tagging Engine: Working!",
                "service": "Tagfolio Tagging Engine",
            }
        )

    # Import the routes to register them with the app
    from app.image.routes import image_bp

    # Register the blueprints
    app.register_blueprint(image_bp, url_prefix="/image")

    return app
