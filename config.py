import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you_will_never_guess'

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    RECAPTCHA_PUBLIC_KEY = '6Lf2-hEqAAAAAMYrAQi2sYe38TK9ZI6-kreK3cEw'
    RECAPTCHA_PRIVATE_KEY = '6Lf2-hEqAAAAAMH_H6upI7jkXpxposp2AWLt1KWs'

    RECAPTCHA_DATA_ATTRS = {'theme': 'dark'}



