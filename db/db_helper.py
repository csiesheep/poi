#!/usr/bin/python
# -*- encoding: utf8 -*-

from py2neo import Graph
from pymongo import MongoClient

import settings


__author__ = 'sheep'


class mongodb_helper(object):

    #TODO ip and port
    @staticmethod
    def get_client():
        return MongoClient(host=settings.DB_HOST,
                           port=settings.DB_PORT)

    @staticmethod
    def drop_db():
        client = mongodb_helper.get_client()
        client.drop_database(settings.DB_NAME)

    @staticmethod
    def get_coll(coll_name):
        client = mongodb_helper.get_client()
        return client[settings.DB_NAME][coll_name]


class Neo4j_helper(object):

    @staticmethod
    def get_client():
        s = 'http://%s:%s@%s:%d/db/data/' % (settings.NEO4J_USER,
                                             settings.NEO4J_PASSWORD,
                                             settings.NEO4J_HOST,
                                             settings.NEO4J_PORT)
        print s
        g = Graph(s)
#       g = Graph(host=settings.NEO4J_HOST,
#                 http_port=settings.NEO4J_PORT,
#                 user=settings.NEO4J_USER,
#                 password=settings.NEO4J_PORT)
        return g
