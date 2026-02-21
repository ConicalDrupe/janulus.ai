from domain.models.generated_sentence import GeneratedSentence
from domain.models.grammar_options import GrammarOptions
from pydantic import BaseModel, Field


class GeminiGeneratedSentence(BaseModel):
    L1_text: str = Field(description="Sentence in English")
    L2_text: str = Field(description="Sentence in Foreign Language")

    def to_domain(
        self, L1: str, L2: str, grammar_options: GrammarOptions
    ) -> GeneratedSentence:
        return GeneratedSentence(
            L1=L1,
            L2=L2,
            L1_text=self.L1_text,
            L2_text=self.L2_text,
            grammar_options=grammar_options,
        )
