# [MODULE] tests.ai_layer.perceive.test_monthly_checkup
# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §ai_layer_perceive
# [DOMAIN] D_GOVERNANCE
# [TTL] permanent
"""施工项 8 验收机检面：建议书 schema 校验过/血肉骨架分流正确/checkups 落盘（md+json 双轨）。

生成器为 scripts 自包含件（importlib 装载）；全部落盘走 tmp_path；PG 走注入假连接（离线确定性）。
"""

from __future__ import annotations

import importlib.util
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import ModuleType

import pytest
import yaml

REPO = Path(__file__).resolve().parents[3]
GEN_SCRIPT = REPO / "scripts" / "ai_layer" / "gen_ai_layer_monthly_checkup.py"
FIXED_NOW: datetime = datetime(2026, 9, 23, 12, 0, 0, tzinfo=timezone.utc)


def _load_gen() -> ModuleType:
    spec = importlib.util.spec_from_file_location("gen_ai_layer_monthly_checkup_under_test", GEN_SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def _flesh(title: str = "配额减半汇报", **extra: object) -> dict:
    base = {
        "level": "flesh",
        "title": title,
        "evidence_ref": "V3 ai_intake_kpi_weekly 2026-W36",
        "ask": "按 KPI 规则对该源配额减半",
        "better_than": "贫矿源不再挤占总量闸 40 的漏斗预算",
        "labor_killed": "消灭 Owner 每月人工翻 KPI 表决定谁降级的整段人工",
    }
    base.update(extra)
    return base


def _skeleton(title: str = "L7 传承段提前立项") -> dict:
    return {
        "level": "skeleton",
        "title": title,
        "evidence_ref": "docs/_working/ai_layer_vision/L7_heredity/DESIGN.md",
        "ask": "传承段是否提前立项",
        "better_than": "经验回流闭环提前一季生效",
        "labor_killed": "消灭每代重踩同坑的人工复盘",
        "options": ["批准立项", "维持挂起", "转 OBJ_R 立案"],
    }


def _write_registry_fixture(path: Path) -> Path:
    path.write_text(
        yaml.safe_dump(
            {
                "schema_version": "1.0",
                "sources": [{
                    "slug": "test-src", "track": "github", "url": "https://example.com/x",
                    "fetch": "监视", "frequency": "weekly", "daily_quota": 5,
                    "health": "active", "last_verified": "2026-09-17", "basis": "测试桩",
                }],
                "longtail_candidates": [],
                "quota_governance": {"total_daily_cap": 40, "per_source_floor": 1, "demotion": {}},
            },
            allow_unicode=True,
        ),
        encoding="utf-8",
    )
    return path


def _broken_conn() -> object:
    class _Broken:
        def cursor(self):  # noqa: ANN001
            raise RuntimeError("pg down")

    return _Broken()


def test_proposal_schema_validation() -> None:
    gen = _load_gen()
    # 缺两问拒收
    bad = _flesh()
    del bad["labor_killed"]
    with pytest.raises(ValueError, match="labor_killed"):
        gen.validate_proposal(bad, 0)
    # 骨架缺 options 拒收（Owner 一键确认接口缺失）
    bad_skeleton = _skeleton()
    del bad_skeleton["options"]
    with pytest.raises(ValueError, match="options"):
        gen.validate_proposal(bad_skeleton, 0)
    # level 白名单
    with pytest.raises(ValueError, match="level"):
        gen.validate_proposal(_flesh(level="boss"), 0)
    gen.validate_proposal(_flesh(), 0)
    gen.validate_proposal(_skeleton(), 0)


def test_route_proposals_flesh_skeleton_split() -> None:
    """验收原文：血肉/骨架分流正确——flesh 可自动→只汇报；flesh 其余→派工；skeleton→Owner 门。"""
    gen = _load_gen()
    proposals = [
        _flesh("自动件", auto_executable=True),
        _flesh("派工件"),
        _skeleton("骨架件"),
    ]
    routing = gen.route_proposals(proposals)
    assert routing == {
        "flesh_report": ["自动件"],
        "flesh_dispatch": ["派工件"],
        "skeleton_owner": ["骨架件"],
    }


def test_detector_digest_window_and_bad_lines(tmp_path: Path) -> None:
    gen = _load_gen()
    events = tmp_path / "commit_block_events.jsonl"
    old_ts = (FIXED_NOW - timedelta(days=40)).isoformat()
    in_ts = (FIXED_NOW - timedelta(days=3)).isoformat()
    lines = [
        json.dumps({"timestamp": in_ts, "event": "commit_blocked", "gate_id": "SYNTAX-GATE"}),
        json.dumps({"timestamp": in_ts, "event": "commit_blocked", "gate_id": "SYNTAX-GATE"}),
        json.dumps({"timestamp": in_ts, "event": "commit_blocked", "gate_id": "OTHER-GATE"}),
        json.dumps({"timestamp": old_ts, "event": "commit_blocked", "gate_id": "SYNTAX-GATE"}),  # 窗外
        "{bad json",
    ]
    events.write_text("\n".join(lines) + "\n", encoding="utf-8")
    digest = gen.collect_detector_digest(events, injected={"e6_decay": {"failed": 2}}, now=FIXED_NOW)
    assert digest["commit_block_by_gate"] == {"SYNTAX-GATE": 2, "OTHER-GATE": 1}
    assert digest["commit_block_total"] == 3
    assert digest["bad_lines_skipped"] == 1
    assert digest["channels"]["e6_decay"] == {"failed": 2}
    assert digest["channels"]["sim_deviation"] is None  # 未注入=如实留空


def test_vein_coverage_reads_generator_artifact(tmp_path: Path) -> None:
    gen = _load_gen()
    veins = tmp_path / "veins.yaml"
    veins.write_text(
        yaml.safe_dump(
            {"veins": [
                {"vein_id": "A", "status": "active"},
                {"vein_id": "B", "status": "active"},
                {"vein_id": "C", "status": "archived"},
            ]},
            allow_unicode=True,
        ),
        encoding="utf-8",
    )
    coverage = gen.collect_vein_coverage(veins)
    assert coverage == {
        "total": 3, "active": 2, "archived": 1, "mined": None, "longtail": None,
        "note": coverage["note"],
    }
    assert coverage["mined"] is None  # v0 未跟踪如实留空
    missing = gen.collect_vein_coverage(tmp_path / "nope.yaml")
    assert "缺失" in missing["note"]


def test_build_report_and_write_outputs_dual_track(tmp_path: Path) -> None:
    """验收原文：建议书 schema 校验过 + checkups 落盘（md 人读轨+json 机读轨）。"""
    gen = _load_gen()
    report = gen.build_report(
        "2026-09",
        proposals=[_flesh("自动件", auto_executable=True), _skeleton()],
        kpi_summary={"quota_by_source": {"test-src": 5}},
        vein_coverage={"total": 27, "active": 27, "archived": 0},
        detector_digest=gen.collect_detector_digest(None, now=FIXED_NOW),
        generated_at=FIXED_NOW,
    )
    assert report["routing"]["skeleton_owner"] == ["L7 传承段提前立项"]
    md_path, json_path = gen.write_outputs(report, tmp_path)
    assert md_path.name == "2026-09.md" and json_path.name == "2026-09.json"
    md_text = md_path.read_text(encoding="utf-8")
    assert "AI 层骨架月度建议书 2026-09" in md_text
    assert "Owner 一键确认选项" in md_text
    assert "骨架级→Owner 门" in md_text
    reloaded = json.loads(json_path.read_text(encoding="utf-8"))
    assert reloaded["schema_version"] == "1.0"
    assert len(reloaded["proposals"]) == 2


def test_build_report_rejects_bad_period() -> None:
    gen = _load_gen()
    with pytest.raises(ValueError, match="period"):
        gen.build_report(
            "2026-13", proposals=[], kpi_summary=None, vein_coverage=None,
            detector_digest={}, generated_at=FIXED_NOW,
        )


def test_kpi_summary_fail_open_offline(tmp_path: Path) -> None:
    """数据诚实契约：PG 不可达（注入坏连接）→V3 段置 None+注记，体检不炸不虚构。"""
    gen = _load_gen()
    registry_path = _write_registry_fixture(tmp_path / "registry.yaml")
    from zephyr.ai_layer.perceive.search_orders import SearchOrderJournal

    kpi = gen.collect_kpi_summary(
        journal=SearchOrderJournal(tmp_path / "orders"),
        conn=_broken_conn(),
        registry_path=registry_path,
    )
    assert kpi["quota_by_source"] == {"test-src": 5}
    assert kpi["total_daily_cap"] == 40
    assert kpi["weekly_rows"] is None
    assert "如实留空" in kpi["note"]
    assert kpi["orders"] == {"orders_by_status": {}, "note": kpi["orders"]["note"]}


def test_kpi_summary_json_safe_real_pg_row(tmp_path: Path) -> None:
    """真实 V3 行含 datetime（2026-09-23 实证）→行值 JSON 化，落盘不炸。"""
    import decimal

    gen = _load_gen()
    registry_path = _write_registry_fixture(tmp_path / "registry.yaml")

    class _FakeCursor:
        def __enter__(self) -> "_FakeCursor":
            return self

        def __exit__(self, *exc: object) -> None:
            return None

        def execute(self, _sql: str) -> None:
            return None

        @property
        def description(self) -> list[tuple[str, ...]]:  # noqa: D102
            return [("week_start",), ("domain_id",), ("cards_total",), ("exam_pass_rate_pct",)]

        def fetchall(self) -> list[tuple]:
            return [
                (datetime(2026, 8, 31, 0, 0, tzinfo=timezone.utc), "governance", 12, decimal.Decimal("25.00")),
            ]

    class _FakeConn:
        def cursor(self) -> _FakeCursor:
            return _FakeCursor()

    from zephyr.ai_layer.perceive.search_orders import SearchOrderJournal

    kpi = gen.collect_kpi_summary(
        journal=SearchOrderJournal(tmp_path / "orders"),
        conn=_FakeConn(),
        registry_path=registry_path,
    )
    assert kpi["weekly_rows"] == [{
        "week_start": "2026-08-31T00:00:00+00:00",
        "domain_id": "governance",
        "cards_total": 12,
        "exam_pass_rate_pct": "25.00",
    }]
    json.dumps(kpi)  # 全量可序列化（write_outputs 同路径）
