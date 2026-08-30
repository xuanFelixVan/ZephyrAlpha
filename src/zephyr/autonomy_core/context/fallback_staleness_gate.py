# [BLUEPRINT] MOD-CONTEXT_ENGINE | docs/03_modules/_cross_layer/context_engine/blueprint.md
# [MODULE] zephyr.autonomy_core.context.fallback_staleness_gate
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.autonomy_core.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-CONTEXT_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
fallback_staleness_gate.py — 兜底层自腐检测 (B13, DD87, TASK-017)

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: defaults_file 参数
#   fields: 参数 defaults_file（无注解）
#   code: fallback_staleness_gate.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① FallbackStalenessGate
#   name_en: FallbackStalenessGate
#   intro: embedded_defaults SHA256 + age check; >90d alert (DD87).
#   desc: embedded_defaults SHA256 + age check; >90d alert (DD87).；公共方法（定义序）: file, check；源码 L67-L97
#   inputs: defaults_file
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: FallbackStalenessGate
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

import hashlib
from dataclasses import dataclass
from datetime import UTC, datetime, timezone
from pathlib import Path
from typing import Final

UTC: Final[timezone] = UTC


@dataclass
class StalenessReport:
    file_path: str
    sha256: str
    age_days: float
    is_stale: bool
    alert_message: str


class FallbackStalenessGate:
    """embedded_defaults SHA256 + age check; >90d alert (DD87)."""

    def __init__(self, defaults_file: str | Path = "AGENTS.md") -> None:
        self._file = Path(defaults_file)

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def file(self):
        """只读：file（Stage 4 公共化）。"""
        return self._file

    @file.setter
    def file(self, value):
        """写入：file（Stage 4 公共化）。"""
        self._file = value

    def check(self) -> StalenessReport:
        exists = self._file.exists()
        sha = hashlib.sha256(self._file.read_bytes()).hexdigest() if exists else ""
        age = 0.0
        if exists:
            age = (datetime.now(UTC) - datetime.fromtimestamp(self._file.stat().st_mtime, UTC)).total_seconds() / 86400
        is_stale = age > 90
        return StalenessReport(
            file_path=str(self._file),
            sha256=sha[:16],
            age_days=round(age, 1),
            is_stale=is_stale,
            alert_message=f"AGENTS.md is {age:.0f} days old — needs review" if is_stale else "OK",
        )
