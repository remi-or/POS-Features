# region Imports
from __future__ import annotations

from typing import Dict, Set, List, Union
from time import perf_counter
import pandas as pd
import spacy
from spacy.tokens.doc import Doc


from document_handling import process_document
from document_parsing import count_morph_of_type, count_lemma_of_type
from grammar_rules import count_transitive
from resources import UniversalPOStags
# endregion

# region Types
Document = Doc
Document_like = Union[str, List[str], Document]
Feature = Dict[str, Union[int, str]]
DataFrame = pd.DataFrame
# endregion

# region FeatureExtractor class
class FeatureExtractor:

    """
    A class to extract features from a text.
    """

    def __init__(
        self,
        document : Document_like,
        ) -> None:
        """
        Initializes the FeatureExtractor with a (document) of type Document_like.
        """
        print('\rProcessing document...', end='')
        t0 = - perf_counter()
        self.document = process_document(document)
        print(f"\rDocument processing finished in {(perf_counter() + t0):.2f}")
        self.morphs = {
            type : count_morph_of_type(self.document, type)
            for type in UniversalPOStags
        }
        self.lemmas = {
            type : count_lemma_of_type(self.document, type)
            for type in UniversalPOStags
        }

    def extract_features(
        self,
        verbose : bool = False,
    ) -> DataFrame:
        """
        Extracts the supported features from a text.
        Prints them along the way if (verbose) is on.
        """
        id, running, names, values, times = 0, True, [], [], []
        while running:
            try:
                t0 = -perf_counter()
                feature = eval(f"self._feature_{id}()")
                time = t0 + perf_counter()
                if verbose:
                    print(f"{feature['name']}: {feature['value']}")
                names.append(feature['name'])
                values.append(feature['value'])
                times.append(time)
                id += 1
            except Exception as e:
                # Expected exception
                if e.args[0] == f"'FeatureExtractor' object has no attribute '_feature_{id}'":
                    running = False
                # Unexpected exception
                else:
                    raise(e)
        return pd.DataFrame({
            'id' : [i for i in range(id)],
            'name' : names,
            'value' : values,
            'execution' : times,
        })


    # region Features
    def _feature_0(self) -> Feature:
        query = 'Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin'
        return {
            'id' : 0,
            'name' : 'Verbes conjugués à la troisième personne du présent indicatif',
            'value' : 0 if query not in self.morphs['VERB'] else self.morphs['VERB'][query],
        }

    def _feature_1(self) -> Feature:
        return {
            'id' : 1,
            'name' : 'Déterminants possessifs',
            'value' : sum((card if morph.endswith('Poss=Yes') else 0) for morph, card in self.morphs['DET'].items()),
        }

    def _feature_2(self) -> Feature:
        return {
            'id' : 2,
            'name' : 'Pronoms interogatifs',
            'value' : sum((card if morph.endswith('PronType=Int') else 0) for morph, card in self.morphs['PRON'].items()),
        }

    def _feature_3(self) -> Feature:
        return {
            'id' : 3,
            'name' : "Adverbes interogatifs",
            'value' : sum((card if morph.endswith('PronType=Int') else 0) for morph, card in self.morphs['ADV'].items()),
        }

    def _feature_4(self) -> Feature:
        return {
            'id' : 4,
            'name' : "Noms au pluriel",
            'value' : sum((card if morph.endswith('Number=Plur') else 0) for morph, card in self.morphs['NOUN'].items()),
        }

    def _feature_5(self) -> Feature:
        return {
            'id' : 5,
            'name' : "Nombres cardinaux",
            'value' : sum((card if morph.endswith('NumType=Card') else 0) for morph, card in self.morphs['NOUN'].items()) + \
                      sum((card if morph.endswith('NumType=Card') else 0) for morph, card in self.morphs['NUM'].items())
        }

    def _feature_6(self) -> Feature:
        return {
            'id' : 6,
            'name' : "Verbes transitifs",
            'value' : count_transitive(self.lemmas['VERB'])
        }


    # endregion


# endregion