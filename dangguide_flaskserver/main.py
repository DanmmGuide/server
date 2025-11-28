# main.py
from flask import Flask
from dotenv import load_dotenv
from routes.thedogapi import dogapi_route

load_dotenv()  # .env 읽어오기

def create_app() -> Flask:
    app = Flask(__name__)

    # /api 밑에 dogapi 라우트 등록
    app.register_blueprint(dogapi_route, url_prefix="/api")

    return app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
