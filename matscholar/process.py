import regex
import string
import unidecode
from os import path
from monty.fractions import gcd_float

from chemdataextractor.doc import Paragraph
from gensim.models.phrases import Phraser
from pymatgen.core.periodic_table import Element
from pymatgen.core.composition import Composition, CompositionError

model_dir = path.join(path.dirname(__file__), "models")
PHRASER_PATH = path.join(model_dir, 'phraser.pkl')

__author__ = "Vahe Tshitoyan"
__credits__ = "John Dagdelen, Leigh Weston, Anubhav Jain"
__copyright__ = "Copyright 2018, Materials Intelligence"
__version__ = "0.0.2"
__maintainer__ = "John Dagdelen"
__email__ = "jdagdelen@berkeley.edu"
__date__ = "December 7, 2018"


class MatScholarProcess:
    """
    Materials Science Text Processing Tools
    """
    ELEMENTS = ['H', 'He', 'Li', 'Be', 'B', 'C', 'N', 'O', 'F', 'Ne', 'Na', 'Mg', 'Al', 'Si', 'P', 'S', 'Cl', 'Ar', 'K',
                'Ca', 'Sc', 'Ti', 'V', 'Cr', 'Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Zn', 'Ga', 'Ge', 'As', 'Se', 'Br', 'Kr',
                'Rb', 'Sr', 'Y', 'Zr', 'Nb', 'Mo', 'Tc', 'Ru', 'Rh', 'Pd', 'Ag', 'Cd', 'In', 'Sn', 'Sb', 'Te', 'I',
                'Xe', 'Cs', 'Ba', 'La', 'Ce', 'Pr', 'Nd', 'Pm', 'Sm', 'Eu', 'Gd', 'Tb', 'Dy', 'Ho', 'Er', 'Tm', 'Yb',
                'Lu', 'Hf', 'Ta', 'W', 'Re', 'Os', 'Ir', 'Pt', 'Au', 'Hg', 'Tl', 'Pb', 'Bi', 'Po', 'At', 'Rn', 'Fr',
                'Ra', 'Ac', 'Th', 'Pa', 'U', 'Np', 'Pu', 'Am', 'Cm', 'Bk', 'Cf', 'Es', 'Fm', 'Md', 'No', 'Lr', 'Rf',
                'Db', 'Sg', 'Bh', 'Hs', 'Mt', 'Ds', 'Rg', 'Cn', 'Nh', 'Fl', 'Mc', 'Lv', 'Ts', 'Og', 'Uue']

    ELEMENT_NAMES = ['hydrogen', 'helium', 'lithium', 'beryllium', 'boron', 'carbon', 'nitrogen', 'oxygen', 'fluorine',
                     'neon', 'sodium', 'magnesium', 'aluminium', 'silicon', 'phosphorus', 'sulfur', 'chlorine', 'argon',
                     'potassium', 'calcium', 'scandium', 'titanium', 'vanadium', 'chromium', 'manganese', 'iron',
                     'cobalt', 'nickel', 'copper', 'zinc', 'gallium', 'germanium', 'arsenic', 'selenium', 'bromine',
                     'krypton', 'rubidium', 'strontium', 'yttrium', 'zirconium', 'niobium', 'molybdenum', 'technetium',
                     'ruthenium', 'rhodium', 'palladium', 'silver', 'cadmium', 'indium', 'tin', 'antimony', 'tellurium',
                     'iodine', 'xenon', 'cesium', 'barium', 'lanthanum', 'cerium', 'praseodymium', 'neodymium',
                     'promethium', 'samarium', 'europium', 'gadolinium', 'terbium', 'dysprosium', 'holmium', 'erbium',
                     'thulium', 'ytterbium', 'lutetium', 'hafnium', 'tantalum', 'tungsten', 'rhenium', 'osmium',
                     'iridium', 'platinum', 'gold', 'mercury', 'thallium', 'lead', 'bismuth', 'polonium', 'astatine',
                     'radon', 'francium', 'radium', 'actinium', 'thorium', 'protactinium', 'uranium', 'neptunium',
                     'plutonium', 'americium', 'curium', 'berkelium', 'californium', 'einsteinium', 'fermium',
                     'mendelevium', 'nobelium', 'lawrencium', 'rutherfordium', 'dubnium', 'seaborgium', 'bohrium',
                     'hassium', 'meitnerium', 'darmstadtium', 'roentgenium', 'copernicium', 'nihonium', 'flerovium',
                     'moscovium', 'livermorium', 'tennessine', 'oganesson', 'ununennium']

    ELEMENTS_AND_NAMES = ELEMENTS + ELEMENT_NAMES + [en.capitalize() for en in ELEMENT_NAMES]
    ELEMENTS_NAMES_UL = ELEMENT_NAMES + [en.capitalize() for en in ELEMENT_NAMES]

    # elemement with the valence state in parenthesis
    ELEMENT_VALENCE_IN_PAR = regex.compile(r'^('+'|'.join(ELEMENTS_AND_NAMES) +
                                           ')(\(([IV|iv]|[Vv]?[Ii]{0,3})\))$')
    ELEMENT_DIRECTION_IN_PAR = regex.compile(r'^(' + '|'.join(ELEMENTS_AND_NAMES) + ')(\(\d\d\d\d?\))')

    # exactly IV, VI or has 2 consecutive II, or roman in parenthesis: is not a simple formula
    VALENCE_INFO = regex.compile(r'(II+|^IV$|^VI$|\(IV\)|\(V?I{0,3}\))')

    SPLIT_UNITS = ['K', 'h', 'V', 'wt', 'wt.', 'MHz', 'kHz', 'GHz', 'Hz', 'days', 'weeks',
                   'hours', 'minutes', 'seconds', 'T', 'MPa', 'GPa', 'at.', 'mol.',
                   'at', 'm', 'N', 's-1', 'vol.', 'vol', 'eV', 'A', 'atm', 'bar',
                   'kOe', 'Oe', 'h.', 'mWcm−2', 'keV', 'MeV', 'meV', 'day', 'week', 'hour',
                   'minute', 'month', 'months', 'year', 'cycles', 'years', 'fs', 'ns',
                   'ps', 'rpm', 'g', 'mg', 'mAcm−2', 'mA', 'mK', 'mT', 's-1', 'dB',
                   'Ag-1', 'mAg-1', 'mAg−1', 'mAg', 'mAh', 'mAhg−1', 'm-2', 'mJ', 'kJ',
                   'm2g−1', 'THz', 'KHz', 'kJmol−1', 'Torr', 'gL-1', 'Vcm−1', 'mVs−1',
                   'J', 'GJ', 'mTorr', 'bar', 'cm2', 'mbar', 'kbar', 'mmol', 'mol', 'molL−1',
                   'MΩ', 'Ω', 'kΩ', 'mΩ', 'mgL−1', 'moldm−3', 'm2', 'm3', 'cm-1', 'cm',
                   'Scm−1', 'Acm−1', 'eV−1cm−2', 'cm-2', 'sccm', 'cm−2eV−1', 'cm−3eV−1',
                   'kA', 's−1', 'emu', 'L', 'cmHz1', 'gmol−1', 'kVcm−1', 'MPam1',
                   'cm2V−1s−1', 'Acm−2', 'cm−2s−1', 'MV', 'ionscm−2', 'Jcm−2', 'ncm−2',
                   'Jcm−2', 'Wcm−2', 'GWcm−2', 'Acm−2K−2', 'gcm−3', 'cm3g−1', 'mgl−1',
                   'mgml−1', 'mgcm−2', 'mΩcm', 'cm−2s−1', 'cm−2', 'ions', 'moll−1',
                   'nmol', 'psi', 'mol·L−1', 'Jkg−1K−1', 'km', 'Wm−2', 'mass', 'mmHg',
                   'mmmin−1', 'GeV', 'm−2', 'm−2s−1', 'Kmin−1', 'gL−1', 'ng', 'hr', 'w',
                   'mN', 'kN', 'Mrad', 'rad', 'arcsec', 'Ag−1', 'dpa', 'cdm−2',
                   'cd', 'mcd', 'mHz', 'm−3', 'ppm', 'phr', 'mL', 'ML', 'mlmin−1', 'MWm−2',
                   'Wm−1K−1', 'Wm−1K−1', 'kWh', 'Wkg−1', 'Jm−3', 'm-3', 'gl−1', 'A−1',
                   'Ks−1', 'mgdm−3', 'mms−1', 'ks', 'appm', 'ºC', 'HV', 'kDa', 'Da', 'kG',
                   'kGy', 'MGy', 'Gy', 'mGy', 'Gbps', 'μB', 'μL', 'μF', 'nF', 'pF', 'mF',
                   'A', 'Å', 'A˚', "μgL−1"]

    NR_BASIC = regex.compile(r'^[+-]?\d*\.?\d+\(?\d*\)?+$', regex.DOTALL)
    NR_AND_UNIT = regex.compile(r'^([+-]?\d*\.?\d+\(?\d*\)?+)([\p{script=Latin}|Ω|μ]+.*)', regex.DOTALL)

    PUNCT = list(string.punctuation) + ['"', '“', '”', '≥', '≤', '×']

    def __init__(self, phraser_path=PHRASER_PATH):
        self.elem_name_dict = {en: es for en, es in zip(self.ELEMENT_NAMES, self.ELEMENTS)}
        self.phraser = Phraser.load(phraser_path)

    def tokenize(self, text, split_oxidation=True, keep_sentences=True):
        """
        Converts string to a list tokens (words) using chemdataextractor tokenizer, with a couple of fixes
        for inorganic materials science.
        Keeps the structure of sentences.
        :param text: input text as a string
        :param split_oxidation: if True, will split the oxidation state from the element, e.g. iron(II)
        will become iron (II), same with Fe(II), etc.
        :param keep_sentences: if False, will disregard the sentence structure and return tokens as a
        single list of strings. Otherwise returns a list of lists, each sentence separately.
        """
        def split_token(token, so=split_oxidation):
            """
            Process a single token, in case it needs to be split up. There are 2 cases:
            It's a number with a unit, or an element with a valence state.
            """
            elem_with_valence = self.ELEMENT_VALENCE_IN_PAR.match(token) if so else None
            nr_unit = self.NR_AND_UNIT.match(token)
            if nr_unit is not None and nr_unit.group(2) in self.SPLIT_UNITS:
                # splitting the unit from number, e.g. "5V" -> ["5", "V"]
                return [nr_unit.group(1), nr_unit.group(2)]
            elif elem_with_valence is not None:
                # splitting element from it's valence state, e.g. "Fe(II)" -> ["Fe", "(II)"]
                return [elem_with_valence.group(1), elem_with_valence.group(2)]
            else:
                return [token]

        cde_p = Paragraph(text)
        tokens = cde_p.tokens
        toks = []
        for sentence in tokens:
            if keep_sentences:
                toks.append([])
                for tok in sentence:
                    toks[-1] += split_token(tok.text, so=split_oxidation)
            else:
                for tok in sentence:
                    toks += split_token(tok.text, so=split_oxidation)
        return toks

    def process(self, tokens, exclude_punct=False, convert_num=True, normalize_materials=True, remove_accents=True,
                make_phrases=False, split_oxidation=True):
        """
        Processes a pre-tokenized list of strings or a string
        (selective lower casing, material normalization, etc.)
        :param tokens: a list of strings or a string
        :param exclude_punct: bool flag to exclude all punctuation
        :param convert_num: bool flag to convert numbers (selectively) to <nUm>
        :param normalize_materials: bool flag to normalize all simple material formula
        :param remove_accents: bool flag to remove accents, e.g. Néel -> Neel
        :param make_phrases: bool flag to convert single tokens to common materials science phrases
        :param split_oxidation: only used if string is supplied, see docstring for tokenize method
        :return: (processed_tokens, material_list)
        """

        if not isinstance(tokens, list):  # if it's a string
            return self.process(self.tokenize(
                tokens, split_oxidation=split_oxidation, keep_sentences=False),
                exclude_punct=exclude_punct,
                convert_num=convert_num,
                normalize_materials=normalize_materials,
                remove_accents=remove_accents,
                make_phrases=make_phrases
            )

        processed, mat_list = [], []

        for i, tok in enumerate(tokens):
            if exclude_punct and tok in self.PUNCT:  # punctuation
                continue
            elif convert_num and self.is_number(tok):  # number
                # replace all numbers with <nUm>, except if it is a crystal direction (e.g. "(111)")
                try:
                    if tokens[i - 1] == "(" and tokens[i + 1] == ")" \
                            or tokens[i - 1] == "〈" and tokens[i + 1] == "〉":
                        pass
                    else:
                        tok = "<nUm>"
                except IndexError:
                    tok = "<nUm>"
            elif tok in self.ELEMENTS_NAMES_UL:  # chemical element name
                # add as a material mention
                mat_list.append((tok, self.elem_name_dict[tok.lower()]))
                tok = tok.lower()
            elif self.is_simple_formula(tok):  # simple chemical formula
                normalized_formula = self.normalized_formula(tok)
                mat_list.append((tok, normalized_formula))
                if normalize_materials:
                    tok = normalized_formula
            elif (len(tok) == 1 or (len(tok) > 1 and tok[0].isupper() and tok[1:].islower())) \
                    and tok not in self.ELEMENTS and tok not in self.SPLIT_UNITS \
                    and self.ELEMENT_DIRECTION_IN_PAR.match(tok) is None:
                # to lowercase if only first letter is uppercase (chemical elements already covered above)
                tok = tok.lower()

            if remove_accents:
                tok = self.remove_accent(tok)

            processed.append(tok)

        if make_phrases:
            processed = self.make_phrases(processed, reps=2)

        return processed, mat_list

    def make_phrases(self, sentence, reps=2):
        """
        generates phrases from a sentence of words
        :param sentence: a list of tokens
        :param reps: how many times to combine the words
        :return:
        """
        while reps > 0:
            sentence = self.phraser[sentence]
            reps -= 1
        return sentence

    def is_number(self, s):
        """
        Determines if the supplied string is number
        :param s: the string
        :return: True or False
        """
        return self.NR_BASIC.match(s.replace(',', '')) is not None

    @staticmethod
    def is_element(txt):
        """
        Checks if the string is a chemical symbol.
        :param txt: input string
        :return: True or False
        """
        try:
            Element(txt)
            return True
        except ValueError:
            return False

    def is_simple_formula(self, text):
        """
        Determine if the string is a simple chemical formula. Excludes some roman numbers, e.g. IV
        :param text: the string
        :return: True or False
        """
        if self.VALENCE_INFO.search(text) is not None:
            # 2 consecutive II, IV or VI should not be parsed as formula
            # related to valence state, so don't want to mix with I and V elements
            return False
        elif any(char.isdigit() or char.islower() for char in text):
            # has to contain at least one lowercase letter or at least one number (to ignore abbreviations)
            # also ignores some materials like BN, but these are few and usually written in the same way,
            # so normalization won't be crucial
            try:
                if text in ["O2", "N2", "Cl2", "F2", "H2"]:
                    # including chemical elements that are diatomic at room temperature and atm pressure,
                    # despite them having only a single element
                    return True
                composition = Composition(text)
                # has to contain more than one element, single elements are handled differently
                if len(composition.keys()) < 2 or any([not self.is_element(key) for key in composition.keys()]):
                    return False
                return True
            except (CompositionError, ValueError):
                return False
        else:
            return False

    @staticmethod
    def get_ordered_integer_formula(el_amt, max_denominator=1000):
        """
        Given a dictionary of {element : stoichiometric value, ..}, returns a string with
        elements ordered alphabetically and stoichiometric values normalized to smallest common
        ingeger denominator
        :param el_amt:
        :param max_denominator:
        :return:
        """
        # return alphabetically ordered formula with integer fractions
        g = gcd_float(list(el_amt.values()), 1 / max_denominator)
        d = {k: round(v / g) for k, v in el_amt.items()}
        formula = ""
        for k in sorted(d):
            if d[k] > 1:
                formula += k + str(d[k])
            elif d[k] != 0:
                formula += k
        return formula

    def normalized_formula(self, text, max_denominator=1000):
        """
        Normalizes chemical formula to smallest common integer denominator, and orders elements
        alphabetically
        :param text: the string formula
        :param max_denominator: highest precision for the denominator (1000 by default)
        :return: a normalized formula string, e.g. Ni0.5Fe0.5 -> FeNi
        """
        try:
            formula_dict = Composition(text).get_el_amt_dict()
            return self.get_ordered_integer_formula(formula_dict, max_denominator)
        except (CompositionError, ValueError):
            return text

    @staticmethod
    def remove_accent(txt):
        """
        Removes accents from a string
        :param txt: input text
        :return: de-accented text
        """
        # there is a problem with angstrom sometimes, so ignoring length 1 strings
        return unidecode.unidecode(txt) if len(txt) > 1 else txt
