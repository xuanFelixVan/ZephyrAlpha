# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md
# [MODULE] MOD-INF-035 | src/zephyr/trading/action_dispatcher | 动作分发器包（外观 + 4 个提取类）
# [DOMAIN] D_TRADING | trading
# [CAPABILITY] action_dispatcher_system
# [SAFETY] M
# [A_module] module_id=MOD-INF-035 | layer=module | stability=stable | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
# [CREATED] 2026-05-04
# [UPDATED] 2026-07-20 | Task 5.150.7: God Class 拆分 — ActionDispatcher 分解为 1 外观 + 4 worker
# [CONSUMERS] orchestrator.py | task_worker.py | test_action_dispatcher.py
# [STABILITY] stable
"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: TaskCard 已完成任务
#   fields: capability / result / payload.text（经 TaskScheduler 完成队列）
#   code: dispatch L335 / drain_results L373
# - id: I2
#   name: 4 个 worker 提取类
#   fields: SearchReplaceEngine / FileLifecycleManager / AnnotationWriter / AuditLogWriter
#   code: import L289-292
# 层: 算法
# - id: A1
#   name_zh: ① capability 路由分发
#   name_en: ActionDispatcher.dispatch
#   intro: 按 capability 把推理结果路由到对应执行器回写源文件
#   desc: 9 种 capability → annotate_py_file/tag_module/annotate_blueprint/search_replace_file/create_file/write_triage_log；空 result 或无执行器 → _skip；异常 → error 报告
#   inputs: I1 I2
#   outputs: ActionReport
#   invariant: 构造函数与公共方法签名不变（5.150.7 God Class 拆分向后兼容）
# - id: A2
#   name_zh: ② 结果队列消费与统计
#   name_en: ActionDispatcher.drain_results
#   intro: 从 TaskScheduler 取已完成未处理任务逐个 dispatch 并累计统计
#   desc: 标记 task.acted=True 防重；按 report.status 累加 _stats（dispatched/modified/created/deleted/search_replaced/skipped）
#   inputs: I1 A1
#   outputs: list[ActionReport] + stats 快照
# - id: A3
#   name_zh: ③ BRAIN 注释块文本编辑
#   name_en: BrainBlockEditor
#   intro: 纯文本构建/插入/更新 # BRAIN 注释块，无 I/O 无状态
#   desc: build_block 逐键序列化加时间戳；insert 跳过 shebang/docstring 后落位；update 替换连续标记行区间
#   inputs: 无（纯文本工具，被 worker 与外观别名调用）
#   outputs: 编辑后文本
# - id: A4
#   name_zh: ④ 模块文件发现
#   name_en: ModuleFileLocator
#   intro: 把模块名/文本提示解析成磁盘上的 .py 或 YAML 文件
#   desc: 剥离 11 种任务前缀取首行 80 字符为模块名；src/**/*.py glob 精确+模糊互配；capability card / blueprint 按 stem 互配查找
#   inputs: 无（查找工具，被外观 wrapper 与 worker 调用）
#   outputs: Path 或 None
# 层: 输出
# - id: O1
#   name_zh: 动作分发器包公共 API
#   name_en: ActionDispatcher / ActionReport / BrainBlockEditor / ModuleFileLocator
#   intro: 推理结果直接回写源文件的外观入口（版本链 + 行级编辑 + 创建/删除）
#   downstream: orchestrator.py / task_worker.py / test_action_dispatcher.py（[CONSUMERS] 头）
# - id: O2
#   name_zh: 动作执行副作用
#   name_en: file mutations
#   intro: 源文件改写/创建/删除（.brain_trash）与 .brain_backups 版本链备份、audit_logs 审计
#   downstream: 无下游/内部使用（直接写盘）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I1 --> A2
# A1 --> A2
# A1 --> O1
# A2 --> O1
# A3 --> O1
# A4 --> O1
# A1 --> O2
"""

from __future__ import annotations

"""动作分发器: 推理结果 -> 直接回写源文件 (Phase 2: 版本链 + 行级编辑 + 创建/删除)。

外观类: ActionDispatcher
提取类:
  - SearchReplaceEngine: 搜索替换引擎（_search_replace_file + 2 个底层方法）
  - FileLifecycleManager: 文件生命周期管理（_create_file / _delete_file / _version_backup）
  - AnnotationWriter: 注解写入器（_annotate_py_file / _tag_module / _annotate_blueprint）
  - AuditLogWriter: 审计日志写入器（_write_triage_log）

公共 API:
  - ActionDispatcher: 外观类（dispatch / drain_results / _skip / _version_backup + 6 locator wrappers + 3 BrainBlock aliases）
  - ActionReport: 动作报告 dataclass
  - BrainBlockEditor: 纯文本注释块编辑器
  - ModuleFileLocator: 模块文件发现器

向后兼容:
  - from zephyr.trading.action_dispatcher import ActionDispatcher  ✅
  - ActionDispatcher(...) 构造函数签名不变 ✅
  - all public methods 签名不变 ✅
  - 从原 .py 迁移到包的 __init__.py, 导入路径不变 ✅
"""

__all__ = [
    "ActionDispatcher",
    "BrainBlockEditor",
    "ModuleFileLocator",
    "ActionReport",
    "REPO_ROOT",
    "_read_text",
    "_git_commit_hash",
]

import json
import logging
import re
import shutil
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Final

from zephyr.shared.io.paths import REPO_ROOT  # 仓库根真源（SSoT：zephyr.shared.io.paths）
from zephyr.shared.io.serialization import dumps

if TYPE_CHECKING:
    from zephyr.infrastructure.queue.task_scheduler import TaskScheduler
    from zephyr.shared.schema.task_types import TaskCard

_log = logging.getLogger(__name__)

CAPABILITY_CARDS_DIR: Final[Path] = REPO_ROOT / "data" / "capability_cards"
AUDIT_LOGS_DIR: Final[Path] = REPO_ROOT / "data" / "audit_logs"
BRAIN_BACKUPS_DIR: Final[Path] = REPO_ROOT / ".brain_backups"
BRAIN_TRASH_DIR: Final[Path] = REPO_ROOT / ".brain_trash"

_BRAIN_MARKER = "# BRAIN"
_MAX_BACKUPS_PER_FILE = 10


def _read_text(filepath: Path) -> str | None:
    try:
        return filepath.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        _log.warning("_read_text: failed to read file %s (%s: %s)", filepath, type(e).__name__, e)
        return None


def _git_commit_hash(project_root: Path) -> str | None:
    try:
        from zephyr.shared.infra.process_pool import run_subprocess_hidden

        result = run_subprocess_hidden(
            ["git", "rev-parse", "HEAD"],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            timeout=3,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
        _log.warning("_git_commit_hash: failed to get git commit hash (%s: %s)", type(e).__name__, e, exc_info=True)
    return None


# ═══════════════════════════════════════════════════════════════════
# 已独立协作者类（保留在原位, 被 worker 和外观引用）
# ═══════════════════════════════════════════════════════════════════
# class-name-alias: 5.150.7 God Class 拆分——从 action_dispatcher.py 迁移到 package __init__.py，原 .py 保留为 ground truth 参考（被包遮蔽，不再被导入）
class BrainBlockEditor:
    """BRAIN 注释块文本编辑器（ActionDispatcher 协作者，职责簇：纯文本块构建/插入/更新，无 I/O 无状态）。

    公共方法:
      - build_block(data) -> str
      - insert_block(original, block) -> str
      - update_block(original, block) -> str
    """

    @staticmethod
    def build_block(data: dict) -> str:
        ts = datetime.now(UTC).isoformat()
        lines = [f"{_BRAIN_MARKER} {k}: {dumps(v, ensure_ascii=False)}" for k, v in data.items()]
        lines.append(f"{_BRAIN_MARKER} at: {ts}")
        return "\n".join(lines)

    @staticmethod
    def insert_block(original: str, block: str) -> str:
        lines = original.split("\n")
        insert_pos = 0

        if lines and lines[0].startswith("#!"):
            insert_pos = 1

        i = insert_pos
        while i < len(lines) and lines[i].strip().startswith('"""'):
            i += 1
            while i < len(lines) and '"""' not in lines[i]:
                i += 1
            i += 1
            insert_pos = i
            break

        while insert_pos < len(lines) and lines[insert_pos].strip().startswith(_BRAIN_MARKER):
            insert_pos += 1

        block_lines = block.split("\n")
        new_lines = lines[:insert_pos] + block_lines + [""] + lines[insert_pos:]
        return "\n".join(new_lines)

    @staticmethod
    def update_block(original: str, block: str) -> str:
        lines = original.split("\n")
        start = -1
        end = -1
        for i, line in enumerate(lines):
            if line.strip().startswith(_BRAIN_MARKER):
                if start < 0:
                    start = i
                end = i
            elif start >= 0:
                break
            else:
                start = -1

        if start < 0:
            return BrainBlockEditor.insert_block(original, block)

        block_lines = block.split("\n")
        new_lines = lines[:start] + block_lines + lines[end + 1 :]
        return "\n".join(new_lines)


# class-name-alias: 5.150.7 God Class 拆分——从 action_dispatcher.py 迁移到 package __init__.py，原 .py 保留为 ground truth 参考（被包遮蔽，不再被导入）
class ModuleFileLocator:
    """模块文件发现器（ActionDispatcher 协作者，职责簇：模块名/文本提示 -> 磁盘文件解析）。

    公共方法:
      - extract_module_name(text) -> str
      - parse_file_path(text) -> Path | None
      - find_module_file(module_name) -> Path | None
      - find_capability_card(module_name) -> Path | None
      - find_blueprint_file(module_name) -> Path | None
      - find_file_by_name(name, search_dirs) -> Path | None
    """

    def extract_module_name(self, text: str) -> str:
        if not text:
            return "unknown"
        for prefix in (
            "classify this module: ",
            "classify this document: ",
            "generate tags for: ",
            "generate tags for config: ",
            "suggest alternative names for module: ",
            "fix bug: ",
            "fix code in: ",
            "refactor: ",
            "analyze file: ",
            "scan dead code in: ",
            "detect dead code: ",
        ):
            if text.startswith(prefix):
                text = text[len(prefix) :]
        first_line = text.split("\n")[0].strip()
        if len(first_line) > 80:
            first_line = first_line[:80]
        return first_line

    def parse_file_path(self, text: str) -> Path | None:
        """从文本中提取可能的文件路径。"""
        for line in text.split("\n"):
            line = line.strip()
            if not line:
                continue
            candidate = REPO_ROOT / line
            if candidate.exists() and candidate.is_file():
                return candidate
            # 尝试只取 stem
            stem = Path(line).stem
            found = self.find_module_file(stem)
            if found:
                return found
        return None

    def find_module_file(self, module_name: str) -> Path | None:
        """在 src/ 下找对应的 .py 文件。"""
        candidates = [
            REPO_ROOT / "src" / "zephyr" / "**" / f"{module_name}.py",
            REPO_ROOT / "src" / f"zephyr/**/{module_name}.py",
        ]
        for pattern in candidates:
            try:
                matches = list(REPO_ROOT.glob(str(pattern.relative_to(REPO_ROOT))))
            except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
                matches = list(REPO_ROOT.rglob(f"{module_name}.py"))
            if matches:
                return matches[0]

        # 模糊搜索
        for py_file in (REPO_ROOT / "src").rglob("*.py"):
            if module_name in py_file.stem or py_file.stem in module_name:
                return py_file
        return None

    def find_capability_card(self, module_name: str) -> Path | None:
        """匹配 Python 模块 -> capability card YAML。"""
        stem = module_name.replace("_", "-").replace(".py", "")
        candidate = CAPABILITY_CARDS_DIR / f"{stem}.yaml"
        if candidate.exists():
            return candidate

        if CAPABILITY_CARDS_DIR.exists():
            for yaml_file in sorted(CAPABILITY_CARDS_DIR.glob("*.yaml")):
                if stem in yaml_file.stem or yaml_file.stem in stem:
                    return yaml_file
        return None

    def find_blueprint_file(self, module_name: str) -> Path | None:
        """在 architecture_model/ 下找 matching YAML。"""
        arch = REPO_ROOT / "architecture_model"
        return self.find_file_by_name(module_name, [arch])

    def find_file_by_name(self, name: str, search_dirs: list[Path]) -> Path | None:
        stem = name.replace("_", "-").replace(".py", "").replace(".yaml", "")
        for sdir in search_dirs:
            if not sdir.exists():
                continue
            for yf in sdir.rglob("*.yaml"):
                if stem in yf.stem or yf.stem in stem:
                    return yf
        return None


# ═══════════════════════════════════════════════════════════════════
# ActionReport — 必须在 worker import 之前定义（worker 内部 inline import 此类型）
# ═══════════════════════════════════════════════════════════════════
# class-name-alias: 5.150.7 God Class 拆分——从 action_dispatcher.py 迁移到 package __init__.py，原 .py 保留为 ground truth 参考（被包遮蔽，不再被导入）
class ActionReport:
    """动作执行报告。"""

    def __init__(self, target: str, capability: str, status: str, detail: str) -> None:
        self.target = target
        self.capability = capability
        self.status = status  # "success" | "skipped" | "failed"
        self.detail = detail

    def __repr__(self) -> str:
        # 5.110.3 修复: 字符串字段加 !r 使 __repr__ 可重建
        return f"ActionReport(target={self.target!r}, capability={self.capability!r}, status={self.status!r}, detail={self.detail!r})"


# ═══════════════════════════════════════════════════════════════════
# 提取类导入（ActionReport 已在上面定义, worker 可安全 import）
# ═══════════════════════════════════════════════════════════════════
from zephyr.trading.action_dispatcher._annotation_writer import AnnotationWriter
from zephyr.trading.action_dispatcher._audit_log_writer import AuditLogWriter
from zephyr.trading.action_dispatcher._file_lifecycle_manager import FileLifecycleManager
from zephyr.trading.action_dispatcher._search_replace_engine import SearchReplaceEngine


# ═══════════════════════════════════════════════════════════════════
# ActionDispatcher 外观类（裁减后仅保留路由 + _skip + _version_backup + locator wrappers + BrainBlock aliases）
# ═══════════════════════════════════════════════════════════════════
# class-name-alias: 5.150.7 God Class 拆分——从 action_dispatcher.py 迁移到 package __init__.py，原 .py 保留为 ground truth 参考（被包遮蔽，不再被导入）
class ActionDispatcher:
    """推理结果->直接回写源文件 (Phase 2: 版本链 + 行级编辑 + 创建/删除)。

    外观类 — 本类只做路由, 具体实现委托给 4 个 worker:
      - _search_replace: SearchReplaceEngine
      - _file_lifecycle: FileLifecycleManager
      - _annotation: AnnotationWriter
      - _audit: AuditLogWriter
    """

    def __init__(self, dry_run: bool = False) -> None:
        self._dry_run = dry_run
        self._locator = ModuleFileLocator()
        self._stats: dict[str, int] = {
            "dispatched": 0,
            "modified": 0,
            "skipped": 0,
            "created": 0,
            "deleted": 0,
            "search_replaced": 0,
            "backups": 0,
        }
        # 构造顺序 A: AuditLogWriter（零依赖，facade 引用供未来扩展）
        self._audit = AuditLogWriter(dry_run=dry_run, facade=self)
        # 构造顺序 B: FileLifecycleManager（需要 facade 引用 + stats）
        self._file_lifecycle = FileLifecycleManager(dry_run=dry_run, facade=self, stats=self._stats)
        # 构造顺序 C: AnnotationWriter（需要 facade 引用，通过 facade 访问 patchable 方法）
        self._annotation = AnnotationWriter(dry_run=dry_run, facade=self)
        # 构造顺序 D: SearchReplaceEngine（需要 facade 引用，后设 stats）
        self._search_replace = SearchReplaceEngine(dry_run=dry_run, facade=self)
        self._search_replace.set_stats(self._stats)

    @property
    def stats(self) -> dict[str, int]:
        """只读统计快照。"""
        return dict(self._stats)

    @property
    def dry_run(self) -> bool:
        return self._dry_run

    def dispatch(self, task: TaskCard) -> ActionReport:
        """主路由: 根据 capability 分发到对应 public 方法。

        调用 public 方法（而非 worker 实例）以支持测试 patch.object(d, "method", ...)。
        """
        capability = task.capability
        result = task.result
        payload = task.payload or {}

        if not result:
            return self._skip(task.task_id, capability, "empty result")

        source_text = payload.get("text", "")

        try:
            if capability == "task_classification":
                return self.annotate_py_file(source_text, result)
            elif capability == "tag_completion":
                return self.tag_module(source_text, result)
            elif capability == "summary_extraction":
                return self.annotate_blueprint(source_text, result)
            elif capability == "naming_suggest":
                return self.annotate_py_file(source_text, result, field="names")
            elif capability == "anomaly_triage":
                return self.write_triage_log(result)
            elif capability == "code_fix":
                return self.search_replace_file(source_text, result, field="fixes")
            elif capability == "refactor":
                return self.search_replace_file(source_text, result, field="changes")
            elif capability == "code_generate":
                return self.create_file(result)
            elif capability == "dead_code_removal":
                return self.search_replace_file(source_text, result, field="dead_sections", remove=True)
            else:
                return self._skip(task.task_id, capability, "no actuator")
        except Exception as exc:  # noqa: BLE001
            return ActionReport(task.task_id, capability, "error", str(exc))

    def drain_results(self, scheduler: TaskScheduler) -> list[ActionReport]:
        """消费 TaskScheduler 已完成队列, 逐个 dispatch 并返回报告列表。"""
        reports: list[ActionReport] = []
        with scheduler.lock:
            task_ids = list(scheduler.results.keys())

        for tid in task_ids:
            with scheduler.lock:
                task = scheduler.results.get(tid)

            if task is None or task.status != "completed":
                continue
            if getattr(task, "acted", False):
                continue

            report = self.dispatch(task)
            task.acted = True
            reports.append(report)

            self._stats["dispatched"] += 1
            if report.status == "modified":
                self._stats["modified"] += 1
            elif report.status == "created":
                self._stats["created"] += 1
            elif report.status == "deleted":
                self._stats["deleted"] += 1
            elif report.status == "search_replaced":
                self._stats["search_replaced"] += 1
            else:
                self._stats["skipped"] += 1

        return reports

    @staticmethod
    def _skip(task_id: str, capability: str, reason: str) -> ActionReport:
        """跳过此任务（无数据/不支持的能力）。"""
        return ActionReport(task_id, capability, "skipped", reason)

    def version_backup(self, filepath: Path) -> str | None:
        """版本链备份 — 外观薄包装, 委托给 FileLifecycleManager。"""
        return self._file_lifecycle.version_backup(filepath)

    def _version_backup(self, filepath: Path) -> str | None:
        """向后兼容薄包装 — 委托给 public version_backup。"""
        return self.version_backup(filepath)

    # ── 业务方法 public（委托给 worker 实例, 支持测试 patch.object(d, "method", ...)） ──

    def search_replace_file(
        self,
        source_text: str,
        result: dict,
        field: str = "fixes",
        remove: bool = False,
    ) -> ActionReport:
        """SearchReplace 入口 — 委托给 SearchReplaceEngine.search_replace_file。"""
        return self._search_replace.search_replace_file(source_text, result, field=field, remove=remove)

    def _search_replace_file(
        self,
        source_text: str,
        result: dict,
        field: str = "fixes",
        remove: bool = False,
    ) -> ActionReport:
        """向后兼容薄包装 — 委托给 public search_replace_file。"""
        return self.search_replace_file(source_text, result, field=field, remove=remove)

    def create_file(self, result: dict) -> ActionReport:
        """创建新文件 — 委托给 FileLifecycleManager.create_file。"""
        return self._file_lifecycle.create_file(result)

    def _create_file(self, result: dict) -> ActionReport:
        """向后兼容薄包装 — 委托给 public create_file。"""
        return self.create_file(result)

    def delete_file(self, source_text: str, result: dict) -> ActionReport:
        """删除文件（移到 .brain_trash/）— 委托给 FileLifecycleManager.delete_file。"""
        return self._file_lifecycle.delete_file(source_text, result)

    def _delete_file(self, source_text: str, result: dict) -> ActionReport:
        """向后兼容薄包装 — 委托给 public delete_file。"""
        return self.delete_file(source_text, result)

    def annotate_py_file(self, source_text: str, result: dict, field: str = "category") -> ActionReport:
        """Python 文件 BRAIN 注释 — 委托给 AnnotationWriter.annotate_py_file。"""
        return self._annotation.annotate_py_file(source_text, result, field=field)

    def _annotate_py_file(self, source_text: str, result: dict, field: str = "category") -> ActionReport:
        """向后兼容薄包装 — 委托给 public annotate_py_file。"""
        return self.annotate_py_file(source_text, result, field=field)

    def tag_module(self, source_text: str, result: dict) -> ActionReport:
        """Capability card 标签追加 — 委托给 AnnotationWriter.tag_module。"""
        return self._annotation.tag_module(source_text, result)

    def _tag_module(self, source_text: str, result: dict) -> ActionReport:
        """向后兼容薄包装 — 委托给 public tag_module。"""
        return self.tag_module(source_text, result)

    def annotate_blueprint(self, source_text: str, result: dict) -> ActionReport:
        """Blueprint 摘要注释 — 委托给 AnnotationWriter.annotate_blueprint。"""
        return self._annotation.annotate_blueprint(source_text, result)

    def _annotate_blueprint(self, source_text: str, result: dict) -> ActionReport:
        """向后兼容薄包装 — 委托给 public annotate_blueprint。"""
        return self.annotate_blueprint(source_text, result)

    def write_triage_log(self, result: dict) -> ActionReport:
        """审计日志写入 — 委托给 AuditLogWriter.write_triage_log。"""
        return self._audit.write_triage_log(result)

    def _write_triage_log(self, result: dict) -> ActionReport:
        """向后兼容薄包装 — 委托给 public write_triage_log。"""
        return self.write_triage_log(result)

    # ── locator public 包装方法（委托给 ModuleFileLocator） ──

    def extract_module_name(self, text: str) -> str:
        return self._locator.extract_module_name(text)

    def _extract_module_name(self, text: str) -> str:
        """向后兼容薄包装 — 委托给 public extract_module_name。"""
        return self.extract_module_name(text)

    def parse_file_path(self, text: str) -> Path | None:
        return self._locator.parse_file_path(text)

    def _parse_file_path(self, text: str) -> Path | None:
        """向后兼容薄包装 — 委托给 public parse_file_path。"""
        return self.parse_file_path(text)

    def find_module_file(self, module_name: str) -> Path | None:
        return self._locator.find_module_file(module_name)

    def _find_module_file(self, module_name: str) -> Path | None:
        """向后兼容薄包装 — 委托给 public find_module_file。"""
        return self.find_module_file(module_name)

    def find_capability_card(self, module_name: str) -> Path | None:
        return self._locator.find_capability_card(module_name)

    def _find_capability_card(self, module_name: str) -> Path | None:
        """向后兼容薄包装 — 委托给 public find_capability_card。"""
        return self.find_capability_card(module_name)

    def find_blueprint_file(self, module_name: str) -> Path | None:
        return self._locator.find_blueprint_file(module_name)

    def _find_blueprint_file(self, module_name: str) -> Path | None:
        """向后兼容薄包装 — 委托给 public find_blueprint_file。"""
        return self.find_blueprint_file(module_name)

    def find_file_by_name(self, name: str, search_dirs: list[Path]) -> Path | None:
        return self._locator.find_file_by_name(name, search_dirs)

    def _find_file_by_name(self, name: str, search_dirs: list[Path]) -> Path | None:
        """向后兼容薄包装 — 委托给 public find_file_by_name。"""
        return self.find_file_by_name(name, search_dirs)

    # ── BrainBlock public static methods ──

    build_py_brain_block = staticmethod(BrainBlockEditor.build_block)
    insert_brain_block = staticmethod(BrainBlockEditor.insert_block)
    update_brain_block = staticmethod(BrainBlockEditor.update_block)

    # ── BrainBlock 向后兼容别名（staticmethod assignments, 委托给 public） ──

    _build_py_brain_block = staticmethod(BrainBlockEditor.build_block)
    _insert_brain_block = staticmethod(BrainBlockEditor.insert_block)
    _update_brain_block = staticmethod(BrainBlockEditor.update_block)
