from pprint import pprint

from google import genai

from domain.models.generated_sentence import GeneratedSentence
from domain.models.grammar_options import GrammarOptions
from domain.models.llm_options import LLMOptions
from domain.models.vocab_list import VocabList
from domain.sentence_generator import SentenceGenerator
from infrastructure.models.gemini_generated_sentence import (
    GeminiGeneratedSentence,
)


class GeminiSentenceGenerator:

    def __init__(self, client: genai.Client, llm_options: LLMOptions):
        self._client = client
        self._llm_options = llm_options

    def generate_all_sentence(
        self, vocab: VocabList, grammar_options_list: list[GrammarOptions]
    ) -> list[GeneratedSentence]:
        pass

    def generate_sentence(
        self,
        nouns: list[str],
        verb: str,
        target_language: str,
        grammar_options: GrammarOptions,
    ) -> GeneratedSentence:
        prompt = f"""
        You are generating a {target_language} sentence under strict lexical constraints.

        Lexical constraints:
        - Nouns allowed: {[noun + ' ' for noun in nouns]}
        - Main verb: {verb}
        - Optional light verbs allowed: want,  like,  to do

        Structural constraints:
        - Tense: {grammar_options.tense}
        - Include possession: {grammar_options.include_possession}
        - Include prepositional phrase: {grammar_options.include_preposition}
        - Sentence type: {grammar_options.sentence_type}
        - Plurality: {grammar_options.grammatical_number}
        """

        response = self._client.models.generate_content(
            model=self._llm_options.model_id,
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_json_schema": GeminiGeneratedSentence.model_json_schema(),
            },
        )

        print("Response Text \n\n")
        pprint(response)
        print("\n" * 6)

        response_sentence = GeminiGeneratedSentence.model_validate_json(response.text)
        print(response_sentence)

        return GeneratedSentence(
            L1="en",
            L2="hi",
            L1_text=response_sentence.L1_text,
            L2_text=response_sentence.L2_text,
            grammar_options=grammar_options,
        )
