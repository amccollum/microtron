#! /usr/bin/env python
# -*- coding: utf-8 -*-

import lxml.etree, lxml.html
from optparse import OptionParser
import os
import pprint
import sys

from microtron import *

def parse(argv = None):
    if argv is None:
        argv = sys.argv

    parser = OptionParser('usage: %prog <file> mf.xml <format>')
    options, arguments = parser.parse_args(argv[1:])
    if len(arguments) != 3:
        parser.error('Incorrect number of arguments')
    source_filename = os.path.abspath(arguments[0])
    formats_filename = os.path.abspath(arguments[1])
    format = arguments[2]

    tree = lxml.html.parse(source_filename)
    formats = lxml.etree.parse(formats_filename)
    pprint.pprint(Parser(tree, formats).parse_format(format))

if __name__ == '__main__':
    sys.exit(parse())
