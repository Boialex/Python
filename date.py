#!/usr/bin/env python3

import re


def is_date(string):
    date = re.compile(r"""
        (
        (^
        (([0-9]{2}\.){2}[0-9]{4}|
        ([0-9]{2}-){2}[0-9]{4}|
        ([0-9]{2}\/){2}[0-9]{4})
        $
        |
        ^
        ([0-9]{4}\.[0-9]{2}\.[0-9]{2}|
        [0-9]{4}-[0-9]{2}-[0-9]{2}|
        [0-9]{4}\/[0-9]{2}\/[0-9]{2})
        $)|
        ^
        [0-9]{1,2}\s*([а-я]+)\s*[0-9]{4}
        $)
        """, re.VERBOSE)
    if date.match(string.lower()):
        return True
    else:
        return False


def main():
    with open('input.txt') as f:
        text = f.readlines()
    for line in text:
        if is_date(line):
            print('YES')
        else:
            print('NO')


if __name__ == "__main__":
    main()
