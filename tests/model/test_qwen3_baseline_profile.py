# [BLUEPRINT] MOD-INF-060 | 待统筹登记（10号文 §4 Phase 2.4）| §test
# [A_test] module_id: MOD-INF-060 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""qwen3:8b 本地推理质量基线测试（MOD-INF-060，10号文 §4 Phase 2.4）。

验收口径：基线成绩入库 data/model_profiles/ 且产物格式与
ModelRouter.load_benchmark_from_disk() / results_writer 消费口径一致。

覆盖：折算映射正确性（quick_profile -> benchmark 记录）/ 落盘原子写 /
_meta 头注行被消费方安全跳过 / 真实仓内产物经 ModelRouter + results_writer
双口径加载可读 / 空记录拒写。
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location(
    "run_qwen3_baseline_exam",
    _REPO_ROOT / "scripts" / "run_qwen3_baseline_exam.py",
)
baseline_script = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(baseline_script)

_PROFILES_DIR = _REPO_ROOT / "data" / "model_profiles"
_QUICK_PROFILE_SRC = _REPO_ROOT / "data" / "brain" / "quick_profiles" / "qwen3_8b.json"

_EXPECTED_KEYS = {
    "model_name",
    "source",
    "benchmark_date",
    "total_tests",
    "passed_tests",
    "average_score",
    "latency_p50_ms",
    "latency_p95_ms",
    "latency_p99_ms",
    "throughput_tokens_per_sec",
    "total_tokens",
    "total_time_ms",
    "category_scores",
    "hallucination_rate",
    "refusal_rate",
    "json_validity_rate",
    "code_validity_rate",
    "recommendation",
    "rank",
    "available",
    "error",
}


@pytest.fixture()
def quick_profile() -> dict:
    return json.loads(_QUICK_PROFILE_SRC.read_text(encoding="utf-8"))


class TestConversion:
    def test_key_set_compatible_with_results_writer(self, quick_profile: dict) -> None:
        record = baseline_script.quick_profile_to_benchmark_record(quick_profile, provenance="test")
        assert set(record) >= _EXPECTED_KEYS

    def test_mapping_values(self, quick_profile: dict) -> None:
        record = baseline_script.quick_profile_to_benchmark_record(quick_profile, provenance="test")
        assert record["model_name"] == "qwen3:8b"
        assert record["source"] == "ollama"
        assert record["average_score"] == pytest.approx(0.743)
        assert record["total_tests"] == len(quick_profile["capability_scores"])
        assert record["passed_tests"] == sum(1 for g in quick_profile["capability_grades"].values() if g != "F")
        assert record["category_scores"]["rule_comprehension"] == pytest.approx(0.833)
        assert record["hallucination_rate"] == pytest.approx(0.0833, abs=1e-3)
        assert record["refusal_rate"] == 0.0
        assert record["available"] is True
        assert record["baseline_provenance"] == "test"

    def test_missing_model_id_fail_closed(self) -> None:
        with pytest.raises(ValueError, match="model_id"):
            baseline_script.quick_profile_to_benchmark_record({}, provenance="test")


class TestWriteBaseline:
    def test_atomic_write_and_meta_line(self, tmp_path: Path, quick_profile: dict) -> None:
        record = baseline_script.quick_profile_to_benchmark_record(quick_profile, provenance="test")
        out = baseline_script.write_baseline_jsonl([record], output_dir=tmp_path, meta={"note": "test"})
        assert out.name.startswith("benchmark_")
        lines = out.read_text(encoding="utf-8").strip().split("\n")
        assert len(lines) == 2
        assert json.loads(lines[0])["_meta"]["note"] == "test"
        assert json.loads(lines[1])["model_name"] == "qwen3:8b"
        assert not list(tmp_path.glob("*.tmp"))

    def test_empty_records_refused(self, tmp_path: Path) -> None:
        with pytest.raises(ValueError, match="为空"):
            baseline_script.write_baseline_jsonl([], output_dir=tmp_path, meta={})


class TestRealArtifactConsumption:
    """仓内真实基线产物（10号文 Phase 2.4 验收物）经消费口径可读。"""

    def test_artifact_exists_with_qwen3_8b(self) -> None:
        files = sorted(_PROFILES_DIR.glob("benchmark_*.jsonl"))
        assert files, "data/model_profiles/ 无 benchmark 产物——先跑 scripts/run_qwen3_baseline_exam.py"
        records = [
            json.loads(line) for line in files[-1].read_text(encoding="utf-8").strip().split("\n") if line.strip()
        ]
        qwen = [r for r in records if r.get("model_name") == "qwen3:8b"]
        assert qwen, "最新 benchmark 文件缺 qwen3:8b 记录"
        assert qwen[0]["available"] is True
        assert "baseline_provenance" in qwen[0]

    def test_model_router_loads_baseline(self) -> None:
        from zephyr.governance.intelligence_governance.model_router import ModelRouter

        router = ModelRouter()
        count = router.load_benchmark_from_disk(str(_PROFILES_DIR))
        assert count >= 1
        assert router.has_benchmarks is True

    def test_results_writer_history_reads_baseline(self) -> None:
        from zephyr.intelligence.model_profiling.results_writer import load_benchmark_history

        history = load_benchmark_history("qwen3:8b", results_dir=str(_PROFILES_DIR))
        assert history, "load_benchmark_history 读不到 qwen3:8b 基线"
        assert history[-1]["average_score"] > 0

    def test_meta_line_skipped_by_consumers(self) -> None:
        """_meta 头注行不得被当作模型记录（无 model_name/available 键即被过滤）。"""
        files = sorted(_PROFILES_DIR.glob("benchmark_*.jsonl"))
        first = json.loads(files[-1].read_text(encoding="utf-8").strip().split("\n")[0])
        assert "_meta" in first
        assert "model_name" not in first
        assert first.get("available") is None
