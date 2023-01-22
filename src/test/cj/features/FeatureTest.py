import unittest

import numpy as np
import pandas as pd

from cj.features.CategoricalFeature import CategoricalFeature
from cj.features.ScalarFeature import ScalarFeature
from cj.features.VectorFeature import VectorFeature


class FeatureTest(unittest.TestCase):
    def test_scalar(self):
        df = pd.DataFrame(
            [[1, 2], [3, 4], [5, 6]], columns=["a", "b"]
        )

        with self.assertRaises(KeyError) as cm:
            ScalarFeature("x").extract(df)
        print(cm.exception)
        self.assertTrue(str(cm.exception).startswith("\"Some of"))

        cols = ["a", "b"]
        sf = ScalarFeature(cols, normalize=True)
        fa, fn = sf.extract(df)

        print(fa)
        faExpected = np.array([[
            [0, 0],
            [0.5, 0.5],
            [1, 1],
        ]])
        self.assertTrue(np.array_equal(fa, faExpected))
        self.assertEqual(fn, cols)

    def test_categorical(self):
        df = pd.DataFrame(
            [["xxx", 2], ['zzz', 4], ['xxx', 6], ["yyy", 10]], columns=["a", "b"]
        )
        print(df)

        cf = CategoricalFeature("a")
        fa, fn = cf.extract(df)

        print(fa)
        faExpected = np.array([[
            [1, 0, 0],
            [0, 0, 1],
            [1, 0, 0],
            [0, 1, 0],
        ]])
        self.assertTrue(np.array_equal(fa, faExpected))
        self.assertEqual(fn, ["a_xxx", "a_yyy", "a_zzz"])

    def test_vector(self):
        df = pd.DataFrame(
            [[[1, 2]], [[3, 4, 5]], [[5, 6]]], columns=["a"]
        )
        print(df)

        with self.assertRaises(KeyError) as cm:
            VectorFeature("b").extract(df)
        print(str(cm.exception))
        self.assertTrue(str(cm.exception).startswith("\"Column b is not in"))

        with self.assertRaises(ValueError) as cm:
            VectorFeature("a").extract(df)
        print(str(cm.exception))
        self.assertTrue(str(cm.exception).startswith("Vector sizes vary"))

        fa, fn = VectorFeature("a", padding=0).extract(df)
        print(fa)

        faExpected = np.array([[
            [1, 2, 0],
            [3, 4, 5],
            [5, 6, 0],
        ]])
        self.assertTrue(np.array_equal(fa, faExpected))

        fa, fn = VectorFeature("a", normalize="length", padding=0).extract(df, df)
        print(fa)
        for v in fa[0]:
            self.assertAlmostEqual(np.linalg.norm(v), 1.0)
        self.assertTrue(np.array_equal(fa[1], fa[0]))

        fa, fn = VectorFeature("a", normalize="column", padding=0).extract(df)
        print(fa)
        faExpected = np.array([[
            [0, 0, 0],
            [0.5, 0.5, 1],
            [1, 1, 0],
        ]])
        self.assertTrue(np.array_equal(fa, faExpected))

        fa, fn = VectorFeature("a", normalize="full", padding=0).extract(df)
        print(fa)
        self.assertEqual(fa[0, 0, 2], 0)
        self.assertEqual(fa[0, 2, 1], 1)


if __name__ == '__main__':
    unittest.main()
