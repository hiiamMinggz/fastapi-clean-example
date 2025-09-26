from abc import abstractmethod
from uuid import UUID


class IdGenerator:
    @abstractmethod
    def __call__(self) -> UUID: ...
