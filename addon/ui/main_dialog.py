"""
Janulus AI — main Anki dialog.

Provides sentence-card generation using a quickstart VocabList pack.
All Qt imports go through aqt.qt so we stay compatible with Anki's
bundled PyQt version.
"""
import asyncio
import traceback
from pathlib import Path

from aqt.qt import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QThread,
    QVBoxLayout,
    Qt,
    pyqtSignal,
)

from addon_config import InfraConfig
from application.service_sentence_deck import SentenceDeckService
from domain.models.deck import Deck
from domain.models.grammar_options import GrammarOptions, SentenceType, Tense
from domain.tts_generator import TtsGenerator
from domain.quickstart_packs.packs import QUICKSTART_PACKS
from infrastructure.anki_deck_writer import AnkiDeckWriter
from infrastructure.csv_deck_writer import CsvDeckWriter
from infrastructure.gemini_sentence_generator import GeminiSentenceGenerator
from infrastructure.gemini_sentence_validator import GeminiSentenceValidator
from infrastructure.elevenlabs_tts_generator import ElevenLabsTtsGenerator
from infrastructure.gemini_tts_generator import GeminiTtsGenerator, plain_language_to_bcp47
from sqlalchemy import Engine

try:
    from google import genai
    _GENAI_AVAILABLE = True
except ImportError:
    _GENAI_AVAILABLE = False

# ─── Constants ────────────────────────────────────────────────────────────────

_GEMINI_TTS_VOICES = [
    "Aoede", "Charon", "Fenrir", "Kore", "Puck",
    "Zephyr", "Achird", "Algieba", "Alnilam", "Aoede",
    "Despina", "Enceladus", "Iocaste", "Rasalgethi",
    "Sadachbia", "Sadaltager", "Schedar", "Sulafat",
    "Umbriel", "Vindemiatrix",
]
_GEMINI_TTS_VOICES = sorted(set(_GEMINI_TTS_VOICES))

_TENSE_GROUPS: list[tuple[str, list[tuple[Tense, str]]]] = [
    ("Present", [
        (Tense.SIMPLE_PRESENT, "Simple"),
        (Tense.PRESENT_CONTINUOUS, "Progressive"),
        (Tense.PRESENT_PERFECT, "Perfect"),
        (Tense.PRESENT_PERFECT_CONTINUOUS, "Perf. Progressive"),
    ]),
    ("Past", [
        (Tense.SIMPLE_PAST, "Simple"),
        (Tense.PAST_CONTINUOUS, "Progressive"),
        (Tense.PAST_PERFECT, "Perfect"),
        (Tense.PAST_PERFECT_CONTINUOUS, "Perf. Progressive"),
    ]),
    ("Future", [
        (Tense.SIMPLE_FUTURE, "Simple"),
        (Tense.FUTURE_CONTINUOUS, "Progressive"),
        (Tense.FUTURE_PERFECT, "Perfect"),
        (Tense.FUTURE_PERFECT_CONTINUOUS, "Perf. Progressive"),
    ]),
]

_SENTENCE_TYPE_LABELS: dict[SentenceType, str] = {
    SentenceType.DECLARATIVE: "Declarative",
    SentenceType.INTERROGATIVE: "Interrogative",
    SentenceType.EXCLAMATORY: "Exclamatory",
    SentenceType.IMPERATIVE: "Imperative",
}

# ─── Worker thread ────────────────────────────────────────────────────────────


class _GeneratorWorker(QThread):
    """Runs the async SentenceDeckService in a background thread."""

    finished = pyqtSignal(object)   # emits Deck on success
    error = pyqtSignal(str)         # emits error message on failure

    def __init__(
        self,
        service: SentenceDeckService,
        vocab,
        L1: str,
        L2: str,
        grammar_options_list: list[GrammarOptions],
        with_audio: bool,
        parent=None,
    ):
        super().__init__(parent)
        self._service = service
        self._vocab = vocab
        self._L1 = L1
        self._L2 = L2
        self._grammar_options_list = grammar_options_list
        self._with_audio = with_audio

    def run(self):
        try:
            deck = asyncio.run(
                self._service.build_deck(
                    vocab=self._vocab,
                    L1=self._L1,
                    L2=self._L2,
                    grammar_options_list=self._grammar_options_list,
                    with_audio=self._with_audio,
                )
            )
            self.finished.emit(deck)
        except Exception as exc:
            self.error.emit(f"{type(exc).__name__}: {exc}\n{traceback.format_exc()}")


# ─── Main dialog ──────────────────────────────────────────────────────────────


class JanulusDialog(QDialog):
    def __init__(self, parent, infra_config: InfraConfig, engine: Engine, user_config: dict):
        super().__init__(parent)
        self._infra_config = infra_config
        self._engine = engine
        self._user_config = user_config
        self._deck: Deck | None = None
        self._worker: _GeneratorWorker | None = None

        self.setWindowTitle("Janulus AI")
        self.setMinimumWidth(480)
        self._build_ui()
        self._load_user_config()

    # ── UI construction ───────────────────────────────────────────────────────

    def _build_ui(self):
        root = QVBoxLayout(self)

        # ── Title ──
        title = QLabel("<h2>Janulus AI</h2>")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(title)

        # ── Language & voice ──
        lang_box = QGroupBox("Language settings")
        lang_layout = QVBoxLayout(lang_box)

        lang_row = QHBoxLayout()
        lang_row.addWidget(QLabel("Target language:"))
        self._lang_combo = QComboBox()
        self._lang_combo.addItems(sorted(plain_language_to_bcp47.keys()))
        lang_row.addWidget(self._lang_combo, 1)
        lang_layout.addLayout(lang_row)

        voice_row = QHBoxLayout()
        voice_row.addWidget(QLabel("TTS Voice:"))
        self._voice_combo = QComboBox()
        self._voice_combo.addItems(_GEMINI_TTS_VOICES)
        voice_row.addWidget(self._voice_combo, 1)
        lang_layout.addLayout(voice_row)

        root.addWidget(lang_box)

        # ── Vocab source ──
        vocab_box = QGroupBox("Vocab source")
        vocab_layout = QVBoxLayout(vocab_box)

        self._quickstart_radio = QRadioButton("Quickstart pack:")
        self._quickstart_radio.setChecked(True)
        self._pack_combo = QComboBox()
        self._pack_combo.addItems(list(QUICKSTART_PACKS.keys()))

        qs_row = QHBoxLayout()
        qs_row.addWidget(self._quickstart_radio)
        qs_row.addWidget(self._pack_combo, 1)
        vocab_layout.addLayout(qs_row)

        self._personalized_radio = QRadioButton("Personalized  (coming soon)")
        self._personalized_radio.setEnabled(False)
        vocab_layout.addWidget(self._personalized_radio)

        root.addWidget(vocab_box)

        # ── Grammar options ──
        grammar_box = QGroupBox("Grammar options")
        grammar_layout = QVBoxLayout(grammar_box)

        tense_row = QHBoxLayout()
        self._tense_checks: dict[Tense, QCheckBox] = {}
        for group_name, tenses in _TENSE_GROUPS:
            group_box = QGroupBox(group_name)
            group_layout = QVBoxLayout(group_box)
            for tense, label in tenses:
                cb = QCheckBox(label)
                cb.setChecked(tense == Tense.SIMPLE_PRESENT)
                self._tense_checks[tense] = cb
                group_layout.addWidget(cb)
            tense_row.addWidget(group_box)
        grammar_layout.addLayout(tense_row)

        type_row = QHBoxLayout()
        type_row.addWidget(QLabel("Sentence type:"))
        self._type_checks: dict[SentenceType, QCheckBox] = {}
        for st, label in _SENTENCE_TYPE_LABELS.items():
            cb = QCheckBox(label)
            cb.setChecked(st == SentenceType.DECLARATIVE)
            self._type_checks[st] = cb
            type_row.addWidget(cb)
        grammar_layout.addLayout(type_row)

        extra_row = QHBoxLayout()
        self._preposition_check = QCheckBox("Include prepositions")
        self._possession_check = QCheckBox("Include possession")
        extra_row.addWidget(self._preposition_check)
        extra_row.addWidget(self._possession_check)
        grammar_layout.addLayout(extra_row)

        root.addWidget(grammar_box)

        # ── TTS checkbox ──
        self._tts_check = QCheckBox("Include TTS audio")
        self._tts_check.setChecked(True)
        root.addWidget(self._tts_check)

        # ── Generate button ──
        self._generate_btn = QPushButton("Generate")
        self._generate_btn.clicked.connect(self._on_generate)
        root.addWidget(self._generate_btn)

        # ── Status ──
        self._status_label = QLabel("Status: Ready")
        root.addWidget(self._status_label)

        # ── Export buttons ──
        export_row = QHBoxLayout()
        self._save_anki_btn = QPushButton("Save to Anki")
        self._save_anki_btn.setEnabled(False)
        self._save_anki_btn.clicked.connect(self._on_save_anki)

        self._save_csv_btn = QPushButton("Save as CSV")
        self._save_csv_btn.setEnabled(False)
        self._save_csv_btn.clicked.connect(self._on_save_csv)

        export_row.addWidget(self._save_anki_btn)
        export_row.addWidget(self._save_csv_btn)
        root.addLayout(export_row)

        # ── Close ──
        close_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        close_box.rejected.connect(self.reject)
        root.addWidget(close_box)

        # Persist language/voice changes
        self._lang_combo.currentTextChanged.connect(self._on_lang_changed)
        self._voice_combo.currentTextChanged.connect(self._on_voice_changed)

    # ── Config helpers ────────────────────────────────────────────────────────

    def _load_user_config(self):
        l2 = self._user_config.get("L2", "Hindi").strip().title()
        idx = self._lang_combo.findText(l2)
        if idx >= 0:
            self._lang_combo.setCurrentIndex(idx)

        voice = self._user_config.get("tts_voice", "Kore")
        idx = self._voice_combo.findText(voice)
        if idx >= 0:
            self._voice_combo.setCurrentIndex(idx)

    def _save_user_config(self):
        try:
            from aqt import mw
            mw.addonManager.saveConfig(mw.addonManager.addonFromModule(__name__), self._user_config)
        except Exception:
            pass  # Outside Anki or save failed — non-fatal

    def _on_lang_changed(self, text: str):
        self._user_config["L2"] = text
        self._save_user_config()

    def _on_voice_changed(self, text: str):
        self._user_config["tts_voice"] = text
        self._save_user_config()

    # ── Generation ────────────────────────────────────────────────────────────

    def _build_grammar_options(self) -> list[GrammarOptions]:
        selected_tenses = [t for t, cb in self._tense_checks.items() if cb.isChecked()]
        if not selected_tenses:
            selected_tenses = [Tense.SIMPLE_PRESENT]

        selected_types = [st for st, cb in self._type_checks.items() if cb.isChecked()]
        if not selected_types:
            selected_types = [SentenceType.DECLARATIVE]

        include_preposition = self._preposition_check.isChecked()
        include_possession = self._possession_check.isChecked()

        return [
            GrammarOptions(
                tense=tense,
                sentence_type=st,
                grammatical_number=None,
                include_preposition=include_preposition,
                include_possession=include_possession,
            )
            for tense in selected_tenses
            for st in selected_types
        ]

    def _build_service(self) -> SentenceDeckService:
        if not _GENAI_AVAILABLE:
            raise RuntimeError("google-genai package not found.")

        client = genai.Client(
            vertexai=True,
            project=self._infra_config.google_project_id,
            location=self._infra_config.google_location,
        )

        from domain.models.llm_options import LLMOptions
        llm_options = LLMOptions(model_id="gemini-2.0-flash")

        generator = GeminiSentenceGenerator(client=client, llm_options=llm_options)

        tts: TtsGenerator | None = None
        if self._tts_check.isChecked():
            provider = self._user_config.get("tts_provider", "gemini")
            if provider == "elevenlabs":
                tts = ElevenLabsTtsGenerator(
                    audio_dir=self._infra_config.audio_dir,
                    api_key=self._infra_config.elevenlabs_api_key,
                    voice_id=self._user_config.get("elevenlabs_voice_id", ""),
                )
            else:
                tts = GeminiTtsGenerator(
                    audio_dir=self._infra_config.audio_dir,
                    client=client,
                    voice_name=self._voice_combo.currentText(),
                )

        from infrastructure.repository.sqlite_sentence_repository import SqliteSentenceRepository
        sentence_repo = SqliteSentenceRepository(self._engine)
        validator = GeminiSentenceValidator(client=client, llm_options=llm_options)
        return SentenceDeckService(generator=generator, tts=tts, sentence_repo=sentence_repo, validator=validator)

    def _on_generate(self):
        vocab = QUICKSTART_PACKS[self._pack_combo.currentText()]
        grammar_options_list = self._build_grammar_options()
        L2 = self._lang_combo.currentText()
        with_audio = self._tts_check.isChecked()

        try:
            service = self._build_service()
        except Exception as exc:
            QMessageBox.critical(self, "Error", f"Failed to build service: {exc}")
            return

        self._generate_btn.setEnabled(False)
        self._save_anki_btn.setEnabled(False)
        self._save_csv_btn.setEnabled(False)
        self._status_label.setText("Status: Generating…")

        self._worker = _GeneratorWorker(
            service=service,
            vocab=vocab,
            L1="english",
            L2=L2,
            grammar_options_list=grammar_options_list,
            with_audio=with_audio,
        )
        self._worker.finished.connect(self._on_generation_done)
        self._worker.error.connect(self._on_generation_error)
        self._worker.start()

    def _on_generation_done(self, deck: Deck):
        self._deck = deck
        n = len(deck.entries)
        self._status_label.setText(f"Status: {n} card{'s' if n != 1 else ''} ready")
        self._generate_btn.setEnabled(True)
        self._save_anki_btn.setEnabled(True)
        self._save_csv_btn.setEnabled(True)

    def _on_generation_error(self, msg: str):
        self._status_label.setText("Status: Error — see details")
        self._generate_btn.setEnabled(True)
        QMessageBox.critical(self, "Generation failed", msg)

    # ── Export ────────────────────────────────────────────────────────────────

    def _on_save_anki(self):
        if self._deck is None:
            return
        try:
            from aqt import mw
            writer = AnkiDeckWriter(output_dir=self._infra_config.user_files_dir)
            mw.checkpoint("Add Janulus AI Deck")
            deck_name = writer.write_to_collection(self._deck)
            mw.reset()
            QMessageBox.information(self, "Done", f"Deck '{deck_name}' added to your collection.")
        except Exception as exc:
            QMessageBox.critical(self, "Import failed", str(exc))

    def _on_save_csv(self):
        if self._deck is None:
            return
        try:
            writer = CsvDeckWriter(output_dir=self._infra_config.user_files_dir)
            out_path = writer.write(self._deck)
            QMessageBox.information(
                self, "Saved", f"CSV saved to:\n{out_path}"
            )
        except Exception as exc:
            QMessageBox.critical(self, "Export failed", str(exc))
