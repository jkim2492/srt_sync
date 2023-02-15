var port = 8080
var sep = String.fromCharCode(31)
var arrsep = String.fromCharCode(30)

function calljsfunction(functionName, args) {
    args = parseArgs(args)
    window[functionName](...args);
}

function waitSocket(socket, callback) {
    setTimeout(
        function () {
            if (socket.readyState === 1) {
                // console.log("Connection is made")
                if (callback != null) {
                    callback();
                }
            } else {
                // console.log("wait for connection...")
                waitSocket(socket, callback);
            }
        }, 5); // wait 5 milisecond for the connection...
}

function run(functionName, args = []) {
    waitSocket(ws, function () {
        let argstr = ""
        if (args.length > 0) {
            argstr = sep + args.join(sep)
        }
        ws.send(`${sep}${functionName}${argstr}`);
    });
}

function parseArgs(args) {
    for (i = 0; i < args.length; i++) {
        if (args[i][0] == arrsep) {
            args[i] = JSON.parse(args[i].substring(1))
            // console.log(args[i])
        }
    }
    return args
}

var ws = new WebSocket(`ws://localhost:${port}/websocket`);
// waitSocket(ws, function () {
//     console.log("Done")
// });
ws.onmessage = function (evt) {
    // console.log("Message: " + evt.data);
    msg = String(evt.data);
    if (msg.startsWith(sep)) {
        splitmsg = msg.split(sep)
        functionName = splitmsg[1]
        args = splitmsg.slice(2)
        // console.log(args.length)
        calljsfunction(functionName, args)
    }
};


