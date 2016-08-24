<?xml version="1.0" encoding="UTF-8" ?>
<Package name="dialog-service" format_version="4">
    <Manifest src="manifest.xml" />
    <BehaviorDescriptions>
        <BehaviorDescription name="behavior" src="testrun" xar="behavior.xar" />
    </BehaviorDescriptions>
    <Dialogs>
        <Dialog name="dialog-service" src="dialog-service/dialog-service.dlg" />
    </Dialogs>
    <Resources>
        <File name="icon" src="icon.png" />
        <File name="myservice" src="scripts/myservice.py" />
        <File name="__init__" src="scripts/stk/__init__.py" />
        <File name="__init__" src="scripts/stk/__init__.pyc" />
        <File name="events" src="scripts/stk/events.py" />
        <File name="events" src="scripts/stk/events.pyc" />
        <File name="logging" src="scripts/stk/logging.py" />
        <File name="logging" src="scripts/stk/logging.pyc" />
        <File name="runner" src="scripts/stk/runner.py" />
        <File name="runner" src="scripts/stk/runner.pyc" />
        <File name="services" src="scripts/stk/services.py" />
        <File name="services" src="scripts/stk/services.pyc" />
    </Resources>
    <Topics>
        <Topic name="dialog-service_enu" src="dialog-service/dialog-service_enu.top" topicName="dialog-service" language="en_US" />
    </Topics>
    <IgnoredPaths>
        <Path src=".metadata" />
    </IgnoredPaths>
</Package>
