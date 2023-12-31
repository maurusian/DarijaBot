import unittest
from unittest.mock import MagicMock
from top_initial_words import get_first_revision_text, remove_wiki_markup, extract_unique_words_darija, update_word_counts
import pywikibot

oldest_text = """
هنري أوحيون (مزيود ف 7 يونيو 1934 ف [[صفرو]]، توفى ف 27 أكتوبر 2023 ف أشكيلون، [[إسرائيل]])<ref>{{cite news
| title = אבל בעולם האופניים: הרוכב האולימפי הראשון של ישראל, הנרי אוחיון, הלך לעולמו
| url = https://www.israelhayom.co.il/sport/other-sports/article/14759439
| access-date = 28 October 2023
| publisher = Israel Hayom
| date = 28 October 2023
}}</ref> هوّ [[سباق د لپيكالات|پيكايلي]] إسرائيلي من أصول [[يهود مغاربا|يهودية مغريبية]].<ref>{{Cite web
| url = https://www.jta.org/archive/eighth-maccabiah-games-open-in-israel-among-festivities-memorial-observance
| title = Eighth Maccabiah Games Open in Israel Among Festivities, Memorial Observance
| access-date = 2023-11-21
}}</ref> كان تنافس ف [[لألعاب لؤلامپية د الصيف 1960]] ف السباق لفردي.<ref name="sports-reference2">{{cite web
| url = https://www.sports-reference.com/olympics/athletes/oh/henry-ohayon-1.html
| title = Henry Ohayon Olympic Results
| work = sports-reference.com
| archiveurl = https://web.archive.org/web/20131216211705/http://www.sports-reference.com/olympics/athletes/oh/henry-ohayon-1.html
| archivedate = 16 December 2013
| accessdate = 1 August 2014
| url-status = dead
| df = dmy-all
}}</ref>

== عيون لكلام ==
{{عيون}}
[[تصنيف:وفيات 2023]]
[[تصنيف:زيادة 1934]]
[[تصنيف:إسرائيل]]
[[تصنيف:يهود مغاربا ف لقرن 20]]
"""


oldest_text2 = """{{مقال_مهضور|Kamal Oudghiri.mp3|29 أكتوبر 2021|}}
{{معلومات شخص}}
'''كمال الودغيري''' (تزاد عام 1968 ف [[فاس]]) هو موهنديس تيصالات، عالم و باحت مغريبي خدام ف وكالة لفضاء [[الولايات المتاحدة د ميريكان|لميريكانية]] [[ناسا|نازا]]<ref name="ref1">{{Cite web
|url=https://www.moroccoworldnews.com/2012/08/50828/kamal-oudrhiri-a-moroccan-in-charge-of-monitoring-nasas-mission-to-mars-2
|title=Kamal Oudrhiri, a Moroccan in charge of Monitoring NASA’s Mission to Mars
|date=6 غشت 2012
|language=en
|archive-url=https://web.archive.org/web/20210413200331/https://www.moroccoworldnews.com/2012/08/50828/kamal-oudrhiri-a-moroccan-in-charge-of-monitoring-nasas-mission-to-mars-2/
|archive-date=13 أبريل 2021
}}</ref>"""

test_title =  "هنري أوحيون"

test_rev_id = 332852

test_user = 'Ideophagous'

class TestGetFirstRevisionText(unittest.TestCase):
    def setUp(self):
        # Mock the Pywikibot library functions used in get_first_revision_text
        pywikibot.Site = MagicMock()
        pywikibot.Page = MagicMock()

    def test_get_first_revision_text(self):
        # Set up a mock page and its first revision
        mock_page = MagicMock()
        mock_revision = MagicMock(revid=test_rev_id, user=test_user)
        mock_page.oldest_revision = mock_revision
        
        mock_page.getOldVersion = MagicMock(return_value=oldest_text)

        # Mock the Page object to return our mock page
        pywikibot.Page.return_value = mock_page

        # Call the function with a mock page title
        site = pywikibot.Site('ary', 'wikipedia')
        page = pywikibot.Page(site, test_title)
        result_text = get_first_revision_text(page)
        #print(result_text)

        # Assert that the results are as expected
        self.assertEqual(result_text, oldest_text)

        # Check if Pywikibot methods were called with correct parameters
        pywikibot.Site.assert_called_with('ary', 'wikipedia')
        pywikibot.Page.assert_called_with(pywikibot.Site.return_value, test_title)
        mock_page.getOldVersion.assert_called_with(test_rev_id)

    def test_remove_wiki_markup_with_categories(self):
        # Define the test Wiki text with categories
        wiki_text_with_categories = oldest_text
        
        # Expected output after removing markup and categories
        expected_output = """هنري أوحيون (مزيود ف 7 يونيو 1934 ف صفرو، توفى ف 27 أكتوبر 2023 ف أشكيلون، إسرائيل) هوّ پيكايلي إسرائيلي من أصول يهودية مغريبية. كان تنافس ف لألعاب لؤلامپية د الصيف 1960 ف السباق لفردي."""

        # Call the function to remove markup and categories
        cleaned_text = remove_wiki_markup(wiki_text_with_categories)

        #print(cleaned_text)

        # Remove any leading/trailing whitespace for comparison
        cleaned_text = cleaned_text.strip()
        expected_output = expected_output.strip()

        # Assert that the cleaned text matches the expected output
        self.assertEqual(cleaned_text, expected_output)

        #SECOND TEST
        # Define the test Wiki text with categories
        wiki_text_with_categories = oldest_text2
        
        # Expected output after removing markup and categories
        expected_output = "كمال الودغيري (تزاد عام 1968 ف فاس) هو موهنديس تيصالات، عالم و باحت مغريبي خدام ف وكالة لفضاء لميريكانية نازا"
        
        # Call the function to remove markup and categories
        cleaned_text = remove_wiki_markup(wiki_text_with_categories)

        #print(cleaned_text)

        # Remove any leading/trailing whitespace for comparison
        cleaned_text = cleaned_text.strip()
        expected_output = expected_output.strip()

        # Assert that the cleaned text matches the expected output
        self.assertEqual(cleaned_text, expected_output)

    def test_extract_unique_words_darija(self):
        # Define test cases
        test_cases = [
            ("هذا 123 اختبار بسيط", ["هذا", "اختبار", "بسيط"]),
            ("كلمة1 كلمة2, كلمة3! كلمة4.", ["كلمة"]),
            ("تجربة ڭديمة وݣديدة", ["تجربة", "ڭديمة", "وݣديدة"]),
            ("", []),
            ("كلمة كلمة كلمة", ["كلمة"])
        ]

        for text, expected in test_cases:
            with self.subTest(text=text):
                self.assertEqual(set(extract_unique_words_darija(text)), set(expected))

    def test_update_word_counts(self):
        word_structure = {}

        # User 1 enters some words
        word_structure = update_word_counts(word_structure, ["apple", "banana", "apple"], "user1")
        word_structure = update_word_counts(word_structure, ["banana", "orange"], "user1")

        # User 2 enters some words
        word_structure = update_word_counts(word_structure, ["banana", "orange"], "user2")
        word_structure = update_word_counts(word_structure, ["apple"], "user2")

        # User 3 enters some words
        word_structure = update_word_counts(word_structure, ["apple", "apple", "kiwi"], "user3")

        # Check overall structure
        expected_structure = {
            "apple": [{'user': 'user1', 'count': 2}, {'user': 'user2', 'count': 1}, {'user': 'user3', 'count': 2}],
            "banana": [{'user': 'user1', 'count': 2}, {'user': 'user2', 'count': 1}],
            "orange": [{'user': 'user1', 'count': 1}, {'user': 'user2', 'count': 1}],
            "kiwi": [{'user': 'user3', 'count': 1}]
        }

        self.assertEqual(word_structure, expected_structure)



# Run the test
unittest.main(argv=[''], exit=False)
