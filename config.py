import os
class Config(object):
    FLASK_DEBUG = True
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'secret-string'