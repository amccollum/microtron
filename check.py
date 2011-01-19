#! /usr/bin/env python
# -*- coding: utf-8 -*-

""" util to check microformat data (not quite validation ;-) """

import lxml.etree, lxml.html
from optparse import OptionParser
import os
import pprint
import sys

from microtron import *

def parse(argv = None):
    if argv is None:
        argv = sys.argv

    parser = OptionParser('usage: %prog <url> <format>')
    parser.add_option("-s", "--strict",
                  action="store_true", dest="strict", default=False,
                  help="be strict about parsing")

    options, arguments = parser.parse_args(argv[1:])
    if len(arguments) != 2:
        parser.error('Incorrect number of arguments')

    url = arguments[0]
    format = arguments[1]

    tree = lxml.html.parse( url )
    parser = Parser( tree, strict=True, collect_errors=True )
    data = parser.parse_format(format) 
#    pprint.pprint(data)
    print "%d errors:" % (len( parser.errors ) )

    errs = parser.errors
    errs.sort(lambda x, y: cmp(x.sourceline,y.sourceline))
    for err in errs:
        print "ERROR (line %d): %s" % (err.sourceline, err)

    # TODO: extra checks for hnews:
    # - warn if dates insane (future, or distant past)
    # - updated but no published
    # - concatenated authors in single vcard ("Bob Smith and Fred Bloggs")
    # - insanity in content (eg adverts, scripts....)

if __name__ == '__main__':
    sys.exit(parse())
