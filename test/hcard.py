#! /usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

import lxml.etree, lxml.html
from microtron import *
import os


class TestHCard(unittest.TestCase):

    def setUp(self):
        dir = os.path.abspath(os.path.dirname(__file__))
        source_filename = dir + '/hcard.html'
        formats_filename = dir + '/../microtron/mf.xml'
        self.tree = lxml.html.parse(source_filename)
        self.formats = lxml.etree.parse(formats_filename)
        self.parser = Parser(self.tree, self.formats)

    def test_hcard(self):
        result = self.parser.parse_format('hcard')
        self.assertEqual(len(result), 1)
        self.assertTrue('fn' in result[0])
        self.assertTrue('org' in result[0])
        self.assertTrue('geo' in result[0])
        self.assertTrue('tel' in result[0])
        self.assertTrue('url' in result[0])
        self.assertEqual(result[0]['fn'], u'Mairie du 14\xe8me')

if __name__ == '__main__':
    unittest.main()
