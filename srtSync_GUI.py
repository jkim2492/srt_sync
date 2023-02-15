import tkinter
import efd
import sys
from tkinter import filedialog as fd
from srtSync import *


srclist = []
reflist = []
status = []
outdir = "Default"
log = ""
buttons = ["srcb", "refb", "procb", "outb"]


def parselist():
    global srclist
    global reflist
    global status

    arr = [srclist, reflist, status]
    arr = copy(arr)
    lens = [len(a) for a in arr]
    l = max(lens)
    for a in arr:
        while len(a) < l:
            a.append("")
    t = np.column_stack(arr).tolist()
    efd.run("updateTable", t)


def addline(x):
    global log
    log = log + x + "\n"
    efd.run("updateContent", "cons", log)


def greyall():
    for x in buttons:
        efd.run("grey", x)


def ungreyall():
    for x in buttons:
        efd.run("ungrey", x)


def process():
    global status
    status = ["Waiting..."] * len(srclist)
    parselist()
    greyall()
    for i in range(len(srclist)):
        processInd(i)
    ungreyall()


def processInd(i):
    global status
    addline(
        f"Syncing {os.path.basename(srclist[i])} to {os.path.basename(reflist[i])}")
    start_time = time.time()
    src, srcf = read(srclist[i])
    ref, _ = read(reflist[i])
    offsets = all_offsets(src, ref, inc=100, window=90, step=5)
    addline(format_offsets(src, offsets).get_string())
    src = shift_offsets(src, offsets)
    filepath, filename = os.path.split(srclist[i])
    if outdir == "Default":
        dest = os.path.join(filepath, "synced")
        makedir(dest)
    else:
        dest = outdir
    savepath = pathjoin(dest, filename)
    write(savepath, src, srcf)
    end_time = time.time()
    addline(f"Saved to {savepath}")
    addline("Time elapsed: {:.3f} seconds".format(end_time - start_time))
    addline("\n")
    status[i] = "Done"
    parselist()


def getFile():
    root = tkinter.Tk()
    root.attributes('-topmost', True)  # Display the dialog in the foreground.
    root.iconify()  # Hide the little window.
    files = list(fd.askopenfilenames(parent=root, filetypes=[
        ("SRT Files", "*.srt")]))
    root.destroy()
    tkinter.Tk().withdraw()
    return files


def getFolder():
    root = tkinter.Tk()
    root.attributes('-topmost', True)  # Display the dialog in the foreground.
    root.iconify()  # Hide the little window.
    folder = fd.askdirectory()
    root.destroy()
    tkinter.Tk().withdraw()
    return folder


def getsrc():
    global srclist
    srclist = getFile()
    if len(srclist) != len(reflist):
        efd.run("grey", "procb")
    else:
        efd.run("ungrey", "procb")
    parselist()
    efd.run("updateValue", "srci", ";".join(srclist))
    # return parselist()


def getref():
    global reflist
    reflist = getFile()
    if len(srclist) != len(reflist):
        efd.run("grey", "procb")
    else:
        efd.run("ungrey", "procb")
    parselist()
    efd.run("updateValue", "refi", "; ".join(reflist))


def getdir():
    global outdir
    outdir = getFolder()
    efd.run("updateValue", "outi", outdir)


def end():
    sys.exit()


path = R"web/neutralino-win_x64.exe"
web = efd.resource_path("web")
efd.start_server(path,f"--path={web}")
