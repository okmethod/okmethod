"""アクティブデッキのセレクタ。

デッキを切り替える際はこのファイルを変更する。
"""

# メガルカリオデッキ
from .mega_lucario.deck_strategy import MegaLucarioDeckStrategy as DeckStrategy

__all__ = ["DeckStrategy"]
