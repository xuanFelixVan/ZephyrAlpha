# [BLUEPRINT] MOD-INF-060 | 待统筹登记（10号文 implementation_plans/10_llm_infrastructure.md §4 Phase 2.3 + aiarch 清单 3.4）| §3.3
# [MODULE] zephyr.intelligence.gguf_model_manager
# [DOMAIN] D_INTELLIGENCE
# [DEPENDENCIES] pyyaml; zephyr.intelligence.local_llm_pool(PoolBudgets 消费出口); zephyr.intelligence.model_profiling.model_discovery(DiscoveredModel 类型，仅注解)
# [CONSUMERS] local_llm_pool 装配件（预算注入）; tests/intelligence/test_gguf_model_manager.py; 新模型引入人工查表流程
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 显存时段配额唯一真源=config/gguf_vram_budget.yaml（10号文 §3.3）；未登记模型加载一律阻断（fail-closed）；未知时段一律阻断；判定纯内存无IO（读表为显式 load 调用，判定路径不隐式读盘）；不复制 local_llm_pool 判定逻辑（PoolBudgets 仅经 to_pool_budgets 出口注入）
# [MODIFY-GUARD] 时段配额数值变更必须同步 10号文 §3.3 时段表与 config/gguf_vram_budget.yaml
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] 预算表文件缺失/结构非法/数值非法 -> GgufBudgetTableError（裸异常——不新增 ZA- 前缀码，沿 MOD-AU-003 域先例，防 error_code_registry 未登记漂移）; check_load 判定不抛异常（deny 经 LoadGateDecision 返回）
# [TESTS] tests/intelligence/test_gguf_model_manager.py
# [A_module] module_id=MOD-INF-060 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
# [ALGO_FLOW]
# I1: config/gguf_vram_budget.yaml（human_gated 显存预算表）；I2: 当前时段 + 已载模型清单
# F1: 读表校验（结构/数值 fail-closed）→ F2: check_load 三重门（登记命中 -> 单模型 ≤ 时段配额 -> 合计 ≤ 时段配额且 ≤ 硬上限）→ F3: to_pool_budgets 折算 PoolBudgets 供 local_llm_pool 消费
# O1: LoadGateDecision(allowed/reasons)；O2: DiscoveryDriftReport（已拉未登记/已登记未拉）；O3: PoolBudgets
# [/ALGO_FLOW]
"""GgufModelManager — GGUF 模型显存预算管理件（MOD-INF-060，10号文 §4 Phase 2.3）。

设计真源：10号文 §3.3「推理优化设计：GGUF/Ollama 为主路径」+ §3.3 显存时段配额表
+ §4 Phase 2.3 验收口径「显存预算表落 config/（human_gated），超预算加载被阻断」。

职责边界：
- 唯一真源：时段配额与模型显存登记只读 config/gguf_vram_budget.yaml，本模块不内嵌
  第二份数值（local_llm_pool 的 PoolBudgets 默认值是"无表兜底"，生产装配必须经
  to_pool_budgets() 注入本表——单真源裁定见 10号文施工令缺口 2.3）。
- 不新建显存调度器（10号文 §3.3：时段切换由既有 gpu_consensus_scheduler 执行）；
  本件只负责"新模型引入前查表 + 超预算阻断加载"的判定核。
- 模型清单枚举复用 ModelDiscovery（MOD-INF-034），sync_with_discovery 只做对账
  不自动改表（human_gated：表只能人改）。
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Final

import yaml

_log = logging.getLogger(__name__)

__all__: Final = [
    "DEFAULT_BUDGET_TABLE_PATH",
    "DiscoveryDriftReport",
    "GgufBudgetTableError",
    "GgufModelManager",
    "GgufModelEntry",
    "LoadGateDecision",
    "PeriodQuota",
    "load_budget_table",
    "period_from_time",
]

DEFAULT_BUDGET_TABLE_PATH: Final[str] = "config/gguf_vram_budget.yaml"

# 判定顺序即优先级：midday/postmarket 是 intraday/night 的子窗口，须先判
# （§3.3：午休 11:30-13:00 切 LLM 最小集，盘后 15:00-15:30 为切换窗口）。
_PERIOD_WINDOWS: Final[dict[str, tuple[tuple[int, int], tuple[int, int]]]] = {
    "premarket": ((8, 30), (9, 0)),
    "midday": ((11, 30), (13, 0)),
    "postmarket": ((15, 0), (15, 30)),
    "intraday": ((9, 15), (15, 0)),
    "night": ((15, 30), (8, 30)),  # 跨日窗口
}


class GgufBudgetTableError(Exception):
    """显存预算表缺失/非法（fail-closed，裸异常——见头部 ERROR_CONTRACT）。"""


@dataclass(frozen=True)
class PeriodQuota:
    """单时段推理侧显存配额。"""

    key: str
    inference_quota_gb: float
    window: tuple[str, str] = ("", "")
    note: str = ""


@dataclass(frozen=True)
class GgufModelEntry:
    """已登记 GGUF 模型条目。"""

    name: str
    vram_gb: float
    role: str = "backup"
    quant: str = ""
    kind: str = "llm"


@dataclass(frozen=True)
class LoadGateDecision:
    """加载门禁判定结果（不抛异常，deny 经本结构返回）。"""

    allowed: bool
    model: str
    period: str
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class DiscoveryDriftReport:
    """ModelDiscovery 枚举结果与预算表的对账报告。"""

    pulled_but_unregistered: tuple[str, ...] = ()
    registered_but_not_pulled: tuple[str, ...] = ()
    registered: tuple[str, ...] = ()


@dataclass(frozen=True)
class _BudgetTable:
    hard_cap_gb: float
    periods: dict[str, PeriodQuota]
    models: dict[str, GgufModelEntry]


def period_from_time(hour: int, minute: int) -> str:
    """按 10号文 §3.3 时段表把 Asia/Shanghai 本地时刻映射到时段键。

    窗口外时刻（09:00-09:15 集合竞价间隙等）按下一临近窗口归属：
    盘前结束→盘中开始之间归 intraday 之前的 premarket 口径不适用，
    保守归入 intraday（推理优先时段口径更宽但状态已是"推理模型已加载"）。
    """
    t = hour * 60 + minute
    for key, ((sh, sm), (eh, em)) in _PERIOD_WINDOWS.items():
        start, end = sh * 60 + sm, eh * 60 + em
        if start < end:
            if start <= t < end:
                return key
        elif t >= start or t < end:  # 跨日窗口（night）
            return key
    # 09:00-09:15 间隙：盘前加载已完成、盘中未开始，按盘中口径
    return "intraday"


def load_budget_table(path: str | Path = DEFAULT_BUDGET_TABLE_PATH) -> GgufModelManager:
    """读取并校验显存预算表（fail-closed：文件缺失/结构非法即抛 GgufBudgetTableError）。"""
    p = Path(path)
    if not p.exists():
        raise GgufBudgetTableError(f"显存预算表不存在: {p}")
    try:
        data = yaml.safe_load(p.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise GgufBudgetTableError(f"显存预算表 YAML 解析失败: {p}: {exc}") from exc
    if not isinstance(data, dict):
        raise GgufBudgetTableError(f"显存预算表顶层必须是 mapping: {p}")
    return GgufModelManager(_parse_table(data, p))


def _parse_table(data: dict[str, Any], path: Path) -> _BudgetTable:
    hard_cap = data.get("hard_cap_gb")
    if not isinstance(hard_cap, int | float) or isinstance(hard_cap, bool) or hard_cap <= 0:
        raise GgufBudgetTableError(f"hard_cap_gb 必须为正数: {path}")

    raw_periods = data.get("period_quotas")
    if not isinstance(raw_periods, dict) or not raw_periods:
        raise GgufBudgetTableError(f"period_quotas 缺失或非 mapping: {path}")
    periods: dict[str, PeriodQuota] = {}
    for key, raw in raw_periods.items():
        if not isinstance(raw, dict):
            raise GgufBudgetTableError(f"period_quotas.{key} 必须是 mapping: {path}")
        quota = raw.get("inference_quota_gb")
        if not isinstance(quota, int | float) or isinstance(quota, bool) or quota <= 0:
            raise GgufBudgetTableError(f"period_quotas.{key}.inference_quota_gb 必须为正数: {path}")
        if quota > hard_cap:
            raise GgufBudgetTableError(
                f"period_quotas.{key}.inference_quota_gb={quota} 超 hard_cap_gb={hard_cap}: {path}"
            )
        window_raw = raw.get("window") or ["", ""]
        periods[str(key)] = PeriodQuota(
            key=str(key),
            inference_quota_gb=float(quota),
            window=(str(window_raw[0]), str(window_raw[1])) if len(window_raw) >= 2 else ("", ""),
            note=str(raw.get("note", "")),
        )

    raw_models = data.get("models")
    if not isinstance(raw_models, list):
        raise GgufBudgetTableError(f"models 缺失或非 list: {path}")
    models: dict[str, GgufModelEntry] = {}
    for raw in raw_models:
        if not isinstance(raw, dict) or not raw.get("name"):
            raise GgufBudgetTableError(f"models 条目缺 name: {path}")
        vram = raw.get("vram_gb")
        if not isinstance(vram, int | float) or isinstance(vram, bool) or vram < 0:
            raise GgufBudgetTableError(f"models.{raw['name']}.vram_gb 必须为非负数: {path}")
        name = str(raw["name"])
        if name in models:
            raise GgufBudgetTableError(f"models 重复登记: {name}: {path}")
        models[name] = GgufModelEntry(
            name=name,
            vram_gb=float(vram),
            role=str(raw.get("role", "backup")),
            quant=str(raw.get("quant", "")),
            kind=str(raw.get("kind", "llm")),
        )

    return _BudgetTable(hard_cap_gb=float(hard_cap), periods=periods, models=models)


class GgufModelManager:
    """GGUF 模型显存预算判定核（判定路径纯内存无 IO）。

    用法::

        mgr = load_budget_table()
        decision = mgr.check_load("qwen3:8b", period="intraday", loaded_models=["BGE-M3:latest"])
        if not decision.allowed:
            ...  # 阻断加载
    """

    def __init__(self, table: _BudgetTable) -> None:
        self._table = table

    @property
    def hard_cap_gb(self) -> float:
        return self._table.hard_cap_gb

    @property
    def periods(self) -> dict[str, PeriodQuota]:
        return dict(self._table.periods)

    @property
    def registered_models(self) -> dict[str, GgufModelEntry]:
        return dict(self._table.models)

    def check_load(
        self,
        model_name: str,
        period: str,
        loaded_models: list[str] | tuple[str, ...] | None = None,
    ) -> LoadGateDecision:
        """新模型引入/加载前三重门判定（fail-closed）。

        门1 登记命中：未在预算表登记的模型一律阻断（新模型须先人审登记入表）。
        门2 单模型配额：模型显存 ≤ 当前时段推理侧配额。
        门3 合计配额：已载登记模型合计 + 本模型 ≤ 时段配额 且 ≤ 硬上限。
        """
        quota = self._table.periods.get(period)
        if quota is None:
            return LoadGateDecision(
                allowed=False,
                model=model_name,
                period=period,
                reasons=(f"未知时段 {period!r}（fail-closed；合法时段={sorted(self._table.periods)}）",),
            )
        entry = self._table.models.get(model_name)
        if entry is None:
            return LoadGateDecision(
                allowed=False,
                model=model_name,
                period=period,
                reasons=(f"模型 {model_name!r} 未登记于 config/gguf_vram_budget.yaml（fail-closed，先登记再加载）",),
            )

        reasons: list[str] = []
        if entry.vram_gb > quota.inference_quota_gb:
            reasons.append(
                f"单模型超时段配额: {model_name} vram={entry.vram_gb}GB > {period} 配额={quota.inference_quota_gb}GB"
            )
        if entry.vram_gb > self._table.hard_cap_gb:
            reasons.append(
                f"单模型超硬上限: {model_name} vram={entry.vram_gb}GB > hard_cap={self._table.hard_cap_gb}GB"
            )

        loaded = list(loaded_models or [])
        unknown_loaded = [m for m in loaded if m not in self._table.models]
        if unknown_loaded:
            reasons.append(f"已载清单含未登记模型（fail-closed）: {unknown_loaded}")
        used = sum(self._table.models[m].vram_gb for m in loaded if m in self._table.models)
        total = used + entry.vram_gb
        if total > quota.inference_quota_gb:
            reasons.append(
                f"合计超时段配额: used={used:.1f}GB + {entry.vram_gb}GB > {period} 配额={quota.inference_quota_gb}GB"
            )
        if total > self._table.hard_cap_gb:
            reasons.append(f"合计超硬上限: {total:.1f}GB > hard_cap={self._table.hard_cap_gb}GB")

        if reasons:
            return LoadGateDecision(allowed=False, model=model_name, period=period, reasons=tuple(reasons))
        return LoadGateDecision(
            allowed=True,
            model=model_name,
            period=period,
            reasons=(f"通过: used={used:.1f}GB + {entry.vram_gb}GB <= {period} 配额={quota.inference_quota_gb}GB",),
        )

    def sync_with_discovery(self, discovered: list[Any]) -> DiscoveryDriftReport:
        """对账 ModelDiscovery 枚举结果（只出报告不改表，human_gated）。

        Args:
            discovered: ModelDiscovery.discover_ollama() 的 DiscoveredModel 列表
                （结构鸭子类型：取 .name，避免对本模块外的 dataclass 硬依赖）。
        """
        pulled = {str(getattr(m, "name", "")) for m in discovered}
        pulled.discard("")
        registered = set(self._table.models)
        return DiscoveryDriftReport(
            pulled_but_unregistered=tuple(sorted(pulled - registered)),
            registered_but_not_pulled=tuple(sorted(registered - pulled)),
            registered=tuple(sorted(registered & pulled)),
        )

    def to_pool_budgets(self) -> Any:
        """折算为 local_llm_pool 的 PoolBudgets（10号文施工令：local_llm_pool 消费本表）。

        映射：intraday 档 = 盘中（intraday）配额；postmarket 档 = 夜间（night）最小集配额。
        local_llm_pool 保持纯内存判定不变，本出口负责把真源数值注入。
        """
        from zephyr.intelligence.local_llm_pool import PoolBudgets

        return PoolBudgets(
            intraday_gb=self._table.periods["intraday"].inference_quota_gb,
            postmarket_gb=self._table.periods["night"].inference_quota_gb,
        )
