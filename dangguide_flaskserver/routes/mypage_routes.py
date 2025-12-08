# dangguide_flaskserver/routes/mypage_routes.py
from __future__ import annotations

from flask import Blueprint, request, jsonify

from dao.mypage_dao import get_user_profile, upsert_user_profile

mypage_bp = Blueprint("mypage", __name__)


def _empty_profile() -> dict:
    """
    처음 마이페이지 들어온 유저처럼,
    아직 user_profiles 레코드가 없을 때 돌려줄 기본값.
    Flutter에서 data["..."] 할 때 에러 안 나도록
    키를 전부 만들어 준다.
    """
    return {
        "guardian_name": "",
        "pet_name": "",
        "species": "",
        "birth": "",
        "gender": "",
        "neutered": "",
        "weight": "",
        "profile_image": None,
        "updated_at": None,
    }


@mypage_bp.get("/my_page/<int:user_id>")
def get_my_page(user_id: int):
    """
    GET /api/my_page/<user_id>

    - 프로필이 있으면 해당 값 반환
    - 없으면 빈 프로필 구조 반환
    """
    profile = get_user_profile(user_id)

    if profile is None:
        return jsonify(_empty_profile()), 200

    # Flutter MyPage에서 사용하는 키 그대로 전달
    return jsonify(profile), 200


@mypage_bp.put("/my_page/<int:user_id>")
def update_my_page(user_id: int):
    """
    PUT /api/my_page/<user_id>
    body(JSON 예):
    {
      "guardian_name": "...",
      "pet_name": "...",
      "species": "...",
      "birth": "...",
      "gender": "...",
      "neutered": "...",
      "weight": "...",
      "profile_image": "이미지 경로(optional)"
    }
    """
    data = request.get_json(silent=True) or {}

    # Flutter에서 아직 profile_image 안 보내면 None으로 처리
    normalized = {
        "guardian_name": data.get("guardian_name"),
        "pet_name": data.get("pet_name"),
        "species": data.get("species"),
        "birth": data.get("birth"),
        "gender": data.get("gender"),
        "neutered": data.get("neutered"),
        "weight": data.get("weight"),
        "profile_image": data.get("profile_image"),
    }

    upsert_user_profile(user_id, normalized)

    return jsonify({"ok": True}), 200
