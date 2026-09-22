# [BLUEPRINT] MOD-GOV_COMMIT_GATES | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §session_worktree audit wrapper
# [MODULE] tests.governance.rule_bridge.test_session_worktree_audit_wrapper
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] pytest; zephyr.gov_enforcement.rule_bridge.session_worktree（session_worktree_commit 包装+审计 helper）
# [CONSUMERS] D5 堵点本覆盖面守卫（worktree 路径阻断必落本+横幅）
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] mock impl（_session_worktree_commit_impl）返回构造结果 dict——不建真实 worktree（零磁盘/git 副作用，审计写 tmp_path）
# [MODIFY-GUARD] 与 session_worktree.py 包装逻辑同批演进
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError
# [TESTS] self
# [A_module] module_id=MOD-GOV_COMMIT_GATES | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""session_worktree_commit 审计包装测试（D5 覆盖面补齐，2026-09-13 Owner 复核发现）。

病根：worktree 提交绕过 GitCommitGateway，其自有门禁阻断（HELD-OVERLAP/DCR/
CROSS-COMMIT-DEP/gates）不进堵点本 commit_block_events.jsonl——堵点本只见
共享区提交，worktree 会话堵点静默丢失。包装后阻断必落本（source=worktree_commit）
+成功慢提交落 commit_slow+全路径打提醒横幅（与 gateway.commit 对齐）。
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import zephyr.gov_enforcement.rule_bridge.session_worktree as sw
from zephyr.gov_enforcement.rule_bridge.session_worktree import session_worktree_commit


def _read_events(tmp_path: Path) -> list[dict]:
    p = tmp_path / ".runtime" / "audit" / "commit_block_events.jsonl"
    if not p.is_file():
        return []
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]


@pytest.fixture()
def mocked_impl(monkeypatch, tmp_path):
    """mock _session_worktree_commit_impl：返回预设 dict 并记录调用参数。

    同时隔离横幅（记录调用而非真打印——横幅行为已有 TestBottleneckBanner 专测）。
    """
    calls: list[dict] = []
    banner_calls: list[Path] = []

    def _impl(session_id, files, message, opts=None, project_root=None):
        calls.append(
            {
                "session_id": session_id,
                "files": files,
                "message": message,
                "opts": opts or {},
                "project_root": project_root,
            }
        )
        return mocked_impl.result

    def _banner(root, context=""):
        banner_calls.append(root)

    monkeypatch.setattr(sw, "_session_worktree_commit_impl", _impl)
    monkeypatch.setattr(sw, "_print_wt_bottleneck_banner", _banner)
    mocked_impl.calls = calls
    mocked_impl.banner_calls = banner_calls
    mocked_impl.result = {"session_id": "s1", "status": "OK", "message": "", "commit_hash": "abc1234"}
    return mocked_impl


class TestBlockEventAudit:
    """worktree 提交阻断 → 落堵点本（source=worktree_commit）。"""

    def test_held_overlap_blocked_audited(self, mocked_impl, tmp_path):
        mocked_impl.result = {
            "session_id": "s1",
            "status": "FAILED",
            "commit_hash": "",
            "message": "HELD_OVERLAP_VIOLATION: 文件被其他活跃 session 持有",
            "held_overlap": True,
        }
        result = session_worktree_commit("s1", ["a.py"], "m", project_root=tmp_path)
        assert result["status"] == "FAILED"
        evs = _read_events(tmp_path)
        assert len(evs) == 1
        assert evs[0]["event"] == "commit_blocked"
        assert evs[0]["gate_id"] == "HELD-OVERLAP"
        assert evs[0]["source"] == "worktree_commit"
        assert evs[0]["session_id"] == "s1"
        assert evs[0]["files_count"] == 1
        assert "gate_chain_ms" in evs[0], "报表聚合依赖 gate_chain_ms 字段"

    def test_gate_message_gate_id_extracted(self, mocked_impl, tmp_path):
        """message 含『门禁 XXX 阻断』→ 精确提取门禁号。"""
        mocked_impl.result = {
            "session_id": "s1",
            "status": "FAILED",
            "commit_hash": "",
            "message": "门禁 FILE-PLACEMENT-TTL 阻断: 永久区新文件",
        }
        session_worktree_commit("s1", ["docs/x.md"], "m", project_root=tmp_path)
        evs = _read_events(tmp_path)
        assert evs[0]["gate_id"] == "FILE-PLACEMENT-TTL"

    def test_worktree_required_gate_results_attribution(self, mocked_impl, tmp_path):
        """WORKTREE-REQUIRED 归因（红蓝 v3 P1-2+P1-4 组合）：worktree 通道调用被其拦截
        属语义错误（skip 名单治本防复发）；万一真拦，落账归因经 gate_results 直取仍精确。"""
        mocked_impl.result = {
            "session_id": "s1",
            "status": "FAILED",
            "commit_hash": "",
            "message": "pre-commit gate 阻断（worktree 路径对标 GitCommitGateway）"
            ": WORKTREE-REQUIRED: 非 worktree 提交被拦截",
            "gate_results": [{"gate_id": "WORKTREE-REQUIRED", "detail": "非 worktree 提交被拦截"}],
        }
        session_worktree_commit("s1", ["a.py"], "m", project_root=tmp_path)
        evs = _read_events(tmp_path)
        assert evs[0]["gate_id"] == "WORKTREE-REQUIRED", "组合验证：直取 gate_results 归因精确"

    def test_dcr_and_cross_dep_flags(self, mocked_impl, tmp_path):
        for flag, expected in (
            ("directory_contract_violation", "DIRECTORY-CONTRACT"),
            ("cross_commit_dep_blocked", "CROSS-COMMIT-DEP"),
        ):
            r = {"session_id": "s1", "status": "FAILED", "commit_hash": "", "message": "x", flag: True}
            mocked_impl.result = r
            session_worktree_commit("s1", ["a.py"], "m", project_root=tmp_path)
            evs = _read_events(tmp_path)
            assert evs[-1]["gate_id"] == expected

    def test_base_sync_failed_audited_as_worktree_base_conflict(self, mocked_impl, tmp_path):
        """堵点本 §2.1 残余 UNKNOWN×26 治本：base 落地冲突阻断端到端落账归因精确（非 UNKNOWN）。"""
        mocked_impl.result = {
            "session_id": "s1",
            "status": "FAILED",
            "commit_hash": "",
            "message": "worktree base 过期且 rebase 冲突（3 commits）. 手动处理: git rebase ...",
            "base_sync_failed": True,
        }
        session_worktree_commit("s1", ["a.py"], "m", project_root=tmp_path)
        evs = _read_events(tmp_path)
        assert len(evs) == 1
        assert evs[0]["event"] == "commit_blocked"
        assert evs[0]["gate_id"] == "WORKTREE-BASE-CONFLICT", "base 冲突此前恒落 UNKNOWN"
        assert evs[0]["source"] == "worktree_commit"

    def test_not_found_not_audited(self, mocked_impl, tmp_path):
        """worktree 不存在（not_found）=用法/环境前置错误，非门禁堵点 → 不记。"""
        mocked_impl.result = {
            "session_id": "s1",
            "status": "FAILED",
            "commit_hash": "",
            "message": "worktree 不存在",
            "not_found": True,
        }
        session_worktree_commit("s1", ["a.py"], "m", project_root=tmp_path)
        assert _read_events(tmp_path) == []

    def test_nothing_to_commit_not_audited(self, mocked_impl, tmp_path):
        mocked_impl.result = {"session_id": "s1", "status": "NOTHING_TO_COMMIT", "commit_hash": "", "message": ""}
        session_worktree_commit("s1", ["a.py"], "m", project_root=tmp_path)
        assert _read_events(tmp_path) == []


class TestWrapperSemantics:
    """包装透传语义：参数原样传 impl、结果原样返回、横幅全路径打。"""

    def test_params_passthrough_and_result_identity(self, mocked_impl, tmp_path):
        result = session_worktree_commit(
            "s1",
            ["a.py", "b.py"],
            "msg",
            project_root=tmp_path,
            allow_overlap=True,
            allow_promote=True,
            allow_migration=True,
            depends_on_sessions=["s2"],
        )
        assert result["status"] == "OK"
        assert len(mocked_impl.calls) == 1
        call = mocked_impl.calls[0]
        assert call["session_id"] == "s1"
        opts = call["opts"]  # 4 开关打包 opts dict 透传（NO-LONG-PARAM-LIST 治本）
        assert opts["allow_overlap"] is True and opts["depends_on_sessions"] == ["s2"]
        assert opts["allow_promote"] is True and opts["allow_migration"] is True
        assert mocked_impl.banner_calls == [tmp_path], "成功路径也打提醒横幅"

    def test_ok_fast_not_audited(self, mocked_impl, tmp_path):
        """快速成功 → 零事件（阈值化防爆炸）。"""
        session_worktree_commit("s1", ["a.py"], "m", project_root=tmp_path)
        assert _read_events(tmp_path) == []

    def test_audit_failure_never_breaks_commit(self, monkeypatch, tmp_path):
        """审计写入异常（如目录只读）→ 提交结果原样返回（fail-open 铁律）。"""
        monkeypatch.setattr(
            sw,
            "_audit_wt_block_event",
            lambda *a, **k: (_ for _ in ()).throw(OSError("disk full")),
        )
        monkeypatch.setattr(
            sw,
            "_print_wt_bottleneck_banner",
            lambda *a, **k: (_ for _ in ()).throw(OSError("boom")),
        )

        def _impl(session_id, files, message, opts=None, project_root=None):
            return {"session_id": session_id, "status": "FAILED", "commit_hash": "", "message": "x"}

        monkeypatch.setattr(sw, "_session_worktree_commit_impl", _impl)
        result = session_worktree_commit("s1", ["a.py"], "m", project_root=tmp_path)
        assert result["status"] == "FAILED", "审计/横幅失败绝不改变提交结果"


class TestPreMergeGateAudit:
    """pre-merge gate 阻断 → 落堵点本（source=pre_merge_gate）。"""

    def test_event_derived_from_detail(self, tmp_path):
        """event 由 detail 推导（NO-LONG-PARAM-LIST 治本）：commit_slow 前缀→slow，
        否则 commit_blocked；source 字段区分来源域。"""
        sw._audit_wt_block_event(
            tmp_path,
            "s1",
            "-",
            3,
            61_000.0,
            "commit_slow: worktree commit 61.2s > 60s",
        )
        sw._audit_wt_block_event(
            tmp_path,
            "s1",
            "HELD-OVERLAP",
            3,
            1_200.0,
            "HELD_OVERLAP_VIOLATION: 文件被其他活跃 session 持有",
            source="pre_merge_gate",
        )
        evs = _read_events(tmp_path)
        assert evs[0]["event"] == "commit_slow" and evs[0]["source"] == "worktree_commit"
        assert evs[1]["event"] == "commit_blocked" and evs[1]["source"] == "pre_merge_gate"

    def test_gate_id_extraction_helper(self, tmp_path):
        """_wt_block_gate_id 判定链：gate_results 直取 > 标志字段 > message 正则 > UNKNOWN。"""
        assert sw._wt_block_gate_id({"held_overlap": True, "message": "anything"}) == "HELD-OVERLAP"
        assert sw._wt_block_gate_id({"message": "门禁 CREATE-GUARD 阻断: 无 token"}) == "CREATE-GUARD"
        assert sw._wt_block_gate_id({"message": "FOREIGN_CHANGE_VIOLATION: xxx"}) == "FOREIGN-CHANGE"
        assert sw._wt_block_gate_id({"message": "奇怪的错误"}) == "UNKNOWN"
        # 堵点本 §2.1 残余病灶治本：commit 路径 base 落地冲突（无 gate_results）此前落 UNKNOWN
        assert (
            sw._wt_block_gate_id(
                {
                    "status": "FAILED",
                    "base_sync_failed": True,
                    "message": "worktree base 过期且 rebase 冲突（3 commits）",
                }
            )
            == "WORKTREE-BASE-CONFLICT"
        )
        assert (
            sw._wt_block_gate_id(
                {
                    "status": "FAILED",
                    "base_sync_failed": True,
                    "message": "worktree base 对齐阻断：worktree 有 5 个未提交改动",
                }
            )
            == "WORKTREE-BASE-CONFLICT"
        )
        # merge 路径优先级：带 gate_results=BASE-FRESHNESS-MERGE 时直取先命中，不受新标志分支影响
        assert (
            sw._wt_block_gate_id(
                {
                    "base_sync_failed": True,
                    "message": "worktree base 过期",
                    "gate_results": [{"gate_id": "BASE-FRESHNESS-MERGE", "detail": "x"}],
                }
            )
            == "BASE-FRESHNESS-MERGE"
        )

    def test_gate_results_direct_attribution(self, mocked_impl, tmp_path):
        """gate_results 直取归因（红蓝 v3 P1-2 治本）：拼接 message 正则失配不再落 UNKNOWN。"""
        # 防御空值：条目缺 gate_id / 空 gate_results → 回退原判定链
        assert (
            sw._wt_block_gate_id(
                {"gate_results": [{"gate_id": "", "detail": "x"}], "message": "门禁 SPLIT-COORDINATION 阻断: x"}
            )
            == "SPLIT-COORDINATION"
        )
        assert sw._wt_block_gate_id({"gate_results": [], "message": "奇怪的错误"}) == "UNKNOWN"
        mocked_impl.result = {
            "session_id": "s1",
            "status": "GATE_VIOLATION",
            "commit_hash": "",
            "message": "pre-commit gate 阻断（worktree 路径对标 GitCommitGateway）"
            ": CREATE-GUARD: 无 creation_token（红蓝 v3 实证失配样本）",
            "gate_violation": True,
            "gate_results": [{"gate_id": "CREATE-GUARD", "detail": "无 creation_token"}],
        }
        session_worktree_commit("s1", ["a.py"], "m", project_root=tmp_path)
        evs = _read_events(tmp_path)
        assert evs[0]["event"] == "commit_blocked"
        assert evs[0]["gate_id"] == "CREATE-GUARD", "直取 gate_results 而非正则失配落 UNKNOWN"
        assert evs[0]["source"] == "worktree_commit"
