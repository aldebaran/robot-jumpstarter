
Clarifying the "service" terminology
=======

There are two different entities that are called "services":

* **NAOqi services** (also called "modules"), that expose an API and are registered to the ServiceDirectory. You can call them with qicli, subscribe to their signals, etc.

* **systemd services**, that are standalone executables packaged in an Application Package, declared in it's manifest with a `<service>` tag. These are managed by ALServiceManager, who can start and stop them (they will have their own process). For clarity's sake, these are called "**Executables**" in this doc.

The confusion between the two is increased by the fact that a common pattern is to write an executable whose sole purpose is to run a NAOqi service, and sometimes to identify both with the same name (e.g. both are called “ALFuchsiaBallTracker”).

Ways of using them in an app:

 * Run a standalone executable during your app, possibly as the only content. This is demonstrated in the `pythonapp` template.

 * Run a NAOqi service during your app (packaged in an executable), but only while the app is running -> this is how `service-tabletpage` is built.

 * Package a NAOqi service running all the time -> this wastes resources, and risks causing hard-to-find bugs, so should only be used for system apps that *really* need to do so.


qi.Application
=======


robot_runner**`.init()`** returns a QiApplication object, the same you would get by calling `qi.Application()̀`.

When your python script is packaged in an application, it should be declared in the manifest with a --qi-url parameter:

`<services>`
`  <service execStart="/usr/bin/python2 scripts/main.py ` **` --qi-url [URL]`**`" autorun="false" name="main"/>`
` </services>`

However, you can also execute that script directly, locally on your computer (python main.py), or from your favourite editor.
