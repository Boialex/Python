def is_polindrom(s):
    forward = s
    backward = s[::-1]
    if forward == backward:
        return True
    else:
        return False


def only_alpha(s):
    new_s = []
    for ch in s:
        if ch.isalpha():
            new_s.append(ch)
    new_s = ''.join(new_s).lower()
    new_s = new_s.replace('ё', 'е')
    return ''.join(new_s).lower()


def main():
    with open('input.txt') as f:
        data = f.readlines()
    for s in data[1:]:
        s = only_alpha(s)
        if is_polindrom(s):
            print('yes')
        else:
            print('no')


if __name__ == "__main__":
    main()
