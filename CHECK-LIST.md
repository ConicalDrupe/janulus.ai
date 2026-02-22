
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
- [x] Domain ABC
- [x] Infrastructure Google Implementation
- [ ] Infrastructure Eleven Labs Implementation

# Use Cases

# Sentence Generator
- [ ] Generate Personalized Vocab -> Insert into Anki or Save as CSV (save tags too)
- [ ] Generate Quickstart Vocab -> Insert into Anki or Save as CSV (save tags too)
<!-- - [ ] Ingest Vocab (Selection of Anki Deck or CSV) -->
- [ ] Generate Vocab -> Generate Sentences -> Insert into Anki or Save as CSV (save tags too)
- [ ] Save Sentences to Anki or CSV (save tags)

### Caching
- [x] db models
 - [x] DbVocab (hash_id, L1,L2,L1_text,L2_text,audio,tags)
 - [x] DbSentence (hash_id, L1,L2,L1_text,L2_text,audio,tags)


# Demo

# Submission
- [ ] 2-min video
- [ ] github readme
- [ ] DevPost
