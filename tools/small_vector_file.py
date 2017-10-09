#!/usr/bin/python
# -*- encoding: utf8 -*-

import sys
import optparse


__author__ = 'sheep'


def main(fname, output_fname, id_fname):
    '''\
    %prog [options] <fname> <output_fname> <id_fname>
    '''
    seq_ids = get_seq_ids(id_fname)
    print len(seq_ids)
    with open(output_fname, 'w') as fo:
        with open(fname) as fi:
            for line in fi:
                line.strip()
                seq_id, _ = line.strip().split(' ', 1)
                if seq_id not in seq_ids:
                    continue
                fo.write(line)

    return 0

def get_seq_ids(id_fname):
    seq_ids = set()
    with open(id_fname) as f:
        for line in f:
            seq, _ = line.strip().split('\t')
            seq_ids.add(seq)
    return seq_ids


if __name__ == '__main__':
    parser = optparse.OptionParser(usage=main.__doc__)
    options, args = parser.parse_args()

    if len(args) != 3:
        parser.print_help()
        sys.exit()

    sys.exit(main(*args))

