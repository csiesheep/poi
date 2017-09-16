#!/usr/bin/python
# -*- encoding: utf8 -*-

import json
import optparse
import sys

import settings


__author__ = 'sheep'


def main(output_fname):
    '''\
    %prog [options] <output_fname>
    '''
    ids = get_ids_with_vectors()
    print len(ids)

    with open(output_fname, 'w') as f:
        for line in get_business_edges(ids):
            f.write(line.encode('utf8'))

    bid2name = get_bid2name(ids)
    uid2name = get_uid2name(ids)
    with open(output_fname, 'a') as f:
        for line in get_business_user(ids, bid2name, uid2name):
            f.write(line.encode('utf8'))

    with open(output_fname, 'a') as f:
        for line in get_user_user(ids, uid2name):
            f.write(line.encode('utf8'))
    return 0

def get_business_edges(ids):
    '''
        return B-L and B-C
    '''
    print 'B-L and B-C...'
    with open(settings.BUSINESS_FILE) as f:
        for line in f:
            business = json.loads(line.strip())
            if business['business_id'] not in ids:
                continue
            bid = business['business_id']
            bname = business['name']
            if 'city' in business and business['city'] in ids:
                yield to_format(bid,
                                settings.BUSINESS_CLASS,
                                bname,
                                business['city'],
                                settings.CITY_CLASS,
                                business['city'])
            if ('categories' in business
                and business['categories'] is not None):
                for cat in business['categories']:
                    if cat in ids:
                        yield to_format(bid,
                                        settings.BUSINESS_CLASS,
                                        bname,
                                        cat,
                                        settings.CATEGORY_CLASS,
                                        cat)

def get_bid2name(ids):
    bid2name = {}
    with open(settings.BUSINESS_FILE) as f:
        for line in f:
            business = json.loads(line.strip())
            if business['business_id'] not in ids:
                continue
            bid2name[business['business_id']] = business['name']
    return bid2name

def get_uid2name(ids):
    uid2name = {}
    with open(settings.USER_FILE) as f:
        for line in f:
            user = json.loads(line.strip())
            if user['user_id'] is None:
                continue
            if user['user_id'] not in ids:
                continue
            uid2name[user['user_id']] = user['name']
    with open(settings.USER_FILE) as f:
        for line in f:
            user = json.loads(line.strip())
            for friend_id in user['friends']:
                if friend_id is None:
                    continue
                if friend_id not in ids:
                    continue
                if friend_id in uid2name:
                    continue
                uid2name[friend_id] = friend_id
    return uid2name

def get_business_user(ids, bid2name, uid2name):
    print 'B-U...'
    with open(settings.REVIEW_FILE) as f:
        for line in f:
            review = json.loads(line.strip())
            bid = review['business_id']
            uid = review['user_id']
            if bid not in bid2name or uid not in uid2name:
                continue
            yield to_format(bid,
                            settings.BUSINESS_CLASS,
                            bid2name[bid],
                            uid,
                            settings.USER_CLASS,
                            uid2name[uid])

def get_user_user(ids, uid2name):
    print 'U-U...'
    with open(settings.USER_FILE) as f:
        for line in f:
            user = json.loads(line.strip())
            uid = user['user_id']
            if uid not in uid2name:
                continue
            for fid in user['friends']:
                if fid is None:
                    continue
                if fid not in uid2name:
                    continue
                yield to_format(uid,
                                settings.USER_CLASS,
                                uid2name[uid],
                                fid,
                                settings.USER_CLASS,
                                uid2name[fid])

def to_format(from_id, from_class, from_name, to_id, to_class, to_name):
    return u'%s\t%s\t%s\t%s\t%s\t%s\n' % (from_id,
                                          from_class,
                                          from_name,
                                          to_id,
                                          to_class,
                                          to_name)

def get_ids_with_vectors():
#   bids = set()
#   cities = set()
#   categories = set()
#   with open(settings.BUSINESS_FILE) as f:
#       for line in f:
#           business = json.loads(line.strip())
#           bids.add(business['business_id'])
#           categories.extend(business['categories'])
#           cities.add(business['city'])
#   print 'business count:', len(bids)
#   print 'category count:', len(categories)
#   print 'city count:', len(cities)

    ids = set()
    with open(settings.SEQ2ID_FILE) as f:
        for line in f:
            _, id_ = line.strip().split('\t')
            ids.add(id_)
    return ids


if __name__ == '__main__':
    parser = optparse.OptionParser(usage=main.__doc__)
    options, args = parser.parse_args()

    if len(args) != 1:
        parser.print_help()
        sys.exit()

    sys.exit(main(*args))

