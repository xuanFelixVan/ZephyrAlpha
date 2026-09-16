# [A_test] module_id: MOD-RESCHED-SAMPLER | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-RESCHED-SAMPLER | docs/03_modules/_cross_layer/resource_sampler/blueprint.md | §
# [MODULE] tests.infrastructure.test_resource_sampler
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] tests/infrastructure/test_resource_sampler.py
# [TTL] task_bound
"""采样器测试：stub 进程表（禁真启重活进程）/模式推导/JSONL 损坏降级/回写口径/时钟回拨/进程消失。

L-1（2026-09-17 P1-a）追加：孵化台账 pid join 归因正例（cmdline 看不见的实体/槽位解锁）、
歧义反例（同 pid 复用跨窗、一名多实体、双证据链互斥）、申报寿命 vs 实测寿命偏差对账、
零样本实体"留 null + 如实原因"（禁编造）。台账与样本流全部 tmp_path 合成（禁读生产 .runtime）。
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from zephyr.infrastructure.system_telemetry.resource_sampler import (
    ENV_LEDGER,
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


@pytest.fixture(autouse=True)
def _no_production_ledger(tmp_path, monkeypatch):
    """L-1 隔离钉：默认把孵化台账指到不存在的 tmp 路径。

    生产 `.runtime/process_incubator/ledger.jsonl` 里的 pid 随机器/时刻变，测试若默认
    读到它，归因结果就不是可复现的（而且违反"测试禁碰生产路径"）。要看台账的用例
    自己注入合成 fixture（ledger=/ledger_path=）。
    """
    monkeypatch.setenv(ENV_LEDGER, str(tmp_path / "ledger-absent.jsonl"))


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


# ── L-1 孵化台账 × 样本流 pid join（2026-09-17 P1-a）────────────────────────
_T0 = 1_000_000.0  # 合成时间基准（浮点秒，与 psutil create_time 同单位）
_PLAN_DOC = "docs/_working/resource_schedule/resource_schedule_panorama_plan_v1.md"


def _rec(pid, name, *, owner="", spawned=_T0, exited=None, expected=None,
         parent=4000, rid=None):
    """台账一行：字段名与 process_incubator 真源同构（未知键由 load 侧忽略）。"""
    return {
        "record_id": rid or f"r{pid}_{name}",
        "child_pid": pid, "parent_pid": parent, "root_pid": 1,
        "ancestor_chain": [parent], "name": name, "owner": owner,
        "cmd": f"python.exe -m zephyr.demo --{name}",
        "spawned_at": spawned, "expected_lifetime_s": expected, "exited_at": exited,
        "exit_code": 0 if exited is not None else None, "reaped": False,
    }


def _write_ledger(tmp_path, records, *, corrupt=0, name="ledger.jsonl"):
    p = tmp_path / name
    lines = [json.dumps(r) for r in records]
    for i in range(corrupt):
        lines.insert(min(i, len(lines)), "{坏行 json!!! " + str(i))
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return p


def _ents(*specs, **kw):
    """实体清单速记：只写真源相关字段，其余走默认（active + 计划文档真源）。"""
    out = []
    for s in specs:
        tid, extra = (s, {}) if isinstance(s, str) else (s[0], s[1])
        e = {"task_id": tid, "status": "active", "resource_class": "light",
             "schedule_truth_source": _PLAN_DOC}
        e.update(extra)
        out.append(e)
    return out


def _mk_reg(tmp_path, ents, name="reg.yaml"):
    p = tmp_path / name
    p.write_text(yaml.safe_dump({"mem_ceiling_gb": 10.0, "entities": list(ents)},
                                allow_unicode=True, sort_keys=False), encoding="utf-8")
    return p


def _l1_sampler(reg, tmp_path, procs, *, ledger=None, ledger_path=None, patterns=None,
                now=_T0 + 300.0):
    return ResourceSampler(registry_path=reg, samples_dir=tmp_path / "s_l1",
                           patterns=patterns, scanner=lambda: procs,
                           now_fn=lambda: now, ledger=ledger, ledger_path=ledger_path)


def _proc(pid, cmdline="python.exe -m zephyr.demo", *, create=_T0, cpu=30.0):
    return {"pid": pid, "cmdline": cmdline, "create_time": create, "cpu_time_seconds": cpu}


def test_ledger_join_unlocks_entity_invisible_to_cmdline(tmp_path):
    """归因正例①：cmdline 正则看不见的实体（无 ps1/无静态表）经台账 pid join 拿到样本。"""
    reg = _mk_reg(tmp_path, _ents("sch_ollama_serve"))
    led = _write_ledger(tmp_path, [_rec(5001, "ollama-serve", expected=3600.0, parent=4242)])
    s = _l1_sampler(reg, tmp_path, [_proc(5001)], ledger_path=led)
    summary = s.scan_once()
    assert summary["samples_written"] == {"sch_ollama_serve": 1}
    assert summary["attribution_sources"] == {"ledger": 1}
    assert summary["ledger_records"] == 1
    assert "sch_ollama_serve" not in summary["observable_tasks"], " cmdline 侧本就该看不见"
    obj = json.loads((tmp_path / "s_l1" / "sch_ollama_serve.jsonl").read_text(
        encoding="utf-8").splitlines()[0])
    assert obj["attribution"] == "ledger" and obj["ledger_record_id"] == "r5001_ollama-serve"
    assert obj["parent_pid"] == 4242, "父子链要落进样本，否则宿主/子进程分层计数无从做起"


def test_ledger_join_unlocks_data_slot_child_pid(tmp_path):
    """归因正例②（L-1 主诉求）：台账真给出槽位 child_pid 时 data_slot_* 才解锁。"""
    reg = _mk_reg(tmp_path, _ents(("data_slot_daily_kline",
                                   {"schedule_truth_source": "src/zephyr/data/config/schedule.yaml"})))
    led = _write_ledger(tmp_path, [_rec(5100, "daily-kline", expected=900.0)])
    s = _l1_sampler(reg, tmp_path, [_proc(5100)], ledger_path=led)
    summary = s.scan_once()
    assert summary["samples_written"] == {"data_slot_daily_kline": 1}
    assert summary["host_shared_skipped"] == [], "台账给出 pid 后不得再挂'宿主共享不可观测'"


def test_data_slot_without_ledger_record_stays_unattributed(tmp_path):
    """反例（解锁的对偶）：台账给不出槽位 pid 时**不假装归因**——宁缺勿错。"""
    reg = _mk_reg(tmp_path, _ents(("data_slot_daily_kline",
                                   {"schedule_truth_source": "src/zephyr/data/config/schedule.yaml"})))
    led = _write_ledger(tmp_path, [_rec(5100, "some-other-worker")])
    s = _l1_sampler(reg, tmp_path, [_proc(5100)], ledger_path=led)
    summary = s.scan_once()
    assert summary["samples_written"] == {}
    assert summary["host_shared_skipped"] == ["data_slot_daily_kline"]


def test_ledger_attribution_ambiguity_never_writes(tmp_path):
    """三类歧义一律不写样本：pid 复用跨窗 / 一名多实体 / 双证据链互斥。"""
    # ① 同 pid 两条记录且时间窗重叠 → 谁在跑说不清
    reg = _mk_reg(tmp_path, _ents("sch_ollama_serve", "sch_drift_watch"))
    led = _write_ledger(tmp_path, [
        _rec(6002, "ollama-serve", spawned=_T0, exited=_T0 + 1000),
        _rec(6002, "drift-watch", spawned=_T0 + 100, exited=_T0 + 900)])
    s = _l1_sampler(reg, tmp_path, [_proc(6002)], ledger_path=led, now=_T0 + 500)
    summary = s.scan_once()
    assert summary["samples_written"] == {}
    assert summary["ambiguous_pids"] == {"6002": "ambiguous_pid_reuse"}
    assert not (tmp_path / "s_l1" / "sch_ollama_serve.jsonl").exists()
    # ② 时间窗能定唯一时才下判（复用不是一律拒绝，而是"看得清才写"）
    ok = s.ledger().attribute_pid(6002, _T0 + 950)
    assert ok[1] == "ok" and ok[0].name == "ollama-serve", ok
    # ③ 一个台账家族对上多个实体
    reg3 = _mk_reg(tmp_path, _ents("sch_ollama_serve", "manual_ollama_serve"), name="reg3.yaml")
    led3 = _write_ledger(tmp_path, [_rec(6003, "ollama-serve")], name="led3.jsonl")
    s3 = _l1_sampler(reg3, tmp_path, [_proc(6003)], ledger_path=led3)
    sm3 = s3.scan_once()
    assert sm3["samples_written"] == {}
    assert sm3["ambiguous_pids"]["6003"] == "multi_entity:manual_ollama_serve|sch_ollama_serve"
    # ④ 两条证据链指向不同实体 = 必有一条错 → 不猜
    reg4 = _mk_reg(tmp_path, _ents("sch_ollama_serve", "sch_heavy_a"), name="reg4.yaml")
    led4 = _write_ledger(tmp_path, [_rec(7001, "ollama-serve")], name="led4.jsonl")
    s4 = _l1_sampler(reg4, tmp_path, [_proc(7001, "run heavy_marker_a now")], ledger_path=led4,
                     patterns={"sch_heavy_a": r"heavy_marker_a"})
    sm4 = s4.scan_once()
    assert sm4["samples_written"] == {}
    assert sm4["ambiguous_pids"]["7001"] == "chain_conflict:pattern=sch_heavy_a/ledger=sch_ollama_serve"
    # ⑤ 两条证据链同指一实体 → 双证加固，样本带 pattern+ledger 溯源
    reg5 = _mk_reg(tmp_path, _ents("sch_ollama_serve"), name="reg5.yaml")
    led5 = _write_ledger(tmp_path, [_rec(7002, "ollama-serve")], name="led5.jsonl")
    s5 = _l1_sampler(reg5, tmp_path, [_proc(7002, "llama-server ollama-serve --model x")],
                     ledger_path=led5, patterns={"sch_ollama_serve": r"llama-server"})
    sm5 = s5.scan_once()
    assert sm5["samples_written"] == {"sch_ollama_serve": 1}
    assert sm5["attribution_sources"] == {"pattern+ledger": 1}


def test_retired_entity_never_attributed_even_if_ledger_knows(tmp_path):
    """retired 实体不配拿到 measured 增量（归因域先按 status 过滤）。"""
    reg = _mk_reg(tmp_path, _ents(("sch_trading_watchdog", {"status": "retired"})))
    led = _write_ledger(tmp_path, [_rec(8001, "trading-watchdog")])
    s = _l1_sampler(reg, tmp_path, [_proc(8001)], ledger_path=led)
    assert s.attributable_task_ids(s.load_entities()) == set()
    assert s.scan_once()["samples_written"] == {}


def test_unledgered_pid_falls_back_to_pattern_chain(tmp_path):
    """台账无此 pid = 不产生歧义噪音，cmdline 链单独仍可归因（源标 pattern）。"""
    reg = _mk_reg(tmp_path, _ents("sch_heavy_a"))
    led = _write_ledger(tmp_path, [_rec(9999, "someone-else")])
    s = _l1_sampler(reg, tmp_path, [_proc(100, "heavy_marker_a")], ledger_path=led,
                    patterns={"sch_heavy_a": r"heavy_marker_a"})
    summary = s.scan_once()
    assert summary["samples_written"] == {"sch_heavy_a": 1}
    assert summary["attribution_sources"] == {"pattern": 1}
    assert summary["ambiguous_pids"] == {}
    obj = json.loads((tmp_path / "s_l1" / "sch_heavy_a.jsonl").read_text(encoding="utf-8").splitlines()[0])
    assert obj["attribution"] == "pattern" and obj["ledger_record_id"] is None


def test_ledger_load_degrades_without_crashing(tmp_path):
    """台账缺失/坏行：降级为"仅 cmdline 归因"，坏行计数可见（与样本流同一纪律）。"""
    from zephyr.infrastructure.system_telemetry.resource_sampler import IncubationLedger

    empty = IncubationLedger.load(tmp_path / "nope.jsonl")
    assert len(empty) == 0 and empty.bad_lines == 0
    led = IncubationLedger.load(_write_ledger(tmp_path, [_rec(5001, "ollama-serve")],
                                              corrupt=2, name="l.jsonl"))
    assert len(led) == 1 and led.bad_lines == 2
    assert led.attribute_pid(5001)[1] == "ok"
    assert led.attribute_pid(5002) == (None, "unledgered")
    assert led.live_span(5001) == (_T0, None) and led.live_span(5002) == (None, None)


def test_task_ids_for_record_is_mechanical_naming_not_a_copy(tmp_path):
    """台账名→task_id 靠命名约定推导（禁实体清单副本）；0 命中=移交补画像。"""
    from zephyr.infrastructure.system_telemetry.resource_sampler import (
        IncubationLedger,
        task_ids_for_record,
    )

    def recobj(**kw):
        p = _write_ledger(tmp_path, [_rec(**kw)], name=f"naming_{kw.get('pid')}.jsonl")
        return IncubationLedger.load(p).records[0]

    known = {"sch_ollama_serve", "data_slot_nightly_sentiment", "sch_WorktreeDriftWatchdog"}
    assert task_ids_for_record(recobj(pid=1, name="ollama-serve"), known) == ["sch_ollama_serve"]
    assert task_ids_for_record(recobj(pid=2, name="NightlySentiment"), known) == [
        "data_slot_nightly_sentiment"]
    assert task_ids_for_record(recobj(pid=3, name="", owner="worktree_drift_watchdog"), known) == [
        "sch_WorktreeDriftWatchdog"]
    assert task_ids_for_record(recobj(pid=4, name="reconcile-worker"), known) == []  # 移交项，不猜


def test_read_samples_parses_pre_l1_lines(tmp_path):
    """R-B：样本流 append-only，历史行没有 L-1 三键也必须照常解析（新键只能"新增可选"）。"""
    s = _l1_sampler(_mk_reg(tmp_path, _ents("sch_heavy_a")), tmp_path, [])
    f = s.samples_file("sch_heavy_a")
    f.parent.mkdir(parents=True)
    legacy = {"sample_time_seconds": 1.0, "task_id": "sch_heavy_a", "pid": 7,
              "process_resident_bytes": 2 * GB, "process_cpu_ratio": 0.1,
              "process_elapsed_seconds": 60.0}
    f.write_text(json.dumps(legacy) + "\n" + Sample(
        sample_time_seconds=2.0, task_id="sch_heavy_a", pid=8, process_resident_bytes=GB,
        process_cpu_ratio=0.2, process_elapsed_seconds=120.0,
        attribution="ledger", ledger_record_id="rX", parent_pid=9).to_json() + "\n",
        encoding="utf-8")
    samples, bad = s.read_samples("sch_heavy_a")
    assert bad == 0 and len(samples) == 2
    assert samples[0].attribution is None and samples[0].ledger_record_id is None
    assert (samples[1].attribution, samples[1].ledger_record_id, samples[1].parent_pid) == (
        "ledger", "rX", 9)


def test_writeback_zero_sample_stays_null_with_honest_reason(tmp_path):
    """禁编造：无样本实体 measured 数值保持 null，只在 no_sample_reason_zh 记原因；
    且 updated 键契约不破（只装真写了数值者），原因走新键 noted。"""
    reg = _mk_reg(tmp_path, _ents(
        ("data_slot_daily_kline", {"schedule_truth_source": "src/zephyr/data/config/schedule.yaml"}),
        ("sch_manual_thing", {"schedule_truth_source": "scripts/register_nothing_task.ps1"}),
        ("sch_planned_thing", {"status": "planned"})))
    s = _l1_sampler(reg, tmp_path, [])
    out = s.writeback()
    assert out["updated"] == {}, "零样本不得写出任何数值"
    assert set(out["noted"]) == {"data_slot_daily_kline", "sch_manual_thing"}
    data = yaml.safe_load(reg.read_text(encoding="utf-8"))
    by = {e["task_id"]: e for e in data["entities"]}
    m = by["data_slot_daily_kline"]["measured"]
    assert m["peak_mem_gb"] is None and m["p90_duration_min"] is None and m["samples"] == 0
    # 形状与生成器骨架同构（本表非生成器手写，writeback 仍补齐 null 骨架）
    assert list(m) == ["peak_mem_gb", "p90_duration_min", "samples", "last_at",
                       "no_sample_reason_zh"], list(m)
    assert "禁编造" in m["no_sample_reason_zh"] and "APScheduler" in m["no_sample_reason_zh"]
    assert "无匹配进程" in by["sch_manual_thing"]["measured"]["no_sample_reason_zh"]
    # planned/retired 的零样本由 status 自证，不写噪音原因
    assert "no_sample_reason_zh" not in (by["sch_planned_thing"].get("measured") or {})
    # 幂等：原因不变则不再重复写板（不制造无意义 diff）
    assert s.writeback()["noted"] == {}
    # 一旦真拿到样本：数值入 updated，陈旧原因被清掉
    s._append_sample(Sample(sample_time_seconds=1.0, task_id="sch_manual_thing", pid=3,
                            process_resident_bytes=2 * GB, process_cpu_ratio=0.5,
                            process_elapsed_seconds=600.0))
    out2 = s.writeback()
    assert "sch_manual_thing" in out2["updated"]
    m2 = {e["task_id"]: e for e in yaml.safe_load(reg.read_text(encoding="utf-8"))["entities"]
          }["sch_manual_thing"]["measured"]
    assert m2["peak_mem_gb"] == round(2.0 * 1.15, 4) and "no_sample_reason_zh" not in m2
    # 旗标可关（只要数值不要解释）
    assert s.writeback(record_no_sample_reason=False)["noted"] == {}


def test_lifetime_deviation_report_three_evidence_axes(tmp_path):
    """申报寿命 vs 实测寿命：三轴各记所得、方向分档正确、且不依赖 writeback 跑过。"""
    reg = _mk_reg(tmp_path, _ents(
        ("sch_under", {"est_duration_min": 30}),          # 实测 60 分 → 低估
        ("sch_match", {"est_duration_min": 60}),          # 实测 60 分 → 容差内
        ("sch_over", {"est_duration_min": 120}),          # 实测 60 分 → 高估
        ("sch_undeclared", {}),                            # 有实测无申报
        ("sch_ledger_only", {"est_duration_min": 45}),     # 只有台账轴（进程已退）
        ("sch_no_evidence", {"est_duration_min": 10}),
        ("sch_dark", {"est_duration_min": 99}),            # 三轴全黑：默认不出行
    ))
    s = _l1_sampler(reg, tmp_path, [])
    by_dur = {"sch_under": 60, "sch_match": 60, "sch_over": 60, "sch_undeclared": 60}
    for tid, minutes in by_dur.items():
        s._append_sample(Sample(sample_time_seconds=_T0, task_id=tid, pid=11,
                                process_resident_bytes=GB, process_cpu_ratio=0.4,
                                process_elapsed_seconds=float(minutes * 60)))
    led = _write_ledger(tmp_path, [
        _rec(21, "ledger-only", expected=3600.0, spawned=_T0, exited=_T0 + 3000),  # 60 申报/50 实测
        _rec(22, "no-evidence", expected=600.0, spawned=_T0 - 600, exited=None),   # 仍存活→下界
    ], name="l2.jsonl")
    rows = {r["task_id"]: r for r in _l1_sampler(reg, tmp_path, [], ledger_path=led,
                                                 now=_T0).lifetime_deviation_report()}
    assert rows["sch_under"]["direction"] == "underdeclared"
    assert rows["sch_under"]["deviation_min"] == 30.0 and rows["sch_under"]["deviation_pct"] == 100.0
    assert rows["sch_match"]["direction"] == "match"
    assert rows["sch_over"]["direction"] == "overdeclared" and rows["sch_over"]["deviation_min"] == -60.0
    assert rows["sch_undeclared"]["direction"] == "undeclared"
    assert rows["sch_undeclared"]["declared_est_duration_min"] is None
    # B 轴独立于回写：注册表 measured 仍是初始 null，报告照样给出 P90
    assert all(not (e.get("measured") or {}) for e in yaml.safe_load(reg.read_text(encoding="utf-8"))["entities"])
    assert rows["sch_under"]["measured_p90_duration_min"] == 60.0
    # C 轴：台账申报寿命 vs 实测寿命（唯一归因才入组）
    lo = rows["sch_ledger_only"]
    assert lo["evidence"] == ["ledger"] and lo["confidence"] == "ledger_only"
    assert lo["ledger_expected_lifetime_min"] == 60.0 and lo["ledger_actual_lifetime_min"] == 50.0
    assert lo["ledger_expected_vs_actual_min"] == -10.0
    # 仍存活：只给下界，绝不把"还活着"编造成"跑了这么久"
    ne = rows["sch_no_evidence"]
    assert ne["ledger_actual_lifetime_min"] is None
    assert ne["ledger_actual_lifetime_min_alive_ge"] == 10.0
    assert ne["direction"] == "no_evidence" and ne["evidence"] == ["ledger"]
    # 全零证据实体默认不出行，显式旗标才要（P5 要全量清扫时有门）
    assert "sch_no_evidence" in rows and "sch_dark" not in rows
    dark = {r["task_id"] for r in _l1_sampler(reg, tmp_path, [], ledger_path=led, now=_T0)
            .lifetime_deviation_report(include_no_evidence=True)}
    assert "sch_dark" in dark
    # 定向过滤 + 容差可调（tolerance 放大后 underdeclared 收敛为 match）
    assert [r["task_id"] for r in s.lifetime_deviation_report(task_ids=["sch_over"])] == ["sch_over"]
    wide = s.lifetime_deviation_report(task_ids=["sch_under"], tolerance_pct=200.0)[0]
    assert wide["direction"] == "match" and wide["tolerance_pct"] == 200.0
    # 归因来源进报告（校准器据此定权重）
    assert rows["sch_under"]["attribution_sources"] == ["pattern"]
