# [BLUEPRINT] MOD-INF-055 | docs/03_modules/MOD-INF-055/
# [MODULE] zephyr.security.ops.ops_maturity
# [DOMAIN] D_SECURITY
# [DEPENDENCIES] zephyr.shared.utils.time_utils
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 逐级解锁禁止跳级;每级解锁MUST连续N周零TNR违规且判定留痕;A-L2人工采纳率MUST留痕;A-L3不在本件范围MUST拒绝
# [MODIFY-GUARD] 16_ai_security_ops.md §4.4 P2-2
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] OpsMaturityError(ZA-SC-0037)
# [TESTS] tests/security/ops/test_ops_maturity.py
# [A_module] module_id=MOD-INF-055 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
自治运维成熟度 A-L0→A-L2 状态机（16号文 §4.4 P2-2 + §3.7）。

A-L 系是「运维闭环的自治深度」标尺（00_index §3.4；与 15号文三套标尺为
独立轴、不建映射，§6 Q4 已裁定）：

- **A-L0 只记录**：事件流只落盘，不告警不动作；
- **A-L1 告警**：事件流触发告警通道；
- **A-L2 自愈建议**：产出修复建议，人工采纳后执行（采纳率留痕）。

解锁规则（§3.7）：每升一级 MUST 满足「上一级连续 N 周零 TNR 违规」，
解锁判定（批准与拒绝）全部 append-only 留痕；禁止跳级（A-L0 直解 A-L2
被拒）；**A-L3 渐进自治不在本件范围**——按 §3.7 实证评估后单独裁定，
本件对 A-L3 请求一律 ``OpsMaturityError`` 拒绝。

TNR 违规（修复不可撤销/修复后恶化）一旦记录，连续零违规周数归零重计。
本件只做状态机与留痕；Learn 回写（fix_pattern_miner 周期挖掘）复用既有
``auto_fix_engine/fix_pattern_miner.py``，不在本件重复实现。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: config 参数
#   fields: 参数 config（无注解）
#   code: ops_maturity.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① OpsMaturityTracker
#   name_en: OpsMaturityTracker
#   intro: A-L0→A-L2 成熟度状态机 + 解锁/违规/采纳留痕（append-only 台账）。
#   desc: A-L0→A-L2 成熟度状态机 + 解锁/违规/采纳留痕（append-only 台账）。 不变量： - 逐级解锁，禁止跳级；A-L3 请求 MUST 拒绝（不在本件范围）；…；公共方法（定义序）: current_…
#   inputs: config
#   outputs: 返回值
#   （注：A1 之后另有 5 个公共定义未列入（含 5 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（6 定义）
#   name_en: public defs
#   intro: OpsMaturityTracker
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Final

from zephyr.shared.utils.time_utils import now_iso

logger = logging.getLogger(__name__)

__all__: Final = [
    "MaturityConfig",
    "OpsMaturityError",
    "OpsMaturityLevel",
    "OpsMaturityTracker",
    "UnlockDecision",
    "UnlockEvidence",
]

DEFAULT_REQUIRED_WEEKS_ZERO_TNR: Final[int] = 2


class OpsMaturityError(Exception):
    """ZA-SC-0037: 成熟度状态机操作非法（跳级/A-L3 越界/缺 reviewer）。"""

    error_code = "ZA-SC-0037"


class OpsMaturityLevel(str, Enum):
    """运维闭环自治深度三级（本件范围 A-L0~A-L2；A-L3 另案裁定）。"""

    A_L0 = "A-L0"
    A_L1 = "A-L1"
    A_L2 = "A-L2"


_NEXT_LEVEL: Final[dict[OpsMaturityLevel, OpsMaturityLevel]] = {
    OpsMaturityLevel.A_L0: OpsMaturityLevel.A_L1,
    OpsMaturityLevel.A_L1: OpsMaturityLevel.A_L2,
}


@dataclass(frozen=True)
class UnlockEvidence:
    """解锁证据：连续零 TNR 违规周数（由运维记录统计供给）。"""

    weeks_zero_tnr: int
    note: str = ""


@dataclass(frozen=True)
class UnlockDecision:
    """解锁判定留痕（批准与拒绝均落台账）。"""

    ts: str
    from_level: str
    to_level: str
    approved: bool
    reason: str
    weeks_zero_tnr: int


@dataclass(frozen=True)
class MaturityConfig:
    """成熟度追踪配置（参数收敛 dataclass）。"""

    state_path: Path
    ledger_path: Path
    required_weeks_zero_tnr: int = DEFAULT_REQUIRED_WEEKS_ZERO_TNR


class OpsMaturityTracker:
    """A-L0→A-L2 成熟度状态机 + 解锁/违规/采纳留痕（append-only 台账）。

    不变量：
    - 逐级解锁，禁止跳级；A-L3 请求 MUST 拒绝（不在本件范围）；
    - 解锁 MUST 满足连续 N 周零 TNR 违规（N 可配，默认 2，16号文 P2-1 口径）；
    - 解锁判定（批准/拒绝）、TNR 违规、A-L2 人工采纳 MUST 全部留痕；
    - TNR 违规 MUST 归零连续零违规周数。
    """

    def __init__(self, config: MaturityConfig) -> None:
        self._config = config
        self._config.state_path.parent.mkdir(parents=True, exist_ok=True)
        self._config.ledger_path.parent.mkdir(parents=True, exist_ok=True)
        self._state = self._load_state()

    # ── 状态查询 ─────────────────────────────────────────────────────

    def current_level(self) -> OpsMaturityLevel:
        return OpsMaturityLevel(self._state["level"])

    def weeks_zero_tnr_streak(self) -> int:
        return int(self._state["weeks_zero_tnr_streak"])

    # ── 解锁 ─────────────────────────────────────────────────────────

    def request_unlock(self, to_level: OpsMaturityLevel | str, evidence: UnlockEvidence) -> UnlockDecision:
        """申请解锁：逐级 + 连续 N 周零 TNR 违规双条件；判定留痕。"""
        target = self._parse_level(to_level)
        current = self.current_level()
        expected = _NEXT_LEVEL.get(current)
        if target is not expected:
            raise OpsMaturityError(
                f"禁止跳级/回退解锁: {current.value} -> {target.value}（仅允许逐级 {current.value} -> {expected.value if expected else '∅'}）"
            )
        required = self._config.required_weeks_zero_tnr
        approved = evidence.weeks_zero_tnr >= required
        reason = (
            f"连续零 TNR 违规 {evidence.weeks_zero_tnr} 周 ≥ 要求 {required} 周"
            if approved
            else f"连续零 TNR 违规 {evidence.weeks_zero_tnr} 周 < 要求 {required} 周"
        )
        decision = UnlockDecision(
            ts=now_iso(),
            from_level=current.value,
            to_level=target.value,
            approved=approved,
            reason=reason,
            weeks_zero_tnr=evidence.weeks_zero_tnr,
        )
        self._append_ledger(
            {
                "kind": "unlock_decision",
                "ts": decision.ts,
                "from_level": decision.from_level,
                "to_level": decision.to_level,
                "approved": decision.approved,
                "reason": decision.reason,
                "weeks_zero_tnr": decision.weeks_zero_tnr,
                "note": evidence.note,
            }
        )
        if approved:
            self._state["level"] = target.value
        self._state["weeks_zero_tnr_streak"] = evidence.weeks_zero_tnr
        self._save_state()
        logger.info("成熟度解锁判定: %s -> %s approved=%s", current.value, target.value, approved)
        return decision

    # ── TNR 违规 ─────────────────────────────────────────────────────

    def record_tnr_violation(self, description: str) -> None:
        """记录一次 TNR 违规：连续零违规周数归零 + 留痕。"""
        if not description:
            raise OpsMaturityError("TNR 违规记录 MUST 含描述")
        self._state["weeks_zero_tnr_streak"] = 0
        self._save_state()
        self._append_ledger(
            {
                "kind": "tnr_violation",
                "ts": now_iso(),
                "level": self._state["level"],
                "description": description,
            }
        )
        logger.warning("TNR 违规已记录，连续零违规周数归零: %s", description)

    # ── A-L2 人工采纳率留痕 ──────────────────────────────────────────

    def record_adoption(self, suggestion_id: str, *, adopted: bool, reviewer: str) -> None:
        """记录自愈建议的人工采纳（A-L2 状态采纳率留痕；reviewer MUST 非空）。"""
        if not suggestion_id or not reviewer:
            raise OpsMaturityError("采纳记录 MUST 含 suggestion_id 与 reviewer（human_gated）")
        self._append_ledger(
            {
                "kind": "adoption",
                "ts": now_iso(),
                "level": self._state["level"],
                "suggestion_id": suggestion_id,
                "adopted": bool(adopted),
                "reviewer": reviewer,
            }
        )

    def adoption_stats(self) -> dict[str, Any]:
        """人工采纳率统计（total/adopted/rate；无记录时 rate=None）。"""
        adoptions = [e for e in self._ledger_entries() if e.get("kind") == "adoption"]
        total = len(adoptions)
        adopted = sum(1 for e in adoptions if e.get("adopted"))
        return {
            "total": total,
            "adopted": adopted,
            "rate": (adopted / total) if total else None,
        }

    # ── 内部 ─────────────────────────────────────────────────────────

    @staticmethod
    def _parse_level(to_level: OpsMaturityLevel | str) -> OpsMaturityLevel:
        if isinstance(to_level, OpsMaturityLevel):
            return to_level
        try:
            return OpsMaturityLevel(str(to_level))
        except ValueError as exc:
            raise OpsMaturityError(
                f"非法/越界成熟度等级: {to_level!r}（本件范围 A-L0~A-L2；A-L3 按 §3.7 单独裁定）"
            ) from exc

    def _load_state(self) -> dict[str, Any]:
        if self._config.state_path.exists():
            with open(self._config.state_path, encoding="utf-8") as fh:
                state = json.load(fh)
            if "level" in state and "weeks_zero_tnr_streak" in state:
                return state
        return {"level": OpsMaturityLevel.A_L0.value, "weeks_zero_tnr_streak": 0}

    def _save_state(self) -> None:
        tmp = self._config.state_path.with_name(self._config.state_path.name + ".tmp")
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(self._state, fh, ensure_ascii=False)
        tmp.replace(self._config.state_path)

    def _append_ledger(self, entry: dict[str, Any]) -> None:
        with open(self._config.ledger_path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, ensure_ascii=False, separators=(",", ":")) + "\n")

    def _ledger_entries(self) -> list[dict[str, Any]]:
        if not self._config.ledger_path.exists():
            return []
        with open(self._config.ledger_path, encoding="utf-8") as fh:
            return [json.loads(line) for line in fh if line.strip()]
