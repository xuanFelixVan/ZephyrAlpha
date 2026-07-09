# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md
# [MODULE] zephyr.trading.action_dispatcher
# [DOMAIN] D_TRADING
# [DEPENDENCIES] zephyr.trading.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-ORC_action_dispatcher | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
ActionDispatcher --- 大脑的"手" v2.0 (Phase 2)
================================================
推理完成 -> 直接把结果写回源文件，不产生中间文件。

Phase 2 新增:
    - Git 版本链备份: 每次修改前保存快照到 .brain_backups/
    - SearchReplace 行级精确替换: old_str -> new_str
    - brain_create_file: 创建新文件 + 自动注册 capability card
    - brain_delete_file: 删除文件(移到 .brain_trash/ 回收站)

工作流:
    LocalModelScheduler 完成推理
        ↓
    ActionDispatcher.dispatch(task)
        ↓              ↓              ↓              ↓              ↓
    Python 注释     YAML 标签      Blueprint 摘要   SearchReplace   创建/删除文件
    # BRAIN 块      brain_tags     # brain-summary  old->new 替换    .brain_trash/

原则:
    - 只修改项目本身的文件，不创建 data/brain/ 中间产物
    - 所有修改标注 # BRAIN 前缀，方便人类识别
    - 版本链备份: 每次修改前保存快照到 .brain_backups/
    - 危险操作(删除)先移入回收站 .brain_trash/
"""

from __future__ import annotations

from typing import Final
from zephyr.shared.io.serialization import dumps

import json
import logging
import re
import shutil
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from zephyr.shared.io.paths import REPO_ROOT  # 仓库根真源（SSoT：zephyr.shared.io.paths）
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from zephyr.shared.schema.task_types import TaskCard
    from zephyr.infrastructure.queue.task_scheduler import TaskScheduler

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
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            timeout=3,
        )
        if result.returncode == 0:
                return result.stdout.strip()
    except Exception as e:
        _log.warning("_git_commit_hash: failed to get git commit hash (%s: %s)", type(e).__name__, e, exc_info=True)
    return None


class ActionDispatcher:
    """推理结果->直接回写源文件 (Phase 2: 版本链 + 行级编辑 + 创建/删除)。"""

    def __init__(self, dry_run: bool = False) -> None:
        self._dry_run = dry_run
        self._stats: dict[str, int] = {
            "dispatched": 0,
            "modified": 0,
            "skipped": 0,
            "created": 0,
            "deleted": 0,
            "search_replaced": 0,
            "backups": 0,
        }

    @property
    def stats(self) -> dict[str, int]:
        return dict(self._stats)

    @property
    def dry_run(self) -> bool:
        return self._dry_run

    # ── 主分发入口 ──────────────────────────────────────

    def dispatch(self, task: TaskCard) -> ActionReport:
        capability = task.capability
        result = task.result
        payload = task.payload or {}

        if not result:
            return self._skip(task.task_id, capability, "empty result")

        source_text = payload.get("text", "")

        try:
            if capability == "task_classification":
                return self._annotate_py_file(source_text, result)
            elif capability == "tag_completion":
                return self._tag_module(source_text, result)
            elif capability == "summary_extraction":
                return self._annotate_blueprint(source_text, result)
            elif capability == "naming_suggest":
                return self._annotate_py_file(source_text, result, field="names")
            elif capability == "anomaly_triage":
                return self._write_triage_log(result)
            elif capability == "code_fix":
                return self._search_replace_file(source_text, result, field="fixes")
            elif capability == "refactor":
                return self._search_replace_file(source_text, result, field="changes")
            elif capability == "code_generate":
                return self._create_file(result)
            elif capability == "dead_code_removal":
                return self._search_replace_file(source_text, result, field="dead_sections", remove=True)
            else:
                return self._skip(task.task_id, capability, "no actuator")
        except Exception as exc:
            return ActionReport(task.task_id, capability, "error", str(exc))

    def drain_results(self, scheduler: TaskScheduler) -> list[ActionReport]:
        reports: list[ActionReport] = []
        with scheduler._lock:
            task_ids = list(scheduler._results.keys())

        for tid in task_ids:
            with scheduler._lock:
                task = scheduler._results.get(tid)

            if task is None or task.status != "completed":
                continue
            if getattr(task, "_acted", False):
                continue

            report = self.dispatch(task)
            task._acted = True
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

    # ── 版本链备份 ──────────────────────────────────────

    @staticmethod
    def _version_backup(filepath: Path) -> str | None:
        """版本链备份: 保存文件快照到 .brain_backups/ 并记录 manifest。

        返回备份文件路径(相对路径字符串)，失败返回 None。
        """
        content = _read_text(filepath)
        if content is None:
            return None

        BRAIN_BACKUPS_DIR.mkdir(parents=True, exist_ok=True)

        ts = datetime.now(UTC).strftime("%Y%m%dT%H%M%S")
        stem = filepath.stem
        suffix = filepath.suffix
        bak_name = f"{stem}.{ts}{suffix}.brain_bak"
        bak_path = BRAIN_BACKUPS_DIR / bak_name

        bak_path.write_text(content, encoding="utf-8")

        git_commit = _git_commit_hash(REPO_ROOT)
        try:
            rel_path = str(filepath.relative_to(REPO_ROOT))
        except ValueError:
            rel_path = str(filepath)
        manifest_entry = json.dumps(
            {
                "file": rel_path,
                "backup": bak_name,
                "timestamp": datetime.now(UTC).isoformat(),
                "git_commit": git_commit,
            },
            ensure_ascii=False,
        )

        manifest_path = BRAIN_BACKUPS_DIR / "manifest.jsonl"
        with open(manifest_path, "a", encoding="utf-8") as f:
            f.write(manifest_entry + "\n")

        # 清理旧备份: 每个文件最多保留 _MAX_BACKUPS_PER_FILE 个
        pattern_prefix = f"{stem}."
        pattern_suffix = f"{suffix}.brain_bak"
        old_backups = sorted(
            [p for p in BRAIN_BACKUPS_DIR.glob(f"{pattern_prefix}*{pattern_suffix}") if p.name != bak_name],
            key=lambda p: p.stat().st_mtime,
        )
        while len(old_backups) >= _MAX_BACKUPS_PER_FILE:
            old = old_backups.pop(0)
            try:
                old.unlink()
            except OSError:
                pass

        return bak_name

    # ── SearchReplace: 行级精确替换 ─────────────────────

    def _search_replace_file(
        self,
        source_text: str,
        result: dict,
        field: str = "fixes",
        remove: bool = False,
    ) -> ActionReport:
        """SearchReplace 核心引擎: old_str -> new_str 精确替换。

        Args:
            source_text: payload 文本，用于提取文件名
            result: 推理结果 dict，包含 fixes/changes/dead_sections 列表
            field: result 中的字段名 ("fixes"|"changes"|"dead_sections")
            remove: True 表示删除(替换为空字符串)，用于 dead_code_removal
        """
        module_name = self._extract_module_name(source_text)
        py_file = self._find_module_file(module_name)
        if py_file is None:
            # 尝试从 source_text 里直接解析路径
            py_file = self._parse_file_path(source_text)
        if py_file is None:
            return ActionReport(module_name, "search_replace", "skipped", f"file not found for: {module_name}")

        entries = result.get(field, [])
        if not entries:
            return ActionReport(module_name, "search_replace", "skipped", f"empty {field}")

        original = _read_text(py_file)
        if original is None:
            return ActionReport(module_name, "search_replace", "error", "cannot read file")

        modified, applied, failed, reasons = self._apply_replacement_entries(py_file, original, entries, remove)

        return self._finalize_replacement(py_file, original, modified, applied, failed, reasons, remove)

    def _apply_replacement_entries(
        self,
        py_file: Path,
        original: str,
        entries: list,
        remove: bool,
    ) -> tuple[str, int, int, list[str]]:
        """Phase 7e: 替换循环提取——遍历 entries 执行精确/宽松匹配替换。

        Returns:
            (modified_text, applied_count, failed_count, reasons)
        """
        modified = original
        applied = 0
        failed = 0
        reasons: list[str] = []

        for entry in entries:
            old_str = entry.get("old_str", "")
            new_str = "" if remove else entry.get("new_str", "")
            reason = entry.get("reason", "")

            if not old_str:
                failed += 1
                continue

            if old_str in modified:
                modified = modified.replace(old_str, new_str, 1)
                applied += 1
                if reason:
                    reasons.append(reason)
            else:
                # 尝试宽松匹配: 去除首尾空白
                old_stripped = old_str.strip()
                if old_stripped and old_stripped in modified:
                    idx = modified.index(old_stripped)
                    actual_old = modified[idx : idx + len(old_stripped)]
                    modified = modified.replace(actual_old, new_str, 1)
                    applied += 1
                    if reason:
                        reasons.append(reason)
                else:
                    failed += 1
                    _log.debug("SearchReplace: old_str not found in %s: %r", py_file.name, old_str[:60])

        return modified, applied, failed, reasons

    def _finalize_replacement(
        self,
        py_file: Path,
        original: str,
        modified: str,
        applied: int,
        failed: int,
        reasons: list[str],
        remove: bool,
    ) -> ActionReport:
        """Phase 7e: 结果构建提取——校验变更、备份、写入、组装 ActionReport。"""
        if applied == 0:
            return ActionReport(py_file.name, "search_replace", "skipped", f"{failed} match(es) failed")

        if modified == original:
            return ActionReport(py_file.name, "search_replace", "skipped", "unchanged")

        # 对于 remove 操作，清理产生的多余空行
        if remove:
            modified = re.sub(r"\n{3,}", "\n\n", modified)

        backup_name = self._version_backup(py_file)
        if backup_name:
            self._stats["backups"] = self._stats.get("backups", 0) + 1

        if not self._dry_run:
            py_file.write_text(modified, encoding="utf-8")

        detail = f"{applied} replaced"
        if reasons:
            detail += f": {reasons[0][:50]}"
        if failed:
            detail += f" ({failed} failed)"

        # 5.53.5 修复：原 failed>0 时仍用 INFO，代码修改部分失败被静默。failed>0 时用 WARNING。
        if failed > 0:
            _log.warning("BrainHands: %s SearchReplace applied=%d failed=%d", py_file.name, applied, failed)
        else:
            _log.info("BrainHands: %s SearchReplace applied=%d failed=%d", py_file.name, applied, failed)
        return ActionReport(py_file.name, "search_replace", "search_replaced", detail)

    # ── 创建新文件 ──────────────────────────────────────

    def _create_file(self, result: dict) -> ActionReport:
        """从推理结果创建新文件。

        result 格式 (来自 code_generate inference):
            {"codegen": {"file_path": "path/to/file.py", "content": "...", "description": "..."}}
        或直接:
            {"file_path": "path/to/file.py", "content": "...", "description": "..."}
        """
        codegen = result.get("codegen", result)
        file_path_str = codegen.get("file_path", "")
        content = codegen.get("content", "")
        description = codegen.get("description", "brain-generated")

        if not file_path_str:
            return ActionReport("unknown", "code_generate", "skipped", "no file_path")
        if not content:
            return ActionReport("unknown", "code_generate", "skipped", "empty content")

        # 安全: 限制在 REPO_ROOT 内
        target = (REPO_ROOT / file_path_str).resolve()
        if not str(target).startswith(str(REPO_ROOT.resolve())):
            return ActionReport(file_path_str, "code_generate", "error", "path escapes REPO_ROOT")

        if target.exists():
            return ActionReport(file_path_str, "code_generate", "skipped", f"file already exists: {target.name}")

        # 添加 BRAIN 标记 header
        ts = datetime.now(UTC).isoformat()
        brain_header = (
            f"{_BRAIN_MARKER} generated: {ts}\n"
            f"{_BRAIN_MARKER} description: {description}\n"
            f"{_BRAIN_MARKER} source: code_generate inference\n\n"
        )
        full_content = brain_header + content
        if not full_content.endswith("\n"):
            full_content += "\n"

        if self._dry_run:
            _log.info("BrainHands: (dry-run) would create %s", target.relative_to(REPO_ROOT))
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(full_content, encoding="utf-8")

        _log.info("BrainHands: created %s (%d chars)", target.relative_to(REPO_ROOT), len(content))
        return ActionReport(
            str(target.relative_to(REPO_ROOT)),
            "code_generate",
            "created",
            f"{len(content)} chars, {description[:60]}",
        )

    # ── 删除文件 (移到 .brain_trash/) ──────────────────

    def _delete_file(self, source_text: str, result: dict) -> ActionReport:
        """将文件移到 .brain_trash/ 回收站而非永久删除。

        支持从 result 中解析文件路径或模块名。
        """
        module_name = self._extract_module_name(source_text)
        target_file = self._find_module_file(module_name)

        if target_file is None:
            # 尝试从 result 中获取路径
            file_path_hint = result.get("file_path", "")
            if file_path_hint:
                target_file = REPO_ROOT / file_path_hint
            elif module_name:
                target_file = self._parse_file_path(source_text)

        if target_file is None:
            return ActionReport(module_name, "dead_code_removal", "skipped", "file not found")
        if not target_file.exists():
            return ActionReport(module_name, "dead_code_removal", "skipped", "file does not exist")

        BRAIN_TRASH_DIR.mkdir(parents=True, exist_ok=True)

        ts = datetime.now(UTC).strftime("%Y%m%dT%H%M%S")
        trash_name = f"{ts}_{target_file.name}"
        trash_path = BRAIN_TRASH_DIR / trash_name

        # 记录 trash manifest
        manifest_entry = json.dumps(
            {
                "original": str(target_file.relative_to(REPO_ROOT)),
                "trashed_as": trash_name,
                "timestamp": datetime.now(UTC).isoformat(),
                "git_commit": _git_commit_hash(REPO_ROOT),
            },
            ensure_ascii=False,
        )

        trash_manifest = BRAIN_TRASH_DIR / "trash_manifest.jsonl"
        with open(trash_manifest, "a", encoding="utf-8") as f:
            f.write(manifest_entry + "\n")

        # 先做版本链备份
        self._version_backup(target_file)

        if self._dry_run:
            _log.info("BrainHands: (dry-run) would trash %s", target_file.name)
        else:
            shutil.move(str(target_file), str(trash_path))

        _log.info("BrainHands: trashed %s -> %s", target_file.name, trash_name)
        return ActionReport(
            str(target_file.relative_to(REPO_ROOT)),
            "dead_code_removal",
            "deleted",
            f"moved to .brain_trash/{trash_name}",
        )

    # ── Python 文件直接注释 ──────────────────────────────

    def _annotate_py_file(self, source_text: str, result: dict, field: str = "category") -> ActionReport:
        module_name = self._extract_module_name(source_text)
        py_file = self._find_module_file(module_name)
        if py_file is None:
            return ActionReport(module_name, "task_classification", "skipped", f"file not found for: {module_name}")

        original = _read_text(py_file)
        if original is None:
            return ActionReport(module_name, "task_classification", "error", "cannot read file")

        if field == "category":
            value = result.get("category", "unknown")
            brain_block = self._build_py_brain_block({"classification": value, **result})
        elif field == "names":
            names = result.get("names", [])
            brain_block = self._build_py_brain_block({"naming_candidates": names})
        else:
            value = str(result.get(field, result))
            brain_block = self._build_py_brain_block({"brain_tag": value})

        if _BRAIN_MARKER in original:
            new_content = self._update_brain_block(original, brain_block)
        else:
            new_content = self._insert_brain_block(original, brain_block)

        if new_content == original:
            return ActionReport(module_name, "task_classification", "skipped", "unchanged")

        self._version_backup(py_file)
        if not self._dry_run:
            py_file.write_text(new_content, encoding="utf-8")

        _log.info("BrainHands: %s <- %s=%s", py_file.name, field, str(value)[:60])
        return ActionReport(py_file.name, "task_classification", "modified", f"{field}={str(value)[:40]}")

    # ── Capability Card 标签追加 ────────────────────────

    def _tag_module(self, source_text: str, result: dict) -> ActionReport:
        module_name = self._extract_module_name(source_text)
        tags = result.get("tags", [])
        if not tags:
            return ActionReport(module_name, "tag_completion", "skipped", "empty tags")

        card_file = self._find_capability_card(module_name)
        if card_file is None:
            return ActionReport(module_name, "tag_completion", "skipped", "no card found")

        content = _read_text(card_file)
        if content is None:
            return ActionReport(module_name, "tag_completion", "error", "cannot read card")

        import yaml

        try:
            data = yaml.safe_load(content)
        except Exception:
            data = {}

        if not isinstance(data, dict):
            data = {}

        existing_tags = set(data.get("tags", []) or [])
        brain_tags = data.get("brain_tags", []) or []
        new_tags = [t for t in tags if t not in existing_tags and t not in brain_tags]
        if not new_tags:
            return ActionReport(module_name, "tag_completion", "skipped", "all tags exist")

        brain_tags.extend(new_tags)
        data["brain_tags"] = brain_tags

        new_yaml = yaml.dump(data, allow_unicode=True, sort_keys=False)
        if not new_yaml.endswith("\n"):
            new_yaml += "\n"

        self._version_backup(card_file)
        if not self._dry_run:
            card_file.write_text(new_yaml, encoding="utf-8")

        _log.info("BrainHands: %s +tags=%s", card_file.name, new_tags)
        return ActionReport(card_file.name, "tag_completion", "modified", f"added {len(new_tags)} tags: {new_tags}")

    # ── Blueprint 摘要注释 ──────────────────────────────

    def _annotate_blueprint(self, source_text: str, result: dict) -> ActionReport:
        module_name = self._extract_module_name(source_text)
        bp_file = self._find_blueprint_file(module_name)
        if bp_file is None:
            bp_file = self._find_file_by_name(module_name, [REPO_ROOT / "architecture_model"])

        points = result.get("result", {}).get("points", [])
        if not points:
            return ActionReport(module_name, "summary_extraction", "skipped", "no points")

        if bp_file is None:
            return ActionReport(module_name, "summary_extraction", "skipped", "blueprint not found")

        original = _read_text(bp_file)
        if original is None:
            return ActionReport(module_name, "summary_extraction", "error", "cannot read")

        summary_block = "\n".join(f"# brain-summary: {p}" for p in points)
        summary_block += f"\n# brain-summary-generated: {datetime.now(UTC).isoformat()}\n"

        if "# brain-summary:" in original:
            new_content = re.sub(
                r"(?:# brain-summary:.*\n)*# brain-summary-generated:.*\n?",
                summary_block,
                original,
            )
        else:
            new_content = summary_block + "\n" + original

        if new_content == original:
            return ActionReport(module_name, "summary_extraction", "skipped", "unchanged")

        self._version_backup(bp_file)
        if not self._dry_run:
            bp_file.write_text(new_content, encoding="utf-8")

        _log.info("BrainHands: %s <- summary (%d points)", bp_file.name, len(points))
        return ActionReport(bp_file.name, "summary_extraction", "modified", f"added {len(points)} summary points")

    # ── 审计日志 ─────────────────────────────────────────

    def _write_triage_log(self, result: dict) -> ActionReport:
        triage = result.get("result", {})
        needs_human = triage.get("needs_human", False)
        reason = triage.get("reason", "")

        today = datetime.now(UTC).strftime("%Y%m%d")
        out_file = AUDIT_LOGS_DIR / f"brain_triage_{today}.jsonl"
        out_file.parent.mkdir(parents=True, exist_ok=True)

        entry = json.dumps(
            {
                "timestamp": datetime.now(UTC).isoformat(),
                "needs_human": needs_human,
                "reason": reason,
            },
            ensure_ascii=False,
        )

        with open(out_file, "a", encoding="utf-8") as f:
            f.write(entry + "\n")

        status = "ALERT" if needs_human else "CLEAR"
        return ActionReport("audit", "anomaly_triage", "modified", f"triage: {status}")

    # ── 文件发现辅助 ────────────────────────────────────

    def _extract_module_name(self, text: str) -> str:
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

    def _parse_file_path(self, text: str) -> Path | None:
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
            found = self._find_module_file(stem)
            if found:
                return found
        return None

    def _find_module_file(self, module_name: str) -> Path | None:
        """在 src/ 下找对应的 .py 文件。"""
        candidates = [
            REPO_ROOT / "src" / "zephyr" / "**" / f"{module_name}.py",
            REPO_ROOT / "src" / f"zephyr/**/{module_name}.py",
        ]
        for pattern in candidates:
            try:
                matches = list(REPO_ROOT.glob(str(pattern.relative_to(REPO_ROOT))))
            except Exception:
                matches = list(REPO_ROOT.rglob(f"{module_name}.py"))
            if matches:
                return matches[0]

        # 模糊搜索
        for py_file in (REPO_ROOT / "src").rglob("*.py"):
            if module_name in py_file.stem or py_file.stem in module_name:
                return py_file
        return None

    def _find_capability_card(self, module_name: str) -> Path | None:
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

    def _find_blueprint_file(self, module_name: str) -> Path | None:
        """在 architecture_model/ 下找 matching YAML。"""
        arch = REPO_ROOT / "architecture_model"
        return self._find_file_by_name(module_name, [arch])

    def _find_file_by_name(self, name: str, search_dirs: list[Path]) -> Path | None:
        stem = name.replace("_", "-").replace(".py", "").replace(".yaml", "")
        for sdir in search_dirs:
            if not sdir.exists():
                continue
            for yf in sdir.rglob("*.yaml"):
                if stem in yf.stem or yf.stem in stem:
                    return yf
        return None

    # ── Python 文件脑注释块 ─────────────────────────────

    @staticmethod
    def _build_py_brain_block(data: dict) -> str:
        ts = datetime.now(UTC).isoformat()
        lines = [f"{_BRAIN_MARKER} {k}: {dumps(v, ensure_ascii=False)}" for k, v in data.items()]
        lines.append(f"{_BRAIN_MARKER} at: {ts}")
        return "\n".join(lines)

    @staticmethod
    def _insert_brain_block(original: str, block: str) -> str:
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
    def _update_brain_block(original: str, block: str) -> str:
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
            return ActionDispatcher._insert_brain_block(original, block)

        block_lines = block.split("\n")
        new_lines = lines[:start] + block_lines + lines[end + 1 :]
        return "\n".join(new_lines)

    @staticmethod
    def _skip(task_id: str, capability: str, reason: str) -> ActionReport:
        return ActionReport(task_id, capability, "skipped", reason)


# ── ActionReport ────────────────────────────────────────


class ActionReport:
    def __init__(self, target: str, capability: str, status: str, detail: str) -> None:
        self.target = target
        self.capability = capability
        self.status = status
        self.detail = detail

    def __repr__(self) -> str:
        # 5.110.3 修复: 字符串字段加 !r 使 __repr__ 可重建
        return f"ActionReport(target={self.target!r}, capability={self.capability!r}, status={self.status!r}, detail={self.detail!r})"
