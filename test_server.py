from http import HTTPStatus
from http.server import ThreadingHTTPServer
import json
import threading
import unittest
from urllib.request import urlopen

from server import Handler, MESSAGE


class HandlerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base_url = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def test_health_payload(self):
        with urlopen(f"{self.base_url}/health", timeout=2) as response:
            payload = json.loads(response.read())

        self.assertEqual(response.status, HTTPStatus.OK)
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["service"], "hello-nas")

    def test_message_is_hello_nas(self):
        self.assertEqual(MESSAGE, "Hello NAS")

    def test_handler_uses_http_ok(self):
        with urlopen(f"{self.base_url}/", timeout=2) as response:
            body = response.read().decode("utf-8")

        self.assertEqual(response.status, HTTPStatus.OK)
        self.assertIn(MESSAGE, body)


if __name__ == "__main__":
    unittest.main()
