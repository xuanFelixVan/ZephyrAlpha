# [BLUEPRINT] MOD-GOV-051 | docs/03_modules/_domain_governance/depmap_engine/blueprint.md
# [MODULE] zephyr.governance.depmap_engine
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] 无（AST 纯内存解析；源码供给/depgraph_reader/层注册表全注入；depgraph 库仅经注入 reader 比对）
# [CONSUMERS] 运行时装配批（CI 门禁装配：仓源码供给回调 + depgraph reader + L0/L1/L2 层注册表统一注入）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 层词表闭合(L0|L1|L2); 合法依赖仅高层→低层(rank大→rank小)或同层; 目录过滤先 include 后 exclude; 语法错误/越顶相对导入 Fail-Closed; 边/循环/越层报告全确定性排序; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_governance/depmap_engine/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] DepmapError(占位 ZA-GOV-UNREGISTERED-DEPMAP)——空层注册表/非法层/空键/语法错误/越顶相对导入/非 .py 路径/空路径/reader 未注入或读取失败时抛
# [TESTS] tests/governance/test_depmap_engine.py
# [A_module] module_id=MOD-GOV-051 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""
DepmapEngine — DepMap 依赖扫描引擎（MOD-GOV-051）。

B13-04303（AUD-DRAFT-001-DIGEST P2 波 P2-W12，CAND-WORKTREE-002，A3
MOD-INF-040）：AST 依赖扫描引擎——全仓 import 解析（ast.walk + 目录过滤）
→ 分层（L0/L1/L2 层注册表）存储 → 与 depgraph 库 diff（注入
depgraph_reader 回调）→ 循环依赖 / 越层调用报告（接 CI 门禁语义）。

查重分工（蓝图 §0）：depgraph_schema=依赖图 PG 库 DDL（本件不写库，仅经
注入 reader 比对）；architecture_governance/dependency_manager=运行时依赖
治理（本件=静态 AST 扫描与 diff 报告，零交集）；import 方向门禁族=提交门
禁实现（本件只产出报告，不挂 hook）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: layer_registry 参数
#   fields: 参数 layer_registry（无注解）
#   code: depmap_engine.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: depgraph_reader 参数
#   fields: 参数 depgraph_reader（无注解）
#   code: depmap_engine.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① DepmapEngine
#   name_en: DepmapEngine
#   intro: AST 依赖扫描引擎（解析 + 分层存储 + depgraph diff + 循环/越层报告）。
#   desc: AST 依赖扫描引擎（解析 + 分层存储 + depgraph diff + 循环/越层报告）。；公共方法（定义序）: scan_sources, edges, edges_by_layer, diff_depgrap…
#   inputs: layer_registry depgraph_reader
#   outputs: 返回值
#   （注：A1 之后另有 5 个公共定义未列入（含 5 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（6 定义）
#   name_en: public defs
#   intro: DepmapEngine
#   downstream: 运行时装配批（CI 门禁装配：仓源码供给回调 + depgraph reader + L0/L1/L2 层注册表统一注入）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> O1
"""

from __future__ import annotations

import ast
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Final, Iterable, Mapping

_log = logging.getLogger(__name__)

__all__: Final = [
    "DepmapDiff",
    "DepmapEngine",
    "DepmapError",
    "DepmapLayer",
    "ImportEdge",
    "LayerViolation",
]

#: 层序号（合法依赖方向仅 rank 大 → rank 小，或同层）
_LAYER_RANK: Final[dict[DepmapLayer, int]] = {}


class DepmapError(Exception):
    """DepMap 扫描输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-GOV-UNREGISTERED-DEPMAP。
    """


class DepmapLayer(str, Enum):
    """分层词表（闭合）：L0 基础设施 / L1 领域服务 / L2 应用编排。"""

    L0 = "L0"
    L1 = "L1"
    L2 = "L2"


_LAYER_RANK.update(
    {
        DepmapLayer.L0: 0,
        DepmapLayer.L1: 1,
        DepmapLayer.L2: 2,
    }
)


@dataclass(frozen=True)
class ImportEdge:
    """单条 import 依赖边（importer → imported，frozen）。"""

    importer: str
    imported: str
    lineno: int


@dataclass(frozen=True)
class DepmapDiff:
    """与 depgraph 库的 diff 结果（确定性排序，frozen）。

    missing_in_depgraph: 扫描到但 depgraph 库缺失的边（importer, imported）。
    stale_in_depgraph:   depgraph 库存量但本次扫描已不存在的边。
    """

    missing_in_depgraph: tuple[tuple[str, str], ...]
    stale_in_depgraph: tuple[tuple[str, str], ...]


@dataclass(frozen=True)
class LayerViolation:
    """越层调用报告条目（低层 import 高层，frozen）。"""

    importer: str
    importer_layer: DepmapLayer
    imported: str
    imported_layer: DepmapLayer
    reason: str


class DepmapEngine:
    """AST 依赖扫描引擎（解析 + 分层存储 + depgraph diff + 循环/越层报告）。"""

    def __init__(
        self,
        *,
        layer_registry: Mapping[str, DepmapLayer],
        depgraph_reader: Callable[[], Iterable[tuple[str, str]]] | None = None,
    ) -> None:
        if not layer_registry:
            raise DepmapError("layer_registry 为空（无 L0/L1/L2 层注册表）")
        for prefix, layer in layer_registry.items():
            if not prefix:
                raise DepmapError("层注册表键（模块前缀）为空")
            if not isinstance(layer, DepmapLayer):
                raise DepmapError(f"非法层级: {layer!r}")
        self._registry: dict[str, DepmapLayer] = dict(layer_registry)
        self._reader = depgraph_reader
        self._edges: set[ImportEdge] = set()
        self._by_layer: dict[DepmapLayer, set[ImportEdge]] = {layer: set() for layer in DepmapLayer}

    # ── 内部 ─────────────────────────────────────────────────────────────

    @staticmethod
    def _module_name(relpath: str) -> str:
        """仓内相对路径 → 点分模块名（src/ 前缀与 __init__ 归一）。"""
        if not relpath:
            raise DepmapError("源码路径为空")
        norm = relpath.replace("\\", "/")
        if not norm.endswith(".py"):
            raise DepmapError(f"非 .py 源码路径: {relpath!r}")
        parts = [seg for seg in norm[:-3].split("/") if seg]
        if parts and parts[0] == "src":
            parts = parts[1:]
        if parts and parts[-1] == "__init__":
            parts = parts[:-1]
        if not parts:
            raise DepmapError(f"无法派生模块名: {relpath!r}")
        return ".".join(parts)

    @staticmethod
    def _imports_of(module: str, source: str, relpath: str) -> list[tuple[str, int]]:
        """AST 解析单文件 import（语法错误/越顶相对导入 Fail-Closed）。"""
        try:
            tree = ast.parse(source)
        except SyntaxError as exc:
            raise DepmapError(f"语法错误: {relpath!r}: {exc}") from exc
        out: list[tuple[str, int]] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    out.append((alias.name, node.lineno))
            elif isinstance(node, ast.ImportFrom):
                if node.level:
                    base = module.split(".")[: -node.level]
                    if node.module:
                        base += node.module.split(".")
                    if not base:
                        raise DepmapError(f"越顶相对导入: {relpath!r} 第 {node.lineno} 行")
                    if node.module:
                        out.append((".".join(base), node.lineno))
                    else:
                        # from . import sibling → 目标为包内子模块
                        for alias in node.names:
                            out.append((".".join(base + [alias.name]), node.lineno))
                elif node.module:
                    out.append((node.module, node.lineno))
        return out

    def _layer_of(self, module: str) -> DepmapLayer | None:
        """最长点分前缀匹配层注册表（外部库未注册 → None，不参与越层判定）。"""
        parts = module.split(".")
        for i in range(len(parts), 0, -1):
            layer = self._registry.get(".".join(parts[:i]))
            if layer is not None:
                return layer
        return None

    # ── 扫描 ─────────────────────────────────────────────────────────────

    def scan_sources(
        self,
        sources: Mapping[str, str],
        *,
        include_prefixes: tuple[str, ...] = (),
        exclude_prefixes: tuple[str, ...] = (),
    ) -> int:
        """扫描源码映射 {相对路径: 源码文本}，返回本次新增边数。

        目录过滤：include_prefixes 非空时仅保留命中的路径；再按
        exclude_prefixes 剔除。同一 importer+imported+lineno 边幂等去重。
        """
        added = 0
        for relpath in sorted(sources):
            norm = relpath.replace("\\", "/")
            if include_prefixes and not any(norm.startswith(p) for p in include_prefixes):
                continue
            if any(norm.startswith(p) for p in exclude_prefixes):
                continue
            module = self._module_name(norm)
            for imported, lineno in self._imports_of(module, sources[relpath], norm):
                edge = ImportEdge(importer=module, imported=imported, lineno=lineno)
                if edge in self._edges:
                    continue
                self._edges.add(edge)
                layer = self._layer_of(module)
                if layer is not None:
                    self._by_layer[layer].add(edge)
                added += 1
        _log.info("DepMap 扫描完成: 新增 %d 边（累计 %d）", added, len(self._edges))
        return added

    # ── 查询 ─────────────────────────────────────────────────────────────

    def edges(self) -> tuple[ImportEdge, ...]:
        """全部依赖边（按 (importer, imported, lineno) 确定性排序）。"""
        return tuple(sorted(self._edges, key=lambda e: (e.importer, e.imported, e.lineno)))

    def edges_by_layer(self, layer: DepmapLayer) -> tuple[ImportEdge, ...]:
        """按 importer 层取边（分层存储视图；非法层 Fail-Closed）。"""
        if not isinstance(layer, DepmapLayer):
            raise DepmapError(f"非法层级: {layer!r}")
        return tuple(sorted(self._by_layer[layer], key=lambda e: (e.importer, e.imported, e.lineno)))

    # ── depgraph diff ────────────────────────────────────────────────────

    def diff_depgraph(self) -> DepmapDiff:
        """与 depgraph 库 diff（reader 未注入 Fail-Closed，不旁路）。"""
        if self._reader is None:
            raise DepmapError("depgraph_reader 未注入（无法与 depgraph 库比对）")
        try:
            known = {(str(a), str(b)) for a, b in self._reader()}
        except DepmapError:
            raise
        except Exception as exc:  # noqa: BLE001 — reader 异常统一 Fail-Closed
            raise DepmapError(f"depgraph_reader 读取失败: {exc}") from exc
        scanned = {(e.importer, e.imported) for e in self._edges}
        diff = DepmapDiff(
            missing_in_depgraph=tuple(sorted(scanned - known)),
            stale_in_depgraph=tuple(sorted(known - scanned)),
        )
        _log.info(
            "depgraph diff: 缺失 %d 边 / 陈旧 %d 边",
            len(diff.missing_in_depgraph),
            len(diff.stale_in_depgraph),
        )
        return diff

    # ── 循环 / 越层报告 ───────────────────────────────────────────────────

    def find_cycles(self) -> list[tuple[str, ...]]:
        """循环依赖检测（DFS 三色标记；环按最小节点旋转归一去重，确定性排序）。"""
        adjacency: dict[str, list[str]] = {}
        for edge in self._edges:
            adjacency.setdefault(edge.importer, []).append(edge.imported)
            adjacency.setdefault(edge.imported, [])
        for node in adjacency:
            adjacency[node] = sorted(set(adjacency[node]))

        color: dict[str, int] = dict.fromkeys(adjacency, 0)  # 0白 1灰 2黑
        path: list[str] = []
        cycles: set[tuple[str, ...]] = set()

        def _dfs(node: str) -> None:
            color[node] = 1
            path.append(node)
            for nxt in adjacency[node]:
                if color[nxt] == 1:
                    cycle = path[path.index(nxt) :]
                    pivot = cycle.index(min(cycle))
                    cycles.add(tuple(cycle[pivot:] + cycle[:pivot]))
                elif color[nxt] == 0:
                    _dfs(nxt)
            path.pop()
            color[node] = 2

        for node in sorted(adjacency):
            if color[node] == 0:
                _dfs(node)
        out = sorted(cycles)
        if out:
            _log.warning("DepMap 循环依赖: %d 个环", len(out))
        return out

    def layer_violations(self) -> list[LayerViolation]:
        """越层调用报告（低层 import 高层；两端均须在层注册表内）。"""
        out: list[LayerViolation] = []
        for edge in sorted(self._edges, key=lambda e: (e.importer, e.imported, e.lineno)):
            src_layer = self._layer_of(edge.importer)
            dst_layer = self._layer_of(edge.imported)
            if src_layer is None or dst_layer is None:
                continue
            if _LAYER_RANK[src_layer] < _LAYER_RANK[dst_layer]:
                out.append(
                    LayerViolation(
                        importer=edge.importer,
                        importer_layer=src_layer,
                        imported=edge.imported,
                        imported_layer=dst_layer,
                        reason=(
                            f"越层调用: {edge.importer}({src_layer.value}) -> "
                            f"{edge.imported}({dst_layer.value})，合法仅高层→低层或同层"
                        ),
                    )
                )
        if out:
            _log.warning("DepMap 越层调用: %d 条", len(out))
        return out
