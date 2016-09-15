"""
stk.events.py

Provides misc. wrappers for ALMemory and Signals (using the same syntax for
handling both).
"""

__version__ = "0.1.1"

__copyright__ = "Copyright 2015, Aldebaran Robotics"
__author__ = 'ekroeger'
__email__ = 'ekroeger@aldebaran.com'

import qi


def on(*keys):
    """Decorator for connecting a callback to one or several events.

    Usage:

    class O:
        @on("MyMemoryKey")
        def my_callback(self,value):
            print "I was called!", value

    o = O()
    events = EventsHelper()
    events.connect_decorators(o)

    After that, whenever MyMemoryKey is raised, o.my_callback will be called
    with the value.
    """
    def decorator(func):
        func.__event_keys__ = keys
        return func
    return decorator


class EventHelper(object):
    "Helper for ALMemory; takes care of event connections so you don't have to"

    def __init__(self, session=None):
        self.session = None
        self.almemory = None
        if session:
            self.init(session)
        self.handlers = {}  # a handler is (subscriber, connections)
        self.subscriber_names = {}
        self.wait_value = None
        self.wait_promise = None

    def init(self, session):
        "Sets the NAOqi session, if it wasn't passed to the constructor"
        self.session = session
        self.almemory = session.service("ALMemory")

    def connect_decorators(self, obj):
        "Connects all decorated methods of target object."
        for membername in dir(obj):
            member = getattr(obj, membername)
            if hasattr(member, "__event_keys__"):
                for event in member.__event_keys__:
                    self.connect(event, member)

    def connect(self, event, callback):
        """Connects an ALMemory event or signal to a callback.

        Note that some events trigger side effects in services when someone
        subscribes to them (such as WordRecognized). Those will *not* be
        triggered by this function, for those, use .subscribe().
        """
        if event not in self.handlers:
            if "." in event:
                # if we have more than one ".":
                service_name, signal_name = event.split(".")
                service = self.session.service(service_name)
                self.handlers[event] = (getattr(service, signal_name), [])
            else:
                # It's a "normal" ALMemory event.
                self.handlers[event] = (
                    self.almemory.subscriber(event).signal, [])
        signal, connections = self.handlers[event]
        connection_id = signal.connect(callback)
        connections.append(connection_id)
        return connection_id

    def subscribe(self, event, attachedname, callback):
        """Subscribes to an ALMemory event so as to notify providers.

        This is necessary for things like WordRecognized."""
        connection_id = self.connect(event, callback)
        dummyname = "on_" + event.replace("/", "")
        self.almemory.subscribeToEvent(event, attachedname, dummyname)
        self.subscriber_names[event] = attachedname
        return connection_id

    def disconnect(self, event, connection_id=None):
        "Disconnects a connection, or all if no connection is specified."
        if event in self.handlers:
            signal, connections = self.handlers[event]
            if connection_id:
                if connection_id in connections:
                    signal.disconnect(connection_id)
                    connections.remove(connection_id)
            else:
                # Didn't specify a connection ID: remove all
                for connection_id in connections:
                    signal.disconnect(connection_id)
                del connections[:]
            if event in self.subscriber_names:
                name = self.subscriber_names[event]
                self.almemory.unsubscribeToEvent(event, name)
                del self.subscriber_names[event]

    def clear(self):
        "Disconnect all connections"
        for event in list(self.handlers):
            self.disconnect(event)

    def get(self, key):
        "Gets ALMemory value."
        return self.almemory.getData(key)

    def get_int(self, key):
        "Gets ALMemory value, cast as int."
        try:
            return int(self.get(key))
        except RuntimeError:
            # Key doesn't exist
            return 0
        except ValueError:
            # Key exists, but can't be parsed to int
            return 0

    def set(self, key, value):
        "Sets value of ALMemory key."
        return self.almemory.raiseEvent(key, value)

    def remove(self, key):
        "Remove key from ALMemory."
        try:
            self.almemory.removeData(key)
        except RuntimeError:
            pass

    def _on_wait_event(self, value):
        "Internal - callback for an event."
        if self.wait_promise:
            self.wait_promise.setValue(value)
            self.wait_promise = None

    def _on_wait_signal(self, *args):
        "Internal - callback for a signal."
        if self.wait_promise:
            self.wait_promise.setValue(args)
            self.wait_promise = None

    def cancel_wait(self):
        "Cancel the current wait (raises an exception in the waiting thread)"
        if self.wait_promise:
            self.wait_promise.setCanceled()
            self.wait_promise = None

    def wait_for(self, event, subscribe=False):
        """Block until a certain event is raised, and returns it's value.

        If you pass subscribe=True, ALMemory.subscribeToEvent will be called
        (sometimes necessary for side effects, i.e. WordRecognized).

        This will block a thread so you should avoid doing this too often!
        """
        if self.wait_promise:
            # there was already a wait in progress, cancel it!
            self.wait_promise.setCanceled()
        self.wait_promise = qi.Promise()
        if subscribe:
            connection_id = self.subscribe(event, "EVENTHELPER",
                                           self._on_wait_event)
        elif "." in event:  # it's a signal
            connection_id = self.connect(event, self._on_wait_signal)
        else:
            connection_id = self.connect(event, self._on_wait_event)
        try:
            result = self.wait_promise.future().value()
        finally:
            self.disconnect(event, connection_id)
        return result
