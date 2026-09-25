# [A_test] module_id: SRC-TST-P3HEAD | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-P3HEAD | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.governance.audit.test_integrity_head_baseline
# [DOMAIN] D_GOV_AUDIT
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-TEST-P3HEAD | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""test_integrity_head_baseline.py — P3（integrity 基线 HEAD 派生制）红绿双态测试

战役 B0/M1·P3（2026-09-24，MQ-1~4 裁定落地）。判据来源：csx_p3_patch_draft.md §9。
每条先证能红（snapshot 态对照）或证"两态都红"（不放松哨兵 R-2/R-5）：

- R-1  假 TAMPERED 不得复发：本提交合法改写受保护文件（own-scope 临时索引）→
       head 态 CHANGING_IN_COMMIT（clean）；snapshot 态同场景 TAMPERED（历史事故复现对照）。
- R-2  真 WIP 篡改必须判红（未暂存漂移，解释位不吃）。
- R-3  HEAD 基线被改写（amend）必须立刻判红；snapshot 态看不见（滞后快照盲区对照）。
- R-4  改 DB 洗白在 head 态结构性失效（snapshot 态仍可洗=历史洞，作对照）。
- R-5  critical 删除永不放行（对抗性：假装路径在提交集内，MISSING 分支仍不吃豁免；MQ-4）。
- R-6  head 态 post-flush 零同步 spawn（gateway 实测）+ landing 双路 mode 分派静态尺。
- R-8  动态清单低于阈值 → MANIFEST_DEGRADED 红（MQ-3：空≠正常）。
- R-9  新模块零定时器（宪法运维红线第 3 条机检）。
- MQ-2 解释位 own-scope 边界：外来在途路径不配享有解释位（仍 TAMPERED）。

R-7（连续落地 chore(integrity) 记账件归零）属生产观测口径，归红蓝/终报对账，不在此单测。

测试隔离：git 沙箱在 tmp_path；_REPO_ROOT/_INTEGRITY_DB/RULES_MANIFEST 全部 monkeypatch；
禁跑 test_ops_guard_red_team.py（本仓真实删源码地雷，与本文件无关但同目录纪律留痕）。
"""

from __future__ import annotations

import json
import subprocess
import sys
import types
from pathlib import Path

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
_META_DIR = _PROJECT_ROOT / "scripts" / "governance" / "meta"
if str(_META_DIR) not in sys.path:
    sys.path.insert(0, str(_META_DIR))

import validate_rules_integrity as v  # noqa: E402


def _git(root: Path, *args: str) -> str:
    r = subprocess.run(
        ["git", *args],
        cwd=root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    assert r.returncode == 0, f"git {args} failed rc={r.returncode}: {r.stderr[:200]}"
    return r.stdout


@pytest.fixture()
def git_sandbox(tmp_path, monkeypatch):
    """git 沙箱：tmp_path 仓库 + HEAD 含 alpha v1；manifest/DB 全 monkeypatch。"""
    root = tmp_path
    _git(root, "init", "-q")
    _git(root, "config", "user.email", "t@example.com")
    _git(root, "config", "user.name", "t")
    (root / "alpha.py").write_text("print('alpha v1')\n", encoding="utf-8")
    (root / "beta.py").write_text("print('beta v1')\n", encoding="utf-8")
    _git(root, "add", "alpha.py", "beta.py")
    _git(root, "commit", "-q", "-m", "init")

    manifest = [
        {"path": "alpha.py", "critical": True, "desc": "受保护A"},
        {"path": "beta.py", "critical": True, "desc": "受保护B"},
    ]
    monkeypatch.setattr(v, "_REPO_ROOT", root)
    monkeypatch.setattr(v, "_INTEGRITY_DB", root / "rules_integrity_db.json")
    monkeypatch.setattr(v, "RULES_MANIFEST", manifest)
    v.register()  # v1 基线（HEAD 面读取路径与生产同源）
    return {"root": root, "alpha": root / "alpha.py", "beta": root / "beta.py"}


def _status_map(result: dict) -> dict:
    return {x["file"]: x["status"] for x in result["results"]}


def _own_scope_index(root: Path, monkeypatch, staged: list[str]) -> None:
    """模拟网关 own-scope 临时索引：GIT_INDEX_FILE = HEAD 树 + 仅 staged 列表。"""
    tmp_idx = root / ".git" / "tmp_own_scope_index"
    monkeypatch.setenv("GIT_INDEX_FILE", str(tmp_idx))
    _git(root, "read-tree", "HEAD")
    if staged:
        _git(root, "add", *staged)


def test_r1_changing_in_commit_not_tampered(git_sandbox, monkeypatch):
    """R-1：own-scope 在途变更 → head 态解释为 CHANGING_IN_COMMIT；snapshot 态判 TAMPERED（对照红）。"""
    root = git_sandbox["root"]
    git_sandbox["alpha"].write_text("print('alpha v2')\n", encoding="utf-8")
    _own_scope_index(root, monkeypatch, staged=["alpha.py"])

    r = v.check(baseline_mode="head")
    assert _status_map(r)["alpha.py"] == "CHANGING_IN_COMMIT"
    assert r["clean"] is True and r["tampered_count"] == 0 and r["changing_count"] == 1
    assert r["baseline_mode"] == "head"

    # 对照（红证）：snapshot 态=DB 停在 v1 ⇒ 同场景判 TAMPERED（历史 6 次阻断的事故机理）
    monkeypatch.delenv("GIT_INDEX_FILE")
    rs = v.check(baseline_mode="snapshot")
    assert _status_map(rs)["alpha.py"] == "TAMPERED"
    assert rs["clean"] is False


def test_r2_unstaged_wip_tamper_still_red(git_sandbox):
    """R-2（不放松哨兵）：未暂存的 WIP 篡改两态都必须 TAMPERED。"""
    git_sandbox["alpha"].write_text("print('tampered')\n", encoding="utf-8")
    for mode in ("head", "snapshot"):
        r = v.check(baseline_mode=mode)
        assert _status_map(r)["alpha.py"] == "TAMPERED", f"mode={mode} 必须红"
        assert r["clean"] is False and r["tampered_count"] == 1


def test_r3_head_rewrite_visible_immediately(git_sandbox):
    """R-3：HEAD 被 amend 改写 → head 态立刻红；snapshot 态结构性看不见（滞后盲区对照）。"""
    root = git_sandbox["root"]
    git_sandbox["alpha"].write_text("print('evil v2')\n", encoding="utf-8")
    _git(root, "add", "alpha.py")
    _git(root, "commit", "-q", "--amend", "-m", "init rewritten")
    git_sandbox["alpha"].write_text("print('alpha v1')\n", encoding="utf-8")  # 工作树复原 v1

    r = v.check(baseline_mode="head")
    assert _status_map(r)["alpha.py"] == "TAMPERED", "HEAD 面已换内容，工作树 v1 != head → 必须红"
    # 对照：snapshot 态 DB 仍指 v1 ⇒ 判 OK（改写历史在旧制下不可见）
    rs = v.check(baseline_mode="snapshot")
    assert _status_map(rs)["alpha.py"] == "OK"


def test_r4_db_edit_cannot_launder_in_head(git_sandbox):
    """R-4：head 态下改 DB hash 洗白失效（DB 退出判定链）；snapshot 态仍可洗（历史洞对照）。"""
    root, db = git_sandbox["root"], v._INTEGRITY_DB
    git_sandbox["alpha"].write_text("print('tampered')\n", encoding="utf-8")
    data = json.loads(Path(db).read_text(encoding="utf-8"))
    data["files"]["alpha.py"]["hash"] = v._hash_file(root / "alpha.py")  # 攻击者：把基线改成篡改后值
    Path(db).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    r = v.check(baseline_mode="head")
    assert _status_map(r)["alpha.py"] == "TAMPERED", "head 态读 HEAD 面，改 DB 无效"
    rs = v.check(baseline_mode="snapshot")
    assert _status_map(rs)["alpha.py"] == "OK", "snapshot 态=历史行为（对照，不改其语义）"


def test_r5_critical_missing_never_excused(git_sandbox, monkeypatch):
    """R-5（MQ-4 哨兵）：对抗性把删除路径塞进解释位集，MISSING 仍计数阻断（显式不吃豁免）。"""
    git_sandbox["alpha"].unlink()
    monkeypatch.setattr(v, "_staged_change_set", lambda paths: {"alpha.py"})
    r = v.check(baseline_mode="head")
    assert _status_map(r)["alpha.py"] == "MISSING"
    assert r["clean"] is False and r["tampered_count"] == 1


def test_r6_head_mode_zero_sync_spawn_in_post_flush(git_sandbox, monkeypatch):
    """R-6a：head 态 post-flush 零 --register spawn，意图账恰 1 行（gateway 实测）。"""
    from zephyr.gov_enforcement.rule_bridge.git_commit_gateway import GitCommitGateway

    root = git_sandbox["root"]
    gw = GitCommitGateway(project_root=root)
    monkeypatch.setenv("ZEPHYR_INTEGRITY_BASELINE", "head")

    calls: list = []
    real_run = subprocess.run

    def _recorder(*a, **k):
        cmd = list(a[0]) if a else list(k.get("args") or [])
        if any("validate_rules_integrity" in str(x) for x in cmd):
            calls.append(cmd)  # 只拦截并记录 --register/--fold spawn
            return subprocess.CompletedProcess(args=cmd, returncode=0, stdout=b"", stderr=b"")
        return real_run(*a, **k)  # 其余（含 run_git 的 rev-parse）透传真跑

    monkeypatch.setattr(subprocess, "run", _recorder)
    gw._post_flush_rules_integrity_re_register("s1")
    monkeypatch.setattr(subprocess, "run", real_run)

    assert calls == [] or all("validate_rules_integrity" not in map(str, c) for c in calls), (
        f"head 态 post-flush 不得 spawn --register/--fold（意图记录的 git rev-parse 允许），实际: {calls}"
    )
    ledger = root / ".runtime" / "derived_dirty" / "integrity_intent.jsonl"
    assert ledger.exists(), "意图账必须落一行"
    lines = [json.loads(x) for x in ledger.read_text(encoding="utf-8").splitlines() if x.strip()]
    assert len(lines) == 1
    assert lines[0]["reason"] == "post_flush_register" and lines[0]["session_id"] == "s1"
    assert len(lines[0]["head_sha"]) == 12


def test_r6b_landing_paths_dispatch_by_mode():
    """R-6b：landing 双路（legacy/池化）都按 mode 分派——snapshot 保留旧 spawn，head 只记意图。"""
    src = (_PROJECT_ROOT / "scripts" / "governance" / "commit_queue_landing.py").read_text(encoding="utf-8")
    assert src.count('if self._integrity_baseline_mode() == "snapshot":') == 2
    assert src.count("self._record_integrity_refresh_intent(item, qid)") == 2


def test_r8_manifest_degradation_red(git_sandbox, monkeypatch):
    """R-8（MQ-3）：动态清单低于阈值 → MANIFEST_DEGRADED 红（空≠正常，防改名波静默归零复发）。"""
    monkeypatch.setattr(v, "_DYNAMIC_GATE_ENTRIES", [])
    r = v.check(baseline_mode="head")
    assert any(x["status"] == "MANIFEST_DEGRADED" for x in r["results"])
    assert r["clean"] is False and r["tampered_count"] >= 1


def test_r9_no_timers_in_new_modules():
    """R-9：新模块零定时器/零 sleep（宪法运维红线第 3 条的机检兑现）。"""
    src = (_PROJECT_ROOT / "src" / "zephyr" / "gov_enforcement" / "derived_dirty_ledger.py").read_text(encoding="utf-8")
    for bad in ("threading.Timer", "time.sleep", "schedule.every", "Timer(", "sleep("):
        assert bad not in src, f"新增模块不得引入定时器原语: {bad}"


def test_mq2_explainer_own_scope_only(git_sandbox, monkeypatch):
    """MQ-2①：解释位 own-scope 边界——外来在途路径（不在本提交临时索引）不配享有，仍 TAMPERED。"""
    root = git_sandbox["root"]
    # beta 先进"真实 index"（模拟外来会话在途暂存），再改工作树
    git_sandbox["beta"].write_text("print('beta foreign staged')\n", encoding="utf-8")
    _git(root, "add", "beta.py")  # 真实 index（此时 GIT_INDEX_FILE 未设）
    # alpha 是本提交 own-scope 文件
    git_sandbox["alpha"].write_text("print('alpha v2')\n", encoding="utf-8")
    _own_scope_index(root, monkeypatch, staged=["alpha.py"])

    r = v.check(baseline_mode="head")
    st = _status_map(r)
    assert st["alpha.py"] == "CHANGING_IN_COMMIT", "own 文件在临时索引内 → 解释"
    assert st["beta.py"] == "TAMPERED", "外来在途路径不配享有解释位（MQ-2①）"
    assert r["clean"] is False
