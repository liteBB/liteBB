# -*- coding: utf-8 -*-


import uuid
from datetime import datetime, timedelta
from flask import render_template, request, make_response, flash, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from flask_babel import _
from . import auth
from .. import db
from ..models import User, LoginLog
from .forms import LoginForm, LoginPasswordForm, ChangePasswordForm



@auth.before_app_first_request
def before_app_first_request():

    if not User.query.filter_by(id=1).first():

        user = User(user_name='admin',
                    password='admin',
                    update_password=uuid.uuid4().hex,
                    language='en-US',
                    ip='127.0.0.1')
        db.session.add(user)
        db.session.commit()

    return redirect(url_for('auth.login'))


@auth.route('/login', methods=['GET', 'POST'])
def login():

    form = LoginForm()

    if form.validate_on_submit():

        user = User.query.filter(User.user_name == form.user_name.data).first()

        if user is not None:
            response = make_response(redirect(url_for('auth.login_password', user_name=user.user_name, next=request.args.get('next'))))
            return response
        else:
            flash(_('User %(username)s not found.', username=form.user_name.data))
            return redirect(url_for('auth.login'))

    return render_template('auth/login.html', form=form)


@auth.route('/login_password/<user_name>', methods=['GET', 'POST'])
def login_password(user_name):

    ip = request.environ.get('HTTP_X_REAL_IP') or request.remote_addr
    form = LoginPasswordForm()

    if form.validate_on_submit():

        if LoginLog.query.filter(LoginLog.ip == ip, LoginLog.status == -1, LoginLog.timestamp > datetime.utcnow() - timedelta(hours=1)).count() > 10:
            flash(_('Too many incorrect attempts, please try again later.'))
            return redirect(url_for('auth.login'))

        user = User.query.filter(User.user_name == user_name).first()

        if user is not None:

            if LoginLog.query.filter(LoginLog.user_id == user.id, LoginLog.status == -1, LoginLog.timestamp > datetime.utcnow() - timedelta(hours=1)).count() > 100:
                flash(_('Too many incorrect attempts, please try again later.'))
                return redirect(url_for('auth.login'))

            if user.verify_password(form.password.data):

                login_log = LoginLog(user_id=user.id,
                                     ip=ip)
                db.session.add(login_log)
                db.session.commit()

                login_user(user, form.remember_me.data)
                update_password = user.update_password
                response = make_response(redirect(request.args.get('next') or url_for('main.index')))
                response.set_cookie('up', update_password, max_age=365*24*60*60)

                return response

            else:

                login_log = LoginLog(user_id=user.id,
                                     ip=ip,
                                     status=-1)
                db.session.add(login_log)
                db.session.commit()

                flash(_('Invalid username or password.'))

        else:

            flash(_('Invalid username or password.'))

    user_name = user_name

    return render_template('auth/login_password.html', form=form, user_name=user_name)


@auth.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():

    form = ChangePasswordForm()
    if form.validate_on_submit():

        if current_user.verify_password(form.password_old.data):
            current_user.password = form.password1.data
            current_user.update_password=uuid.uuid4().hex
            db.session.add(current_user)
            db.session.commit()

            update_password = current_user.update_password
            response = make_response(redirect(url_for('main.account')))
            response.set_cookie('up', update_password, max_age=365 * 24 * 60 * 60)

            flash(_('Your password has been updated.'))
            return response

        else:

            flash(_('Invalid old password.'))

    return render_template('auth/change_password.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash(_('You have been logged out.'))
    return redirect(url_for('main.index'))

