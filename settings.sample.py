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
BUSINESS_KEYWORD_COLL = 'business_keyword'
USER_COLL = 'user'
REVIEW_COLL = 'review'
TIP_COLL = 'tip'
CHECKIN_COLL = 'checkin'
#TODO refactor with SEQ2VEC_FILE
VECTOR_COLL = 'vector'
VECTOR_DEEPWALK_COLL = 'vector_deepwalk'
VECTOR_PTE_COLL = 'vector_pte'
VECTOR_ESIM_COLL = 'vector_esim'
#TODO
#VECTOR_LINE_COLL = 'vector_line'
#VECTOR_HINE_COLL = 'vector_hine'

BUSINESS_FILE = 'res/small_dataset/yelp_academic_dataset_business.json'
INDEXING_FILE = 'res/small_dataset/yelp_academic_dataset_business_for_indexing.json'
USER_FILE = 'res/small_dataset/yelp_academic_dataset_user.json'
REVIEW_FILE = 'res/small_dataset/yelp_academic_dataset_review.json'
TIP_FILE = 'res/small_dataset/yelp_academic_dataset_tip.json'
CHECKIN_FILE = 'res/small_dataset/yelp_academic_dataset_checkin.json'

SEQ2ID_FILE = 'res/small_dataset/yelp_id_names.txt'
SEQ2VEC_FILE = 'res/small_dataset/yelp_id_vectors.txt'
SEQ2VEC_DEEPWALK_FILE = 'res/small_dataset/yelp_id_vectors_DeepWalk.txt'
SEQ2VEC_PTE_FILE = 'res/small_dataset/yelp_id_vectors_PTE.txt'
SEQ2VEC_ESIM_FILE = 'res/small_dataset/yelp_id_vectors_ESim.txt'
#TODO
#SEQ2VEC_LINE_FILE = 'res/small_dataset/yelp_id_vectors.txt'
#SEQ2VEC_HINE_FILE = 'res/small_dataset/yelp_id_vectors.txt'

#--- Neo4j settings
NEO4J_USER = 'neo4j'
NEO4J_PASSWORD = ''
NEO4J_HOST = ''
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
