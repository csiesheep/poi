#!/usr/bin/python
# -*- encoding: utf8 -*-

from math import *

from db.db_helper import mongodb_helper
import settings


__author__ = 'sheep'


def get_knn(type_, id_, k=10):
    print type_
    if type_ == 'euclidean':
        return by_euclidean_distance(id_, k=k)
    if type_ == 'manhattan':
        return by_manhattan_distance(id_, k=k)
    if type_ == 'inner':
        return by_inner_product(id_, k=k)
    if type_ == 'sigmoid':
        return by_sigmoid_inner_product(id_, k=k)
    if type_ == 'cosine':
        return by_cosine(id_, k=k)
    return []

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

def by_inner_product(id_, k=10):
    distances = []
    vector_coll = mongodb_helper.get_coll(settings.VECTOR_COLL)
    rest = vector_coll.find_one({'id': id_})
    if rest is None:
        return []

    v = rest['v']
    for business in vector_coll.find({'type': settings.BUSINESS_COLL}):
        v2 = business['v']
        distance = sum(a*b for a, b in zip(v, v2))
        distances.append((distance, business['id']))
    return sorted(distances)[1:k+1]

def by_sigmoid_inner_product(id_, k=10):
    distances = []
    vector_coll = mongodb_helper.get_coll(settings.VECTOR_COLL)
    rest = vector_coll.find_one({'id': id_})
    if rest is None:
        return []

    v = rest['v']
    for business in vector_coll.find({'type': settings.BUSINESS_COLL}):
        v2 = business['v']
        distance = 1/(1 + exp(-sum(a*b for a, b in zip(v, v2))))
        distances.append((distance, business['id']))
    return sorted(distances)[1:k+1]

def by_cosine(id_, k=10):
    distances = []
    vector_coll = mongodb_helper.get_coll(settings.VECTOR_COLL)
    rest = vector_coll.find_one({'id': id_})
    if rest is None:
        return []

    v = rest['v']
    for business in vector_coll.find({'type': settings.BUSINESS_COLL}):
        v2 = business['v']
        distance = sum(a*b for a, b in zip(v, v2))/(sqrt(sum(pow(a,2) for a in v))*sqrt(sum(pow(b,2) for b in v2)))
        distances.append((distance, business['id']))
    return sorted(distances)[1:k+1]

def by_manhattan_distance(id_, k=10):
    distances = []
    vector_coll = mongodb_helper.get_coll(settings.VECTOR_COLL)
    rest = vector_coll.find_one({'id': id_})
    if rest is None:
        return []

    v = rest['v']
    for business in vector_coll.find({'type': settings.BUSINESS_COLL}):
        v2 = business['v']
        distance = sum(abs(a-b) for a, b in zip(v, v2))
        distances.append((distance, business['id']))
    return sorted(distances)[1:k+1]
