# [BLUEPRINT] MOD-INF-028 | docs/03_modules/_cross_layer/semantic_auditor/blueprint.md | §3.1 Stage 9
# [MODULE] zephyr.governance.resilience_governance.blast_radius
# [DOMAIN] D_GOV_OPS_RESILIENCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] fix_prioritizer.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] depgraph_path必须指向合法YAML; max_depth>=1; analyze输入finding.source_location非空时才计算文件级影响
# [MODIFY-GUARD] blueprint.md §3.1 Stage 9; semantic-auditor/__init__.py __all__
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DepgraphLoadError on invalid YAML; ValueError on max_depth<1
# [TESTS] tests/semantic-auditor/test_blast_radius.py
# [A_module] module_id=MOD-INF-028 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""


blast_radius — MOD-INF-028 §3.1 Stage 9
========================================
影响爆炸半径分析器：基于 depgraph 计算修复操作的影响范围。

核心能力:
- 直接依赖数: 修改目标文件后，直接 import 它的文件数量
- 传递依赖数: 沿依赖链逐层传播后，所有受影响的文件数量
- 受影响文件列表: 完整的下游消费者路径清单
- 级联深度: 最长传播链的深度

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: depgraph 依赖图 YAML文件
#   fields: nodes 字典（每节点 path + imports 列表）
#   code: depgraph_path 参数 L116 / _load_depgraph L163
# - id: I2
#   name: 语义审计发现 数据对象
#   fields: finding_id + source_location（含文件路径）+ module
#   code: SemanticAuditFinding analyze(finding) L279
# - id: I3
#   name: 最大搜索深度 配置参数
#   fields: max_depth 传递依赖 BFS 层数上限
#   code: max_depth=5 L117
# - id: I4
#   name: 优先级修复结果 列表数据
#   fields: PrioritizedFixResult 列表（.fix.finding 链式属性）
#   code: integrate_with_pipeline L361
# 层: 算法
# - id: A1
#   name_zh: ① depgraph 加载与反向索引构建
#   name_en: _load_depgraph
#   intro: 读 depgraph YAML，把"谁 import 谁"翻转成"谁被谁 import"的反向索引
#   desc: yaml.safe_load → 校验 nodes 键 → 逐节点建 path_to_id/id_to_path；按 imports 累成 _reverse_deps（模块→引用它的文件列表）；YAML 非法/缺 nodes 抛 DepgraphLoadError
#   inputs: I1
#   outputs: 反向依赖索引 + 路径映射
#   invariant: depgraph_path 必传，无默认路径（防路径污染）；延迟加载只建一次
# - id: A2
#   name_zh: ② 源文件路径解析
#   name_en: _resolve_source_path
#   intro: 从审计发现的 source_location 文本里抠出真正的文件路径
#   desc: source_location 按空白拆词，取第一个含 / 或 \\ 或以 .py 结尾的词，统一成正斜杠；抠不出返回空串（analyze 直接给 LOW 空报告）
#   inputs: I2
#   outputs: source_path（可能为空）
# - id: A3
#   name_zh: ③ 直接依赖查找
#   name_en: _find_direct_dependents
#   intro: 查反向索引，找出直接 import 源文件的下游文件清单
#   desc: source_path→node_id→模块路径（剥 src/ 前缀、去 .py、/转点）→ _reverse_deps 查；查不到再用推断模块路径兜底；dict.fromkeys 去重保序
#   inputs: A1 A2
#   outputs: 直接下游文件列表
# - id: A4
#   name_zh: ④ BFS 传递依赖扩散
#   name_en: _find_transitive_dependents
#   intro: 从源文件出发一层层往外扩，算所有被波及的文件和最长传播链深度
#   desc: BFS 逐层扩 reverse_deps，visited 集合防环；depth 1..max_depth，无新节点即停；返回全部受影响文件 + max_reached_depth
#   inputs: A3 I3
#   outputs: affected_files + cascade_depth
#   invariant: max_depth>=1
# - id: A5
#   name_zh: ⑤ 风险等级判定
#   name_en: _compute_risk_level
#   intro: 按波及面大小和链条长短给修复操作定四档风险
#   desc: transitive>=20 或 depth>=4→CRITICAL；>=10 或 >=3→HIGH；>=3 或 >=2→MEDIUM；其余 LOW
#   inputs: A4
#   outputs: risk_level LOW/MEDIUM/HIGH/CRITICAL
# - id: A6
#   name_zh: ⑥ Stage9 管道集成
#   name_en: integrate_with_pipeline
#   intro: 接 FixPrioritizer 的输出列表，逐个解包 finding 做爆炸半径分析
#   desc: 逐 pf 取 .fix.finding（SemanticAuditFinding 才收）→ analyze → 汇总报告列表
#   inputs: I4 A2
#   outputs: BlastRadiusReport 列表
# 层: 输出
# - id: O1
#   name_zh: 爆炸半径分析报告
#   name_en: BlastRadiusReport
#   intro: 直接/传递依赖数 + 受影响文件清单 + 级联深度 + 四档风险等级
#   downstream: fix_prioritizer.py（[CONSUMERS]）
# - id: O2
#   name_zh: 批量爆炸半径报告
#   name_en: list[BlastRadiusReport]
#   intro: 与输入发现一一对应的报告列表，供修复排序参考波及面
#   downstream: fix_prioritizer.py / Stage 9 管道
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A2
# A1 --> A3
# A2 --> A3
# A3 --> A4
# I3 --> A4
# A4 --> A5
# I4 --> A6
# A6 --> A2
# A5 --> O1
# A6 --> O2
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from zephyr.governance.semantic_audit.models import SemanticAuditFinding
from zephyr.shared.io.paths import REPO_ROOT  # 仓库根真源（SSoT：zephyr.shared.io.paths）

__all__ = ["BlastRadiusAnalyzer", "BlastRadiusReport"]

logger = logging.getLogger(__name__)

# 治本（2026-06-27）：删除 _DEPGRAPH_DEFAULT_PATH 常量（路径污染源）。
# blast_radius 读取的是 depgraph YAML 文件（非 SQLite/PG），调用方必须显式传入 depgraph_path。
# 历史默认指向 depgraph.db 是 latent bug（db 文件不能用 yaml.safe_load 读取）。


class DepgraphLoadError(RuntimeError):
    """depgraph YAML 加载或结构校验失败."""

    error_code = "ZA-GV-0037"

    def __init__(self, *args, error_code: str | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        if error_code is not None:
            self.error_code = error_code


@dataclass
class BlastRadiusReport:
    """爆炸半径分析报告 — 蓝图 §3.1 Stage 9 产出.

    字段:
    - finding_id: 原始审计发现 ID
    - source_path: 被修复的源文件路径
    - direct_dependents: 直接依赖该文件的下游数量
    - transitive_dependents: 传递依赖链上的下游总数量（含直接）
    - affected_files: 所有受影响文件的路径列表
    - cascade_depth: 最长传播链深度（0=无下游, 1=仅直接下游）
    - risk_level: 风险等级 LOW/MEDIUM/HIGH/CRITICAL
    """

    finding_id: str = ""
    source_path: str = ""
    direct_dependents: int = 0
    transitive_dependents: int = 0
    affected_files: list[str] = field(default_factory=list)
    cascade_depth: int = 0
    risk_level: str = "LOW"


def _compute_risk_level(transitive: int, depth: int) -> str:
    """根据传递依赖数和级联深度判定风险等级.

    判定规则:
    - transitive >= 20 或 depth >= 4 -> CRITICAL
    - transitive >= 10 或 depth >= 3 -> HIGH
    - transitive >= 3  或 depth >= 2 -> MEDIUM
    - 其余 -> LOW
    """
    if transitive >= 20 or depth >= 4:
        return "CRITICAL"
    if transitive >= 10 or depth >= 3:
        return "HIGH"
    if transitive >= 3 or depth >= 2:
        return "MEDIUM"
    return "LOW"


class BlastRadiusAnalyzer:
    """爆炸半径分析器 — 蓝图 §3.1 Stage 9.

    基于 depgraph 构建反向依赖索引，
    对给定 SemanticAuditFinding 计算修复操作的影响范围。

    用法:
        analyzer = BlastRadiusAnalyzer()
        report = analyzer.analyze(finding)
        print(report.transitive_dependents, report.risk_level)
    """

    def __init__(
        self,
        depgraph_path: Path | str | None = None,
        max_depth: int = 5,
    ) -> None:
        """初始化分析器.

        Args:
            depgraph_path: depgraph YAML 文件路径。必传（治本2026-06-27：删除默认路径常量，
                防止路径污染）。调用方应从 extract_depgraph.py 导出 YAML 后传入。
            max_depth: 传递依赖最大搜索深度，必须 >= 1。

        Raises:
            ValueError: max_depth < 1 或 depgraph_path 为 None 时抛出。
            DepgraphLoadError: depgraph 文件不存在或格式无效时抛出。
        """
        if max_depth < 1:
            raise ValueError(f"max_depth 必须 >= 1，实际为 {max_depth}")
        if depgraph_path is None:
            raise ValueError(
                "depgraph_path 必须显式传入（治本2026-06-27：删除默认路径常量防止污染）。"
                "请从 extract_depgraph.py 导出 YAML 后传入。"
            )
        self._depgraph_path = Path(depgraph_path)
        self._max_depth = max_depth
        self._reverse_deps: dict[str, list[str]] = {}
        self._path_to_id: dict[str, str] = {}
        self._id_to_path: dict[str, str] = {}
        self._loaded = False

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def max_depth(self):
        """只读：max_depth（Stage 4 公共化）。"""
        return self._max_depth

    @max_depth.setter
    def max_depth(self, value):
        """写入：max_depth（Stage 4 公共化）。"""
        self._max_depth = value

    def _ensure_loaded(self) -> None:
        """延迟加载 depgraph 并构建反向依赖索引."""
        if self._loaded:
            return
        self._load_depgraph()
        self._loaded = True

    def _load_depgraph(self) -> None:
        """加载 depgraph YAML 并构建索引."""
        if not self._depgraph_path.exists():
            raise DepgraphLoadError(f"depgraph not found: {self._depgraph_path}")
        try:
            with open(self._depgraph_path, encoding="utf-8") as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as exc:
            raise DepgraphLoadError(f"invalid YAML: {exc}") from exc

        if not isinstance(data, dict) or "nodes" not in data:
            raise DepgraphLoadError("depgraph missing 'nodes' key")

        nodes: dict[str, Any] = data.get("nodes", {})
        self._reverse_deps.clear()
        self._path_to_id.clear()
        self._id_to_path.clear()

        for node_id, node_info in nodes.items():
            if not isinstance(node_info, dict):
                continue
            node_path = node_info.get("path", "")
            if not node_path:
                continue
            normalized = node_path.replace("\\", "/")
            self._path_to_id[normalized] = node_id
            self._id_to_path[node_id] = normalized

            imports: list[str] = node_info.get("imports", [])
            for imp in imports:
                if imp not in self._reverse_deps:
                    self._reverse_deps[imp] = []
                self._reverse_deps[imp].append(normalized)

    def _resolve_source_path(self, finding: SemanticAuditFinding) -> str:
        """从 finding 中解析源文件路径.

        优先使用 source_location 中的路径部分，
        回退到 finding.module 转换的模块路径。
        """
        loc = finding.source_location.strip()
        if loc:
            parts = loc.split()
            for part in parts:
                if "/" in part or "\\" in part or part.endswith(".py"):
                    return part.replace("\\", "/")
        return ""

    def _find_direct_dependents(self, source_path: str) -> list[str]:
        """查找直接依赖 source_path 的文件列表.

        通过反向依赖索引查找: 哪些文件的 imports 列表包含该路径对应的模块。
        """
        self._ensure_loaded()
        direct: list[str] = []

        node_id = self._path_to_id.get(source_path)
        if node_id:
            module_path = self._module_path_from_file(source_path)
            dependents = self._reverse_deps.get(module_path, [])
            direct.extend(dependents)

        if not direct:
            module_path = self._infer_module_path(source_path)
            if module_path:
                dependents = self._reverse_deps.get(module_path, [])
                direct.extend(dependents)

        return list(dict.fromkeys(direct))

    def _module_path_from_file(self, file_path: str) -> str:
        """将文件路径转换为 Python 模块路径.

        例: src/zephyr/semantic-auditor/models.py -> zephyr.governance.semantic_audit.models
        """
        normalized = file_path.replace("\\", "/")
        if normalized.startswith("src/"):
            normalized = normalized[len("src/") :]
        if normalized.endswith(".py"):
            normalized = normalized[: -len(".py")]
        if normalized.endswith("/__init__"):
            normalized = normalized[: -len("/__init__")]
        return normalized.replace("/", ".")

    def _infer_module_path(self, file_path: str) -> str:
        """从文件路径推断模块路径（与 _module_path_from_file 相同逻辑）."""
        return self._module_path_from_file(file_path)

    def _find_transitive_dependents(self, source_path: str) -> tuple[list[str], int]:
        """BFS 查找传递依赖，返回 (所有受影响文件, 最长链深度).

        从 source_path 出发，逐层扩展反向依赖，
        直到无新节点或达到 max_depth。
        """
        self._ensure_loaded()
        visited: set[str] = {source_path}
        all_affected: list[str] = []
        current_layer: list[str] = [source_path]
        max_reached_depth = 0

        for depth in range(1, self._max_depth + 1):
            next_layer: list[str] = []
            for node in current_layer:
                dependents = self._find_direct_dependents(node)
                for dep in dependents:
                    if dep not in visited:
                        visited.add(dep)
                        all_affected.append(dep)
                        next_layer.append(dep)
            if not next_layer:
                break
            max_reached_depth = depth
            current_layer = next_layer

        return all_affected, max_reached_depth

    def analyze(self, finding: SemanticAuditFinding) -> BlastRadiusReport:
        """分析单个审计发现的爆炸半径.

        Args:
            finding: 语义审计发现，source_location 或 module 用于定位源文件。

        Returns:
            BlastRadiusReport 含直接/传递依赖数、受影响文件、风险等级。
        """
        self._ensure_loaded()

        source_path = self._resolve_source_path(finding)

        if not source_path:
            return BlastRadiusReport(
                finding_id=finding.finding_id,
                source_path="",
                direct_dependents=0,
                transitive_dependents=0,
                affected_files=[],
                cascade_depth=0,
                risk_level="LOW",
            )

        direct = self._find_direct_dependents(source_path)
        transitive, cascade_depth = self._find_transitive_dependents(source_path)

        risk = _compute_risk_level(len(transitive), cascade_depth)

        return BlastRadiusReport(
            finding_id=finding.finding_id,
            source_path=source_path,
            direct_dependents=len(direct),
            transitive_dependents=len(transitive),
            affected_files=transitive,
            cascade_depth=cascade_depth,
            risk_level=risk,
        )

    def analyze_batch(self, findings: list[SemanticAuditFinding]) -> list[BlastRadiusReport]:
        """批量分析多个审计发现的爆炸半径.

        Args:
            findings: 审计发现列表。

        Returns:
            对应的 BlastRadiusReport 列表。
        """
        return [self.analyze(f) for f in findings]

    def get_dependency_chain(self, source_path: str, max_depth: int | None = None) -> dict[str, list[str]]:
        """获取指定文件的逐层依赖链.

        Args:
            source_path: 源文件路径。
            max_depth: 最大深度，None 使用实例默认值。

        Returns:
            字典: depth(0-based) -> 该层依赖文件列表。
        """
        self._ensure_loaded()
        effective_depth = max_depth if max_depth is not None else self._max_depth

        chain: dict[str, list[str]] = {}
        visited: set[str] = {source_path}
        current_layer: list[str] = [source_path]

        for depth in range(effective_depth):
            next_layer: list[str] = []
            for node in current_layer:
                dependents = self._find_direct_dependents(node)
                for dep in dependents:
                    if dep not in visited:
                        visited.add(dep)
                        next_layer.append(dep)
            if not next_layer:
                break
            chain[str(depth + 1)] = next_layer
            current_layer = next_layer

        return chain

    def integrate_with_pipeline(
        self,
        prioritized_fixes: list[Any],
    ) -> list[BlastRadiusReport]:
        """Stage 9 管道集成入口 — 接受 PrioritizedFixResult 列表.

        对每个 PrioritizedFixResult 中的 finding 执行爆炸半径分析，
        返回对应的 BlastRadiusReport 列表。

        Args:
            prioritized_fixes: FixPrioritizer.prioritize() 的输出列表。
                每项须有 .fix.finding 属性（FixResult -> SemanticAuditFinding）。

        Returns:
            BlastRadiusReport 列表，与输入一一对应。
        """
        if not prioritized_fixes:
            return []
        reports: list[BlastRadiusReport] = []
        for pf in prioritized_fixes:
            finding = getattr(pf, "fix", None)
            if finding is None:
                continue
            inner_finding = getattr(finding, "finding", None)
            if inner_finding is not None and isinstance(inner_finding, SemanticAuditFinding):
                reports.append(self.analyze(inner_finding))
            elif isinstance(finding, SemanticAuditFinding):
                reports.append(self.analyze(finding))
        return reports
