from django.shortcuts import render
from django.http import HttpResponse
import pysolr
#from pymongo import MongoClient

from db.db_helper import mongodb_helper
from se.similarity import knn
import settings
from se.statistics import distribution


__author__ = 'sheep'


def search(request):
    results = []
    if 'q' in request.GET:
        solr = pysolr.Solr('http://localhost:8983/solr/gettingstarted/',
                           timeout=10)
        keywords = request.GET['q']
        results = solr.search(keywords)

        vector_coll = mongodb_helper.get_coll(settings.VECTOR_COLL)
        filtered = []
        for r in results:
            if vector_coll.find_one({'id': r['business_id'][0]}) is not None:
                filtered.append(r)

    return render(request, 'se.html', {'rests': filtered})

def detail(request, rest_id):
    business_coll = mongodb_helper.get_coll(settings.BUSINESS_COLL)
    rest_info = business_coll.find_one({'business_id': rest_id})
    vector_coll = mongodb_helper.get_coll(settings.VECTOR_COLL)
    rest_vec = vector_coll.find_one({'id': rest_id})

    knn_ids = [id_ for _, id_ in knn.by_euclidean_distance(rest_id)]
    knn_infos = [business_coll.find_one({'business_id': id_})
                 for id_ in knn_ids]
    categories = rest_info['categories']
    knn_cat_dist = []
    for cat, score in distribution.category_distribution(knn_ids):
        if cat in categories:
            knn_cat_dist.append((cat, score, True))
            continue
        knn_cat_dist.append((cat, score, False))
    return render(request, 'rest.html', {'rest_info': rest_info,
                                         'rest_vec': rest_vec,
                                         'knn_infos': knn_infos,
                                         'knn_cat_dist': knn_cat_dist})
