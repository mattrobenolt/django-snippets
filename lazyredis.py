"""Lazy initialization of a Redis connection within Django.

The same redis connection object is reused across your entire
Django application, and lazily connected when first accessed.

** Depends on REDIS being defined in settings.py:
    REDIS = {'HOST': '127.0.0.1', 'PORT': 6379}

Usage:
    
    from lazyredis import redis
    redis.get('my_key')
"""
from django.conf import settings
import redis as redis_

REDIS_CONFIG = getattr(settings, 'REDIS', None)
if not REDIS_CONFIG:
    REDIS_CONFIG = {'HOST': '127.0.0.1', 'PORT': 6379}

class LazyRedis(object):
    def __init__(self):
        self.__cache = None
    
    def __getattr__(self, key):
        if not self.__cache:
            self.__cache = redis_.Redis(host=REDIS_CONFIG['HOST'], port=REDIS_CONFIG['PORT'])
        return getattr(self.__cache, key)

redis = LazyRedis()