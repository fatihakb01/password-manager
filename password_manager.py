import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from password_input import PasswordInput
from dotenv import load_dotenv
import sqlite3

# Load environment variables
load_dotenv()
db_path = os.getenv("DB_PATH")


class PasswordManager:
    def __init__(self, browser):
        """ Initialize the PasswordManager with a specific browser.
        :param browser: str - Name of the browser (chrome, brave, edge)
        """
        self.browser = browser
        password_input = PasswordInput(self.browser)
        self.decrypted_key = password_input.get_decrypted_aes_key()

    def return_aes_key(self):
        password_input = PasswordInput(self.browser)
        decrypted_key = password_input.get_decrypted_aes_key()
        return decrypted_key

    def encrypt_password(self, plain_password):
        """ Encrypt a plain password using AES-GCM.
        :param plain_password: str - The password in plain text.
        :return: bytes - The encrypted password.
        """
        nonce = os.urandom(12)

        cipher = Cipher(algorithms.AES(self.decrypted_key), modes.GCM(nonce), backend=default_backend())
        encryptor = cipher.encryptor()

        ciphertext = encryptor.update(plain_password.encode('utf-8')) + encryptor.finalize()

        encrypted_password = b'v10' + nonce + ciphertext + encryptor.tag
        return encrypted_password

    def decrypt_password(self, encrypted_password):
        """ Decrypt an encrypted password using AES-GCM.
        :param encrypted_password: bytes - The encrypted password blob from the database.
        :return: str - The decrypted password in plain text.
        """
        try:
            nonce = encrypted_password[3:15]
            ciphertext = encrypted_password[15:-16]
            tag = encrypted_password[-16:]

            cipher = Cipher(algorithms.AES(self.decrypted_key), modes.GCM(nonce, tag), backend=default_backend())
            decryptor = cipher.decryptor()
            decrypted_password = decryptor.update(ciphertext) + decryptor.finalize()

            return decrypted_password.decode('utf-8')

        except Exception as e:
            print(f"Failed to decrypt password: {e}")
            return None

    def read_and_decrypt_password(self, user_id, account_id):
        """ Read the password from the SQLite database and decrypt it.
        :param account_id: int - The account ID for which to fetch the password.
        :param user_id: int - The user ID for which to fetch the password.
        :return: str - The decrypted password.
        """
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT password FROM accounts WHERE user_id = ? and id = ?",
                       (user_id, account_id))
        encrypted_password_blob = cursor.fetchone()[0]
        conn.close()

        decrypted_password = self.decrypt_password(encrypted_password_blob)
        return decrypted_password

    def encrypt_and_store_password(self, plain_password):
        """ Encrypt a plain password and return the encrypted blob to store in the database.
        :param plain_password: str - The password in plain text.
        :return: bytes - The encrypted password blob.
        """
        encrypted_password = self.encrypt_password(plain_password)
        return encrypted_password


# # Test
# if __name__ == "__main__":
#     manager = PasswordManager("Microsoft Edge")
#     print(manager.return_aes_key())
#     password = manager.read_and_decrypt_password(1, 9)
#     print(password)
#     encrypted_password = manager.encrypt_and_store_password(password)
#     print(encrypted_password)
