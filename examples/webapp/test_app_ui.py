#!/usr/bin/env python3

import unittest

from selenium import webdriver

from unicodeutil import UnicodeData


base_url = "http://localhost:5000/"
ucd_url = base_url + "unicodeutil/ucd/"
ucd = UnicodeData()


class TestUnicodeDataWebApp(unittest.TestCase):

    def setUp(self):
        self.browser = webdriver.Chrome()

    def tearDown(self):
        self.browser.quit()

    def test_redirect(self):
        self.browser.get(base_url)
        self.assertEqual(ucd_url, self.browser.current_url)

    def test_lookup_by_value(self):
        search_char = "D4DB"
        self.browser.get(ucd_url)
        search_text_input = self.browser.find_element_by_id("search_text_input")
        search_text_input.send_keys(search_char)
        lookup_by_value = self.browser.find_element_by_id("lookup_by_value")
        lookup_by_value.click()
        self.assertEqual(ucd_url + search_char, self.browser.current_url)
        page_title = self.browser.find_element_by_id("page_title")
        self.assertTrue("(U+{0})".format(search_char) in page_title.text)
        char_data = ucd[int(search_char, 16)]
        for attr in ['code', 'name']:
            expected = getattr(char_data, attr)
            actual = self.browser.find_element_by_id("char_data_value_{0}".format(attr)).text
            self.assertEqual(expected, actual)

    def test_lookup_by_name(self):
        search_name = "T-REX"
        self.browser.get(ucd_url)
        search_text_input = self.browser.find_element_by_id("search_text_input")
        search_text_input.send_keys(search_name)
        lookup_by_name = self.browser.find_element_by_id("lookup_by_name")
        lookup_by_name.click()
        page_title = self.browser.find_element_by_id("page_title")
        self.assertTrue(search_name in page_title.text)
        char_data = ucd.lookup_by_name(search_name)
        for attr in ['code', 'name']:
            expected = getattr(char_data, attr)
            actual = self.browser.find_element_by_id("char_data_value_{0}".format(attr)).text
            self.assertEqual(expected, actual)

    def test_lookup_404(self):
        search_name = "non-existent name"
        expected_error_text = "ERROR - No character info found!"
        self.browser.get(ucd_url)
        search_text_input = self.browser.find_element_by_id("search_text_input")
        search_text_input.send_keys(search_name)
        lookup_by_name = self.browser.find_element_by_id("lookup_by_name")
        lookup_by_name.click()
        self.assertEqual(expected_error_text, self.browser.title)
        page_title = self.browser.find_element_by_id("page_title")
        self.assertTrue(expected_error_text in page_title.text)


if __name__ == "__main__":
    unittest.main()
