""" Celery """
from __future__ import absolute_import
import os
import time
from django.core.exceptions import ValidationError

from django.conf import settings

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "chron.settings")

APP = Celery()

APP.conf.result_backend = APP.conf.broker_url = settings.CACHEOPS_REDIS

@APP.task
def debug_success(message, delay=0):
    """ Return message """
    print(message)
    time.sleep(delay)
    return message

@APP.task
def debug_failure(message, delay=0):
    """ Return message """
    print(message)
    time.sleep(delay)
    raise ValidationError("AAAA")
