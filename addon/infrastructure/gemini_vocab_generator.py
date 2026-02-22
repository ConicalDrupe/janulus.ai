from domain.models.vocab import VocabGenerator
from domain.models.user_qa import UserQA
from domain.models.llm_options import LLMOptions

from infrastructure.models.gemini_generated_vocab import GeminiGeneratedVocabList

class GeminiVocabGenerator(VocabGenerator):
    def _init_(self, client:genai.Client, llm_options: LLMOptions):
        self._client = client
        self._llm_options = llm_options
        #helper functions
    def generate_vocab(self, user_qa: UserQA, target_language) -> VocabList:
        prompt = f"""
        You are an expert linguistic. You are helping a beginner learn {target_language}. They are a complete beginner. You should help provide them with sentences they can use in their daily lives. To do so, first ask the user the following questions.
        {"\n".join(f"Q{i}: {q}" for i, q in enumerate(UserQA.questions, start=1))}
        Then, based on context (implicit and explicit) of their answers, come up with some subject, object, and verbs that they would use use. With up to 5 subjects, 5 verbs, and 10 objects. Be sure to give general yet applicable vocabulary words. Here is their response. Give me the english vocab words. Be sure to include meta-context. 
        {"\n".join(f"A{i}: {a}" for i, a in enumerate(UserQA.answers, start=1))}
        """

        response = self._client.models.generate_content(
            model=self._llm_options.model_id, contents=prompt, 
            config={
                "response_mime_type": "application/json", 
                "response_json_schema":
                GeminiGeneratedVocabList.
                model_json_schema(),
            },
        )
        response_vocablist = GeminiGeneratedVocabList.model_validate_json(response.text)
        return VocabList(
            subjects=response_vocablist.subjects
            objects=response_vocablist.objects
            verbs=response_vocablist.verbs,
        )
        


        