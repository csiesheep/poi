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
from se.statistics import distribution



###################################################################
# Added By: Dan Colom
# Function Name: get_top_keywords
# Description: get the top k keywords for a business
#              based on TFIDF scores
# Parameter: dist - list of keywords distributions
#			 k - integer number of top keywords to return
# Return: top_k - sorted list of top k keywords and their frequency
###################################################################
def get_top_keywords(dist, k):
    top_k = []
    for _ in k:
        top_k.append(0)
    for iter in range(0, k-1):
        top_k[iter][0] = dist[iter]
    return top_k
