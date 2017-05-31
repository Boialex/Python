#!/usr/bin/env python3

import sys


def unique(sequence):
    previous = None
    for x in sequence:
        if x != previous:
            yield x
        previous = x


exec(sys.stdin.read())
