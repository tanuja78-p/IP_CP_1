from flask import Flask
from backend.routes.analysis import analysis_bp

def create_app():
    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024
    app.register_blueprint(analysis_bp, url_prefix="/api")
    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
