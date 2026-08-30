# [BLUEPRINT] MOD-INF-072 | docs/03_modules/_domain_infrastructure_operations/strategy_canary_release/blueprint.md
# [MODULE] zephyr.infrastructure.strategy_canary_release
# [DOMAIN] D_INFRA_OPS
# [DEPENDENCIES] 标准库(dataclasses/datetime/enum)
# [CONSUMERS] 运行时装配批（D_ASHARE_SIGNAL 策略运行面按 ratio 切流 / D_RISK 风控完整性指标供给 / config/canary.yaml 加载器 / 交易时段真源 trading_calendar）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 纯内存状态机无IO; 交易时段禁启动(HC-05); 6维验证缺维Fail-Closed; 任一维不达标自动回滚ratio归零; 只产目标ratio不直接切流量; 回滚动作即时完成(配置回滚语义<10s)
# [MODIFY-GUARD] docs/03_modules/_domain_infrastructure_operations/strategy_canary_release/blueprint.md
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] StrategyCanaryError(占位 ZA-INF-UNREGISTERED-STRATEGY-CANARY)——时段门禁/重复start/未start推进/配置非法/指标缺维时抛
# [TESTS] tests/infrastructure/test_strategy_canary_release.py
# [A_module] module_id=MOD-INF-072 | layer=module | stability=evolving | safety=H | ai_autonomy=human_gated
# [TTL] permanent
"""
StrategyCanaryRelease — 策略灰度发布（MOD-INF-072）。

B14-04678（AUD-DRAFT-001-DIGEST P1 波 W-P1-24，CAND-INFRAOPS-002，A9运维架构
§8.3.6 D-SIGNAL-140）：config 驱动 1-5% → 25-50% → 100% 三阶段放量阶梯 +
6 维验证（功能/性能/错误率/资源/风控完整性/数据一致性）+ 失败 <10s 配置
回滚 + 交易时段禁启动（HC-05）。防 Knight Capital 类事故关键件。

查重分工（蓝图 §0）：gray_release_shadow_deployer=模型影子观测（B-009 不
生效）；canary_manager=通用权重桩；grayscale_rollout/lifecycle_state_machine
=因子级放量与生命周期；本件=**策略级**真实流量分阶段灰度状态机。本件只产
目标 ratio 与状态，不直接切流量（执行归运行时装配批）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: strategy_id 参数
#   fields: 参数 strategy_id，类型注解 str
#   code: strategy_canary_release.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: raw 参数
#   fields: 参数 raw，类型注解 dict
#   code: strategy_canary_release.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① config_from_dict
#   name_en: config_from_dict
#   intro: 从 config/canary.yaml 语义的 dict 构造配置（装配批加载 YAML 后调用）。
#   desc: 从 config/canary.yaml 语义的 dict 构造配置（装配批加载 YAML 后调用）。；源码 L196-L225
#   inputs: strategy_id raw
#   outputs: StrategyCanaryConfig
# - id: A2
#   name_zh: ② StrategyCanaryRelease
#   name_en: StrategyCanaryRelease
#   intro: 策略灰度发布状态机（MOD-INF-072）。
#   desc: 策略灰度发布状态机（MOD-INF-072）。 用法： rel = StrategyCanaryRelease() rel.start(config, now_utc, is_t…；公共方法（定义序）: start,…
#   inputs: 无参数
#   outputs: 返回值
#   （注：A2 之后另有 6 个公共定义未列入（含 6 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: StrategyCanaryConfig
#   name_en: StrategyCanaryConfig
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 运行时装配批（D_ASHARE_SIGNAL 策略运行面按 ratio 切流 / D_RISK 风控完整性指标供给 / config/canary.yaml…
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> A2
# A2 --> O1
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Final

_log = logging.getLogger(__name__)

__all__: Final = [
    "DEFAULT_STAGES",
    "CanaryReleaseState",
    "CanaryStage",
    "CanaryStatus",
    "StrategyCanaryConfig",
    "StrategyCanaryError",
    "StrategyCanaryRelease",
    "ValidationDimension",
    "config_from_dict",
]


class StrategyCanaryError(Exception):
    """策略灰度发布操作非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-INF-UNREGISTERED-STRATEGY-CANARY。
    """


class ValidationDimension(str, Enum):
    """6 维验证维度。"""

    FUNCTIONALITY = "functionality"
    PERFORMANCE = "performance"
    ERROR_RATE = "error_rate"
    RESOURCE = "resource"
    RISK_COMPLETENESS = "risk_completeness"
    DATA_CONSISTENCY = "data_consistency"


class CanaryStatus(str, Enum):
    """灰度发布状态。"""

    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    ROLLED_BACK = "rolled_back"


# 维度方向：upper=指标须 ≤ 阈值（越低越好）；lower=指标须 ≥ 阈值（越高越好）
_DIM_DIRECTION: Final[dict[ValidationDimension, str]] = {
    ValidationDimension.FUNCTIONALITY: "lower",
    ValidationDimension.PERFORMANCE: "lower",
    ValidationDimension.ERROR_RATE: "upper",
    ValidationDimension.RESOURCE: "upper",
    ValidationDimension.RISK_COMPLETENESS: "lower",
    ValidationDimension.DATA_CONSISTENCY: "lower",
}

_DEFAULT_THRESHOLDS: Final[dict[ValidationDimension, float]] = {
    ValidationDimension.FUNCTIONALITY: 0.99,  # 功能通过率 ≥ 99%
    ValidationDimension.PERFORMANCE: 0.95,  # 性能得分 ≥ 95% 基线
    ValidationDimension.ERROR_RATE: 0.01,  # 错误率 ≤ 1%
    ValidationDimension.RESOURCE: 1.20,  # 资源占用 ≤ 120% 基线
    ValidationDimension.RISK_COMPLETENESS: 1.0,  # 风控完整性 = 100%
    ValidationDimension.DATA_CONSISTENCY: 0.999,  # 数据一致性 ≥ 99.9%
}


@dataclass(frozen=True)
class CanaryStage:
    """单阶段放量区间。"""

    name: str
    min_ratio: float
    max_ratio: float

    def __post_init__(self) -> None:
        if not (0.0 < self.min_ratio <= self.max_ratio <= 1.0):
            raise StrategyCanaryError(
                f"阶段 {self.name} 区间非法: [{self.min_ratio}, {self.max_ratio}]（须 0<min≤max≤1）"
            )


DEFAULT_STAGES: Final[tuple[CanaryStage, ...]] = (
    CanaryStage("stage1_canary", 0.01, 0.05),
    CanaryStage("stage2_partial", 0.25, 0.50),
    CanaryStage("stage3_full", 1.0, 1.0),
)


@dataclass(frozen=True)
class StrategyCanaryConfig:
    """策略灰度配置（config/canary.yaml 语义，装配批加载后注入）。"""

    strategy_id: str
    stages: tuple[CanaryStage, ...] = DEFAULT_STAGES
    validation_thresholds: dict[ValidationDimension, float] = field(default_factory=lambda: dict(_DEFAULT_THRESHOLDS))
    rollback_timeout_sec: int = 10  # 配置回滚语义 <10s
    freeze_during_trading: bool = True  # HC-05 交易时段禁启动

    def __post_init__(self) -> None:
        if not self.strategy_id:
            raise StrategyCanaryError("strategy_id 不能为空")
        if not self.stages:
            raise StrategyCanaryError("stages 不能为空")
        if self.rollback_timeout_sec <= 0:
            raise StrategyCanaryError("rollback_timeout_sec 须为正")
        missing = set(ValidationDimension) - set(self.validation_thresholds)
        if missing:
            raise StrategyCanaryError(f"validation_thresholds 缺维度: {missing}")


@dataclass(frozen=True)
class CanaryReleaseState:
    """策略灰度发布状态（只读快照）。"""

    strategy_id: str
    status: CanaryStatus
    stage_index: int  # -1=未启动
    current_ratio: float
    history: tuple[str, ...] = ()


def config_from_dict(strategy_id: str, raw: dict) -> StrategyCanaryConfig:
    """从 config/canary.yaml 语义的 dict 构造配置（装配批加载 YAML 后调用）。"""
    if not isinstance(raw, dict):
        raise StrategyCanaryError("raw 配置须为 dict")
    raw_stages = raw.get("stages")
    if raw_stages is None:
        stages = DEFAULT_STAGES
    else:
        if not isinstance(raw_stages, list) or not raw_stages:
            raise StrategyCanaryError("stages 须为非空列表")
        stages = tuple(
            CanaryStage(
                name=str(s["name"]),
                min_ratio=float(s["min_ratio"]),
                max_ratio=float(s["max_ratio"]),
            )
            for s in raw_stages
        )
    raw_th = raw.get("validation_thresholds")
    if raw_th is None:
        thresholds = dict(_DEFAULT_THRESHOLDS)
    else:
        thresholds = {ValidationDimension(k): float(v) for k, v in raw_th.items()}
    return StrategyCanaryConfig(
        strategy_id=strategy_id,
        stages=stages,
        validation_thresholds=thresholds,
        rollback_timeout_sec=int(raw.get("rollback_timeout_sec", 10)),
        freeze_during_trading=bool(raw.get("freeze_during_trading", True)),
    )


class StrategyCanaryRelease:
    """策略灰度发布状态机（MOD-INF-072）。

    用法：
        rel = StrategyCanaryRelease()
        rel.start(config, now_utc, is_trading_session=False)
        rel.advance("strat_alpha", metrics, now_utc)   # 6 维全过 → 下一阶段
        rel.rollback("strat_alpha", "手动回滚", now_utc)
    """

    def __init__(self) -> None:
        self._configs: dict[str, StrategyCanaryConfig] = {}
        self._states: dict[str, CanaryReleaseState] = {}

    # ── 启动（HC-05 时段门禁）──

    def start(
        self,
        config: StrategyCanaryConfig,
        now_utc: datetime | None = None,
        is_trading_session: bool = False,
    ) -> CanaryReleaseState:
        """启动灰度：进入 stage1（ratio=阶段下界）。交易时段 Fail-Closed（HC-05）。"""
        if now_utc is None:
            now_utc = datetime.now(timezone.utc)
        if not isinstance(config, StrategyCanaryConfig):
            raise StrategyCanaryError("config 须为 StrategyCanaryConfig")
        sid = config.strategy_id
        # HC-05 时段门禁优先于重复启动检查（安全闸口先行）
        if config.freeze_during_trading and is_trading_session:
            raise StrategyCanaryError(f"HC-05：交易时段禁止启动灰度发布（策略 {sid}）")
        prev = self._states.get(sid)
        if prev is not None and prev.status in (CanaryStatus.RUNNING, CanaryStatus.COMPLETED):
            raise StrategyCanaryError(f"策略 {sid} 已在 {prev.status.value} 状态，禁止重复 start")
        stage = config.stages[0]
        note = f"{now_utc.isoformat()} start → {stage.name} ratio={stage.min_ratio}" + (
            f"（重启，前态 {prev.status.value}）" if prev else ""
        )
        st = CanaryReleaseState(
            strategy_id=sid,
            status=CanaryStatus.RUNNING,
            stage_index=0,
            current_ratio=stage.min_ratio,
            history=(prev.history + (note,)) if prev else (note,),
        )
        self._configs[sid] = config
        self._states[sid] = st
        _log.info("策略灰度启动: %s → %s ratio=%.2f", sid, stage.name, stage.min_ratio)
        return st

    # ── 推进（6 维验证）──

    def advance(
        self,
        strategy_id: str,
        metrics: dict[ValidationDimension, float],
        now_utc: datetime | None = None,
    ) -> CanaryReleaseState:
        """6 维验证全过 → 推进；任一维不达标 → 自动回滚。缺维 Fail-Closed。"""
        if now_utc is None:
            now_utc = datetime.now(timezone.utc)
        st, config = self._require_running(strategy_id)
        missing = set(ValidationDimension) - set(metrics)
        if missing:
            raise StrategyCanaryError(f"metrics 缺维度（Fail-Closed）: {missing}")
        failures = self._validate(config, metrics)
        if failures:
            return self.rollback(
                strategy_id,
                f"6维验证未过自动回滚: {','.join(failures)}",
                now_utc,
            )
        next_index = st.stage_index + 1
        if next_index >= len(config.stages):
            new_st = CanaryReleaseState(
                strategy_id=strategy_id,
                status=CanaryStatus.COMPLETED,
                stage_index=st.stage_index,
                current_ratio=st.current_ratio,
                history=st.history + (f"{now_utc.isoformat()} 末阶段验证通过 → completed",),
            )
        else:
            stage = config.stages[next_index]
            new_st = CanaryReleaseState(
                strategy_id=strategy_id,
                status=CanaryStatus.RUNNING,
                stage_index=next_index,
                current_ratio=stage.min_ratio,
                history=st.history + (f"{now_utc.isoformat()} 6维验证通过 → {stage.name} ratio={stage.min_ratio}",),
            )
        self._states[strategy_id] = new_st
        return new_st

    # ── 回滚（配置回滚语义 <10s：动作纯内存即时完成）──

    def rollback(
        self,
        strategy_id: str,
        reason: str,
        now_utc: datetime | None = None,
    ) -> CanaryReleaseState:
        """回滚：ratio 立归 0、状态 ROLLED_BACK、留痕。"""
        if now_utc is None:
            now_utc = datetime.now(timezone.utc)
        st = self._states.get(strategy_id)
        if st is None:
            raise StrategyCanaryError(f"策略 {strategy_id} 未启动，无法回滚")
        if st.status != CanaryStatus.RUNNING:
            raise StrategyCanaryError(f"策略 {strategy_id} 当前 {st.status.value}，仅 RUNNING 可回滚")
        new_st = CanaryReleaseState(
            strategy_id=strategy_id,
            status=CanaryStatus.ROLLED_BACK,
            stage_index=st.stage_index,
            current_ratio=0.0,
            history=st.history + (f"{now_utc.isoformat()} rollback ratio=0.0 reason={reason}",),
        )
        self._states[strategy_id] = new_st
        _log.warning("策略灰度回滚: %s reason=%s", strategy_id, reason)
        return new_st

    # ── 查询 ──

    def status(self, strategy_id: str) -> CanaryReleaseState:
        """查询策略灰度状态（未启动返回 IDLE 快照）。"""
        st = self._states.get(strategy_id)
        if st is None:
            return CanaryReleaseState(
                strategy_id=strategy_id,
                status=CanaryStatus.IDLE,
                stage_index=-1,
                current_ratio=0.0,
            )
        return st

    # ── 内部 ──

    def _require_running(self, strategy_id: str) -> tuple[CanaryReleaseState, StrategyCanaryConfig]:
        st = self._states.get(strategy_id)
        if st is None or st.status != CanaryStatus.RUNNING:
            raise StrategyCanaryError(f"策略 {strategy_id} 未在 RUNNING 状态")
        config = self._configs[strategy_id]
        return st, config

    @staticmethod
    def _validate(config: StrategyCanaryConfig, metrics: dict[ValidationDimension, float]) -> list[str]:
        """6 维验证：按维度方向判定，返回未过维度清单（空=全过）。"""
        failures: list[str] = []
        for dim in ValidationDimension:
            th = config.validation_thresholds[dim]
            val = float(metrics[dim])
            if _DIM_DIRECTION[dim] == "upper":
                if val > th:
                    failures.append(f"{dim.value}={val}>{th}")
            else:
                if val < th:
                    failures.append(f"{dim.value}={val}<{th}")
        return failures
