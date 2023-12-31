import unittest

def convert_dict(input_dict):
    result_dict = {}
    for key, value in input_dict.items():
        sub_dict = {}
        for entry in value:
            sub_dict[entry["user"]] = entry["count"]
        result_dict[key] = sub_dict
    return result_dict

class TestConvertDictFunction(unittest.TestCase):
    
    def test_empty_input_dict(self):
        input_dict = {}
        expected_output = {}
        self.assertEqual(convert_dict(input_dict), expected_output)

    def test_single_entry(self):
        input_dict = {
            "إنترنت": [
                {
                    "user": "anonymous",
                    "count": 1
                }
            ]
        }
        expected_output = {
            "إنترنت": {
                "anonymous": 1
            }
        }
        self.assertEqual(convert_dict(input_dict), expected_output)

    def test_multiple_entries(self):
        input_dict = {
            "إنترنت": [
                {
                    "user": "anonymous",
                    "count": 1
                },
                {
                    "user": "Tifratin",
                    "count": 2
                }
            ],
            "Python": [
                {
                    "user": "user1",
                    "count": 3
                }
            ]
        }
        expected_output = {
            "إنترنت": {
                "anonymous": 1,
                "Tifratin": 2
            },
            "Python": {
                "user1": 3
            }
        }
        self.assertEqual(convert_dict(input_dict), expected_output)

if __name__ == '__main__':
    unittest.main()
