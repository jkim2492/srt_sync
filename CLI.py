#!/usr/bin/python3
import sys, srtSync, time
from srtSync import *

srcp = sys.argv[1]
refp = sys.argv[2]
outp = sys.argv[3]

src, srctext = read(srcp)
ref, _ = read(refp)
step = max(int(len(src) / 35), 15)
inc, window = 100, 90

for i in range(3, len(sys.argv)):

    if sys.argv[i].startswith("--inc="):
        inc = int(sys.argv[i].split("--inc=")[-1])
    if sys.argv[i].startswith("--size="):
        step = int(sys.argv[i].split("--size=")[-1])
    if sys.argv[i].startswith("--window="):
        window = int(sys.argv[i].split("--window=")[-1])

print(f"Syncing {srcp} to {refp}")
start_time = time.time()
offsets = all_offsets(src, ref, inc=inc, window=window, step=step)
offsets = offsets.astype(int)
print(format_offsets(src, offsets))
for offset in offsets:
    src[offset[0]:offset[1]] = shift(src[offset[0]:offset[1]], offset[2])
write(outp, src, srctext)
print(f"Time elapsed: {time.time() - start_time} seconds")
