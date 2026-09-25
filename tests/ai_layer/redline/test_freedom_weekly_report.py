# [A_test] module_id: zephyr.ai_layer.redline.freedom_weekly_report | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §obj_s_freedom_weekly_report
# [MODULE] tests.ai_layer.redline.test_freedom_weekly_report
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] pytest; zephyr.ai_layer.redline.freedom_weekly_report
# [CONSUMERS] pytest 自动发现
# [STARTUP] python -m pytest tests/ai_layer/redline/test_freedom_weekly_report.py
# [MATURITY] testing
# [INVARIANTS] 验收标准（DESIGN 红蓝 R1-F4）：样例周报含自由使用/擦边/配额三节；
#              输出落 tmp_path（零生产路径写）
# [MODIFY-GUARD] —
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即测试失败
# [TESTS] 本文件
# [TTL] permanent
"""test_freedom_weekly_report.py — S7 自由域透明度周报生成器单测。"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import yaml

from zephyr.ai_layer.redline.freedom_weekly_report import (
    OWNER_CALLS_KPI,
    WeeklyInput,
    build_report,
    collect_hits_by_rule,
    render_markdown,
    week_id_for,
    write_report,
)


def _sample_report() -> dict:
    return build_report(
        WeeklyInput(
            week_id="2026-W38",
            free_domain_usage=(
                {"capability": "自动补齐词典别名", "first_used": "2026-09-16", "runs": 12, "domain": "D_LIBRARY"},
            ),
            near_miss_events=(
                {"rule_id": "NL-5", "what": "只改任务书未带产物", "why_warn_not_block": "同批无施工产物", "count": 1},
            ),
            negative_list_hits=({"rule_id": "NL-2", "blocks": 3},),
            quota_consumption=({"resource": "llm_token", "used": 800, "quota": 1000, "pct": 0.8},),
            sev_incidents={"sev1": 0, "sev2": 0, "sev3": 1, "sev4": 0},
            owner_calls=2,
            degradation_events=1,
            next_week_proposals=("新增 ch 冷表自动巡检",),
        )
    )


def test_week_id_iso_format():
    assert week_id_for(datetime(2026, 9, 23, 12, 0, 0)).startswith("2026-W")
    parts = week_id_for(datetime(2026, 1, 1)).split("-W")
    assert len(parts[0]) == 4 and len(parts[1]) == 2


def test_sample_report_has_three_required_sections():
    report = _sample_report()
    assert report["free_domain_usage"], "自由使用节"
    assert report["near_miss_events"], "擦边节"
    assert report["quota_consumption"], "配额节"
    assert report["negative_list_hits"] == [{"rule_id": "NL-2", "blocks": 3}]
    assert report["sev_incidents"]["sev3"] == 1
    assert report["degradation_events"] == 1


def test_owner_calls_kpi_flag():
    report = _sample_report()
    assert report["owner_calls_kpi"]["breach"] is False
    over = build_report(
        WeeklyInput(week_id="2026-W38", owner_calls=OWNER_CALLS_KPI + 1, sev_incidents={})
    )
    assert over["owner_calls_kpi"]["breach"] is True, "越线只标记不拦（透明面非执法面）"


def test_markdown_renders_one_screen_sections():
    md = render_markdown(_sample_report())
    for section in ("自由域使用", "擦边事件", "配额消耗", "负面清单机检阻断", "下周新增自由提案"):
        assert section in md
    assert "2026-W38" in md


def test_write_report_dual_format(tmp_path: Path):
    yaml_path, md_path = write_report(_sample_report(), tmp_path / "reports")
    loaded = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    assert loaded["week_id"] == "2026-W38"
    assert md_path.read_text(encoding="utf-8").startswith("# 自由域透明度周报")


def test_collect_hits_by_rule_from_audit_jsonl(tmp_path: Path):
    audit = tmp_path / "gate_audit" / "real_key_reference_scan.jsonl"
    audit.parent.mkdir(parents=True)
    lines = [
        '{"timestamp": "t1", "rule_id": "NL-2", "action": "block"}',
        '{"timestamp": "t2", "rule_id": "NL-2", "action": "block"}',
        '{"timestamp": "t3", "rule_id": "NL-2", "action": "near_miss_warn"}',
        "not-json-garbage",
    ]
    audit.write_text("\n".join(lines) + "\n", encoding="utf-8")
    hits = collect_hits_by_rule([audit], action="block", count_key="blocks")
    assert hits == [{"rule_id": "NL-2", "blocks": 2}]
    warns = collect_hits_by_rule([audit], action="near_miss_warn", count_key="warns")
    assert warns == [{"rule_id": "NL-2", "warns": 1}]
    missing = collect_hits_by_rule([tmp_path / "nope.jsonl"])
    assert missing == [], "缺审计源 fail-open 计 0"
