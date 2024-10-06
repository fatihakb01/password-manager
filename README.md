# Password Manager Application

## Overview
This is a password manager web application built using Flask, SQLAlchemy, and Flask-Login. The app allows users to securely store and manage their account credentials, and it checks for any breached passwords to ensure account security.

### Features
- **User Registration & Authentication**: Register new users and log in securely.
- **Password Encryption**: Securely store user passwords using encryption.
- **Password Breach Detection**: Check if stored passwords have been compromised.
- **CRUD Operations**: Create, Read, Update, and Delete (CRUD) account credentials.
- **Browser-based Password Management**: Import passwords from browsers and manage them within the application.
- **Responsive UI**: Built with Flask-Bootstrap for a consistent and responsive user experience.

## Table of Contents
1. [Installation](#installation)
2. [Setup](#setup)
3. [Usage](#usage)
4. [Project Structure](#project-structure)
5. [Environment Variables](#environment-variables)
6. [Database Models](#database-models)
7. [Security Considerations](#security-considerations)
8. [Contributing](#contributing)
9. [License](#license)

## Installation
### Prerequisites
Ensure you have the following installed on your system:
- Python 3.7+
- Flask
- Flask-SQLAlchemy
- Flask-Login
- SQLite

### Steps
1. Clone the repository:
    ```bash
    git clone https://github.com/fatihakb01/password-manager.git
    cd password-manager
    ```

2. Create a virtual environment and activate it:
    ```bash
    # On Windows
    python -m venv venv
    venv\Scripts\activate

    # On MacOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4. Create the SQLite database:
    ```bash
    flask shell
    from main import db
    db.create_all()
    exit()
    ```

5. Run the application:
    ```bash
    flask run
    ```

## Setup
1. **Environment Variables**: Create a `.env` file in the root directory and add the following variables:
    ```
    SECRET_KEY=your_secret_key
    DB_PATH=path_to_your_database_file
    CHROME_DB_PATH=path_to_your_chrome_login_data_file
    EDGE_DB_PATH=path_to_your_edge_login_data_file
    CHROME_LOCAL_STATE_PATH=path_to_your_chrome_local_state_file
    EDGE_LOCAL_STATE_PATH=path_to_your_edge_local_state_file
    DEFAULT_BROWSER=default_browser_name # use either 'Chrome' or 'Microsoft Edge'
    ```

2. **Database Configuration**: Ensure that `SQLALCHEMY_DATABASE_URI` is set up correctly in `main.py`:
    ```python 
   from flask import Flask
   app = Flask(__name__)
   app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pwmanager.db'
    ```

## Usage
### Register a New User
- Navigate to `/register` and create a new account.
- After registration, you will be redirected to the login page.

### Login
- Use your registered email and password to log in to the application.

### Managing Vaults
- You can view, add, edit, and delete your account credentials from the `Vaults` page.
- Use the `Check Breaches` feature to see if any of your stored passwords have been compromised.

## Project Structure
```
   password-manager/
   ├── instance/                         # Contains the SQLite database file.
   │   └── pwmanager.db                  # SQLite database for storing user and account data.
   ├── static/                           # Static files (CSS, JS, Images)
   │   ├── css/
   │   │   └── styles.css                # Custom styles for the web application.
   │   ├── images/                       # Website icons and images.
   │   │   ├── copy.png                  # image of copy button.
   │   │   ├── favicon.ico               # image of favicon.
   │   │   ├── hide.png                  # image of hide button.
   │   │   └── show.png                  # image of show button.
   │   └── js/                           # JavaScript scripts for frontend functionality.
   │       ├── edit.js                   # Handle logic regarding generating, copying, displaying, hiding/unhiding passwords.
   │       ├── register.js               # Handle logic regarding generating, copying, displaying, hiding/unhiding passwords.
   │       └── show.js                   # Handle logic regarding copying, displaying, hiding/unhiding passwords.
   ├── templates/                        # HTML templates for the Flask application.
   │   ├── all_vaults.html               # Template to display all vaults.
   │   ├── edit_vault.html               # Template to add/edit a vault.
   │   ├── footer.html                   # Template to show footer (twitter, github and facebook button).
   │   ├── header.html                   # Registration page template.
   │   ├── login.html                    # Login page template. 
   │   ├── register.html                 # Registration page template. 
   │   └── show_vault.html               # Template to show a specific vault's details. 
   ├── venv/                             # Virtual environment directory (not included in Git).
   ├── .env                              # Environment variables (not included in Git).
   ├── .gitignore                        # Git ignore file (ensures sensitive files aren't committed).
   ├── forms.py                          # Forms for handling user input.
   ├── main.py                           # Main application logic and route definitions.
   ├── password_breached.py              # Module to check for breached passwords.
   ├── password_input.py                 # Module to handle password import and storage.
   ├── password_manager.py               # Module for password encryption and decryption.
   ├── requirements.txt                  # List of dependencies required for the project.
   ├── README.md                         # Project documentation.
   └── LICENSE.md                        # License.
```

## Environment Variables
The `.env` file should contain the following variables:
- **SECRET_KEY**: A secret key for your Flask app, used for sessions and CSRF protection.
- **DB_PATH**: The path to your SQLite database file.
- **DEFAULT_BROWSER**: The name of the default browser to use for password management if none is specified.

Example `.env` file:
```
   SECRET_KEY="cd374dedwoaidwedcwjk374rfde"
   DB_PATH="./instance/pwmanager.db"
   CHROME_LOCAL_STATE_PATH="C:/Users/<Name>/AppData/Local/Google/Chrome/User Data/Local State"
   EDGE_LOCAL_STATE_PATH="C:/Users/<Name>/AppData/Local/Microsoft/Edge/User Data/Local State"
   CHROME_DB_PATH="C:/Users/<Name>/AppData/Local/Google/Chrome/User Data/Default/Login Data"
   EDGE_DB_PATH="C:/Users/<Name>/AppData/Local/Microsoft/Edge/User Data/Default/Login Data"
   DEFAULT_BROWSER="Chrome"
```

## Database Models
The application uses SQLAlchemy for database management with the following models:

### User Model
- `id`: Integer, Primary Key
- `email`: String, Unique
- `password`: String (hashed password)
- `name`: String
- `browser`: String (the browser used for password storage)
- `encrypted_key`: LargeBinary (encryption key)

### Account Model
- `id`: Integer, Primary Key
- `user_id`: Integer (Foreign Key linked to User)
- `url`: String (base URL of the account)
- `full_url`: String (full URL of the account)
- `icon`: String (URL to the website icon)
- `username`: String (username used for the account)
- `password`: LargeBinary (encrypted password)
- `browser`: String (the browser used for the account)
- `is_breached`: Boolean (status if the password is breached)
- `date_created`: Integer (timestamp when the account was created - not accurate after import)
- `date_last_used`: Integer (timestamp when the account was last used - not accurate after import)
- `date_password_modified`: Integer (timestamp when the password was last changed - not accurate after import)

## Security Considerations
- **Password Encryption**: Ensure the passwords are stored securely using encryption.
- **Database Security**: Store the database file in a secure location and restrict access permissions.
- **Environment Variables**: Do not commit the `.env` file to the repository. Store sensitive information in environment variables.

## Contributing
Contributions are welcome! Please fork the repository and submit a pull request for any new features or bug fixes.

## License
This project is licensed under the MIT License. See the `LICENSE` file for details.


