#!/usr/bin/python
# -*- encoding: utf8 -*-

import optparse
import sys

import settings


__author__ = 'sheep'


def main():
    '''\
    %prog [options]
    '''
    with open(settings.INDEXING_FILE, 'w') as fo:
        fo.write('[\n')
        with open(settings.BUSINESS_FILE) as f:
            for line in f:
                fo.write('%s,\n' % (line.strip()))
        fo.write(']\n')

    return 0


if __name__ == '__main__':
    parser = optparse.OptionParser(usage=main.__doc__)
    options, args = parser.parse_args()

    if len(args) != 0:
        parser.print_help()
        sys.exit()

    sys.exit(main(*args))

