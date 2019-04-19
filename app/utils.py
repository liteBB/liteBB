# -*- coding: utf-8 -*-

import os
import math


image_formats = ['jpg', 'png', 'jpeg', 'gif', 'bmp', 'tif', 'tiff', 'webp']
video_formats = ['webm', 'ogg', 'mp4']


def create_folder(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        os.chmod(folder_path, os.O_RDWR)


def convert_size(size_bytes):
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return "%s %s" % (s, size_name[i])





