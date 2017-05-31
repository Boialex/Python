#!/usr/bin/env python3

import re


def find_imports(code):
    modules = []
    is_import = re.compile(r"""import(?P<all>\s+((\w+\.?)+)(,\s+((\w+\.?)+))*)|
                            from\s+(?P<from>\w+)\s+import""", re.VERBOSE)
    all = is_import.findall(code)
    # print(all)
    for match in all:
        if match[-1]:
            modules += [match[-1].strip()]
        else:
            current = match[0].strip().split(',')
            current = list(map(lambda s: s.strip(), current))
            # print('cur', current)
            modules += current
    return modules


def main():
    with open('input.txt') as f:
        data = f.read()
    print(', '.join(sorted(set(find_imports(data)))))


if __name__ == "__main__":
    main()
