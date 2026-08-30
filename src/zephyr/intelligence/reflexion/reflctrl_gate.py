# [BLUEPRINT] MOD-REFLEXION_AGENT | docs/02_enterprise_architecture/09_ai_architecture/implementation_plans/12_reflexion_multi_agent.md | §4.3-P1-1
# [MODULE] zephyr.intelligence.reflexion.reflctrl_gate
# [DOMAIN] D_INTELLIGENCE
# [DEPENDENCIES] zephyr.shared.io.paths(MAIN_REPO_ROOT)
# [CONSUMERS] tests/intelligence/test_reflctrl_gate.py
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 规则外触发请求必拒(fail-closed); 每次放行 matched_rules 恒非空可追溯; 单任务反思轮次上限强制规则不豁免; token 仅放行计; 非法 layer/requested_level 即 ValueError; 落盘 IO 失败不阻断裁决
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ValueError — 非法 layer/requested_level 即抛, fail-closed; 错误消息零 session_id
# [TESTS] tests/intelligence/test_reflctrl_gate.py
# [A_module] module_id=MOD-REFLEXION_AGENT | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
ReflCtrl 反思频率闸门（12号文 §3.4/§4.3 P1-1）.

定位：反思触发的前置门卫——想反思必须报上哪条显式规则让你来的，防无闸门反思
循环把 token 烧光。§3.4 显式规则集全量落地（默认值即源设计参数）：

- L1 强制三条件：执行结果与预期偏差 >20% / 风控否决 / 执行失败。
- Agent-R 轨迹内异常四场景（盘后轨迹复盘异常检测规则，实时档不启用）：
  信号 >2σ 偏离 / 滑点 ×2 / 风控参数漂移 >10% / 状态转换概率 >90% 未触发。
- HITL 低置信触发：置信 <0.70 → L1；<0.50 → L1+L2。
- 分层频率：执行层仅异常触发 / 战术层每 5 次同类任务 L1 / 战略层每次任务 L1。
- L2 累积触发：同类任务累积 N=5 次允许 L2。
- 频率控制决策矩阵：连续优秀 ≥5 跳过 L1 / 连续正常 ≥3 仅 L2 聚合 /
  严重偏差 L1+L2 / 失败 L1+L2+L3；强制规则优先于矩阵跳过。
- 单任务反思轮次上限默认 3（强制规则不豁免）。

可审计：每次裁决（放行/拒绝）写 reflctrl_decisions.jsonl；token 消耗仅放行计，
写 reflctrl_token_stats.jsonl，total_estimated_tokens() 可汇总。
规则可配置：ReflCtrlConfig 注入覆盖全部阈值。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: config 参数
#   fields: 参数 config（无注解）
#   code: reflctrl_gate.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: stats_root 参数
#   fields: 参数 stats_root（无注解）
#   code: reflctrl_gate.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① ReflCtrlGate
#   name_en: ReflCtrlGate
#   intro: ReflCtrl 频率闸门：显式规则集裁决 + 全量留痕 + token 统计.
#   desc: ReflCtrl 频率闸门：显式规则集裁决 + 全量留痕 + token 统计.；公共方法（定义序）: config, decide, total_estimated_tokens；源码 L171-L329
#   inputs: config stats_root
#   outputs: 返回值
#   （注：A1 之后另有 3 个公共定义未列入（含 3 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（4 定义）
#   name_en: public defs
#   intro: ReflCtrlGate
#   downstream: tests/intelligence/test_reflctrl_gate.py
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> O1
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Final

from zephyr.shared.io.paths import MAIN_REPO_ROOT

logger = logging.getLogger(__name__)

# ── 显式规则 ID 集（12号文 §3.4） ─────────────────────────────
RULE_L1_FORCE_DEVIATION: Final[str] = "L1-FORCE-DEVIATION"
RULE_L1_FORCE_RISK_VETO: Final[str] = "L1-FORCE-RISK-VETO"
RULE_L1_FORCE_EXECUTION_FAILURE: Final[str] = "L1-FORCE-EXECUTION-FAILURE"
RULE_AGENT_R_SIGNAL_SIGMA: Final[str] = "AGENT-R-SIGNAL-SIGMA"
RULE_AGENT_R_SLIPPAGE: Final[str] = "AGENT-R-SLIPPAGE"
RULE_AGENT_R_RISK_PARAM: Final[str] = "AGENT-R-RISK-PARAM"
RULE_AGENT_R_REGIME: Final[str] = "AGENT-R-REGIME"
RULE_HITL_CONFIDENCE_L1: Final[str] = "HITL-CONFIDENCE-L1"
RULE_HITL_CONFIDENCE_L2: Final[str] = "HITL-CONFIDENCE-L2"
RULE_LAYER_TACTICAL_NTH: Final[str] = "LAYER-TACTICAL-NTH"
RULE_LAYER_STRATEGIC_ALWAYS: Final[str] = "LAYER-STRATEGIC-ALWAYS"
RULE_L2_ACCUMULATED: Final[str] = "L2-ACCUMULATED"

# ── 拒绝原因码 ────────────────────────────────────────────────
DENIED_NO_RULE: Final[str] = "DENIED-NO-RULE"
DENIED_MAX_ROUNDS: Final[str] = "DENIED-MAX-ROUNDS"
DENIED_EXCELLENT_STREAK: Final[str] = "DENIED-EXCELLENT-STREAK"
DENIED_NORMAL_STREAK: Final[str] = "DENIED-NORMAL-STREAK"

VALID_LAYERS: Final[frozenset[str]] = frozenset({"execution", "tactical", "strategic"})
VALID_LEVELS: Final[frozenset[str]] = frozenset({"L1", "L2", "L3"})

_DECISIONS_FILE: Final[str] = "reflctrl_decisions.jsonl"
_TOKEN_STATS_FILE: Final[str] = "reflctrl_token_stats.jsonl"


@dataclass(frozen=True)
class ReflCtrlConfig:
    """闸门阈值配置（默认值即 12号文 §3.4 源设计参数；注入覆盖即生效）."""

    deviation_force_pct: float = 20.0  # L1 强制：偏差 >20%
    signal_sigma_force: float = 2.0  # Agent-R：信号 >2σ 偏离
    slippage_ratio_force: float = 2.0  # Agent-R：滑点 ×2
    risk_param_deviation_force_pct: float = 10.0  # Agent-R：风控参数漂移 >10%
    regime_transition_force_pct: float = 90.0  # Agent-R：状态转换概率 >90% 未触发
    hitl_confidence_l1: float = 0.70  # HITL：<0.70 → L1
    hitl_confidence_l2: float = 0.50  # HITL：<0.50 → L1+L2
    tactical_nth: int = 5  # 战术层每 5 次同类任务 L1
    l2_accumulated_n: int = 5  # L2 累积 N=5
    excellent_streak_skip: int = 5  # 决策矩阵：连续优秀 ≥5 跳过 L1
    normal_streak_l2_only: int = 3  # 决策矩阵：连续正常 ≥3 仅 L2 聚合
    max_rounds_per_task: int = 3  # 单任务反思轮次上限（强制规则不豁免）


@dataclass(frozen=True)
class ReflectionRequest:
    """单次反思触发请求（执行层上报的上下文快照）."""

    task_id: str
    layer: str  # execution | tactical | strategic
    requested_level: str  # L1 | L2 | L3
    deviation_pct: float = 0.0  # 执行结果与预期偏差 %
    risk_vetoed: bool = False  # 风控否决
    outcome: str = ""  # success | failure | ""
    signal_sigma_deviation: float = 0.0  # Agent-R：信号 σ 偏离
    slippage_ratio: float = 0.0  # Agent-R：滑点倍数
    risk_param_deviation_pct: float = 0.0  # Agent-R：风控参数漂移 %
    regime_transition_prob_pct: float = 0.0  # Agent-R：状态转换概率 %
    regime_triggered: bool = False  # Agent-R：状态转换是否已触发应对
    eval_confidence: float = 1.0  # HITL 评估置信度 0~1
    similar_task_count: int = 0  # 同类任务累计次数
    excellent_streak: int = 0  # 连续优秀次数
    normal_streak: int = 0  # 连续正常次数
    severity: str = ""  # severe | ""
    reflection_round: int = 0  # 本任务已反思轮次
    estimated_tokens: int = 0  # 本次反思预估 token

    def __post_init__(self) -> None:
        if self.layer not in VALID_LAYERS:
            raise ValueError(f"ReflectionRequest.layer 非法取值拒收: {self.layer!r}（合法={sorted(VALID_LAYERS)}）")
        if self.requested_level not in VALID_LEVELS:
            raise ValueError(
                f"ReflectionRequest.requested_level 非法取值拒收: {self.requested_level!r}"
                f"（合法={sorted(VALID_LEVELS)}）"
            )


@dataclass(frozen=True)
class ReflCtrlDecision:
    """闸门裁决（放行恒带非空 matched_rules 可追溯；拒绝带 denied_by 原因码）."""

    allowed: bool
    matched_rules: tuple[str, ...] = ()
    granted_levels: tuple[str, ...] = ()
    denied_by: str = ""


class ReflCtrlGate:
    """ReflCtrl 频率闸门：显式规则集裁决 + 全量留痕 + token 统计."""

    def __init__(
        self,
        config: ReflCtrlConfig | None = None,
        stats_root: str | Path | None = None,
    ) -> None:
        self._config = config or ReflCtrlConfig()
        self._stats_root = Path(stats_root) if stats_root else MAIN_REPO_ROOT / "data" / "brain" / "reflctrl"

    @property
    def config(self) -> ReflCtrlConfig:
        return self._config

    # ── 裁决 ──────────────────────────────────────────────────

    def decide(self, request: ReflectionRequest) -> ReflCtrlDecision:
        """裁决一次反思触发请求（规则外必拒；轮次上限强制规则不豁免）."""
        cfg = self._config
        if request.reflection_round >= cfg.max_rounds_per_task:
            decision = ReflCtrlDecision(allowed=False, denied_by=DENIED_MAX_ROUNDS)
            self._trace(request, decision)
            return decision
        matched, granted = self._match_rules(request)
        if matched:
            decision = ReflCtrlDecision(
                allowed=True,
                matched_rules=tuple(matched),
                granted_levels=tuple(granted),
            )
        else:
            denied_by = DENIED_NO_RULE
            if request.outcome == "success":
                if request.excellent_streak >= cfg.excellent_streak_skip:
                    denied_by = DENIED_EXCELLENT_STREAK
                elif request.normal_streak >= cfg.normal_streak_l2_only:
                    denied_by = DENIED_NORMAL_STREAK
            decision = ReflCtrlDecision(allowed=False, denied_by=denied_by)
        self._trace(request, decision)
        return decision

    def _match_rules(self, request: ReflectionRequest) -> tuple[list[str], list[str]]:
        """§3.4 显式规则集逐条评估（确定性顺序；矩阵仅在规则命中后叠加授权）."""
        cfg = self._config
        matched: list[str] = []
        granted: list[str] = []

        def grant(*levels: str) -> None:
            for level in ("L1", "L2", "L3"):
                if level in levels and level not in granted:
                    granted.append(level)

        # L1 强制三条件
        if request.deviation_pct > cfg.deviation_force_pct:
            matched.append(RULE_L1_FORCE_DEVIATION)
            grant("L1")
        if request.risk_vetoed:
            matched.append(RULE_L1_FORCE_RISK_VETO)
            grant("L1")
        if request.outcome == "failure":
            # 决策矩阵：失败 → 执行 L1 + 立即 L2 + 触发 L3
            matched.append(RULE_L1_FORCE_EXECUTION_FAILURE)
            grant("L1", "L2", "L3")
        # Agent-R 轨迹内异常四场景（盘后复盘异常检测规则）
        if request.signal_sigma_deviation > cfg.signal_sigma_force:
            matched.append(RULE_AGENT_R_SIGNAL_SIGMA)
            grant("L1")
        if request.slippage_ratio > cfg.slippage_ratio_force:
            matched.append(RULE_AGENT_R_SLIPPAGE)
            grant("L1")
        if request.risk_param_deviation_pct > cfg.risk_param_deviation_force_pct:
            matched.append(RULE_AGENT_R_RISK_PARAM)
            grant("L1")
        if request.regime_transition_prob_pct > cfg.regime_transition_force_pct and not request.regime_triggered:
            matched.append(RULE_AGENT_R_REGIME)
            grant("L1")
        # HITL 低置信触发
        if request.eval_confidence < cfg.hitl_confidence_l2:
            matched.append(RULE_HITL_CONFIDENCE_L2)
            grant("L1", "L2")
        elif request.eval_confidence < cfg.hitl_confidence_l1:
            matched.append(RULE_HITL_CONFIDENCE_L1)
            grant("L1")
        # 分层频率
        if (
            request.layer == "tactical"
            and request.similar_task_count > 0
            and request.similar_task_count % cfg.tactical_nth == 0
        ):
            matched.append(RULE_LAYER_TACTICAL_NTH)
            grant("L1")
        if request.layer == "strategic":
            matched.append(RULE_LAYER_STRATEGIC_ALWAYS)
            grant("L1")
        # L2 累积触发（同类任务累积 N 次）
        if request.requested_level == "L2" and request.similar_task_count >= cfg.l2_accumulated_n:
            matched.append(RULE_L2_ACCUMULATED)
            grant("L2")
        # 决策矩阵：严重偏差 L1+L2（叠加在偏差强制规则上）
        if request.severity == "severe" and RULE_L1_FORCE_DEVIATION in matched:
            grant("L1", "L2")
        return matched, granted

    # ── 留痕与 token 统计 ─────────────────────────────────────

    def _trace(self, request: ReflectionRequest, decision: ReflCtrlDecision) -> None:
        """全量裁决写 decisions.jsonl；放行才计 token 写 token_stats.jsonl（IO 失败不阻断）."""
        timestamp = datetime.now(UTC).isoformat()
        record = {
            "timestamp": timestamp,
            "task_id": request.task_id,
            "layer": request.layer,
            "requested_level": request.requested_level,
            "allowed": decision.allowed,
            "matched_rules": list(decision.matched_rules),
            "granted_levels": list(decision.granted_levels),
            "denied_by": decision.denied_by,
        }
        self._append_jsonl(self._stats_root / _DECISIONS_FILE, record)
        if decision.allowed:
            self._append_jsonl(
                self._stats_root / _TOKEN_STATS_FILE,
                {
                    "timestamp": timestamp,
                    "task_id": request.task_id,
                    "estimated_tokens": request.estimated_tokens,
                    "matched_rules": list(decision.matched_rules),
                },
            )

    @staticmethod
    def _append_jsonl(path: Path, record: dict[str, Any]) -> None:
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(record, ensure_ascii=False) + "\n")
        except OSError as exc:
            logger.warning("reflctrl 留痕写入失败（裁决仍生效）: %r", exc)

    def total_estimated_tokens(self) -> int:
        """汇总全部放行反思的预估 token（读 token_stats.jsonl）."""
        path = self._stats_root / _TOKEN_STATS_FILE
        if not path.exists():
            return 0
        total = 0
        try:
            with path.open("r", encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        total += int(json.loads(line).get("estimated_tokens", 0))
                    except (json.JSONDecodeError, TypeError, ValueError):
                        continue
        except OSError as exc:
            logger.warning("reflctrl token 统计读取失败: %r", exc)
        return total


__all__ = [
    "DENIED_EXCELLENT_STREAK",
    "DENIED_MAX_ROUNDS",
    "DENIED_NO_RULE",
    "DENIED_NORMAL_STREAK",
    "RULE_AGENT_R_REGIME",
    "RULE_AGENT_R_RISK_PARAM",
    "RULE_AGENT_R_SIGNAL_SIGMA",
    "RULE_AGENT_R_SLIPPAGE",
    "RULE_HITL_CONFIDENCE_L1",
    "RULE_HITL_CONFIDENCE_L2",
    "RULE_L1_FORCE_DEVIATION",
    "RULE_L1_FORCE_EXECUTION_FAILURE",
    "RULE_L1_FORCE_RISK_VETO",
    "RULE_L2_ACCUMULATED",
    "RULE_LAYER_STRATEGIC_ALWAYS",
    "RULE_LAYER_TACTICAL_NTH",
    "ReflCtrlConfig",
    "ReflCtrlDecision",
    "ReflCtrlGate",
    "ReflectionRequest",
]
