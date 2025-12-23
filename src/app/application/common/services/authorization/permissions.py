from collections.abc import Mapping
from dataclasses import dataclass

from app.application.common.services.authorization.base import (
    Permission,
    PermissionContext,
)
from app.application.common.services.authorization.role_hierarchy import (
    SUBORDINATE_ROLES,
)
from app.domain.user.user import User
from app.domain.challenge.challenge import Challenge
from app.domain.user.user_role import UserRole
from app.domain.challenge.challenge_status import Status


@dataclass(frozen=True, kw_only=True)
class UserManagementContext(PermissionContext):
    subject: User
    target: User


class CanManageSelf(Permission[UserManagementContext]):
    def is_satisfied_by(self, context: UserManagementContext) -> bool:
        return context.subject == context.target


class CanManageSubordinate(Permission[UserManagementContext]):
    def __init__(
        self,
        role_hierarchy: Mapping[UserRole, set[UserRole]] = SUBORDINATE_ROLES,
    ) -> None:
        self._role_hierarchy = role_hierarchy

    def is_satisfied_by(self, context: UserManagementContext) -> bool:
        allowed_roles = self._role_hierarchy.get(context.subject.role, set())
        return context.target.role in allowed_roles


@dataclass(frozen=True, kw_only=True)
class RoleManagementContext(PermissionContext):
    subject: User
    target_role: UserRole


class CanManageRole(Permission[RoleManagementContext]):
    def __init__(
        self,
        role_hierarchy: Mapping[UserRole, set[UserRole]] = SUBORDINATE_ROLES,
    ) -> None:
        self._role_hierarchy = role_hierarchy

    def is_satisfied_by(self, context: RoleManagementContext) -> bool:
        allowed_roles = self._role_hierarchy.get(context.subject.role, set())
        return context.target_role in allowed_roles


@dataclass(frozen=True, kw_only=True)
class ChallengeManagementContext(PermissionContext):
    subject: User  # The user attempting the action
    challenge: Challenge  # The challenge being modified

class CanUpdateChallengeContent(Permission[ChallengeManagementContext]):
    """Permission to update challenge title and description.
    Creator can update challenge content"""
    
    def is_satisfied_by(self, context: ChallengeManagementContext) -> bool:
        return context.subject.id_ == context.challenge.created_by


class CanUpdateChallengeAmount(Permission[ChallengeManagementContext]):
    """Permission to update challenge amount.
    Creator can update or increase challenge amount"""
    
    def is_satisfied_by(self, context: ChallengeManagementContext) -> bool:
        return context.subject.id_ == context.challenge.created_by


class CanExtendChallengeDeadline(Permission[ChallengeManagementContext]):
    """Permission to extend challenge deadline.
    Creator can extend deadline"""
    
    def is_satisfied_by(self, context: ChallengeManagementContext) -> bool:
        return context.subject.id_ == context.challenge.created_by
        
class CanChangeChallengeStatus(Permission[ChallengeManagementContext]):
    """Permission to change challenge status.
    Both the creator and the assignee can change status."""
    
    def is_satisfied_by(self, context: ChallengeManagementContext) -> bool:
        is_involved = (
            context.subject.id_ == context.challenge.created_by or
            context.subject.id_ == context.challenge.assigned_to
        )
        return is_involved
