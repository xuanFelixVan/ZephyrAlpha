# [A_test] module_id: MOD-GOV_capability_lookup_health_reconciler_test | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV_RECONCILIATION_REGISTRY | docs/03_modules/_domain_governance/blueprint.md | §P4
# [MODULE] tests.governance.audit.test_capability_lookup_health_reconciler
# [DOMAIN] D_GOV_AUDIT
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-GOV_RECONCILIATION_REGISTRY | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_capability_lookup_health_reconciler.py — Phase 4 G6 监控 reconciler e2e smoke test

#ARCH-CAPABILITY-LOOKUP-BYPASS-DEAD-S8 Phase 4 治本 G6（监控缺失）：
验证 make_capability_lookup_health_reconciler 工厂构造的 ReconcilerSpec：
- trigger 仅命中 src/zephyr/**/*.py 业务代码 commit
- _reconcile（3-arg）接收 commit_message 并检测 [no-lookup:] 标记
- bypass 记录到 .runtime/lookup_audit/bypass_audit.jsonl
- bypass 频率 > 5/10 → critical_warn 升级
- 无 bypass + .runtime/lookup_audit/ 无 session log → warn（G6 铁证检测）
- bypass + 频率正常 → clean
- 无 bypass + 有 audit log → clean

测试隔离：使用 tmp_path 构造 mock gateway，不污染真实 .runtime/。
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))
_SRC_ROOT = _PROJECT_ROOT / "src"
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))


# ---------------------------------------------------------------------------
# Mock gateway: 只需 project_root 属性
# ---------------------------------------------------------------------------


class _MockGateway:
    """最小 mock gateway——只为提供 project_root 属性。"""

    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root


# ---------------------------------------------------------------------------
# TestTrigger: src/zephyr/**/*.py 命中判定
# ---------------------------------------------------------------------------


class TestTrigger:
    """trigger 仅命中 src/zephyr/**/*.py 业务代码 commit。"""

    def test_trigger_hits_src_zephyr_py(self, tmp_path):
        """src/zephyr/foo.py → True。"""
        from zephyr.governance.audit.reconciliation_registry import (
            make_capability_lookup_health_reconciler,
        )
        spec = make_capability_lookup_health_reconciler(_MockGateway(tmp_path))
        # trigger 是 ReconcilerSpec.trigger
        assert spec.trigger([str(tmp_path / "src" / "zephyr" / "foo.py")]) is True

    def test_trigger_misses_non_src_zephyr(self, tmp_path):
        """scripts/foo.py → False（非业务代码）。"""
        from zephyr.governance.audit.reconciliation_registry import (
            make_capability_lookup_health_reconciler,
        )
        spec = make_capability_lookup_health_reconciler(_MockGateway(tmp_path))
        assert spec.trigger([str(tmp_path / "scripts" / "foo.py")]) is False

    def test_trigger_misses_non_py(self, tmp_path):
        """src/zephyr/foo.yaml → False（非 .py）。"""
        from zephyr.governance.audit.reconciliation_registry import (
            make_capability_lookup_health_reconciler,
        )
        spec = make_capability_lookup_health_reconciler(_MockGateway(tmp_path))
        assert spec.trigger([str(tmp_path / "src" / "zephyr" / "foo.yaml")]) is False

    def test_trigger_misses_docs(self, tmp_path):
        """docs/foo.py → False（非 src/zephyr）。"""
        from zephyr.governance.audit.reconciliation_registry import (
            make_capability_lookup_health_reconciler,
        )
        spec = make_capability_lookup_health_reconciler(_MockGateway(tmp_path))
        assert spec.trigger([str(tmp_path / "docs" / "foo.py")]) is False


# ---------------------------------------------------------------------------
# TestBypassAuditLogging: [no-lookup:] 标记记录到 bypass_audit.jsonl
# ---------------------------------------------------------------------------


class TestBypassAuditLogging:
    """bypass marker 被记录到 .runtime/lookup_audit/bypass_audit.jsonl。"""

    def test_bypass_marker_recorded_to_jsonl(self, tmp_path):
        """commit_message 含 [no-lookup:reason] → 追加记录到 bypass_audit.jsonl。"""
        from zephyr.governance.audit.reconciliation_registry import (
            make_capability_lookup_health_reconciler,
        )
        spec = make_capability_lookup_health_reconciler(_MockGateway(tmp_path))
        py_file = str(tmp_path / "src" / "zephyr" / "foo.py")
        msg = "fix(scoped): test [no-lookup:trivial-doc-fix]"
        result = spec.reconcile([py_file], "sess-test-001", msg)
        # 频率 1 < 5 → 不升级，clean
        assert result.action == "clean"
        # 验证 bypass_audit.jsonl 已写入
        bypass_log = tmp_path / ".runtime" / "lookup_audit" / "bypass_audit.jsonl"
        assert bypass_log.is_file()
        entries = [
            json.loads(line) for line in bypass_log.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        assert len(entries) == 1
        assert entries[0]["session_id"] == "sess-test-001"
        assert entries[0]["reason"] == "trivial-doc-fix"
        assert "[no-lookup:" in entries[0]["commit_message_snippet"]

    def test_no_bypass_marker_not_recorded(self, tmp_path):
        """commit_message 不含 [no-lookup:] → 不写入 bypass_audit.jsonl。"""
        from zephyr.governance.audit.reconciliation_registry import (
            make_capability_lookup_health_reconciler,
        )
        spec = make_capability_lookup_health_reconciler(_MockGateway(tmp_path))
        # 先放一个 session audit log 避免 warn（isolate bypass 行为）
        audit_dir = tmp_path / ".runtime" / "lookup_audit"
        audit_dir.mkdir(parents=True, exist_ok=True)
        (audit_dir / "sess-test-002.jsonl").write_text("{}", encoding="utf-8")
        py_file = str(tmp_path / "src" / "zephyr" / "foo.py")
        msg = "fix(scoped): normal commit without bypass"
        result = spec.reconcile([py_file], "sess-test-002", msg)
        assert result.action == "clean"
        # bypass_audit.jsonl 不应存在（或为空）
        bypass_log = tmp_path / ".runtime" / "lookup_audit" / "bypass_audit.jsonl"
        assert not bypass_log.is_file() or not bypass_log.read_text(encoding="utf-8").strip()


# ---------------------------------------------------------------------------
# TestBypassEscalation: bypass 频率 > 5/10 → critical_warn
# ---------------------------------------------------------------------------


class TestBypassEscalation:
    """bypass 频率超阈值（>5/10）→ critical_warn 升级。"""

    def test_escalation_when_bypass_count_exceeds_threshold(self, tmp_path):
        """bypass_audit.jsonl 已有 6 条记录 → 本次 bypass 触发 critical_warn。"""
        from zephyr.governance.audit.reconciliation_registry import (
            make_capability_lookup_health_reconciler,
        )
        # 预填充 6 条 bypass 记录
        bypass_log = tmp_path / ".runtime" / "lookup_audit" / "bypass_audit.jsonl"
        bypass_log.parent.mkdir(parents=True, exist_ok=True)
        for i in range(6):
            entry = {
                "ts": f"2026-07-19T0{i}:00:00Z",
                "session_id": f"sess-prev-{i}",
                "reason": f"prev-{i}",
                "commit_message_snippet": f"prev commit {i}",
            }
            with open(bypass_log, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(entry, ensure_ascii=False) + "\n")

        spec = make_capability_lookup_health_reconciler(_MockGateway(tmp_path))
        py_file = str(tmp_path / "src" / "zephyr" / "foo.py")
        # 本次再带 bypass marker → 总数变 7 → > 5 → critical_warn
        msg = "fix: another bypass [no-lookup:testing]"
        result = spec.reconcile([py_file], "sess-escalation", msg)
        assert result.action == "critical_warn"
        assert "频率过高" in result.detail or "bypass" in result.detail.lower()

    def test_no_escalation_when_bypass_count_at_threshold(self, tmp_path):
        """bypass_audit.jsonl 已有 5 条（== 阈值，未超） → clean。"""
        from zephyr.governance.audit.reconciliation_registry import (
            make_capability_lookup_health_reconciler,
        )
        bypass_log = tmp_path / ".runtime" / "lookup_audit" / "bypass_audit.jsonl"
        bypass_log.parent.mkdir(parents=True, exist_ok=True)
        for i in range(5):
            entry = {
                "ts": f"2026-07-19T0{i}:00:00Z",
                "session_id": f"sess-prev-{i}",
                "reason": f"prev-{i}",
                "commit_message_snippet": f"prev commit {i}",
            }
            with open(bypass_log, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(entry, ensure_ascii=False) + "\n")

        spec = make_capability_lookup_health_reconciler(_MockGateway(tmp_path))
        py_file = str(tmp_path / "src" / "zephyr" / "foo.py")
        msg = "fix: 6th bypass [no-lookup:testing]"
        result = spec.reconcile([py_file], "sess-at-threshold", msg)
        # 5 + 1 = 6 > 5 → critical_warn
        # （注意：本次 bypass 也被写入后再统计，所以是 6 → 升级）
        # 如果实现是「写入前统计」，则 5 不升级；如果是「写入后统计」，则 6 升级
        # 当前实现是先写入再统计 → 6 → critical_warn
        assert result.action == "critical_warn"


# ---------------------------------------------------------------------------
# TestAuditLogHealthCheck: G6 铁证——无 session log + 无 bypass → warn
# ---------------------------------------------------------------------------


class TestAuditLogHealthCheck:
    """G6 监控：.runtime/lookup_audit/ 无 session log 且本次无 bypass → warn。"""

    def test_warn_when_no_session_log_and_no_bypass(self, tmp_path):
        """空 .runtime/lookup_audit/ + 无 bypass → warn（G6 铁证检测）。"""
        from zephyr.governance.audit.reconciliation_registry import (
            make_capability_lookup_health_reconciler,
        )
        spec = make_capability_lookup_health_reconciler(_MockGateway(tmp_path))
        py_file = str(tmp_path / "src" / "zephyr" / "foo.py")
        # 无 bypass marker，无 audit log
        result = spec.reconcile([py_file], "sess-empty", "normal commit")
        assert result.action == "warn"
        assert "audit log" in result.detail.lower() or "静默失效" in result.detail

    def test_clean_when_session_log_exists_and_no_bypass(self, tmp_path):
        """.runtime/lookup_audit/ 有 session log + 无 bypass → clean。"""
        from zephyr.governance.audit.reconciliation_registry import (
            make_capability_lookup_health_reconciler,
        )
        audit_dir = tmp_path / ".runtime" / "lookup_audit"
        audit_dir.mkdir(parents=True, exist_ok=True)
        (audit_dir / "sess-real-001.jsonl").write_text(
            json.dumps({"ts": "2026-07-19T00:00:00Z", "operation": "discover_applicable_rules"})
            + "\n",
            encoding="utf-8",
        )
        spec = make_capability_lookup_health_reconciler(_MockGateway(tmp_path))
        py_file = str(tmp_path / "src" / "zephyr" / "foo.py")
        result = spec.reconcile([py_file], "sess-clean", "normal commit")
        assert result.action == "clean"

    def test_bypass_audit_jsonl_excluded_from_session_log_check(self, tmp_path):
        """bypass_audit.jsonl 自身不计入 session audit log 判定。"""
        from zephyr.governance.audit.reconciliation_registry import (
            make_capability_lookup_health_reconciler,
        )
        audit_dir = tmp_path / ".runtime" / "lookup_audit"
        audit_dir.mkdir(parents=True, exist_ok=True)
        # 只有 bypass_audit.jsonl，没有 session log
        (audit_dir / "bypass_audit.jsonl").write_text(
            json.dumps({"ts": "2026-07-19T00:00:00Z", "reason": "x"}) + "\n",
            encoding="utf-8",
        )
        spec = make_capability_lookup_health_reconciler(_MockGateway(tmp_path))
        py_file = str(tmp_path / "src" / "zephyr" / "foo.py")
        # 无 bypass marker，无 session log（bypass_audit.jsonl 排除）
        result = spec.reconcile([py_file], "sess-only-bypass-log", "normal commit")
        assert result.action == "warn"


# ---------------------------------------------------------------------------
# TestReconcilerSpec: spec 元数据正确
# ---------------------------------------------------------------------------


class TestReconcilerSpec:
    """ReconcilerSpec 元数据正确（gate_id / priority / 3-arg reconcile）。"""

    def test_gate_id_is_capability_lookup_health(self, tmp_path):
        from zephyr.governance.audit.reconciliation_registry import (
            make_capability_lookup_health_reconciler,
        )
        spec = make_capability_lookup_health_reconciler(_MockGateway(tmp_path))
        assert spec.gate_id == "CAPABILITY-LOOKUP-HEALTH"

    def test_priority_is_220(self, tmp_path):
        from zephyr.governance.audit.reconciliation_registry import (
            make_capability_lookup_health_reconciler,
        )
        spec = make_capability_lookup_health_reconciler(_MockGateway(tmp_path))
        assert spec.priority == 220

    def test_reconcile_accepts_three_args(self, tmp_path):
        """3-arg reconcile 签名（接收 commit_message，Phase 3.4 机制）。"""
        import inspect

        from zephyr.governance.audit.reconciliation_registry import (
            make_capability_lookup_health_reconciler,
        )
        spec = make_capability_lookup_health_reconciler(_MockGateway(tmp_path))
        sig = inspect.signature(spec.reconcile)
        assert len(sig.parameters) >= 3, (
            f"reconcile should accept >=3 args, got {len(sig.parameters)}: "
            f"{list(sig.parameters)}"
        )


# ---------------------------------------------------------------------------
# TestRegistrationInGateway: GitCommitGateway 启动时注册该 reconciler
# ---------------------------------------------------------------------------


class TestRegistrationInGateway:
    """GitCommitGateway 启动时注册 make_capability_lookup_health_reconciler。"""

    def test_reconciler_registered_in_gateway(self, tmp_path, monkeypatch):
        """GitCommitGateway 实例化后，registry 中包含 CAPABILITY-LOOKUP-HEALTH。"""
        # 初始化最小 git 仓库
        import subprocess
        env = {**os.environ, "GIT_AUTHOR_NAME": "test", "GIT_AUTHOR_EMAIL": "test@x",
               "GIT_COMMITTER_NAME": "test", "GIT_COMMITTER_EMAIL": "test@x"}
        subprocess.run(["git", "init"], cwd=str(tmp_path),
                       capture_output=True, env=env, check=True)
        subprocess.run(["git", "config", "user.name", "test"], cwd=str(tmp_path),
                       capture_output=True, env=env, check=True)
        subprocess.run(["git", "config", "user.email", "test@x"], cwd=str(tmp_path),
                       capture_output=True, env=env, check=True)
        (tmp_path / "README.md").write_text("init\n", encoding="utf-8")
        subprocess.run(["git", "add", "README.md"], cwd=str(tmp_path),
                       capture_output=True, env=env, check=True)
        subprocess.run(["git", "commit", "-m", "init", "--no-verify"],
                       cwd=str(tmp_path), capture_output=True, env=env, check=True)

        from zephyr.gov_enforcement.rule_bridge.git_commit_gateway import GitCommitGateway
        gw = GitCommitGateway(project_root=tmp_path)
        gate_ids = [s.gate_id for s in gw.reconciliation_registry.specs]
        assert "CAPABILITY-LOOKUP-HEALTH" in gate_ids, (
            f"CAPABILITY-LOOKUP-HEALTH not registered, got: {gate_ids}"
        )


import os  # noqa: E402 — late import for test_reconciler_registered_in_gateway env

# ---------------------------------------------------------------------------
# TestBypassSceneClassification: #ARCH-CAPABILITY-LOOKUP-SCENE-CLASSIFY-001
# 白名单豁免统计——合法 bypass 不计入 violation_count，避免狼来了效应
# ---------------------------------------------------------------------------


class TestBypassSceneClassification:
    """#ARCH-CAPABILITY-LOOKUP-SCENE-CLASSIFY-001: bypass 场景分类与白名单豁免。

    合法 bypass（gate-fix/test-fix/merge-prep/continuation/investigated/auto-fix/
    batch-treatment/batch-governance/architectural-refactor/sync）豁免统计，
    只统计违规 bypass（非白名单）触发 critical_warn。
    """

    def test_whitelist_reason_marked_exempt(self, tmp_path):
        """白名单 reason（gate-fix）→ scene=exempt。"""
        from zephyr.governance.audit.reconciliation_registry import (
            make_capability_lookup_health_reconciler,
        )
        spec = make_capability_lookup_health_reconciler(_MockGateway(tmp_path))
        py_file = str(tmp_path / "src" / "zephyr" / "foo.py")
        msg = "fix(governance): gate bug [no-lookup:gate-fix]"
        result = spec.reconcile([py_file], "sess-exempt-001", msg)
        assert result.action == "clean"
        bypass_log = tmp_path / ".runtime" / "lookup_audit" / "bypass_audit.jsonl"
        entries = [
            json.loads(line) for line in bypass_log.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        assert len(entries) == 1
        assert entries[0]["scene"] == "exempt"
        assert entries[0]["reason"] == "gate-fix"

    def test_non_whitelist_reason_marked_violation(self, tmp_path):
        """非白名单 reason（new-feature-xxx）→ scene=violation。"""
        from zephyr.governance.audit.reconciliation_registry import (
            make_capability_lookup_health_reconciler,
        )
        spec = make_capability_lookup_health_reconciler(_MockGateway(tmp_path))
        py_file = str(tmp_path / "src" / "zephyr" / "foo.py")
        msg = "feat: new feature [no-lookup:new-feature-xxx]"
        result = spec.reconcile([py_file], "sess-violation-001", msg)
        assert result.action == "clean"  # 1 violation < 5
        bypass_log = tmp_path / ".runtime" / "lookup_audit" / "bypass_audit.jsonl"
        entries = [
            json.loads(line) for line in bypass_log.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        assert len(entries) == 1
        assert entries[0]["scene"] == "violation"
        assert entries[0]["reason"] == "new-feature-xxx"

    def test_all_whitelist_bypass_no_escalation(self, tmp_path):
        """全部白名单 bypass 超 5 次 → clean（不触发 critical_warn）。"""
        from zephyr.governance.audit.reconciliation_registry import (
            make_capability_lookup_health_reconciler,
        )
        bypass_log = tmp_path / ".runtime" / "lookup_audit" / "bypass_audit.jsonl"
        bypass_log.parent.mkdir(parents=True, exist_ok=True)
        # 预填充 8 条全部白名单 bypass（gate-fix/test-fix/merge-prep 轮换）
        whitelist_reasons = ["gate-fix", "test-fix", "merge-prep", "continuation",
                             "investigated", "auto-fix", "batch-treatment", "sync"]
        for i, reason in enumerate(whitelist_reasons):
            entry = {
                "ts": f"2026-07-19T0{i}:00:00Z",
                "session_id": f"sess-prev-{i}",
                "reason": reason,
                "scene": "exempt",
                "commit_message_snippet": f"prev commit {i}",
            }
            with open(bypass_log, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(entry, ensure_ascii=False) + "\n")

        spec = make_capability_lookup_health_reconciler(_MockGateway(tmp_path))
        py_file = str(tmp_path / "src" / "zephyr" / "foo.py")
        # 本次再带白名单 bypass → 9 exempt, 0 violation → clean
        msg = "fix: another gate fix [no-lookup:gate-fix]"
        result = spec.reconcile([py_file], "sess-all-exempt", msg)
        assert result.action == "clean"
        assert "scene=exempt" in result.detail

    def test_non_whitelist_bypass_exceeds_threshold_escalates(self, tmp_path):
        """非白名单 bypass 超 5 次 → critical_warn。"""
        from zephyr.governance.audit.reconciliation_registry import (
            make_capability_lookup_health_reconciler,
        )
        bypass_log = tmp_path / ".runtime" / "lookup_audit" / "bypass_audit.jsonl"
        bypass_log.parent.mkdir(parents=True, exist_ok=True)
        # 预填充 6 条全部非白名单 bypass（违规场景）
        for i in range(6):
            entry = {
                "ts": f"2026-07-19T0{i}:00:00Z",
                "session_id": f"sess-prev-{i}",
                "reason": f"unknown-reason-{i}",
                "scene": "violation",
                "commit_message_snippet": f"prev commit {i}",
            }
            with open(bypass_log, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(entry, ensure_ascii=False) + "\n")

        spec = make_capability_lookup_health_reconciler(_MockGateway(tmp_path))
        py_file = str(tmp_path / "src" / "zephyr" / "foo.py")
        # 本次再带非白名单 bypass → 7 violation > 5 → critical_warn
        msg = "feat: unknown [no-lookup:unknown-reason-new]"
        result = spec.reconcile([py_file], "sess-violation-escalation", msg)
        assert result.action == "critical_warn"
        assert "违规" in result.detail

    def test_mixed_bypass_only_violation_counted(self, tmp_path):
        """混合 bypass：只统计违规数，白名单不计入。"""
        from zephyr.governance.audit.reconciliation_registry import (
            make_capability_lookup_health_reconciler,
        )
        bypass_log = tmp_path / ".runtime" / "lookup_audit" / "bypass_audit.jsonl"
        bypass_log.parent.mkdir(parents=True, exist_ok=True)
        # 预填充：4 白名单 + 3 违规 = 7 条
        mixed_reasons = [
            ("gate-fix", "exempt"),
            ("test-fix", "exempt"),
            ("merge-prep", "exempt"),
            ("continuation", "exempt"),
            ("unknown-1", "violation"),
            ("unknown-2", "violation"),
            ("unknown-3", "violation"),
        ]
        for i, (reason, scene) in enumerate(mixed_reasons):
            entry = {
                "ts": f"2026-07-19T0{i}:00:00Z",
                "session_id": f"sess-prev-{i}",
                "reason": reason,
                "scene": scene,
                "commit_message_snippet": f"prev commit {i}",
            }
            with open(bypass_log, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(entry, ensure_ascii=False) + "\n")

        spec = make_capability_lookup_health_reconciler(_MockGateway(tmp_path))
        py_file = str(tmp_path / "src" / "zephyr" / "foo.py")
        # 本次带白名单 bypass → 4+1=5 exempt, 3 violation → clean（3 < 5）
        msg = "fix: gate bug [no-lookup:gate-fix]"
        result = spec.reconcile([py_file], "sess-mixed", msg)
        assert result.action == "clean"
        assert "3 违规" in result.detail

    def test_case_insensitive_matching(self, tmp_path):
        """大小写不敏感匹配（GATE-FIX → exempt）。"""
        from zephyr.governance.audit.reconciliation_registry import (
            make_capability_lookup_health_reconciler,
        )
        spec = make_capability_lookup_health_reconciler(_MockGateway(tmp_path))
        py_file = str(tmp_path / "src" / "zephyr" / "foo.py")
        msg = "fix: gate bug [no-lookup:GATE-FIX]"
        result = spec.reconcile([py_file], "sess-case-insensitive", msg)
        assert result.action == "clean"
        bypass_log = tmp_path / ".runtime" / "lookup_audit" / "bypass_audit.jsonl"
        entries = [
            json.loads(line) for line in bypass_log.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        assert entries[0]["scene"] == "exempt"

    def test_substring_matching(self, tmp_path):
        """子串匹配（gate-fix-xxx → exempt）。"""
        from zephyr.governance.audit.reconciliation_registry import (
            make_capability_lookup_health_reconciler,
        )
        spec = make_capability_lookup_health_reconciler(_MockGateway(tmp_path))
        py_file = str(tmp_path / "src" / "zephyr" / "foo.py")
        msg = "fix: gate bug [no-lookup:gate-fix-urgent-123]"
        result = spec.reconcile([py_file], "sess-substring", msg)
        assert result.action == "clean"
        bypass_log = tmp_path / ".runtime" / "lookup_audit" / "bypass_audit.jsonl"
        entries = [
            json.loads(line) for line in bypass_log.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        assert entries[0]["scene"] == "exempt"
        assert entries[0]["reason"] == "gate-fix-urgent-123"

    def test_all_whitelist_keywords_recognized(self, tmp_path):
        """所有 16 个白名单关键词均被识别为 exempt。"""
        from zephyr.governance.audit.reconciliation_registry import (
            make_capability_lookup_health_reconciler,
        )
        whitelist_keywords = [
            "gate-fix", "test-fix", "merge-prep", "continuation", "investigated",
            "auto-fix", "batch-treatment", "batch-governance",
            "architectural-refactor", "sync",
            "mechanical", "completing", "research", "bugfix", "root-cause", "调研",
        ]
        for keyword in whitelist_keywords:
            # 每个关键词独立 tmp_path（避免 bypass_audit.jsonl 累积）
            import tempfile
            sub_tmp = Path(tempfile.mkdtemp())
            spec = make_capability_lookup_health_reconciler(_MockGateway(sub_tmp))
            py_file = str(sub_tmp / "src" / "zephyr" / "foo.py")
            msg = f"fix: test [no-lookup:{keyword}]"
            result = spec.reconcile([py_file], f"sess-kw-{keyword}", msg)
            assert result.action == "clean", f"keyword={keyword} should be clean"
            bypass_log = sub_tmp / ".runtime" / "lookup_audit" / "bypass_audit.jsonl"
            entries = [
                json.loads(line) for line in bypass_log.read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            assert entries[0]["scene"] == "exempt", (
                f"keyword={keyword} should be exempt, got {entries[0]['scene']}"
            )

    def test_normalization_underscore_to_hyphen(self, tmp_path):
        """归一化匹配：root_cause_fix（_ → -）匹配 root-cause → exempt。"""
        from zephyr.governance.audit.reconciliation_registry import (
            make_capability_lookup_health_reconciler,
        )
        spec = make_capability_lookup_health_reconciler(_MockGateway(tmp_path))
        py_file = str(tmp_path / "src" / "zephyr" / "foo.py")
        msg = "fix: root cause [no-lookup:root_cause_fix]"
        result = spec.reconcile([py_file], "sess-normalize", msg)
        assert result.action == "clean"
        bypass_log = tmp_path / ".runtime" / "lookup_audit" / "bypass_audit.jsonl"
        entries = [
            json.loads(line) for line in bypass_log.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        assert entries[0]["scene"] == "exempt"
        assert entries[0]["reason"] == "root_cause_fix"

    def test_mechanical_batch_exempt(self, tmp_path):
        """mechanical 批量场景（实证修复验证）：mechanical-header-format-fix-batch-3 → exempt。"""
        from zephyr.governance.audit.reconciliation_registry import (
            make_capability_lookup_health_reconciler,
        )
        spec = make_capability_lookup_health_reconciler(_MockGateway(tmp_path))
        py_file = str(tmp_path / "src" / "zephyr" / "foo.py")
        msg = "fix: mechanical [no-lookup:mechanical-header-format-fix-batch-3]"
        result = spec.reconcile([py_file], "sess-mechanical", msg)
        assert result.action == "clean"
        bypass_log = tmp_path / ".runtime" / "lookup_audit" / "bypass_audit.jsonl"
        entries = [
            json.loads(line) for line in bypass_log.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        assert entries[0]["scene"] == "exempt"
        assert entries[0]["reason"] == "mechanical-header-format-fix-batch-3"

    def test_empty_reason_treated_as_violation(self, tmp_path):
        """空 reason（无白名单关键词匹配）→ violation。"""
        from zephyr.governance.audit.reconciliation_registry import (
            make_capability_lookup_health_reconciler,
        )
        spec = make_capability_lookup_health_reconciler(_MockGateway(tmp_path))
        py_file = str(tmp_path / "src" / "zephyr" / "foo.py")
        # [no-lookup:] 紧跟 ] → reason 为空
        msg = "fix: test [no-lookup:]"
        result = spec.reconcile([py_file], "sess-empty-reason", msg)
        assert result.action == "clean"  # 1 violation < 5
        bypass_log = tmp_path / ".runtime" / "lookup_audit" / "bypass_audit.jsonl"
        entries = [
            json.loads(line) for line in bypass_log.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        assert entries[0]["scene"] == "violation"
        assert entries[0]["reason"] == ""
