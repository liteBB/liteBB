# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm as Form
from wtforms import StringField, TextAreaField, RadioField, BooleanField, SelectField, SubmitField, PasswordField, FileField, DateField
from wtforms.validators import Required, Length, Regexp, DataRequired
from wtforms import ValidationError
from flask_pagedown.fields import PageDownField
from flask_babel import lazy_gettext as _l
from ..models import User


class PostForm(Form):
    content = PageDownField('', validators=[DataRequired()], render_kw={'autofocus': 'autofocus', 'placeholder': _l('New post...')})
    submit = SubmitField(_l('Post'), render_kw={'onclick': 'return loading()'})
    file = FileField('', render_kw={'onchange': 'ValidateSize(this)'})
    public = BooleanField(_l('Public'), default=True)


class EditForm(Form):
    content = PageDownField('', validators=[DataRequired()])
    submit = SubmitField(_l('Save'), render_kw={'onclick': 'return loading()'})
    file = FileField('', render_kw={'onchange': 'ValidateSize(this)'})
    public = BooleanField(_l('Public'))


class CommentForm(Form):
    content = PageDownField('', validators=[DataRequired()], render_kw={'autofocus': 'autofocus'})
    submit = SubmitField(_l('Submit'))


class ExportForm(Form):

    export = RadioField('', choices=[('html', _l('Export in HTML format')),
                                      ('md', _l('Export in Markdown format'))], default='html')
    submit = SubmitField(_l('Done'))


class SearchForm(Form):
    keyword = StringField('', validators = [DataRequired(), Length(1, 64)], render_kw={'placeholder': _l('Keyword')})
    submit = SubmitField(_l('Search'))


class LanguageForm(Form):
    language = RadioField('', choices=[('en', 'English'),
                                       ('zh-CN', '中文(简体)')])
    submit = SubmitField(_l('Save'))


class ProfileForm(Form):
    photo = FileField(_l('Upload/Change Photo'), render_kw={'accept': 'image/*'})
    gender = SelectField(_l('Gender'), choices=[('Male', _l('Male')), ('Female', _l('Female')), ('Other', _l('Other'))])
    birthday = DateField(_l('Birthday (eg. 1999/01/31)'), default='', validators=[DataRequired()], format='%Y/%m/%d')
    introduction = TextAreaField(_l('Introduction'), validators=[DataRequired()], render_kw={'placeholder': _l('Who I am...')})
    submit = SubmitField(_l('Save'))


class UserNameForm(Form):
    username = StringField(_l('New Username'), validators=[DataRequired(), Length(1, 32)])
    submit = SubmitField(_l('Save'))

    def validate_username(self, field):
        if User.query.filter_by(user_name=field.data).first():
            raise ValidationError(_l('Username already in use.'))

class PhotoForm(Form):
    title = StringField('', render_kw={'placeholder': _l('Description')})
    submit = SubmitField(_l('Upload'), render_kw={'onclick': 'return loading()'})
    file = FileField('', validators=[DataRequired()], render_kw={'accept': 'image/*'})
    public = BooleanField(_l('Public'), default=True)


class EditImageForm(Form):
    title = StringField('', validators=[DataRequired(), Length(1, 128)], render_kw={'placeholder': _l('Description')})
    submit = SubmitField(_l('Confirm'))
    public = BooleanField(_l('Public'), default=True)
