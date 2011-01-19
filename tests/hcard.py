#! /usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

import lxml.etree, lxml.html
from microtron import *
import datetime, os


class TestHCard(unittest.TestCase):

    def setUp(self):
        dirname = os.path.abspath(os.path.dirname(__file__))
        source_filename = dirname + '/examples/hcard.html'
        formats_filename = dirname + '/../microtron/mf.xml'
        self.tree = lxml.html.parse(source_filename)
        self.formats = lxml.etree.parse(formats_filename)
        self.parser = Parser(self.tree, self.formats)

    def test_hcard(self):
        result = self.parser.parse_format('hcard')
        self.assertEqual(len(result), 1)
        
        for prop_name in ('fn', 'org', 'geo', 'tel', 'url'):
            self.assertTrue(prop_name in result[0])

        self.assertEqual(result[0]['fn'], u'Mairie du 14\xe8me')


class TestHCard2(unittest.TestCase):

    def setUp(self):
        dirname = os.path.abspath(os.path.dirname(__file__))
        source_filename = dirname + '/examples/hcard2.html'
        formats_filename = dirname + '/../microtron/mf.xml'
        self.tree = lxml.html.parse(source_filename)
        self.formats = lxml.etree.parse(formats_filename)
        self.parser = Parser(self.tree, self.formats)

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

    def test_hcard2(self):
        result = self.parser.parse_format('hcard')
        
        expected = [{
            'adr': [{
                'country-name': 'United Kingdom',
                'locality': 'Neath',
                'postal-code': 'SA11 1PB',
                'region': 'West Glamorgan',
                'street-address': ['20 Brookdale Street'],
                'type': ['home']}],
            'bday': {
                'date': datetime.date(1982, 4, 9),
                'text': '9th April, 1982'},
            'email': [{
                'href': 'mailto:mail@jdclark.org',
                'mailto': 'mail@jdclark.org',
                'text': 'mail@jdclark.org'}],
            'fn': 'Jordan Daniel Clark',
            'geo': {
                'latitude': '51.65731',
                'longitude': '-3.80727'},
            'n': {
                'additional-name': ['Daniel'],
                'family-name': ['Clark'],
                'given-name': ['Jordan']},
            'tel': [{
                'type': ['home'],
                'value': '01639 765466'}],
            'url': [{
                'href': 'http://www.jdclark.org/',
                'text': 'www.jdclark.org'}]}]
        
        self.assertSubsetEqual(result, expected)


if __name__ == '__main__':
    unittest.main()
