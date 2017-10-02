#!/usr/bin/python
# -*- encoding: utf8 -*-


__author__ = 'sheep'


#--- Solr settings ---
SOLR_HOST = ''
SOLR_PORT = None
SOLR_CORE = 'test'

#--- Mongodb settings ---
DB_HOST = ''
DB_PORT = None
DB_NAME = 'yelp_test'

BUSINESS_COLL = 'business'
USER_COLL = 'user'
REVIEW_COLL = 'review'
TIP_COLL = 'tip'
CHECKIN_COLL = 'checkin'
VECTOR_COLL = 'vector'

BUSINESS_FILE = 'res/small_dataset/yelp_academic_dataset_business.json'
INDEXING_FILE = 'res/small_dataset/yelp_academic_dataset_business_for_indexing.json'
USER_FILE = 'res/small_dataset/yelp_academic_dataset_user.json'
REVIEW_FILE = 'res/small_dataset/yelp_academic_dataset_review.json'
TIP_FILE = 'res/small_dataset/yelp_academic_dataset_tip.json'
CHECKIN_FILE = 'res/small_dataset/yelp_academic_dataset_checkin.json'

SEQ2ID_FILE = 'res/small_dataset/yelp_id_names.txt'
SEQ2VEC_FILE = 'res/small_dataset/yelp_id_vectors.txt'

#--- Neo4j settings
NEO4J_USER = 'neo4j'
NEO4J_PASSWORD = 'sheep1234'
NEO4J_HOST = '138.197.3.62'
NEO4J_HTTP_PORT = 7474
NEO4J_HTTPS_PORT = 7473
NEO4J_BOLT_PORT = 7687

BUSINESS_CLASS = 'B'
USER_CLASS = 'U'
CITY_CLASS = 'C'
CATEGORY_CLASS = 'L'

EDGE_CLASSES = {
    (BUSINESS_CLASS, USER_CLASS): 'BU', #business to user
    (USER_CLASS, BUSINESS_CLASS): 'UB', #user to business
    (USER_CLASS, USER_CLASS): 'UU', #user to user
    (BUSINESS_CLASS, CATEGORY_CLASS): 'BC', #business to category
    (CATEGORY_CLASS, BUSINESS_CLASS): 'CB', #category to business
    (BUSINESS_CLASS, CITY_CLASS): 'BL', #business to city
    (CITY_CLASS, BUSINESS_CLASS): 'CB', #city to business
}

GRAPH_FILE = 'res/small_dataset/graph.txt'
