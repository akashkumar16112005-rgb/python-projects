import hashlib
import hmac
import secrets

import pymysql

class DBCode:
    def __init__(self):
        self.con = pymysql.connect(
            host="localhost",
            user="root",
            password="Admin@123",
            database="event_management",
            cursorclass=pymysql.cursors.Cursor
        )
        with self.con.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS app_users (
                    username VARCHAR(50) PRIMARY KEY,
                    password_salt CHAR(32) NOT NULL,
                    password_hash CHAR(128) NOT NULL
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS event_requests (
                    request_id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) NOT NULL,
                    event_name VARCHAR(100) NOT NULL,
                    person_count INT NOT NULL,
                    location VARCHAR(150) NOT NULL,
                    phone_number VARCHAR(16) NOT NULL,
                    requested_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (username) REFERENCES app_users(username)
                )
            """)
        print("Welcome to Event Management App")

    @staticmethod
    def _hashPassword(password, salt):
        return hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), bytes.fromhex(salt), 200_000
        ).hex()

    def createUser(self, username, password):
        salt = secrets.token_hex(16)
        password_hash = self._hashPassword(password, salt)
        with self.con.cursor() as cur:
            result = cur.execute(
                "INSERT IGNORE INTO app_users (username, password_salt, password_hash) VALUES (%s, %s, %s)",
                (username, salt, password_hash)
            )
        self.con.commit()
        return result == 1

    def authenticateUser(self, username, password):
        with self.con.cursor() as cur:
            cur.execute(
                "SELECT password_salt, password_hash FROM app_users WHERE username = %s",
                (username,)
            )
            row = cur.fetchone()
        if not row:
            return False
        password_hash = self._hashPassword(password, row[0])
        return hmac.compare_digest(password_hash, row[1])

    def addEventRequest(self, username, event_name, person_count, location, phone_number):
        with self.con.cursor() as cur:
            result = cur.execute(
                """
                INSERT INTO event_requests
                    (username, event_name, person_count, location, phone_number)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (username, event_name, person_count, location, phone_number)
            )
        self.con.commit()
        return result == 1

    def listEventRequests(self, username):
        with self.con.cursor() as cur:
            cur.execute(
                """
                SELECT request_id, event_name, person_count, location, phone_number, requested_at
                FROM event_requests
                WHERE username = %s
                ORDER BY requested_at DESC, request_id DESC
                """,
                (username,)
            )
            rows = cur.fetchall()
        if not rows:
            print("You have no event requests yet.")
            return
        for row in rows:
            print("-" * 55)
            print(f"Request ID : {row[0]}")
            print(f"Event Name : {row[1]}")
            print(f"People     : {row[2]}")
            print(f"Location   : {row[3]}")
            print(f"Phone      : {row[4]}")
            print(f"Submitted  : {row[5]}")

    def addEvent(self, event_id, name, event_type, event_date, location, budget):
        query = """
            INSERT INTO events (event_id, customer_name, event_type, event_date, location, budget)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        with self.con.cursor() as cur:
            result = cur.execute(query, (event_id, name, event_type, event_date, location, budget))
        self.con.commit()
        return result

    def listEvents(self):
        with self.con.cursor() as cur:
            cur.execute("SELECT event_id, customer_name, event_type, event_date, location, budget FROM events ORDER BY event_id")
            rows = cur.fetchall()
        if not rows:
            print("No events found.")
            return
        for row in rows:
            print("-" * 55)
            print(f"Event ID   : {row[0]}")
            print(f"Name       : {row[1]}")
            print(f"Type       : {row[2]}")
            print(f"Date       : {row[3]}")
            print(f"location   : {row[4]}")
            print(f"Budget     : ₹{row[5]}")

    def viewEvent(self, event_id):
        with self.con.cursor() as cur:
            cur.execute(
                "SELECT event_id, customer_name, event_type, event_date, location, budget FROM events WHERE event_id = %s",
                (event_id,)
            )
            row = cur.fetchone()
        if row:
            print("-" * 55)
            print(f"Event ID   : {row[0]}")
            print(f"Name       : {row[1]}")
            print(f"Type       : {row[2]}")
            print(f"Date       : {row[3]}")
            print(f"location   : {row[4]}")
            print(f"Budget     : ₹{row[5]}")
            return True
        print("Event Not Found")
        return False

    def countEvents(self):
        with self.con.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM events")
            count = cur.fetchone()[0]
        print(f"Total Events Registered: {count}")

    def editEvent(self, event_id, location, budget):
        with self.con.cursor() as cur:
            result = cur.execute(
                "UPDATE events SET location = %s, budget = %s WHERE event_id = %s",
                (location, budget, event_id)
            )
        self.con.commit()
        return result

    def editEventBudget(self, event_id, budget):
        with self.con.cursor() as cur:
            result = cur.execute(
                "UPDATE events SET budget = %s WHERE event_id = %s",
                (budget, event_id)
            )
        self.con.commit()
        return result

    def removeEvent(self, event_id):
        with self.con.cursor() as cur:
            result = cur.execute("DELETE FROM events WHERE event_id = %s", (event_id,))
        self.con.commit()
        return result

    def appClose(self):
        self.con.close()
