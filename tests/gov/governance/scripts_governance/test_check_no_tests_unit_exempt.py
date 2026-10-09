# [A_test] module_id: scripts.governance.d7_code.check_no_tests_unit | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.governance.scripts_governance.test_check_no_tests_unit_exempt
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] pytest; scripts.governance.d7_code.check_no_tests_unit
# [CONSUMERS] pytest 自动发现
# [STARTUP] python -m pytest tests/gov/governance/scripts_governance/test_check_no_tests_unit_exempt.py
# [MATURITY] testing
# [INVARIANTS] no-tests-unit 豁免清单扩容（2026-10-09 SD 车道平权扩容批）：案卷普查册
#              (*census*)/机生清单(*manifest*)/机生数据目录(_data/*.csv) 数据面入豁免
#              （历史路径=交割键，死信专案 01_ledger §三受阻件两案实证）；普通 .py 与
#              普查/清单同名 .py 代码面照拦（收窄不外溢）；复审期限 2027-01-09
# [MODIFY-GUARD] —
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即测试失败
# [TESTS] 本文件
# [TTL] task_bound
"""test_check_no_tests_unit_exempt.py — no-tests-unit 门案卷普查册/机生清单豁免腿单测。

背景（死信专案 01_ledger §三受阻件）：tests_cure_campaign/02_reference_census.md
（普查册正文照录 tests/unit=其记录对象本身）与 deadcure_campaign/
05_tests_restore_manifest.yaml（交割清单逐字收录被删测试树原路径=交割索引键）
被门内容级匹配拦死——清单数据非旧路径重引入。
"""

from __future__ import annotations

import importlib

_MOD = "scripts.governance.d7_code.check_no_tests_unit"


def _mod():
    return importlib.import_module(_MOD)


def test_census_md_exempt():
    """普查册数据面入豁免：*census*.md 含 tests/unit 字面量不拦（C2 案原样路径）。"""
    m = _mod()
    assert m._is_exempt("docs/_working/tests_cure_campaign/02_reference_census.md")


def test_manifest_yaml_exempt():
    """机生清单数据面入豁免：*manifest*.yaml 含 tests/unit 存量条目不拦（C3 案原样路径）。"""
    m = _mod()
    assert m._is_exempt("docs/_working/deadcure_campaign/05_tests_restore_manifest.yaml")
    assert m._is_exempt("docs/_working/final_delivery_campaign/baseline_manifest_v1.json")


def test_data_csv_exempt():
    """机生数据清单目录入豁免：_data/*.csv（防御扫描面扩展回归）。"""
    m = _mod()
    assert m._is_exempt("data/strategy_intake/_data/lane_manifest.csv")


def test_plain_py_still_blocked():
    """红证：普通 .py 含 tests/unit 活引用照拦（豁免不外溢到代码面）。"""
    m = _mod()
    assert not m._is_exempt("src/zephyr/foo/bar.py")
    assert not m._is_exempt("scripts/governance/legacy_path_probe.py")


def test_census_named_py_still_blocked():
    """收窄：普查/清单同名的 .py 代码面照拦——代码里 tests/unit 是活引用不是清单条目。"""
    m = _mod()
    assert not m._is_exempt("scripts/governance/make_census.py")
    assert not m._is_exempt("scripts/gen_manifest.py")


def test_manifest_md_not_exempt():
    """收窄：manifest 命名的 .md 不在机生清单豁免形态（清单=机读格式 md 属散文）。"""
    m = _mod()
    assert not m._is_exempt("docs/_working/restore_manifest_notes.md")


def test_scannable_ext_unchanged():
    """扫描面回归护栏：.py/.md/.yaml/.yml 可扫、csv/json 仍不在扫描面（豁免腿不扩扫描面）。"""
    m = _mod()
    assert m._is_scannable("a/b.py") and m._is_scannable("a/b.md") and m._is_scannable("a/b.yaml")
    assert not m._is_scannable("a/b.csv") and not m._is_scannable("a/b.json")
