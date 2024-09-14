import unittest
import re
from header_task import has_sources, is_bot, is_created_by_bot, is_human_edits_sum_exceed_1000_bytes, is_human_pure_text_sum_exceed_1000_bytes, isBotArticle
from unittest.mock import MagicMock, patch
import pywikibot


site = pywikibot.Site()

# Defining the has_sources function
def has_sources(text):
    source_patterns = [r"<ref[^>]*>", r"\{\{[Ss]fn\|([^}|]+)(\|[^}|]+)*\}\}"] # Source and SFN patterns
    for pattern in source_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False

# Defining the unit test class for the has_sources function
class TestHasSourcesFunction(unittest.TestCase):

    def test_has_sources_with_ref_tag(self):
        text_with_ref = "Some text <ref>Reference</ref>"
        self.assertTrue(has_sources(text_with_ref))

    def test_has_sources_with_sfn_tag(self):
        text_with_sfn = "Some text {{Sfn|Author|Year|p=Page}}"
        self.assertTrue(has_sources(text_with_sfn))

    def test_has_sources_with_sfn_tag_case_insensitive(self):
        text_with_sfn_lower = "Some text {{sfn|Author|Year|p=Page}}"
        self.assertTrue(has_sources(text_with_sfn_lower))

    def test_has_sources_with_no_source_tags(self):
        text_without_sources = "Some text without any source tags."
        self.assertFalse(has_sources(text_without_sources))

    def test_has_sources_with_varied_sfn_parameters(self):
        text_with_varied_sfn = "Text with {{Sfn|Author}} and {{sfn|Author|Year}}"
        self.assertTrue(has_sources(text_with_varied_sfn))


class TestBotArticleFunctions(unittest.TestCase):
    
    def test_is_bot(self):
        # Provide a known bot and human user for testing
        self.assertTrue(is_bot('AmgharBot'))  # Replace with an actual bot username
        self.assertTrue(is_bot('BotFunast'))  # Replace with an actual bot username
        self.assertFalse(is_bot('Ideophagous'))  # Replace with an actual human username

    def test_is_created_by_bot(self):
        # Provide a page title that is known to be created by a bot
        page_title = 'أبادو (أيت سعدلي لوطا)'  # Replace with an actual page created by a bot
        page = pywikibot.Page(site, page_title)
        self.assertTrue(is_created_by_bot(page))

        # Provide a page title that is known to be created by a human
        page_title = 'سنوريات الشكل'  # Replace with an actual page created by a human
        page = pywikibot.Page(site, page_title)
        self.assertFalse(is_created_by_bot(page))

    def test_is_human_edits_sum_exceed_1000_bytes(self):
        # Provide a page title where human edits exceed 1000 bytes
        page_title = 'عوام 2000'  # Replace with an actual page where human edits exceed 1000 bytes
        page = pywikibot.Page(site, page_title)
        self.assertTrue(is_human_edits_sum_exceed_1000_bytes(page))

        # Provide a page title where human edits are less than 1000 bytes
        page_title = 'عوام 1990'  # Replace with an actual page where human edits are less than 1000 bytes
        page = pywikibot.Page(site, page_title)
        self.assertTrue(is_human_edits_sum_exceed_1000_bytes(page))

    def is_human_pure_text_sum_exceed_1000_bytes(self):
        # Provide a page title where pure text edits exceed 1000 bytes
        page_title = 'عوام 2000'  # Replace with an actual page where pure text edits exceed 1000 bytes
        page = pywikibot.Page(site, page_title)
        self.assertTrue(is_human_pure_text_sum_exceed_1000_bytes(page))

        # Provide a page title where pure text edits are less than 1000 bytes
        page_title = 'عوام 1990'  # Replace with an actual page where pure text edits are less than 1000 bytes
        page = pywikibot.Page(site, page_title)
        self.assertFalse(is_human_pure_text_sum_exceed_1000_bytes(page))

    def test_isBotArticle(self):
        # Provide a page title that is considered a bot article
        page_title = 'عوام 1970'  # Replace with an actual page considered a bot article
        page = pywikibot.Page(site, page_title)
        self.assertTrue(isBotArticle(page))

        # Provide a page title that is not considered a bot article
        page_title = 'عوام 2010'  # Replace with an actual page not considered a bot article
        page = pywikibot.Page(site, page_title)
        self.assertFalse(isBotArticle(page))

        # Provide a page title that is not considered a bot article
        page_title = 'شمال إفريقيا و الشرق لأوسط'  # Replace with an actual page not considered a bot article
        page = pywikibot.Page(site, page_title)
        self.assertFalse(isBotArticle(page))
# Running the tests
unittest.main(argv=[''], exit=False)
