#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import requests
import unittest

from unicodeutil import UnicodeData, casefold


base_url = "http://localhost:5000/unicodeutil/api/v1.0/"
headers = {"Content-Type": "application/json"}
ucd = UnicodeData()


class TestGetUnicodeData(unittest.TestCase):

    def test_get_name(self):
        test_value = 0x00DF
        resp = requests.get(base_url + "ucd/" + "0x%04x" % test_value, headers=headers)
        self.assertEqual(ucd[test_value].name, resp.json()['name'])


class TestCaseFold(unittest.TestCase):
    leading_trailing_quotes = re.compile(r'^"|"$')

    def test_default_casefold(self):
        input_string = u"WEIẞ"
        resp = requests.post(base_url + "casefold", json={"input_string": input_string})
        resp_str = self.leading_trailing_quotes.sub('', resp.content.strip().decode('unicode-escape'))
        self.assertEqual(casefold(input_string), resp_str)

    def test_simple_casefold(self):
        input_string = u"WEIẞ"
        resp = requests.post(base_url + "casefold", json={"input_string": input_string, "fullcasefold": False})
        resp_str = self.leading_trailing_quotes.sub('', resp.content.strip().decode('unicode-escape'))
        self.assertEqual(casefold(input_string, fullcasefold=False), resp_str)

    def test_full_casefold(self):
        input_string = u"WEIẞ"
        resp = requests.post(base_url + "casefold", json={"input_string": input_string, "fullcasefold": True})
        resp_str = self.leading_trailing_quotes.sub('', resp.content.strip().decode('unicode-escape'))
        self.assertEqual(casefold(input_string, fullcasefold=True), resp_str)

    def test_turkic_casefold(self):
        input_string = u"DİYARBAKIR"
        resp = requests.post(base_url + "casefold", json={"input_string": input_string})
        resp_str = self.leading_trailing_quotes.sub('', resp.content.strip().decode('unicode-escape'))
        self.assertEqual(casefold(input_string), resp_str)
        resp = requests.post(base_url + "casefold", json={"input_string": input_string, "useturkicmapping": True})
        resp_str = self.leading_trailing_quotes.sub('', resp.content.strip().decode('unicode-escape'))
        self.assertEqual(casefold(input_string, useturkicmapping=True), resp_str)


if __name__ == "__main__":
    unittest.main()
