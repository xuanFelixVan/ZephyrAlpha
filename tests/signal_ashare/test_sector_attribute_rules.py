# [BLUEPRINT] MOD-SIG-077 | 待统筹登记（blueprint 未建，真源=缺口总账 GAP-F-18 行）
# [MODULE] tests.signal_ashare.test_sector_attribute_rules
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] zephyr.signal_ashare.sector_attribute_rules
# [CONSUMERS] none
# [STARTUP] pytest
# [MATURITY] testing
# [INVARIANTS] 合成数据不触库不触网不读真实 yaml（字典注入）；pytest filterwarnings=error 兼容
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 测试失败=板块属性规则库逻辑缺陷
# [TESTS] 本文件
# [A_module] module_id=MOD-SIG-077_test | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""MOD-SIG-077 板块属性标注规则库 单元测试（GAP-F-18，字典注入不读文件）。

覆盖：规则解析（合法/非法载荷 fail-closed）、code 优先于 keyword、首命中生效、
三分类封闭集合、未命中→未标注不强行归类、批量标注、真实配置 yaml 加载冒烟
（仅校验文件存在时可解析，不断言具体规则数——规则演进不炸测试）、
JSON 可序列化。
"""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

import pytest

from zephyr.signal_ashare.sector_attribute_rules import (
    ATTR_BALANCED,
    ATTR_DEFENSIVE,
    ATTR_OFFENSIVE,
    ATTR_UNLABELED,
    SectorAttributeRule,
    annotate_sectors,
    load_attribute_mapping,
    parse_attribute_mapping,
    resolve_sector_attribute,
)

PAYLOAD: dict = {
    "version": "0.1.0",
    "rules": [
        {
            "key": "bank",
            "name": "银行",
            "attribute": "defensive",
            "code": "881386.SH",
            "keywords": ["银行"],
            "evidence": "锚定",
        },
        {
            "key": "tech_semiconductor",
            "name": "半导体",
            "attribute": "offensive",
            "code": "881319.SH",
            "keywords": ["半导体", "芯片"],
            "evidence": "锚定",
        },
        {
            "key": "liquor",
            "name": "白酒",
            "attribute": "balanced",
            "code": "",
            "keywords": ["白酒", "酿酒"],
            "evidence": "初拍",
        },
        {
            "key": "broker",
            "name": "证券(券商)",
            "attribute": "offensive",
            "code": "881394.SH",
            "keywords": ["证券", "券商"],
            "evidence": "锚定",
        },
    ],
}


# ------------------------------------------------------------------
# parse_attribute_mapping（载荷校验 fail-closed）
# ------------------------------------------------------------------


def test_parse_valid_payload() -> None:
    rules = parse_attribute_mapping(PAYLOAD)
    assert len(rules) == 4
    assert all(isinstance(r, SectorAttributeRule) for r in rules)
    assert rules[0].key == "bank"
    assert rules[0].attribute == ATTR_DEFENSIVE


def test_parse_rejects_non_mapping() -> None:
    with pytest.raises(ValueError, match="载荷非法"):
        parse_attribute_mapping(["not", "a", "dict"])  # type: ignore[arg-type]


def test_parse_rejects_bad_attribute() -> None:
    bad = {"rules": [{"key": "x", "name": "x", "attribute": "aggressive", "code": "", "keywords": []}]}
    with pytest.raises(ValueError, match="attribute 非法"):
        parse_attribute_mapping(bad)


def test_parse_rejects_empty_key_or_name() -> None:
    bad = {"rules": [{"key": "", "name": "x", "attribute": "offensive", "code": "", "keywords": []}]}
    with pytest.raises(ValueError, match="key/name 非法"):
        parse_attribute_mapping(bad)


def test_parse_rejects_duplicate_key() -> None:
    bad = {
        "rules": [
            {"key": "bank", "name": "银行", "attribute": "defensive", "code": "", "keywords": []},
            {"key": "bank", "name": "银行2", "attribute": "offensive", "code": "", "keywords": []},
        ]
    }
    with pytest.raises(ValueError, match="key 重复"):
        parse_attribute_mapping(bad)


def test_parse_rejects_bad_keywords_type() -> None:
    bad = {"rules": [{"key": "x", "name": "x", "attribute": "offensive", "code": "", "keywords": "半导体"}]}
    with pytest.raises(ValueError, match="keywords 非法"):
        parse_attribute_mapping(bad)


# ------------------------------------------------------------------
# resolve_sector_attribute（code 优先 / 首命中 / 未标注兜底）
# ------------------------------------------------------------------


def test_resolve_by_code_exact() -> None:
    rules = parse_attribute_mapping(PAYLOAD)
    out = resolve_sector_attribute(sector_name="某某板块", sector_code="881386.SH", rules=rules)
    assert out.attribute == ATTR_DEFENSIVE
    assert out.rule_key == "bank"
    assert out.match_via == "code"


def test_resolve_code_priority_over_keyword() -> None:
    rules = parse_attribute_mapping(PAYLOAD)
    # 名称含"芯片"（半导体关键词）但 code 命中银行 → code 优先
    out = resolve_sector_attribute(sector_name="芯片银行混合", sector_code="881386.SH", rules=rules)
    assert out.rule_key == "bank"
    assert out.match_via == "code"


def test_resolve_by_keyword_substring() -> None:
    rules = parse_attribute_mapping(PAYLOAD)
    out = resolve_sector_attribute(sector_name="白酒指数", sector_code="", rules=rules)
    assert out.attribute == ATTR_BALANCED
    assert out.rule_key == "liquor"
    assert out.match_via == "keyword"


def test_resolve_first_match_wins_on_multiple_keyword_hits() -> None:
    rules = parse_attribute_mapping(PAYLOAD)
    # "证券芯片"同时命中券商（序后）与半导体（序前）→ 首命中（半导体，rules 序第二）
    out = resolve_sector_attribute(sector_name="证券芯片", sector_code="", rules=rules)
    assert out.rule_key == "tech_semiconductor"
    assert out.attribute == ATTR_OFFENSIVE


def test_resolve_unlabeled_when_no_hit() -> None:
    rules = parse_attribute_mapping(PAYLOAD)
    out = resolve_sector_attribute(sector_name="林业", sector_code="881999.SH", rules=rules)
    assert out.attribute == ATTR_UNLABELED
    assert out.rule_key == ""
    assert out.match_via == "none"


def test_resolve_empty_name_and_code_unlabeled() -> None:
    rules = parse_attribute_mapping(PAYLOAD)
    out = resolve_sector_attribute(sector_name="", sector_code="", rules=rules)
    assert out.attribute == ATTR_UNLABELED


def test_resolve_rejects_bad_rules_type() -> None:
    with pytest.raises(ValueError, match="rules 元素非法"):
        resolve_sector_attribute(sector_name="银行", sector_code="", rules=["x"])  # type: ignore[list-item]


# ------------------------------------------------------------------
# annotate_sectors 批量
# ------------------------------------------------------------------


def test_annotate_sectors_batch() -> None:
    rules = parse_attribute_mapping(PAYLOAD)
    rows = [
        {"sector_code": "881386.SH", "sector_name": "银行"},
        {"sector_code": "881319.SH", "sector_name": "半导体"},
        {"sector_code": "", "sector_name": "白酒"},
        {"sector_code": "881999.SH", "sector_name": "林业"},
    ]
    out = annotate_sectors(rows, rules=rules)
    assert [r.attribute for r in out] == [ATTR_DEFENSIVE, ATTR_OFFENSIVE, ATTR_BALANCED, ATTR_UNLABELED]
    assert out[0].label == "防御"
    assert out[1].label == "进攻"
    assert out[2].label == "平衡"
    assert out[3].label == "未标注"


def test_annotate_sectors_rejects_bad_row() -> None:
    rules = parse_attribute_mapping(PAYLOAD)
    with pytest.raises(ValueError, match="行非法"):
        annotate_sectors([{"sector_code": 123}], rules=rules)  # type: ignore[list-item]


def test_result_json_serializable() -> None:
    rules = parse_attribute_mapping(PAYLOAD)
    out = resolve_sector_attribute(sector_name="银行", sector_code="881386.SH", rules=rules)
    json.dumps(asdict(out), ensure_ascii=False)


# ------------------------------------------------------------------
# 真实配置 yaml 冒烟（存在即可解析+规则非空+属性封闭）
# ------------------------------------------------------------------


def test_load_real_config_yaml_smoke() -> None:
    cfg = Path("config/sector_attribute_mapping.yaml")
    if not cfg.exists():
        pytest.skip("配置文件不存在（CI 环境差异）")
    rules = load_attribute_mapping(cfg)
    assert len(rules) > 0
    assert {r.attribute for r in rules} <= {ATTR_OFFENSIVE, ATTR_DEFENSIVE, ATTR_BALANCED}
    # 锚定码规则可经 code 命中
    bank = resolve_sector_attribute(sector_name="", sector_code="881386.SH", rules=rules)
    assert bank.rule_key == "bank"
    assert bank.match_via == "code"


def test_load_attribute_mapping_missing_file_fail_closed() -> None:
    with pytest.raises(ValueError, match="配置文件读取失败|配置解析失败"):
        load_attribute_mapping(Path("config/__nonexistent__.yaml"))
