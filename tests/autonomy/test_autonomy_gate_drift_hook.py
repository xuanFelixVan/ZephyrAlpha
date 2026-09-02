# [BLUEPRINT] MOD-AU-001/MOD-AU-003 | docs/02_enterprise_architecture/09_ai_architecture/implementation_plans/15_autonomy_boundary_risk.md | §4.2-S1.2
# [MODULE] tests.autonomy.test_autonomy_gate_drift_hook
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [TESTS] 本文件（pytest -q；落盘全走 tmp_path 注入，真源注册表只读引用）
# [TTL] permanent
"""S0.2 gate × S1.2 Agentic Drift 内联挂接验收测试（15号文 §4.2 S1.2）.

验收对照（§4.2 S1.2 步骤验收口径）：
- 构造渐变操作链样例：read→write→delete 类型漂移触发 WARNING（降级 auto_guard，
  不阻断）；src/→config/ 类多顶层段路径漂移触发 DETECTED（blocked + P0 告警）。
- 正常施工链不误报。
- 内联性能：挂接增量 P95 < 1ms 级（时间统计口径，非墙钟硬断言单点）。
- 挂接开关 drift_check_enabled=False 时零行为变化。
- 会话滑窗按 session_id 键控隔离，互不染指。

被测对象：src/zephyr/autonomy_core/autonomy_boundary_gate.py（内联挂点）
+ src/zephyr/autonomy_core/agentic_drift_guard.py（判定核，事件落盘）。
真源注册表：GOV-AI-001（ai_autonomy_authority_registry.yaml）只读引用。
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import pytest

from zephyr.autonomy_core.autonomy_boundary_gate import (
    AutonomyBoundaryGate,
    AutonomyLayer,
    GateDecision,
    GateVerdict,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = (
    REPO_ROOT / "docs" / "01_policies_and_standards" / "_registry" / "catalogs" / "ai_autonomy_authority_registry.yaml"
)

# read→write→delete 类型漂移链（同顶层段 src/，路径熵=0 隔离路径维度）：
# 窗口 10 = read×4/write×3/delete×3 → 类型熵≈1.571>1.5 且偏离率 0.6>0.3 → WARNING
TYPE_DRIFT_STEPS: list[tuple[str, str]] = (
    [("read", f"src/zephyr/factor/r{i}.py") for i in range(4)]
    + [("write", f"src/zephyr/factor/w{i}.py") for i in range(3)]
    + [("delete", f"src/zephyr/factor/d{i}.py") for i in range(3)]
)

# 多顶层段路径漂移链（全 write，类型熵=0 隔离类型维度）：
# 窗口 10 = src×3/scripts×2/docs×2/tests×2/data×1 → 路径熵≈2.246>2.0 且偏离率 0.7>0.3 → DETECTED
# 终步 scripts/governance/validate_truth_source_cascade.py 注册表登记为 AI-Modifiable——
# 本可放行，验证 DETECTED Hard-Gate 把 ALLOW 升级为 BLOCK。
PATH_DRIFT_STEPS: list[tuple[str, str]] = [
    ("write", "docs/01_policies_and_standards/ai-onboarding-guide.md"),
    ("write", "scripts/governance/archive_drafts_zone.py"),
    ("write", "src/zephyr/factor/a.py"),
    ("write", "tests/autonomy/test_pd_a.py"),
    ("write", "docs/01_policies_and_standards/master-registry-index.md"),
    ("write", "src/zephyr/signal/b.py"),
    ("write", "data/circuit_breaker.db"),
    ("write", "tests/autonomy/test_pd_b.py"),
    ("write", "src/zephyr/research/c.py"),
    ("write", "scripts/governance/validate_truth_source_cascade.py"),
]


def _gate(runtime_dir: Path, **kwargs) -> AutonomyBoundaryGate:
    return AutonomyBoundaryGate(registry_path=REGISTRY_PATH, runtime_dir=runtime_dir, repo_root=REPO_ROOT, **kwargs)


def _run_chain(gate: AutonomyBoundaryGate, session_id: str, steps: list[tuple[str, str]]) -> list[GateVerdict]:
    """按 (op_type, target) 链推进 gate 判定（op_type 经 session_context 上报工具层）。"""
    return [
        gate.check_write_permission(f"{session_id}-{i}", target, {"session_id": session_id, "op_type": op_type})
        for i, (op_type, target) in enumerate(steps)
    ]


def _read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


class TestTypeDriftWarning:
    """S1.2 验收①：read→write→delete 类型漂移 → WARNING（auto_guard 降级，不阻断）."""

    def test_type_drift_triggers_warning_auto_guard(self, tmp_path):
        gate = _gate(tmp_path)
        try:
            verdicts = _run_chain(gate, "sess-type-drift", TYPE_DRIFT_STEPS)
        finally:
            gate.close()
        final = verdicts[-1]
        # WARNING 不阻断：判定保持放行，但打 auto_guard 降级标记（autonomy_regressor 语义）
        assert final.decision is GateDecision.ALLOW
        assert final.allowed is True
        assert final.auto_guard is True
        assert final.drift_level == "warning"
        assert final.drift_verdict_id
        # 前 8 步窗口类型熵未越阈（小样本不判 + 熵<1.5），不误报
        assert all(v.auto_guard is False for v in verdicts[:8])
        assert all(v.drift_level == "ok" for v in verdicts[:8])

    def test_type_drift_trace_and_no_p0_alert(self, tmp_path):
        gate = _gate(tmp_path)
        try:
            _run_chain(gate, "sess-type-trace", TYPE_DRIFT_STEPS)
        finally:
            gate.close()
        # gate 审计尾行：威胁类别改写 agentic_drift、严重度提升但 decision 仍 allow
        records = _read_jsonl(tmp_path / "audit" / "autonomy_boundary_gate.jsonl")
        assert len(records) == len(TYPE_DRIFT_STEPS)
        assert records[-1]["decision"] == "allow"
        assert records[-1]["threat_category"] == "agentic_drift"
        assert records[-1]["severity"] == "elevated"
        assert records[-1]["auto_guard"] is True
        assert records[-1]["evidence"]["drift_level"] == "warning"
        # guard 侧全量检查留痕（16号文统一 schema）；WARNING 不产 P0 告警
        drift_records = _read_jsonl(tmp_path / "audit" / "agentic_drift_guard.jsonl")
        assert len(drift_records) == len(TYPE_DRIFT_STEPS)
        assert drift_records[-1]["level"] == "warning"
        assert drift_records[-1]["schema_version"] == "1.0"
        assert drift_records[-1]["source_domain"] == "gov_drift"
        assert not (tmp_path / "audit" / "agentic_drift_guard_alerts.jsonl").exists()


class TestPathDriftDetected:
    """S1.2 验收②：多顶层段路径漂移 → DETECTED（blocked + P0 告警）."""

    def test_path_drift_blocks_allow_verdict(self, tmp_path):
        gate = _gate(tmp_path)
        try:
            verdicts = _run_chain(gate, "sess-path-drift", PATH_DRIFT_STEPS)
        finally:
            gate.close()
        final = verdicts[-1]
        # 终步目标注册表登记 ai_modifiable（本可放行），DETECTED Hard-Gate 升级为 BLOCK
        assert final.layer is AutonomyLayer.AI_MODIFIABLE
        assert final.decision is GateDecision.BLOCK
        assert final.allowed is False
        assert final.fail_closed is False
        assert final.auto_guard is False
        assert final.drift_level == "detected"
        # 倒数第二步（src/zephyr/research/，ai_modifiable）同样被漂移 Hard-Gate 拦截
        assert verdicts[-2].layer is AutonomyLayer.AI_MODIFIABLE
        assert verdicts[-2].decision is GateDecision.BLOCK

    def test_path_drift_p0_alert_unified_schema(self, tmp_path):
        gate = _gate(tmp_path)
        try:
            _run_chain(gate, "sess-path-alert", PATH_DRIFT_STEPS)
        finally:
            gate.close()
        # P0 告警由 guard 按 16号文统一事件 schema 落盘（severity=critical）
        alerts = _read_jsonl(tmp_path / "audit" / "agentic_drift_guard_alerts.jsonl")
        assert len(alerts) >= 1
        alert = alerts[-1]
        assert alert["schema_version"] == "1.0"
        assert alert["source_domain"] == "gov_drift"
        assert alert["event_type"] == "agentic_drift_detected"
        assert alert["threat_category"] == "agentic_drift"
        assert alert["severity"] == "critical"
        assert alert["blocked"] is True
        # gate 审计尾行同步改写：decision=block + threat_category=agentic_drift
        records = _read_jsonl(tmp_path / "audit" / "autonomy_boundary_gate.jsonl")
        assert records[-1]["decision"] == "block"
        assert records[-1]["threat_category"] == "agentic_drift"
        assert records[-1]["severity"] == "critical"


class TestNormalChainNoFalsePositive:
    """S1.2 验收③：正常施工链不误报."""

    def test_normal_construction_chain_all_ok(self, tmp_path):
        gate = _gate(tmp_path)
        try:
            steps = [("write", f"src/zephyr/factor/normal_{i}.py") for i in range(10)]
            verdicts = _run_chain(gate, "sess-normal", steps)
        finally:
            gate.close()
        assert all(v.decision is GateDecision.ALLOW for v in verdicts)
        assert all(v.auto_guard is False for v in verdicts)
        assert all(v.drift_level == "ok" for v in verdicts)
        records = _read_jsonl(tmp_path / "audit" / "autonomy_boundary_gate.jsonl")
        assert len(records) == 10
        assert all(r["threat_category"] == "none" and r["severity"] == "info" for r in records)
        assert not (tmp_path / "audit" / "agentic_drift_guard_alerts.jsonl").exists()


class TestSessionWindowIsolation:
    """会话滑窗按 session_id 键控：漂移会话不染指同 gate 下的正常会话."""

    def test_sessions_isolated(self, tmp_path):
        gate = _gate(tmp_path)
        try:
            # s1 类型漂移链推进到 WARNING；s2 交错正常写
            for i, (op_type, target) in enumerate(TYPE_DRIFT_STEPS):
                gate.check_write_permission(f"s1-{i}", target, {"session_id": "s1", "op_type": op_type})
                v_s2 = gate.check_write_permission(f"s2-{i}", f"src/zephyr/factor/solo_{i}.py", {"session_id": "s2"})
                assert v_s2.decision is GateDecision.ALLOW
                assert v_s2.auto_guard is False
                assert v_s2.drift_level == "ok"
            v_s1_final = gate.check_write_permission(
                "s1-final",
                "src/zephyr/factor/final.py",
                {"session_id": "s1", "op_type": "write"},
            )
            assert v_s1_final.auto_guard is True
            assert v_s1_final.drift_level == "warning"
        finally:
            gate.close()


class TestDriftHookSwitch:
    """挂接开关：drift_check_enabled=False → 零行为变化."""

    def test_disabled_zero_behavior_change(self, tmp_path):
        gate = _gate(tmp_path, drift_check_enabled=False)
        try:
            verdicts = _run_chain(gate, "sess-off", PATH_DRIFT_STEPS)
        finally:
            gate.close()
        final = verdicts[-1]
        # 同一条路径漂移链，关断开关后终步恢复放行，无任何漂移字段/文件产出
        assert final.decision is GateDecision.ALLOW
        assert final.allowed is True
        assert final.auto_guard is False
        assert all(v.drift_level == "" for v in verdicts)
        assert all(v.drift_verdict_id == "" for v in verdicts)
        assert not (tmp_path / "audit" / "agentic_drift_guard.jsonl").exists()
        assert not (tmp_path / "audit" / "agentic_drift_guard_alerts.jsonl").exists()
        records = _read_jsonl(tmp_path / "audit" / "autonomy_boundary_gate.jsonl")
        assert records[-1]["decision"] == "allow"
        assert records[-1]["threat_category"] == "none"
        assert records[-1]["severity"] == "info"

    def test_no_session_id_skips_drift_check(self, tmp_path):
        gate = _gate(tmp_path)
        try:
            for i in range(6):
                verdict = gate.check_write_permission(f"nosess-{i}", "src/zephyr/factor/x.py")
                assert verdict.decision is GateDecision.ALLOW
                assert verdict.drift_level == ""
        finally:
            gate.close()
        # 无 session_id 即无链可判：guard 侧零留痕
        assert not (tmp_path / "audit" / "agentic_drift_guard.jsonl").exists()


class TestInlinePerformance:
    """S1.2 内联性能：挂接增量 P95 < 1ms 级（1000 次采样时间统计，防环境抖动）."""

    def test_p95_delta_within_budget(self, tmp_path):
        n = 1000
        gate_off = _gate(tmp_path / "off", drift_check_enabled=False)
        gate_on = _gate(tmp_path / "on", drift_check_enabled=True)

        def _measure(g: AutonomyBoundaryGate) -> list[float]:
            for i in range(100):  # 预热：文件句柄/滑窗/注册表缓存
                g.check_write_permission(f"warm-{i}", "src/zephyr/factor/perf.py", {"session_id": "perf"})
            samples: list[float] = []
            for i in range(n):
                t0 = time.perf_counter()
                g.check_write_permission(f"meas-{i}", "src/zephyr/factor/perf.py", {"session_id": "perf"})
                samples.append(time.perf_counter() - t0)
            samples.sort()
            return samples

        try:
            off_samples = _measure(gate_off)
            on_samples = _measure(gate_on)
        finally:
            gate_off.close()
            gate_on.close()
        p95_off = off_samples[int(0.95 * n) - 1]
        p95_on = on_samples[int(0.95 * n) - 1]
        median_off = off_samples[n // 2]
        median_on = on_samples[n // 2]
        delta_p95_ms = (p95_on - p95_off) * 1000
        print(
            f"\n[S1.2 内联性能] P95 off={p95_off * 1e3:.3f}ms on={p95_on * 1e3:.3f}ms "
            f"Δ={delta_p95_ms:.3f}ms | median off={median_off * 1e3:.3f}ms "
            f"on={median_on * 1e3:.3f}ms"
        )
        # 性能预算对齐蓝图 L2 ABAC 参考值（≈0.25ms 量级），P95 增量 <1ms 达标线
        assert delta_p95_ms < 1.0
