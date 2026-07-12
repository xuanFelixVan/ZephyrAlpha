# [A_test] module_id: SRC-TST-0145 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-302 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.infrastructure.drift_red_blue_adversarial
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""
Red-Blue Adversarial Test — drift-detector v1.0.1
==================================================
红队(Blue): chaos_injector 注入 4 类漂移
蓝队(Red):  AIConstructionDetectors + scan() 检测
裁判:       对比注入清单 vs 检出清单
"""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

from zephyr.gov_drift.ai_construction_detectors import AIConstructionDetectors
from zephyr.gov_drift.chaos_injector import (
    ChaosInjection,
    ChaosInjectionType,
    ChaosMetrics,
    ChaosResult,
    import_hallucination,
    inject_fake_todo_bomb,
    inject_path_rename,
    inject_yaml_field_flip,
)
from zephyr.gov_drift.drift_models import DriftEvent
from zephyr.gov_drift.self_test_verifier import SelfTestVerifier


def setup_target_files(tmp_dir: str) -> list[Path]:
    """创建 4 个有真实内容的测试文件，用于注入。"""
    files = []
    py_file = Path(tmp_dir) / "worker.py"
    py_file.write_text(
        """from __future__ import annotations
import os
from typing import Optional

def process(data: dict) -> Optional[str]:
    path = data.get("path", "")
    if os.path.exists(path):
        return path
    return None
""",
        encoding="utf-8",
    )
    files.append(py_file)

    yaml_file = Path(tmp_dir) / "config.yaml"
    yaml_file.write_text(
        """features:
  auto_fix: true
  auto_fixable: true
  enabled: true
  required: true
  timeout: 30
""",
        encoding="utf-8",
    )
    files.append(yaml_file)

    py2_file = Path(tmp_dir) / "handler.py"
    py2_file.write_text(
        """from __future__ import annotations
from uuid import uuid4

def handle_event(event_id: str) -> str:
    return f"handled:{event_id}"

class EventBus:
    def publish(self, msg: str) -> None:
        pass
""",
        encoding="utf-8",
    )
    files.append(py2_file)

    py3_file = Path(tmp_dir) / "utils.py"
    py3_file.write_text(
        """from __future__ import annotations
import json

def parse_config(path: str) -> dict:
    with open(path) as f:
        return json.load(f)
""",
        encoding="utf-8",
    )
    files.append(py3_file)

    return files


def run_adversarial_test():
    print("=" * 60)
    print("  红白对抗 — Drift Detector v1.0.1")
    print("=" * 60)

    tmp_dir = tempfile.mkdtemp(prefix="chaos_test_")
    print(f"\n[SETUP] Test sandbox: {tmp_dir}")

    targets = setup_target_files(tmp_dir)
    print(f"[SETUP] {len(targets)} target files created")

    injections: list[ChaosInjection] = []
    injection_map: dict[str, ChaosInjectionType] = {}

    injections_config = [
        (targets[0], ChaosInjectionType.PATH_RENAME, inject_path_rename, "ai_dead_code"),
        (targets[1], ChaosInjectionType.YAML_FIELD_FLIP, inject_yaml_field_flip, "yaml_field_flip"),
        (targets[2], ChaosInjectionType.FAKE_TODO_BOMB, inject_fake_todo_bomb, "ai_broken_logic"),
        (targets[3], ChaosInjectionType.IMPORT_HALLUCINATION, import_hallucination, "ai_hallucination_import"),
    ]

    print("\n" + "=" * 40)
    print("  PHASE 1: INJECT (红队 — 混沌注入)")
    print("=" * 40)
    for target, itype, injector, expected_detector in injections_config:
        original, mutated = injector(target)
        if original == mutated:
            print(f"  SKIP  {itype.value} on {target.name} — injector produced no change")
            continue
        ci = ChaosInjection(
            injection_type=itype,
            target_file=str(target),
            original_content=original,
            mutated_content=mutated,
        )
        target.write_text(mutated, encoding="utf-8")
        ci.phase = "INJECT"
        injections.append(ci)
        injection_map[str(target)] = itype
        print(f"  INJECTED {itype.value:25s} → {target.name}")

    print(f"\n  Total injected: {len(injections)}")

    print("\n" + "=" * 40)
    print("  PHASE 2: DETECT (蓝队 — 漂移检测)")
    print("=" * 40)

    ai = AIConstructionDetectors()
    all_detected: list[DriftEvent] = []

    detector_methods = [
        ("ai_hallucination_import", ai.detect_ai_hallucination_import),
        ("ai_dead_code", ai.detect_ai_dead_code),
        ("ai_broken_logic", ai.detect_ai_broken_logic),
        ("ai_duplicate_functionality", ai.detect_ai_duplicate_functionality),
        ("ai_session_style_drift", ai.detect_ai_session_style_drift),
        ("ai_knowledge_pollution", ai.detect_ai_knowledge_pollution),
    ]

    for det_name, det_method in detector_methods:
        try:
            events = det_method(tmp_dir)
            all_detected.extend(events)
            if events:
                print(f"  {det_name:30s} → {len(events)} events detected")
                for e in events[:2]:
                    print(f"    - {e.resolution_detail[:100]}")
        except Exception as ex:
            print(f"  {det_name:30s} → ERROR: {ex}")

    print(f"\n  Total drift events detected: {len(all_detected)}")

    print("\n" + "=" * 40)
    print("  PHASE 3: VERDICT (裁判 — 检出率)")
    print("=" * 40)

    detected_types: set[str] = set()
    for e in all_detected:
        detected_types.add(e.detector_id)

    results = []
    for ci in injections:
        itype = ci.injection_type.value
        expected_detector = {
            "path_rename": "ai_dead_code",
            "yaml_field_flip": "ai_broken_logic",
            "fake_todo_bomb": "ai_broken_logic",
            "import_hallucination": "ai_hallucination_import",
        }.get(itype, "")

        if expected_detector in detected_types:
            ci.result = ChaosResult.DETECTED
            print(f"  DETECTED   {itype:25s} → {ci.target_file.rsplit(chr(92), 1)[-1]}")
        else:
            ci.result = ChaosResult.MISSED
            found = [d for d in detected_types if d]
            print(f"  MISSED     {itype:25s} → {ci.target_file.rsplit(chr(92), 1)[-1]} (detectors active: {found})")
        results.append(ci)

    print("\n" + "=" * 40)
    print("  PHASE 4: ROLLBACK (回滚 — 恢复现场)")
    print("=" * 40)
    for ci in injections:
        Path(ci.target_file).write_text(ci.original_content, encoding="utf-8")
        print(f"  ROLLED BACK {ci.target_file.rsplit(chr(92), 1)[-1]}")

    print("\n" + "=" * 40)
    print("  PHASE 5: SELF-TEST (自检)")
    print("=" * 40)
    verifier = SelfTestVerifier()
    result = verifier.run_all()
    for c in result.checks:
        icon = "PASS" if c["status"] == "PASS" else "FAIL"
        print(f"  [{icon}] {c['check']}")
    print(f"  Verdict: {result.summary}")

    metrics = ChaosMetrics()
    metrics.total_injections = len(injections)
    metrics.detected = sum(1 for r in results if r.result == ChaosResult.DETECTED)
    metrics.missed = sum(1 for r in results if r.result == ChaosResult.MISSED)
    if metrics.total_injections > 0:
        metrics.false_negative_rate = metrics.missed / metrics.total_injections

    shutil.rmtree(tmp_dir, ignore_errors=True)

    print("\n" + "=" * 60)
    print("  FINAL REPORT")
    print("=" * 60)
    print(f"  Injections:    {metrics.total_injections}")
    print(f"  Detected:      {metrics.detected}")
    print(f"  Missed:        {metrics.missed}")
    print(
        f"  Detection Rate: {metrics.detected}/{metrics.total_injections} = {metrics.detected / max(metrics.total_injections, 1) * 100:.1f}%"
    )
    print(f"  FN Rate:       {metrics.false_negative_rate * 100:.1f}%")
    print(f"  Self-Test:     {result.summary}")

    if metrics.missed > 0:
        print(f"\n  ROOT CAUSE ANALYSIS REQUIRED for {metrics.missed} missed injections")
        return False, metrics, results
    else:
        print("\n  ALL INJECTIONS DETECTED — DRIFT DETECTOR OPERATIONAL")
        return True, metrics, results


if __name__ == "__main__":
    passed, metrics, results = run_adversarial_test()
    exit(0 if passed else 1)
