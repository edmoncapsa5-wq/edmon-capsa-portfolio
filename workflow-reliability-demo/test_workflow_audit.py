import unittest
from workflow_audit import inspect

class StaticAuditTests(unittest.TestCase):
    def test_missing_target(self):
        w={"nodes":[{"name":"A","type":"n8n-nodes-base.webhook"}],"connections":{"A":{"main":[[{"node":"B"}]]}}}
        self.assertIn("DANGLING_CONNECTION", [x["code"] for x in inspect(w)])
    def test_unreachable_node(self):
        w={"nodes":[{"name":"A","type":"n8n-nodes-base.webhook"},{"name":"B","type":"n8n-nodes-base.set"}],"connections":{}}
        self.assertIn("NO_INCOMING_PATH", [x["code"] for x in inspect(w)])
    def test_duplicate_name(self):
        w={"nodes":[{"name":"A","type":"n8n-nodes-base.set"},{"name":"A","type":"n8n-nodes-base.set"}],"connections":{}}
        self.assertIn("DUPLICATE_NAME", [x["code"] for x in inspect(w)])
    def test_clean_path(self):
        w={"nodes":[{"name":"A","type":"n8n-nodes-base.webhook"},{"name":"B","type":"n8n-nodes-base.set"}],"connections":{"A":{"main":[[{"node":"B"}]]}}}
        self.assertEqual([], inspect(w))
    def test_risky_http_path(self):
        w={"nodes":[{"name":"A","type":"n8n-nodes-base.httpRequest","parameters":{}}],"connections":{}}
        self.assertIn("NETWORK_FAILURE_PATH_UNSPECIFIED", [x["code"] for x in inspect(w)])

if __name__ == "__main__":
    unittest.main()
