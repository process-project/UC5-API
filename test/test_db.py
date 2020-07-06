"""Unittest for papi.db.DB class"""
import unittest

class TestDB(unittest.TestCase):

    def test_noop(self):
        self.assertEqual(True, True)


if __name__ == '__main__':
    unittest.main()