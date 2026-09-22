# [A_test] module_id: MOD-GOV-047 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV-047 | scripts/governance/commit_queue_landing.py | §三向合并拼接与身份作用域
# [MODULE] tests.governance.test_commit_queue_landing_nightfix
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] pytest; pyyaml; scripts.governance.commit_queue_landing
# [CONSUMERS] pytest 自动发现
# [STARTUP] python -m pytest tests/governance/test_commit_queue_landing_nightfix.py
# [MATURITY] testing
# [INVARIANTS] 纯函数层红蓝（零 IO 零 tmp 仓）；红=钉住夜班实测双缺陷（族尾多插拼接漂移 q-20260923-wm1-mineC-0003 死信实证 + 翻译册族身份单键误杀），绿=修复后全过；不改既有 test_commit_queue_landing.py 语义
# [MODIFY-GUARD] 夜班手术二a（st-nightfix-20260923，Lane 0b 授权）：①族尾同点多插 splice（取消 +1 伪递增）②module_translation_registry 族身份作用域化（entries=(module_path,name_zh,name_en)/algo_submodules=(module_path,node_id)，按 rel_path 键控，其余注册表走默认复合键零漂移）
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即测试失败
# [TESTS] 本文件
# [TTL] permanent
"""test_commit_queue_landing_nightfix.py — 夜班手术二a 红蓝钉（2026-09-23）。

两个实测缺陷（死信/直连绕行实证在案）：
1. **族尾多插拼接漂移**：_plan_insert_splices 对同族多条插入用 ``cached+1`` 伪递增，
   但全部插入点的正确坐标都是族尾同一行（降序应用天然保序）——第 2 条起落到
   末尾标量键（di_seam_exemptions）之后，渲染自检报"结果不可解析"
   （q-20260923-st-wm1-mineC-20260923-0003 与 st-ibt-remedy-a 批A 双死信实证）。
2. **翻译册族身份单键误杀**：module_translation_registry 的 entries/algo_submodules
   族合法持同 module_path 多条（7196/968 条实测 194 个 module_path 多条），单键身份
   一进合并就"同侧身份键重复"死信——翻译册落地结构性死锁，逼出直连绕行。

红=本文件在缺陷代码上必红；绿=修复后全过 + 既有 test_commit_queue_landing.py 回归零漂移。
"""

from __future__ import annotations

import yaml

import scripts.governance.commit_queue_landing as cql

_TRANS_REL = "docs/01_policies_and_standards/_registry/catalogs/module_translation_registry.yaml"


def _last_key_order(merged: str) -> list[str]:
    """merged 顶层键序（registry_yaml_parse_gate 同款 di_seam 居末断言的原料）。"""
    return list((yaml.safe_load(merged) or {}).keys())


class TestFamilyTailSpliceFix:
    """缺陷1：同族多条插入必须全部落在族尾之内，末尾标量键保持居末。"""

    BASE = "schema_version: 1.0.0\ntitle: t\nitems:\n  - id: a\n    path: a.md\ndi_seam_exemptions: []\n"
    THEIRS = (
        "schema_version: 1.0.0\n"
        "title: t\n"
        "items:\n"
        "  - id: a\n    path: a.md\n"
        "  - id: b\n    path: b.md\n"
        "  - id: c\n    path: c.md\n"
        "di_seam_exemptions: []\n"
    )

    def test_two_inserts_into_last_family_parse_and_stay_inside(self):
        """ours==base，theirs 追加 2 条 → 两条都进 items 族，di_seam 仍居末（q-0003 死形）。"""
        merged, err = cql.three_way_merge_registry_yaml(
            self.BASE, self.BASE, self.THEIRS, rel_path="docs/x/registry.yaml"
        )
        assert err == "", f"合并失败: {err}"
        data = yaml.safe_load(merged)  # 不可解析即炸（缺陷形态）
        ids = [e["id"] for e in data["items"]]
        assert ids == ["a", "b", "c"], f"族内条目序漂移: {ids}"
        assert _last_key_order(merged)[-1] == "di_seam_exemptions", "di_seam_exemptions 必须居末"

    def test_multi_insert_order_preserved(self):
        """同点多条插入保持 theirs 相对顺序（b 在 c 前）。"""
        merged, err = cql.three_way_merge_registry_yaml(
            self.BASE, self.BASE, self.THEIRS, rel_path="docs/x/registry.yaml"
        )
        assert err == ""
        assert merged.index("- id: b") < merged.index("- id: c"), "插入顺序须保持 theirs 序"


class TestTranslationFamilyIdentityScoping:
    """缺陷2：module_translation_registry 族真键（按 rel_path 键控，其余册零漂移）。"""

    @staticmethod
    def _entry(mp: str, nz: str, plain: str = "") -> str:
        return f"  - module_path: {mp}\n    name_zh: {nz}\n    plain_zh: {plain}\n"

    BASE_TRANS = "module_id: MOD-X\ntitle: 翻译册\nentries:\n" + _entry.__func__("src/zephyr/a.py", "甲", "旧")

    def test_entries_same_module_diff_name_both_survive(self):
        """theirs：改甲的 plain + 新增同 module_path 不同 name_zh 的乙 → 双条共存零死信。"""
        theirs = (
            "module_id: MOD-X\n"
            "title: 翻译册\n"
            "entries:\n" + self._entry("src/zephyr/a.py", "甲", "新") + self._entry("src/zephyr/a.py", "乙", "第二条")
        )
        merged, err = cql.three_way_merge_registry_yaml(self.BASE_TRANS, self.BASE_TRANS, theirs, rel_path=_TRANS_REL)
        assert err == "", f"同 module_path 不同 name 误死信: {err}"
        data = yaml.safe_load(merged)
        rows = [e for e in data["entries"] if e["module_path"] == "src/zephyr/a.py"]
        assert sorted(e["name_zh"] for e in rows) == ["乙", "甲"], f"条目集漂移: {rows}"
        assert rows[0]["plain_zh"] in ("新", "旧")

    def test_algo_submodules_multi_node_merge(self):
        """algo_submodules 同 module_path 多 node（A1 在 ours，theirs 追加 A2）→ 合并成功。"""
        base = (
            "module_id: MOD-Y\n"
            "title: 翻译册\n"
            "algo_submodules:\n"
            "  - module_path: src/zephyr/m.py\n    node_id: A1\n    name_zh: 一号\n"
        )
        theirs = (
            "module_id: MOD-Y\n"
            "title: 翻译册\n"
            "algo_submodules:\n"
            "  - module_path: src/zephyr/m.py\n    node_id: A1\n    name_zh: 一号\n"
            "  - module_path: src/zephyr/m.py\n    node_id: A2\n    name_zh: 二号\n"
        )
        merged, err = cql.three_way_merge_registry_yaml(base, base, theirs, rel_path=_TRANS_REL)
        assert err == "", f"同 module_path 多 node 误死信: {err}"
        nodes = [e["node_id"] for e in yaml.safe_load(merged)["algo_submodules"]]
        assert nodes == ["A1", "A2"]

    def test_translation_true_conflict_still_dead_letters(self):
        """真冲突仍死信：双侧各自新增同 (module_path, name_zh) 且内容异。"""
        ours = "module_id: MOD-X\ntitle: 翻译册\nentries:\n" + self._entry("src/zephyr/a.py", "甲", "ours版")
        theirs = "module_id: MOD-X\ntitle: 翻译册\nentries:\n" + self._entry("src/zephyr/a.py", "甲", "theirs版")
        merged, err = cql.three_way_merge_registry_yaml(self.BASE_TRANS, ours, theirs, rel_path=_TRANS_REL)
        assert merged is None and err, "真冲突必须死信"
        assert "同键条目内容冲突" in err


class TestDefaultIdentityZeroDrift:
    """非翻译册走默认复合键零漂移（creation_tokens 同 file 多 token 共存）。"""

    BASE = "title: t\nitems:\n  - file: a.py\n    token: t1\n"

    def test_same_file_multi_token_both_survive(self):
        theirs = "title: t\nitems:\n  - file: a.py\n    token: t1\n  - file: a.py\n    token: t2\n"
        merged, err = cql.three_way_merge_registry_yaml(self.BASE, self.BASE, theirs, rel_path="docs/x/registry.yaml")
        assert err == "", f"复合键零漂移破坏: {err}"
        assert [e["token"] for e in yaml.safe_load(merged)["items"]] == ["t1", "t2"]

    def test_non_translation_registry_single_key_still_works(self):
        """entries 族在非翻译册仍走默认身份（id 首字段）——既有 W2 测试语义不变。"""
        base = "title: t\nentries:\n  - id: a\n    path: a.md\n"
        theirs = "title: t\nentries:\n  - id: a\n    path: a.md\n  - id: b\n    path: b.md\n"
        merged, err = cql.three_way_merge_registry_yaml(base, base, theirs, rel_path="docs/x/other.yaml")
        assert err == ""
        assert [e["id"] for e in yaml.safe_load(merged)["entries"]] == ["a", "b"]


class TestTranslationUnknownFamiliesDefaultIdentity:
    """夜班追加：翻译册未知族（battle_map_steps 等）必须走默认复合键，不越权造键。"""

    BASE_STEPS = (
        "module_id: MOD-Z\n"
        "title: 翻译册\n"
        "battle_map_steps:\n"
        "  - step_id: BM-X-01\n    flow_stage: buy_flow\n    name_zh: 甲\n"
    )

    def test_battle_map_step_append_merges(self):
        theirs = (
            "module_id: MOD-Z\n"
            "title: 翻译册\n"
            "battle_map_steps:\n"
            "  - step_id: BM-X-01\n    flow_stage: buy_flow\n    name_zh: 甲\n"
            "  - step_id: BM-X-02\n    flow_stage: buy_flow\n    name_zh: 乙\n"
        )
        merged, err = cql.three_way_merge_registry_yaml(self.BASE_STEPS, self.BASE_STEPS, theirs, rel_path=_TRANS_REL)
        assert err == "", f"未知族默认身份误死信: {err}"
        assert [e["step_id"] for e in yaml.safe_load(merged)["battle_map_steps"]] == ["BM-X-01", "BM-X-02"]


# ---------------------------------------------------------------------------
# 工棚条目间重置纪律（收尾追加回归，st-nightfix-20260923）
# 病根：混乱期工棚瞬时污染——第一项文件残留未清时第二项 gate 已开跑，blob 主区
# 全过但落地侧判死（行号漂移实证）。钉死不变量：第 N 项 gate 可见内容 == 第 N 项
# 自身快照 blob，与前序项残留零相关。
# ---------------------------------------------------------------------------

import os
import subprocess
import tempfile

import scripts.commit_queue as cq
from zephyr.gov_enforcement.rule_bridge.git_commit_gateway import CommitResult, CommitStatus


def _nf_git(repo: object, *args: str, check: bool = True):
    ps_fd, msgp = tempfile.mkstemp(prefix="nf_git_")
    os.close(ps_fd)
    try:
        r = subprocess.run(["git", *args], cwd=str(repo), capture_output=True, check=False)
    finally:
        os.remove(msgp)
    if check and r.returncode != 0:
        raise AssertionError(f"git {args} 失败: {r.stderr.decode('utf-8', errors='replace')[:200]}")
    return r


import pytest


@pytest.fixture()
def tmp_repo(tmp_path):
    """裸 git 仓：main 初始提交 + dev 同点（对齐 test_commit_queue_landing 夹具语义）。"""
    repo = tmp_path / "repo"
    repo.mkdir()
    _nf_git(repo, "init", "-q", "-b", "main")
    _nf_git(repo, "config", "user.email", "t@example.com")
    _nf_git(repo, "config", "user.name", "test")
    _nf_git(repo, "config", "core.autocrlf", "false")
    (repo / ".gitignore").write_text(".runtime/\n.ailocks/\n", encoding="utf-8")
    (repo / "base.txt").write_text("base\n", encoding="utf-8")
    _nf_git(repo, "add", ".")
    _nf_git(repo, "commit", "-qm", "init")
    _nf_git(repo, "branch", "dev")
    return repo


@pytest.fixture()
def queue_root(tmp_path):
    return tmp_path / "commit_queue"


class _GateViewSpyGateway:
    """pathspec 保真桩（单文件版）+ gate 视角内容探针：commit 时先抓 worktree 目标文件字节。"""

    def __init__(self, worktree_path, target: str) -> None:
        self._wt = worktree_path
        self._target = target
        self.captures: list = []
        self.commits = 0

    def claim_files(self, session_id: str, files, adopt_prior_work: bool = False):
        return list(files)

    def release_files(self, session_id: str, files):
        pass

    def commit(
        self,
        session_id,
        files,
        message,
        allow_non_worktree=False,
        allow_tracked_drift=False,
        allow_multi_domain=False,
        allow_promote=False,
        lock_wait_timeout=None,
    ):
        target = self._wt / self._target
        # gate 视角探针：gateway 开跑瞬间 worktree 文件的字节态（含行结构）
        self.captures.append(target.read_bytes() if target.is_file() else b"<MISSING>")
        _nf_git(self._wt, "add", "--", self._target)
        ps_fd, pspec = tempfile.mkstemp(prefix="nf_ps_", suffix=".txt")
        with os.fdopen(ps_fd, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(f":(icase){self._target}\n")
        msg_fd, msgp = tempfile.mkstemp(prefix="nf_msg_", suffix=".txt")
        with os.fdopen(msg_fd, "w", encoding="utf-8") as fh:
            fh.write(message)
        try:
            r = _nf_git(self._wt, "commit", "--no-verify", "-F", msgp, f"--pathspec-from-file={pspec}", check=False)
            if r.returncode != 0:
                return CommitResult(status=CommitStatus.COMMIT_FAILED, message="nf spy commit failed")
            sha = _nf_git(self._wt, "rev-parse", "HEAD").stdout.decode("utf-8").strip()
            self.commits += 1
        finally:
            os.remove(pspec)
            os.remove(msgp)
        return CommitResult(status=CommitStatus.OK, message="nf spy committed", commit_hash=sha)


class TestWorktreeInterItemResetDiscipline:
    """同文件两版本连续落地：第二项 gate 视角必须=自身快照 blob（零第一项残留）。"""

    def test_second_item_gate_view_is_own_snapshot(self, tmp_repo, queue_root):
        v1 = "".join(f"line {i} V1_MARKER\n" for i in range(1, 13)).encode()  # 12 行
        v2 = "".join(f"line {i} V2_MARKER\n" for i in range(1, 8)).encode()  # 7 行（行数不同→残留必致行漂移）
        target = "docs/x/same_file.py"

        spy = _GateViewSpyGateway(queue_root / "worktree", target)
        landing = cql.WorktreeLanding(repo_root=tmp_repo, queue_root=queue_root, gateway=spy)

        cq.enqueue_item("s-nf-a", "feat: v1", [(target, v1)], queue_root=queue_root)
        s1 = cq.drain_queue(queue_root, landing=landing)
        assert s1["done"] == 1 and s1["dead"] == 0, f"第一项落地异常: {s1}"
        assert spy.captures == [v1], "第一项 gate 视角=V1"

        cq.enqueue_item("s-nf-b", "feat: v2", [(target, v2)], queue_root=queue_root)
        s2 = cq.drain_queue(queue_root, landing=landing)
        assert s2["done"] == 1 and s2["dead"] == 0, f"第二项落地异常: {s2}"

        # 核心断言：第二项 gate 视角 == 自身快照 V2 字节级
        assert len(spy.captures) == 2
        gate_view = spy.captures[1]
        assert gate_view == v2, f"工棚污染/残留: {gate_view[:120]!r}"
        assert b"V1_MARKER" not in gate_view, "第一项残留渗入第二项 gate 视角"
        assert gate_view.splitlines()[1] == b"line 2 V2_MARKER", "行号漂移（残留致行错位）"

        # dev 终态 = V2（真实 commit 内容）且 worktree 终态干净
        r = _nf_git(tmp_repo, "show", f"dev:{target}", check=False)
        assert r.stdout == v2, "dev 终态内容 ≠ V2"
        assert _nf_git(landing.worktree_path, "status", "--porcelain", check=False).stdout.strip() == b"", (
            "落盘后 worktree 非干净（重置纪律破损）"
        )
