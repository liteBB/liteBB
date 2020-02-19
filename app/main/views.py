# -*- coding: utf-8 -*-

import re
import os
import shutil
import hashlib, uuid
from datetime import date, datetime, timedelta
from flask import render_template, request, flash, redirect, url_for, session, current_app, g, json, jsonify, Response, Markup, escape, make_response, send_file, send_from_directory
from flask_login import login_required, current_user, logout_user
from flask_babel import _, get_locale
from flask_wtf.csrf import CSRFError
from config import APP_TITLE
from . import main
from .forms import PostForm, EditForm, CommentForm, SearchForm, LanguageForm, ProfileForm, UserNameForm, ExportForm, PhotoForm, EditImageForm
from .. import db, csrf
from ..models import User, UserProfile, LoginLog, Post, Comment, Like, PostTag, PostTagRelationship, Photo
from ..utils import convert_size, image_formats, video_formats
from ..export_posts import export_zipfile




@main.before_app_request
def before_app_request():

    if not current_user.is_authenticated:
        if 'language' in session:
            g.language = session.get('language')
        else:
            g.language = request.accept_languages.best_match(current_app.config['ACCEPT_LANGUAGES']) or 'en'
    else:
        if current_user.language in current_app.config['ACCEPT_LANGUAGES']:
            g.language = current_user.language
        else:
            g.language = request.accept_languages.best_match(current_app.config['ACCEPT_LANGUAGES']) or 'en'


@main.before_request
def before_request():

    if current_user.is_authenticated:
        if current_user.update_password != request.cookies.get('up'):
            logout_user()
            return redirect(url_for('auth.login'))


@main.route('/')
def index():

    page = request.args.get('page', 1, type=int)

    tags = PostTag.query.filter(PostTag.count > 0).order_by(PostTag.count.desc()).all()[:25]

    if not current_user.is_authenticated:

        pagination = Post.query.filter(Post.public == 1).order_by(Post.create_time.desc()) \
                .paginate(page, per_page=current_app.config['LISTS_PER_PAGE'], error_out=False)
        posts = pagination.items

    else:

        if current_user.new_comment:
            flash(Markup(_('You have new comments! <a href="/admin">View now &raquo;</a>')))

        pagination = Post.query.order_by(Post.create_time.desc()) \
            .paginate(page, per_page=current_app.config['LISTS_PER_PAGE'], error_out=False)
        posts = pagination.items

    return render_template('index.html', title=APP_TITLE, posts=posts, pagination=pagination, page=page, tags=tags)


@main.route('/new', methods=['GET', 'POST'])
@login_required
def new():

    ip = request.environ.get('HTTP_X_REAL_IP') or request.remote_addr
    form = PostForm()

    if form.validate_on_submit():

        post = Post(uuid=uuid.uuid1().hex,
                    user_id=current_user.id,
                    user_name=current_user.user_name,
                    public=form.public.data,
                    content=form.content.data,
                    summary=form.content.data[:current_app.config['SUMMARY_COUNT']],
                    update_ip=ip,
                    language=request.accept_languages.best)
        db.session.add(post)
        db.session.commit()

        if form.file.data:

            post_id = str(post.id)

            filename = re.sub('[\\\\/:*?"<>|\s]', '-', form.file.data.filename)
            buffer = form.file.data.read()

            ext = filename.split('.')

            md5_obj = hashlib.md5()
            md5_obj.update(buffer)
            file_md5 = md5_obj.hexdigest()

            if ext[-1].lower() in image_formats:

                image = file_md5 + '.' + ext[-1].lower()
                os.mkdir('app/static/image/' + post_id)
                f = open(os.path.join('app', 'static', 'image', post_id, image), 'wb')
                f.write(buffer)
                f.close()

                post.image = image

            elif ext[-1].lower() in video_formats:

                video = file_md5 + '.' + ext[-1].lower()
                os.mkdir('app/static/video/' + post_id)
                f = open(os.path.join('app', 'static', 'video', post_id, video), 'wb')
                f.write(buffer)
                f.close()

                post.video = video

            else:

                os.makedirs('app/static/attachment/' + post_id + '/' + file_md5)
                f = open(os.path.join('app', 'static', 'attachment', post_id, file_md5, filename), 'wb')
                f.write(buffer)
                f.close()

                file_size = convert_size(len(buffer))

                post.file_md5 = file_md5
                post.filename = filename
                post.file_size = file_size

        db.session.add(post)
        db.session.commit()

        return redirect(url_for('.post', postid=post.id, order='newest'))

    return render_template('new.html', title=APP_TITLE, form=form)


@main.route('/edit/<int:postid>', methods=['GET', 'POST'])
@login_required
def edit(postid):

    post = Post.query.filter_by(id=postid).first_or_404()

    if post.user_id != current_user.id:
        flash(_('You can not edit this post!'))
        return redirect(url_for('.post', postid=postid, order='newest'))

    form = EditForm()
    ip = request.environ.get('HTTP_X_REAL_IP') or request.remote_addr

    if form.validate_on_submit():        

        post.uuid = uuid.uuid1().hex
        post.public = form.public.data
        post.content = form.content.data
        post.summary = form.content.data[:current_app.config['SUMMARY_COUNT']]
        post.update_ip = ip
        post.update_time = datetime.utcnow()
        post.language = request.accept_languages.best

        db.session.add(post)
        db.session.commit()

        if form.file.data:

            old_image = post.image
            old_video = post.video
            old_file_md5 = post.file_md5
            old_filename = post.filename
            post_id = str(post.id)

            filename = re.sub('[\\\\/:*?"<>|\s]', '-', form.file.data.filename)
            buffer = form.file.data.read()

            ext = filename.split('.')

            md5_obj = hashlib.md5()
            md5_obj.update(buffer)
            file_md5 = md5_obj.hexdigest()

            if ext[-1].lower() in image_formats:

                if old_image:
                    try:
                        shutil.rmtree(os.path.join('app', 'static', 'image', post_id))
                    except:
                        pass
                if old_video:
                    try:
                        shutil.rmtree(os.path.join('app', 'static', 'video', post_id))
                    except:
                        pass
                post.image = None
                post.video = None
                db.session.add(post)
                db.session.commit()

                image = file_md5 + '.' + ext[-1].lower()
                os.mkdir('app/static/image/' + post_id)
                f = open(os.path.join('app', 'static', 'image', post_id, image), 'wb')
                f.write(buffer)
                f.close()

                post.image = image

            elif ext[-1].lower() in video_formats:

                if old_image:
                    try:
                        shutil.rmtree(os.path.join('app', 'static', 'image', post_id))
                    except:
                        pass
                if old_video:
                    try:
                        shutil.rmtree(os.path.join('app', 'static', 'video', post_id))
                    except:
                        pass
                post.image = None
                post.video = None
                db.session.add(post)
                db.session.commit()

                video = file_md5 + '.' + ext[-1].lower()
                os.mkdir('app/static/video/' + post_id)
                f = open(os.path.join('app', 'static', 'video', post_id, video), 'wb')
                f.write(buffer)
                f.close()

                post.video = video

            else:

                if old_filename:
                    try:
                        shutil.rmtree(os.path.join('app', 'static', 'attachment', post_id, old_file_md5))
                    except:
                        pass

                try:
                    os.makedirs('app/static/attachment/' + post_id + '/' + file_md5)
                except:
                    pass
                f = open(os.path.join('app', 'static', 'attachment', post_id, file_md5, filename), 'wb')
                f.write(buffer)
                f.close()

                file_size = convert_size(len(buffer))

                post.file_md5 = file_md5
                post.filename = filename
                post.file_size = file_size

            db.session.add(post)
            db.session.commit()

        return redirect(url_for('.post', postid=postid, order='newest'))

    form.public.default = post.public
    form.process()
    form.content.data = post.content

    return render_template('edit_post.html', title=APP_TITLE, form=form, post=post)


@main.route('/delete/<int:postid>')
@login_required
def delete(postid):

    post = Post.query.filter_by(id=postid).first_or_404()

    if post.user_id != current_user.id:
        flash(_('You can not delete this post.'))
        return redirect(url_for('.post', postid=postid, order='newest'))

    db.session.query(Post).filter(Post.id == postid).delete()
    db.session.commit()

    post_tags = PostTag.query.join(PostTagRelationship, PostTagRelationship.post_tag_id == PostTag.id).filter(
        PostTagRelationship.post_id == postid).all()
    for post_tag in post_tags:
        post_tag_relationship = PostTagRelationship.query.filter(PostTagRelationship.post_id == postid, PostTagRelationship.post_tag_id == post_tag.id).first()
        db.session.delete(post_tag_relationship)
        post_tag.count -= 1
        db.session.add(post_tag)
    db.session.commit()

    comments = Comment.query.filter(Comment.post_id == postid).all()
    for comment in comments:
        db.session.query(Comment).filter(Comment.id == comment.id).delete()        
    db.session.commit()

    flash(_('The post has been deleted.'))
    return redirect(url_for('.index'))


@main.route('/post/<int:postid>/<order>')
def post(postid, order):

    post = Post.query.filter_by(id=postid).first_or_404()

    if order not in ['newest', 'oldest']:
        order = 'newest'

    if not current_user.is_authenticated:

        if post.public == 0:
            flash(_('You can not access, or page not found.'))
            return redirect(url_for('.index'))

        post.views_count += 1
        db.session.add(post)
        db.session.commit()

        post_tags = PostTag.query.join(PostTagRelationship, PostTagRelationship.post_tag_id == PostTag.id).filter(
            PostTagRelationship.post_id == postid).all()

        if order == 'newest':

            comments = Comment.query.filter(Comment.post_id == postid, Comment.approved == 1) \
                .order_by(Comment.create_time.desc()).all()

        elif order == 'oldest':

            comments = Comment.query.filter(Comment.post_id == postid, Comment.approved == 1) \
                .order_by(Comment.create_time.asc()).all()

        return render_template('post.html', title=APP_TITLE, post=post, comments=comments, order=order, post_tags=post_tags)

    else:

        post.views_count += 1
        db.session.add(post)
        db.session.commit()

        post_tags = PostTag.query.join(PostTagRelationship, PostTagRelationship.post_tag_id == PostTag.id).filter(
            PostTagRelationship.post_id == postid).all()

        if order == 'newest':

            comments = Comment.query.filter(Comment.post_id == postid).order_by(Comment.create_time.desc()).all()

        elif order == 'oldest':

            comments = Comment.query.filter(Comment.post_id == postid).order_by(Comment.create_time.asc()).all()

        return render_template('post.html', title=APP_TITLE, post=post, comments=comments, order=order, post_tags=post_tags)


@main.route('/comment/<int:postid>', methods=['GET', 'POST'])
def comment(postid):

    post = Post.query.filter_by(id=postid).first_or_404()
    ip = request.environ.get('HTTP_X_REAL_IP') or request.remote_addr

    if not current_user.is_authenticated:

        if post.public == 0:
            flash(_('You can not access, or page not found.'))
            return redirect(url_for('.index'))

        if Comment.query.filter(Comment.ip == ip, Comment.create_time > datetime.utcnow() - timedelta(minutes=10)).count() > 10:
            flash(_('Are you a robot? please take a rest...'))
            return redirect(url_for('.post', postid=postid, order='newest'))

    form = CommentForm()
    replied_id = request.args.get('replied_id')

    if replied_id:
        Comment.query.filter(Comment.id == replied_id, Comment.post_id == postid).first_or_404()

    if form.validate_on_submit():

        comment = Comment(post_id=postid,
                    replied_id=replied_id,
                    content=form.content.data,
                    language=request.accept_languages.best,
                    ip=ip)
        db.session.add(comment)
        db.session.commit()

        post.comments_count += 1
        db.session.add(post)
        db.session.commit()

        user = User.query.filter_by(id=1).first()
        user.new_comment = datetime.utcnow()
        db.session.add(user)
        db.session.commit()

        flash(_('Thanks! your comment will be published after approval.'))

        return redirect(url_for('.post', postid=postid, order='newest', _anchor='tab'))

    return render_template('comment.html', title=APP_TITLE, form=form, post=post, replied_id=replied_id)


@main.route('/like', methods=['GET', 'POST'])
@csrf.exempt
def like():

    postid = request.form.get('postid')
    post = Post.query.filter_by(id=postid).first_or_404()
    ip = request.environ.get('HTTP_X_REAL_IP') or request.remote_addr

    result = Like.query.filter(Like.ip == ip, Like.post_id == postid).first()

    if result is not None:
        callback = post.likes_count
        return Response(str(callback))
    else:
        result = Like(ip=ip,
                      post_id=postid)
        db.session.add(result)

        post.likes_count += 1
        callback = post.likes_count
        db.session.add(post)
        db.session.commit()
        return Response(str(callback))


@main.route('/tag/<path:tag>/<order>')
def tag(tag, order):

    post_tag = PostTag.query.filter_by(content=tag).first()
    page = request.args.get('page', 1, type=int)

    if not post_tag or post_tag.count == 0:
        flash(_('No posts is tagged with %(tag)s.', tag=tag))
        return redirect(url_for('.index'))

    if order == 'time':

        if not current_user.is_authenticated:
            pagination = Post.query.join(PostTagRelationship, PostTagRelationship.post_id==Post.id) \
                .filter(Post.public == 1, PostTagRelationship.post_tag_id==post_tag.id) \
                .order_by(Post.create_time.desc()) \
                .paginate(page, per_page=current_app.config['LISTS_PER_PAGE'], error_out=False)
        else:
            pagination = Post.query.join(PostTagRelationship, PostTagRelationship.post_id == Post.id) \
                .filter(PostTagRelationship.post_tag_id == post_tag.id) \
                .order_by(Post.create_time.desc()) \
                .paginate(page, per_page=current_app.config['LISTS_PER_PAGE'], error_out=False)

        posts = pagination.items

        if not posts and  pagination.has_prev:
                return redirect(url_for('.tag', tag=tag, order=order, page=page - 1))

        return render_template('tag.html', title=APP_TITLE, page=page, pagination=pagination, posts=posts, tag=tag, order=order)

    elif order == 'likes_count':

        if not current_user.is_authenticated:
            pagination = Post.query.join(PostTagRelationship, PostTagRelationship.post_id == Post.id) \
                .filter(Post.public == 1, PostTagRelationship.post_tag_id == post_tag.id) \
                .order_by(Post.likes_count.desc()) \
                .paginate(page, per_page=current_app.config['LISTS_PER_PAGE'], error_out=False)
        else:
            pagination = Post.query.join(PostTagRelationship, PostTagRelationship.post_id == Post.id) \
                .filter(PostTagRelationship.post_tag_id == post_tag.id) \
                .order_by(Post.likes_count.desc()) \
                .paginate(page, per_page=current_app.config['LISTS_PER_PAGE'], error_out=False)

        posts = pagination.items

        if not posts and  pagination.has_prev:
                return redirect(url_for('.tag', tag=tag, order=order, page=page - 1))

        return render_template('tag.html', title=APP_TITLE, page=page, pagination=pagination, posts=posts, tag=tag, order=order)

    else:
        return render_template('404.html')


@main.route('/add_post_tag/<int:postid>', methods=['GET', 'POST'])
@login_required
def add_post_tag(postid):
    
    post = Post.query.filter_by(id=postid).first_or_404()

    if request.method == 'POST':

        text = request.form['tags']
        tags = ' '.join(text.split())
        tags = tags.split(' ')[0:5]

        if re.search(r'[<>\\?*!]', text):
            flash(_('Can not add these special characters: < > \ ? * !'))
            return redirect(url_for('.post', postid=postid, order='newest'))

        if tags != ['']:
            
            tag_list = []
            
            for tag in tags:
                
                tag = tag.strip('#')
                tag = tag[:32]
                post_tag = PostTag.query.filter_by(content=tag).first()

                if post_tag:
                    
                    status = PostTagRelationship.query.filter(PostTagRelationship.post_id==postid,
                                                              PostTagRelationship.post_tag_id==post_tag.id).first()
                    if status:
                        tag_list.append(tag)
                    else:
                        post_tag_relationship = PostTagRelationship(post_id=postid, post_tag_id=post_tag.id)
                        post_tag.count += 1
                        db.session.add(post_tag)
                        db.session.add(post_tag_relationship)
                        db.session.commit()
                        tag_list.append(tag)
                        
                else:
                    
                    post_tag = PostTag(content=tag)
                    db.session.add(post_tag)
                    db.session.commit()
                    
                    post_tag_relationship = PostTagRelationship(post_id=postid, post_tag_id=post_tag.id)
                    post_tag.count += 1
                    db.session.add(post_tag)
                    db.session.add(post_tag_relationship)
                    db.session.commit()

                    tag_list.append(tag)

            flash(_('You have added %(number)d tags: %(tags)s', number=len(tag_list), tags=', '.join(tag_list)))

            return redirect(url_for('.post', postid=postid, order='newest'))

        else:
            flash(_('Can not add a blank tag.'))
            return redirect(url_for('.post', postid=postid, order='newest'))


@main.route('/remove_tag/<int:postid>')
@login_required
def remove_tag(postid):

    tag = request.args.get('tag')
    order = request.args.get('order')
    post_tag = PostTag.query.filter_by(content=tag).first_or_404()
    page = request.args.get('page', 1, type=int)
    post_tag_relationship = PostTagRelationship.query.filter(PostTagRelationship.post_tag_id==post_tag.id, PostTagRelationship.post_id==postid).first_or_404()

    post_tag.count -= 1
    db.session.add(post_tag)
    db.session.delete(post_tag_relationship)
    db.session.commit()

    flash(_('You have removed tag: %(tag)s', tag=tag))

    return redirect(url_for('.tag', tag=tag, order=order, page=page))


@main.route('/remove_tags/<int:postid>')
@login_required
def remove_tags(postid):

    tag = request.args.get('tag')
    order = request.args.get('order')
    page = request.args.get('page', 1, type=int)
    post_tag_relationships = PostTagRelationship.query.filter(PostTagRelationship.post_id==postid).all()

    tag_list = []
    for post_tag_relationship in post_tag_relationships:

        post_tag = PostTag.query.filter(PostTag.id==post_tag_relationship.post_tag_id).first()

        post_tag.count -= 1
        db.session.add(post_tag)
        db.session.delete(post_tag_relationship)
        db.session.commit()

        tag_list.append(post_tag.content)

    flash(_('You have removed %(number)d tags: %(tags)s', number=len(tag_list), tags=', '.join(tag_list)))

    if tag:
        return redirect(url_for('.tag', tag=tag, order=order, page=page))
    else:
        return redirect(url_for('.post', postid=postid, order='newest'))


@main.route('/show_full/<int:postid>')
def show_full(postid):
    return redirect(url_for('.post', postid=postid, order='newest'))


@main.route('/search', methods=['POST', 'GET'])
def search():
    
    form = SearchForm()
    page = request.args.get('page', 1, type=int)
    keyword = request.args.get('keyword')

    if keyword:

        if form.validate_on_submit():

            page = 1
            keyword = request.form.get('keyword')

            if keyword[0] == '#':
                tag = keyword.strip('#')
                return redirect(url_for('.tag', tag=tag, order='time'))

            else:

                form.keyword.data = keyword
                fuzzy_keyword = '%' + keyword + '%'

                if not current_user.is_authenticated:
                    pagination = Post.query.filter(Post.public == 1, Post.content.like(fuzzy_keyword)) \
                        .order_by(Post.create_time.desc()).paginate(page, per_page=current_app.config['LISTS_PER_PAGE'],
                                                                    error_out=False)
                else:
                    pagination = Post.query.filter(Post.content.like(fuzzy_keyword)) \
                        .order_by(Post.create_time.desc()).paginate(page, per_page=current_app.config['LISTS_PER_PAGE'],
                                                                    error_out=False)
                posts = pagination.items

                return render_template('search.html', title=APP_TITLE, posts=posts, pagination=pagination, form=form, keyword=keyword)

        else:

            if keyword[0] == '#':
                tag = keyword.strip('#')
                return redirect(url_for('.tag', tag=tag, order='time'))

            else:

                form.keyword.data = keyword
                fuzzy_keyword = '%' + keyword + '%'

                if not current_user.is_authenticated:
                    pagination = Post.query.filter(Post.public == 1, Post.content.like(fuzzy_keyword)) \
                        .order_by(Post.create_time.desc()).paginate(page, per_page=current_app.config['LISTS_PER_PAGE'],
                                                                    error_out=False)
                else:
                    pagination = Post.query.filter(Post.content.like(fuzzy_keyword)) \
                        .order_by(Post.create_time.desc()).paginate(page, per_page=current_app.config['LISTS_PER_PAGE'],
                                                                    error_out=False)
                posts = pagination.items

                return render_template('search.html', title=APP_TITLE, posts=posts, pagination=pagination, form=form, keyword=keyword)

    else:

        form = SearchForm()
        if form.validate_on_submit():
            keyword = form.keyword.data
            return redirect(url_for('.search', keyword=keyword))
        return render_template('search.html', title=APP_TITLE, form=form, keyword=form.keyword.data)


@main.route('/about')
def about():

    username = request.args.get('username')
    if username:
        user = User.query.filter_by(user_name=username).first_or_404()
    else:
        user = User.query.filter_by(id=1).first()
    user_profile = UserProfile.query.filter_by(user_id=user.id).first()
    return render_template('about.html', title=APP_TITLE, user=user, user_profile=user_profile)


@main.route('/choose_language', methods=['GET', 'POST'])
def choose_language():

    form = LanguageForm()

    if not current_user.is_authenticated:
        if form.validate_on_submit():
            session['language'] = form.language.data
            return redirect(url_for('main.menu'))
    else:
        user = User.query.filter_by(id=current_user.id).first()
        if form.validate_on_submit():
            user.language = form.language.data
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('main.menu'))

    return render_template('choose_language.html', title=APP_TITLE, form=form)


@main.route('/login_log')
@login_required
def login_log():

    login_logs = LoginLog.query.filter(LoginLog.user_id == current_user.id, LoginLog.status == 1).order_by(LoginLog.timestamp.desc()).all()[:20]

    return render_template('login_log.html', title=APP_TITLE, login_logs=login_logs)


@main.route('/account')
@login_required
def account():

    latest_log = LoginLog.query.filter(LoginLog.user_id == current_user.id, LoginLog.status == 1).order_by(LoginLog.timestamp.desc()).first()

    user_profile = UserProfile.query.filter_by(user_id=current_user.id).first()

    if user_profile:
        photo = user_profile.photo
        gender = user_profile.gender
        birthday = user_profile.birthday
        introduction = user_profile.introduction
    else:
        photo = ''
        gender = ''
        birthday = ''
        introduction = ''

    return render_template('account.html', title=APP_TITLE, login_ip = latest_log.ip, photo=photo, gender=gender, birthday=birthday,
                           introduction=introduction)


@main.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():

    user_profile = UserProfile.query.filter_by(user_id=current_user.id).first()

    form = ProfileForm()

    if form.validate_on_submit():

        if user_profile:
            image = user_profile.photo
        else:
            image = ''

        if form.photo.data:

            filename = re.sub('[\\\\/:*?"<>|\s]', '-', form.photo.data.filename)
            buffer = form.photo.data.read()
            ext = filename.split('.')

            if ext[-1].lower() not in image_formats:
                flash(_('Image format: jpg/jpeg、png、gif、bmp、tif、webp'))
                return redirect(url_for('.edit_profile'))

            uuid3 = uuid.uuid3(uuid.NAMESPACE_DNS, str(current_user.id)).hex
            path = 'photo'
            image = uuid3 + '.' + ext[-1].lower()
            f = open(os.path.join('app', 'static', 'image', path, image), 'wb')
            f.write(buffer)
            f.close()

        db.session.query(UserProfile).filter(UserProfile.user_id == current_user.id).delete()

        user_profile = UserProfile(user_id=current_user.id,
                                   photo=image,
                                   gender=form.gender.data,
                                   birthday=form.birthday.data,
                                   introduction=form.introduction.data)
        db.session.add(user_profile)
        db.session.commit()

        flash(_('The profile has been updated.'))
        return redirect(url_for('.account'))

    if user_profile:
        form.photo = user_profile.photo
        form.gender.data = user_profile.gender
        form.birthday.data = user_profile.birthday
        form.introduction.data = user_profile.introduction

    return render_template('edit_profile.html', title=APP_TITLE, form=form)


@main.route('/change_username', methods=['GET', 'POST'])
@login_required
def change_username():

    form = UserNameForm()
    user = User.query.filter_by(id=current_user.id).first()

    if form.validate_on_submit():

        user.user_name = form.username.data
        db.session.add(user)
        db.session.commit()

        posts = Post.query.filter(Post.user_id == user.id).all()
        for post in posts:
            post.user_name = form.username.data
            db.session.add(post)
        db.session.commit()

        flash(_('Username changes have been saved.'))
        return redirect(url_for('.account'))

    return render_template('change_username.html', title=APP_TITLE, form=form)


@main.route('/export', methods=['GET', 'POST'])
@login_required
def export():

    form = ExportForm()

    if form.validate_on_submit():

        user_id = current_user.id
        export_format = form.export.data
        export_path = str(uuid.uuid4().hex)

        current_user.last_export = datetime.utcnow()
        current_user.export_path = export_path
        db.session.add(current_user)
        db.session.commit()

        zip_file = current_user.user_name + '-' + str(current_user.last_export.strftime('%Y-%m-%d')) + '.zip'
        user_name = current_user.user_name

        try:
            os.mkdir('app/static/cache')
        except:
            pass
        export_zipfile(user_id, user_name, export_path, export_format, zip_file)

        return redirect(url_for('.export'))

    if current_user.last_export:
        download_url = os.path.join('static/cache/', current_user.export_path + '/' + current_user.user_name + '-' + str(current_user.last_export.strftime('%Y-%m-%d')) + '.zip')
    else:
        download_url = '#'

    ten_minutes = datetime.utcnow() - timedelta(minutes=10)

    return render_template('export.html', title=APP_TITLE, form=form, download_url=download_url, ten_minutes=ten_minutes)


@main.route('/photos', methods=['GET', 'POST'])
def photos():

    ip = request.environ.get('HTTP_X_REAL_IP') or request.remote_addr
    page = request.args.get('page', 1, type=int)

    if not current_user.is_authenticated:

        pagination = Photo.query.filter(Photo.public == 1).order_by(
            Photo.timestamp.desc()) \
            .paginate(page, per_page=current_app.config['LISTS_PER_PAGE'], error_out=False)

        photos = pagination.items

        return render_template('photos.html', title=APP_TITLE, page=page, pagination=pagination, photos=photos)

    else:

        form = PhotoForm()

        if form.validate_on_submit():

            if form.file.data:

                filename = re.sub('[\\\\/:*?"<>|\s]', '-', form.file.data.filename)
                buffer = form.file.data.read()

                ext = filename.split('.')

                md5_obj = hashlib.md5()
                md5_obj.update(buffer)
                file_md5 = md5_obj.hexdigest()

                if ext[-1].lower() in image_formats:

                    path = datetime.utcnow().strftime('%Y/%m/%d')
                    image = file_md5 + '.' + ext[-1].lower()
                    try:
                        os.makedirs('app/static/image/' + path)
                    except:
                        pass
                    f = open(os.path.join('app', 'static', 'image', path, image), 'wb')
                    f.write(buffer)
                    f.close()

                    upload = Photo(user_id=current_user.id,
                                 ip=ip,
                                 path=path,
                                 image=image,
                                 title=form.title.data or filename,
                                 public=form.public.data)
                    db.session.add(upload)
                    db.session.commit()

                return redirect(url_for('.photos'))

        pagination = Photo.query.order_by(Photo.timestamp.desc()) \
            .paginate(page, per_page=current_app.config['LISTS_PER_PAGE'], error_out=False)

        photos = pagination.items

        return render_template('photos.html', title=APP_TITLE, form=form, page=page, pagination=pagination, photos=photos)


@main.route('/edit_image/<int:image_id>', methods=['GET', 'POST'])
@login_required
def edit_image(image_id):

    photo = Photo.query.filter_by(id=image_id).first_or_404()
    page = request.args.get('page', 1, type=int)
    ip = request.environ.get('HTTP_X_REAL_IP') or request.remote_addr

    form = EditImageForm()

    if form.validate_on_submit():

        photo.title = form.title.data
        photo.public = form.public.data
        photo.ip = ip
        photo.timestamp = datetime.utcnow()
        db.session.add(photo)
        db.session.commit()

        return redirect(url_for('.photos', page=page))

    form.public.default = photo.public
    form.process()
    form.title.data = photo.title

    return render_template('edit_image.html', title=APP_TITLE, form=form, page=page)


@main.route('/delete_image/<int:image_id>')
@login_required
def delete_image(image_id):

    photo = Photo.query.filter_by(id=image_id).first_or_404()
    page = request.args.get('page', 1, type=int)

    if photo.user_id != current_user.id:
        return redirect(url_for('.photos'))

    count = Photo.query.filter(Photo.path == photo.path, Photo.image == photo.image).count()

    if count > 1:
        db.session.delete(photo)
        db.session.commit()
    else:
        db.session.delete(photo)
        db.session.commit()

        try:
            os.remove(os.path.join('app', 'static', 'image', photo.path, photo.image))
        except:
            pass

    return redirect(url_for('.photos', page=page))


@main.route('/menu')
def menu():
    return render_template('menu.html', title=APP_TITLE)

@main.app_errorhandler(403)
def forbidden(e):
    return render_template('403.html'), 403

@main.app_errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@main.app_errorhandler(500)
def internal_serve_error(e):
    db.session.rollback()
    return render_template('500.html'), 500

@main.app_errorhandler(CSRFError)
def handle_csrf_error(e):
    return render_template('csrf_error.html', reason=e.description), 400

@main.route('/manifest.json')
def manifest():
    return send_from_directory('static', 'manifest.json')

@main.route('/sw.js')
def service_worker():
    response = make_response(send_from_directory('static', 'sw.js'))
    response.headers['Cache-Control'] = 'no-cache'
    return response

@main.route('/ip')
def ip():
    ip = request.environ.get('HTTP_X_REAL_IP') or request.remote_addr
    return render_template('ip.html', ip=ip)

@main.route('/language')
def language():

    language = g.language
    if current_user.is_authenticated:
        user_language = current_user.language
    else:
        user_language = None
    best = request.accept_languages.best

    return render_template('language.html', language=language, user_language=user_language,  best=best)

