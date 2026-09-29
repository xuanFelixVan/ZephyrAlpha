# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §ai_layer_cleaning
# [MODULE] tests.ai_layer.cleaning.test_washer
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.ai_layer.cleaning.washer; zephyr.ai_layer.cleaning.policy
# [CONSUMERS] pytest tests/ai_layer/cleaning/test_washer.py
# [STARTUP] manual
# [MATURITY] new
# [INVARIANTS] 网关/消毒器/卡读写/journal 全注入（零真实外呼零生产写盘）；
#              AST 静态断言 washer 源码零裸调 import（拦截器语义单测化证伪）；
#              默认路由解析 fail-closed 用 tmp_path 假配置（禁触生产 model_routing_policy）
# [MODIFY-GUARD] docs/_working/ai_layer_vision/L3_cleaning/DESIGN.md §2.2/§2.3/§2.4
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即红
# [TESTS] tests/ai_layer/cleaning/test_washer.py
# [TTL] permanent
"""test_washer - 清洗执行器验收（C4）：全通/P1/P3/E1/预算/退回留痕/零裸调/路由 fail-closed。"""

from __future__ import annotations

import ast
import json
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from zephyr.ai_layer.cleaning import washer as washer_mod
from zephyr.ai_layer.cleaning.policy import load_cleaning_policy
from zephyr.ai_layer.cleaning.spec_store import SpecDraft
from zephyr.ai_layer.cleaning.washer import (
    GatewayReply,
    RouteNotResolvedError,
    Washer,
    WasherDeps,
    resolve_route_from_config,
    validate_staging_path,
)

POLICY = load_cleaning_policy()

SPEC_BODY: dict[str, Any] = {
    "mechanism_one_liner": "动量因子在趋势市的加速入场效应",
    "mechanism_detail": "价格动量在高趋势 regime 下入场加速，回撤靠波动率滤窗控制。",
    "applicability": {"regime": "trend", "frequency": "daily", "universe": "CSI300"},
    "ashare_precheck": {
        "overall": "adapt_needed",
        "adaptation_plan": "T+1 下改为隔日开盘进场",
        "t_plus_1": {"verdict": "adapt", "note": "隔日化"},
        "price_limits": {"verdict": "pass", "note": "流动性充足"},
        "retail_dominance": {"verdict": "pass", "note": "影响有限"},
    },
    "risk_flags": ["overfit_history"],
    "data_fields": [{"field": "close", "source_ref": "tushare", "quality_note": "缺失率低"}],
    "reproduction_notes": "伪代码：动量排名前 10% 等权持有，月度再平衡。",
    "source_quotes": ["momentum accelerates in trending markets"],
}
LOCALIZED = {"applicability": {"regime": "趋势", "frequency": "日", "universe": "沪深300"}}

RAW_TEXT = "A momentum strategy paper body.\n\n```python\nbad.package.install()\n```"


class InjectionError(Exception):
    """模拟 ContextInjectionError（P1 拒收面）。"""


class FakeStore:
    def __init__(self) -> None:
        self.inserted: list[SpecDraft] = []

    def insert(self, draft: SpecDraft, policy: Any) -> str:
        self.inserted.append(draft)
        return f"SP-{draft.card_id}-v{len(self.inserted)}"


class FakeReader:
    def __init__(self, card: Any | None) -> None:
        self._card = card

    def get(self, card_id: str) -> Any:
        return self._card


class FakeWriter:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str, dict[str, Any]]] = []

    def transition(self, card_id: str, stage: str, **refs: Any) -> str:
        self.calls.append((card_id, stage, refs))
        return stage


class FakeJournal:
    def __init__(self) -> None:
        self.events: list[tuple[str, dict[str, Any]]] = []

    def emit(self, kind: str, payload: dict[str, Any]) -> Any:
        self.events.append((kind, payload))
        return SimpleNamespace(id="E-1", kind=kind)


class FakeSanitizer:
    def __init__(self, *, inject: bool = False) -> None:
        self._inject = inject

    def validate_llm_context(self, text: str) -> None:
        if self._inject:
            raise InjectionError("blocked pattern")


def _gateway(script: dict[str, list[GatewayReply]]):
    calls: list[dict[str, Any]] = []

    def gw(messages: list[dict[str, str]], *, task_type: str, tier: str) -> GatewayReply:
        calls.append({"task_type": task_type, "tier": tier, "messages": messages})
        queue = script[task_type]
        return queue.pop(0) if len(queue) > 1 else queue[0]

    gw.calls = calls  # type: ignore[attr-defined]
    return gw


def _ok_gateway() -> Any:
    return _gateway(
        {
            "mining_deep": [
                GatewayReply(
                    content="结构化笔记：动量机制",
                    model="deepseek-reasoner",
                    request_id_ref="lsg:d:r1",
                    tokens_in=500,
                    tokens_out=200,
                )
            ],
            "cleaning_rewrite": [
                GatewayReply(
                    content="```json\n" + json.dumps(SPEC_BODY, ensure_ascii=False) + "\n```",
                    model="deepseek-chat",
                    request_id_ref="lsg:d:r2",
                    tokens_in=800,
                    tokens_out=400,
                )
            ],
            "translation_registry": [
                GatewayReply(
                    content=json.dumps(LOCALIZED, ensure_ascii=False),
                    model="glm-4.5-free",
                    request_id_ref="lsg:d:r3",
                    tokens_in=300,
                    tokens_out=100,
                )
            ],
        }
    )


def _deps(gateway: Any, **kw: Any) -> WasherDeps:
    return WasherDeps(
        session_id="st-test",
        store=kw.get("store", FakeStore()),
        policy=kw.get("policy", POLICY),
        gateway=gateway,
        sanitizer=kw.get("sanitizer", FakeSanitizer()),
        dedup_query=kw.get("dedup_query", lambda text: []),
        card_reader=kw.get("card_reader"),
        card_writer=kw.get("card_writer", FakeWriter()),
        journal=kw.get("journal", FakeJournal()),
    )


CARD = SimpleNamespace(
    card_id="CC-W1",
    domain_id="trading_algo",
    mechanism="动量机制原文",
    source_name="arxiv",
    source_url="https://arxiv.org/abs/x",
    source_publisher="arXiv",
    source_year=2025,
    mechanism_family="prediction",
    raw_ref=None,
    four_gates={},
    risk_flags=[],
)


# ---------------------------------------------------------------- 主流程


def test_wash_success_full_path() -> None:
    gw = _ok_gateway()
    store = FakeStore()
    writer = FakeWriter()
    outcome = Washer(_deps(gw, store=store, card_writer=writer, card_reader=FakeReader(CARD))).wash_card(
        "CC-W1", raw_text=RAW_TEXT
    )
    assert outcome.status == "washed" and outcome.spec_id == "SP-CC-W1-v1"
    assert [c["task_type"] for c in gw.calls] == ["mining_deep", "cleaning_rewrite", "translation_registry"], (
        "三工序按 OBJ_M 轨分派"
    )
    assert outcome.tokens_used == 500 + 200 + 800 + 400 + 300 + 100
    draft = store.inserted[0]
    assert draft.source_name == "arxiv" and draft.source_url == "https://arxiv.org/abs/x"
    assert draft.source_name == CARD.source_name, "来源四件套只读继承（闸 1）"
    assert draft.applicability["regime"] == "趋势", "④中文术语对齐落地"
    assert draft.lsg["request_id_ref"] == "lsg:d:r2" and draft.lsg["input_scan"] == "pass"
    assert draft.wash["session"] == "st-test" and draft.wash["task_type"] == "cleaning_rewrite"
    assert writer.calls == [("CC-W1", "E2", {"spec_ref": "SP-CC-W1-v1"})]


def test_wash_via_card_reader_raw_ref(tmp_path: Path) -> None:
    """产线形态：卡经 intake 服务层读出，raw_ref 指向 E1 staging 内文件。"""
    gw = _ok_gateway()
    card = SimpleNamespace(**{**CARD.__dict__, "raw_ref": "fetched.txt"})
    washer = Washer(_deps(gw, card_reader=FakeReader(card)))
    outcome = washer.wash_card("CC-W1", raw_text=RAW_TEXT)  # 文本直给=免落盘路径
    assert outcome.status == "washed"


def test_process_clean_due_summary(monkeypatch: pytest.MonkeyPatch) -> None:
    gw = _ok_gateway()
    # 生产文本面=E1 staging 的 raw_ref；单测注入 _resolve_text 返回固定文本，其余流程真实。
    monkeypatch.setattr(Washer, "_resolve_text", lambda self, raw_text, raw_path, card_map: RAW_TEXT)
    summary = Washer(_deps(gw, card_reader=FakeReader(CARD))).process_clean_due(
        {"card_ids": ["CC-W1", "CC-W2"], "domain_id": "trading_algo"}
    )
    assert summary["washed"] == 2 and summary["rejected"] == 0


# ---------------------------------------------------------------- P1/P3/E1/预算


def test_p1_injection_rejected_as_suspect() -> None:
    gw = _ok_gateway()
    journal = FakeJournal()
    writer = FakeWriter()
    outcome = Washer(_deps(gw, sanitizer=FakeSanitizer(inject=True), journal=journal, card_writer=writer)).wash_card(
        "CC-W1", raw_text=RAW_TEXT
    )
    assert outcome.status == "rejected" and outcome.rejection_reason == "injection_suspect"
    assert not gw.calls, "P1 拒收不得进任何 API 工序"
    kind, payload = journal.events[0]
    assert kind == "intake_reject_due" and payload["stage"] == "L3"
    assert payload["rejection_reason"] == "injection_suspect"
    assert (
        "CC-W1",
        "rejected",
        {"rejection_reason": "injection_suspect", "evidence_ref": outcome.evidence_ref},
    ) in writer.calls


def test_p3_blocked_rewashes_once_then_rejects() -> None:
    gw = _gateway(
        {
            "mining_deep": [GatewayReply(content="笔记", tokens_in=10, tokens_out=5)],
            "cleaning_rewrite": [
                GatewayReply(content="好想法 [BLOCKED BY LSG]", tokens_in=10, tokens_out=5),
                GatewayReply(content="还是 [BLOCKED BY LSG]", tokens_in=10, tokens_out=5),
            ],
            "translation_registry": [],
        }
    )
    outcome = Washer(_deps(gw)).wash_card("CC-W1", raw_text=RAW_TEXT)
    assert outcome.status == "rejected" and outcome.rejection_reason == "wash_failed"
    assert "p3_broken:rewrite" in outcome.evidence_ref
    rewrite_calls = [c for c in gw.calls if c["task_type"] == "cleaning_rewrite"]
    assert len(rewrite_calls) == 2, "P3 破损重洗一次（rewash_max=1）"


def test_p3_rewash_recovers() -> None:
    gw = _gateway(
        {
            "mining_deep": [GatewayReply(content="笔记", tokens_in=10, tokens_out=5)],
            "cleaning_rewrite": [
                GatewayReply(error="all providers failed"),
                GatewayReply(
                    content="```json\n" + json.dumps(SPEC_BODY, ensure_ascii=False) + "\n```",
                    model="deepseek-chat",
                    tokens_in=10,
                    tokens_out=5,
                ),
            ],
            "translation_registry": [
                GatewayReply(content=json.dumps(LOCALIZED, ensure_ascii=False), tokens_in=10, tokens_out=5)
            ],
        }
    )
    outcome = Washer(_deps(gw)).wash_card("CC-W1", raw_text=RAW_TEXT)
    assert outcome.status == "washed", "第一次破损、重洗恢复=正常洗成"


def test_token_budget_preflight_rejects_without_any_call() -> None:
    tiny = replace(POLICY, per_card_token_budget=10)
    gw = _ok_gateway()
    outcome = Washer(_deps(gw, policy=tiny)).wash_card("CC-W1", raw_text=RAW_TEXT)
    assert outcome.status == "rejected" and outcome.rejection_reason == "wash_failed"
    assert "token_budget_preflight" in outcome.evidence_ref
    assert not gw.calls, "预算硬闸在先，禁任何 API 消耗"


def test_card_missing_rejected_not_found_without_card_write() -> None:
    gw = _ok_gateway()
    journal = FakeJournal()
    writer = FakeWriter()
    outcome = Washer(_deps(gw, card_reader=FakeReader(None), journal=journal, card_writer=writer)).wash_card(
        "CC-ghost", raw_text=RAW_TEXT
    )
    assert outcome.status == "rejected" and outcome.rejection_reason == "not_found"
    assert journal.events and writer.calls == [], "卡不存在：只发事件，不写卡态"


def test_e1_staging_violation_rejected() -> None:
    gw = _ok_gateway()
    card = SimpleNamespace(**{**CARD.__dict__, "raw_ref": "../../etc/passwd"})
    outcome = Washer(_deps(gw, card_reader=FakeReader(card))).wash_card("CC-W1")
    assert outcome.status == "rejected" and outcome.rejection_reason == "not_found"
    assert "e1_staging_violation" in outcome.evidence_ref
    assert not gw.calls


def test_validate_staging_path_guards() -> None:
    with pytest.raises(Exception, match="session_id_invalid"):
        validate_staging_path("x.txt", "../evil")
    with pytest.raises(Exception, match="e1_staging_violation"):
        validate_staging_path("C:/Windows/system32/cmd.exe", "st-test")
    with pytest.raises(Exception, match="raw_not_found"):
        validate_staging_path("definitely-missing.bin", "st-test")


# ---------------------------------------------------------------- 零裸调与路由


def test_washer_source_has_zero_bare_llm_imports() -> None:
    """拦截器语义单测化：washer 源码零 openai/anthropic/requests/httpx/urllib import。"""
    banned = {"openai", "anthropic", "requests", "httpx", "urllib", "socket", "aiohttp"}
    tree = ast.parse(Path(washer_mod.__file__).read_text(encoding="utf-8"))
    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            roots.add(node.module.split(".")[0])
    hit = roots & banned
    assert not hit, f"发现裸调面 import：{hit}（宪法 §9.2 全部 LLM 调用必经 LSG）"


def test_default_route_fail_closed_without_track(tmp_path: Path) -> None:
    config = tmp_path / "model_routing_policy.yaml"
    config.write_text("period_rules: {}\n", encoding="utf-8")
    with pytest.raises(RouteNotResolvedError, match="route_missing:cleaning_rewrite"):
        resolve_route_from_config("cleaning_rewrite", config)


def test_default_route_resolves_track_when_present(tmp_path: Path) -> None:
    config = tmp_path / "model_routing_policy.yaml"
    config.write_text(
        "ai_layer_routes:\n  - task_type: cleaning_rewrite\n    provider: deepseek\n    model: deepseek-chat\n",
        encoding="utf-8",
    )
    target = resolve_route_from_config("cleaning_rewrite", config)
    assert (target.provider, target.model) == ("deepseek", "deepseek-chat")
    with pytest.raises(RouteNotResolvedError, match="OBJ_M C6"):
        resolve_route_from_config("review_judge", config)


def test_default_route_reads_task_routes_truth_source(tmp_path: Path) -> None:
    """C6 消费端修复：真源键=task_routes 映射（附表 A 'provider:model' 串）命中。"""
    config = tmp_path / "model_routing_policy.yaml"
    config.write_text(
        "task_routes:\n"
        "  cleaning_rewrite:\n"
        "    preferred: deepseek:deepseek-chat\n"
        "    fallbacks: ['zhipu:glm-4-plus']\n"
        "  mining_deep:\n"
        "    preferred: deepseek:deepseek-reasoner\n",
        encoding="utf-8",
    )
    target = resolve_route_from_config("cleaning_rewrite", config)
    assert (target.provider, target.model) == ("deepseek", "deepseek-chat")
    target2 = resolve_route_from_config("mining_deep", config)
    assert (target2.provider, target2.model) == ("deepseek", "deepseek-reasoner")
    # 查无轨仍 fail-closed
    with pytest.raises(RouteNotResolvedError, match="route_missing:review_judge"):
        resolve_route_from_config("review_judge", config)


def test_default_route_prefers_task_routes_over_alias(tmp_path: Path) -> None:
    """真源优先：task_routes 与 ai_layer_routes 别名并存时真源胜（别名只兜底）。"""
    config = tmp_path / "model_routing_policy.yaml"
    config.write_text(
        "task_routes:\n"
        "  cleaning_rewrite:\n"
        "    preferred: deepseek:deepseek-chat\n"
        "ai_layer_routes:\n"
        "  - task_type: cleaning_rewrite\n"
        "    provider: stale\n"
        "    model: stale-model\n",
        encoding="utf-8",
    )
    target = resolve_route_from_config("cleaning_rewrite", config)
    assert (target.provider, target.model) == ("deepseek", "deepseek-chat")


def test_default_route_real_config_cleaning_rewrite_hit() -> None:
    """端到端钉：生产真源 config（Owner 终批数据，只读）下 cleaning_rewrite 轨可解析。"""
    target = resolve_route_from_config("cleaning_rewrite")
    assert target.provider == "deepseek" and target.model


def test_lsg_gateway_annotation_present() -> None:
    """接线批注留痕验收：P2 适配器在源码内点名 LSG 扫描语义与 OBJ_M 前置。"""
    source = Path(washer_mod.__file__).read_text(encoding="utf-8")
    assert "LSGSecurityGateway" in source and "scan_input" in source
    assert "BareLLMCallError" in source and "OBJ_M C6" in source
