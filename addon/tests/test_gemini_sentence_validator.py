import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from domain.models.generated_sentence import GeneratedSentence
from domain.models.grammar_options import GrammarOptions, SentenceType, Tense
from domain.models.llm_options import LLMOptions
from google import genai
from infrastructure.gemini_sentence_validator import GeminiSentenceValidator


def test_validate_natural_sentence():
    asyncio.run(_test_validate_natural_sentence())

def test_validate_unnatural_sentence():
    asyncio.run(_test_validate_unnatural_sentence())

async def _test_validate_natural_sentence():
    llm_options = LLMOptions(model_id="gemini-3-flash-preview")
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    google_client = genai.Client(vertexai=True, project=project_id, location="global")

    validator = GeminiSentenceValidator(client=google_client, llm_options=llm_options)

    grammar_options = GrammarOptions(
        tense=Tense.SIMPLE_PRESENT,
        sentence_type=SentenceType.DECLARATIVE,
        grammatical_number=None,
        include_preposition=False,
        include_possession=False,
    )

    sentence = GeneratedSentence(
        L1="english",
        L2="Hindi",
        L1_text="I like you.",
        L2_text="मुझे तुमसे प्यार है।",
        grammar_options=grammar_options,
    )

    result = await validator.validate(sentence)
    assert isinstance(result, bool)
    print(f"Validation result: {result}")


async def _test_validate_unnatural_sentence():
    llm_options = LLMOptions(model_id="gemini-3-flash-preview")
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    google_client = genai.Client(vertexai=True, project=project_id, location="global")

    validator = GeminiSentenceValidator(client=google_client, llm_options=llm_options)

    grammar_options = GrammarOptions(
        tense=Tense.SIMPLE_PRESENT,
        sentence_type=SentenceType.DECLARATIVE,
        grammatical_number=None,
        include_preposition=False,
        include_possession=False,
    )

    sentence = GeneratedSentence(
        L1="English",
        L2="Hindi",
        L1_text="I am liking you.",
        L2_text="मैं तुम्हें पसंद कर रहा हूं",
        grammar_options=grammar_options,
    )

    result = await validator.validate(sentence)
    assert isinstance(result, bool)
    print(f"Validation result: {result}")


if __name__ == "__main__":
    test_validate_natural_sentence()
    test_validate_unnatural_sentence()
