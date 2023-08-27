# output.py - tools for managing terminal output

from dataclasses       import dataclass
from typing            import Any

from rich              import box
from rich.panel        import Panel

from frplib.env        import environment


@dataclass(frozen=True)
class RichQuantity:
    this: Any

    def __str__(self) -> str:
        return str(self.this)

    def __repr__(self) -> str:
        return repr(self.this)

    def __frplib_repr__(self):
        if environment.ascii_only:
            return str(self)
        return Panel(str(self), expand=False, box=box.SQUARE)

@dataclass(frozen=True)
class TitledRichQuantity:
    this: Any
    title: str = ''

    def __str__(self) -> str:
        return self.title + str(self.this)

    def __repr__(self) -> str:
        return repr(self.this)

    def __frplib_repr__(self):
        if environment.ascii_only:
            return str(self)
        return Panel(str(self), expand=False, box=box.SQUARE)

@dataclass(frozen=True)
class RichFacade:
    this: Any
    facade: str = ''

    def __str__(self) -> str:
        if self.facade:
            return self.facade
        else:
            return str(self.this)

    def __repr__(self) -> str:
        return repr(self.this)

    def __frplib_repr__(self):
        if environment.ascii_only:
            return str(self)
        return Panel(str(self), expand=False, box=box.SQUARE)

@dataclass(frozen=True)
class TitledRichFacade:
    this: Any
    facade: str = ''
    title: str = ''

    def __str__(self) -> str:
        if self.facade:
            return self.title + self.facade
        else:
            return self.title + str(self.this)

    def __repr__(self) -> str:
        return repr(self.this)

    def __frplib_repr__(self):
        if environment.ascii_only:
            return str(self)
        return Panel(str(self), expand=False, box=box.SQUARE)
