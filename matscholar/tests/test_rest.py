from matscholar import Rester
import numpy.testing as npt
import unittest
import numpy as np


class EmbeddingEngineTest(unittest.TestCase):
    r = Rester()

    def test_materials_search(self):

        top_thermoelectrics = self.r.materials_search("thermoelectric", top_k=10)

        self.assertListEqual(top_thermoelectrics["counts"], [2452, 9, 2598, 13, 5, 9, 831, 167, 8, 390])
        self.assertListEqual(top_thermoelectrics["materials"], ['Bi2Te3', 'MgAgSb', 'PbTe', 'PbSe0.5Te0.5',
                                                                'In0.25Co3FeSb12', '(Bi0.15Sb0.85)2Te3', 'CoSb3',
                                                                'Bi0.4Sb1.6Te3', 'CeFe3CoSb12', 'Bi0.5Sb1.5Te3'])
        self.assertEqual(top_thermoelectrics["original_positive"], "thermoelectric")
        self.assertEqual(top_thermoelectrics["original_negative"], "")
        npt.assert_array_almost_equal(top_thermoelectrics["scores"], [0.19262796640396118, 0.13790667057037354,
                                                                      0.12772011756896973, 0.1259261965751648,
                                                                      0.12495005130767822, 0.12300053983926773,
                                                                      0.12144004553556442, 0.11942288279533386,
                                                                      0.11764131486415863, 0.11382885277271271])
        self.assertListEqual(top_thermoelectrics["positive"], [['thermoelectric']])

    def test_close_words(self):

        # test data
        positives = ["thermoelectric figure of merit", "Piezoelectric asdasdfasasd", "thermoelectric,Perovskite"]
        negatives = [None, "Perovskite", "anode,cathode"]
        top_ks = [10, 5, 5]
        ignore_missing = [False, True, True]

        # expected response
        close_words = [
            ['ZT', 'figure_of_merit_ZT', 'thermoelectric_figure_of_merit_ZT', 'seebeck_coefficient', 'zT',
             'thermoelectric_figure_-_of_-_merit', 'thermoelectric_power_factor', 'ZT_value', 'ZT_values',
             'dimensionless_figure_of_merit'],
            ['d31', 'electromechanical', 'electromechanical_coupling', 'd33', 'pC'],
            ['thermoelectric_properties', 'Cs2AgBiBr6', 'perovskites', 'tetradymite_-_like', 'ABX3']

        ]
        scores = [
            [0.865725, 0.862376, 0.849371, 0.847059, 0.843266, 0.835109, 0.831514, 0.82924, 0.825901, 0.822744],
            [0.465956, 0.463872, 0.458091, 0.457684, 0.436465],
            [0.356694, 0.335016, 0.329782, 0.319091, 0.314465]
        ]
        processed_positives = [
            ['thermoelectric_figure_of_merit'],
            ["piezoelectric"],
            ["thermoelectric", "perovskite"]
        ]
        processed_negatives = [
            [],
            ["perovskite"],
            ["anode", "cathode"]
        ]

        # running the tests
        for p, n, tk, im, cw, sc, pp, pn in zip(
                positives,
                negatives,
                top_ks,
                ignore_missing,
                close_words,
                scores,
                processed_positives,
                processed_negatives):
            zt_words = self.r.close_words(p, negative=n, ignore_missing=im, top_k=tk)

            self.assertEqual(zt_words["original_positive"], p)
            self.assertEqual(zt_words["original_negative"], n if n else "")
            self.assertListEqual(zt_words["close_words"], cw)
            npt.assert_array_almost_equal(zt_words["scores"], sc)

            self.assertListEqual(zt_words["positive"], pp)
            self.assertListEqual(zt_words["negative"], pn)

    def test_get_embedding(self):
        # test data
        wordphrases = [
            "Thermoelectric",
            "Solar cells",
            "asdfsdfgsregbndffff Thermoelectric",
            "asdfsdfgsregbndffff Thermoelectric",
            ["Thermoelectric", "Solar cells"],
            ["Thermoelectric solar cells", "Superconducting Randomtextthatsnotthere", "Te3Bi2"],
            ["Thermoelectric solar cells", "Superconducting Randomtextthatsnotthere", "Bi2Te3"],
            [],
            ["asdfsdfgsregbndffff", "Thermoelectric"],
            ["asdfsdfgsregbndffff"]
        ]
        ignore_missing = [False, False, True, False, False, False, True, False, True, True]
        processed_wordphrases = [
            [["thermoelectric"]],
            [["solar_cells"]],
            [["thermoelectric"]],
            [["asdfsdfgsregbndffff", "thermoelectric"]],
            [["thermoelectric"], ["solar_cells"]],
            [["thermoelectric", "solar_cells"], ["superconducting", "randomtextthatsnotthere"], ["Bi2Te3"]],
            [["thermoelectric", "solar_cells"], ["superconducting"], ["Bi2Te3"]],
            [],
            [[], ["thermoelectric"]],
            [[]]
        ]
        embedding_shapes = [
            (1, 200), (1, 200), (1, 200), (1, 200), (2, 200), (3, 200), (3, 200), (0, ), (2, 200), (1, 200)
        ]

        # valid request
        for wps, pwps, es, im in zip(wordphrases, processed_wordphrases, embedding_shapes, ignore_missing):
            response_dict = self.r.get_embedding(wps, ignore_missing=im)

            self.assertEqual(response_dict["original_wordphrases"], wps)
            self.assertEqual(response_dict["processed_wordphrases"], pwps)

            self.assertEqual(np.asarray(response_dict["embeddings"]).shape, es)

    def test_materials_map(self):

        highlights = [
            "Thermoelectric",
            ""
        ]
        ignore_missing = [True, True]
        limit = [None, None]
        dims = [2, 3]

        first3materials = [
            ["Bi2Te3", "PbTe", "PbSe0.5Te0.5"],
            ["V", "TiO2", "Ag"]
        ]
        first3scores = [
            [0.19262794200173894, 0.12772010975015763, 0.12592619653180906],
            [np.nan, np.nan, np.nan]
        ]
        processed_highlights = [
            [["thermoelectric"]],
            [[]]
        ]
        coords = [
            ["x", "y"],
            ["x", "y", "z"]
        ]
        nr_mats = [12285, 1988]

        for h, im, l, d, f3m, f3s, ph, c, nm in \
                zip(highlights, ignore_missing, limit, dims, first3materials,
                    first3scores, processed_highlights, coords, nr_mats):

            response = self.r.materials_map(highlight=h, ignore_missing=im, limit=l, dims=d)

            self.assertEqual(response["original_highlight"], h)
            self.assertEqual(response["processed_highlight"], ph)

            for xyz in c:
                self.assertIn(xyz, response["plot_data"])
            self.assertListEqual(response["plot_data"]["text"][:3], f3m)
            npt.assert_array_almost_equal(response["plot_data"]["marker"]["color"][:3], f3s)

            self.assertEqual(len(response["plot_data"]["text"]), nm)
            self.assertEqual(len(response["plot_data"]["x"]), nm)
            self.assertEqual(len(response["plot_data"]["y"]), nm)
          
class EntSearchTest(unittest.TestCase):

    rester = Rester()
    KEYS = ['doi', 'MAT', 'PRO', 'APL', 'SPL', 'DSC', 'SMT', 'CMT']
    test_query = {
        'material': ['GaN'],
        'application': ['LED']
    }

    def test_ent_search(self):

        result = self.rester.search_ents(self.test_query)
        self.assertEqual(len(result), 738)
        self.assertTrue(all(key in result[0].keys() for key in self.KEYS))

    def test_summary(self):
        result = self.rester.get_summary(self.test_query)
        self.assertEqual(result['MAT'][0][1], 738)
        subkeys = [key for key in self.KEYS if key != 'doi']
        self.assertTrue(all(key in result for key in subkeys))