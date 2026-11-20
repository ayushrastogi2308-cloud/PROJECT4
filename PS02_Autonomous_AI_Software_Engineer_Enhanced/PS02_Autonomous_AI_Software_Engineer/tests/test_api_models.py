import unittest
from pydantic import ValidationError
from app.main import RunRequest

class RequestTests(unittest.TestCase):
    def test_valid_prompt(self):
        self.assertIn("calculator",RunRequest(prompt="Build a Python calculator").prompt)
    def test_short_prompt_rejected(self):
        with self.assertRaises(ValidationError): RunRequest(prompt="short")

if __name__=="__main__": unittest.main()
