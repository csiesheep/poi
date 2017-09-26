#!/usr/bin/python
# -*- encoding: utf8 -*-

from math import *
import numpy as np
import unittest

from db.db_helper import mongodb_helper
import settings


__author__ = 'sheep'


def get_knn(type_, id_, k=10):
    print type_
    distances = []
    vector_coll = mongodb_helper.get_coll(settings.VECTOR_COLL)
    rest = vector_coll.find_one({'id': id_})
    if rest is None:
        return []

    v = rest['v']
    for business in vector_coll.find({'type': settings.BUSINESS_COLL}):
        v2 = business['v']
        if type_ == 'euclidean':
            distance = by_euclidean_distance(v, v2)
        if type_ == 'manhattan':
            distance = by_manhattan_distance(v, v2)
        if type_ == 'inner':
            distance = np.inner(v, v2)
        if type_ == 'sigmoid':
            distance = by_sigmoid_inner_product(v, v2)
        if type_ == 'cosine':
            distance = by_cosine(v, v2)
        distances.append((distance, business['id']))

    if type_ in ['inner', 'sigmoid', 'cosine']:
        results = sorted(distances, reverse=True)[1:k + 1]
        print results
        return results
    return sorted(distances)[1:k + 1]


#TODO refector and speed up
def by_euclidean_distance(v, v2):
    return sqrt(sum(pow(a-b,2) for a, b in zip(v, v2)))

def by_inner_product(v, v2):
    return sum(a*b for a, b in zip(v, v2))

def by_sigmoid_inner_product(v, v2):
    return 1/(1 + exp(-sum(a*b for a, b in zip(v, v2))))

def by_cosine(v, v2):
    return sum(a*b for a, b in zip(v, v2))/(sqrt(sum(pow(a,2) for a in v))*sqrt(sum(pow(b,2) for b in v2)))

def by_manhattan_distance(v, v2):
    return sum(abs(a-b) for a, b in zip(v, v2))
