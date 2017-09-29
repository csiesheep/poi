#!/usr/bin/python
# -*- encoding: utf8 -*-

from py2neo import authenticate, Graph
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
        authenticate('%s:%d' % (settings.NEO4J_HOST,
                                settings.NEO4J_HTTP_PORT),
                     settings.NEO4J_USER,
                     settings.NEO4J_PASSWORD)
        g = Graph(host=settings.NEO4J_HOST,
                  user=settings.NEO4J_USER,
                  password=settings.NEO4J_PASSWORD,
                  http_port=settings.NEO4J_HTTP_PORT,
                  https_port=settings.NEO4J_HTTPS_PORT,
                  bolt_port=settings.NEO4J_BOLT_PORT)
        return g
