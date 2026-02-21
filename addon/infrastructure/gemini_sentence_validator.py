from domain.models.generated_sentence import GeneratedSentence
from domain.models.llm_options import LLMOptions
from domain.sentence_validator import SentenceValidator
from google import genai
from infrastructure.models.gemini_sentence_validator import GeminiSentenceValidater


class GeminiSentenceValidator(SentenceValidator):

    def __init__(self, client: genai.Client, llm_options: LLMOptions):
        self._client = client
        self._llm_options = llm_options

    async def validate(self, sentence: GeneratedSentence) -> bool:
        prompt = f"""
        You are a {sentence.L2} language expert evaluating whether a sentence sounds natural.

        Evaluate this sentence: "{sentence.L2_text}"

        Would a native {sentence.L2} speaker naturally use this sentence?
        """

        response = await self._client.aio.models.generate_content(
            model=self._llm_options.model_id,
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_json_schema": GeminiSentenceValidater.model_json_schema(),
            },
        )

        result = GeminiSentenceValidater.model_validate_json(response.text)
        return result.is_used
