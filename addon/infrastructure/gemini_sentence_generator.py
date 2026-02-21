from addon.domain.models.grammar_options import GrammarOptions

prompt = f"""
You are generating a {target_language} sentence under strict lexical constraints.

Lexical constraints:
- Nouns allowed: {nouns}
- Main verb: {verb}
- Optional light verbs allowed: want,  like,  to do

Structural constraints:
- Tense: {GrammarOptions.tense}
- Include possession: {GrammarOptions.include_possession}
- Include prepositional phrase: {GrammarOptions.include_preposition}
- Sentence type: {GrammarOptions.sentence_type}
- Plurality: {GrammarOptions.plurality}
"""
