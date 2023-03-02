#!/usr/bin/python3
import time
import numpy as np
from copy import deepcopy as copy
import re
import os
from prettytable import PrettyTable

tags = r"{\\an\d*}|&lt;.*?&gt;|<.*?>"
SMALLEST = 3
INCR = 100
RAD1 = 120
STEP = 5



def toMs(match):
    def ms_helper(quad):
        return (
            int(quad[0]) * 3600000
            + int(quad[1]) * 60000
            + int(quad[2]) * 1000
            + +int(quad[3])
        )

    return [ms_helper(match[:4]), ms_helper(match[4:])]


def format_offsets(src, data):
    t = PrettyTable(["From ", "To", "Offset (sec)"])
    for x in data:
        y = [toTs(src[x[0]][0]), toTs(src[x[1] - 1][1]), x[2] / 1000]
        t.add_row(y)
    return t


def makedir(name):
    if not os.path.exists(name):
        os.makedirs(name)


def shift_offsets(src, offsets):
    src = copy(src)
    for offset in offsets:
        src[offset[0] : offset[1]] = shift(src[offset[0] : offset[1]], offset[2])
    return src


def toTs(ms):
    hr = ms // 3600000
    ms = ms - hr * 3600000
    mn = ms // 60000
    ms = ms - mn * 60000
    sc = ms // 1000
    ms = ms - sc * 1000
    return (
        str(hr).rjust(2, "0")
        + ":"
        + str(mn).rjust(2, "0")
        + ":"
        + str(sc).rjust(2, "0")
        + ","
        + str(ms).ljust(3, "0")
    )


def read(filename):
    with open(filename, "r", encoding="utf-8") as f:
        x = f.read()
        if ord(x[0]) == 65279:
            x = x[1:]
        texts = re.split(
            r"\d*\n\d*?[:|\.|,]\d*?[:|\.|,]\d*?[:|\.|,]\d*? --> \d*?[:|\.|,]\d*?[:|\.|,]\d*?[:|\.|,]\d*",
            x,
        )
        texts = list(filter(None, texts))
        texts = [s.strip() for s in texts]
        matches = re.findall(
            r"(\d*?)[:|\.|,](\d*?)[:|\.|,](\d*?)[:|\.|,](\d*?) --> (\d*?)[:|\.|,](\d*?)[:|\.|,](\d*?)[:|\.|,](\d*)",
            x,
        )
        for i in range(len(matches)):
            matches[i] = toMs(matches[i])
        return np.array(matches), texts


def write(filename, times, texts):
    with open(filename, "w", encoding="utf-8") as f:
        row = 0
        for i in range(len(times)):
            if times[i][0] >= 0:
                f.write(f"{row}\n")
                f.write(f"{toTs(times[i][0])} --> {toTs(times[i][1])}\n")
                f.write(texts[i] + "\n\n")
                row += 1


def safepath(filepath):
    if os.path.exists(filepath):
        name, ext = path_ext(filepath)
        filepath = os.path.join(name + "_1" + ext)
    return filepath


def path_ext(filepath):
    return os.path.splitext(filepath)


def shift(sub, milliseconds):
    tmp = copy(sub)
    tmp = tmp + milliseconds
    return tmp


def mindex(arr):
    ind = np.argmin(arr)
    return arr[ind], ind


def time_offset(sub1, sub2, RAD2):
    def offset_helper(sign):
        tmp = copy(sub1)
        losses = np.array([], dtype=np.int32)
        rep = int(RAD2 * 1000 // INCR)
        tmp = shift(tmp, -sign * INCR)
        for _ in range(rep):
            tmp = shift(tmp, sign * INCR)
            loss = total_loss(tmp, sub2)
            if loss == 0:
                return 0, 0
            losses = np.append(losses, loss)
        ind = np.argmin(losses)
        return ind * INCR, losses[ind]

    noffset, nloss = offset_helper(sign=-1)
    poffset, ploss = offset_helper(sign=1)
    if nloss < ploss:
        return -noffset
    return poffset


def line_offset(sub1, sub2):
    def offset_helper():
        losses = np.array([], dtype=np.int32)
        diffs = sub2[:, 0] - sub1[0][0]
        diffs = diffs[diffs >= -RAD1 * 1000]
        diffs = diffs[diffs <= RAD1 * 1000]

        diffs = np.unique(np.append([0], diffs))
        if len(diffs) == 0:
            return -RAD1 * 1000, 10000000
        for diff in diffs:
            tmp = copy(sub1)
            tmp = shift(tmp, diff)
            tmploss = total_loss(tmp, sub2)
            # if tmploss == 0:
            #     return 0, 0
            losses = np.append(losses, tmploss)
        ind = np.argmin(losses)
        return diffs[ind], losses[ind]

    offset, loss = offset_helper()
    # print(offset,loss)
    return offset, loss


def all_offsets(sub1, sub2):
    # RAD2 = np.median(np.diff(sub1[:, 0]))

    def findstart():
        ls = []
        for j in range(STEP):
            tmp = sub1[j : j + STEP]
            _, tmploss = line_offset(tmp, sub2)
            ls.append(tmploss)
        _, ind = mindex(ls)
        return ind

    i = findstart()
    fin = False
    offsets = []
    while not fin:
        if i + STEP * 2 >= len(sub1):
            to = len(sub1)
            fin = True
        else:
            to = min(i + STEP, len(sub1))
        piece = sub1[i:to]
        offset, loss = line_offset(piece, sub2)
        # print(offset, loss)
        piece = shift(piece, offset)
        # Use time based here
        offset2 = time_offset(piece, sub2, RAD2=5)
        # print(offset2)
        offsets.append([i, to, offset2 + offset])
        i += STEP
    # print(format_offsets(sub1, offsets))
    offsets = adjust_loop(sub1, sub2, offsets)
    return np.array(offsets)


def adjust(sub1, sub2, offsets):
    def sieve(ind):
        if len(data) > 1:
            ll = data[ind][1] - data[ind][0]
            if ind == 0:
                if sub1[ll // 2][1] + data[ind][2] < 0:
                    return True
            elif data[ind][0] + data[ind][2] < data[ind - 1][1] + data[ind - 1][
                2
            ] and ll <= (data[ind - 1][1] - data[ind - 1][0]):
                return True
            if ind == len(data) - 1:
                if sub1[-ll // 2][0] + data[ind][2] > sub2[-1][1]:
                    return True
            elif data[ind][1] + data[ind][2] > data[ind + 1][0] + data[ind + 1][
                2
            ] and ll < (data[ind + 1][1] - data[ind + 1][0]):
                return True
            if ll <= SMALLEST:
                return True
        return False

    data = copy(offsets)
    for i in range(len(data) - 1):
        a = data[i]
        b = data[i + 1]
        if abs(a[2] - b[2]) <= 100:
            a[1] = a[0]
            b[0] = a[0]
        else:
            k = pivot(sub1[a[0] : b[1]], sub2, a[2], b[2])
            a[1] = a[0] + k
            b[0] = a[0] + k
    newdata = []
    if len(data) > 1:
        # This should run till the end sINCe we check endpoints in sieve
        for i in range((len(data))):
            if not sieve(i):
                newdata.append((data[i]))
        return newdata
    else:
        return data


def adjust_loop(sub1, sub2, data):
    prev = data
    data = adjust(sub1, sub2, data)
    # print(data)
    while prev != data:
        prev = data
        data = adjust(sub1, sub2, data)
        # print(data)
    data[0][0] = 0
    data[-1][1] = len(sub1) - 1
    return data


def pivot(sub1, sub2, fr, to):
    def mabs(x):
        return mindex(abs(sub2[:, 0] - x))

    vf = np.vectorize(mabs)
    mjlist1 = np.column_stack(vf(shift(sub1, fr)[:, 0])[:2])
    mjlist2 = np.column_stack(vf(shift(sub1, to)[:, 0])[:2])

    losses = np.array([], dtype=np.int32)
    for i in range(SMALLEST // 2, len(sub1) - SMALLEST // 2):
        # piece1 = shift(sub1[:i], fr)
        # piece2 = shift(sub1[i:], to)
        # piece1 = np.append(piece1, piece2, axis=0)
        mjlist = np.concatenate((mjlist1[:i], mjlist2[i:]))
        loss = mjt(sub2, mjlist)
        losses = np.append(losses, loss)
    return np.argmin(losses) + SMALLEST // 2


def sgm(z):
    return np.exp(z - 4) + 1


def mjt(sub2, mjlist):
    total = 0
    prevmin = -1
    prevind = -1
    prevdur = 0
    matched = []
    for mj in mjlist:
        m, j = mj
        if j == prevind and prevdur > 0:
            m = prevmin
            prevdur = prevdur - (sub2[j][1] - sub2[j][0])
        else:
            prevmin = m
            prevind = j
            prevdur = sub2[j][1] - sub2[j][0]
        matched.append(prevind)
        total += m
    matched = np.unique(matched)
    segment_length = matched[-1] - matched[0]
    mul = sgm(abs(segment_length - len(matched)))
    return total * mul


def total_loss(sub1, sub2):
    total = 0
    prevmin = -1
    prevind = -1
    prevdur = 0
    matched = []
    for line in sub1:
        m, j = mindex(abs(sub2[:, 0] - line[0]))
        if j == prevind and prevdur > 0:
            m = prevmin
            prevdur = prevdur - (sub2[j][1] - sub2[j][0])
        else:
            prevmin = m
            prevind = j
            prevdur = sub2[j][1] - sub2[j][0]
        matched.append(prevind)
        total += m
    matched = np.unique(matched)
    segment_length = matched[-1] - matched[0]
    mul = sgm(abs(segment_length - len(matched)))
    return total * mul
