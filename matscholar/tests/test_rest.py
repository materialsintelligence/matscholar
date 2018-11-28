from matscholar import Rester
import unittest


class EmbeddingEngineTest(unittest.TestCase):

    def test_rester(self):
        r = Rester()
        self.assertIsNotNone(r.search({'material':['LiCoO2']}, limit=1))
