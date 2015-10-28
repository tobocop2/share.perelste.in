"""
Instantiate all extensions used by the application here
"""
from flask.ext.sqlalchemy import SQLAlchemy
db = SQLAlchemy()

from flask_migrate import Migrate
migrate = Migrate()

from flask.ext.cache import Cache
cache = Cache(config={'CACHE_TYPE': 'redis',
                      'CACHE_KEY_PREFIX': 'abort_cache',
                      'CACHE_REDIS_URL': 'redis://localhost:6379',
                      'CACHE_REDIS_PORT': '6379',
                      'CACHE_REDIS_HOST': 'localhost'})

from flask.ext.celery import Celery
celery = Celery()
