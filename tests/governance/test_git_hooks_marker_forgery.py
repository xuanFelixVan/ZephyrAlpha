# [A_test] module_id: MOD-GOV_git_hooks_marker_forgery | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-005 | docs/03_modules/_domain_governance/blueprint.md | §git-hooks
# [MODULE] tests.governance.test_git_hooks_marker_forgery
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] pytest; subprocess(git); scripts/governance/git_hooks/post_commit_guard.sh; scripts/governance/git_hooks/reference_transaction_guard.sh
# [CONSUMERS] pytest 自动发现
# [STARTUP] python -m pytest tests/governance/test_git_hooks_marker_forgery.py
# [MATURITY] testing
# [INVARIANTS] 只测一次性 tmp_path 仓（永不触主区）；红队加固回归：注册表字段名不再充当 GW 通行证；不带 <old> 的 update-ref 不再享"creation"万能豁免；分叉式移动按正向审查；合法 gateway 提交与合法快进落地必须仍绿
# [MODIFY-GUARD] 两个 .sh 判据的 e2e 契约；改 hook 语义须同步本文件
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即测试失败；git 不可用 → skip
# [TESTS] 本文件
# [TTL] permanent
"""test_git_hooks_marker_forgery.py — GW 标记伪造/plumbing 绕过 hook 的 e2e 回归

全流通战役红蓝对抗车道 st-ff-rb-gov-20260918 攻面一产出（scratch 实弹 → 加严 → 回归钉）。

三条判据（红队实测病根）：
  1. post_commit_guard.sh 的"session 是否注册"原为**整份 JSON 子串 grep**，
     注册表恒含 "pid"/"held_files"/"last_heartbeat" 等键 → `[GW:pid]` 恒判合法；
  2. reference_transaction_guard.sh 原"跳过 creation（old 全零）"——实测
     `git update-ref <ref> <new>`（不带 <old>）交给 hook 的事务行 old 恒为全零，
     与该 guard 想堵的 `commit-tree + update-ref` 完全同形 → 万能豁免；
  3. 同 guard 原把"old 非 new 祖先"全当 reset 放行，分叉式移动（吞他人已落提交）不受审。

能红证据：本文件在加严前跑必红（红队首轮 scratch 复现记录见战役回报第 8 节）。
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
HOOKS = REPO_ROOT / "scripts" / "governance" / "git_hooks"
POST_COMMIT = HOOKS / "post_commit_guard.sh"
REF_TX = HOOKS / "reference_transaction_guard.sh"
SID = "st-ff-rb-gov-20260918"


def _git(repo: Path, *args: str, env: dict | None = None) -> subprocess.CompletedProcess:
    e = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
         "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}
    if env:
        e.update(env)
    return subprocess.run(["git", *args], cwd=str(repo), capture_output=True,
                          text=True, encoding="utf-8", errors="replace", env=e)


@pytest.fixture
def hook_repo(tmp_path):
    """一次性仓：dev 分支 + 两个 guard 已安装（源文件逐字节复制，仅改相对前缀）。"""
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q", "--initial-branch=dev")
    _git(repo, "config", "user.email", "t@t")
    _git(repo, "config", "user.name", "t")
    hooks_dir = repo / "hooks_src"
    hooks_dir.mkdir()
    for src in (POST_COMMIT, REF_TX):
        txt = src.read_text(encoding="utf-8").replace("scripts/governance/git_hooks/", "hooks_src/")
        (hooks_dir / src.name).write_text(txt, encoding="utf-8")
    h = repo / ".git" / "hooks"
    (h / "post-commit").write_text(
        "#!/bin/sh" + chr(10) + 'if [ -f "hooks_src/post_commit_guard.sh" ]; then' + chr(10)
        + "    . hooks_src/post_commit_guard.sh" + chr(10) + "fi" + chr(10), encoding="utf-8")
    (h / "reference-transaction").write_text(
        "#!/bin/sh" + chr(10) + 'if [ -f "hooks_src/reference_transaction_guard.sh" ]; then' + chr(10)
        + "    . hooks_src/reference_transaction_guard.sh" + chr(10) + "fi" + chr(10), encoding="utf-8")
    # 生产同款扁平注册表（SessionRegistry._save 的 indent=2 口径）
    reg = repo / ".runtime"
    reg.mkdir(exist_ok=True)
    (reg / "session_registry.json").write_text(
        "{" + chr(10) + f'  "{SID}": ' + "{" + chr(10) + '    "session_id": "' + SID + '",' + chr(10)
        + '    "pid": 0,' + chr(10) + '    "held_files": [' + chr(10) + '      "docs/x.yaml"' + chr(10)
        + '    ],' + chr(10) + '    "last_heartbeat": 1' + chr(10) + "  }" + chr(10) + "}" + chr(10),
        encoding="utf-8")
    (repo / "seed.txt").write_text("seed" + chr(10), encoding="utf-8")
    _git(repo, "add", "--", "seed.txt")
    _git(repo, "commit", "-q", "--no-verify", "-m", f"seed [GW:{SID}]",
         env={"ZEPHYR_COMMIT_GATEWAY": "1"})
    return repo


def _commit(repo: Path, name: str, msg: str, gw_env: bool = False) -> tuple[bool, str]:
    before = _git(repo, "rev-parse", "HEAD").stdout.strip()
    (repo / name).write_text(f"payload {name}" + chr(10), encoding="utf-8")
    _git(repo, "add", "--", name)
    env = {"ZEPHYR_COMMIT_GATEWAY": "1"} if gw_env else None
    r = _git(repo, "commit", "--no-verify", "-m", msg, "--", name, env=env)
    out = r.stdout + r.stderr
    return _git(repo, "rev-parse", "HEAD").stdout.strip() != before, out


def _plumbing_commit(repo: Path, parent: str, relname: str, msg: str, payload_dir: Path) -> str:
    payload_dir.mkdir(exist_ok=True)
    src = payload_dir / f"{relname}.txt"
    src.write_text("evil payload" + chr(10), encoding="utf-8")
    blob = _git(repo, "hash-object", "-w", "--", str(src)).stdout.strip()
    idx = repo / ".git" / "t_index.tmp"
    if idx.exists():
        idx.unlink()
    e = {"GIT_INDEX_FILE": str(idx)}
    _git(repo, "read-tree", parent, env=e)
    _git(repo, "update-index", "--add", "--cacheinfo", f"100644,{blob},{relname}", env=e)
    tree = _git(repo, "write-tree", env=e).stdout.strip()
    return _git(repo, "commit-tree", tree, "-p", parent, "-m", msg).stdout.strip()


# ── 判据 1：影子 token（注册表字段名当 sid）────────────────────────────────
@pytest.mark.parametrize("shadow", ["pid", "held_files", "last_heartbeat", "session_id"])
def test_shadow_token_from_registry_keys_is_reset(hook_repo, shadow):
    landed, out = _commit(hook_repo, "s.txt", f"伪造 [GW:{shadow}]")
    assert not landed, f"字段名 {shadow} 被当会话通行证，commit 未被回滚：{out}"
    assert "伪造 GW 标记" in out


def test_legit_gateway_marker_still_lands(hook_repo):
    """正控：加严不得打死正门——真会话键 + GW env 必须保留。"""
    landed, out = _commit(hook_repo, "ok.txt", f"合法网关尾注 [GW:{SID}]", gw_env=True)
    assert landed, f"合法 GW 提交被误杀：{out}"


def test_documentation_mention_of_gw_still_lands(hook_repo):
    """正控：`[GW: 空格`（文档性提及，无可解析标识符）维持既有豁免。"""
    landed, out = _commit(hook_repo, "doc.txt", "说明文档提到 [GW: 标记的口径", gw_env=True)
    assert landed, out


# ── 判据 2：不带 <old> 的 update-ref 不再是万能豁免 ─────────────────────────
def test_update_ref_without_old_is_reviewed(hook_repo):
    new = _plumbing_commit(hook_repo, _git(hook_repo, "rev-parse", "HEAD").stdout.strip(),
                           "u1.txt", "plumbing 无标记", hook_repo.parent / "pl")
    tip = _git(hook_repo, "rev-parse", "HEAD").stdout.strip()
    r = _git(hook_repo, "update-ref", "refs/heads/dev", new)
    assert r.returncode != 0, "update-ref 不带 old 仍享 creation 豁免：plumbing 提交直落 dev"
    assert _git(hook_repo, "rev-parse", "HEAD").stdout.strip() == tip
    assert "缺少合法 [GW: 标记" in r.stdout + r.stderr or "aborted by hook" in r.stderr


def test_plumbing_fast_forward_with_registered_marker_passes(hook_repo):
    """正控：真会话键 + 快进（队列落地/emergency 同形）必须仍过 ref-tx。"""
    tip = _git(hook_repo, "rev-parse", "HEAD").stdout.strip()
    new = _plumbing_commit(hook_repo, tip, "u2.txt", f"合法落地 [GW:{SID}]:emergency",
                           hook_repo.parent / "pl")
    r = _git(hook_repo, "update-ref", "refs/heads/dev", new, tip)
    assert r.returncode == 0, f"合法 CAS 快进被打死：{r.stdout}{r.stderr}"


def test_fork_move_with_forged_shadow_marker_is_blocked(hook_repo):
    """攻面一 A1-5b：分叉 + `[GW:pid]` 影子标记 → 必须阻断（两态同时收紧）。"""
    tip = _git(hook_repo, "rev-parse", "HEAD").stdout.strip()
    parent = _git(hook_repo, "rev-parse", "HEAD~0").stdout.strip()
    _commit(hook_repo, "x.txt", f"占位提交 [GW:{SID}]", gw_env=True)
    new = _plumbing_commit(hook_repo, parent, "u3.txt", "分叉 + 影子标记 [GW:pid]",
                           hook_repo.parent / "pl")
    r = _git(hook_repo, "update-ref", "refs/heads/dev", new)
    assert r.returncode != 0, "分叉式移动 + 伪造 sid 仍畅通"
    assert _git(hook_repo, "rev-parse", "HEAD").stdout.strip() != new
    shutil.rmtree(hook_repo.parent / "pl", ignore_errors=True)


def test_true_rewind_still_allowed(hook_repo):
    """正控：真回退（new 是 old 祖先，POST-COMMIT-GUARD 的 reset --soft 走这条）不拦。"""
    _commit(hook_repo, "y.txt", f"再来一笔 [GW:{SID}]", gw_env=True)
    tip = _git(hook_repo, "rev-parse", "HEAD").stdout.strip()
    back = _git(hook_repo, "rev-parse", "HEAD~1").stdout.strip()
    r = _git(hook_repo, "update-ref", "refs/heads/dev", back, tip)
    assert r.returncode == 0, f"真回退被误拦：{r.stdout}{r.stderr}"


def test_plumbing_emergency_marker_not_killed(hook_repo):
    """正控：emergency 通道（非注册 sid + `:emergency]`）不得被本收紧掐断。

    病根自纠：emergency_commit 的存在前提就是"注册表/锁不可用"，
    若在 ref-tx 硬拦未注册 sid，恰在最需要逃生时把唯一出路焊死。
    """
    tip = _git(hook_repo, "rev-parse", "HEAD").stdout.strip()
    new = _plumbing_commit(hook_repo, tip, "u4.txt", "P0 紧急修复 [GW:sess-emergency-001:emergency]",
                           hook_repo.parent / "pl4")
    r = _git(hook_repo, "update-ref", "refs/heads/dev", new, tip)
    assert r.returncode == 0, f"emergency 逃生通道被误杀：{r.stdout}{r.stderr}"
    reports = list((hook_repo / ".runtime/reconcile_reports").glob("reference_transaction_guard_*.json"))
    assert reports, "warn_only 必须落审计（可疑不静默）"
    assert any("unregistered_gw_sid" in p.read_text(encoding="utf-8") for p in reports)
