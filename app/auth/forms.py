# -*- coding: utf-8 -*-


from flask_wtf import FlaskForm as Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Regexp, EqualTo
from wtforms import ValidationError
from flask_babel import _, lazy_gettext as _l



class LoginForm(Form):
    user_name = StringField('', validators=[DataRequired(), Length(1, 32)], render_kw={'autofocus': 'autofocus', 'placeholder': _l('Username')})
    submit = SubmitField(_l('Log in'))

class LoginPasswordForm(Form):
    password = PasswordField('', validators=[DataRequired()], render_kw={'autofocus': 'autofocus', 'placeholder': _l('password')})
    submit = SubmitField(_l('Confirm'))
    remember_me = BooleanField(_l('Remember me'), default=True)

class ChangePasswordForm(Form):
    password_old = PasswordField(_l('Old password'), validators=[DataRequired()])
    password1 = PasswordField(_l('New password'), validators=[DataRequired(), EqualTo('password2', message=_l('Passwords must match.'))])
    password2 = PasswordField(_l('Confirm new password'), validators=[DataRequired()])
    submit = SubmitField(_l('Done'))
