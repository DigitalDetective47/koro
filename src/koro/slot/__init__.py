from abc import ABC, abstractmethod

from ..stage import Stage

__all__ = ["Slot"]


class Slot(ABC):
    __slots__ = ()

    def __bool__(self) -> bool:
        """Return whether this slot is filled."""
        return self.load() is not None

    @abstractmethod
    def load(self) -> Stage | None:
        pass

    @abstractmethod
    def save(self, data: Stage | None, /) -> None:
        pass
