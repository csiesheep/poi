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

__author__ = 'sheep', 'Licheng Jiang'

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
            processed_text = preprocess_review_text(original_text)
            review_text_list.append(processed_text)
        result_dict[id_] = review_text_list
    return result_dict


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
def keyword_distribution_single_business(id, processed_text):
    vectorizer = TfidfVectorizer(min_df=1)
    vectorizer.fit_transform(processed_text)
    idf = vectorizer.idf_
    return sorted(dict(zip(vectorizer.get_feature_names(), idf)).items(), key=lambda x: x[1], reverse=True)


###################################################################
# Added By: Licheng
# Function Name: keyword_distribution
# Description: calculate keyword distribution based on the words
#              with highest DFIDF score for each business id
# Parameter: ids - a list of business id
# Return: a sorted dictionary with keyword as key and its frequency
#         in reviews of listed business ids
###################################################################
def keyword_distribution(ids):
    processed_dict = extract_review_text(ids)
    keyword_dist = {}
    for id_ in ids:
        word_score_list = keyword_distribution_single_business(id_, processed_dict[id_])
        for word_tuple in word_score_list:
            if word_tuple[1] == word_score_list[0][1]:
                if word_tuple[0] not in keyword_dist:
                    keyword_dist[word_tuple[0]] = 1.0/len(ids)
                    continue
                keyword_dist[word_tuple[0]] += 1.0/len(ids)
    return sorted(keyword_dist.items(), key=lambda x: x[1], reverse=True)


#TODO
def pairwise_similarity_distribution(ids):
    pass


#TODO
def pairwise_co_customer_distribution(ids):
    pass
