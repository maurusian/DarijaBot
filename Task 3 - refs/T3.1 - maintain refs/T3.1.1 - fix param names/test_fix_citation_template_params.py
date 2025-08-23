import unittest, re
from fix_citation_template_params import (
    extract_params,
    correct_param_keys,
    rebuild_template,
    fix_single_template,
    fix_single_citation_match,
    fix_citation_templates_in_text
)

class TestFixCitationHelpers(unittest.TestCase):
    maxDiff = None

    def test_extract_params(self):
        # 1. Basic key-value
        raw = "|titre=Hello|url=https://x.com|site=abc|consulté le=2024"
        expected_basic = {
            "titre": "Hello",
            "url": "https://x.com",
            "site": "abc",
            "consulté le": "2024"
        }
        self.assertEqual(extract_params(raw), expected_basic)

        # 2. Nested wikilink (pipe inside [[...]])
        raw_nested = "|title=موشحات مغربية|location=[[الدار البيضا|كازا]]|publisher=دار النشر المغربية|year=1973"
        expected_nested = {
            'title': 'موشحات مغربية',
            'location': '[[الدار البيضا|كازا]]',
            'publisher': 'دار النشر المغربية',
            'year': '1973'
        }
        self.assertEqual(extract_params(raw_nested), expected_nested)

        # 3. Template inside param (e.g., {{lang|ar|value}})
        raw_template = "|title={{lang|ar|موشحات}}|url=https://x.com"
        expected_template = {
            'title': '{{lang|ar|موشحات}}',
            'url': 'https://x.com'
        }
        self.assertEqual(extract_params(raw_template), expected_template)

        # 4. Param with no value
        raw_empty = "|title=Test|dead-url="
        expected_empty = {
            'title': 'Test',
            'dead-url': ''
        }
        self.assertEqual(extract_params(raw_empty), expected_empty)

        # 5. Value with multiple equal signs
        raw_equals = "|title=Example|quote=Key=value is used|access-date=2024"
        expected_equals = {
            'title': 'Example',
            'quote': 'Key=value is used',
            'access-date': '2024'
        }
        self.assertEqual(extract_params(raw_equals), expected_equals)


    
    def test_correct_param_keys(self):
        input_dict = {
            "titre": "Hello",
            "url": "https://x.com",
            "site": "abc",
            "consulté le": "2024",
            "unknown": "keep"
        }
        expected = {
            "title": "Hello",
            "url": "https://x.com",
            "website": "abc",
            "access-date": "2024",
            "unknown": "keep"
        }
        self.assertEqual(correct_param_keys(input_dict), expected)

    
    def test_rebuild_template(self):
        name = "lien web"
        params = {
            "title": "Hello",
            "url": "https://x.com",
            "website": "abc",
            "access-date": "2024"
        }
        expected = (
            "{{lien web\n"
            "|title=Hello\n"
            "|url=https://x.com\n"
            "|website=abc\n"
            "|access-date=2024\n"
            "}}"
        )
        self.assertEqual(rebuild_template(name, params), expected)
    

    def test_fix_single_template(self):
        template_name = "lien web"
        raw_param_text = "|titre=Example title|site=example.com|consulté le=2024"
        expected = (
            "{{lien web\n"
            "|title=Example title\n"
            "|website=example.com\n"
            "|access-date=2024\n"
            "}}"
        )
        result = fix_single_template(template_name, raw_param_text)
        self.assertEqual(result, expected)

    
    def test_fix_single_citation_match(self):
        text = "{{lien web|titre=Site Title|site=site.org|consulté le=2023}}"
        pattern = re.compile(
            r"\{\{(lien web)((?:\|[^{}]*)*)\}\}",
            re.IGNORECASE | re.DOTALL
        )
        match = pattern.search(text)

        expected = (
            "{{lien web\n"
            "|title=Site Title\n"
            "|website=site.org\n"
            "|access-date=2023\n"
            "}}"
        )

        self.assertIsNotNone(match, "Regex should match template.")
        result = fix_single_citation_match(match)
        self.assertEqual(result, expected)


    
    def test_fix_citation_templates_in_text(self):
        text = (
            "Text before.<ref>{{lien web|titre=Hello|url=https://x.com|site=abc|consulté le=2024}}</ref> Text after."
        )
        expected = (
            "Text before.<ref>{{lien web\n"
            "|title=Hello\n"
            "|url=https://x.com\n"
            "|website=abc\n"
            "|access-date=2024\n"
            "}}</ref> Text after."
        )
        self.assertEqual(fix_citation_templates_in_text(text), expected)
    #"""

if __name__ == "__main__":
    unittest.main()
