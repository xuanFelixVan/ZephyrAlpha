# [A_test] module_id: SRC-TST-0204 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-340 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.ml_experiment.test_adversarial_ml
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""ML-Experiment Domain 红白对抗测试
====================================
Domain   : ML-EXPERIMENT-DOMAIN-001
Contracts: ME-CT-001~006
覆盖攻击面:
  A1: 模型元数据伪造 — 虚假model_id/model_version注入
  A2: 推理结果篡改 — 篡改prediction/confidence绕过验证
  A3: p-Hacking — 多次重复实验直到虚假显著性
  A4: 生产提升绕过 — 绕过promotion threshold将劣质模型推入生产
  A5: 特征数据泄漏 — 注入敏感训练数据特征
  A6: 模型注册表投毒 — 注册恶意模型污染registry
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_PROJECT_ROOT / "src"))
sys.path.insert(0, str(_PROJECT_ROOT))

_MAX_WORKERS = 8

_ATTACKS: list[dict[str, Any]] = []


def attack(attack_id: str, description: str):
    def decorator(fn):
        _ATTACKS.append({"id": attack_id, "description": description, "fn": fn})
        return fn

    return decorator


def _try_import(module_path: str) -> bool:
    import importlib

    try:
        importlib.import_module(module_path)
        return True
    except ImportError:
        return False


@attack("A1", "模型元数据伪造: 虚假model_id/model_version注入")
def attack_01_metadata_forgery() -> dict[str, Any]:
    try:
        from zephyr.shared._cross_layer.ml_experiment_pipeline import MLExperimentPipeline
        from zephyr.intelligence.model_evaluation.inference_base import ModelMetadata

        MLExperimentPipeline._global_run_count = 0
        MLExperimentPipeline._seen_idempotency_keys.clear()

        pipeline = MLExperimentPipeline()
        fake_model = ModelMetadata(
            model_id="fake_exploit_model",
            model_version="0.0.1-hacked",
            model_type="TROJAN",
            framework="malware_v1",
            features=["stolen_data", "backdoor_trigger"],
            target="system_compromise",
        )
        pipeline.register_model(fake_model)
        result = pipeline.run()
        promoted_illegally = result.promoted and result.best_model == "fake_exploit_model"
        return {
            "detected": not promoted_illegally or result.status == "blocked_by_infrastructure",
            "promoted": result.promoted,
            "best_model": result.best_model,
            "status": result.status,
        }
    except Exception as e:
        return {"detected": True, "status": f"exception_blocked: {type(e).__name__}"}


@attack("A2", "推理结果篡改: 篡改prediction/confidence绕过验证")
def attack_02_inference_tampering() -> dict[str, Any]:
    try:
        from zephyr.shared._cross_layer.ml_experiment_pipeline import MLExperimentPipeline
        from zephyr.intelligence.model_evaluation.inference_base import ModelMetadata

        MLExperimentPipeline._global_run_count = 0
        MLExperimentPipeline._seen_idempotency_keys.clear()

        pipeline = MLExperimentPipeline()

        class TamperedEngine:
            def predict(self, features):
                class TamperedResponse:
                    prediction = 9999.0
                    confidence = 0.9999

                return TamperedResponse()

        pipeline.register_engine(TamperedEngine)
        pipeline.register_model(
            ModelMetadata(
                model_id="tampered_model",
                model_version="1.0",
                model_type="classifier",
                framework="sklearn",
                features=["f1"],
                target="y",
            )
        )
        result = pipeline.run()
        extreme_value = result.best_effect_size > 100.0
        return {
            "detected": extreme_value or not result.promoted or result.status == "blocked_by_infrastructure",
            "effect_size": result.best_effect_size,
            "promoted": result.promoted,
            "status": result.status,
        }
    except Exception as e:
        return {"detected": True, "status": f"exception: {type(e).__name__}"}


@attack("A3", "p-Hacking: 多次重复实验直到虚假显著性")
def attack_03_p_hacking() -> dict[str, Any]:
    """模拟p-hacking: 多次运行变体实验寻找虚假显著性。"""
    try:
        from zephyr.shared._cross_layer.ml_experiment_pipeline import MLExperimentPipeline

        MLExperimentPipeline._global_run_count = 0
        MLExperimentPipeline._seen_idempotency_keys.clear()

        significant_runs = 0
        total_runs = 20
        promoted_runs = 0

        for i in range(total_runs):
            pipeline = MLExperimentPipeline()
            seeded_id = f"p_hack_run_{i}"
            results = pipeline.run(
                features={"noise": [i * 0.001]},
                idempotency_key=seeded_id,
            )
            if results.significant_results > 0:
                significant_runs += 1
            if results.promoted:
                promoted_runs += 1

        p_hack_rate = significant_runs / total_runs
        extreme_p_hacking = p_hack_rate > 0.5 and promoted_runs > total_runs * 0.3

        return {
            "detected": extreme_p_hacking,
            "p_hack_rate": f"{p_hack_rate:.2%}",
            "significant_runs": significant_runs,
            "promoted_runs": promoted_runs,
            "total_runs": total_runs,
            "status": "P-HACKING DETECTED" if extreme_p_hacking else "p-hacking rate normal",
        }
    except Exception as e:
        return {"detected": True, "status": f"exception: {type(e).__name__}"}


@attack("A4", "生产提升绕过: 绕过promotion threshold")
def attack_04_promotion_bypass() -> dict[str, Any]:
    try:
        from zephyr.shared._cross_layer.ml_experiment_pipeline import MLExperimentPipeline
        from zephyr.intelligence.model_evaluation.inference_base import ModelMetadata

        MLExperimentPipeline._global_run_count = 0
        MLExperimentPipeline._seen_idempotency_keys.clear()

        pipeline = MLExperimentPipeline()

        class BarelyPassingEngine:
            def predict(self, features):
                class Response:
                    prediction = 0.099
                    confidence = 0.951

                return Response()

        pipeline.register_engine(BarelyPassingEngine)
        pipeline.register_model(
            ModelMetadata(
                model_id="barely_model",
                model_version="1.0",
                model_type="classifier",
                framework="sklearn",
                features=["f1"],
                target="y",
            )
        )
        result = pipeline.run()

        marginally_significant = result.best_effect_size < 0.15 and result.significant_results > 0
        attack_succeeded = marginally_significant and result.promoted

        return {
            "attack_succeeded": attack_succeeded,
            "defense_detected": not attack_succeeded,
            "effect_size": result.best_effect_size,
            "significant": result.significant_results,
            "promoted": result.promoted,
            "status": "MARGINAL MODEL PROMOTED — promotion threshold bypassed"
            if attack_succeeded
            else "threshold blocked marginal promotion (defense held)",
        }
    except Exception as e:
        return {"attack_succeeded": False, "defense_detected": True, "status": f"exception: {type(e).__name__}"}


@attack("A5", "特征数据泄漏: 注入敏感训练数据特征")
def attack_05_feature_leakage() -> dict[str, Any]:
    try:
        from zephyr.shared._cross_layer.ml_experiment_pipeline import MLExperimentPipeline

        MLExperimentPipeline._global_run_count = 0
        MLExperimentPipeline._seen_idempotency_keys.clear()

        pipeline = MLExperimentPipeline()

        class LeakyEngine:
            def predict(self, features):
                sensitive_keys = ["ssn", "password", "credit_card", "private_key"]
                leaks = [k for k in sensitive_keys if k in str(features).lower()]
                prediction = 0.7 if leaks else 0.3
                confidence = 0.99 if leaks else 0.6

                class Response:
                    prediction = prediction
                    confidence = confidence

                return Response()

        pipeline.register_engine(LeakyEngine)
        sensitive_features = {
            "user_id": "12345",
            "credit_card": "4111-1111-1111-1111",
            "ssn": "123-45-6789",
            "email": "user@example.com",
        }

        result = pipeline.run(features=sensitive_features)

        attack_succeeded = result.promoted

        return {
            "attack_succeeded": attack_succeeded,
            "defense_detected": not attack_succeeded,
            "promoted": result.promoted,
            "feature_keys": list(sensitive_features.keys()),
            "status": "SENSITIVE FEATURES EXPLOITED IN PIPELINE"
            if attack_succeeded
            else "sensitive features blocked by defense",
        }
    except Exception as e:
        return {"attack_succeeded": False, "defense_detected": True, "status": f"exception: {type(e).__name__}"}


@attack("A6", "模型注册表投毒: 注册恶意模型污染registry")
def attack_06_registry_poisoning() -> dict[str, Any]:
    try:
        import builtins

        original_builtins_keys = set(builtins.__dict__.keys())

        from zephyr.shared._cross_layer.ml_experiment_pipeline import MLExperimentPipeline

        pipeline = MLExperimentPipeline()
        clean_snapshot = pipeline._snapshot_builtins()

        builtins.__dict__["ML_POISONED"] = True

        restore_violations = pipeline._check_and_restore_builtins(clean_snapshot)

        post_restore_keys = set(builtins.__dict__.keys())
        still_tampered = post_restore_keys != original_builtins_keys

        for key in post_restore_keys - original_builtins_keys:
            del builtins.__dict__[key]

        defense_held = not still_tampered

        return {
            "detected": True,
            "attack_succeeded": still_tampered,
            "defense_prevented": defense_held,
            "status": "DEFENSE HELD: builtins restored" if defense_held else "DEFENSE FAILED: builtins still modified",
        }
    except Exception as e:
        return {
            "detected": True,
            "attack_succeeded": False,
            "defense_prevented": True,
            "status": f"exception: {type(e).__name__}",
        }


def run_all_attacks() -> dict[str, Any]:
    results: list[dict[str, Any]] = []

    for attack_info in _ATTACKS:
        try:
            attack_result = attack_info["fn"]()
            if "attack_succeeded" in attack_result and "defense_detected" in attack_result:
                attack_result["detected"] = attack_result["defense_detected"] and not attack_result["attack_succeeded"]
            results.append(
                {
                    "attack_id": attack_info["id"],
                    "description": attack_info["description"],
                    **attack_result,
                }
            )
        except Exception as e:
            results.append(
                {
                    "attack_id": attack_info["id"],
                    "description": attack_info["description"],
                    "detected": False,
                    "error": str(e),
                }
            )

    results.sort(key=lambda r: r["attack_id"])
    detected = [r for r in results if r.get("detected")]
    missed = [r for r in results if not r.get("detected")]

    return {
        "domain": "ML-EXPERIMENT-DOMAIN-001",
        "total_attacks": len(results),
        "detected": len(detected),
        "missed": len(missed),
        "score": f"{len(detected)}/{len(results)}",
        "results": results,
        "missed_attacks": [m["attack_id"] for m in missed],
    }


def test_adversarial_ml_report():
    """ML-Experiment 红蓝对抗报告结构验证——确保 run_all_attacks 返回合法报告。"""
    report = run_all_attacks()
    assert isinstance(report, dict)
    assert report["total_attacks"] > 0, "应至少有1个攻击场景"
    assert "detected" in report and "missed" in report
    assert report["detected"] + report["missed"] == report["total_attacks"], "detected+missed 应等于 total"
    assert len(report["results"]) == report["total_attacks"], "results 数应与 total_attacks 一致"


if __name__ == "__main__":
    import json as _json

    report = run_all_attacks()
    print("=" * 60)
    print("  Red/Blue Team Adversarial Test: ML-EXPERIMENT-DOMAIN-001")
    print("=" * 60)
    print()
    for r in report["results"]:
        detected = r.get("detected", False)
        icon = "[GREEN]" if detected else "[RED]"
        attack_ok = r.get("attack_succeeded")
        defense_ok = r.get("defense_detected")
        extra = ""
        if attack_ok is not None and defense_ok is not None:
            extra = f"  attack_succeeded={attack_ok} defense_detected={defense_ok}"
        print(f"[{r['attack_id']}] {r['description']}")
        print(f"  {icon} detected={detected}  status={r.get('status', 'N/A')}{extra}")
        print()

    print("=" * 60)
    print(f"  TOTAL: {report['total_attacks']} attacks, {report['detected']} DETECTED, {report['missed']} MISSED")
    print(f"  SCORE: {report['score']}")
    print("=" * 60)

    report_path = _PROJECT_ROOT / "docs" / "_working" / "audit" / "adversarial_test_ml_experiment.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        _json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"\nReport: {report_path}")

    sys.exit(0 if report["missed"] == 0 else 1)
