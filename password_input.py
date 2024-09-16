import sqlite3
import shutil
import os
import tempfile
from flask_login import current_user


class PasswordInput:
    def __init__(self, browser):
        self.browser = browser
        self.origin_urls = []
        self.usernames = []
        self.passwords = []
        self.creation_dates = []
        self.last_used_dates = []
        self.password_modified_dates = []
        self.data = []

    def import_all_browsers(self):
        """Import data from all browsers."""
        for browser in ['Chrome', 'Brave', 'Edge']:
            self.browser = browser
            self.import_password()
            self.insert_data()

    def import_password(self):
        """Import the data from your Chrome browser"""
        try:
            db_path = None

            # Set the database path based on the browser
            if self.browser == "None":
                pass
            elif self.browser == "Chrome":
                db_path = "C:\\Users\\Fatih\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\Login Data"
            elif self.browser == "Brave":
                db_path = ("C:\\Users\\Fatih\\AppData\\Local\\BraveSoftware\\Brave-Browser\\User Data\\Default\\Login "
                           "Data")
            elif self.browser == "Edge":
                db_path = "C:\\Users\\Fatih\\AppData\\Local\\Microsoft\\Edge\\User Data\\Default\\Login Data"

            # Only proceed if a valid path was set
            if db_path:
                # Use a temporary directory
                with tempfile.TemporaryDirectory() as tmpdirname:
                    db_copy_path = os.path.join(tmpdirname, "Login Data")

                    # Copy the database file to avoid locking issues
                    shutil.copyfile(db_path, db_copy_path)

                    # Now work with the copied database
                    conn = sqlite3.connect(db_copy_path)
                    cursor = conn.cursor()

                    # Find the data and put them in the lists
                    query = ("SELECT origin_url, username_value, password_value, "
                             "date_created, date_last_used, date_password_modified "
                             "FROM logins")
                    cursor.execute(query)
                    rows = cursor.fetchall()
                    self.origin_urls = [row[0] for row in rows]
                    self.usernames = [row[1] for row in rows]
                    self.passwords = [row[2] for row in rows]
                    self.creation_dates = [row[3] for row in rows]
                    self.last_used_dates = [row[4] for row in rows]
                    self.password_modified_dates = [row[5] for row in rows]
                    self.data = rows

                    conn.close()

        except PermissionError as e:
            print(f"Permission denied: {e.filename} - {e.strerror}")
        except Exception as e:
            print({e})

    def insert_data(self):
        """Insert the browser data in the accounts table after registration."""
        try:
            db_path = "./instance/pwmanager.db"
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Ensure that user_id is set correctly
            user_id = current_user.id

            # # Insert each row of browser data into the accounts table, avoiding duplicates
            for row in self.data:
                origin_url, username_value, password_value, date_created, date_last_used, date_modified_password = row

                # Check if the combination of user_id, url, and username already exists
                cursor.execute(
                    ("SELECT 1 FROM accounts WHERE user_id = ? AND url = ? AND username = ?"),
                    (user_id, origin_url, username_value)
                )

                result = cursor.fetchone()
                if result is None:
                    # Only insert the new record if it doesn't exist
                    cursor.execute(
                        ("INSERT INTO accounts (user_id, url, username, password, "
                         "date_created, date_last_used, date_password_modified) "
                         "VALUES (?, ?, ?, ?, ?, ?, ?)"),
                        (user_id, origin_url, username_value, password_value,
                         date_created, date_last_used, date_modified_password)
                    )

            # Save the changes and close connection
            conn.commit()
            conn.close()
        except Exception as e:
            print({e})
