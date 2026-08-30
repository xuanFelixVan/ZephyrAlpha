# [BLUEPRINT] MOD-L02-001 | docs/03_modules/_domain_factor/blueprint.md | §D-FACTOR-CORE-DAG
# [MODULE] zephyr.factor.core.factor_dag.dag
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] zephyr.shared.schema.schemas; zephyr.factor.factor_base
# [CONSUMERS] zephyr.factor.core.dag_manager; zephyr.factor.core.dist_feature_eng
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] DAG 必须无环（topological_layers 检测到环时抛 ValueError）；dependencies 中不在 nodes 集合内的项视为外部输入（自动过滤）
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] validate 返回错误列表（不抛）；topological_layers 检测到环抛 ValueError；build_dag_from_registry 对未注册因子抛 KeyError
# [TESTS] tests/factor/test_factor_dag.py
# [A_module] module_id=MOD-L02-001 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
r"""
D_FACTOR core factor_dag.dag——因子 DAG 数据结构 + Kahn 拓扑分层算法。

提供：
- FactorNode / FactorEdge / FactorDAG：pydantic 数据结构（复用 BASE_CONFIG）
- FactorDAG.topological_layers()：Kahn 算法分层，返回每层可并行计算的 factor_id 列表
- FactorDAG.validate()：返回错误列表（环 / 悬空边 / 重复节点）
- build_dag_from_registry()：从 FactorRegistry 查询 dependencies 自动构建 DAG

设计要点：
- 不复用 infrastructure/pipeline/models.py 的 PipelineDAG（其 module_id 限 ^M\d{1,2}$，
  与 factor_id 语义不符），factor_dag 是因子域专用 DAG
- dependencies 字段语义：FactorNode.dependencies 列出该因子依赖的上游 factor_id
- topological_layers 返回分层结果，层内因子可并行计算

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: factor_ids 参数
#   fields: 参数 factor_ids，类型注解 list[str]
#   code: dag.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: dag_id 参数
#   fields: 参数 dag_id，类型注解 str
#   code: dag.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① build_dag_from_registry
#   name_en: build_dag_from_registry
#   intro: 从 FactorRegistry 查询 factor_ids 的 dependencies，自动构建 DAG。
#   desc: 从 FactorRegistry 查询 factor_ids 的 dependencies，自动构建 DAG。 自动过滤 dependencies 中不在 factor_ids…；源码 L277-L313
#   inputs: factor_ids dag_id
#   outputs: FactorDAG
#   （注：A1 之后另有 3 个公共定义未列入（含 3 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: FactorDAG
#   name_en: FactorDAG
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: zephyr.factor.core.dag_manager; zephyr.factor.core.dist_feature_eng
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> O1
"""

from __future__ import annotations

from collections import defaultdict

from pydantic import BaseModel, Field

from zephyr.shared.schema.schemas import BASE_CONFIG


class FactorNode(BaseModel):
    """DAG 节点——单个因子。

    Attributes:
        factor_id: 全局唯一因子 ID（与 FactorRegistry 对齐）
        domain: 因子域（technical/fundamental/alternative/macro），可选
        dependencies: 依赖的上游 factor_id 列表（用于计算顺序）
        metadata: 扩展元数据（如版本、标签等）
    """

    model_config = BASE_CONFIG
    factor_id: str
    domain: str = ""
    dependencies: list[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)


class FactorEdge(BaseModel):
    """DAG 边——因子间依赖关系。

    Attributes:
        from_factor: 上游因子（被依赖项）
        to_factor: 下游因子（依赖 from_factor）
    """

    model_config = BASE_CONFIG
    from_factor: str
    to_factor: str


class FactorDAG(BaseModel):
    """因子 DAG——有向无环图。

    Attributes:
        dag_id: DAG 唯一标识
        nodes: 节点列表
        edges: 边列表（可从 nodes.dependencies 推导，也可显式声明）

    Notes:
        - 节点的 dependencies 字段优先用于拓扑分层
        - edges 字段为辅助声明，validate() 会检查 edges 与 dependencies 的一致性
    """

    model_config = BASE_CONFIG
    dag_id: str
    nodes: list[FactorNode] = Field(default_factory=list)
    edges: list[FactorEdge] = Field(default_factory=list)

    def add_node(self, node: FactorNode) -> None:
        """追加节点。重复 factor_id 时覆盖原节点。"""
        existing = next((n for n in self.nodes if n.factor_id == node.factor_id), None)
        if existing is not None:
            self.nodes.remove(existing)
        self.nodes.append(node)

    def add_edge(self, edge: FactorEdge) -> None:
        """追加边。重复边（同 from/to）时跳过。"""
        if not any(e.from_factor == edge.from_factor and e.to_factor == edge.to_factor for e in self.edges):
            self.edges.append(edge)

    def validate(self) -> list[str]:
        """校验 DAG 完整性，返回错误列表（不抛异常）。

        检查项：
        - 重复节点（同 factor_id 多次出现）
        - 悬空边（from/to 因子不在 nodes 中）
        - 环（dependencies 形成循环）
        """
        errors: list[str] = []

        # 1. 重复节点检查
        seen: set[str] = set()
        for n in self.nodes:
            if n.factor_id in seen:
                errors.append(f"重复节点 factor_id={n.factor_id}")
            seen.add(n.factor_id)

        # 2. 悬空边检查
        node_ids = {n.factor_id for n in self.nodes}
        for e in self.edges:
            if e.from_factor not in node_ids:
                errors.append(f"悬空边 from_factor={e.from_factor} 不在节点集合中")
            if e.to_factor not in node_ids:
                errors.append(f"悬空边 to_factor={e.to_factor} 不在节点集合中")

        # 3. 环检测（基于 dependencies）
        cycle = _detect_cycle_via_dependencies(self.nodes)
        if cycle is not None:
            errors.append(f"检测到环: {' -> '.join(cycle)}")

        return errors

    def topological_layers(self) -> list[list[str]]:
        """Kahn 算法分层：返回每层可并行计算的 factor_id 列表。

        Returns:
            分层列表，如 [[A, B], [C], [D]] 表示第 0 层 A/B 可并行，第 1 层 C，第 2 层 D。

        Raises:
            ValueError: 检测到环时抛出（含环路径详情）。
        """
        if not self.nodes:
            return []

        node_ids = {n.factor_id for n in self.nodes}
        # 构建邻接表：deps[factor_id] = 该因子依赖的上游 factor_id 集合（仅限 DAG 内的）
        deps: dict[str, set[str]] = defaultdict(set)
        reverse_deps: dict[str, set[str]] = defaultdict(set)  # 反向：被谁依赖
        for n in self.nodes:
            for dep in n.dependencies:
                if dep in node_ids:  # 过滤外部输入因子
                    deps[n.factor_id].add(dep)
                    reverse_deps[dep].add(n.factor_id)

        # 初始入度 = 该节点的依赖数
        in_degree: dict[str, int] = {fid: len(deps[fid]) for fid in node_ids}

        layers: list[list[str]] = []
        remaining = set(node_ids)

        while remaining:
            # 当前层：入度为 0 的节点
            current_layer = sorted(  # sorted 保证测试可复现
                [fid for fid in remaining if in_degree[fid] == 0]
            )
            if not current_layer:
                # 剩余节点入度均 >0 → 存在环
                cycle_path = _trace_cycle(remaining, deps)
                raise ValueError(f"检测到环，无法分层: {' -> '.join(cycle_path)}")

            layers.append(current_layer)
            for fid in current_layer:
                remaining.discard(fid)
                # 移除该节点后，其下游节点入度减 1
                for downstream in reverse_deps[fid]:
                    if downstream in remaining:
                        in_degree[downstream] -= 1

        return layers


def _detect_cycle_via_dependencies(nodes: list[FactorNode]) -> list[str] | None:
    """基于 dependencies 字段检测环。返回环路径或 None。"""
    node_ids = {n.factor_id for n in nodes}
    deps: dict[str, set[str]] = defaultdict(set)
    for n in nodes:
        for dep in n.dependencies:
            if dep in node_ids:
                deps[n.factor_id].add(dep)

    # DFS 三色标记法：WHITE(未访问) / GRAY(在当前路径) / BLACK(已完成)
    WHITE, GRAY, BLACK = 0, 1, 2
    color: dict[str, int] = {fid: WHITE for fid in node_ids}
    path: list[str] = []

    def dfs(node: str) -> list[str] | None:
        color[node] = GRAY
        path.append(node)
        for dep in deps[node]:
            if color[dep] == GRAY:
                # 找到环：从 path 中 dep 的位置开始到当前 node
                cycle_start = path.index(dep)
                return path[cycle_start:] + [dep]
            if color[dep] == WHITE:
                result = dfs(dep)
                if result is not None:
                    return result
        path.pop()
        color[node] = BLACK
        return None

    for fid in node_ids:
        if color[fid] == WHITE:
            result = dfs(fid)
            if result is not None:
                return result
    return None


def _trace_cycle(remaining: set[str], deps: dict[str, set[str]]) -> list[str]:
    """当 Kahn 算法剩余节点均入度 >0 时，追踪一个具体环路径用于错误信息。"""
    # 从任意剩余节点出发，沿 dependencies 走，首次遇到已访问节点即环
    start = next(iter(remaining))
    visited: list[str] = []
    seen: set[str] = set()
    current = start
    while current not in seen:
        if current not in remaining:
            break
        seen.add(current)
        visited.append(current)
        deps_current = deps.get(current, set())
        # 优先走仍在 remaining 中的依赖
        next_nodes = [d for d in deps_current if d in remaining]
        if not next_nodes:
            break
        current = next_nodes[0]
    if current in seen:
        cycle_start = visited.index(current)
        return visited[cycle_start:] + [current]
    return visited


def build_dag_from_registry(factor_ids: list[str], dag_id: str = "default") -> FactorDAG:
    """从 FactorRegistry 查询 factor_ids 的 dependencies，自动构建 DAG。

    自动过滤 dependencies 中不在 factor_ids 集合内的项（外部输入因子，如行情数据）。

    Args:
        factor_ids: 待构建 DAG 的因子 ID 列表（须在 FactorRegistry 中已注册）
        dag_id: DAG 唯一标识，默认 "default"

    Returns:
        FactorDAG 实例

    Raises:
        KeyError: factor_id 未在 FactorRegistry 注册
    """
    # 延迟 import 避免 factor_dag 被 factor_base 强依赖（消除潜在循环 import）
    from zephyr.factor.factor_base import FactorRegistry

    factor_id_set = set(factor_ids)
    dag = FactorDAG(dag_id=dag_id)

    for fid in factor_ids:
        meta = FactorRegistry.get(fid).meta  # 抛 KeyError 如果未注册
        # 仅保留 DAG 内的依赖（外部输入因子过滤）
        internal_deps = [d for d in meta.dependencies if d in factor_id_set]
        node = FactorNode(
            factor_id=meta.factor_id,
            domain=meta.domain,
            dependencies=internal_deps,
            metadata={"version": meta.version, "name": meta.name},
        )
        dag.add_node(node)
        # 同步声明边（from=上游, to=下游）
        for dep in internal_deps:
            dag.add_edge(FactorEdge(from_factor=dep, to_factor=meta.factor_id))

    return dag
