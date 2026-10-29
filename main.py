from datetime import datetime
from getpass import getpass
import re

from db import DBCode

def read_int(prompt):
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("Please enter a valid whole number.")

def read_positive_int(prompt):
    while True:
        value = read_int(prompt)
        if value > 0:
            return value
        print("Please enter a number greater than zero.")

def read_phone(prompt):
    while True:
        value = input(prompt).strip()
        if re.fullmatch(r"\+?[0-9() -]+", value):
            digits = re.sub(r"\D", "", value)
            if 7 <= len(digits) <= 15:
                return ("+" if value.startswith("+") else "") + digits
        print("Enter a valid phone number with 7 to 15 digits.")

def read_budget(prompt):
    while True:
        try:
            value = float(input(prompt))
            if value < 0:
                print("Budget cannot be negative.")
                continue
            return value
        except ValueError:
            print("Please enter a valid amount.")

def read_date(prompt):
    while True:
        value = input(prompt).strip()
        try:
            datetime.strptime(value, "%Y-%m-%d")
            return value
        except ValueError:
            print("Use date format YYYY-MM-DD (example: 2026-12-25).")

def login(db):
    while True:
        print("""
========== EVENT MANAGEMENT LOGIN ==========
1. Log In
2. Create Account
0. Exit
============================================
""")
        choice = input("Enter choice: ").strip()

        if choice == "0":
            print("App Closed.")
            return None

        if choice not in {"1", "2"}:
            print("Invalid option. Please choose 0-2.")
            continue

        username = input("Username: ").strip()
        password = getpass("Password: ")
        if not username or len(username) > 50 or not password:
            print("Enter a username (up to 50 characters) and password.")
            continue

        if choice == "1":
            if db.authenticateUser(username, password):
                print(f"Welcome, {username}.")
                return username
            print("Invalid username or password.")
            continue

        if len(password) < 8:
            print("Password must be at least 8 characters long.")
            continue
        if password != getpass("Confirm password: "):
            print("Passwords do not match.")
            continue
        if db.createUser(username, password):
            print("Account created. You can now log in.")
        else:
            print("That username is already registered.")

def run_app():
    db = None
    try:
        db = DBCode()
        username = login(db)
        if username is None:
            return
        while True:
            print("""
========== EVENT MANAGEMENT ==========
1. Add Event
2. View All Events
3. Search Event by ID
4. Edit Event Budget
5. Delete Event
6. Submit Event Request
7. My Event Requests
0. Exit
=====================================
""")
            choice = input("Enter choice: ").strip()

            if choice == "1":
                print("Enter Event Details")
                event_id = read_int("Event ID: ")
                name = input("Customer Name: ").strip()
                print (""" 
                select event type:
                1.Wedding
                2.Birthday
                3.Corporate
                4.College Function
                5.Anniversary
                6.Other""")
                type_choice= input("enter your choice: ").strip()
                event_types={
                    "1":"Wedding",
                    "2":"Birthday",
                    "3":"Corporate",
                    "4":"College Function",
                    "5":"Anniversary",
                    "6":"Other"
                }
                event_type = event_types.get(type_choice)
                event_date = read_date("Event Date (YYYY-MM-DD): ")
                location = input("location: ").strip()
                budget = read_budget("Budget (₹): ")
                if not name or not event_type or not location: 
                    print("Name, type, and location cannot be empty.")
                    continue
                try:
                    result = db.addEvent(event_id, name, event_type, event_date, location, budget)
                    print("Event Saved Successfully" if result else "Event Not Saved")
                    db.countEvents()
                except Exception as exc:
                    print(f"Could not add event: {exc}")

            elif choice == "2":
                db.listEvents()
                db.countEvents()

            elif choice == "3":
                event_id = read_int("Enter Event ID: ")
                db.viewEvent(event_id)

            elif choice == "4":
                event_id = read_int("Enter Event ID to edit: ")
                if db.viewEvent(event_id):
                    budget = read_budget("New Budget (₹): ")
                    result = db.editEventBudget(event_id, budget)
                    print("Event Modified Successfully" if result else "No changes made / event not found.")
                    db.viewEvent(event_id)

            elif choice == "5":
                event_id = read_int("Enter Event ID to delete: ")
                if db.viewEvent(event_id):
                    confirm = input("Are you sure? (Y/N): ").strip().lower()
                    if confirm == "y":
                        result = db.removeEvent(event_id)
                        print("Event Removed" if result else "Event not found.")
                    else:
                        print("Delete cancelled.")

            elif choice == "6":
                event_name = input("Event Name: ").strip()
                if not event_name or len(event_name) > 100:
                    print("Event name must be between 1 and 100 characters.")
                    continue
                person_count = read_positive_int("Number of People: ")
                location = input("Location: ").strip()
                if not location or len(location) > 150:
                    print("Location must be between 1 and 150 characters.")
                    continue
                phone_number = read_phone("Phone Number: ")
                try:
                    result = db.addEventRequest(
                        username, event_name, person_count, location, phone_number
                    )
                    print("Event request submitted successfully." if result else "Event request was not saved.")
                except Exception as exc:
                    print(f"Could not submit event request: {exc}")

            elif choice == "7":
                db.listEventRequests(username)

            elif choice == "0":
                print("App Closed.")
                break

            else:
                print("Invalid option. Please choose 0-7.")
    except Exception as exc:
        print(f"Application error: {exc}")
        print("Check that MySQL is running and database credentials in db.py are correct.")
    finally:
        if db is not None:
            try:
                db.appClose()
            except Exception:
                pass

if __name__ == "__main__":
    run_app()
