# main.py
from flask import Flask
from dotenv import load_dotenv

load_dotenv()

from routes.board_routes import board_bp
from routes.breed_routes import breed_bp
from routes.breed_admin_routes import breed_admin_bp
from routes.user_routes import user_bp
from routes.mypage_routes import mypage_bp



from db import init_db
from dao.breed_dao import count_breeds
from dao.breed_sync import sync_breeds_from_api


def create_app() -> Flask:
    app = Flask(__name__)

    # ✅ 앱 시작할 때 DB 테이블 초기화
    with app.app_context():
        init_db()

    if count_breeds() == 0:
        print("🔄 dog_breeds 테이블이 비어있음 → DogAPI에서 자동 동기화 시작...")
        try:
            saved = sync_breeds_from_api()
            print(f"✅ 동기화 완료! 저장된 개수: {saved}")
        except Exception as e:
            print(f"❌ 동기화 실패: {e}")

    app.register_blueprint(breed_bp, url_prefix="/api")
    app.register_blueprint(breed_admin_bp, url_prefix="/api")
    app.register_blueprint(board_bp, url_prefix="/api")             # 게시판 API: /api/posts
    app.register_blueprint(user_bp, url_prefix="/api")
    app.register_blueprint(mypage_bp, url_prefix="/api")
    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)



