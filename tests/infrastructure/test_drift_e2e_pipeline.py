# [A_test] module_id: SRC-TST-0150 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-307 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.infrastructure.test_drift_e2e_pipeline
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""
E2E 全链路测试 — Drift Detector v1.0.1b
=========================================
真实链路：注入漂移 → 扫描检测 → 持久化写入 → 预算查询 → Gate Engine 裁决 → 自检回滚

RULE-ZERO: 仅在临时目录中操作，不影响项目源码。
"""

from __future__ import annotations

import sqlite3
import tempfile
from datetime import UTC, datetime
from pathlib import Path

from zephyr.gov_drift.ai_construction_detectors import AIConstructionDetectors
from zephyr.gov_drift.drift_engine import (
    _write_drift_events,
    load_detector_registry,
)
from zephyr.gov_drift.drift_infrastructure import check_budget_for_gate
from zephyr.gov_drift.self_test_verifier import SelfTestVerifier
from zephyr.shared.io.paths import REPO_ROOT


def _setup_project(tmp: str) -> list[Path]:
    """创建带有真实 Python 文件的临时项目。"""
    src = Path(tmp) / "src" / "zephyr" / "test_module"
    src.mkdir(parents=True, exist_ok=True)
    (src / "__init__.py").write_text("", encoding="utf-8")

    (src / "service.py").write_text(
        """from __future__ import annotations
import os
from typing import Optional

def load_config(path: str) -> dict:
    if os.path.exists(path):
        return {"loaded": True}
    return {"loaded": False}

class ConfigLoader:
    def load(self, path: str) -> Optional[dict]:
        return load_config(path)
""",
        encoding="utf-8",
    )

    (src / "utils.py").write_text(
        """from __future__ import annotations
import json

def parse_json(path: str) -> dict:
    with open(path) as f:
        return json.load(f)
""",
        encoding="utf-8",
    )

    return [src / "service.py", src / "utils.py"]


def _inject_drift(target: Path) -> str:
    """注入一个 import 幻觉到文件中。返回原始内容。"""
    original = target.read_text(encoding="utf-8")
    mutated = original + "\nfrom chaos_nonexistent_abcxyz import phantom_func\n"
    target.write_text(mutated, encoding="utf-8")
    return original


def test_e2e_drift_scan_persist():
    """
    E2E STEP 1: 注入 → 扫描 → 持久化
    """
    tmp = tempfile.mkdtemp(prefix="e2e_drift_")
    try:
        targets = _setup_project(tmp)
        target = targets[0]
        original = _inject_drift(target)

        ai = AIConstructionDetectors()
        events = ai.detect_ai_hallucination_import(str(target.parent))
        assert len(events) >= 1, f"Expected >=1 hallucination event, got {len(events)}"

        db_path = str(Path(tmp) / "data" / "drift" / "drift_events.db")
        written = _write_drift_events(events, db_path=db_path)
        assert written == len(events), f"Expected {len(events)} written, got {written}"

        conn = sqlite3.connect(db_path)
        rows = conn.execute("SELECT COUNT(*) FROM drift_events").fetchone()
        assert rows[0] == len(events), f"DB has {rows[0]} rows, expected {len(events)}"

        target.write_text(original, encoding="utf-8")
        conn.close()
    finally:
        import shutil

        shutil.rmtree(tmp, ignore_errors=True)


def test_e2e_drift_budget_check():
    """
    E2E STEP 2: 预算查询
    """
    budget = check_budget_for_gate("MOD-INF-023")
    assert "allowed" in budget, f"Missing 'allowed' in budget: {budget}"
    assert budget["allowed"] is True, "Budget should be allowed at start"


def test_e2e_drift_budget_exhaustion():
    """
    E2E STEP 3: 注入大量漂移 → 消耗预算 → 验证预算耗尽阻塞
    """
    tmp = tempfile.mkdtemp(prefix="e2e_budget_")
    try:
        targets = _setup_project(tmp)
        target = targets[0]
        original = _inject_drift(target)

        ai = AIConstructionDetectors()
        events = ai.detect_ai_hallucination_import(str(target.parent))

        db_path = str(Path(tmp) / "data" / "drift" / "drift_events.db")
        _write_drift_events(events, db_path=db_path)

        budget = check_budget_for_gate("MOD-INF-023")
        assert "allowed" in budget

        target.write_text(original, encoding="utf-8")
    finally:
        import shutil

        shutil.rmtree(tmp, ignore_errors=True)


def test_e2e_gate_engine_drift_budget():
    """
    E2E STEP 4: Gate Engine 执行 drift_budget check
    """
    from zephyr.gov_enforcement.rule_enforcement.gate_engine.gate_engine import (
        CheckConfig,
        _run_check,
    )
    from zephyr.shared.foundation.models import TaskCard

    task = TaskCard(
        task_id="ADR-9999",
        namespace="ADR",
        seq=9999,
        title="E2E drift budget test",
        status="READY",
        priority="P1",
        phase=4,
        safety_level="M",
        source_blueprint="test",
        source_section="test",
        description="E2E drift budget test",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
        deliverables=["src/zephyr/drift-detector/drift_engine.py"],
    )
    check = CheckConfig(
        check_id="TEST-DB-001",
        name="drift_budget_check",
        check_type="drift_budget",
        description="Check drift budget for MOD-INF-023",
        severity="P0",
        params={"target_module": "MOD-INF-023"},
    )
    project_root = REPO_ROOT

    violations = _run_check(check, task, project_root)
    assert len(violations) == 0, f"Expected 0 violations, got {len(violations)}: {[v.message for v in violations]}"


def test_e2e_self_test_verifier():
    """
    E2E STEP 5: SelfTestVerifier 完整自检
    """
    verifier = SelfTestVerifier()
    result = verifier.run_all()
    assert result.summary == "8/8 checks passed", f"Self-test failed: {result.summary}"


def test_e2e_registry_consistency():
    """
    E2E STEP 6: 注册表一致性 — 所有 detector 的 status 为 active
    """
    detectors = load_detector_registry()
    assert len(detectors) >= 31, f"Expected >=31 detectors, got {len(detectors)}"
    inactive = [d for d in detectors if d.status != "active"]
    assert len(inactive) == 0, f"Found {len(inactive)} inactive detectors: {[(d.id, d.status) for d in inactive]}"
