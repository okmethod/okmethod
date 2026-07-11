"""アクティブデッキのセレクタ。

デッキを切り替える際は `active_deck` ファイルを変更する。
"""

from pathlib import Path
from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .fuudin.deck_strategy import FuudinDeckStrategy
    from .mega_lucario.deck_strategy import MegaLucarioDeckStrategy

_active = (Path(__file__).parent / "active_deck").read_text().strip()

DeckStrategy: "Union[type[MegaLucarioDeckStrategy], type[FuudinDeckStrategy]]"

if _active == "mega_lucario":
    from .mega_lucario.deck_strategy import MegaLucarioDeckStrategy as DeckStrategy
elif _active == "fuudin":
    from .fuudin.deck_strategy import FuudinDeckStrategy as DeckStrategy
else:
    raise ValueError(f"Unknown deck: {_active}")

__all__ = ["DeckStrategy"]
