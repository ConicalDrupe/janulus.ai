
# Main Components

## Vocab Personalization
- [x] Test Prompts in Gemini
    - [x] Questions for User to answer
- [x] Domain Entities (VocabList)
- [x] Domain Abstract Class
- [ ] Infrastructure Concrete Class
- [ ] Infrastructure Test
- [ ] Create Application Use-case

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
- [x] Infrastructure Eleven Labs Implementation

# Use Cases

- [ ] Generate Personalized Vocab -> Insert into Anki or Save as CSV (save tags too)
- [ ] Generate Personalized Vocab -> Generate Sentences -> Insert into Anki or Save as CSV (save tags too)
    - [ ] Same as above, but generate vocab from quickstart lists. (common questions, needs, etc.)
- [ ] Ingest Vocab (Selection of Anki Deck or CSV) -> Requires Ingest
    - [ ] Ingest Interface + Parser
    - [ ] Part of speech labeler
- [x] Generate Quickstart Vocab -> Insert into Anki or Save as CSV (save tags too)
- [x] Save Sentences to Anki or CSV (save tags)

### Caching
- [x] db models
 - [x] DbVocab (hash_id, L1,L2,L1_text,L2_text,audio,tags)
 - [x] DbSentence (hash_id, L1,L2,L1_text,L2_text,audio,tags)


# Improvements
- [ ] Remove Async garbage
- [ ] Use Gemini batch api
    - [ ] Correct Semiphore calls
    - [ ] Exponential backoff
- [ ] Strategy Pattern for different sentence types/grammatical options. (Different specialized prompts for different options)
- [ ] Autosave to csv after generation (so we dont loose progress?)
- [ ] UI: Generation % complete bar
- [ ] Generation History UI (language,vocab, grammar options)


# Submission
- [x] 2-min video
- [x] github readme
    - [x] Use instructions
- [x] DevPost
