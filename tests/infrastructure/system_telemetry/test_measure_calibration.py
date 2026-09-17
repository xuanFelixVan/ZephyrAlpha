# [A_test] module_id: MOD-RESCHED-CALIB | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-RESCHED-CALIB | docs/03_modules/_cross_layer/measure_calibration/blueprint.md | §
# [MODULE] tests.infrastructure.system_telemetry.test_measure_calibration
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] tests/infrastructure/system_telemetry/test_measure_calibration.py
# [TTL] task_bound
"""p90 校准器测试：三类实体（样本充足偏差>30% / 样本充足偏差<30% / 零样本）+ 边界 + 只读纪律。

全部 tmp_path 合成（禁读生产 .runtime 样本流与 config/ 注册表）；台账经 ENV_LEDGER 指到
不存在路径（pid 随机器变，读到生产台账就不可复现）。
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from zephyr.infrastructure.system_telemetry.measure_calibration import (
    DEFAULT_DEVIATION_TOLERANCE_PCT,
    FIELD_DURATION,
    FIELD_MEMORY,
    MeasureCalibrator,
    calibrate,
    main,
    read_calibration_report,
)
from zephyr.infrastructure.system_telemetry.resource_sampler import ENV_LEDGER, ENV_REGISTRY

GB = 1024**3


def _entity(tid, *, status="active", est=None, mem=None, **kw):
    e = {"task_id": tid, "status": status, "resource_class": "cpu_heavy",
         "schedule_truth_source": "docs/_working/resource_schedule/resource_schedule_panorama_plan_v1.md"}
    if est is not None:
        e["est_duration_min"] = est
    if mem is not None:
        e["peak_mem_gb"] = mem
    e.update(kw)
    return e


def _samples(path: Path, rows: list[dict]) -> None:
    """合成样本流（字段名 Prometheus 口径，与 sampler 写侧一致）。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    base = {"process_cpu_ratio": 0.5, "exit_code": None, "attribution": "pattern"}
    with open(path, "w", encoding="utf-8") as fh:
        for i, r in enumerate(rows):
            obj = {**base, "sample_time_seconds": 1000.0 + i * 60, "pid": 500 + i, **r}
            fh.write(json.dumps(obj, ensure_ascii=False) + "\n")


def _elapsed_rows(tid, elapsed_s, rss_bytes, n=5):
    return [{"task_id": tid, "process_elapsed_seconds": elapsed_s,
             "process_resident_bytes": rss_bytes} for _ in range(n)]


@pytest.fixture()
def fake_root(tmp_path, monkeypatch):
    """三类实体：偏差>30%（低估）、偏差<30%（match）、零样本（样本不足）。"""
    entities = [
        _entity("sch_under_est", est=10, mem=1.0),          # 实测 30min / 2.3GB → 两轴都低估
        _entity("sch_match", est=30, mem=2.3),               # 实测 30min / 2.3GB → 两轴都 match
        _entity("sch_no_sample", est=60, mem=4.0),           # 零样本
        _entity("sch_resident", est=0, mem=None),            # 常驻：分母为零不可比
        _entity("sch_zero_rss", est=30, mem=2.0),            # 样本有但 RSS 全 0
        _entity("sch_retired", est=10, mem=1.0, status="retired"),
    ]
    root = tmp_path / "root"
    reg = root / "config" / "resource_profile_registry.yaml"
    reg.parent.mkdir(parents=True, exist_ok=True)
    reg.write_text(yaml.safe_dump({"mem_ceiling_gb": 10.0, "entities": entities},
                                  allow_unicode=True), encoding="utf-8")
    sdir = root / ".runtime" / "logs" / "resource_samples"
    _samples(sdir / "sch_under_est.jsonl", _elapsed_rows("sch_under_est", 1800, 2 * GB))
    _samples(sdir / "sch_match.jsonl", _elapsed_rows("sch_match", 1800, 2 * GB))
    _samples(sdir / "sch_resident.jsonl", _elapsed_rows("sch_resident", 600, GB))
    _samples(sdir / "sch_zero_rss.jsonl", _elapsed_rows("sch_zero_rss", 1800, 0))
    _samples(sdir / "sch_retired.jsonl", _elapsed_rows("sch_retired", 1800, 2 * GB))
    monkeypatch.setenv(ENV_LEDGER, str(tmp_path / "ledger-absent.jsonl"))
    monkeypatch.delenv(ENV_REGISTRY, raising=False)
    return root


def _report(root, **kw):
    return calibrate(root=root, **kw)


def _row(report, tid):
    return next(r for r in report["rows"] if r["task_id"] == tid)


def _axis(row, field):
    return next(a for a in row["axes"] if a["field"] == field)


def test_flag_over_tolerance_both_axes(fake_root):
    """偏差>30% → 两轴都 flag，方向=低估（实测>申报，班次会压到下一班）。"""
    row = _row(_report(fake_root), "sch_under_est")
    assert row["calibration_status"] == "已校准"
    assert set(row["flags"]) == {FIELD_DURATION, FIELD_MEMORY}
    dur = _axis(row, FIELD_DURATION)
    assert dur["declared"] == 10 and dur["measured_p90"] == 30.0
    assert dur["deviation_ratio"] == 2.0 and dur["direction"] == "低估"
    mem = _axis(row, FIELD_MEMORY)
    assert mem["measured_p90"] == pytest.approx(2.3)  # 2GiB×(1+15% margin)
    assert mem["direction"] == "低估" and mem["flagged"] is True


def test_within_tolerance_not_flagged(fake_root):
    """偏差在 30% 容差内 → 不 flag（flagged 判据不放松）。"""
    row = _row(_report(fake_root), "sch_match")
    assert row["flags"] == []
    assert all(a["direction_code"] == "match" for a in row["axes"])


def test_zero_samples_never_fabricates(fake_root):
    """零样本 → 状态『样本不足』、实测一律 null、无校正条目（禁编造）。"""
    row = _row(_report(fake_root), "sch_no_sample")
    assert row["calibration_status"] == "样本不足"
    assert row["samples"] == 0
    assert row["proposed_corrections"] == []
    assert all(a["measured_p90"] is None for a in row["axes"])
    assert all(a["direction_code"] == "no_measurement" for a in row["axes"])
    assert "禁" in row["note_zh"]


def test_totals_and_flat_corrections(fake_root):
    """totals 与扁平校正清单同数（晨报摘要段按此取数）。"""
    rep = _report(fake_root)
    flat = rep["proposed_corrections"]
    assert rep["totals"]["flagged_fields"] == len(flat) == 2
    assert rep["totals"]["低估"] == 2 and rep["totals"]["高估"] == 0
    assert rep["totals"]["insufficient_samples"] >= 1
    assert {c["task_id"] for c in flat} == {"sch_under_est"}
    assert {c["field"] for c in flat} == {FIELD_DURATION, FIELD_MEMORY}
    assert all(c["caliber_zh"] and c["verdict"] for c in flat)


def test_resident_and_zero_rss_not_comparable(fake_root):
    """申报为 0（常驻）与 RSS 全 0：判不可比/无证据，不硬算比值（分母为零=编造）。"""
    rep = _report(fake_root)
    res = _axis(_row(rep, "sch_resident"), FIELD_DURATION)
    assert res["direction_code"] == "not_comparable" and res["flagged"] is False
    zrss = _axis(_row(rep, "sch_zero_rss"), FIELD_MEMORY)
    assert zrss["measured_p90"] is None
    assert zrss["direction_code"] == "no_rss_evidence" and zrss["flagged"] is False


def test_retired_excluded_from_correction_batch(fake_root):
    """退役实体不进校正批（即便样本显示偏差巨大）。"""
    row = _row(_report(fake_root), "sch_retired")
    assert row["calibration_status"] == "已退役不计"
    assert row["flags"] == [] and row["proposed_corrections"] == []


def test_tolerance_boundary_strict_greater(tmp_path, monkeypatch):
    """恰等阈值不 flag、超一点即 flag（严格大于口径，与 sampler match 边界一致）。"""
    ent = [_entity("sch_edge", est=10)]
    root = tmp_path / "root"
    (root / "config").mkdir(parents=True)
    (root / "config" / "resource_profile_registry.yaml").write_text(
        yaml.safe_dump({"entities": ent}), encoding="utf-8")
    sdir = root / ".runtime" / "logs" / "resource_samples"
    monkeypatch.setenv(ENV_LEDGER, str(tmp_path / "none.jsonl"))
    # 780s → P90 13.0min → ratio 恰 0.30；改 790s → 13.2min → 0.32 越界
    _samples(sdir / "sch_edge.jsonl", _elapsed_rows("sch_edge", 780, GB))
    assert _axis(_row(_report(root), "sch_edge"), FIELD_DURATION)["flagged"] is False
    _samples(sdir / "sch_edge.jsonl", _elapsed_rows("sch_edge", 790, GB))
    edge = _axis(_row(_report(root), "sch_edge"), FIELD_DURATION)
    assert edge["flagged"] is True and edge["direction"] == "低估"


def test_high_estimate_direction_overdeclared(tmp_path, monkeypatch):
    """实测远小于申报 → 方向=高估（白占并发预算）。"""
    root = tmp_path / "root"
    (root / "config").mkdir(parents=True)
    (root / "config" / "resource_profile_registry.yaml").write_text(
        yaml.safe_dump({"entities": [_entity("sch_over", est=120, mem=8.0)]}), encoding="utf-8")
    monkeypatch.setenv(ENV_LEDGER, str(tmp_path / "none.jsonl"))
    _samples(root / ".runtime" / "logs" / "resource_samples" / "sch_over.jsonl",
             _elapsed_rows("sch_over", 300, GB // 4))  # 5min / 0.2875GB
    rep = _report(root)
    row = _row(rep, "sch_over")
    assert {a["direction"] for a in row["axes"] if a["flagged"]} == {"高估"}
    assert all(a["deviation_ratio"] < 0 for a in row["axes"] if a["flagged"])
    assert rep["totals"]["高估"] == 2


def test_corrupt_sample_line_degrades(tmp_path, monkeypatch):
    """样本流坏行：跳过计数，不炸校准（JSONL 降级纪律与 sampler 同侧）。"""
    root = tmp_path / "root"
    (root / "config").mkdir(parents=True)
    (root / "config" / "resource_profile_registry.yaml").write_text(
        yaml.safe_dump({"entities": [_entity("sch_bad", est=10, mem=1.0)]}), encoding="utf-8")
    f = root / ".runtime" / "logs" / "resource_samples" / "sch_bad.jsonl"
    _samples(f, _elapsed_rows("sch_bad", 1800, 2 * GB))
    with open(f, "a", encoding="utf-8") as fh:
        fh.write("{ not json\n")
    monkeypatch.setenv(ENV_LEDGER, str(tmp_path / "none.jsonl"))
    assert _axis(_row(_report(root), "sch_bad"), FIELD_DURATION)["measured_p90"] == 30.0


def test_default_tolerance_is_thirty_percent():
    assert DEFAULT_DEVIATION_TOLERANCE_PCT == 30.0


def test_calibrate_does_not_write_registry(fake_root):
    """只读纪律：校准全程不得触碰注册表（measured.* 写权归 sampler.writeback）。"""
    reg = fake_root / "config" / "resource_profile_registry.yaml"
    before = reg.read_bytes()
    _report(fake_root)
    assert reg.read_bytes() == before


def test_cli_root_injection_and_report_roundtrip(fake_root, tmp_path, capsys):
    """CLI --root 注入 → YAML 报告落盘（GENERATED 头）→ 读回摘要一致。"""
    out = tmp_path / "calibration_report.yaml"
    rc = main(["--root", str(fake_root), "--output", str(out), "--print"])
    assert rc == 0
    summary = json.loads(capsys.readouterr().out.strip().splitlines()[-1])
    assert summary["totals"]["flagged_fields"] == 2
    text = out.read_text(encoding="utf-8")
    assert "[GENERATED]" in text and "proposed_corrections" in text
    loaded = read_calibration_report(out)
    assert loaded["totals"] == summary["totals"]
    assert loaded["tolerance_pct"] == 30.0


def test_cli_no_write_skips_file(fake_root, tmp_path, capsys):
    """--no-write 演练模式不落盘（晨报跑在报告之前时不必留半成品）。"""
    out = tmp_path / "nested" / "report.yaml"
    rc = main(["--root", str(fake_root), "--output", str(out), "--no-write"])
    assert rc == 0
    assert not out.exists()
    assert "未落盘" in capsys.readouterr().out


def test_missing_report_reads_as_none(tmp_path):
    """报告缺席/损坏 → None（晨报据实写『未生成』，不臆造摘要）。"""
    assert read_calibration_report(tmp_path / "nope.yaml") is None
    bad = tmp_path / "bad.yaml"
    bad.write_text("\t- : :\n  broken: [", encoding="utf-8")
    assert read_calibration_report(bad) is None


def test_task_filter_limits_rows(fake_root):
    rep = calibrate(root=fake_root, task_ids=["sch_match"])
    assert [r["task_id"] for r in rep["rows"]] == ["sch_match"]
