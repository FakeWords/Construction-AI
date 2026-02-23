"""
Fieldwise AI - Database Layer
PostgreSQL connection and schema management
"""

import os
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
except ImportError:
    psycopg2 = None
    RealDictCursor = None
from contextlib import contextmanager

DATABASE_URL = os.environ.get("DATABASE_URL")



@contextmanager
def get_db():
    """Get database connection as context manager"""
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    """Initialize database schema"""
    with get_db() as conn:
        cur = conn.cursor()

        # Users table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                company VARCHAR(255),
                created_at TIMESTAMP DEFAULT NOW(),
                last_login TIMESTAMP
            )
        """)

        # Projects table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                name VARCHAR(255) NOT NULL,
                trade VARCHAR(100),
                code_book VARCHAR(100),
                filename VARCHAR(255),
                analysis TEXT,
                excel_filename VARCHAR(255),
                status VARCHAR(50) DEFAULT 'complete',
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            )
        """)

        # Project shares table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS project_shares (
                id SERIAL PRIMARY KEY,
                project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
                shared_by_user_id INTEGER REFERENCES users(id),
                shared_with_email VARCHAR(255) NOT NULL,
                permission VARCHAR(50) DEFAULT 'view',
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)

        print("[DB] Schema initialized successfully")


def get_user_by_email(email: str):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        return cur.fetchone()


def get_user_by_id(user_id: int):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        return cur.fetchone()


def create_user(name: str, email: str, password_hash: str, company: str = None):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO users (name, email, password_hash, company) VALUES (%s, %s, %s, %s) RETURNING *",
            (name, email, password_hash, company)
        )
        return cur.fetchone()


def update_last_login(user_id: int):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("UPDATE users SET last_login = NOW() WHERE id = %s", (user_id,))


def create_project(user_id: int, name: str, trade: str, code_book: str,
                   filename: str, analysis: str, excel_filename: str):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO projects (user_id, name, trade, code_book, filename, analysis, excel_filename)
            VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING *
        """, (user_id, name, trade, code_book, filename, analysis, excel_filename))
        return cur.fetchone()


def get_user_projects(user_id: int):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT * FROM projects WHERE user_id = %s ORDER BY created_at DESC
        """, (user_id,))
        return cur.fetchall()


def get_project_by_id(project_id: int):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM projects WHERE id = %s", (project_id,))
        return cur.fetchone()


def delete_project(project_id: int, user_id: int):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            "DELETE FROM projects WHERE id = %s AND user_id = %s",
            (project_id, user_id)
        )


def share_project(project_id: int, shared_by: int, shared_with_email: str, permission: str = "view"):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO project_shares (project_id, shared_by_user_id, shared_with_email, permission)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT DO NOTHING RETURNING *
        """, (project_id, shared_by, shared_with_email, permission))
        return cur.fetchone()


def get_shared_projects(email: str):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT p.*, ps.permission, u.name as owner_name
            FROM projects p
            JOIN project_shares ps ON p.id = ps.project_id
            JOIN users u ON p.user_id = u.id
            WHERE ps.shared_with_email = %s
            ORDER BY p.created_at DESC
        """, (email,))
        return cur.fetchall()
