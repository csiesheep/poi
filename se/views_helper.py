#!/usr/bin/python
# -*- encoding: utf8 -*-

from db.db_helper import mongodb_helper
import settings


__author__ = 'sheep'


def get_keywords(bid):
    coll = mongodb_helper.get_coll(settings.BUSINESS_KEYWORD_COLL)
    data = coll.find_one({'id': bid})
    return [w['word'] for w in data['keywords']]
