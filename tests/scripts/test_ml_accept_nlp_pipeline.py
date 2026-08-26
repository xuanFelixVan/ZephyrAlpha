# [BLUEPRINT] MOD-NLP-PIPELINE | 13_regime_phase3_engineering_plan.md | §Phase 8
# [TTL] permanent
"""test_ml_accept_nlp_pipeline.py — NLP 验收脚本单元测试（Phase 8）。

覆盖（tmp fixture 产物驱动，不跑真实推理）：
  1. check_sft_f1 —— 达标/不达标/产物缺失/字段缺失
  2. check_inference_speed —— 达标/超时/样本量不足/产物缺失
  3. check_e2e_pipeline —— 字段齐备/缺字段/空产物
  4. check_batch_coverage —— 覆盖达标/起点不足/空产物
  5. check_weights_persisted / check_rlsp_weights —— 存在/缺失（WARN 不阻塞）
  6. summarize / main —— 全 PASS exit 0；任一必需 FAIL exit 1；WARN 不阻塞
"""

from __future__ import annotations

import importlib.util
import json
import pathlib
import sys

import pytest

_ROOT = pathlib.Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location(
    "accept_nlp_pipeline",
    _ROOT / "scripts" / "ml" / "accept_nlp_pipeline.py",
)
acp = importlib.util.module_from_spec(_spec)
sys.modules["accept_nlp_pipeline"] = acp  # dataclass 字符串注解解析需模块在册
_spec.loader.exec_module(acp)


def _write_json(path: pathlib.Path, obj: dict) -> None:
    path.write_text(json.dumps(obj), encoding="utf-8")


def _write_jsonl(path: pathlib.Path, rows: list[dict]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def _daily_row(day: str = "2010-01-04") -> dict:
    return {
        "day": day,
        "n_news": 5,
        "n_positive": 1,
        "n_negative": 2,
        "n_neutral": 2,
        "negative_count": 2,
        "mean_polarity": -0.1,
        "vote_direction": -1,
        "vote_score": -0.5,
        "vote_strength": "strong",
        "symbol": "",
    }


# ============ 1. check_sft_f1 ============


class TestSftF1:
    def test_pass(self, tmp_path):
        p = tmp_path / "m.json"
        _write_json(p, {"macro_f1": 0.7699})
        item = acp.check_sft_f1(p)
        assert item.status == "PASS"
        assert "0.7699" in item.detail

    def test_fail_below_threshold(self, tmp_path):
        p = tmp_path / "m.json"
        _write_json(p, {"macro_f1": 0.70})
        assert acp.check_sft_f1(p).status == "FAIL"

    def test_fail_missing_file(self, tmp_path):
        assert acp.check_sft_f1(tmp_path / "nope.json").status == "FAIL"

    def test_fail_missing_field(self, tmp_path):
        p = tmp_path / "m.json"
        _write_json(p, {"accuracy": 0.82})
        assert acp.check_sft_f1(p).status == "FAIL"


# ============ 2. check_inference_speed ============


class TestInferenceSpeed:
    def test_pass(self, tmp_path):
        p = tmp_path / "b.json"
        _write_json(p, {"items": 1000, "elapsed_s": 240.0})
        assert acp.check_inference_speed(p).status == "PASS"

    def test_fail_too_slow(self, tmp_path):
        p = tmp_path / "b.json"
        _write_json(p, {"items": 1000, "elapsed_s": 1000.0})  # 等效 1000s/1000 ≥ 900s 门槛
        assert acp.check_inference_speed(p).status == "FAIL"

    def test_rate_normalization(self, tmp_path):
        """速率语义：长批总耗时大但等效每千条达标 → PASS（防长腿批误伤）。"""
        p = tmp_path / "b.json"
        _write_json(p, {"items": 2000, "elapsed_s": 1000.0})  # 等效 500s/1000
        assert acp.check_inference_speed(p).status == "PASS"

    def test_fail_insufficient_items(self, tmp_path):
        p = tmp_path / "b.json"
        _write_json(p, {"items": 500, "elapsed_s": 60.0})
        assert acp.check_inference_speed(p).status == "FAIL"

    def test_fail_missing(self, tmp_path):
        assert acp.check_inference_speed(tmp_path / "nope.json").status == "FAIL"


# ============ 3. check_e2e_pipeline ============


class TestE2EPipeline:
    def test_pass(self, tmp_path):
        p = tmp_path / "daily.jsonl"
        _write_jsonl(p, [_daily_row()])
        assert acp.check_e2e_pipeline(p).status == "PASS"

    def test_fail_missing_field(self, tmp_path):
        p = tmp_path / "daily.jsonl"
        _write_jsonl(p, [{"day": "2010-01-04", "negative_count": 1}])
        assert acp.check_e2e_pipeline(p).status == "FAIL"

    def test_fail_empty(self, tmp_path):
        assert acp.check_e2e_pipeline(tmp_path / "nope.jsonl").status == "FAIL"


# ============ 4. check_batch_coverage ============


class TestBatchCoverage:
    def test_pass_full_history(self, tmp_path):
        p = tmp_path / "daily.jsonl"
        _write_jsonl(p, [_daily_row("2010-01-04"), _daily_row("2026-08-19")])
        assert acp.check_batch_coverage(p).status == "PASS"

    def test_fail_late_start(self, tmp_path):
        p = tmp_path / "daily.jsonl"
        _write_jsonl(p, [_daily_row("2020-06-01")])
        assert acp.check_batch_coverage(p).status == "FAIL"

    def test_custom_start_date(self, tmp_path):
        p = tmp_path / "daily.jsonl"
        _write_jsonl(p, [_daily_row("2020-06-01")])
        assert acp.check_batch_coverage(p, start_date="2020-07-01").status == "PASS"

    def test_fail_empty(self, tmp_path):
        assert acp.check_batch_coverage(tmp_path / "nope.jsonl").status == "FAIL"


# ============ 5. 权重持久化 ============


class TestWeights:
    def test_sft_present(self, tmp_path):
        (tmp_path / "adapter_model.safetensors").write_bytes(b"x")
        assert acp.check_weights_persisted(tmp_path).status == "PASS"

    def test_sft_missing(self, tmp_path):
        assert acp.check_weights_persisted(tmp_path).status == "FAIL"

    def test_rlsp_missing_is_warn_not_fail(self, tmp_path):
        item = acp.check_rlsp_weights(tmp_path)
        assert item.status == "WARN"
        assert item.required is False

    def test_rlsp_present(self, tmp_path):
        (tmp_path / "adapter_model.safetensors").write_bytes(b"x")
        assert acp.check_rlsp_weights(tmp_path).status == "PASS"


# ============ 6. summarize / main ============


def _all_pass_dir(tmp_path: pathlib.Path) -> dict[str, pathlib.Path]:
    metrics = tmp_path / "metrics.json"
    _write_json(metrics, {"macro_f1": 0.7699})
    bench = tmp_path / "bench.json"
    _write_json(bench, {"items": 1000, "elapsed_s": 200.0})
    daily = tmp_path / "daily.jsonl"
    _write_jsonl(daily, [_daily_row("2010-01-04")])
    adapter = tmp_path / "sft"
    adapter.mkdir()
    (adapter / "adapter_model.safetensors").write_bytes(b"x")
    rlsp = tmp_path / "rlsp"
    rlsp.mkdir()
    return {
        "metrics_path": metrics,
        "benchmark_path": bench,
        "daily_path": daily,
        "adapter_dir": adapter,
        "rlsp_dir": rlsp,
    }


class TestSummarize:
    def test_all_pass_true(self, tmp_path):
        items = acp.run_acceptance(**_all_pass_dir(tmp_path))
        assert acp.summarize(items) is True

    def test_required_fail_false(self, tmp_path):
        paths = _all_pass_dir(tmp_path)
        (paths["adapter_dir"] / "adapter_model.safetensors").unlink()
        items = acp.run_acceptance(**paths)
        assert acp.summarize(items) is False

    def test_warn_does_not_block(self, tmp_path):
        # RLSP 缺失（WARN）但总验收仍通过
        items = acp.run_acceptance(**_all_pass_dir(tmp_path))
        statuses = {it.name: it.status for it in items}
        assert statuses["rlsp_weights"] == "WARN"
        assert acp.summarize(items) is True


# ============ 7. 验收报告生成件（render_markdown_report / --report-out）============


class TestRenderMarkdownReport:
    def test_contains_items_and_verdict(self, tmp_path):
        items = acp.run_acceptance(**_all_pass_dir(tmp_path))
        md = acp.render_markdown_report(items)
        assert "# NLP 管道验收报告" in md
        assert "sft_f1" in md and "inference_speed" in md and "e2e_pipeline" in md
        assert "PASS" in md and "WARN" in md  # rlsp_weights WARN 行
        assert "总验收" in md and "通过" in md

    def test_fail_verdict_wording(self, tmp_path):
        paths = _all_pass_dir(tmp_path)
        (paths["adapter_dir"] / "adapter_model.safetensors").unlink()
        items = acp.run_acceptance(**paths)
        md = acp.render_markdown_report(items)
        assert "未通过" in md
        assert "sft_weights" in md and "FAIL" in md

    def test_metrics_summary_section(self, tmp_path):
        items = acp.run_acceptance(**_all_pass_dir(tmp_path))
        md = acp.render_markdown_report(items)
        # 指标汇总：各检查项 detail 入表
        assert "0.7699" in md
        assert "1000" in md


class TestReportOut:
    def test_main_writes_report_file(self, tmp_path, monkeypatch):
        paths = _all_pass_dir(tmp_path)
        report = tmp_path / "out" / "acceptance.md"
        monkeypatch.setattr(
            acp.sys,
            "argv",
            [
                "accept_nlp_pipeline.py",
                "--metrics",
                str(paths["metrics_path"]),
                "--benchmark",
                str(paths["benchmark_path"]),
                "--daily",
                str(paths["daily_path"]),
                "--adapter-dir",
                str(paths["adapter_dir"]),
                "--rlsp-dir",
                str(paths["rlsp_dir"]),
                "--report-out",
                str(report),
            ],
        )
        with pytest.raises(SystemExit) as exc:
            acp.main()
        assert exc.value.code == 0
        assert report.exists()
        md = report.read_text(encoding="utf-8")
        assert "# NLP 管道验收报告" in md


class TestMain:
    def test_main_exit_0(self, tmp_path, monkeypatch):
        paths = _all_pass_dir(tmp_path)
        monkeypatch.setattr(
            acp.sys,
            "argv",
            [
                "accept_nlp_pipeline.py",
                "--metrics",
                str(paths["metrics_path"]),
                "--benchmark",
                str(paths["benchmark_path"]),
                "--daily",
                str(paths["daily_path"]),
                "--adapter-dir",
                str(paths["adapter_dir"]),
                "--rlsp-dir",
                str(paths["rlsp_dir"]),
            ],
        )
        with pytest.raises(SystemExit) as exc:
            acp.main()
        assert exc.value.code == 0

    def test_main_exit_1_on_missing_artifacts(self, tmp_path, monkeypatch):
        monkeypatch.setattr(
            acp.sys,
            "argv",
            [
                "accept_nlp_pipeline.py",
                "--metrics",
                str(tmp_path / "no1.json"),
                "--benchmark",
                str(tmp_path / "no2.json"),
                "--daily",
                str(tmp_path / "no3.jsonl"),
                "--adapter-dir",
                str(tmp_path / "no4"),
                "--rlsp-dir",
                str(tmp_path / "no5"),
            ],
        )
        with pytest.raises(SystemExit) as exc:
            acp.main()
        assert exc.value.code == 1
