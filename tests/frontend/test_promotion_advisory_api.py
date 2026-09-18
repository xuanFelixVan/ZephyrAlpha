# [BLUEPRINT] MOD-FE-PROMO-API-TEST | docs/_working/full-auto-chain/S13_frontend_approval/README.md §5 | §
# [TTL] permanent
# [MODULE] tests.frontend.test_promotion_advisory_api
# [DOMAIN] D_FRONTEND
"""C5 验收单测：策略转正审批两端点（api_server 第 4 获准写端点 + 只读清单）。

覆盖：
- GET  /api/promotion-advisories：空态 / 有数据态 / 执行器异常降级 / 执行器缺位降级
- POST /api/promotion-decide：成功（参数契约 advisory_id,decision,token=None,via="frontend"）
  / 业务拒绝（ok:false 200 承载）/ decision 非法 400 / advisory_id 缺失 400
  / 执行器缺位 503 / 执行器意外异常 500

测试隔离：FastAPI TestClient + monkeypatch 假执行器模块（不 import 真实
zephyr.strategy_pipeline.promotion_advisory——Y1 并行施工未落地/落地均不依赖，
不触生产路径、零写副作用）。
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
import zephyr.strategy_pipeline as sp_pkg  # noqa: E402


ADVISORY_OK: dict[str, Any] = {
    "advisory_id": "advisory-20260915-demo1",
    "strategy_id": "momentum-20d",
    "lifecycle_now": "sim",
    "evidence": {
        "sim_pass_months": 3,
        "sim_breach_months": 0,
        "fw_backtest": {
            "run_id": "bt-fw-demo",
            "sharpe": 1.42,
            "max_dd": -0.08,
            "total_return": 0.21,
            "panel_ok": True,
        },
    },
    "recommendation": "promote",
    "generated_at": "2026-09-15T03:00:00+00:00",
}


def _install_executor(
    monkeypatch: pytest.MonkeyPatch,
    *,
    list_fn=None,
    decide_fn=None,
) -> types.ModuleType:
    """向 strategy_pipeline 包挂假 promotion_advisory 模块（端点惰性 import 的落点）。"""
    fake = types.ModuleType("zephyr.strategy_pipeline.promotion_advisory")
    fake.list_advisories = list_fn if list_fn is not None else (lambda: [])
    fake.decide = decide_fn
    monkeypatch.setattr(sp_pkg, "promotion_advisory", fake, raising=False)
    return fake


def _uninstall_executor(monkeypatch: pytest.MonkeyPatch) -> None:
    """摘除执行器：包属性置 None（from-import 成功返回 None → 端点判执行器未就位）。

    注：不走 sys.modules[key]=None 的 import-halted 技巧——#ARCH-107 污染探针盯防该形态。
    """
    monkeypatch.setattr(sp_pkg, "promotion_advisory", None, raising=False)


@pytest.fixture()
def client() -> TestClient:
    return TestClient(api_server.app)


# ── GET /api/promotion-advisories ────────────────────────────────────────────


def test_get_empty_list_ok(client, monkeypatch):
    """空态：执行器返回 [] → 200 ok:true count=0 data=[]（前端渲染空态）。"""
    _install_executor(monkeypatch, list_fn=lambda: [])
    r = client.get("/api/promotion-advisories")
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True
    assert body["count"] == 0
    assert body["data"] == []


def test_get_with_data_passthrough(client, monkeypatch):
    """有数据态：执行器返回建议包列表 → 原样透传（含已决卡 decision 字段）。"""
    decided = {**ADVISORY_OK, "advisory_id": "advisory-20260915-demo2",
               "decision": {"decision": "approve", "message": "已批准进整装"}}
    _install_executor(monkeypatch, list_fn=lambda: [ADVISORY_OK, decided])
    r = client.get("/api/promotion-advisories")
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True
    assert body["count"] == 2
    assert body["data"][0]["strategy_id"] == "momentum-20d"
    assert body["data"][0]["evidence"]["fw_backtest"]["panel_ok"] is True
    assert body["data"][1]["decision"]["decision"] == "approve"


def test_get_executor_exception_degrades(client, monkeypatch):
    """执行器异常 → 200 ok:false + 空列表 + error（不 500 硬崩，前端渲染空态）。"""
    def _boom():
        raise RuntimeError("advisory store corrupted")
    _install_executor(monkeypatch, list_fn=_boom)
    r = client.get("/api/promotion-advisories")
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is False
    assert body["count"] == 0
    assert body["data"] == []
    assert "promotion_advisory unavailable" in body["error"]


def test_get_executor_missing_degrades(client, monkeypatch):
    """执行器缺位（Y1 未落地常态）→ 200 ok:false + 空列表（同降级契约）。"""
    _uninstall_executor(monkeypatch)
    r = client.get("/api/promotion-advisories")
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is False
    assert body["count"] == 0
    assert body["data"] == []


# ── POST /api/promotion-decide ───────────────────────────────────────────────


def test_post_decide_success_contract(client, monkeypatch):
    """成功：参数契约钉死 decide(advisory_id, decision, token=None, via="frontend")；结果透传。"""
    captured: dict[str, Any] = {}

    def _decide(advisory_id, decision, token=None, via="api"):
        captured.update(advisory_id=advisory_id, decision=decision, token=token, via=via)
        return {"ok": True, "message": "已批准", "new_lifecycle": "production",
                "receipt": {"receipt_id": "rc-1"}}

    _install_executor(monkeypatch, decide_fn=_decide)
    r = client.post("/api/promotion-decide",
                    json={"advisory_id": "advisory-20260915-demo1", "decision": "approve"})
    assert r.status_code == 200
    assert captured == {"advisory_id": "advisory-20260915-demo1", "decision": "approve",
                        "token": None, "via": "frontend"}
    body = r.json()
    assert body["ok"] is True
    assert body["new_lifecycle"] == "production"
    assert body["receipt"] == {"receipt_id": "rc-1"}


def test_post_decide_business_rejection_200(client, monkeypatch):
    """业务拒绝（已决幂等/FSM 非法转换等）由执行器返回 ok:false → 200 承载原因。"""
    _install_executor(monkeypatch, decide_fn=lambda *a, **k: {"ok": False, "message": "该建议已拍板（幂等拒绝）"})
    r = client.post("/api/promotion-decide",
                    json={"advisory_id": "advisory-20260915-demo1", "decision": "approve"})
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is False
    assert "已拍板" in body["message"]


def test_post_decide_invalid_decision_400(client, monkeypatch):
    """decision 非法值 → 400（合法域仅 approve|reject）。"""
    _install_executor(monkeypatch, decide_fn=lambda *a, **k: {"ok": True})
    for bad in ("promote", "APPROVE", "", "yes"):
        r = client.post("/api/promotion-decide",
                        json={"advisory_id": "advisory-20260915-demo1", "decision": bad})
        assert r.status_code == 400, f"decision={bad!r} 应 400，得 {r.status_code}"


def test_post_decide_missing_advisory_id_400(client, monkeypatch):
    """advisory_id 缺失/空白 → 400。"""
    _install_executor(monkeypatch, decide_fn=lambda *a, **k: {"ok": True})
    r = client.post("/api/promotion-decide", json={"decision": "approve"})
    assert r.status_code == 400
    r2 = client.post("/api/promotion-decide", json={"advisory_id": "   ", "decision": "reject"})
    assert r2.status_code == 400


def test_post_decide_executor_missing_503(client, monkeypatch):
    """执行器缺位 → 503（服务端依赖未就绪语义，非客户端错）。"""
    _uninstall_executor(monkeypatch)
    r = client.post("/api/promotion-decide",
                    json={"advisory_id": "advisory-20260915-demo1", "decision": "approve"})
    assert r.status_code == 503
    assert "promotion_advisory" in r.json()["detail"]


def test_post_decide_executor_import_error_503(client, monkeypatch):
    """执行器模块 import 失败（真源在册但不可载）→ 503（ImportError 分支）。

    手法：delattr 包属性（monkeypatch 自恢复）+ 包级 __getattr__（PEP 562）抛 ImportError
    ——from-import 走 getattr 落空→__getattr__ 路径，全程不碰 sys.modules（#ARCH-107 合规）。
    """
    monkeypatch.delattr(sp_pkg, "promotion_advisory", raising=False)

    def _raise_import(name: str):
        raise ImportError(f"simulated missing submodule: {name}")

    monkeypatch.setattr(sp_pkg, "__getattr__", _raise_import, raising=False)
    r = client.post("/api/promotion-decide",
                    json={"advisory_id": "advisory-20260915-demo1", "decision": "approve"})
    assert r.status_code == 503
    assert "unavailable" in r.json()["detail"]


def test_post_decide_executor_crash_500(client, monkeypatch):
    """执行器意外异常 → 500（异常串进 detail 供排查，不裸抛堆栈）。"""
    def _boom(*a, **k):
        raise ValueError("FSM executor exploded")
    _install_executor(monkeypatch, decide_fn=_boom)
    r = client.post("/api/promotion-decide",
                    json={"advisory_id": "advisory-20260915-demo1", "decision": "reject"})
    assert r.status_code == 500
    assert "FSM executor exploded" in r.json()["detail"]
