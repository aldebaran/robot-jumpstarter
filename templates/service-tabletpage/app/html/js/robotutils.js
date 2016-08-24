/*
 * robotutils.js version 0.2
 * 
 * A utility library for naoqi; requires jQuery.
 * 
 * This library is a wrapper over qimessaging.js. Some advantages:
 *  - debugging and iterating are made easier by support for a
 *    ?robot=<my-robots-ip> query parameter in the URL, that allows
 *    you to open a local file and connect it to a remote robot.
 *  - there is some syntactic sugar over common calls that
 *    allows you to keep your logic simple without too much nesting
 *
 * You can of course directly use qimessaging.js instead.
 * 
 * See the method documentations below for sample usage.
 * 
 * Copyright Aldebaran Robotics
 * Authors: ekroeger@aldebaran.com, jjeannin@aldebaran.com
 */

RobotUtils = (function(self) {

    /*---------------------------------------------
     *   Public API
     */

    /* RobotUtils.onServices(servicesCallback, errorCallback) 
     * 
     * A function for using NAOqi services.
     * 
     * "servicesCallback" should be a function whose arguments are the
     * names of NAOqi services; the callback will be called
     * with those services as parameters (or the errorCallback
     * will be called with a reason).
     * 
     * Sample usage:
     *
     *   RobotUtils.onServices(function(ALLeds, ALTextToSpeech) {
     *     ALLeds.randomEyes(2.0);
     *     ALTextToSpeech.say("I can speak");
     *   });
     * 
     * This is actually syntactic sugar over RobotUtils.connect() and 
     * some basic QiSession functions, so that the code stays simple.
     */
    self.onServices = function(servicesCallback, errorCallback) {
        self.connect(function(session) {
            var wantedServices = getParamNames(servicesCallback);
            var pendingServices = wantedServices.length;
            var services = new Array(wantedServices.length);
            var i;
            for (i = 0; i < wantedServices.length; i++) {
                (function (i){
                    session.service(wantedServices[i]).then(function(service) {
                        services[i] = service;
                        pendingServices -= 1;
                        if (pendingServices == 0) {
                            servicesCallback.apply(undefined, services);
                        }
                    }, function() {
                        var reason = "Failed getting a NaoQi Module: " + wantedServices[i]
                        console.log(reason);
                        if (errorCallback) {
                            errorCallback(reason);
                        }
                    });
                })(i);
            }
        }, errorCallback);
    }
    
    // alias, so that the code looks natural when there is only one service.
    self.onService = self.onServices;

    /* RobotUtils.subscribeToALMemoryEvent(event, eventCallback, subscribeDoneCallback)
     *
     * connects a callback to an ALMemory event. Returns a MemoryEventSubscription.
     * 
     * This is just syntactic sugar over calls to the ALMemory service, which you can
     * do yourself if you want finer control.
     */
    self.subscribeToALMemoryEvent = function(event, eventCallback, subscribeDoneCallback) {
        var evt = new MemoryEventSubscription(event);
        self.onServices(function(ALMemory) {
            ALMemory.subscriber(event).then(function (sub) {
                evt.setSubscriber(sub)
                sub.signal.connect(eventCallback).then(function(id) {
                    evt.setId(id);
                    if (subscribeDoneCallback) subscribeDoneCallback(id)
                });
            },
            onALMemoryError);
        });
        return evt;
    }

    /* RobotUtils.connect(connectedCallback, failureCallback)
     * 
     * connectedCallback should take a single argument, a NAOqi session object
     * 
     * This function is mostly meant for intenral use, for your app you
     * should probably use the more specific RobotUtils.onServices or
     * RobotUtils.subscribeToALMemoryEvent.
     *
     * There can be several calls to .connect() in parallel, only one
     * session will be created.
     */
    self.connect = function(connectedCallback, failureCallback) {
        if (self.session) {
            // We already have a session, don't create a new one
            connectedCallback(self.session);
            return;
        }
        else if (pendingConnectionCallbacks.length > 0) {
            // A connection attempt is in progress, just add this callback to the queue
            pendingConnectionCallbacks.push(connectedCallback);
            return;
        }
        else {
            // Add self to the queue, but create a new connection.
            pendingConnectionCallbacks.push(connectedCallback);
        }
        
        var qimAddress = null;
        var robotlibs = '/libs/';
        if (self.robotIp) {
            // Special case: we're doing remote debugging on a robot.
            robotlibs = "http://" + self.robotIp + "/libs/";
            qimAddress = self.robotIp + ":80";
        }

        function onConnected(session) {
            self.session = session;
            var numCallbacks = pendingConnectionCallbacks.length;
            for (var i = 0; i < numCallbacks; i++) {
                pendingConnectionCallbacks[i](session);
            }
        }

        getScript(robotlibs + 'qimessaging/2/qimessaging.js', function() {
            QiSession(
                onConnected,
                failureCallback,
                qimAddress
            )
        }, function() {
            if (self.robotIp) {
                console.error("Failed to get qimessaging.js from robot: " + self.robotIp);
            } else {
                console.error("Failed to get qimessaging.js from this domain; host this app on a robot or add a ?robot=MY-ROBOT-IP to the URL.");
            }
            failureCallback();
        });
    }

    // public variables that can be useful.
    self.robotIp = _getRobotIp();
    self.session = null;

    /*---------------------------------------------
     *   Internal helper functions
     */
    
    // Repalement for jQuery's getScript function
    function getScript(source, successCallback, failureCallback) {
        var script = document.createElement('script');
        var prior = document.getElementsByTagName('script')[0];
        script.async = 1;
        prior.parentNode.insertBefore(script, prior);

        script.onload = script.onreadystatechange = function( _, isAbort ) {
            if(isAbort || !script.readyState || /loaded|complete/.test(script.readyState) ) {
                script.onload = script.onreadystatechange = null;
                script = undefined;

                if(isAbort) {
                    if (failureCallback) failureCallback();
                } else {
                    // Success!
                    if (successCallback) successCallback();
                }
            }
        };

        script.src = source;
    }     
    
    function _getRobotIp() {
        var regex = new RegExp("[\\?&]robot=([^&#]*)");
        var results = regex.exec(location.search);
        return results == null ? "" : decodeURIComponent(results[1].replace(/\+/g, " ").replace("/", ""));
    }

    // Helper for getting the parameters from a function.
    var STRIP_COMMENTS = /((\/\/.*$)|(\/\*[\s\S]*?\*\/))/mg;
    function getParamNames(func) {
        var fnStr = func.toString().replace(STRIP_COMMENTS, '');
        var result = fnStr.slice(fnStr.indexOf('(')+1, fnStr.indexOf(')')).match(/([^\s,]+)/g);
        if(result === null)
            result = [];
        return result;
    };

    // ALMemory helpers (event subscription requires a lot of boilerplate)

    function MemoryEventSubscription(event) {
        this._event = event;
        this._internalId = null;
        this._sub = null;
        this._unsubscribe = false;
    }

    MemoryEventSubscription.prototype.setId = function(id) {
        this._internalId = id;
        // as id can be receveid after unsubscribe call, defere
        if (this._unsubscribe) this.unsubscribe(this._unsubscribeCallback);
    }

    MemoryEventSubscription.prototype.setSubscriber = function(sub) {
        this._sub = sub;
        // as sub can be receveid after unsubscribe call, defere
        if (this._unsubscribe) this.unsubscribe(this._unsubscribeCallback);
    }

    MemoryEventSubscription.prototype.unsubscribe = function(unsubscribeDoneCallback)
    {
        if (this._internalId != null && this._sub != null) {
            evtSubscription = this;
            evtSubscription._sub.signal.disconnect(evtSubscription._internalId).then(function() {
                if (unsubscribeDoneCallback) unsubscribeDoneCallback();
            }).fail(onALMemoryError);
        }
        else
        {
            this._unsubscribe = true;
            this._unsubscribeCallback = unsubscribeDoneCallback;
        }
    }

    var onALMemoryError = function(errMsg) {
        console.log("ALMemory error: " + errMsg);
    }

    var pendingConnectionCallbacks = [];

    return self;

})(window.RobotUtils || {});
