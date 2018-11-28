from matscholar import Rester
import numpy.testing as npt
import unittest


class EmbeddingEngineTest(unittest.TestCase):
    r = Rester()

    def test_materials_search(self):

        top_thermoelectrics = self.r.materials_search("thermoelectric", top_k=10)

        self.assertListEqual(top_thermoelectrics["counts"], [2452, 9, 2598, 13, 5, 9, 831, 167, 8, 390])
        self.assertListEqual(top_thermoelectrics["materials"], ['Bi2Te3', 'MgAgSb', 'PbTe', 'PbSe0.5Te0.5',
                                                                'In0.25Co3FeSb12', '(Bi0.15Sb0.85)2Te3', 'CoSb3',
                                                                'Bi0.4Sb1.6Te3', 'CeFe3CoSb12', 'Bi0.5Sb1.5Te3'])
        self.assertEqual(top_thermoelectrics["original_wordphrase"], "thermoelectric")
        self.assertListEqual(top_thermoelectrics["sentence"], ['thermoelectric'])
        npt.assert_array_almost_equal(top_thermoelectrics["scores"], [0.19262796640396118, 0.13790667057037354,
                                                                      0.12772011756896973, 0.1259261965751648,
                                                                      0.12495005130767822, 0.12300053983926773,
                                                                      0.12144004553556442, 0.11942288279533386,
                                                                      0.11764131486415863, 0.11382885277271271])

    def test_close_words(self):

        zt_words = self.r.close_words("thermoelectric figure of merit", top_k=10)

        self.assertEqual(zt_words["original_wordphrase"], "thermoelectric figure of merit")
        self.assertListEqual(zt_words["sentence"], ['thermoelectric_figure_of_merit'])
        self.assertListEqual(
            zt_words["close_words"],
            ['ZT', 'figure_of_merit_ZT', 'thermoelectric_figure_of_merit_ZT', 'seebeck_coefficient', 'zT',
             'thermoelectric_figure_-_of_-_merit', 'thermoelectric_power_factor', 'ZT_value', 'ZT_values',
             'dimensionless_figure_of_merit'])

        npt.assert_array_almost_equal(
            zt_words["scores"],
            [0.865725, 0.862376, 0.849371, 0.847059, 0.843266, 0.835109, 0.831514, 0.82924, 0.825901, 0.822744])

    def test_mentioned_with(self):

        response_dict = self.r.mentioned_with(material="Te3Bi2", words=["thermoelectric", "solar_cell"])

        self.assertTrue(response_dict["mentioned_with"])
        self.assertEqual(response_dict["material"], "Te3Bi2")
        self.assertEqual(response_dict["words"], ["thermoelectric", "solar_cell"])

        response_dict = self.r.mentioned_with(material="Cu7Te5", words=["thermoelectric", "ZT"])

        self.assertFalse(response_dict["mentioned_with"])
        self.assertEqual(response_dict["material"], "Cu7Te5")
        self.assertEqual(response_dict["words"], ["thermoelectric", "ZT"])

