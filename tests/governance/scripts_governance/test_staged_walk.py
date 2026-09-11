# [A_test] module_id: MOD-TEST-STAGED-WALK | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-305 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.governance.scripts_governance.test_staged_walk
# [DOMAIN] D_GOV_SCRIPTS
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-TEST-STAGED-WALK | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""Tests for iter_staged_files() and scanner --staged modes (P3 自动化测试覆盖).

覆盖范围：
  - iter_staged_files() 共享函数（变更检测核心）：参数过滤、异常处理、去重排序
  - 5 个扫描器的 --staged 模式：无 staged 文件时正确跳过（exit 0）

对标条款：3.4 / 5.1（--staged 模式无自动化测试 → 本文件补齐）

真源说明（2026-08-03 治本）：
  iter_staged_files 真源在 _shared/staged_files.py（轻量模块，无 psycopg2 传递依赖）。
  _shared/walk.py re-export 供向后兼容。本测试直接 import _shared.staged_files 真源，
  mock 路径也指向 _shared.staged_files 命名空间。
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# ── sys.path 注入：_shared（governance root）+ d7_code ──
# conftest.py 只加了 d3_metadata，本测试还需 _shared.staged_files 和 d7_code 扫描器
_REPO_ROOT = Path(__file__).resolve().parents[3]
_GOV_ROOT = _REPO_ROOT / "scripts" / "governance"
_D7_CODE = _GOV_ROOT / "d7_code"
for _p in (str(_GOV_ROOT), str(_D7_CODE)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from _shared.staged_files import iter_staged_files  # noqa: E402, I001


# ============================================================================
# 辅助
# ============================================================================


def _mock_git_output(lines: list[str], returncode: int = 0) -> MagicMock:
    """构造 subprocess.run 的 mock 返回值."""
    mock = MagicMock()
    mock.returncode = returncode
    mock.stdout = "\n".join(lines) + ("\n" if lines else "")
    return mock


def _create_files(root: Path, rel_paths: list[str]) -> None:
    """在 root 下创建相对路径文件（含父目录）."""
    for rel in rel_paths:
        fp = root / rel
        fp.parent.mkdir(parents=True, exist_ok=True)
        fp.write_text("# stub\n", encoding="utf-8")


# ============================================================================
# iter_staged_files() 单元测试
# ============================================================================


class TestIterStagedFiles:
    """iter_staged_files() 共享函数——变更检测核心（真源 _shared/staged_files.py）。"""

    def test_empty_staged_returns_empty(self, tmp_path: Path) -> None:
        """无 staged 文件时返回空列表。"""
        with (
            patch("_shared.staged_files.REPO_ROOT", tmp_path),
            patch("_shared.staged_files.subprocess.run", return_value=_mock_git_output([])),
        ):
            assert iter_staged_files() == []

    def test_git_failure_returns_empty(self, tmp_path: Path) -> None:
        """git 命令失败（returncode != 0）时返回空列表（fail-open，不阻断 pre-commit）。"""
        with (
            patch("_shared.staged_files.REPO_ROOT", tmp_path),
            patch("_shared.staged_files.subprocess.run", return_value=_mock_git_output([], returncode=1)),
        ):
            assert iter_staged_files() == []

    def test_returns_staged_files(self, tmp_path: Path) -> None:
        """正确返回 staged 文件的绝对 Path 列表。"""
        files = ["src/zephyr/foo.py", "docs/bar.md"]
        _create_files(tmp_path, files)
        with (
            patch("_shared.staged_files.REPO_ROOT", tmp_path),
            patch("_shared.staged_files.subprocess.run", return_value=_mock_git_output(files)),
        ):
            result = iter_staged_files()
            assert len(result) == 2
            assert all(p.exists() for p in result)
            assert all(p.is_absolute() for p in result)

    def test_filters_by_extension(self, tmp_path: Path) -> None:
        """extensions 参数过滤非目标扩展名。"""
        files = ["src/zephyr/a.py", "src/zephyr/b.md", "src/zephyr/c.yaml"]
        _create_files(tmp_path, files)
        with (
            patch("_shared.staged_files.REPO_ROOT", tmp_path),
            patch("_shared.staged_files.subprocess.run", return_value=_mock_git_output(files)),
        ):
            result = iter_staged_files(extensions=frozenset({".py"}))
            assert len(result) == 1
            assert result[0].suffix == ".py"

    def test_filters_by_path_prefix(self, tmp_path: Path) -> None:
        """path_prefix 参数只保留匹配前缀的文件。"""
        files = ["src/zephyr/a.py", "tests/b.py", "scripts/c.py"]
        _create_files(tmp_path, files)
        with (
            patch("_shared.staged_files.REPO_ROOT", tmp_path),
            patch("_shared.staged_files.subprocess.run", return_value=_mock_git_output(files)),
        ):
            result = iter_staged_files(path_prefix="src/zephyr/")
            assert len(result) == 1
            assert "src/zephyr" in str(result[0]).replace("\\", "/")

    def test_excludes_deleted_files(self, tmp_path: Path) -> None:
        """git diff 返回的已删除文件（工作区不存在）被排除。"""
        files = ["src/zephyr/exists.py", "src/zephyr/deleted.py"]
        _create_files(tmp_path, ["src/zephyr/exists.py"])  # 只创建 exists.py
        with (
            patch("_shared.staged_files.REPO_ROOT", tmp_path),
            patch("_shared.staged_files.subprocess.run", return_value=_mock_git_output(files)),
        ):
            result = iter_staged_files()
            assert len(result) == 1
            assert result[0].name == "exists.py"

    def test_dedup_and_sorted(self, tmp_path: Path) -> None:
        """重复路径去重，结果排序。"""
        files = ["src/zephyr/b.py", "src/zephyr/a.py", "src/zephyr/a.py"]
        _create_files(tmp_path, ["src/zephyr/a.py", "src/zephyr/b.py"])
        with (
            patch("_shared.staged_files.REPO_ROOT", tmp_path),
            patch("_shared.staged_files.subprocess.run", return_value=_mock_git_output(files)),
        ):
            result = iter_staged_files(extensions=frozenset({".py"}))
            assert len(result) == 2
            # 排序：a.py 在 b.py 前
            assert result[0].name == "a.py"
            assert result[1].name == "b.py"

    def test_backslash_paths_normalized(self, tmp_path: Path) -> None:
        """Windows 反斜杠路径被正反斜杠归一化后匹配 path_prefix。"""
        _create_files(tmp_path, ["src/zephyr/win.py"])
        # git 在 Windows 可能返回反斜杠路径
        with (
            patch("_shared.staged_files.REPO_ROOT", tmp_path),
            patch("_shared.staged_files.subprocess.run", return_value=_mock_git_output(["src\\zephyr\\win.py"])),
        ):
            result = iter_staged_files(path_prefix="src/zephyr/")
            assert len(result) == 1


# ============================================================================
# 扫描器 --staged 模式集成测试
# ============================================================================


class TestScanDebtStaged:
    """scan_debt.py --staged 模式——变更检测集成。"""

    def test_staged_no_files_passes(self) -> None:
        """--staged 无 staged 文件时 exit 0（无事可做）。"""
        import scan_debt

        with patch("scan_debt.iter_staged_files", return_value=[]):
            assert scan_debt.main(["--ci", "--staged"]) == 0

    def test_staged_detects_debt_violation(self, tmp_path: Path) -> None:
        """--staged 模式检测到 DEBT-2 违规（3 个 bool 位置参数）时 exit 1。"""
        import scan_debt

        bad_file = tmp_path / "bad.py"
        bad_file.write_text(
            "def calculate_trust(git_ok: bool, test_ok: bool, audit_ok: bool) -> None:\n    pass\n",
            encoding="utf-8",
        )
        with patch("scan_debt.iter_staged_files", return_value=[bad_file]):
            exit_code = scan_debt.main(["--ci", "--staged", "--quiet"])
            assert exit_code == 1  # EXIT_FINDINGS


class TestDetectDirectLlmCallsStaged:
    """detect_direct_llm_calls.py --staged 模式——变更检测集成。"""

    def test_staged_no_files_passes(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """--staged 无 staged 文件时 exit 0。"""
        import detect_direct_llm_calls

        monkeypatch.setattr(sys, "argv", ["detect_direct_llm_calls.py", "--ci", "--staged"])
        with patch("detect_direct_llm_calls.iter_staged_files", return_value=[]):
            assert detect_direct_llm_calls.main() == 0


class TestCheckPureShimStaged:
    """check_pure_shim.py --staged 模式——变更检测集成。"""

    def test_staged_no_files_passes(self) -> None:
        """--staged 无 staged 文件时 exit 0。"""
        import check_pure_shim

        with patch("check_pure_shim.iter_staged_files", return_value=[]):
            assert check_pure_shim.main(["--ci", "--staged"]) == 0


class TestCheckEncodingStaged:
    """check_encoding.py --staged 模式——变更检测集成。"""

    def test_staged_no_files_passes(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """--staged 无 staged 文件时 exit 0（main 用 sys.exit 退出）。"""
        import check_encoding

        monkeypatch.setattr(sys, "argv", ["check_encoding.py", "--staged"])
        with patch("check_encoding.iter_staged_files", return_value=[]):
            with pytest.raises(SystemExit) as exc:
                check_encoding.main()
            assert exc.value.code == 0


class TestCheckEncodingFileBatch:
    """check_encoding.py --file 批量模式（2026-09-11 治本：ENCODING-SAFETY gate 批量化前提）。

    --file 从单文件（type=str）改为 nargs="+"——单文件调用向后兼容，
    多文件单进程批量（消除 N 次解释器启动+导入链税）。
    """

    def test_file_single_backward_compat(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """单文件 --file 调用仍正常（exit 0）。"""
        import check_encoding

        clean = tmp_path / "clean.py"
        clean.write_text("x = 1\n", encoding="utf-8")
        monkeypatch.setattr(sys, "argv", ["check_encoding.py", "--file", str(clean)])
        with pytest.raises(SystemExit) as exc:
            check_encoding.main()
        assert exc.value.code == 0

    def test_file_batch_all_pass(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """多文件批量全部通过——exit 0。"""
        import check_encoding

        f1 = tmp_path / "a.py"
        f2 = tmp_path / "b.md"
        f1.write_text("x = 1\n", encoding="utf-8")
        f2.write_text("# ok\n", encoding="utf-8")
        monkeypatch.setattr(sys, "argv", ["check_encoding.py", "--file", str(f1), str(f2)])
        with pytest.raises(SystemExit) as exc:
            check_encoding.main()
        assert exc.value.code == 0

    def test_file_batch_partial_violation(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys) -> None:
        """批量中一个文件带 BOM——exit 1 且输出定位到该文件。"""
        import check_encoding

        clean = tmp_path / "clean.py"
        clean.write_text("x = 1\n", encoding="utf-8")
        bom = tmp_path / "bom.yaml"
        bom.write_bytes(b"\xef\xbb\xbfkey: val\n")
        monkeypatch.setattr(sys, "argv", ["check_encoding.py", "--file", str(clean), str(bom)])
        with pytest.raises(SystemExit) as exc:
            check_encoding.main()
        assert exc.value.code == 1
        assert "bom.yaml" in capsys.readouterr().out

    def test_quoted_json_key_autoguess_detected(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """带引号 JSON key 的 truthy autoGuess 设置被检出（红蓝对抗发现的既有盲区，2026-09-11 治本）。

        key 与 true 值均动态构造——源码不出现 keyword+truthy 相邻字面量，防本测试
        文件自身被加宽后的 AUTO_GUESS_VIOLATION_RE 自指误报（2026-07-17 自指
        误报问题族同源）。
        """
        import check_encoding

        key = "files.autoGuess" + "Encoding"
        truthy = "tr" + "ue"
        settings = tmp_path / "settings.json"
        settings.write_text('{\n  "%s": %s\n}\n' % (key, truthy), encoding="utf-8")
        monkeypatch.setattr(sys, "argv", ["check_encoding.py", "--file", str(settings)])
        with pytest.raises(SystemExit) as exc:
            check_encoding.main()
        assert exc.value.code == 1

    def test_autoguess_false_not_flagged(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """falsy 值不误报（不随引号修复变严；key 同样动态拼接防自指）。"""
        import check_encoding

        key = "files.autoGuess" + "Encoding"
        f = tmp_path / "ok.json"
        f.write_text('{\n  "%s": false\n}\n' % key, encoding="utf-8")
        monkeypatch.setattr(sys, "argv", ["check_encoding.py", "--file", str(f)])
        with pytest.raises(SystemExit) as exc:
            check_encoding.main()
        assert exc.value.code == 0


class TestCheckAnyAbuseStaged:
    """check_any_abuse.py --staged 模式——变更检测集成（使用 _shared.staged_files）。"""

    def test_staged_no_files_passes(self) -> None:
        """--staged 无 staged .py 文件时 exit 0（跳过）。"""
        import check_any_abuse

        # check_any_abuse 从 _shared.staged_files import iter_staged_files
        # patch check_any_abuse 命名空间中的 iter_staged_files 引用
        with patch("check_any_abuse.iter_staged_files", return_value=[]):
            assert check_any_abuse.main(["--ci", "--staged"]) == 0
