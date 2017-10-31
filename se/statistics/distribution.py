#!/usr/bin/python
# -*- encoding: utf8 -*-

from db.db_helper import mongodb_helper
import settings
import math
import re, string
from nltk.stem import PorterStemmer
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction import FeatureHasher
from se import views_helper



__author__ = 'sheep', 'Licheng Jiang', 'Dan Colom'

###################################################################
# NOTICE:
#   To run this file, be sure to install nltk with:
#       $ sudo pip install -U nltk
#       $ sudo pip intsall -U numpy
#       $ pip install -U scikit-learn
#       $ sudo pip install scipy
#   Then in python shell type:
#       import nltk
#       nltk.download('stopwords')
#       nltk.download('punkt')
###################################################################

###################################################################
# Added By: Licheng
# Description: Flag of data type
# Function: Indicating type of data taken from database
###################################################################
DEFAULT = 0
GEO_COORDS = 1

###################################################################
# Added By: Licheng
# Description: Earth Radius
# Function: Earth radius in km as constant
###################################################################
EARTH_RADIUS = 6371

BUSINESS_KEYWORD_COLL = 'business_keyword'


###################################################################
# Added By: Licheng
# Function Name: fetch_data
# Description: Fetch data collection from database
# Parameter: ids - ids of stores
#            key - the name of item to fetch, string for default
#                  tuple of string ('longitude', 'latitude') for
#                  GEO_COORDS flag
#            data_type_flag - a flag to indicate what data to fetch
#                             1. DEFAULT
#                             2. GEO_COORDS
# Return: a list of fetched data
###################################################################
# TO DO: add test for NONE result
# business_coll.find_one({'business_id': id_})[key] May return
# error if no result match given id
###################################################################
def fetch_business_data(ids, key, data_type_flag):
    business_coll = mongodb_helper.get_coll(settings.BUSINESS_COLL)
    result_list = []
    if data_type_flag == GEO_COORDS:
        for id_ in ids:
            longitude = business_coll.find_one({'business_id': id_})[key[0]]
            latitude = business_coll.find_one({'business_id': id_})[key[1]]
            result = (longitude, latitude, id_)
            if result is None:
                continue
            result_list.append(result)
    else:
        for id_ in ids:
            result = business_coll.find_one({'business_id': id_})[key]
            if result is None:
                continue

            if isinstance(result, list):
                for item in result:
                    result_list.append(item)
            else:
                result_list.append(result)
    return result_list


###################################################################
# Added By: Licheng
# Function Name: calc_distribution
# Description: Calculate default distribution with input data list
# Parameter: input_list - a list of default data
#            quantity - total number of items
# Return: a dictionary with distribution data
###################################################################
def calc_distribution(input_list, quantity):
    result_dict = {}
    for item in input_list:
        if item not in result_dict:
            result_dict[item] = 1.0/quantity
            continue
        result_dict[item] += 1.0/quantity
    return result_dict


###################################################################
# Added By: Licheng
# Function Name: calc_geo_dist_distribution
# Description: Calculate geo distance distribution with input data
#              list
# Parameter: input_list - a list of geo coordinate data in form of
#                         tuples (longitude, latitude, business_id)
#            quantity - total number of items
# Return: a dictionary with form business: distance to target
#         unit: km
###################################################################
def calc_geo_dist_distribution(input_list, quantity, target_coords):
    result_dict = {}
    target_long_rad = math.radians(target_coords[0])
    target_lat_rad = math.radians(target_coords[1])
    for item in input_list:
        store_long_rad = math.radians(item[0])
        store_lat_rad = math.radians(item[1])
        delta_long = target_long_rad - store_long_rad
        delta_lat = target_lat_rad - store_lat_rad
        a = math.pow(math.sin(delta_lat/2), 2) + \
            math.cos(target_lat_rad) * math.cos(store_lat_rad) * math.pow(math.sin(delta_long/2), 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        d = EARTH_RADIUS * c
        if d not in result_dict:
            result_dict[item[2]] = d
    return result_dict


###################################################################
# Added By: Licheng
# Function Name: category_distribution
# Description: Distribution for store categories
# Parameter: ids - ids of stores
# Return: a sorted list of category distribution
###################################################################
def category_distribution(ids):
    data_list = fetch_business_data(ids, 'categories', DEFAULT)
    cat_dist = calc_distribution(data_list, len(ids))
    return sorted(cat_dist.items(), key=lambda x: x[1], reverse=True)  # PASS TEST

def keyword_distribution(ids):
    keywords = []
    for id_ in ids:
        keywords.extend(views_helper.get_keywords(id_))
    cat_dist = calc_distribution(keywords, len(ids))
    return sorted(cat_dist.items(), key=lambda x: x[1], reverse=True)  # PASS TEST

###################################################################
# Added By: Licheng
# Function Name: city_distribution
# Description: Distribution for city location
# Parameter: ids - ids of stores
# Return: a sorted list of city distribution
###################################################################
def city_distribution(ids):
    data_list = fetch_business_data(ids, 'city', DEFAULT)
    city_dist = calc_distribution(data_list, len(ids))
    return sorted(city_dist.items(), key=lambda x: x[1], reverse=True)  # PASS TEST


###################################################################
# Added By: Licheng
# Function Name: review_stars_distribution
# Description: Distribution for review stars
# Parameter: ids - ids of stores
# Return: a sorted list of star distribution
###################################################################
def review_stars_distribution(ids):
    data_list = fetch_business_data(ids, 'stars', DEFAULT)
    review_dist = calc_distribution(data_list, len(ids))
    return sorted(review_dist.items(), key=lambda x: x[1], reverse=True)  # PASS TEST


###################################################################
# Added By: Licheng
# Function Name: geo_distance_distribution
# Description: Distribution for distance with a target position
# Parameter: ids - ids of stores
#            target_id - id of the target store, which is a string
# Return: a sorted list of distance to target in km
###################################################################
def geo_distance_distribution(ids, target_id):
    data_list = fetch_business_data(ids, ('longitude', 'latitude'), GEO_COORDS)
    target_coords = fetch_business_data([target_id], ('longitude', 'latitude'), GEO_COORDS)[0]
    geo_dist_dist = calc_geo_dist_distribution(data_list, len(ids), target_coords)
    return sorted(geo_dist_dist.items(), key=lambda x: x[1], reverse=True)  # PASS TEST


###################################################################
# Added By: Licheng
# Function Name: extract_review_text
# Description: Extract all related review text to given id
#              from REVIEW_COLL
# Parameter: ids - ids of stores
# Return: a dictionary with business as id and list of all related
#         review as value
###################################################################
def extract_review_text(ids):
    review_coll = mongodb_helper.get_coll(settings.REVIEW_COLL)
    result_dict = {}
    for id_ in ids:
        review_text_list = []
        result = review_coll.find({'business_id': id_})
        for record in result:
            original_text = record['text']
            #processed_text = preprocess_review_text(original_text)
            #review_text_list.append(processed_text)
            review_text_list.append(original_text)
        result_dict[id_] = review_text_list
    return result_dict


def extract_all_review():
    review_coll = mongodb_helper.get_coll(settings.REVIEW_COLL)
    a = review_coll.find({})
    text_lists = []
    for record in a:
        text_lists.append(record['text'])
    return text_lists


###################################################################
# Added By: Licheng
# Function Name: preprocess_review_text
# Description: Process all raw review text with steps:
#              1. eliminate all punctuations
#              2. translate into lower case
#              3. tokenize the text
#              4. stemming the text
#              5. filter the stop words
#              6. assemble processed token into processed text
#                 string
# Parameter: review_text - raw review text get from database
# Return: a string of processed text
###################################################################
def preprocess_review_text(review_text):
    result_text_list = []
    result_text = ""
    # Eliminate punctuation
    regex = re.compile('[%s]' % re.escape(string.punctuation))
    pure_text = regex.sub('', review_text)
    # Translate into lowercase
    lower_text = pure_text.lower()
    # Tokenize text
    tokenized_text = word_tokenize(lower_text)
    # Stemming text
    ps = PorterStemmer()
    for word in tokenized_text:
        stemmed_word = ps.stem(word)
        # Filter stopwords
        if stemmed_word not in stopwords.words('english'):
            result_text_list.append(stemmed_word)
            result_text += stemmed_word
            result_text += " "
    return result_text


###################################################################
# Added By: Licheng
# Function Name: keyword_distribution_single_business
# Description: calculate keyword TFIDF score
# Parameter: id - a single business id
#            processed_text - a preprocessed text string
# Return: a sorted list with (keyword, TFIDF score) as element
###################################################################
def keyword_distribution_single_business(text):
    vectorizer = CountVectorizer()
    x = vectorizer.fit_transform(text)
    words = vectorizer.get_feature_names()
    counts = x.toarray()

    transformer = TfidfTransformer(smooth_idf=False)
    tfidf = transformer.fit_transform(counts)
    scores = tfidf.toarray()

    return (words, counts, scores)


###################################################################
# Added By: Dan Colom
# Modified By: Licheng Jiang
# Function Name: get_top_keywords
# Description: get the top k keywords for a business
#              based on TFIDF scores
# Parameter: dist - list of keywords distributions
# 			 k - integer number of top keywords to return
# Return: top_k - sorted list of top k keywords and their frequency
###################################################################
def get_top_keywords(dist, k):
    top_k = []
    for iter in range(k):
        word = dist[iter][0]
        top_k.append(word)
    return top_k


def get_top_keywords_single_review(k, review_text, word_count_score_tuple, all_text):
    words = word_count_score_tuple[0]
    counts = word_count_score_tuple[1]
    scores = word_count_score_tuple[2]
    tfidf_dict = {}
    index = all_text.index(review_text)
    for i in range(len(words)):
        if counts[index][i] != 0:
            tfidf_dict[words[i]] = scores[index][i]
    score_result = sorted(tfidf_dict.items(), key=lambda x: x[1], reverse=True)
    return get_top_keywords(score_result, k)


def top_keywords_single_business_auxiliary(id, k, word_count_score_tuple, all_text):
    group_list = []
    merged_list = []
    candidate_list = []
    id_keyword_dist = {}
    processed_dict = extract_review_text([id])
    review_num = len(processed_dict[id])
    for i in range(len(processed_dict[id])):
        review_top_k = get_top_keywords_single_review(k, processed_dict[id][i], word_count_score_tuple, all_text)
        merged_list += review_top_k
        group_list.append(review_top_k)

    for keyword in merged_list:
        if keyword not in candidate_list and candidate_list.count(keyword) > 1:
            candidate_list.append(keyword)
    if len(candidate_list) == 0:
        for i in range(k):  # if all words are unique, return random top-k keywords by default
            id_keyword_dist[merged_list[i]] = 1 * 1.0 / review_num
    elif len(candidate_list) < k:
        for keyword in candidate_list:
            id_keyword_dist[keyword] = merged_list.count(keyword) * 1.0 / review_num
        for i in range(k - len(candidate_list)):
            for keyword in merged_list:
                if keyword not in candidate_list and keyword not in id_keyword_dist.keys():
                    id_keyword_dist[keyword] = 1.0 / review_num
                    break
    else:
        for i in range(k):
            for keyword in candidate_list:
                if keyword not in id_keyword_dist.keys():
                    id_keyword_dist[keyword] = merged_list.count(keyword) * 1.0 / review_num
                    break
    db_writer(id, id_keyword_dist)
    return id_keyword_dist


def get_top_keywords_single_business(id, k, word_count_score_tuple, all_text):
    id_keyword_dist = top_keywords_single_business_auxiliary(id, k, word_count_score_tuple, all_text)
    return id_keyword_dist.keys()


def independent_get_top_keywords_single_business(id, k):
    all_text = extract_all_review()
    word_count_score_tuple = keyword_distribution_single_business(all_text)
    id_keyword_dist = top_keywords_single_business_auxiliary(id, k, word_count_score_tuple, all_text)
    return id_keyword_dist.keys()


def db_writer(id, keyword_dict):
    client = mongodb_helper.get_client()
    business_keyword_coll = client[settings.DB_NAME][BUSINESS_KEYWORD_COLL]
    keywords_dict_list = []
    keywords_list = keyword_dict.keys()
    keywords_score_list = keyword_dict.values()
    for i in range(len(keywords_list)):
        keywords_dict_list.append({'word':keywords_list[i], 'weight':keywords_score_list[i]})
    data = {'id': id, 'keywords':keywords_dict_list}
    business_keyword_coll.insert_one(data)



###################################################################
# Added By: Licheng
# Function Name: keyword_distribution
# Description: calculate keyword distribution based on the words
#              with highest DFIDF score for each business id
# Parameter: ids - a list of business id
# Return: a sorted dictionary with keyword as key and its frequency
#         in reviews of listed business ids
###################################################################
#ef keyword_distribution(ids, k):
#   group_list = []
#   merged_list = []
#   candidate_list = []
#   id_num = len(ids)
#   all_text = extract_all_review()
#   word_count_score_tuple = keyword_distribution_single_business(all_text)
#   keyword_dist = {}
#   for id_ in ids:
#       single_top_k = get_top_keywords_single_business(id_, k, word_count_score_tuple, all_text)
#       group_list.append(single_top_k)
#       merged_list += single_top_k
#   for keyword in merged_list:
#       if keyword not in candidate_list and candidate_list.count(keyword) > 1:
#           candidate_list.append(keyword)
#   if len(candidate_list) == 0:
#       for i in range(k):    # if all words are unique, return random top-k keywords by default
#           keyword_dist[merged_list[i]] = 1 * 1.0 / id_num
#   elif len(candidate_list) < k:
#       for keyword in candidate_list:
#           keyword_dist[keyword] = merged_list.count(keyword) * 1.0 / id_num
#       for i in range(k - len(candidate_list)):
#           for keyword in merged_list:
#               if keyword not in candidate_list and keyword not in keyword_dist.keys():
#                   keyword_dist[keyword] = 1.0 / id_num
#                   print keyword
#                   break
#   else:
#       for i in range(k):
#           for keyword in candidate_list:
#               if keyword not in keyword_dist.keys():
#                   keyword_dist[keyword] = merged_list.count(keyword) * 1.0 / id_num
#                   break
#   return sorted(keyword_dist.items(), key=lambda x: x[1], reverse=True)


#TODO
def pairwise_similarity_distribution(ids):
    pass


#TODO
def pairwise_co_customer_distribution(ids):
    pass


# TEST CASE
#print keyword_distribution(["cdk-qqJ71q6P7TJTww_DSA", "0DI8Dt2PJp07XkVvIElIcQ", "LTlCaCGZE14GuaUXUGbamg","EDqCEAGXVGCH4FJXgqtjqg", "Cu4_Fheh7IrzGiK-Pc79ig"], 10)
#print get_top_keywords_single_business("cdk-qqJ71q6P7TJTww_DSA", 5)
#print len(extract_all_review())
