#!/usr/bin/python
# -*- encoding: utf8 -*-

from db.db_helper import mongodb_helper
import settings


__author__ = 'sheep'


def category_distribution(ids):
    business_coll = mongodb_helper.get_coll(settings.BUSINESS_COLL)
    cat_dist = {}
    for id_ in ids:
        cats = business_coll.find_one({'business_id': id_})['categories']
        if cats is None:
            continue

        for cat in cats:
            if cat not in cat_dist:
                cat_dist[cat] = 1.0/len(ids)
                continue
            cat_dist[cat] += 1.0/len(ids)
    return sorted(cat_dist.items(), key=lambda x:x[1], reverse=True)

def city_distribution(ids):
    business_coll = mongodb_helper.get_coll(settings.BUSINESS_COLL)
    city_dist = {}
    for id_ in ids:
        city = business_coll.find_one({'business_id': id_})['city']
        if city is None:
            continue

        if city not in city_dist:
            city_dist[city] = 1.0/len(ids)
            continue
        city_dist[city] += 1.0/len(ids)
    return sorted(city_dist.items(), key=lambda x:x[1], reverse=True)

#TODO
def keyword_distribution(ids):
    pass

#TODO
def pairwise_similarity_distribution(ids):
    pass

#TODO
def pairwise_co_customer_distribution(ids):
    pass
