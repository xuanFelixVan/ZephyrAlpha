from __future__ import annotations

from datetime import date
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class ChangeImpact(str, Enum):
    BREAKING = "Breaking"
    ENHANCEMENT = "Enhancement"
    FIX = "Fix"


class ChangeRecord(BaseModel):
    date: str
    version: str
    impact: ChangeImpact
    sections_affected: str
    description: str
    author: str = "AI-assisted, Owner ratified"


CHANGELOG: list[ChangeRecord] = [
    ChangeRecord(
        date="2026-02-15",
        version="v1.0.0",
        impact=ChangeImpact.BREAKING,
        sections_affected="§1-50 全局",
        description="初始蓝图创建",
        author="AI 辅助 Owner 终裁",
    ),
]


def append_change(record: ChangeRecord) -> None:
    CHANGELOG.insert(0, record)


def get_latest() -> Optional[ChangeRecord]:
    return CHANGELOG[0] if CHANGELOG else None


def latest_version() -> str:
    return CHANGELOG[0].version if CHANGELOG else "v0.1.0"
