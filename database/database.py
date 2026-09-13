
import sqlite3
from pathlib import Path

from database.models import Incident


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATABASE_FILE = PROJECT_ROOT / "smart_health.db"


def get_connection():
    return sqlite3.connect(DATABASE_FILE)


def initialize_database():
    connection = get_connection()

    try:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS incidents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                source TEXT,
                reason TEXT,
                status TEXT
            )
            """
        )

        connection.commit()

    finally:
        connection.close()


def save_incident(incident):
    initialize_database()

    connection = get_connection()

    try:
        cursor = connection.execute(
            """
            INSERT INTO incidents (
                timestamp,
                source,
                reason,
                status
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                incident.timestamp,
                incident.source,
                incident.reason,
                incident.status
            )
        )

        connection.commit()

        return cursor.lastrowid

    finally:
        connection.close()


def get_incidents():
    initialize_database()

    connection = get_connection()

    try:
        cursor = connection.execute(
            """
            SELECT
                id,
                timestamp,
                source,
                reason,
                status
            FROM incidents
            ORDER BY id DESC
            """
        )

        return cursor.fetchall()

    finally:
        connection.close()

# ============================================================
# AMBULANCE RESPONSE STATUS
# ============================================================

def initialize_ambulance_response():

    connection = get_connection()

    try:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS ambulance_response (
                incident_id INTEGER PRIMARY KEY,
                status TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        connection.commit()

    finally:
        connection.close()


def update_ambulance_status(
    incident_id,
    status
):

    initialize_ambulance_response()

    from datetime import datetime

    updated_at = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    connection = get_connection()

    try:

        connection.execute(
            """
            INSERT INTO ambulance_response (
                incident_id,
                status,
                updated_at
            )
            VALUES (?, ?, ?)

            ON CONFLICT(incident_id)
            DO UPDATE SET
                status = excluded.status,
                updated_at = excluded.updated_at
            """,
            (
                incident_id,
                status,
                updated_at
            )
        )

        connection.commit()

    finally:
        connection.close()


def get_ambulance_status(incident_id):

    initialize_ambulance_response()

    connection = get_connection()

    try:

        cursor = connection.execute(
            """
            SELECT
                status,
                updated_at
            FROM ambulance_response
            WHERE incident_id = ?
            """,
            (incident_id,)
        )

        result = cursor.fetchone()

        if result:
            return {
                "status": result[0],
                "updated_at": result[1]
            }

        return {
            "status": "NOT_DISPATCHED",
            "updated_at": None
        }

    finally:
        connection.close()

def display_incident_history():
    incidents = get_incidents()

    print()
    print("=" * 70)
    print("INCIDENT HISTORY")
    print("=" * 70)

    if not incidents:
        print("No incidents recorded.")
    else:
        for incident in incidents:
            incident_id, timestamp, source, reason, status = incident

            print(f"ID       : {incident_id}")
            print(f"TIME     : {timestamp}")
            print(f"SOURCE   : {source}")
            print(f"REASON   : {reason}")
            print(f"STATUS   : {status}")
            print("-" * 70)

    print("=" * 70)


if __name__ == "__main__":
    initialize_database()
    print("Database initialized successfully.")
