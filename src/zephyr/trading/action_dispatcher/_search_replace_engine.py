# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md | §5.150.7
# [MODULE] MOD-INF-035 | zephyr.trading.action_dispatcher._search_replace_engine
# [DOMAIN] D_TRADING
# [DEPENDENCIES] zephyr.trading.action_dispatcher (facade module: _facade_mod.REPO_ROOT/_read_text/ActionReport; facade ref: _extract_module_name/_find_module_file/_parse_file_path/_version_backup)
# [CONSUMERS] zephyr.trading.action_dispatcher.ActionDispatcher.__init__ (构造 _search_replace 实例)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 搜索替换引擎——对 .py 源文件执行精确/宽松字符串替换；通过 facade ref 访问 patchable 实例方法以支持 patch.object(d, "_method", ...) 测试；apply_replacement_entries 为纯函数 @staticmethod（无 I/O，可独立测试）
# [MODIFY-GUARD] 公共方法 search_replace_file/apply_replacement_entries/finalize_replacement 签名变更需同步 facade thin wrapper 与测试
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] search_replace_file 返回 ActionReport(status=skipped|search_replaced|error)；文件不存在/无匹配→skipped；dry_run 模式不写盘
# [TESTS] tests/action/test_action_dispatcher.py (TestActionDispatcherSearchReplace + TestActionDispatcherSearchReplacePaths)
# [A_module] module_id=MOD-INF-035 | layer=module | stability=stable | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""搜索替换引擎（从 ActionDispatcher._search_replace_file 及两个底层方法提取）。

职责：对 Python 源文件执行精确/宽松搜索替换，包含版本备份和 dry-run 保护。
通过 facade 引用访问 patchable 实例方法（_extract_module_name/_find_module_file/_version_backup 等）。
通过 _facade_mod 访问 patchable 模块级常量（_read_text/_log/ActionReport）。
"""

from __future__ import annotations

import logging
import re
from pathlib import Path

from zephyr.trading import action_dispatcher as _facade_mod

_log = logging.getLogger(__name__)


class SearchReplaceEngine:
    """搜索替换引擎。

    从 ActionDispatcher 提取，负责 LLM 推理结果中的 search_replace/delete 操作。
    module_name 提取和文件查找委托给 facade（patchable）。
    version_backup 由 facade 注入（patchable）。
    """

    def __init__(self, dry_run: bool, facade=None) -> None:
        self._dry_run = dry_run
        self._facade = facade
        self._stats: dict | None = None

    def set_stats(self, stats: dict) -> None:
        """由 facade 注入共享 _stats 字典。"""
        self._stats = stats

    def search_replace_file(
        self,
        source_text: str,
        result: dict,
        field: str = "fixes",
        remove: bool = False,
    ):
        """搜索替换入口：提取模块名 → 定位文件 → 应用替换 → 写回。"""
        # Use facade methods (patchable in tests)
        module_name = self._facade._extract_module_name(source_text)
        py_file = self._facade._find_module_file(module_name)
        if py_file is None:
            # 尝试从 source_text 里直接解析路径
            py_file = self._facade._parse_file_path(source_text)
        if py_file is None:
            return _facade_mod.ActionReport(
                module_name,
                "search_replace",
                "skipped",
                f"file not found for: {module_name}",
            )

        entries = result.get(field, [])
        if not entries:
            return _facade_mod.ActionReport(
                module_name,
                "search_replace",
                "skipped",
                f"empty {field}",
            )

        original = _facade_mod._read_text(py_file)
        if original is None:
            return _facade_mod.ActionReport(
                module_name,
                "search_replace",
                "error",
                "cannot read file",
            )

        modified, applied, failed, reasons = self.apply_replacement_entries(
            py_file,
            original,
            entries,
            remove,
        )
        return self.finalize_replacement(
            py_file,
            original,
            modified,
            applied,
            failed,
            reasons,
            remove,
        )

    @staticmethod
    def apply_replacement_entries(
        py_file: Path,
        original: str,
        entries: list,
        remove: bool,
    ) -> tuple[str, int, int, list[str]]:
        """逐条应用替换条目（精确匹配 → 宽松匹配回退）。

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
                    _log.debug(
                        "SearchReplace: old_str not found in %s: %r",
                        py_file.name,
                        old_str[:60],
                    )

        return modified, applied, failed, reasons

    def finalize_replacement(
        self,
        py_file: Path,
        original: str,
        modified: str,
        applied: int,
        failed: int,
        reasons: list[str],
        remove: bool,
    ):
        """验证修改 → 版本备份 → 写回文件 → 组装 ActionReport。"""
        if applied == 0:
            return _facade_mod.ActionReport(
                py_file.name,
                "search_replace",
                "skipped",
                f"{failed} match(es) failed",
            )
        if modified == original:
            return _facade_mod.ActionReport(
                py_file.name,
                "search_replace",
                "skipped",
                "unchanged",
            )

        # 对于 remove 操作，清理产生的多余空行
        if remove:
            modified = re.sub(r"\n{3,}", "\n\n", modified)

        # Use facade method (patchable in tests)
        backup_name = self._facade._version_backup(py_file)
        if backup_name and self._stats is not None:
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
            _log.warning(
                "BrainHands: %s SearchReplace applied=%d failed=%d",
                py_file.name,
                applied,
                failed,
            )
        else:
            _log.info(
                "BrainHands: %s SearchReplace applied=%d failed=%d",
                py_file.name,
                applied,
                failed,
            )
        return _facade_mod.ActionReport(
            py_file.name,
            "search_replace",
            "search_replaced",
            detail,
        )
