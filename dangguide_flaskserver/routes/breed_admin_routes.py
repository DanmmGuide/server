from flask import Blueprint, jsonify
from dao.breed_dao import save_breed
from routes.thedogapi import fetch_breeds, normalize_breed, translate_breed

breed_admin_bp = Blueprint("breed_admin", __name__)


@breed_admin_bp.post("/admin/sync_breeds")
def sync_breeds():
    """DogAPI에서 종 정보를 가져와 DB에 저장"""
    try:
        raw_breeds = fetch_breeds(limit=200)  # DogAPI 최대 172종
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

    count = 0
    for raw in raw_breeds:
        breed = normalize_breed(raw)
        breed = translate_breed(breed)  # 한국어 번역
        save_breed(breed)
        count += 1

    return jsonify({"ok": True, "saved": count}), 200
