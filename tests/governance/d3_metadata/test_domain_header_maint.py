# [A_test] module_id: MOD-GOV_domain_header_maint_tests | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-005 | scripts/governance/d3_metadata/domain_header_maint.py | §
# [MODULE] tests.governance.d3_metadata.test_domain_header_maint
# [DOMAIN] D_GOV_SCRIPTS
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] permanent
"""test_domain_header_maint.py — domain_header_maint.py 单元测试

测试组：
- TestClassifyFile: classify_file 在各种文件内容下的分类
  - ok / missing / no_module / domain_only / empty_file / 50行截断
- TestVerifyFile: _verify_file header 格式校验
  - ok / missing / position_error / empty_value / no_module / not_exist / ok_with_warn
- TestReadHead: _read_head 读取头部逻辑
  - 正常文件 / 空文件 / 长文件截断 / IO异常
- TestIsProcessAlive: is_process_alive 进程检测
  - 当前进程 / 不存在PID / 零/负PID
- TestShouldSkip: _should_skip 跳过逻辑
- TestCleanLock: cmd_clean_lock 孤儿锁清理
  - 无锁 / 孤儿锁 / 活跃锁 / 强制清理 / 损坏锁
- TestCmdScan: cmd_scan 扫描子命令
  - 全OK / 有缺失 / 有空值

测试隔离：tmp_path 构造临时文件，monkeypatch 替换模块级 REPO/SCAN_DIRS/COMMIT_LOCK_FILE，
不读/不写真实仓库。
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
_SCRIPTS_DIR = _PROJECT_ROOT / "scripts" / "governance" / "d3_metadata"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

import domain_header_maint as dhm  # noqa: E402
from domain_header_maint import (  # noqa: E402
    _read_head,
    _should_skip,
    _verify_file,
    classify_file,
    cmd_clean_lock,
    cmd_scan,
    is_process_alive,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_OK_HEADER = """\
# [A_test] module_id: MOD-FOO | layer=test | stability=volatile | safety=L
# [BLUEPRINT] MOD-FOO | blueprint.md | §
# [MODULE] tests.foo.test_bar
# [DOMAIN] D_GOVERNANCE
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] permanent
\"\"\"docstring\"\"\"
"""

_MISSING_DOMAIN_HEADER = """\
# [A_test] module_id: MOD-FOO | layer=test
# [BLUEPRINT] MOD-FOO | blueprint.md
# [MODULE] tests.foo.test_bar
# [STABILITY] evolving
# [SAFETY] L
\"\"\"docstring\"\"\"
"""

_DOMAIN_ONLY_HEADER = """\
# [BLUEPRINT] MOD-FOO | blueprint.md
# [DOMAIN] D_DATA
# [TTL] permanent
\"\"\"docstring\"\"\"
"""

_NO_HEADER = """\
\"\"\"just a docstring\"\"\"
import os
"""


def _write(tmp_path: Path, name: str, content: str) -> Path:
    """在 tmp_path 下写一个文件，返回路径。"""
    p = tmp_path / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return p


# ---------------------------------------------------------------------------
# TestClassifyFile
# ---------------------------------------------------------------------------

class TestClassifyFile:
    """验证 classify_file() 在各种文件内容下的分类。"""

    def test_ok_file(self, tmp_path):
        """有 [MODULE] 且有 [DOMAIN] → ok。"""
        p = _write(tmp_path, "ok.py", _OK_HEADER)
        status, dom = classify_file(p)
        assert status == "ok"
        assert dom == "D_GOVERNANCE"

    def test_missing_domain(self, tmp_path):
        """有 [MODULE] 但无 [DOMAIN] → missing。"""
        p = _write(tmp_path, "missing.py", _MISSING_DOMAIN_HEADER)
        status, dom = classify_file(p)
        assert status == "missing"
        assert dom is None

    def test_no_module(self, tmp_path):
        """无 [MODULE] → no_module。"""
        p = _write(tmp_path, "no_mod.py", _DOMAIN_ONLY_HEADER)
        status, _ = classify_file(p)
        assert status == "domain_only"

    def test_domain_only(self, tmp_path):
        """有 [DOMAIN] 但无 [MODULE] → domain_only。"""
        p = _write(tmp_path, "dom_only.py", _DOMAIN_ONLY_HEADER)
        status, dom = classify_file(p)
        assert status == "domain_only"
        assert dom == "D_DATA"

    def test_empty_file(self, tmp_path):
        """空文件 → no_module（关键：非 read_error）。"""
        p = _write(tmp_path, "empty.py", "")
        status, _ = classify_file(p)
        assert status == "no_module"

    def test_no_header_at_all(self, tmp_path):
        """完全无 header 的文件 → no_module。"""
        p = _write(tmp_path, "plain.py", _NO_HEADER)
        status, _ = classify_file(p)
        assert status == "no_module"

    def test_module_after_50_lines(self, tmp_path):
        """[MODULE] 在50行之后 → no_module（只读前50行）。"""
        content = "\n".join(f"# line {i}" for i in range(1, 55))
        content += "\n# [MODULE] foo\n# [DOMAIN] D_BAR\n"
        p = _write(tmp_path, "late.py", content)
        status, _ = classify_file(p)
        assert status == "no_module"

    def test_domain_exactly_at_line_50(self, tmp_path):
        """[MODULE] 在第49行，[DOMAIN] 在第50行 → ok（边界值）。"""
        lines = [f"# line {i}" for i in range(1, 49)]
        lines.append("# [MODULE] foo")
        lines.append("# [DOMAIN] D_BAR")
        p = _write(tmp_path, "boundary.py", "\n".join(lines) + "\n")
        status, dom = classify_file(p)
        assert status == "ok"
        assert dom == "D_BAR"

    def test_domain_with_hash_no_space(self, tmp_path):
        """#[MODULE] 无空格也能匹配。"""
        content = "#[MODULE]foo\n#[DOMAIN]D_BAR\n"
        p = _write(tmp_path, "nospace.py", content)
        status, dom = classify_file(p)
        assert status == "ok"
        assert dom == "D_BAR"

    def test_nonexistent_file(self, tmp_path):
        """不存在的文件 → read_error。"""
        p = tmp_path / "nonexistent.py"
        status, _ = classify_file(p)
        assert status == "read_error"

    def test_only_docstring_no_header(self, tmp_path):
        """只有 docstring 没有代码/header → no_module。"""
        p = _write(tmp_path, "docstring.py", '"""just a docstring"""\n')
        status, _ = classify_file(p)
        assert status == "no_module"

    def test_only_whitespace_lines(self, tmp_path):
        """只有空白行 → no_module。"""
        p = _write(tmp_path, "whitespace.py", "\n\n\n\n")
        status, _ = classify_file(p)
        assert status == "no_module"

    def test_only_comments_no_header(self, tmp_path):
        """只有普通注释（无 header）→ no_module。"""
        p = _write(tmp_path, "comments.py", "# just a comment\n# another comment\n")
        status, _ = classify_file(p)
        assert status == "no_module"

    def test_no_trailing_newline(self, tmp_path):
        """无换行符结尾也能正确匹配 header → ok。"""
        p = _write(tmp_path, "nonewline.py", "# [MODULE] foo\n# [DOMAIN] D_BAR")
        status, dom = classify_file(p)
        assert status == "ok"
        assert dom == "D_BAR"

    def test_domain_after_docstring(self, tmp_path):
        """[DOMAIN] 在 docstring 之后（50行内）→ ok（classify 不检查位置）。"""
        content = (
            "# [MODULE] tests.foo\n"
            '"""docstring\nmulti line\n"""\n'
            "# [DOMAIN] D_LATE\n"
        )
        p = _write(tmp_path, "dom_after_doc.py", content)
        status, dom = classify_file(p)
        assert status == "ok"
        assert dom == "D_LATE"


# ---------------------------------------------------------------------------
# TestVerifyFile
# ---------------------------------------------------------------------------

class TestVerifyFile:
    """验证 _verify_file() header 格式校验。"""

    def test_ok(self, tmp_path, monkeypatch):
        """正确格式 → ok。"""
        monkeypatch.setattr(dhm, "REPO", tmp_path)
        _write(tmp_path, "ok.py", _OK_HEADER)
        status, dom = _verify_file("ok.py")
        assert status == "ok"
        assert dom == "D_GOVERNANCE"

    def test_missing_domain(self, tmp_path, monkeypatch):
        """有 MODULE 无 DOMAIN → missing。"""
        monkeypatch.setattr(dhm, "REPO", tmp_path)
        _write(tmp_path, "miss.py", _MISSING_DOMAIN_HEADER)
        status, _ = _verify_file("miss.py")
        assert status == "missing"

    def test_position_error(self, tmp_path, monkeypatch):
        """DOMAIN 在 MODULE 之前 → position_error。"""
        monkeypatch.setattr(dhm, "REPO", tmp_path)
        content = "# [DOMAIN] D_FOO\n# [MODULE] foo\n"
        _write(tmp_path, "pos.py", content)
        status, detail = _verify_file("pos.py")
        assert status == "position_error"
        assert "之前" in detail

    def test_empty_value(self, tmp_path, monkeypatch):
        """DOMAIN 值为 # → empty_value。"""
        monkeypatch.setattr(dhm, "REPO", tmp_path)
        content = "# [MODULE] foo\n# [DOMAIN]\n# next line\n"
        _write(tmp_path, "empty_val.py", content)
        status, detail = _verify_file("empty_val.py")
        assert status == "empty_value"

    def test_no_module(self, tmp_path, monkeypatch):
        """无 MODULE → no_module。"""
        monkeypatch.setattr(dhm, "REPO", tmp_path)
        _write(tmp_path, "no_mod.py", _NO_HEADER)
        status, _ = _verify_file("no_mod.py")
        assert status == "no_module"

    def test_not_exist(self, tmp_path, monkeypatch):
        """文件不存在 → not_exist。"""
        monkeypatch.setattr(dhm, "REPO", tmp_path)
        status, _ = _verify_file("nonexistent.py")
        assert status == "not_exist"

    def test_ok_with_warn(self, tmp_path, monkeypatch):
        """MODULE 和 DOMAIN 之间有内容 → ok_with_warn。"""
        monkeypatch.setattr(dhm, "REPO", tmp_path)
        content = (
            "# [MODULE] foo\n"
            "# [STABILITY] evolving\n"
            "# [DOMAIN] D_BAR\n"
        )
        _write(tmp_path, "warn.py", content)
        status, detail = _verify_file("warn.py")
        assert status == "ok_with_warn"
        assert "STABILITY" in detail

    def test_empty_file(self, tmp_path, monkeypatch):
        """空文件 → no_module（非 read_error）。"""
        monkeypatch.setattr(dhm, "REPO", tmp_path)
        _write(tmp_path, "empty.py", "")
        status, _ = _verify_file("empty.py")
        assert status == "no_module"

    def test_domain_in_template_string(self, tmp_path, monkeypatch):
        """模板字符串中的 [DOMAIN] 不干扰头部校验（只读前50行）。"""
        monkeypatch.setattr(dhm, "REPO", tmp_path)
        content = (
            "# [MODULE] foo\n"
            "# [DOMAIN] D_BAR\n"
            "# [TTL] permanent\n"
            "\"\"\"docstring\"\"\"\n"
            "_TEMPLATE = \"\"\"# [DOMAIN] D_FAKE\"\"\"\n"
        )
        _write(tmp_path, "tmpl.py", content)
        status, dom = _verify_file("tmpl.py")
        assert status == "ok"
        assert dom == "D_BAR"

    def test_verify_domain_after_docstring(self, tmp_path, monkeypatch):
        """[DOMAIN] 在 docstring 之后 → ok_with_warn（verify 检查位置，classify 不检查）。

        这验证了 classify_file 和 _verify_file 的设计差异：
        - classify_file 只关心有无 MODULE/DOMAIN → ok
        - _verify_file 额外检查 MODULE 和 DOMAIN 之间有无内容 → ok_with_warn
        """
        monkeypatch.setattr(dhm, "REPO", tmp_path)
        content = (
            "# [MODULE] tests.foo\n"
            '"""docstring\nmulti line\n"""\n'
            "# [DOMAIN] D_LATE\n"
        )
        _write(tmp_path, "dom_after_doc.py", content)
        status, detail = _verify_file("dom_after_doc.py")
        assert status == "ok_with_warn"
        assert "docstring" in detail

    def test_verify_only_docstring(self, tmp_path, monkeypatch):
        """只有 docstring 无 header → no_module。"""
        monkeypatch.setattr(dhm, "REPO", tmp_path)
        _write(tmp_path, "doc.py", '"""just a docstring"""\n')
        status, _ = _verify_file("doc.py")
        assert status == "no_module"

    def test_verify_only_whitespace(self, tmp_path, monkeypatch):
        """只有空白行 → no_module。"""
        monkeypatch.setattr(dhm, "REPO", tmp_path)
        _write(tmp_path, "ws.py", "\n\n\n\n")
        status, _ = _verify_file("ws.py")
        assert status == "no_module"


# ---------------------------------------------------------------------------
# TestReadHead
# ---------------------------------------------------------------------------

class TestReadHead:
    """验证 _read_head() 读取头部逻辑。"""

    def test_normal_file(self, tmp_path):
        """正常文件返回前50行。"""
        content = "\n".join(f"# line {i}" for i in range(1, 10))
        p = _write(tmp_path, "normal.py", content)
        head = _read_head(p)
        assert head is not None
        assert "# line 1" in head
        assert "# line 9" in head

    def test_empty_file(self, tmp_path):
        """空文件返回空字符串（非 None）。"""
        p = _write(tmp_path, "empty.py", "")
        head = _read_head(p)
        assert head == ""

    def test_long_file_truncated(self, tmp_path):
        """超过50行的文件只返回前50行。"""
        content = "\n".join(f"# line {i}" for i in range(1, 100))
        p = _write(tmp_path, "long.py", content)
        head = _read_head(p)
        assert head is not None
        lines = head.split("\n")
        assert len(lines) == 50
        assert "# line 1" in head
        assert "# line 50" in head
        assert "# line 51" not in head

    def test_nonexistent_file(self, tmp_path):
        """不存在的文件返回 None。"""
        p = tmp_path / "nonexistent.py"
        head = _read_head(p)
        assert head is None


# ---------------------------------------------------------------------------
# TestIsProcessAlive
# ---------------------------------------------------------------------------

class TestIsProcessAlive:
    """验证 is_process_alive() 进程检测。"""

    def test_current_process_alive(self):
        """当前进程 PID → True。"""
        assert is_process_alive(os.getpid()) is True

    def test_nonexistent_pid(self):
        """不存在的 PID → False。"""
        # 使用一个几乎不可能存在的 PID
        assert is_process_alive(999999) is False

    def test_zero_pid(self):
        """PID=0 → False。"""
        assert is_process_alive(0) is False

    def test_negative_pid(self):
        """负 PID → False。"""
        assert is_process_alive(-1) is False


# ---------------------------------------------------------------------------
# TestShouldSkip
# ---------------------------------------------------------------------------

class TestShouldSkip:
    """验证 _should_skip() 跳过逻辑。"""

    def test_py_file_not_skipped(self):
        """.py 文件 → False（不跳过）。"""
        assert _should_skip(Path("src/foo.py")) is False

    def test_non_py_file(self):
        """非 .py 文件 → True（跳过）。"""
        assert _should_skip(Path("src/foo.txt")) is True
        assert _should_skip(Path("src/foo.md")) is True

    def test_pycache_skipped(self):
        """__pycache__ 下的文件 → True。"""
        assert _should_skip(Path("src/__pycache__/foo.py")) is True

    def test_venv_skipped(self):
        """.venv 下的文件 → True。"""
        assert _should_skip(Path(".venv/lib/foo.py")) is True

    def test_runtime_skipped(self):
        """.runtime 下的文件 → True。"""
        assert _should_skip(Path(".runtime/tmp/foo.py")) is True


# ---------------------------------------------------------------------------
# TestCleanLock
# ---------------------------------------------------------------------------

class TestCleanLock:
    """验证 cmd_clean_lock() 孤儿锁清理。"""

    def test_no_lock_file(self, tmp_path, monkeypatch, capsys):
        """无锁文件 → exit 0。"""
        monkeypatch.setattr(dhm, "COMMIT_LOCK_FILE", tmp_path / "nonexistent.lock")
        monkeypatch.setattr(dhm, "REPO", tmp_path)
        args = argparse.Namespace(remove=False, force=False)
        rc = cmd_clean_lock(args)
        assert rc == 0
        out = capsys.readouterr().out
        assert "无需清理" in out

    def test_orphan_lock_detected(self, tmp_path, monkeypatch, capsys):
        """孤儿锁（PID 已死）→ 报告，返回 1（未 --remove）。"""
        lock_file = tmp_path / "git_commit_global.lock"
        lock_file.write_text(json.dumps({"pid": 999999, "acquired_at": 0}), encoding="utf-8")
        monkeypatch.setattr(dhm, "COMMIT_LOCK_FILE", lock_file)
        monkeypatch.setattr(dhm, "REPO", tmp_path)
        args = argparse.Namespace(remove=False, force=False)
        rc = cmd_clean_lock(args)
        assert rc == 1
        out = capsys.readouterr().out
        assert "孤儿锁" in out
        assert lock_file.exists()  # 未清理

    def test_orphan_lock_removed(self, tmp_path, monkeypatch, capsys):
        """孤儿锁 + --remove → 清理，exit 0。"""
        lock_file = tmp_path / "git_commit_global.lock"
        lock_file.write_text(json.dumps({"pid": 999999, "acquired_at": 0}), encoding="utf-8")
        monkeypatch.setattr(dhm, "COMMIT_LOCK_FILE", lock_file)
        monkeypatch.setattr(dhm, "REPO", tmp_path)
        args = argparse.Namespace(remove=True, force=False)
        rc = cmd_clean_lock(args)
        assert rc == 0
        out = capsys.readouterr().out
        assert "已清理" in out
        assert not lock_file.exists()

    def test_active_lock_not_removed(self, tmp_path, monkeypatch, capsys):
        """活跃锁（当前进程）→ 报告但不清理，exit 1。"""
        lock_file = tmp_path / "git_commit_global.lock"
        lock_file.write_text(
            json.dumps({"pid": os.getpid(), "acquired_at": 0}), encoding="utf-8"
        )
        monkeypatch.setattr(dhm, "COMMIT_LOCK_FILE", lock_file)
        monkeypatch.setattr(dhm, "REPO", tmp_path)
        args = argparse.Namespace(remove=False, force=False)
        rc = cmd_clean_lock(args)
        assert rc == 1
        out = capsys.readouterr().out
        assert "仍在运行" in out
        assert lock_file.exists()  # 未清理

    def test_active_lock_force_removed(self, tmp_path, monkeypatch, capsys):
        """活跃锁 + --force → 强制清理，exit 0。"""
        lock_file = tmp_path / "git_commit_global.lock"
        lock_file.write_text(
            json.dumps({"pid": os.getpid(), "acquired_at": 0}), encoding="utf-8"
        )
        monkeypatch.setattr(dhm, "COMMIT_LOCK_FILE", lock_file)
        monkeypatch.setattr(dhm, "REPO", tmp_path)
        args = argparse.Namespace(remove=False, force=True)
        rc = cmd_clean_lock(args)
        assert rc == 0
        out = capsys.readouterr().out
        assert "已清理" in out
        assert not lock_file.exists()

    def test_corrupted_lock_force(self, tmp_path, monkeypatch, capsys):
        """损坏的锁文件 + --force → 清理，exit 0。"""
        lock_file = tmp_path / "git_commit_global.lock"
        lock_file.write_text("NOT JSON{{{", encoding="utf-8")
        monkeypatch.setattr(dhm, "COMMIT_LOCK_FILE", lock_file)
        monkeypatch.setattr(dhm, "REPO", tmp_path)
        args = argparse.Namespace(remove=False, force=True)
        rc = cmd_clean_lock(args)
        assert rc == 0
        out = capsys.readouterr().out
        assert "清理" in out
        assert not lock_file.exists()

    def test_lock_no_pid_field(self, tmp_path, monkeypatch, capsys):
        """锁文件无 PID 字段 → 损坏，exit 1（未 --force）。"""
        lock_file = tmp_path / "git_commit_global.lock"
        lock_file.write_text(json.dumps({"foo": "bar"}), encoding="utf-8")
        monkeypatch.setattr(dhm, "COMMIT_LOCK_FILE", lock_file)
        monkeypatch.setattr(dhm, "REPO", tmp_path)
        args = argparse.Namespace(remove=False, force=False)
        rc = cmd_clean_lock(args)
        assert rc == 1
        out = capsys.readouterr().out
        assert "损坏" in out or "PID" in out


# ---------------------------------------------------------------------------
# TestCmdScan
# ---------------------------------------------------------------------------

class TestCmdScan:
    """验证 cmd_scan() 扫描子命令。"""

    @pytest.fixture(autouse=True)
    def _clear_exclude_dirs(self, monkeypatch):
        """pytest 的 tmp_path 落在 .runtime/tmp/ 下，而 EXCLUDE_DIRS 包含
        '.runtime'，会导致 _should_skip 跳过所有测试文件。
        清空 EXCLUDE_DIRS 确保测试文件不被跳过。"""
        monkeypatch.setattr(dhm, "EXCLUDE_DIRS", set())

    def test_all_ok(self, tmp_path, monkeypatch, capsys):
        """所有文件都有 header → exit 0。"""
        _write(tmp_path, "ok1.py", _OK_HEADER)
        _write(tmp_path, "ok2.py", _OK_HEADER)
        monkeypatch.setattr(dhm, "SCAN_DIRS", [tmp_path])
        monkeypatch.setattr(dhm, "REPO", tmp_path)
        args = argparse.Namespace()
        rc = cmd_scan(args)
        assert rc == 0
        out = capsys.readouterr().out
        assert "无缺失" in out or "✅" in out

    def test_with_missing(self, tmp_path, monkeypatch, capsys):
        """有缺失文件 → exit 1。"""
        _write(tmp_path, "ok.py", _OK_HEADER)
        _write(tmp_path, "miss.py", _MISSING_DOMAIN_HEADER)
        monkeypatch.setattr(dhm, "SCAN_DIRS", [tmp_path])
        monkeypatch.setattr(dhm, "REPO", tmp_path)
        args = argparse.Namespace()
        rc = cmd_scan(args)
        assert rc == 1
        out = capsys.readouterr().out
        assert "1 个缺失" in out or "缺失" in out

    def test_with_empty_domain(self, tmp_path, monkeypatch, capsys):
        """有 [DOMAIN] 空值文件 → exit 1。"""
        _write(tmp_path, "ok.py", _OK_HEADER)
        _write(tmp_path, "empty_dom.py", "# [MODULE] foo\n# [DOMAIN]\n# next\n")
        monkeypatch.setattr(dhm, "SCAN_DIRS", [tmp_path])
        monkeypatch.setattr(dhm, "REPO", tmp_path)
        args = argparse.Namespace()
        rc = cmd_scan(args)
        assert rc == 1
        out = capsys.readouterr().out
        assert "空值" in out

    def test_empty_file_classified_as_no_module(self, tmp_path, monkeypatch, capsys):
        """空文件归入 no_module，不计入 missing → exit 0（如果其余都 ok）。"""
        _write(tmp_path, "ok.py", _OK_HEADER)
        _write(tmp_path, "empty.py", "")
        monkeypatch.setattr(dhm, "SCAN_DIRS", [tmp_path])
        monkeypatch.setattr(dhm, "REPO", tmp_path)
        args = argparse.Namespace()
        rc = cmd_scan(args)
        assert rc == 0
        out = capsys.readouterr().out
        # 空文件应出现在 NO_MODULE 统计中
        assert "NO_MODULE" in out

    def test_excluded_dirs_skipped(self, tmp_path, monkeypatch, capsys):
        """排除目录下的文件不扫描。"""
        # 恢复 EXCLUDE_DIRS（autouse fixture 清空了它）以测试排除逻辑
        monkeypatch.setattr(dhm, "EXCLUDE_DIRS", {"__pycache__", ".venv"})
        _write(tmp_path, "ok.py", _OK_HEADER)
        _write(tmp_path, "__pycache__/skip.py", _MISSING_DOMAIN_HEADER)
        _write(tmp_path, ".venv/lib/skip.py", _MISSING_DOMAIN_HEADER)
        monkeypatch.setattr(dhm, "SCAN_DIRS", [tmp_path])
        monkeypatch.setattr(dhm, "REPO", tmp_path)
        args = argparse.Namespace()
        rc = cmd_scan(args)
        assert rc == 0  # 排除目录中的 missing 不计入

    def test_domain_distribution(self, tmp_path, monkeypatch, capsys):
        """域分布统计正确。"""
        _write(tmp_path, "a.py", _OK_HEADER)  # D_GOVERNANCE
        content_b = (
            "# [MODULE] foo\n# [DOMAIN] D_DATA\n"
        )
        _write(tmp_path, "b.py", content_b)
        monkeypatch.setattr(dhm, "SCAN_DIRS", [tmp_path])
        monkeypatch.setattr(dhm, "REPO", tmp_path)
        args = argparse.Namespace()
        rc = cmd_scan(args)
        assert rc == 0
        out = capsys.readouterr().out
        assert "D_GOVERNANCE" in out
        assert "D_DATA" in out
