# Import modules.
import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from password_input import PasswordInput
from dotenv import load_dotenv
import sqlite3

# Load environment variables.
load_dotenv()
db_path = os.getenv("DB_PATH")


class PasswordManager:
    """
    A class to manage password encryption and decryption using AES-GCM.

    Attributes:
        browser (str): The browser for which passwords are managed ('Chrome', 'Microsoft Edge').
        decrypted_key (bytes): The decrypted AES key used for encrypting and decrypting passwords.
    """

    def __init__(self, browser):
        """
        Initialize the PasswordManager with a specific browser and retrieve the decrypted AES key.

        Parameters:
            browser (str): The browser name ('Chrome', 'Microsoft Edge') from which passwords are managed.
        """
        self.browser = browser
        password_input = PasswordInput(self.browser)
        self.decrypted_key = password_input.get_decrypted_aes_key()

    # def return_aes_key(self):
    #     """
    #     Retrieve the decrypted AES key used by the browser for encrypting/decrypting passwords.
    #
    #     Returns:
    #         bytes: The decrypted AES key.
    #     """
    #     password_input = PasswordInput(self.browser)
    #     decrypted_key = password_input.get_decrypted_aes_key()
    #     return decrypted_key

    def encrypt_password(self, plain_password):
        """
        Encrypt a plain password using AES-GCM encryption.

        Parameters:
            plain_password (str): The password in plain text to be encrypted.

        Returns:
            bytes: The encrypted password as a binary blob, which includes a nonce and an authentication tag.
        """
        # Generate a random 12-byte nonce.
        nonce = os.urandom(12)

        # Create a Cipher object using AES-GCM mode with the decrypted AES key and nonce.
        cipher = Cipher(algorithms.AES(self.decrypted_key), modes.GCM(nonce), backend=default_backend())
        encryptor = cipher.encryptor()

        # Encrypt the plain password and finalize encryption.
        ciphertext = encryptor.update(plain_password.encode('utf-8')) + encryptor.finalize()

        # Format the encrypted password blob: 'v10' + nonce + ciphertext + authentication tag.
        encrypted_password = b'v10' + nonce + ciphertext + encryptor.tag
        return encrypted_password

    def decrypt_password(self, encrypted_password):
        """
        Decrypt an encrypted password using AES-GCM.

        Parameters:
            encrypted_password (bytes): The encrypted password blob retrieved from the database.

        Returns:
            str: The decrypted password in plain text, or None if decryption fails.
        """
        try:
            # Extract nonce, ciphertext, and authentication tag from the encrypted blob.
            nonce = encrypted_password[3:15]
            ciphertext = encrypted_password[15:-16]
            tag = encrypted_password[-16:]

            # Create a Cipher object using AES-GCM mode with the nonce and tag.
            cipher = Cipher(algorithms.AES(self.decrypted_key), modes.GCM(nonce, tag), backend=default_backend())
            decryptor = cipher.decryptor()

            # Decrypt the ciphertext and finalize decryption.
            decrypted_password = decryptor.update(ciphertext) + decryptor.finalize()
            return decrypted_password.decode('utf-8')

        except Exception as e:
            # Handle any errors during the decryption process.
            print(f"Failed to decrypt password: {e}")
            return None

    def read_and_decrypt_password(self, user_id, account_id):
        """
        Read an encrypted password from the SQLite database and decrypt it.

        Args:
            user_id (int): The ID of the user who owns the account.
            account_id (int): The ID of the account for which the password is stored.

        Returns:
            str: The decrypted password in plain text, or None if decryption fails.
        """
        try:
            # Connect to the SQLite database.
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Query the database for the encrypted password.
            cursor.execute("SELECT password FROM accounts WHERE user_id = ? and id = ?", (user_id, account_id))
            encrypted_password_blob = cursor.fetchone()[0]
            conn.close()

            # Decrypt the password.
            decrypted_password = self.decrypt_password(encrypted_password_blob)
            return decrypted_password

        except Exception as e:
            # Handle any errors during the database read or decryption.
            print(f"Error reading and decrypting password: {e}")
            return None

    def encrypt_and_store_password(self, plain_password):
        """
        Encrypt a plain password and return the encrypted blob to store in the database.

        Args:
            plain_password (str): The password in plain text to be encrypted.

        Returns:
            bytes: The encrypted password blob, including a nonce and authentication tag.
        """
        encrypted_password = self.encrypt_password(plain_password)
        return encrypted_password
