from django.shortcuts import render
from django.http import HttpResponse
import networkx as nx
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
import plotly.graph_objs as go
import pysolr

from db.db_helper import mongodb_helper
from db import graph_db
from se.similarity import knn
from se.similarity import co_customers
import settings
from se.statistics import distribution



__author__ = 'sheep'


def search(request):
    filtered = []
    if 'q' in request.GET:
        solr = pysolr.Solr('http://%s:%d/solr/%s/' % (settings.SOLR_HOST,
                                                      settings.SOLR_PORT,
                                                      settings.SOLR_CORE),
                           timeout=10)
        keywords = request.GET['q']
        results = solr.search(keywords, rows=1000)

        vector_coll = mongodb_helper.get_coll(settings.VECTOR_COLL)
        review_coll = mongodb_helper.get_coll(settings.REVIEW_COLL)
        for r in results:
            b_id = r['business_id'][0]
            if vector_coll.find_one({'id': b_id}) is not None:
                review_count = review_coll.count({'business_id': b_id})
                r['review_count'] = review_count
                filtered.append(r)

    return render(request, 'se.html', {'rests': filtered})

def create_network(nodes, edges):
    G = nx.Graph()
    n_users = 0 
    for node in nodes:
        G.add_node(node)
        for attribute in nodes[node]:
             G.node[node][attribute] = nodes[node][attribute]
        if G.node[node]["type"] != settings.BUSINESS_CLASS: n_users += 1

    G.add_edges_from(edges)

    return G

def draw_network(G):
    pos = nx.fruchterman_reingold_layout(G)
#   print pos

    dmin=1
    ncenter=0
    for n in pos:
        x,y=pos[n]
        d=(x-0.5)**2+(y-0.5)**2
        if d<dmin:
            ncenter=n
            dmin=d

    p=nx.single_source_shortest_path_length(G,ncenter)

    edge_trace = go.Scatter(
            x=[],
            y=[],
            line=go.Line(width=0.5,color='#888'),
            hoverinfo='none',
            mode='lines')

    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_trace['x'] += [x0, x1, None]
        edge_trace['y'] += [y0, y1, None]

    node_trace = go.Scatter(
            x=[],
            y=[],
            text=[],
            mode='markers',
            hoverinfo='text',
            marker=go.Marker(
            color = [],
            reversescale=True,
            size = [],
            line=dict(width=2)))

    node_types = [settings.BUSINESS_CLASS, settings.USER_CLASS, settings.CITY_CLASS, settings.CATEGORY_CLASS]
    node_path_roles = ["source", "destination", "inner"]
    for node in G.nodes():
        x, y = pos[node]
        node_trace['x'].append(x)
        node_trace['y'].append(y)
        node_trace['text'].append(G.node[node]['name'])
        node_trace['marker']['color'].append(node_types.index(G.node[node]['type']))
        if G.node[node]['on_path'] in ["source", "destination"]:
            node_trace['marker']['size'].append(30)
        else:
            node_trace['marker']['size'].append(20)

    fig = go.Figure(data=go.Data([edge_trace, node_trace]),
                    layout=go.Layout(
                        title='Sub-network between two restaurants',
                        titlefont=dict(size=16),
                        showlegend=False,
                        hovermode='closest',
                        margin=dict(b=20,l=5,r=5,t=40),
                        annotations=[ dict(
                            showarrow=False,
                            xref="paper", yref="paper",
                            x=0.005, y=-0.002 ) ],
                        xaxis=go.XAxis(showgrid=False,
                                       zeroline=False,
                                       showticklabels=False),
                        yaxis=go.YAxis(showgrid=False,
                                       zeroline=False,
                                       showticklabels=False)))
    return plot(fig, output_type = "div")

def detail(request, rest_id):
    business_coll = mongodb_helper.get_coll(settings.BUSINESS_COLL)
    rest_info = business_coll.find_one({'business_id': rest_id})
    vector_coll = mongodb_helper.get_coll(settings.VECTOR_COLL)
    rest_vec = vector_coll.find_one({'id': rest_id})

    # generate google map search string
    query = "https://www.google.com/maps/embed/v1/place?key=AIzaSyC0woDjDcggf1PhuX9POXxTO0F059_JpjU"
    query += "&q=" + "+".join(rest_info['address'].split(" "))
    query += "," + "+".join(rest_info['city'].split(" "))

    similarity_types = [['euclidean', 'Euclidean distance', False],
                        ['manhattan', 'Manhattan distance', False],
                        ['inner', 'Inner product', False],
                        ['cosine', 'Cosine', False]]
    selected_sim_type = request.GET.get('similarity', 'euclidean')
    for s in similarity_types:
        if s[0] == selected_sim_type:
            s[2] = True
            break

    approaches = [['hin2vec', 'HIN2Vec', False],
                  ['deepwalk', 'DeepWalk', False],
                  ['pte', 'PTE', False],
                  ['esim', 'Esim', False]]
    selected_approach = request.GET.get('approach', 'hin2vec')
    for s in approaches:
        if s[0] == selected_approach:
            s[2] = True
            break
    print selected_sim_type, selected_approach

    knn_result = knn.get_knn(selected_sim_type,
                             rest_id,
                             approach=selected_approach)
    knn_ids = [id_ for _, id_ in knn_result]
    knn_infos = [business_coll.find_one({'business_id': id_})
                 for id_ in knn_ids]
    for ith, b in enumerate(knn_infos):
        b['co_user_count'] = co_customers.get_number_com_customers(rest_id,
                                                          b['business_id'])
        b['co_user_ratio'] = co_customers.get_ratio_com_customers(rest_id,
                                                          b['business_id'])
        b['score'] = knn_result[ith][0]

    categories = rest_info['categories']
    knn_cat_dist = []
    for cat, score in distribution.category_distribution(knn_ids):
        if cat in categories:
            knn_cat_dist.append((cat, score, True))
            continue
        knn_cat_dist.append((cat, score, False))

    barchart_data = [go.Bar(x = [row[0] for row in knn_cat_dist],
                     y = [row[1] for row in knn_cat_dist]
    )]

    barchart_cat = plot(barchart_data, output_type = "div").replace("<div>", "<div style='height:500px'>")

    piechart_data_cat = [go.Pie(labels = [row[0] for row in knn_cat_dist],
                     values = [row[1] for row in knn_cat_dist]
    )]

    piechart_cat = plot(piechart_data_cat, output_type = "div").replace("<div>", "<div style='height:500px'>")

    city = rest_info['city']
    knn_city_dist = []
    for c, score in distribution.city_distribution(knn_ids):
        if c == city:
            knn_city_dist.append((c, score, True))
            continue
        knn_city_dist.append((c, score, False))
    barchart_data = [go.Bar(x = [row[0] for row in knn_city_dist],
                            y = [row[1] for row in knn_city_dist])]

    barchart_city = plot(barchart_data, output_type = "div").replace("<div>", "<div style='height:500px'>")
    f = open("tmp.html", "w")
    f.write(barchart_city)
    f.close()

    piechart_data = [go.Pie(labels = [row[0] for row in knn_city_dist],
                            values = [row[1] for row in knn_city_dist])]

    piechart_city = plot(piechart_data, output_type = "div").replace("<div>", "<div style='height:500px'>")

        
#   edges = [(1,2), (3,2), (1,4), (3,4)]
#   nodes = {1: {"name": "McDonald's", "type": "business"},
#            2: {"name": "Jack",       "type": "user"},
#            3: {"name": "Burger King","type": "business"},
#            4: {"name": "Anthony",    "type": "user"}}
    
    # network generation

    rest_id1 = rest_info['business_id']
    rest_id2 = knn_ids[int(request.GET.get('knn_business', 0))]
    meta_paths = graph_db.get_meta_path_count(rest_id1, rest_id2, 2)
    temp_ = []
    for mp, count in sorted(meta_paths.items(), key=lambda x: len(x[0])):
        temp_.append(('B-%s-B' % ('-'.join(mp)), count))
    meta_paths = temp_

    nodes, edges = graph_db.get_paths(rest_id1, rest_id2, 2)
    print nodes, edges

    if len(nodes) == 0:
        network_div = ''
    else:
        G = create_network(nodes, edges)
        network_div = draw_network(G)

    return render(request,
                  'rest.html',
                  {
                    'rest_info':        rest_info,
                    'rest_vec':         rest_vec,
 		    'query':            query,
                    'knn_infos':        knn_infos,
                    'knn_cat_dist':     knn_cat_dist,
                    'barchart_cat':     barchart_cat,
                    'piechart_data_cat':piechart_data_cat,
                    'piechart_cat':     piechart_cat,
                    'knn_city_dist':    knn_city_dist,
                    'barchart_city':    barchart_city,
                    'piechart_city':    piechart_city,
                    'network_div':      network_div,
                    'similarity_types': similarity_types,
                    'approaches':       approaches,
                    'meta_paths':       meta_paths,
                  })
