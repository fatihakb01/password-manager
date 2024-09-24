import sqlite3
import shutil
import os
import tempfile
import requests
from flask_login import current_user
from dotenv import load_dotenv
import base64
import json
import win32crypt

# Load environment variables in here
load_dotenv()


def get_clearbit_logo(url):
    try:
        # Extract base domain from URL
        base_url = url.split('/')[2]
        logo_url = f"https://logo.clearbit.com/{base_url}"

        # Check if the logo URL is accessible
        response = requests.get(logo_url)
        if response.status_code == 200:
            return logo_url
        else:
            return None
    except Exception as e:
        print(f"Error retrieving logo for {url}: {e}")
        return None


class PasswordInput:
    def __init__(self, browser):
        self.browser = browser
        self.origin_urls = []
        self.urls = []
        self.icons = []
        self.usernames = []
        self.passwords = []
        self.creation_dates = []
        self.last_used_dates = []
        self.password_modified_dates = []
        self.data = []

    def get_decrypted_aes_key(self):
        """Extract and decrypt the AES key from the Local State file."""
        try:
            # Set the local state path based on the browser
            local_state_path = None

            if self.browser == "None":
                return None
            elif self.browser == "Chrome":
                local_state_path = os.getenv('CHROME_LOCAL_STATE_PATH')
            elif self.browser == "Microsoft Edge":
                local_state_path = os.getenv('EDGE_LOCAL_STATE_PATH')

            if local_state_path:
                # Open and load the Local State file to retrieve the encrypted key
                with open(local_state_path, "r", encoding="utf-8") as file:
                    local_state = json.load(file)

                # Base64 decode the encrypted AES key
                encrypted_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])

                # Remove 'DPAPI' prefix from the encrypted key (first 5 bytes)
                encrypted_key = encrypted_key[5:]

                # Use CryptUnprotectData to decrypt the AES key
                decrypted_key = win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]
                return decrypted_key
            else:
                return None

        except Exception as e:
            print(f"Error decrypting AES key: {e}")
            return None

    def import_browser(self):
        """Import the data from the specified browser and retrieve the encrypted key."""
        try:
            db_path = None

            # Set the database path based on the browser
            if self.browser == "None":
                pass
            elif self.browser == "Chrome":
                db_path = os.getenv('CHROME_DB_PATH')
            elif self.browser == "Microsoft Edge":
                db_path = os.getenv('EDGE_DB_PATH')

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
                    query = ("SELECT origin_url, signon_realm, username_value, password_value, "
                             "date_created, date_last_used, date_password_modified "
                             "FROM logins")
                    cursor.execute(query)
                    rows = cursor.fetchall()
                    self.origin_urls = [row[0] for row in rows]
                    self.urls = [row[1] for row in rows]
                    self.usernames = [row[2] for row in rows]
                    self.passwords = [row[3] for row in rows]
                    self.creation_dates = [row[4] for row in rows]
                    self.last_used_dates = [row[5] for row in rows]
                    self.password_modified_dates = [row[6] for row in rows]
                    self.data = rows

                    conn.close()

            # After fetching passwords, get the decrypted AES key and store it in the users table
            decrypted_key = self.get_decrypted_aes_key()
            if decrypted_key:
                # Insert the decrypted key into the current user record
                db_path = os.getenv("DB_PATH")
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()

                cursor.execute("UPDATE users SET encrypted_key = ? WHERE id = ?", (decrypted_key, current_user.id))
                conn.commit()
                conn.close()

        except PermissionError as e:
            print(f"Permission denied: {e.filename} - {e.strerror}")
        except Exception as e:
            print({e})

    def insert_data(self):
        """Insert the browser data in the accounts table after registration."""
        try:
            db_path = os.getenv("DB_PATH")
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Ensure that user_id is set correctly
            user_id = current_user.id

            # Insert each row of browser data into the accounts table, avoiding duplicates
            for row in self.data:
                (origin_url, signon_realm, username_value, password_value,
                 date_created, date_last_used, date_modified_password) = row

                # Fetch the icon for the URL and retrieve browser
                icon_url = get_clearbit_logo(origin_url)
                browser = self.browser

                # Check if the combination of user_id, url, and username already exists
                cursor.execute(
                    "SELECT 1 FROM accounts WHERE user_id = ? AND full_url = ? AND username = ?",
                    (user_id, origin_url, username_value)
                )

                result = cursor.fetchone()
                if result is None:
                    # Only insert the new record if it doesn't exist
                    cursor.execute(
                        ("INSERT INTO accounts (user_id, full_url, url, icon, username, password, "
                         "browser, date_created, date_last_used, date_password_modified) "
                         "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"),
                        (user_id, origin_url, signon_realm, icon_url, username_value, password_value,
                         browser, date_created, date_last_used, date_modified_password)
                    )

            # Save the changes and close connection
            conn.commit()
            conn.close()
        except Exception as e:
            print({e})

# For debug purposes
# password_input = PasswordInput("Chrome")
# password_input.import_browser()
# password_input.get_decrypted_aes_key()
# print(password_input.passwords)
# print(password_input.browser)
# print(password_input.get_decrypted_aes_key())
