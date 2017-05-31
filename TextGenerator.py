#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import collections
import random
import re
import string
import unittest
from collections import defaultdict


class TextGenerator(object):
    def __init__(self):
        self.tokens = []
        self.ngrams = defaultdict(list)
        self.depth = 0

    @staticmethod
    def _parse_string(s):
        find = re.compile(r'([a-zA-Zа-яА-Я\']+|[0-9]+|[^a-zA-Zа-яА-Я0-9\'])')
        m = find.findall(s)
        return m

    def tokenize(self, text):
        for line in text.split('\n'):
            self.tokens.append(self._parse_string(line))
        return self.get_tokens()

    def _count_words(self):
        for line in self.tokens:
            for word in line:
                if word.isalpha():
                    self.words_number += 1

    @staticmethod
    def _get_words(array):
        return [s for s in array if s.isalpha()]

    def probabilities(self, text, depth=0):
        self.fit(text, depth=depth, only_words=True)
        output = []
        for key, value in sorted(self.ngrams.items()):
            str_key = ''.join(key)
            if str_key.isalpha() or str_key == '':
                str_key = ' '.join(key)
                output.append(str_key)
                block = collections.Counter(self._get_words(value))
                count = sum(block.values())
                for word, number in sorted(block.items()):
                    output.append('  {}: {:.2f}'.format(word, number / count))
        return '\n'.join(output)

    def fit(self, text, depth=0, only_words=False):
        self.tokens = []
        self.depth = depth
        text = text.split('\n')
        for line in text:
            self.tokenize(line)
        for i in range(depth + 1):
            for line in self.tokens:
                if only_words:
                    line = self._get_words(line)
                for j, token in enumerate(line[i:]):
                    key = tuple(line[j: j + i])
                    if token:
                        self.ngrams[key].append(token)

    @staticmethod
    def _get_correct_begin(tokens):
        return [s for s in tokens if s.isalpha() or s.isnumeric()]

    def generate(self, size=1):
        key = tuple()
        text = []
        new_sentence = True
        need_space = False
        words_generated = []  # to get relevant key
        for i in range(size):
            if new_sentence:
                while len(self._get_correct_begin(self.ngrams[key])) == 0:
                    key = tuple(key[1:])
                new_word = random.choice(self._get_correct_begin(self.ngrams[key]))
            else:
                while key not in self.ngrams.keys():
                    key = tuple(key[1:])
                new_word = random.choice(self.ngrams[key])  # здесь вероятности учитываются за
                # счет повторений, так как value у self.ngrams - list, поэтому чем больше копий
                # одного токена, тем больше вероятность его выбрать
            words_generated.append(new_word)

            if new_sentence:
                new_word = new_word.capitalize()
                new_sentence = False
            if new_word in string.whitespace or new_word in string.punctuation:
                need_space = False
            if new_word in string.punctuation and text[-1] in string.whitespace:
                text.pop()
            if new_word == '"' or new_word == "'":
                text.append(' ')
            if need_space:
                need_space = False
                text += ' '
            text.append(new_word)

            if new_word.isalpha():
                need_space = True

            if new_word in string.punctuation:
                new_sentence = True
                need_space = True

            key = tuple(words_generated[-self.depth:])
        if text[-1] in string.whitespace:
            text[-1] = '.'
        if text[-1] not in string.punctuation:
            text += '.'
        return ''.join(text)

    def get_tokens(self):
        tokens = []
        for line in self.tokens:
            tokens += line
        return tokens


class TestTextGenerator(unittest.TestCase):
    def test_tokenize(self):
        self.assertListEqual(list(('Hello',)),
                             TextGenerator().tokenize('Hello'))
        self.assertListEqual(list(('Hello', ',', ' ', 'world', '!')),
                             TextGenerator().tokenize('Hello, world!'))
        self.assertListEqual(list(('abc', ' ', 'cab')),
                             TextGenerator().tokenize('abc cab'))
        self.assertListEqual(list(('abc', '123', 'abc')),
                             TextGenerator().tokenize('abc123abc'))
        self.assertListEqual(list(('во', '-', 'первых')),
                             TextGenerator().tokenize('во-первых'))
        self.assertListEqual(list(('First', ' ', 'line', 'Second', ' ', 'line')),
                             TextGenerator().tokenize('First line\nSecond line'))
        self.assertListEqual(list(('a', '2', 'c', '.', ' ', 'a')),
                             TextGenerator().tokenize('a2c. a'))
        self.assertListEqual(list(('12', '.', 'a')),
                             TextGenerator().tokenize('12.a'))
        self.assertListEqual(list(("let's",)),
                             TextGenerator().tokenize("let's"))
        self.assertListEqual(list(("don't",)),
                             TextGenerator().tokenize("don't"))

    def test_possibilities(self):
        self.assertEqual('\n  test: 1.00', TextGenerator().probabilities('test'))
        self.assertEqual('\n  Hello: 0.50\n  world: 0.50\nHello\n  world: 1.00',
                         TextGenerator().probabilities('Hello, world!', 1))
        # test from the problem description
        block1 = '\n  First: 0.17\n  Second: 0.17\n  line: 0.17\n  sentence: 0.17\n  test: 0.33\n'
        block2 = 'First\n  test: 1.00\n'
        block3 = 'Second\n  test: 1.00\n'
        block4 = 'test\n  line: 0.50\n  sentence: 0.50'
        s = block1 + block2 + block3 + block4
        self.assertEqual(s,
                         TextGenerator().probabilities('First test sentence\nSecond test line', 1))

    def test_fit(self):
        generator = TextGenerator()
        generator.fit('Hello, world!', 2)
        expect = {
            '': ['Hello', ',', ' ', 'world', '!'],
            'Hello': [','],
            ' ': ['world'],
            ',': [' '],
            'world': ['!'],
            ',  ': ['world'],
            'Hello ,': [' '],
            '  world': ['!']
        }
        got = generator.ngrams
        out = {}
        for key in got.keys():
            out[' '.join(key)] = got[key]
        self.assertDictEqual(expect, out)

    def test_generator(self):
        s = 'Hello'
        generator = TextGenerator()
        generator.fit(s, 1)
        self.assertEqual(' '.join([s] * 10) + '.', generator.generate(10))


def main():
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers(dest="command")

    parser_tokenize = subparsers.add_parser('tokenize', help='Tokenize input text')

    parser_probabilities = subparsers.add_parser('probabilities',
                                                 help='Count probabilities for input text')
    parser_probabilities.add_argument('--depth', metavar='NUM', default=0, type=int)

    parser_generate = subparsers.add_parser('generate', help='fit and generate text')
    parser_generate.add_argument('-d', '--depth', metavar='NUM', default=0, type=int)
    parser_generate.add_argument('-s', '--size', metavar='NUM', default=1, type=int)

    parser_test = subparsers.add_parser('test', help='start testing')

    generator = TextGenerator()

    with open('input.txt') as f:
        args = parser.parse_args(f.readline().split())
        text = ''.join(f.readlines())

    if args.command == 'tokenize':
        generator.tokenize(text=text)
        print(*generator.get_tokens(), sep='\n')
    elif args.command == 'probabilities':
        print(generator.probabilities(text, args.depth))
    elif args.command == 'generate':
        generator.fit(text, args.depth)
        print(generator.generate(args.size))
    elif args.command == 'test':
        unittest.main()


if __name__ == "__main__":
    main()
