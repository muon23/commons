import unittest

import numpy as np

from work.npc.ai.utilities.CosineIndexer import CosineIndexer


class MyTestCase(unittest.TestCase):
    def test_something(self):
        a = CosineIndexer(np.array([1, 0, 0]))
        a.add(np.array([[0, 2, 0], [0, 0, -1]]))
        a.add(np.array([-3, 0, 0]))
        a.show()

        halfPi = np.pi/2
        expected = np.array([
            [0, halfPi, halfPi, np.pi],
            [halfPi, 0, halfPi, halfPi],
            [halfPi, halfPi, 0, halfPi],
            [np.pi, halfPi, halfPi, 0]
        ])

        self.assertTrue(np.allclose(a.angles, expected))

        print("======")
        a.add(np.array([[2, 2, 0], [2, 3, 0]]))
        a.show()

        found = a.find(np.array([1, 1, 0]), 2)
        print(f"{found} from {a.lastSearchSpace}")

        found = a.find(np.array([1, 0.1, 0]), 2, accurate=True)
        print(f"{found} from {a.lastSearchSpace}")


if __name__ == '__main__':
    unittest.main()
