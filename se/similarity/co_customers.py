#!/usr/bin/python
# -*- encoding: utf8 -*-

from math import *
from db.db_helper import Neo4j_helper
import numpy as np
import unittest

from db.db_helper import mongodb_helper
import settings


__author__ = 'djc5627', 'sheep'


def get_number_com_customers(rest_id1, rest_id2):
    client = Neo4j_helper.get_client()
    s = ("MATCH (a:B {id: '%s'})-[]-(c:U)-[]-(b:B {id: '%s'}) "
         "RETURN DISTINCT a, b, c"
         "" % (rest_id1, rest_id2))
    count = len(client.run(s).data())
    return count

def get_ratio_com_customers(rest_id1, rest_id2):
    def get_customers(rest_id):
        client = Neo4j_helper.get_client()
        s = "MATCH (a:B {id:'%s'})-[]-(c:U) RETURN DISTINCT a, c" % rest_id
        customers = set([a['c']['id'] for a in client.run(s).data()])
        return customers

    customers1 = get_customers(rest_id1)
    customers2 = get_customers(rest_id2)
    return float(len(customers1.intersection(customers2)))/len(customers1.union(customers2))
