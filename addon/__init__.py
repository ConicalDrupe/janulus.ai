import sys
from pathlib import Path

try:
    from aqt import mw
except ImportError:
    pass  # Running outside of Anki (e.g. tests)
else:
    try:
        addon_dir = Path(__file__).parent

        # Adding addon root and external libraries to path
        sys.path.insert(0, str(addon_dir))
        sys.path.insert(0, str(addon_dir / "external"))

        from addon_config import load_infra_config, make_engine

        infra_config = load_infra_config()
        engine = make_engine(infra_config)

        # Anki merges config.json defaults with per-profile user overrides
        user_config = mw.addonManager.getConfig(__name__)

    except Exception as e:
        from aqt.utils import showWarning
        showWarning(f"Janulus AI failed to initialise: {e}")
