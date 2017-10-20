#!/usr/bin/python
# -*- encoding: utf8 -*-

from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
import optparse
import re
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
import string
import sys

from db.db_helper import mongodb_helper
import settings


__author__ = 'sheep', 'Licheng', 'Dan Colom'


def main(k):
    '''\
    %prog [options] <k>
    '''
    k = int(k)

    bid2indexes, texts = extract_all_review()
    print 'Business count:', len(bid2indexes)
    print 'Review count:', len(texts)

    words, counts, tfidfs = compute_tfidf(texts)
    print 'Distinct word count:', len(words)
    seq2word = {}
    for seq, word in enumerate(words):
        seq2word[seq] = word

    coll = mongodb_helper.get_coll(settings.BUSINESS_KEYWORD_COLL)
    coll.drop()
    ith = 0
    for bid, indexes in bid2indexes.items():
        keywords = get_topk_keywords(k, indexes, tfidfs, seq2word)
        insert_db(bid, keywords)
        if ith % 100 == 0:
            print ith
        ith += 1
    coll.create_index('id')
    return 0

def insert_db(bid, keywords):
    coll = mongodb_helper.get_coll(settings.BUSINESS_KEYWORD_COLL)
    keywords_dict_list = []
    for word, score in keywords.items():
        keywords_dict_list.append({'word': word, 'score': score})
    data = {'id': bid, 'keywords':keywords_dict_list}
    coll.insert_one(data)

def get_topk_keywords_of_a_review(k, review_tfidfs, seq2word):
    keywords = []
    for _, seq in sorted([(s, seq)
                          for seq, s in enumerate(review_tfidfs)],
                         reverse=True)[:k]:
        keywords.append(seq2word[seq])
    return keywords

def get_topk_keywords(k, indexes, tfidfs, seq2word):
    keyword2count = {}
    for index in indexes:
        review_keywords = get_topk_keywords_of_a_review(k,
                                                        tfidfs[index],
                                                        seq2word)
        for keyword in review_keywords:
            if keyword not in keyword2count:
                keyword2count[keyword] = 1
                continue
            keyword2count[keyword] += 1
    keywords = dict([(k, float(count)/len(indexes))
                    for k, count in
                    sorted(keyword2count.items(),
                           key=lambda x: x[1],
                           reverse=True)[:k]])
    return keywords

def extract_all_review():
    review_coll = mongodb_helper.get_coll(settings.REVIEW_COLL)
    text_lists = []
    bid2indexes = {}
    index = 0
    for record in review_coll.find({}):
        text_lists.append(preprocess_review_text(record['text']))
        bid = record['business_id']
        if bid not in bid2indexes:
            bid2indexes[bid] = [index]
            continue
        bid2indexes[bid].append(index)
        index += 1
        if index % 1000 == 0:
            print index
    return bid2indexes, text_lists

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

def compute_tfidf(texts):
    vectorizer = CountVectorizer()
    x = vectorizer.fit_transform(texts)
    words = vectorizer.get_feature_names()
    counts = x.toarray()

    transformer = TfidfTransformer(smooth_idf=False)
    tfidf = transformer.fit_transform(counts)
    scores = tfidf.toarray()

    return (words, counts, scores)


if __name__ == '__main__':
    parser = optparse.OptionParser(usage=main.__doc__)
    options, args = parser.parse_args()

    if len(args) != 1:
        parser.print_help()
        sys.exit()

    sys.exit(main(*args))

