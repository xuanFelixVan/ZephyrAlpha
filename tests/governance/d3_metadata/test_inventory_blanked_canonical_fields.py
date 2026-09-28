# [MODULE] tests.governance.d3_metadata.test_inventory_blanked_canonical_fields
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] stdlib（unittest/pathlib/importlib）；yaml
# [CONSUMERS] META-TESTS-COVERAGE；D3 盘点尺回归
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 纯 tmp_path 式测试：不写任何仓库/生产路径（宪法 §9.6 测试隔离）；
#   被测函数纯输入输出（registry 文本进、报告 dict 出），零 git 依赖路径单测可跑
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即测试失败；不吞异常
# [TESTS] self
# [TTL] permanent
# [COMPLETES_WHEN] 被测尺 inventory_blanked_canonical_fields.py 退役时本测试同步退役
"""tests for scripts/governance/d3_metadata/inventory_blanked_canonical_fields.py."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import yaml

_MODULE_PATH = (
    Path(__file__).resolve().parents[3]
    / "scripts"
    / "governance"
    / "d3_metadata"
    / "inventory_blanked_canonical_fields.py"
)
_SPEC = importlib.util.spec_from_file_location("d3_inventory_ruler", _MODULE_PATH)
_mod = importlib.util.module_from_spec(_SPEC)
sys.modules.setdefault("d3_inventory_ruler", _mod)
_SPEC.loader.exec_module(_mod)

_SPEC_DICT = {
    "name": "mini_registry",
    "path": "docs/_working/test/mini.yaml",
    "sections": [
        {
            "root": "entries",
            "identity": "module_path",
            "required": ["module_path", "name_zh", "plain_zh"],
        }
    ],
}


def _wrap(entries: list) -> str:
    return yaml.safe_dump({"entries": entries}, allow_unicode=True)


def test_blank_fields_counted_by_identity():
    disk = _wrap(
        [
            {"module_path": "a.py", "name_zh": "甲", "plain_zh": "做事情的工具说明"},
            {"module_path": "b.py", "name_zh": "", "plain_zh": None},
            {"module_path": "b.py", "name_zh": "乙", "plain_zh": "另一段大白话说明"},
        ]
    )
    result = _mod.inventory(_SPEC_DICT, head_text=disk, disk_text=disk)
    sec = result["sections"][0]
    # b.py 空白按身份键计 1（两行中 1 键），a.py 干净
    assert sec["blanked_identity_count"] == 1
    assert sec["blanked_entries"][0]["key"] == "b.py"
    assert set(sec["blanked_entries"][0]["blank_fields"]) == {"name_zh", "plain_zh"}
    assert result["key_diff_count"] == 0


def test_duplicate_identity_keys_per_section():
    disk = _wrap(
        [
            {"module_path": "a.py", "name_zh": "甲", "plain_zh": "第一份大白话说明"},
            {"module_path": "a.py", "name_zh": "甲二", "plain_zh": "第二份大白话说明"},
            {"module_path": "c.py", "name_zh": "丙", "plain_zh": "丙的大白话说明文"},
        ]
    )
    result = _mod.inventory(_SPEC_DICT, head_text=disk, disk_text=disk)
    sec = result["sections"][0]
    assert sec["duplicate_identity_count"] == 1
    assert sec["duplicates"] == {"a.py": 2}
    assert sec["duplicate_extra_occurrences"] == 1


def test_head_vs_disk_key_set_diff_both_directions():
    head = _wrap(
        [
            {"module_path": "kept.py", "name_zh": "留", "plain_zh": "两边都在的条目"},
            {"module_path": "lost.py", "name_zh": "失", "plain_zh": "HEAD 有磁盘无"},
        ]
    )
    disk = _wrap(
        [
            {"module_path": "kept.py", "name_zh": "留", "plain_zh": "两边都在的条目"},
            {"module_path": "new.py", "name_zh": "新", "plain_zh": "磁盘有 HEAD 无"},
        ]
    )
    result = _mod.inventory(_SPEC_DICT, head_text=head, disk_text=disk)
    kd = result["key_diff"][0]
    assert kd["missing_on_disk"] == ["lost.py"]
    assert kd["missing_on_head"] == ["new.py"]
    assert result["key_diff_count"] == 2


def test_structural_error_is_reported_not_raised():
    result = _mod.inventory(_SPEC_DICT, head_text=None, disk_text="entries: {not: a_list}")
    assert result["structural_error"] is not None
    assert result["blanked_count"] == 0


def test_build_report_verdict_and_totals():
    disk = _wrap(
        [
            {"module_path": "a.py", "name_zh": "", "plain_zh": "空白必填的条目项"},
            {"module_path": "a.py", "name_zh": "乙", "plain_zh": "重复身份的条目项"},
        ]
    )
    result = _mod.inventory(_SPEC_DICT, head_text=disk, disk_text=disk)
    report = _mod.build_report([result])
    assert report["totals"]["blanked_total"] == 1
    assert report["totals"]["duplicate_keys_total"] == 1
    assert report["verdict"] == "debt_present"

    clean = _mod.inventory(_SPEC_DICT, head_text=None, disk_text=_wrap([]))
    assert _mod.build_report([clean])["verdict"] == "clean"


def test_real_repo_specs_shape():
    """真册配置自检：identity/required 字段名与册头 entry_schema 对齐。"""
    mt = next(s for s in _mod.REGISTRY_SPECS if "module_translation" in s["name"])
    assert mt["sections"][0]["identity"] == "module_path"
    cc = next(s for s in _mod.REGISTRY_SPECS if "capability_canonical" in s["name"])
    roots = {s["root"] for s in cc["sections"]}
    assert {"capabilities", "creation_tokens"} <= roots
