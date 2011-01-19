#! /usr/bin/env python
# -*- coding: utf-8 -*-


import unittest

import lxml.etree, lxml.html
from microtron import *
import datetime, os
from pprint import pprint
#import pytz

class TestHNews1(unittest.TestCase):

    def setUp(self):
        dirname = os.path.abspath(os.path.dirname(__file__))
        source_filename = dirname + '/hnews1.html'
        self.tree = lxml.html.parse(source_filename)
        self.parser = Parser(self.tree)

        
    def assertSubsetEqual(self, ob1, ob2):
        '''Test whether all the values in ob2 exist in ob1'''
        self.assert_(isinstance(ob1, type(ob2)), " -> type() differs: %s != %s" % (type(ob1), type(ob2)))
            
        if isinstance(ob2, list):
            self.assertEqual(len(ob1), len(ob2), " -> len() differs: %s != %s" % (len(ob1), len(ob2)))
                
            for i in xrange(len(ob2)):
                try:
                    self.assertSubsetEqual(ob1[i], ob2[i])
                except AssertionError, e:
                    raise AssertionError('[%s]%s' % (i, e.message))
    
        elif isinstance(ob2, dict):
            for k in ob2:
                try:
                    self.assertSubsetEqual(ob1[k], ob2[k])
                except AssertionError, e:
                    raise AssertionError('[%s]%s' % (k, e.message))

        else:
            self.assertEqual(ob1, ob2, " -> value differs: %r != %r" % (ob1, ob2))


    def test_hnews1(self):
        result = self.parser.parse_format('hnews')

        self.assertEqual(len(result), 1)
        expected = [{
            '__type__': 'hnews',
            'author': [{'__type__': 'vcard', 'fn': 'BEN FELLER'}],
            'entry-title': 'Renewing US ties with Latin America, Obama says he wants to lead, not lecture, on democracy',
            'source-org': {'__type__': 'vcard',
                 'fn': 'Associated Press',
                 'org': ['Associated Press']},
            'updated': {'date': datetime.datetime(2009, 4, 19, 18, 17, 29, 0, isodate.tzinfo.Utc()) }
        }]

        self.assertSubsetEqual( result, expected )

if __name__ == '__main__':
    unittest.main()
