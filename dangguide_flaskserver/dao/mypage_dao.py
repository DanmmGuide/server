# dangguide_flaskserver/dao/mypage_dao.py
from __future__ import annotations

from typing import Optional, Dict, Any

from db import get_conn


def get_user_profile(user_id: int) -> Optional[Dict[str, Any]]:
    """
    user_profiles 테이블에서 해당 user_id의 프로필을 한 건 조회.
    없으면 None 반환.
    """
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT
            guardian_name,
            pet_name,
            species,
            birth,
            gender,
            neutered,
            weight,
            profile_image,
            updated_at
        FROM user_profiles
        WHERE user_id = ?
        """,
        (user_id,),
    )

    row = cur.fetchone()
    conn.close()

    if row is None:
        return None

    # sqlite3.Row 덕분에 키 이름으로 접근 가능
    return {
        "guardian_name": row["guardian_name"],
        "pet_name": row["pet_name"],
        "species": row["species"],
        "birth": row["birth"],
        "gender": row["gender"],
        "neutered": row["neutered"],
        "weight": row["weight"],
        "profile_image": row["profile_image"],
        "updated_at": row["updated_at"],
    }


def upsert_user_profile(user_id: int, data: Dict[str, Any]) -> None:
    """
    user_id 기준으로 user_profiles 테이블에 INSERT 또는 UPDATE.
    이미 있으면 UPDATE, 없으면 INSERT.
    """
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO user_profiles (
            user_id,
            guardian_name,
            pet_name,
            species,
            birth,
            gender,
            neutered,
            weight,
            profile_image,
            updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(user_id) DO UPDATE SET
            guardian_name = excluded.guardian_name,
            pet_name      = excluded.pet_name,
            species       = excluded.species,
            birth         = excluded.birth,
            gender        = excluded.gender,
            neutered      = excluded.neutered,
            weight        = excluded.weight,
            profile_image = excluded.profile_image,
            updated_at    = CURRENT_TIMESTAMP
        """,
        (
            user_id,
            data.get("guardian_name"),
            data.get("pet_name"),
            data.get("species"),
            data.get("birth"),
            data.get("gender"),
            data.get("neutered"),
            data.get("weight"),
            data.get("profile_image"),
        ),
    )

    conn.commit()
    conn.close()
