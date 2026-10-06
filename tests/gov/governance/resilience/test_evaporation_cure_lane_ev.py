# [MODULE] tests.gov.governance.resilience.test_evaporation_cure_lane_ev
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] pytest; subprocess; sys; os; argparse; pathlib;
#   scripts.governance.commit_queue_landing（WorktreeLanding._git_wt/_verify_wt_integrity_post）;
#   scripts.governance.evaporation_blackbox（_snapshot per-path 见证/_lock_window/_add_args）;
#   scripts.ops_guard（CLI check 面）
# [CONSUMERS] pytest 自动发现
# [STARTUP] python -m pytest tests/gov/governance/resilience/test_evaporation_cure_lane_ev.py
# [MATURITY] testing
# [INVARIANTS] 全 tmp 隔离（tmp git 主仓 + tmp linked worktree，绝不碰生产 .runtime 与主区
#   工作区，宪法运维红线 6）；被检对象真函数直调（WorktreeLanding 以 object.__new__ 最小
#   装配，绕开队列/gateway 依赖面）；ops_guard 断言走真实子进程 CLI 面（案根复现端到端）
# [MODIFY-GUARD] 蒸发案治本 LANE-EV 证尺（先红后绿史=15 号文 EV-01/EV-02 行）：
#   摘 _git_wt 入口门（.git 链接/toplevel 前置硬校验）、摘 _verify_wt_integrity_post
#   执行后复核接线（_sync_worktree reset/clean 之后）、摘黑匣子 tracked_deleted_* 三字段
#   或 --lock-window、ops_guard 保护区放水——任一即红。
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [A_module] module_id=TEST-EV01-EV02-CURE-LANE-EV | layer=module | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [ERROR_CONTRACT] AssertionError; RuntimeError（被测 fail-closed 面按 match 断言）
# [TTL] task_bound
"""test_evaporation_cure_lane_ev.py — 蒸发案治本 LANE-EV 证尺（重收编版）。

原件 2026-09-28 落 tests/governance/（先红后绿），字节从未入 git 史，10-04/05 tests
重排中随旧路径蒸发（仅存 pyc 骨架）；本件按 pyc 全骨架 + 现行落地形态重建于新家。

覆盖两条施工（现行落地形态）：
  1. EV-02（2026-09-30 F 组夜班落地；原稿设想的"动词钉死 --git-dir/--work-tree +
     landing_guard.jsonl 审计面"未按该形态落地，内收进前置门+执行后复核+既有
     死信/环境分类链路，见 _git_wt/_verify_wt_integrity_post 文档）：
       - 入口门：_git_wt 执行前硬校验 worktree .git 链接存在 + toplevel 解析回自身，
         cwd walk-up 打穿主仓的结构通道封死（2026-08-29 事故形态）；
       - TOCTOU 窗：reset/clean 在飞后由 _verify_wt_integrity_post 复核（_sync_worktree
         于 1750/1758、1753/1771 行接线），链接丢失/toplevel 漂移即 RuntimeError 中止，
         宁停勿伤；主区 tracked 面 + HEAD 零损伤（untracked 观测面归 EV-01 黑匣子
         专职——实现文档明示的分工）。
  2. EV-01 强化：黑匣子 per-path 删除见证（tracked_deleted_count/paths/sig）+
     ``--lock-window`` 一键锁定"存在→缺失"分钟级区间——2026-09-25 取证时只有聚合计数，
     40 件整目录蒸发在计数里被同期 commit 完全抵消。
  3. ops_guard CLI 面真实拦截：案根目录递归删除命中保护区必须拦（原稿断言的 POSIX
     rm 原语已随 ops_guard 内收退役，现行面=Remove-Item -Recurse/powershell_recurse）。
"""

from __future__ import annotations

import argparse
import importlib.util
import os
import subprocess
import sys
from pathlib import Path

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[4]


def _load(name: str, rel: str):
    """同口径装载 scripts 真源模块（sys.modules 先注册，保 dataclass/包内引用可用）。"""
    spec = importlib.util.spec_from_file_location(name, _PROJECT_ROOT / rel)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def cql():
    return _load("_cql_evap", "scripts/governance/commit_queue_landing.py")


@pytest.fixture(scope="module")
def bb():
    return _load("_bb_evap", "scripts/governance/evaporation_blackbox.py")


def _git(cwd: Path, *args: str) -> str:
    r = subprocess.run(
        ["git", *args],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=180,
    )
    assert r.returncode == 0, f"git {' '.join(args)} -> {r.stderr}"
    return r.stdout.strip()


@pytest.fixture()
def tmp_repo(tmp_path: Path) -> Path:
    """主仓形态的 git 仓：dev 分支 + 在册件 + 一个 untracked 探针（clean 的靶）。"""
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "dev")
    _git(repo, "config", "user.email", "t@example.com")
    _git(repo, "config", "user.name", "test")
    (repo / ".gitignore").write_text(".runtime/\n.ailocks/\n", encoding="utf-8")
    (repo / "tracked_probe.txt").write_text("keep-me\n", encoding="utf-8")
    camp = repo / "docs" / "_working" / "campaign"
    camp.mkdir(parents=True)
    (camp / "01.md").write_text("one\n", encoding="utf-8")
    (camp / "02.md").write_text("two\n", encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "-qm", "notes")
    (repo / "untracked_probe.txt").write_text("volatile\n", encoding="utf-8")
    return repo


@pytest.fixture()
def worktree_of(tmp_repo: Path) -> Path:
    """真实 linked worktree（.git 为指针文件），检出 serializer 分支。"""
    wt = tmp_repo / ".runtime" / "commit_queue" / "worktrees" / "w0"
    wt.parent.mkdir(parents=True, exist_ok=True)
    _git(tmp_repo, "worktree", "add", "-q", "-b", "serializer/commit-queue-w0", str(wt))
    return wt


def _landing(cql, repo: Path, wt: Path):
    """最小可用 WorktreeLanding（只喂 _git_wt 用到的三个属性，绕开队列/gateway 装配）。"""
    landing = object.__new__(cql.WorktreeLanding)
    landing.repo_root = repo
    landing.worktree_path = wt
    landing.target_branch = "dev"
    return landing


def _assert_main_repo_untouched(tmp_repo: Path) -> None:
    """主区 tracked 面 + HEAD 零损伤（打穿事故的判据特征）。"""
    assert (tmp_repo / "tracked_probe.txt").read_text(encoding="utf-8") == "keep-me\n", "主区在册件被改"
    assert (tmp_repo / "docs" / "_working" / "campaign" / "01.md").exists(), "主区在册件消失"
    assert _git(tmp_repo, "rev-parse", "HEAD") == _git(tmp_repo, "rev-parse", "refs/heads/dev"), "主区 HEAD 被动过"


# ===========================================================================
# EV-02：破坏性 git 调用与 cwd 解析彻底解耦——入口门 + 执行后复核
# ===========================================================================


class TestGitWtPunchthroughGuard:
    """EV-02 现行形态：破坏性 git 调用必须与 cwd 解析解耦，执行后自证未打穿主仓。"""

    def test_entry_gate_rejects_missing_git_link(self, cql, tmp_repo, worktree_of):
        """修复前实证：worktree 目录在而 .git 指针丢失 → git walk-up 命中主仓 .git，
        reset --hard/clean 直接打穿主工作区。入口门必须在此形态拒绝执行。"""
        (worktree_of / ".git").unlink()
        landing = _landing(cql, tmp_repo, worktree_of)
        with pytest.raises(RuntimeError, match="打穿主仓"):
            landing._git_wt("reset", "--hard", "refs/heads/dev")
        _assert_main_repo_untouched(tmp_repo)

    def test_entry_gate_rejects_toplevel_drift(self, cql, tmp_repo, worktree_of, monkeypatch):
        """toplevel 漂移（解析回主仓而非 worktree 自身）→ 入口门拒绝，禁越权执行。"""

        def drifting(root, args, *, check=True):
            return subprocess.CompletedProcess(
                args, 0, stdout=f"{tmp_repo}\n", stderr=""
            )  # toplevel 探针谎报主仓根=漂移形态

        monkeypatch.setattr(cql, "_run_git", drifting)
        landing = _landing(cql, tmp_repo, worktree_of)
        with pytest.raises(RuntimeError, match="toplevel 漂移"):
            landing._git_wt("clean", "-fd")
        _assert_main_repo_untouched(tmp_repo)

    def test_post_verify_fail_closed_on_toctou_window(self, cql, tmp_repo, worktree_of):
        """复现案根时序：前置校验通过后 .git 指针被摘（TOCTOU 窗命中）→
        _verify_wt_integrity_post（_sync_worktree 于 reset --hard/clean -fd 之后接线的
        执行后复核）必须 RuntimeError 中止本轮（宁停勿伤）；主区 tracked 面+HEAD 零损。"""
        landing = _landing(cql, tmp_repo, worktree_of)
        # 前置门通过的正常执行（与 _sync_worktree 1750 行同参）
        landing._git_wt("reset", "--hard", "refs/heads/dev")
        # 命令在飞后链接被外力摘除（TOCTOU 窗命中）
        (worktree_of / ".git").unlink()
        # 与 _sync_worktree 1758 行同参的执行后复核必须 fail-closed
        with pytest.raises(RuntimeError, match="复核"):
            landing._verify_wt_integrity_post("reset --hard")
        _assert_main_repo_untouched(tmp_repo)


# ===========================================================================
# EV-01 强化：黑匣子 per-path 删除见证 + --lock-window 分钟级锁窗
# ===========================================================================


class TestBlackboxDeletionWitness:
    """EV-01 强化：黑匣子必须留下 per-path 缺失见证，并能一键锁窗口。"""

    def _snapshot_at(self, bb, repo: Path, monkeypatch, tmp_path: Path) -> dict:
        monkeypatch.setattr(bb, "REPO_ROOT", repo)
        monkeypatch.setattr(bb, "BLACKBOX_DIR", tmp_path / "blackbox")
        monkeypatch.setattr(bb, "BLACKBOX_FILE", tmp_path / "blackbox" / "blackbox.jsonl")
        return bb._snapshot()

    def test_snapshot_records_tracked_deleted_paths(self, bb, tmp_repo, monkeypatch, tmp_path):
        (tmp_repo / "docs" / "_working" / "campaign" / "01.md").unlink()  # 工作区侧缺失=案根判据特征
        rec = self._snapshot_at(bb, tmp_repo, monkeypatch, tmp_path)
        assert rec["tracked_deleted_count"] >= 1, f"未记录工作区缺失件: {rec}"
        assert "docs/_working/campaign/01.md" in rec["tracked_deleted_paths"]
        assert rec["tracked_deleted_sig"], "缺 sig 字段则同集合快照无法去重对账"

    def test_lock_window_pins_present_to_missing_interval(self, bb, monkeypatch, tmp_path):
        """合成两帧（存在/缺失）→ --lock-window 必须报出分钟级区间，不再靠人肉拼三本审计。"""
        monkeypatch.setattr(bb, "REPO_ROOT", tmp_path)
        records = [
            {
                "ts": "2026-09-25T08:11:00.000+00:00",
                "ts_local": "2026-09-25T16:11:00+08:00",
                "tracked_deleted_paths": [],
            },
            {
                "ts": "2026-09-25T08:16:00.000+00:00",
                "ts_local": "2026-09-25T16:16:00+08:00",
                "tracked_deleted_paths": [
                    "docs/_working/campaign/01.md",
                    "docs/_working/campaign/02.md",
                ],
            },
        ]
        out = bb._lock_window(records, "docs/_working/campaign")
        assert out, "锁窗口零输出=仍不能定位现场"
        joined = "\n".join(out)
        assert "16:11:00" in joined and "16:16:00" in joined, f"未给出存在→缺失区间: {joined}"
        assert "存在→缺失" in joined

    def test_cli_lock_window_mode_exists(self, bb):
        """CLI 必须暴露 --lock-window（案卷取证口径的唯一入口）。"""
        parser = argparse.ArgumentParser()
        bb._add_args(parser)
        assert any(
            "--lock-window" in action.option_strings
            for action in parser._actions  # noqa: SLF001
        ), "缺 --lock-window"


# ===========================================================================
# ops_guard CLI 面真实拦截（案根复现，端到端一层）
# ===========================================================================


class TestGuardCliUsable:
    def test_cli_check_blocks_recursive_delete_on_docs_zone(self):
        """ops_guard CLI 的保护区判定在真实仓现场必须拦得住（现行原语面=powershell_recurse；
        原稿的 POSIX sh_rm_recurse 原语已随 ops_guard 内收退役）。"""
        cmd = [
            sys.executable,
            str(_PROJECT_ROOT / "scripts" / "ops_guard.py"),
            "check",
            "Remove-Item",
            "-Recurse",
            "docs/_working/decision_map_campaign_20260924",
        ]
        env = dict(os.environ)
        env["ZEPHYR_FORCE_DELETE"] = ""  # 无人工授权=必须拦
        proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", env=env)
        out = (proc.stdout or "") + (proc.stderr or "")
        assert proc.returncode != 0, f"案根命令在 CLI 面未被拦: rc={proc.returncode} out={out[:200]}"
        assert "powershell_recurse" in out, f"fail-closed 未点名原语: {out[:200]}"
        assert "命中保护区" in out, f"fail-closed 未点名保护区: {out[:200]}"
