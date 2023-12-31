import unittest
from pywikibot import Page, Site
from pywikibot.page import ItemPage

# Assuming the add_main_topic_to_cat function is defined in a script or module named 'your_script'
from add_main_topic import add_main_topic_to_cat, TEMPLATE_NAME

#TEMPLATE_NAME = "مقالة تصنيف"

class MockPage:
    def __init__(self, title, text):
        self.title_value = title
        self.text = text

    def title(self, with_ns=False):
        return self.title_value

class MockItemPage:
    def __init__(self, sitelinks):
        self.sitelinks = sitelinks

class TestAddMainTopicToCat(unittest.TestCase):
    def setUp(self):
        self.cat_page = MockPage("تصنيف:رومان قدام", "[[تصنيف:لإمبراطورية الرومانية]]\n[[تصنيف:روما]]")
        self.target_item = MockItemPage({'arywiki': 'رومان'})

    def test_add_main_topic_to_cat(self):
        updated_text = add_main_topic_to_cat(self.cat_page, self.target_item)
        expected_text = "{{مقالة تصنيف|رومان}}\n[[تصنيف:لإمبراطورية الرومانية]]\n[[تصنيف:روما]]"
        self.assertEqual(updated_text, expected_text)

if __name__ == '__main__':
    unittest.main()
