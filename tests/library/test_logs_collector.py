# [A_test] module_id: MOD-LIB-004 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-LIB-004 | docs/03_modules/_domain_library/blueprint.md | §4
# [MODULE] tests.library.test_logs_collector
# [DOMAIN] D_GOVERNANCE
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-LIB-004 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_logs_collector.py — 日志抽屉族采集器单测（ulib3 T10）

权威依据：logs_collector.py（collect）

测试组：
- 正常登记：asset_id=FILE:<path>、tags=[日志]、title=name_zh、ai_contract 含抽屉语义
- legacy 状态映射 archived
- path 空条目跳过
- 注册表缺失 fail-soft（单条 error）
- 损坏 YAML fail-soft

测试隔离：tmp_path 造临时注册表，零真实仓依赖。
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from zephyr.library.collectors.logs_collector import LOG_REGISTRY_REL, collect  # noqa: E402


def _write_registry(tmp_path: Path, logs_yaml: str) -> None:
    p = tmp_path / LOG_REGISTRY_REL
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(logs_yaml, encoding="utf-8")


_LOGS_YAML = """\
logs:
  - log_id: LOG-RBK-001
    name_zh: 个股回测运行日志
    kind: run_log
    path: logs/c1_repro/
    writers: [src/zephyr/backtest/runner.py]
    consumers: [AI 研究查询]
    schema_summary: 逐行 JSON，含 ts/level/stage/msg
    retention: 90 天
    status: active
  - log_id: LOG-GOV-001
    name_zh: 旧审计日志
    kind: audit_log
    path: logs/legacy_audit/
    writers: []
    consumers: []
    schema_summary: csv
    retention: 已停写
    status: legacy
  - log_id: LOG-BAD-001
    name_zh: 缺路径条目
    kind: run_log
    path: ''
    writers: []
    consumers: []
    schema_summary: ''
    retention: ''
    status: active
"""


class TestCollect:
    def test_family_assets_derived(self, tmp_path):
        _write_registry(tmp_path, _LOGS_YAML)
        assets = collect(str(tmp_path))
        assert not any("error" in a for a in assets)
        by_id = {a["asset_id"]: a for a in assets}
        assert "FILE:logs/c1_repro/" in by_id
        a = by_id["FILE:logs/c1_repro/"]
        assert a["kind"] == "file"
        assert a["tags"] == ["日志"]
        assert a["title"] == "个股回测运行日志"
        assert "抽屉" in a["ai_contract"] and "LOG-RBK-001" in a["ai_contract"]
        assert a["status"] == "active"

    def test_legacy_maps_archived(self, tmp_path):
        _write_registry(tmp_path, _LOGS_YAML)
        by_id = {a["asset_id"]: a for a in collect(str(tmp_path))}
        assert by_id["FILE:logs/legacy_audit/"]["status"] == "archived"

    def test_empty_path_skipped(self, tmp_path):
        _write_registry(tmp_path, _LOGS_YAML)
        assets = collect(str(tmp_path))
        assert len(assets) == 2  # 缺路径条目跳过

    def test_missing_registry_fail_soft(self, tmp_path):
        assets = collect(str(tmp_path))
        assert len(assets) == 1 and "error" in assets[0]

    def test_corrupted_yaml_fail_soft(self, tmp_path):
        _write_registry(tmp_path, "logs: [ {broken\n  ::%%%yaml")
        assets = collect(str(tmp_path))
        assert len(assets) == 1 and "error" in assets[0]


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__]))
