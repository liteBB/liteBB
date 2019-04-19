# -*- coding: utf-8 -*-

import os
import time
import re
import zipfile
import shutil
from threading import Thread
from flask import current_app
from .models import Post



def async_export_zipfile(app, user_id, user_name, export_path, export_format, zip_file):

    with app.app_context():

        os.mkdir('app/static/cache/' + export_path)

        posts = Post.query.filter(Post.user_id == user_id, Post.content_html.isnot(None)).order_by(Post.create_time.desc()).all()

        index_list = []
        for post in posts:

            post_title = post.content.split('\n').pop(0).lstrip('#').strip()
            post_title_safe = re.sub('[\\\\/:*?"<>|\s]', '-', post_title)

            index_list.append('<p><a href="' + post_title_safe[:72] + '-' + post.create_time.strftime('%Y-%m-%d-%H-%M') + '.html">' +
                              post_title.rstrip('\n').rstrip() + ' ' + post.create_time.strftime('%Y-%m-%d') +
                              '</a></p>\n')

            f = open(os.path.join('app', 'static', 'cache', export_path,
                                  post_title_safe[:72] + '-' + post.create_time.strftime('%Y-%m-%d-%H-%M') + '.' + export_format), 'w', encoding='utf-8')
            if export_format == 'md':
                f.write(post.content)
            elif export_format == 'html':
                f.write('<!DOCTYPE html>\n<html lang="en">\n<head>\n' +
                        '<meta charset="UTF-8">\n' +
                        '<meta name="viewport" content="width=device-width, initial-scale=1">\n' +
                        '<title>' + post_title.rstrip('\n').rstrip() + '</title>\n' +
                        '</head>\n<body>\n' +
                        '<h3>' + post_title.rstrip('\n').rstrip() + '</h3>\n' +
                        '<p><a href="index.html">' + '« Back' + '</a>&nbsp;&nbsp;|&nbsp;&nbsp;by&nbsp;' + post.user_name + '</p>' +
                        '<hr>' +
                        post.content_html + '\n' + '<br><br>' +
                        '\n</body>\n</html>')
            f.close()

        if export_format == 'html':
            f = open(os.path.join('app', 'static', 'cache', export_path, 'index.html'), 'w', encoding='utf-8')
            f.write('<!DOCTYPE html>\n<html lang="en">\n<head>\n' +
                    '<meta charset="UTF-8">\n' +
                    '<meta name="viewport" content="width=device-width, initial-scale=1">\n' +
                    '<title>' + user_name + '\'s Posts' + '</title>\n' +
                    '</head>\n<body>\n' +
                    '<h1>' + user_name + '\'s Posts' + '</h1>\n' +
                    '<p>by&nbsp;' + user_name + '</p>' +
                    '<hr>' +
                    ''.join(index_list) + '<br>' +
                    '\n</body>\n</html>')
            f.close()

        z = zipfile.ZipFile(os.path.join('app', 'static', 'cache', zip_file), 'w', zipfile.ZIP_DEFLATED)

        startdir = os.path.join('app', 'static', 'cache', export_path)

        for dirpath, dirnames, filenames in os.walk(startdir):
            for filename in filenames:
                z.write(os.path.join(dirpath, filename), arcname=filename)
        z.close()

        shutil.move(os.path.join('app', 'static', 'cache', zip_file), os.path.join('app', 'static', 'cache', export_path, zip_file))
        time.sleep(600)
        shutil.rmtree(os.path.join('app/static/cache', export_path))

def export_zipfile(user_id, user_name, export_path, export_format, zip_file):
    app = current_app._get_current_object()
    thr = Thread(target=async_export_zipfile, args=[app, user_id, user_name, export_path, export_format, zip_file])
    thr.start()
    return thr
