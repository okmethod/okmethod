"""アクティブデッキのセレクタ。

デッキを切り替える際は `active_deck` ファイルを変更する。
"""

from pathlib import Path

_active = (Path(__file__).parent / "active_deck").read_text().strip()

if _active == "mega_lucario":
    from .mega_lucario.deck_strategy import MegaLucarioDeckStrategy as DeckStrategy
else:
    raise ValueError(f"Unknown deck: {_active}")

__all__ = ["DeckStrategy"]
