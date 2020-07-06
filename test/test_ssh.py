"""Unittest for papi.ssh.Ssh class"""
import unittest

class TestSsh(unittest.TestCase):

    def test_noop(self):
        self.assertEqual(True, True)


if __name__ == '__main__':
    unittest.main()