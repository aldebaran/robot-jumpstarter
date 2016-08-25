"""
A helper script for testing your app's local html files, with no robot install.

Usage:
Run serve.py, a browser will open on a debug page, enter your robot's IP address
and your local pages will be served as if they were on the robot.

Using a server like this (as opposed to just file:// etc.) is only necessary
if you do ajax calls in your page.
"""

__version__ = "0.0.3"

__copyright__ = "Copyright 2015, Aldebaran Robotics"
__author__ = 'ekroeger'
__email__ = 'ekroeger@aldebaran.com'

import os
import threading
import webbrowser
import BaseHTTPServer
import SimpleHTTPServer
import urlparse 
import urllib

USE_SERVER = False

PORT = 8081

def open_browser():
    """Start a browser after waiting for half a second."""
    if USE_SERVER:
        def _open_browser():
            url = 'http://localhost:%s/debug/index.html' % PORT
            webbrowser.open(url)
        thread = threading.Timer(0.5, _open_browser)
        thread.start()
    else:
        indexpath = os.path.join(os.getcwd(), "debug/index.html")
        url = urlparse.urljoin('file:', urllib.pathname2url(indexpath))
        webbrowser.open(url)

def start_server():
    """Start the server."""
    if USE_SERVER:
        server_address = ("", PORT)
        handler_class = SimpleHTTPServer.SimpleHTTPRequestHandler
        handler_class.extensions_map['.png'] = 'image/png'
        server = BaseHTTPServer.HTTPServer(server_address, handler_class)
        server.serve_forever()

def run():
    open_browser() # Comment out this line if you don't want to open a browser
    start_server()

if __name__ == "__main__":
    run()

