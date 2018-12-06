from matscholar.utils import parse_word_expression
import unittest


class TestUtils(unittest.TestCase):

    def test_parse_word_expression(self):
        expressions = [
            "LiFePO4 - cathode + anode",
            "ab - bc + cd - df",
            "abdc",
            " - abc",
        ]

        parsed_expressions = [
            (["LiFePO4", "anode"], ["cathode"]),
            (["ab", "cd"], ["bc", "df"]),
            (["abdc"], []),
            ([], ["abc"])
        ]

        for e, pe in zip(expressions, parsed_expressions):
            parsed_expression = parse_word_expression(e)
            self.assertListEqual(parsed_expression[0], pe[0])
            self.assertListEqual(parsed_expression[1], pe[1])
