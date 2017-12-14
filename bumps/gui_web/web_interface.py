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

def do_load():
    filename = request.form["filename"]
    load_model(filename)
    return "done"
    
app.add_url_rule("/load_model", "/load_model", do_load, methods=["POST"])

@app.errorhandler(Exception)
def handle_error(e):
    code = 500
    if isinstance(e, HTTPException):
        code = e.code
    content = {'exception': repr(e), 'traceback': traceback.format_exc()}
    logging.info(content['traceback'])
    return make_response(msgpack_converter.dumps(content), code)

@app.route("/")
def hello():
    return "Hello World!"


# Allow "python -m bumps.gui.gui_app options..."
if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)    
    port = 8002
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    app.run(port=port)

