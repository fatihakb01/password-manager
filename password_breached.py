# Import modules.
import os
import requests
import hashlib
from password_manager import PasswordManager
from dotenv import load_dotenv

# Load environment variables.
load_dotenv()
db_path = os.getenv("DB_PATH")


class PasswordBreached:
    """
    A class to check if a password has been breached using the Pwned Passwords API.

    Attributes:
        browser (str): The browser where the password is stored.
        password (str): The decrypted password to check against the breach database.
    """
    def __init__(self, browser, user_id, account_id):
        """
        Initialize the PasswordBreached class.

        Parameters:
            browser (str): The browser where the password is stored ('Chrome', 'Microsoft Edge').
            user_id (int): The user ID of the current user.
            account_id (int): The account ID corresponding to the password.

        This constructor retrieves the password by using the PasswordManager class to
        decrypt the password stored in the browser's database.
        """
        self.browser = browser
        manager = PasswordManager(self.browser)
        self.password = manager.read_and_decrypt_password(user_id, account_id)

    def check_password_pwned(self):
        """
        Check if the password has been involved in a data breach using the Pwned Passwords API.

        This method hashes the password using SHA-1, sends a request to the Pwned Passwords API,
        and checks if the password hash has been exposed in any known data breaches.

        Returns:
            bool: True if the password has been breached; False if it has not been breached.
            None: Returns None if there was an error during the API request.

        Example:
            If the password is found in a breach, the method prints the number of times it was
            found, otherwise it indicates that the password is safe.
        """
        try:
            # Hash the password using SHA-1.
            sha1_password = hashlib.sha1(self.password.encode('utf-8')).hexdigest().upper()
            prefix, suffix = sha1_password[:5], sha1_password[5:]

            # Pwned Passwords API URL.
            url = f"https://api.pwnedpasswords.com/range/{prefix}"
            response = requests.get(url)

            # If the request was successful, check the response for breaches.
            if response.status_code == 200:
                # Parse the API response.
                hashes = (line.split(':') for line in response.text.splitlines())

                # Check if the password's suffix matches any breached password hash.
                for h, count in hashes:
                    if h == suffix:
                        print(f"The password has been pwned {count} times!")
                        return True  # Password is breached.

                print("The password has not been pwned.")
                return False  # Password is safe.
            else:
                # Handle error in case of failed API request.
                print(f"Error checking password: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            # Catch and print any errors that occur during the process.
            print(f"Error while checking password breach: {e}")
            return None
