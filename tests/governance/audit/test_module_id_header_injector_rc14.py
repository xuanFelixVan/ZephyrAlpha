# [BLUEPRINT] MOD-INF-005 | docs/03_modules/_domain_governance/governance_automation/blueprint.md | §
# [MODULE] tests.governance.audit.test_module_id_header_injector_rc14
# [DOMAIN] D_GOV_AUDIT
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-INF-005 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_module_id_header_injector_rc14.py — RC-14 头注入器治本回归（裁定#338③ 工单）

真源：docs/_working/full-auto-chain/S11_assembled_backtest/nodes/
reconciler_event_trigger_chain_mining.md RC-14 行。

四缺陷 × 回归用例：
①  只看 content[:500] 的 [BLUEPRINT] 便整块前置注入
    → test_skip_when_header_line_beyond_500_chars
②  模板恒带 "# [TTL] permanent" ⇒ 已有 TTL 文件重复头
    → test_inject_skipped_for_existing_ttl_limited_preserves_value（工单钦定夹具）
    → test_inject_skipped_for_existing_ttl_beyond_head_window
③  [MODULE] 槽填散文 "(auto-injected by S4 reconciler)"
    → test_unknown_slot_when_blueprint_target_unresolved（unknown+计数告警）
    → test_resolved_slot_uses_declared_blueprint_path
④  module_id 由目录前缀反查猜出（MOD-ALT-001 错配 / 幻影 MOD-D5_ARCH_TOOLS）
    → test_infer_failsafe_without_declared_index
    → test_infer_rejects_undeclared_phantom_id
    → test_infer_skips_ambiguous_declared_dir
    → test_classify_end_to_end_phantom_never_written
    → test_classify_end_to_end_unique_declared_injected

去重工具（存量修复）：test_dedup_file_*（幂等/保真值）。

测试隔离：tmp_path 构造独立 project_root（含 docs/03_modules 蓝图 frontmatter 真源）；
depgraph 连接以 monkeypatch 打在 zephyr.governance.depgraph_schema 槽位（函数内
from-import 的真源），不触真实库；不写生产路径。
"""

from __future__ import annotations

import sys
import types
from pathlib import Path

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from zephyr.governance.audit import reconciliation_registry as rr  # noqa: E402

# 与被测函数同款幻影/错配实证 id（真源=mining RC-14 行）
_PHANTOM_ID = "MOD-D5_ARCH_TOOLS"
_MISMATCH_ID = "MOD-ALT-001"
_DECLARED_ID = "MOD-GOV_X"
_DECLARED_BP = "docs/03_modules/_domain_governance/gx/blueprint.md"


@pytest.fixture(autouse=True)
def _isolate_inject_stats():
    rr._reset_inject_stats()
    yield
    rr._reset_inject_stats()


def _make_project(tmp_path: Path, declared: dict[str, str] | None = None) -> Path:
    """构造隔离 project_root；declared 非空时落对应蓝图 frontmatter 真源。"""
    (tmp_path / "docs" / "03_modules").mkdir(parents=True, exist_ok=True)
    for mid, bp_rel in (declared or {}).items():
        bp = tmp_path / bp_rel
        bp.parent.mkdir(parents=True, exist_ok=True)
        bp.write_text(f"---\nmodule_id: {mid}\n---\n# blueprint\n", encoding="utf-8")
    return tmp_path


def _install_fake_depgraph(monkeypatch: pytest.MonkeyPatch, ids_by_call: list[list[str]]) -> None:
    """把 depgraph 连接 stub 进 from-import 真源槽位 zephyr.governance.depgraph_schema。"""
    calls = {"n": 0}

    class _FakeCur:
        def execute(self, sql, params):
            self._rows = [(x,) for x in ids_by_call[min(calls["n"], len(ids_by_call) - 1)]]

        def fetchall(self):
            return self._rows

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

    class _FakeConn:
        def cursor(self, *a, **k):
            calls["n"] += 1
            return _FakeCur()

        def close(self):
            pass

    fake_schema = types.ModuleType("zephyr.governance.depgraph_schema")
    fake_schema.get_depgraph_pg_connection = lambda *a, **k: _FakeConn()
    monkeypatch.setitem(sys.modules, "zephyr.governance.depgraph_schema", fake_schema)


class TestDefect12DuplicateHeader:
    """缺陷①②：重复头杜绝——已有 [TTL]/[BLUEPRINT] 行的文件一律跳过注入。"""

    def test_inject_skipped_for_existing_ttl_limited_preserves_value(self, tmp_path):
        """工单钦定夹具：对已含 [TTL] limited 的文件跑注入，断言 count("# [TTL]")==1 且原值保留。"""
        root = _make_project(tmp_path)
        rel = "src/pkg/mod_a.py"
        f = root / rel
        f.parent.mkdir(parents=True)
        original = "# [A_module] module_id=MOD-GOV_X | layer=module\n# [TTL] limited\n\nx = 1\n"
        f.write_text(original, encoding="utf-8")

        ok = rr._module_id_inject_header(root, rel, _DECLARED_ID, None)

        assert ok is False
        content = f.read_text(encoding="utf-8")
        assert content == original, "文件被改动——注入器必须原样跳过"
        assert content.count("# [TTL]") == 1
        assert "# [TTL] limited" in content
        assert rr._get_inject_stats()["skip_existing_header"] == 1

    def test_skip_when_header_line_beyond_500_chars(self, tmp_path):
        """缺陷①：[BLUEPRINT]/[TTL] 行在 500 字符窗口之外也必须判重（旧口径会漏）。"""
        root = _make_project(tmp_path)
        rel = "src/pkg/mod_b.py"
        f = root / rel
        f.parent.mkdir(parents=True)
        filler = "#" + "x" * 600 + "\n"
        f.write_text(filler + "# [TTL] permanent\n", encoding="utf-8")

        ok = rr._module_id_inject_header(root, rel, _DECLARED_ID, None)

        assert ok is False
        assert f.read_text(encoding="utf-8").count("# [TTL]") == 1


class TestDefect3Slots:
    """缺陷③：注入块各槽只允许真源解析值；解析不出落 unknown 并计数告警。"""

    def test_unknown_slot_when_blueprint_target_unresolved(self, tmp_path, caplog):
        root = _make_project(tmp_path)
        rel = "src/pkg/new_file.py"
        f = root / rel
        f.parent.mkdir(parents=True)
        f.write_text("value = 1\n", encoding="utf-8")

        ok = rr._module_id_inject_header(root, rel, _DECLARED_ID, None)

        assert ok is True
        content = f.read_text(encoding="utf-8")
        first, ttl = content.splitlines()[:2]
        assert first == f"# [BLUEPRINT] {_DECLARED_ID} | unknown | §"
        assert ttl == "# [TTL] permanent"
        assert "(auto-injected by S4 reconciler)" not in content, "散文槽禁令"
        assert rr._get_inject_stats()["unknown_blueprint_slot"] == 1
        assert any("unknown" in rec.message for rec in caplog.records), "计数告警必须可见"

    def test_resolved_slot_uses_declared_blueprint_path(self, tmp_path):
        root = _make_project(tmp_path)
        rel = "src/pkg/new_file2.py"
        f = root / rel
        f.parent.mkdir(parents=True)
        f.write_text("value = 2\n", encoding="utf-8")

        ok = rr._module_id_inject_header(root, rel, _DECLARED_ID, _DECLARED_BP)

        assert ok is True
        assert f.read_text(encoding="utf-8").startswith(
            f"# [BLUEPRINT] {_DECLARED_ID} | {_DECLARED_BP} | §\n"
        )
        assert rr._get_inject_stats()["unknown_blueprint_slot"] == 0


class TestDefect4NoGuess:
    """缺陷④：module_id 反查禁猜——未声明/多义/无索引一律跳过。"""

    def test_infer_failsafe_without_declared_index(self):
        assert rr._module_id_infer_from_dir("src/pkg/a.py", None) is None
        assert rr._get_inject_stats()["skip_no_declared_module"] == 1

    def test_infer_rejects_undeclared_phantom_id(self, tmp_path, monkeypatch):
        """幻影 id（depgraph 有、frontmatter 零声明）不得被反查采信。"""
        _make_project(tmp_path, declared={})
        _install_fake_depgraph(monkeypatch, [[_PHANTOM_ID]])

        got = rr._module_id_infer_from_dir("tests/d5/test_sync.py", {})

        assert got is None, f"幻影 {_PHANTOM_ID} 被猜中"
        assert rr._get_inject_stats()["skip_no_declared_module"] == 1

    def test_infer_skips_ambiguous_declared_dir(self, tmp_path, monkeypatch):
        """目录下多声明 id 共存（实测 MOD-ALT-001 错配形态）→ 拒绝猜测。"""
        _make_project(tmp_path, declared={_MISMATCH_ID: "docs/03_modules/a/bp.md", _DECLARED_ID: _DECLARED_BP})
        _install_fake_depgraph(monkeypatch, [[_MISMATCH_ID, _DECLARED_ID]])

        got = rr._module_id_infer_from_dir("tests/governance/test_x.py", rr._load_declared_blueprint_index(tmp_path))

        assert got is None

    def test_classify_end_to_end_phantom_never_written(self, tmp_path, monkeypatch):
        """端到端：同目录 depgraph 只回幻影 id → 不注入，幻影 id 不出现在任何文件头。"""
        root = _make_project(tmp_path, declared={_DECLARED_ID: _DECLARED_BP})
        rel = "tests/governance/test_target.py"
        f = root / rel
        f.parent.mkdir(parents=True)
        f.write_text("def test_ok():\n    assert True\n", encoding="utf-8")
        _install_fake_depgraph(monkeypatch, [[_PHANTOM_ID]])

        injected, skipped = rr._classify_headerless_files([str(f)], root)

        assert injected == []
        assert skipped == [rel]
        assert _PHANTOM_ID not in f.read_text(encoding="utf-8")
        assert "[BLUEPRINT]" not in f.read_text(encoding="utf-8")

    def test_classify_end_to_end_unique_declared_injected(self, tmp_path, monkeypatch):
        """端到端：depgraph 混回幻影 id 但声明集唯一收敛 → 注入真源槽值。"""
        root = _make_project(tmp_path, declared={_DECLARED_ID: _DECLARED_BP})
        rel = "src/pkg/child/new_mod.py"
        f = root / rel
        f.parent.mkdir(parents=True)
        f.write_text("const = 3\n", encoding="utf-8")
        _install_fake_depgraph(monkeypatch, [[_PHANTOM_ID, _DECLARED_ID, _MISMATCH_ID]])

        injected, skipped = rr._classify_headerless_files([str(f)], root)

        assert injected == [(rel, _DECLARED_ID)]
        assert skipped == []
        content = f.read_text(encoding="utf-8")
        assert content.startswith(f"# [BLUEPRINT] {_DECLARED_ID} | {_DECLARED_BP} | §\n# [TTL] permanent\n")
        for bad in (_PHANTOM_ID, _MISMATCH_ID):
            assert bad not in content


class TestDedupTool:
    """存量去重工具：幂等、保真值。"""

    @staticmethod
    def _load_tool():
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "dedup_ttl_headers",
            _PROJECT_ROOT / "scripts" / "governance" / "dedup_ttl_headers.py",
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    def test_dedup_file_drops_injected_block_keeps_original_ttl(self, tmp_path):
        tool = self._load_tool()
        f = tmp_path / "dup.py"
        f.write_text(
            f"# [BLUEPRINT] {_PHANTOM_ID} | {tool.INJECTED_PROSE} | §\n"
            "# [TTL] permanent\n"
            "# [A_module] module_id=MOD-GOV_SCRIPTS\n"
            "# [TTL] permanent\n"
            "\n"
            "x = 1\n",
            encoding="utf-8",
        )

        changed, _ = tool.dedup_file(f)

        assert changed is True
        content = f.read_text(encoding="utf-8")
        assert content.count("# [TTL]") == 1
        assert tool.INJECTED_PROSE not in content
        assert _PHANTOM_ID not in content

    def test_dedup_file_idempotent(self, tmp_path):
        tool = self._load_tool()
        f = tmp_path / "dup2.py"
        f.write_text(
            f"# [BLUEPRINT] MOD-A | {tool.INJECTED_PROSE} | §\n# [TTL] permanent\n# [TTL] limited\nv = 1\n",
            encoding="utf-8",
        )

        assert tool.dedup_file(f)[0] is True
        after_once = f.read_text(encoding="utf-8")
        changed, why = tool.dedup_file(f)

        assert changed is False
        assert why in ("too-short", "line1-not-injected-block"), f"二次运行动作异常: {why}"
        assert f.read_text(encoding="utf-8") == after_once
        assert "# [TTL] limited" in after_once, "原 TTL 值必须保留"

    def test_dedup_file_never_removes_only_ttl(self, tmp_path):
        """注入块是文件唯一 TTL 时不动（删除会制造无 TTL 半成品）。"""
        tool = self._load_tool()
        f = tmp_path / "only.py"
        f.write_text(f"# [BLUEPRINT] MOD-A | {tool.INJECTED_PROSE} | §\n# [TTL] permanent\nv = 1\n", encoding="utf-8")

        changed, why = tool.dedup_file(f)

        assert changed is False
        assert why == "injected-block-is-only-ttl"
        assert f.read_text(encoding="utf-8").count("# [TTL]") == 1

    def test_classify_rejects_non_injected_shapes(self, tmp_path):
        tool = self._load_tool()
        plain = tmp_path / "plain.py"
        plain.write_text("# [TTL] permanent\n# [TTL] limited\nv = 1\n", encoding="utf-8")
        hit, why = tool.classify_file(plain)

        assert hit is False
        assert why == "line1-not-injected-block"

    def test_parse_args_accepts_documented_dry_run_flag(self, monkeypatch):
        """红队批回归：docstring 与工单口径均写 `--dry-run`，但 argparse 未注册该旗标
        → 按文档调用直接 unrecognized arguments（exit 2）。注册后 --dry-run 显式生效
        并压过 --apply（双旗标歧义取保守侧）。"""
        import sys

        tool = self._load_tool()
        monkeypatch.setattr(sys, "argv", ["dedup_ttl_headers.py", "--dry-run"])
        args = tool._parse_args()
        assert args.dry_run is True and args.apply is False

        monkeypatch.setattr(sys, "argv", ["dedup_ttl_headers.py", "--apply", "--dry-run"])
        args2 = tool._parse_args()
        assert args2.dry_run is True and args2.apply is True  # main 内 apply_mode= dry-run 胜


_BRK086_TOOL = _PROJECT_ROOT / "scripts" / "governance" / "dedup_ttl_headers.py"


def _brk086_git(repo: Path, *args: str):
    """临时仓 git 调用：关 autocrlf 与 hooksPath，保证字节口径可复现（BRK-086 钉）。"""
    from zephyr.shared.infra.process_pool import run_subprocess_hidden

    return run_subprocess_hidden(
        ["git", "-c", "core.autocrlf=false", "-c", "core.hooksPath=", *args],
        cwd=str(repo),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def _brk086_make_crlf_repo(repo: Path, n_body_lines: int = 9) -> Path:
    """造一个 HEAD 侧为 CRLF 的小仓，工作文件的头部块含第 2 条重复 TTL 行（BRK-086 复现夹具）。

    形态与仓内 31 件存量一致：line1 是文件自带的 BLUEPRINT 头（非 auto-injected），
    头部块尾部多出一条 `# [TTL] permanent` → 真实改动恰为删 1 行。
    """
    header = [
        "# [BLUEPRINT] GREATWALL-BRK086 | (fixture) | §",
        "# [TTL] permanent",
        "# [MODULE] dup_crlf",
        "# [TTL] permanent",
    ]
    body = [f"VALUE_{i} = {i}" for i in range(n_body_lines)]
    target = repo / "dup_crlf.py"
    target.write_bytes(("\r\n".join(header + body) + "\r\n").encode("utf-8"))
    assert _brk086_git(repo, "init", "-q").returncode == 0
    _brk086_git(repo, "config", "user.email", "brk086@example.invalid")
    _brk086_git(repo, "config", "user.name", "brk086")
    assert _brk086_git(repo, "add", "--", "dup_crlf.py").returncode == 0
    committed = _brk086_git(repo, "commit", "-q", "--no-verify", "-m", "seed CRLF baseline")
    assert committed.returncode == 0, committed.stderr
    return target


class TestDedupLineEndingFidelityBrk086:
    """BRK-086 换行保真钉：去重只许删目标行，禁把 CRLF 折叠成 LF（差评级假差异）。

    能红判据：把改写改回文本模式整篇读写（read_text + write_text），
    `test_apply_on_crlf_file_reports_plus_zero_minus_one` 即以 +12 -13 形态失败
    （实测修前为 `+N -(N±1)` 的整篇重写），字节保真用例同时失败。
    """

    def test_apply_on_crlf_file_reports_plus_zero_minus_one(self, tmp_path):
        """CLI 端到端：对 CRLF 编码 .py 跑 --apply 后 git diff --numstat 必须是 +0 -1。"""
        from zephyr.shared.infra.process_pool import run_subprocess_hidden

        target = _brk086_make_crlf_repo(tmp_path)
        before = target.read_bytes()
        assert before.count(b"\r\n") == before.count(b"\n")  # 前置：全篇 CRLF

        run = run_subprocess_hidden(
            [sys.executable, str(_BRK086_TOOL), "--root", str(tmp_path), "--apply"],
            cwd=str(tmp_path),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        assert run.returncode == 0, f"apply 失败 rc={run.returncode}\n{run.stdout}\n{run.stderr}"

        after = target.read_bytes()
        stray_lf = after.count(b"\n") - after.count(b"\r\n")
        assert stray_lf == 0, f"--apply 改写了换行符：{stray_lf} 行由 CRLF 变成 LF（BRK-086 复发）"

        numstat = _brk086_git(tmp_path, "diff", "--numstat", "--", "dup_crlf.py")
        assert numstat.returncode == 0, numstat.stderr
        fields = numstat.stdout.split("\t")
        assert len(fields) == 3, f"numstat 异常（可能被报成整篇重写）: {numstat.stdout!r}"
        added, removed = int(fields[0]), int(fields[1])
        assert (added, removed) == (0, 1), (
            f"真实只差 1 行却报成 +{added} -{removed}：换行污染回归（BRK-086），"
            "必须是 +0 -1"
        )

        # 幂等复跑：二次 --apply 不得再动字节，diff 仍为 +0 -1
        again = run_subprocess_hidden(
            [sys.executable, str(_BRK086_TOOL), "--root", str(tmp_path), "--apply"],
            cwd=str(tmp_path),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        assert again.returncode == 0, again.stderr
        assert target.read_bytes() == after, "复跑 --apply 必须零改动（幂等）"

    def test_dedup_file_preserves_per_line_ending_bytes(self, tmp_path):
        """单元口径：删前两行注入块，其余每一行的字节（含各自换行符）逐字不变。"""
        import importlib.util

        spec = importlib.util.spec_from_file_location("dedup_ttl_headers_brk086", _BRK086_TOOL)
        tool = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(tool)

        f = tmp_path / "mixed.py"
        original = f.with_suffix(".orig")
        payload = (
            "# [BLUEPRINT] MOD-BRK086 | (auto-injected by S4 reconciler) | §\r\n"
            "# [TTL] permanent\r\n"
            "# [MODULE] mixed\r\n"
            "# [TTL] permanent\n"
            "A = 1\r\n"
            "B = 2\n"
        )
        f.write_bytes(payload.encode("utf-8"))
        original.write_bytes(payload.encode("utf-8"))

        changed, _why = tool.dedup_file(f)
        assert changed is True

        kept_tail = original.read_bytes().splitlines(keepends=True)[2:]
        assert f.read_bytes() == b"".join(kept_tail), "保留部分必须与原始字节逐字相同（含 CRLF/LF 混排）"
        assert f.read_bytes().count(b"\r\n") == 2, "原 CRLF 行必须仍是 CRLF"
