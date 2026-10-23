import unittest
from check_model_sunsets import scan

class ModelSunsetTests(unittest.TestCase):
    def test_exact_retired_snapshot(self):
        doc = {"nodes":[{"name":"LLM","parameters":{"model":"gpt-4o-2024-05-13"}}]}
        self.assertEqual(scan(doc)[0]["node"], "LLM")
        self.assertEqual(scan(doc)[0]["model"], "gpt-4o-2024-05-13")

    def test_nonretired_longer_snapshot_is_not_flagged(self):
        self.assertEqual([], scan({"model":"gpt-4-turbo-2024-04-09"}))

    def test_expression_reference(self):
        doc = {"nodes":[{"name":"Dynamic","parameters":{"model":"={{ $json.old || 'o4-mini-2025-04-16' }}"}}]}
        self.assertEqual(scan(doc)[0]["model"], "o4-mini-2025-04-16")

    def test_list_nested(self):
        doc = {"x":[{"name":"One","parameters":{"models":["gpt-3.5-turbo-0125","gpt-6-luna"]}}]}
        self.assertEqual(len(scan(doc)), 1)

    def test_malformed_top_level(self):
        with self.assertRaises(ValueError): scan([])

    def test_retired_fine_tune(self):
        self.assertEqual(scan({"params":{"model":"ft-o4-mini-2025-04-16"}})[0]["model"], "ft-o4-mini-2025-04-16")

if __name__ == "__main__":
    unittest.main()
