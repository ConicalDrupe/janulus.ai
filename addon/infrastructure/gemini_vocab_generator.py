from domain.models.vocab import VocabGenerator
from domain.models.user_qa import UserQA
from domain.models.llm_options import LLMOptions

from infrastructure.models.gemini_generated_vocab import GeminiGeneratedVocabList

class GeminiGeneratedVocabList(VocabGenerator):
    def _init_(self, client:genai.Client, llm_options: LLMOptions):
        self._client = client
        self._llm_options = llm_options
        #helper functions
    def generate_vocab(self, user_qa: UserQA, target_language) -> VocabList:
        prompt = f"""
        You are an expert linguistic. You are helping a beginner learn . They are a complete beginner.
You should help provide them with sentences they can use in their daily lives. To do so, first ask the user the following questions.y