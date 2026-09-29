# [q0213-RESCUE] 本件字节捞回自 q-0213 死袋 blob sha256=e93869078483dc88…（HEAD_MISSING 真孤儿，2026-09-29 车道 st-finaldel-crescue-20260929 落盘）。
# [TTL] permanent
# [STARTUP] test_only  (pytest 收集；无 scheduled_task)
# [CONSUMERS] CI / 本地 pytest：tests/governance/test_enforcement_surface_reconcile_canary.py 自检强制面对账尺的"能红"性
# [MODULE] tests.governance.test_enforcement_surface_reconcile_canary
# [INVARIANTS] 变异输入全部用内存 dict / tmp_path 注入，禁读改生产 gate_registry.yaml / in_process_gate_registry.yaml / rules/*.yaml。
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] stdlib(dataclasses/re/pathlib)；zephyr.gov_enforcement.rule_bridge.commit_gate_registry
# [MATURITY] draft
# [MODIFY-GUARD] 改白名单或判据须与 gate_registry 与 92 册验收尺同批
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 读不到实载集合必抛，禁降级为'无冲突'
# [TESTS] tests/gov_enforcement/test_union_priority_canary.py
"""强制面对账尺 · 能红变异自检（波 1A.3 + 1A.4；对应 92 册 G-05 并入的红证）。

证明这把尺"能红"：人为造两类变异输入
  (1) 名册声明 enabled 的一台门，进程内实载集合里没有 → 必须点名（装载缺口）。
  (2) files_trigger 声明的模式在 HEAD 全树零命中 → 必须点名（死触发）。
断言尺非空且精确点名该两台；同时以健康输入证明尺不空转（特异性）。
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# 让脚本在无 PYTHONPATH 注入时也能被导入：tests/governance/<f> → parents[2]=车道根
_HERE = Path(__file__).resolve()
_ROOT = _HERE.parents[2]
for _cand in (_ROOT, _ROOT / "src"):
    if str(_cand) not in sys.path and _cand.exists():
        sys.path.insert(0, str(_cand))

# [q0213-RESCUE] 适配：被测生产件 scripts/governance/meta/enforcement_surface_reconcile.py 尚未落 HEAD，模块级 importorskip 防收集炸弹，生产件落库后自动恢复实跑
pytest.importorskip("scripts.governance.meta.enforcement_surface_reconcile")

from scripts.governance.meta.enforcement_surface_reconcile import (  # noqa: E402
    normalize_rule_token,
    reconcile_rule_coverage,
    reconcile_trigger_surface,
)


# ── 健康基线：尺不该空转，也不该乱红 ─────────────────────────────────────────
def _healthy_inputs():
    roster = [
        {"gate_id": "GOOD-COND", "enabled": True, "files_trigger": ["src/app/"]},
        {"gate_id": "GOOD-ALWAYS", "enabled": True},  # 无触发 → always_fire，非红
        {"gate_id": "DISABLED-GATE", "enabled": False},  # 主动禁用实载缺 → 非红（归因表另议）
    ]
    catalog = {
        "GOOD-COND": {"gate_id": "GOOD-COND", "files_trigger": ["src/app/"], "always_run": False},
        "GOOD-ALWAYS": {"gate_id": "GOOD-ALWAYS", "files_trigger": "", "always_run": False},
        "DISABLED-GATE": {"gate_id": "DISABLED-GATE", "files_trigger": "", "always_run": False},
    }
    loaded = {"GOOD-COND", "GOOD-ALWAYS"}  # DISABLED 未装载属正常
    head = {"src/app/main.py", "docs/readme.md", "scripts/x.py"}
    return roster, catalog, loaded, head


def test_healthy_input_is_green():
    """健康输入 → 红名单空（证明尺不空转、不滥红）。"""
    roster, catalog, loaded, head = _healthy_inputs()
    rows, red = reconcile_trigger_surface(roster, catalog, loaded, head)
    assert red == []
    by_id = {r["gate_id"]: r for r in rows}
    assert by_id["GOOD-ALWAYS"]["always_fire"] is True and by_id["GOOD-ALWAYS"]["trigger_hit_count"] is None
    assert by_id["DISABLED-GATE"]["roster_enabled"] is False and by_id["DISABLED-GATE"]["in_process_loaded"] is False


# ── 核心红证：名册有门而实载集合里没有 / files_trigger 全树零命中 ─────────────
def test_ruler_goes_red_on_mutant():
    """两类变异输入 → 尺必须红，且精确点名两台。"""
    roster, catalog, loaded, head = _healthy_inputs()

    # 变异1：新增一台 enabled 门，但故意不放进 loaded_ids（名册有、实载 0）
    roster.append({"gate_id": "MUTANT-NOTLOADED", "enabled": True, "files_trigger": ["src/app/"]})
    catalog["MUTANT-NOTLOADED"] = {"gate_id": "MUTANT-NOTLOADED", "files_trigger": ["src/app/"], "always_run": False}

    # 变异2：新增一台 enabled 门，其 files_trigger 在 HEAD 全树零命中（命中 0）
    roster.append({"gate_id": "MUTANT-DEADTRIGGER", "enabled": True, "files_trigger": ["no_such_dir_zzz/"]})
    catalog["MUTANT-DEADTRIGGER"] = {
        "gate_id": "MUTANT-DEADTRIGGER",
        "files_trigger": ["no_such_dir_zzz/"],
        "always_run": False,
    }

    rows, red = reconcile_trigger_surface(roster, catalog, loaded, head)
    red_ids = {r["gate_id"] for r in red}

    assert red, "变异输入下尺必须非空（能红）"
    assert "MUTANT-NOTLOADED" in red_ids, "装载缺口（enabled 却未实载）必须点名"
    assert "MUTANT-DEADTRIGGER" in red_ids, "死触发（files_trigger 全树零命中）必须点名"
    # 健康台不得被连坐
    assert "GOOD-COND" not in red_ids and "GOOD-ALWAYS" not in red_ids
    assert "DISABLED-GATE" not in red_ids, "主动禁用的实载 0 不算红（归因表另处理）"

    # 点名理由可核（装载缺口/死触发各自可辨）
    reasons = {r["gate_id"]: r["reason"] for r in red}
    assert any("装载缺口" in x for x in reasons["MUTANT-NOTLOADED"])
    assert any("死触发" in x for x in reasons["MUTANT-DEADTRIGGER"])


def test_dead_subpattern_of_multi_trigger_gate_is_red():
    """多模式 files_trigger 中只要有一个子模式全树零命中即红（密钥门 password/api_key 同型）。"""
    roster = [{"gate_id": "SECRET-GATE", "enabled": True, "files_trigger": ["secret", "password_zzz"]}]
    catalog = {
        "SECRET-GATE": {"gate_id": "SECRET-GATE", "files_trigger": ["secret", "password_zzz"], "always_run": False}
    }
    loaded = {"SECRET-GATE"}
    head = {"src/secret_utils.py", "src/app.py"}  # 命中 secret，聚合 >0，但 password_zzz 死
    rows, red = reconcile_trigger_surface(roster, catalog, loaded, head)
    assert [r["gate_id"] for r in red] == ["SECRET-GATE"]
    assert red[0]["reason"][0].count("password_zzz") == 1
    row = rows[0]
    assert row["trigger_hit_count"] > 0 and row["trigger_hit_by_pattern"]["password_zzz"] == 0


# ── 规则↔执法面：别名归一 + 覆盖率 + 零匹配二级字段 ─────────────────────────
@pytest.mark.parametrize(
    "token",
    ["TRAE-060", "trae_060", "trae_60", "TRAE 60", "trae-0060"],
)
def test_rule_alias_normalization(token):
    assert normalize_rule_token(token) == 60


def test_rule_coverage_two_tier():
    rule_files = [
        "docs/01_policies_and_standards/rules/trae_060_inward.yaml",  # 真执法面命中
        "docs/01_policies_and_standards/rules/trae_074_worktree.yaml",  # 仅被提及（册），代码零匹配
    ]
    code_corpus = {
        "src/zephyr/gov_enforcement/some_gate.py": "此门禁执行 TRAE-060 判据（也写 trae_060 变体）",
    }
    catalog_corpus = {
        "docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml": "description: 关联 trae_074 与 trae_060",
    }
    rows, zero, stats = reconcile_rule_coverage(rule_files, code_corpus, catalog_corpus)
    by = {r["rule_no"]: r for r in rows}
    assert by["060"]["enforced_in_code"] is True
    # 074 代码零匹配 → 进 zero_match，且带"仅被册提及"二级字段
    assert by["074"]["enforced_in_code"] is False
    assert by["074"]["mentioned_in_catalog"] is True
    assert [z["rule_no"] for z in zero] == ["074"]
    assert stats["rules_enforced_in_code"] == 1 and stats["rules_total"] == 2
    assert stats["rules_mentioned_not_enforced"] == 1


def test_mutant_roster_file_injection(tmp_path):
    """tmp 注入变异门册（禁改生产册）→ 经 yaml 载入后尺仍须红。"""
    import yaml

    mutant = {
        "total_gates": 2,
        "gates": [
            {"gate_id": "ROSTER-ONLY-NOTLOADED", "enabled": True, "module_path": "x", "factory_function": "y"},
            {
                "gate_id": "ROSTER-DEAD-TRIGGER",
                "enabled": True,
                "module_path": "z",
                "factory_function": "w",
                "files_trigger": ["ghost_path_qq/"],
            },
        ],
    }
    p = tmp_path / "mutant_roster.yaml"
    p.write_text(yaml.safe_dump(mutant), encoding="utf-8")
    roster = yaml.safe_load(p.read_text(encoding="utf-8"))["gates"]
    rows, red = reconcile_trigger_surface(roster, {}, set(), {"real/file.py"})
    red_ids = {r["gate_id"] for r in red}
    assert red_ids == {"ROSTER-ONLY-NOTLOADED", "ROSTER-DEAD-TRIGGER"}
