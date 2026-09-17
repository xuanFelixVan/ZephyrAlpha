# [BLUEPRINT] MOD-FWCOMP-001 | docs/03_modules/_domain_portfolio_core/framework_composer_blueprint.md
# [MODULE] zephyr.pf_core.strategy_engine.framework_composer
# [DOMAIN] D_PF_CORE
# [DEPENDENCIES] zephyr.pf_core.strategy_engine.strategy_runner; zephyr.backtest.implementations.vectorized_engine; zephyr.backtest.io.backtest_result_sink; zephyr.backtest.io.result_repository; zephyr.regime.core.regime_detector; zephyr.pf_core.strategy_engine.event_sentiment_adapter（lazy，eventdriven 成员负载路 T1A-1）; zephyr.signal_ashare.core.environment_switch（lazy，六段 activation 词表真源 T1A-3）; zephyr.backtest.core.portfolio（lazy，现金账本 Σ 闭合真源 reconcile_cash_ledger）
# [CONSUMERS] src/zephyr/frontend/dashboard/api_server.py(GET /api/framework-plans; POST|GET /api/framework-backtest-run)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 不重写撮合逻辑（复用 DefaultBacktestEngine/StrategyRunner，与本模块正交）; 合成面板 Σw=1 显式归一化并披露（ablation.py 同款纪律，禁静默再分配）; tick-only 成员跳过必须落报告（skipped 落 artifact metrics）; BacktestResult 15 字段契约冻结（plan_id 走 metrics 扩展字段，不动 artifact 顶层 schema）; 本模块只出净值/面板，不写 market_signal_history（管道 A 语义=子策略权重，禁污染）; 三期动态模式=逐日查 regime_overrides 取 α_i(t)（查表不做判定，禁自造 regime 判定逻辑——宪章 §3 约束三），未覆盖 regime/日期回退基准权重并披露（regime_day_counts），状态词表唯一真源=regime_detector.REGIME_STATES（非法状态 fail-closed 拒绝），静态模式（无 regime 序）行为与二期逐位一致; 死成员（面板非空但恒零权重）必进 skipped 带明确 reason 并落 metrics.dead_weight_disclosed，禁只靠行归一 notes 暗示（T1A-2）; 方案权重合法域 [0,1]——0=显式剔除成员（T1A-3）; activation 非当日六段态的成员 α=0（六段词表真源=environment_switch.SIX_STATES，r→六段映射唯一位点 REGIME_STATE_TO_ACTIVATION_PHASE）; RSC-2 Shrinkage 口径=引擎边界节流（run_framework_backtest 经 ShrinkageBacktestEngine 在归一化后乘当日 Shrinkage，compose 面板保持 Σ=1 纪律；剩余质量一律落现金禁再归一化回填——裁定#270；shrinkage_by_date=None/空=满仓逐位零漂移）; #24 执行链证据必落 metrics（cash_ledger_reconciliation 现金腿 Σ 闭合 / target_weight_renormalization 引擎 Σ→1 归一统计 / skipped_fills 拒单分类 / execution_model_disclosure 未建模清单 / signal_age_disclosed 混频龄），缺披露=fail-closed 由 fw_backtest 验收闸否决，禁静默通过
# [MODIFY-GUARD] blueprint
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] FrameworkPlanError: 配置缺失/plan_id 未找到/权重和≠1/strategy_id 为空; FrameworkValidationError: 合成输入面板为空/参与成员为空/shrinkage 日序非法（入口即拒，先于取数与引擎）
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

死成员治本（T1A-1/2/3，矿脉 decision_kernel_mining §4——"16 员方案里 44.1% 权重质量由
死成员与 tick 跳过员构成，经显式再归一静默摊给幸存成员"）:
    - **成员信号契约路由**（_build_member_panels + MEMBER_PAYLOAD_ROUTES）: StrategyRunner
      只会喂扁平标量 ``{sym: float}``，而 eventdriven-sleeve 要 ``{sym: {"event": …}}``、
      multifactor-sleeve 要 ``{sym: {factor_id: val}}``——契约不匹配即恒返回 {} 的死成员。
      现按成员路由接载荷: eventdriven 复用 event_sentiment_adapter.build_event_weight_panel
      （情绪分富负载），multifactor 用 MultifactorPayloadRunner（`_multifactor_payload_runner_cls`
      惰性绑父类）把逐因子值包成嵌套负载——只覆写契约落点一处，面板装配全复用父类。
      daban-sleeve 的四引擎负载批产源已落（ex_core.daban_load_producer），但**本 compose
      面板路未接入**，**不在本班造**——由方案侧显式置 0 权重剔除
      （本模块支持），走 [0,1] 合法域，缺源事实落 metrics.member_signal_contracts。
    - **判死口径**（_partition_members，静/动/对账三处同一真源）: 面板缺失或空 →
      "panel missing/empty"；面板非空但全格为零 → "all-zero weight rows"（死成员，
      旧版只查 DataFrame.empty 查不出这一类）；α=0 → "explicit zero weight (α=0)"。
      三类一律进 skipped 并落 metrics.dead_weight_disclosed（含各员 α/占方案份额/原因），
      不再只靠"行级 Σw 偏差已归一"的数字暗示。
    - **成员零信号日**（部分日死）: 参与成员某日行和=0 时，行归一同样把该日缺口摊给
      幸存成员——落 dead_weight_disclosed.member_zero_row_counts 逐员计数，禁静默。
    - **activation α=0 生效**（T1A-3）: 方案成员可声明 activation=六段状态子集（真源词表
      environment_switch.SIX_STATES），动态模式下当日 regime 经
      REGIME_STATE_TO_ACTIVATION_PHASE 折算六段态，不在集内的成员 α 强制 0 并逐组披露；
      静态模式（无 regime 序）不套 activation（无态可依，行为与二期逐位一致）。

RSC-2 Shrinkage 进整装回测（裁定#270，2026-09-16，双轨披露制）:
    run_framework_backtest 增 config.shrinkage_by_date（{date: factor}，None/空=关）。
    **节流在引擎边界生效而非 compose 层**：引擎 _normalize_day_signals 会把 Σ<1 的
    行放大回满仓（vectorized_engine.py AI-NIGHT-001 口径），compose 层乘 Shrinkage
    会被静默吞掉——故 compose 面板保持 Σ=1 纪律不变，启用时改用
    ShrinkageBacktestEngine（归一化后乘当日 Shrinkage，钳 [0,1] 只减不增，剩余质量
    经 MatchingEngine target_value=NAV×weight 天然落现金，禁再归一化回填=T1A-5
    现金语义合并裁定）。schedule 查表=PIT as-of join（ScheduleShrinkageProvider，
    不查未来；早于首条=1.0 未启动）。验收语义=双跑对照：
    run_framework_backtest_shrinkage_dual 产出开/关两条净值曲线+shrinkage_diff_stamp
    差值章（只披露不否决，C1 一票否决权仍在 C1ShrinkageComparator 域）。
    启用时 metrics 落 shrinkage_disclosure（禁静默），不启用不加键（零漂移）。
    裁定真源: docs/_working/full-auto-chain/S11_assembled_backtest/
    rsc2_shrinkage_backtest_ruling.md + ruling_registry.yaml 裁定#270。

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
import re
import uuid
from dataclasses import dataclass, field, replace
from decimal import Decimal
from functools import cache, lru_cache, partial
from pathlib import Path
from typing import Any, Final, Sequence

import pandas as pd
import yaml

# 引擎引用模块级持有（非函数内惰性导入）：vectorized_engine 腿由本包 __init__ 经
# 同包 strategy_runner 顶层导入**必然已加载**（`zephyr.pf_core.strategy_engine.*`
# 任一导入都会带它），故顶层化零冷导入成本、零新增副作用，且让 DefaultBacktestEngine
# 成为可检的模块属性（默认路健在性探针/消费方 patch 位点有唯一落点，RSC-2 零漂移锚）。
from zephyr.backtest.implementations.vectorized_engine import (
    BacktestConfig,
    DefaultBacktestEngine,
)
from zephyr.shared.io.paths import REPO_ROOT

logger = logging.getLogger(__name__)

DEFAULT_PLANS_PATH = REPO_ROOT / "config" / "framework_plans.yaml"
_WEIGHT_TOLERANCE = 1e-6
_ARTIFACT_RUN_PREFIX = "bt-fw"

_VALID_RISK_PROFILES = ("defensive", "balanced", "aggressive")

# 动态合成回退组标签：未覆盖 regime / 未覆盖日期的行归入此组（用方案基准权重）
_FALLBACK_GROUP_KEY = "__base__"

# REGIME_STATES（7 态）与 SIX_STATES（六段情绪态）两份词表的加载口径同构（惰性导入 +
# 进程内缓存 + 真源不可用 fail-closed），统一由 `_states_from_source` 承担——CloneGuard
# extract 级克隆治本：两条腿共用一条通道，冷导入经济性与缓存语义不变。

#: regime r 态 → 六段情绪态唯一映射位点（T1A-3 activation 折算用）。
#: 真源现状：同一张表在 scripts/backtest/auto_mount.py 的 ``R2SIX``（挂图侧证据分段），
#: src 不能 import scripts（分层边界）故本处独立声明——**两处必须同步**，已登记主会话
#: 收编为共享真源（候选落点 zephyr.shared.contracts 或 config 规则 YAML）。
#: r1 低波震荡/r2 中波震荡无六段对应（auto_mount 同口径"不路由"）；六段的
#: euphoria/distribution 无 r 态来源 ⇒ 只挂这两态的成员在整装口径下恒不激活（如实披露）。
REGIME_STATE_TO_ACTIVATION_PHASE: Final[dict[str, str]] = {
    "r10": "capitulation",
    "r4": "accumulation",
    "r11": "accumulation",
    "r3": "expansion",
    "r12": "ignition",
}

#: activation 无态可依时的口径：strict=激活集未含当前六段态即 α=0（r1/r2/无快照日
#: 一律不激活，宁漏勿误）；lenient=回退方案基准权重（旧行为）。
ACTIVATION_POLICY_STRICT: Final = "strict"
ACTIVATION_POLICY_LENIENT: Final = "lenient"
_ACTIVATION_POLICIES: Final = (ACTIVATION_POLICY_STRICT, ACTIVATION_POLICY_LENIENT)

#: 成员判死原因码（skipped/披露的稳定词，禁散落字符串）
REASON_PANEL_MISSING: Final = "panel missing/empty"
REASON_ALL_ZERO_ROWS: Final = "all-zero weight rows"
REASON_ZERO_WEIGHT: Final = "explicit zero weight (α=0)"
REASON_TICK_ONLY: Final = "tick-only（向量化整装回测跳过，权重显式再归一化）"
#: 成员**构建路**（StrategyRunner / 翻译件适配器）交付的 (行情, 面板) 对不可用——面板
#: 半区为空即整对不可用。与 REASON_PANEL_MISSING 分域不同：后者是**合成侧**对已交面板
#: 字典的判死口径（`_partition_members`，含"字典无此员"），前者是取数/适配腿本身空跑，
#: 处置动作不同（查 runner/适配器 vs 查方案成员表），禁合并成一个字符串吞没分域。
REASON_MEMBER_PANEL_DATA_EMPTY: Final = "panel/data empty"
#: 行级归一"大额"阈值——超过即在 notes 里点名（缺口摊派幅度显著，不可只当数值噪声）
_ROW_NORM_MATERIALITY: Final = 0.05
#: 死成员 α 占方案总额上限——超过即"组合已非方案原意"（44.1% 摊派案例）。
#: 唯一阈值真源：本模块 warn 绊线 + 消费端 `zephyr.strategy_pipeline.fw_backtest`
#: 组合完整性闸均引用本常量，禁消费端另写字面量。
DEAD_MEMBER_ALPHA_SHARE_LIMIT: Final = 0.25


#: 状态词表真源键（`_states_from_source` 的唯一分派入参，禁散落字符串）
STATES_SOURCE_REGIME: Final = "regime"
STATES_SOURCE_ACTIVATION: Final = "activation"
_STATES_SOURCE_KINDS: Final = (STATES_SOURCE_REGIME, STATES_SOURCE_ACTIVATION)


@cache
def _states_from_source(kind: str) -> tuple[str, ...]:
    """状态词表唯一加载通道：惰性 import 真源 + 进程内缓存（两份词表共用一条腿）。

    惰性 import 留在函数内且写成静态 ImportFrom——`importlib.import_module(<str>)` 会被
    depgraph 的 AST 抽取漏记依赖边（generate_project_depgraph 只认 zephyr/scripts 前缀的
    Import/ImportFrom 节点）。
    """
    if kind not in _STATES_SOURCE_KINDS:
        raise FrameworkPlanError(f"未知状态词表真源键: {kind!r}（合法={_STATES_SOURCE_KINDS}）")
    try:
        if kind == STATES_SOURCE_REGIME:
            from zephyr.regime.core.regime_detector import REGIME_STATES as states
        else:
            from zephyr.signal_ashare.core.environment_switch import SIX_STATES as states
    except Exception as exc:  # noqa: BLE001 — 词表真源不可用必须显式暴露
        raise FrameworkPlanError(f"状态词表真源不可用（kind={kind}）: {exc}") from exc
    if not states:
        raise FrameworkPlanError(f"状态词表真源为空（kind={kind}）")
    return tuple(states)


# partial 绑定而非再写一个 def：调用点 `_activation_states()` 语义不变
_activation_states = partial(_states_from_source, STATES_SOURCE_ACTIVATION)


def _activation_phase(regime_state: str | None) -> str | None:
    """regime r 态 → 六段态（无映射/无状态返回 None，由 activation_policy 决定口径）。"""
    if not regime_state:
        return None
    return REGIME_STATE_TO_ACTIVATION_PHASE.get(regime_state)


# partial 绑定（同 `_activation_states`）：调用点 `_regime_states()` 语义不变
_regime_states = partial(_states_from_source, STATES_SOURCE_REGIME)

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
        weight: 资金权重（[0,1]，方案内合计=1.0（容差 1e-6））；**0=显式剔除该成员**
            ——不是"权重极小"，而是"该成员不参与合成"（T1A-3 合法域含 0 的语义），
            判死后走 skipped 披露，不占 α 合计也不受再归一化摊派。
        role: 角色备注（防御底仓/进攻主力等，透传前端展示）。
        activation: 该成员激活的六段情绪态子集（真源词表
            environment_switch.SIX_STATES）；None=全段无限制。动态模式下当日 regime
            折算六段态后不在集内 → α 强制 0（T1A-3）；静态模式不套用（无态可依）。
    """

    strategy_id: str
    weight: float
    role: str = ""
    activation: tuple[str, ...] | None = None


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
        activation_source: activation 声明来源披露（""=未声明；"weights"=成员 activation
            键；"x_tdm_provenance"=生成器产物 x_tdm_provenance.activation_state 兜底；
            两者皆有="weights+x_tdm_provenance"）。
    """

    plan_id: str
    name: str
    risk_profile: str
    description: str
    weights: tuple[PlanWeight, ...]
    regime_overrides: tuple[tuple[str, tuple[PlanWeight, ...]], ...] = ()
    activation_source: str = ""

    @property
    def total_weight(self) -> float:
        return round(sum(w.weight for w in self.weights), 9)

    @property
    def strategy_ids(self) -> tuple[str, ...]:
        return tuple(w.strategy_id for w in self.weights)

    @property
    def weight_map(self) -> dict[str, float]:
        """strategy_id → 基准 α（单一查表口径，禁散落 dict 推导）。"""
        return {w.strategy_id: float(w.weight) for w in self.weights}

    @property
    def activation_map(self) -> dict[str, tuple[str, ...] | None]:
        """strategy_id → 激活六段态集合（None=全段无限制）。"""
        return {w.strategy_id: w.activation for w in self.weights}

    @property
    def has_activation_rules(self) -> bool:
        """方案是否声明了任何 activation（决定动态分组是否按六段态细分）。"""
        return any(w.activation is not None for w in self.weights)

    def max_alpha_across_tables(self, strategy_id: str) -> float:
        """成员在基准表与各 regime 覆盖表中的最大 α（=0 时全表都不参与，面板无需构建）。"""
        best = float(self.weight_map.get(strategy_id, 0.0))
        for _state, override in self.regime_overrides:
            for w in override:
                if w.strategy_id == strategy_id:
                    best = max(best, float(w.weight))
        return best

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
        dead_weight_disclosed: 死成员/静默摊派全量披露（T1A-2 治本，禁只靠 notes 数字暗示）：
            {"schema": 1, "participants": [{strategy_id, alpha}], "skipped_members":
            [{strategy_id, alpha, alpha_share_of_plan, reason, kind}], "participants_alpha_base",
            "skipped_alpha_base", "rescale_factor", "member_zero_row_counts",
            "row_normalization": {rows_total, rows_normalized, max_deviation,
            mean_abs_deviation, material}, "activation": {...}}——落 artifact metrics 同名字段。
    """

    panel: pd.DataFrame
    participants: list[str] = field(default_factory=list)
    skipped: list[tuple[str, str]] = field(default_factory=list)
    alpha_total: float = 1.0
    rescale_factor: float = 1.0
    notes: str = ""
    regime_day_counts: dict[str, int] = field(default_factory=dict)
    regime_rescale_factors: dict[str, float] = field(default_factory=dict)
    dead_weight_disclosed: dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# 方案配置加载（YAML 唯一真源）
# ---------------------------------------------------------------------------


def _parse_activation(
    raw: Any,
    *,
    plan_id: str,
    index: int,
    strategy_id: str,
) -> tuple[str, ...] | None:
    """解析成员 activation 键 → 六段态元组（None=全段无限制）。

    词表真源=environment_switch.SIX_STATES（非法词 fail-closed，禁放行拼错的态名——
    错一个字母即整段静默失活，regime 错=权重错同源纪律）。
    写法兼容：list/tuple（生成器产物口径）、"a+b" / "a,b" 字符串（人读口径）、
    null/缺省（=全段）、空列表（=任何态都不激活，等价显式停用）。

    Raises:
        FrameworkPlanError: 含非六段态 / 类型不可解析。
    """
    if raw is None:
        return None
    states = _activation_states()
    if isinstance(raw, str):
        tokens = [t.strip() for t in re.split(r"[+,/、\s]+", raw) if t.strip()]
    elif isinstance(raw, (list, tuple, set)):
        tokens = [str(t).strip() for t in raw if str(t).strip()]
    else:
        raise FrameworkPlanError(
            f"plan {plan_id} weights[{index}]（{strategy_id}）activation 类型不可解析: "
            f"{raw!r}（合法=六段态列表或 '+' 分隔串）"
        )
    bad = [t for t in tokens if t not in states]
    if bad:
        raise FrameworkPlanError(
            f"plan {plan_id} weights[{index}]（{strategy_id}）activation 含非法六段态: {bad}"
            f"（合法 {list(states)}，真源 environment_switch.SIX_STATES）"
        )
    return tuple(dict.fromkeys(tokens))


def _parse_plan_weights(
    plan_id: str,
    weights_raw: list[Any],
    *,
    activation_state: dict[str, tuple[str, ...] | None] | None = None,
    is_override_table: bool = False,
) -> list[PlanWeight]:
    """解析单个方案的 weights 数组（越界/缺字段校验）。

    合法域 [0,1]：**0=显式剔除该成员**（T1A-3——旧域 (0,1] 不收 0，导致"想停用某成员
    只能改方案删条目"，而生成器产物禁手改，停用意图无处表达）。

    Args:
        activation_state: x_tdm_provenance.activation_state 兜底表（成员无显式
            activation 键时按此声明；None=无兜底）。
        is_override_table: True=regime 覆盖表条目（activation 只允许在基准 weights
            声明，覆盖表再声明=两个真源，fail-closed 拒绝）。

    Raises:
        FrameworkPlanError: strategy_id 为空 / weight 非数值或越界 [0,1] /
                            activation 非法 / 覆盖表声明 activation。
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
        if weight < 0.0 or weight > 1.0:
            raise FrameworkPlanError(
                f"plan {plan_id} weights[{j}]（{sid}）weight 越界: {weight}（合法 [0,1]，"
                f"0=显式剔除该成员）"
            )
        if "activation" in w:
            if is_override_table:
                raise FrameworkPlanError(
                    f"plan {plan_id} weights[{j}]（{sid}）regime 覆盖表不得声明 activation"
                    "（activation 是成员属性，唯一声明位=基准 weights）"
                )
            activation = _parse_activation(w.get("activation"), plan_id=plan_id, index=j, strategy_id=sid)
        elif activation_state is not None:
            activation = activation_state.get(sid)
        else:
            activation = None
        weights.append(
            PlanWeight(
                strategy_id=sid,
                weight=weight,
                role=str(w.get("role", "")),
                activation=activation,
            )
        )
    return weights


def _parse_regime_overrides(
    plan_id: str,
    raw: Any,
    base_weights: list[PlanWeight],
) -> tuple[tuple[str, tuple[PlanWeight, ...]], ...]:
    """解析方案 regime_overrides（三期：键=REGIME_STATES 7 态，值=完整权重覆盖表）。

    纪律: 键词表唯一真源=regime_detector.REGIME_STATES（非法键 fail-closed）；
    覆盖表成员集合必须与基准 weights 一致（仅权重不同）；每套覆盖表 Σ=1（容差同基准）；
    覆盖表条目不得声明 activation（成员属性，唯一声明位=基准 weights）。

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
        oweights = tuple(
            _parse_plan_weights(
                f"{plan_id}·regime {state_key}", rows or [], is_override_table=True
            )
        )
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


def _plan_activation_state(
    p: dict[str, Any], plan_id: str
) -> dict[str, tuple[str, ...] | None]:
    """生成器产物 ``x_tdm_provenance.activation_state`` → {strategy_id: 六段态元组|None}。

    为什么要读它（T1A-3）: fw-tdm-current 是 generate_framework_plan_from_tdm.py 的产物
    （运维红线 5——禁手工维护），activation 已经以 activation_state 键落在 YAML 里但
    composer 从不读——**读现成真源**比要求 Owner 手改一份 regime_overrides 覆盖表更
    抗漂移（重跑生成器不会丢语义，覆盖表手写块会被生成器管养路径绕过）。

    未列出的成员=全段无限制（None）。activation 非法词 fail-closed（同 weights 口径）。
    """
    prov = p.get("x_tdm_provenance")
    rows = prov.get("activation_state") if isinstance(prov, dict) else None
    out: dict[str, tuple[str, ...] | None] = {}
    if not isinstance(rows, list):
        return out
    for j, row in enumerate(rows):
        if not isinstance(row, dict):
            continue
        sid = str(row.get("strategy_ref", "")).strip()
        if not sid:
            continue
        out[sid] = _parse_activation(row.get("activation"), plan_id=plan_id, index=j, strategy_id=sid)
    return out


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

    weights_raw = p.get("weights") or []
    prov_activation = _plan_activation_state(p, plan_id)
    weights = _parse_plan_weights(plan_id, weights_raw, activation_state=prov_activation)
    total = sum(w.weight for w in weights)
    if abs(total - 1.0) > _WEIGHT_TOLERANCE:
        raise FrameworkPlanError(f"plan {plan_id} 权重合计≠1: {total:.9f}（容差 {_WEIGHT_TOLERANCE}）")

    regime_overrides = _parse_regime_overrides(plan_id, p.get("regime_overrides"), weights)

    sources: list[str] = []
    if any(isinstance(w, dict) and "activation" in w for w in weights_raw):
        sources.append("weights")
    if prov_activation:
        sources.append("x_tdm_provenance")

    return FrameworkPlan(
        plan_id=plan_id,
        name=str(p.get("name_zh", plan_id)),
        risk_profile=risk_profile,
        description=str(p.get("description", "")),
        weights=tuple(weights),
        regime_overrides=regime_overrides,
        activation_source="+".join(sources),
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
# 成员判死与摊派披露（T1A-2——静/动/对账三处共用同一判据，禁各写一套）
# ---------------------------------------------------------------------------


def _panel_is_all_zero(panel: pd.DataFrame) -> bool:
    """面板非空但**全格为零**＝死成员（旧判定只查 DataFrame.empty，查不出这一类）。

    矿脉实证：multifactor/daban/eventdriven 三员信号契约不匹配时策略恒返回 {}，
    runner 组装出的面板形状正常但整表为 0 → 旧口径把它当"真出权重的参与成员"，
    其 α 经行归一静默摊派给幸存成员。
    """
    try:
        arr = panel.abs().fillna(0.0).to_numpy()
    except (TypeError, ValueError):  # 非数值面板＝无法判定为全零（保守按参与处理）
        return False
    if arr.size == 0:
        return True
    return float(arr.sum()) <= 1e-15


def _partition_members(
    plan: FrameworkPlan,
    panels: dict[str, pd.DataFrame],
    *,
    prior_skipped: Sequence[tuple[str, str]] = (),
    dynamic: bool = False,
) -> tuple[list[tuple[str, float, pd.DataFrame]], list[tuple[str, str]], list[dict[str, Any]]]:
    """成员三分类（唯一判据位点）：参与 / 跳过（带原因）/ 死成员披露条目。

    判死优先级（每一类都落 skipped，禁静默）：
        1. α=0 → 显式剔除（配置决策，面板无需构建）；
        2. 上游游已判跳（tick-only 等）→ 沿用其 reason（不降级成 "panel missing"）；
        3. 面板缺失/空 → panel missing/empty；
        4. 面板非空但全格为零 → all-zero weight rows（本批新增，即"死成员假组合"根因）。

    Args:
        dynamic: True=动态（regime 覆盖表）模式。此时"α=0 剔除"按
            ``max_alpha_across_tables`` 判——基准表 0 但某 regime 覆盖表非 0 的成员
            在该 regime 日仍可参与，只看基准表会与构建侧（`_build_member_panels`
            同用 max_alpha_across_tables 决定是否取数）判据打架。披露 α 仍报基准值
            （非 0 时另附 ``alpha_max_across_tables``），静态模式该标志恒 False，
            二期语义逐位一致。

    Returns:
        (usable=[(sid, 基准 α, panel)], skipped=[(sid, reason)], dead_entries=[披露条目])
    """
    prior = {sid: reason for sid, reason in prior_skipped}
    plan_total = plan.total_weight or 1.0
    usable: list[tuple[str, float, pd.DataFrame]] = []
    skipped: list[tuple[str, str]] = []
    dead: list[dict[str, Any]] = []
    for w in plan.weights:
        sid = w.strategy_id
        alpha = float(w.weight)
        alpha_max = plan.max_alpha_across_tables(sid) if dynamic else alpha
        panel = panels.get(sid)
        kind: str
        if alpha_max == 0.0:
            reason, kind = REASON_ZERO_WEIGHT, "explicit-zero-weight"
        elif sid in prior:
            reason, kind = prior[sid], "upstream-skipped"
        elif panel is None or panel.empty:
            reason, kind = REASON_PANEL_MISSING, "panel-missing-or-empty"
        elif _panel_is_all_zero(panel):
            reason, kind = REASON_ALL_ZERO_ROWS, "dead-member"
        else:
            usable.append((sid, alpha, panel))
            continue
        skipped.append((sid, reason))
        entry: dict[str, Any] = {
            "strategy_id": sid,
            "alpha": round(alpha, 9),
            "alpha_share_of_plan": round(alpha / plan_total, 9) if plan_total else 0.0,
            "reason": reason,
            "kind": kind,
        }
        if alpha_max != alpha:
            entry["alpha_max_across_tables"] = round(alpha_max, 9)
        dead.append(entry)
    return usable, skipped, dead


def _row_normalization_stats(composed: pd.DataFrame) -> dict[str, Any]:
    """行级 Σw 归一前的质量统计（把"摊派了多少"变成可读数字，T1A-2）。"""
    row_sums = composed.sum(axis=1)
    nonzero = row_sums[row_sums.abs() > 1e-12]
    devs = (nonzero - 1.0).abs()
    return {
        "rows_total": int(len(row_sums)),
        "rows_all_zero": int(len(row_sums) - len(nonzero)),
        "rows_normalized": int((devs > 1e-9).sum()),
        "max_deviation": round(float(devs.max()), 9) if len(devs) else 0.0,
        "mean_abs_deviation": round(float(devs.mean()), 9) if len(devs) else 0.0,
        "materiality_threshold": _ROW_NORM_MATERIALITY,
        "material": bool(len(devs) and float(devs.max()) > _ROW_NORM_MATERIALITY),
    }


def _normalize_rows_with_disclosure(
    composed: pd.DataFrame,
    notes: list[str],
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """行级 Σw=1 归一（Σ>0 行归一；全零行保留=现金日）+ 偏差披露。

    大额偏差（>``_ROW_NORM_MATERIALITY``）单独点名"缺口由幸存成员摊派"——这是
    死成员问题的第二个静默通道（成员部分日无信号），逐员零信号日计数另落披露。
    """
    stats = _row_normalization_stats(composed)
    if stats["rows_normalized"] == 0:
        return composed, stats
    row_sums = composed.sum(axis=1)
    nonzero = row_sums[row_sums.abs() > 1e-12]
    scale = 1.0 / nonzero
    composed = composed.copy()
    composed.loc[nonzero.index] = composed.loc[nonzero.index].mul(scale, axis=0)
    if stats["material"]:
        notes.append(
            f"行级 Σw 偏差最大 {stats['max_deviation']:.4f}（>{_ROW_NORM_MATERIALITY} 显著阈值）"
            f"已归一至 1.0（{stats['rows_normalized']} 行）——该日缺口由幸存成员按 α 摊派承担，"
            f"逐员零信号日计数见 metrics.dead_weight_disclosed.member_zero_row_counts"
        )
    else:
        notes.append(
            f"行级 Σw 偏差 {stats['max_deviation']:.3e} 已归一至 1.0（{stats['rows_normalized']} 行）"
        )
    return composed, stats


def _member_zero_row_counts(
    aligned: dict[str, pd.DataFrame],
    usable: Sequence[tuple[str, float, pd.DataFrame]],
) -> dict[str, int]:
    """参与成员"当日无信号"行数（部分日死——行归一把该日缺口摊给同日的其他成员）。"""
    out: dict[str, int] = {}
    for sid, _alpha, _panel in usable:
        frame = aligned.get(sid)
        if frame is None:
            continue
        out[sid] = int((frame.abs().sum(axis=1) <= 1e-15).sum())
    return out


def _dead_weight_disclosure(
    plan: FrameworkPlan,
    *,
    usable: Sequence[tuple[str, float, pd.DataFrame]],
    dead_entries: Sequence[dict[str, Any]],
    rescale_factor: float,
    alpha_total: float,
    zero_row_counts: dict[str, int],
    row_stats: dict[str, Any],
    activation: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """组装 metrics.dead_weight_disclosed（JSON 可序列化，验收字段）。"""
    plan_total = plan.total_weight or 1.0
    skipped_alpha = sum(float(e["alpha"]) for e in dead_entries)
    return {
        "schema": 1,
        "plan_id": plan.plan_id,
        "plan_weight_total": round(plan_total, 9),
        "participants": [
            {
                "strategy_id": sid,
                "alpha": round(alpha, 9),
                "alpha_share_of_participating_base": round(
                    alpha / alpha_total, 9
                )
                if alpha_total
                else 0.0,
                "zero_signal_rows": int(zero_row_counts.get(sid, 0)),
            }
            for sid, alpha, _ in usable
        ],
        "skipped_members": [dict(e) for e in dead_entries],
        "member_zero_row_counts": {k: int(v) for k, v in zero_row_counts.items()},
        "participants_alpha_base": round(alpha_total, 9),
        "skipped_alpha_base": round(skipped_alpha, 9),
        "skipped_alpha_share_of_plan": round(skipped_alpha / plan_total, 9) if plan_total else 0.0,
        "dead_member_alpha_base": round(
            sum(float(e["alpha"]) for e in dead_entries if e["kind"] == "dead-member"), 9
        ),
        "explicit_zero_weight_alpha": round(
            sum(float(e["alpha"]) for e in dead_entries if e["kind"] == "explicit-zero-weight"), 9
        ),
        "rescale_factor": round(float(rescale_factor), 9),
        "row_normalization": dict(row_stats),
        "activation": dict(activation or {}),
    }


# ---------------------------------------------------------------------------
# activation 闸（T1A-3——动态模式逐组 α 生效，判据与分组命名单一真源）
# ---------------------------------------------------------------------------


REASON_ACTIVATION_OFF: Final = "activation gated off for all regime days"
#: 无六段态可依（r1/r2 未映射 / 该日无 regime）的组标签后缀
_NO_PHASE_SUFFIX: Final = "no-phase"


def _activation_gated_alpha(
    plan: FrameworkPlan,
    eff: tuple[PlanWeight, ...],
    *,
    phase: str | None,
    activation_policy: str,
) -> tuple[dict[str, float], list[dict[str, Any]]]:
    """有效权重表 × 当日六段态 → 闸后 ``{strategy_id: α}`` + 被闸掉条目。

    闸语义（T1A-3 治本——此前 activation 只在 role 注释里写，代码从不读，
    "只在某段情绪态有效的成员"在其余态照常吃满 α，等于把风险敞口铺开）:
        - 成员未声明 activation（None）→ 全段无限制，α 不变；
        - 声明 ``()`` 空集 → 任何态都不激活（显式停用，两口径一致 α=0）；
        - 当日有六段态且 ∈ 激活集 → α 不变；∉ → α=0；
        - 当日无六段态（r1/r2 未映射、或该日无 regime）→ strict α=0（宁漏勿误，
          与 auto_mount 的"未映射不路由"同口径）/ lenient 回退基准权重。

    Returns:
        ({sid: 闸后 α}, [{"strategy_id", "alpha", "reason"}]——闸掉且原本 α>0 者)
    """
    activation_map = plan.activation_map
    out: dict[str, float] = {}
    gated: list[dict[str, Any]] = []
    for w in eff:
        sid = w.strategy_id
        alpha = float(w.weight)
        act = activation_map.get(sid)
        if act is None:
            out[sid] = alpha
            continue
        if len(act) == 0:
            reason = "activation declared empty (never active)"
        elif phase is None:
            if activation_policy == ACTIVATION_POLICY_LENIENT:
                out[sid] = alpha
                continue
            reason = "no six-phase today (strict policy)"
        elif phase in act:
            out[sid] = alpha
            continue
        else:
            reason = f"phase '{phase}' not in activation {list(act)}"
        out[sid] = 0.0
        if alpha > 0.0:
            gated.append({"strategy_id": sid, "alpha": round(alpha, 9), "reason": reason})
    return out, gated


def _dynamic_group_label(
    plan: FrameworkPlan,
    state: str | None,
    *,
    covered: bool,
    phase: str | None,
) -> str:
    """动态组标签（compose 与 per_regime_summary 共用命名口径）。

    命中覆盖表的 regime → 标签=状态本身（状态唯一定位 α 向量，含 activation 折算）；
    未命中/无状态 → ``__base__``；但方案声明了 activation 时必须再按六段态细分
    （否则同一 ``__base__`` 标签下 capitulation 日与 expansion 日共用一张 α 表，
    闸语义会被组内平均掉）。
    """
    if covered and state is not None:
        return state
    if not plan.has_activation_rules:
        return _FALLBACK_GROUP_KEY
    return f"{_FALLBACK_GROUP_KEY}#{phase or _NO_PHASE_SUFFIX}"


@dataclass(frozen=True)
class _DynamicGrouping:
    """逐日分组结果（动态合成与面板对账共用——两处分组口径必须逐位一致）。"""

    labels: tuple[str, ...]  # 组序（按首次出现日排序）
    positions: dict[str, tuple[int, ...]]  # label -> union_index 行位置
    alphas: dict[str, dict[str, float]]  # label -> {sid: 闸后 α}
    gated: dict[str, list[dict[str, Any]]]  # label -> 闸掉条目
    state_of: dict[str, str]  # label -> regime 状态（回退组=空串）
    phase_of: dict[str, str]  # label -> 六段态（无映射=``no-phase``）
    row_alphas: tuple[dict[str, float], ...]  # union_index 逐行闸后 α（对账复算用）
    always_off: tuple[str, ...]  # 所有组都被闸到 α=0 的成员（判死进 skipped）


def _group_dynamic_rows(
    plan: FrameworkPlan,
    usable: Sequence[tuple[str, float, pd.DataFrame]],
    union_index: Sequence[Any],
    lookup: dict[pd.Timestamp, str],
    *,
    activation_policy: str,
) -> _DynamicGrouping:
    """逐日归组（查表不判定）：当日 regime → 有效权重表 → activation 闸 → 组。

    同 (regime 状态, 六段态) 的日必归同一组（组内 α 向量相同），组的 α 合计/再归一
    系数按组独立核算——动态模式"禁静默"的落点。
    """
    override_map = plan.regime_override_map
    sids = tuple(sid for sid, _a, _p in usable)
    cache: dict[tuple[str | None, str | None], tuple[str, dict[str, float], list[dict[str, Any]]]] = {}
    row_labels: list[str] = []
    row_alphas: list[dict[str, float]] = []
    row_state: list[str | None] = []
    row_phase: list[str | None] = []
    row_gated: list[list[dict[str, Any]]] = []
    for ts in union_index:
        state = lookup.get(pd.Timestamp(ts).normalize())
        covered = state is not None and state in override_map
        phase = _activation_phase(state)
        key = (state if covered else None, phase)
        if key not in cache:
            eff = plan.effective_weights(state if covered else None)
            alphas, gated_rows = _activation_gated_alpha(
                plan, eff, phase=phase, activation_policy=activation_policy
            )
            label = _dynamic_group_label(plan, state, covered=covered, phase=phase)
            cache[key] = (label, alphas, gated_rows)
        label, alphas, gated_rows = cache[key]
        row_labels.append(label)
        row_alphas.append(alphas)
        row_state.append(state)
        row_phase.append(phase)
        row_gated.append(gated_rows)

    labels: list[str] = []
    positions: dict[str, list[int]] = {}
    alphas_by_label: dict[str, dict[str, float]] = {}
    gated_by_label: dict[str, list[dict[str, Any]]] = {}
    state_of: dict[str, str] = {}
    phase_of: dict[str, str] = {}
    for i, label in enumerate(row_labels):
        if label not in positions:
            positions[label] = []
            labels.append(label)
            alphas_by_label[label] = row_alphas[i]
            gated_by_label[label] = list(row_gated[i])
            state_of[label] = row_state[i] or ""
            phase_of[label] = row_phase[i] or _NO_PHASE_SUFFIX
        positions[label].append(i)

    always_off = tuple(
        sid
        for sid in sids
        if all(float(alphas_by_label[lab].get(sid, 0.0)) == 0.0 for lab in labels)
    )
    return _DynamicGrouping(
        labels=tuple(labels),
        positions={k: tuple(v) for k, v in positions.items()},
        alphas=alphas_by_label,
        gated=gated_by_label,
        state_of=state_of,
        phase_of=phase_of,
        row_alphas=tuple(row_alphas),
        always_off=always_off,
    )


# ---------------------------------------------------------------------------
# 合成算子（与 ablation.ablate_weight_panel 姊妹——剥离/叠加正交，禁合并）
# ---------------------------------------------------------------------------


def compose_weight_panels(
    plan: FrameworkPlan,
    panels: dict[str, pd.DataFrame],
    *,
    allow_partial: bool = True,
    regime_by_date: Any = None,
    prior_skipped: Sequence[tuple[str, str]] = (),
    activation_policy: str = ACTIVATION_POLICY_STRICT,
) -> ComposeReport:
    """方案权重 × 各子策略日频权重面板 → 线性合成组合面板（纯函数，不改入参）。

    语义:
        静态（regime_by_date=None，二期语义逐位一致）:
            W(t, s) = Σ_i α_i · w_i(t, s)，i ∈ 参与成员（有面板、非空、非全零、α>0 者）。
        动态（regime_by_date 非空，三期）:
            W(t, s) = Σ_i α_i(t) · w_i(t, s)，α_i(t) = 当日 regime 查 plan.regime_overrides
            （未覆盖 regime/日期回退基准权重，逐组落 regime_day_counts 披露——查表不做
            判定，禁自造 regime 判定逻辑，宪章 §3 约束三）；方案声明 activation 时再乘
            激活闸（当日六段态不在成员 activation 集内 → α=0，T1A-3）。
        - 不参与合成的成员一律进 skipped 带明确 reason（_partition_members 四分类：
          α=0 / 上游游跳过 / 面板缺失空 / 面板全零死成员），禁静默。
        - 参与成员 α 合计 α_total < 1（跳过成员缺口）:
          allow_partial=True → 显式等比再归一化（静态 rescale_factor；动态按 regime 组
          披露 regime_rescale_factors）；allow_partial=False → FrameworkValidationError。
        - 行级 Σw=1 校验: Σ>0 的行归一至 1.0（偏差计入 notes + dead_weight_disclosed）；
          全零行保留（现金日）。

    Args:
        plan: 整装方案（权重 α_i；动态模式另含 regime_overrides/activation）。
        panels: {strategy_id: date×symbol 权重面板}（引擎 signals 同构）。
        allow_partial: 参与权重合计<1 时是否显式再归一化（False=严格拒绝）。
        regime_by_date: regime 日序（{date-like: state} 映射或 pd.Series）；None=静态模式。
            state 合法值=REGIME_STATES 7 态（真源 regime_detector），非法 fail-closed 拒绝。
        prior_skipped: 上游游（run_framework_backtest）已判跳成员及原因（tick-only 等），
            合成侧沿用其 reason，不让它退化成 "panel missing/empty"。
        activation_policy: strict（默认，激活集未含当日六段态即 α=0）| lenient
            （无态可依时回退基准权重）；仅动态模式生效。

    Returns:
        ComposeReport（panel + participants/skipped/alpha_total/rescale_factor/notes/
        dead_weight_disclosed；动态模式另含 regime_day_counts/regime_rescale_factors）。

    Raises:
        FrameworkValidationError: 无任何参与成员 / 参与权重合计为 0 / 严格模式下 α_total≠1 /
                                  regime 日序为空或含非法状态/日期 / activation_policy 非法。
    """
    if activation_policy not in _ACTIVATION_POLICIES:
        raise FrameworkValidationError(
            f"activation_policy 非法: {activation_policy}（合法 {list(_ACTIVATION_POLICIES)}）"
        )
    if regime_by_date is not None:
        return _compose_weight_panels_dynamic(
            plan,
            panels,
            allow_partial=allow_partial,
            regime_by_date=regime_by_date,
            prior_skipped=prior_skipped,
            activation_policy=activation_policy,
        )
    notes: list[str] = []

    usable, skipped, dead_entries = _partition_members(
        plan, panels, prior_skipped=prior_skipped
    )
    participants = [sid for sid, _a, _p in usable]

    if not usable:
        raise FrameworkValidationError(
            "无任何参与成员的面板——组合回测不可执行（跳过明细: "
            + "; ".join(f"{sid}({reason})" for sid, reason in skipped)
            + "）"
        )

    alpha_total = sum(a for _sid, a, _ in usable)
    if alpha_total <= 0.0:
        raise FrameworkValidationError("参与成员权重合计为 0")
    rescale_factor = 1.0
    if abs(alpha_total - 1.0) > _WEIGHT_TOLERANCE:
        if not allow_partial:
            raise FrameworkValidationError(
                f"参与成员权重合计 {alpha_total:.6f} ≠ 1 且 allow_partial=False（严格模式拒绝）"
            )
        rescale_factor = 1.0 / alpha_total
        dead_mass = sum(float(e["alpha"]) for e in dead_entries if e["kind"] == "dead-member")
        notes.append(
            f"参与成员权重合计 {alpha_total:.6f}<1（跳过 {len(dead_entries)} 员，其中死成员"
            f" α 合计 {dead_mass:.6f}＝方案 {dead_mass / (plan.total_weight or 1.0) * 100:.1f}% "
            f"被摊派；明细: "
            f"{'; '.join(f'{sid}({reason})' for sid, reason in skipped) or '无'}），"
            f"已显式再归一化 ×{rescale_factor:.6f}（禁静默纪律，ablation 同款；"
            f"逐员口径见 metrics.dead_weight_disclosed）"
        )

    # 联合索引对齐（缺失 date/symbol 填 0），线性加权求和
    union_index = sorted({idx for _, _, p in usable for idx in p.index.unique()})
    union_cols = sorted({c for _, _, p in usable for c in p.columns.unique()})
    aligned = {
        sid: panel.reindex(index=union_index, columns=union_cols).fillna(0.0)
        for sid, _a, panel in usable
    }
    composed = pd.DataFrame(0.0, index=union_index, columns=union_cols)
    for sid, alpha, _panel in usable:
        composed = composed.add(aligned[sid] * float(alpha))

    composed = composed * rescale_factor

    # 行级 Σw 校验（Σ>0 的行归一至 1.0；全零行保留=现金日，引擎无调仓语义）
    composed, row_stats = _normalize_rows_with_disclosure(composed, notes)

    zero_row_counts = _member_zero_row_counts(aligned, usable)
    disclosure = _dead_weight_disclosure(
        plan,
        usable=usable,
        dead_entries=dead_entries,
        rescale_factor=rescale_factor,
        alpha_total=alpha_total,
        zero_row_counts=zero_row_counts,
        row_stats=row_stats,
        activation={
            "applied": False,
            "note": "静态模式无 regime 序可依，activation 不套用（二期逐位一致锚）",
        },
    )

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
        dead_weight_disclosed=disclosure,
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
    """单 regime 组合成的共享上下文（参数对象，防长参数列表 §5.150）。

    不持有 plan——组内 α 由调用方经"覆盖表查表 + activation 闸"一次性算好传入
    （单一查表口径 `_group_dynamic_rows`，防合成/对账两处各查各的）。
    """

    union_index: list[Any]
    union_cols: list[Any]
    aligned: dict[str, pd.DataFrame]
    usable: Sequence[tuple[str, float, pd.DataFrame]]
    allow_partial: bool


def _compose_regime_group(
    ctx: _GroupComposeContext,
    label: str,
    positions: Sequence[int],
    alphas: dict[str, float],
) -> tuple[pd.DataFrame, int, float, float]:
    """单 regime 组合成块：闸后 α → 参与合计校验 → 显式再归一化 → 加权求和。

    组内 α 合计=0（该组所有成员都被 activation 闸关掉）= **空仓组**，是 activation
    的正常语义（该情绪态不出手），全零行交由行级校验保留为现金日——不当错误抛；
    但 ``allow_partial=False``（严格模式）仍拒绝（缺口无人承担）。

    Returns:
        (block, 日数, 组内参与 α 合计, 组再归一化系数——空仓组记 0.0)。

    Raises:
        FrameworkValidationError: 严格模式下组合计≠1（含 0）。
    """
    idx = [ctx.union_index[i] for i in positions]
    block = pd.DataFrame(0.0, index=idx, columns=ctx.union_cols)
    alpha_total_g = sum(float(alphas.get(sid, 0.0)) for sid, _a, _p in ctx.usable)
    if alpha_total_g <= 0.0:
        if not ctx.allow_partial:
            raise FrameworkValidationError(
                f"regime 组 {label} 参与成员权重合计为 0（activation 闸全关）且 "
                f"allow_partial=False（严格模式拒绝）"
            )
        return block, len(positions), 0.0, 0.0
    factor = 1.0
    if abs(alpha_total_g - 1.0) > _WEIGHT_TOLERANCE:
        if not ctx.allow_partial:
            raise FrameworkValidationError(
                f"regime 组 {label} 参与成员权重合计 {alpha_total_g:.6f} ≠ 1 且 "
                f"allow_partial=False（严格模式拒绝）"
            )
        factor = 1.0 / alpha_total_g
    pos = list(positions)
    for sid, _base_alpha, _panel in ctx.usable:
        alpha = float(alphas.get(sid, 0.0))
        if alpha == 0.0:
            continue  # 闸关成员贡献恒 0，跳过不改数值（省一次全表乘加）
        block = block.add(ctx.aligned[sid].iloc[pos] * alpha)
    if factor != 1.0:
        block = block * factor
    return block, len(positions), alpha_total_g, factor


def _compose_weight_panels_dynamic(
    plan: FrameworkPlan,
    panels: dict[str, pd.DataFrame],
    *,
    allow_partial: bool,
    regime_by_date: Any,
    prior_skipped: Sequence[tuple[str, str]] = (),
    activation_policy: str = ACTIVATION_POLICY_STRICT,
) -> ComposeReport:
    """三期动态合成：逐日按当日 regime 查 regime_overrides 取 α_i(t)（纯函数，不改入参）。

    分组语义: 当日 regime 命中覆盖表 → 该组权重；未覆盖 regime / 未覆盖日期 →
    __base__ 组（基准权重）；方案声明 activation 时 __base__ 再按六段态细分
    （``__base__#capitulation`` 等，见 `_dynamic_group_label`）。各组独立做参与权重
    合计校验与显式再归一化（禁静默），行级 Σw=1 归一化与静态同款。

    成员判死与静态共用 `_partition_members`（T1A-2——旧动态路径只查 DataFrame.empty，
    死成员照样进 participants）；全组都被 activation 闸到 α=0 的成员另记
    ``REASON_ACTIVATION_OFF``（T1A-3）。
    """
    lookup = _normalize_regime_series(regime_by_date)
    notes: list[str] = []
    usable, skipped, dead_entries = _partition_members(
        plan, panels, prior_skipped=prior_skipped, dynamic=True
    )
    if not usable:
        raise FrameworkValidationError(
            "无任何参与成员的面板——组合回测不可执行（跳过明细: "
            + "; ".join(f"{sid}({reason})" for sid, reason in skipped)
            + "）"
        )

    union_index = sorted({idx for _, _, p in usable for idx in p.index.unique()})
    union_cols = sorted({c for _, _, p in usable for c in p.columns.unique()})
    aligned = {
        sid: p.reindex(index=union_index, columns=union_cols).fillna(0.0)
        for sid, _a, p in usable
    }
    grouping = _group_dynamic_rows(
        plan, usable, union_index, lookup, activation_policy=activation_policy
    )

    # 每天都闸到 α=0 的成员＝动态口径下的死成员：移出 participants，进 skipped+披露
    # （面板仍参与 union 索引，α=0 不改任何数值，只改"谁在参与"的披露口径）
    always_off = set(grouping.always_off)
    if always_off:
        plan_total = plan.total_weight or 1.0
        for w in plan.weights:
            if w.strategy_id not in always_off:
                continue
            skipped.append((w.strategy_id, REASON_ACTIVATION_OFF))
            dead_entries.append(
                {
                    "strategy_id": w.strategy_id,
                    "alpha": round(float(w.weight), 9),
                    "alpha_share_of_plan": round(float(w.weight) / plan_total, 9),
                    "reason": REASON_ACTIVATION_OFF,
                    "kind": "activation-gated-off",
                }
            )
    # 动态模式参与成员"真 α"口径 = 各组最大值（基准表 0/覆盖表非 0 的复活成员报基准 0
    # 会让"参与者 α=0"这种自相矛盾的披露重新出现；逐组真值在 activation.groups[].alphas）
    alpha_effective = {
        sid: max((float(a.get(sid, 0.0)) for a in grouping.alphas.values()), default=0.0)
        for sid, _base, _p in usable
    }
    usable_reporting = [
        (sid, alpha_effective.get(sid, base), panel)
        for sid, base, panel in usable
        if sid not in always_off
    ]
    participants = [sid for sid, _a, _p in usable_reporting]

    composed = pd.DataFrame(0.0, index=union_index, columns=union_cols)
    regime_day_counts: dict[str, int] = {}
    regime_rescale_factors: dict[str, float] = {}
    group_alpha_totals: dict[str, float] = {}
    zero_alpha_groups: list[str] = []
    ctx = _GroupComposeContext(
        union_index=union_index,
        union_cols=union_cols,
        aligned=aligned,
        usable=usable,
        allow_partial=allow_partial,
    )
    for label in grouping.labels:
        positions = list(grouping.positions[label])
        block, n_days, alpha_total_g, factor = _compose_regime_group(
            ctx, label, positions, grouping.alphas[label]
        )
        composed.iloc[positions] = block.values
        regime_day_counts[label] = n_days
        group_alpha_totals[label] = alpha_total_g
        if alpha_total_g <= 0.0:
            zero_alpha_groups.append(label)
        elif factor != 1.0:
            regime_rescale_factors[label] = round(factor, 9)
    if not any(v > 0.0 for v in group_alpha_totals.values()):
        raise FrameworkValidationError(
            "所有 regime 组经 activation 闸后 α 合计均为 0——组合无可投资产"
            f"（policy={activation_policy}，组={list(regime_day_counts)}）"
        )

    if skipped:
        notes.append(
            "跳过成员: " + "; ".join(f"{sid}({reason})" for sid, reason in skipped)
        )
    group_desc = " ".join(
        f"{label}×{regime_day_counts[label]}日"
        + (f"(×{regime_rescale_factors[label]:.4f} 再归一)" if label in regime_rescale_factors else "")
        + ("(空仓)" if label in zero_alpha_groups else "")
        for label in regime_day_counts
    )
    notes.insert(
        0,
        f"regime 动态合成: {group_desc}（未覆盖 regime/日期回退基准权重，查表真源 regime_overrides）",
    )
    if plan.has_activation_rules:
        gated_total = sum(len(v) for v in grouping.gated.values())
        notes.append(
            f"activation 闸生效: policy={activation_policy} 声明来源={plan.activation_source or '-'}"
            f"，闸事件 {gated_total} 条（逐组明细见 metrics.dead_weight_disclosed.activation.groups）"
        )
    if always_off:
        notes.append(
            f"activation 全期失活成员 {sorted(always_off)}（每天都 α=0→已移出 participants，"
            f"其权重经再归一化摊给当日激活成员）"
        )

    composed, row_stats = _normalize_rows_with_disclosure(composed, notes)

    nonzero_totals = [v for v in group_alpha_totals.values() if v > 0.0]
    alpha_min = round(min(nonzero_totals), 9)
    rescale_max = round(max(regime_rescale_factors.values()) if regime_rescale_factors else 1.0, 9)
    disclosure = _dead_weight_disclosure(
        plan,
        usable=usable_reporting,
        dead_entries=dead_entries,
        rescale_factor=rescale_max,
        alpha_total=alpha_min,
        zero_row_counts=_member_zero_row_counts(aligned, usable_reporting),
        row_stats=row_stats,
        activation={
            "applied": True,
            "policy": activation_policy,
            "declaration_source": plan.activation_source,
            "declared": {
                sid: list(act)
                for sid, act in plan.activation_map.items()
                if act is not None
            },
            "regime_to_phase": dict(REGIME_STATE_TO_ACTIVATION_PHASE),
            "groups": [
                {
                    "group": label,
                    "regime_state": grouping.state_of[label] or None,
                    "six_phase": None if grouping.phase_of[label] == _NO_PHASE_SUFFIX else grouping.phase_of[label],
                    "days": regime_day_counts[label],
                    "alphas": {
                        sid: round(float(a), 9)
                        for sid, a in grouping.alphas[label].items()
                        if float(a) > 0.0
                    },
                    "alpha_total": round(group_alpha_totals[label], 9),
                    "rescale_factor": regime_rescale_factors.get(label, 1.0),
                    "empty_position": label in zero_alpha_groups,
                    "gated_off": grouping.gated[label],
                }
                for label in grouping.labels
            ],
            "always_inactive_members": sorted(always_off),
            "zero_alpha_groups": zero_alpha_groups,
        },
    )

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
        # 动态模式单值口径=各非空仓组最坏情形（alpha_total 取 min / rescale 取 max），
        # 逐组真值在 regime_day_counts/regime_rescale_factors/activation.groups 披露
        alpha_total=alpha_min,
        rescale_factor=rescale_max,
        notes="; ".join(notes),
        regime_day_counts=regime_day_counts,
        regime_rescale_factors=regime_rescale_factors,
        dead_weight_disclosed=disclosure,
    )


def verify_weight_panel_identity(
    plan: FrameworkPlan,
    panels: dict[str, pd.DataFrame],
    composed: pd.DataFrame,
    regime_by_date: Any = None,
    tolerance: float = 1e-9,
    *,
    prior_skipped: Sequence[tuple[str, str]] = (),
    activation_policy: str = ACTIVATION_POLICY_STRICT,
) -> dict[str, Any]:
    """面板级对账（tracker #275 定案口径①）：按合成公式独立重算并与实际面板逐位对比。

    分工边界（机构 sleeve attribution 同款）：
        - 本函数验「权重合成的数学」——W(t,s)=Σα_i(t)·w_i(t,s) 独立重算（不复用
          compose 的面板产物），逐位硬验收（默认容差 1e-9）。
        - NAV 层残差（整手取整/成本/涨跌停拒绝的执行层效应）属归因披露，不进本容差；
          look-through 混合对账不适用单一账户统一框架（宪章约束二无独立子账户，
          重写引擎亦不消除取整残差）。

    判死与 activation 口径**必须**与 compose 同源（`_partition_members` +
    `_group_dynamic_rows`，T1A-2/3）——"谁参与"是公式定义的一部分，两处各判各的
    会让死成员/被闸成员在 1e-9 绊线上产生假阳性；独立的是**算术**，不是**成员集合**。

    Args:
        plan / panels / regime_by_date: 与 compose_weight_panels 同参。
        composed: 被验面板（compose 产物或引擎实际消费的 signals）。
        tolerance: 逐格精确容差（默认 1e-9）。
        prior_skipped / activation_policy: 与 compose 同参（口径必须一致）。

    Returns:
        {"max_abs_diff", "samples", "over_tolerance_cells", "within_tolerance",
         "tolerance", "note"}（note 披露参与成员口径）。
    """
    usable, _skipped, _dead = _partition_members(
        plan, panels, prior_skipped=prior_skipped, dynamic=regime_by_date is not None
    )
    participants = [sid for sid, _a, _p in usable]
    union_index = list(composed.index)
    union_cols = list(composed.columns)
    if regime_by_date is not None:
        lookup = _normalize_regime_series(regime_by_date)
        grouping = _group_dynamic_rows(
            plan,
            usable,
            union_index,
            lookup,
            activation_policy=activation_policy,
        )
        row_alphas: list[dict[str, float]] = list(grouping.row_alphas)
        mode_note = "逐日 regime 查表+activation 闸"
    else:
        base_map = {w.strategy_id: float(w.weight) for w in plan.weights}
        row_alphas = [base_map for _ in union_index]
        mode_note = "静态基准权重"
    active_members = {
        sid for alphas in row_alphas for sid, a in alphas.items() if float(a) > 0.0
    }

    recomputed = pd.DataFrame(0.0, index=union_index, columns=union_cols)
    for i, ts in enumerate(union_index):
        alphas = row_alphas[i]
        alpha_total = sum(float(alphas.get(sid, 0.0)) for sid in participants)
        if alpha_total <= 0.0:
            continue  # 空仓/现金行（含 activation 全关组）：重算同为全零行
        row = pd.Series(0.0, index=union_cols)
        for sid in participants:
            a = float(alphas.get(sid, 0.0))
            if a == 0.0:
                continue
            aligned = panels[sid].reindex(index=[ts], columns=union_cols).fillna(0.0).iloc[0]
            row = row.add(aligned * a)
        # 与 compose 可观察输出对齐：组内 rescale 后再做行级 Σ→1 归一——行归一吞掉 rescale，
        # 故复算只需 行=Σα_i·w_i 再归一（全零行保留=现金日）
        row_sum = float(row.sum())
        if abs(row_sum) > 1e-12:
            row = row * (1.0 / row_sum)
        recomputed.loc[ts] = row

    diff = (composed - recomputed).abs()
    max_abs = float(diff.to_numpy().max()) if diff.size else 0.0
    over = int((diff > tolerance).to_numpy().sum())
    return {
        "max_abs_diff": round(max_abs, 12),
        "samples": int(diff.size),
        "over_tolerance_cells": over,
        "within_tolerance": over == 0,
        "tolerance": tolerance,
        "note": f"独立复算口径=参与成员({len(active_members)}员有α>0，判死/激活与 compose 同源)×{mode_note}×行归一；NAV 层执行残差另行归因披露",
    }


def per_regime_summary(
    plan: FrameworkPlan,
    equity_curve: list[dict[str, Any]],
    regime_by_date: Any,
) -> list[dict[str, Any]]:
    """per-regime 分段摘要（T4 done 响应消费）：各 regime 状态下的组合收益/回撤贡献。

    分组口径与 compose 动态路径一致（覆盖 regime 按状态归组，未覆盖归 __base__；
    方案声明 activation 时回退组再按六段态细分 ``__base__#<phase>``——同一命名函数
    `_dynamic_group_label`，禁两处各写一遍）:
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
        covered = state is not None and state in override_map
        label = _dynamic_group_label(
            plan, state, covered=covered, phase=_activation_phase(state)
        )
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


# ts 里**不进** `sink_backtest_result` 形参集、改由 artifact `metrics` 显式落盘的键。
# sink 只收 equity/trade/drawdown/benchmark 四条（其 [MODIFY-GUARD] 禁结构变更），
# 其余时序若不在这里登记就会"内存里有、产物里没有"——H4-B 现金腿即栽在此（GT-15）。
# 新增 `_collect_timeseries` 返回键必须二选一：进 sink 形参 或 进本集合，否则测试结构闸红。
_PERSISTED_VIA_METRICS_TS_KEYS: frozenset[str] = frozenset({"cash_curve"})


def _collect_timeseries(engine: Any) -> dict[str, Any]:
    """从引擎 last_portfolio 收集时序（与 scripts/run_backtest._collect_timeseries 同契约）。

    说明: scripts 层的收集器无法从 src 模块导入（分层边界），本处按同一 sink 契约
    实现最小集（equity_curve/cash_curve/trade_log/drawdown_curve；benchmark 引擎层
    无通道，留 None）。

    cash_curve（H4-A，#24）: 净值腿之外必须单独落现金腿——只有合计曲线时，"手续费/
    过户费有没有真扣到现金上"这类账本轧差无法外部复核，主动持现金（Shrinkage 节流）
    的仓位形态也看不见。
    """
    portfolio = getattr(engine, "last_portfolio", None)
    if portfolio is None:
        return {
            "equity_curve": [],
            "cash_curve": [],
            "trade_log": [],
            "drawdown_curve": [],
            "benchmark_curve": None,
        }
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
    cash_curve: list[dict[str, Any]] = [
        {"timestamp": str(d)[:10], "cash": float(c)}
        for d, c in (getattr(portfolio, "cash_history", []) or [])
        if d is not None
    ]
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
        "cash_curve": cash_curve,
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
        activation_policy: activation 闸口径（T1A-3）——``"strict"``（默认，当日无
            六段态可依即 r1/r2/无快照日 ⇒ 声明了 activation 的成员 α=0，宁漏勿误）
            或 ``"lenient"``（无态可依时回退基准权重）。仅动态模式生效：静态模式
            无 regime 序可依，不套用。
        shrinkage_by_date: RSC-2 Shrinkage 节流日序（裁定#270）——{date-like: factor}
            映射，factor 钳 [0,1]（只减不增）；None/空表=关（满仓，既有语义逐位
            零漂移）。启用时引擎改用 ShrinkageBacktestEngine（归一化后乘当日
            Shrinkage，剩余质量落现金，PIT as-of join），面板/合成路径不变。
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
    activation_policy: str = ACTIVATION_POLICY_STRICT
    shrinkage_by_date: Any = None


def _select_vectorizable_members(
    plan: FrameworkPlan,
) -> tuple[list[PlanWeight], list[tuple[str, str]]]:
    """按注册表筛出可向量化成员（tick-only 跳过并披露）。"""
    daily_ids, tick_ids = _resolve_member_modes()
    skipped: list[tuple[str, str]] = []
    members: list[PlanWeight] = []
    for w in plan.weights:
        if w.strategy_id in tick_ids and w.strategy_id not in daily_ids:
            skipped.append((w.strategy_id, REASON_TICK_ONLY))
            continue
        if w.weight == 0.0 and plan.max_alpha_across_tables(w.strategy_id) == 0.0:
            skipped.append((w.strategy_id, REASON_ZERO_WEIGHT))  # 显式剔除，无需构建面板
            continue
        members.append(w)
    return members, skipped


# ---------------------------------------------------------------------------
# 成员信号契约路由（T1A-1——"有面板无载荷"死成员的根因治疗）
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class MemberPayloadRoute:
    """单个成员的信号载荷契约与供给路（落 artifact，禁"为什么这员全零"再靠人肉查）。

    根因（矿脉 decision_kernel_mining §1.3）: StrategyRunner 的契约落点只喂扁平标量
    ``{symbol: float}``（strategy_runner._rebalance_one_day），而部分 sleeve 策略签名
    要求嵌套载荷（eventdriven=``{sym: {"event": {…}}}``、multifactor=
    ``{sym: {factor_id: value}}``）——契约不匹配时策略**如实返回 {}**，runner 组装出
    一张形状正常但全零的面板＝死成员，其 α 经行归一静默摊给幸存成员。
    """

    route: str         # 供给路 ID（``ROUTE_*`` 常量，禁散落字符串）
    contract: str      # 策略侧要求的 signals 形状（人读，落披露）
    disclosure: str    # 强制披露文案；``<FACTOR_IDS>`` 占位符按实际喂入因子替换


#: 供给路 ID（稳定词，产物/前端按此检索）
ROUTE_FLAT: Final = "runner-flat"
ROUTE_EVENT_PANEL: Final = "event-sentiment-adapter"
ROUTE_NESTED_FACTOR: Final = "runner-nested-factor-payload"
ROUTE_NO_DAILY_SOURCE: Final = "no-daily-payload-source"
ROUTE_TRANSLATED: Final = "translated-strategy-adapter"

MEMBER_PAYLOAD_ROUTES: Final[dict[str, MemberPayloadRoute]] = {
    "eventdriven-sleeve": MemberPayloadRoute(
        route=ROUTE_EVENT_PANEL,
        contract='{symbol: {"event": {class_, surprise_direction, sentiment_score, …}}}',
        disclosure=(
            "情绪分富负载由 event_sentiment_adapter.build_event_weight_panel 供"
            "（PIT 窗 [T-1 18:00, T 08:00)，源 c1_market.news_sentiment_window；"
            "空窗日该行全零=引擎 hold 语义）"
        ),
    ),
    "multifactor-sleeve": MemberPayloadRoute(
        route=ROUTE_NESTED_FACTOR,
        contract="{symbol: {factor_id: value}}",
        disclosure=(
            "逐因子嵌套载荷由 _MultifactorPayloadRunner 供（因子值仍按 PIT 平移 "
            "signal[t]=factor[t-pit_shift]）。**降级如实披露**: 整装 runner 当前只喂 "
            "factor_ids=<FACTOR_IDS>（合成法 equal_weight、无 IC 权重注入），单因子"
            "等权==该因子本身 ⇒ 本成员选型退化为单因子 Top<N> 动量，与 topn-momentum "
            "成员高度共线——不是真多因子合成。真多因子须扩 factor_ids 并注入 "
            "constraints[\"ic_weights\"]（MultifactorSleeveStrategy.compute_ic_weights 已有产路）"
        ),
    ),
    "daban-sleeve": MemberPayloadRoute(
        route=ROUTE_NO_DAILY_SOURCE,
        contract="{symbol: {四引擎打板负载（连板/封单/龙头/情绪）}}",
        disclosure=(
            "打板四引擎负载的日频批产源已落地（ex_core.daban_load_producer → "
            "c1_market.daban_engine_load，实盘消费方=daban_sleeve_strategy 的 PIT 真读），"
            "但**本 compose 面板路尚未接入该持久源**——本班不造数据：面板若"
            "全零按死成员披露（metrics.dead_weight_disclosed.skipped_members），"
            "方案侧要停用须显式 weight: 0（合法域 [0,1]，T1A-3）而不是留着一个不出手的成员"
        ),
    ),
}


#: 载荷适配器类缓存（惰性绑父类——见 `_multifactor_payload_runner_cls`）
_MF_PAYLOAD_RUNNER_CLS: type | None = None


def _multifactor_payload_runner_cls() -> type:
    """multifactor-sleeve 载荷适配器类（首次使用才绑父类，进程内缓存）。

    为什么不用模块级 ``class``: 父类 StrategyRunner 所在包链冷导入实测 ~7.5s，而本模块
    是 ``[STARTUP] imported`` 启动路径件（api_server 启动即载）——顶层导入违反惰性导入
    纪律（同 regime/environment_switch 词表手法）。类体只覆写父类两个契约落点，
    面板装配（调仓日选择/PIT/ffill/空面板兜底）全复用——复刻即违反 RULE-CLONEGUARD。

    PIT 铁律不因路由改变: 暂存的逐因子面板同样按 ``signal[t]=factor[t-pit_shift]`` 平移。
    """
    global _MF_PAYLOAD_RUNNER_CLS
    if _MF_PAYLOAD_RUNNER_CLS is not None:
        return _MF_PAYLOAD_RUNNER_CLS

    from zephyr.pf_core.strategy_engine.strategy_runner import StrategyRunner

    class MultifactorPayloadRunner(StrategyRunner):  # noqa: PYI052 — 契约覆写件
        """把扁平 ``{sym: float}`` 换成嵌套 ``{sym: {factor_id: val}}`` 喂策略。"""

        def __init__(self) -> None:
            super().__init__()
            self._raw_factor_panels: dict[str, pd.DataFrame] = {}

        def _build_signal_panel(self, factor_panels: dict, config) -> pd.DataFrame:
            signal_panel = super()._build_signal_panel(factor_panels, config)
            shift = max(int(config.pit_shift), 0)
            self._raw_factor_panels = {
                fid: (fp.shift(shift) if shift > 0 else fp) for fid, fp in factor_panels.items()
            }
            return signal_panel

        def _rebalance_one_day(self, strategy, signal_panel, date, config) -> dict:
            cross = signal_panel.loc[date].dropna()
            if cross.empty:
                return {}
            payload: dict[str, dict[str, float]] = {}
            for sym in cross.index:
                per_factor: dict[str, float] = {}
                for fid, fp in self._raw_factor_panels.items():
                    if date in fp.index and sym in fp.columns:
                        v = fp.at[date, sym]
                        if pd.notna(v):
                            per_factor[fid] = float(v)
                if per_factor:
                    payload[str(sym)] = per_factor
            if not payload:
                return {}
            return strategy.generate_target_weights(
                universe=list(payload.keys()),
                signals=payload,
                constraints={"top_n": config.top_n, "max_single": config.max_single},
            )

    _MF_PAYLOAD_RUNNER_CLS = MultifactorPayloadRunner
    return MultifactorPayloadRunner


def _event_panel_axes(
    history: pd.DataFrame,
) -> tuple[pd.DatetimeIndex, list[str], dict[str, str]]:
    """行情历史 → (交易日轴, 纯数字标的轴, 纯数字→面板原始列名 回程映射)。

    适配层与 load_history 同源口径=纯数字代码（event_sentiment_adapter 不变量）；
    若上游 symbols 带 .SH/.SZ 后缀（面板列=canonical），此处剥后缀喂适配层、
    产面板再映射回 canonical 列名，防 union 对齐时凭空多出一列幽灵标的。
    """
    dates = pd.DatetimeIndex(
        pd.unique(pd.to_datetime(history.index.get_level_values("trade_date")))
    ).sort_values()
    raw = sorted({str(s) for s in history.index.get_level_values("symbol")})
    plain = sorted({(s.split(".")[0] if "." in s else s) for s in raw})
    back: dict[str, str] = {}
    if len(raw) != len(plain):  # 存在后缀——面板列需回程映射
        for s in raw:
            head = s.split(".")[0] if "." in s else s
            if head != s:
                back.setdefault(head, s)
    return dates, plain, back


def _build_member_panels(
    plan: FrameworkPlan,
    symbols: list[str],
    start: str,
    end: str,
    config: FrameworkBacktestConfig,
) -> tuple[pd.DataFrame | None, dict[str, pd.DataFrame], list[tuple[str, str]]]:
    """逐成员构建日频权重面板（单成员失败跳过并披露，不拖垮整装回测）。

    成员路由（两轴，互不影响）:
        1. **载荷契约轴**（T1A-1，`MEMBER_PAYLOAD_ROUTES`）——策略签名要求嵌套载荷的
           成员，扁平 runner 会让它恒返回 {}（死成员）：
           eventdriven-sleeve 走 event_sentiment_adapter 情绪分富负载面板，
           multifactor-sleeve 走 MultifactorPayloadRunner 逐因子嵌套载荷；
        2. **实现形态轴**（S11/C3 断桥②）——``STR-`` 前缀成员走翻译件适配器
           （translated_strategy_adapter，c4_*.py build() 契约→面板），其余走
           StrategyRunner 注册表策略×通用因子。

    α 全表为 0 的成员（显式剔除，T1A-3）直接判死跳过——不浪费一次 CH 取数。
    契约/降级披露是配置的纯函数，另由 `_member_signal_contracts` 产出（不混进取数路径）。

    Returns:
        (data（首个非空成员的行情；成员全建失败但事件路已取到行情时透出该**原对象**，
        None=一次取数都没成功）, panels, skipped)
    """
    from zephyr.pf_core.strategy_engine.strategy_runner import StrategyRunner, StrategyRunnerConfig

    runner = StrategyRunner()
    mf_runner: Any | None = None
    panels: dict[str, pd.DataFrame] = {}
    data: pd.DataFrame | None = None
    history_source: pd.DataFrame | None = None  # 事件路已取行情的原对象（输入透传锚）
    skipped: list[tuple[str, str]] = []
    history_cache: dict[str, pd.DataFrame] = {}

    def _history() -> pd.DataFrame:
        """行情历史（事件路日期轴/标的轴用）——优先复用已建成员的 data，否则取一次。"""
        if "h" not in history_cache:
            from zephyr.factor.core.evaluation.backtest import load_history

            if data is not None and not data.empty:
                history_cache["h"] = data
            else:
                try:
                    history_cache["h"] = load_history(symbols, start, end)
                except Exception as exc:  # noqa: BLE001 — 取数失败降级空表（成员按缺数据披露跳过）
                    logger.warning("事件路 load_history 失败: %s", exc)
                    history_cache["h"] = pd.DataFrame()
        return history_cache["h"]

    for w in plan.weights:
        sid = w.strategy_id
        route = MEMBER_PAYLOAD_ROUTES.get(sid)
        if plan.max_alpha_across_tables(sid) == 0.0:
            skipped.append((sid, REASON_ZERO_WEIGHT))
            continue
        data_i: pd.DataFrame | None
        panel_i: pd.DataFrame | None
        if route is not None and route.route == ROUTE_EVENT_PANEL:
            hist = _history()
            if hist.empty:
                skipped.append((sid, "event route: 行情历史为空（日期轴/标的轴无源）"))
                continue
            data_i = hist
            # 输入透传锚：记下 load_history/复用的**原对象**（禁派生副本）——本员乃至
            # 全员构建失败时由它充当返回的 data，调用方不必为同一窗口再取一次数。
            history_source = hist
            try:
                from zephyr.pf_core.strategy_engine import event_sentiment_adapter as _esa

                dates, plain_universe, col_back = _event_panel_axes(hist)
                ev_panel = _esa.build_event_weight_panel(
                    dates,
                    plain_universe,
                    top_n=config.top_n,
                    max_single=config.max_single,
                )
                if col_back:  # canonical 后缀口径：面板列名映射回其他成员同源
                    ev_panel.columns = [col_back.get(str(c), str(c)) for c in ev_panel.columns]
                panel_i = ev_panel
            except Exception as exc:  # noqa: BLE001 — 单成员失败跳过并披露
                skipped.append((sid, f"event panel build failed: {str(exc)[:120]}"))
                continue
        elif route is not None and route.route == ROUTE_NESTED_FACTOR:
            if mf_runner is None:
                mf_runner = _multifactor_payload_runner_cls()()
            try:
                data_i, panel_i = mf_runner.build_weight_panel(
                    symbols, start, end, _runner_cfg(sid, config, StrategyRunnerConfig)
                )
            except Exception as exc:  # noqa: BLE001 — 单成员失败跳过并披露
                skipped.append((sid, f"nested-factor panel build failed: {str(exc)[:120]}"))
                continue
        elif sid.startswith("STR-"):
            from zephyr.pf_core.strategy_engine.translated_strategy_adapter import (
                build_translated_weight_panel,
            )

            try:
                data_i, panel_i = build_translated_weight_panel(sid, symbols, start, end)
            except Exception as exc:  # noqa: BLE001 — 单成员失败跳过并披露（不拖垮整装回测）
                skipped.append((sid, f"translated panel build failed: {str(exc)[:120]}"))
                continue
        else:
            try:
                data_i, panel_i = runner.build_weight_panel(
                    symbols, start, end, _runner_cfg(sid, config, StrategyRunnerConfig)
                )
            except Exception as exc:  # noqa: BLE001 — 单成员失败跳过并披露（不拖垮整装回测）
                skipped.append((sid, f"panel build failed: {str(exc)[:120]}"))
                continue
        if panel_i is None or panel_i.empty:
            skipped.append(
                (
                    sid,
                    REASON_MEMBER_PANEL_DATA_EMPTY
                    + (
                        ""
                        if route is None
                        else f"（契约缺源 {route.route}——见 metrics.member_signal_contracts）"
                    ),
                )
            )
            continue
        if data_i is None or data_i.empty:
            skipped.append((sid, "行情历史为空（CH 无数据或窗口不覆盖）"))
            continue
        if data is None:
            data = data_i
        panels[sid] = panel_i
    # fail-closed 但原样透出：一员面板都没建成 → panels={}（调用方据此判空），
    # 已付出的取数代价（事件路行情）仍以**原对象**透出，禁静默换成 None 或副本。
    return (data if data is not None else history_source), panels, skipped


def _member_route_id(strategy_id: str) -> str:
    """成员 → 信号供给路 ID（`_build_member_panels` 的派发口径单一真源）。"""
    route = MEMBER_PAYLOAD_ROUTES.get(strategy_id)
    if route is not None:
        return route.route
    return ROUTE_TRANSLATED if strategy_id.startswith("STR-") else ROUTE_FLAT


def _runner_cfg(strategy_id: str, config: FrameworkBacktestConfig, cfg_cls: Any) -> Any:
    """StrategyRunnerConfig 组装（整装 v1=全成员同参，单一构造点）。"""
    return cfg_cls(
        strategy_id=strategy_id,
        factor_ids=tuple(config.factor_ids),
        rebalance_freq=config.rebalance_freq,
        top_n=config.top_n,
        max_single=config.max_single,
        pit_shift=config.pit_shift,
    )


def _member_contract(
    strategy_id: str,
    config: FrameworkBacktestConfig,
    *,
    panel_built: bool,
) -> dict[str, Any]:
    """成员信号契约披露条目（T1A-1 强制留痕——含降级事实，禁"看起来正常"）。"""
    route = MEMBER_PAYLOAD_ROUTES.get(strategy_id)
    if route is None:
        return {
            "strategy_id": strategy_id,
            "route": _member_route_id(strategy_id),
            "payload_contract": "{symbol: float}（扁平合成信号）",
            "disclosure": "注册表策略×通用因子扁平契约，无需富负载",
            "panel_built": panel_built,
        }
    disclosure = route.disclosure.replace(
        "<FACTOR_IDS>", str(tuple(config.factor_ids))
    ).replace("<TOP_N>", str(config.top_n))
    return {
        "strategy_id": strategy_id,
        "route": route.route,
        "payload_contract": route.contract,
        "disclosure": disclosure,
        "panel_built": panel_built,
    }


def _member_signal_contracts(
    plan: FrameworkPlan,
    config: FrameworkBacktestConfig,
    panels: dict[str, pd.DataFrame],
) -> dict[str, dict[str, Any]]:
    """方案全体成员的信号契约披露（纯函数，不触数据）。

    为什么必要（T1A-1）: 光看产物净值无法回答"这员的权重是它自己的信号出的，
    还是别人缺席摊派来的"——契约/降级必须随产物同源留痕，前端与审计都能查。
    """
    return {
        w.strategy_id: _member_contract(
            w.strategy_id, config, panel_built=w.strategy_id in panels
        )
        for w in plan.weights
    }


def _cash_ledger_reconciliation(engine: Any) -> dict[str, Any]:
    """现金账本 Σ 闭合对账（H4-A/H4-B，#24）——整装回测自带的账本绊线。

    引擎 NAV 曲线由同一份 `_cash` 算出，"手续费/过户费双计或漏扣"这类账本破口在净值
    曲线上自洽地看不见——故用成交流水（trades_log.total_cost，佣金/过户费已含、滑点在
    价内）独立重算现金腿，与逐日 cash_history 快照相减。真源算法在 portfolio
    （账本属主），本处只接线，容差单一真源 CASH_LEDGER_TOLERANCE。

    fail-closed：无 portfolio / 无 cash_history 属性（引擎被换成不经账本的实现）→
    samples=0 且 within_tolerance=False，由 fw_backtest 验收闸否决，禁"没数据=通过"。
    """
    from zephyr.backtest.core.portfolio import reconcile_cash_ledger

    portfolio = getattr(engine, "last_portfolio", None)
    cash_history = getattr(portfolio, "cash_history", None)
    if cash_history is None:
        return {
            "schema": "cash_ledger_reconciliation/v1",
            "samples": 0,
            "over_tolerance": 1,
            "within_tolerance": False,
            "note": "引擎未提供 last_portfolio.cash_history——现金腿不可核对（fail-closed 否决）",
        }
    return reconcile_cash_ledger(
        cash_history,
        getattr(portfolio, "trades_log", []) or [],
        portfolio.initial_capital,
    )


def _signal_age_disclosed(panel: pd.DataFrame | None, rebalance_freq: str = "") -> dict[str, Any]:
    """混频绊线（H3-B，#24）：合成面板的"有效信号龄"逐日分布。

    方案面板按 rebalance_freq（默认 W-FRI）调仓，但引擎**逐日**把持仓拉回目标权重——
    同一目标被连续交易多日，回测的执行假设是"周内每日都能按同一目标再平衡"。本函数
    不猜频率，直接从面板行变化反推真实龄（=距上次目标变化的行数），让混频在证据包里
    可见：age_max 大 = 目标长期不变仍每日撮合（漂移换手主因），rebalance_days 与
    面板天数之比即实际调仓节奏。引擎另有 execution_lag_days=1 滞后，龄在真实执行上
    再 +1（口径写进 note，禁消费方自行加减）。
    """
    out: dict[str, Any] = {
        "schema": "signal_age_disclosed/v1",
        "available": False,
        "rebalance_freq": rebalance_freq,
        "days": 0,
        "rebalance_days": 0,
        "signal_age_days_mean": None,
        "signal_age_days_max": None,
        "note": "合成面板不可用——混频节奏未测量",
    }
    if panel is None or len(panel) == 0 or len(panel.columns) == 0:
        return out
    values = panel.fillna(0.0)
    changed = values.ne(values.shift()).any(axis=1)
    positions = pd.Series(range(len(values)), index=values.index, dtype="float64")
    last_change = positions.where(changed).ffill()
    ages = positions - last_change.fillna(0.0)
    out.update(
        {
            "available": True,
            "days": int(len(values)),
            "rebalance_days": int(changed.sum()),
            "signal_age_days_mean": round(float(ages.mean()), 4),
            "signal_age_days_max": int(ages.max()),
            "note": (
                f"龄=距上次目标变化的交易日数（面板真值反推，非按 {rebalance_freq or '配置频率'} 假定）；"
                "引擎逐日按目标再平衡，故龄内每日都在撮合；执行另有 lag 1 日（引擎侧再加）"
            ),
        }
    )
    return out


def _engine_chain_diagnostics(engine: Any) -> dict[str, Any]:
    """引擎侧执行链诊断透传（H3-C/H4-C/H4-D/H4-E，#24）——缺失即出声，禁补默认值。

    引擎新增的三个只读口（目标权重行 Σ 统计 / 拒单统计 / 未建模清单）在此原样进产物。
    属性不存在（引擎被替换成不经该口径的实现）→ 落 `{"available": False}` 占位，
    让证据包显式说"未测量"，而不是静默缺键（消费方按缺键 fail-closed）。
    """
    from zephyr.backtest.implementations.vectorized_engine import EXECUTION_MODEL_CAPABILITY

    out: dict[str, Any] = {"execution_model_disclosure": dict(EXECUTION_MODEL_CAPABILITY)}
    for key, attr in (
        ("target_weight_renormalization", "last_signal_row_stats"),
        ("skipped_fills", "last_skipped_fills"),
    ):
        value = getattr(engine, attr, None)
        out[key] = (
            dict(value)
            if isinstance(value, dict)
            else {"schema": f"{key}/v1", "available": False, "note": f"引擎未提供 {attr}"}
        )
    return out


def _persist_framework_artifact(
    result: Any,
    engine: Any,
    plan: FrameworkPlan,
    report: ComposeReport,
    config: FrameworkBacktestConfig,
    panel_recon: dict[str, Any] | None = None,
    contracts: dict[str, dict[str, Any]] | None = None,
    shrinkage_disclosure: dict[str, Any] | None = None,
) -> tuple[str, dict[str, Any], dict[str, Any]]:
    """引擎结果 → sink → artifact（bt-fw-* 命名 + plan_id 披露字段）→ 落盘。

    shrinkage_disclosure 非 None（RSC-2 裁定#270 节流启用）时落
    metrics.shrinkage_disclosure；None 不加键（默认满仓路径产物零漂移）。
    """
    from zephyr.backtest.io.backtest_result_sink import sink_backtest_result
    from zephyr.backtest.io.result_repository import build_artifact_from_data, save_artifact

    ts = _collect_timeseries(engine)
    # H3/H4 执行链绊线（#24）：现金账本闭合 + 引擎侧静默点 + 混频节奏——同源算一次，
    # 产物 metrics 与 result_out 共用（两个计算点必然漂移）
    chain = {
        "cash_ledger_reconciliation": _cash_ledger_reconciliation(engine),
        **_engine_chain_diagnostics(engine),
        "signal_age_disclosed": _signal_age_disclosed(
            getattr(report, "panel", None), getattr(config, "rebalance_freq", "")
        ),
    }
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
            # T1A-2 验收字段：死成员/摊派全量披露（禁只靠 compose_notes 数字暗示）
            "dead_weight_disclosed": report.dead_weight_disclosed,
            # T1A-1 验收字段：成员信号契约与降级/缺源披露（含 runner 只喂单因子）
            "member_signal_contracts": dict(contracts or {}),
            # #24 H3/H4 验收字段：现金腿时序 + 现金账本闭合 + 引擎静默点 + 混频节奏
            # （禁只进日志/只进内存 ts——H4-B：产物不落现金序列则"手续费扣到现金没"
            #  从不可事后复核）。落 metrics 而非 artifact 顶层：BacktestRunArtifact 顶层
            #  字段 [MODIFY-GUARD] 结构冻结，metrics 本就是执行链证据载体。
            #  按登记表推导而非逐行手写：使"登记了什么"与"实际落盘了什么"无法漂移。
            **{k: list(ts.get(k) or []) for k in sorted(_PERSISTED_VIA_METRICS_TS_KEYS)},
            **chain,
        }
    )
    if report.regime_day_counts:  # 三期动态模式披露（静态模式不加键，二期产物零漂移）
        metrics.update(
            {
                "dynamic": True,
                "regime_day_counts": report.regime_day_counts,
                "regime_rescale_factors": report.regime_rescale_factors,
                "activation_policy": config.activation_policy,
                "activation_source": plan.activation_source,
                "plan_regime_overrides": {
                    state: {w.strategy_id: w.weight for w in weights}
                    for state, weights in plan.regime_overrides
                },
            }
        )
    if panel_recon is not None:  # 面板级对账（#275 定案口径①）——静/动两模式均落产物
        metrics["panel_reconciliation"] = panel_recon
    if shrinkage_disclosure is not None:  # RSC-2（裁定#270）：节流启用才落键（零漂移）
        metrics["shrinkage_disclosure"] = shrinkage_disclosure
    run_id = f"{_ARTIFACT_RUN_PREFIX}-{uuid.uuid4().hex[:8]}"
    artifact = replace(artifact, run_id=run_id, metrics=metrics)
    saved_run_id = save_artifact(
        artifact, storage_path=Path(config.storage_path) if config.storage_path else None
    )
    return saved_run_id, ts, metrics


def _assemble_run_warn(
    ts: dict[str, Any],
    report: ComposeReport,
    panel_recon: dict[str, Any] | None,
    chain: dict[str, Any] | None = None,
) -> str | None:
    """run_framework_backtest 的 warn 组装（空净值/跳过成员/摊派绊线/面板对账超容差/现金账本破）。

    摊派绊线（T1A-2）: 死成员 α 占方案份额 >``DEAD_MEMBER_ALPHA_SHARE_LIMIT`` 或行级归一
    显著偏差（>``_ROW_NORM_MATERIALITY``）→ warn——
    整装回测的"组合"若大半来自摊派，回测结论不可用，必须在 done 响应里可见。
    现金账本（H4-A，#24）: ``chain.cash_ledger_reconciliation.within_tolerance`` 为假 →
    warn（**含缺键**——引擎/账本没接线也是破口，禁静默通过；acceptance 侧另有硬闸）。
    """
    parts: list[str] = []
    if not ts.get("equity_curve"):
        parts.append("equity_curve empty")
    cash_recon = (chain or {}).get("cash_ledger_reconciliation")
    if chain is not None and not cash_recon:
        parts.append("cash ledger reconciliation MISSING——现金腿未核对（H4-A）")
    elif cash_recon is not None and not cash_recon.get("within_tolerance"):
        parts.append(
            f"cash ledger OPEN (max abs residual {cash_recon.get('max_abs_residual')}"
            f">容差 {cash_recon.get('tolerance_abs')}, worst {cash_recon.get('worst_date')})"
            "——成交流水与现金余额不闭合"
        )
    if report.skipped:
        parts.append("skipped: " + "; ".join(f"{s}({r})" for s, r in report.skipped))
    disclosure = report.dead_weight_disclosed or {}
    dead_share = float(disclosure.get("skipped_alpha_share_of_plan") or 0.0)
    dead_only = float(disclosure.get("dead_member_alpha_base") or 0.0) / float(
        disclosure.get("plan_weight_total") or 1.0
    )
    if dead_only > DEAD_MEMBER_ALPHA_SHARE_LIMIT:
        parts.append(
            f"dead-member alpha {dead_only * 100:.1f}% of plan"
            f"(>限 {DEAD_MEMBER_ALPHA_SHARE_LIMIT * 100:.0f}%，含跳过员 {dead_share * 100:.1f}%)"
            "——组合已非方案原意，见 metrics.dead_weight_disclosed"
        )
    row_norm = disclosure.get("row_normalization") or {}
    if row_norm.get("material"):
        parts.append(
            f"row normalization MATERIAL (max dev {row_norm.get('max_deviation')})"
            "——缺口由幸存成员摊派，非数值噪声"
        )
    if panel_recon is not None and not panel_recon["within_tolerance"]:
        parts.append(f"panel reconciliation OVER tolerance: max_abs_diff={panel_recon['max_abs_diff']}")
    return "; ".join(parts) if parts else None


def _normalize_shrinkage_schedule(raw: Any) -> dict[Any, float] | None:
    """RSC-2 节流日序归一化（裁定#270）：None/空 → None（关，满仓）；映射 → 钳制后 schedule。

    fail-closed 纪律（regime 错=权重错同族）：非映射类型 / 日期不可解析 / 因子非数值 /
    NaN 一律 FrameworkValidationError 拒绝——provider 的 clamp 虽把 NaN 当 1.0 满部署
    （保守退化），但入参侧 NaN 更可能是上游 bug，禁静默放行。

    Returns:
        {datetime(归一): factor∈[0,1]}；None=未启用（调用方走 DefaultBacktestEngine 原路）。
    """
    if raw is None:
        return None
    if not hasattr(raw, "items"):
        raise FrameworkValidationError(
            f"shrinkage_by_date 须为 {{date: factor}} 映射或 None/空（关），got {type(raw).__name__}"
        )
    if not raw:
        return None
    from zephyr.backtest.regime_validation.shrinkage_provider import clamp_shrinkage

    out: dict[Any, float] = {}
    for k, v in raw.items():
        try:
            ts = pd.Timestamp(k)
        except (ValueError, TypeError) as exc:
            raise FrameworkValidationError(f"shrinkage 日序日期无法解析: {k!r}") from exc
        if pd.isna(ts):
            raise FrameworkValidationError(f"shrinkage 日序日期无法解析: {k!r}")
        try:
            factor = float(v)
        except (TypeError, ValueError) as exc:
            raise FrameworkValidationError(f"shrinkage 日序因子非数值: {k!r} → {v!r}") from exc
        if factor != factor:  # NaN
            raise FrameworkValidationError(f"shrinkage 日序因子为 NaN: {k!r}")
        out[ts.normalize().to_pydatetime()] = clamp_shrinkage(factor)
    return out


def _shrinkage_disclosure(
    schedule: dict[Any, float] | None,
    applied_log: Sequence[tuple[Any, float]],
) -> dict[str, Any] | None:
    """RSC-2 披露组装（禁静默纪律）：schedule 统计 + 引擎逐日生效 log。

    schedule=None（未启用）返回 None——调用方不落 metrics 键（默认路径产物零漂移）。
    applied_log 取自 ShrinkageBacktestEngine.shrinkage_log（仅"有信号日"有记录，与
    引擎早返回语义一致——无信号日本就无仓位可节流）。
    """
    if schedule is None:
        return None
    log = [(str(dt)[:10], round(float(v), 6)) for dt, v in (applied_log or [])]
    values = [v for _d, v in log]
    throttled = [v for v in values if v < 1.0]
    return {
        "schema": 1,
        "caliber": "rsc2-engine-boundary-throttle",
        "ruling": "裁定#270",
        "provider": "schedule-pit-asof",
        "schedule_days": len(schedule),
        "applied_days": len(log),
        "throttled_days": len(throttled),
        "factor_min": round(min(values), 6) if values else None,
        "factor_mean": round(sum(values) / len(values), 6) if values else None,
        "factor_max": round(max(values), 6) if values else None,
        "cash_semantics": "剩余质量落现金（T1A-5 合并裁定，禁再归一化回填）",
        "log": log,
    }


def shrinkage_diff_stamp(
    equity_off: Sequence[dict[str, Any]],
    equity_on: Sequence[dict[str, Any]],
    shrinkage_log: Sequence[tuple[Any, float]] = (),
) -> dict[str, Any]:
    """RSC-2 双跑差值章（裁定#270 验收件，纯函数）：开/关两净值曲线的逐日差+汇总统计。

    方向语义：diff/total_return_diff = on − off（节流在盈利段降低收益→负；在亏损段
    减损→正）；max_drawdown_diff = on − off（负=节流后回撤更浅）。**只披露不否决**——
    C1 一票否决判定权在 C1ShrinkageComparator（裁定#270 边界，禁越域）。

    Args:
        equity_off: 关（满仓）跑的 equity_curve（[{"timestamp","equity"},...]，升序）。
        equity_on: 开（节流）跑的 equity_curve（同构）。
        shrinkage_log: 开跑实际生效的 (date, factor) 序列（引擎 shrinkage_log 或披露 log）。

    Returns:
        披露 dict（schema/caliber/days_compared/throttled_days/factor 统计/终值/总收益差/
        最大回撤差/nav_diff_by_day 逐日明细）。
    """

    def _by_date(curve: Sequence[dict[str, Any]]) -> dict[str, float]:
        return {str(p.get("timestamp", ""))[:10]: float(p.get("equity", 0.0)) for p in curve}

    off_map = _by_date(equity_off)
    on_map = _by_date(equity_on)
    common = [d for d in sorted(set(off_map) & set(on_map)) if d]
    rows = []
    for d in common:
        o, n = off_map[d], on_map[d]
        rows.append(
            {
                "date": d,
                "equity_off": round(o, 2),
                "equity_on": round(n, 2),
                "diff_pct": round((n - o) / o * 100.0, 4) if o else None,
            }
        )

    def _total_return(mapping: dict[str, float]) -> float | None:
        vals = [mapping[d] for d in common if mapping[d] > 0]
        if len(vals) < 2:
            return None
        return (vals[-1] / vals[0] - 1.0) * 100.0

    def _max_drawdown(mapping: dict[str, float]) -> float:
        peak: float | None = None
        mdd = 0.0
        for d in common:
            v = mapping[d]
            if v <= 0:
                continue
            peak = v if peak is None else max(peak, v)
            if peak > 0:
                mdd = max(mdd, 1.0 - v / peak)
        return mdd * 100.0

    total_off, total_on = _total_return(off_map), _total_return(on_map)
    mdd_off, mdd_on = _max_drawdown(off_map), _max_drawdown(on_map)
    throttle_values = [float(v) for _d, v in (shrinkage_log or [])]
    throttled = [v for v in throttle_values if v < 1.0]
    return {
        "schema": 1,
        "caliber": "rsc2-shrinkage-dual-run-diff",
        "ruling": "裁定#270",
        "days_compared": len(rows),
        "throttled_days": len(throttled),
        "throttle_factor_min": round(min(throttle_values), 6) if throttle_values else None,
        "throttle_factor_mean": (
            round(sum(throttle_values) / len(throttle_values), 6) if throttle_values else None
        ),
        "final_equity_off": rows[-1]["equity_off"] if rows else None,
        "final_equity_on": rows[-1]["equity_on"] if rows else None,
        "total_return_off_pct": round(total_off, 4) if total_off is not None else None,
        "total_return_on_pct": round(total_on, 4) if total_on is not None else None,
        # 差值方向单一口径 = on − off（回撤为正则更深、收益为正则更好）：
        # total_return_diff<0=节流放弃了收益；max_drawdown_diff<0=节流把回撤做浅了。
        "total_return_diff_pct": (
            round(total_on - total_off, 4) if (total_on is not None and total_off is not None) else None
        ),
        "max_drawdown_off_pct": round(mdd_off, 4),
        "max_drawdown_on_pct": round(mdd_on, 4),
        "max_drawdown_diff_pct": round(mdd_on - mdd_off, 4),
        "cash_semantics": "on<1 日差额=现金（T1A-5 合并裁定）；diff=on−off，负=节流降低净值",
        "note": "差值章只披露不否决——C1 一票否决权在 C1ShrinkageComparator（裁定#270 边界）",
        "nav_diff_by_day": rows,
    }


def _run_framework_backtest_core(
    plan_id: str,
    symbols: list[str],
    start: str,
    end: str,
    config: FrameworkBacktestConfig | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """整装回测内核（双产物 (result, ts)）——单跑入口与 RSC-2 双跑编排共用（禁克隆编排）。

    Shrinkage 路由（裁定#270）：cfg.shrinkage_by_date 归一化后非空 → 引擎改用
    ShrinkageBacktestEngine+ScheduleShrinkageProvider（引擎边界节流，compose 面板
    保持 Σ=1）；否则 DefaultBacktestEngine 原路（逐位一致）。启用时 result 顶层增
    ``shrinkage`` 键（同源披露），artifact metrics 落 ``shrinkage_disclosure``。
    归一化在函数**第一行**完成——非法 schedule 不进取数/合成/引擎（fail-closed 于算力
    之前，且禁"面板全建失败早返回"把非法 schedule 顺带放过）。

    Raises:
        FrameworkValidationError: cfg.shrinkage_by_date 非法（非映射/日期不可解析/
            因子非数值/NaN）——先于任何取数与引擎工作抛出。

    Args:
        plan_id: 整装方案 ID（fw-defensive / fw-balanced / fw-aggressive）。
        symbols: 标的清单（与单策略回测同口径，纯数字代码可带 .SH/.SZ 后缀）。
        start/end: 回测窗口（YYYY-MM-DD）。
        config: 参数对象（None=FrameworkBacktestConfig() 默认值；cfg.regime_by_date 非空
            时为动态模式——逐日查 regime_overrides，详见 compose_weight_panels；
            cfg.shrinkage_by_date 非空时为 RSC-2 节流口径，详见裁定#270）。

    Returns:
        (result, ts) 二元组。result={"ok", "run_id", "plan_id", "participants", "skipped",
         "rescale_factor", "dynamic", "regime_day_counts", "per_regime",
         "panel_reconciliation", "dead_weight_disclosed", "member_signal_contracts",
         "shrinkage", "equity_points", "trades", "metrics", "warn"}（ok=False 时含 error；
         动态模式 dynamic/regime_day_counts/per_regime 三键有值，静态模式=False/{}/[]——
         二期消费方零漂移；panel_reconciliation=面板级对账（#275 定案口径①），超容差落
         warn；dead_weight_disclosed=死成员/摊派全量披露（T1A-2 验收字段），
         member_signal_contracts=各员信号契约与降级披露（T1A-1）；shrinkage=RSC-2 节流
         披露（None=未启用，键恒存在供消费方统一 .get()））。ts=_collect_timeseries 产物
         （equity_curve/trade_log/drawdown_curve——双跑编排取净值曲线用）。
    """
    cfg = config or FrameworkBacktestConfig()
    # Shrinkage schedule 归一化**前置**（RSC-2 裁定#270 fail-closed）：非法日序必须在任何
    # 取数/合成/对账/引擎开销之前拒绝。留在引擎路由处有两重病灶——① bad-schedule 跑先把
    # CH 取数+compose+面板对账全付掉才报错（拒算不省钱）；② 成员面板全建失败时函数在
    # 路由之前 ok=False 早返回，非法 schedule **永不被校验**（静默放行=更坏）。
    # 归一化产物单一真值：既作引擎路由判据，也作披露入参（禁二次归一）。
    shrinkage_schedule = _normalize_shrinkage_schedule(cfg.shrinkage_by_date)
    plan = get_framework_plan(plan_id, cfg.plans_path)

    members, pre_skipped = _select_vectorizable_members(plan)
    data, panels, build_skipped = _build_member_panels(
        # replace 保留 regime_overrides/activation_source——手搓新实例会把 activation
        # 与覆盖表丢掉（T1A-3：面板构建侧也要看得到 activation 才能判"全表 α=0"）
        replace(plan, weights=tuple(members)),
        symbols,
        start,
        end,
        cfg,
    )
    skipped = pre_skipped + build_skipped
    contracts = _member_signal_contracts(plan, cfg, panels)

    # 判空口径=「行情源缺失」或「一员面板都没建成」——后者是 fail-closed 的正式信号
    # （`_build_member_panels` 会把已取到的行情原样透出，data 非 None 不代表可回测）；
    # 少了 `not panels` 这一半，无参与成员的运行会从 graceful ok=False 变成
    # compose_weight_panels 抛未捕获 FrameworkValidationError（消费方契约漂移）。
    if data is None or not panels:
        return {
            "ok": False,
            "error": "all member panels empty（CH 无数据或因子为空）",
            "plan_id": plan.plan_id,
            "skipped": [list(s) for s in skipped],
            "member_signal_contracts": contracts,
        }

    # 引擎 index 契约: date level（run_one 同款归一化）
    if isinstance(data.index, pd.MultiIndex):
        names = data.index.names or []
        if "trade_date" in names:
            data.index = data.index.rename({"trade_date": "date"})
        elif "trade_time" in names:
            data.index = data.index.rename({"trade_time": "date"})

    report = compose_weight_panels(
        plan,
        panels,
        allow_partial=cfg.allow_partial,
        regime_by_date=cfg.regime_by_date,
        prior_skipped=skipped,  # 上游 reason（tick-only/构建失败）沿用，不降级成 "panel missing"
        activation_policy=cfg.activation_policy,
    )

    # 面板级对账（tracker #275 定案口径①）：独立复算逐位硬验收，每次运行自带回归绊线
    panel_recon = verify_weight_panel_identity(
        plan,
        panels,
        report.panel,
        regime_by_date=cfg.regime_by_date,
        prior_skipped=skipped,
        activation_policy=cfg.activation_policy,
    )

    # 引擎路由（RSC-2 裁定#270）：启用=引擎边界节流（compose 面板保持 Σ=1 纪律）；
    # 未启用=DefaultBacktestEngine 原路（逐位一致零漂移）。`shrinkage_schedule` 已在
    # 入口归一化并 fail-closed——此处禁二次归一（两个归一点必然漂移）。
    engine_config = BacktestConfig(initial_capital=Decimal(str(cfg.initial_capital)))
    if shrinkage_schedule is None:
        engine: Any = DefaultBacktestEngine(
            config=engine_config,
            enable_stk_limit_provider=cfg.enable_stk_limit_provider,
        )
    else:
        from zephyr.backtest.implementations.shrinkage_engine import ShrinkageBacktestEngine
        from zephyr.backtest.regime_validation.shrinkage_provider import ScheduleShrinkageProvider

        engine = ShrinkageBacktestEngine(
            config=engine_config,
            shrinkage_provider=ScheduleShrinkageProvider(shrinkage_schedule),
            enable_stk_limit_provider=cfg.enable_stk_limit_provider,
        )
    result = engine.run(data=data, signals=report.panel, strategy_name=plan.plan_id)

    disclosure = _shrinkage_disclosure(
        shrinkage_schedule, getattr(engine, "shrinkage_log", ()) or ()
    )
    saved_run_id, ts, artifact_metrics = _persist_framework_artifact(
        result, engine, plan, report, cfg, panel_recon=panel_recon, contracts=contracts,
        shrinkage_disclosure=disclosure,
    )

    # 三期动态模式：per-regime 分段摘要（收益/回撤贡献，done 响应消费）
    dynamic = bool(report.regime_day_counts)
    per_regime: list[dict[str, Any]] = []
    if dynamic and cfg.regime_by_date is not None:
        per_regime = per_regime_summary(plan, ts.get("equity_curve") or [], cfg.regime_by_date)

    n_eq = len(ts.get("equity_curve") or [])
    # chain=产物 metrics：现金账本闭合等执行链绊线在 warn 里也要可见（H4-A）
    warn = _assemble_run_warn(ts, report, panel_recon, chain=artifact_metrics)

    result_out: dict[str, Any] = {
        "ok": True,
        "run_id": saved_run_id,
        "plan_id": plan.plan_id,
        "participants": report.participants,
        "skipped": [list(s) for s in report.skipped],
        "rescale_factor": report.rescale_factor,
        "dynamic": dynamic,
        "regime_day_counts": report.regime_day_counts,
        "per_regime": per_regime,
        "panel_reconciliation": panel_recon,
        "dead_weight_disclosed": report.dead_weight_disclosed,
        "member_signal_contracts": contracts,
        "shrinkage": disclosure,
        "equity_points": n_eq,
        "trades": len(ts.get("trade_log") or []),
        "metrics": artifact_metrics,
        "warn": warn,
    }
    return result_out, ts


def run_framework_backtest(
    plan_id: str,
    symbols: list[str],
    start: str,
    end: str,
    config: FrameworkBacktestConfig | None = None,
) -> dict[str, Any]:
    """整装回测全链路: 方案权重 × 子策略面板 → 合成 → 引擎 → 产物 bt-fw-*.json。

    签名/返回契约与既有消费方（api_server/fw_backtest_due）兼容——本体在
    `_run_framework_backtest_core`（返回 (result, ts)），本入口仅取 result（既有
    返回形状零漂移）。cfg.shrinkage_by_date 非空=RSC-2 节流口径（裁定#270），
    result["shrinkage"] 为披露 dict；None=满仓原路。

    Args:
        plan_id: 整装方案 ID（fw-defensive / fw-balanced / fw-aggressive）。
        symbols: 标的清单（与单策略回测同口径，纯数字代码可带 .SH/.SZ 后缀）。
        start/end: 回测窗口（YYYY-MM-DD）。
        config: 参数对象（None=FrameworkBacktestConfig() 默认值）。

    Returns:
        result dict（同 `_run_framework_backtest_core` 文档；ok=False 时含 error）。
    """
    result, _ts = _run_framework_backtest_core(plan_id, symbols, start, end, config)
    return result


def run_framework_backtest_shrinkage_dual(
    plan_id: str,
    symbols: list[str],
    start: str,
    end: str,
    config: FrameworkBacktestConfig | None = None,
    *,
    shrinkage_by_date: Any,
) -> dict[str, Any]:
    """RSC-2 双跑对照编排（裁定#270 验收件）：关/开各跑一次整装回测，产出两条净值曲线+差值章。

    同参唯 shrinkage 异：关跑强制 shrinkage_by_date=None（满仓基线），开跑注入给定
    schedule（引擎边界节流）。对应 C1 一票否决验证语义的整装版——但**只出披露章
    不出否决判定**（C1 裁定权在 C1ShrinkageComparator，禁越域）。

    Args:
        plan_id/symbols/start/end/config: 与 run_framework_backtest 同参。
        shrinkage_by_date: 节流日序 {date-like: factor}（开跑侧；归一化 fail-closed 同
            `_normalize_shrinkage_schedule`）。必填关键字参数——双跑无 schedule 即无意义。

    Returns:
        {"ok", "plan_id", "run_ids": {"off","on"}, "off"/"on": 两跑摘要透传,
         "equity_curves": {"off","on"}, "diff": shrinkage_diff_stamp 产物, "note"}。
        任一侧失败 → ok=False + error + phase + 已完成侧完整结果（不静默）。
    """
    base = config or FrameworkBacktestConfig()
    # 前置 fail-closed 校验：非法 schedule 在 off 腿开跑前即拒（否则 off 跑完并落产物后
    # 才在 on 腿抛错——白付一次整装回测算力 + 留下半套证据）。归一化真值仍由 core 产出
    # （单一归一点），此处只作入参守门，cfg_on 原样透传。
    _normalize_shrinkage_schedule(shrinkage_by_date)
    cfg_off = replace(base, shrinkage_by_date=None)
    cfg_on = replace(base, shrinkage_by_date=shrinkage_by_date)

    off, ts_off = _run_framework_backtest_core(plan_id, symbols, start, end, cfg_off)
    if not off.get("ok"):
        return {
            "ok": False,
            "error": f"shrinkage dual off 跑失败: {off.get('error')}",
            "phase": "off",
            "off": off,
        }
    on, ts_on = _run_framework_backtest_core(plan_id, symbols, start, end, cfg_on)
    if not on.get("ok"):
        return {
            "ok": False,
            "error": f"shrinkage dual on 跑失败: {on.get('error')}",
            "phase": "on",
            "off": off,
            "on": on,
        }

    shrink_log = ((on.get("shrinkage") or {}).get("log")) or []
    diff = shrinkage_diff_stamp(
        ts_off.get("equity_curve") or [], ts_on.get("equity_curve") or [], shrink_log
    )
    summary_keys = (
        "ok", "participants", "skipped", "rescale_factor", "dynamic",
        "regime_day_counts", "equity_points", "warn",
    )
    return {
        "ok": True,
        "plan_id": off.get("plan_id"),
        "run_ids": {"off": off.get("run_id"), "on": on.get("run_id")},
        "off": {k: off.get(k) for k in summary_keys},
        "on": {k: on.get(k) for k in summary_keys} | {"shrinkage": on.get("shrinkage")},
        "equity_curves": {
            "off": ts_off.get("equity_curve") or [],
            "on": ts_on.get("equity_curve") or [],
        },
        "diff": diff,
        "note": (
            "双跑=同参唯 shrinkage 异（裁定#270）；面板构建×2 如实披露——共享 compose "
            "面板的单跑双引擎编排留待 due 链挂接（RSC-3 供给投产后按 §5 门位裁定）"
        ),
    }


__all__: Final = (
    "ACTIVATION_POLICY_LENIENT",
    "ACTIVATION_POLICY_STRICT",
    "ComposeReport",
    "FrameworkBacktestConfig",
    "FrameworkPlan",
    "FrameworkPlanError",
    "FrameworkValidationError",
    "MEMBER_PAYLOAD_ROUTES",
    "MemberPayloadRoute",
    "PlanWeight",
    "REASON_ALL_ZERO_ROWS",
    "REASON_MEMBER_PANEL_DATA_EMPTY",
    "REASON_PANEL_MISSING",
    "REASON_TICK_ONLY",
    "REASON_ZERO_WEIGHT",
    "REGIME_STATE_TO_ACTIVATION_PHASE",
    "ROUTE_EVENT_PANEL",
    "ROUTE_FLAT",
    "ROUTE_NESTED_FACTOR",
    "ROUTE_NO_DAILY_SOURCE",
    "ROUTE_TRANSLATED",
    "compose_weight_panels",
    "get_framework_plan",
    "load_framework_plans",
    "per_regime_summary",
    "reconcile_composed_nav",
    "run_framework_backtest",
    "run_framework_backtest_shrinkage_dual",
    "shrinkage_diff_stamp",
    "verify_weight_panel_identity",
)
