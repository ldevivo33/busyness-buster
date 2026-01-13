"""
Seed script to create the initial user for Busyness Buster.
Run this once after setting up the database.

Usage: python seed_user.py
"""

import sys
from db import SessionLocal, User
from services.auth import hash_password


def get_password(prompt: str) -> str:
    """Get password input, handling Windows terminal issues."""
    # getpass has known issues on Windows terminals (returns garbage bytes)
    # Using visible input for reliability - this is a local-only app anyway
    print("(Note: password will be visible - local use only)")
    return input(prompt)


def create_user():
    db = SessionLocal()

    try:
        # Check if a user already exists
        existing_user = db.query(User).first()
        if existing_user:
            print(f"User '{existing_user.username}' already exists.")
            print("Delete busyness.db and restart if you want to reset.")
            return

        # Get username and password
        print("=== Busyness Buster - Create User ===\n")
        username = input("Enter username: ").strip()
        if not username:
            print("Error: Username cannot be empty.")
            return

        password = get_password("Enter password: ").strip()
        if not password:
            print("Error: Password cannot be empty.")
            return

        # bcrypt has a 72-byte limit on passwords
        if len(password.encode('utf-8')) > 72:
            print("Error: Password too long (max 72 bytes).")
            return

        confirm_password = get_password("Confirm password: ").strip()
        if password != confirm_password:
            print("Error: Passwords do not match.")
            return

        # Create user with hashed password
        user = User(
            username=username,
            hashed_password=hash_password(password)
        )
        db.add(user)
        db.commit()

        print(f"\nUser '{username}' created successfully!")

    except Exception as e:
        db.rollback()
        print(f"Error creating user: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    create_user()
