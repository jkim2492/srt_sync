#!/usr/bin/python3
from prettytable import PrettyTable
import sys, SyncSubs, time
from SyncSubs import *

srcp = sys.argv[1]
refp = sys.argv[2]
outp = sys.argv[3]

srcfile = pysrt.open(srcp)
src = read(srcfile)
ref = read(pysrt.open(refp))
step = max(int(len(src) / 35), 15)
inc, window = 100, 90


def format_offsets(srcf, data):
    def timestring(t):
        a = str(t.hours).rjust(2, "0") + ":"
        b = str(t.minutes).rjust(2, "0") + ":"
        c = str(t.seconds).rjust(2, "0") + "."
        d = str(t.milliseconds).ljust(3, "0")
        return a + b + c + d

    t = PrettyTable(['From ', 'To', "Offset (ms)"])
    for x in data:
        y = [timestring(srcf[x[0]].start), timestring(srcf[x[1]].end), x[2]]
        t.add_row(y)
    return t


for i in range(3, len(sys.argv)):

    if sys.argv[i].startswith("--inc="):
        inc = int(sys.argv[i].split("--inc=")[-1])
    if sys.argv[i].startswith("--size="):
        step = int(sys.argv[i].split("--size=")[-1])
    if sys.argv[i].startswith("--minimum="):
        SyncSubs.SMALLEST = int(sys.argv[i].split("--minimum=")[-1])
    if sys.argv[i].startswith("--window="):
        window = int(sys.argv[i].split("--window=")[-1])

print(f"Syncing {srcp} to {refp}")
start_time = time.time()
offsets = all_offsets(src, ref, inc=inc, window=window, step=step)
offsets = offsets.astype(int)
print(format_offsets(srcfile, offsets))
for offset in offsets:
    srcfile[offset[0]:offset[1]].shift(milliseconds=offset[2])
srcfile.save(outp, encoding='utf-8')
print(f"Time elapsed: {time.time() - start_time} seconds")
