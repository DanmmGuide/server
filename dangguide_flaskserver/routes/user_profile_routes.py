from flask import Blueprint, request, jsonify
from dao.user_profile_dao import get_user_profile, upsert_user_profile

user_profile_bp = Blueprint("user_profile", __name__)


# 현재 유저 프로필 조회
@user_profile_bp.get("/users/<int:user_id>/profile")
def get_profile_route(user_id: int):
    profile = get_user_profile(user_id)
    if profile is None:
        # 아직 프로필이 없으면 비어있는 값으로 내려주기
        profile = {
            "user_id": user_id,
            "guardian_name": None,
            "pet_name": None,
            "pet_species": None,
            "pet_birth": None,
            "pet_gender": None,
            "pet_neutered": None,
            "pet_weight": None,
        }
    return jsonify({"ok": True, "profile": profile}), 200


# 프로필 저장/업데이트
@user_profile_bp.put("/users/<int:user_id>/profile")
def update_profile_route(user_id: int):
    data = request.get_json(silent=True) or {}

    profile = upsert_user_profile(user_id, data)
    return jsonify({"ok": True, "profile": profile}), 200
