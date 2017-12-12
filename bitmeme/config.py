import os


class BaseConfig(object):
    """Base configuration."""

    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY',
                           '!(*@(JKKJDLLJWUIHKJMmkjnksljaiudjlI13476JH')
    CSRF_ENABLED = True
    SEND_FILE_MAX_AGE_DEFAULT = 0
    MEDIA_ROOT = 'static/img/media'
    ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

    # Flask-Mail settings
    MAIL_USERNAME = os.getenv('MAIL_USERNAME', 'bitmemeregister@gmail.com')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER',
                                    '"BitMeme" <bitmemeregister@gmail.com>')
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', '465'))
    MAIL_USE_SSL = int(os.getenv('MAIL_USE_SSL', True))

    # Flask-User settings
    USER_APP_NAME = "BitMeme"
