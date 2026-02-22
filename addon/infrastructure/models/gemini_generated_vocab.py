from domain.models.vocab_list import VocabList
from pydantic import BaseModel, Field

class GeminiGeneratedVocabList(BaseModel):
    subjects: list[str] Field(description="Subjects generated from user answers.")
    objects: list[str] Field(description="Objects generated from user answers.")
    objects: list[str] Field(description="Verbs generated from user answers.")

    
    def to_domain(

        self) -> VocabList 
        return VocabList(
            subjects=self.subjects
            objects=self.objects
            verbs=self.verbs

        )