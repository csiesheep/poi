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

    def update_nodes(node, id2seq, nodes, on_path='inner'):
        id_, name, label = get_info(node)
        if id_ not in id2seq:
            seq = len(id2seq)+1
            id2seq[id_] = seq
            nodes[seq] = {'name': name,
                          'type': label,
                          'id': id_,
                          'on_path': on_path}
        return id2seq[id_]


    client = Neo4j_helper.get_client()

    id2seq = {}
    nodes = {}
    edges = set([])

    for kth in range(1, k+1):
        nodeString = '[]'
        returnString = ''
        c = list(string.ascii_lowercase)

        for i in range(kth):
            nodeString += ('-(%s)-[]' % c[i])
            returnString += (', %s' % c[i])
        s = ('MATCH (S:B {id:"%s"})-%s-(E:B {id:"%s"}) '
             'RETURN DISTINCT S, E%s'
             '' % (rest_id1, nodeString, rest_id2, returnString))

        for data in client.run(s).data():
            seq_S = update_nodes(data['S'],
                                 id2seq,
                                 nodes,
                                 on_path='source')
            seq_E = update_nodes(data['E'],
                                 id2seq,
                                 nodes,
                                 on_path='destination')
            seq_a = update_nodes(data['a'], id2seq, nodes)
            edges.add((seq_S, seq_a))
            if kth == 1:  # append edges to the end node if k = 1
                edges.add((seq_a, seq_E))
            i = 1
            while i < kth:
                seq_c1 = update_nodes(data[c[i-1]], id2seq, nodes)
                seq_c2 = update_nodes(data[c[i]], id2seq, nodes)
                edges.add((seq_c1, seq_c2))

                # append edge to next node if there is still nodes left
                if i+1 <kth:
                    seq_c3 = update_nodes(data[c[i+1]], id2seq, nodes)
                    edges.add((seq_c2, seq_c3))
                # append edge to end node if i is the last node
                else:
                    edges.add((seq_c2, seq_E))
                i += 2
                # append edge to end node if i+1 is the last node
                if i == k:
                    edges.add((seq_c3, seq_E))
    return nodes, edges

def get_meta_path_count(rest_id1, rest_id2, k):
    
    client = Neo4j_helper.get_client()
    meta_graph = {}
    Type = 'UCL'
    
    def set_path_count(T, N):
        query = ('MATCH path=(S:B {id:"%s"})-%s-(E:U {id:"%s"}) '
                 'RETURN DISTINCT count(path)'
                 '' % (rest_id1, N, rest_id2))
        num = graph.run(query).evaluate()
        T += ('B',)
        meta_graph[T] = num
        
    for kth in range(1, k+1):
        nodeString = '[]'
        typeString = ('B',)
        if kth == 2:
            nodeString += ('-(:U)-[]-(:U)-[]')
            typeString += ('U','U',)
            set_path_count(typeString, nodeString)
        else:
            for a in Type:
                nodeString = '[]'
                typeString = ('B',)
                typeString += (a,)
                nodeString += ('-(:%s)-[]' % a)
                if kth == 1:
                    set_path_count(typeString, nodeString)
                else:
                    if a == 'U':
                        nextType = 'BU'
                    else:
                        nextType = 'B'
                    temp_type_a = typeString
                    temp_node_a = nodeString
                    for b in nextType:
                        typeString = temp_type_a
                        nodeString = temp_node_a
                        typeString += (b,)
                        nodeString += ('-(:%s)-[]' % b)
                        temp_type_b = typeString
                        temp_node_b = nodeString
                        if kth != 4:
                            if b == 'B':
                                nextType = Type
                            else:
                                nextType = 'U'
                        else:
                            if b == 'B':
                                nextType = 'U'
                            else:
                                nextType = 'BU'
                        for c in nextType:
                            typeString = temp_type_b
                            nodeString = temp_node_b
                            typeString += (c,)
                            nodeString += ('-(:%s)-[]' % c)
                            if kth == 3:
                                set_path_count(typeString, nodeString)
                            else:
                                if kth == 4:
                                    if c == 'U':
                                        nextType = 'U'
                                    else:
                                        nextType = Type
                                else:
                                    if c == 'U':
                                        nextType = 'UB'
                                    else:
                                        nextType = 'U'
                                temp_node_c = nodeString
                                temp_type_c = typeString
                                for d in nextType:
                                    typeString = temp_type_c
                                    nodeString = temp_node_c
                                    typeString += (d,)
                                    nodeString += ('-(:%s)-[]' % d)
                                    if kth == 4:
                                        set_path_count(typeString, nodeString)
                                    else:
                                        if d == 'U':
                                            nextType = 'UB'
                                        else:
                                            nextType = Type
                                        temp_node_d = nodeString
                                        temp_type_d = typeString
                                        for e in nextType:
                                            typeString = temp_type_d
                                            nodeString = temp_node_d
                                            typeString += (e,)
                                            nodeString += ('-(:%s)-[]' % e)
                                            set_path_count(typeString, nodeString)

    return meta_graph

# get_meta_graph_count("YPavuOh2XsnRbLfl0DH2lQ","j8EHmuebLe8avjeFqrL0eg", 2)
