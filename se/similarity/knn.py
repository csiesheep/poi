#!/usr/bin/python
# -*- encoding: utf8 -*-

from math import *

from db.db_helper import mongodb_helper
import settings


__author__ = 'sheep'


#TODO refector and speed up
def by_euclidean_distance(id_, k=10):
    distances = []
    vector_coll = mongodb_helper.get_coll(settings.VECTOR_COLL)
    rest = vector_coll.find_one({'id': id_})
    if rest is None:
        return []

    v = rest['v']
    for business in vector_coll.find({'type': settings.BUSINESS_COLL}):
        v2 = business['v']
        distance = sqrt(sum(pow(a-b,2) for a, b in zip(v, v2)))
        distances.append((distance, business['id']))
    return sorted(distances)[1:k+1]

#TODO
def by_inner_product(id_, k=10):
    pass

#TODO
def by_sigmoid_inner_product(id_, k=10):
    pass

#TODO
def by_cosine(id_, k=10):
    pass

#TODO
def by_manhattan_distance(id_, k=10):
    pass
