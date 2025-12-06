# routes/thedogapi.py
from __future__ import annotations

from flask import Blueprint, request, jsonify
from typing import List, Dict, Any, Optional
import os
import requests
from deep_translator import GoogleTranslator

dogapi_route = Blueprint("dogapi", __name__)

# ---- 설정 ----
DOG_API_BASE_URL = "https://api.thedogapi.com/v1"
DOG_API_KEY = os.getenv("DOG_API_KEY")
HTTP_TIMEOUT = 5

session: Optional[requests.Session] = None


def _get_session() -> requests.Session:
    global session
    if session is None:
        s = requests.Session()
        s.headers.update({
            "x-api-key": DOG_API_KEY or "",
            "Accept": "application/json",
            "User-Agent": "DangGuide-Flask/1.0",
        })
        session = s
    return session


def _ok(payload: dict, code: int = 200):
    return jsonify(payload), code


def _err(
    msg: str,
    code: int,
    *,
    error_code: str | None = None,
    details: dict | None = None
):
    body = {"ok": False, "error": msg}
    if error_code:
        body["code"] = error_code
    if details:
        body["details"] = details
    return jsonify(body), code


translator = GoogleTranslator(source="en", target="ko")


# TheDogAPI에서 견종 리스트 가져오기
def fetch_breeds(limit: int) -> List[Dict[str, Any]]:
    s = _get_session()
    params = {
        "limit": limit,
        "page": 0,
    }

    resp = s.get(f"{DOG_API_BASE_URL}/breeds",
                 params=params, timeout=HTTP_TIMEOUT)

    if resp.status_code == 401:
        raise RuntimeError(("UNAUTHORIZED", 502, "TheDogAPI 키 오류 또는 미설정"))

    if resp.status_code >= 500:
        raise RuntimeError((
            "UPSTREAM_ERROR",
            502,
            "TheDogAPI 서버 오류",
            {"status": resp.status_code},
        ))

    if resp.status_code != 200:
        raise RuntimeError((
            "UPSTREAM_BAD_RESPONSE",
            502,
            "TheDogAPI 비정상 응답",
            {"status": resp.status_code},
        ))

    try:
        return resp.json()
    except Exception as e:
        raise RuntimeError((
            "UPSTREAM_PARSE_FAILED",
            502,
            f"TheDogAPI 응답 파싱 실패: {e}",
        ))


# 필요한 필드만 정리
def normalize_breed(raw: Dict[str, Any]) -> Dict[str, Any]:
    image = raw.get("image") or {}

    return {
        "id": raw.get("id"),
        "name_en": raw.get("name"),
        "temperament_en": raw.get("temperament"),
        "bred_for_en": raw.get("bred_for"),
        "breed_group_en": raw.get("breed_group"),
        "life_span_en": raw.get("life_span"),
        "origin_en": raw.get("origin"),
        "weight_kg": raw.get("weight", {}).get("metric"),
        "height_cm": raw.get("height", {}).get("metric"),
        "image_url": image.get("url"),
    }


def translate_breed(breed: Dict[str, Any]) -> Dict[str, Any]:
    # 영어 → 한국어 필드 목록
    fields = [
        ("name_en", "name_ko"),
        ("temperament_en", "temperament_ko"),
        ("bred_for_en", "bred_for_ko"),
        ("breed_group_en", "breed_group_ko"),
        ("life_span_en", "life_span_ko"),
        ("origin_en", "origin_ko"),
    ]

    for src, dst in fields:
        text = breed.get(src)
        if text:
            try:
                breed[dst] = translator.translate(text)
            except Exception as e:
                print(f"[translate error] field={src}, text={text}, error={e}")
                breed[dst] = "(번역 실패)"

    return breed


@dogapi_route.route("/dogs/breeds", methods=["GET"])
def get_dog_breeds():
    """
    Flutter에서 호출하는 엔드포인트
    예) /api/dogs/breeds?limit=10&translate=true
    """

    # limit 처리
    try:
        limit = int(request.args.get("limit", "10"))
        if limit <= 0 or limit > 50:
            return _err(
                "limit는 1~50 사이여야 합니다.",
                400,
                error_code="INVALID_PARAM",
            )
    except ValueError:
        return _err(
            "limit는 정수여야 합니다.",
            400,
            error_code="INVALID_PARAM",
        )

    translate_flag = (
        request.args.get("translate", "false").lower()
        in ("true", "1", "yes")
    )

    if not DOG_API_KEY:
        return _err(
            "DOG_API_KEY 환경변수가 설정되지 않았습니다.",
            500,
            error_code="NO_API_KEY",
        )

    # API 호출
    try:
        raw_breeds = fetch_breeds(limit)
    except RuntimeError as re:
        if isinstance(re.args[0], tuple):
            code, http, msg, *rest = re.args[0]
            details = rest[0] if rest else None
        else:
            code, http, msg = ("UPSTREAM_ERROR", 502, str(re))
            details = None

        return _err(msg, http, error_code=code, details=details)
    except Exception as e:
        return _err(
            "알 수 없는 서버 오류",
            500,
            error_code="UNKNOWN_ERROR",
            details={"reason": str(e)},
        )

    # 정규화 + 번역
    breeds: List[Dict[str, Any]] = []
    for raw in raw_breeds:
        b = normalize_breed(raw)
        if translate_flag:
            b = translate_breed(b)
        breeds.append(b)

    return _ok({
        "ok": True,
        "count": len(breeds),
        "breeds": breeds,
    })