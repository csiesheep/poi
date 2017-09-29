#!/usr/bin/python
# -*- encoding: utf8 -*-

import optparse
import sys

from db import graph_db_importer
from db.db_helper import Neo4j_helper


__author__ = 'sheep'


def main():
    '''\
    %prog [options]
    '''
    client = Neo4j_helper.get_client()
    graph_db_importer.show_statistics(client)
    return 0


if __name__ == '__main__':
    parser = optparse.OptionParser(usage=main.__doc__)
    options, args = parser.parse_args()

    if len(args) != 0:
        parser.print_help()
        sys.exit()

    sys.exit(main(*args))

