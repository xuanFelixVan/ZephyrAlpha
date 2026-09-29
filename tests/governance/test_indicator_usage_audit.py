# [BLUEPRINT] MOD-GOV-INDUSAGE | tests/governance/test_indicator_usage_audit.py
# [TTL] permanent
"""indicator_usage_audit 单测（W-R 三域落地）——tmp 合成仓库三态。"""

from __future__ import annotations

import pytest

from zephyr.governance.indicator_usage_audit import run_indicator_usage_audit


def test_usage_audit_three_states(tmp_path):
    # 登记册键名随真源演化：consumption_census 族①规格（单一真源）list_key="indicators"，
    # 旧别名 technical_indicators 已废（2026-09-29 SW14 薄壳化后 shim 委托 census，
    # fixture 必须镜像真源登记册现形态，否则普查族无实体 CensusInputError）。
    reg = tmp_path / "registry.yaml"
    reg.write_text(
        "indicators:\n"
        "  - indicator_id: IND-A\n    name: A\n"
        "  - indicator_id: IND-B\n    name: B\n"
        "  - indicator_id: IND-C\n    name: C\n",
        encoding="utf-8",
    )
    src = tmp_path / "src"
    src.mkdir()
    (src / "consumer.py").write_text("x = IND_A + IND_B\n", encoding="utf-8")
    r = run_indicator_usage_audit(
        registry_path=reg,
        scan_root=tmp_path,
        output_path=tmp_path / "led.json",
        today="D1",
    )
    assert r["counts"]["active"] == 2  # IND-A/IND-B 有消费者（下划线形式）
    assert r["counts"]["zero"] == 1  # IND-C 零消费
    doc = __import__("json").loads((tmp_path / "led.json").read_text(encoding="utf-8"))
    by_id = {e["indicator_id"]: e for e in doc["entries"]}
    assert by_id["IND-C"]["recommendation"].startswith("retire_candidate")
