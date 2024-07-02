from abc import ABC, abstractmethod

from ..level import Level

__all__ = ["Slot"]


class Slot(ABC):
    __slots__ = ()

    def __bool__(self) -> bool:
        """Return whether this slot is filled."""
        return self.load() is not None

    @abstractmethod
    def load(self) -> Level | None:
        pass

    @abstractmethod
    def save(self, data: Level | None, /) -> None:
        pass
