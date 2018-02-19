#!/usr/bin/python
# -*- encoding: utf8 -*-

from math import *
import numpy as np
import unittest

from db.db_helper import mongodb_helper
import settings


__author__ = 'sheep'


def get_knn(type_, id_, k=10, approach='hin2vec'):
    distances = []
    #TODO refector
    coll_mapping = {
        'hin2vec': settings.VECTOR_COLL,
        'deepwalk': settings.VECTOR_DEEPWALK_COLL,
        'pte': settings.VECTOR_PTE_COLL,
        'esim': settings.VECTOR_ESIM_COLL,
    }
    vector_coll = mongodb_helper.get_coll(coll_mapping[approach])
    rest = vector_coll.find_one({'id': id_})
    if rest is None:
        return []

    v = rest['v']
    hin2vec_path_dim = [2, 15, 24, 31, 46, 52, 58, 68, 78, 85,
                        87, 92, 93, 98, 122, 125]
#   hin2vec_path_dim = []
    if approach == 'hin2vec':
        for i in hin2vec_path_dim:
            v[i] = 0
    for business in vector_coll.find({'type': settings.BUSINESS_COLL}):
        if business['id'] == id_:
            continue

        v2 = business['v']
        if approach == 'hin2vec':
            for i in hin2vec_path_dim:
                v2[i] = 0
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
        results = sorted(distances, reverse=True)[:k]
        return results
    return sorted(distances)[:k]


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
