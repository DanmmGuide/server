from typing import List, Dict, Any
from db import get_conn


def save_breed(breed: Dict[str, Any]):
    """DogAPI에서 받은 데이터를 dog_breeds 테이블에 저장/업데이트"""
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        INSERT OR REPLACE INTO dog_breeds (
            id,
            name_en, name_ko,
            temperament_en, temperament_ko,
            bred_for_en, bred_for_ko,
            breed_group_en, breed_group_ko,
            life_span_en, life_span_ko,
            origin_en, origin_ko,
            weight_kg, height_cm,
            image_url
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        breed["id"],
        breed.get("name_en"), breed.get("name_ko"),
        breed.get("temperament_en"), breed.get("temperament_ko"),
        breed.get("bred_for_en"), breed.get("bred_for_ko"),
        breed.get("breed_group_en"), breed.get("breed_group_ko"),
        breed.get("life_span_en"), breed.get("life_span_ko"),
        breed.get("origin_en"), breed.get("origin_ko"),
        breed.get("weight_kg"), breed.get("height_cm"),
        breed.get("image_url"),
    ))

    conn.commit()
    conn.close()


def get_all_breeds() -> List[Dict[str, Any]]:
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""SELECT * FROM dog_breeds ORDER BY id ASC""")
    rows = cur.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def get_breed_by_id(breed_id: int):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""SELECT * FROM dog_breeds WHERE id = ?""", (breed_id,))
    row = cur.fetchone()
    conn.close()

    return dict(row) if row else None

def count_breeds() -> int:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) AS cnt FROM dog_breeds")
    row = cur.fetchone()
    conn.close()
    return row["cnt"]

