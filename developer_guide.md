# Working in Git

Before working on any changes:
- check your branch (ensure you are in main) - git checkout
- pull most recent changes of main branch
```{bash}
git pull
```
```{bash}
git checkout -b my_feature-initals
```
And begin your work.
As you make progress in your feature, add your changes and commit a meaningful message.

Once your feature is complete. We can merge to main (via PR?).

# Python Standards
class file names should be snake_case.py, classes themselves are Titled case.
method names are also snake_case().

Ex. For persisting a collection of vocab or sentencens, we want to create a CollectionRepository
thus we would create
/domain/repository/collection_repository.py (defines the CollectionRepository abstract class)
/domain/models/collection.py (defines the Collection class (a list of notes, with a header), treated as a business object)
/domain/models/note.py (defines the Note class, a single record, treated as a business object)

CollectionRepository class methods are in snake case. ex. save_all()

/infrastructure/repository/csv_collection_repository.py (holds CsvCollectionRepository with concrete implementation)
/infrastructure/repository/anki_collection_repository.py (holds AnkiCollectionRepository with concrete implementation)

# Quick start
Clone repository

(Install uv)[https://docs.astral.sh/uv/getting-started/installation/]

The project uses UV-package manager in place of pip.

Inititalize  and sync to changes.
```{bash}
uv sync
```
In development you should sync if you have package import errors.
If you need to add or remove a package you can use.
```{bash}
uv add numpy
```
```{bash}
uv remove numpy
```

# Architecture

__init__.py should act as a Anki framework bootstrap only!
- Register Menus
- Register Hooks
- Initialize Services
- Nothing Else

addon/
│
├── __init__.py          # Entry point (Anki adapter)
│
├── ui/        # UI + hooks + menus (Anki-dependent)
│   ├── menu.py
│   └── reviewer_hooks.py
│
├── application/         # Services / Use cases (orchestrates logic)
│
├── domain/              # Pure business logic (Anki-independent)
│
├── infrastructure/      #  Specific Implementations of Business Logic access, persistence
│   └── deck_repo.py
│
└── config.py            # Addon config loading
