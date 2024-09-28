# Import libraries.
import os
from datetime import date
from flask import Flask, abort, render_template, redirect, url_for, flash, request, jsonify
from flask_bootstrap import Bootstrap5
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean, UniqueConstraint
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from forms import RegisterForm, LoginForm, EditVaultForm
from password_input import PasswordInput
from password_manager import PasswordManager
from password_breached import PasswordBreached
from dotenv import load_dotenv

'''
Make sure the required packages are installed: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from the requirements.txt for this project.
'''

# Create the Flask application and initialise the bootstrap extensions.
load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
Bootstrap5(app)

# Connect Flask to the login manager (extension).
login_manager = LoginManager()
login_manager.init_app(app)


# Create the database.
class Base(DeclarativeBase):
    pass


# Connect Flask application to the Database (extension).
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pwmanager.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# Create a users table for all registered users.
# Implement the default Flask-login (UserMixin).
class User(UserMixin, db.Model):
    # Define table name and columns
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(100))
    encrypted_key: Mapped[bytes] = mapped_column(db.LargeBinary, nullable=True)

    # Connect users with accounts table
    accounts = relationship("Account", back_populates="parent_user")


# Create an accounts table for all accounts that belong to the user.
class Account(db.Model):
    # Define table name and columns
    __tablename__ = "accounts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("users.id"))
    url: Mapped[str] = mapped_column(String(100))
    full_url: Mapped[str] = mapped_column(String(100))
    icon: Mapped[str] = mapped_column(String(100), nullable=True)
    username: Mapped[str] = mapped_column(String(100))
    password: Mapped[str] = mapped_column(db.LargeBinary)
    browser: Mapped[str] = mapped_column(String(100))
    is_breached: Mapped[bool] = mapped_column(Boolean, nullable=True)
    date_created: Mapped[int] = mapped_column(Integer, nullable=False)
    date_last_used: Mapped[int] = mapped_column(Integer, nullable=False)
    date_password_modified: Mapped[int] = mapped_column(Integer, nullable=False)

    # Enforce unique combination of user_id, full_url, and username
    __table_args__ = (UniqueConstraint('user_id', 'full_url', 'username', name='unique_user_url_username'),)

    # Connect accounts with users table
    parent_user = relationship("User", back_populates="accounts")


# You will need to provide a user_loader callback.
# This callback is used to reload the user object from the user ID stored in the session.
# It should take the str ID of a user, and return the corresponding user object.
@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)


# Create the database environment.
with app.app_context():
    db.create_all()


# # Create admin-only decorator.
def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # If id is not 1 then return abort with 403 error.
        if current_user.is_authenticated and current_user.id != 1:
            return abort(403)
        # If user is anonymous then return abort with 404 error.
        elif current_user.is_anonymous:
            return abort(404)
        else:
            # Otherwise continue with the route function.
            return f(*args, **kwargs)

    return decorated_function


# Go to the home page.
@app.route('/')
def home():
    # return "Hello world"
    return render_template("index.html", current_user=current_user)


# Show all vaults (all accounts)
@app.route('/vaults')
def all_vaults():
    result = db.session.execute(db.select(Account).where(Account.user_id == current_user.id))
    accounts = result.scalars().all()
    return render_template("all_vaults.html", current_user=current_user,
                           accounts=accounts, referrer="all_vaults")


# Check and update breached vaults (but don't render any page)
@app.route('/check_breaches')
def check_breaches():
    # Query all accounts of the current user
    result = db.session.execute(db.select(Account).where(Account.user_id == current_user.id))
    accounts = result.scalars().all()

    # Check for breached passwords and update the is_breached status
    for account in accounts:
        password_breached = PasswordBreached(account.browser, current_user.id, account.id)
        is_breached = password_breached.check_password_pwned()

        # Update is_breached column in the database
        account.is_breached = is_breached
        db.session.commit()

    # After checking, redirect back to the all vaults page
    flash('Breached vaults have been checked and updated.', 'success')
    return redirect(url_for('all_vaults'))


# Show only the breached vaults (no checking, just display)
@app.route('/breached_vaults')
def breached_vaults():
    # Query accounts with breached passwords (only those already marked as breached)
    breached_accounts = db.session.execute(
        db.select(Account).where(Account.is_breached == 1)
    ).scalars().all()

    return render_template("all_vaults.html", current_user=current_user,
                           accounts=breached_accounts, referrer="breached_vaults")


# Show a specific vault
@app.route('/vaults/<int:account_id>', methods=["GET", "POST"])
def show_vault(account_id):
    account = db.get_or_404(Account, account_id)
    manager = PasswordManager(account.browser)

    # Decrypt the password stored as a BLOB
    decrypted_password = manager.read_and_decrypt_password(current_user.id, account.id)

    # Get the referrer from the query string (either 'all_vaults' or 'breached_vaults')
    referrer = request.args.get('ref', 'all_vaults')

    return render_template("show_vault.html", current_user=current_user,
                           account=account, decrypted_password=decrypted_password, referrer=referrer)


# Route to delete a specific vault
@app.route('/vaults/<int:account_id>/delete', methods=["POST"])
def delete_vault(account_id):
    account = db.get_or_404(Account, account_id)

    # Delete the account from the database
    db.session.delete(account)
    db.session.commit()

    # Notify the user and redirect them back to the all vaults page (or breached_vaults based on referrer)
    flash('Account deleted successfully.', 'success')
    referrer = request.args.get('ref', 'all_vaults')
    return redirect(url_for(referrer))


# Edit the information inside the vault.
@app.route('/vaults/<int:account_id>/edit', methods=["GET", "POST"])
def edit_vault(account_id):
    account = db.get_or_404(Account, account_id)
    manager = PasswordManager(account.browser)

    # Decrypt the password to show in the form
    decrypted_password = manager.read_and_decrypt_password(current_user.id, account.id)

    # Prefill the form with account data
    form = EditVaultForm(obj=account)

    if form.validate_on_submit():
        # Normal submission without generating a password (password already filled by JavaScript if generated)
        account.url = form.url.data
        account.username = form.username.data

        # Encrypt and store the new password (from input field)
        account.password = manager.encrypt_and_store_password(form.password.data)

        # Save the changes to the database
        db.session.commit()

        flash('Account updated successfully!', 'success')
        return redirect(url_for('show_vault', account_id=account.id, ref=request.args.get('ref', 'all_vaults')))

    return render_template("edit_vault.html", form=form, account=account, decrypted_password=decrypted_password)


# Register a new user account and redirect the user to the
# home page if registration has been successful.
@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    selected_browser = form.browser_option.data
    password_input = PasswordInput(selected_browser)
    # Check if form has been submitted.
    if form.validate_on_submit():
        # Check if user email is already present in the database.
        email = form.email.data
        result = db.session.execute(db.select(User).where(User.email == email))
        user = result.scalar()

        # Redirect user to login page if user already exists.
        if user:
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('login'))

        # Hashing and salting the password entered by the user.
        has_and_salted_password = generate_password_hash(
            password=form.password1.data,
            method="pbkdf2:sha256",
            salt_length=8
        )

        # Storing the hashed password in our database.
        new_user = User(
            email=form.email.data,
            name=form.name.data,
            password=has_and_salted_password
        )
        db.session.add(new_user)
        db.session.commit()

        # Log in and authenticate user after adding details to database.
        login_user(new_user)

        # Import the password from the browser and insert it into the accounts table
        if app.config['SQLALCHEMY_DATABASE_URI']:
            password_input.import_browser()
            password_input.insert_data()

        # Can redirect() and get name from the current_user.
        return redirect(url_for("all_vaults"))

    # Passing True or False if the user is authenticated.
    return render_template("register.html", current_user=current_user, form=form)


# Retrieve a user from the database based on their email.
@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        # Find user by email entered.
        result = db.session.execute(db.select(User).where(User.email == email))
        user = result.scalar()

        # Check whether email doesn't exist or password is incorrect.
        if not user:
            flash("That email does not exist, please try again.")
            return redirect(url_for('login'))
        elif not check_password_hash(user.password, password):
            flash("Password incorrect, please try again.")
            return redirect(url_for('login'))
        else:
            login_user(user)
            return redirect(url_for('all_vaults'))
    return render_template("login.html", form=form, current_user=current_user)


# Sign out and go to the home page.
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for("home"))


# Go to the about page.
@app.route('/about')
def about():
    return render_template("index.html", current_user=current_user)


# Go to the contact page.
@app.route('/contact')
def contact():
    return render_template("index.html", current_user=current_user)


# Run Flask application with debug mode turned on.
if __name__ == "__main__":
    app.run(debug=True, port=5000)
