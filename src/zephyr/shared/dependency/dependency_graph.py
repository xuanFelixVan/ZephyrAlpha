# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/governance_core_blueprint.md
# [MODULE] zephyr.shared.dependency.dependency_graph
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-016 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""


Dependency Graph — 任务卡依赖关系管理。

依据：
    蓝图 MOD-TASK_SYSTEM §5 依赖项 + v0.6.0
    任务卡 TASK-INF-0107

功能：
    - depends_on/blocked_by 格式校验
    - 环检测（DFS cycle detection）
    - 依赖浅深分析 + 硬杀伤链构建

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 任务依赖声明 字符串列表
#   fields: task_id 加 depends_on/block blocked_by 任务ID列表，add_node 注册入图
#   code: add_node(task_id, depends_on, blocked_by) L77
# - id: I2
#   name: 任务卡字典 task_card dict
#   fields: 含 task_id/depends_on/blocked_by 键，供格式合法性校验
#   code: validate_task_deps(task_card) L146
# 层: 算法
# - id: A1
#   name_zh: ① 节点注册与传递依赖解析
#   name_en: add_node/_resolve_all_deps
#   intro: 把任务及其直接依赖注册进图，并递归算出全部传递依赖集合
#   desc: 按 task_id 建/取 DependencyNode 写入 depends_on、blocked_by；_resolve_all_deps 带 visited 防重递归遍历 depends_on，all_deps 集合递归并集后 sorted，回填 node.all_dependencies
#   inputs: I1
#   outputs: DependencyNode（含 all_dependencies）
# - id: A2
#   name_zh: ② DFS环检测
#   name_en: detect_cycles
#   intro: 用访问集加栈内集双标记的深度搜索找依赖环并记录环路径
#   desc: visited/in_stack/path 三态 DFS：命中 in_stack 即回边，path.index(tid) 起截环生成 CycleDetection(cycle_path+message)；全图逐未访节点起跑
#   inputs: I1
#   outputs: list[CycleDetection]
#   invariant: 环路径首尾同节点，如 A -> B -> A
# - id: A3
#   name_zh: ③ 硬杀伤链构建
#   name_en: build_kill_chain/_depth_first_path
#   intro: 从某任务出发深搜依赖链，输出链深与直接/传递依赖计数
#   desc: _depth_first_path 递归拼去重依赖路径；KillChain(task_id, chain_depth=len(path)-1, chain_path, direct_deps=len(depends_on), transitive_deps=len(全量依赖))
#   inputs: I1
#   outputs: KillChain 或 None
# - id: A4
#   name_zh: ④ 依赖格式校验
#   name_en: validate_task_deps
#   intro: 校验任务卡 depends_on/blocked_by 必须是列表、无自依赖、两表不冲突
#   desc: isinstance 校验两者皆 list；任一 ID 等于 task_id 判自依赖失败；同 ID 同现 depends_on 与 blocked_by 判冲突失败；否则返回 (True, "Dependencies valid")
#   inputs: I2
#   outputs: (bool, 校验消息)
# 层: 输出
# - id: O1
#   name_zh: 环检测报告
#   name_en: list[CycleDetection]
#   intro: 全图环检测结果列表，每项含 has_cycle/cycle_path/可读 message
#   downstream: 无下游/内部使用
# - id: O2
#   name_zh: 杀伤链与校验结论
#   name_en: KillChain/tuple[bool,str]
#   intro: 单任务依赖链深度报告（build_kill_chain）与任务卡依赖合法性结论（validate_task_deps）
#   downstream: 无下游/内部使用
# [/ALGO_FLOW]
# 边:
# I1 --> A1
# I1 --> A2
# A1 --> A3
# I1 --> A3
# I2 --> A4
# A2 --> O1
# A3 --> O2
# A4 --> O2
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class DependencyNode:
    task_id: str
    depends_on: list[str] = field(default_factory=list)
    blocked_by: list[str] = field(default_factory=list)
    all_dependencies: list[str] = field(default_factory=list)


@dataclass
class CycleDetection:
    has_cycle: bool
    cycle_path: list[str]
    message: str = ""


@dataclass
class KillChain:
    task_id: str
    chain_depth: int
    chain_path: list[str]
    direct_deps: int
    transitive_deps: int


class DependencyGraph:
    def __init__(self) -> None:
        self._nodes: dict[str, DependencyNode] = {}

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def nodes(self) -> dict[str, DependencyNode]:
        """只读：nodes（Stage 4 公共化）。"""
        return self._nodes

    @nodes.setter
    def nodes(self, value):
        """写入：nodes（Stage 4 公共化）。"""
        self._nodes = value

    def add_node(
        self, task_id: str, depends_on: list[str] | None = None, blocked_by: list[str] | None = None
    ) -> DependencyNode:
        if task_id not in self._nodes:
            self._nodes[task_id] = DependencyNode(task_id=task_id)

        node = self._nodes[task_id]
        if depends_on is not None:
            node.depends_on = list(depends_on)
        if blocked_by is not None:
            node.blocked_by = list(blocked_by)

        node.all_dependencies = self._resolve_all_deps(task_id)

        return node

    def detect_cycles(self) -> list[CycleDetection]:
        cycles: list[CycleDetection] = []
        visited: set[str] = set()
        in_stack: set[str] = set()
        path: list[str] = []

        def dfs(tid: str) -> None:
            if tid in in_stack:
                cycle_start = path.index(tid)
                cycles.append(
                    CycleDetection(
                        has_cycle=True,
                        cycle_path=path[cycle_start:] + [tid],
                        message=f"Dependency cycle detected: {' -> '.join(path[cycle_start:] + [tid])}",
                    )
                )
                return

            if tid in visited or tid not in self._nodes:
                return

            visited.add(tid)
            in_stack.add(tid)
            path.append(tid)

            for dep in self._nodes[tid].depends_on:
                dfs(dep)

            path.pop()
            in_stack.discard(tid)

        for tid in self._nodes:
            if tid not in visited:
                dfs(tid)

        return cycles

    def build_kill_chain(self, task_id: str) -> KillChain | None:
        if task_id not in self._nodes:
            return None

        node = self._nodes[task_id]
        all_deps = self._resolve_all_deps(task_id)
        chain_path = self._depth_first_path(task_id)

        return KillChain(
            task_id=task_id,
            chain_depth=len(chain_path) - 1,
            chain_path=chain_path,
            direct_deps=len(node.depends_on),
            transitive_deps=len(all_deps),
        )

    def validate_task_deps(self, task_card: dict[str, Any]) -> tuple[bool, str]:
        depends_on = task_card.get("depends_on", [])
        blocked_by = task_card.get("blocked_by", [])

        if not isinstance(depends_on, list) or not isinstance(blocked_by, list):
            return False, "depends_on and blocked_by must be lists"

        all_ids = set(depends_on + blocked_by)
        for tid in all_ids:
            if tid == task_card.get("task_id"):
                return False, f"Self-dependency detected: {tid}"
            if tid in depends_on and tid in blocked_by:
                return False, f"Conflicting dependency: {tid} in both depends_on and blocked_by"

        return True, "Dependencies valid"

    def _resolve_all_deps(self, task_id: str, visited: set[str] | None = None) -> list[str]:
        if visited is None:
            visited = set()

        if task_id in visited or task_id not in self._nodes:
            return []

        visited.add(task_id)
        all_deps: set[str] = set()

        for dep in self._nodes[task_id].depends_on:
            all_deps.add(dep)
            all_deps.update(self._resolve_all_deps(dep, visited))

        return sorted(all_deps)

    def _depth_first_path(self, task_id: str) -> list[str]:
        node = self._nodes.get(task_id)
        if node is None:
            return [task_id]

        path = [task_id]
        for dep in node.depends_on:
            sub_path = self._depth_first_path(dep)
            for item in sub_path:
                if item not in path:
                    path.append(item)
        return path
