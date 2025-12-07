from dao.breed_dao import save_breed
from routes.thedogapi import fetch_breeds, normalize_breed, translate_breed


def sync_breeds_from_api(limit: int = 200) -> int:
    """
    DogAPI에서 breed 정보를 가져와 DB에 저장.
    return: 저장된 개수
    """
    raw_breeds = fetch_breeds(limit)
    count = 0

    for raw in raw_breeds:
        breed = normalize_breed(raw)
        breed = translate_breed(breed)
        save_breed(breed)
        count += 1

    return count
