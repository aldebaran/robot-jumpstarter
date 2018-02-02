"""
stk.logging.py

Utility library for logging with qi.
"""

__version__ = "0.1.2"

__copyright__ = "Copyright 2015, Aldebaran Robotics"
__author__ = 'ekroeger'
__email__ = 'ekroeger@aldebaran.com'

import functools
import traceback

import qi


def get_logger(session, app_id):
    """Returns a qi logger object."""
    logger = qi.logging.Logger(app_id)
    try:
        qicore = qi.module("qicore")
        log_manager = session.service("LogManager")
        provider = qicore.createObject("LogProvider", log_manager)
        log_manager.addProvider(provider)
    except RuntimeError:
        # no qicore, we're not running on a robot, it doesn't matter
        pass
    except AttributeError:
        # old version of NAOqi - logging will probably not work.
        pass
    return logger


def log_exceptions(func):
    """Catches all exceptions in decorated method, and prints them.

    Attached function must be on an object with a "logger" member.
    """
    @functools.wraps(func)
    def wrapped(self, *args):
        try:
            return func(self, *args)
        except Exception as exc:
            self.logger.error(traceback.format_exc())
            raise exc
    return wrapped


def log_exceptions_and_return(default_value):
    """If an exception occurs, print it and return default_value.

    Attached function must be on an object with a "logger" member.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapped(self, *args):
            try:
                return func(self, *args)
            except Exception:
                self.logger.error(traceback.format_exc())
                return default_value
        return wrapped
    return decorator
