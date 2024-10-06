# Import modules.
import os
import sqlite3
from datetime import datetime
from urllib.parse import urlparse
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_bootstrap import Bootstrap5
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean, UniqueConstraint
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from forms import RegisterForm, LoginForm, EditVaultForm
from password_input import PasswordInput, get_clearbit_logo
from password_manager import PasswordManager
from password_breached import PasswordBreached
from dotenv import load_dotenv

# Initialize the Flask application and Bootstrap extension.
load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
Bootstrap5(app)

# Set up the login manager.
login_manager = LoginManager()
login_manager.init_app(app)


# Define the base model class for the database.
class Base(DeclarativeBase):
    pass


# Set up the SQLAlchemy database connection.
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pwmanager.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# Define the User model.
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(100))
    browser: Mapped[str] = mapped_column(String(100))
    encrypted_key: Mapped[bytes] = mapped_column(db.LargeBinary, nullable=True)
    accounts = relationship("Account", back_populates="parent_user")


# Define the Account model.
class Account(db.Model):
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

    __table_args__ = (UniqueConstraint('user_id', 'full_url', 'username', name='unique_user_url_username'),)
    parent_user = relationship("User", back_populates="accounts")


# Define the user loader callback for Flask-Login.
@login_manager.user_loader
def load_user(user_id):
    """
    Load a user by their user ID.

    Parameters:
        user_id (int): The ID of the user to load.

    Returns:
        User: The user instance or a 404 error if not found.
    """
    return db.get_or_404(User, user_id)


# Create the database if it doesn't exist.
with app.app_context():
    db.create_all()


# Decorator to check if a user is signed in.
def signed_in(f):
    """
    Decorator to ensure the user is signed in.

    Parameters:
        f (function): The function to wrap.

    Returns:
        function: A wrapped function that checks if the user is authenticated.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


# Register a new user account.
@app.route('/register', methods=["GET", "POST"])
def register():
    """
    Register a new user.

    If registration is successful, log the user in and redirect them to the vaults page.

    Returns:
        render_template (str): Renders the registration page with the form if GET request,
                               or redirects to the vaults page after successful registration.
    """
    form = RegisterForm()
    selected_browser = form.browser_option.data
    password_input = PasswordInput(selected_browser)
    if form.validate_on_submit():
        email = form.email.data
        result = db.session.execute(db.select(User).where(User.email == email))
        user = result.scalar()

        if user:
            flash("You've already signed up with that email, log in instead!", "failure")
            return redirect(url_for('login'))

        has_and_salted_password = generate_password_hash(
            password=form.password1.data,
            method="pbkdf2:sha256",
            salt_length=8
        )

        new_user = User(
            email=form.email.data,
            name=form.name.data,
            browser=selected_browser,
            password=has_and_salted_password
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)

        if app.config['SQLALCHEMY_DATABASE_URI']:
            password_input.import_browser()
            password_input.insert_data()

        return redirect(url_for("all_vaults"))

    return render_template("register.html", current_user=current_user, form=form)


# Log in an existing user.
@app.route('/', methods=["GET", "POST"])
def login():
    """
    Log in an existing user.

    If login is successful, redirect to the vaults page. If the credentials are incorrect,
    display an error message and reload the login page.

    Returns:
        render_template (str): Renders the login page with the form if GET request,
                               or redirects to the vaults page after successful login.
    """
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        result = db.session.execute(db.select(User).where(User.email == email))
        user = result.scalar()

        if not user:
            flash("That email does not exist, please try again.", "failure")
            return redirect(url_for('login'))
        elif not check_password_hash(user.password, password):
            flash("Password incorrect, please try again.", "failure")
            return redirect(url_for('login'))
        else:
            login_user(user)
            return redirect(url_for('all_vaults'))

    return render_template("login.html", form=form, current_user=current_user)


# Log out the user.
@app.route('/logout')
def logout():
    """
    Log out the current user and redirect to the login page.

    Returns:
        redirect (str): Redirects to the login page after logging out.
    """
    logout_user()
    return redirect(url_for("login"))


# Display all vaults for the signed-in user.
@signed_in
@app.route('/vaults')
def all_vaults():
    """
    Display all vaults (accounts) for the signed-in user.

    Returns:
        render_template (str): Renders the all vaults page showing the user's accounts.
    """
    result = db.session.execute(db.select(Account).where(Account.user_id == current_user.id))
    accounts = result.scalars().all()
    return render_template("all_vaults.html", current_user=current_user,
                           accounts=accounts, referrer="all_vaults")


# Check for breached vaults and update the status.
@signed_in
@app.route('/check_breaches')
def check_breaches():
    """
    Check for any breached passwords for the user's accounts and update the breach status.

    Returns:
        redirect (str): Redirects to the all vaults page after updating breach statuses.
    """
    result = db.session.execute(db.select(Account).where(Account.user_id == current_user.id))
    accounts = result.scalars().all()

    for account in accounts:
        password_breached = PasswordBreached(account.browser, current_user.id, account.id)
        is_breached = password_breached.check_password_pwned()
        account.is_breached = is_breached
        db.session.commit()

    flash('Breached vaults have been checked and updated.', 'success')
    return redirect(url_for('all_vaults'))


# Display only breached vaults.
@signed_in
@app.route('/breached_vaults')
def breached_vaults():
    """
    Display only the vaults (accounts) that have been marked as breached.

    Returns:
        render_template (str): Renders the all vaults page showing only breached accounts.
    """
    breached_accounts = db.session.execute(
        db.select(Account).where(Account.is_breached == 1, Account.user_id == current_user.id)
    ).scalars().all()

    return render_template("all_vaults.html", current_user=current_user,
                           accounts=breached_accounts, referrer="breached_vaults")


# Display a specific vault's details.
@signed_in
@app.route('/vaults/<int:account_id>', methods=["GET", "POST"])
def show_vault(account_id):
    """
    Display the details of a specific vault (account), including its decrypted password.

    Parameters:
        account_id (int): The ID of the account to display.

    Returns:
        render_template (str): Renders the vault details page with the account information.
    """
    account = db.get_or_404(Account, account_id)
    manager = PasswordManager(account.browser)
    decrypted_password = manager.read_and_decrypt_password(current_user.id, account.id)
    referrer = request.args.get('ref', 'all_vaults')

    return render_template("show_vault.html", current_user=current_user,
                           account=account, decrypted_password=decrypted_password, referrer=referrer)


# Delete a specific vault.
@signed_in
@app.route('/vaults/<int:account_id>/delete', methods=["POST"])
def delete_vault(account_id):
    """
    Delete a specific vault (account) and redirect to the appropriate page based on referrer.

    Parameters:
        account_id (int): The ID of the account to delete.

    Returns:
        redirect (str): Redirects to the all vaults page after deletion.
    """
    account = db.get_or_404(Account, account_id)
    db.session.delete(account)
    db.session.commit()

    flash('Account deleted successfully!', 'success')
    referrer = request.args.get('ref', 'all_vaults')
    return redirect(url_for(referrer))


# Edit the details of a specific vault.
@signed_in
@app.route('/vaults/<int:account_id>/edit', methods=["GET", "POST"])
def edit_vault(account_id):
    """
    Edit the details (URL, username, password) of a specific vault (account) and save changes.

    Parameters:
        account_id (int): The ID of the account to edit.

    Returns:
        render_template (str): Renders the edit vault page with the form if GET request,
                            or redirects to the vaults page after successful update.
    """
    account = db.get_or_404(Account, account_id)
    manager = PasswordManager(account.browser)
    decrypted_password = manager.read_and_decrypt_password(current_user.id, account.id)
    form = EditVaultForm(obj=account)

    if form.validate_on_submit():
        account.url = form.url.data
        account.username = form.username.data
        account.password = manager.encrypt_and_store_password(form.password.data)
        db.session.commit()

        flash('Account updated successfully!', 'success')
        return redirect(url_for('show_vault', account_id=account.id, ref=request.args.get('ref', 'all_vaults')))

    return render_template("edit_vault.html", form=form, account=account, decrypted_password=decrypted_password)


# Add the information to a new vault.
@signed_in
@app.route('/vaults/add', methods=["GET", "POST"])
def add_vault():
    """
    Add a new vault (account) to the user's account.
    If the account is added successfully, redirect to the vaults page.
    Otherwise, the account already exist, stay on the add page.

    Returns:
        render_template (str): Renders the add vault page with the form if GET request,
        or redirects to the vaults page after successful addition, or stay on the add page
        in case of failure.
    """
    form = EditVaultForm()
    db_path = os.getenv("DB_PATH")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT browser FROM users WHERE id = ?", (current_user.id,))
    browser = cursor.fetchone()[0]

    if browser is None:
        browser = os.getenv("DEFAULT_BROWSER")
    conn.close()

    if form.validate_on_submit():
        try:
            parsed_url = urlparse(form.url.data)
            base_url = parsed_url.scheme + '://' + parsed_url.netloc

            new_account = Account(
                user_id=current_user.id,
                url=base_url,
                full_url=form.url.data,
                icon=get_clearbit_logo(form.url.data),
                username=form.username.data,
                password=form.password.data,
                browser=browser,
                date_created=int(datetime.now().timestamp()),
                date_last_used=int(datetime.now().timestamp()),
                date_password_modified=int(datetime.now().timestamp())
            )

            manager = PasswordManager(browser)
            new_account.password = manager.encrypt_and_store_password(form.password.data)
            db.session.add(new_account)
            db.session.commit()

            flash('Account added successfully!', 'success')
            return redirect(url_for('all_vaults'))
        except Exception as e:
            print({e})
            flash('Account already exist!', 'failure')

    return render_template("edit_vault.html", form=form, account=None,
                           decrypted_password=None)


# Run Flask application with debug mode turned on.
if __name__ == "__main__":
    app.run(debug=True, port=5000)
