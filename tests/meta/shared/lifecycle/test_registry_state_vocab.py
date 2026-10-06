# [A_test] module_id: zephyr.shared.lifecycle.registry_state_vocab | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-BT-188 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §lifecycle_fsm_vocab
# [MODULE] tests.shared.lifecycle.test_registry_state_vocab
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] pytest; PyYAML; zephyr.shared.lifecycle.registry_state_vocab;
#                zephyr.strategy_pipeline.lifecycle_fsm（只读五态常量做同源判别，不改热件）
# [CONSUMERS] pytest 自动发现
# [STARTUP] python -m pytest tests/shared/lifecycle/test_registry_state_vocab.py
# [MATURITY] testing
# [INVARIANTS] 造册一律 tmp_path（禁写 catalogs 热册）；判别力主证=FSM 五态恰好等于映射定义域
#              （多一个态/少一个态即红）+ production 落册必须是 live；机读字段缺失与落地两态都钉
# [MODIFY-GUARD] —
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即测试失败
# [TESTS] 本文件
# [TTL] permanent
"""test_registry_state_vocab.py — F75 词表对齐层单测（三处硬伤里的两处拼写面）。

钉三件事：①"production" 永不落注册表（必须翻成 "live"）；②"shelved" 只有在 catalog 机读词表
收编后才准写（未收编=越界值被拒，暴露缺口而非静默放行）；3demote/decayed 语义不在本件射程
（本件只拼写对齐，测试也钉住"不许顺手改语义"——decayed 仍不是 FSM 可达态）。
"""

from __future__ import annotations

import pytest

pytest.skip(
    "[st-chiefzc-rescue-20260928 捞回袋标注] 被测模块 zephyr.shared.lifecycle.registry_state_vocab "
    "因 ORPHAN-MODULE 门禁暂缓随本袋落地（其 src 消费方 zephyr.shared.vocab.market_state "
    "在 st-ailayer-final-20260924 车道同波，不在本袋清单）——消费方波次落地时模块+本测试一并恢复硬测。",
    allow_module_level=True,
)

from pathlib import Path

import pytest
import yaml

from zephyr.shared.lifecycle.registry_state_vocab import (
    FSM_STATE_TO_REGISTRY_STATE,
    MACHINE_READABLE_FIELD,
    REGISTRY_LIFECYCLE_STATES_PROVISIONAL,
    RegistryVocabError,
    aligned_lifecycle_state_for_write,
    assert_registry_lifecycle_state,
    registry_lifecycle_vocabulary,
    to_registry_lifecycle_state,
    vocab_report,
)
from zephyr.strategy_pipeline.lifecycle_fsm import (
    CANDIDATE,
    PRODUCTION,
    RETIRED,
    SHELVED,
    SIM,
)

FSM_FIVE_STATES = (CANDIDATE, SIM, PRODUCTION, SHELVED, RETIRED)


def _catalog(tmp_path: Path, *, values: list[str] | None) -> Path:
    payload: dict[str, object] = {"registry_id": "REG-STR-001", "strategies": []}
    if values is not None:
        payload[MACHINE_READABLE_FIELD] = values
    path = tmp_path / "strategy_registry.yaml"
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
    return path


def test_mapping_domain_equals_fsm_five_states_exactly() -> None:
    """同源判别：映射定义域恰好=FSM 五态（增删状态而漏改对齐层=立即红）。"""
    assert set(FSM_STATE_TO_REGISTRY_STATE) == set(FSM_FIVE_STATES)


def test_production_spelling_aligned_to_live() -> None:
    """硬伤 1 治本钉值：转正写册必须落 "live"，"production" 不得出现在注册表面。"""
    assert to_registry_lifecycle_state(PRODUCTION) == "live"
    assert to_registry_lifecycle_state(SIM) == "sim"
    assert to_registry_lifecycle_state(CANDIDATE) == "candidate"
    assert to_registry_lifecycle_state(RETIRED) == "retired"
    with pytest.raises(RegistryVocabError):
        to_registry_lifecycle_state("live")  # 反向：注册表词不是 FSM 词，不许混用
    with pytest.raises(RegistryVocabError):
        to_registry_lifecycle_state("")


def test_write_boundary_rejects_shelved_until_catalog_ratifies_it(tmp_path: Path) -> None:
    """硬伤 3：catalog 机读词表未收编 shelved 时，写 "shelved" 被拒（越界有门禁，非静默）。"""
    eight = ["candidate", "backtest", "sim", "paper", "live", "monitoring", "decayed", "retired"]
    catalog = _catalog(tmp_path, values=eight)
    assert aligned_lifecycle_state_for_write(PRODUCTION, registry_path=catalog) == "live"
    with pytest.raises(RegistryVocabError):
        aligned_lifecycle_state_for_write(SHELVED, registry_path=catalog)


def test_write_boundary_accepts_shelved_after_catalog_extension(tmp_path: Path) -> None:
    """收编后（YAML 块由总筹落地）同一路径转绿——证明卡的是词表而非硬编码放行。"""
    nine = [
        "candidate",
        "backtest",
        "sim",
        "paper",
        "live",
        "monitoring",
        "decayed",
        "retired",
        "shelved",
    ]
    catalog = _catalog(tmp_path, values=nine)
    assert aligned_lifecycle_state_for_write(SHELVED, registry_path=catalog) == "shelved"
    values, source = registry_lifecycle_vocabulary(catalog)
    assert source == "catalog_machine_readable" and "shelved" in values


def test_missing_machine_readable_field_falls_back_and_is_loud(tmp_path: Path) -> None:
    """诚实回退：无机读字段（今天的事实）→ builtin_provisional，且 report 标出来源。"""
    catalog = _catalog(tmp_path, values=None)
    values, source = registry_lifecycle_vocabulary(catalog)
    assert values == REGISTRY_LIFECYCLE_STATES_PROVISIONAL
    report = vocab_report(catalog)
    assert report.source == "builtin_provisional"
    assert "backtest" in report.registry_only_values, "注册表独有价值（FSM 无边可达）须可见"


def test_vocab_does_not_invent_decayed_edge() -> None:
    """禁越界自证：本件只做拼写，decayed 不得被映射成任何 FSM 词的替身。"""
    assert "decayed" not in set(FSM_STATE_TO_REGISTRY_STATE.values())
    with pytest.raises(RegistryVocabError):
        to_registry_lifecycle_state("decayed")
    with pytest.raises(RegistryVocabError):
        assert_registry_lifecycle_state("production", allowed_values=frozenset({"live"}))
    assert assert_registry_lifecycle_state("live", allowed_values=frozenset({"live"})) == "live"
