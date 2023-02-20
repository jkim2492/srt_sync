from gevent.pywsgi import WSGIServer
from geventwebsocket import WebSocketError
from geventwebsocket.handler import WebSocketHandler
from bottle import request, Bottle, abort
import inspect
import subprocess
import json
import os
import sys
from collections.abc import Container

app = Bottle()
ws = None
module = None
arrayHead = chr(30)
sep = chr(31)


@app.route('/websocket')
def handle_websocket():
    global ws
    ws = request.environ.get('wsgi.websocket')
    if not ws:
        abort(400, 'Expected WebSocket request.')
    while True:
        try:
            msg = ws.receive()
            if msg is None:
                sys.exit()
            if msg.startswith(sep):
                splitmsg = msg.split(sep)
                functionName = splitmsg[1]
                args = splitmsg[2:]
                callpyfunction(functionName, args)
        except WebSocketError:
            break


def pack(args):
    if len(args) == 0:
        return ""
    ret = ""
    for arg in args:
        ret += sep
        if isinstance(arg, Container):
            ret = ret + arrayHead + json.dumps(arg)
        else:
            ret = ret + arg

    return ret


def unpack(argstr):
    arglist = argstr.split(sep)
    for arg in arglist:
        if arg[0] == arrayHead:
            arg = json.loads(arg)
    return arglist


def start_server(path, *args, port=8080):
    global module
    frm = inspect.stack()[1]
    module = inspect.getmodule(frm[0])
    server = WSGIServer(("localhost", port),
                        app,
                        handler_class=WebSocketHandler)
    path = resource_path(path)
    args = list(args)
    args.insert(0, path)
    subprocess.Popen(args)
    server.serve_forever()


def callpyfunction(functionName, args=[]):
    f = getattr(module, functionName)
    f(*args)


def run(jsName, *args):
    ws.send(f"{sep}{jsName}{pack(args)}")


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS',
                        os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)
