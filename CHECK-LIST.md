
# Main Components

## Vocab Personalization
- [ ] Test Prompts in Gemini
    - [ ] Questions for User to answer
- [x] Domain Entities (VocabList)
- [ ] Domain Abstract Class
- [ ] Infrastructure Concrete Class
- [ ] Test

## Sentence Generation
- [x] Domain GrammarOptions
- [x] Domain GeneratedSentence
- [x] Infrastructure Implementation (Single Sentenc)
- [x] Infrastructure Implementation (Multiple Sentences from VocabList)
- [x] Converted to Async
- [x] Validator

## Deck Writer
- [x] Domain ABC
- [x] Infrastructure CSV implementation
- [x] Infrastructure Anki implementation
- [x] Support Audio (Need to verify)

## Text-to-Speech
- [ ] Domain ABC
- [ ] Infrastructure Google Implementation
- [ ] Infrastructure Eleven Labs Implementation

# Use Cases

# Sentence Generator
- [ ] Ingest Vocab (Selection of Anki Deck or CSV)
- [ ] Generate Sentences
- [ ] Save Sentences
- [ ] Save Sentences to Anki or CSV (save tags)

### Caching
- [ ] db models
 - [ ] DbVocab (hash_id, L1,L2,L1_text,L2_text,audio,tags)
 - [ ] DbSentence (hash_id, L1,L2,L1_text,L2_text,audio,tags)
 - [ ] DbAudio (hash_id, L1,L2,L1_text,L2_text, voice, voice_model,tags)


# Demo

# Submission
- [ ] 2-min video
- [ ] github readme
- [ ] DevPost
