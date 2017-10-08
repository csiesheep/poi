#!/usr/bin/python
# -*- encoding: utf8 -*-

from py2neo import Graph
import string


__author__ = 'Liuxuan Huang'


def get_meta_graph(rest_id1, rest_id2, k):
    
  #  client = Neo4j_helper.get_client()
    graph = Graph('http://neo4j:hlxhlx1996@localhost:7474/db/data/')
    meta_graph = {}

#   rest_id2 = 'ybHlmdUHLPKfv85bRK4Wtw'
    for kth in range(1, k+1):
        nodeString = '[]'
        typeStringU = ('U',)
        c = list(string.ascii_lowercase) # get a list of lowercase alphabets
        # construct partial strings to query
        for i in range(kth):
            nodeString += ('-(%s)-[]' % c[i])
        # query for number of paths
        queryU = ('MATCH path=(S:B {id:"%s"})-%s-(E:B {id:"%s"}) '
             'RETURN DISTINCT count(path)'
             '' % (rest_id1, nodeString, rest_id2))
        queryC = ('MATCH path=(S:B {id:"%s"})-[]-(X)-[]-(E:B {id:"%s"}) '
             'WHERE (X: C)'
             'RETURN DISTINCT count(path)'
             '' % (rest_id1, rest_id2))
        numU = graph.run(queryU).evaluate()
        numC = graph.run(queryC).evaluate()
        # construct partial string into metagraph as types
        for i in range(kth-1):
            typeStringU += ('U',)

        meta_graph[typeStringU] = numU
        meta_graph['C',] = numC

    print(meta_graph)
    return meta_graph

#   Test case for B-U, since there is only two unconnected B in small grah database
#   get_meta_graph("YPavuOh2XsnRbLfl0DH2lQ","j8EHmuebLe8avjeFqrL0eg", 2)