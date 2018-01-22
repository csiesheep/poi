#!/usr/bin/python
# -*- encoding: utf8 -*-

from db.db_helper import Neo4j_helper
import string


__author__ = 'sheep','Liuxuan Huang'

def get_local_network(rest_id1, k):
    def get_info(node):
        for label in node.labels():
            break
        return node['id'], node['name'], label

    def update_nodes(node, id2seq, nodes, on_path='inner'):
        id_, name, label = get_info(node)
        if id_ not in id2seq:
            seq = len(id2seq)+1
            id2seq[id_] = seq
            nodes[seq] = {'id': id_,
                          'type': label}
        return id2seq[id_]


    client = Neo4j_helper.get_client()

    id2seq = {}
    nodes = {}
    edges = set([])

    for kth in range(1, k+1):
        nodeString = ''
        returnString = ''
        c = list(string.ascii_lowercase)

        for i in range(kth):
            nodeString += ('-[]-(%s)' % c[i])
            returnString += (', %s' % c[i])

        s = ('MATCH (S:B {id:"%s"})%s'
             'RETURN DISTINCT S%s'
             '' % (rest_id1, nodeString, returnString))

        for data in client.run(s).data():
            seq_S = update_nodes(data['S'],
                                 id2seq,
                                 nodes,)
            seq_a = update_nodes(data['a'], id2seq, nodes)
            edges.add((seq_S, seq_a))

            if (kth > 1):
	            i = 1
	            while i < kth:
	                seq_c1 = update_nodes(data[c[i-1]], id2seq, nodes)
	                seq_c2 = update_nodes(data[c[i]], id2seq, nodes)
	                edges.add((seq_c1, seq_c2))

	                if i+1 < kth:
	                    seq_c3 = update_nodes(data[c[i+1]], id2seq, nodes)
	                    edges.add((seq_c2, seq_c3))
	                i += 2

    return nodes, edges

#get_local_network("YPavuOh2XsnRbLfl0DH2lQ", 3)
