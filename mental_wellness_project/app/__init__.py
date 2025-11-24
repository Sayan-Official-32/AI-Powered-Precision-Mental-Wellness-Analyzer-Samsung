from flask import Flask
from flask_cors import CORS

from app.database import init_db
from app.routes import main


def create_app():
    app = Flask(__name__, static_folder="../frontend", static_url_path="/")
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    init_db()

    @app.route("/")
    def index():
        return app.send_static_file("index.html")

    app.register_blueprint(main)
    return app
