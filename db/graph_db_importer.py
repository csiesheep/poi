#!/usr/bin/python
# -*- encoding: utf8 -*-

import datetime
import optparse
from py2neo import Graph, Relationship
import sys

from db.db_helper import Neo4j_helper
import settings


__author__ = 'Liuxuan Huang', 'sheep'


def main():
    '''\
    %prog [options]
    '''
    graph = Neo4j_helper.get_client()
#   graph.delete_all()
#   create_nodes(graph, settings.GRAPH_FILE)
#   create_indexes(graph)
    create_edges(graph, settings.GRAPH_FILE)
    show_statistics(graph)
    return 0

def create_nodes(graph, fname):
    nodes = set()
    with open(fname) as f:
        for line in f:
            tokens = line[:-1].split('\t')
            node1 = tuple(tokens[:3])
            node2 = tuple(tokens[3:])
            nodes.add(node1)
            nodes.add(node2)

    print 'node count:', len(nodes)
    for ith, node in enumerate(nodes):
        s = ('CREATE (n: %s {id: "%s", name: "%s"})'
             '' % (node[1], node[0], node[2].replace('"', "'")))
        graph.run(s)
        if ith % 1000 == 0:
            print 'progress %d/%d' % (ith, len(nodes))

def create_indexes(graph):
    for type_ in [settings.BUSINESS_CLASS,
                  settings.USER_CLASS,
                  settings.CITY_CLASS,
                  settings.CATEGORY_CLASS]:
        graph.run('CREATE INDEX ON :%s(id)' % type_)

def create_edges(graph, fname):
    def get_edges(fname):
        current_id = None
        current_class = []
        tos = []
        with open(fname) as f:
            for line in f:
                tokens = line[:-1].split('\t')
                from_id, from_class, _, to_id, to_class, _ = tokens

                if current_id is None:
                    current_id = from_id
                    current_class = from_class
                    tos = []
                elif current_id != from_id:
                    yield current_id, current_class, tos
                    current_id = from_id
                    current_class = from_class
                    tos = []

                tos.append((to_id, to_class))
            yield current_id, current_class, tos

    def get_sub_tos(tos, k=50):
        if len(tos) < k:
            yield tos
        else:
            index = 0
            while index < len(tos):
                yield tos[index:index+k]
                index += k

    count = 0
    ith_from = 0
    for from_id, from_class, tos in get_edges(fname):
        head = "MATCH (f:%s {id:'%s'})" % (from_class, from_id)
        for sub_tos in get_sub_tos(tos):
            matches = [head]
            creates = []
            for ith, (to_id, to_class) in enumerate(sub_tos):
                matches.append("(t%d:%s {id:'%s'})" % (ith,
                                                       to_class,
                                                       to_id))
                creates.append('(f)-[:%s]->(t%d)'
                               '' % (settings.EDGE_CLASSES[(from_class,
                                                            to_class)],
                                     ith))
#               creates.append('(t%d)-[:%s]->(f)'
#                              '' % (ith,
#                                    settings.EDGE_CLASSES[(to_class,
#                                                           from_class)]))
            s = '%s CREATE %s' % (', '.join(matches), ', '.join(creates))
            graph.run(s)

            ith_from += 1
            count += len(sub_tos)
            if ith_from % 100 == 0:
                print ith_from, count, datetime.datetime.now()

def show_statistics(graph):
    s = 'MATCH (n) RETURN DISTINCT count(labels(n)) as c, labels(n) as l;'
    for data in graph.run(s).data():
        print 'Node %s count: %d' % (data['l'][0], data['c'])
    for (from_class,to_class), edge_class in settings.EDGE_CLASSES.items():
        count = len(list(graph.run('MATCH (a:%s)-[]->(b:%s) '
                                   'RETURN a.name, b.name'
                                   '' % (from_class, to_class))))
        print 'Edge %s count: %d' % (edge_class, count)

#   for a in graph.run('MATCH (a)-[]-(b) RETURN a, b').data():
#       print a


if __name__ == '__main__':
    parser = optparse.OptionParser(usage=main.__doc__)
    options, args = parser.parse_args()

    if len(args) != 0:
        parser.print_help()
        sys.exit()

    sys.exit(main(*args))
