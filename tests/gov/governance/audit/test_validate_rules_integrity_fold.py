# [A_test] module_id: SRC-TST-F1FOLD | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.governance.audit.test_validate_rules_integrity_fold
# [DOMAIN] D_GOV_AUDIT
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-TEST-F1FOLD | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""test_validate_rules_integrity_fold.py — F1 衍生提交并入原子化单测

覆盖 S18 F1 判据：
- register_fold：changed_files 命中受保护文件 → 工作树 hash 重基线（返回 True）；
  无受保护改动 → 基线不变（返回 False，不写盘）。
- 判据②（手动编辑 rules_integrity_db hash → 必报 TAMPERED）：check() 检测。
- 安全等价（不降级红蓝发现3）：未入 changed_files 的受保护文件即使工作树被篡改，
  register_fold 复用旧 DB hash → check() 仍报 TAMPERED（WIP 篡改检测保住）。

测试隔离：monkeypatch _REPO_ROOT/_INTEGRITY_DB/RULES_MANIFEST 到 tmp_path，
不触碰生产 DB 与真实受保护文件（遵守"测试禁写生产路径"红线）。
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[4]
_META_DIR = _PROJECT_ROOT / "scripts" / "governance" / "meta"
if str(_META_DIR) not in sys.path:
    sys.path.insert(0, str(_META_DIR))

import validate_rules_integrity as v  # noqa: E402


@pytest.fixture()
def sandbox(tmp_path, monkeypatch):
    """构造隔离沙箱：tmp_path 作 _REPO_ROOT，两个假受保护文件 + 假 manifest + 隔离 DB。"""
    root = tmp_path
    # 假受保护文件 A（将被"提交"，工作树==即将提交内容）
    fa = root / "alpha.py"
    fa.write_text("print('alpha v1')\n", encoding="utf-8")
    # 假受保护文件 B（不在 changed_files，模拟 WIP 篡改场景）
    fb = root / "beta.py"
    fb.write_text("print('beta v1')\n", encoding="utf-8")

    manifest = [
        {"path": "alpha.py", "critical": True, "desc": "假受保护文件 A"},
        {"path": "beta.py", "critical": True, "desc": "假受保护文件 B"},
    ]
    db_path = root / "rules_integrity_db.json"

    monkeypatch.setattr(v, "_REPO_ROOT", root)
    monkeypatch.setattr(v, "_INTEGRITY_DB", db_path)
    monkeypatch.setattr(v, "RULES_MANIFEST", manifest)
    # _hash_git_head 在非 git 沙箱返回 None（git show 失败）→ register_fold 回退工作树/旧 DB
    return {"root": root, "db": db_path, "alpha": fa, "beta": fb}


def _read_db(db_path: Path) -> dict:
    return json.loads(db_path.read_text(encoding="utf-8"))


def test_fold_rehashes_changed_protected_file(sandbox):
    """changed_files 命中受保护文件 → 工作树 hash 重基线，返回 True。"""
    db = sandbox["db"]
    # 初始基线：alpha v1
    assert v.register_fold({"alpha.py"}) is True
    base = _read_db(db)
    h_v1 = base["files"]["alpha.py"]["hash"]

    # 模拟本提交链改动 alpha（reconciler/用户改盘 → 工作树==即将提交内容）
    sandbox["alpha"].write_text("print('alpha v2')\n", encoding="utf-8")
    # 未折入前 check 应报 alpha TAMPERED（工作树 v2 != DB v1）
    assert v.check()["clean"] is False

    # 折入：alpha 在 changed_files → 重基线到 v2 工作树 hash
    assert v.register_fold({"alpha.py"}) is True
    after = _read_db(db)
    h_v2 = after["files"]["alpha.py"]["hash"]
    assert h_v2 != h_v1
    # 折入后 check 干净（DB == 工作树最终态）
    assert v.check()["clean"] is True


def test_fold_noop_when_no_protected_change(sandbox):
    """无受保护文件改动（changed_files 不含受保护项）→ 基线不变，返回 False，不写盘。"""
    db = sandbox["db"]
    assert v.register_fold({"alpha.py", "beta.py"}) is True  # 建初始基线
    base = _read_db(db)

    # changed_files 仅含非受保护文件 → 所有受保护文件复用旧 DB hash → 无变化
    assert v.register_fold({"some_untracked.txt", "docs/x.md"}) is False
    assert _read_db(db) == base  # DB 字节未变（registered_at 也未刷新）


def test_manual_db_hash_edit_reports_tampered(sandbox):
    """判据②：手动编辑 rules_integrity_db hash → check() 必报 TAMPERED。"""
    db = sandbox["db"]
    v.register_fold({"alpha.py", "beta.py"})  # 建基线（check 干净）
    assert v.check()["clean"] is True

    # 攻击者手动篡改 DB 里 alpha 的 hash（试图合法化对 alpha.py 的篡改）
    data = _read_db(db)
    data["files"]["alpha.py"]["hash"] = "deadbeefdeadbeef"
    db.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    result = v.check()
    # alpha.py 工作树 hash != 被篡改的 DB hash → TAMPERED
    assert result["clean"] is False
    tampered_files = [r["file"] for r in result["results"] if r["status"] == "TAMPERED"]
    assert "alpha.py" in tampered_files


def test_fold_preserves_wip_tamper_detection(sandbox):
    """安全等价：未入 changed_files 的受保护文件即使工作树被篡改，fold 复用旧 hash → check 仍报 TAMPERED。

    红蓝发现3 防护不降级：攻击者篡改 beta.py（受保护）但不把它纳入提交，
    随后提交无关文件触发 fold（changed 不含 beta）→ fold 不为 beta 重基线 →
    check() 工作树 hash != DB 旧 hash → TAMPERED 仍被检出。
    """
    db = sandbox["db"]
    v.register_fold({"alpha.py", "beta.py"})  # 建基线
    beta_base_hash = _read_db(db)["files"]["beta.py"]["hash"]

    # 攻击者篡改 beta.py 工作树，但不纳入提交
    sandbox["beta"].write_text("print('beta PWNED')\n", encoding="utf-8")

    # 提交无关文件触发 fold（changed 仅含 alpha，不含 beta）
    v.register_fold({"alpha.py"})

    # beta 复用旧 DB hash（未被篡改合法化）
    assert _read_db(db)["files"]["beta.py"]["hash"] == beta_base_hash
    # check() 检出 beta TAMPERED（工作树 PWNED != DB 旧 hash）
    result = v.check()
    assert result["clean"] is False
    tampered_files = [r["file"] for r in result["results"] if r["status"] == "TAMPERED"]
    assert "beta.py" in tampered_files


# ── 甲-0 own-diff 收窄（Owner 批 2026-10-13·维护六班；宪法 §3.1/§3.4）──────────────


@pytest.fixture()
def head_channel(sandbox, monkeypatch):
    """head 参考面 + 网关通道沙箱：参考面恒与盘面不等，own 范围由 in_commit 注入。"""
    monkeypatch.setattr(v, "_read_head_blobs", lambda paths: {p: "REF-MISMATCH" for p in paths})
    monkeypatch.setattr(v, "_MIN_DYNAMIC_GATES", 0)  # 假 manifest 不触发 MQ-3 空清单红
    monkeypatch.setenv("ZEPHYR_COMMIT_GATEWAY", "1")
    monkeypatch.setenv("GIT_INDEX_FILE", str(sandbox["root"] / "own-scope.index"))
    return sandbox


def _foreign_audit_calls(monkeypatch) -> list[list[str]]:
    """把共享审计原语换成记录器，验证"外来降级"确实留痕（不是只改文案）。"""
    import zephyr.gov_enforcement.commit_gates._diff_helpers as dh

    calls: list[list[str]] = []
    monkeypatch.setattr(
        dh,
        "_audit_foreign_staged",
        lambda gateway, session_id, foreign, *, gate_name: calls.append(list(foreign)),
    )
    return calls


class TestOwnScopeNarrowing:
    """收窄只改"谁为该件受阻"：own 件判定式一字不动，外来件转 warn+审计。"""

    def test_foreign_drift_downgraded_and_own_kept_blocked(self, head_channel, monkeypatch):
        """本袋只碰 alpha（在途）时，beta 的外来漂移不得拦本袋；alpha 自身缺失照旧阻断。"""
        calls = _foreign_audit_calls(monkeypatch)
        (head_channel["root"] / "beta.py").write_text("PWNED\n", encoding="utf-8")
        (head_channel["root"] / "alpha.py").unlink()  # own 件缺失＝critical 阻断
        monkeypatch.setattr(v, "_staged_change_set", lambda paths: {"alpha.py"})

        result = v.check(baseline_mode="head")

        statuses = {r["file"]: r["status"] for r in result["results"]}
        assert statuses["beta.py"] == "FOREIGN_WIP"
        assert statuses["alpha.py"] == "MISSING"
        assert result["tampered_count"] == 1 and result["clean"] is False
        assert result["foreign_count"] == 1 and result["own_scope_narrowed"] is True
        assert calls == [["beta.py"]], "外来降级必须经共享审计原语留痕"

    def test_empty_own_scope_makes_every_drift_foreign(self, head_channel, monkeypatch):
        """本袋零受保护件在途（治理面袋的典型形态）→ 全部漂移按外来，袋放行。"""
        _foreign_audit_calls(monkeypatch)
        (head_channel["root"] / "beta.py").write_text("WIP by another session\n", encoding="utf-8")
        monkeypatch.setattr(v, "_staged_change_set", lambda paths: set())

        result = v.check(baseline_mode="head")

        assert result["own_scope_narrowed"] is True
        assert {r["file"]: r["status"] for r in result["results"]}["beta.py"] == "FOREIGN_WIP"
        assert result["tampered_count"] == 0 and result["clean"] is True

    def test_outside_channel_keeps_full_scan_blocking(self, head_channel, monkeypatch):
        """反向对照（不收窄面）：通道外人工直跑/独立巡检仍把外来漂移判 TAMPERED。"""
        monkeypatch.delenv("ZEPHYR_COMMIT_GATEWAY")
        (head_channel["root"] / "beta.py").write_text("drift\n", encoding="utf-8")
        monkeypatch.setattr(v, "_staged_change_set", lambda paths: set())

        result = v.check(baseline_mode="head")

        assert result["own_scope_narrowed"] is False
        assert {r["file"]: r["status"] for r in result["results"]}["beta.py"] == "TAMPERED"
        assert result["clean"] is False

    def test_snapshot_mode_does_not_narrow(self, head_channel, monkeypatch):
        """回滚态（snapshot 参考面）不收窄——own 解释位在该态本就不存在（in_commit 恒空）。"""
        monkeypatch.setattr(v, "_staged_change_set", lambda paths: set())
        (head_channel["root"] / "beta.py").write_text("drift\n", encoding="utf-8")

        result = v.check(baseline_mode="snapshot")

        assert result["own_scope_narrowed"] is False

    def test_narrowing_helper_is_fail_closed(self, tmp_path, monkeypatch):
        """helper 三态：无通道 env→不收窄；有通道无临时索引→不收窄；两者齐→收窄且空 own 合法。"""
        monkeypatch.delenv("ZEPHYR_COMMIT_GATEWAY", raising=False)
        monkeypatch.delenv("GIT_INDEX_FILE", raising=False)
        assert v._own_scope_narrowing(set())[0] is False
        monkeypatch.setenv("ZEPHYR_COMMIT_GATEWAY", "1")
        assert v._own_scope_narrowing(set())[0] is False
        monkeypatch.setenv("GIT_INDEX_FILE", str(tmp_path / "idx"))
        active, own, view, norm = v._own_scope_narrowing({"scripts/x.py"})
        assert active is True and view is not None and norm is not None
        assert own == {str(norm(view, "scripts/x.py"))}
        assert v._own_scope_narrowing(set())[1] == set()
