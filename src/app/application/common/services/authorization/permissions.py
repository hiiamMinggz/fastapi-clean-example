from collections.abc import Mapping
from dataclasses import dataclass

from app.application.common.services.authorization.base import (
    Permission,
    PermissionContext,
)
from app.application.common.services.authorization.role_hierarchy import (
    SUBORDINATE_ROLES,
)
from app.domain.entities.user import User
from app.domain.entities.challenge import Challenge
from app.domain.enums.user_role import UserRole
from app.domain.enums.challenge_status import Status


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


class CanManageChallenge(Permission[ChallengeManagementContext]):
    """Base permission for challenge management.
    Ensures the user is either the creator or the assigned streamer."""
    
    def is_satisfied_by(self, context: ChallengeManagementContext) -> bool:
        return (
            context.subject.id_ == context.challenge.created_by or 
            context.subject.id_ == context.challenge.assigned_to
        )


class CanUpdateChallengeContent(Permission[ChallengeManagementContext]):
    """Permission to update challenge title and description.
    Only the creator can update content, and only when the challenge is PENDING."""
    
    def is_satisfied_by(self, context: ChallengeManagementContext) -> bool:
        return (
            context.subject.id_ == context.challenge.created_by and
            context.challenge.status == Status.PENDING
        )


class CanUpdateChallengeAmount(Permission[ChallengeManagementContext]):
    """Permission to update challenge amount.
    - Creator can update amount in PENDING status
    - Creator can increase amount in ACCEPTED status
    - Cannot update amount in other statuses"""
    
    def is_satisfied_by(self, context: ChallengeManagementContext) -> bool:
        if context.subject.id_ != context.challenge.created_by:
            return False
            
        return context.challenge.status in {Status.PENDING, Status.ACCEPTED}


class CanExtendChallengeDeadline(Permission[ChallengeManagementContext]):
    """Permission to extend challenge deadline.
    Both creator and assigned streamer can extend deadline in PENDING or ACCEPTED status."""
    
    def is_satisfied_by(self, context: ChallengeManagementContext) -> bool:
        is_involved = (
            context.subject.id_ == context.challenge.created_by or
            context.subject.id_ == context.challenge.assigned_to
        )
        return (
            is_involved and
            context.challenge.status in {Status.PENDING, Status.ACCEPTED}
        )
        
class CanChangeChallengeStatus(Permission[ChallengeManagementContext]):
    """Permission to change challenge status.
    - Creator can change status in PENDING status
    - Assigned streamer can change status in PENDING or ACCEPTED status
    - Streamer can change status in ACCEPTED status
    - User can change status in ACCEPTED status"""
    
    def is_satisfied_by(self, context: ChallengeManagementContext) -> bool:
        is_involved = (
            context.subject.id_ == context.challenge.created_by or
            context.subject.id_ == context.challenge.assigned_to
        )
        return (
            is_involved and
            context.challenge.status in {Status.PENDING, Status.ACCEPTED}
        )
