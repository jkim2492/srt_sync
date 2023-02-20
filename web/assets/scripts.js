var current = "main"

function srcFiles() {
    run("getsrc", []);
}

function refFiles() {
    run("getref", []);
}

function outDir() {
    run("getdir", []);
}

function clearTable() {
    let headerCount = 1;
    let table = document.getElementById('fileTable');
    let rowCount = table.rows.length;
    for (var i = headerCount; i < rowCount; i++) {
        table.deleteRow(headerCount);
    }
}

function addRow(quad) {
    table = document.getElementById("fileTable");
    // let rowCount = table.rows.length;
    let row = table.insertRow(-1);
    for (x of quad) {
        cell = row.insertCell(-1);
        cell.appendChild(document.createTextNode(x));
    }
}


function updateTable(arr) {
    clearTable();
    arr.forEach(function (value, i) {
        addRow([i + 1, value[0], value[1], value[2]]);
    });
}


function grey(x) {
    document.getElementById(x).disabled = true;
}


function ungrey(x) {
    document.getElementById(x).disabled = false;
}


function updateContent(id, x) {
    document.getElementById(id).textContent = x;
}


function updateValue(id, x) {
    document.getElementById(id).value = x;
}

function updateParam() {
    i = document.getElementById("inci").value
    w = document.getElementById("wini").value
    s = document.getElementById("stpi").value
    run("updateParam", [i, w, s]);
}

async function process() {
    run("process", []);
}

function changePage(currentPage) {
    let page = document.getElementById(current)
    page.style.display = "none"
    document.getElementById(currentPage).style.display = "block"
    let banner = document.getElementById(currentPage + 'b')
    banner.setAttribute("class", "nav-item active")
    document.getElementById(current + 'b').setAttribute("class", "nav-item")
    current = currentPage
}

window.addEventListener("contextmenu", e => e.preventDefault());
