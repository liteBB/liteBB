# liteBB


liteBB is a lite Blog & Board on mobile.


* Mobile first
* lite and Powerful
* Share text, image, video and file
* Markdown & real-time preview
* Comment / Reply to comment
* i18n Support
* PWA standalone App (Android and iOS13)


# Quickstart

Clone or download liteBB, only 2 steps to start with Python 3:

    pip3 install -r requirements.txt
    python3 manage.py runserver

Visit http://127.0.0.1:5000/ ( the default User/Password is `admin/admin` )


# Install in one minute

The code has been tested on Ubuntu 14/16/18 and Debian 8/9:

    ubuntu@vm-ubuntu:~$ sudo apt update
    ubuntu@vm-ubuntu:~$ sudo apt install git
    ubuntu@vm-ubuntu:~$ sudo git clone https://github.com/litebb/litebb
    ubuntu@vm-ubuntu:~$ cd litebb
    ubuntu@vm-ubuntu:~/litebb$ sudo apt install python3-pip
    ubuntu@vm-ubuntu:~/litebb$ sudo pip3 install -r requirements.txt
    ubuntu@vm-ubuntu:~/litebb$ sudo /usr/local/bin/gunicorn -D -w 4 -b 0.0.0.0:80 wsgi:application

liteBB is running on your server now!

*Prerequisites: only Python 3 is required on other Linux distributions.*

***

Suggestions for liteBB deployment:

1. Create a virtualenv
2. Install MySQL for liteBB (default is SQLite)
2. Run liteBB with Gunicorn, or Gunicorn and Nginx
4. Use Supervisor or Systemd to start Gunicorn on boot
5. Enforce HTTPS (PWA required)

# Screenshots

![](app/static/screenshots.jpg)

# License

liteBB is licensed under the [CC-BY-SA 4.0](http://creativecommons.org/licenses/by-sa/4.0/), the attribution requires the following foot-note:

    Powered by <a href="https://litebb.com">liteBB</a>


# Links

* [liteBB](https://litebb.com)
