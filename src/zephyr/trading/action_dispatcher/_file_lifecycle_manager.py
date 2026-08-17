# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md | §5.150.7
# [MODULE] MOD-INF-035 | zephyr.trading.action_dispatcher._file_lifecycle_manager
# [DOMAIN] D_TRADING
# [DEPENDENCIES] zephyr.trading.action_dispatcher (facade module: _facade_mod.REPO_ROOT/BRAIN_BACKUPS_DIR/BRAIN_TRASH_DIR/_read_text/_git_commit_hash/ActionReport/_MAX_BACKUPS_PER_FILE; facade ref: _extract_module_name/_find_module_file/_parse_file_path/_version_backup)
# [CONSUMERS] zephyr.trading.action_dispatcher.ActionDispatcher.__init__ (构造 _file_lifecycle 实例); ActionDispatcher._version_backup (facade 委托)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 文件生命周期管理——create_file/delete_file/version_backup；通过 facade ref 访问 patchable 实例方法以支持 patch.object(d, "_method", ...) 测试；version_backup 保留最近 N 份备份（_MAX_BACKUPS_PER_FILE）
# [MODIFY-GUARD] 公共方法 create_file/delete_file/version_backup 签名变更需同步 facade thin wrapper 与测试
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] create_file 路径逃逸 REPO_ROOT→error；空 file_path/empty content/already exists→skipped；delete_file 文件不存在→skipped；version_backup 失败返回 None
# [TESTS] tests/action/test_action_dispatcher.py (TestActionDispatcherCreateFile + TestActionDispatcherDeleteFile)
# [A_module] module_id=MOD-INF-035 | layer=module | stability=stable | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""文件生命周期管理器（从 ActionDispatcher._create_file / _delete_file / _version_backup 提取）。

职责簇：文件创建/删除/版本备份。
通过 facade 引用访问 patchable 实例方法（_extract_module_name/_find_module_file/_version_backup 等）。
通过 _facade_mod 访问 patchable 模块级常量（REPO_ROOT/BRAIN_BACKUPS_DIR/BRAIN_TRASH_DIR）。
"""

from __future__ import annotations

import json
import logging
import shutil
from datetime import UTC, datetime
from pathlib import Path

from zephyr.trading import action_dispatcher as _facade_mod

_log = logging.getLogger(__name__)


class FileLifecycleManager:
    """文件生命周期管理器。

    Public API:
        version_backup(filepath) -> str | None
        create_file(result) -> ActionReport
        delete_file(source_text, result) -> ActionReport
    """

    def __init__(self, dry_run: bool, facade=None, stats: dict | None = None) -> None:
        self._dry_run = dry_run
        self._facade = facade
        self._stats = stats if stats is not None else {}

    def version_backup(self, filepath: Path) -> str | None:
        """版本链备份: 保存文件快照到 .brain_backups/ 并记录 manifest。

        Returns:
            bak_name: 备份文件名（不含目录），失败返回 None。
        """
        content = _facade_mod._read_text(filepath)
        if content is None:
            return None

        _facade_mod.BRAIN_BACKUPS_DIR.mkdir(parents=True, exist_ok=True)

        ts = datetime.now(UTC).strftime("%Y%m%dT%H%M%S")
        stem = filepath.stem
        suffix = filepath.suffix
        bak_name = f"{stem}.{ts}{suffix}.brain_bak"
        bak_path = _facade_mod.BRAIN_BACKUPS_DIR / bak_name

        bak_path.write_text(content, encoding="utf-8")

        git_commit = _facade_mod._git_commit_hash(_facade_mod.REPO_ROOT)
        try:
            rel_path = str(filepath.relative_to(_facade_mod.REPO_ROOT))
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

        manifest_path = _facade_mod.BRAIN_BACKUPS_DIR / "manifest.jsonl"
        with open(manifest_path, "a", encoding="utf-8") as f:
            f.write(manifest_entry + "\n")

        # 清理旧备份: 每个文件最多保留 _MAX_BACKUPS_PER_FILE 个
        pattern_prefix = f"{stem}."
        pattern_suffix = f"{suffix}.brain_bak"
        old_backups = sorted(
            [p for p in _facade_mod.BRAIN_BACKUPS_DIR.glob(f"{pattern_prefix}*{pattern_suffix}") if p.name != bak_name],
            key=lambda p: p.stat().st_mtime,
        )
        while len(old_backups) >= _facade_mod._MAX_BACKUPS_PER_FILE:
            old = old_backups.pop(0)
            try:
                old.unlink()
            except OSError:
                pass

        return bak_name

    def create_file(self, result: dict):
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
            return _facade_mod.ActionReport("unknown", "code_generate", "skipped", "no file_path")
        if not content:
            return _facade_mod.ActionReport("unknown", "code_generate", "skipped", "empty content")

        # 安全: 限制在 REPO_ROOT 内
        target = (_facade_mod.REPO_ROOT / file_path_str).resolve()
        if not str(target).startswith(str(_facade_mod.REPO_ROOT.resolve())):
            return _facade_mod.ActionReport(file_path_str, "code_generate", "error", "path escapes REPO_ROOT")

        if target.exists():
            return _facade_mod.ActionReport(
                file_path_str, "code_generate", "skipped", f"file already exists: {target.name}"
            )

        # 添加 BRAIN 标记 header
        ts = datetime.now(UTC).isoformat()
        brain_header = (
            f"{_facade_mod._BRAIN_MARKER} generated: {ts}\n"
            f"{_facade_mod._BRAIN_MARKER} description: {description}\n"
            f"{_facade_mod._BRAIN_MARKER} source: code_generate inference\n\n"
        )
        full_content = brain_header + content
        if not full_content.endswith("\n"):
            full_content += "\n"

        if self._dry_run:
            _log.info("BrainHands: (dry-run) would create %s", target.relative_to(_facade_mod.REPO_ROOT))
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(full_content, encoding="utf-8")

        _log.info("BrainHands: created %s (%d chars)", target.relative_to(_facade_mod.REPO_ROOT), len(content))
        return _facade_mod.ActionReport(
            str(target.relative_to(_facade_mod.REPO_ROOT)),
            "code_generate",
            "created",
            f"{len(content)} chars, {description[:60]}",
        )

    def delete_file(self, source_text: str, result: dict):
        """将文件移到 .brain_trash/ 回收站而非永久删除。

        支持从 result 中解析文件路径或模块名。
        """
        # Use facade methods (patchable in tests)
        module_name = self._facade._extract_module_name(source_text)
        target_file = self._facade._find_module_file(module_name)

        if target_file is None:
            # 尝试从 result 中获取路径
            file_path_hint = result.get("file_path", "")
            if file_path_hint:
                target_file = _facade_mod.REPO_ROOT / file_path_hint
            elif module_name:
                target_file = self._facade._parse_file_path(source_text)

        if target_file is None:
            return _facade_mod.ActionReport(module_name, "dead_code_removal", "skipped", "file not found")
        if not target_file.exists():
            return _facade_mod.ActionReport(module_name, "dead_code_removal", "skipped", "file does not exist")

        _facade_mod.BRAIN_TRASH_DIR.mkdir(parents=True, exist_ok=True)

        ts = datetime.now(UTC).strftime("%Y%m%dT%H%M%S")
        trash_name = f"{ts}_{target_file.name}"
        trash_path = _facade_mod.BRAIN_TRASH_DIR / trash_name

        # 记录 trash manifest
        manifest_entry = json.dumps(
            {
                "original": str(target_file.relative_to(_facade_mod.REPO_ROOT)),
                "trashed_as": trash_name,
                "timestamp": datetime.now(UTC).isoformat(),
                "git_commit": _facade_mod._git_commit_hash(_facade_mod.REPO_ROOT),
            },
            ensure_ascii=False,
        )

        trash_manifest = _facade_mod.BRAIN_TRASH_DIR / "trash_manifest.jsonl"
        with open(trash_manifest, "a", encoding="utf-8") as f:
            f.write(manifest_entry + "\n")

        # 先做版本链备份
        self._facade._version_backup(target_file)

        if self._dry_run:
            _log.info("BrainHands: (dry-run) would trash %s", target_file.name)
        else:
            shutil.move(str(target_file), str(trash_path))

        _log.info("BrainHands: trashed %s -> %s", target_file.name, trash_name)
        return _facade_mod.ActionReport(
            str(target_file.relative_to(_facade_mod.REPO_ROOT)),
            "dead_code_removal",
            "deleted",
            f"moved to .brain_trash/{trash_name}",
        )
