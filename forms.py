# Import libraries.
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, SelectField
from wtforms.validators import DataRequired, Email, InputRequired, EqualTo, Length
from flask_ckeditor import CKEditorField


# Create a RegisterForm to register new users.
class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password1 = PasswordField('New Password',
                              [InputRequired(),
                               EqualTo('password2', message='Passwords must match'),
                               Length(10, 20, message='Length should be between 10 and 20 characters/numbers/symbols')
                               ])
    password2 = PasswordField('Repeat Password', validators=[DataRequired()])
    name = StringField("Name", validators=[DataRequired()])
    browser_option = SelectField(
        "From which browser would you like to import your passwords?",
        choices=[
            ('Chrome', 'Chrome'),
            ('Brave', 'Brave'),
            ('Firefox', 'Firefox'),
            ('Microsoft Edge', 'Microsoft Edge'),
            ('All', 'All Browsers'),
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
