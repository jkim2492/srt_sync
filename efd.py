from gevent.pywsgi import WSGIServer
from geventwebsocket import WebSocketError
from geventwebsocket.handler import WebSocketHandler
from bottle import request, Bottle, abort
import inspect
import subprocess
import json
import os
import sys
import socket
import webview
from collections.abc import Container

app = Bottle()
ws = None
module = None
arrayHead = chr(30)
sep = chr(31)


@app.route("/websocket")
def handle_websocket():
    global ws
    ws = request.environ.get("wsgi.websocket")
    if not ws:
        abort(400, "Expected WebSocket request.")
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


def next_free_port():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    port = 8000
    max_port = 65535
    while port <= max_port:
        try:
            sock.bind(("", port))
            sock.close()
            return port
        except OSError:
            port += 1
    raise IOError("no free ports")


def replaceport(num):
    jspath = resource_path(R"web\assets\efd.js")
    with open(jspath, "r") as f:
        lines = f.readlines()
    lines[0] = f"var port = {num}\n"
    with open(jspath, "w") as f:
        f.writelines(lines)

def start_server():
    port = next_free_port()
    replaceport(port)
    server = WSGIServer(("localhost", port), app, handler_class=WebSocketHandler)
    server.serve_forever()

def start(url,width=1280,height=720):
    global module
    frm = inspect.stack()[1]
    module = inspect.getmodule(frm[0])
    window = webview.create_window('srtSync', url,width=width, height=height, resizable=False)
    webview.start (start_server,storage_path=resource_path("/"))
    

def callpyfunction(functionName, args=[]):
    f = getattr(module, functionName)
    f(*args)


def run(jsName, *args):
    ws.send(f"{sep}{jsName}{pack(args)}")

def build():
    scriptPath = "gui.py"
    assetPath = "web"
    iconPath = R"web\assets\favicon.ico"
    buildstr = f'pyinstaller {scriptPath} "--add-data={assetPath};{assetPath}" "--icon={iconPath}" --onefile --clean --noconsole'
    subprocess.run(buildstr)

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)



