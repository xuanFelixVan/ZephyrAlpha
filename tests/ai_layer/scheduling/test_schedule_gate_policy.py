# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §ai_layer_scheduling
# [MODULE] tests.ai_layer.scheduling.test_schedule_gate_policy
# [DOMAIN] D_GOVERNANCE
# [TTL] permanent
"""test_schedule_gate_policy — C1 验收：全常数齐（M1-M4/优势分桶/降级线/配额上限/首批白名单区）+
Owner 点头记录位+治理锚定头+与词表真源锚定一致；真实治理文件只读（零写）。"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from zephyr.ai_layer.scheduling.maturity import DEFAULT_POLICY_PATH, load_gate_policy
from zephyr.shared.io.paths import REPO_ROOT


def test_policy_file_is_repo_config() -> None:
    assert DEFAULT_POLICY_PATH == REPO_ROOT / "config" / "schedule_gate_policy.yaml"


def test_all_constants_present(policy: dict[str, Any]) -> None:
    m = policy["maturity"]
    for key in (
        "m1_min_wins",
        "m2_min_win_rate",
        "m2_min_samples",
        "m3_freshness_max_days",
        "m4_first_batch_whitelist",
    ):
        assert key in m, f"M1-M4 常数缺 {key}"
    prio = policy["priority"]
    assert set(prio["advantage_buckets"]) == {"large", "medium", "small"}  # 优势分桶三档
    assert prio["starred_demote_factor"] == 0.5
    assert prio["starvation_age_days"] > 0 and prio["starvation_bump"] > 0  # 防饥饿
    quota = policy["quota"]
    for key in (
        "q1_active_session_cap",
        "q2_subagent_max",
        "q3_daily_token_budget",
        "q4_commit_queue_pending_cap",
        "defer_critical_streak",
        "dead_dispatch_fail_n",
    ):
        assert key in quota, f"配额/降级线缺 {key}"
    assert quota["q2_subagent_max"] <= 3  # DESIGN budget.subagent_quota ≤3
    assert policy["dispatch"]["reviewer_model_tier"] == "strong"


def test_owner_signoff_slots(policy: dict[str, Any]) -> None:
    """C1 验收：Owner 点头记录位——初值追认已销（L5-#1）；白名单 L5-#2 已随 F5 通电批
    （裁定#450，2026-09-30 夜总攻）approved_by_night_batch（钉值随批翻转，W2-FIN 终验车道重落地）。"""
    signoff = policy["owner_signoff"]
    assert signoff["policy_initial_values"]["status"] == "approved_by_night_batch"
    assert signoff["first_batch_whitelist"]["status"] == "approved_by_night_batch"
    assert policy["maturity"]["m4_first_batch_whitelist"] == ["ai_eng", "tooling"]  # F5 首批白名单


def test_vocab_anchors_match_generation_sources(policy: dict[str, Any]) -> None:
    """词表锚定与真源一致（引用不复制——漂移即测试红，两处同批改）。"""
    cc = policy["compute_classes"]
    assert cc["e0_class_to_resource"] == {
        "local": "light",
        "local_gpu": "cpu_heavy",
        "mixed": "cpu_heavy",
        "api": "llm_api_paid",
    }
    assert set(cc["trading_sensitive_classes"]) == {"cpu_heavy", "gpu", "llm_api_local", "db_heavy"}
    # 幽灵池禁令：lanes 真池词表不得含 light/cpu/gpu（daily_crypto 事故语义）
    lanes = set(cc["pool_vocabulary_lanes"])
    assert lanes == {"default", "heavy", "intraday_minute", "intraday_sector", "realtime"}
    assert not (lanes & {"light", "cpu", "gpu"})
    assert "light" not in cc["seg_vocabulary"]
    # 排班一张真源：种子真源路径指向 seeds 文件，非 GENERATED 注册表直改
    assert cc["seg_vocabulary"] == ["build", "accept"]


def test_governance_header_anchors(tmp_path: Path) -> None:
    """治理锚定头+净零声明+初值追认三件在文（照 README §3 台账行原文）。"""
    text = DEFAULT_POLICY_PATH.read_text(encoding="utf-8")
    assert "ai_layer_vision/README.md §3" in text
    assert "不建第二张排班表" in text or "唯一 OBJ_R 管辖常量件" in text
    assert "Owner 夜批授权原值生效" in text  # 初值追认（L5-#1 已销项原文）
    assert "OBJ_R" in text and "禁运行时改值" in text
