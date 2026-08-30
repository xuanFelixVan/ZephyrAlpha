# [BLUEPRINT] MOD-SIG-127 | docs/03_modules/_domain_signal/causal_ml_engine/blueprint.md
# [MODULE] zephyr.signal_ashare.causal_ml_engine
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] 无（编排核纯内存；dml_runner/causal_forest_runner/dowhy_runner/discovery_runner/clock 全注入）
# [CONSUMERS] 运行时装配批（盘前因果图预计算 / 因子因果效应显著性筛选接信号装配）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 四通道 runner 全注入（库未装/未注入/异常一律降级标记不阻断）; 盘前预计算因果图单槽缓存按数据指纹失效（指纹变更即重算）; 显著性筛选严格 |效应|>阈值 且 p<阈值(默认0.05); 单通道降级不影响他通道; 输出按通道定义序/|效应|降序确定性排序; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_signal/causal_ml_engine/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] CausalMlError(占位 ZA-SIG-UNREGISTERED-CAUSAL-ML)——空treatment/空outcome/未知通道/非法显著性阈值/空数据指纹/空变量集或含空白变量时抛
# [TESTS] tests/signal_ashare/test_causal_ml_engine.py
# [A_module] module_id=MOD-SIG-127 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""
CausalMlEngine — 因果ML引擎（MOD-SIG-127）。

B10-01858（AUD-DRAFT-001-DIGEST P2 波 P2-W06，CAND-TESTB-051，A1 §29.18；
canonical 承接 TESTB-035/047 归并）：**DML 因子因果效应估计**（注入
dml_runner，econml 未装由注入方降级）+ **CausalForest 异质效应**（注入
causal_forest_runner，CATE 均值口径）+ **DoWhy 因果图证伪**（注入
dowhy_runner，证伪结论入 note，降级标记不阻断）+ **PC/LiNGAM 因果发现**
（注入 discovery_runner）+ **盘前预计算因果图缓存**（单槽缓存，按数据
指纹失效）+ **效应显著性筛选**（|效应|>阈值 且 p<0.05）。

查重分工（蓝图 §0）：causal_inference_engine（MOD-SIG-042）= lead-lag 双
IC/偏 IC 轻量统计因果本体（本件=四通道外部 runner 纯编排层，不实现任何
统计算法本体，亦不 import econml/DoWhy 等因果库）；event_causal_reasoner
（MOD-SIG-112）= 事件传导边模板 BFS（本件=因子级效应估计与因果图发现，
零交集）；四通道库是否安装由注入方判定，本件对 runner 缺失/异常/产出非
法一律打降级标记，永不阻断其余通道。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: effect_threshold 参数
#   fields: 参数 effect_threshold（无注解）
#   code: causal_ml_engine.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: p_value_threshold 参数
#   fields: 参数 p_value_threshold（无注解）
#   code: causal_ml_engine.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: dml_runner 参数
#   fields: 参数 dml_runner（无注解）
#   code: causal_ml_engine.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: causal_forest_runner 参数
#   fields: 参数 causal_forest_runner（无注解）
#   code: causal_ml_engine.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① CausalMlEngine
#   name_en: CausalMlEngine
#   intro: 因果ML引擎（四通道注入编排 + 盘前图缓存 + 显著性筛选）。
#   desc: 因果ML引擎（四通道注入编排 + 盘前图缓存 + 显著性筛选）。 runner 契约（全部为注入回调；本件不 import 任何因果库，库未装由注入方 自行降级或缺席）： - d…；公共方法（定义序）: estimat…
#   inputs: effect_threshold p_value_threshold dml_runner causal_forest_runner do…
#   outputs: 返回值
#   （注：A1 之后另有 6 个公共定义未列入（含 6 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（7 定义）
#   name_en: public defs
#   intro: CausalMlEngine
#   downstream: 运行时装配批（盘前因果图预计算 / 因子因果效应显著性筛选接信号装配）
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
import math
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Final, Iterable, Mapping

_log = logging.getLogger(__name__)

__all__: Final = [
    "CausalChannel",
    "CausalEffect",
    "CausalGraphSnapshot",
    "CausalMlEngine",
    "CausalMlError",
    "CausalMlReport",
    "SignificantEffect",
]


class CausalMlError(Exception):
    """因果ML引擎输入/配置非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-SIG-UNREGISTERED-CAUSAL-ML。
    """


class CausalChannel(str, Enum):
    """四通道词表（闭合）。"""

    DML = "dml"  # DML 因子因果效应估计
    CAUSAL_FOREST = "causal_forest"  # CausalForest 异质效应
    DOWHY_REFUTE = "dowhy_refute"  # DoWhy 因果图证伪
    DISCOVERY = "discovery"  # PC/LiNGAM 因果发现


#: 效应估计通道（DISCOVERY 发现通道产出因果图而非效应，专属 precompute_causal_graph）
_EFFECT_CHANNELS: Final = (CausalChannel.DML, CausalChannel.CAUSAL_FOREST, CausalChannel.DOWHY_REFUTE)


@dataclass(frozen=True)
class CausalEffect:
    """单通道因果效应估计产出。"""

    channel: CausalChannel
    treatment: str
    outcome: str
    effect: float  # 点估计（降级时 0.0）
    p_value: float  # 显著性（降级时 1.0）
    n_samples: int
    downgraded: bool  # runner 未注入/异常/产出非法 → True（不阻断）
    note: str = ""


@dataclass(frozen=True)
class SignificantEffect:
    """通过显著性筛选的效应（|effect|>阈值 且 p<p阈值，严格不等号）。"""

    channel: CausalChannel
    treatment: str
    outcome: str
    effect: float
    p_value: float


@dataclass(frozen=True)
class CausalMlReport:
    """四通道汇总报告。"""

    treatment: str
    outcome: str
    effects: tuple[CausalEffect, ...]
    significant: tuple[SignificantEffect, ...]
    degraded_channels: tuple[CausalChannel, ...]
    ran_at: datetime.datetime


@dataclass(frozen=True)
class CausalGraphSnapshot:
    """盘前预计算因果图缓存快照（按数据指纹失效）。"""

    fingerprint: str
    edges: tuple[tuple[str, str], ...]  # (cause, effect) 去自环去重升序
    n_variables: int
    computed_at: datetime.datetime
    downgraded: bool
    note: str = ""


#: runner 产出映射的数值键契约
_EFFECT_RUNNERS_DOC: Final = (
    "键 effect(float)/p_value(float) 必填，n_samples(int)/note(str) 可选，dowhy 通道另可带 refuted(bool)"
)


class CausalMlEngine:
    """因果ML引擎（四通道注入编排 + 盘前图缓存 + 显著性筛选）。

    runner 契约（全部为注入回调；本件不 import 任何因果库，库未装由注入方
    自行降级或缺席）：
      - dml_runner(treatment, outcome, context) -> Mapping：DML 平均效应；
      - causal_forest_runner(treatment, outcome, context) -> Mapping：同上
        （effect=CATE 均值，异质效应汇总口径由注入方定）；
      - dowhy_runner(treatment, outcome, context) -> Mapping：同上，可选
        refuted(bool)——证伪未通过仅记 note（筛选阈值自然拦截，不剔除）；
      - discovery_runner(fingerprint, variables, context) -> Mapping：
        键 edges(Iterable[(cause, effect)])。
    效应三通道产出键契约见 _EFFECT_RUNNERS_DOC；任一 runner 未注入/抛异常/
    产出非法 → 该通道 downgraded=True，其余通道照常。
    """

    def __init__(
        self,
        *,
        effect_threshold: float = 0.05,
        p_value_threshold: float = 0.05,
        dml_runner: Callable[[str, str, Mapping[str, object]], Mapping[str, object]] | None = None,
        causal_forest_runner: Callable[[str, str, Mapping[str, object]], Mapping[str, object]] | None = None,
        dowhy_runner: Callable[[str, str, Mapping[str, object]], Mapping[str, object]] | None = None,
        discovery_runner: Callable[[str, tuple[str, ...], Mapping[str, object]], Mapping[str, object]] | None = None,
        clock: Callable[[], datetime.datetime] | None = None,
    ) -> None:
        if not math.isfinite(effect_threshold) or effect_threshold < 0.0:
            raise CausalMlError(f"effect_threshold 非法: {effect_threshold!r}（须为非负有限值）")
        if not math.isfinite(p_value_threshold) or not 0.0 < p_value_threshold < 1.0:
            raise CausalMlError(f"p_value_threshold 越界: {p_value_threshold!r}（须∈(0,1)）")
        self._effect_threshold = float(effect_threshold)
        self._p_value_threshold = float(p_value_threshold)
        self._runners: dict[CausalChannel, Callable | None] = {
            CausalChannel.DML: dml_runner,
            CausalChannel.CAUSAL_FOREST: causal_forest_runner,
            CausalChannel.DOWHY_REFUTE: dowhy_runner,
            CausalChannel.DISCOVERY: discovery_runner,
        }
        self._clock = clock or datetime.datetime.now
        self._graph_cache: CausalGraphSnapshot | None = None  # 单槽缓存（指纹变更即失效）

    # ── 内部 ─────────────────────────────────────────────────────────────

    @staticmethod
    def _validate_names(treatment: str, outcome: str) -> None:
        if not treatment or not str(treatment).strip():
            raise CausalMlError("treatment 为空")
        if not outcome or not str(outcome).strip():
            raise CausalMlError("outcome 为空")

    @staticmethod
    def _validate_fingerprint(data_fingerprint: str) -> str:
        if not data_fingerprint or not str(data_fingerprint).strip():
            raise CausalMlError("data_fingerprint 为空（缓存失效判定无所依）")
        return str(data_fingerprint)

    @staticmethod
    def _validate_variables(variables: Iterable[str]) -> tuple[str, ...]:
        out: list[str] = []
        seen: set[str] = set()
        for v in variables:
            if not v or not str(v).strip():
                raise CausalMlError(f"变量集含空白项: {v!r}")
            s = str(v)
            if s not in seen:
                seen.add(s)
                out.append(s)
        if not out:
            raise CausalMlError("variables 为空（因果发现无节点）")
        return tuple(out)

    def _degraded_effect(self, channel: CausalChannel, treatment: str, outcome: str, note: str) -> CausalEffect:
        return CausalEffect(
            channel=channel,
            treatment=treatment,
            outcome=outcome,
            effect=0.0,
            p_value=1.0,
            n_samples=0,
            downgraded=True,
            note=note,
        )

    def _run_channel(
        self,
        channel: CausalChannel,
        treatment: str,
        outcome: str,
        context: Mapping[str, object],
    ) -> CausalEffect:
        """执行单通道效应估计；未注入/异常/产出非法一律降级不阻断。"""
        runner = self._runners[channel]
        if runner is None:
            return self._degraded_effect(channel, treatment, outcome, f"{channel.value} runner 未注入，降级跳过")
        try:
            raw = runner(treatment, outcome, context)
        except Exception as exc:  # noqa: BLE001 — 降级不阻断（蓝图 §1）
            _log.warning("因果通道 %s 执行异常，降级: %s", channel.value, exc)
            return self._degraded_effect(channel, treatment, outcome, f"{channel.value} 异常降级: {exc}")
        try:
            effect = float(raw.get("effect"))  # type: ignore[arg-type]
            p_value = float(raw.get("p_value"))  # type: ignore[arg-type]
        except (TypeError, ValueError):
            return self._degraded_effect(
                channel, treatment, outcome, f"{channel.value} 产出缺 effect/p_value 或不可转 float"
            )
        try:
            n_samples = int(raw.get("n_samples", 0) or 0)  # type: ignore[arg-type]
        except (TypeError, ValueError):
            n_samples = 0
        note = str(raw.get("note", "") or "")
        if raw.get("refuted"):
            note = (note + "；" if note else "") + "DoWhy证伪未通过"
        if not math.isfinite(effect) or not math.isfinite(p_value) or not 0.0 <= p_value <= 1.0 or n_samples < 0:
            return self._degraded_effect(
                channel, treatment, outcome, f"{channel.value} 产出数值非法（effect/p_value/n_samples 越界）"
            )
        return CausalEffect(
            channel=channel,
            treatment=treatment,
            outcome=outcome,
            effect=effect,
            p_value=p_value,
            n_samples=n_samples,
            downgraded=False,
            note=note,
        )

    # ── 效应估计 ──────────────────────────────────────────────────────────

    def estimate_effect(
        self,
        channel: CausalChannel,
        treatment: str,
        outcome: str,
        *,
        context: Mapping[str, object] | None = None,
    ) -> CausalEffect:
        """单通道效应估计（降级标记不阻断）。

        DISCOVERY 发现通道产出因果图而非效应估计，须走 precompute_causal_graph。
        """
        if not isinstance(channel, CausalChannel):
            raise CausalMlError(f"未知通道: {channel!r}")
        if channel is CausalChannel.DISCOVERY:
            raise CausalMlError("DISCOVERY 为因果发现通道，无效应估计（请用 precompute_causal_graph）")
        self._validate_names(treatment, outcome)
        ctx = dict(context) if context else {}
        return self._run_channel(channel, treatment, outcome, ctx)

    def estimate_all(
        self,
        treatment: str,
        outcome: str,
        *,
        context: Mapping[str, object] | None = None,
    ) -> CausalMlReport:
        """三效应通道全量估计 + 显著性筛选 + 降级清单（按通道定义序）。

        DISCOVERY 发现通道产出因果图而非效应估计，专属 precompute_causal_graph，
        不参与本汇总。
        """
        self._validate_names(treatment, outcome)
        ctx = dict(context) if context else {}
        effects = tuple(self._run_channel(ch, treatment, outcome, ctx) for ch in _EFFECT_CHANNELS)
        significant = self.filter_significant(effects)
        degraded = tuple(e.channel for e in effects if e.downgraded)
        return CausalMlReport(
            treatment=treatment,
            outcome=outcome,
            effects=effects,
            significant=significant,
            degraded_channels=degraded,
            ran_at=self._clock(),
        )

    # ── 显著性筛选 ────────────────────────────────────────────────────────

    def filter_significant(self, effects: Iterable[CausalEffect]) -> tuple[SignificantEffect, ...]:
        """显著性筛选：非降级 且 |effect|>阈值 且 p<p阈值（严格不等号）。

        输出按 |effect| 降序，同幅按 (channel, treatment, outcome) 字典序（确定性）。
        """
        out = [
            SignificantEffect(
                channel=e.channel,
                treatment=e.treatment,
                outcome=e.outcome,
                effect=e.effect,
                p_value=e.p_value,
            )
            for e in effects
            if not e.downgraded and abs(e.effect) > self._effect_threshold and e.p_value < self._p_value_threshold
        ]
        out.sort(key=lambda s: (-abs(s.effect), s.channel.value, s.treatment, s.outcome))
        return tuple(out)

    # ── 盘前预计算因果图缓存（按数据指纹失效） ─────────────────────────────

    @staticmethod
    def _normalize_edges(edges: Iterable[Iterable[str]]) -> tuple[tuple[tuple[str, str], ...], str]:
        """边归一化：去自环/去空白/去重/升序；返回 (边集, 丢弃说明)。"""
        seen: set[tuple[str, str]] = set()
        dropped_self = 0
        dropped_bad = 0
        for raw in edges:
            try:
                cause, effect = raw
            except (TypeError, ValueError):
                dropped_bad += 1
                continue
            cause_s, effect_s = str(cause).strip(), str(effect).strip()
            if not cause_s or not effect_s:
                dropped_bad += 1
                continue
            if cause_s == effect_s:
                dropped_self += 1
                continue
            seen.add((cause_s, effect_s))
        notes: list[str] = []
        if dropped_self:
            notes.append(f"丢弃自环边 {dropped_self} 条")
        if dropped_bad:
            notes.append(f"丢弃非法边 {dropped_bad} 条")
        return tuple(sorted(seen)), "；".join(notes)

    def precompute_causal_graph(
        self,
        data_fingerprint: str,
        variables: Iterable[str],
        *,
        context: Mapping[str, object] | None = None,
    ) -> CausalGraphSnapshot:
        """盘前预计算因果图：指纹与缓存一致→命中直返；不同→重算并替换缓存。"""
        fp = self._validate_fingerprint(data_fingerprint)
        vars_ = self._validate_variables(variables)
        if self._graph_cache is not None and self._graph_cache.fingerprint == fp:
            return self._graph_cache  # 缓存命中（数据未变更）
        ctx = dict(context) if context else {}
        downgraded = False
        note = ""
        edges: tuple[tuple[str, str], ...] = ()
        runner = self._runners[CausalChannel.DISCOVERY]
        if runner is None:
            downgraded, note = True, "discovery_runner 未注入，降级为空图"
        else:
            try:
                raw = runner(fp, vars_, ctx)
                edges, drop_note = self._normalize_edges(raw.get("edges", ()))
                note = str(raw.get("note", "") or "")
                if drop_note:
                    note = (note + "；" if note else "") + drop_note
            except Exception as exc:  # noqa: BLE001 — 降级不阻断（蓝图 §1）
                _log.warning("因果发现执行异常，降级: %s", exc)
                downgraded, note, edges = True, f"因果发现异常降级: {exc}", ()
        snap = CausalGraphSnapshot(
            fingerprint=fp,
            edges=edges,
            n_variables=len(vars_),
            computed_at=self._clock(),
            downgraded=downgraded,
            note=note,
        )
        self._graph_cache = snap
        return snap

    def cached_causal_graph(self, data_fingerprint: str) -> CausalGraphSnapshot | None:
        """按指纹查询缓存；指纹不一致（数据已变更）→ None（失效）。"""
        fp = self._validate_fingerprint(data_fingerprint)
        if self._graph_cache is None or self._graph_cache.fingerprint != fp:
            return None
        return self._graph_cache

    def invalidate_graph_cache(self) -> None:
        """手动失效缓存（盘前强制重算用）。"""
        self._graph_cache = None
