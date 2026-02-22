import sys

try:
    from aqt import mw
except ImportError:
    pass  # Running outside of Anki (e.g. tests)
else:
    try:
        # Creating user_data directory - for caching data
        addon_dir = Path(__file__).parent
        data_dir = addon_dir / "user_data"
        data_dir.mkdir(exist_ok=True)

        # Adding addon root and external libraries to path
        sys.path.insert(0, str(addon_dir))
        sys.path.insert(0, str(addon_dir / "external"))
