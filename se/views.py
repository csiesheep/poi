from django.shortcuts import render
from django.http import HttpResponse
import pysolr
#from pymongo import MongoClient

from db.db_helper import mongodb_helper
from db import graph_db, graph_db_k
from se.similarity import knn
import settings
from se.statistics import distribution

# for plotting graphs
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
import plotly.graph_objs as go
import networkx as nx


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

    # set node position
    count_user = 0.0
    count_business = 0.0
    for node in G.nodes():
        if G.node[node]["type"] in [settings.USER_CLASS, settings.CITY_CLASS]:
            G.node[node]["pos"] = [0.5, 0 + count_user / n_users]
            count_user += 1
        else:
            G.node[node]["pos"] = [0 + count_business, 0.5]
            count_business += 1
    G.add_edges_from(edges)

    return G

def draw_network(G):
    pos=nx.get_node_attributes(G,'pos')

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
        x0, y0 = G.node[edge[0]]['pos']
        x1, y1 = G.node[edge[1]]['pos']
        edge_trace['x'] += [x0, x1, None]
        edge_trace['y'] += [y0, y1, None]

    node_trace = go.Scatter(
            x=[],
            y=[],
            text=[],
	    mode='markers',
	    hoverinfo='text',
	    marker=go.Marker(
		# colorscale options
		# 'Greys' | 'Greens' | 'Bluered' | 'Hot' | 'Picnic' | 'Portland' |
		# Jet' | 'RdBu' | 'Blackbody' | 'Earth' | 'Electric' | 'YIOrRd' | 'YIGnBu'
		color = [],
		reversescale=True,
		size=20,
		line=dict(width=2)))

    for node in G.nodes():
        x, y = G.node[node]['pos']
        node_trace['x'].append(x)
        node_trace['y'].append(y)	
        node_trace['text'].append(G.node[node]['name'])
	if G.node[node]['type'] == settings.BUSINESS_CLASS:
            node_trace['marker']['color'].append(-1)
        else:
            node_trace['marker']['color'].append(1)

    fig = go.Figure(data=go.Data([edge_trace, node_trace]),
		     layout=go.Layout(
		        title='Co-consumer Graph',
		        titlefont=dict(size=16),
		        showlegend=False,
		        hovermode='closest',
		        margin=dict(b=20,l=5,r=5,t=40),
		        annotations=[ dict(
		            showarrow=False,
		            xref="paper", yref="paper",
		            x=0.005, y=-0.002 ) ],
		        xaxis=go.XAxis(showgrid=False, zeroline=False, showticklabels=False),
		        yaxis=go.YAxis(showgrid=False, zeroline=False, showticklabels=False)))

    return plot(fig, output_type = "div")

def detail(request, rest_id):
    business_coll = mongodb_helper.get_coll(settings.BUSINESS_COLL)
    rest_info = business_coll.find_one({'business_id': rest_id})
    vector_coll = mongodb_helper.get_coll(settings.VECTOR_COLL)
    rest_vec = vector_coll.find_one({'id': rest_id})

    similarity_types = [['euclidean', 'Euclidean distance', False],
                        ['manhattan', 'Manhattan distance', False],
                        ['inner', 'Inner product', False],
#                       ['sigmoid', 'Sigmoid of inner product', False],
                        ['cosine', 'Cosine', False]]
    selected_sim_type = request.GET.get('similarity', 'euclidean')
    for s in similarity_types:
        if s[0] == selected_sim_type:
            s[2] = True
            break

    knn_ids = [id_ for _, id_ in knn.get_knn(selected_sim_type, rest_id)]
    knn_infos = [business_coll.find_one({'business_id': id_})
                 for id_ in knn_ids]

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

    barchart_cat = plot(barchart_data, output_type = "div")

    piechart_data = [go.Pie(labels = [row[0] for row in knn_cat_dist],
                     values = [row[1] for row in knn_cat_dist]
    )]

    piechart_cat = plot(piechart_data, output_type = "div")

    city = rest_info['city']
    knn_city_dist = []
    for c, score in distribution.city_distribution(knn_ids):
        if c == city:
            knn_city_dist.append((c, score, True))
            continue
        knn_city_dist.append((c, score, False))
    barchart_data = [go.Bar(x = [row[0] for row in knn_city_dist],
			    y = [row[1] for row in knn_city_dist]
    )]

    barchart_city = plot(barchart_data, output_type = "div")

    piechart_data = [go.Pie(labels = [row[0] for row in knn_city_dist], 
			    values = [row[1] for row in knn_city_dist]
    )]

    piechart_city = plot(piechart_data, output_type = "div")

    # network generation
    rest_id1 = rest_info['business_id']
    rest_id2 = knn_ids[0]
    nodes, edges = graph_db_k.get_paths(rest_id1, rest_id2, 2)
    print nodes, edges
#   edges = [(1,2), (3,2), (1,4), (3,4)]
#   nodes = {1: {"name": "McDonald's", "type": "business"},
#            2: {"name": "Jack",       "type": "user"},
#            3: {"name": "Burger King","type": "business"},
#            4: {"name": "Anthony",    "type": "user"}}
    
    if len(nodes) == 0:
        network_div = ''
    else:
        G = create_network(nodes, edges)
        network_div = draw_network(G)

    return render(request, 'rest.html', {'rest_info':        rest_info,
                                         'rest_vec':         rest_vec,
                                         'knn_infos':        knn_infos,
                                         'knn_cat_dist':     knn_cat_dist,
					 'barchart_cat':     barchart_cat,
					 'piechart_cat':     piechart_cat,
                                         'knn_city_dist':    knn_city_dist,
					 'barchart_city':    barchart_city,
					 'piechart_city':    piechart_city,
					 'network_div':      network_div,
					 'similarity_types': similarity_types})
