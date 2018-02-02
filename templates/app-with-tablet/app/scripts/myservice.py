
"""
A sample showing how to make a Python script as an app.
"""

__version__ = "0.0.8"

__copyright__ = "Copyright 2015, Aldebaran Robotics"
__author__ = 'YOURNAME'
__email__ = 'YOUREMAIL@aldebaran.com'

import json
import time

import stk.runner
import stk.events
import stk.services
import stk.logging

KEY_TABLETSETATE = "app-with-tablet/TabletState"

class ALMyService(object):
    "A sample standalone app, that demonstrates simple Python usage"
    APP_ID = "com.aldebaran.dx-team-presentation"
    def __init__(self, qiapp):
        self.qiapp = qiapp
        self.events = stk.events.EventHelper(qiapp.session)
        self.s = stk.services.ServiceCache(qiapp.session)
        self.logger = stk.logging.get_logger(qiapp.session, self.APP_ID)

    def show(self, command):
        self.events.set(KEY_TABLETSETATE, json.dumps(command))

    def on_start(self):
        "Ask to be touched, waits, and exits."
        self.show({"title": "intro"})
        self.s.ALTextToSpeech.say("This is the first page")
        time.sleep(1.0)
        self.show({"title": "other"})
        self.s.ALTextToSpeech.say("This is another page")
        time.sleep(1.0)
        self.show({"title": "last"})
        self.s.ALTextToSpeech.say("This is the last page, I'm done")
        self.stop()

    def stop(self):
        "Standard way of stopping the application."
        self.qiapp.stop()

    def on_stop(self):
        "Cleanup"
        self.show({})
        self.logger.info("Application finished.")
        self.events.clear()

if __name__ == "__main__":
    stk.runner.run_service(ALMyService)
