"""
Module Birth Registry — 模块出生登记表 (盲点 #54)
特性：
  - 记录每个模块的创建时间/版本/依赖
  - 与 blueprint 版本对比，自动标记过期模块
"""
import time
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class ModuleBirthRecord:
    module_name: str
    created_at: str
    created_version: str
    dependencies: list[str] = field(default_factory=list)
    last_updated: str = ""
    expired: bool = False


class ModuleBirthRegistry:
    """
    模块出生登记表 (盲点 #54)
    """

    def __init__(self):
        self._records: dict[str, ModuleBirthRecord] = {}
        self._current_version = "2.6.0"

    def register(self, module_name: str, created_version: str = "",
                 dependencies: Optional[list[str]] = None):
        now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        record = ModuleBirthRecord(
            module_name=module_name,
            created_at=now,
            created_version=created_version or self._current_version,
            dependencies=dependencies or [],
            last_updated=now,
        )
        self._records[module_name] = record
        return record

    def check_expiration(self) -> list[str]:
        expired = []
        for name, record in self._records.items():
            if record.created_version != self._current_version:
                record.expired = True
                expired.append(name)
        return expired

    def get_all(self) -> dict[str, dict]:
        return {
            name: {
                "created_at": r.created_at,
                "version": r.created_version,
                "expired": r.expired,
                "dependencies": r.dependencies,
            }
            for name, r in self._records.items()
        }
