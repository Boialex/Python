#!/usr/bin/env python3
import sys


class AssertRaises(object):
    def __init__(self, expecting_exception):
        self.expecting_exception = expecting_exception

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if isinstance(exc_val, self.expecting_exception):
            return True
        else:
            raise AssertionError


exec(sys.stdin.read())
