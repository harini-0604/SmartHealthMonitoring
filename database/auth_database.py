import sqlite3
import hashlib
from pathlib import Path


# ============================================================
# DATABASE PATH
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
AUTH_DB = PROJECT_ROOT / "database" / "users.db"


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

def initialize_auth_database():

    connection = sqlite3.connect(AUTH_DB)

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'patient'
        )
    """)

    connection.commit()
    connection.close()


# ============================================================
# PASSWORD HASHING
# ============================================================

def hash_password(password):

    return hashlib.sha256(
        password.encode("utf-8")
    ).hexdigest()


# ============================================================
# CREATE ACCOUNT
# ============================================================

def create_user(
    full_name,
    username,
    email,
    password,
    role="patient"
):

    initialize_auth_database()

    connection = sqlite3.connect(AUTH_DB)

    cursor = connection.cursor()

    try:

        cursor.execute("""
            INSERT INTO users
            (full_name, username, email, password, role)
            VALUES (?, ?, ?, ?, ?)
        """, (
            full_name,
            username,
            email,
            hash_password(password),
            role
        ))

        connection.commit()

        return True, "Account created successfully."

    except sqlite3.IntegrityError as error:

        if "username" in str(error).lower():

            return False, "Username already exists."

        if "email" in str(error).lower():

            return False, "Email already exists."

        return False, "Account could not be created."

    finally:

        connection.close()


# ============================================================
# LOGIN
# ============================================================

def verify_user(
    username,
    password,
    role
):

    initialize_auth_database()

    connection = sqlite3.connect(AUTH_DB)

    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, full_name, username, email, role
        FROM users
        WHERE username = ?
        AND password = ?
        AND role = ?
    """, (
        username,
        hash_password(password),
        role
    ))

    user = cursor.fetchone()

    connection.close()

    return user


# ============================================================
# CHECK USER
# ============================================================

def user_exists(username, email=None):

    initialize_auth_database()

    connection = sqlite3.connect(AUTH_DB)

    cursor = connection.cursor()

    if email:

        cursor.execute("""
            SELECT id
            FROM users
            WHERE username = ?
            AND email = ?
        """, (
            username,
            email
        ))

    else:

        cursor.execute("""
            SELECT id
            FROM users
            WHERE username = ?
        """, (username,))

    result = cursor.fetchone()

    connection.close()

    return result is not None


# ============================================================
# RESET PASSWORD
# ============================================================

def reset_password(
    username,
    email,
    new_password
):

    initialize_auth_database()

    connection = sqlite3.connect(AUTH_DB)

    cursor = connection.cursor()

    cursor.execute("""
        UPDATE users
        SET password = ?
        WHERE username = ?
        AND email = ?
    """, (
        hash_password(new_password),
        username,
        email
    ))

    connection.commit()

    updated = cursor.rowcount

    connection.close()

    if updated == 1:

        return True, "Password reset successfully."

    return False, "Username and email do not match."


# ============================================================
# INITIALIZE
# ============================================================

initialize_auth_database()