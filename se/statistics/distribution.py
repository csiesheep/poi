#!/usr/bin/python
# -*- encoding: utf8 -*-

from db.db_helper import mongodb_helper
import settings
import math

__author__ = 'sheep'

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
# Function: Earth radius in Km as constant
###################################################################
EARTH_RADIUS = 6378.137


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
def fetch_data(ids, key, data_type_flag):
    business_coll = mongodb_helper.get_coll(settings.BUSINESS_COLL)
    result_list = []
    if data_type_flag == GEO_COORDS:
        for id_ in ids:
            longitude = business_coll.find_one({'business_id': id_})[key[0]]
            latitude = business_coll.find_one({'business_id': id_})[key[1]]
            result = (longitude, latitude)
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


<<<<<<< HEAD
###################################################################
# Added By: Licheng
# Function Name: calc_geo_dist_distribution
# Description: Calculate geo distance distribution with input data
#              list
# Parameter: input_list - a list of geo coordinate data in form of
#                         tuples (longitude, latitude)
#            quantity - total number of items
# Return: a dictionary with geo distance distribution data
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
        s = 2 * math.asin(math.sqrt(math.pow(math.sin(delta_lat / 2), 2) +
                                    math.cos(target_lat_rad) * math.cos(store_lat_rad) *
                                    math.pow(math.sin(delta_long / 2), 2)))
        s *= EARTH_RADIUS
        s = round(s * 10000) / 10000
        if s not in result_dict:
            result_dict[item] = 1.0 / quantity
            continue
        result_dict[item] += 1.0 / quantity
    return result_dict


###################################################################
# Added By: Licheng
# Function Name: category_distribution
# Description: Distribution for store categories
# Parameter: ids - ids of stores
# Return: a sorted list of category distribution
###################################################################
def category_distribution(ids):
    data_list = fetch_data(ids, 'categories', DEFAULT)
    cat_dist = calc_distribution(data_list, len(ids))
    return sorted(cat_dist.items(), key=lambda x: x[1], reverse=True)


###################################################################
# Added By: Licheng
# Function Name: city_distribution
# Description: Distribution for city location
# Parameter: ids - ids of stores
# Return: a sorted list of city distribution
###################################################################
def city_distribution(ids):
    data_list = fetch_data(ids, 'city', DEFAULT)
    city_dist = calc_distribution(data_list, len(ids))
    return sorted(city_dist.items(), key=lambda x: x[1], reverse=True)


###################################################################
# Added By: Licheng
# Function Name: review_stars_distribution
# Description: Distribution for review stars
# Parameter: ids - ids of stores
# Return: a sorted list of star distribution
###################################################################
def review_stars_distribution(ids):
    data_list = fetch_data(ids, 'stars', DEFAULT)
    review_dist = calc_distribution(data_list, len(ids))
    return sorted(review_dist.items(), key=lambda x: x[1], reverse=True)


###################################################################
# Added By: Licheng
# Function Name: geo_distance_distribution
# Description: Distribution for distance with a target position
# Parameter: ids - ids of stores
#            target_coords - a tuple with form (longitude, latitude)
#                            which is a reference position like
#                            current position
# Function: Earth radius in Km as constant
###################################################################
def geo_distance_distribution(ids, target_coords):
    data_list = fetch_data(ids, ('longitude', 'latitude'), GEO_COORDS)
    geo_dist_dist = calc_geo_dist_distribution(data_list, len(ids), target_coords)
    return sorted(geo_dist_dist.items(), key=lambda x: x[1], reverse=True)

=======
def city_distribution(ids):
    business_coll = mongodb_helper.get_coll(settings.BUSINESS_COLL)
    city_dist = {}
    for id_ in ids:
        city = business_coll.find_one({'business_id': id_})['city']
        if city is None:
            continue

        if city not in city_dist:
            city_dist[city] = 1.0/len(ids)
            continue
        city_dist[city] += 1.0/len(ids)
    return sorted(city_dist.items(), key=lambda x:x[1], reverse=True)

#TODO
def keyword_distribution(ids):
    pass


#TODO
def pairwise_similarity_distribution(ids):
    pass


#TODO
def pairwise_co_customer_distribution(ids):
    pass
