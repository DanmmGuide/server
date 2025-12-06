# main.py
from flask import Flask
from dotenv import load_dotenv

# ✅ 1) .env를 제일 먼저 읽는다
load_dotenv()

# ✅ 2) 그 다음에 라우트들을 import
from routes.thedogapi import dogapi_route
from routes.dog_translate import dog_translate_route  # 번역 라우트
from routes.board_routes import board_bp             # ✅ 게시판 라우트
from db import init_db                              # ✅ DB 초기화 함수
from routes.user_routes import user_bp


def create_app() -> Flask:
    app = Flask(__name__)

    # ✅ 앱 시작할 때 DB 테이블 초기화
    with app.app_context():
        init_db()

    # /api 밑에 라우트 등록
    app.register_blueprint(dogapi_route, url_prefix="/api")
    app.register_blueprint(dog_translate_route, url_prefix="/api")  # 번역 API: /api/translate/dog
    app.register_blueprint(board_bp, url_prefix="/api")             # 게시판 API: /api/posts
    app.register_blueprint(user_bp, url_prefix="/api")
    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)



