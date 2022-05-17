from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError
from .models import User


class RegisterForm(FlaskForm):

    def validate_email_address(self, given_email_address):
        email_address = User.query.filter_by(email_address=given_email_address.data).first()
        if email_address:
            raise ValidationError('Account already exists!')

    first_name = StringField(label='First Name:', validators=[Length(min=2, max=50), DataRequired()])
    email_address = StringField(label='Email Address:', validators=[Email(), DataRequired()])
    password1 = PasswordField(label='Password:', validators=[Length(min=6), DataRequired()])
    password2 = PasswordField(label='Confirm Password:', validators=[EqualTo('password1'), DataRequired()])
    submit = SubmitField(label='Create Account')
