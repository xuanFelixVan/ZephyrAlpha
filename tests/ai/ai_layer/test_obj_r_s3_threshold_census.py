"""OBJ_R S3 阈值普查生成器测试：AST 采集口径 + 提案骨架计数自洽 + 零改写断言。

零生产写：样例源码全在 tmp_path，绝不扫真仓、绝不写 src/。
"""

from __future__ import annotations

import hashlib
import importlib.util
import sys
from datetime import date
from pathlib import Path
from typing import Any

import pytest
import yaml

_SCRIPT = Path(__file__).resolve().parents[3] / "scripts" / "ai_layer" / "gen_obj_r_s3_threshold_census.py"
_SPEC = importlib.util.spec_from_file_location("gen_obj_r_s3_threshold_census", _SCRIPT)
assert _SPEC is not None and _SPEC.loader is not None  # 缺件即红，禁 skip 装绿
mod = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = mod  # dataclass 需模块在 sys.modules
_SPEC.loader.exec_module(mod)

SAMPLE = """
import yaml

CFG = yaml.safe_load("{}")
_NAME = "identity-string"
_HARD_LIMIT = 120
_MAX_COMPLEXITY: Final[int] = 15
_FNV_PRIME_64 = 1099511628211
_FLAGS = 1 << 3
_BLOOM_SIZES = {"small": 32768, "large": 65536}
_TIMEOUTS = {"a": 1, "b": 2}


def helper() -> None:
    _LOCAL_NOT_MODULE_LEVEL = 99
    assert _LOCAL_NOT_MODULE_LEVEL
"""


@pytest.fixture()
def sample_file(tmp_path: Path) -> Path:
    path = tmp_path / "sample_gate.py"
    path.write_text(SAMPLE, encoding="utf-8")
    return path


def _by_name(findings: list[Any]) -> dict[str, Any]:
    return {f.name: f for f in findings}


def test_scan_module_level_numeric_only(sample_file: Path, tmp_path: Path) -> None:
    findings = mod.scan_file(sample_file, tmp_path)
    by = _by_name(findings)
    assert "_LOCAL_NOT_MODULE_LEVEL" not in by  # 函数内常量不入面（仅模块级）
    assert {"_NAME", "_HARD_LIMIT", "_MAX_COMPLEXITY", "_FNV_PRIME_64", "_FLAGS", "_BLOOM_SIZES", "_TIMEOUTS"} <= set(
        by
    )
    assert by["_HARD_LIMIT"].is_threshold is True
    assert by["_MAX_COMPLEXITY"].is_threshold is True
    assert by["_TIMEOUTS"].is_threshold is True  # 含数值容器亦属阈值族
    assert by["_NAME"].is_threshold is False  # 标识串非判据
    assert by["_FNV_PRIME_64"].is_threshold is False  # 算法魔数非判据
    assert by["_FLAGS"].is_threshold is False  # 位运算式且名无语素


def test_injection_marker_is_orthogonal_axis(sample_file: Path, tmp_path: Path) -> None:
    by = _by_name(mod.scan_file(sample_file, tmp_path))
    assert by["_HARD_LIMIT"].is_threshold is True
    assert by["_HARD_LIMIT"].injection_marker == "yaml.safe_load"  # 两轴同时成立、不互斥


def test_gate_index_maps_module_path_to_file(tmp_path: Path) -> None:
    registry = tmp_path / "in_process_gate_registry.yaml"
    registry.write_text(
        yaml.safe_dump(
            {
                "gates": [
                    {
                        "gate_id": "FOLDER-CAPACITY-HARD-LIMIT",
                        "register_line": 12,
                        "enabled": True,
                        "module_path": "zephyr.gov_enforcement.commit_gates.folder_capacity_gate",
                    },
                ]
            }
        ),
        encoding="utf-8",
    )
    monkey_registry_path = Path(mod.GATE_REGISTRY_PATH)
    assert monkey_registry_path.name == "in_process_gate_registry.yaml"
    assert mod._module_to_file("zephyr.gov_enforcement.commit_gates.folder_capacity_gate").endswith(
        "commit_gates/folder_capacity_gate.py"
    )


def test_payload_counts_are_fields_and_self_consistent(sample_file: Path, tmp_path: Path) -> None:
    findings = mod.scan_file(sample_file, tmp_path)
    stats = {"scan_roots": ["tmp"], "files_scanned": 1}
    payload = mod.build_payload(findings, stats, date(2026, 9, 26))
    meta = payload["meta"]
    counts = meta["counts"]
    assert counts["module_level_constants_total"] == len(findings)
    assert counts["threshold_candidates"] + counts["non_threshold_entries"] == counts["module_level_constants_total"]
    assert (
        counts["threshold_candidates_without_injection_point"] + counts["threshold_candidates_with_injection_point"]
        == counts["threshold_candidates"]
    )
    assert counts["threshold_candidate_files"] == len(payload["per_file_summary"])
    assert meta["status"] == "filed_proposal_only"
    assert "零改写" in meta["execution_policy"]
    assert payload["target_config"]["registry_id"] == mod.PROPOSED_REGISTRY_ID
    assert "threshold_id" in payload["target_config"]["entry_schema"]
    ids = [c["suggested_threshold_id"] for c in payload["constants"] if c["is_threshold"]]
    assert all(ids) and len(set(ids)) == len(ids)  # 逐常量有条目号且唯一


def test_generator_writes_no_source_files(sample_file: Path, tmp_path: Path) -> None:
    before = hashlib.sha256(sample_file.read_bytes()).hexdigest()
    payload = mod.build_payload(
        mod.scan_file(sample_file, tmp_path),
        {"scan_roots": ["tmp"], "files_scanned": 1},
        date(2026, 9, 26),
    )
    out = mod.write_payload(payload, tmp_path / "out" / "proposal.yaml")
    assert out.is_file()
    assert hashlib.sha256(sample_file.read_bytes()).hexdigest() == before  # 源码零改写
    reloaded = yaml.safe_load(out.read_text(encoding="utf-8"))
    assert reloaded["meta"]["counts"]["threshold_candidates"] == payload["meta"]["counts"]["threshold_candidates"]
