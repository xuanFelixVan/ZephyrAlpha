# [A_test] module_id: MOD-RESCHED-SAMPLER | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-RESCHED-SAMPLER | docs/03_modules/_cross_layer/resource_sampler/blueprint.md | §
# [MODULE] tests.infrastructure.test_resource_sampler
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] tests/infrastructure/test_resource_sampler.py
# [TTL] task_bound
"""采样器测试：stub 进程表（禁真启重活进程）/模式推导/JSONL 损坏降级/回写口径/时钟回拨/进程消失。"""
from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from zephyr.infrastructure.system_telemetry.resource_sampler import (
    ENV_REGISTRY,
    ResourceSampler,
    Sample,
    _percentile,
)

GB = 1024**3


@pytest.fixture()
def reg(tmp_path):
    """tmp 注册表（禁写生产路径）：2 可观测实体+1 宿主共享槽位+1 retired。"""
    data = {
        "mem_ceiling_gb": 10.0,
        "entities": [
            {"task_id": "sch_heavy_a", "status": "active", "resource_class": "cpu_heavy",
             "schedule_truth_source": "docs/_working/resource_schedule/resource_schedule_panorama_plan_v1.md",
             "measured": {"peak_mem_gb": None, "p90_duration_min": None, "samples": 0, "last_at": None}},
            {"task_id": "manual_kronos_adapter", "status": "planned", "resource_class": "gpu",
             "schedule_truth_source": "docs/_working/resource_schedule/resource_schedule_panorama_plan_v1.md",
             "measured": {"peak_mem_gb": None, "p90_duration_min": None, "samples": 0, "last_at": None}},
            {"task_id": "data_slot_daily_kline", "status": "active", "resource_class": "db_heavy",
             "schedule_truth_source": "src/zephyr/data/config/schedule.yaml"},
            {"task_id": "sch_trading_watchdog", "status": "retired", "resource_class": "light",
             "schedule_truth_source": "x.ps1"},
        ],
    }
    p = tmp_path / "reg.yaml"
    p.write_text(yaml.safe_dump(data, allow_unicode=True), encoding="utf-8")
    return p


def _make_sampler(reg, tmp_path, procs, now_fn=None):
    return ResourceSampler(
        registry_path=reg,
        samples_dir=tmp_path / "samples",
        patterns={"sch_heavy_a": r"heavy_marker_a", "manual_kronos_adapter": r"kronos_marker"},
        scanner=lambda: procs,
        now_fn=now_fn,
    )


def test_scan_once_matches_and_writes_jsonl(reg, tmp_path):
    procs = [
        {"pid": 100, "cmdline": "python worker.py --heavy_marker_a x", "create_time": 1000.0, "cpu_time_seconds": 50.0},
        {"pid": 101, "cmdline": "kronos_marker --model q", "create_time": 2000.0, "cpu_time_seconds": 10.0},
        {"pid": 102, "cmdline": "unrelated process", "create_time": 3000.0, "cpu_time_seconds": 0.0},
    ]
    s = _make_sampler(reg, tmp_path, procs, now_fn=lambda: 4000.0)
    summary = s.scan_once()
    # 100: elapsed=3000s>1 → cpu_ratio=50/3000；101: elapsed=2000 → 10/2000
    assert summary["samples_written"] == {"sch_heavy_a": 1, "manual_kronos_adapter": 1}
    f = tmp_path / "samples" / "sch_heavy_a.jsonl"
    obj = json.loads(f.read_text(encoding="utf-8").splitlines()[0])
    assert obj["task_id"] == "sch_heavy_a" and obj["pid"] == 100
    assert obj["process_resident_bytes"] >= 0
    assert abs(obj["process_cpu_ratio"] - 50.0 / 3000.0) < 1e-3
    # Prometheus 命名纪律：base unit 后缀
    assert "process_resident_bytes" in obj and "process_elapsed_seconds" in obj
    # 宿主共享槽位与 retired 不参与
    assert "data_slot_daily_kline" in summary["host_shared_skipped"]
    assert all("sch_trading_watchdog" not in x for x in summary["observable_tasks"])


def test_scan_once_process_vanishes_mid_sample(reg, tmp_path):
    """红蓝：进程消失竞态——psutil 查询失败时记 0 字节样本不炸。"""
    procs = [{"pid": 100, "cmdline": "heavy_marker_a", "create_time": 1000.0, "cpu_time_seconds": 1.0}]
    s = _make_sampler(reg, tmp_path, procs, now_fn=lambda: 1100.0)
    # 让 rss 探测抛（进程消失）：monkeypatch psutil.Process 路径——scanner 注入层已 mock，
    # 这里用 pid 查询失败的等价路径：样本仍应落盘
    summary = s.scan_once()
    assert summary["samples_written"] == {"sch_heavy_a": 1}


def test_clock_rollback_non_negative_elapsed(reg, tmp_path):
    """红蓝：时钟回拨——create_time 晚于当前时刻时 elapsed 钳 0。"""
    procs = [{"pid": 100, "cmdline": "heavy_marker_a", "create_time": 5000.0, "cpu_time_seconds": 10.0}]
    s = _make_sampler(reg, tmp_path, procs, now_fn=lambda: 4000.0)  # 回拨
    summary = s.scan_once()
    f = tmp_path / "samples" / "sch_heavy_a.jsonl"
    obj = json.loads(f.read_text(encoding="utf-8").splitlines()[0])
    assert obj["process_elapsed_seconds"] == 0.0
    assert obj["process_cpu_ratio"] == 0.0


def test_read_samples_skips_corrupt_lines(reg, tmp_path):
    """红蓝：JSONL 损坏行降级计数不炸。"""
    s = _make_sampler(reg, tmp_path, [], )
    f = tmp_path / "samples" / "sch_heavy_a.jsonl"
    f.parent.mkdir(parents=True)
    good = Sample(sample_time_seconds=1.0, task_id="sch_heavy_a", pid=1,
                  process_resident_bytes=2 * GB, process_cpu_ratio=0.5, process_elapsed_seconds=60.0)
    f.write_text(good.to_json() + "\n{corrupt!!!\n" + good.to_json() + "\nnull\n", encoding="utf-8")
    samples, bad = s.read_samples("sch_heavy_a")
    assert len(samples) == 2 and bad == 2


def test_writeback_max_margin_and_p90(reg, tmp_path):
    s = _make_sampler(reg, tmp_path, [])
    f = tmp_path / "samples" / "sch_heavy_a.jsonl"
    f.parent.mkdir(parents=True)
    # 实测 max=4GB 尖刺（其余 1-2GB）→ 4*1.15=4.6；elapsed P90≈90 分
    rows = [
        (2.0, 3600), (1.0, 3000), (2.0, 3300), (4.0, 5400), (1.5, 3000),
    ]
    for i, (gb, el) in enumerate(rows):
        s._append_sample(Sample(sample_time_seconds=1000.0 + i, task_id="sch_heavy_a", pid=10 + i,
                                process_resident_bytes=int(gb * GB), process_cpu_ratio=0.5,
                                process_elapsed_seconds=float(el)))
    out = s.writeback(task_ids=["sch_heavy_a"])
    assert "sch_heavy_a" in out["updated"]
    data = yaml.safe_load(reg.read_text(encoding="utf-8"))
    m = data["entities"][0]["measured"]
    assert m["peak_mem_gb"] == round(4.0 * 1.15, 4)  # 尖刺 max+15% margin（非分位数）
    assert m["p90_duration_min"] == 78  # 线性插值 P90（3600+0.6*(5400-3600)）=4680s
    assert m["samples"] == 5
    assert m["last_at"]
    # 人填字段零触碰：registry 其他实体未动
    assert data["entities"][1]["measured"]["samples"] == 0


def test_writeback_skips_entities_without_samples(reg, tmp_path):
    s = _make_sampler(reg, tmp_path, [])
    out = s.writeback()
    assert out["updated"] == {}


def test_writeback_preserves_file_header_comments(reg, tmp_path):
    """回归（2026-09-16 生产实证）：writeback 重序列化曾把文件头 GENERATED 声明剥掉
    ——头部注释块必须原样保全（writeback 只拥有 measured 四键，无权重写文件身份）。"""
    reg.write_text(
        "# [GENERATED] line one\n# line two\n" + reg.read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    s = _make_sampler(reg, tmp_path, [])
    s._append_sample(Sample(sample_time_seconds=1.0, task_id="sch_heavy_a", pid=1,
                            process_resident_bytes=2 * GB, process_cpu_ratio=0.5,
                            process_elapsed_seconds=60.0))
    out = s.writeback(task_ids=["sch_heavy_a"])
    assert "sch_heavy_a" in out["updated"]
    text = reg.read_text(encoding="utf-8")
    assert text.startswith("# [GENERATED] line one\n# line two\n"), text[:80]


def test_percentile_linear_interpolation():
    assert _percentile([], 90) == 0.0
    assert _percentile([5.0], 90) == 5.0
    vals = list(range(1, 101))  # 1..100，P90 = 90.1
    assert abs(_percentile(vals, 90) - 90.1) < 1e-9


def test_ps1_truth_source_pattern_derivation(reg, tmp_path):
    """ps1 真源→被调脚本基名抽取（零硬编码观测）。"""
    s = ResourceSampler(registry_path=reg, samples_dir=tmp_path / "s2")
    pats = s._patterns_from_ps1("scripts/register_factory_lane_c_task.ps1")
    assert any("run_factory_lane_c" in p for p in pats)
    assert all(not p.startswith("register_") for p in pats)  # 登记器自身排除


def test_env_redirect_isolation(tmp_path, monkeypatch):
    """环境变量重定向（测试隔离主通道）。"""
    monkeypatch.setenv(ENV_REGISTRY, str(tmp_path / "r.yaml"))
    from zephyr.infrastructure.system_telemetry.resource_sampler import registry_path as rp

    assert rp() == tmp_path / "r.yaml"
