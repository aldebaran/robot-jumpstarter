"""
stk.runner.py

A helper library for making simple standalone python scripts as apps.

Wraps some NAOqi and system stuff, you could do all this by directly using the
Python SDK, these helper functions just isolate some frequently used/hairy
bits so you don't have them mixed in your logic.
"""

__version__ = "0.1.3"

__copyright__ = "Copyright 2015, Aldebaran Robotics"
__author__ = 'ekroeger'
__email__ = 'ekroeger@aldebaran.com'

import sys
import qi
from distutils.version import LooseVersion

#
# Helpers for making sure we have a robot to connect to
#


def check_commandline_args(description):
    "Checks whether command-line parameters are enough"
    import argparse
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('--qi-url', help='connect to specific NAOqi instance')

    args = parser.parse_args()
    return args


def is_on_robot():
    "Returns whether this is being executed on an Aldebaran robot."
    import platform
    return "aldebaran" in platform.platform()


def get_debug_robot():
    "Returns IP address of debug robot, complaining if not found"
    try:
        import qiq.config
        qiqrobot = qiq.config.defaultHost()
        if qiqrobot:
            robot = raw_input(
                "connect to which robot? (default is {0}) ".format(qiqrobot))
            if robot:
                return robot
            else:
                return qiqrobot
        else:
            print "qiq found, but it has no default robot configured."
    except ImportError:
        # qiq not installed
        print "qiq not installed (you can use it to set a default robot)."
    return raw_input("connect to which robot? ")


def init(qi_url=None):
    "Returns a QiApplication object, possibly with interactive input."
    if qi_url:
        sys.argv.extend(["--qi-url", qi_url])
    else:
        args = check_commandline_args('Run the app.')
        if bool(args.qi_url):
            qi_url = args.qi_url
        elif not is_on_robot():
            print "no --qi-url parameter given; interactively getting debug robot."
            debug_robot = get_debug_robot()
            if debug_robot:
                sys.argv.extend(["--qi-url", debug_robot])
                qi_url = debug_robot
            else:
                raise RuntimeError("No robot, not running.")

    qiapp = None
    sys.argv[0] = str(sys.argv[0])

    # In versions bellow 2.3, look for --qi-url in the arguemnts and call accordingly the Application
    if qi_url and  LooseVersion(qi.__version__) < LooseVersion("2.3"):
        position = 0
        qiapp = qi.Application(url="tcp://"+qi_url+":9559")
    # In versions greater than 2.3 the ip can simply be passed through argv[0]
    else:
        # In some environments sys.argv[0] has unicode, which qi rejects
        qiapp = qi.Application()

    qiapp.start()
    return qiapp


# Main runner

def run_activity(activity_class, service_name=None):
    """Instantiate the given class, and runs it.

    The given class must take a qiapplication object as parameter, and may also
    have on_start and on_stop methods, that will be called before and after
    running it."""
    qiapp = init()
    activity = activity_class(qiapp)
    service_id = None

    try:
        # if it's a service, register it
        if service_name:
            # Note: this will fail if there is already a service. Unregistering
            # it would not be a good practice, because it's process would still
            # be running.
            service_id = qiapp.session.registerService(service_name, activity)

        if hasattr(activity, "on_start"):
            def handle_on_start_done(on_start_future):
                "Custom callback, for checking errors"
                if on_start_future.hasError():
                    try:
                        msg = "Error in on_start(), stopping application: %s" \
                            % on_start_future.error()
                        if hasattr(activity, "logger"):
                            activity.logger.error(msg)
                        else:
                            print msg
                    finally:
                        qiapp.stop()
            qi.async(activity.on_start).addCallback(handle_on_start_done)

        # Run the QiApplication, which runs until someone calls qiapp.stop()
        qiapp.run()

    finally:
        # Cleanup
        if hasattr(activity, "on_stop"):
            # We need a qi.async call so that if the class is single threaded,
            # it will wait for callbacks to be finished.
            qi.async(activity.on_stop).wait()
        if service_id:
            qiapp.session.unregisterService(service_id)


def run_service(service_class, service_name=None):
    """Instantiate the given class, and registers it as a NAOqi service.

    The given class must take a qiapplication object as parameter, and may also
    have on_start and on_stop methods, that will be called before and after
    running it.

    If the service_name parameter is not given, the classes' name will be used.
    """
    if not service_name:
        service_name = service_class.__name__
    run_activity(service_class, service_name)
