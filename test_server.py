from contextlib import redirect_stdout
from http import HTTPStatus
from http.server import ThreadingHTTPServer
import io
import json
import os
import threading
from types import SimpleNamespace
import unittest
from urllib.request import urlopen

from server import DEFAULT_MESSAGE, Handler, MESSAGE_ENV, message


class ConfigTests(unittest.TestCase):
    def test_default_message_is_hello_nas(self):
        self.assertEqual(message(), DEFAULT_MESSAGE)

    def test_message_can_come_from_env(self):
        os.environ[MESSAGE_ENV] = "Configured NAS"
        try:
            self.assertEqual(message(), "Configured NAS")
        finally:
            os.environ.pop(MESSAGE_ENV, None)


class HandlerUnitTests(unittest.TestCase):
    def test_canary_error_endpoint_returns_ok_without_error_log(self):
        payloads = []
        handler = SimpleNamespace(path="/canary-error", _send_json=payloads.append)
        stdout = io.StringIO()

        with redirect_stdout(stdout):
            Handler.do_GET(handler)

        self.assertEqual(payloads, [{"status": "ok"}])
        self.assertNotIn("ERROR", stdout.getvalue())


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
        self.assertFalse(payload["message_configured"])

    def test_handler_uses_http_ok(self):
        with urlopen(f"{self.base_url}/", timeout=2) as response:
            body = response.read().decode("utf-8")

        self.assertEqual(response.status, HTTPStatus.OK)
        self.assertIn(DEFAULT_MESSAGE, body)

    def test_canary_error_endpoint_is_ok(self):
        with urlopen(f"{self.base_url}/canary-error", timeout=2) as response:
            payload = json.loads(response.read())

        self.assertEqual(response.status, HTTPStatus.OK)
        self.assertEqual(payload["status"], "ok")


if __name__ == "__main__":
    unittest.main()
