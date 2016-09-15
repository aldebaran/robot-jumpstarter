"""
stk.services.py

Syntactic sugar for accessing NAOqi services.
"""

__version__ = "0.1.2"

__copyright__ = "Copyright 2015, Aldebaran Robotics"
__author__ = 'ekroeger'
__email__ = 'ekroeger@aldebaran.com'


class ServiceCache(object):
    "A helper for accessing NAOqi services."

    def __init__(self, session=None):
        self.session = None
        self.services = {}
        if session:
            self.init(session)

    def init(self, session):
        "Sets the session object, if it wasn't passed to constructor."
        self.session = session

    def __getattr__(self, servicename):
        "We overload this so (instance).ALMotion returns the service, or None."
        if (not servicename in self.services) or (
                servicename == "ALTabletService"):
            # ugly hack: never cache ALtabletService, always ask for a new one
            if servicename.startswith("__"):
                # Behave like a normal python object for those
                raise AttributeError
            try:
                self.services[servicename] = self.session.service(servicename)
            except RuntimeError:  # Cannot find service
                self.services[servicename] = None
        return self.services[servicename]
