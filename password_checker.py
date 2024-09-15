import requests
import hashlib

# Function to check if a password has been pwned
def check_password_pwned(password):
    sha1_password = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
    prefix, suffix = sha1_password[:5], sha1_password[5:]
    url = f"https://api.pwnedpasswords.com/range/{prefix}"
    response = requests.get(url)

    if response.status_code == 200:
        hashes = (line.split(':') for line in response.text.splitlines())
        for h, count in hashes:
            if h == suffix:
                print(f"The password has been pwned {count} times!")
                return
        print("The password has not been pwned.")
    else:
        print(f"Error checking password: {response.status_code} - {response.text}")


# Example usage:
email_address = "fakbulut363@gmail.com"
pwd = "abcd1234!"

print("\nChecking password...")
check_password_pwned(pwd)
