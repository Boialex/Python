#!/usr/bin/env python3
import sys
import functools


def takes(*types):
    def decorator(func):
        @functools.wraps(func)
        def decorated(*args):
            for t, x in zip(types, args):
                if not isinstance(x, t):
                    raise TypeError
            return func(*args)
        return decorated
    return decorator


exec(sys.stdin.read())
