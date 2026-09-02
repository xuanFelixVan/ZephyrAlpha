# [BLUEPRINT] MOD-AU-003 | docs/02_enterprise_architecture/09_ai_architecture/implementation_plans/15_autonomy_boundary_risk.md | §4.2-S1.1/S1.2
# [MODULE] tests.autonomy_core.test_agentic_drift_guard
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [TESTS] 本文件（pytest -n 0 -q；DB/网络/IO 落盘全走 tmp_path 注入）
# [TTL] permanent
"""MOD-AU-003 agentic_drift_guard 验收测试（15号文 §4.2 S1.1/S1.2 + 双维 Hard-Gate + Challenge 工单）.

验收对照：
- S1.1：对历史数据建基线；注入合成异常（单会话 commit 频率突增 10×、首次触碰从未涉及
  的 production 模块）能检出并告警。
- S1.2：构造渐变操作链样例（read→write→delete 类型漂移、src/→config/ 路径漂移）分别
  触发 WARNING 与 DETECTED；正常施工链不误报。
- 双维度阈值（置信度 × 意图偏差度）Hard-Gate：双维同坏 → blocked；单维异常 → WARNING。
- Challenge 工单：字段=原始任务意图复述+当前动作链对齐说明+检测器证据；落盘+降级标记。
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import pytest

from zephyr.autonomy_core.agentic_drift_guard import (
    DEFAULT_DRIFT_CONFIG,
    AgenticDriftGuard,
    ChallengeTicket,
    ChainOperation,
    DriftGuardError,
    DriftLevel,
    build_behavior_baseline,
    build_challenge_ticket,
    check_operation_chain,
    check_session_against_baseline,
    evaluate_dual_dimension,
    shannon_entropy,
    write_challenge_ticket,
)
from zephyr.governance.lifecycle_governance.ai_behavior_baseline import SessionBehavior


# ── S1.1 行为基线 ──────────────────────────────────────────────


def _history_sessions() -> list[SessionBehavior]:
    """正常历史会话样本（commits/hour≈2，模块集稳定）."""
    return [
        SessionBehavior(
            session_id=f"hist-{i}",
            commits=4 + (i % 2),
            duration_hours=2.0,
            files_docs=2,
            files_code=6,
            files_registry=1,
            modules_touched=("src/zephyr/autonomy_core", "tests/autonomy"),
        )
        for i in range(5)
    ]


def test_baseline_built_from_history() -> None:
    baseline = build_behavior_baseline(_history_sessions())
    assert baseline.n_sessions == 5
    assert "src/zephyr/autonomy_core" in baseline.known_modules


def test_synthetic_anomaly_commit_frequency_10x_detected() -> None:
    """S1.1 验收：单会话 commit 频率突增 10× → 检出 commit_frequency 异常."""
    baseline = build_behavior_baseline(_history_sessions())
    spike = SessionBehavior(
        session_id="synth-spike",
        commits=90,  # 45 commits/hour，约基线 2.2 的 20×（>10×）
        duration_hours=2.0,
        files_docs=2,
        files_code=6,
        files_registry=1,
        modules_touched=("src/zephyr/autonomy_core",),
    )
    anomalies = check_session_against_baseline(spike, baseline)
    rules = {a.rule for a in anomalies}
    assert "commit_frequency" in rules


def test_synthetic_anomaly_first_touch_production_module_detected() -> None:
    """S1.1 验收：首次触碰从未涉及的 production 模块 → 检出 first_touch_module 异常."""
    baseline = build_behavior_baseline(_history_sessions())
    first_touch = SessionBehavior(
        session_id="synth-first-touch",
        commits=4,
        duration_hours=2.0,
        files_docs=0,
        files_code=3,
        files_registry=0,
        modules_touched=("src/zephyr/trading/trading_contracts",),  # 基线外 production 模块
    )
    anomalies = check_session_against_baseline(first_touch, baseline)
    rules = {a.rule for a in anomalies}
    assert "first_touch_module" in rules


def test_normal_session_no_anomaly() -> None:
    baseline = build_behavior_baseline(_history_sessions())
    normal = SessionBehavior(
        session_id="normal-1",
        commits=4,
        duration_hours=2.0,
        files_docs=2,
        files_code=6,
        files_registry=1,
        modules_touched=("src/zephyr/autonomy_core",),
    )
    assert check_session_against_baseline(normal, baseline) == []


# ── S1.2 操作链内联漂移检查（纯函数核）─────────────────────────


def _normal_construction_chain() -> list[ChainOperation]:
    """正常施工链：read/write 两类，路径集中 src/+tests/（熵低于阈值）."""
    return [
        ChainOperation("read", "src/zephyr/autonomy_core/a.py"),
        ChainOperation("read", "src/zephyr/autonomy_core/b.py"),
        ChainOperation("read", "src/zephyr/autonomy_core/c.py"),
        ChainOperation("write", "src/zephyr/autonomy_core/a.py"),
        ChainOperation("write", "src/zephyr/autonomy_core/b.py"),
        ChainOperation("read", "tests/autonomy_core/test_a.py"),
        ChainOperation("write", "tests/autonomy_core/test_a.py"),
        ChainOperation("write", "src/zephyr/autonomy_core/c.py"),
        ChainOperation("read", "src/zephyr/autonomy_core/d.py"),
        ChainOperation("write", "tests/autonomy_core/test_b.py"),
    ]


def test_normal_chain_no_false_positive() -> None:
    """S1.2 验收：正常施工链不误报（OK，无 auto_guard/blocked 标记）."""
    verdict = check_operation_chain(_normal_construction_chain())
    assert verdict.level is DriftLevel.OK
    assert not verdict.auto_guard
    assert not verdict.blocked


def test_gradual_type_drift_triggers_warning() -> None:
    """S1.2 验收：read→write→delete 类型渐变（4/3/3 混合，类型熵>1.5）→ WARNING."""
    chain = [
        ChainOperation("read", "src/zephyr/autonomy_core/a.py"),
        ChainOperation("read", "src/zephyr/autonomy_core/b.py"),
        ChainOperation("read", "src/zephyr/autonomy_core/c.py"),
        ChainOperation("read", "src/zephyr/autonomy_core/d.py"),
        ChainOperation("write", "src/zephyr/autonomy_core/a.py"),
        ChainOperation("write", "src/zephyr/autonomy_core/b.py"),
        ChainOperation("write", "src/zephyr/autonomy_core/c.py"),
        ChainOperation("delete", "src/zephyr/autonomy_core/x.py"),
        ChainOperation("delete", "src/zephyr/autonomy_core/y.py"),
        ChainOperation("delete", "src/zephyr/autonomy_core/z.py"),
    ]
    verdict = check_operation_chain(chain)
    assert verdict.level is DriftLevel.WARNING
    assert verdict.auto_guard  # WARNING → auto_guard 降级标记
    assert not verdict.blocked
    assert verdict.type_entropy > DEFAULT_DRIFT_CONFIG.type_entropy_threshold


def test_gradual_path_drift_triggers_detected() -> None:
    """S1.2 验收：src/→config/ 等路径漂移（5 顶层目录均布，路径熵>2.0）→ DETECTED."""
    chain = [
        ChainOperation("write", "src/zephyr/autonomy_core/a.py"),
        ChainOperation("write", "src/zephyr/autonomy_core/b.py"),
        ChainOperation("write", "config/flags.yaml"),
        ChainOperation("write", "config/budget_policy.yaml"),
        ChainOperation("write", "scripts/governance/foo.py"),
        ChainOperation("write", "scripts/ops/bar.py"),
        ChainOperation("write", "docs/01_policies_and_standards/rules/x.yaml"),
        ChainOperation("write", "docs/02_enterprise_architecture/y.md"),
        ChainOperation("write", "data/fix_patterns/z.yaml"),
        ChainOperation("write", "data/brain/w.json"),
    ]
    verdict = check_operation_chain(chain)
    assert verdict.level is DriftLevel.DETECTED
    assert verdict.blocked  # DETECTED → blocked
    assert verdict.path_entropy > DEFAULT_DRIFT_CONFIG.path_entropy_threshold


def test_window_limits_to_last_10_ops() -> None:
    """10 步滑动窗口：前段正常后段路径漂移 → 只看最近 10 步."""
    chain = [ChainOperation("read", f"src/zephyr/autonomy_core/h{i}.py") for i in range(20)]
    chain += [
        ChainOperation("write", "config/a.yaml"),
        ChainOperation("write", "scripts/b.py"),
        ChainOperation("write", "docs/c.md"),
        ChainOperation("write", "data/d.json"),
        ChainOperation("write", "config/e.yaml"),
        ChainOperation("write", "scripts/f.py"),
        ChainOperation("write", "docs/g.md"),
        ChainOperation("write", "data/h.json"),
        ChainOperation("write", "src/i.py"),
        ChainOperation("write", ".runtime/j.json"),
    ]
    verdict = check_operation_chain(chain)
    assert verdict.level is DriftLevel.DETECTED
    assert verdict.path_entropy > DEFAULT_DRIFT_CONFIG.path_entropy_threshold


def test_short_chain_skipped_as_ok() -> None:
    """窗口内样本过少（<min_ops）不做熵判定 → OK（小样本不判，对齐基线口径）."""
    chain = [ChainOperation("read", "a.py"), ChainOperation("write", "config/b.yaml")]
    verdict = check_operation_chain(chain)
    assert verdict.level is DriftLevel.OK


def test_invalid_config_rejected() -> None:
    with pytest.raises(DriftGuardError):
        check_operation_chain(
            _normal_construction_chain(),
            config=DEFAULT_DRIFT_CONFIG.__class__(window_size=0),
        )


def test_shannon_entropy_math() -> None:
    assert shannon_entropy([10]) == pytest.approx(0.0)
    assert shannon_entropy([5, 5]) == pytest.approx(1.0)
    assert shannon_entropy([1, 1, 1, 1]) == pytest.approx(2.0)
    assert shannon_entropy([]) == 0.0


def test_inline_check_perf_budget() -> None:
    """性能预算粗证：1000 次内联检查远低于 0.25ms/次 的量级外沿（给 Windows 负载留 40× 余量）."""
    chain = _normal_construction_chain()
    start = time.perf_counter()
    for _ in range(1000):
        check_operation_chain(chain)
    elapsed_ms = (time.perf_counter() - start) * 1000
    assert elapsed_ms / 1000 < 10.0  # 0.25ms 预算的 40× 宽松上界，仅防病态实现


# ── 双维度阈值 Hard-Gate ──────────────────────────────────────


def test_dual_dimension_both_bad_blocked() -> None:
    """低置信（<0.3）× 高意图偏差（>0.3）→ Hard-Gate blocked."""
    verdict = evaluate_dual_dimension(confidence=0.1, intent_deviation=0.8)
    assert verdict.level is DriftLevel.DETECTED
    assert verdict.blocked


def test_dual_dimension_single_bad_warning() -> None:
    """单维异常分开处置：低置信但守规矩 / 高置信但跑偏 → 均 WARNING 不阻断."""
    low_conf = evaluate_dual_dimension(confidence=0.1, intent_deviation=0.1)
    high_dev = evaluate_dual_dimension(confidence=0.9, intent_deviation=0.8)
    assert low_conf.level is DriftLevel.WARNING
    assert low_conf.auto_guard
    assert not low_conf.blocked
    assert high_dev.level is DriftLevel.WARNING
    assert not high_dev.blocked


def test_dual_dimension_both_fine_ok() -> None:
    verdict = evaluate_dual_dimension(confidence=0.9, intent_deviation=0.1)
    assert verdict.level is DriftLevel.OK
    assert not verdict.blocked


def test_dual_dimension_invalid_input_rejected() -> None:
    with pytest.raises(DriftGuardError):
        evaluate_dual_dimension(confidence=1.5, intent_deviation=0.0)


# ── Guard 编排层：P0 告警事件落盘 ─────────────────────────────


def test_guard_detected_writes_p0_alert(tmp_path: Path) -> None:
    """DETECTED → blocked + P0 告警事件产出（16号文统一事件 schema jsonl）."""
    guard = AgenticDriftGuard(runtime_dir=tmp_path)
    chain = [
        ChainOperation("write", p)
        for p in (
            "src/a.py",
            "src/b.py",
            "config/c.yaml",
            "config/d.yaml",
            "scripts/e.py",
            "scripts/f.py",
            "docs/g.md",
            "docs/h.md",
            "data/i.json",
            "data/j.json",
        )
    ]
    verdict = guard.inspect(chain)
    assert verdict.level is DriftLevel.DETECTED
    assert verdict.blocked
    alerts = (tmp_path / "audit" / "agentic_drift_guard_alerts.jsonl").read_text(encoding="utf-8").strip().splitlines()
    assert len(alerts) == 1
    event = json.loads(alerts[0])
    assert event["severity"] == "critical"  # P0
    assert event["threat_category"] == "agentic_drift"
    assert event["source_domain"] == "gov_drift"
    assert event["schema_version"] == "1.0"
    assert "session_id" not in event["reason"]  # 纪律：错误/原因消息禁含 session_id


def test_guard_warning_no_alert_but_audit_trace(tmp_path: Path) -> None:
    guard = AgenticDriftGuard(runtime_dir=tmp_path)
    chain = [
        ChainOperation(t, f"src/zephyr/autonomy_core/{i}.py")
        for i, t in enumerate(["read", "read", "read", "read", "write", "write", "write", "delete", "delete", "delete"])
    ]
    verdict = guard.inspect(chain)
    assert verdict.level is DriftLevel.WARNING
    assert verdict.auto_guard
    assert not (tmp_path / "audit" / "agentic_drift_guard_alerts.jsonl").exists()
    audit = (tmp_path / "audit" / "agentic_drift_guard.jsonl").read_text(encoding="utf-8")
    assert "drift_check" in audit


def test_guard_io_failure_does_not_break_verdict(tmp_path: Path) -> None:
    """落盘 IO 失败不阻断判定（把审计路径指向一个已存在的文件制造 OSError）."""
    guard = AgenticDriftGuard(runtime_dir=tmp_path)
    blocker = tmp_path / "audit"
    blocker.write_text("occupied", encoding="utf-8")  # audit 是文件而非目录 → mkdir 失败
    verdict = guard.inspect(_normal_construction_chain())
    assert verdict.level is DriftLevel.OK
    guard.close()


# ── Agent Challenge 工单 ──────────────────────────────────────


def test_challenge_ticket_fields_and_persistence(tmp_path: Path) -> None:
    """工单字段=原始任务意图复述+当前动作链对齐说明+检测器证据；落盘返回路径."""
    verdict = check_operation_chain(_normal_construction_chain())
    ticket = build_challenge_ticket(
        verdict,
        original_intent_restatement="修复 autonomy_core 某 Bug（原始任务意图复述）",
        action_chain_alignment="当前动作链仍围绕 src/zephyr/autonomy_core 与对应测试（对齐说明）",
        degraded=False,
    )
    assert isinstance(ticket, ChallengeTicket)
    assert ticket.status == "pending_cross_review"
    assert not ticket.degraded
    assert ticket.detector_evidence["level"] == DriftLevel.OK.value
    rel = write_challenge_ticket(ticket, tmp_path)
    payload = json.loads((tmp_path / Path(rel).name).read_text(encoding="utf-8"))
    assert payload["original_intent_restatement"].startswith("修复")
    assert payload["action_chain_alignment"]
    assert payload["detector_evidence"]
    assert payload["status"] == "pending_cross_review"


def test_challenge_ticket_degraded_goes_human_queue(tmp_path: Path) -> None:
    """降级形态：交叉会话不可用/超时 → degraded=True 直接进人审队列标记."""
    verdict = check_operation_chain(_normal_construction_chain())
    ticket = build_challenge_ticket(
        verdict,
        original_intent_restatement="意图复述",
        action_chain_alignment="对齐说明",
        degraded=True,
    )
    assert ticket.degraded
    assert ticket.status == "degraded_human_review"
    rel = write_challenge_ticket(ticket, tmp_path)
    payload = json.loads((tmp_path / Path(rel).name).read_text(encoding="utf-8"))
    assert payload["status"] == "degraded_human_review"
    assert payload["degraded"] is True
