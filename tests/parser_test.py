import unittest
import sys
sys.path.append('../')
from parser_adapter import SumDict


class ParserTestCase(unittest.TestCase):
    def test_sum_dict(self):
        dic = {
            'a': {
                'b': [
                    'c',
                    {'d': 1, 'e': 2}
                ],
                'f': 3
            }
        }
        sd = SumDict(dic.items())
        result = sd.expand_dict()

        self.assertEqual(result['a.b.0'], 'c')
        self.assertEqual(result['a.b.1.e'], 2)
        self.assertEqual(result['a.b.1.d'], 1)
        self.assertEqual(result['a.f'], 3)


if __name__ == '__main__':
    unittest.main()
