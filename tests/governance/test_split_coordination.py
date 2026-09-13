# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §split_coordination
# [MODULE] tests.governance.test_split_coordination
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] pytest; scripts.governance.split_coordination（load_declarations 损坏态 fail-loud）
# [CONSUMERS] 红蓝 v3 P2-4 守卫（active_splits.yaml 损坏态 status/begin 统一 exit 2，不崩不哑）
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] tmp_path 写坏 YAML + monkeypatch DECL_PATH——零真实 .runtime/coordination 副作用（测试隔离铁律）
# [MODIFY-GUARD] 与 scripts/governance/split_coordination.py load_declarations 同批演进
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError
# [TESTS] self
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""split_coordination CLI 损坏声明文件统一防御测试（红蓝 v3 P2-4 治本守卫）。

病根：active_splits.yaml 写坏后两副面孔——cmd_status 裸 yaml traceback 崩溃，
cmd_begin 经 load_declarations 吞异常静默返回空列表（协调窗口根本没立起来也不报
错）。治本：load_declarations 解析失败统一 print FAIL 到 stderr + sys.exit(2)，
status/begin 行为一致；文件不存在仍返回 []（正常路径不受影响）。
"""

from __future__ import annotations

from types import SimpleNamespace

import pytest

import scripts.governance.split_coordination as sc

_CORRUPT_YAML = "splits: [ { dir: docs/_working/lab, "  # 截断 flow 序列 → YAMLError


@pytest.fixture()
def corrupt_decl(tmp_path, monkeypatch):
    """tmp 目录写坏 YAML 并把 DECL_PATH 指过去。"""
    p = tmp_path / "active_splits.yaml"
    p.write_text(_CORRUPT_YAML, encoding="utf-8")
    monkeypatch.setattr(sc, "DECL_PATH", p)
    return p


class TestCorruptDeclarationFailLoud:
    """损坏态统一防御：status/begin 都 exit 2 且 stderr 带 FAIL（不崩不哑）。"""

    def test_status_exit2_with_fail(self, corrupt_decl, capsys):
        with pytest.raises(SystemExit) as ei:
            sc.cmd_status(SimpleNamespace())
        assert ei.value.code == 2
        err = capsys.readouterr().err
        assert "FAIL: 协调声明文件损坏" in err, f"stderr 应带 FAIL 指引，实际: {err!r}"

    def test_begin_exit2_with_fail(self, corrupt_decl, tmp_path, capsys):
        # old_paths 经文件提供非空清单，让 begin 走到 load_declarations（先于写盘）
        old_paths_file = tmp_path / "old_paths.txt"
        old_paths_file.write_text("docs/_working/lab/a.md\n", encoding="utf-8")
        args = SimpleNamespace(
            dir="docs/_working/lab",
            session="s1",
            old_paths_file=str(old_paths_file),
            new_root="docs/_working/lab/a",
        )
        with pytest.raises(SystemExit) as ei:
            sc.cmd_begin(args)
        assert ei.value.code == 2
        err = capsys.readouterr().err
        assert "FAIL: 协调声明文件损坏" in err, f"stderr 应带 FAIL 指引，实际: {err!r}"

    def test_missing_file_returns_empty(self, tmp_path, monkeypatch):
        """文件不存在 = 正常路径，仍返回 []（不受 fail-loud 改造影响）。"""
        monkeypatch.setattr(sc, "DECL_PATH", tmp_path / "nonexistent.yaml")
        assert sc.load_declarations() == []

    def test_valid_file_still_loads(self, tmp_path, monkeypatch):
        """合法声明照常解析（改造零回归）。"""
        p = tmp_path / "active_splits.yaml"
        p.write_text(
            "splits:\n- dir: docs/_working/lab\n  mover_session: s1\n  old_paths: [docs/_working/lab/a.md]\n"
            "  new_root: docs/_working/lab/a\n  declared_at: '2026-09-14T00:00:00+00:00'\n",
            encoding="utf-8",
        )
        monkeypatch.setattr(sc, "DECL_PATH", p)
        splits = sc.load_declarations()
        assert len(splits) == 1 and splits[0]["dir"] == "docs/_working/lab"
