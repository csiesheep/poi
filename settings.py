#!/usr/bin/python
# -*- encoding: utf8 -*-


__author__ = 'sheep'


#--- Solr settings ---
SOLR_HOST = '138.197.3.62'
SOLR_PORT = 8983
SOLR_CORE = 'test'

#--- Mongodb settings ---
DB_HOST = '138.197.3.62'
DB_PORT = 27018
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

#--- Network settings ---
BUSINESS_CLASS = 'B'
USER_CLASS = 'U'
CITY_CLASS = 'C'
CATEGORY_CLASS = 'L'
