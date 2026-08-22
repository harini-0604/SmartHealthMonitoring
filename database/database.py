
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
        connection.execute(
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
