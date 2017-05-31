import re
from urllib.request import urlopen

import bs4


def get_pushkin_poem(url):
    with urlopen(url) as conn:
        soup = bs4.BeautifulSoup(conn, 'html5lib')
    content = soup.find('div', {'class': 'entry-content'}).findAll('p')
    pattern = re.compile('<[^>]*>', re.UNICODE)
    content = re.sub(pattern, '', str(content))
    some_rubbish = re.compile(r'1\)', re.UNICODE)
    content = re.sub(some_rubbish, '', content)
    return content[1:-1]  # to erase []


def get_pushkin_joined(url):
    with urlopen(url) as conn:
        soup = bs4.BeautifulSoup(conn, 'html5lib')
    content = soup.find('div', {'class': 'entry-content'}).findAll('p')
    pattern = re.compile('<[^>]*>', re.UNICODE)
    content = re.sub(pattern, '', str(content))
    some_rubbish = re.compile(r'1\)', re.UNICODE)
    content = re.sub(some_rubbish, '', content)
    return ' '.join(content[1:-1].split('\n'))


def get_pushkin():
    url = "http://stih.su/pushkin/"
    with urlopen(url) as conn:
        soup = bs4.BeautifulSoup(conn, 'html5lib')
    urls = []
    start = soup.find('ol', {'class': 'number-navi best'})
    poem = start.findNext('li')
    while poem is not None:
        urls += [poem.a['href']]
        poem = poem.findNextSibling('li')
    urls.pop(0)  # bad html
    data_as_poems = ''
    for url in urls:
        data_as_poems += get_pushkin_poem(url)
        if len(data_as_poems) > 300000:
            break
    data_as_one = []
    for url in urls:
        data_as_one += [get_pushkin_joined(url)]
        if sum([len(s) for s in data_as_one]) > 300000:
            break
    return data_as_poems, data_as_one


def get_dostoevskiy():
    url = "http://az.lib.ru/d/dostoewskij_f_m/text_0060.shtml"
    with urlopen(url) as conn:
        soup = bs4.BeautifulSoup(conn, 'html5lib')
    content = soup.findAll('dd')
    pattern = re.compile('<[^>]*>', re.UNICODE)
    content = re.sub(pattern, '', str(content))
    some_rubbish = re.compile('&nbsp;', re.UNICODE)
    content = re.sub(some_rubbish, '', content)
    content = content[:content.find(u'(Г. М. Фридлендер)')]
    spaces = re.compile(' +', re.UNICODE)
    content = re.sub(spaces, ' ', content)
    enters = re.compile('\n+', re.UNICODE)
    content = re.sub(enters, '\n', content)
    return content[100:len(content) // 5]  # around a half


def get():
    pushkin_poem, pushkin_texts = get_pushkin()
    pushkin_poem = 'generate --depth 2 --size 300\n' + pushkin_poem
    pushkin_texts = ['generate --depth 2 --size 300\n'] + pushkin_texts
    dostoevskiy = 'generate --depth 3 --size 300\n' + get_dostoevskiy()
    with open('input_poem.txt', 'w') as f:
        f.write(pushkin_poem)
    with open('input_text.txt', 'w') as f:
        f.write('\n'.join(pushkin_texts))
    with open('input_dost.txt', 'w') as f:
        f.write(dostoevskiy[:len(dostoevskiy) // 2])

# if __name__ == "__main__":
#     main()
