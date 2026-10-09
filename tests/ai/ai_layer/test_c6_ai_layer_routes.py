# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §ai_layer_routes
# [MODULE] tests.ai_layer.test_c6_ai_layer_routes
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] config/model_routing_policy.yaml（只读真源）; PyYAML safe_load; src/zephyr/ai_layer/cleaning/washer.resolve_route_from_config（只读解析）
# [CONSUMERS] pytest tests/ai_layer/test_c6_ai_layer_routes.py；OBJ_M 施工项 C6 落地验收（Owner 终批 OBJ_M-#1）
# [STARTUP] manual
# [MATURITY] new
# [INVARIANTS] 本测试是 C6 提案 8 条 AI 层轨的**逐条字面钉桩**——真源=
#              docs/_working/ai_layer_vision/OBJ_M_models/C6_routing_diff_proposal.md §2.2（表照录，
#              含 preferred/fallbacks/free_window_pref/period_constraint/evidence_ref 五字段）；
#              生产 YAML 只读不写（零 tmp 写盘、零 DB、零网络、零时钟）；
#              既有 12 条交易轨与 api_providers/local_providers 四前缀=零改动（提案 §3.1/§3.4 合规自查）；
#              AI 层轨落位=独立顶层段 ai_layer_routes（非 task_routes 子项）：task_routes 的
#              preferred 语义是通道模式（api|local|hybrid|rule_engine），AI 层轨是具体模型键，
#              混段会使 cascade_orchestrator mode 链整体落空并静默退化 static_mapping.default；
#              禁在本测试发明提案外阈值——新增判据=待裁项，不进桩
# [MODIFY-GUARD] docs/_working/ai_layer_vision/OBJ_M_models/C6_routing_diff_proposal.md §2
#                docs/_working/ai_layer_vision/OBJ_M_models/DESIGN.md §5.2/§5.3
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即红；ai_layer_routes 段缺失=8 轨全红（提案未落地）
# [TESTS] tests/ai_layer/test_c6_ai_layer_routes.py
# [TTL] permanent
"""test_c6_ai_layer_routes — C6 路由八轨终批落地验收（提案 §2.2 逐条字面钉桩 + 既有 12 轨零改动）。"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Final

import yaml

REPO: Final = Path(__file__).resolve().parents[3]
POLICY_PATH: Final = REPO / "config" / "model_routing_policy.yaml"

# 提案 §2.2 逐条照录（键=task_type，值=该轨五字段字面量；改一格即红）
PROPOSAL_TRACKS: Final[dict[str, dict[str, Any]]] = {
    "mining_broad": {
        "preferred": "zhipu:glm-4.5-free",
        "fallbacks": ["zhipu:qwen-flash", "deepseek:deepseek-chat"],
        "free_window_pref": {
            "enabled": True,
            "window": "00:30-08:30 UTC+8",
            "quota_guard": "免费配额尽/上下文超限→谷时付费档",
        },
        "period_constraint": "inherit",
        "evidence_ref": "OBJ_M DESIGN §5.3+挖矿SOP §2 二维法+2026-09-17 通宵班夜间 Flash 免费实战",
    },
    "mining_deep": {
        "preferred": "deepseek:deepseek-reasoner",
        "fallbacks": ["anthropic:claude-sonnet", "local:qwen3:8b"],
        "free_window_pref": {
            "enabled": True,
            "window": "00:30-08:30 UTC+8 谷时半价",
            "quota_guard": ">128k 上下文→长上下文档",
        },
        "period_constraint": "inherit",
        "evidence_ref": 'OBJ_M DESIGN §5.3+挖矿 SOP 二维法"最强模型"轴',
    },
    "cleaning_rewrite": {
        "preferred": "deepseek:deepseek-chat",
        "fallbacks": ["zhipu:glm-4-plus"],
        "free_window_pref": {
            "enabled": True,
            "window": "00:30-08:30 UTC+8 谷时半价",
            "quota_guard": "",
        },
        "period_constraint": "inherit",
        "evidence_ref": "OBJ_M DESIGN §5.3+主文档 §一 L2=API 强模型执行",
    },
    "review_judge": {
        "preferred": "anthropic:claude-sonnet",
        "fallbacks": ["deepseek:deepseek-reasoner"],
        "free_window_pref": {
            "enabled": False,
            "window": "",
            "quota_guard": "同源互判禁止（MCE RISK-3.2）",
        },
        "period_constraint": "inherit",
        "evidence_ref": "OBJ_M DESIGN §5.3+MCE RISK-3.2 裁判解耦",
    },
    "translation_registry": {
        "preferred": "zhipu:glm-4.5-free",
        "fallbacks": ["zhipu:qwen-flash"],
        "free_window_pref": {
            "enabled": True,
            "window": "00:30-08:30 UTC+8",
            "quota_guard": "术语表命中失败→升 standard 复核",
        },
        "period_constraint": "inherit",
        "evidence_ref": "OBJ_M DESIGN §5.3+三层翻译 loader 现状",
    },
    "daily_report": {
        "preferred": "zhipu:qwen-flash",
        "fallbacks": ["zhipu:glm-4-flash"],
        "free_window_pref": {
            "enabled": True,
            "window": "00:30-08:30 UTC+8",
            "quota_guard": "",
        },
        "period_constraint": "inherit",
        "evidence_ref": "OBJ_M DESIGN §5.3+model_pricing.yaml 最低价档",
    },
    "overseer_dispatch": {
        "preferred": "deepseek:deepseek-reasoner",
        "fallbacks": ["anthropic:claude-sonnet"],
        "free_window_pref": {
            "enabled": False,
            "window": "",
            "quota_guard": "派工裁定需强模型",
        },
        "period_constraint": "inherit",
        "evidence_ref": "OBJ_M DESIGN §5.3+总令模板实践",
    },
    "budget_analysis": {
        "preferred": "local:qwen3:8b",
        "fallbacks": ["zhipu:glm-4-flash"],
        "free_window_pref": {
            "enabled": True,
            "window": "本地优先（成本 0）",
            "quota_guard": "Ollama 忙（llm_local 组互斥）→落免费档",
        },
        "period_constraint": "inherit",
        "evidence_ref": "OBJ_M DESIGN §5.3+数据不出域+成本 0",
    },
}

# 提案 §1 现状基线：既有 12 条交易轨（附表 A），落地后必须一字不动
EXISTING_12_TRACKS: Final[frozenset[str]] = frozenset(
    {
        "risk_veto",
        "risk_diagnosis",
        "compliance_review",
        "signal_generation",
        "param_tuning",
        "anomaly_classification",
        "market_regime",
        "attribution",
        "reflection_l1",
        "reflection_l23",
        "strategy_codegen",
        "paper_reading",
        "cross_validation",
    }
)


def _policy() -> dict[str, Any]:
    with POLICY_PATH.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def _ai_routes() -> dict[str, dict[str, Any]]:
    """ai_layer_routes 段 -> {task_type: entry}（段缺失/重复 task_type 即红）。"""
    entries = _policy().get("ai_layer_routes")
    assert isinstance(entries, list), "ai_layer_routes 段缺失或非列表（C6 八轨未落地）"
    assert len(entries) == len(PROPOSAL_TRACKS), f"AI 层轨条数={len(entries)}，提案 §2.2 恒为 {len(PROPOSAL_TRACKS)} 条"
    out: dict[str, dict[str, Any]] = {}
    for e in entries:
        tt = str(e.get("task_type"))
        assert tt not in out, f"task_type 重复登记：{tt}"
        out[tt] = e
    return out


def test_eight_ai_tracks_present_with_proposal_task_types() -> None:
    """八轨齐且命名与提案 §2.2 逐条一致（无多无少）。"""
    assert set(_ai_routes()) == set(PROPOSAL_TRACKS)


def test_each_track_matches_proposal_literal() -> None:
    """逐条字面比对提案五字段（evidence_ref 逐条留提案锚点，禁缺禁改）。"""
    routes = _ai_routes()
    for task_type, expected in PROPOSAL_TRACKS.items():
        entry = routes[task_type]
        for field, want in expected.items():
            assert field in entry, f"{task_type} 缺提案字段 {field}"
            assert entry[field] == want, f"{task_type}.{field} 偏离提案：{entry[field]!r} != {want!r}"


def test_preferred_splits_into_provider_and_model_for_existing_loader() -> None:
    """route_entry 的 provider/model 派生字段须与 preferred 严格同解（唯一消费方读 provider+model）。"""
    for task_type, entry in _ai_routes().items():
        provider, _, model = str(entry["preferred"]).partition(":")
        assert entry["provider"] == provider, f"{task_type}.provider 与 preferred 前缀不符"
        assert entry["model"] == model, f"{task_type}.model 与 preferred 后缀不符"


def test_existing_consumer_resolves_cleaning_rewrite_from_real_config() -> None:
    """既有消费方（washer.resolve_route_from_config，源码点名「OBJ_M C6 产物」）读真配置即放行。

    内收验收：不新建平行解析器——C6 落地前该轨缺席=fail-closed（route_missing），落地后须解析出
    提案 §2.2 cleaning_rewrite 首选 deepseek:deepseek-chat。
    """
    from zephyr.ai_layer.cleaning.washer import resolve_route_from_config

    target = resolve_route_from_config("cleaning_rewrite")
    assert (target.provider, target.model) == ("deepseek", "deepseek-chat")


def test_period_constraint_inherit_not_relaxed() -> None:
    """提案 §3.3「全部 inherit，不放松任何交易时段限制」：八轨 period_constraint 恒 inherit，
    且 AI 轨不落 task_routes（不参与 kind 白名单扩权——period_rules 一字未动）。"""
    for task_type, entry in _ai_routes().items():
        assert entry["period_constraint"] == "inherit", f"{task_type} 不得偏离 inherit"
    policy = _policy()
    assert set(policy["period_rules"]) == {"pre_open", "call_auction", "trading", "post_close"}
    assert policy["period_rules"]["trading"] == {
        "api": "restricted",
        "api_allowed_kinds": ["strategic", "reflection"],
    }
    for task_type in PROPOSAL_TRACKS:
        assert "kind" not in _ai_routes()[task_type], f"{task_type} 禁带 kind（提案外字段=扩权）"


def test_billing_line_no_new_channel_and_existing_12_tracks_untouched() -> None:
    """提案 §3.1 合规自查：api_providers 四前缀零增删；既有 12 轨零改动（diff 只增不改）。"""
    policy = _policy()
    assert policy["api_providers"] == ["zhipu", "deepseek", "openai_azure", "anthropic"]
    assert policy["local_providers"] == ["ollama", "local"]
    routes = policy["task_routes"]
    assert set(routes) == EXISTING_12_TRACKS, "task_routes 必须仍是既有 12 轨（AI 层轨不并入此段）"
    # 逐轨结构零改动（preferred/fallbacks/kind 三键原样）
    for task_type, entry in routes.items():
        assert {"preferred", "fallbacks", "kind", "reason"} <= set(entry), f"{task_type} 既有轨字段被改"
    assert routes["risk_veto"] == {  # noqa: 首轨字面钉桩
        "preferred": "rule_engine",
        "fallbacks": [],
        "kind": "risk",
        "reason": "确定性规则，<1ms（无 LLM）",
    }


def test_free_window_pref_only_declares_preference_and_two_tracks_forbid_it() -> None:
    """提案 §3.2：free_window_pref 是偏好标记；review_judge/overseer_dispatch 内置 enabled:false。"""
    enabled = {tt for tt, e in _ai_routes().items() if e["free_window_pref"]["enabled"]}
    assert enabled == set(PROPOSAL_TRACKS) - {"review_judge", "overseer_dispatch"}
    for tt in ("review_judge", "overseer_dispatch"):
        assert _ai_routes()[tt]["free_window_pref"]["quota_guard"], f"{tt} 禁免费窗须留禁因说明"
