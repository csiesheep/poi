#!/usr/bin/python
# -*- encoding: utf8 -*-

from math import *
import unittest

from db.db_helper import mongodb_helper
import settings
import knn


__author__ = 'djc5627'


class EuclieanDistanceTest(unittest.TestCase):

    def testAllZero(self):
        v = [0]
        v2 = [0]
        actual = knn.by_euclidean_distance(v, v2)
        expected = 0.0
        self.assertEquals(actual, expected)

    def testSimple(self):
        v = [0, 1, 0, 1]
        v2 = [1, 0, 1, 0]
        actual = knn.by_euclidean_distance(v, v2)
        expected = 2.0
        self.assertEquals(actual, expected)

    def testFloat(self):
        v = [.25, .25, .25, .25]
        v2 = [-.25, -.25, -.25, -.25]
        actual = knn.by_euclidean_distance(v, v2)
        expected = 1.0
        self.assertEquals(actual, expected)

    def testNegative(self):
        v = [.5, .5, -.25, -.25]
        v2 = [.25, .25, -.5, -.5]
        actual = knn.by_euclidean_distance(v, v2)
        expected = 0.5
        self.assertEquals(actual, expected)

    def testComplex(self):
        v = [.1253, .535, .132, .453, -.452, -.33]
        v2 = [.3532, .535, .531, .565, -.4586, .4875]
        actual = knn.by_euclidean_distance(v, v2)
        expected = 0.9444751029010771
        self.assertEquals(actual, expected)

class InnerDistanceTest(unittest.TestCase):

    def testAllZero(self):
        v = [0]
        v2 = [0]
        actual = knn.by_inner_product(v, v2)
        expected = 0.0
        self.assertEquals(actual, expected)

    def testSimple(self):
        v = [0, 1, 0, 1]
        v2 = [1, 0, 1, 0]
        actual = knn.by_inner_product(v, v2)
        expected = 0.0
        self.assertEquals(actual, expected)

    def testFloat(self):
        v = [.25, .25, .25, .25]
        v2 = [-.25, -.25, -.25, -.25]
        actual = knn.by_inner_product(v, v2)
        expected = -0.25
        self.assertEquals(actual, expected)

    def testNegative(self):
        v = [.5, .5, -.25, -.25]
        v2 = [.25, .25, -.5, -.5]
        actual = knn.by_inner_product(v, v2)
        expected = 0.5
        self.assertEquals(actual, expected)

    def testComplex(self):
        v = [.1253, .535, .132, .453, -.452, -.33]
        v2 = [.3532, .535, .531, .565, -.4586, .4875]
        actual = knn.by_inner_product(v, v2)
        expected = 0.70293016
        self.assertEquals(actual, expected)

class SigmoidDistanceTest(unittest.TestCase):

    def testAllZero(self):
        v = [0]
        v2 = [0]
        actual = knn.by_sigmoid_inner_product(v, v2)
        expected = 0.5
        self.assertEquals(actual, expected)

    def testSimple(self):
        v = [0, 1, 0, 1]
        v2 = [1, 0, 1, 0]
        actual = knn.by_sigmoid_inner_product(v, v2)
        expected = 0.5
        self.assertEquals(actual, expected)

    def testFloat(self):
        v = [.25, .25, .25, .25]
        v2 = [-.25, -.25, -.25, -.25]
        actual = knn.by_sigmoid_inner_product(v, v2)
        expected = 0.43782349911420193
        self.assertEquals(actual, expected)

    def testNegative(self):
        v = [.5, .5, -.25, -.25]
        v2 = [.25, .25, -.5, -.5]
        actual = knn.by_sigmoid_inner_product(v, v2)
        expected = 0.6224593312018546
        self.assertEquals(actual, expected)

    def testComplex(self):
        v = [.1253, .535, .132, .453, -.452, -.33]
        v2 = [.3532, .535, .531, .565, -.4586, .4875]
        actual = knn.by_sigmoid_inner_product(v, v2)
        expected = 0.668837105893633
        self.assertEquals(actual, expected)

class CosineDistanceTest(unittest.TestCase):

    def testAllOne(self):
        v = [1]
        v2 = [1]
        actual = knn.by_cosine(v, v2)
        expected = 1.0
        self.assertEquals(actual, expected)

    def testSimple(self):
        v = [0, 1, 0, 1]
        v2 = [1, 0, 1, 0]
        actual = knn.by_cosine(v, v2)
        expected = 0.0
        self.assertEquals(actual, expected)

    def testFloat(self):
        v = [.25, .25, .25, .25]
        v2 = [-.25, -.25, -.25, -.25]
        actual = knn.by_cosine(v, v2)
        expected = -1
        self.assertEquals(actual, expected)

    def testNegative(self):
        v = [.5, .5, -.25, -.25]
        v2 = [.25, .25, -.5, -.5]
        actual = knn.by_cosine(v, v2)
        expected = 0.7999999999999998
        self.assertEquals(actual, expected)

    def testComplex(self):
        v = [.1253, .535, .132, .453, -.452, -.33]
        v2 = [.3532, .535, .531, .565, -.4586, .4875]
        actual = knn.by_cosine(v, v2)
        expected = 0.6355589632212779
        self.assertEquals(actual, expected)

class ManhattanDistanceTest(unittest.TestCase):

    def testAllZero(self):
        v = [0]
        v2 = [0]
        actual = knn.by_manhattan_distance(v, v2)
        expected = 0.0
        self.assertEquals(actual, expected)

    def testSimple(self):
        v = [0, 1, 0, 1]
        v2 = [1, 0, 1, 0]
        actual = knn.by_manhattan_distance(v, v2)
        expected = 4.0
        self.assertEquals(actual, expected)

    def testFloat(self):
        v = [.25, .25, .25, .25]
        v2 = [-.25, -.25, -.25, -.25]
        actual = knn.by_manhattan_distance(v, v2)
        expected = 2.0
        self.assertEquals(actual, expected)

    def testNegative(self):
        v = [.5, .5, -.25, -.25]
        v2 = [.25, .25, -.5, -.5]
        actual = knn.by_manhattan_distance(v, v2)
        expected = 1.0
        self.assertEquals(actual, expected)

    def testComplex(self):
        v = [.1253, .535, .132, .453, -.452, -.33]
        v2 = [.3532, .535, .531, .565, -.4586, .4875]
        actual = knn.by_manhattan_distance(v, v2)
        expected = 1.5629999999999997
        self.assertEquals(actual, expected)