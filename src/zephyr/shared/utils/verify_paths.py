# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md
# [MODULE] zephyr.shared.utils.verify_paths
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.autonomy_core.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-ORC_verify_paths | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
verify_paths.py — 代码路径索引验证 (TASK-012)
==============================================
验证 §12 和 §14 中的所有文件路径与实际磁盘一致。
"""

import json
from pathlib import Path
from typing import Any

CE_DIR = Path(__file__).resolve().parent
TESTS_DIR = CE_DIR.parent.parent.parent / "tests"

SOURCE_FILES = {
    "context_assembler.py": "source",
    "context_budget_tracker.py": "source",
    "context_injector.py": "source",
    "context_rot_model.py": "source",
    "context_evictor.py": "source",
    "doc_compressor.py": "source",
    "intent_keyword_mapper.py": "source",
    "intent_parser.py": "source",
    "pattern_library.py": "source",
    "prompt_registry.py": "source",
    "system_snapshot.py": "source",
    "architecture-context.json": "data",
    "task_validator.py": "source",
    "pipeline_orchestrator.py": "source",
    "vector_bridge.py": "source",
}

TEST_FILES = {
    "unit/context-engine/test_context_assembler.py": "test",
    "unit/context-engine/test_context_budget_tracker.py": "test",
    "unit/context-engine/test_context_injector.py": "test",
    "unit/context-engine/test_doc_compressor.py": "test",
    "unit/context-engine/test_intent_keyword_mapper.py": "test",
    "unit/context-engine/test_intent_parser.py": "test",
    "unit/context-engine/test_pattern_library.py": "test",
    "unit/context-engine/test_prompt_registry.py": "test",
    "unit/context-engine/test_system_snapshot.py": "test",
    "unit/context-engine/test_context_rot_model.py": "test",
    "unit/context-engine/test_context_evictor.py": "test",
    "unit/context-engine/test_curation_loop.py": "test",
    "unit/context-engine/test_context_evaluator.py": "test",
    "unit/context-engine/test_memory_bank.py": "test",
    "unit/context-engine/test_intent_accuracy.py": "test",
    "unit/context-engine/test_context_pipeline.py": "test",
    "test_pipeline_orchestrator.py": "ghost",
}


def verify_all() -> dict[str, Any]:
    results: dict[str, Any] = {"source_files": {}, "test_files": {}, "stats": {}}

    expected_exists = 0
    expected_missing = 0

    for filename, category in SOURCE_FILES.items():
        path = CE_DIR / filename
        exists = path.exists()
        results["source_files"][filename] = {
            "expected": "✅" if filename != "task_validator.py" else "❌",
            "exists": exists,
            "size": path.stat().st_size if exists else 0,
            "category": category,
        }
        if filename == "task_validator.py":
            if not exists:
                results["source_files"][filename]["discrepancy"] = "none — 预期缺失，实际缺失，一致"
            expected_missing += 1
        else:
            expected_exists += 1

    for test_path, test_type in TEST_FILES.items():
        full_path = TESTS_DIR / test_path
        exists = full_path.exists()
        results["test_files"][test_path] = {
            "type": test_type,
            "exists": exists,
            "ghost": test_type == "ghost",
        }

    results["stats"] = {
        "source_expected_exist": expected_exists,
        "source_expected_missing": expected_missing,
        "source_actually_exist": sum(1 for v in results["source_files"].values() if v["exists"]),
        "tests_total": len(TEST_FILES),
        "tests_exist": sum(1 for v in results["test_files"].values() if v["exists"]),
        "ghost_tests": sum(1 for v in results["test_files"].values() if v["type"] == "ghost"),
    }

    return results


if __name__ == "__main__":
    import sys

    data = verify_all()
    sys.stdout.reconfigure(encoding="utf-8")
    json.dump(data, sys.stdout, indent=2, ensure_ascii=False)
    print()
