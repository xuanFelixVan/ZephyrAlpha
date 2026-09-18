# [A_test] module_id: MOD-INF-001 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-001 | docs/03_modules/_domain_infrastructure_operations/capacity_assurance/blueprint.md | §tests
# [MODULE] tests.autonomy.test_system_watermark_gate
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.capacity_assurance.host_resource_governor
# [CONSUMERS] pytest
# [STARTUP] n/a
# [MATURITY] testing
# [INVARIANTS] 探针必须是实探（本文件的第一条断言就是打旧假通道的脸：硬编码 16000/12.5 复现即红）;
#   阈值只认 config/alert_rules.yaml，缺规则=不告警+loud warning（禁代码兜底阈值）;
#   测试禁写生产路径（板目录/规则文件全 tmp_path）
# [MODIFY-GUARD] none
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] self
# [TESTS] self
# [TTL] permanent
"""test_system_watermark_gate — 全系统内存/提交水位真闸（BRK-066）.

治的是"假通道"：旧 `HostResourceGovernor.probe()` 恒返
`ResourceStatus(total_ram_mb=16000, used=2000, usage_pct=12.5, degraded=False, "OK")`，
文档自称 psutil 实探而代码零调用——整机 RAM 可用掉到 17.6GB 时它仍报 OK。
本文件第一条断言就是**证伪那个硬编码**，因此它不是恒真断言。
"""

from __future__ import annotations

from pathlib import Path

import pytest

from zephyr.infrastructure.capacity_assurance.host_resource_governor import (
    METRIC_COMMIT_PCT,
    METRIC_MEM_AVAIL_GB,
    SystemWatermark,
    check_system_watermark,
    probe_system_watermark,
)

_RULES = """\
version: "test"
rules:
  - id: ALERT-SYS-003
    name: commit_charge_exhaustion
    severity: critical
    metric: system.commit_mem_pct
    condition: "> 90"
    description: 提交内存超 90%
    silence_window: "10m"
  - id: ALERT-SYS-004
    name: ram_available_low
    severity: critical
    metric: system.mem_avail_gb
    condition: "< 12"
    description: 可用内存不足
    silence_window: "10m"
"""


def _write_rules(tmp_path: Path, text: str = _RULES) -> Path:
    path = tmp_path / "alert_rules.yaml"
    path.write_text(text, encoding="utf-8")
    return path


def test_probe_is_real_not_the_hardcoded_stub() -> None:
    """实探：读数不得等于旧硬编码，且必须与本机 psutil 一致量级."""
    wm = probe_system_watermark()
    assert (wm.ram_total_gb, wm.ram_used_pct) != (16.0, 12.5), "假通道复现"
    assert wm.ram_total_gb > 1.0, f"RAM 实探失真: {wm}"
    assert wm.ram_avail_gb > 0.0
    assert 0.0 <= wm.ram_used_pct <= 100.0
    assert wm.cpu_pct >= 0.0


def test_commit_charge_surface_reported() -> None:
    """Windows 提交内存面必须有值（本机即 Windows；平台缺席时 note 必须说明，禁冒充）."""
    wm = probe_system_watermark()
    if wm.commit_pct is None:
        assert "commit" in wm.note, "commit 面缺席必须如实标注，不得静默"
    else:
        assert wm.commit_total_gb > wm.commit_used_gb >= 0.0
        assert METRIC_COMMIT_PCT in wm.metric_values()


def test_breach_publishes_to_board(tmp_path: Path) -> None:
    """⑤哨兵在岗 + ⑥失败会响：注入超限水位 → 命中规则 id 并发布通知板."""
    rules = _write_rules(tmp_path)
    board = tmp_path / "board"
    wm = SystemWatermark(
        ram_total_gb=64.0, ram_avail_gb=4.0, ram_used_pct=93.7,
        commit_total_gb=96.0, commit_used_gb=92.0, commit_pct=95.8, cpu_pct=50.0,
    )
    result = check_system_watermark(rules_path=rules, board_dir=board, watermark=wm)
    assert sorted(result["breached"]) == ["ALERT-SYS-003", "ALERT-SYS-004"]
    assert result["published"] == result["breached"]
    import json

    entries = (board / "notifications.jsonl").read_text(encoding="utf-8").strip().splitlines()
    keys = {json.loads(line)["key"] for line in entries}
    assert keys == {"ALERT-SYS-003", "ALERT-SYS-004"}
    messages = " ".join(json.loads(line)["message"] for line in entries)
    assert "95.8" in messages and "4.0" in messages, "告警必带实测数字，禁空喊"


def test_healthy_watermark_is_silent(tmp_path: Path) -> None:
    """未越线不得发布（防噪音）——把断言改成恒真就会在这里红."""
    rules = _write_rules(tmp_path)
    board = tmp_path / "board"
    wm = SystemWatermark(
        ram_total_gb=64.0, ram_avail_gb=40.0, ram_used_pct=37.0,
        commit_total_gb=96.0, commit_used_gb=30.0, commit_pct=31.0, cpu_pct=25.0,
    )
    result = check_system_watermark(rules_path=rules, board_dir=board, watermark=wm)
    assert result["breached"] == [] and result["published"] == []
    assert not (board / "notifications.jsonl").exists()


def test_missing_rules_never_invents_threshold(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    """规则缺席=不评估 + 必须 loud warning（禁代码兜底阈值把闸门悄悄造出来）."""
    rules = _write_rules(tmp_path, 'version: "t"\nrules: []\n')
    wm = SystemWatermark(
        ram_total_gb=64.0, ram_avail_gb=0.1, ram_used_pct=99.9,
        commit_total_gb=96.0, commit_used_gb=95.0, commit_pct=99.0, cpu_pct=99.0,
    )
    with caplog.at_level("WARNING"):
        result = check_system_watermark(rules_path=rules, board_dir=tmp_path / "b", watermark=wm)
    assert result["breached"] == []
    assert any("无 system.* 水位规则" in r.message for r in caplog.records)


def test_unreadable_rules_is_loud_error(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    """规则文件不可读 → 本周期不评估且出声（静默失明比误报更坏）."""
    wm = SystemWatermark(
        ram_total_gb=64.0, ram_avail_gb=1.0, ram_used_pct=99.0,
        commit_total_gb=96.0, commit_used_gb=95.0, commit_pct=99.0, cpu_pct=99.0,
    )
    with caplog.at_level("ERROR"):
        result = check_system_watermark(
            rules_path=tmp_path / "nope.yaml", board_dir=tmp_path / "b", watermark=wm
        )
    assert result["breached"] == []
    assert any("水位规则不可读" in r.message for r in caplog.records)


def test_mem_avail_metric_key_is_stable() -> None:
    """指标名是规则真源的连接键——改名即断链，故钉死."""
    assert METRIC_MEM_AVAIL_GB == "system.mem_avail_gb"
    prod = SystemWatermark(64, 8, 87.5, 96, 90, 93.7, 40).metric_values()
    assert set(prod) == {"system.mem_used_pct", "system.mem_avail_gb", "system.cpu_percent",
                         METRIC_COMMIT_PCT}
