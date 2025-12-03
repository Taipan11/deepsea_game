# ui/style_utils.py
import os
import sys
from PySide6.QtWidgets import QWidget

def load_styles(widget: QWidget):
    """Applique le fichier styles.qss au widget (fenêtre, dialog, etc.)."""
    qss_path = os.path.join(os.path.dirname(__file__), "styles.qss")
    try:
        with open(qss_path, "r", encoding="utf-8") as f:
            widget.setStyleSheet(f.read())
    except FileNotFoundError:
        print(f"[WARN] Fichier de style introuvable : {qss_path}", file=sys.stderr)
