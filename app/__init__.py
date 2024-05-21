# app/__init__.py

import os
from flask_jwt_extended import JWTManager
from datetime import timedelta

from flask import Flask, jsonify
from colorama import Fore, Style
from flask_cors import CORS

from app.engine.facial.load_embeddings import load_global_embeddings
from app.engine.facial.recognize import recognize_faces

from app.utils.database import db_alive


def create_app():

    app = Flask(__name__)
    CORS(app)

    jwt = JWTManager(app)

    # Connections with database
    app.config["DB_URI"] = f"mongodb://127.0.0.1:27017/"
    app.config["DB_NAME"] = "tagfolio"
    # JWT and other stuff
    app.config["JWT_SECRET_KEY"] = "super-secret"
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=6)
    app.config["CONTENT-DIRECTORY"] = os.path.join(os.getcwd(), "content")
    app.config["TEMP_FOLDER_PATH"] = os.path.join(
        os.getcwd(), "app", "engine", "facial", "_temp"
    )
    app.config["BRAIN_PATH"] = os.path.join(os.getcwd(), "app", "engine", "facial")

    app.config["global_embeddings"] = load_global_embeddings()
    print(Fore.BLUE, "Loading global embeddings....", Style.RESET_ALL)

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
        return jsonify(
            {
                "status": 200,
                "msg": "Tagfolio Tagging Engine: Working!",
                "service": "Tagfolio Tagging Engine",
            }
        )

    # Import the routes to register them with the app
    # from app.image.routes import image_bp
    from app.chat.routes import chat_bp

    # Register the blueprints
    # app.register_blueprint(image_bp, url_prefix="/image")
    app.register_blueprint(chat_bp, url_prefix="/chat")

    return app
