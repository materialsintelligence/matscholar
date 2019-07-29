import unittest
from matscholar.collect import ScopusCollector

class MatScholarCollectTest(unittest.TestCase):

    def setUp(self):

        self.sc = ScopusCollector()

        self.results_1 = "We measured 100 materials, including Ni(CO)4 and obtained very " \
                          "high Thermoelectric Figures of merit ZT. These results demonstrate " \
                          "the utility of Machine Learning methods for materials discovery."
        self.sentence_2 = "iron(II) was oxidized to obtain 5mg Ferrous Oxide"

    def test_tokenize(self):

        # test data
        sentences = [self.sentence_1] * 2 + [self.sentence_2] * 2
        split_oxidation = [True, False, True, False]
        keep_sentences = [True, False, True, False]

        # results
        tokens = [
            ["We measured 100 materials , including Ni(CO)4 and obtained very "
             "high Thermoelectric Figures of merit ZT .".split(),
             "These results demonstrate the utility of Machine Learning methods "
             "for materials discovery .".split()],
            "We measured 100 materials , including Ni(CO)4 and obtained very "
            "high Thermoelectric Figures of merit ZT . These results demonstrate "
            "the utility of Machine Learning methods for materials discovery .".split(),
            ["iron (II) was oxidized to obtain 5 mg Ferrous Oxide".split()],
            "iron(II) was oxidized to obtain 5 mg Ferrous Oxide".split(),
        ]

        # running the tests
        for sent, toks, so, ks in zip(sentences, tokens, split_oxidation, keep_sentences):
            self.assertListEqual(self.msp.tokenize(sent, split_oxidation=so, keep_sentences=ks), toks)