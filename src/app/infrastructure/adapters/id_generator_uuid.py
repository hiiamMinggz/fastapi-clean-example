from uuid import UUID

import uuid6

from app.domain.ports.id_generator import IdGenerator


class UuidIdGenerator(IdGenerator):
    def __call__(self) -> UUID:
        return uuid6.uuid7()
