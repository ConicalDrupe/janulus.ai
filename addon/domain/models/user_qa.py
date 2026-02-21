from dataclass import dataclass

@dataclass
class UserQA:
        questions: list[str]
        answers: list[str]
        