#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest

import requests
from selenium import webdriver

from unicodeutil import UnicodeBlocks, UnicodeData


base_url = "http://localhost:5000/"
ucd_url = base_url + "unicodeutil/ucd/"
ucd = UnicodeData()
unicode_blocks = UnicodeBlocks()


def get_http_response(url):
    """
    Selenium does not provide a way to get the raw HTTP response (e.g. the status
    code of 200: 0K, 404: Page not found is part of the response) so we need to
    use requests to get a HTTP response which we can use later to check for
    things like status codes, redirect history, etc.

    :param url: URL to load
    :returns: response object.
    """
    headers = {"Accept": "text/html"}
    return requests.get(url, headers=headers)


class TestUnicodeDataWebApp(unittest.TestCase):

    def setUp(self):
        self.browser = webdriver.Chrome()

    def tearDown(self):
        self.browser.quit()

    def test_redirect(self):
        """Test for ensuring that going to '/' redirects to the the app url."""
        self.browser.get(base_url)
        self.assertEqual(ucd_url, self.browser.current_url)
        r = get_http_response(base_url)
        self.assertEqual(200, r.status_code)
        self.assertEqual(302, r.history[0].status_code)

    def test_lookup_by_value(self):
        """Test for verifying that looking up by value works."""
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
        """Test for verifying that name lookup succeeds."""
        search_name = "T-REX"
        self.browser.get(ucd_url)
        search_text_input = self.browser.find_element_by_id("search_text_input")
        search_text_input.send_keys(search_name)
        use_partial_name = self.browser.find_element_by_id("use_partial_name")
        if use_partial_name.is_selected():
            use_partial_name.click()
        lookup_by_name = self.browser.find_element_by_id("lookup_by_name")
        lookup_by_name.click()
        page_title = self.browser.find_element_by_id("page_title")
        self.assertTrue(search_name in page_title.text)
        char_data = ucd.lookup_by_name(search_name)
        for attr in ['code', 'name']:
            expected = getattr(char_data, attr)
            actual = self.browser.find_element_by_id("char_data_value_{0}".format(attr)).text
            self.assertEqual(expected, actual)

    def test_lookup_by_partial_name(self):
        """Test for verifying that lookup by partial name succeeds."""
        search_text = "LATIN CAPITAL LETTER A"
        self.browser.get(ucd_url)
        search_text_input = self.browser.find_element_by_id("search_text_input")
        search_text_input.send_keys(search_text)
        use_partial_name = self.browser.find_element_by_id("use_partial_name")
        if not use_partial_name.is_selected():
            use_partial_name.click()
        lookup_by_name = self.browser.find_element_by_id("lookup_by_name")
        lookup_by_name.click()
        page_title = self.browser.find_element_by_id("page_title")
        self.assertTrue("partial name search" in page_title.text)
        search_input = self.browser.find_element_by_id("search_input")
        self.assertEqual(search_text, search_input.text)
        # Go through the table of results and verify that the search text is actually in each entry found.
        for name in self.browser.find_elements_by_xpath("//table[@id='table_matches']/tbody/tr/td[4]"):
            self.assertTrue(search_text in name.text)

    def test_lookup_non_existent_char(self):
        """Test for verifying that searching for a non-existent character by name produces the no char found page."""
        search_name = "non-existent name"
        expected_error_text = "ERROR - No character info found!"
        self.browser.get(ucd_url)
        search_text_input = self.browser.find_element_by_id("search_text_input")
        search_text_input.send_keys(search_name)
        use_partial_name = self.browser.find_element_by_id("use_partial_name")
        if use_partial_name.is_selected():
            use_partial_name.click()
        lookup_by_name = self.browser.find_element_by_id("lookup_by_name")
        lookup_by_name.click()
        self.assertEqual(expected_error_text, self.browser.title)
        page_title = self.browser.find_element_by_id("page_title")
        self.assertTrue(expected_error_text in page_title.text)

    def test_404(self):
        """Test for verifying that attempting to navigate to a non-existent page produces the 404 error page."""
        error_url = ucd_url + "non_existent_page.html"
        expected_error_text = "404 Error"
        self.browser.get(error_url)
        self.assertTrue(expected_error_text in self.browser.title)
        page_title = self.browser.find_element_by_id("page_title")
        self.assertTrue(expected_error_text in page_title.text)
        self.assertEqual(404, get_http_response(error_url).status_code)

    def test_load_blocks_page(self):
        """Test for verifying that navigating to the full list of Unicode blocks is working."""
        self.browser.get(ucd_url)
        unicode_blocks_link = self.browser.find_element_by_id("unicode_blocks_link")
        self.browser.get(unicode_blocks_link.get_attribute("href"))
        page_title = self.browser.find_element_by_id("page_title")
        self.assertEqual(u"Unicode® Blocks list", page_title.text)
        actual_block_names = self.browser.find_elements_by_xpath("//table[@id='block_list_table']/tbody/tr/td[3]")
        self.assertEqual(len(unicode_blocks.values()), len(actual_block_names))
        # Go through the table of results and verify the block names all match.
        for expected, actual in zip(unicode_blocks.values(), map(lambda x:x.text, actual_block_names)):
            self.assertEqual(expected, actual)

    def test_load_latin_extended_a_block_page(self):
        """Test for verifying that navigating to a Unicode block page is working."""
        block_name = "Latin Extended-A"  # We'll use Latin Extended-A for our test
        self.browser.get(ucd_url)
        unicode_blocks_link = self.browser.find_element_by_id("unicode_blocks_link")
        self.browser.get(unicode_blocks_link.get_attribute("href"))
        latin_extended_a = self.browser.find_element_by_link_text(block_name)
        latin_extended_a.click()
        self.assertTrue(block_name in self.browser.title)
        page_title = self.browser.find_element_by_id("page_title")
        self.assertTrue(block_name in page_title.text)
        actual_codes = self.browser.find_elements_by_xpath("//table[@id='char_list_table']/tbody/tr/td[1]")
        actual_names = self.browser.find_elements_by_xpath("//table[@id='char_list_table']/tbody/tr/td[3]")
        # Get the info about the Latin Extended-A block from the library and verify that the character info (code point
        # and name) for all the characters in the block match what is in the results table.
        for curr_range, curr_block_name in unicode_blocks.items():
            if curr_block_name == block_name:
                self.assertEqual(len(curr_range), len(actual_names))
                for index, code, name in zip(curr_range,
                                             map(lambda x:x.text, actual_codes),
                                             map(lambda x:x.text, actual_names)):
                    char_info = ucd[index]
                    self.assertEqual(char_info.code, code)
                    self.assertEqual(char_info.name, name)


if __name__ == "__main__":
    unittest.main()
