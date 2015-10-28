import os

"""
All app configurations are set here and
the configuration used by the app can easily be updated
by switching an enviornmental variable since everything
inherits from DefaultConfig
"""


class DefaultConfig(object):
    PROJECT = 'Super Wicked File Sharing Service'
    DEBUG = False
    TESTING = False
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    CSRF_ENABLED = True
    UPLOAD_FOLDER = '/tmp/files'
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    BROKER_URL = 'redis://localhost:6380/0'
    CELERY_BROKER_URL = 'redis://localhost:6380/0',
    CELERY_RESULT_BACKEND = 'redis://localhost:6380/0'


class ProductionConfig(DefaultConfig):
    DEBUG = False


class StagingConfig(DefaultConfig):
    DEVELOPMENT = True
    DEBUG = True


class DevelopmentConfig(DefaultConfig):
    DEVELOPMENT = True
    DEBUG = True


class TestingConfig(DefaultConfig):
    TESTING = True

print(os.environ['DATABASE_URL'])
