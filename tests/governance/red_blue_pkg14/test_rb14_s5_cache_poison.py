# [A_test] module_id: MOD-TEST-RB14-S5 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-RB14 | src/zephyr/gov_enforcement/rule_bridge/gate_cache_preflight.py | §T7/B2 新键（cb3c13b74f 内容哈希）
# [MODULE] governance.red_blue_pkg14.test_rb14_s5_cache_poison
# [DOMAIN] D_GOV_ENFORCEMENT
# [DEPENDENCIES] pytest; zephyr.gov_enforcement.rule_bridge.gate_cache_preflight; zephyr...git_commit_gateway; _common(本包)
# [CONSUMERS] pytest 自动发现
# [STARTUP] python -m pytest tests/governance/red_blue_pkg14/test_rb14_s5_cache_poison.py
# [MATURITY] testing
# [INVARIANTS] 全沙盒（tmp 仓 + tmp 门实现面/注册表；git show 只读提取 cb3c13b74f
#   blob 至 tmp，产品文件零触碰）。三连毒判据（新键=「门实际读什么」）：门源码一字节
#   → miss（spec_sha）；注册表字节 → miss（GATE_INPUT_MANIFEST）；HEAD 推进 → 仍 hit
#   （键禁含全局态）。红证双件：①本 worktree 现码=df8507ac9b 中间形态（键缺
#   spec_sha/manifest 分量）→ 门源码毒不判失（尺红）；②dev 已收口形态（cb3c13b74f）
#   同攻击全防（尺蓝）。
# [MODIFY-GUARD] 包14 场景5（缓存投毒）
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即测试失败
# [TESTS] 本文件
# [TTL] task_bound
"""test_rb14_s5_cache_poison.py — 场景5「缓存投毒」红蓝对抗（T7/B2 新键尺）。

状态勘察结论（对抗发现，详见对抗报告）：
- 新键收口形态 = dev 分支 commit cb3c13b74f（spec_sha + GATE_INPUT_MANIFEST + 批量
  ls-files）——本 worktree（csx-pkg5b，基于 df8507ac9b）尚未含该收口件；
- 故本场景蓝方真源=cb3c13b74f blob（只读提取），红方=worktree 现行中间形态。
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

import zephyr.gov_enforcement.rule_bridge.gate_cache_preflight as gcp_wt  # worktree 现行形态
from governance.red_blue_pkg14._common import git
from zephyr.gov_enforcement.rule_bridge.git_commit_gateway import GitCommitGateway

_GATE_ID = "NO-HARDCODED-URL"  # cb3c13b74f 白名单在册台
_SCOPE = "rb14-s5-own-scope"
_DETAIL = "clean"
_CB3C = "cb3c13b74f"  # dev 已收口的新键 commit（任务口径的「新键」）
_BLOB_PATH = "src/zephyr/gov_enforcement/rule_bridge/gate_cache_preflight.py"


def _load_cb3c_module(tmp_path: Path):
    """只读提取 dev 收口形态 blob → tmp 副本 → 独立模块名装载（产品文件零触碰）。"""
    r = subprocess.run(
        ["git", "show", f"{_CB3C}:{_BLOB_PATH}"],
        capture_output=True,
        timeout=30,
    )
    assert r.returncode == 0, f"cb3c13b74f blob 提取失败（对象不在共享库?）: {r.stderr.decode(errors='replace')[:200]}"
    dst = tmp_path / "gate_cache_preflight_cb3c.py"
    dst.write_bytes(r.stdout)
    spec = importlib.util.spec_from_file_location("gcp_rb14_s5_new", dst)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["gcp_rb14_s5_new"] = mod
    spec.loader.exec_module(mod)
    # 真源核验：提取物必须确为新键形态（spec_sha + manifest 在场）
    assert hasattr(mod, "GATE_INPUT_MANIFEST") and hasattr(mod, "_spec_sha"), (
        "提取的 cb3c13b74f blob 不含新键分量——红蓝真源错位"
    )
    return mod


def _make_lab(tmp_path: Path, mod):
    """沙盒投毒实验台：own staged 件 + 假门实现面 + 注册表文件 + 指定键形态的 cache。"""
    repo = tmp_path / "s5_repo"
    repo.mkdir()
    git(repo, "init", "-q", "--initial-branch=dev")
    git(repo, "config", "user.email", "t@t")
    git(repo, "config", "user.name", "t")
    git(repo, "config", "core.autocrlf", "false")
    (repo / "base.txt").write_text("base\n", encoding="utf-8")
    git(repo, "add", "--", "base.txt")
    git(repo, "commit", "-qm", "init")  # HEAD 必须存在（中间形态 compute_fingerprint 读 HEAD）
    (repo / "a.txt").write_text("own staged content\n", encoding="utf-8")
    git(repo, "add", "--", "a.txt")
    spec_dir = repo / "src" / "zephyr" / "gov_enforcement" / "commit_gates"
    spec_dir.mkdir(parents=True)
    gate_file = spec_dir / "rb14_fake_gate.py"
    gate_file.write_text("# rb14 fake gate implementation v1\n", encoding="utf-8")
    reg_file = repo / "registry" / "rb14_reg.yaml"
    reg_file.parent.mkdir()
    reg_file.write_text("rb14: v1\n", encoding="utf-8")
    gw = GitCommitGateway(project_root=repo)
    lab = SimpleNamespace(mod=mod, gw=gw, repo=repo, gate_file=gate_file, reg_file=reg_file, manifest_orig=None)
    if hasattr(mod, "GATE_INPUT_MANIFEST"):
        # 键形态自带 manifest 机制才注入声明（中间形态无此属性=无注册表判失面）。
        # 注入只作用于本进程模块对象（cb3c 副本/在册模块），不写任何产品文件。
        lab.manifest_orig = mod.GATE_INPUT_MANIFEST
        mod.GATE_INPUT_MANIFEST = {_GATE_ID: ("registry/rb14_reg.yaml",)}

    def fresh_cache():
        cache = mod.GateResultCache(gw, ["a.txt"])
        assert cache.usable, "缓存基座必须可用"
        return cache

    lab.fresh_cache = fresh_cache  # type: ignore[attr-defined]
    return lab


def _seed(lab) -> None:
    lab.fresh_cache().store(_GATE_ID, _SCOPE, _DETAIL)


def _run_three_poisons(lab, *, gate_poison_misses: bool):
    """三连毒攻击序；按被测形态声明毒①的预期（miss=防住）。返回毒③后的 lookup。"""
    _seed(lab)
    assert lab.fresh_cache().lookup(_GATE_ID, _SCOPE) == _DETAIL, "基线必须命中"

    # 毒①：门源码一字节
    src = lab.gate_file.read_text(encoding="utf-8")
    lab.gate_file.write_text(src + "# one poisoned byte\n", encoding="utf-8")
    hit1 = lab.fresh_cache().lookup(_GATE_ID, _SCOPE)
    lab.gate_file.write_text(src, encoding="utf-8")
    if gate_poison_misses:
        assert hit1 is None, "毒① 门源码字节变化必须判失（spec_sha）"
        assert lab.fresh_cache().lookup(_GATE_ID, _SCOPE) == _DETAIL, "毒① 还原后回 hit（内容哈希可逆）"
    else:
        assert hit1 == _DETAIL, "红证失真：该形态对门源码毒竟判失了"

    # 毒②：注册表字节（仅新键形态有判失面）
    if lab.manifest_orig is not None:
        reg = lab.reg_file.read_text(encoding="utf-8")
        lab.reg_file.write_text(reg + "poisoned: true\n", encoding="utf-8")
        assert lab.fresh_cache().lookup(_GATE_ID, _SCOPE) is None, "毒② 注册表字节变化必须判失（manifest）"
        lab.reg_file.write_text(reg, encoding="utf-8")
        assert lab.fresh_cache().lookup(_GATE_ID, _SCOPE) == _DETAIL, "毒② 还原后回 hit"

    # 毒③：HEAD 推进 → 仍 hit（新键禁含 HEAD——他人推进不得作废我的缓存）
    git(lab.repo, "add", "-A")
    git(lab.repo, "commit", "-qm", "rb14 S5 head advance")
    return lab.fresh_cache().lookup(_GATE_ID, _SCOPE)


# ── 蓝方：cb3c13b74f 新键——三连毒前两必 miss、第三必 hit ────────────────────


def test_s5_blue_new_key_cb3c_three_poisons(tmp_path):
    lab = _make_lab(tmp_path, _load_cb3c_module(tmp_path))
    final = _run_three_poisons(lab, gate_poison_misses=True)
    assert final == _DETAIL, "毒③ HEAD 推进必须仍命中（新键语义：键不含全局态）"


def test_s5_blue_new_key_own_content_flip_misses(tmp_path):
    """补充毒面：own staged 内容一字节 → miss（inputs_sha，两形态同防）。"""
    lab = _make_lab(tmp_path, _load_cb3c_module(tmp_path))
    _seed(lab)
    (lab.repo / "a.txt").write_text("own staged content CHANGED\n", encoding="utf-8")
    git(lab.repo, "add", "--", "a.txt")
    assert lab.fresh_cache().lookup(_GATE_ID, _SCOPE) is None, "own 内容变化必须判失"


def test_s5_blue_worktree_key_head_advance_still_hits(tmp_path):
    """worktree 中间形态对毒③（HEAD 推进）也已防住（df8507ac9b 语义：键不含 HEAD）。"""
    lab = _make_lab(tmp_path, gcp_wt)
    _seed(lab)
    git(lab.repo, "add", "-A")
    git(lab.repo, "commit", "-qm", "head advance on intermediate key")
    assert lab.fresh_cache().lookup(_GATE_ID, _SCOPE) == _DETAIL, "HEAD 推进不得作废缓存"


# ── 红证：worktree 现行中间形态（df8507ac9b）——门源码毒不判失 ───────────────


@pytest.mark.skipif(
    hasattr(gcp_wt, "_spec_sha"), reason="本检出已含包7收口件（新键在场）——中间形态红证仅对 df8507ac9b 基有意义"
)
def test_s5_red_worktree_intermediate_key_gate_source_poison_still_hits(tmp_path):
    """红方战果：中间形态键缺 spec_sha 分量——门源码修复/篡改后 10min TTL 内
    旧 passed=True 判定继续放行（投毒窗）。此即包7收口件 cb3c13b74f 要拔的刺。"""
    lab = _make_lab(tmp_path, gcp_wt)
    final = _run_three_poisons(lab, gate_poison_misses=False)
    assert final == _DETAIL, "HEAD 推进不得作废缓存（两形态共同语义）"
