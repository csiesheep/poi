#!/usr/bin/python
# -*- encoding: utf8 -*-

from db.db_helper import Neo4j_helper
import string

__author__ = 'sheep','Liuxuan Huang'


def get_paths(rest_id1, rest_id2, k):
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
    
    nodeString = '[]'
    returnString = ''
    c = list(string.ascii_lowercase) # get a list of lowercase alphabets
    
    # construct partial strings to query
    for i in range(k):
        nodeString += ('-(%s)-[]' % c[i])
        returnString += (', %s' % c[i])
        
    s = ('MATCH (S:B {id:"%s"})-%s-(E:B {id:"%s"}) '
         'RETURN S, E%s'
         '' % (rest_id1, nodeString, rest_id2, returnString))
    
    id2seq = {}
    nodes = {}
    edges = []
    i = 1
    for data in client.run(s).data():
        seq_S = update_nodes(data['S'], id2seq, nodes)
        seq_E = update_nodes(data['E'], id2seq, nodes)
        seq_a = update_nodes(data['a'], id2seq, nodes)
        edges.append((seq_S, seq_E))
        if k == 1:  # append edges to the end node if k = 1
            edges.append((seq_a, seq_E))
        while i < k:
            seq_c1 = update_nodes(data[c[i-1]], id2seq, nodes)
            seq_c2 = update_nodes(data[c[i]], id2seq, nodes)
            edges.append((seq_c1, seq_c2))
            if i+1 <k: # append edge to next node if there is still nodes left
                seq_c3 = update_nodes(data[c[i+1]], id2seq, nodes)
                edges.append((seq_c2, seq_c3))
            else: # append edge to end node if i is the last node
                edges.append((seq_c2, seq_E))
            i += 2
            if i == k: # append edge to end node if i+1 is the last node
                edges.append((seq_c3, seq_E))
    return nodes, edges