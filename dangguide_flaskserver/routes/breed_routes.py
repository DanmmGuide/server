from flask import Blueprint, jsonify
from dao.breed_dao import get_all_breeds, get_breed_by_id

breed_bp = Blueprint("breed", __name__)


@breed_bp.get("/breeds")
def list_breeds():
    """DB에서 전체 견종 리스트 반환"""
    breeds = get_all_breeds()
    return jsonify({"ok": True, "count": len(breeds), "breeds": breeds}), 200


@breed_bp.get("/breeds/<int:breed_id>")
def get_breed_detail(breed_id):
    """DB에서 특정 견종 상세 정보 반환"""
    breed = get_breed_by_id(breed_id)
    if not breed:
        return jsonify({"ok": False, "error": "breed not found"}), 404

    return jsonify({"ok": True, "breed": breed}), 200
