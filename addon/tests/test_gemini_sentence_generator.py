import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from google import genai

from domain.models.grammar_options import GrammarOptions, SentenceType, Tense
from domain.models.llm_options import LLMOptions
from infrastructure.gemini_sentence_generator import GeminiSentenceGenerator

if __name__ == "__main__":

    llm_options = LLMOptions(model_id="gemini-3-flash-preview")

    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")

    google_client = genai.Client(vertexai=True, project=project_id, location="global")

    sentence_generator = GeminiSentenceGenerator(
        client=google_client, llm_options=llm_options
    )

    grammar_options = GrammarOptions(
        tense=Tense.PRESENT_CONTINUOUS,
        sentence_type=SentenceType.DECLARATIVE,
        grammatical_number=None,
        include_preposition=False,
        include_possession=False,
    )

    sentence = sentence_generator.generate_sentence(
        nouns=["I"], verb="to walk", target_language="Hindi", grammar_options=grammar_options
    )
