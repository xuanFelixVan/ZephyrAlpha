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
        assert ent["pool"] == "light" and ent["resource_class"] == "light"
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
    codes = {gate_mod.REASON_OVERLAP, gate_mod.REASON_MEM, gate_mod.REASON_E0, gate_mod.REASON_DRIFT,
             gate_mod.REASON_GATE_ABSENT, gate_mod.REASON_VIEW_STALE}
    assert codes <= set(bridge._TITLES), codes - set(bridge._TITLES)


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
    assert "注册表与三真源漂移" in entries[0]["message"]


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
