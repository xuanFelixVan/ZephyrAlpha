# [BLUEPRINT] MOD-FWCOMP-001 | docs/03_modules/_domain_portfolio_core/framework_composer_blueprint.md
# [MODULE] zephyr.pf_core.strategy_engine.framework_composer
# [DOMAIN] D_PF_CORE
# [DEPENDENCIES] zephyr.pf_core.strategy_engine.strategy_runner; zephyr.backtest.implementations.vectorized_engine; zephyr.backtest.io.backtest_result_sink; zephyr.backtest.io.result_repository; zephyr.regime.core.regime_detector
# [CONSUMERS] src/zephyr/frontend/dashboard/api_server.py(GET /api/framework-plans; POST|GET /api/framework-backtest-run)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 不重写撮合逻辑（复用 DefaultBacktestEngine/StrategyRunner，与本模块正交）; 合成面板 Σw=1 显式归一化并披露（ablation.py 同款纪律，禁静默再分配）; tick-only 成员跳过必须落报告（skipped 落 artifact metrics）; BacktestResult 15 字段契约冻结（plan_id 走 metrics 扩展字段，不动 artifact 顶层 schema）; 本模块只出净值/面板，不写 market_signal_history（管道 A 语义=子策略权重，禁污染）; 三期动态模式=逐日查 regime_overrides 取 α_i(t)（查表不做判定，禁自造 regime 判定逻辑——宪章 §3 约束三），未覆盖 regime/日期回退基准权重并披露（regime_day_counts），状态词表唯一真源=regime_detector.REGIME_STATES（非法状态 fail-closed 拒绝），静态模式（无 regime 序）行为与二期逐位一致
# [MODIFY-GUARD] blueprint
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] FrameworkPlanError: 配置缺失/plan_id 未找到/权重和≠1/strategy_id 为空; FrameworkValidationError: 合成输入面板为空/参与成员为空
# [TESTS] tests/pf_core/test_framework_composer.py
# [A_module] module_id=MOD-FWCOMP-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""整装组合回测器（二期整装回测后端，任务批 2026-09-09；三期 regime 动态权重联动 2026-09-10）。

语义（Owner 批准任务书）: 输入 = 方案权重 α_i（config/framework_plans.yaml 三套预设）
× 各子策略日频权重面板 → 按资金比例线性合成组合权重面板（同日多策略权重加权求和，
Σw=1 归一化纪律与 ablation.py 同款）→ 复用现有回测引擎（DefaultBacktestEngine）跑出
组合净值。方法论根据 = system_charter.md §3 约束二「统一框架派：1 框架 × N 子策略 ×
regime 权重切换」。

三期动态化（α_i(t) 动态）: compose_weight_panels 增 regime_by_date 参数——逐日按当日
regime 状态查方案 regime_overrides 覆盖表取 α_i(t)；未覆盖 regime/日期回退方案基准权重。
**查表不做判定**：regime 状态词表唯一真源 = zephyr.regime.core.regime_detector.REGIME_STATES
（MOD-REGIME-001，r1/r2/r3/r4/r10/r11/r12 七态），非法状态 fail-closed 拒绝；日序的
生产责任在真源检测器（MOD-REGIME-001×002 离线回放，先例 shrinkage_provider
build_schedule_from_detector），本模块禁自造判定逻辑——regime 错=权重错（宪章 §3 约束三
生死线）。静态模式（regime_by_date=None）行为与二期逐位一致（向后兼容锚）。

合成算子 compose_weight_panels（与消融算子 ablate_weight_panel 是姊妹算子——
消融=从面板"剥离"，合成=按方案"叠加"，职责不同禁止合并，见 MOD-TDMVAL-001）:
    静态: W(t, s) = Σ_i α_i · w_i(t, s)   （i ∈ 参与成员，date×symbol 联合索引对齐，缺失填 0）
    动态: W(t, s) = Σ_i α_i(t) · w_i(t, s)，α_i(t) = 当日 regime 查 regime_overrides
    - 参与成员 α 合计 < 1（如 tick-only 成员被向量化回测跳过）时：显式等比再归一化
      （静态 rescale_factor = 1/α_total；动态按 regime 组分别披露 regime_rescale_factors），
      禁静默——引擎 _normalize_day_signals 本身会做 Σ=1 再分配，静默等价于把缺口偷给
      其他持仓（ablation 盘点⑦-2 同源污染）。
    - 行级 Σw 校验: Σ>0 的行归一至 1.0（偏差 >1e-9 记入 notes）；全零行保留（现金日，
      引擎无调仓语义）。

净值对账 reconcile_composed_nav: 组合净值 vs Σα_i·nav_i（手工加权）逐日误差表——
线性合成下两者应一致（同价、同成本比例、无约束事件扰动），验收判据=抽样≥5 日
最大误差 <0.01%（任务硬约束 4）。动态模式对账语义=按日分段（每段权重不同），
仅适用静态模式（动态用 per_regime_summary 分段归因替代）。

产物: data/backtest_artifacts/bt-fw-<8hex>.json——与单策略产物 schema 对齐
（BacktestRunArtifact CTR-P1-017 冻结不动），plan_id/参与成员/跳过成员/再归一化系数/
动态模式 regime_day_counts 落 metrics 扩展字段；run_id 前缀 bt-fw- 便于检索（原引擎
idempotency_key 保底 metrics.engine_run_id 可追溯）。

已知边界（如实披露）:
    - v1 仅向量化日频合成回测；tick-only 成员（做T三策略）跳过并披露，其权重经
      显式再归一化分摊给参与成员。tick 模式整装回测（逐成员 tick 回放+组合合成）
      为后续迭代。
    - 组合面板不写 market_signal_history（管道 A signal_id=子策略 strategy_id，
      组合面板是派生物，真源仍为各子策略面板）。
    - 回测必须扣全成本（system_charter §3 约束一）——成本模型在引擎层（BacktestConfig
      佣金/印花税/滑点），本模块透传不绕过。
    - regime 日序当前为显式注入（无逐日持久化真源表，T1 盘点结论 2026-09-10）；
      内置检测器自动回放（walk-forward HMM）另批立项，不在本模块范围。

真源: 任务书《整装回测（二期）后端建设——组合回测器 + 方案权重骨架（v2）》
     +《整装回测（三期）——regime 动态权重联动》
     + config/framework_plans.yaml（方案权重+regime_overrides 唯一真源）。
"""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field, replace
from decimal import Decimal
from pathlib import Path
from typing import Any, Final

import pandas as pd
import yaml

from zephyr.shared.io.paths import REPO_ROOT

logger = logging.getLogger(__name__)

DEFAULT_PLANS_PATH = REPO_ROOT / "config" / "framework_plans.yaml"
_WEIGHT_TOLERANCE = 1e-6
_ARTIFACT_RUN_PREFIX = "bt-fw"

_VALID_RISK_PROFILES = ("defensive", "balanced", "aggressive")

# 动态合成回退组标签：未覆盖 regime / 未覆盖日期的行归入此组（用方案基准权重）
_FALLBACK_GROUP_KEY = "__base__"

# REGIME_STATES 7 态词表进程内缓存（唯一真源 zephyr.regime.core.regime_detector，
# 惰性导入——regime 包链冷导入 ~20s，静态路径二期语义零开销）
_REGIME_STATES_CACHE: tuple[str, ...] | None = None


def _regime_states() -> tuple[str, ...]:
    """REGIME_STATES 7 态词表（唯一真源 regime_detector.REGIME_STATES，惰性导入+缓存）。

    Raises:
        FrameworkPlanError: regime 真源模块不可用（fail-closed，禁静默放行任意键）。
    """
    global _REGIME_STATES_CACHE
    if _REGIME_STATES_CACHE is None:
        try:
            from zephyr.regime.core.regime_detector import REGIME_STATES
        except Exception as exc:  # noqa: BLE001 — 词表真源不可用必须显式暴露
            raise FrameworkPlanError(
                f"regime 状态词表真源不可用（zephyr.regime.core.regime_detector）: {exc}"
            ) from exc
        _REGIME_STATES_CACHE = tuple(REGIME_STATES)
    return _REGIME_STATES_CACHE


class FrameworkPlanError(Exception):
    """整装方案配置异常（缺失/格式/权重校验失败）。"""

    error_code = "ZA-FWCOMP-0001"


class FrameworkValidationError(Exception):
    """合成/回测输入数据异常（与 ablation.ValidationError 同族，独立定义防跨模块循环导入）。"""

    error_code = "ZA-FWCOMP-0002"


@dataclass(frozen=True)
class PlanWeight:
    """方案内单个子策略的资金权重。

    Attributes:
        strategy_id: 真实注册的子策略 ID（StrategyRegistry/TickStrategyBase 注册表）。
        weight: 资金权重（0,1]，方案内合计=1.0（容差 1e-6）。
        role: 角色备注（防御底仓/进攻主力等，透传前端展示）。
    """

    strategy_id: str
    weight: float
    role: str = ""


@dataclass(frozen=True)
class FrameworkPlan:
    """整装方案（防御型/均衡型/激进型三套预设的内存形态）。

    Attributes:
        plan_id: 方案唯一 ID（fw-defensive / fw-balanced / fw-aggressive）。
        name: 中文方案名。
        risk_profile: 风险画像（defensive/balanced/aggressive）。
        description: 方案说明。
        weights: 子策略权重清单（PlanWeight 元组，基准权重）。
        regime_overrides: regime 联动覆盖表（三期）：((state, (PlanWeight, ...)), ...)，
            键=REGIME_STATES 7 态；未覆盖 regime 回退基准 weights（三期语义）。
    """

    plan_id: str
    name: str
    risk_profile: str
    description: str
    weights: tuple[PlanWeight, ...]
    regime_overrides: tuple[tuple[str, tuple[PlanWeight, ...]], ...] = ()

    @property
    def total_weight(self) -> float:
        return round(sum(w.weight for w in self.weights), 9)

    @property
    def strategy_ids(self) -> tuple[str, ...]:
        return tuple(w.strategy_id for w in self.weights)

    @property
    def regime_override_map(self) -> dict[str, tuple[PlanWeight, ...]]:
        """regime 状态 → 覆盖权重表（dict 视图，运行时查表用）。"""
        return dict(self.regime_overrides)

    def effective_weights(self, regime_state: str | None) -> tuple[PlanWeight, ...]:
        """给定 regime 状态的有效权重：有覆盖表用覆盖，否则（含 None）回退基准。

        查表语义单一入口——compose 动态路径与 per_regime_summary 分组共用，
        不做任何 regime 判定（判定真源=MOD-REGIME-001，本模块只消费其状态输出）。
        """
        if regime_state is not None:
            override = self.regime_override_map.get(regime_state)
            if override is not None:
                return override
        return self.weights


@dataclass
class ComposeReport:
    """合成报告（面板 + 全量披露字段，禁静默纪律的载体）。

    Attributes:
        panel: 合成后组合权重面板（date×symbol，与引擎 signals 同构）。
        participants: 实际参与合成的成员 strategy_id 清单。
        skipped: 被跳过成员 [(strategy_id, reason), ...]。
        alpha_total: 参与成员权重合计（再归一化前；动态模式=各 regime 组最坏口径 min）。
        rescale_factor: 再归一化系数（1/alpha_total；=1.0 表示未再归一；动态模式=各组最坏口径 max）。
        notes: 披露说明（再归一化语义/行级校验结果）。
        regime_day_counts: 动态模式各组分日数（state→n；回退组=__base__）；静态模式为空 dict。
        regime_rescale_factors: 动态模式各组再归一化系数（state→factor，仅 ≠1 的组登记）。
    """

    panel: pd.DataFrame
    participants: list[str] = field(default_factory=list)
    skipped: list[tuple[str, str]] = field(default_factory=list)
    alpha_total: float = 1.0
    rescale_factor: float = 1.0
    notes: str = ""
    regime_day_counts: dict[str, int] = field(default_factory=dict)
    regime_rescale_factors: dict[str, float] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# 方案配置加载（YAML 唯一真源）
# ---------------------------------------------------------------------------


def _parse_plan_weights(plan_id: str, weights_raw: list[Any]) -> list[PlanWeight]:
    """解析单个方案的 weights 数组（越界/缺字段校验）。

    Raises:
        FrameworkPlanError: strategy_id 为空 / weight 非数值或越界 (0,1]。
    """
    if not weights_raw:
        raise FrameworkPlanError(f"plan {plan_id} weights 为空")
    weights: list[PlanWeight] = []
    for j, w in enumerate(weights_raw):
        sid = str(w.get("strategy_id", "")).strip()
        if not sid:
            raise FrameworkPlanError(f"plan {plan_id} weights[{j}] 缺 strategy_id")
        try:
            weight = float(w.get("weight", 0.0))
        except (TypeError, ValueError) as exc:
            raise FrameworkPlanError(
                f"plan {plan_id} weights[{j}] weight 非数值: {w.get('weight')}"
            ) from exc
        if weight <= 0.0 or weight > 1.0:
            raise FrameworkPlanError(
                f"plan {plan_id} weights[{j}]（{sid}）weight 越界: {weight}（合法 (0,1]）"
            )
        weights.append(PlanWeight(strategy_id=sid, weight=weight, role=str(w.get("role", ""))))
    return weights


def _parse_regime_overrides(
    plan_id: str,
    raw: Any,
    base_weights: list[PlanWeight],
) -> tuple[tuple[str, tuple[PlanWeight, ...]], ...]:
    """解析方案 regime_overrides（三期：键=REGIME_STATES 7 态，值=完整权重覆盖表）。

    纪律: 键词表唯一真源=regime_detector.REGIME_STATES（非法键 fail-closed）；
    覆盖表成员集合必须与基准 weights 一致（仅权重不同）；每套覆盖表 Σ=1（容差同基准）。

    Raises:
        FrameworkPlanError: 键非法 / 非映射 / 成员集合不一致 / 覆盖表 Σ≠1 / 条目为空。
    """
    if not raw:
        return ()
    if not isinstance(raw, dict):
        raise FrameworkPlanError(
            f"plan {plan_id} regime_overrides 须为映射 {{regime: [weights]}}，got {type(raw).__name__}"
        )
    states = _regime_states()
    base_ids = {w.strategy_id for w in base_weights}
    overrides: list[tuple[str, tuple[PlanWeight, ...]]] = []
    for state, rows in raw.items():
        state_key = str(state).strip()
        if state_key not in states:
            raise FrameworkPlanError(
                f"plan {plan_id} regime_overrides 键非法: {state_key}"
                f"（合法 {list(states)}，真源 regime_detector.REGIME_STATES）"
            )
        oweights = tuple(_parse_plan_weights(f"{plan_id}·regime {state_key}", rows or []))
        oids = {w.strategy_id for w in oweights}
        if oids != base_ids:
            raise FrameworkPlanError(
                f"plan {plan_id} regime_overrides[{state_key}] 成员集合与基准 weights 不一致: "
                f"{sorted(oids ^ base_ids)}"
            )
        total = sum(w.weight for w in oweights)
        if abs(total - 1.0) > _WEIGHT_TOLERANCE:
            raise FrameworkPlanError(
                f"plan {plan_id} regime_overrides[{state_key}] 权重合计≠1: "
                f"{total:.9f}（容差 {_WEIGHT_TOLERANCE}）"
            )
        overrides.append((state_key, oweights))
    return tuple(overrides)


def _parse_plan(p: dict[str, Any], index: int, seen_ids: set[str]) -> FrameworkPlan:
    """解析单个方案条目（plan_id/risk_profile/权重和校验）。

    Raises:
        FrameworkPlanError: 缺 plan_id / plan_id 重复 / risk_profile 非法 / 权重和≠1。
    """
    plan_id = str(p.get("plan_id", "")).strip()
    if not plan_id:
        raise FrameworkPlanError(f"plans[{index}] 缺 plan_id")
    if plan_id in seen_ids:
        raise FrameworkPlanError(f"plan_id 重复: {plan_id}")
    seen_ids.add(plan_id)

    risk_profile = str(p.get("risk_profile", "")).strip()
    if risk_profile not in _VALID_RISK_PROFILES:
        raise FrameworkPlanError(
            f"plan {plan_id} risk_profile 非法: {risk_profile}（合法: {_VALID_RISK_PROFILES}）"
        )

    weights = _parse_plan_weights(plan_id, p.get("weights") or [])
    total = sum(w.weight for w in weights)
    if abs(total - 1.0) > _WEIGHT_TOLERANCE:
        raise FrameworkPlanError(f"plan {plan_id} 权重合计≠1: {total:.9f}（容差 {_WEIGHT_TOLERANCE}）")

    regime_overrides = _parse_regime_overrides(plan_id, p.get("regime_overrides"), weights)

    return FrameworkPlan(
        plan_id=plan_id,
        name=str(p.get("name_zh", plan_id)),
        risk_profile=risk_profile,
        description=str(p.get("description", "")),
        weights=tuple(weights),
        regime_overrides=regime_overrides,
    )


def load_framework_plans(path: str | Path | None = None) -> list[FrameworkPlan]:
    """从 config/framework_plans.yaml 加载全部整装方案并校验。

    Args:
        path: 配置路径（None=默认 config/framework_plans.yaml）。

    Returns:
        FrameworkPlan 列表（按文件顺序）。

    Raises:
        FrameworkPlanError: 文件缺失 / YAML 非法 / 权重和≠1（容差 1e-6）/
                            plan_id 重复 / strategy_id 为空。
    """
    plan_path = Path(path) if path else DEFAULT_PLANS_PATH
    if not plan_path.exists():
        raise FrameworkPlanError(f"整装方案配置缺失: {plan_path}")
    try:
        raw = yaml.safe_load(plan_path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        raise FrameworkPlanError(f"整装方案配置 YAML 非法: {exc}") from exc

    plans_raw = raw.get("plans")
    if not plans_raw or not isinstance(plans_raw, list):
        raise FrameworkPlanError("整装方案配置缺少 plans 数组或为空")

    plans: list[FrameworkPlan] = []
    seen_ids: set[str] = set()
    for i, p in enumerate(plans_raw):
        plans.append(_parse_plan(p, i, seen_ids))
    return plans


def get_framework_plan(plan_id: str, path: str | Path | None = None) -> FrameworkPlan:
    """按 plan_id 取整装方案。

    Raises:
        FrameworkPlanError: plan_id 不存在。
    """
    wanted = str(plan_id).strip()
    for plan in load_framework_plans(path):
        if plan.plan_id == wanted:
            return plan
    raise FrameworkPlanError(f"整装方案不存在: {plan_id}")


# ---------------------------------------------------------------------------
# 合成算子（与 ablation.ablate_weight_panel 姊妹——剥离/叠加正交，禁合并）
# ---------------------------------------------------------------------------


def compose_weight_panels(
    plan: FrameworkPlan,
    panels: dict[str, pd.DataFrame],
    *,
    allow_partial: bool = True,
    regime_by_date: Any = None,
) -> ComposeReport:
    """方案权重 × 各子策略日频权重面板 → 线性合成组合面板（纯函数，不改入参）。

    语义:
        静态（regime_by_date=None，二期语义逐位一致）:
            W(t, s) = Σ_i α_i · w_i(t, s)，i ∈ 参与成员（面板存在且非空者）。
        动态（regime_by_date 非空，三期）:
            W(t, s) = Σ_i α_i(t) · w_i(t, s)，α_i(t) = 当日 regime 查 plan.regime_overrides
            （未覆盖 regime/日期回退基准权重，逐组落 regime_day_counts 披露——查表不做
            判定，禁自造 regime 判定逻辑，宪章 §3 约束三）。
        - 缺失面板的成员跳过并记入 skipped（reason 落报告，禁静默）。
        - 参与成员 α 合计 α_total < 1（tick-only 跳过等）:
          allow_partial=True → 显式等比再归一化（静态 rescale_factor；动态按 regime 组
          披露 regime_rescale_factors）；allow_partial=False → FrameworkValidationError。
        - 行级 Σw=1 校验: Σ>0 的行归一至 1.0（偏差计入 notes）；全零行保留（现金日）。

    Args:
        plan: 整装方案（权重 α_i；动态模式另含 regime_overrides）。
        panels: {strategy_id: date×symbol 权重面板}（引擎 signals 同构）。
        allow_partial: 参与权重合计<1 时是否显式再归一化（False=严格拒绝）。
        regime_by_date: regime 日序（{date-like: state} 映射或 pd.Series）；None=静态模式。
            state 合法值=REGIME_STATES 7 态（真源 regime_detector），非法 fail-closed 拒绝。

    Returns:
        ComposeReport（panel + participants/skipped/alpha_total/rescale_factor/notes；
        动态模式另含 regime_day_counts/regime_rescale_factors）。

    Raises:
        FrameworkValidationError: 无任何参与成员 / 参与权重合计为 0 / 严格模式下 α_total≠1 /
                                  regime 日序为空或含非法状态/日期。
    """
    if regime_by_date is not None:
        return _compose_weight_panels_dynamic(
            plan, panels, allow_partial=allow_partial, regime_by_date=regime_by_date
        )
    if plan.weights:
        pass  # 权重合法性已由 load_framework_plans 校验
    notes: list[str] = []
    participants: list[str] = []
    skipped: list[tuple[str, str]] = []

    usable: list[tuple[float, pd.DataFrame]] = []
    for w in plan.weights:
        panel = panels.get(w.strategy_id)
        if panel is None or panel.empty:
            skipped.append((w.strategy_id, "panel missing/empty"))
            continue
        usable.append((w.weight, panel))
        participants.append(w.strategy_id)

    if not usable:
        raise FrameworkValidationError("无任何参与成员的面板——组合回测不可执行")

    alpha_total = sum(a for a, _ in usable)
    if alpha_total <= 0.0:
        raise FrameworkValidationError("参与成员权重合计为 0")
    rescale_factor = 1.0
    if abs(alpha_total - 1.0) > _WEIGHT_TOLERANCE:
        if not allow_partial:
            raise FrameworkValidationError(
                f"参与成员权重合计 {alpha_total:.6f} ≠ 1 且 allow_partial=False（严格模式拒绝）"
            )
        rescale_factor = 1.0 / alpha_total
        notes.append(
            f"参与成员权重合计 {alpha_total:.6f}<1（跳过: "
            f"{'; '.join(f'{sid}({reason})' for sid, reason in skipped) or '无'}），"
            f"已显式再归一化 ×{rescale_factor:.6f}（禁静默纪律，ablation 同款）"
        )

    # 联合索引对齐（缺失 date/symbol 填 0），线性加权求和
    union_index = sorted({idx for _, p in usable for idx in p.index.unique()})
    union_cols = sorted({c for _, p in usable for c in p.columns.unique()})
    composed = pd.DataFrame(0.0, index=union_index, columns=union_cols)
    for alpha, panel in usable:
        aligned = panel.reindex(index=union_index, columns=union_cols).fillna(0.0)
        composed = composed.add(aligned * float(alpha))

    composed = composed * rescale_factor

    # 行级 Σw 校验（Σ>0 的行归一至 1.0；全零行保留=现金日，引擎无调仓语义）
    row_sums = composed.sum(axis=1)
    nonzero = row_sums[row_sums.abs() > 1e-12]
    if len(nonzero) > 0:
        max_dev = float((nonzero - 1.0).abs().max())
        if max_dev > 1e-9:
            notes.append(f"行级 Σw 偏差 {max_dev:.3e} 已归一至 1.0（{len(nonzero)} 行）")
            scale = 1.0 / nonzero
            composed.loc[nonzero.index] = composed.loc[nonzero.index].mul(scale, axis=0)

    logger.info(
        "组合面板合成完成: plan=%s 参与=%s 跳过=%s alpha_total=%.6f",
        plan.plan_id,
        participants,
        skipped,
        alpha_total,
    )
    return ComposeReport(
        panel=composed,
        participants=participants,
        skipped=skipped,
        alpha_total=round(alpha_total, 9),
        rescale_factor=round(rescale_factor, 9),
        notes="; ".join(notes),
    )


# ---------------------------------------------------------------------------
# 三期动态合成（逐日 regime 查表——查表不做判定，判定真源=MOD-REGIME-001）
# ---------------------------------------------------------------------------


def _normalize_regime_series(regime_by_date: Any) -> dict[pd.Timestamp, str]:
    """regime 日序归一化：{date-like: state} 映射 / pd.Series → {Timestamp(归一): state}。

    fail-closed 纪律：state 不在 REGIME_STATES 7 态 → 拒绝（regime 错=权重错，
    禁静默回退——宪章 §3 约束三）；日期无法解析 / 日序为空 → 拒绝。

    Raises:
        FrameworkValidationError: 日序为空 / 日期无法解析 / 状态非法。
    """
    if not hasattr(regime_by_date, "items"):
        raise FrameworkValidationError(
            f"regime_by_date 须为 {{date: state}} 映射或 pd.Series，got {type(regime_by_date).__name__}"
        )
    states = _regime_states()
    out: dict[pd.Timestamp, str] = {}
    for k, v in regime_by_date.items():
        try:
            ts = pd.Timestamp(k)
        except (ValueError, TypeError) as exc:
            raise FrameworkValidationError(f"regime 日序日期无法解析: {k!r}") from exc
        if pd.isna(ts):
            raise FrameworkValidationError(f"regime 日序日期无法解析: {k!r}")
        state = str(v).strip()
        if state not in states:
            raise FrameworkValidationError(
                f"regime 日序状态非法: {state!r}（合法 {list(states)}，真源 regime_detector.REGIME_STATES）"
            )
        out[ts.normalize()] = state
    if not out:
        raise FrameworkValidationError("regime 日序为空（动态模式要求非空 {date: regime} 映射）")
    return out


@dataclass(frozen=True)
class _GroupComposeContext:
    """单 regime 组合成的共享上下文（参数对象，防长参数列表 §5.150）。"""

    plan: FrameworkPlan
    union_index: list[Any]
    union_cols: list[Any]
    aligned: dict[str, pd.DataFrame]
    usable: list[tuple[str, pd.DataFrame]]
    allow_partial: bool


def _compose_regime_group(
    ctx: _GroupComposeContext,
    label: str,
    positions: list[int],
) -> tuple[pd.DataFrame, int, float, float]:
    """单 regime 组合成块：有效权重 → 参与合计校验 → 显式再归一化 → 加权求和。

    Returns:
        (block, 日数, 组内参与 α 合计, 组再归一化系数)。

    Raises:
        FrameworkValidationError: 组参与合计为 0 / 严格模式下合计≠1。
    """
    eff = ctx.plan.effective_weights(None if label == _FALLBACK_GROUP_KEY else label)
    eff_map = {w.strategy_id: float(w.weight) for w in eff}
    alpha_total_g = sum(eff_map.get(sid, 0.0) for sid, _ in ctx.usable)
    if alpha_total_g <= 0.0:
        raise FrameworkValidationError(f"regime 组 {label} 参与成员权重合计为 0")
    factor = 1.0
    if abs(alpha_total_g - 1.0) > _WEIGHT_TOLERANCE:
        if not ctx.allow_partial:
            raise FrameworkValidationError(
                f"regime 组 {label} 参与成员权重合计 {alpha_total_g:.6f} ≠ 1 且 "
                f"allow_partial=False（严格模式拒绝）"
            )
        factor = 1.0 / alpha_total_g
    block = pd.DataFrame(
        0.0, index=[ctx.union_index[i] for i in positions], columns=ctx.union_cols
    )
    for sid, _panel in ctx.usable:
        block = block.add(ctx.aligned[sid].iloc[positions] * eff_map.get(sid, 0.0))
    if factor != 1.0:
        block = block * factor
    return block, len(positions), alpha_total_g, factor


def _compose_weight_panels_dynamic(
    plan: FrameworkPlan,
    panels: dict[str, pd.DataFrame],
    *,
    allow_partial: bool,
    regime_by_date: Any,
) -> ComposeReport:
    """三期动态合成：逐日按当日 regime 查 regime_overrides 取 α_i(t)（纯函数，不改入参）。

    分组语义: 当日 regime 命中覆盖表 → 该组权重；未覆盖 regime / 未覆盖日期 →
    __base__ 组（基准权重）。各组独立做参与权重合计校验与显式再归一化（禁静默），
    行级 Σw=1 归一化与静态同款。
    """
    lookup = _normalize_regime_series(regime_by_date)
    notes: list[str] = []
    participants: list[str] = []
    skipped: list[tuple[str, str]] = []
    usable: list[tuple[str, pd.DataFrame]] = []
    for w in plan.weights:
        panel = panels.get(w.strategy_id)
        if panel is None or panel.empty:
            skipped.append((w.strategy_id, "panel missing/empty"))
            continue
        usable.append((w.strategy_id, panel))
        participants.append(w.strategy_id)
    if not usable:
        raise FrameworkValidationError("无任何参与成员的面板——组合回测不可执行")

    override_map = plan.regime_override_map
    union_index = sorted({idx for _, p in usable for idx in p.index.unique()})
    union_cols = sorted({c for _, p in usable for c in p.columns.unique()})
    aligned = {
        sid: p.reindex(index=union_index, columns=union_cols).fillna(0.0) for sid, p in usable
    }

    # 逐行归组（保序）：命中覆盖表的 regime 按状态分组，其余归 __base__
    row_group: list[str] = []
    for ts in union_index:
        state = lookup.get(pd.Timestamp(ts).normalize())
        row_group.append(state if state in override_map else _FALLBACK_GROUP_KEY)

    composed = pd.DataFrame(0.0, index=union_index, columns=union_cols)
    regime_day_counts: dict[str, int] = {}
    regime_rescale_factors: dict[str, float] = {}
    group_alpha_totals: dict[str, float] = {}
    ctx = _GroupComposeContext(
        plan=plan,
        union_index=union_index,
        union_cols=union_cols,
        aligned=aligned,
        usable=usable,
        allow_partial=allow_partial,
    )
    for label in dict.fromkeys(row_group):
        positions = [i for i, g in enumerate(row_group) if g == label]
        block, n_days, alpha_total_g, factor = _compose_regime_group(ctx, label, positions)
        composed.iloc[positions] = block.values
        regime_day_counts[label] = n_days
        group_alpha_totals[label] = alpha_total_g
        if factor != 1.0:
            regime_rescale_factors[label] = round(factor, 9)

    if skipped:
        notes.append(
            "跳过成员: " + "; ".join(f"{sid}({reason})" for sid, reason in skipped)
        )
    group_desc = " ".join(
        f"{label}×{regime_day_counts[label]}日"
        + (f"(×{regime_rescale_factors[label]:.4f} 再归一)" if label in regime_rescale_factors else "")
        for label in regime_day_counts
    )
    notes.insert(
        0,
        f"regime 动态合成: {group_desc}（未覆盖 regime/日期回退基准权重，查表真源 regime_overrides）",
    )

    # 行级 Σw 校验（与静态同款：Σ>0 的行归一至 1.0；全零行保留=现金日）
    row_sums = composed.sum(axis=1)
    nonzero = row_sums[row_sums.abs() > 1e-12]
    if len(nonzero) > 0:
        max_dev = float((nonzero - 1.0).abs().max())
        if max_dev > 1e-9:
            notes.append(f"行级 Σw 偏差 {max_dev:.3e} 已归一至 1.0（{len(nonzero)} 行）")
            scale = 1.0 / nonzero
            composed.loc[nonzero.index] = composed.loc[nonzero.index].mul(scale, axis=0)

    logger.info(
        "组合面板动态合成完成: plan=%s 参与=%s 跳过=%s 组=%s",
        plan.plan_id,
        participants,
        skipped,
        regime_day_counts,
    )
    return ComposeReport(
        panel=composed,
        participants=participants,
        skipped=skipped,
        # 动态模式单值口径=各组最坏情形（alpha_total 取 min / rescale 取 max），逐组真值
        # 在 regime_day_counts/regime_rescale_factors/notes 披露
        alpha_total=round(min(group_alpha_totals.values()), 9),
        rescale_factor=round(max(regime_rescale_factors.values()) if regime_rescale_factors else 1.0, 9),
        notes="; ".join(notes),
        regime_day_counts=regime_day_counts,
        regime_rescale_factors=regime_rescale_factors,
    )


def per_regime_summary(
    plan: FrameworkPlan,
    equity_curve: list[dict[str, Any]],
    regime_by_date: Any,
) -> list[dict[str, Any]]:
    """per-regime 分段摘要（T4 done 响应消费）：各 regime 状态下的组合收益/回撤贡献。

    分组口径与 compose 动态路径一致（覆盖 regime 按状态归组，未覆盖归 __base__）:
        - days: 组内交易日数
        - return_pct: 组内日收益连乘-1（组首日以上一净值点为基——链式贡献语义，
          各组 return 加权不直接可加，仅作分段归因）
        - max_drawdown_pct: 组内净值子序列自身 running peak 最大回撤（段内口径）

    Args:
        plan: 整装方案（提供 regime_overrides 分组语义）。
        equity_curve: [{"timestamp": "YYYY-MM-DD", "equity": float}, ...]（升序）。
        regime_by_date: regime 日序（同 compose.regime_by_date 契约）。

    Returns:
        [{"regime", "days", "return_pct", "max_drawdown_pct"}, ...]（按首日出现序）。
    """
    lookup = _normalize_regime_series(regime_by_date)
    override_map = plan.regime_override_map
    order: list[str] = []
    groups: dict[str, list[tuple[float, float | None]]] = {}
    prev_equity: float | None = None
    for point in equity_curve:
        key = pd.Timestamp(str(point.get("timestamp", ""))[:10])
        state = lookup.get(pd.Timestamp(key).normalize())
        label = state if state in override_map else _FALLBACK_GROUP_KEY
        if label not in groups:
            groups[label] = []
            order.append(label)
        groups[label].append((float(point.get("equity", 0.0)), prev_equity))
        prev_equity = float(point.get("equity", 0.0))

    summary: list[dict[str, Any]] = []
    for label in order:
        ret = 1.0
        peak: float | None = None
        max_dd = 0.0
        for equity, prev in groups[label]:
            base = prev if (prev is not None and prev > 0) else equity
            if base > 0:
                ret *= equity / base
            peak = equity if peak is None else max(peak, equity)
            if peak > 0:
                max_dd = max(max_dd, 1.0 - equity / peak)
        summary.append(
            {
                "regime": label,
                "days": len(groups[label]),
                "return_pct": round((ret - 1.0) * 100.0, 4),
                "max_drawdown_pct": round(max_dd * 100.0, 4),
            }
        )
    return summary


# ---------------------------------------------------------------------------
# 净值对账（验收判据: 抽样≥5 日最大误差 <0.01%）
# ---------------------------------------------------------------------------


def reconcile_composed_nav(
    composed_nav: pd.Series,
    member_navs: dict[str, pd.Series],
    plan: FrameworkPlan,
) -> dict[str, Any]:
    """组合净值 vs 手工按权重加权单策略净值（Σα_i·nav_i）逐日对账。

    线性合成语义下（同价、同成本比例、无约束事件扰动），composed_nav(t) 应等于
    Σ_i α_i·nav_i(t)。约束事件（涨跌停拒单/T+1 不对称）会造成路径二阶差异——
    与 ablation.py 披露口径一致，误差超限的日期单独列出供人工判读。

    Args:
        composed_nav: 组合回测净值序列（引擎 last_portfolio.nav_series，NaT 行已过滤）。
        member_navs: {strategy_id: 该成员单独回测的 nav_series}。
        plan: 整装方案（提供 α_i；仅参与成员参与对账）。

    Returns:
        {"dates": [...], "max_abs_rel_error": float, "over_tolerance": [...],
         "tolerance": 1e-4, "samples": n}
        每日条目: {"date", "composed", "manual", "rel_error"}；over_tolerance 为
        超容差日期清单。
    """
    tolerance = 1e-4  # 0.01%
    # 对账权重与合成侧同口径：仅参与成员（有净值者），并应用再归一化
    # （合成侧 rescale_factor = 1/α_participants；跳过成员的缺口不参与对账分母）
    used: list[str] = []
    alpha_participants = 0.0
    for w in plan.weights:
        if w.strategy_id in member_navs:
            alpha_participants += float(w.weight)
            used.append(w.strategy_id)
    if alpha_participants <= 0.0:
        return {
            "participants_reconciled": [],
            "tolerance": tolerance,
            "samples": 0,
            "max_abs_rel_error": 0.0,
            "over_tolerance": [],
            "dates": [],
        }
    manual = pd.Series(0.0, index=composed_nav.index)
    for w in plan.weights:
        nav = member_navs.get(w.strategy_id)
        if nav is None:
            continue
        aligned = nav.reindex(composed_nav.index).ffill().fillna(0.0)
        manual = manual + aligned * (float(w.weight) / alpha_participants)

    denom = manual.abs().where(manual.abs() > 1e-9)
    rel_err = ((composed_nav - manual) / denom).abs()
    rows = []
    over: list[str] = []
    for ts in composed_nav.index:
        re_val = float(rel_err.loc[ts]) if pd.notna(rel_err.loc[ts]) else 0.0
        rows.append(
            {
                "date": str(ts)[:10],
                "composed": round(float(composed_nav.loc[ts]), 2),
                "manual": round(float(manual.loc[ts]), 2),
                "rel_error": re_val,
            }
        )
        if re_val > tolerance:
            over.append(str(ts)[:10])
    return {
        "participants_reconciled": used,
        "tolerance": tolerance,
        "samples": len(rows),
        "max_abs_rel_error": round(float(rel_err.max()) if len(rel_err) else 0.0, 9),
        "over_tolerance": over,
        "dates": rows,
    }


# ---------------------------------------------------------------------------
# 整装回测主入口（复用引擎，禁重写撮合）
# ---------------------------------------------------------------------------


def _resolve_member_modes() -> tuple[set[str], set[str]]:
    """解析日频/tick 两注册表的成员 ID 集合（autodiscover 失败降级为空集）。"""
    daily_ids: set[str] = set()
    tick_ids: set[str] = set()
    try:
        from zephyr.governance.strategies.strategy_base import StrategyRegistry, autodiscover_strategies

        try:
            autodiscover_strategies("zephyr.pf_core")
        except Exception:  # noqa: BLE001 — 已注册集合仍可用
            pass
        daily_ids = set(StrategyRegistry.list_all().keys())
    except Exception as exc:  # noqa: BLE001 — 注册表不可用时 tick 判定降级
        logger.warning("日频策略注册表不可用: %s", exc)
    try:
        from zephyr.pf_core.strategy_engine.tick_strategy_base import TickStrategyBase, autodiscover_tick_strategies

        try:
            autodiscover_tick_strategies("zephyr.pf_core")
        except Exception:  # noqa: BLE001
            pass
        tick_ids = set(getattr(TickStrategyBase, "_registry", {}).keys())
    except Exception as exc:  # noqa: BLE001
        logger.warning("tick 策略注册表不可用: %s", exc)
    return daily_ids, tick_ids


def _collect_timeseries(engine: Any) -> dict[str, Any]:
    """从引擎 last_portfolio 收集时序（与 scripts/run_backtest._collect_timeseries 同契约）。

    说明: scripts 层的收集器无法从 src 模块导入（分层边界），本处按同一 sink 契约
    实现最小集（equity_curve/trade_log/drawdown_curve；benchmark 引擎层无通道，留 None）。
    """
    portfolio = getattr(engine, "last_portfolio", None)
    if portfolio is None:
        return {"equity_curve": [], "trade_log": [], "drawdown_curve": [], "benchmark_curve": None}
    equity_curve: list[dict[str, Any]] = []
    drawdown_curve: list[dict[str, Any]] = []
    nav = portfolio.nav_series
    if nav is not None and len(nav) > 0:
        nav = nav[nav.index.notna()]  # 首日 NaT 初始化行过滤（runner 同款）
        peak: float | None = None
        for ts, v in nav.items():
            ts_str = str(ts)[:10]
            equity_curve.append({"timestamp": ts_str, "equity": float(v)})
            peak = float(v) if peak is None else max(peak, float(v))
            dd = (float(v) / peak - 1.0) if peak > 0 else 0.0
            drawdown_curve.append({"timestamp": ts_str, "drawdown": abs(dd)})
    trade_log: list[dict[str, Any]] = []
    for t in getattr(portfolio, "trades_log", []) or []:
        trade_log.append(
            {
                "timestamp": str(t.get("date", ""))[:10],
                "symbol": str(t.get("symbol", "")),
                "side": str(t.get("side", "")).lower(),
                "price": float(t.get("price", 0.0)),
                "quantity": int(t.get("quantity", 0)),
                "commission": float(t.get("commission", 0.0)),
                "decision_price": (
                    float(t["decision_price"]) if t.get("decision_price") is not None else None
                ),
                "order_type": t.get("order_type"),
            }
        )
    return {
        "equity_curve": equity_curve,
        "trade_log": trade_log,
        "drawdown_curve": drawdown_curve,
        "benchmark_curve": None,
    }


@dataclass(frozen=True)
class FrameworkBacktestConfig:
    """整装回测参数对象（run_framework_backtest 的可选参数集合，防长参数列表）。

    Attributes:
        factor_ids: 透传各成员 StrategyRunnerConfig 的因子（全部成员同参——v1 简化）。
        rebalance_freq/top_n/max_single/pit_shift: 透传各成员 StrategyRunnerConfig。
        initial_capital: 初始资金。
        allow_partial: 参与成员权重合计<1 时是否显式再归一化（默认 True+披露）。
        regime_by_date: 三期动态模式 regime 日序（{date: state} 映射或 pd.Series；
            state ∈ REGIME_STATES 7 态，真源 regime_detector）；None=静态模式（二期
            语义逐位一致）。日序生产责任=真源检测器离线回放，本模块只查表不判定。
        plans_path: 方案配置路径（None=默认真源；测试注入用）。
        storage_path: 产物存储目录（None=data/backtest_artifacts/；测试注入用，
            ARCH-BENCH-LEAK-001 测试禁写生产路径）。
        enable_stk_limit_provider: 涨跌停 provider 开关（引擎默认 True；离线单测
            注入 False 保证确定性，对标 ablation 同款）。
    """

    factor_ids: tuple[str, ...] = ("momentum_20d",)
    rebalance_freq: str = "W-FRI"
    top_n: int = 10
    max_single: float = 0.10
    initial_capital: float = 1_000_000.0
    pit_shift: int = 1
    allow_partial: bool = True
    regime_by_date: Any = None
    plans_path: str | Path | None = None
    storage_path: str | Path | None = None
    enable_stk_limit_provider: bool = True


def _select_vectorizable_members(
    plan: FrameworkPlan,
) -> tuple[list[PlanWeight], list[tuple[str, str]]]:
    """按注册表筛出可向量化成员（tick-only 跳过并披露）。"""
    daily_ids, tick_ids = _resolve_member_modes()
    skipped: list[tuple[str, str]] = []
    members: list[PlanWeight] = []
    for w in plan.weights:
        if w.strategy_id in tick_ids and w.strategy_id not in daily_ids:
            skipped.append((w.strategy_id, "tick-only（向量化整装回测跳过，权重显式再归一化）"))
            continue
        members.append(w)
    return members, skipped


def _build_member_panels(
    plan: FrameworkPlan,
    symbols: list[str],
    start: str,
    end: str,
    config: FrameworkBacktestConfig,
) -> tuple[pd.DataFrame | None, dict[str, pd.DataFrame], list[tuple[str, str]]]:
    """逐成员构建日频权重面板（单成员失败跳过并披露，不拖垮整装回测）。

    Returns:
        (data（首个非空成员的行情，None=全空）, panels, skipped)
    """
    from zephyr.pf_core.strategy_engine.strategy_runner import StrategyRunner, StrategyRunnerConfig

    runner = StrategyRunner()
    panels: dict[str, pd.DataFrame] = {}
    data: pd.DataFrame | None = None
    skipped: list[tuple[str, str]] = []
    for w in plan.weights:
        cfg = StrategyRunnerConfig(
            strategy_id=w.strategy_id,
            factor_ids=tuple(config.factor_ids),
            rebalance_freq=config.rebalance_freq,
            top_n=config.top_n,
            max_single=config.max_single,
            pit_shift=config.pit_shift,
        )
        try:
            data_i, panel_i = runner.build_weight_panel(symbols, start, end, cfg)
        except Exception as exc:  # noqa: BLE001 — 单成员失败跳过并披露（不拖垮整装回测）
            skipped.append((w.strategy_id, f"panel build failed: {str(exc)[:120]}"))
            continue
        if panel_i is None or panel_i.empty or data_i is None or data_i.empty:
            skipped.append((w.strategy_id, "panel/data empty"))
            continue
        if data is None:
            data = data_i
        panels[w.strategy_id] = panel_i
    return data, panels, skipped


def _persist_framework_artifact(
    result: Any,
    engine: Any,
    plan: FrameworkPlan,
    report: ComposeReport,
    config: FrameworkBacktestConfig,
) -> tuple[str, dict[str, Any], dict[str, Any]]:
    """引擎结果 → sink → artifact（bt-fw-* 命名 + plan_id 披露字段）→ 落盘。"""
    from zephyr.backtest.io.backtest_result_sink import sink_backtest_result
    from zephyr.backtest.io.result_repository import build_artifact_from_data, save_artifact

    ts = _collect_timeseries(engine)
    sink = sink_backtest_result(
        result,
        equity_curve=ts.get("equity_curve"),
        trade_log=ts.get("trade_log"),
        drawdown_curve=ts.get("drawdown_curve"),
        benchmark_curve=ts.get("benchmark_curve"),
    )
    artifact = build_artifact_from_data(sink)

    metrics = dict(artifact.metrics or {})
    metrics.update(
        {
            "plan_id": plan.plan_id,
            "plan_name": plan.name,
            "plan_weights": {w.strategy_id: w.weight for w in plan.weights},
            "participants": report.participants,
            "skipped": [list(s) for s in report.skipped],
            "rescale_factor": report.rescale_factor,
            "compose_notes": report.notes,
            "engine_run_id": getattr(result, "idempotency_key", "") or "",
        }
    )
    if report.regime_day_counts:  # 三期动态模式披露（静态模式不加键，二期产物零漂移）
        metrics.update(
            {
                "dynamic": True,
                "regime_day_counts": report.regime_day_counts,
                "regime_rescale_factors": report.regime_rescale_factors,
                "plan_regime_overrides": {
                    state: {w.strategy_id: w.weight for w in weights}
                    for state, weights in plan.regime_overrides
                },
            }
        )
    run_id = f"{_ARTIFACT_RUN_PREFIX}-{uuid.uuid4().hex[:8]}"
    artifact = replace(artifact, run_id=run_id, metrics=metrics)
    saved_run_id = save_artifact(
        artifact, storage_path=Path(config.storage_path) if config.storage_path else None
    )
    return saved_run_id, ts, metrics


def run_framework_backtest(
    plan_id: str,
    symbols: list[str],
    start: str,
    end: str,
    config: FrameworkBacktestConfig | None = None,
) -> dict[str, Any]:
    """整装回测全链路: 方案权重 × 子策略面板 → 合成 → 引擎 → 产物 bt-fw-*.json。

    Args:
        plan_id: 整装方案 ID（fw-defensive / fw-balanced / fw-aggressive）。
        symbols: 标的清单（与单策略回测同口径，纯数字代码可带 .SH/.SZ 后缀）。
        start/end: 回测窗口（YYYY-MM-DD）。
        config: 参数对象（None=FrameworkBacktestConfig() 默认值；cfg.regime_by_date 非空
            时为动态模式——逐日查 regime_overrides，详见 compose_weight_panels）。

    Returns:
        {"ok", "run_id", "plan_id", "participants", "skipped", "rescale_factor",
         "dynamic", "regime_day_counts", "per_regime", "equity_points", "trades",
         "metrics", "warn"}（ok=False 时含 error；动态模式三键有值，静态模式
         dynamic=False/regime_day_counts={} /per_regime=[]——二期消费方零漂移）。
    """
    from zephyr.backtest.implementations.vectorized_engine import BacktestConfig, DefaultBacktestEngine

    cfg = config or FrameworkBacktestConfig()
    plan = get_framework_plan(plan_id, cfg.plans_path)

    members, pre_skipped = _select_vectorizable_members(plan)
    data, panels, build_skipped = _build_member_panels(
        FrameworkPlan(
            plan_id=plan.plan_id,
            name=plan.name,
            risk_profile=plan.risk_profile,
            description=plan.description,
            weights=tuple(members),
        ),
        symbols,
        start,
        end,
        cfg,
    )
    skipped = pre_skipped + build_skipped

    if data is None:
        return {
            "ok": False,
            "error": "all member panels empty（CH 无数据或因子为空）",
            "plan_id": plan.plan_id,
            "skipped": [list(s) for s in skipped],
        }

    # 引擎 index 契约: date level（run_one 同款归一化）
    if isinstance(data.index, pd.MultiIndex):
        names = data.index.names or []
        if "trade_date" in names:
            data.index = data.index.rename({"trade_date": "date"})
        elif "trade_time" in names:
            data.index = data.index.rename({"trade_time": "date"})

    report = compose_weight_panels(
        plan, panels, allow_partial=cfg.allow_partial, regime_by_date=cfg.regime_by_date
    )

    engine = DefaultBacktestEngine(
        config=BacktestConfig(initial_capital=Decimal(str(cfg.initial_capital))),
        enable_stk_limit_provider=cfg.enable_stk_limit_provider,
    )
    result = engine.run(data=data, signals=report.panel, strategy_name=plan.plan_id)

    saved_run_id, ts, artifact_metrics = _persist_framework_artifact(result, engine, plan, report, cfg)

    # 三期动态模式：per-regime 分段摘要（收益/回撤贡献，done 响应消费）
    dynamic = bool(report.regime_day_counts)
    per_regime: list[dict[str, Any]] = []
    if dynamic and cfg.regime_by_date is not None:
        per_regime = per_regime_summary(plan, ts.get("equity_curve") or [], cfg.regime_by_date)

    n_eq = len(ts.get("equity_curve") or [])
    warn = None
    if n_eq == 0:
        warn = "equity_curve empty"
    if report.skipped:
        warn = (warn + "; " if warn else "") + "skipped: " + "; ".join(f"{s}({r})" for s, r in report.skipped)

    return {
        "ok": True,
        "run_id": saved_run_id,
        "plan_id": plan.plan_id,
        "participants": report.participants,
        "skipped": [list(s) for s in report.skipped],
        "rescale_factor": report.rescale_factor,
        "dynamic": dynamic,
        "regime_day_counts": report.regime_day_counts,
        "per_regime": per_regime,
        "equity_points": n_eq,
        "trades": len(ts.get("trade_log") or []),
        "metrics": artifact_metrics,
        "warn": warn,
    }


__all__: Final = (
    "ComposeReport",
    "FrameworkBacktestConfig",
    "FrameworkPlan",
    "FrameworkPlanError",
    "FrameworkValidationError",
    "PlanWeight",
    "compose_weight_panels",
    "get_framework_plan",
    "load_framework_plans",
    "per_regime_summary",
    "reconcile_composed_nav",
    "run_framework_backtest",
)
