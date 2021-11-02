# region Imports
from __future__ import annotations

from typing import Dict, Set, List, Union
from time import perf_counter
import pandas as pd
import numpy as np
from spacy.tokens.doc import Doc


from document_handling import process_document
from document_parsing import count_morph_of_type, count_lemma_of_type, count_ner_by_label
from grammar_rules import count_transitive, get_lexique_3_subtitles_freqs, count_interrogative_words
from resources import UniversalPOStags, UniversalPOStagsFrench, NerLabels
# endregion

# region Types
Document = Doc
Document_like = Union[str, List[str], Document]
Features = List[Dict[str, Union[int, str]]]
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

        # self.morph[type] = {morph : instances of morph in self.document}
        self.morphs = {
            type : count_morph_of_type(self.document, type)
            for type in UniversalPOStags
        }

        # self.lemmas[_type] = {lemma : instances of lemma of type _type in self.document}
        self.lemmas = {
            type : count_lemma_of_type(self.document, type)
            for type in UniversalPOStags
        }
        self.lemmas['ALL'] = {}
        for type in UniversalPOStags:
            for lemma, cardinal in self.lemmas[type].items():
                if not lemma in self.lemmas['ALL']:
                    self.lemmas['ALL'][lemma] = 0
                self.lemmas['ALL'][lemma] += cardinal
        
        # self.freqs[type] = {lemma : frequency of lemma in lexique3's subtitles}
        self.freqs = {
            type : {
                lemma : freq for lemma, freq in zip(self.lemmas[type].keys(), get_lexique_3_subtitles_freqs(type, list(self.lemmas[type].keys())))
            }
            for type in UniversalPOStags
        }
        self.freqs['ALL'] = {
            lemma : sum(self.freqs[type][lemma] for type in UniversalPOStags if lemma in self.freqs[type])
            for lemma in self.lemmas['ALL']
        }

        # self.ners[label] = {text : instances of text in self.document tagged as label}
        self.ners = {
            label : count_ner_by_label(self.document, label)
            for label in NerLabels
        }
        self.ners['ALL'] = {}
        for label in NerLabels:
            for text, instances in self.ners[label].items():
                if text not in self.ners['ALL']:
                    self.ners['ALL'][text] = 0
                self.ners['ALL'][text] += instances
        

    def extract_features(
        self,
        verbose : bool = False,
    ) -> DataFrame:
        """
        Extracts the supported features from a text.
        Prints them along the way if (verbose) is on.
        """
        names, values, times = [], [], []
        for something in dir(self):
            if something.startswith('_feature'):
                t0 = -perf_counter()
                features = eval(f"self.{something}()")
                time = t0 + perf_counter()
                for feature in features:
                    if verbose:
                        print(f"{feature['name']}: {feature['value']}")
                    names.append(feature['name'])
                    values.append(feature['value'])
                    times.append(time)
        return pd.DataFrame({
            'name' : names,
            'value' : values,
            'execution' : times,
        })


    # region Features
    def _feature_0(self) -> Features:
        query = 'Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin'
        return [{
            'name' : 'Verbes conjugués à la troisième personne du présent indicatif',
            'value' : 0 if query not in self.morphs['VERB'] else self.morphs['VERB'][query],
        }]

    def _feature_1(self) -> Features:
        return [{
            'name' : 'Déterminants possessifs',
            'value' : sum((card if morph.endswith('Poss=Yes') else 0) for morph, card in self.morphs['DET'].items()),
        }]

    def _feature_2(self) -> Features:
        return [{
            'name' : 'Pronoms interogatifs',
            'value' : sum((card if morph.endswith('PronType=Int') else 0) for morph, card in self.morphs['PRON'].items()),
        }]

    def _feature_3(self) -> Features:
        return [{
            'name' : "Adverbes interogatifs",
            'value' : sum((card if morph.endswith('PronType=Int') else 0) for morph, card in self.morphs['ADV'].items()),
        }]

    def _feature_4(self) -> Features:
        return [{
            'name' : "Noms au pluriel",
            'value' : sum((card if morph.endswith('Number=Plur') else 0) for morph, card in self.morphs['NOUN'].items()),
        }]

    def _feature_5(self) -> Features:
        return [{
            'name' : "Nombres cardinaux",
            'value' : sum((card if morph.endswith('NumType=Card') else 0) for morph, card in self.morphs['NOUN'].items()) + \
                      sum((card if morph.endswith('NumType=Card') else 0) for morph, card in self.morphs['NUM'].items())
        }]

    def _feature_6(self) -> Features:
        return [{
            'name' : "Verbes transitifs",
            'value' : count_transitive(self.lemmas['VERB'])
        }]

    def _feature_7(self) -> Features:
        return [{
            'name' : 'Moyenne de la fréquence des mots dans le texte selon L3ST',
            'value' :  np.mean(list(self.freqs['ALL'].values()))
        }]

    def _feature_8(self) -> Features:
        return [{
            'name' : 'Moyenne de la fréquence des noms comptés avec leur multiplicité dans le texte selon L3ST',
            'value' : float(np.average(
                a=list(self.freqs['NOUN'].values()), 
                weights=list(self.lemmas['NOUN'].values()),
                ))
        }]

    def _feature_9(self) -> Features:
        return [{
            'name' : "Interjections",
            'value' : sum(x for x in self.lemmas['INTJ'].values())
        }]

    def _features_10(self) -> Features:
        return [{
            'name' : f"Ecart type de la fréquence des mots dans le texte selon L3ST",
            'value' : np.std(list(self.freqs['ALL'].values()))
        }]

    def _feature_11(self) -> Features:
        return [{
            'name' : 'Mots interrogatifs',
            'value' : sum(
                count_interrogative_words(self.lemmas[cgram], cgram)
                for cgram in ['ADJ', 'PRON', 'ADV']
            )
        }]

    def _feature_ner(self) -> Features:
        features = []
        for label in NerLabels:
            features.append({
                'name' : f'{NerLabels[label]}',
                'value' : sum(instances for instances in self.ners[label].values()),
            })
        return features

    def _features_M(self) -> Features:
        features = []
        for cgram in UniversalPOStags:
            features.append({
                'name' : f"Moyenne de la fréquence des {UniversalPOStagsFrench[cgram]} dans le texte selon L3ST",
                'value' : np.mean(list(self.freqs[cgram].values()))
            })
        return features

    def _features_SD(self) -> Features:
        features = []
        for cgram in UniversalPOStags:
            features.append({
                'name' : f"Ecart type de la fréquence des {UniversalPOStagsFrench[cgram]} dans le texte selon L3ST",
                'value' : np.std(list(self.freqs[cgram].values()))
            })
        return features

    # endregion


# endregion