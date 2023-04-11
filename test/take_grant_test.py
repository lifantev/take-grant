import unittest

class TestTG(unittest.TestCase):

    def test_upper(self):
        self.assertEqual('foo'.upper(), 'FOO')
    

if __name__ == '__main__':
    unittest.main()