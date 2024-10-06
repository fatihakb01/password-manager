# Import modules.
from flask_wtf import FlaskForm
from wtforms.fields import StringField, SubmitField, PasswordField, SelectField, BooleanField, IntegerField
from wtforms.validators import DataRequired, Email, EqualTo, URL, NumberRange


class RegisterForm(FlaskForm):
    """
    Form for registering new users.

    Fields:
        email (StringField): The email address of the user. Validates presence and proper email format.
        password_length (IntegerField): The length of the randomly generated password.
                                        Must be between 15 and 30 characters. Default is 16.
        use_uppercase (BooleanField): A checkbox field indicating whether to include uppercase letters in
                                      the generated password. Default is True.
        use_lowercase (BooleanField): A checkbox field indicating whether to include lowercase letters in
                                      the generated password. Default is True.
        use_digits (BooleanField): A checkbox field indicating whether to include digits in the generated
                                   password. Default is True.
        use_special (BooleanField): A checkbox field indicating whether to include special characters in the
                                    generated password. Default is True.
        password1 (PasswordField): The first input for the user's password. Must match 'password2'.
        password2 (PasswordField): The second input for the user's password, used to confirm the first password.
        name (StringField): The user's full name. This field is required.
        browser_option (SelectField): A dropdown field for selecting the browser from which to import passwords.
                                      Options are 'Chrome', 'Microsoft Edge', and 'None'.
        submit (SubmitField): Button to submit the registration form.
    """
    # Add password customization fields
    password_length = IntegerField("Password Length", default=16,
                                   validators=[DataRequired(),
                                               NumberRange(min=15, max=30,
                                                           message='Length should be between 15 and 30 characters')
                                               ])
    use_uppercase = BooleanField("Include Uppercase Letters", default=True)
    use_lowercase = BooleanField("Include Lowercase Letters", default=True)
    use_digits = BooleanField("Include Digits", default=True)
    use_special = BooleanField("Include Special Characters", default=True)

    # Password fields with matching validation
    password1 = PasswordField(
        'New Password',
        validators=[DataRequired(),
                    EqualTo('password2', message='Passwords must match')])

    password2 = PasswordField(
        'Repeat Password',
        validators=[DataRequired()])

    # Other existing fields
    email = StringField("Email", validators=[DataRequired(), Email()])
    name = StringField("Name", validators=[DataRequired()])
    browser_option = SelectField(
        "From which browser would you like to import your passwords?",
        choices=[('Chrome', 'Chrome'), ('Microsoft Edge', 'Microsoft Edge'), ('None', None)],
        validators=[DataRequired()]
    )
    submit = SubmitField("Sign Me Up!")


class LoginForm(FlaskForm):
    """
    Form for logging in existing users.

    Fields:
        email (StringField): The email address of the user. Validates presence and proper email format.
        password (PasswordField): The password of the user. This field is required.
        submit (SubmitField): Button to submit the login form.
    """
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Let Me In!")


class EditVaultForm(FlaskForm):
    """
    Form for adding or editing account details in a user's vault.

    Fields:
        url (StringField): The website URL for the account. Validates presence and proper URL format.
        username (StringField): The username associated with the account. This is an optional field.
        password (PasswordField): The password for the account. This is an optional field.
        password_length (IntegerField): The length of the randomly generated password.
                                        Must be between 15 and 30 characters. Default is 16.
        use_uppercase (BooleanField): A checkbox field indicating whether to include uppercase letters in
                                      the generated password. Default is True.
        use_lowercase (BooleanField): A checkbox field indicating whether to include lowercase letters in
                                      the generated password. Default is True.
        use_digits (BooleanField): A checkbox field indicating whether to include digits in the generated
                                   password. Default is True.
        use_special (BooleanField): A checkbox field indicating whether to include special characters in the
                                    generated password. Default is True.
        submit (SubmitField): Button to save the form changes.
        generate (SubmitField): Button to trigger random password generation.
    """
    url = StringField("URL",
                      validators=[DataRequired(), URL(message="You should start your url with 'https://'")])
    username = StringField("Username")
    password = PasswordField(
        "Password",
        validators=[DataRequired()])
    password_length = IntegerField(
        "Password Length", default=16,
        validators=[DataRequired(),
                    NumberRange(min=15, max=30, message='Length should be between 15 and 30 characters')
                    ])
    use_uppercase = BooleanField("Include Uppercase Letters", default=True)
    use_lowercase = BooleanField("Include Lowercase Letters", default=True)
    use_digits = BooleanField("Include Digits", default=True)
    use_special = BooleanField("Include Special Characters", default=True)
    submit = SubmitField("Save Changes")
    generate = SubmitField("Generate Random Password")
