# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §split_coordination_gate
# [MODULE] tests.governance.commit_gates.test_split_coordination_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] pytest; yaml; zephyr.gov_enforcement.commit_gates.split_coordination_gate；scripts.governance.split_coordination（工具位）
# [CONSUMERS] SPLIT-COORDINATION gate 质量守卫（红=旧路径重建必拦；蓝=无声明/mover/新路径必过）
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 全部用例构造于 tmp git 仓库（含初始 commit），不碰生产 .runtime；工具用例 monkeypatch DECL_PATH 指向 tmp 副本
# [MODIFY-GUARD] 与 gate/工具同批演进（声明 schema 变更须同步用例）
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError
# [TESTS] self
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""SPLIT-COORDINATION gate 红蓝对抗测试（#ARCH-SPLIT-COORDINATION-001，F5 协议根治）。

红队（必拦）：他会话提交清单命中活跃声明 old_paths → 阻断（防旧平铺路径重建=
             双重存在事故）；**生产形态绝对路径**亦必命中（2026-09-13 触发面
             归一实弹教训：朴素反斜杠替换对绝对路径恒 miss）；**搬移落地后旧路径
             重建仍必拦**（落地≠失活——落地即失活会在风险窗口起点拆掉保护）。
蓝队（必过）：无声明文件 skip；mover 本人放行；他会话文件不在 old_paths（含
             re-base 后新路径）放行；声明损坏 fail-open 放行；陈旧声明（>48h
             弃单）降级放行防砖。
工具：begin 幂等声明 / finish 权限 / sweep 只清陈旧（不按落地清）/ 原子写可解析。
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

_REPO = Path(__file__).resolve().parents[3]
if str(_REPO / "src") not in sys.path:
    sys.path.insert(0, str(_REPO / "src"))

import scripts.governance.split_coordination as sc  # noqa: E402
from zephyr.gov_enforcement.commit_gates.split_coordination_gate import (  # noqa: E402
    make_split_coordination_gate,
)


class _FakeGW:
    """最小 gateway 桩：project_root + run_git（gate 只消费这两者）。"""

    def __init__(self, root: Path) -> None:
        self.project_root = root

    def run_git(self, cmd: list[str]):
        return subprocess.run(
            cmd, capture_output=True, text=True, encoding="utf-8", errors="replace",
            cwd=str(self.project_root),
        )


def _init_repo(tmp_path: Path) -> _FakeGW:
    """tmp git 仓库 + 初始 commit（lab/seg_001.md、lab/seg_002.md 平铺 tracked）。"""
    env = {**os.environ, "GIT_AUTHOR_NAME": "T", "GIT_AUTHOR_EMAIL": "t@t.com",
           "GIT_COMMITTER_NAME": "T", "GIT_COMMITTER_EMAIL": "t@t.com"}

    def _git(*args: str) -> None:
        subprocess.run(["git", *args], cwd=str(tmp_path), capture_output=True, env=env, check=True)

    _git("init")
    lab = tmp_path / "lab"
    lab.mkdir()
    (lab / "seg_001.md").write_text("v1\n", encoding="utf-8")
    (lab / "seg_002.md").write_text("v1\n", encoding="utf-8")
    _git("add", "-A")
    _git("commit", "-m", "init", "--no-verify")
    return _FakeGW(tmp_path)


def _declare(gw: _FakeGW, mover: str = "mover-A", old_paths: list[str] | None = None) -> Path:
    p = Path(str(gw.project_root)) / ".runtime" / "coordination" / "active_splits.yaml"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(
        yaml.safe_dump(
            {
                "splits": [
                    {
                        "dir": "lab",
                        "mover_session": mover,
                        "old_paths": old_paths or ["lab/seg_001.md", "lab/seg_002.md"],
                        "new_root": "lab/a",
                        "declared_at": "2026-09-13T10:00:00+00:00",
                    }
                ]
            },
            allow_unicode=True,
        ),
        encoding="utf-8",
    )
    return p


@pytest.fixture()
def gate():
    return make_split_coordination_gate()


class TestRed:
    """红队：旧平铺路径重建必拦（F5 双重存在事故根治点）。"""

    def test_foreign_commit_old_path_blocked(self, gate, tmp_path):
        """他会话提交清单命中活跃声明 old_paths → 硬阻断+re-base 指引。"""
        gw = _init_repo(tmp_path)
        _declare(gw)
        passed, detail = gate.check(
            gw, files=[str(tmp_path / "lab" / "seg_001.md")], session_id="editor-B"
        )
        assert not passed
        assert "SPLIT-COORDINATION" in detail
        assert "mover-A" in detail and "re-base" in detail

    def test_absolute_path_production_form(self, gate, tmp_path):
        """生产形态：commit() 传入绝对路径（gateway abspath）必命中——
        触发面归一铁律（2026-09-13 三发两漏实弹教训）。"""
        gw = _init_repo(tmp_path)
        _declare(gw)
        passed, detail = gate.check(
            gw, files=[str(tmp_path / "lab" / "seg_001.md")], session_id="editor-B"
        )
        assert not passed, f"绝对路径形态漏拦（触发面归一缺陷复发）: {detail}"

    def test_backslash_relative_path_blocked(self, gate, tmp_path):
        """反斜杠相对路径归一后亦命中。"""
        gw = _init_repo(tmp_path)
        _declare(gw)
        passed, _ = gate.check(gw, files=["lab\\seg_002.md"], session_id="editor-B")
        assert not passed

    def test_editor_recreation_scenario(self, gate, tmp_path):
        """历史事故形态复现：mover 已搬走（盘上无旧文件），编辑者在旧路径重建
        新文件后提交 → 必拦（磁盘存在 → 未落地 → 窗口仍开）。"""
        gw = _init_repo(tmp_path)
        # mover 声明后搬移：旧路径删除+新路径落地（未 finish——声明残留）
        (tmp_path / "lab" / "seg_001.md").unlink()
        (tmp_path / "lab" / "a").mkdir()
        (tmp_path / "lab" / "a" / "seg_001.md").write_text("moved\n", encoding="utf-8")
        _declare(gw)
        # 编辑者旧路径重建（xtreme 红蓝事故形态）
        (tmp_path / "lab" / "seg_001.md").write_text("recreated by editor\n", encoding="utf-8")
        passed, detail = gate.check(
            gw, files=[str(tmp_path / "lab" / "seg_001.md")], session_id="editor-B"
        )
        assert not passed, "编辑者旧路径重建未拦——双重存在事故复发"


class TestBlue:
    """蓝队：合法流量零误拦。"""

    def test_no_declaration_skips(self, gate, tmp_path):
        gw = _init_repo(tmp_path)
        passed, detail = gate.check(
            gw, files=[str(tmp_path / "lab" / "seg_001.md")], session_id="editor-B"
        )
        assert passed and "skip" in detail

    def test_mover_passes(self, gate, tmp_path):
        """mover 本人的搬移提交（旧路径删除+新路径新增）放行。"""
        gw = _init_repo(tmp_path)
        _declare(gw)
        passed, detail = gate.check(
            gw,
            files=[str(tmp_path / "lab" / "seg_001.md"), str(tmp_path / "lab" / "a" / "seg_001.md")],
            session_id="mover-A",
        )
        assert passed, f"mover 被误拦: {detail}"

    def test_foreign_new_root_path_passes(self, gate, tmp_path):
        """他会话 re-base 到新挂基点路径 → 放行（协议正确出路）。"""
        gw = _init_repo(tmp_path)
        _declare(gw)
        passed, _ = gate.check(
            gw, files=[str(tmp_path / "lab" / "a" / "seg_001.md")], session_id="editor-B"
        )
        assert passed

    def test_foreign_unrelated_file_passes(self, gate, tmp_path):
        """他会话提交声明外文件 → 放行（零误伤）。"""
        gw = _init_repo(tmp_path)
        _declare(gw)
        passed, _ = gate.check(
            gw, files=[str(tmp_path / "src" / "other.py")], session_id="editor-B"
        )
        assert passed

    def test_corrupt_declaration_fail_open(self, gate, tmp_path):
        """声明 YAML 损坏 → fail-open 放行（协调态非真源，不砖死提交链）。"""
        gw = _init_repo(tmp_path)
        p = _declare(gw)
        p.write_text("splits: [broken yaml {{{", encoding="utf-8")
        passed, detail = gate.check(
            gw, files=[str(tmp_path / "lab" / "seg_001.md")], session_id="editor-B"
        )
        assert passed and "fail-open" in detail

    def test_stale_declaration_fail_open(self, gate, tmp_path):
        """陈旧声明（>48h mover 弃单）→ 降级 warn 放行（防砖自愈）。"""
        gw = _init_repo(tmp_path)
        _declare(gw)
        p = Path(str(gw.project_root)) / ".runtime" / "coordination" / "active_splits.yaml"
        data = yaml.safe_load(p.read_text(encoding="utf-8"))
        from datetime import datetime, timedelta, timezone

        data["splits"][0]["declared_at"] = (
            datetime.now(timezone.utc) - timedelta(hours=72)
        ).isoformat()
        p.write_text(yaml.safe_dump(data, allow_unicode=True), encoding="utf-8")
        passed, _ = gate.check(
            gw, files=[str(tmp_path / "lab" / "seg_001.md")], session_id="editor-B"
        )
        assert passed, "陈旧声明（弃单）应降级放行，防目录被永久锁死"

    def test_protection_survives_move_landing(self, gate, tmp_path):
        """设计核心（教训用例）：mover 已搬移落地（旧路径 HEAD 无+盘无）后，
        编辑者旧路径重建仍必须被拦——落地≠失活（落地即失活会在风险窗口起点
        拆掉保护）。"""
        gw = _init_repo(tmp_path)
        env = {**os.environ, "GIT_AUTHOR_NAME": "T", "GIT_AUTHOR_EMAIL": "t@t.com",
               "GIT_COMMITTER_NAME": "T", "GIT_COMMITTER_EMAIL": "t@t.com"}
        _declare(gw)
        # mover 搬移落地：删旧路径+建新路径+提交（不 finish——声明继续保护）
        (tmp_path / "lab" / "a").mkdir()
        for f in ("seg_001.md", "seg_002.md"):
            (tmp_path / "lab" / f).rename(tmp_path / "lab" / "a" / f)
        subprocess.run(["git", "add", "-A"], cwd=str(tmp_path), capture_output=True, env=env)
        subprocess.run(["git", "commit", "-m", "move", "--no-verify"],
                       cwd=str(tmp_path), capture_output=True, env=env)
        # 编辑者旧路径重建（事故形态）
        (tmp_path / "lab" / "seg_001.md").write_text("recreated\n", encoding="utf-8")
        passed, _ = gate.check(
            gw, files=[str(tmp_path / "lab" / "seg_001.md")], session_id="editor-B"
        )
        assert not passed, "搬移落地后旧路径重建未拦——落地即失活缺陷复发"

    def test_empty_files_skip(self, gate, tmp_path):
        gw = _init_repo(tmp_path)
        passed, _ = gate.check(gw, files=[], session_id="x")
        assert passed


class TestTool:
    """split_coordination.py 工具：声明生命周期闭环（monkeypatch DECL_PATH 到 tmp）。"""

    def _load_tool(self, monkeypatch, tmp_path: Path):
        target = tmp_path / "active_splits.yaml"
        monkeypatch.setattr(sc, "DECL_PATH", target)
        monkeypatch.setattr(sc, "_REPO", tmp_path)
        return target

    def test_begin_finish_roundtrip(self, monkeypatch, tmp_path):
        target = self._load_tool(monkeypatch, tmp_path)
        lab = tmp_path / "lab"
        lab.mkdir()
        (lab / "x.md").write_text("1\n", encoding="utf-8")
        rc = sc.main(["begin", "--session", "m1", "--dir", "lab", "--new-root", "lab/a"])
        assert rc == 0
        data = yaml.safe_load(target.read_text(encoding="utf-8"))
        assert data["splits"][0]["mover_session"] == "m1"
        assert "lab/x.md" in data["splits"][0]["old_paths"]
        # 非 mover 无权 finish
        assert sc.main(["finish", "--session", "other", "--dir", "lab"]) == 1
        # mover finish 后声明移除
        assert sc.main(["finish", "--session", "m1", "--dir", "lab"]) == 0
        assert yaml.safe_load(target.read_text(encoding="utf-8"))["splits"] == []

    def test_begin_idempotent_overwrite(self, monkeypatch, tmp_path):
        """同 dir 重复 begin = 覆盖刷新（不产生重复条目）。"""
        target = self._load_tool(monkeypatch, tmp_path)
        lab = tmp_path / "lab"
        lab.mkdir()
        (lab / "x.md").write_text("1\n", encoding="utf-8")
        assert sc.main(["begin", "--session", "m1", "--dir", "lab"]) == 0
        assert sc.main(["begin", "--session", "m1", "--dir", "lab"]) == 0
        data = yaml.safe_load(target.read_text(encoding="utf-8"))
        assert len(data["splits"]) == 1

    def test_sweep_removes_stale_only(self, monkeypatch, tmp_path):
        """sweep 只清扫陈旧声明（>max-age 弃单），新鲜声明保留——
        不按"已落地"清扫（落地=保护最需存在的时点，教训语义）。"""
        target = self._load_tool(monkeypatch, tmp_path)
        from datetime import datetime, timedelta, timezone

        now = datetime.now(timezone.utc)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            yaml.safe_dump({"splits": [
                {"dir": "stale", "mover_session": "m1", "old_paths": ["stale/x.md"],
                 "new_root": "", "declared_at": (now - timedelta(hours=72)).isoformat()},
                {"dir": "live", "mover_session": "m2", "old_paths": ["live/y.md"],
                 "new_root": "", "declared_at": now.isoformat()},
            ]}, allow_unicode=True),
            encoding="utf-8",
        )
        assert sc.main(["sweep"]) == 0
        data = yaml.safe_load(target.read_text(encoding="utf-8"))
        assert [s["dir"] for s in data["splits"]] == ["live"]
