# [BLUEPRINT] MOD-POS-029 | docs/03_modules/_domain_position/position_recipe_compiler/blueprint.md
# [MODULE] zephyr.position.core.position_recipe_compiler
# [DOMAIN] D_POSITION
# [DEPENDENCIES] zephyr.shared.foundation.errors
# [CONSUMERS] F-06批次A执行器(planned); E2预审(position_recipe候选面)
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] 同schema+context编译结果确定性; 失活维折叠为baseline对N贡献=1; active_if受控命名空间求值异常fail-closed; baseline必须∈values; depends_on无环; 每recipe带内容寻址出生证(全维取值+折叠记录+prefix_key); 编译器内部零时钟取用(时间戳由调用方盖)
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidGridSchemaError(ZA-POS-0045)
# [TESTS] tests/position/test_position_recipe_compiler.py
# [A_module] module_id=MOD-POS-029 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
D_POSITION — 仓位配方编译器（F-06 组合层穷尽网格 · 编译器雏形）

把「维度 schema + 求值上下文」编译成 position_recipe 候选全集。
设计真源: docs/_working/2026-09-14-combination-layer-exhaustive-charter.md §十/§十二
机制出处: 条件/树结构参数空间（SMAC 2011 / TPE 2011 / Add-Tree 2017，蓝图附录 A-C1）。

三条编译铁律（蓝图 §8.2）:
  1. Schema 一次定型，执行分期——维度存在性由终局设计空间决定;
  2. 退化维度由编译器折叠，不被人裁剪——active_if 不活跃 → 折叠为 baseline;
  3. 失活维对试验数 N 的贡献 = 1（不是 |values|），N 只数真正发生过的尝试。

# [ALGO_FLOW] external: docs/03_modules/_domain_position/algo_flow/position_recipe_compiler.yaml
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass, field
from pathlib import Path
from statistics import NormalDist
from typing import Final

import yaml

from zephyr.shared.foundation.errors import ZephyrBaseError

_logger = __import__("logging").getLogger(__name__)


# active_if 受控求值白名单——只开无副作用的纯函数，禁 __builtins__ 全量注入
_SAFE_PREDICATE_BUILTINS: dict[str, object] = {
    "len": len,
    "abs": abs,
    "min": min,
    "max": max,
    "sum": sum,
    "int": int,
    "float": float,
    "bool": bool,
    "round": round,
}


class InvalidGridSchemaError(ZephyrBaseError):
    """ZA-POS-0045: 网格 schema 非法（baseline 越界 / depends_on 成环 / 谓词求值失败）。"""

    error_code = "ZA-POS-0045"


# cost_tier 语义（立项稿 §12.1 前缀共享的分组依据）:
#   signal_side — 影响信号/因子生成（贵，跨配方可共享前缀，进 prefix_key）
#   weight_invariant — 只影响组合权重调配（廉价重放，不进 prefix_key）
COST_TIERS = ("signal_side", "weight_invariant")

# E[max(Z_N)] 闭式常量（WO-12/C12 与官方件 deflated_sharpe_calculator 同源对齐；
# 数值真源=该件 EULER_MASCHERONI，此处副本仅为免拉模拟依赖的预览路径服务）
_EULER_MASCHERONI: Final[float] = 0.5772156649015329
_STD_NORMAL = NormalDist()


@dataclass(frozen=True)
class DimensionSpec:
    """单维声明——schema 一次定型的最小单元。

    active_if: 受控命名空间可求值的 Python 表达式（对 compile(context) 的 context
    求值）；None=恒活跃。求值异常按 ZA-POS-0045 fail-closed。
    """

    id: str
    values: tuple[str, ...]
    baseline: str
    active_if: str | None = None
    depends_on: tuple[str, ...] = ()
    cost_tier: str = "weight_invariant"
    desc: str = ""


@dataclass(frozen=True)
class PositionRecipe:
    """单条仓位配方 + 出生证。recipe_id = sha1(规范 JSON 取值)[:12]（内容寻址）。"""

    recipe_id: str
    values: dict[str, str]
    folded_dimensions: dict[str, str]
    prefix_key: str


@dataclass(frozen=True)
class GridExpansion:
    """编译产物：候选全集 + N 记账 + 折叠清单（出生证汇总）。"""

    recipes: tuple[PositionRecipe, ...]
    n_raw: int
    active_dimensions: tuple[str, ...]
    folded_dimensions: dict[str, str]
    schema_digest: str
    context: dict = field(default_factory=dict)


def _canonical(values: dict[str, str]) -> str:
    return json.dumps(values, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


class GridCompiler:
    """维度 schema → 配方全集的确定性编译器。

    Usage:
        schema = {"id": "D1_freq", "values": ["daily", "weekly"], "baseline": "weekly"}
        compiler = GridCompiler.from_dimensions([schema])
        expansion = compiler.compile({"strategy_pool": ["alpha"]})
        expansion.n_raw          # 名义格点数（失活维按 1 计）
        expansion.recipes[0]     # PositionRecipe（带出生证）
    """

    def __init__(self, dimensions: tuple[DimensionSpec, ...]) -> None:
        self._validate(dimensions)
        self._dimensions = tuple(sorted(dimensions, key=lambda d: self._topo_rank(d, dimensions)))

    @property
    def dimensions(self) -> tuple[DimensionSpec, ...]:
        return self._dimensions

    # ── 构造入口 ──────────────────────────────────────────────
    @classmethod
    def from_dimensions(cls, specs: list[dict]) -> GridCompiler:
        dims = tuple(
            DimensionSpec(
                id=s["id"],
                values=tuple(s["values"]),
                baseline=s["baseline"],
                active_if=s.get("active_if"),
                depends_on=tuple(s.get("depends_on", ())),
                cost_tier=s.get("cost_tier", "weight_invariant"),
                desc=s.get("desc", ""),
            )
            for s in specs
        )
        return cls(dims)

    @classmethod
    def from_yaml(cls, path: str | Path) -> GridCompiler:
        data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
        if not isinstance(data, dict) or "dimensions" not in data:
            raise InvalidGridSchemaError("schema YAML 顶层须为 {dimensions: [...]}", details={"path": str(path)})
        return cls.from_dimensions(data["dimensions"])

    # ── 校验（fail-closed） ───────────────────────────────────
    @staticmethod
    def _validate(dimensions: tuple[DimensionSpec, ...]) -> None:
        seen: set[str] = set()
        for d in dimensions:
            if d.id in seen:
                raise InvalidGridSchemaError("维度 id 重复", details={"dimension": d.id})
            seen.add(d.id)
            if not d.values:
                raise InvalidGridSchemaError("维度 values 为空", details={"dimension": d.id})
            if len(set(d.values)) != len(d.values):
                raise InvalidGridSchemaError("维度 values 有重复取值", details={"dimension": d.id})
            if d.baseline not in d.values:
                raise InvalidGridSchemaError(
                    "维度 baseline 不在 values 内",
                    details={"dimension": d.id, "baseline": d.baseline},
                )
            if d.cost_tier not in COST_TIERS:
                raise InvalidGridSchemaError(
                    "维度 cost_tier 非法", details={"dimension": d.id, "cost_tier": d.cost_tier}
                )
        for d in dimensions:
            for dep in d.depends_on:
                if dep not in seen:
                    raise InvalidGridSchemaError(
                        "维度依赖未声明维",
                        details={"dimension": d.id, "depends_on": dep},
                    )
        GridCompiler._check_cycles(dimensions)

    @staticmethod
    def _check_cycles(dimensions: tuple[DimensionSpec, ...]) -> None:
        by_id = {d.id: d for d in dimensions}
        state: dict[str, int] = {}

        def visit(node: str) -> None:
            if state.get(node) == 1:
                raise InvalidGridSchemaError("depends_on 成环", details={"dimension": node})
            if state.get(node) == 2:
                return
            state[node] = 1
            for dep in by_id[node].depends_on:
                visit(dep)
            state[node] = 2

        for d in dimensions:
            visit(d.id)

    @staticmethod
    def _topo_rank(d: DimensionSpec, all_dims: tuple[DimensionSpec, ...]) -> int:
        by_id = {x.id: x for x in all_dims}
        rank = 0
        frontier = {d.id}
        while frontier:
            frontier = {dep for fid in frontier for dep in by_id[fid].depends_on}
            rank += len(frontier)
        return rank

    # ── 编译 ──────────────────────────────────────────────────
    def compile(self, context: dict | None = None) -> GridExpansion:
        ctx = dict(context or {})
        active_map = self._evaluate_active(ctx)
        live = [d for d in self._dimensions if active_map[d.id]]
        folded = {d.id: d.baseline for d in self._dimensions if not active_map[d.id]}
        recipes = self._expand(live, folded)
        digest = hashlib.sha1(_canonical({d.id: list(d.values) for d in self._dimensions}).encode("utf-8")).hexdigest()[
            :12
        ]
        return GridExpansion(
            recipes=tuple(recipes),
            n_raw=len(recipes),
            active_dimensions=tuple(d.id for d in live),
            folded_dimensions=folded,
            schema_digest=digest,
            context=ctx,
        )

    def _evaluate_active(self, ctx: dict) -> dict[str, bool]:
        """求值每维 active_if。受控命名空间（无内建），异常 fail-closed。"""
        out: dict[str, bool] = {}
        for d in self._dimensions:
            if d.active_if is None:
                out[d.id] = True
                continue
            try:
                names = {**_SAFE_PREDICATE_BUILTINS, **ctx}
                out[d.id] = bool(eval(d.active_if, {"__builtins__": {}}, names))  # noqa: S307
            except Exception as exc:  # noqa: BLE001 谓词失败=编译失败，不静默折叠
                raise InvalidGridSchemaError(
                    "维度 active_if 求值失败",
                    details={
                        "dimension": d.id,
                        "active_if": d.active_if,
                        "error": str(exc),
                        "context_keys": sorted(ctx),
                    },
                ) from exc
        return out

    def _expand(self, live: list[DimensionSpec], folded: dict[str, str]) -> list[PositionRecipe]:
        signal_dims = [d.id for d in live if d.cost_tier == "signal_side"]
        combos: list[dict[str, str]] = [{}]
        for d in live:
            combos = [{**row, d.id: v} for row in combos for v in d.values]
        out = []
        for row in combos:
            full = {**row, **folded}
            prefix = _canonical({k: full[k] for k in signal_dims}) if signal_dims else ""
            out.append(
                PositionRecipe(
                    recipe_id=hashlib.sha1(_canonical(full).encode("utf-8")).hexdigest()[:12],
                    values=full,
                    folded_dimensions=dict(folded),
                    prefix_key=prefix,
                )
            )
        return out

    def count_n_raw(self, context: dict | None = None) -> int:
        """不展开直接计 N（失活维贡献=1）。O(维数)，供 36 万级名义空间预算。"""
        active_map = self._evaluate_active(dict(context or {}))
        n = 1
        for d in self._dimensions:
            n *= len(d.values) if active_map[d.id] else 1
        return n

    def estimate_max_z(self, n: int) -> float:
        """E[max(Z_N)]（Bailey & López de Prado 2014 闭式）——供 N 记账预览。

        唯真源仍是 zephyr.simulation.deflated_sharpe_calculator.expected_max_sharpe_z
        （全仓唯一真源，含公式推导与精度注记）；此处仅供网格预算阶段不拉模拟依赖时
        快速预览。WO-12/C12：旧实现用已废弃的 Euler–Maclaurin 渐近式（N=2 给 0.8469，
        官方件已切论文闭式给 0.5198），与本函数"与官方件同一公式"的自我声明矛盾，
        现按官方闭式逐位对齐（同一 stdlib NormalDist.inv_cdf，运算次序一致）。
        """
        if n <= 1:
            return 0.0
        nf = float(n)
        gamma = _EULER_MASCHERONI
        return (1.0 - gamma) * _STD_NORMAL.inv_cdf(1.0 - 1.0 / nf) + gamma * _STD_NORMAL.inv_cdf(
            1.0 - 1.0 / (nf * math.e)
        )


__all__: Final = [
    "COST_TIERS",
    "DimensionSpec",
    "GridCompiler",
    "GridExpansion",
    "InvalidGridSchemaError",
    "PositionRecipe",
]
