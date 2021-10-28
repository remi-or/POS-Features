# region Imports
from typing import Dict, Optional
import json
from pathlib import Path


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


# endregion