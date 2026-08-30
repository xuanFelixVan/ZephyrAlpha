# [BLUEPRINT] MOD-ML-018 | docs/03_modules/_domain_machine_learning_train/continual_learning_antiforget/blueprint.md
# [MODULE] zephyr.ml_train.continual_learning_antiforget
# [DOMAIN] D_ML_TRAIN
# [DEPENDENCIES] 无（纯内存/DI；fisher_estimator/clock 全注入；语义旁挂 feedback_loop.evolution.ewc_kb_review）
# [CONSUMERS] 运行时装配批（Fisher 盘后批处理绑定 / regime 标注源绑定 / 微调流水线门禁装配）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] Fisher 信息仅经注入盘后批处理计算并缓存重要性权重+锚点; 每市场状态回放缓冲≤max_replay_per_regime(默认1000)硬约束; 旧状态验证性能降>max_drop_ratio(默认5%)即门禁拒绝; 验证失败回滚最近参数快照(无快照 Fail-Closed); 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_machine_learning_train/continual_learning_antiforget/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] ContinualLearnError(占位 ZA-MLT-UNREGISTERED-CONTINUAL-LEARN)——fisher 未注入/非法参数/回放超限/未知快照/验证缺项/回滚无快照时抛
# [TESTS] tests/ml_train/test_continual_learning_antiforget.py
# [A_module] module_id=MOD-ML-018 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""
ContinualLearningAntiForget — 持续学习抗遗忘框架（MOD-ML-018）。

B10-01881（AUD-DRAFT-001-DIGEST P2 波 P2-W07，CAND-MLT-025，A1 §29.35）：
**EWC 正则**（Fisher 信息盘后批处理注入计算，重要性权重缓存 + 锚点参数）
+ **经验回放**（每市场状态代表样本缓冲 ≤1000 条硬约束，regime 标注注入）
+ **微调后旧状态验证**（各 regime 性能降 ≤5% 门禁判定）
+ **回滚机制**（参数快照 + 验证失败回滚最近快照，无快照 Fail-Closed）。

分工：本件只做抗遗忘协议面（正则/缓冲/门禁/回滚），不做真训练；
Fisher 估计器为盘后批处理注入回调，本件不实现估计算法。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: fisher_estimator 参数
#   fields: 参数 fisher_estimator（无注解）
#   code: continual_learning_antiforget.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: clock 参数
#   fields: 参数 clock（无注解）
#   code: continual_learning_antiforget.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: max_replay_per_regime 参数
#   fields: 参数 max_replay_per_regime（无注解）
#   code: continual_learning_antiforget.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: max_drop_ratio 参数
#   fields: 参数 max_drop_ratio（无注解）
#   code: continual_learning_antiforget.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① ContinualLearningAntiForget
#   name_en: ContinualLearningAntiForget
#   intro: 持续学习抗遗忘框架（EWC + 经验回放 + 旧状态验证 + 快照回滚）。
#   desc: 持续学习抗遗忘框架（EWC + 经验回放 + 旧状态验证 + 快照回滚）。；公共方法（定义序）: compute_importance, importance_weights, ewc_penalty, add_rep…
#   inputs: fisher_estimator clock max_replay_per_regime max_drop_ratio
#   outputs: 返回值
#   （注：A1 之后另有 5 个公共定义未列入（含 5 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（6 定义）
#   name_en: public defs
#   intro: ContinualLearningAntiForget
#   downstream: 运行时装配批（Fisher 盘后批处理绑定 / regime 标注源绑定 / 微调流水线门禁装配）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> O1
"""

from __future__ import annotations

import datetime
import logging
from dataclasses import dataclass
from typing import Callable, Final, Mapping

_log = logging.getLogger(__name__)

__all__: Final = [
    "ContinualLearnError",
    "ContinualLearningAntiForget",
    "GateDecision",
    "ParameterSnapshot",
    "ReplaySample",
    "ValidationResult",
]

#: 默认每市场状态回放代表样本上限（硬约束）
DEFAULT_MAX_REPLAY_PER_REGIME: Final = 1000
#: 默认旧状态性能降幅门禁（5%）
DEFAULT_MAX_DROP_RATIO: Final = 0.05


class ContinualLearnError(Exception):
    """持续学习抗遗忘输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-MLT-UNREGISTERED-CONTINUAL-LEARN。
    """


@dataclass(frozen=True)
class ReplaySample:
    """经验回放代表样本（frozen；regime 标注注入）。"""

    sample_id: str
    regime: str
    payload: dict
    added_at: datetime.datetime


@dataclass(frozen=True)
class ParameterSnapshot:
    """参数快照（回滚载体，frozen；写后不可改）。"""

    snapshot_id: str
    params: dict
    tag: str
    taken_at: datetime.datetime


@dataclass(frozen=True)
class ValidationResult:
    """单市场状态微调后旧状态验证结果（frozen）。"""

    regime: str
    old_metric: float
    new_metric: float
    drop_ratio: float
    passed: bool


@dataclass(frozen=True)
class GateDecision:
    """微调门禁裁决（frozen）：全过→接受新参数；任一失败→回滚最近快照。"""

    accepted: bool
    results: tuple[ValidationResult, ...]
    active_params: dict
    rolled_back_to: str | None


def _validate_params(params: Mapping[str, float], *, what: str = "params") -> None:
    """参数映射校验：非空、键非空、值为非 bool 数值。"""
    if not isinstance(params, Mapping) or not params:
        raise ContinualLearnError(f"{what} 为空或非映射")
    for name, value in params.items():
        if not name:
            raise ContinualLearnError(f"{what} 存在空参数名")
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ContinualLearnError(f"{what}[{name!r}] 非数值: {value!r}")


class ContinualLearningAntiForget:
    """持续学习抗遗忘框架（EWC + 经验回放 + 旧状态验证 + 快照回滚）。"""

    def __init__(
        self,
        *,
        fisher_estimator: Callable[[Mapping[str, float]], Mapping[str, float]] | None = None,
        clock: Callable[[], datetime.datetime] | None = None,
        max_replay_per_regime: int = DEFAULT_MAX_REPLAY_PER_REGIME,
        max_drop_ratio: float = DEFAULT_MAX_DROP_RATIO,
    ) -> None:
        if max_replay_per_regime <= 0:
            raise ContinualLearnError(f"max_replay_per_regime 须为正: {max_replay_per_regime!r}")
        if not 0.0 < max_drop_ratio <= 1.0:
            raise ContinualLearnError(f"max_drop_ratio 越界: {max_drop_ratio!r}（需 ∈(0,1]）")
        self._fisher_estimator = fisher_estimator
        self._clock = clock or datetime.datetime.now
        self._max_replay = int(max_replay_per_regime)
        self._max_drop = float(max_drop_ratio)
        self._fisher: dict[str, float] | None = None
        self._anchor: dict[str, float] | None = None
        self._replay: dict[str, dict[str, ReplaySample]] = {}
        self._snapshots: dict[str, ParameterSnapshot] = {}
        self._snapshot_order: list[str] = []
        self._snapshot_counter = 0

    # ── EWC 正则（Fisher 盘后批处理注入） ─────────────────────────────────

    def compute_importance(self, params: Mapping[str, float]) -> dict[str, float]:
        """盘后批处理：注入估计器计算 Fisher 信息，缓存重要性权重与锚点参数。"""
        if self._fisher_estimator is None:
            raise ContinualLearnError("fisher_estimator 未注入（Fisher 信息须盘后批处理注入计算）")
        _validate_params(params)
        fisher = self._fisher_estimator(dict(params))
        if not isinstance(fisher, Mapping):
            raise ContinualLearnError("fisher_estimator 返回非映射")
        missing = [k for k in params if k not in fisher]
        if missing:
            raise ContinualLearnError(f"Fisher 信息缺参数: {sorted(missing)!r}")
        out: dict[str, float] = {}
        for name in sorted(fisher):
            if name not in params:
                raise ContinualLearnError(f"Fisher 信息含未知参数: {name!r}")
            value = fisher[name]
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ContinualLearnError(f"Fisher[{name!r}] 非数值: {value!r}")
            if value < 0:
                raise ContinualLearnError(f"Fisher[{name!r}] 为负: {value!r}（信息须非负）")
            out[name] = float(value)
        self._anchor = {k: float(v) for k, v in params.items()}
        self._fisher = out
        _log.info("EWC 重要性权重已缓存: %d 参数", len(out))
        return dict(out)

    def importance_weights(self) -> dict[str, float]:
        """已缓存重要性权重（未计算 Fail-Closed）。"""
        if self._fisher is None:
            raise ContinualLearnError("尚未计算 Fisher 重要性权重")
        return dict(self._fisher)

    def ewc_penalty(self, new_params: Mapping[str, float]) -> float:
        """EWC 正则惩罚 Σ F_i·(θ_i−θ*_i)²（确定性；键序排序求和）。"""
        if self._fisher is None or self._anchor is None:
            raise ContinualLearnError("尚未计算重要性权重（先 compute_importance）")
        _validate_params(new_params, what="new_params")
        if set(new_params) != set(self._anchor):
            raise ContinualLearnError("new_params 参数集与锚点不一致")
        return sum(self._fisher[k] * (float(new_params[k]) - self._anchor[k]) ** 2 for k in sorted(self._anchor))

    # ── 经验回放（每市场状态代表样本硬约束） ───────────────────────────────

    def add_replay_sample(self, sample_id: str, regime: str, payload: Mapping) -> ReplaySample:
        """注入 regime 标注的代表样本入缓冲；超每状态上限 Fail-Closed。"""
        if not sample_id:
            raise ContinualLearnError("sample_id 为空")
        if not regime:
            raise ContinualLearnError("regime 标注为空（须注入市场状态标注）")
        if not isinstance(payload, Mapping):
            raise ContinualLearnError("payload 非映射")
        if any(sample_id in buf for buf in self._replay.values()):
            raise ContinualLearnError(f"sample_id 重复: {sample_id!r}")
        buf = self._replay.setdefault(regime, {})
        if len(buf) >= self._max_replay:
            raise ContinualLearnError(f"regime {regime!r} 回放缓冲已满（≤{self._max_replay} 条硬约束）")
        sample = ReplaySample(sample_id=sample_id, regime=regime, payload=dict(payload), added_at=self._clock())
        buf[sample_id] = sample
        return sample

    def replay_samples(self, regime: str | None = None) -> tuple[ReplaySample, ...]:
        """回放样本视图（按 (added_at, sample_id) 确定性排序；未知 regime → 空）。"""
        if regime is not None:
            items = list(self._replay.get(regime, {}).values())
        else:
            items = [s for buf in self._replay.values() for s in buf.values()]
        items.sort(key=lambda s: (s.added_at, s.sample_id))
        return tuple(items)

    def replay_size(self, regime: str) -> int:
        """单市场状态缓冲条数。"""
        if not regime:
            raise ContinualLearnError("regime 为空")
        return len(self._replay.get(regime, {}))

    # ── 参数快照 / 回滚 ────────────────────────────────────────────────────

    def snapshot_params(self, params: Mapping[str, float], tag: str = "") -> ParameterSnapshot:
        """参数快照（不可变副本；snapshot_id 按调用序确定性生成）。"""
        _validate_params(params)
        self._snapshot_counter += 1
        snap = ParameterSnapshot(
            snapshot_id=f"snap-{self._snapshot_counter:04d}",
            params={k: float(v) for k, v in params.items()},
            tag=tag,
            taken_at=self._clock(),
        )
        self._snapshots[snap.snapshot_id] = snap
        self._snapshot_order.append(snap.snapshot_id)
        _log.info("参数快照: %s (%s)", snap.snapshot_id, tag)
        return snap

    def latest_snapshot(self) -> ParameterSnapshot:
        """最近快照（无快照 Fail-Closed）。"""
        if not self._snapshot_order:
            raise ContinualLearnError("无参数快照")
        return self._snapshots[self._snapshot_order[-1]]

    def rollback_to(self, snapshot_id: str) -> dict[str, float]:
        """回滚：取快照参数副本（未知快照 Fail-Closed）。"""
        snap = self._snapshots.get(snapshot_id)
        if snap is None:
            raise ContinualLearnError(f"未知参数快照: {snapshot_id!r}")
        _log.warning("参数回滚至快照: %s", snapshot_id)
        return dict(snap.params)

    # ── 微调后旧状态验证（≤5% 门禁） ───────────────────────────────────────

    def validate_old_regimes(
        self,
        old_metrics: Mapping[str, float],
        new_metrics: Mapping[str, float],
    ) -> tuple[ValidationResult, ...]:
        """逐市场状态比对旧基线：降幅 >max_drop_ratio 即不通过（确定性排序）。"""
        if not isinstance(old_metrics, Mapping) or not old_metrics:
            raise ContinualLearnError("old_metrics 为空或非映射")
        if not isinstance(new_metrics, Mapping):
            raise ContinualLearnError("new_metrics 非映射")
        results: list[ValidationResult] = []
        for regime in sorted(old_metrics):
            old = old_metrics[regime]
            if isinstance(old, bool) or not isinstance(old, (int, float)):
                raise ContinualLearnError(f"old_metrics[{regime!r}] 非数值: {old!r}")
            if old <= 0:
                raise ContinualLearnError(f"old_metrics[{regime!r}] 基线须为正: {old!r}")
            if regime not in new_metrics:
                raise ContinualLearnError(f"new_metrics 缺市场状态: {regime!r}")
            new = new_metrics[regime]
            if isinstance(new, bool) or not isinstance(new, (int, float)):
                raise ContinualLearnError(f"new_metrics[{regime!r}] 非数值: {new!r}")
            drop = (float(old) - float(new)) / float(old)
            results.append(
                ValidationResult(
                    regime=regime,
                    old_metric=float(old),
                    new_metric=float(new),
                    drop_ratio=drop,
                    passed=drop <= self._max_drop,
                )
            )
        return tuple(results)

    def finetune_gate(
        self,
        new_params: Mapping[str, float],
        old_metrics: Mapping[str, float],
        new_metrics: Mapping[str, float],
    ) -> GateDecision:
        """微调门禁：旧状态验证全过→接受新参数；任一超阈→回滚最近快照。

        验证失败且无快照可回滚 → Fail-Closed 抛错（禁止带病上线）。
        """
        _validate_params(new_params, what="new_params")
        results = self.validate_old_regimes(old_metrics, new_metrics)
        if all(r.passed for r in results):
            return GateDecision(
                accepted=True,
                results=results,
                active_params={k: float(v) for k, v in new_params.items()},
                rolled_back_to=None,
            )
        failed = [r.regime for r in results if not r.passed]
        _log.warning("旧状态验证失败 regime=%s，触发回滚", failed)
        if not self._snapshot_order:
            raise ContinualLearnError(f"旧状态验证失败（{failed!r} 降幅超阈）且无参数快照可回滚（Fail-Closed）")
        snap_id = self._snapshot_order[-1]
        return GateDecision(
            accepted=False,
            results=results,
            active_params=self.rollback_to(snap_id),
            rolled_back_to=snap_id,
        )
