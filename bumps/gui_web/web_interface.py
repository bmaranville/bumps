"""
Bumps web interface.

The functions in this module are used by the bumps command to implement
the command line interface.  Bumps plugin models can use them to create
stand alone applications with a similar interface.  For example, the
Refl1D application uses the following::

    from . import fitplugin
    import bumps.gui_web.web_interface as wi
    wi.set_mplconfig(appdatadir='Refl1D')
    wi.install_plugin(fitplugin)
    wi.main()

After completing a set of fits on related systems, a post-analysis script
can use :func:`load_model` to load the problem definition and
:func:`load_best` to load the best value  found in the fit.  This can
be used for example in experiment design, where you look at the expected
parameter uncertainty when fitting simulated data from a range of experimental
systems.
"""
import os, sys, posixpath
import traceback
import logging

from flask import Flask, request, make_response
from werkzeug.exceptions import HTTPException
import msgpack as msgpack_converter

from bumps import plugin
from bumps import cli
from bumps import options as bumps_options

from .. import plugin
from ..cli import load_model

RPC_ENDPOINT = '/RPC2'

app = Flask(__name__)

app.add_url_rule("/load_model", "/load_model", load_model, methods=["POST"])


# Allow "python -m bumps.gui.gui_app options..."
if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    #import http.server
    #import socketserver
    #Handler = http.server.SimpleHTTPRequestHandler
    #httpd = socketserver.TCPServer(("", PORT), Handler)
    #print("serving at port", PORT)
    #httpd.serve_forever()
    
    port = 8002
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    app.run(port=port)

