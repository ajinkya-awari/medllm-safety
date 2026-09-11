from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ApprovalStatus(str, Enum):
    NOT_REQUESTED = "not_requested"
    REQUESTED = "requested"
    APPROVED = "approved"
    REJECTED = "rejected"


@dataclass(frozen=True)
class ApprovalRecord:
    target_type: str
    target_id: str
    revision: str
    license: str
    checksum: str
    status: ApprovalStatus
    reviewed_remote_code: bool = False


@dataclass(frozen=True)
class ApprovalValidation:
    ready_for_external_access: bool
    blockers: list[str]


def validate_approval_record(record: ApprovalRecord) -> ApprovalValidation:
    if record.target_type not in {"dataset", "model"}:
        raise ValueError("target_type must be dataset or model")
    if not record.target_id:
        raise ValueError("target_id is required")
    if record.status == ApprovalStatus.APPROVED:
        missing = [
            field_name
            for field_name in ("revision", "license", "checksum")
            if not getattr(record, field_name)
        ]
        if missing:
            raise ValueError(f"approved record missing {', '.join(missing)}")
    blockers: list[str] = []
    if record.status != ApprovalStatus.APPROVED:
        blockers.append("explicit approval is not recorded")
    if record.revision in {"", "not_accessed"}:
        blockers.append("revision has not been verified")
    if record.license in {"", "not_reviewed"}:
        blockers.append("license has not been reviewed")
    if record.checksum in {"", "not_computed"}:
        blockers.append("checksum has not been computed")
    return ApprovalValidation(ready_for_external_access=not blockers, blockers=blockers)
