# [A_test] module_id: MOD-RESCHED-PROFILE | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-RESCHED-PROFILE | docs/03_modules/_cross_layer/resource_profile_registry/blueprint.md | §
# [MODULE] tests.infrastructure.test_resource_schedule_regen_check
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] tests/infrastructure/test_resource_schedule_regen_check.py
# [TTL] task_bound
"""P0 排产自检臂测试：① L-2 再生排产化 ② C-5 闸缺席告警 ③ C-10 视图新鲜度。

纪律：注册表/视图/告警板一律 tmp_path 注入（测试禁写 data/ 与生产 .runtime 板；
main() 级用例经 ZEPHYR_OPS_NOTIFICATION_DIR 重定向——告警板路径单源，不开旗标）。
--check 幂等性（连跑两次零漂移）是排产化的前置条件，单独设测。
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
_GEN_PATH = REPO_ROOT / "scripts" / "governance" / "generators" / "generate_resource_profile_registry.py"
_VIEW_PATH = REPO_ROOT / "scripts" / "governance" / "generators" / "generate_resource_week_view.py"

_SPEC = importlib.util.spec_from_file_location("gen_resched_regen_test", _GEN_PATH)
gen = importlib.util.module_from_spec(_SPEC)
sys.modules.setdefault("gen_resched_regen_test", gen)
_SPEC.loader.exec_module(gen)


def _load_week_view():
    spec = importlib.util.spec_from_file_location("gen_resched_view_test", _VIEW_PATH)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["gen_resched_view_test"] = mod
    spec.loader.exec_module(mod)
    return mod


def _fresh_registry(path: Path) -> dict:
    """以生产三真源全量再生一份注册表写到指定路径（tmp 沙箱起点）。"""
    reg = gen.build_registry(existing_path=path, output_path=path)
    path.write_text(gen.registry_text(reg), encoding="utf-8")
    return reg


def _read_board(board: Path) -> list[dict]:
    f = board / "notifications.jsonl"
    if not f.exists():
        return []
    return [json.loads(x) for x in f.read_text(encoding="utf-8").splitlines() if x.strip()]


def _run_main(monkeypatch, *argv: str) -> int:
    monkeypatch.setattr(sys, "argv", [str(_GEN_PATH), *argv])
    return gen.main()


# ── ① L-2 再生排产化：幂等 + 漂移自愈 + 新任务自登记 ─────────────────────────
def test_check_is_idempotent_two_runs(tmp_path, monkeypatch, capsys):
    """连跑两次：第一次无漂移、第二次仍无漂移且再生不产生内容差异。"""
    out = tmp_path / "reg.yaml"
    _fresh_registry(out)
    before = out.read_bytes()
    assert _run_main(monkeypatch, "--check", "--output", str(out), "--existing", str(out)) == 0
    assert out.read_bytes() == before, "--check 必须只读"
    assert _run_main(monkeypatch, "--check", "--output", str(out), "--existing", str(out)) == 0
    assert out.read_bytes() == before
    # 全量再生两次：除 generated_at 时间戳外零差异（排产化前提=幂等）
    _run_main(monkeypatch, "--output", str(out))
    first = out.read_text(encoding="utf-8")
    _run_main(monkeypatch, "--output", str(out))
    second = out.read_text(encoding="utf-8")

    def strip_ts(text: str) -> list[str]:
        return [ln for ln in text.splitlines() if not ln.startswith("generated_at:")]

    assert strip_ts(first) == strip_ts(second), capsys.readouterr().out
    assert _run_main(monkeypatch, "--check", "--output", str(out), "--existing", str(out)) == 0


def test_auto_regen_repairs_tampered_window_expr(tmp_path, monkeypatch):
    """手改表（时间值漂移）→ --check 报 2；--auto-regen 就地跟上真源。"""
    out = tmp_path / "reg.yaml"
    reg = _fresh_registry(out)
    data = yaml.safe_load(out.read_text(encoding="utf-8"))
    tid = next(e["task_id"] for e in data["entities"] if e.get("window_expr"))
    truth = next(e["window_expr"] for e in reg["entities"] if e["task_id"] == tid)
    for e in data["entities"]:
        if e["task_id"] == tid:
            e["window_expr"] = "0 3 2 2 *"  # 手填假时间（window_expr 禁手填 = 制造漂移）
    out.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")
    assert _run_main(monkeypatch, "--check", "--output", str(out), "--existing", str(out)) == 2
    assert _run_main(monkeypatch, "--check", "--auto-regen", "--output", str(out), "--existing", str(out)) == 0
    fixed = yaml.safe_load(out.read_text(encoding="utf-8"))
    back = next(e["window_expr"] for e in fixed["entities"] if e["task_id"] == tid)
    assert back == truth, "再生必须把时间值抄回真源，而不是保留手填值"


def test_human_and_measured_fields_survive_auto_regen(tmp_path, monkeypatch):
    """再生的合并保全纪律：人复核字段与采样器字段不被排产轮次冲掉。"""
    out = tmp_path / "reg.yaml"
    _fresh_registry(out)
    data = yaml.safe_load(out.read_text(encoding="utf-8"))
    target = data["entities"][0]
    target["module_id"] = "MOD-TEST-KEEP"
    target["peak_mem_gb"] = 7.5
    target["measured"] = {"peak_mem_gb": 6.9, "p90_duration_min": 41, "samples": 9, "last_at": "x"}
    target["window_expr"] = "0 9 3 3 *"  # 同时制造漂移，逼 --auto-regen 落盘
    out.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")
    assert _run_main(monkeypatch, "--check", "--auto-regen", "--output", str(out), "--existing", str(out)) == 0
    after = yaml.safe_load(out.read_text(encoding="utf-8"))
    kept = next(e for e in after["entities"] if e["task_id"] == target["task_id"])
    assert kept["module_id"] == "MOD-TEST-KEEP" and kept["peak_mem_gb"] == 7.5
    assert kept["measured"]["samples"] == 9 and kept["measured"]["p90_duration_min"] == 41


def test_measured_no_sample_reason_survives_regen_roundtrip(tmp_path, monkeypatch):
    """合并保全公理延伸到 L-1 子键：`measured.no_sample_reason_zh` 也是采样器的私有财产。

    丢数值=丢实测，丢原因=丢"为什么是 null"的解释——读表人只剩一堆 null 无从分辨
    "还没跑过"与"永远取不到"，那是禁编造纪律的配套件，不得只活过一次 writeback。
    """
    out = tmp_path / "reg.yaml"
    _fresh_registry(out)
    data = yaml.safe_load(out.read_text(encoding="utf-8"))
    target = data["entities"][1]
    reason = ("无槽位级 pid：schedule.yaml 槽位跑在 DataScheduler 单进程内（APScheduler 线程），"
              "L-1 台账 join 亦未给出该槽位记录，故 measured 留 null（禁编造）")
    target["measured"] = {"peak_mem_gb": None, "p90_duration_min": None, "samples": 0,
                          "last_at": None, "no_sample_reason_zh": reason}
    target["window_expr"] = "0 9 3 3 *"  # 制造漂移，逼 --auto-regen 真的落盘
    out.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")
    assert _run_main(monkeypatch, "--check", "--auto-regen", "--output", str(out),
                     "--existing", str(out)) == 0
    after = yaml.safe_load(out.read_text(encoding="utf-8"))
    kept = next(e for e in after["entities"] if e["task_id"] == target["task_id"])
    assert kept["measured"]["no_sample_reason_zh"] == reason, "零样本原因被再生冲掉"
    assert kept["measured"]["peak_mem_gb"] is None and kept["measured"]["samples"] == 0
    # 骨架侧同步钉（[MODIFY-GUARD] 双向）：生成器必须声明同一子键，否则新建实体永远
    # 没有这一格，实测段形状由采样器单方面漂移。
    assert set(gen._base_entity("sch_newborn", "新生儿")["measured"]) == {
        "peak_mem_gb", "p90_duration_min", "samples", "last_at", "no_sample_reason_zh"}


def test_regen_tasks_materialize_as_active_entities():
    """吃自己狗粮：两个新 register_*.ps1 经 ps1 真源源自动物化为 active 实体。"""
    ents, warns = gen.parse_ps1_entities()
    by = {e["task_id"]: e for e in ents}
    assert not warns, warns
    for tid, ps1 in (
        ("sch_resource_regen_check", "scripts/register_resource_regen_check_task.ps1"),
        ("sch_resource_view_publish", "scripts/register_resource_view_publish_task.ps1"),
    ):
        assert (REPO_ROOT / ps1).exists(), f"计划任务真源缺失 {ps1}"
        ent = by[tid]
        assert ent["status"] == "active"
        assert ent["schedule_truth_source"] == ps1
        assert ent["resource_class"] == "light"
        # C-7/R-C（2026-09-17 P1-a）：历史上这两个任务挂着幽灵池 light（执行器字典里
        # 根本没有这条泳道）→ 已改挂真实泳道 default（8 线程通用池=无争抢档）。
        assert ent["pool"] == "default"
        assert ent["pool"] in gen.pool_vocabulary()[0]
    # 日视图任务有可抽 cron（时间值来自真源，非手填）；小时任务=PS5.1 后置补
    # Repetition，静态文本无 cron → event（与 ResourceSamplerScan 同型先例）
    assert by["sch_resource_view_publish"]["window_type"] == "cron"
    assert by["sch_resource_view_publish"]["window_expr"] == "50 5 * * *"
    assert by["sch_resource_regen_check"]["window_type"] == "event"
    assert by["sch_resource_regen_check"]["window_expr"] is None


# ── ② C-5 闸缺席告警（原先整条链静默）───────────────────────────────────────
def test_gate_availability_healthy_in_this_repo():
    assert gen.check_gate_availability() == []


def test_gate_absent_when_module_files_missing(tmp_path):
    problems = gen.check_gate_availability(repo_root=tmp_path)
    assert any(p.startswith("e0_module_missing") for p in problems)
    assert any(p.startswith("gate_module_missing") for p in problems)


def _sandbox_root(tmp_path, *, gate_id="RESOURCE-SCHEDULE", enabled=True) -> Path:
    """造一个只含排产链三件的假仓根（闸/E0 文件在场 + 可控注册目录）。"""
    (tmp_path / gen.GATE_MODULE_RELPATH.rsplit("/", 1)[0]).mkdir(parents=True, exist_ok=True)
    (tmp_path / gen.E0_MODULE_RELPATH.rsplit("/", 1)[0]).mkdir(parents=True, exist_ok=True)
    (tmp_path / gen.GATE_MODULE_RELPATH).write_text("# gate\n", encoding="utf-8")
    (tmp_path / gen.E0_MODULE_RELPATH).write_text("# e0\n", encoding="utf-8")
    (tmp_path / gen.GATE_REGISTRATION_RELPATH).parent.mkdir(parents=True, exist_ok=True)
    entries = [] if gate_id is None else [{"gate_id": gate_id, "enabled": enabled,
                                          "module_path": "zephyr.gov_enforcement.commit_gates.resource_schedule_gate",
                                          "factory_function": "make_resource_schedule_gate"}]
    (tmp_path / gen.GATE_REGISTRATION_RELPATH).write_text(
        yaml.safe_dump({"gates": entries}, allow_unicode=True), encoding="utf-8"
    )
    return tmp_path


def test_gate_absent_when_unregistered(tmp_path):
    root = _sandbox_root(tmp_path, gate_id=None)
    problems = gen.check_gate_availability(repo_root=root)
    assert len(problems) == 1 and problems[0].startswith("gate_unregistered")


def test_gate_absent_when_registered_but_disabled(tmp_path):
    root = _sandbox_root(tmp_path, enabled=False)
    problems = gen.check_gate_availability(repo_root=root)
    assert len(problems) == 1 and problems[0].startswith("gate_disabled")


def test_gate_absent_when_import_broken(tmp_path):
    root = _sandbox_root(tmp_path)
    p = root / gen.GATE_REGISTRATION_RELPATH
    data = yaml.safe_load(p.read_text(encoding="utf-8"))
    data["gates"][0]["module_path"] = "zephyr.no_such_gate_module_at_all"
    p.write_text(yaml.safe_dump(data, allow_unicode=True), encoding="utf-8")
    problems = gen.check_gate_availability(repo_root=root)
    assert any(x.startswith("gate_import_failed") for x in problems), problems


def test_gate_absent_finding_is_block_and_lands_on_board(tmp_path):
    """C-5 的终态：闸缺席 → block finding → 告警板 critical 条目（不再静默）。"""
    findings = gen.collect_check_findings([], ["gate_module_missing: x"], [])
    assert len(findings) == 1
    f = findings[0]
    assert f.reason_code == gen.REASON_GATE_ABSENT and f.severity == "block"
    board = tmp_path / "ops_board"
    r = gen.publish_check_findings(findings, board_dir=board)
    assert r["active_keys"] == ["sched_gate_absent:<schedule_chain>"]
    entries = _read_board(board)
    assert entries[0]["severity"] == "critical"
    assert entries[0]["module_id"] == gen.REGEN_PUBLISHER_MODULE_ID
    assert "排班闸缺席" in entries[0]["title"]


def test_findings_do_not_depend_on_gate_import(tmp_path):
    """红蓝：闸缺席时取不到闸的 Finding 也必须能报警（告警链不得自我依赖）。

    自检臂产的是 duck-typed SimpleNamespace（告警桥只 getattr 取值），故闸不在场
    时报警路径完整——这里连 import 都不做，直接断言产物类型与落板结果。
    """
    findings = gen.collect_check_findings(["tid.window_expr: a b"], [], ["view_stale: x"])
    assert all(type(f).__name__ == "SimpleNamespace" for f in findings)
    board = tmp_path / "b"
    r = gen.publish_check_findings(findings, board_dir=board)
    keys = {e["key"] for e in _read_board(board)}
    assert keys == {"sched_view_stale:<resource_week_view>", "sched_truth_drift:<registry>"}
    assert r["active_keys"] and all(e["resolved_at"] is None for e in _read_board(tmp_path / "b"))


# ── ③ C-10 视图新鲜度 ────────────────────────────────────────────────────────
def test_view_freshness_ok_when_sha_matches(tmp_path):
    reg = tmp_path / "reg.yaml"
    _fresh_registry_small(reg)
    sha = gen.registry_content_sha(reg)
    view = tmp_path / "rw-data.js"
    view.write_text(f"window.RW_VIEW_DATA = {{\"registry_sha256\": \"{sha}\"}};\n", encoding="utf-8")
    assert gen.check_view_freshness(view, reg) == []


def test_view_freshness_detects_stale_sha(tmp_path):
    reg = tmp_path / "reg.yaml"
    _fresh_registry_small(reg)
    view = tmp_path / "rw-data.js"
    view.write_text('window.RW_VIEW_DATA = {"registry_sha256": "000000000000"};\n', encoding="utf-8")
    problems = gen.check_view_freshness(view, reg)
    assert len(problems) == 1 and problems[0].startswith("view_stale:")


def test_view_missing_or_shafield_absent_counts_as_stale(tmp_path):
    reg = tmp_path / "reg.yaml"
    _fresh_registry_small(reg)
    assert gen.check_view_freshness(tmp_path / "nope.js", reg)[0].startswith("view_missing")
    empty = tmp_path / "rw-empty.js"
    empty.write_text("window.RW_VIEW_DATA = {};\n", encoding="utf-8")
    assert gen.check_view_freshness(empty, reg)[0].startswith("view_no_registry_sha256_field")


def _fresh_registry_small(path: Path) -> None:
    """小而全的假注册表（含视图/闸消费所需头部，避免测试背上生产 74 实体）。"""
    payload = {
        "schema_version": "1.0.0", "ttl": "permanent", "status": "active",
        "total_entities": 1, "field_count": 18, "mem_ceiling_gb": 10.0, "groups": {"g1": "测试组"},
        "entities": [gen._base_entity("t_small", "测试实体") | {
            "window_type": "cron", "window_expr": "0 4 * * *", "est_duration_min": 10,
            "peak_mem_gb": 1.0, "status": "active",
        }],
    }
    path.write_text(gen.registry_text(payload), encoding="utf-8")


def test_freshness_sha_recipe_matches_view_writer(tmp_path):
    """口径锁死：视图写侧内嵌指纹 == 自检读侧算法（改一处必须改两处）。"""
    vw = _load_week_view()
    from datetime import datetime, timezone

    reg = tmp_path / "reg.yaml"
    _fresh_registry_small(reg)
    view = vw.build_view_data(reg, datetime(2026, 9, 17, 4, 0, tzinfo=timezone.utc))
    assert view["registry_sha256"] == gen.registry_content_sha(reg)
    # 且自检对该视图判新鲜（写→读闭环）
    js = tmp_path / "rw-data.js"
    js.write_text(vw.render_js(view), encoding="utf-8")
    assert gen.check_view_freshness(js, reg) == []


def test_freshness_sha_survives_line_ending_churn(tmp_path):
    """行尾翻转不是过期：git stash/checkout、编辑器另存会把整份 YAML 的
    CRLF↔LF 翻转，内容一字未改——归一化前这会被误判 sched_view_stale（实测踩过）。"""
    reg = tmp_path / "reg.yaml"
    _fresh_registry_small(reg)
    text = reg.read_text(encoding="utf-8")
    reg.write_bytes(text.replace("\r\n", "\n").encode("utf-8"))  # 强制 LF
    sha_lf = gen.registry_content_sha(reg)
    js = tmp_path / "rw-data.js"
    js.write_text(f'window.RW_VIEW_DATA = {{"registry_sha256": "{sha_lf}"}};\n', encoding="utf-8")
    assert gen.check_view_freshness(js, reg) == []

    reg.write_bytes(text.replace("\n", "\r\n").encode("utf-8"))  # 同一内容改 CRLF
    assert gen.registry_content_sha(reg) == sha_lf
    assert gen.check_view_freshness(js, reg) == []

    # 真内容变化仍须被抓到（归一化不得把指纹抹成常数）
    bumped = text.replace("total_entities: 1", "total_entities: 2")
    assert bumped != text
    reg.write_bytes(bumped.replace("\n", "\r\n").encode("utf-8"))
    assert gen.registry_content_sha(reg) != sha_lf
    assert gen.check_view_freshness(js, reg)[0].startswith("view_stale:")


# ── ④ 理由码三处同步 + ⑤ 多发布方划界 ───────────────────────────────────────
def test_reason_codes_synced_with_gate_and_alerts_bridge():
    """新增码必须与闸清单/告警桥标题三处同步（改码不同步=板上裸码）。"""
    from zephyr.gov_enforcement.commit_gates import resource_schedule_gate as gate_mod
    from zephyr.infrastructure.system_telemetry.alerts import resource_schedule_alerts as bridge

    assert gen.REASON_GATE_ABSENT == gate_mod.REASON_GATE_ABSENT == "sched_gate_absent"
    assert gen.REASON_VIEW_STALE == gate_mod.REASON_VIEW_STALE == "sched_view_stale"
    assert gen.REASON_DRIFT == gate_mod.REASON_DRIFT == "sched_truth_drift"
    # P1-a 第二批（C-7/C-15）——生成器字面量与闸清单必须逐字相等
    for attr, code in (
        ("REASON_POOL_UNDECLARED", "sched_pool_undeclared"),
        ("REASON_TASK_DISABLED", "sched_task_disabled"),
        ("REASON_TASK_MISSING", "sched_task_missing"),
        ("REASON_TASK_ORPHAN", "sched_task_orphan"),
        ("REASON_TASK_PROBE", "sched_task_probe_unavailable"),
    ):
        assert getattr(gen, attr) == getattr(gate_mod, attr) == code
    codes = {gate_mod.REASON_OVERLAP, gate_mod.REASON_MEM, gate_mod.REASON_E0, gate_mod.REASON_DRIFT,
             gate_mod.REASON_GATE_ABSENT, gate_mod.REASON_VIEW_STALE, gate_mod.REASON_POOL_UNDECLARED,
             gate_mod.REASON_TASK_DISABLED, gate_mod.REASON_TASK_MISSING, gate_mod.REASON_TASK_ORPHAN,
             gate_mod.REASON_TASK_PROBE}
    assert len(codes) == 11
    assert codes <= set(bridge._TITLES), codes - set(bridge._TITLES)
    # 闸必须导出这些码（清单真源=闸；生成器/告警桥都从它取口径）——__all__ 记的是符号名
    missing = {attr for attr, _c in (
        ("REASON_OVERLAP", 0), ("REASON_MEM", 0), ("REASON_E0", 0), ("REASON_DRIFT", 0),
        ("REASON_GATE_ABSENT", 0), ("REASON_VIEW_STALE", 0), ("REASON_POOL_UNDECLARED", 0),
        ("REASON_TASK_DISABLED", 0), ("REASON_TASK_MISSING", 0), ("REASON_TASK_ORPHAN", 0),
        ("REASON_TASK_PROBE", 0)) if attr not in gate_mod.__all__}
    assert not missing, f"闸 __all__ 未导出理由码符号: {missing}"


# ── ⑥ C-7 池词表臂（v2 方案 C-7/裁定 R-C，2026-09-17 P1-a）──────────────────
def test_executor_vocabulary_measured_from_scheduler_source():
    """词表实测提取（禁硬编码）：真源=DataScheduler APScheduler 执行器字典。"""
    workers, problems = gen.extract_executor_vocabulary()
    assert problems == [], problems
    assert set(workers) >= {"default", "heavy", "realtime"}, workers
    assert workers["default"] >= 1 and workers["heavy"] >= 1
    # 审计侧空间维池（cpu/gpu）单独提取——它永不是排班泳道
    audit_ns, ap = gen.extract_audit_pool_namespace()
    assert ap == [] and {"cpu", "gpu"} <= audit_ns
    vocab, vp = gen.pool_vocabulary()
    assert vp == [] and vocab == set(workers)
    assert not (vocab & audit_ns), "两套词表不得重叠（C-6 同名认知风险）"


def test_extract_executor_vocabulary_degrades_without_crashing(tmp_path):
    """真源读不动=返回问题清单而非抛崩（自检臂必须在最脏的环境里也能跑）。"""
    workers, problems = gen.extract_executor_vocabulary(tmp_path / "nope.py")
    assert workers == {} and any("executor_source_unreadable" in p for p in problems)
    bad = tmp_path / "scheduler.py"
    bad.write_text("x = 1\n", encoding="utf-8")
    workers2, problems2 = gen.extract_executor_vocabulary(bad)
    assert workers2 == {} and any("executor_source_no_match" in p for p in problems2)
    # 降级时词表用兜底值继续工作（不阻断再生），且必发健康码
    v, p = gen.pool_vocabulary()
    assert set(gen.FALLBACK_POOL_VOCAB) <= v and p == []


def test_derive_pool_rules_pass_through_unknown_values():
    """派生规则：声明→executor→类映射→兜底；未知值**不洗**（洗了词表校验就抓不到）。"""
    assert gen.derive_pool("cpu_heavy") == "heavy"
    assert gen.derive_pool("light") == "default"
    assert gen.derive_pool("network_download") == "default"
    assert gen.derive_pool("light", executor="intraday_minute") == "intraday_minute"
    assert gen.derive_pool("light", declared="heavy") == "heavy"
    assert gen.derive_pool("light", declared="light") == "light"  # 幽灵池原样透传给校验臂
    assert gen.derive_pool("light", executor="does_not_exist") == "does_not_exist"


def test_check_pool_vocabulary_flags_ghost_and_audit_pools():
    """幽灵池/串维度池 → severity=block finding；真实泳道零告警。"""
    ents = [
        {"task_id": "ghost_one", "pool": "light", "resource_class": "light"},
        {"task_id": "audit_cross", "pool": "gpu", "resource_class": "gpu"},
        {"task_id": "ok_default", "pool": "default", "resource_class": "light"},
        {"task_id": "ok_realtime", "pool": "realtime", "resource_class": "light"},
    ]
    findings = gen.check_pool_vocabulary(ents)
    by = {t: f for f in findings for t in f["task_ids"]}
    assert set(by) == {"ghost_one", "audit_cross"}
    assert all(f["severity"] == "block" for f in findings)
    assert all(f["reason_code"] == gen.REASON_POOL_UNDECLARED for f in findings)
    assert "daily_crypto" in by["ghost_one"]["detail"]           # 事故自证必须出现在报警里
    assert "空间维" in by["audit_cross"]["detail"]                 # C-6 串维度另有说法
    assert gen.check_pool_vocabulary(ents[2:]) == []


def test_merge_preserve_discards_ghost_pool_only():
    """合并保全的唯一例外：磁盘幽灵池回落派生值，其余人填字段/measured 双轨照旧保全。"""
    fresh = [gen._base_entity("sch_demo", "生成值") | {"pool": "default", "resource_class": "light"}]
    old = [gen._base_entity("sch_demo", "生成值") | {
        "pool": "light", "peak_mem_gb": 7.5, "est_duration_min": 42, "status": "active",
        "notes_zh": "人复核备注", "module_id": "MOD-X",
        "measured": {"peak_mem_gb": 6.9, "p90_duration_min": 41, "samples": 9, "last_at": "x"},
    }]
    merged, warns = gen.merge_preserve(fresh, old)
    assert len(merged) == 1
    ent = merged[0]
    assert ent["pool"] == "default", "幽灵池不得永生"
    assert any(w.startswith("ghost_pool_discarded: sch_demo") for w in warns), warns  # 留痕
    # 其余人复核字段与 measured 双轨一字不动（v1 公理不破）
    assert ent["peak_mem_gb"] == 7.5 and ent["est_duration_min"] == 42
    assert ent["status"] == "active" and ent["notes_zh"] == "人复核备注" and ent["module_id"] == "MOD-X"
    assert ent["measured"]["samples"] == 9 and ent["measured"]["p90_duration_min"] == 41
    # 合法池的人复核值仍优先（例外只针对违规值）
    m2, w2 = gen.merge_preserve(fresh, [dict(old[0], pool="heavy")])
    assert m2[0]["pool"] == "heavy" and not [w for w in w2 if w.startswith("ghost_pool")]


def test_pool_guard_blocks_writing_unknown_pool(tmp_path, monkeypatch):
    """写盘前置守卫：未知池实体一律拒写（宁可留漂移），退出码 2、文件不落。"""
    out = tmp_path / "reg.yaml"
    monkeypatch.setitem(gen.PS1_TASK_OVERRIDES, "ResourceViewPublish",
                        dict(gen.PS1_TASK_OVERRIDES["ResourceViewPublish"], pool="light"))
    rc = _run_main(monkeypatch, "--output", str(out))
    assert rc == 2, "词表守卫必须阻断写出并留非零码"
    assert not out.exists(), "阻断=真不写，不能先写再报"
    assert _run_main(monkeypatch, "--check", "--auto-regen", "--output", str(out),
                     "--existing", str(out)) == 2  # 磁盘无表→漂移→再生同样被守卫挡住


def test_regenerated_production_registry_has_zero_ghost_pool():
    """P1-a 验收硬判据：以现盘为合并基再生一次，light/未知池归零且实体数不变。"""
    disk = yaml.safe_load(gen.DEFAULT_OUTPUT.read_text(encoding="utf-8")) or {}
    disk_ents = list(disk.get("entities") or [])
    reg = gen.build_registry(existing_path=gen.DEFAULT_OUTPUT, output_path=gen.DEFAULT_OUTPUT)
    ents = list(reg["entities"])
    vocab, problems = gen.pool_vocabulary()
    assert problems == [], problems
    assert len(ents) == len(disk_ents), "词表治理不得增删实体（条目数变化须另有解释）"
    assert all(str(e.get("pool")) in vocab for e in ents), "仍有实体挂在词表外"
    # 现盘同样零幽灵池：这是**长效回归钉**而非迁移期快照——若它再变红，说明 P1-a
    # 治理被回退（或有人手改表把实体挂回词表外的车道），而不是"还没修"。
    # 幽灵机制本身非空转由 test_merge_preserve_discards_ghost_pool 钉住。
    ghosts_on_disk = [str(e.get("task_id")) for e in disk_ents
                      if str(e.get("pool")) not in vocab]
    assert ghosts_on_disk == [], f"现盘重新出现幽灵池（P1-a 治理被回退？）：{ghosts_on_disk}"
    assert reg["pool_vocabulary"]["lanes"] == sorted(vocab)
    assert gen.check_pool_vocabulary(ents) == []
    # measured 双轨（R-B）在治理过程中不受影响
    kept = {str(e["task_id"]): e for e in ents}
    for e in disk_ents:
        tid = str(e.get("task_id"))
        if (e.get("measured") or {}).get("samples") and tid in kept:
            assert kept[tid]["measured"] == e["measured"], f"{tid} measured 被词表治理冲掉"


# ── ⑦ C-15 计划任务实测对账臂（v2 方案 C-15，2026-09-17 P1-a）────────────────
_SCH_FIXTURE = (
    '"TaskName","Next Run Time","Status"\n'
    r'"\ZephyrAlpha_Foo","2026/9/17 4:06:30","Ready"' + "\n"
    r'"\ZephyrAlpha_Bar","N/A","Disabled"' + "\n"
    '"TaskName","Next Run Time","Status"\n'  # 每目录块重印表头——必须按内容跳
    r'"\ZephyrAlpha_Baz","-","已禁用"' + "\n"  # 中文系统语言
    r'"\Alien","2026/9/17 4:06:30","Ready"' + "\n"  # 非本项目任务
    r'"\ZephyrAlpha_Short"' + "\n"                   # 列数不足
    r'"\ZephyrAlpha_Run","-","Running"' + "\n"
    # C4Exam 由 register_c4_exam_task.ps1 真实声明为 active → 实测 Disabled = 纸面班次
    r'"\ZephyrAlpha_C4Exam","N/A","Disabled"' + "\n"
    # NightlySentiment=豁免表在册孤儿残余（现役真源=schedule.yaml）→ 差集转 EXEMPT 留痕行
    r'"\ZephyrAlpha_NightlySentiment","N/A","Disabled"' + "\n"
)


def test_parse_schtasks_csv_normalizes_real_shape():
    live, problems = gen.parse_schtasks_csv(_SCH_FIXTURE)
    assert any("short_rows" in p for p in problems), problems
    assert live["ZephyrAlpha_Foo"] == ["Ready"] and live["ZephyrAlpha_Run"] == ["Running"]
    assert "ZephyrAlpha_Bar" in live and "Alien" in live           # 非本项目任务照收，判定在下游
    assert "ZephyrAlpha_Short" not in live                          # 列数不足不入表
    assert live["ZephyrAlpha_C4Exam"] == ["Disabled"]
    assert "TaskName" not in live                                   # 重复表头不当任务


def test_disabled_detection_covers_en_and_zh():
    live, _ = gen.parse_schtasks_csv(_SCH_FIXTURE)
    assert gen._RE_DISABLED_TOKEN.search(live["ZephyrAlpha_Bar"][0])
    assert gen._RE_DISABLED_TOKEN.search(live["ZephyrAlpha_Baz"][0])
    assert not gen._RE_DISABLED_TOKEN.search(live["ZephyrAlpha_Foo"][0])
    assert not gen._RE_DISABLED_TOKEN.search(live["ZephyrAlpha_Run"][0])


def _ents(tids: tuple[str, ...] | None = None, *, retired: tuple[str, ...] = ()) -> list[dict]:
    base = tids if tids is not None else ("sch_foo", "sch_bar", "sch_gone", "sch_retired", "sch_planned")
    out = []
    for tid in base:
        e = gen._base_entity(tid, tid)
        e["status"] = "retired" if tid in retired else ("planned" if tid.endswith("planned") else "active")
        out.append(e)
    return out


def test_reconcile_sched_tasks_three_diff_sets():
    """三类差集各自落码：Disabled/有源无任务/系统里有而表里没有。"""
    live = {
        "ZephyrAlpha_Foo": ["Ready"], "ZephyrAlpha_Bar": ["Disabled"],
        "ZephyrAlpha_Unknown": ["Ready"], "ZephyrAlpha_Retired": ["Ready"],
        "Alien": ["Ready"],
    }
    claims = {
        "ZephyrAlpha_Foo": "sch_foo", "ZephyrAlpha_Bar": "sch_bar",
        "ZephyrAlpha_Gone": "sch_gone", "ZephyrAlpha_Retired": "sch_retired",
        "ZephyrAlpha_Planned": "sch_planned",
    }
    findings, exempted = gen.reconcile_sched_tasks(_ents(retired=("sch_retired",)), live,
                                                   claims=claims, aliases={}, exemptions={})
    assert exempted == []
    by_code: dict[str, list[str]] = {}
    for f in findings:
        by_code.setdefault(f["reason_code"], []).append(f["task_ids"][0])
    assert by_code[gen.REASON_TASK_DISABLED] == ["sch_bar"]
    assert by_code[gen.REASON_TASK_MISSING] == ["sch_gone"]
    # 孤儿两类：完全不认识的报系统任务名；注册表认得但已退役却仍在跑的报 task_id
    assert set(by_code[gen.REASON_TASK_ORPHAN]) == {"ZephyrAlpha_Unknown", "sch_retired"}
    assert all(f["severity"] == "warn" for f in findings)  # 实测差集不阻断再生（改表改不动系统）


def test_reconcile_consistency_cases_stay_silent():
    """一致态零告警：active+Ready、retired+Disabled（实测先例 TradingWatchdog）、
    planned+在册（ops_* 直注册补录批）、非本项目任务不参与。"""
    live = {"ZephyrAlpha_Foo": ["Ready"], "ZephyrAlpha_Retired": ["Disabled"],
            "ZephyrAlpha_Planned": ["Ready"], "Alien": ["Ready"]}
    claims = {"ZephyrAlpha_Foo": "sch_foo", "ZephyrAlpha_Retired": "sch_retired",
              "ZephyrAlpha_Planned": "sch_planned"}
    findings, exempted = gen.reconcile_sched_tasks(
        _ents(("sch_foo", "sch_retired", "sch_planned"), retired=("sch_retired",)), live,
        claims=claims, aliases={}, exemptions={})
    assert findings == [] and exempted == []


def test_reconcile_aliases_and_exemptions_ledger():
    """别名收编=不是孤儿；豁免=不落码但必须留痕（豁免表是留痕机制不是静默开关）。"""
    live = {"ZephyrAlpha_Foo": ["Ready"], "ZephyrAlpha_Dash-Task": ["Ready"]}
    findings, exempted = gen.reconcile_sched_tasks(
        _ents(), live, claims={"ZephyrAlpha_Foo": "sch_foo"},
        aliases={"ZephyrAlpha_Dash-Task": "sch_planned"}, exemptions={})
    assert findings == [] and exempted == []
    # 同一差集挂豁免表 → 变留痕不变告警（孤儿任务本身仍归集在豁免项里）
    ex = {"ZephyrAlpha_Unknown": {"reason_code": gen.REASON_TASK_ORPHAN, "reason_zh": "已登记待裁"}}
    f2, e2 = gen.reconcile_sched_tasks(_ents(), {"ZephyrAlpha_Unknown": ["Ready"],
                                                 "ZephyrAlpha_New": ["Ready"]},
                                       claims={}, aliases={}, exemptions=ex)
    assert [x["task_name"] for x in e2] == ["ZephyrAlpha_Unknown"] and e2[0]["reason_zh"]
    assert [f["task_ids"] for f in f2] == [["ZephyrAlpha_New"]]


def test_reconcile_reports_real_machine_diffs():
    """生产实表对账（只读）：现盘 ZephyrAlpha_* 任务的差集必须逐项有交代——
    要么出 finding，要么进豁免表（不允许"既不报警也不留痕"的静默黑洞）。"""
    live, problems = gen.query_schtasks()
    if not live:
        pytest.skip(f"本机 schtasks 探针不可用: {problems}")
    reg = gen.build_registry(existing_path=gen.DEFAULT_OUTPUT, output_path=gen.DEFAULT_OUTPUT)
    findings, exempted = gen.reconcile_sched_tasks(list(reg["entities"]), live)
    handled = {f["task_ids"][0] for f in findings} | {e["task_name"] for e in exempted}
    za = {n for n in live if n.startswith(gen.ZA_TASK_PREFIXES)}
    assert len(za) >= 30, f"实测任务数异常偏少（{len(za)}），探针可疑"
    claims = gen.collect_ps1_task_claims()
    for name in handled:  # 反向：报出来的每一项都得能落到真实对象上（不得凭空造差集）
        assert (name in live or name in claims or name in gen.OPS_TASK_ALIASES
                or name in {str(e["task_id"]) for e in reg["entities"]}), name
    # 已知实测差集（2026-09-17 P3 收尾批后）：4 个实验遗留 + NightlySentiment（OS 退役
    # 残余，现役真源=schedule.yaml）——删任务=Owner 门位，豁免留痕在册（豁免表是留痕
    # 机制，不是静默开关）。PatternMining/WeeklyRest 已销项：前者真挂上系统（每日
    # 09:01），后者收编为 ops_weekly_rest 实体+machine_blackout 组标。
    assert {"ZephyrAlpha_C4Exam_Full0916", "ZephyrAlpha_C4Exam_OneShot0915",
            "ZephyrAlpha_FactoryLaneC_Full0916", "ZephyrAlpha_FactoryLaneC_OneShot0915",
            "ZephyrAlpha_NightlySentiment"} <= {e["task_name"] for e in exempted}, exempted
    resolved = {"ZephyrAlpha_PatternMining", "ZephyrAlpha_WeeklyRest"}
    assert not (resolved & {e["task_name"] for e in exempted}), "销项项不得回潮豁免表"
    assert not (resolved & {f["task_ids"][0] for f in findings}), "销项项不得报差集"
    # 别名表不得指向不存在的实体（那会变成孤儿误报）
    by_tid = {str(e["task_id"]) for e in reg["entities"]}
    assert set(gen.OPS_TASK_ALIASES.values()) <= by_tid, "别名指向不存在的实体=孤儿误报"


def _point_default_output(monkeypatch, reg: Path, tmp_path: Path) -> Path:
    """把"生产注册表"身份临时指向沙箱表（C-15/C-10 的"只对生产负责"纪律需要它才触发）。"""
    monkeypatch.setattr(gen, "DEFAULT_OUTPUT", reg)
    view = tmp_path / "rw-data.js"
    view.write_text('window.RW_VIEW_DATA = {"registry_sha256": "%s"};\n'
                    % gen.registry_content_sha(reg), encoding="utf-8")
    monkeypatch.setattr(gen, "DEFAULT_VIEW", view)
    return view


def test_schtasks_probe_failure_degrades_loudly(tmp_path, monkeypatch, capsys):
    """探针读不动=sched_task_probe_unavailable（C-15 的意义是有人看门，看门人缺席必吭声）。"""
    def _boom(*a, **k):
        return {}, ["schtasks_probe_unavailable: 模拟无 powershell"]
    monkeypatch.setattr(gen, "query_schtasks", _boom)
    reg = tmp_path / "reg.yaml"
    _fresh_registry(reg)
    _point_default_output(monkeypatch, reg, tmp_path)
    assert _run_main(monkeypatch, "--check", "--output", str(reg), "--existing", str(reg)) == 3
    assert gen.REASON_TASK_PROBE in capsys.readouterr().out


def test_main_c15_arm_only_for_production_registry_and_exit_three(tmp_path, monkeypatch, capsys):
    """沙箱表不得拿本机任务表对账（同 C-10 纪律）；表=生产时差集必须报警且退出码 3。"""
    reg = tmp_path / "reg.yaml"
    _fresh_registry(reg)
    assert _run_main(monkeypatch, "--check", "--output", str(reg), "--existing", str(reg)) == 0
    fixture = tmp_path / "sch.csv"
    fixture.write_text(_SCH_FIXTURE, encoding="utf-8")
    _point_default_output(monkeypatch, reg, tmp_path)
    rc = _run_main(monkeypatch, "--check", "--schtasks-csv", str(fixture),
                   "--output", str(reg), "--existing", str(reg))
    assert rc == 3, "实测差集=健康码（不触发再生，故 3 不是 2）"
    out = capsys.readouterr().out
    assert gen.REASON_TASK_ORPHAN in out and gen.REASON_TASK_DISABLED in out
    assert gen.REASON_TASK_MISSING in out and "EXEMPT:" in out
    assert gen.REASON_TASK_PROBE in out  # 列数不足行 → 探针降级码也得上报（不静默）
    # --skip-schtasks 必须完全绕开本臂（离线/CI 通道）
    assert _run_main(monkeypatch, "--check", "--skip-schtasks",
                     "--output", str(reg), "--existing", str(reg)) == 0


def test_regen_publisher_does_not_erase_view_arm_alerts(tmp_path):
    """两个发布方共用一块板：解除联动按 module_id 划界，不得互删。"""
    from zephyr.infrastructure.system_telemetry.alerts.resource_schedule_alerts import publish_findings

    board = tmp_path / "board"
    findings = gen.collect_check_findings([], [], ["view_stale: x"])
    publish_findings(findings, board_dir=board, module_id=gen.REGEN_PUBLISHER_MODULE_ID)
    # 另一臂（闸/视图）跑一轮空 findings：不得解除再生臂的告警
    publish_findings([], board_dir=board, module_id="resource-schedule-gate")
    assert _read_board(board)[0]["resolved_at"] is None
    # 再生臂自己看到视图转新鲜（空 findings）→ 正常解除
    publish_findings([], board_dir=board, module_id=gen.REGEN_PUBLISHER_MODULE_ID)
    assert _read_board(board)[0]["resolved_at"] is not None


def test_empty_findings_still_reaches_bridge(tmp_path):
    """回归护栏：曾因空表提前 return 而使 stale 告警永不解除。"""
    board = tmp_path / "board"
    gen.publish_check_findings(gen.collect_check_findings([], [], ["view_stale: x"]), board_dir=board)
    r = gen.publish_check_findings([], board_dir=board)
    assert any(o.get("op") == "resolved" for o in r["ops"]), r
    assert _read_board(board)[0]["resolved_at"] is not None


# ── 全链（main 级，板经环境变量重定向，禁写生产 .runtime）────────────────────
def test_main_publish_alerts_lands_scheduling_entry_on_board(tmp_path, monkeypatch):
    """P0 验收硬判据的可测形态：自检→notifications.jsonl 出现排班条目。"""
    board = tmp_path / "ops_board"
    monkeypatch.setenv("ZEPHYR_OPS_NOTIFICATION_DIR", str(board))
    reg = tmp_path / "reg.yaml"
    data = _fresh_registry(reg)
    for e in data["entities"]:
        if e.get("window_expr"):
            e["window_expr"] = "0 3 2 2 *"
            break
    reg.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")
    assert _run_main(monkeypatch, "--check", "--publish-alerts", "--output", str(reg), "--existing", str(reg)) == 2
    entries = _read_board(board)
    assert entries and entries[0]["module_id"] == gen.REGEN_PUBLISHER_MODULE_ID
    assert entries[0]["key"] == "sched_truth_drift:<registry>"
    assert "注册表与四真源漂移" in entries[0]["message"]


def test_main_view_freshness_only_for_production_registry(tmp_path, monkeypatch, capsys):
    """临时注册表无视图：不得拿生产视图指纹去比 tmp 表（防自造噪音）。"""
    reg = tmp_path / "reg.yaml"
    _fresh_registry(reg)
    stale_view = tmp_path / "rw-data.js"
    stale_view.write_text('window.RW_VIEW_DATA = {"registry_sha256": "deadbeef0000"};\n', encoding="utf-8")
    assert _run_main(monkeypatch, "--check", "--view", str(stale_view),
                     "--output", str(reg), "--existing", str(reg)) == 0
    assert "sched_view_stale" not in capsys.readouterr().out
    # 生产注册表路径下同一视图必须报过期
    problems = gen.check_view_freshness(stale_view, gen.DEFAULT_OUTPUT)
    assert problems and problems[0].startswith("view_stale")


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(pytest.main([__file__, "-q"]))
