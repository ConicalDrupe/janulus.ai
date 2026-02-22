import sys
from pathlib import Path
import os 

sys.path.insert(0, str(Path(__file__).parent.parent))

from domain.models.user_qa import UserQA
from domain.models.llm_options import LLMOptions
from google import genai
from infrastructure.models.gemini_generated_vocab import GeminiGeneratedVocabList

from infrastructure.gemini_vocab_generator import GeminiVocabGenerator

target_language = "Hindi"
Q = ["What do you like to do during your free time? ", "What is your occupation/work?"]
A = [
    "I like to paint and hang out with my friends",
    "I am a student studying Electrical Engineering",
]
user_info = UserQA(Q, A)
def vocab_generation():
    llm_options = LLMOptions(model_id="gemini-3-flash-preview")

    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")

    google_client = genai.Client(vertexai=True, project=project_id, location="global")

    vocab_list_generator = GeminiVocabGenerator(client=google_client, llm_options=llm_options
    )
    vocab_list = vocab_list_generator.generate_vocab(user_info, target_language
    )

    print(vocab_list)

if __name__ == "__main__":
    vocab_generation()