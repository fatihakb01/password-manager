# Import modules.
import sqlite3
import shutil
import os
import tempfile
import requests
import base64
import json
import win32crypt
from flask_login import current_user
from dotenv import load_dotenv

# Load environment variables.
load_dotenv()


def get_clearbit_logo(url):
    """
    Retrieve the logo URL for the specified domain using Clearbit's Logo API.

    Parameters:
        url (str): The full URL of the website for which to retrieve the logo.

    Returns:
        str or None: Returns the logo URL if found; otherwise, returns None.
    """
    try:
        # Extract the base domain from the URL.
        base_url = url.split('/')[2]
        logo_url = f"https://logo.clearbit.com/{base_url}"

        # Check if the logo URL is accessible.
        response = requests.get(logo_url)
        if response.status_code == 200:
            return logo_url
        else:
            return None
    except Exception as e:
        print(f"Error retrieving logo for {url}: {e}")
        return None


class PasswordInput:
    """
    A class to manage the import and decryption of browser-stored passwords.

    Attributes:
        browser (str): The browser to import passwords from ('Chrome', 'Microsoft Edge').
        origin_urls (list): List of origin URLs where passwords were used.
        urls (list): List of signon realms (base URLs).
        icons (list): List of website logos retrieved via Clearbit API.
        usernames (list): List of usernames associated with each account.
        passwords (list): List of encrypted passwords from the browser.
        creation_dates (list): List of dates when passwords were created.
        last_used_dates (list): List of dates when passwords were last used.
        password_modified_dates (list): List of dates when passwords were last modified.
        data (list): Raw data imported from the browser database.
    """
    def __init__(self, browser):
        """
        Initialize the PasswordInput class for the specified browser.

        Parameters:
            browser (str): The browser to import passwords from ('Chrome', 'Microsoft Edge').
        """
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
        """
        Extract and decrypt the AES key from the browser's Local State file.

        Returns:
            bytes or None: The decrypted AES key if successfully extracted, otherwise None.
        """
        try:
            # Set the local state path based on the browser.
            if self.browser in ["Chrome", None]:
                local_state_path = os.getenv('CHROME_LOCAL_STATE_PATH')
            else:
                local_state_path = os.getenv('EDGE_LOCAL_STATE_PATH')

            if local_state_path:
                # Open and load the Local State file to retrieve the encrypted key.
                with open(local_state_path, "r", encoding="utf-8") as file:
                    local_state = json.load(file)

                # Base64 decode the encrypted AES key.
                encrypted_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])

                # Remove 'DPAPI' prefix from the encrypted key (first 5 bytes).
                encrypted_key = encrypted_key[5:]

                # Use CryptUnprotectData to decrypt the AES key.
                decrypted_key = win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]
                return decrypted_key
            else:
                return None

        except Exception as e:
            print(f"Error decrypting AES key: {e}")
            return None

    def import_browser(self):
        """
        Import password data from the browser's database, and store the encrypted AES key in the database.

        This method copies the browser's database to avoid locking issues, then queries it to retrieve
        password-related information. It also decrypts the AES key and stores it in the user's table.
        """
        try:
            db_path = None

            # Set the database path based on the browser.
            if self.browser == "None":
                pass
            elif self.browser == "Chrome":
                db_path = os.getenv('CHROME_DB_PATH')
            elif self.browser == "Microsoft Edge":
                db_path = os.getenv('EDGE_DB_PATH')

            # Only proceed if a valid path was set.
            if db_path:
                # Use a temporary directory to copy the database and avoid file lock issues.
                with tempfile.TemporaryDirectory() as tmpdirname:
                    db_copy_path = os.path.join(tmpdirname, "Login Data")

                    # Copy the database file.
                    shutil.copyfile(db_path, db_copy_path)

                    # Connect to the copied database.
                    conn = sqlite3.connect(db_copy_path)
                    cursor = conn.cursor()

                    # Query the database for password-related data.
                    query = ("SELECT origin_url, signon_realm, username_value, password_value, "
                             "date_created, date_last_used, date_password_modified "
                             "FROM logins")
                    cursor.execute(query)
                    rows = cursor.fetchall()

                    # Store the retrieved data in class attributes.
                    self.origin_urls = [row[0] for row in rows]
                    self.urls = [row[1] for row in rows]
                    self.usernames = [row[2] for row in rows]
                    self.passwords = [row[3] for row in rows]
                    self.creation_dates = [row[4] for row in rows]
                    self.last_used_dates = [row[5] for row in rows]
                    self.password_modified_dates = [row[6] for row in rows]
                    self.data = rows

                    conn.close()

            # Retrieve and store the decrypted AES key in the user's table.
            decrypted_key = self.get_decrypted_aes_key()
            if decrypted_key:
                db_path = os.getenv("DB_PATH")
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()

                # Update the user's record with the decrypted AES key.
                cursor.execute("UPDATE users SET encrypted_key = ? WHERE id = ?", (decrypted_key, current_user.id))
                conn.commit()
                conn.close()

        except PermissionError as e:
            print(f"Permission denied: {e.filename} - {e.strerror}")
        except Exception as e:
            print({e})

    def insert_data(self):
        """
        Insert the retrieved browser password data into the user's accounts table in the database.

        This method checks for duplicates before inserting new records and retrieves the website icons using Clearbit's
        Logo API.
        """
        try:
            db_path = os.getenv("DB_PATH")
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Ensure that user_id is set correctly.
            user_id = current_user.id

            # Insert each row of browser data into the accounts table, avoiding duplicates.
            for row in self.data:
                (origin_url, signon_realm, username_value, password_value,
                 date_created, date_last_used, date_modified_password) = row

                # Fetch the icon for the URL and retrieve browser.
                icon_url = get_clearbit_logo(origin_url)
                browser = self.browser

                # Check if the combination of user_id, url, and username already exists.
                cursor.execute(
                    "SELECT 1 FROM accounts WHERE user_id = ? AND full_url = ? AND username = ?",
                    (user_id, origin_url, username_value)
                )

                result = cursor.fetchone()
                if result is None:
                    # Only insert the new record if it doesn't exist.
                    cursor.execute(
                        ("INSERT INTO accounts (user_id, full_url, url, icon, username, password, "
                         "browser, date_created, date_last_used, date_password_modified) "
                         "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"),
                        (user_id, origin_url, signon_realm, icon_url, username_value, password_value,
                         browser, date_created, date_last_used, date_modified_password)
                    )

            # Save the changes and close connection.
            conn.commit()
            conn.close()
        except Exception as e:
            print({e})
