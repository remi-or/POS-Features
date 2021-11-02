# region Imports
from __future__ import annotations

from typing import Dict, Optional, List
import json
from pathlib import Path

from resources import UniversalPOStags


# endregion

# region Functions
def count_transitive(
    verb_lemmas : Dict[str, int],
    path : Optional[str] = None,
) -> bool:
    """
    Given a (verb_lemmas) dictionnary containing lemmas and their count, returns the number of transitive verbs.
    This function uses a dictionnary where keys are transitive verbs that is encoded as a json at (json_relative_path).
    """
    if path is None:
        path = Path(__file__).parent / 'verbes_transitifs/verbes_transitifs.json'
    with open(path, encoding='utf-8') as file:
        transitives = json.load(file)
    count = 0
    for lemma, cardinal in verb_lemmas.items():
        if lemma in transitives:
            count += cardinal
    return count


def get_lexique_3_subtitles_freqs(
    types : str | List[str],
    lemmas : str | List[str],
    path : Optional[str] = None,
) -> List[float]:
    """
    Given a list of (lemmas) and their (types), chosen among the universal POS tags, 
    returns their frequencies in the french language according to the lexique.
    A single type / lemma couple can be passed as well, as two strings.
    A single type can be passed for mutliple lemmas as well.
    """
    ## Type checking
    # Single couple case
    if isinstance(types, str) and isinstance(lemmas, str):
        types, lemmas = [types], [lemmas]
    # One type one list case
    elif isinstance(types, str) and isinstance(lemmas, list):
        types = [types] * len(lemmas)
    # Two lists case
    elif isinstance(types, list) and isinstance(lemmas, list):
        pass
    # Error case
    else:
        raise TypeError(f"Unsupported input types: {type(types)}, {type(lemmas)}.\nThis functions excepts str/str, list/list, str/list for types/lemmas")
    
    ## Loading the frequency table
    # Default path is set if None is given
    if path is None:
        path = Path(__file__).parent / 'lexique/lemma_to_freq_table.json'
    # Load the frequency tables
    with open(path, encoding='utf-8') as file:
        lemma_to_freq = json.load(file)
    
    ## Main loop
    frequencies = []
    for _type, lemma in zip(types, lemmas):
        # Check if the type is right
        assert _type in UniversalPOStags, \
            f"This type isn't an universal POS tag: {_type}. The universal POS tags are: {UniversalPOStags}"
        # Case where the frequency isn't zero
        try:
            frequencies.append(lemma_to_freq[_type][lemma])
        # Case where the frequency is zero, excepted exception
        except KeyError:
            frequencies.append(0)
        # Error case, unexcepted exception
        except Exception as unexcepected_exception:
            raise unexcepected_exception
    
    return frequencies
    
    

# endregion