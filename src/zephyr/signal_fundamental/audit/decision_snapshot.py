# [BLUEPRINT] 90_methodology_open_questions.md §22.5（C-030，L6，design→Phase 2 候选）
# [MODULE] zephyr.signal_fundamental.audit.decision_snapshot
# [DOMAIN] D_FUNDAMENTAL_SIGNAL
# [DEPENDENCIES] 无（stdlib json/dataclass）
# [CONSUMERS] Owner 周复盘溯源（C-031 置信度分层触发人工复核时呈现证据）；决策链路埋点接线待排期
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 快照不可变；JSONL append-only；可解释性缺失→degraded 降级人工复核不阻塞交易链路
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] decision_id 空/confidence 越界→ValueError
# [TESTS] tests/signal_fundamental/audit/test_decision_snapshot.py
# [A_module] module_id=MOD-SIG-DSNAP | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
D_FUNDAMENTAL_SIGNAL — 结构化决策快照（90 号 §22.5 C-030 溯源链最小实现）

裁定真源：90_methodology_open_questions.md §22.5（BM-SEL-26，Phase 2 候选，
溯源链先于协作接口建设）：
  - 缺的是"为什么这么决策"的可回溯性——Owner 复盘时唯一信任来源就是溯源链；
  - MVP 先用结构化日志（决策时快照输入因子值+触发规则 id）低成本实现 80% 价值；
  - 契约：溯源链 = 决策 id → 触发信号列表+因子贡献度+数据版本引用；
  - 降级：可解释性缺失时降级人工复核（不阻塞交易链路）——input_factors 与
    triggered_rule_ids 双空即 degraded=True，记录仍成功。

注意：本模块为 90 号 Phase2 交付物，MATURITY=testing；决策链路埋点（信号/组合/
执行各层调用点）接线挂起待 Owner（宪章 B-007 纪律）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: log_path 参数
#   fields: 参数 log_path（无注解）
#   code: decision_snapshot.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① DecisionSnapshot
#   name_en: DecisionSnapshot
#   intro: 决策快照（C-030 溯源链最小单元，不可变）。
#   desc: 决策快照（C-030 溯源链最小单元，不可变）。 Attributes: decision_id: 决策唯一标识（溯源链锚点） timestamp: 决策时间 strategy_…；公共方法（定义序）: degrade…
#   inputs: 无参数
#   outputs: 返回值
# - id: A2
#   name_zh: ② DecisionSnapshotRecorder
#   name_en: DecisionSnapshotRecorder
#   intro: 决策快照记录器——内存索引 + 可选 JSONL 追加持久化（append-only）。
#   desc: 决策快照记录器——内存索引 + 可选 JSONL 追加持久化（append-only）。 Args: log_path: JSONL 日志路径；None=纯内存模式（测试/进程内…；公共方法（定义序）: record,…
#   inputs: log_path
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: DecisionSnapshot, DecisionSnapshotRecorder
#   downstream: Owner 周复盘溯源（C-031 置信度分层触发人工复核时呈现证据）；决策链路埋点接线待排期
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# A2 --> O1
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

_logger = logging.getLogger(__name__)

__all__ = ["DecisionSnapshot", "DecisionSnapshotRecorder"]


@dataclass(frozen=True)
class DecisionSnapshot:
    """决策快照（C-030 溯源链最小单元，不可变）。

    Attributes:
        decision_id: 决策唯一标识（溯源链锚点）
        timestamp: 决策时间
        strategy_id: 策略 id
        symbol: 标的
        action: 决策动作（buy/sell/hold/...）
        input_factors: 决策时输入因子值快照
        triggered_rule_ids: 触发规则 id 列表
        factor_contributions: 因子贡献度（可选）
        data_versions: 数据版本引用（如 universe 版本/PIT 快照标识）
        confidence: 置信度 [0,1]（可选，对接 C-031 分层）
    """

    decision_id: str
    timestamp: datetime
    strategy_id: str
    symbol: str
    action: str
    input_factors: dict[str, float] = field(default_factory=dict)
    triggered_rule_ids: tuple[str, ...] = ()
    factor_contributions: dict[str, float] = field(default_factory=dict)
    data_versions: dict[str, str] = field(default_factory=dict)
    confidence: float | None = None

    def __post_init__(self) -> None:
        if not self.decision_id:
            raise ValueError("decision_id 不能为空")
        if not self.action:
            raise ValueError("action 不能为空")
        if self.confidence is not None and not 0 <= self.confidence <= 1:
            raise ValueError(f"confidence 必须在 [0,1]，实际 {self.confidence}")

    @property
    def degraded(self) -> bool:
        """可解释性缺失→降级人工复核（§22.5 降级语义，不阻塞交易链路）。"""
        return not self.input_factors and not self.triggered_rule_ids

    def to_dict(self) -> dict:
        return {
            "decision_id": self.decision_id,
            "timestamp": self.timestamp.isoformat(),
            "strategy_id": self.strategy_id,
            "symbol": self.symbol,
            "action": self.action,
            "input_factors": dict(self.input_factors),
            "triggered_rule_ids": list(self.triggered_rule_ids),
            "factor_contributions": dict(self.factor_contributions),
            "data_versions": dict(self.data_versions),
            "confidence": self.confidence,
            "degraded": self.degraded,
        }

    @classmethod
    def from_dict(cls, data: dict) -> DecisionSnapshot:
        return cls(
            decision_id=data["decision_id"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            strategy_id=data["strategy_id"],
            symbol=data["symbol"],
            action=data["action"],
            input_factors=dict(data.get("input_factors") or {}),
            triggered_rule_ids=tuple(data.get("triggered_rule_ids") or ()),
            factor_contributions=dict(data.get("factor_contributions") or {}),
            data_versions=dict(data.get("data_versions") or {}),
            confidence=data.get("confidence"),
        )


class DecisionSnapshotRecorder:
    """决策快照记录器——内存索引 + 可选 JSONL 追加持久化（append-only）。

    Args:
        log_path: JSONL 日志路径；None=纯内存模式（测试/进程内溯源）
    """

    def __init__(self, log_path: Path | None = None) -> None:
        self._log_path = Path(log_path) if log_path is not None else None
        self._records: list[DecisionSnapshot] = []

    def record(self, snapshot: DecisionSnapshot) -> None:
        """记录决策快照（内存索引 + JSONL 追加）。"""
        self._records.append(snapshot)
        if self._log_path is not None:
            self._log_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self._log_path, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(snapshot.to_dict(), ensure_ascii=False, sort_keys=True) + "\n")
        if snapshot.degraded:
            _logger.warning(
                "Decision snapshot degraded (missing factor/rule evidence): %s → 人工复核",
                snapshot.decision_id,
            )
        else:
            _logger.info("Decision snapshot recorded: %s", snapshot.decision_id)

    def get(self, decision_id: str) -> DecisionSnapshot | None:
        """按决策 id 溯源。"""
        for s in self._records:
            if s.decision_id == decision_id:
                return s
        return None

    def query(
        self,
        symbol: str | None = None,
        strategy_id: str | None = None,
    ) -> list[DecisionSnapshot]:
        """按标的/策略过滤溯源。"""
        out = self._records
        if symbol is not None:
            out = [s for s in out if s.symbol == symbol]
        if strategy_id is not None:
            out = [s for s in out if s.strategy_id == strategy_id]
        return list(out)

    @classmethod
    def load_log(cls, log_path: Path) -> list[DecisionSnapshot]:
        """读回 JSONL 日志（Owner 复盘溯源）。"""
        snapshots: list[DecisionSnapshot] = []
        with open(log_path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    snapshots.append(DecisionSnapshot.from_dict(json.loads(line)))
        return snapshots
