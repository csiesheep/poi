#!/usr/bin/python
# -*- encoding: utf8 -*-

import unittest

from tools.extract_keywords import *


__author__ = "sheep"


class GetTokKeywordsOfAReview(unittest.TestCase):

    def testSimple(self):
        seq2word = {
            0: 'A',
            1: 'B',
            2: 'C',
            3: 'D',
        }
        review_tfidfs = [0.1, 0.2, 0.9, 0.3]
        expected = ['C', 'D', 'B']
        actual = get_topk_keywords_of_a_review(3, review_tfidfs, seq2word)
        self.assertEquals(actual, expected)


class GetTokKeywords(unittest.TestCase):

    def testSimple(self):
        seq2word = {
            0: 'A',
            1: 'B',
            2: 'C',
            3: 'D',
            4: 'E',
            5: 'F',
        }
        tfidfs = [
            [0.1, 0.2, 0.9, 0.3, 0.1, 0.1],
            [0.9, 0.8, 0.7, 0.1, 0.1, 0.1],
            [0.1, 0.1, 0.1, 0.7, 0.8, 0.9],
        ]
        indexes = [0, 1]
        expected = {'C': 1.0, 'B': 1.0, 'A': 0.5}
        actual = get_topk_keywords(3, indexes, tfidfs, seq2word)
        self.assertEquals(actual, expected)


if __name__ == '__main__':
    unittest.main()

