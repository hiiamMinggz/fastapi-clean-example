from collections.abc import Mapping
from app.domain.base import DomainError, Entity
from app.domain.challenge.challenge_status import ChallengeStatus
from app.domain.shared.value_objects.id import ChallengeHistoryId, ProductId, UserId
from app.domain.shared.value_objects.time import CreatedAt


class ChallengeHistory(Entity[ChallengeHistoryId]):
    ALLOWED_CHANGE_FIELDS = frozenset(
        {
            "title",
            "description",
            "amount",
            "fee",
            "expires_at",
        }
    )

    def __init__(
        self,
        *,
        id_: ChallengeHistoryId,
        challenge_id: ProductId,
        previous_status: ChallengeStatus | None,
        current_status: ChallengeStatus,
        changed_by: UserId | None,
        changed_at: CreatedAt,
        changes: Mapping[str, Mapping[str, object]] | None = None,
        note: str | None = None,
    ) -> None:
        super().__init__(id_=id_)
        self.challenge_id = challenge_id
        self.previous_status = previous_status
        self.current_status = current_status
        self.changed_by = changed_by
        self.changed_at = changed_at
        self.changes = changes
        self.note = note
        self.validate()

    def validate(self) -> None:
        if (
            self.previous_status is not None
            and self.previous_status == self.current_status
            and self.changes is None
        ):
            raise DomainError(
                "Challenge history transition must change the status when no field changes are provided.",
            )
        self._validate_changes()

    def _validate_changes(self) -> None:
        if self.changes is None:
            return
        if not self.changes:
            raise DomainError(
                "Challenge history changes must be non-empty when provided.",
            )
        for field, change in self.changes.items():
            if field not in self.ALLOWED_CHANGE_FIELDS:
                raise DomainError(
                    f"Challenge history changes cannot include '{field}'.",
                )
            if not isinstance(change, Mapping):
                raise DomainError(
                    f"Challenge history change for '{field}' must be a mapping.",
                )
            if "from" not in change or "to" not in change:
                raise DomainError(
                    f"Challenge history change for '{field}' must include 'from' and 'to'.",
                )
            if change.get("from") == change.get("to"):
                raise DomainError(
                    f"Challenge history change for '{field}' must differ.",
                )

    @classmethod
    def build_changes(
        cls,
        *,
        title_from: object | None = None,
        title_to: object | None = None,
        description_from: object | None = None,
        description_to: object | None = None,
        amount_from: object | None = None,
        amount_to: object | None = None,
        expires_at_from: object | None = None,
        expires_at_to: object | None = None,
    ) -> Mapping[str, Mapping[str, object]]:
        changes: dict[str, dict[str, object]] = {}
        cls._add_change(changes, "title", title_from, title_to)
        cls._add_change(changes, "description", description_from, description_to)
        cls._add_change(changes, "amount", amount_from, amount_to)
        cls._add_change(changes, "expires_at", expires_at_from, expires_at_to)
        return changes

    @classmethod
    def _add_change(
        cls,
        changes: dict[str, dict[str, object]],
        field: str,
        before: object | None,
        after: object | None,
    ) -> None:
        if before == after:
            return
        if before is None and after is None:
            return
        changes[field] = {"from": before, "to": after}
