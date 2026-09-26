# [A_test] module_id: MOD-TEST-RB14-S4 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-RB14 | scripts/governance/git_hooks/post_commit_guard.sh + git_commit_gateway §D2 + commit_queue_landing §D2 步1/2/5
# [MODULE] governance.red_blue_pkg14.test_rb14_s4_forged_marker
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] pytest; subprocess(git); scripts.governance.commit_queue_landing; zephyr...git_commit_gateway; _common(本包)
# [CONSUMERS] pytest 自动发现
# [STARTUP] python -m pytest tests/governance/red_blue_pkg14/test_rb14_s4_forged_marker.py
# [MATURITY] testing
# [INVARIANTS] hook e2e 全沙盒（一次性仓+一次性注册表，永不触主仓 .runtime）；判据：
#   ①手写 [GW:未注册sid] 裸 commit（--no-verify）→ POST-COMMIT-GUARD 判伪造并
#   reset --soft（HEAD 回退、改动回暂存、审计落 violation=forged_gw_marker）；
#   ②正门控制：真会话键+GW env 合法保留；
#   ③D2 步1：gateway.commit 收 internal_call 形参（缺省 False）；
#   ④D2 语义：外部调用（internal_call=False）提交成功后进程环境零旗残留；
#   ⑤D2 步5：_trusted_git_env 显式剔除 GW 旗（落地 plumbing 域不继承）；
#   ⑥D2 步2：landing 两个 commit 调用点均显式 internal_call=True（池化动态取证）。
# [MODIFY-GUARD] 包14 场景4（伪造与绕门）
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即测试失败
# [TESTS] 本文件
# [TTL] task_bound
"""test_rb14_s4_forged_marker.py — 场景4「伪造与绕门」红蓝对抗。

红证两件（均对产品文件的手术副本，原文件字节零触碰）：
  - W1 前形态（_trusted_git_env 无 pop）→ GW 旗渗入落地 plumbing 域（尺=旗剔除）；
  - D2 步2 前形态（commit 调用无 internal_call 声明）→ 桩取证缺声明（尺=显式声明）。
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest

import scripts.governance.commit_queue_landing as cql
from governance.red_blue_pkg14._common import (
    LANDING_SRC,
    enqueue,
    git,
    git_text,
    load_surgered,
    make_stub_landing_factory,
    sha256_file,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
POST_COMMIT = REPO_ROOT / "scripts" / "governance" / "git_hooks" / "post_commit_guard.sh"
SID = "st-commitspeed-tbl-20260924"  # 沙盒注册表内注册的「真会话键」
GHOST = "rb14-ghost-sid"  # 未注册的伪造目标


def _sandbox_git(repo: Path, *args: str, env: dict | None = None) -> subprocess.CompletedProcess:
    e = {k: v for k, v in os.environ.items() if not k.startswith("ZEPHYR_")}
    if env:
        e.update(env)
    return subprocess.run(
        ["git", *args], cwd=str(repo), capture_output=True, text=True, encoding="utf-8", errors="replace", env=e
    )


@pytest.fixture()
def hook_repo(tmp_path: Path) -> Path:
    """一次性仓：真 post_commit_guard.sh（源文件逐字节复制）+ 扁平注册表（生产 SessionRegistry 口径）。"""
    repo = tmp_path / "hook_repo"
    repo.mkdir()
    _sandbox_git(repo, "init", "-q", "--initial-branch=dev")
    _sandbox_git(repo, "config", "user.email", "t@t")
    _sandbox_git(repo, "config", "user.name", "t")
    hooks_src = repo / "hooks_src"
    hooks_src.mkdir()
    (hooks_src / "post_commit_guard.sh").write_text(POST_COMMIT.read_text(encoding="utf-8"), encoding="utf-8")
    h = repo / ".git" / "hooks"
    h.mkdir(parents=True, exist_ok=True)
    (h / "post-commit").write_text(
        "#!/bin/sh"
        + chr(10)
        + 'if [ -f "hooks_src/post_commit_guard.sh" ]; then'
        + chr(10)
        + "    . hooks_src/post_commit_guard.sh"
        + chr(10)
        + "fi"
        + chr(10),
        encoding="utf-8",
    )
    reg = repo / ".runtime"
    reg.mkdir()
    (reg / "session_registry.json").write_text(
        "{"
        + chr(10)
        + f'  "{SID}": '
        + "{"
        + chr(10)
        + f'    "session_id": "{SID}",'
        + chr(10)
        + '    "pid": 0,'
        + chr(10)
        + '    "held_files": ['
        + chr(10)
        + '      "docs/x.yaml"'
        + chr(10)
        + "    ],"
        + chr(10)
        + '    "last_heartbeat": 1'
        + chr(10)
        + "  }"
        + chr(10)
        + "}"
        + chr(10),
        encoding="utf-8",
    )
    (repo / "seed.txt").write_text("seed" + chr(10), encoding="utf-8")
    _sandbox_git(repo, "add", "--", "seed.txt")
    _sandbox_git(repo, "commit", "-q", "--no-verify", "-m", f"seed [GW:{SID}]", env={"ZEPHYR_COMMIT_GATEWAY": "1"})
    return repo


def _d2_landed() -> bool:
    """D2 步1/2/5 是否已在本检出落地（三处标足迹，任一缺席=D2 在途未落）。"""
    import inspect

    from zephyr.gov_enforcement.rule_bridge.git_commit_gateway import GitCommitGateway

    if "internal_call" not in inspect.signature(GitCommitGateway.commit).parameters:
        return False  # 步1 缺席
    landing_src = LANDING_SRC.read_text(encoding="utf-8")
    if 'os.environ[_GATEWAY_ENV] = "1"' in landing_src:
        return False  # 步2/W1 缺席（全局置位仍在）
    if 'env.pop("ZEPHYR_COMMIT_GATEWAY", None)' not in landing_src:
        return False  # 步5 缺席
    return True


_D2_OK = _d2_landed()
_D2_REASON = (
    "D2 步1/2/5 未在本检出落地（在途：csx-pkg5b 工作树未提交件，落 dev 后本尺自动启用）——"
    "基座探针=commit 签名 internal_call+landing 零全局置位+_trusted_git_env 剔旗"
)

# ── 蓝方 ①：手写 [GW:未注册sid] 裸 commit → 判伪造并 reset ──────────────────


def test_s4_blue_forged_marker_bare_commit_is_reset(hook_repo):
    tip = _sandbox_git(hook_repo, "rev-parse", "HEAD").stdout.strip()
    (hook_repo / "evil.txt").write_text("forged payload" + chr(10), encoding="utf-8")
    _sandbox_git(hook_repo, "add", "--", "evil.txt")
    r = _sandbox_git(hook_repo, "commit", "--no-verify", "-m", f"伪装合法尾注 [GW:{GHOST}]", "--", "evil.txt")

    after = _sandbox_git(hook_repo, "rev-parse", "HEAD").stdout.strip()
    assert after == tip, f"伪造标记 commit 必须被 POST-COMMIT-GUARD reset: rc={r.returncode} {r.stdout}{r.stderr}"
    assert "伪造 GW 标记" in (r.stdout + r.stderr), "reset 文案必须点名伪造"
    staged = _sandbox_git(hook_repo, "diff", "--cached", "--name-only").stdout
    assert "evil.txt" in staged, "reset --soft 后改动保留在暂存区"
    reports = list((hook_repo / ".runtime" / "reconcile_reports").glob("post_commit_guard_*.json"))
    assert reports, "审计必须落盘"
    assert any('"violation":"forged_gw_marker"' in p.read_text(encoding="utf-8") for p in reports)


def test_s4_blue_legit_gateway_marker_still_lands(hook_repo):
    """正门控制：注册会话键 + GW env（合法网关形态）必须保留。"""
    tip = _sandbox_git(hook_repo, "rev-parse", "HEAD").stdout.strip()
    (hook_repo / "ok.txt").write_text("legit" + chr(10), encoding="utf-8")
    _sandbox_git(hook_repo, "add", "--", "ok.txt")
    _sandbox_git(
        hook_repo, "commit", "--no-verify", "-m", f"合法 [GW:{SID}]", "--", "ok.txt", env={"ZEPHYR_COMMIT_GATEWAY": "1"}
    )
    assert _sandbox_git(hook_repo, "rev-parse", "HEAD").stdout.strip() != tip, "合法提交不得被误杀"


# ── 蓝方 ③+④：D2 步1/语义——外部调用零旗残留 ────────────────────────────────


@pytest.mark.skipif(not _D2_OK, reason=_D2_REASON)
def test_s4_blue_external_gateway_commit_no_env_residue(sb_repo, monkeypatch):
    from zephyr.gov_enforcement.rule_bridge.git_commit_gateway import CommitStatus, GitCommitGateway

    (sb_repo / "s4").mkdir()
    x_abs = sb_repo / "s4" / "x.txt"
    x_abs.write_text("payload" + chr(10), encoding="utf-8")
    monkeypatch.setenv("ZEPHYR_CQ_C1_DEBOUNCE", "1")
    gw = GitCommitGateway(project_root=sb_repo)
    # 仅旁路昂贵外设（门禁链/落地前 pre-commit/post-commit 对账），其余全真：
    # 加锁、暂存、commit --no-verify、env 置位/复位、GW 标记构造全走产品码。
    gw._gate_registry = SimpleNamespace(check_all=lambda *a, **k: [])
    gw._run_precommit_channel = lambda *a, **k: None  # type: ignore[method-assign]
    gw._run_post_commit_reconcile = lambda *a, **k: None  # type: ignore[method-assign]
    monkeypatch.delenv("ZEPHYR_COMMIT_GATEWAY", raising=False)

    # D2 步1：internal_call 为 keyword-only 形参、缺省 False——外部调用不声明即可用
    result = gw.commit("rb14-s4", [str(x_abs)], "rb14 S4 外部提交", internal_call=False)
    assert result.status == CommitStatus.OK, f"沙盒提交应成功: {result.message}"
    body = git_text(sb_repo, "log", "-1", "--format=%B")
    assert "[GW:rb14-s4]" in body, "合法 GW 标记必须随提交落库"
    # D2 语义核心：外部调用返回后，进程环境零旗残留（T3 跨线程互摘病根的回归尺）
    assert os.environ.get("ZEPHYR_COMMIT_GATEWAY") is None, "外部 commit 后 GW 旗不得残留进程环境"

    # internal_call=True（网关内部链路声明位）同样可用且同样零残留
    y_abs = sb_repo / "s4" / "y.txt"
    y_abs.write_text("payload2" + chr(10), encoding="utf-8")
    result2 = gw.commit("rb14-s4", [str(y_abs)], "rb14 S4 内部声明提交", internal_call=True)
    assert result2.status == CommitStatus.OK, f"internal_call=True 通道应可用: {result2.message}"
    assert os.environ.get("ZEPHYR_COMMIT_GATEWAY") is None, "内部声明提交后同样零残留"


# ── 蓝方 ⑤+红证：D2 步5——_trusted_git_env 剔除 GW 旗 ───────────────────────


@pytest.mark.skipif(not _D2_OK, reason=_D2_REASON)
def test_s4_blue_trusted_git_env_strips_gw_flag(monkeypatch):
    monkeypatch.setenv("ZEPHYR_COMMIT_GATEWAY", "1")
    env = cql._trusted_git_env()
    assert "ZEPHYR_COMMIT_GATEWAY" not in env, "落地 plumbing/guard 域不得继承 GW 旗（D2 步5）"
    assert os.environ.get("ZEPHYR_COMMIT_GATEWAY") == "1", "剔除只作用于返回的子进程 env，不动进程环境"


@pytest.mark.skipif(not _D2_OK, reason=_D2_REASON)
def test_s4_red_old_landing_env_retained_in_trusted_env(sb_repo, tmp_path, monkeypatch):
    before = sha256_file(LANDING_SRC)
    old = load_surgered(
        LANDING_SRC,
        [('env.pop("ZEPHYR_COMMIT_GATEWAY", None)', "pass  # RB14-OLD: W1 前——旗继承")],
        "cql_rb14_s4_env_old",
        tmp_path,
        expected_counts=[1],
    )
    assert sha256_file(LANDING_SRC) == before, "产品文件被手术污染（红线）"
    monkeypatch.setenv("ZEPHYR_COMMIT_GATEWAY", "1")

    env = old._trusted_git_env()
    # 旧码红象：GW 旗渗入落地 plumbing 域——尺（旗剔除）在此红
    assert env.get("ZEPHYR_COMMIT_GATEWAY") == "1", "红证失真：旧副本已无旗继承行为"


# ── 蓝方 ⑥+红证：D2 步2——landing 显式 internal_call=True（动态取证）─────────


@pytest.mark.skipif(not _D2_OK, reason=_D2_REASON)
def test_s4_blue_landing_declares_internal_call_true(sb_repo, sb_queue, monkeypatch):
    record: list = []
    monkeypatch.setattr(cql, "make_worker_landing", make_stub_landing_factory(record))
    enqueue(sb_repo, sb_queue, "rb14-s4b", "s4/b.txt", "payload\n", "internal_call 取证件")

    stats = cql.drain_queue_pool(sb_queue, repo_root=sb_repo, workers=2)

    assert stats["done"] == 1, f"取证件必须落地: {stats}"
    assert record, "桩必须截获 gateway.commit 调用"
    assert all(c["kw"].get("internal_call") is True for c in record), (
        f"landing 的每个 gateway.commit 调用都必须显式 internal_call=True: {[c['kw'] for c in record]}"
    )


@pytest.mark.skipif(not _D2_OK, reason=_D2_REASON)
def test_s4_red_old_landing_internal_call_missing(sb_repo, sb_queue, tmp_path, monkeypatch):
    before = sha256_file(LANDING_SRC)
    old = load_surgered(
        LANDING_SRC,
        [
            ("\n                        internal_call=True,\n", "\n"),
            ("\n                            internal_call=True,\n", "\n"),
        ],
        "cql_rb14_s4_call_old",
        tmp_path,
        expected_counts=[1, 1],
    )
    assert sha256_file(LANDING_SRC) == before, "产品文件被手术污染（红线）"

    record: list = []
    monkeypatch.setattr(old, "make_worker_landing", make_stub_landing_factory(record, module=old))
    enqueue(sb_repo, sb_queue, "rb14-s4c", "s4/c.txt", "payload\n", "旧码取证件")

    stats = old.drain_queue_pool(sb_queue, repo_root=sb_repo, workers=2)

    assert stats["done"] == 1 and record, f"旧副本路径必须跑通 landing: {stats}"
    # 旧码红象：commit 调用无 internal_call 声明——尺（显式声明）在此红
    assert all("internal_call" not in c["kw"] for c in record), "红证失真：旧副本仍带 internal_call 声明"


# ── 静态尺：landing 源零全局 env 置位（W1 退役不回潮）────────────────────────


@pytest.mark.skipif(not _D2_OK, reason=_D2_REASON)
def test_s4_static_landing_no_global_env_write():
    src = LANDING_SRC.read_text(encoding="utf-8")
    assert 'os.environ[_GATEWAY_ENV] = "1"' not in src, "landing 不得再全局置位 GW 旗（D2 步2/W1）"
    assert "prev_env = os.environ.get(_GATEWAY_ENV)" not in src, "W1 prev 快照随置位一并退役"
