# main.py
from flask import Flask
from dotenv import load_dotenv

# ✅ 1) .env를 제일 먼저 읽는다
load_dotenv()

# ✅ 2) 그 다음에 라우트들을 import
from routes.thedogapi import dogapi_route
from routes.dog_translate import dog_translate_route  # 번역 라우트도 같이 등록 가능

def create_app() -> Flask:
    app = Flask(__name__)

    # /api 밑에 dogapi 라우트 등록
    app.register_blueprint(dogapi_route, url_prefix="/api")
    app.register_blueprint(dog_translate_route, url_prefix="/api")  # 번역 API: /api/translate/dog

    return app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)



