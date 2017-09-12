#!/usr/bin/python
# -*- encoding: utf8 -*-

from bson import json_util
import optparse
import sys

from db.db_helper import mongodb_helper
import settings


__author__ = 'sheep'


def main():
    '''\
    %prog [options] <folder>
    '''
#   mongodb_helper.drop_db()
#   import_yelp_data()
#   imoprt_vectors()
    indexing()
    return 0

def import_yelp_data():
    colls = [
        (settings.BUSINESS_COLL, settings.BUSINESS_FILE),
        (settings.USER_COLL, settings.USER_FILE),
        (settings.REVIEW_COLL, settings.REVIEW_FILE),
        (settings.TIP_COLL, settings.TIP_FILE),
        (settings.CHECKIN_COLL, settings.CHECKIN_FILE),
    ]
    for coll_name, fpath in colls:
        coll = mongodb_helper.get_coll(coll_name)
        for sub_dataset in load_dataset(fpath):
            coll.insert_many(sub_dataset)
        print coll_name, coll.count()

def load_dataset(fpath, k=1000):
    sub_dataset = []
    with open(fpath) as f:
        for line in f:
            sub_dataset.append(json_util.loads(line))
            if len(sub_dataset) % k == 0:
                yield sub_dataset
                sub_dataset = []
        if len(sub_dataset) > 0:
            yield sub_dataset

def imoprt_vectors():
    coll = mongodb_helper.get_coll(settings.VECTOR_COLL)
    for sub_vectors in load_vectors():
        coll.insert_many(sub_vectors)

def load_vectors(k=1000):
    '''
        return {type_: [(seq_id, yelp_id)]}
    '''
    seq2id = {}
    with open(settings.SEQ2ID_FILE) as f:
        for line in f:
            seq, id_ = line.strip().split('\t')
            seq2id[int(seq)] = id_

    type2fpath = [
        (settings.BUSINESS_COLL, settings.BUSSINESS_FILE, 'business_id'),
        (settings.USER_COLL, settings.USER_FILE, 'user_id'),
    ]
    #TODO refactor
    id2type = {
        'Tempe': 'city',
        'Las Vegas': 'city',
        'Toronto': 'city',
        'Scottsdale': 'city',
        'Henderson': 'city',
        'Phoenix': 'city',
        'Charlotte': 'city',
        'Mesa': 'city',
        'Pittsburgh': 'city',
        'Edinburgh': 'city',
    }
    for type_, fpath, key in type2fpath:
        for sub_dataset in load_dataset(fpath, k=1):
            id2type[sub_dataset[0][key]] = type_

    sub_vectors = []
    with open(settings.SEQ2VEC_FILE) as f:
        for line in f:
            tokens = line.strip().split(' ')
            seq = int(tokens[0])
            vec = map(float, tokens[1:])

            if seq not in seq2id:
                continue

            id_ = seq2id[seq]
            type_ = id2type.get(id_, 'category')

            data = {
                'id': id_,
                'seq': seq,
                'v': vec,
                'type': type_,
            }
            sub_vectors.append(data)
            if len(sub_vectors) % k == 0:
                yield sub_vectors
                sub_vectors = []
        if len(sub_vectors) > 0:
            yield sub_vectors

def indexing():
    business_coll = mongodb_helper.get_coll(settings.BUSINESS_COLL)
    business_coll.create_index("business_id")

    vector_coll = mongodb_helper.get_coll(settings.VECTOR_COLL)
    vector_coll.create_index("id")
    vector_coll.create_index("type")


if __name__ == '__main__':
    parser = optparse.OptionParser(usage=main.__doc__)
    options, args = parser.parse_args()

    if len(args) != 0:
        parser.print_help()
        sys.exit()

    sys.exit(main(*args))

