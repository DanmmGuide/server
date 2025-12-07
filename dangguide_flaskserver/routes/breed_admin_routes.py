from flask import Blueprint, jsonify
from dao.breed_dao import save_breed
from routes.thedogapi import fetch_breeds, normalize_breed, translate_breed

breed_admin_bp = Blueprint("breed_admin", __name__)


@breed_admin_bp.post("/admin/sync_breeds")
def sync_breeds():
    """DogAPI에서 종 정보를 가져와 DB에 저장 + 진행률 출력"""

    print("\n==============================")
    print("🔄 DogAPI 품종 동기화 시작")
    print("==============================")

    # 1) 전체 목록 가져오기
    try:
        print("📡 DogAPI에서 품종 가져오는 중...")
        raw_breeds = fetch_breeds(limit=200)
    except Exception as e:
        print(f"❌ DogAPI fetch 실패: {e}")
        return jsonify({"ok": False, "error": str(e)}), 500

    total = len(raw_breeds)
    print(f"📥 총 {total}개 수신 완료\n")

    # 2) 번역 + 저장
    print("📝 번역 + DB 저장 중...\n")
    count = 0

    for idx, raw in enumerate(raw_breeds):
        breed = normalize_breed(raw)
        breed = translate_breed(breed)

        save_breed(breed)
        count += 1

        # --- 진행률 출력 (20개 단위로 표시) ---
        if idx % 20 == 0:
            print(f"  진행률: {idx}/{total}")

    print("\n🎉 동기화 완료!")
    print(f"총 {count}개 저장됨")
    print("==============================\n")

    return jsonify({"ok": True, "saved": count}), 200
