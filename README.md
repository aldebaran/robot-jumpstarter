Author(s): <ekroeger@aldebaran.com>

Copyright (C) 2015 Aldebaran Robotics

Overview
========

Making and testing NAOqi apps can be a bit of a pain. In an ideal world:

* your essential logic should not be mixed up with cruft and boilerplate
* you should be able to test your code in a matter of seconds, without any unnecessary steps

**`skeleton-generator`** making it easier to start a new app or service from a template that takes care of these aspects. It contains:

* Application template folders
* A script for generating a new project from one of those

For example, calling 

`python generate.py pythonapp my-super-app`

... will create a new folder "my-super-app" containing a copy of the pythonapp template, with all necessary parts renamed.



Creating a project
========

Projects are created by calling

`python generate.py template-name app-name [service-name] (optional)`

A project with the given name will be created in the "output" folder.


Application templates
========

There are currently three basic templates:

* **pythonapp**, a standalone Python script
* **simple-tabletpage**, a simple webpage
* **service-tabletpage**, a Python service linked to a webpage

You can also create your own template just by putting it in the "templates" folder.

For more details:

Template: pythonapp
--------

*Usage:* `python generate.py pythonapp my-app-name`

An interactive application made as a simple standalone Python script.

All the logic is in **`app/scripts/main.py`**.

When the application is installed on the robot, running the behavior is equivalent to running main.py (the behavior will exit when main.py stops, and stopping the behavior will kill main.py).

But for development, you can also run it in standalone on your computer;  pass the robot's address as parameter (**`python main.py --qi-url [your robot's IP]`**), or don't pass an address and you will interactively be asked for one (if you use qiq, it will offer to use your qiq default robot). This allows quicker iterations.

If you build an application from this template, you should only have to change:

* main.py (which can include other Python files)
* the project Properties, in Choregraphe (icon, description, trigger condition, supported languages, etc.)

Note that this application doesn't register a service in NAOqi.


Template: simple-tabletpage
--------

*Usage:* `python generate.py simple-tabletpage my-app-name`

This demonstrates a simple way of having a webpage that uses NAOqi services by calling them with QiMessaging.js.

It also contains a behavior, who, when run on Pepper, will require that webpage to be displayed on her tablet.

This template can be a good starting point for either making a webpage that can be opened on the robot (for debug or configuration purposes, e.g. testing text to speech), or for making a simple tablet-driven animation.

To test the page without installing it on a robot, run `python serve.py` (in the app's root), and a new tab will be opened on your browser, in which you will be prompted to enter your robot's IP address, then given your app page as if it was installed on the robot (so you can use all your browser's debug facilities, and just reload the page when you edited your html/js/css).

Template: service-tabletpage
--------

*Usage:* `python generate.py service-tabletpage my-app-name ALMyServiceName`

Combines the above two above to have an application consisting of a (Python) NAOqi service, and a webpage that calls it (which is a common pattern in application development).

The service will be started when the application is launched, and stopped with a call to it's .exit() method (that can be done from the webpage).

This project also contains unit tests: run `python testrun.py` in the project root (this is experimental).


Utility libraries
========

Python
--------

See [the doc of Studio Libraries](doc/).


robotutils.js
--------

A utility library for qimessaging.js (used in simple-tabletpage and service-tabletpage).

Includes:

* Support for remote debugging (as described in simple-tabletpage above) by running pages from your local computer.
* Syntactic sugar:

Getting services:

    RobotUtils.onServices(function(ALLeds, ALTextToSpeech) {
      ALLeds.randomEyes(2.0);
      ALTextToSpeech.say("I can speak");
    });

Subscribing to ALMemory:

    RobotUtils.subscribeToALMemoryEvent("FrontTactilTouched", function(value) {
      alert("Head touched: " + value);
    });
