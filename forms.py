# Import libraries.
from flask_wtf import FlaskForm
from wtforms.fields import StringField, SubmitField, PasswordField, SelectField
from wtforms.validators import DataRequired, Email, InputRequired, EqualTo, Length, URL


# Create a RegisterForm to register new users.
class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password1 = PasswordField('New Password',
                              [InputRequired(),
                               EqualTo('password2', message='Passwords must match'),
                               Length(10, 30, message='Length should be between 10 and 30 characters/numbers/symbols')
                               ])
    password2 = PasswordField('Repeat Password', validators=[DataRequired()])
    name = StringField("Name", validators=[DataRequired()])
    browser_option = SelectField(
        "From which browser would you like to import your passwords?",
        choices=[
            ('Chrome', 'Chrome'),
            ('Microsoft Edge', 'Microsoft Edge'),
            ('None', 'None')
        ],
        validators=[DataRequired()]
    )
    submit = SubmitField("Sign Me Up!")


# Create a LoginForm to login existing users.
class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Let Me In!")


# Create an EditForm to edit account details.
class EditVaultForm(FlaskForm):
    url = StringField("URL", validators=[DataRequired(), URL()])
    username = StringField("Username")
    password = PasswordField("Password")
    submit = SubmitField("Save Changes")
