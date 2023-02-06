#!/usr/bin/python3
from SyncSubs import *
import PySimpleGUI as sg
import os, time, threading, SyncSubs
from showinfm import show_in_file_manager

"""
    Basic use of the Table Element

    Copyright 2022 PySimpleGUI
"""

# ------ Event Loop ------
inc, window, step, SyncSubs.SMALLEST = 100, 90, "Default", 5
cwd = os.getcwd()


def parselist(a, b):
    a = copy(a)
    b = copy(b)
    tmp = []
    while len(a) > 0 and len(b) > 0:
        tmp.append([a.pop(0), b.pop(0)])
    while len(a) > 0:
        tmp.append([a.pop(0), ""])
    while len(b) > 0:
        tmp.append(["", b.pop(0)])
    return tmp


def timestring(t):
    a = str(t.hours).rjust(2, "0") + ":"
    b = str(t.minutes).rjust(2, "0") + ":"
    c = str(t.seconds).rjust(2, "0") + "."
    d = str(t.milliseconds).ljust(3, "0")
    return a + b + c + d


def process(wn):
    def prt(t):
        wn['-console-'].print(t)

    global step
    global cwd
    global overwrite
    if cwd == "":
        prt("Empty output path detected. Using current directory as output path with overwrite disabled.")
        overwrite = False
        cwd = os.getcwd()
        # f = os.path.dirname(srclist[0])
        # if not os.path.exists(f):
        #     os.makedirs(f + "\\out\\")
    for i in range(len(srclist)):
        prt(f"Syncing {os.path.basename(srclist[i])} to {os.path.basename(reflist[i])}")
        start_time = time.time()
        src, srctext = read(srclist[i])
        ref, _ = read(reflist[i])
        if type(step) != int:
            step = max(int(len(src) / 35), 15)
        offsets = all_offsets(src, ref, inc=inc, window=window, step=step)
        offsets = offsets.astype(int)
        prt(format_offsets(src, offsets))
        for offset in offsets:
            src[offset[0]:offset[1]] = shift(src[offset[0]:offset[1]], offset[2])
        outp = cwd + "\\" + os.path.basename(srclist[i])
        if os.path.isfile(outp) and not overwrite:
            outp = outp[:-4] + "_1" + outp[-4:]
        write(outp, src, srctext)
        end_time = time.time()
        prt("Time elapsed: {:.3f} seconds".format(end_time - start_time))
    prt("Done! Click 'Browse' to sync more or press 'Quit")


def options_window():
    layout2 = [[sg.Text("All entries should be integers")],
               [sg.Text("Piece size (lines): "), sg.Input(str(step), key="-step-", change_submits=True), sg.Text("Default: max{15,subtitle length//35}")],
               [sg.Text("Search window (seconds): "), sg.Input(str(window), key="-window-", change_submits=True), sg.Text("Default: 90")],
               [sg.Text("Increment (milliseconds): "), sg.Input(str(inc), key="-inc-", change_submits=True), sg.Text("Default: 100")],
               [sg.Text("Minimum piece size "), sg.Input(str(SyncSubs.SMALLEST), key="-sml-", change_submits=True), sg.Text("Default: 5")],
               [sg.Text("The script will divide the subtitle into pieces of %piece size% lines")],
               [sg.Text("then minimize error, checking after shifting +/- %increment% in the range of +/- %search window%")],
               [sg.Text("Increase minimum piece size if you are getting lots of short, off-sync segments")],
               [sg.Button("Apply")]
               ]
    display2 = sg.Window("Options", layout2, modal=True)

    while True:
        event2, values2 = display2.read()
        if event2 == "Exit" or event2 == sg.WIN_CLOSED:
            break
        if event2 == "Apply":
            display2.close()
            for v in values2.keys():
                if values2[v].isdigit():
                    values2[v] = int(values2[v])
                elif values2[v] != "Default" and values2[v] != "default":
                    values2[v] = ""
            return values2['-inc-'], values2['-window-'], values2['-step-'], values2['-sml-']

    display2.close()


# ------ Make the Table Data ------
# data = make_table(num_rows=0, num_cols=2)
headings = ['Unsynced', 'Reference']

# ------ Window Layout ------
layout = [[sg.Table(values=[["", ""]], headings=headings,
                    # max_col_width=900,
                    auto_size_columns=True,
                    # cols_justification=('left','center','right','c', 'l', 'bad'),       # Added on GitHub only as of June 2022
                    # display_row_numbers=True,
                    justification='left',
                    num_rows=20,
                    # alternating_row_color='lightblue',
                    key='-TABLE-',
                    # selected_row_colors='red on yellow',
                    enable_events=True,
                    expand_x=True,
                    expand_y=True,
                    vertical_scroll_only=False,
                    # enable_click_events=True,  # Comment out to not enable header and other clicks
                    )],
          [sg.Text("Unsynced Files: "), sg.Input(change_submits=True),
           sg.FilesBrowse(key="-UF-", file_types=(("SRT Files", "*.srt"),), tooltip="Files with incorrect sync")],
          [sg.Text("Reference Files: "), sg.Input(change_submits=True),
           sg.FilesBrowse(key="-RF-", file_types=(("SRT Files", "*.srt"),), tooltip="Files with correct sync")],
          [sg.Text("Output Directory: "), sg.Input(cwd, change_submits=True), sg.FolderBrowse(key="-OD-", tooltip="Where synced files will be saved"),
           sg.Button("Open", tooltip="Open the output folder in file browser")],
          [sg.Checkbox('Overwrite?', default=False, key="-OW-")],
          [sg.Button("Process"), sg.Button("Options"), sg.Button("Quit")],
          [sg.Multiline(size=(100, 20), key='-console-', font=('Courier New', 12))]
          ]

# ------ Create Window ------
display = sg.Window('Subtitle Sync', layout,
                    ttk_theme='default',
                    # font='Helvetica 25',
                    resizable=True,
                    finalize=True
                    )

while True:
    event, values = display.read()
    if event == sg.WIN_CLOSED or event == "Quit":
        break
    srclist = sorted(values['-UF-'].split(";"))
    reflist = sorted(values['-RF-'].split(";"))
    overwrite = values['-OW-']
    if values['-OD-'] != "":
        cwd = values['-OD-']
    if event == "Open":
        show_in_file_manager(cwd)
    display['-TABLE-'].update(values=parselist(srclist, reflist))
    if event == "Options":
        inc, window, step, SyncSubs.SMALLEST = options_window()
        print(inc, window, step, SyncSubs.SMALLEST)

    if event == "Process":
        if len(srclist) == len(reflist) and srclist[0] != "" and reflist[0] != "":
            threading.Thread(target=process, args=(display,), daemon=True).start()
        else:
            display['-console-'].print("Number of unsynced files and reference files must match!")

display.close()
