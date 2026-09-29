# [BLUEPRINT] MOD-FE-REPORTS-API-TEST | docs/_working/fullconnect_campaign/k_frontend_docs/10_f115_report_generation.md | §
# [TTL] permanent
# [MODULE] tests.frontend.test_api_server_reports
# [DOMAIN] D_FRONTEND
"""F115 R3 投影链薄刀测试——GET /api/reports 报告归档只读投影。

覆盖：
- 正常态：ok:true + 降序（最新在前）+ source/report_type 精确过滤 + limit 截尾
- 空态：loader 返回空 → ok:true count=0（投影零副作用不 500）
- 读取面异常 → ok:false + error（前端回退空态，同演示诚实纪律）

测试隔离：FastAPI TestClient + sys.modules 注入假 sink 模块（monkeypatch.setitem
官方豁免通道，路由 lazy import 命中假面）——不触生产 data/reports/report_archive.jsonl，
也不 real-import reporting 包（api_server 导入链与其余 zephyr.* 导入序耦合，假面注入
把投影测试与 reporting 包导入态解耦）；投影真源（JSONL 落盘面）由
tests/reporting/test_report_archive_sink.py 覆盖。
worktree 解析走 ZEPHYR_ALPHA_ROOT 环境变量（usercustomize 官方开关）。
"""

from __future__ import annotations

import sys
import types
from pathlib import Path
from typing import Any

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT / "src"))

from fastapi.testclient import TestClient  # noqa: E402

import zephyr.frontend.dashboard.api_server as api_server  # noqa: E402


def _record(archive_id: str, source: str = "risk", report_type: str = "daily_risk_review") -> dict[str, Any]:
    return {
        "archive_id": archive_id,
        "report_id": f"RPT-{archive_id}",
        "source": source,
        "report_type": report_type,
        "archived_at": f"2026-09-28T15:00:0{archive_id[-1]}+00:00",
        "content": {"k": archive_id},
        "content_hash": "ch",
        "prev_hash": "ph",
        "record_hash": "rh",
        "schema_version": "1.0",
    }


def _install_fake_loader(
    monkeypatch: pytest.MonkeyPatch,
    loader: Any,
) -> None:
    """sys.modules 注入假 sink 模块——路由 lazy `from zephyr.reporting.report_archive_sink
    import load_report_records` 命中假面（sys.modules 拦截，零文件系统 import）。"""
    fake = types.ModuleType("zephyr.reporting.report_archive_sink")
    fake.load_report_records = loader  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "zephyr.reporting.report_archive_sink", fake)


@pytest.fixture()
def client() -> TestClient:
    return TestClient(api_server.app)


def test_reports_desc_and_filters(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    records = [_record(f"ARCH-{i}") for i in range(5)]
    _install_fake_loader(monkeypatch, lambda path=None: list(records))
    resp = client.get("/api/reports")
    assert resp.status_code == 200
    body = resp.json()
    assert body["ok"] is True and body["count"] == 5
    assert body["reports"][0]["archive_id"] == "ARCH-4"  # 降序（最新在前）
    assert body["reports"][-1]["archive_id"] == "ARCH-0"

    filtered = client.get("/api/reports", params={"source": "risk", "report_type": "daily_risk_review"})
    assert filtered.json()["count"] == 5
    miss = client.get("/api/reports", params={"source": "no-such"})
    assert miss.json()["ok"] is True and miss.json()["count"] == 0

    limited = client.get("/api/reports", params={"limit": 2})
    body_l = limited.json()
    assert body_l["count"] == 2 and body_l["reports"][0]["archive_id"] == "ARCH-4"


def test_reports_empty_state(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    _install_fake_loader(monkeypatch, lambda path=None: [])
    body = client.get("/api/reports").json()
    assert body == {"ok": True, "count": 0, "reports": []}


def test_reports_loader_exception_degrades(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    def _boom(path: object = None) -> list[dict[str, Any]]:
        raise OSError("read fail")

    _install_fake_loader(monkeypatch, _boom)
    resp = client.get("/api/reports")
    assert resp.status_code == 200
    body = resp.json()
    assert body["ok"] is False and "read fail" in body["error"] and body["count"] == 0


if __name__ == "__main__":  # pragma: no cover
    pytest.main([__file__, "-q"])
