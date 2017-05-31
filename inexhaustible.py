#!/usr/bin/env python3
import sys


def inexhaustible(generator):
    class MyGenerator(object):
        def __init__(self, *args, **kwargs):
            self._args = args
            self._kwargs = kwargs

        def __iter__(self):
            self.generator = generator(*self._args, **self._kwargs)
            return self

        def __next__(self):
            return next(self.generator)

    MyGenerator.__name__ = generator.__name__
    MyGenerator.__doc__ = generator.__doc__

    return MyGenerator


exec(sys.stdin.read())
