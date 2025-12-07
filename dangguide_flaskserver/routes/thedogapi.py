# routes/thedogapi.py

from __future__ import annotations
from typing import List, Dict, Any, Optional
import os
import requests
from deep_translator import GoogleTranslator

# ---- 설정 ----
DOG_API_BASE_URL = "https://api.thedogapi.com/v1"
DOG_API_KEY = os.getenv("DOG_API_KEY")
HTTP_TIMEOUT = 5

session: Optional[requests.Session] = None
translator = GoogleTranslator(source="en", target="ko")


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


# ✅ 전체 견종 리스트 가져오기 (limit/page 안 씀 = 전부)
def fetch_all_breeds() -> List[Dict[str, Any]]:
    s = _get_session()

    resp = s.get(f"{DOG_API_BASE_URL}/breeds", timeout=HTTP_TIMEOUT)

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


# (원래 함수가 필요하면 남겨두고, 내부에서 위 함수 재사용하게 해도 됨)
def fetch_breeds(limit: int) -> List[Dict[str, Any]]:
    """
    옛날 코드 호환용: limit가 충분히 크면 사실상 전체.
    새로 짤 땐 fetch_all_breeds()를 직접 쓰는 걸 추천.
    """
    all_breeds = fetch_all_breeds()
    # 너무 적게 잘려나가는 문제 방지용: limit이 전체보다 크면 그냥 전체 리턴
    if limit >= len(all_breeds):
        return all_breeds
    return all_breeds[:limit]


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

def fetch_all_breeds() -> List[Dict[str, Any]]:
    s = _get_session()

    all_items = []
    page = 0

    while True:
        params = {"limit": 50, "page": page}
        resp = s.get(f"{DOG_API_BASE_URL}/breeds",
                     params=params, timeout=HTTP_TIMEOUT)

        if resp.status_code != 200:
            break

        items = resp.json()
        if not items:
            break  # 더 이상 없음

        all_items.extend(items)
        page += 1

    return all_items
