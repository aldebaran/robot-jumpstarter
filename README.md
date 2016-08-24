Author(s): <ekroeger@aldebaran.com>

Copyright (C) 2015-2016 SBRE


What is robot-jumpstarter?
========

**robot-jumpstarter** helps you make NAOqi Applications, for the robots NAO and Pepper.

It's inspired by [Yeoman](http://yeoman.io/), and aims to be as useful for making NAOqi apps.

It is aimed for making apps in **Python** and **Javascript**, as opposed to:

* **Choregraphe** - for those, see [the official documentation](http://doc.aldebaran.com/2-4/software/choregraphe/)
* **Android** - see [Pepper SDK for Android](https://android.aldebaran.com/doc/)

Why?
========

Making and testing NAOqi apps can be a bit of a pain. In an ideal world:

* your essential logic should not be mixed up with cruft and boilerplate
* you should be able to test your code in a matter of seconds, without any unnecessary steps

**`robot-jumpstarter`** makes it easy to start a new app or service from a template that takes care of these aspects. It contains:

* Application templates (folders)
* A script for generating a new project from a template

For example, calling 

`python jumpstart.py pythonapp my-super-app`

... will create a new project "my-super-app" containing a copy of the pythonapp template, with all necessary parts renamed.

Installation
========

`git clone ....`


Creating a project
========

Projects are created by calling

`python jumpstart.py template-name app-name [service-name] (optional)`

A project with the given name will be created in the "output" folder.


Application templates
========

There are currently three basic templates:

* **pythonapp**, a standalone Python script
* **python-service**, a NAOqi service in Python
* **simple-tabletpage**, a simple webpage
* **service-tabletpage**, a Python service linked to a webpage
* **dialog-service**, collaborative dialogue with a helper service

You can also create your own template just by putting it in the "templates" folder.

For more details:

Template: pythonapp
--------

*Usage:* `python jumpstart.py pythonapp my-app-name`

An interactive application made as a simple standalone Python script.

All the logic is in **`app/scripts/main.py`**.

When the application is installed on the robot, running the behavior is equivalent to running `main.py` (the behavior will exit when main.py stops, and stopping the behavior will kill main.py).

But for development, you can also run it in standalone on your computer;  pass the robot's address as parameter (**`python main.py --qi-url [your robot's IP]`**), or don't pass an address and you will interactively be asked for one. This allows quicker iterations.

If you build an application from this template, you should only have to change:

* `main.py` (which can include other Python files)
* the project Properties, in Choregraphe (icon, description, trigger condition, supported languages, etc.)

Note that this application doesn't register a service in NAOqi.

Template: python-service
--------

*Usage:* `python jumpstart.py python-service my-package-name MyServiceName`

A NAOqi service that will be running at all times on your robot. 

All the logic is in **`app/scripts/myservice.py`**. (it will be renamed by the generator script)

As long as the application is installed on the robot, the service is present and can be called from anywhere with `MyServiceName.get()` (or whatever others you want to define).

For development, as with the previous template, you can run it in standalone on your computer  (**`python main.py --qi-url [your robot's IP]`**), and you will still be able to call it as if it was running on the robot.

This project also contains unit tests: run `python testrun.py` in the project root (this is experimental).

Template: simple-tabletpage
--------

*Usage:* `python jumpstart.py simple-tabletpage my-package-name`

This demonstrates a simple way of having a webpage that uses NAOqi services by calling them with QiMessaging.js.

It also contains a behavior, who, when run on Pepper, will require that webpage to be displayed on her tablet.

This template can be a good starting point for either making a webpage that can be opened on the robot (for debug or configuration purposes, e.g. testing text to speech), or for making a simple tablet-driven animation.

To test the page without installing it on a robot, run `python serve.py` (in the app's root), and a new tab will be opened on your browser, in which you will be prompted to enter your robot's IP address, then given your app page as if it was installed on the robot (so you can use all your browser's debug facilities, and just reload the page when you edited your html/js/css).


Template: service-tabletpage
--------

*Usage:* `python jumpstart.py service-tabletpage my-package-name MyServiceName`

Combines **python-service** and **simple-tabletpage**  to have an application consisting of a (Python) NAOqi service, and a webpage that calls it (a common pattern in application development).


Template: dialog-service
--------

*Usage:* `python jumpstart.py service-tabletpage my-package-name MyServiceName`

Works like **python-service**, but with an extra collaborative dialogue file (a qichat file, that can be edited through choregraphe), to show how you can call the service from dialogue.

This is again a common pattern: Anything needing computations or complex actions can be done by the service (in Python), the dialogue provides the interface (as opposed to putting the logic in qichat too, which is less readable, harder to debug, and makes it harder to handle several languages).

See also
========

 * [The Official Python SDK documentation](http://doc.aldebaran.com/2-4/dev/python/).
 * The [Studio Toolkit libraries](https://github.com/pepperhacking/studiotoolkit/), used in these templates (stk, and robotutils.js)
 * [Notes on "Services"](/doc/services)
