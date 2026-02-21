from dataclasses import dataclass


@dataclass
class VocabList:
    subjects: list[str]
    objects: list[str]
    verbs: list[str]
