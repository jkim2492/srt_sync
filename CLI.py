#!/usr/bin/python3
import srtSync, time, argparse
from srtSync import *

parser = argparse.ArgumentParser()
parser.add_argument("src", type=str, help="Unsynced subtitle path")
parser.add_argument("ref", type=str, help="Reference subtitle path")
parser.add_argument("out", type=str, help="Output subtitle path")
parser.add_argument(
    "--incr", default=srtSync.INCR, type=int, help="increment in value in ms to use during sync"
)
parser.add_argument(
    "--step", default=srtSync.STEP, type=int, help="output file for the moshed video"
)
parser.add_argument("--rad1", default=srtSync.RAD1, type=int, help="search radius")
args = parser.parse_args().__dict__

srcp = args["src"]
refp = args["ref"]
outp = args["out"]

src, srctext = read(srcp)
ref, _ = read(refp)
srtSync.INCR = args["incr"]
srtSync.STEP = args["step"]
srtSync.RAD1 = args["rad1"]

print(f"Syncing {srcp} to {refp}")
start_time = time.time()
offsets = all_offsets(src, ref)
offsets = offsets.astype(int)
print(format_offsets(src, offsets))
for offset in offsets:
    src[offset[0] : offset[1]] = shift(src[offset[0] : offset[1]], offset[2])
write(outp, src, srctext)
print(f"Time elapsed: {time.time() - start_time} seconds")
