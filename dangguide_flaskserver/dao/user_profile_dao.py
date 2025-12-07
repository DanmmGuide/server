from typing import Optional, Dict, Any
from db import get_conn


def get_user_profile(user_id: int) -> Optional[Dict[str, Any]]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT user_id,
               guardian_name,
               pet_name,
               pet_species,
               pet_birth,
               pet_gender,
               pet_neutered,
               pet_weight
        FROM user_profiles
        WHERE user_id = ?
    """, (user_id,))
    row = cur.fetchone()
    conn.close()

    if row is None:
        return None

    return {
        "user_id": row["user_id"],
        "guardian_name": row["guardian_name"],
        "pet_name": row["pet_name"],
        "pet_species": row["pet_species"],
        "pet_birth": row["pet_birth"],
        "pet_gender": row["pet_gender"],
        "pet_neutered": row["pet_neutered"],
        "pet_weight": row["pet_weight"],
    }


def upsert_user_profile(user_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
    conn = get_conn()
    cur = conn.cursor()

    guardian_name = data.get("guardian_name")
    pet_name = data.get("pet_name")
    pet_species = data.get("pet_species")
    pet_birth = data.get("pet_birth")
    pet_gender = data.get("pet_gender")
    pet_neutered = data.get("pet_neutered")
    pet_weight = data.get("pet_weight")

    cur.execute("""
        INSERT INTO user_profiles (
            user_id,
            guardian_name,
            pet_name,
            pet_species,
            pet_birth,
            pet_gender,
            pet_neutered,
            pet_weight
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            guardian_name = excluded.guardian_name,
            pet_name      = excluded.pet_name,
            pet_species   = excluded.pet_species,
            pet_birth     = excluded.pet_birth,
            pet_gender    = excluded.pet_gender,
            pet_neutered  = excluded.pet_neutered,
            pet_weight    = excluded.pet_weight
    """, (
        user_id,
        guardian_name,
        pet_name,
        pet_species,
        pet_birth,
        pet_gender,
        pet_neutered,
        pet_weight,
    ))

    conn.commit()
    conn.close()

    return {
        "user_id": user_id,
        "guardian_name": guardian_name,
        "pet_name": pet_name,
        "pet_species": pet_species,
        "pet_birth": pet_birth,
        "pet_gender": pet_gender,
        "pet_neutered": pet_neutered,
        "pet_weight": pet_weight,
    }
