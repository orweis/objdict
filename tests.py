__author__ = 'OW'

import unittest
import objdict


class TestObjdict(unittest.TestCase):
    def test_recursive_access(self):
        o = objdict.Objdict()
        o.a.b.c = 1
        self.assertIsInstance(o.a, objdict.Objdict)
        self.assertIsInstance(o.a.b, objdict.Objdict)
        self.assertEqual(o.a.b.c, 1)

    def test_recursive_update(self):
        o = objdict.Objdict()
        o.a.b.c = 1
        o.update({"x": [1, 2, 3]})
        # Update doesn't damage preset value
        self.assertIsInstance(o.a, objdict.Objdict)
        self.assertIsInstance(o.a.b, objdict.Objdict)
        self.assertEqual(o.a.b.c, 1)
        # Update creates new entry
        self.assertEqual(o.x, [1, 2, 3])
        # Update appends to lists
        o.update({"x": [4]})
        self.assertEqual(o.x, [1, 2, 3, 4])

    def test_split(self):
        o = objdict.Objdict()
        # Fill with values
        o.a.b.c = 1
        o.d = "2"
        o.another_key = 6
        o.yet_another_key = []

        #Split into 3 groups - (a,d) , another_key and the rest
        dicts = o.split([("a", "d"), ("another_key",)])
        self.assertEqual(dicts[0].keys(), ["a","d"])
        self.assertEqual(dicts[1].keys(), ["another_key"])
        self.assertEqual(dicts[2].keys(), ["yet_another_key"])
        print dicts

if __name__ == '__main__':
    unittest.main()
