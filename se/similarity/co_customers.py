#!/usr/bin/python
# -*- encoding: utf8 -*-

from math import *
from db.db_helper import Neo4j_helper
import numpy as np
import unittest

from db.db_helper import mongodb_helper
import settings


__author__ = 'djc5627'


def get_number_com_customers(rest_id1, rest_id2):
    client = Neo4j_helper.get_client()
    number_co_customers = len(client.run("MATCH (a:B {id: {rest_id1}})-[]-(c)-[]-(b:B {id: {rest_id2}}) RETURN a, b, c",
                                         rest_id1 = rest_id1, rest_id2 = rest_id2).data())
    return co_customers

def get_ratio_com_customers(rest_id1, rest_id2):
    #Get customers from each business, get co-customers, find the ratio
    client = Neo4j_helper.get_client()
    number_customers1 = len(client.run("MATCH (a:B {id:{rest_id1}})-[]-(c) RETURN a, c",  rest_id1 = rest_id1).data())
    number_customers2 = len(client.run("MATCH (a:B {id:{rest_id2}})-[]-(c) RETURN a, c", rest_id2 = rest_id2).data())
    number_co_customers = len(client.run("MATCH (a:B {id:{rest_id1}})-[]-(c)-[]-(b:B {id:{rest_id2}}) RETURN a, b, c",
                                         rest_id1 = rest_id1, rest_id2 = rest_id2).data())
    ratio = number_co_customers / (number_customers1 + number_customers2 - number_co_customers)
    return ratio
