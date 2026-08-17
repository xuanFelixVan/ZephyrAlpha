# [BLUEPRINT] SH-MAIN-001 | docs/03_modules/_cross_layer/shared-core/governance_core_blueprint.md
# [MODULE] zephyr.shared.blueprint_tools.blueprint_decomposer
# [DOMAIN] D_SHARED
# [DEPENDENCIES] zephyr.shared.models; zephyr.shared.schema.task_types; zephyr.shared.__init__; zephyr.shared.schema.severity_types
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
# [A_module] module_id=MOD-INF-blueprint_decomposer | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

r"""


ZephyrAlpha 蓝图拆解器
=====================
依据：MOD-TASK_SYSTEM v0.3.0 §5 TaskCard 接口契约
输入：治理文档（KB 决策记录/TD/CS/CP 等 blueprint.yaml），可选 task_repo
输出：双向存储——SQLite（task_repo.create）+ ``docs_dir/decomposition/`` 下
``decomposition_result.json`` 及逐任务 ``tasks/{task_id}.md``（human companion）。

蓝图前缀 -> Task.namespace（task-card-standard / schemas.TaskNamespace）映射：
  ADR-* -> KBG     TD-* -> DW（技术债登记）
  CS-*  -> STD     CP-* -> CP
  INFRA-* / SCRIPT-* -> OPS（基础设施与脚本治理并入 OPS 序号空间）

task_id 真源：`schemas.Task` 要求 `^(KBG|CP|KE|STD|DW|SRC|OPS)-\d+$`

task_id 格式（§3.2.1）：{NAMESPACE}-{SEQ}（SQLite auto-increment 保证唯一性）

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 治理蓝图文件 Markdown文档
#   fields: YAML frontmatter（functional_domain/layer）+ 列表项（ADR/TD/CS/CP/INFRA/SCRIPT marker、模块名、描述、depends_on 行）
#   code: blueprint_path
# - id: I2
#   name: 任务仓库 task_repo 可选SQLite仓储
#   fields: next_seq(ns) 取号、create(task) 入库、transition 状态流转；为 None 时用内存序号
#   code: task_repo
# - id: I3
#   name: 文档输出目录 docs_dir 可选路径
#   fields: 指定时写 decomposition/decomposition_result.json 与 tasks/{task_id}.md
#   code: docs_dir
# 层: 算法
# - id: A1
#   name_zh: ① frontmatter解析与target_layer推断
#   name_en: _parse_frontmatter/_infer_target_layer
#   intro: 读蓝图头部 YAML，按功能域/架构层词表映射出 target_layer 域标识
#   desc: 解析 --- 包裹的 YAML frontmatter；先查 functional_domain→D_* 映射表（13 域），再查 layer=L0_infrastructure 特例，命中即得 target_layer，否则 None
#   inputs: I1
#   outputs: target_layer 字符串或 None
# - id: A2
#   name_zh: ② 列表项抽取与TaskCard构建
#   name_en: _extract_tasks/_build_task_card
#   intro: 逐行扫蓝图，用正则抓任务条目并组装成带命名空间序号的 TaskCard
#   desc: _ITEM_PATTERN/_UNIVERSAL_ITEM_PATTERN 匹配列表项得 marker+模块名+描述；marker→蓝图标签→TaskNamespace（ADR→KBG、TD→DW、CS→STD、INFRA/SCRIPT→OPS）；序号取 task_repo.next_seq 或内存自增；描述不足自动补齐根因/施工步骤/验收标准三段
#   inputs: I1 I2
#   outputs: TaskCard 列表 + unassigned + warnings
#   invariant: task_id 满足 ^(KBG|CP|KE|STD|DW|SRC|OPS)-\d+$
# - id: A3
#   name_zh: ③ 依赖解析与依赖图构建
#   name_en: _resolve_depends_on_ids/_build_dependency_graph/topology_sort
#   intro: 把 depends_on 里的标题别名解析成 task_id，再建图并可拓扑排序
#   desc: depends_on 条目依次按 task_id 精确、标题别名、TASK_ID_RE 正则解析；无显式依赖时默认串行依赖前一条；拓扑排序用 Kahn 入度法，检测到环则告警回退插入序
#   inputs: I1
#   outputs: dependency_graph 字典 / 排序后 TaskCard 列表
# - id: A4
#   name_zh: ④ 双向持久化入库与落盘
#   name_en: _write_tasks/_write_task_companion_md
#   intro: TaskCard 双向写入——SQLite 入库 + docs_dir 下 JSON/Markdown 同步产物
#   desc: task_repo.create 逐卡入库（ValueError 记为门禁拒绝 warning），无依赖卡自动 PENDING→READY；docs_dir 指定时写 decomposition_result.json 与逐任务 companion md（含 SSoT 警告头）
#   inputs: I2 I3
#   outputs: SQLite 任务记录 + decomposition 目录文件
# 层: 输出
# - id: O1
#   name_zh: 拆解结果 DecompositionResult
#   name_en: DecompositionResult
#   intro: 含 total_tasks/tasks/dependency_graph/unassigned_items/warnings 的拆解结果对象，decompose_blueprint 返回值
#   downstream: 无下游/内部使用
# - id: O2
#   name_zh: SQLite任务记录与companion文档
#   name_en: task_repo.create/decomposition_result.json
#   intro: 持久化产物——TaskRepository 库内任务卡（真源）与 docs_dir/decomposition/ 下 JSON 及逐任务 Markdown（human companion）
#   invariant: Markdown 仅为同步产物，真源为 SQLite DB
#   downstream: 无下游/内部使用
# [/ALGO_FLOW]
# 边:
# I1 --> A1
# I1 --> A2
# A1 --> A2
# I2 --> A2
# A2 --> A3
# A3 --> A4
# I2 --> A4
# I3 --> A4
# A2 --> O1
# A3 --> O1
# A4 --> O2
"""

from __future__ import annotations

import logging
import re
from datetime import UTC, datetime
from pathlib import Path

import yaml

from zephyr.shared.foundation.models import (
    DecompositionResult,
    GateLevel,
    TaskCard,
    TaskStatus,
)
from zephyr.shared.io.frontmatter_utils import parse_frontmatter_from_file
from zephyr.shared.schema.severity_types import Priority, SafetyLevel
from zephyr.shared.schema.task_types import ExecutionModel, TaskNamespace, TaskStatus

logger = logging.getLogger(__name__)

# 蓝图里出现的别名 -> schemas.TaskNamespace（合法 task_id 前缀）
_BLUEPRINT_LABEL_TO_NAMESPACE: dict[str, TaskNamespace] = {
    "CP": TaskNamespace.CP,
    "KE": TaskNamespace.KE,
    "STD": TaskNamespace.STD,
    "DW": TaskNamespace.DW,
    "SRC": TaskNamespace.SRC,
    "OPS": TaskNamespace.OPS,
    "KB 决策记录": TaskNamespace.KBG,
    "TD": TaskNamespace.DW,
    "TECH-DEBT": TaskNamespace.DW,
    "TECH_DEBT": TaskNamespace.DW,
    "CS": TaskNamespace.STD,
    "CODING-STANDARD": TaskNamespace.STD,
    "CODING_STANDARD": TaskNamespace.STD,
    "INFRA": TaskNamespace.OPS,
    "SCRIPT": TaskNamespace.OPS,
}

_ITEM_PATTERN = re.compile(
    r"[-*]\s+(?P<marker>"
    r"\[ADR-\d+-\d+\]|"
    r"TD-\d+|"
    r"CS-\d+|"
    r"CP-\d+|"
    r"INFRA-\d+|"
    r"SCRIPT-\d+"
    r")\s+\*\*(?P<module>[^*]+)\*\*\s*[—\-:]?\s*(?P<desc>.+?)(?:\s*$)",
)

_UNIVERSAL_ITEM_PATTERN = re.compile(
    r"^\s*\d+\.\s+\*\*(?P<module>[^*]+)\*\*\s*[—\-:]\s*(?P<desc>.+?)$",
)

_DEPENDS_LINE_PATTERN = re.compile(
    r"^\s*depends_on:\s*\[(.*?)\]\s*(?:#.*)?$",
    re.IGNORECASE,
)

_TASK_ID_RE = re.compile(r"^(KBG|CP|KE|STD|DW|SRC|OPS|DM)-\d+$")


def _split_desc_and_depends(desc_lines: list[str]) -> tuple[list[str], list[str]]:
    """从任务描述行中拆出叙事文本与 ``depends_on`` 列表。"""
    narrative: list[str] = []
    deps: list[str] = []
    for line in desc_lines:
        m = _DEPENDS_LINE_PATTERN.match(line.strip())
        if m:
            raw = m.group(1)
            for part in raw.split(","):
                part = part.strip().strip("\"'")
                if part:
                    deps.append(part)
            continue
        narrative.append(line)
    return narrative, deps


def _marker_to_blueprint_label(marker: str) -> str | None:
    """从列表行 marker 解析蓝图前缀标签（如 TD、KB 决策记录）。"""
    raw = marker.strip().strip("[]")
    if raw.startswith("ADR-"):
        return "KB 决策记录"
    if raw.startswith("TD-"):
        return "TD"
    if raw.startswith("CS-"):
        return "CS"
    if raw.startswith("CP-"):
        return "CP"
    if raw.startswith("INFRA-"):
        return "INFRA"
    if raw.startswith("SCRIPT-"):
        return "SCRIPT"
    return None


def _resolve_task_namespace(label: str) -> TaskNamespace | None:
    """将调用方或 marker 得出的标签解析为合法 TaskNamespace。"""
    key = label.upper().strip()
    if key in _BLUEPRINT_LABEL_TO_NAMESPACE:
        return _BLUEPRINT_LABEL_TO_NAMESPACE[key]
    norm = key.replace("-", "_")
    if norm in _BLUEPRINT_LABEL_TO_NAMESPACE:
        return _BLUEPRINT_LABEL_TO_NAMESPACE[norm]
    try:
        return TaskNamespace[key]
    except KeyError:
        return None


class BlueprintDecomposer:
    """
    治理文档 -> 逐条拆解 -> 生成 TaskCard 列表。

    每条列表项可从 marker 推断命名空间；否则使用 decompose_* 传入的 namespace。
    """

    def __init__(
        self,
        task_repo: object | None = None,
        docs_dir: str | None = None,
    ):
        self.task_repo = task_repo
        self.docs_dir = Path(docs_dir) if docs_dir else None
        self._global_seq: dict[str, int] = {}

    def next_global_seq(self, ns) -> int:
        """公共接口：next_global_seq（Stage 4 公共化）。"""
        return self._next_global_seq(ns)

    @property
    def global_seq(self) -> dict[str, int]:
        """只读：global_seq（Stage 4 公共化）。"""
        return self._global_seq

    @global_seq.setter
    def global_seq(self, value):
        """写入：global_seq（Stage 4 公共化）。"""
        self._global_seq = value

    # === target_layer 自动映射（对齐 target_layer_vocabulary.yaml v1.0.0）===

    # 功能域 -> 域标识符映射（基于 target_layer_vocabulary.yaml）
    _FUNC_DOMAIN_TO_TARGET_LAYER: dict[str, str] = {
        "data": "D_MKT_DATA",
        "factor": "D_FACTOR",
        "signal": "D_SIGLEGACY",
        "risk": "D_RISK",
        "backtest": "D_BACKTEST",
        "compliance": "D_GOV_ENFORCEMENT",
        "governance": "D_GOVERNANCE",
        "operations": "D_OPS",
        "intelligence": "D_INTELLIGENCE",
        "execution": "D_EX_CORE",
        "capacity": "D_INFRA_OPS",
        "infra": "D_INFRA_RUNTIME",
        "safety_escalation": "D_AUTONOMY_PERM",
    }

    # 架构层 -> 域标识符映射（仅 L0 有明确1:1映射，其他层不映射）
    # SSoT: layer_vocabulary.yaml — layer 合法值参考词表
    _LAYER_TO_TARGET_LAYER: dict[str, str] = {
        "L0_infrastructure": "D_INFRA_OPS",
    }

    def _parse_frontmatter(self, blueprint_path: str) -> dict:
        """解析蓝图文件的 YAML frontmatter（委托 SSoT frontmatter_utils）。"""
        try:
            return parse_frontmatter_from_file(blueprint_path) or {}
        except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
            return {}

    def _infer_target_layer(self, fm: dict) -> str | None:
        """从 frontmatter 推断 target_layer。

        优先级：functional_domain > layer（L0_infrastructure）
        对齐 target_layer_vocabulary.yaml v1.0.0
        """
        func_domain = str(fm.get("functional_domain", "")).strip().lower()
        if func_domain in self._FUNC_DOMAIN_TO_TARGET_LAYER:
            return self._FUNC_DOMAIN_TO_TARGET_LAYER[func_domain]

        layer = str(fm.get("layer", "")).strip()
        if layer in self._LAYER_TO_TARGET_LAYER:
            return self._LAYER_TO_TARGET_LAYER[layer]

        return None

    def decompose_blueprint(
        self,
        blueprint_path: str,
        namespace: str = "CP",
        phase: int = 1,
    ) -> DecompositionResult:
        """
        拆解单个蓝图文件 -> 生成 DecompositionResult。

        Args:
            blueprint_path: 蓝图文件路径
            namespace: 命名空间前缀（蓝图 marker 未识别时的默认值）
            phase: Phase 编号
        """
        path = Path(blueprint_path)
        if not path.exists():
            raise FileNotFoundError(f"蓝图文件不存在: {blueprint_path}")

        content = path.read_text(encoding="utf-8")

        # target_layer 自动映射：从 frontmatter 推断（对齐 target_layer_vocabulary.yaml v1.0.0）
        fm = self._parse_frontmatter(blueprint_path)
        target_layer = self._infer_target_layer(fm)

        tasks, unassigned, warnings = self._extract_tasks(content, blueprint_path, namespace, phase, target_layer)
        self._resolve_depends_on_ids(tasks)
        dep_graph = self._build_dependency_graph(tasks)

        result = DecompositionResult(
            total_tasks=len(tasks),
            tasks=tasks,
            dependency_graph=dep_graph,
            unassigned_items=unassigned,
            warnings=warnings,
        )

        self._write_tasks(result)

        return result

    def decompose_blueprints_batch(
        self,
        blueprint_paths: list[str],
        namespace: str = "OPS",
        phase: int = 1,
    ) -> list[DecompositionResult]:
        """
        批量拆解多个蓝图文件。

        默认 namespace 为 OPS（对应历史 INFRA/SCRIPT 批量拆解场景）；
        仍可通过参数传入 CP/KB 决策记录 等。
        """
        results: list[DecompositionResult] = []
        for bp_path in blueprint_paths:
            result = self.decompose_blueprint(bp_path, namespace, phase)
            results.append(result)
        return results

    def _next_global_seq(self, ns: TaskNamespace) -> int:
        key = ns.value
        self._global_seq[key] = self._global_seq.get(key, 0) + 1
        return self._global_seq[key]

    def _extract_tasks(
        self,
        content: str,
        blueprint_path: str,
        namespace: str,
        phase: int,
        target_layer: str | None = None,
    ) -> tuple[list[TaskCard], list[str], list[str]]:
        tasks: list[TaskCard] = []
        unassigned: list[str] = []
        warnings: list[str] = []

        lines = content.split("\n")
        task_name_buf: list[str] = []
        task_desc_buf: list[str] = []
        in_task = False
        task_namespace_label: str | None = None

        default_label = namespace.upper()

        for line in lines:
            item_match = _ITEM_PATTERN.match(line)
            if item_match:
                if in_task and task_name_buf:
                    label = task_namespace_label or default_label
                    desc_lines, dep_ids = _split_desc_and_depends(task_desc_buf)
                    task = self._build_task_card(
                        name=" ".join(task_name_buf),
                        description=" ".join(desc_lines),
                        blueprint_path=blueprint_path,
                        namespace_label=label,
                        phase=phase,
                        depends_on=dep_ids,
                        target_layer=target_layer,
                    )
                    if task:
                        tasks.append(task)
                    else:
                        warnings.append(f"无法解析任务: {task_name_buf}")

                in_task = True
                task_namespace_label = _marker_to_blueprint_label(item_match.group("marker"))
                task_name_buf = [item_match.group("module").strip()]
                task_desc_buf = [item_match.group("desc").strip()]
            elif in_task and line.strip():
                task_desc_buf.append(line.strip())

        if in_task and task_name_buf:
            label = task_namespace_label or default_label
            desc_lines, dep_ids = _split_desc_and_depends(task_desc_buf)
            task = self._build_task_card(
                name=" ".join(task_name_buf),
                description=" ".join(desc_lines),
                blueprint_path=blueprint_path,
                namespace_label=label,
                phase=phase,
                depends_on=dep_ids,
            )
            if task:
                tasks.append(task)
            else:
                unassigned.append(" ".join(task_name_buf))

        return tasks, unassigned, warnings

    def _build_task_card(
        self,
        name: str,
        description: str,
        blueprint_path: str,
        namespace_label: str,
        phase: int,
        depends_on: list[str] | None = None,
        target_layer: str | None = None,
    ) -> TaskCard | None:
        try:
            ns = _resolve_task_namespace(namespace_label)
            if ns is None:
                logger.warning("未知命名空间标签 %r，跳过 TaskCard", namespace_label)
                return None

            if self.task_repo:
                seq = self.task_repo.next_seq(ns)
            else:
                seq = self._next_global_seq(ns)

            task_id = f"{ns.value}-{seq}"

            bp_module_id = Path(blueprint_path).stem
            now = datetime.now(UTC)

            desc = description.strip()
            if len(desc) < 10:
                desc = desc + "（蓝图条目摘要不足十字由拆解器补齐）"
            if "根因" not in desc:
                desc = f"根因：蓝图 {bp_module_id} 要求实现 {name}。治根：按蓝图规格实现。{desc}"
            if "施工步骤" not in desc:
                desc = desc + f" 施工步骤：(1) 按蓝图 {bp_module_id} §auto-extracted 实现 {name}。"
            if "验收标准" not in desc:
                desc = desc + f" 验收标准：{name} 的产出物存在且符合蓝图描述。"

            return TaskCard(
                task_id=task_id,
                namespace=ns,
                seq=seq,
                title=name[:200],
                status=TaskStatus.PENDING,
                priority=Priority.P2,
                phase=phase,
                execution_model=ExecutionModel.deepseek,
                safety_level=SafetyLevel.L,
                source_blueprint=bp_module_id,
                source_section="auto-extracted",
                description=desc,
                files_in_scope=[blueprint_path],
                deliverables=[f"{name} 完成"],
                acceptance=[f"验证 {name} 的产出物存在且符合描述"],
                upstream_files=[blueprint_path],
                downstream_outputs=[],
                allowed_touch=[blueprint_path],
                forbidden_touch=[],
                applicable_rules=[
                    {
                        "module_id": "MOD-TASK_SYSTEM",
                        "section": "§3.2.1",
                        "reason": "TaskCard Schema——任务格式合规",
                    }
                ],
                context_assembly_manifest=[
                    {
                        "file_path": blueprint_path,
                        "reason": "源蓝图",
                    }
                ],
                rollback_instructions="git checkout -- <modified_files>",
                post_sync_standard=["python scripts/governance/d11_compliance/audit_registration.py --warn-only"],
                dependency_type="soft",
                estimated_tokens=4000,
                timeout_minutes=30,
                completed_gates=[],
                blocked_gates={},
                assigned_pipeline="A",
                pipeline_modules=[],
                blocked_by=[],
                artifact_paths=[],
                audit_findings=[],
                ke_entries=[],
                tags=[f"blueprint:{namespace_label.upper()}"],
                depends_on=list(depends_on) if depends_on else [],
                ai_autonomy_level="supervised",
                autonomy_checklist=[],
                construction_status="pending",
                verification_status="unverified",
                pipeline_task_type="CODE_GEN",  # 蓝图拆解默认为代码生成
                target_layer=target_layer,
                created_at=now,
                updated_at=now,
            )
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            logger.warning(f"TaskCard 构造失败: {name} — {e}", exc_info=True)
            return None

    def _resolve_depends_on_ids(self, tasks: list[TaskCard]) -> None:
        """将 ``depends_on`` 中的标题别名解析为 ``task_id``（若可解析）。"""
        title_to_id = {t.title: t.task_id for t in tasks}
        id_set = {t.task_id for t in tasks}
        for t in tasks:
            resolved: list[str] = []
            for dep in t.depends_on:
                s = dep.strip()
                if s in id_set:
                    resolved.append(s)
                elif s in title_to_id:
                    resolved.append(title_to_id[s])
                elif _TASK_ID_RE.match(s):
                    resolved.append(s)
            t.depends_on = list(dict.fromkeys(resolved))

    def _build_dependency_graph(self, tasks: list[TaskCard]) -> dict[str, list[str]]:
        graph: dict[str, list[str]] = {}
        for i, task in enumerate(tasks):
            explicit = list(dict.fromkeys(task.depends_on))
            if explicit:
                graph[task.task_id] = explicit
            elif i > 0:
                graph[task.task_id] = [tasks[i - 1].task_id]
            else:
                graph[task.task_id] = []
        return graph

    def topology_sort(self, tasks: list[TaskCard]) -> list[TaskCard]:
        """拓扑排序——按 depends_on 关系确保父任务在子任务之前。

        循环依赖通过回边检测并报告为 warning。
        """
        adj: dict[str, list[str]] = {}
        in_degree: dict[str, int] = {}
        task_map: dict[str, TaskCard] = {}

        for t in tasks:
            adj[t.task_id] = []
            in_degree[t.task_id] = 0
            task_map[t.task_id] = t

        for t in tasks:
            for dep_id in t.depends_on:
                if dep_id in task_map:
                    adj[dep_id].append(t.task_id)
                    in_degree[t.task_id] += 1

        queue = [tid for tid, deg in in_degree.items() if deg == 0]
        sorted_ids: list[str] = []

        while queue:
            tid = queue.pop(0)
            sorted_ids.append(tid)
            for child_id in adj.get(tid, []):
                in_degree[child_id] -= 1
                if in_degree[child_id] == 0:
                    queue.append(child_id)

        if len(sorted_ids) != len(tasks):
            logger.warning(
                "Cyclic dependency detected in %d tasks; falling back to insertion order",
                len(tasks) - len(sorted_ids),
            )
            return list(tasks)

        return [task_map[tid] for tid in sorted_ids]

    def extract_depends_from_content(self, content: str) -> dict[str, list[str]]:
        """从蓝图内容中提取 ``depends_on``，锚定为紧前一条列表项的 **module** 标题。

        返回 ``{ 列表项标题: [依赖项, ...] }``；依赖项可为 ``task_id`` 或尚未解析的标题。
        """
        result: dict[str, list[str]] = {}
        current_title: str | None = None
        for line in content.split("\n"):
            im = _ITEM_PATTERN.match(line)
            if im:
                current_title = im.group("module").strip()
                continue
            um = _UNIVERSAL_ITEM_PATTERN.match(line)
            if um:
                current_title = um.group("module").strip()
                continue
            m = _DEPENDS_LINE_PATTERN.match(line.strip())
            if m and current_title:
                raw = m.group(1)
                deps = [d.strip().strip("\"'") for d in raw.split(",") if d.strip()]
                if deps:
                    result[current_title] = deps
        return result

    def _write_tasks(self, result: DecompositionResult) -> None:
        if self.task_repo:
            failed_ids: list[str] = []
            for task in result.tasks:
                try:
                    self.task_repo.create(task)
                except ValueError as e:
                    logger.error(f"task_repo.create 粒度/模板校验失败: {task.task_id} — {e}")
                    failed_ids.append(task.task_id)
                    result.warnings.append(f"TaskCard {task.task_id} 被门禁拒绝: {e}")
                    continue
                except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                    logger.error(f"task_repo.create 失败: {task.task_id} — {e}", exc_info=True)
                    failed_ids.append(task.task_id)
                    result.warnings.append(f"TaskCard {task.task_id} 入库失败: {e}")
                    continue
                if not task.depends_on:
                    try:
                        self.task_repo.transition(task.task_id, TaskStatus.READY)
                        task.status = TaskStatus.READY
                    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                        logger.warning(f"PENDING->READY 转换失败: {task.task_id} — {e}", exc_info=True)
            if failed_ids:
                logger.warning(f"共 {len(failed_ids)} 张卡入库失败: {failed_ids}")

        if self.docs_dir:
            out_dir = self.docs_dir / "decomposition"
            out_dir.mkdir(parents=True, exist_ok=True)
            out_path = out_dir / "decomposition_result.json"
            out_path.write_text(
                result.model_dump_json(indent=2),
                encoding="utf-8",
            )
            tasks_dir = out_dir / "tasks"
            tasks_dir.mkdir(parents=True, exist_ok=True)
            for task in result.tasks:
                self._write_task_companion_md(task, tasks_dir)

    def _write_task_companion_md(self, task: TaskCard, md_dir: Path) -> None:
        """每张 TaskCard 写一个可读 companion Markdown（frontmatter + 正文摘要）。"""
        safe_id = task.task_id.replace("/", "_").replace("\\", "_")
        path = md_dir / f"{safe_id}.md"
        fm = {
            "task_id": task.task_id,
            "title": task.title,
            "namespace": task.namespace.value if hasattr(task.namespace, "value") else str(task.namespace),
            "status": task.status.value if hasattr(task.status, "value") else str(task.status),
            "priority": task.priority.value if hasattr(task.priority, "value") else str(task.priority),
            "source_blueprint": task.source_blueprint,
            "source_section": task.source_section,
            "phase": task.phase,
            "ssot_warning": "本文件是 TaskRepository 的 human companion，真源为 SQLite DB，禁止以此文件内容为准做决策，查询请用 TaskRepository.get(task_id)",
        }
        header = yaml.safe_dump(fm, allow_unicode=True, sort_keys=False)
        warning_banner = (
            "> ⚠ **SSoT 警告**：本文件是 TaskRepository 的 human companion（同步产物），"
            "真源为 SQLite DB。禁止以本文件内容为准做决策（status/blocked_by 等可能过期）。"
            "查询任务真源请用 `TaskRepository.get(task_id)` 或 MCP `task_manager.get_task`。\n\n"
        )
        body = f"\n## Description\n\n{task.description}\n"
        path.write_text(f"---\n{header}---\n\n{warning_banner}{body}", encoding="utf-8")

    def check_gate(self, gate_id: GateLevel, task: TaskCard) -> bool:
        if gate_id is GateLevel.G0:
            return bool(
                task.source_blueprint
                and task.description
                and len(task.description.strip()) >= 10
                and task.priority is not None
            )
        if gate_id is GateLevel.G7:
            return task.verification_status == "verified" and all(f.resolved for f in task.audit_findings)
        return True
