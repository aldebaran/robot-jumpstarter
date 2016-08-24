"""
A test runner for a NAOqi service (to test the service packaged in the app)

Edit it to set your robot's IP to run it (or use arv etc.)

So far it's pretty hard-coded
"""

__version__ = "0.0.1"

__copyright__ = "Copyright 2015, Aldebaran Robotics"
__author__ = 'ekroeger'
__email__ = 'ekroeger@aldebaran.com'


import subprocess
import time
import sys
import traceback

import qi

#########################################
# Helper base class
#########################################

class ServiceTester:
    _app = None
    _testresults = []

    @classmethod
    def configure(cls, robot):
        sys.argv.extend(["--qi-url", robot])
        cls.robot = robot
        cls._app = qi.Application()
        cls._app.start()

    @classmethod
    def recap(cls):
        succeeded = 0
        failed = []
        for name, result in cls._testresults:
            if result:
                succeeded += 1
            else:
                failed.append(name)
        print "================================================"
        print "Successes: {0}/{1}".format(succeeded, len(cls._testresults))
        if failed:
            print "Failed tests:", ", ".join(failed)
        else:
            print "All OK :)"

    def service(self, service_name):
        return self._app.session.service(service_name)

    def __init__(self):
        self.name = self.__class__.__name__
        self.start()

    def start(self):
        command = ["/usr/bin/python", self.script, "--qi-url", self.robot]
        self.popen = subprocess.Popen(command, stdout=subprocess.PIPE,
                                      stderr=subprocess.STDOUT)
        self.running = True
        #print "Spawned", self.script, "with ID", self.popen.pid
        #print

    def finish_and_dump(self, verbose=True):
        if self.running:
            self.running = False
            self.popen.terminate()
            if verbose:
                print
                print "Killed. Output:"
                lines_iterator = iter(self.popen.stdout.readline, b"")
                for line in lines_iterator:
                    print ">", line.strip("\n") # yield line
                print

    def run_wrapped(self):
        succeeded = False
        try:
            print
            print "--------------------"
            print "starting", self.name
            succeeded = self.run()
            print "finished", self.name
        except Exception as e:
            print "error in", self.name
            print traceback.format_exc() 
        finally:
            self.finish_and_dump(verbose=(not succeeded))
            self._testresults.append((self.name, succeeded))

#########################################
# Specific test classes
#########################################

class SetGetTest(ServiceTester):
    script = "app/scripts/myservice.py"
    def run(self):
        time.sleep(1)
        
        ALMyService = self.service("ALMyService")
        ALMyService.set(0)
        assert ALMyService.get() == 0
        ALMyService.set(2)
        assert ALMyService.get() == 2
        return True
        
 
class ResetTest(ServiceTester):
    script = "app/scripts/myservice.py"
    def run(self):
        time.sleep(1)
        
        ALMyService = self.service("ALMyService")
        ALMyService.reset()
        assert ALMyService.get() == 0
        return True
        
 
class StopTest(ServiceTester):
    script = "app/scripts/myservice.py"
    def run(self):
        time.sleep(1)
        
        ALMyService = self.service("ALMyService")
        goterror = False
        try:
            ALMyService.stop()
            time.sleep(1)
            ALMyService.set(1)
        except RuntimeError:
            print "Got error after exit, as expected"
            goterror = True
        assert goterror, "Expected an exception after exit!"
        return True

def run_tests(robotname, *testclasses):
    ServiceTester.configure(robotname)
    for cls in testclasses:
        cls().run_wrapped()
    ServiceTester.recap()
    

def test_all(robotname):
    run_tests(robotname,
              SetGetTest,
              ResetTest,
              StopTest,
              )

if __name__ == "__main__":
    ROBOTNAME = "yourrobot.local" # Adapt this depending of your robot
    ROBOTNAME = "citadelle.local"
    test_all(ROBOTNAME)
