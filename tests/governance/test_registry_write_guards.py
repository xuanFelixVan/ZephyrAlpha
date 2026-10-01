# [A_test] module_id: zephyr.shared.io.file_utils | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §safe_write_text 注册表族质量守卫
# [MODULE] tests.governance.test_registry_write_guards
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] pytest; zephyr.shared.io.file_utils
# [CONSUMERS] pytest 自动发现
# [STARTUP] python -m pytest tests/governance/test_registry_write_guards.py
# [MATURITY] testing
# [INVARIANTS] 全 tmp 隔离（tmp 仓根 + tmp 注册表路径，monkeypatch 无生产写入）；守卫判据=删除行数 >0.5% 且未 allow_mass_edit → 拒写；allow_mass_edit=True 放行且审计留痕；非注册表路径零守卫（行为零变更）
# [MODIFY-GUARD] W4 防呆（2026-09-22 注册表事故，emomine 4772 条误删治本）DISPATCH_v1 Lane A 卡片
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即测试失败
# [TESTS] 本文件
# [TTL] permanent
"""test_registry_write_guards.py — safe_write_text 注册表族质量守卫（W4）正反例。"""

from __future__ import annotations

from pathlib import Path

import pytest

from zephyr.shared.io.file_utils import (
    RegistryMassEditRefused,
    content_sha256,
    safe_write_text,
)


def _catalog_file(tmp_path: Path, lines: int) -> tuple[Path, str]:
    """tmp 仓根下的注册表族文件（N 行条目）；返回 (path, 初始文本)。"""
    root = tmp_path / "repo"
    target = root / "docs/01_policies_and_standards/_registry/catalogs/w4_case.yaml"
    target.parent.mkdir(parents=True, exist_ok=True)
    text = "".join(f"- id: item_{i}\n  note: x\n" for i in range(lines))
    target.write_text(text, encoding="utf-8", newline="\n")
    return target, text


def _plain_file(tmp_path: Path, lines: int) -> tuple[Path, str]:
    """tmp 仓根下的非注册表文件（对照组）。"""
    root = tmp_path / "repo"
    target = root / "docs/_working/plain.yaml"
    target.parent.mkdir(parents=True, exist_ok=True)
    text = "".join(f"- id: item_{i}\n" for i in range(lines))
    target.write_text(text, encoding="utf-8", newline="\n")
    return target, text


class TestRegistryMassEditGuard:
    def test_mass_deletion_refused_without_flag(self, tmp_path: Path):
        """反例：删掉一半条目（4772 条误删复形）无旗 → RegistryMassEditRefused 拒写。"""
        target, old_text = _catalog_file(tmp_path, 100)
        new_text = "".join(f"- id: item_{i}\n  note: x\n" for i in range(50))  # 删一半
        with pytest.raises(RegistryMassEditRefused) as ei:
            safe_write_text(target, new_text, repo_root=tmp_path / "repo")
        assert ei.value.details["deleted_lines"] == 100 and ei.value.details["total_old_lines"] == 200
        assert target.read_text(encoding="utf-8") == old_text, "拒写=磁盘零变化"

    def test_small_edit_passes_without_flag(self, tmp_path: Path):
        """正例：0.5% 以内的删除（追加+微调）照常写入——守卫不伤正常登记。"""
        target, old_text = _catalog_file(tmp_path, 1000)  # 2000 行，阈值 10 行
        new_text = old_text + "- id: new_item\n  note: y\n"  # 纯插入零删除
        res = safe_write_text(target, new_text, repo_root=tmp_path / "repo")
        assert res.written is True
        assert "new_item" in target.read_text(encoding="utf-8")

    def test_mass_deletion_with_flag_passes_and_audits(self, tmp_path: Path):
        """显式 allow_mass_edit=True：批量删除放行 + 审计 registry_mass_edit_allowed 留痕。"""
        root = tmp_path / "repo"
        target, old_text = _catalog_file(tmp_path, 100)
        new_text = "".join(f"- id: item_{i}\n  note: x\n" for i in range(50))
        res = safe_write_text(target, new_text, repo_root=root, allow_mass_edit=True)
        assert res.written is True
        audit = (root / ".runtime/audit/safe_write.jsonl").read_text(encoding="utf-8")
        assert "registry_mass_edit_allowed" in audit

    def test_plain_path_not_guarded(self, tmp_path: Path):
        """对照组：非注册表路径大批删除照常写入（守卫作用域仅 catalogs 族）。"""
        target, _ = _plain_file(tmp_path, 100)
        new_text = "- id: only\n"
        res = safe_write_text(target, new_text, repo_root=tmp_path / "repo")
        assert res.written is True

    def test_new_file_creation_not_guarded(self, tmp_path: Path):
        """新建文件（无旧内容）零删除 → 守卫不拦。"""
        root = tmp_path / "repo"
        target = root / "docs/01_policies_and_standards/_registry/catalogs/new_reg.yaml"
        target.parent.mkdir(parents=True, exist_ok=True)
        res = safe_write_text(target, "- id: a\n", repo_root=root)
        assert res.written is True

    def test_guard_refuses_even_with_stale_base_order(self, tmp_path: Path):
        """守卫在 CAS 之后仍生效：base 对但大批删 → 拒（两层防线并存不互斥）。"""
        target, old_text = _catalog_file(tmp_path, 100)
        base = content_sha256(old_text)
        new_text = "".join(f"- id: item_{i}\n  note: x\n" for i in range(40))
        with pytest.raises(RegistryMassEditRefused):
            safe_write_text(target, new_text, expected_base_sha256=base, repo_root=tmp_path / "repo")

    def test_small_registry_single_line_edit_passes(self, tmp_path: Path):
        """B-F1 回归（st-ibt-remedy-cf-20260923）：70 行小册阈值原为 0.35 行，
        任何 1 行变更即拒写（N 账本 sync 考试尾步全局阻断病根）。max(1, ceil(0.5%×N))
        下限后单行编辑永不误炸。"""
        target, old_text = _catalog_file(tmp_path, 35)  # 70 行，旧阈值 0.35 行=1 行即炸
        new_text = old_text.replace("- id: item_0\n  note: x", "- id: item_0\n  note: fixed")
        res = safe_write_text(target, new_text, repo_root=tmp_path / "repo")
        assert res.written is True
        assert "note: fixed" in target.read_text(encoding="utf-8")

    def test_small_registry_two_line_deletion_still_refused(self, tmp_path: Path):
        """B-F1 反例：小册下限只救个位行编辑——删除超过 max(1, ceil(0.5%×N)) 行仍拒。"""
        target, old_text = _catalog_file(tmp_path, 35)  # 70 行，阈值 max(1, 1)=1
        lines = old_text.splitlines(keepends=True)
        new_text = "".join(lines[:-4])  # 删 4 行（2 条目）> 1
        with pytest.raises(RegistryMassEditRefused) as ei:
            safe_write_text(target, new_text, repo_root=tmp_path / "repo")
        assert ei.value.details["threshold"] == 1
        assert ei.value.details["deleted_lines"] == 4
