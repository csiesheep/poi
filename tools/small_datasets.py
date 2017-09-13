#!/usr/bin/python
# -*- encoding: utf8 -*-

import json
import optparse
import os
import sys

import settings


__author__ = 'sheep'


def main(output_folder, k):
    '''\
    %prog [options] <output_folder> <k>
    '''
    os.system('rm -r %s' % output_folder)
    os.mkdir(output_folder)

    k = int(k)
    bids = sample_businesses(output_folder, k)
    uids = sample_yelp_others(bids, output_folder)
    sample_vectors(bids, uids, output_folder)
    return 0

def sample_vectors(bids, uids, output_folder):
    seq_ids = set()
    fname = os.path.basename(settings.SEQ2ID_FILE)
    with open(os.path.join(output_folder, fname), 'w') as fo:
        with open(settings.SEQ2ID_FILE) as f:
            for line in f:
                seq_id, id_ = line.strip().split('\t')
                if id_ not in bids and id_ not in uids:
                    continue
                fo.write(line)
                seq_ids.add(seq_id)
    print 'seq_id count:', len(seq_ids)

    fname = os.path.basename(settings.SEQ2VEC_FILE)
    count = 0
    with open(os.path.join(output_folder, fname), 'w') as fo:
        with open(settings.SEQ2VEC_FILE) as f:
            for line in f:
                seq_id, _ = line.strip().split(' ', 1)
                if seq_id not in seq_ids:
                    continue
                fo.write(line)
                count += 1
    print 'vector count:', count

def sample_businesses(output_folder, k):
    ids = set()
    with open(settings.SEQ2ID_FILE) as f:
        for line in f:
            _, id_ = line.strip().split('\t')
            ids.add(id_)

    selected_ids = set()
    business_fname = os.path.basename(settings.BUSINESS_FILE)
    with open(os.path.join(output_folder, business_fname), 'w') as fo:
        with open(settings.BUSINESS_FILE) as f:
            for line in f:
                business = json.loads(line.strip())
                if not business['business_id'] in ids:
                    continue
                selected_ids.add(business['business_id'])
                fo.write(line)
                if len(selected_ids) == k:
                    break
    print 'business count:', len(selected_ids)
    return selected_ids

def sample_yelp_others(bids, output_folder):
    checkin_fname = os.path.basename(settings.CHECKIN_FILE)
    count = 0
    with open(os.path.join(output_folder, checkin_fname), 'w') as fo:
        with open(settings.CHECKIN_FILE) as f:
            for line in f:
                checkin = json.loads(line.strip())
                if checkin['business_id'] not in bids:
                    continue
                fo.write(line)
                count += 1
    print 'checkin count:', count

    user_ids = set()
    review_fname = os.path.basename(settings.REVIEW_FILE)
    count = 0
    with open(os.path.join(output_folder, review_fname), 'w') as fo:
        with open(settings.REVIEW_FILE) as f:
            for line in f:
                review = json.loads(line.strip())
                if review['business_id'] not in bids:
                    continue
                fo.write(line)
                user_ids.add(review['user_id'])
                count += 1
    print 'review count:', count

    tip_fname = os.path.basename(settings.TIP_FILE)
    count = 0
    with open(os.path.join(output_folder, tip_fname), 'w') as fo:
        with open(settings.TIP_FILE) as f:
            for line in f:
                tip = json.loads(line.strip())
                if tip['business_id'] not in bids:
                    continue
                fo.write(line)
                user_ids.add(tip['user_id'])
                count += 1
    print 'tip count:', count

    user_fname = os.path.basename(settings.USER_FILE)
    count = 0
    with open(os.path.join(output_folder, user_fname), 'w') as fo:
        with open(settings.USER_FILE) as f:
            for line in f:
                user = json.loads(line.strip())
                if user['user_id'] not in user_ids:
                    continue
                fo.write(line)
                count += 1
    print 'user count:', count
    return user_ids


if __name__ == '__main__':
    parser = optparse.OptionParser(usage=main.__doc__)
    options, args = parser.parse_args()

    if len(args) != 2:
        parser.print_help()
        sys.exit()

    sys.exit(main(*args))

