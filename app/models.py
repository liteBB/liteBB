# -*- coding: utf-8 -*-

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from . import db, login_manager
from markdown import markdown
import bleach



class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(32), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    update_password = db.Column(db.String(32))
    new_comment = db.Column(db.DateTime)
    last_export = db.Column(db.DateTime)
    export_path = db.Column(db.String(32))
    status = db.Column(db.Integer, default=1)
    language = db.Column(db.String(8))
    ip = db.Column(db.String(48), index=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User %r>' % self.user_name

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class UserProfile(db.Model):
    __tablename__ = 'user_profiles'
    user_id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(64))
    gender = db.Column(db.String(10))
    birthday = db.Column(db.Date)
    photo = db.Column(db.String(64))
    introduction = db.Column(db.Text())
    address = db.Column(db.String(128))


class LoginLog(db.Model):
    __tablename__ = 'login_logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, index=True)
    ip = db.Column(db.String(48))
    status = db.Column(db.Integer, default=1)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(32), index=True)
    user_id = db.Column(db.Integer, index=True)
    user_name = db.Column(db.String(64), index=True)
    summary = db.Column(db.Text)
    summary_html = db.Column(db.Text)
    content = db.Column(db.Text)
    content_html = db.Column(db.Text)
    image = db.Column(db.String(48))
    video = db.Column(db.String(48))
    poster = db.Column(db.String(48))
    file_md5 = db.Column(db.String(32))
    filename = db.Column(db.String(128))
    file_size = db.Column(db.String(16))
    public = db.Column(db.Integer, default=1)
    likes_count = db.Column(db.Integer, default=0)
    views_count = db.Column(db.Integer, default=0)
    comments_count = db.Column(db.Integer, default=0)
    create_time = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    update_time = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    update_ip = db.Column(db.String(48), index=True)
    language = db.Column(db.String(8), index=True, default='en-US')

    @staticmethod
    def on_changed_summary(target, value, oldvalue, initiator):
        if value:
            allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 'del',
                            'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                            'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'br', 'hr']
            target.summary_html = bleach.linkify(bleach.clean(
                markdown(value, output_format='html', extensions=['fenced_code', 'nl2br']),
                tags=allowed_tags, strip=True))

    @staticmethod
    def on_changed_content(target, value, oldvalue, initiator):
        if value:
            allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 'del',
                            'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                            'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'br', 'hr', 'img', 'video']
            allowed_attrs = {'h1': ['id'], 'h2': ['id'], 'h3': ['id'], 'h4': ['id'], 'h5': ['id'], 'h6': ['id'],
                             'a': ['href', 'rel', 'id'], 'img': ['src', 'alt'],
                             'video': ['src', 'poster', 'width', 'height', 'controls']}
            target.content_html = bleach.linkify(bleach.clean(
                markdown(value, output_format='html', extensions=['fenced_code', 'nl2br']),
                tags=allowed_tags, strip=True, attributes=allowed_attrs))


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, index=True)
    replied_id = db.Column(db.Integer)
    content = db.Column(db.Text)
    content_html = db.Column(db.Text)
    ip = db.Column(db.String(48), index=True)
    create_time = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    language = db.Column(db.String(8), index=True, default='en-US')
    approved = db.Column(db.Integer, default=0)

    @staticmethod
    def on_changed_content(target, value, oldvalue, initiator):
        if value:
            allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 'del',
                            'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                            'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'br', 'hr', 'img', 'video']
            allowed_attrs = {'h1': ['id'], 'h2': ['id'], 'h3': ['id'], 'h4': ['id'], 'h5': ['id'], 'h6': ['id'],
                             'a': ['href', 'rel', 'id'], 'img': ['src', 'alt'],
                             'video': ['src', 'poster', 'width', 'height', 'controls']}
            target.content_html = bleach.linkify(bleach.clean(
                markdown(value, output_format='html', extensions=['fenced_code', 'nl2br']),
                tags=allowed_tags, strip=True, attributes=allowed_attrs))


class PostTag(db.Model):
    __tablename__ = 'post_tags'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(64), index=True)
    count = db.Column(db.Integer, default=0)


class PostTagRelationship(db.Model):
    __tablename__ = 'post_tag_relationships'
    post_id = db.Column(db.Integer, primary_key=True)
    post_tag_id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)


class Like(db.Model):
    __tablename__ = 'likes'
    ip = db.Column(db.String(48), primary_key=True)
    post_id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class Photo(db.Model):
    __tablename__ = 'photos'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, index=True)
    ip = db.Column(db.String(48), index=True)
    path = db.Column(db.String(16), index=True)
    image = db.Column(db.String(64), index=True)
    title = db.Column(db.String(128))
    public = db.Column(db.Integer, default=1)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)


db.event.listen(Post.content, 'set', Post.on_changed_content)
db.event.listen(Post.summary, 'set', Post.on_changed_summary)
db.event.listen(Comment.content, 'set', Comment.on_changed_content)





