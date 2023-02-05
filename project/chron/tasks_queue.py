""" Celery """
from __future__ import absolute_import
import os
import time

from celery import Celery
from celery.schedules import crontab
from django.conf import settings
from django.core import management
from django.core.exceptions import ValidationError


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "chron.settings")

APP = Celery()

APP.conf.result_backend = APP.conf.broker_url = settings.CACHEOPS_REDIS


@APP.task
def debug_success(message, delay=0):
    """Return message"""
    print(message)
    time.sleep(delay)
    return message


@APP.task
def debug_failure(message, delay=0):
    """Return message"""
    print(message)
    time.sleep(delay)
    raise ValidationError("AAAA")


@APP.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    """
    Registers cached data commands to run once per day, 1 hr apart
    """

    for i, cmd in enumerate(
        ["fetch_actors", "fetch_battles", "fetch_cities", "fetch_treaties"]
    ):
        sender.add_periodic_task(
            crontab(hour=i, minute=0),
            call_command.s(cmd),
        )


@APP.task
def call_command(arg):
    """
    Runs management command by name
    """
    print(f"Running {arg}")
    management.call_command(arg)
