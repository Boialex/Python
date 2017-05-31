#!/usr/bin/env python3
def make_language_dict(data):
    languages = {}
    for i, line in enumerate(data):
        if line == '\n':
            break
        line = line.strip().lower().split()
        lang_name = line[0]
        for ch in line[1]:
            if ch not in languages:
                languages[ch] = set()
            languages[ch].add(lang_name)

    return languages, i


def get_word_language(word, languages):
    count = dict()
    default = set()
    default.add('')
    for ch in word:
        lang = languages.get(ch, default)
        for l in lang:
            get = count.get(l, 0)
            count[l] = get + 1
    sort_cnt = sorted(count.items(), key=lambda x: (-x[1], x[0]))
    if sort_cnt[0][0] == '' and len(sort_cnt) > 1:
        return sort_cnt[1][0]
    return sort_cnt[0][0]


def get_request_languages(s, languages):
    words = s.split()
    has_languages = set()
    for word in words:
        new_lang = get_word_language(word, languages)
        if new_lang != '':
            has_languages.add(new_lang)
    if '' in has_languages and len(has_languages) == 1:
        return ''
    else:
        return ' '.join(sorted(has_languages))


def main():
    with open('input.txt') as f:
        data = f.readlines()
    languages, end_block = make_language_dict(data)

    for line in data[end_block + 1:]:
        line = line.strip().lower()
        print(get_request_languages(line, languages))


if __name__ == "__main__":
    main()
