#!/usr/bin/python3
import pysrt
import numpy as np
from copy import deepcopy as copy

tags = r"{\\an\d*}|&lt;.*?&gt;|<.*?>"
SMALLEST = 5


def ms(ls):
    return ls.hours * 3600000 + ls.minutes * 60000 + ls.seconds * 1000 + ls.milliseconds


def read(r):
    sub = []
    for line in r:
        sub.append((ms(line.start), ms(line.end)))
    return np.array(sub)


def readf(r):
    return read(pysrt.open(r))


def shift(sub, milliseconds):
    tmp = copy(sub)
    tmp = tmp + milliseconds
    return tmp


def mindex(arr):
    ind = np.argmin(arr)
    return arr[ind], ind


def single_offset(sub1, sub2, inc, window):
    def offset_helper(sign):
        tmp = copy(sub1)
        losses = np.array([], dtype=np.int32)
        rep = int(window * 1000 // inc)
        tmp = shift(tmp, -sign * inc)
        for i in range(rep):
            tmp = shift(tmp, sign * inc)
            loss = total_loss(tmp, sub2)
            if loss == 0:
                return 0, 0
            losses = np.append(losses, loss)
        ind = np.argmin(losses)
        return ind * inc, losses[ind]

    noffset, nloss = offset_helper(sign=-1)
    poffset, ploss = offset_helper(sign=1)

    if nloss < ploss:
        return -noffset
    return poffset


def all_offsets(sub1, sub2, inc, window, step):
    i = 0
    fin = False
    offsets = []
    while not fin:
        if i + step * 2 >= len(sub1):
            to = len(sub1)
            fin = True
        else:
            to = min(i + step, len(sub1))
        piece = sub1[i:to]
        offset = single_offset(piece, sub2, inc=inc, window=window)
        offsets.append([i, to, offset])
        i += step
    offsets = adjust_loop(sub1, sub2, offsets)

    return np.array(offsets)


def adjust(sub1, sub2, data1):
    def sieve(ind):
        if len(data) > 1:
            ll = data[ind][1] - data[ind][0]
            if ind == 0:
                if sub1[ll // 2][1] + data[ind][2] < 0:
                    # print(ind, 1)
                    return True
            elif data[ind][0] + data[ind][2] < data[ind - 1][1] + data[ind - 1][2] and ll <= (data[ind - 1][1] - data[ind - 1][0]):
                # print(ind, 2)

                return True
            if ind == len(data) - 1:
                if sub1[-ll // 2][0] + data[ind][2] > sub2[-1][1]:
                    # print(ind, 3)

                    return True
            elif data[ind][1] + data[ind][2] > data[ind + 1][0] + data[ind + 1][2] and ll < (data[ind + 1][1] - data[ind + 1][0]):
                # print(ind, 4)

                return True
            if ll <= SMALLEST:
                # print(ind, 5)
                return True
        return False

    data = copy(data1)
    for i in range(len(data) - 1):
        a = data[i]
        b = data[i + 1]
        if a[2] != b[2]:
            k = pivot(sub1[a[0]:b[1]], sub2, a[2], b[2])
            a[1] = a[0] + k
            b[0] = a[0] + k
        else:
            a[1] = a[0]
            b[0] = a[0]
    newdata = []
    if len(data) > 1:
        # This should run till the end since we check endpoints in sieve
        for i in range((len(data))):
            if not sieve(i):
                newdata.append((data[i]))
        return newdata
    else:
        return data


def adjust_loop(sub1, sub2, data):
    prev = data
    data = adjust(sub1, sub2, data)
    while prev != data:
        prev = data
        data = adjust(sub1, sub2, data)
    data[0][0] = 0
    data[-1][1] = len(sub1) - 1
    return data


def pivot(sub1, sub2, fr, to):
    losses = np.array([], dtype=np.int32)
    for i in range(SMALLEST // 2, len(sub1) - SMALLEST // 2):
        sub = copy(sub1)
        piece1 = shift(sub[:i], fr)
        piece2 = shift(sub[i:], to)
        piece1 = np.append(piece1, piece2, axis=0)
        loss = total_loss(piece1, sub2)
        losses = np.append(losses, loss)
    return np.argmin(losses) + SMALLEST // 2


def total_loss(sub1, sub2):
    total = 0
    prevmin = -1
    prevind = -1
    prevdur = 0
    for line in sub1:
        m, j = mindex(abs(sub2[:, 0] - line[0]))
        if j == prevind and prevdur > 0:
            m = prevmin
            prevdur = prevdur - (sub2[j][1] - sub2[j][0])
        else:
            prevmin = m
            prevind = j
            prevdur = sub2[j][1] - sub2[j][0]
        total += m
    return total
