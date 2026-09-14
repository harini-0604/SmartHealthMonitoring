import os

import bcrypt
from dotenv import load_dotenv
from supabase import create_client


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")


if not SUPABASE_URL:
    raise RuntimeError("SUPABASE_URL is missing from .env")

if not SUPABASE_SERVICE_KEY:
    raise RuntimeError("SUPABASE_SERVICE_KEY is missing from .env")


# ============================================================
# SUPABASE CONNECTION
# ============================================================

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_SERVICE_KEY
)


# ============================================================
# PASSWORD HASHING
# ============================================================

def hash_password(password):

    password_bytes = password.encode("utf-8")

    hashed = bcrypt.hashpw(
        password_bytes,
        bcrypt.gensalt()
    )

    return hashed.decode("utf-8")


def verify_password(password, hashed_password):

    try:

        return bcrypt.checkpw(
            password.encode("utf-8"),
            hashed_password.encode("utf-8")
        )

    except (ValueError, TypeError):

        return False


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

    try:

        existing_username = (
            supabase
            .table("users")
            .select("id")
            .eq("username", username)
            .limit(1)
            .execute()
        )

        if existing_username.data:

            return False, "Username already exists."


        existing_email = (
            supabase
            .table("users")
            .select("id")
            .eq("email", email)
            .limit(1)
            .execute()
        )

        if existing_email.data:

            return False, "Email already exists."


        password_hash = hash_password(password)


        response = (
            supabase
            .table("users")
            .insert({
                "full_name": full_name,
                "username": username,
                "email": email,
                "password": password_hash,
                "role": role
            })
            .execute()
        )


        if response.data:

            return True, "Account created successfully."


        return False, "Account could not be created."


    except Exception as error:

        print("CREATE USER ERROR:", error)

        return False, "Account could not be created."


# ============================================================
# LOGIN
# ============================================================

def verify_user(
    username,
    password,
    role
):

    try:

        response = (
            supabase
            .table("users")
            .select(
                "id, full_name, username, email, password, role"
            )
            .eq("username", username)
            .eq("role", role)
            .limit(1)
            .execute()
        )


        if not response.data:

            return None


        user = response.data[0]


        if not verify_password(
            password,
            user["password"]
        ):

            return None


        return (
            user["id"],
            user["full_name"],
            user["username"],
            user["email"],
            user["role"]
        )


    except Exception as error:

        print("LOGIN ERROR:", error)

        return None


# ============================================================
# CHECK USER
# ============================================================

def user_exists(
    username,
    email=None
):

    try:

        query = (
            supabase
            .table("users")
            .select("id")
            .eq("username", username)
        )


        if email:

            query = query.eq(
                "email",
                email
            )


        response = (
            query
            .limit(1)
            .execute()
        )


        return bool(response.data)


    except Exception as error:

        print("USER EXISTS ERROR:", error)

        return False


# ============================================================
# RESET PASSWORD
# ============================================================

def reset_password(
    username,
    email,
    new_password
):

    try:

        response = (
            supabase
            .table("users")
            .select("id")
            .eq("username", username)
            .eq("email", email)
            .limit(1)
            .execute()
        )


        if not response.data:

            return False, "Username and email do not match."


        new_hash = hash_password(
            new_password
        )


        update_response = (
            supabase
            .table("users")
            .update({
                "password": new_hash
            })
            .eq("username", username)
            .eq("email", email)
            .execute()
        )


        if update_response.data:

            return True, "Password reset successfully."


        return False, "Password reset failed."


    except Exception as error:

        print("PASSWORD RESET ERROR:", error)

        return False, "Password reset failed."