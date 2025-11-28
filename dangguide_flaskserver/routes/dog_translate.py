# routes/dog_translate.py
from __future__ import annotations
from flask import Blueprint, request, jsonify
from typing import Dict, Any, Optional
from deep_translator import GoogleTranslator

dog_translate_route = Blueprint("dog_translate", __name__)

def _ok(payload: dict, code: int = 200):
    return jsonify(payload), code

def _err(msg: str, code: int, *, error_code: str | None = None, details: dict | None = None):
    body = {"ok": False, "error": msg}
    if error_code:
        body["code"] = error_code
    if details:
        body["details"] = details
    return jsonify(body), code

translator = GoogleTranslator(source="en", target="ko")

@dog_translate_route.route("/translate/dog", methods=["POST"])
def translate_dog():
    """
    TheDogAPI에서 가져온 한 견종 정보를 받아서 번역하는 엔드포인트

    요청 예시(JSON):
    {
      "name": "Labrador Retriever",
      "temperament": "Friendly, Active, Outgoing",
      "bred_for": "Water retrieving",
      "breed_group": "Sporting",
      "life_span": "10 - 12 years",
      "origin": "Canada, United Kingdom"
    }
    """
    data = request.get_json(silent=True) or {}
    names: List[str] = data.get("names") or []

    if not isinstance(names, list) or not names:
        return _err("names 리스트가 필요합니다.", 400, error_code="INVALID_BODY")

    fields_to_translate = [
        "name",
        "temperament",
        "bred_for",
        "breed_group",
        "life_span",
        "origin",
    ]

    result: Dict[str, Any] = {}

    # 원본 값 복사
    for field in fields_to_translate:
        if field in data:
            result[field] = data[field]

    # 번역 값 추가
    for field in fields_to_translate:
        text: Optional[str] = data.get(field)
        if text:
            try:
                translated = translator.translate(text)
            except Exception as e:
                translated = "(번역 실패)"
                print(f"[translate error] field={field}, text={text}, error={e}")
            result[f"{field}_ko"] = translated

    return _ok({"ok": True, "translated": result})
