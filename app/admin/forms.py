# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm as Form
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from wtforms import ValidationError
from flask_babel import _, lazy_gettext as _l


class ResetForm(Form):
    secret_key = StringField('', validators=[DataRequired()], render_kw={'placeholder': _l('Secret key')})
    submit = SubmitField(_l('Reset admin'))
