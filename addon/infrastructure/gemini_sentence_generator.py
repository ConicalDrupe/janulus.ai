import asyncio
import itertools

from domain.models.generated_sentence import GeneratedSentence
from domain.models.grammar_options import GrammarOptions
from domain.models.llm_options import LLMOptions
from domain.models.vocab_list import VocabList
from domain.sentence_generator import SentenceGenerator
from google import genai
from infrastructure.models.gemini_generated_sentence import \
    GeminiGeneratedSentence


class GeminiSentenceGenerator(SentenceGenerator):

    def __init__(self, client: genai.Client, llm_options: LLMOptions):
        self._client = client
        self._llm_options = llm_options

    # Helper function
    def process_vocab_products(self, subjects: list[str], objects: list[str]) -> list[list[str]]:
        nouns = list(set(subjects + objects))
        return [list(pair) for pair in itertools.combinations(nouns, 2)]

    async def generate_all_sentence(
        self, vocab: VocabList, target_language: str, grammar_options_list: list[GrammarOptions]
    ) -> list[GeneratedSentence]:

        noun_permutations = self.process_vocab_products(vocab.subjects, vocab.objects)

        tasks = [
            self.generate_sentence(nouns=noun_pair, verb=verb, target_language=target_language, grammar_options=grammar_option)
            for grammar_option in grammar_options_list
            for verb in vocab.verbs
            for noun_pair in noun_permutations
        ]
        return list(await asyncio.gather(*tasks))

    async def generate_sentence(
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

        response = await self._client.aio.models.generate_content(
            model=self._llm_options.model_id,
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_json_schema": GeminiGeneratedSentence.model_json_schema(),
            },
        )

        response_sentence = GeminiGeneratedSentence.model_validate_json(response.text)

        return GeneratedSentence(
            L1="english",
            L2=target_language,
            L1_text=response_sentence.L1_text,
            L2_text=response_sentence.L2_text,
            grammar_options=grammar_options,
        )
