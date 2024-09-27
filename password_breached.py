import os
import requests
import hashlib
from password_manager import PasswordManager
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
db_path = os.getenv("DB_PATH")


class PasswordBreached:
    def __init__(self, browser, user_id, account_id):
        self.browser = browser
        manager = PasswordManager(self.browser)
        self.password = manager.read_and_decrypt_password(user_id, account_id)

    def check_password_pwned(self):
        sha1_password = hashlib.sha1(self.password.encode('utf-8')).hexdigest().upper()
        prefix, suffix = sha1_password[:5], sha1_password[5:]
        url = f"https://api.pwnedpasswords.com/range/{prefix}"
        response = requests.get(url)

        if response.status_code == 200:
            hashes = (line.split(':') for line in response.text.splitlines())
            for h, count in hashes:
                if h == suffix:
                    print(f"The password has been pwned {count} times!")
                    return True  # Password is breached
            print("The password has not been pwned.")
            return False  # Password is safe
        else:
            print(f"Error checking password: {response.status_code} - {response.text}")
            return None


# Test
# if __name__ == "__main__":
#     password_breached = PasswordBreached("Chrome", 1, 3)
#     password_breached.check_password_pwned()
