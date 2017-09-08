#!/usr/bin/python
# -*- encoding: utf8 -*-

from pymongo import MongoClient

import settings


__author__ = 'sheep'


class mongodb_helper(object):

    #TODO ip and port
    @staticmethod
    def get_client():
        return MongoClient()

    @staticmethod
    def drop_db():
        client = mongodb_helper.get_client()
        client.drop_database(settings.DB_NAME)

    @staticmethod
    def get_coll(coll_name):
        client = mongodb_helper.get_client()
        return client[settings.DB_NAME][coll_name]
