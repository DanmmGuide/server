# db.py
import sqlite3
from pathlib import Path

# 같은 폴더에 DB 파일 생성
DB_PATH = Path(__file__).parent / "dangguide_server.db"


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # dict처럼 접근 가능
    return conn


def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            content TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            like_count INTEGER DEFAULT 0,
            comment_count INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS post_images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER NOT NULL,
            image_path TEXT NOT NULL,
            FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS comments
        (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            post_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS post_likes
    (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        post_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(post_id, user_id),   -- 같은 유저가 같은 글을 두 번 좋아요할 수 없음
        FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS breed_guides (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            -- 외부 데이터와 매칭할 ID (TheDogAPI)
            breed_id INTEGER NOT NULL UNIQUE,

            -- 견종명(영문/한글)
            breed_name TEXT NOT NULL,
            breed_name_kr TEXT,     -- 번역된 이름 저장 가능

            -- 기본 정보
            life_span TEXT,
            weight_range TEXT,
            height_range TEXT,

            -- 성격 및 수치화된 평가
            temperament TEXT,         -- 성격 한 줄 텍스트
            energy_level INTEGER,      -- 1~5
            friendliness INTEGER,      -- 친화력 1~5
            trainability INTEGER,      -- 훈련 난이도 1~5
            shedding_level INTEGER,    -- 털빠짐 1~5
            grooming_level INTEGER,    -- 관리 난이도 1~5
            bark_level INTEGER,        -- 짖음 빈도 1~5

            -- 가이드 요소(앱에서 보여줄 핵심 텍스트)
            summary TEXT,              -- 한 줄 요약
            care_tips TEXT,            -- 관리 팁
            caution TEXT               -- 주의사항
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS user_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_id INTEGER NOT NULL UNIQUE,   -- users 테이블과 1:1 매칭

            guardian_name TEXT,
            pet_name TEXT,
            species TEXT,
            birth TEXT,
            gender TEXT,
            neutered TEXT,
            weight TEXT,

            profile_image TEXT,                -- 이미지 경로 저장

            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
    """)

    conn.commit()
    conn.close()