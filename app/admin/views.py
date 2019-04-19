# -*- coding: utf-8 -*-

from flask import render_template, request, flash, redirect, url_for, current_app, Response
from flask_login import login_required, current_user
from flask_babel import _
from .. import db, csrf
from . import admin
from ..models import User, Post, Comment
from .forms import ResetForm


@admin.route('/')
@admin.route('/comments')
@login_required
def comments():

    current_user.new_comment = None
    db.session.add(current_user)
    db.session.commit()

    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.order_by(Comment.create_time.desc()) \
        .paginate(page, per_page=current_app.config['LISTS_PER_PAGE'], error_out=False)
    comments = pagination.items

    return render_template('admin/comments.html', comments=comments, pagination=pagination)


@admin.route('/moderate', methods=['GET', 'POST'])
@csrf.exempt
@login_required
def moderate():

    comment_id = request.form.get('commentid')
    comment = Comment.query.filter_by(id=comment_id).first()

    if comment.approved == 1:
        comment.approved = 0
        db.session.add(comment)
        db.session.commit()
        return Response(str(comment.approved))
    elif comment.approved == 0:
        comment.approved = 1
        db.session.add(comment)
        db.session.commit()
        return Response(str(comment.approved))


@admin.route('/reset', methods=['GET', 'POST'])
def reset():

    form = ResetForm()

    if form.validate_on_submit():

        if form.secret_key.data != 'hard-to-guess-string' and form.secret_key.data == current_app.config['SECRET_KEY']:

            user = User.query.filter_by(id=1).first()
            user.user_name = 'admin'
            user.password = 'admin'
            db.session.add(user)
            db.session.commit()

            posts = Post.query.filter(Post.user_id == 1).all()
            for post in posts:
                post.user_name = 'admin'
                db.session.add(post)
            db.session.commit()

            flash(_('User/Password has been reset to admin/admin'))
            return redirect(url_for('auth.login'))

        else:

            flash(_('Incorrect secret key! Please try again.'))

    return render_template('admin/reset.html', form=form)