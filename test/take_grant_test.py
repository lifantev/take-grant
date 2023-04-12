import unittest

from take_grant import *

class TestTG(unittest.TestCase):

    def test_upper(self):
        read_graph()
        self.assertEqual('foo'.upper(), 'FOO')
    

if __name__ == '__main__':
    unittest.main()