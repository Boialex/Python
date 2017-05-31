#!/usr/bin/env python3
def main():
    set_of_words = {}
    with open('input.txt', 'r') as f:
        data = f.readlines()

    for line in data[1:]:
        line = line.strip().lower()
        sorted_line = ''.join(sorted(line))
        if sorted_line in set_of_words:
            set_of_words[sorted_line].add(line)
        else:
            new_set = set()
            new_set.add(line)
            set_of_words[sorted_line] = new_set

    out = []
    for i in set_of_words.keys():
        if len(set_of_words[i]) == 1:
            continue
        anagrams = []
        for s in set_of_words[i]:
            anagrams.append(s)
        out.append(' '.join(sorted(anagrams)))
    for s in sorted(out):
        print(*s, sep='')


if __name__ == "__main__":
    main()
