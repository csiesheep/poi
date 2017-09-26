#!/usr/bin/python
# -*- encoding: utf8 -*-

from db.db_helper import Neo4j_helper


__author__ = 'sheep'


#TODO support k-hops
def get_paths(rest_id1, rest_id2, k=1):
    def get_info(node):
        for label in node.labels():
            break
        return node['id'], node['name'], label

    def update_nodes(node, id2seq, nodes):
        id_, name, label = get_info(node)
        if id_ not in id2seq:
            seq = len(id2seq)+1
            id2seq[id_] = seq
            nodes[seq] = {'name': name, 'type': label, 'id': id_}
        return id2seq[id_]


    client = Neo4j_helper.get_client()
    s = ('MATCH (a:B {id:"%s"})-[]-(c)-[]-(b:B {id:"%s"}) '
         'RETURN a, b, c'
         '' % (rest_id1, rest_id2))
    id2seq = {}
    nodes = {}
    edges = []
    for data in client.run(s).data():
        seq_a = update_nodes(data['a'], id2seq, nodes)
        seq_b = update_nodes(data['b'], id2seq, nodes)
        seq_c = update_nodes(data['c'], id2seq, nodes)

        edges.append((seq_a, seq_c))
        edges.append((seq_c, seq_b))

    return nodes, edges
