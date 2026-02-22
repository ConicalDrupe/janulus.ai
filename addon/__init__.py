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

        from aqt import gui_hooks
        from aqt.qt import QAction
        from ui.main_dialog import JanulusDialog

        def _open_dialog() -> None:
            JanulusDialog(mw, infra_config, engine, user_config).exec()

        # Keep the Tools menu entry for discoverability
        action = QAction("Janulus AI...", mw)
        action.triggered.connect(_open_dialog)
        mw.form.menuTools.addAction(action)

        # Inject a "Janulus Method" button into the main deck browser web view,
        # after the decks table so it sits just above the fixed bottom bar.
        _JANULUS_JS = """
        (function() {
            if (document.getElementById('janulus-method-btn')) return;
            var btn = document.createElement('button');
            btn.id = 'janulus-method-btn';
            btn.textContent = 'Janulus Method';
            btn.style.cssText = [
                'background:#3a86d4',
                'color:#fff',
                'border:none',
                'padding:8px 22px',
                'border-radius:5px',
                'font-size:14px',
                'font-weight:600',
                'cursor:pointer',
                'margin:4px',
                'box-shadow:0 2px 5px rgba(0,0,0,.18)',
            ].join(';');
            btn.onmouseover = function(){ this.style.background='#2563ae'; };
            btn.onmouseout  = function(){ this.style.background='#3a86d4'; };
            btn.onclick     = function(){ pycmd('janulus:open'); };
            var wrap = document.createElement('div');
            wrap.style.cssText = 'text-align:center;padding:10px 0 4px;';
            wrap.appendChild(btn);
            var table = document.querySelector('table') || document.body;
            table.parentNode.insertBefore(wrap, table.nextSibling);
        })();
        """

        def _on_deck_browser_did_render(deck_browser) -> None:
            deck_browser.web.eval(_JANULUS_JS)

        def _on_js_message(handled, message, context):
            if message == "janulus:open":
                _open_dialog()
                return (True, None)
            return handled

        gui_hooks.deck_browser_did_render.append(_on_deck_browser_did_render)
        gui_hooks.webview_did_receive_js_message.append(_on_js_message)

    except Exception as e:
        from aqt.utils import showWarning
        showWarning(f"Janulus AI failed to initialise: {e}")
