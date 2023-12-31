import unittest
import re
from header_task import has_sources

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

# Running the tests
unittest.main(argv=[''], exit=False)
