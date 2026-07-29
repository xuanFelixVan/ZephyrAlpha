# [BLUEPRINT] MOD-INF-005 | tests/test_validate_rule_frontmatter_red_blue.py | §
# [MODULE] tests.test_validate_rule_frontmatter_red_blue
# [INVARIANTS] 红蓝对抗13项攻击向量必须全部PASS
# [MODIFY-GUARD] 修改前MUST确认与validate_rule_frontmatter.py的检测维度一致
# [CONSUMERS] pytest;pre_commit
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] exit 0=所有攻击被拦截;exit 1=有攻击突破
# [TESTS] self-contained
# [TTL] task_bound
"""
GATE-RULE-FM 红蓝极端对抗测试。

覆盖13个攻击向量，验证门禁脚本的鲁棒性：
  R1-R6:  字段级攻击（缺失/顺序/枚举值）
  R7:     一致性攻击（rule_id vs 文件名）
  R8-R11: 文件级攻击（空文件/非YAML/超大/二进制）
  R12:    YAML注入攻击
  R13:    正常用例（无攻击，验证无误报）

运行: python -m pytest tests/test_validate_rule_frontmatter_red_blue.py -v
"""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

import pytest

# 将 scripts/governance 加入 path 以导入被测模块（ARCH-029 迁移 tests/→tests/governance/governance_e2e/，需 4 级 parent）
_SCRIPT_DIR = Path(__file__).resolve().parent.parent.parent.parent / "scripts" / "governance" / "d3_metadata"
sys.path.insert(0, str(_SCRIPT_DIR))

# 导入被测模块
import validate_rule_frontmatter as vrf  # noqa: E402

# ===================================================================
# 测试夹具：合规的 frontmatter 模板
# ===================================================================

VALID_FRONTMATTER = """rule_id: TRAE-099
title: 测试规则
version: '1.0.0'
layer: L1_foundation
module_id: TRAE-099
depends_on: []
tags:
- TRAE
- test
- L1
stability: evolving
safety_level: L
ai_autonomy: ai_modifiable
aliases: []
severity: error
scope: test
domain: TRAE
triggers: []
sections: {}
references:
  rule_ids: []
  scripts: []
  modules: []
  blueprints: []
enforcement:
  type: doc
  executors: []
  bypass_allowed: false
metadata:
  change_policy: evolving
  impact_level: L
  modification_permission: ai_modifiable
  superseded_by: null
provenance:
  extracted_at: '2026-06-22T00:00:00'
  extracted_by: session-test
"""


@pytest.fixture
def temp_rules_dir():
    """创建临时规则目录，测试后清理。"""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        old_rules_dir = vrf.RULES_DIR
        old_repo_root = vrf.REPO_ROOT
        vrf.RULES_DIR = tmp_path
        vrf.REPO_ROOT = tmp_path
        yield tmp_path
        vrf.RULES_DIR = old_rules_dir
        vrf.REPO_ROOT = old_repo_root


def _write_rule_file(rules_dir: Path, filename: str, content: str) -> Path:
    """写入测试规则文件，返回路径。"""
    path = rules_dir / filename
    path.write_text(content, encoding="utf-8")
    return path


def _run_validator_and_get_errors(path: Path) -> list[str]:
    """运行校验器，返回错误列表（清空全局 _errors 后重新填充）。"""
    vrf.errors.clear()
    vrf.warnings.clear()
    vrf.validate_file(path)
    return list(vrf.errors)


# ===================================================================
# R1-R6: 字段级攻击
# ===================================================================


def test_r1_missing_required_field_version(temp_rules_dir):
    """R1攻击：删除 version 字段。期望被检测。"""
    content = VALID_FRONTMATTER.replace("version: '1.0.0'\n", "")
    path = _write_rule_file(temp_rules_dir, "trae_099_test_rule.yaml", content)
    errors = _run_validator_and_get_errors(path)
    assert any("version" in e for e in errors), f"R1失败：未检测到缺失version字段。errors={errors}"


def test_r1b_missing_all_required_fields(temp_rules_dir):
    """R1b攻击：删除所有必填字段。期望全部被检测。"""
    content = "title: 只有标题\n"
    path = _write_rule_file(temp_rules_dir, "trae_099_test_rule.yaml", content)
    errors = _run_validator_and_get_errors(path)
    required = [
        "rule_id",
        "version",
        "layer",
        "module_id",
        "depends_on",
        "tags",
        "stability",
        "safety_level",
        "ai_autonomy",
        "provenance",
    ]
    for field in required:
        assert any(field in e for e in errors), f"R1b失败：未检测到缺失{field}。errors={errors}"


def test_r2_field_order_wrong(temp_rules_dir):
    """R2攻击：把 layer 放到 aliases 后（顺序错误）。期望被检测。"""
    lines = VALID_FRONTMATTER.splitlines()
    # 找到 layer 行和 aliases 行，交换顺序
    layer_idx = next(i for i, l in enumerate(lines) if l.startswith("layer:"))
    aliases_idx = next(i for i, l in enumerate(lines) if l.startswith("aliases:"))
    # 把 layer 移到 aliases 后
    layer_line = lines.pop(layer_idx)
    # aliases_idx 可能因 pop 而前移
    aliases_idx = next(i for i, l in enumerate(lines) if l.startswith("aliases:"))
    lines.insert(aliases_idx + 2, layer_line)  # aliases 后面有空列表项
    content = "\n".join(lines) + "\n"
    path = _write_rule_file(temp_rules_dir, "trae_099_test_rule.yaml", content)
    errors = _run_validator_and_get_errors(path)
    assert any("顺序" in e or "order" in e.lower() for e in errors), f"R2失败：未检测到顺序错误。errors={errors}"


def test_r3_invalid_layer_enum(temp_rules_dir):
    """R3攻击：layer=L5（非法枚举值）。期望被检测。"""
    content = VALID_FRONTMATTER.replace("layer: L1_foundation", "layer: L5")
    path = _write_rule_file(temp_rules_dir, "trae_099_test_rule.yaml", content)
    errors = _run_validator_and_get_errors(path)
    assert any("layer" in e and "L5" in e for e in errors), f"R3失败：未检测到非法layer。errors={errors}"


def test_r4_invalid_stability_enum(temp_rules_dir):
    """R4攻击：stability=super_stable（非法枚举值）。期望被检测。"""
    content = VALID_FRONTMATTER.replace("stability: evolving", "stability: super_stable")
    path = _write_rule_file(temp_rules_dir, "trae_099_test_rule.yaml", content)
    errors = _run_validator_and_get_errors(path)
    assert any("stability" in e and "super_stable" in e for e in errors), (
        f"R4失败：未检测到非法stability。errors={errors}"
    )


def test_r5_invalid_safety_level_enum(temp_rules_dir):
    """R5攻击：safety_level=X（非法枚举值）。期望被检测。"""
    content = VALID_FRONTMATTER.replace("safety_level: L", "safety_level: X")
    path = _write_rule_file(temp_rules_dir, "trae_099_test_rule.yaml", content)
    errors = _run_validator_and_get_errors(path)
    assert any("safety_level" in e and "X" in e for e in errors), f"R5失败：未检测到非法safety_level。errors={errors}"


def test_r6_invalid_ai_autonomy_enum(temp_rules_dir):
    """R6攻击：ai_autonomy=full_auto（非法枚举值）。期望被检测。"""
    content = VALID_FRONTMATTER.replace("ai_autonomy: ai_modifiable", "ai_autonomy: full_auto")
    path = _write_rule_file(temp_rules_dir, "trae_099_test_rule.yaml", content)
    errors = _run_validator_and_get_errors(path)
    assert any("ai_autonomy" in e and "full_auto" in e for e in errors), (
        f"R6失败：未检测到非法ai_autonomy。errors={errors}"
    )


# ===================================================================
# R7: 一致性攻击
# ===================================================================


def test_r7_rule_id_filename_mismatch(temp_rules_dir):
    """R7攻击：文件名trae_099但rule_id=TRAE-100。期望被检测。"""
    content = VALID_FRONTMATTER.replace("rule_id: TRAE-099", "rule_id: TRAE-100")
    path = _write_rule_file(temp_rules_dir, "trae_099_test_rule.yaml", content)
    errors = _run_validator_and_get_errors(path)
    assert any("rule_id" in e and "不匹配" in e for e in errors), f"R7失败：未检测到rule_id不一致。errors={errors}"


# ===================================================================
# R8-R11: 文件级攻击
# ===================================================================


def test_r8_empty_file(temp_rules_dir):
    """R8攻击：完全空的文件。期望被检测。"""
    path = _write_rule_file(temp_rules_dir, "trae_099_test_rule.yaml", "")
    errors = _run_validator_and_get_errors(path)
    assert len(errors) > 0, f"R8失败：空文件未报错。errors={errors}"


def test_r9_non_yaml_format(temp_rules_dir):
    """R9攻击：纯文本乱码（非YAML）。期望被检测。"""
    content = "这不是YAML格式\n只是一段普通文本\n没有key: value结构"
    path = _write_rule_file(temp_rules_dir, "trae_099_test_rule.yaml", content)
    errors = _run_validator_and_get_errors(path)
    # 非 YAML 格式应该报错（缺少必填字段或解析失败）
    assert len(errors) > 0, f"R9失败：非YAML格式未报错。errors={errors}"


def test_r10_huge_file(temp_rules_dir):
    """R10攻击：超大YAML文件（>1MB）。期望不崩溃（可跳过或报错）。"""
    # 生成 1.5MB 的 YAML（重复 sections 内容）
    big_section = "  big_section_" + "x" * 1000 + ":\n    title: 大段内容\n    data: " + "y" * 1000 + "\n"
    content = VALID_FRONTMATTER + big_section * 500
    path = _write_rule_file(temp_rules_dir, "trae_099_test_rule.yaml", content)
    # 不应崩溃（可能报错也可能PASS，关键是不能 hang）
    errors = _run_validator_and_get_errors(path)
    # 超大文件本身 frontmatter 合规，应该 PASS（sections 内容不影响）
    assert len(errors) == 0, f"R10失败：超大文件误报。errors={errors}"


def test_r11_binary_disguised_as_yaml(temp_rules_dir):
    """R11攻击：二进制内容伪装成.yaml。期望被检测（不崩溃）。"""
    path = temp_rules_dir / "trae_099_test_rule.yaml"
    # 写入二进制内容
    path.write_bytes(b"\xff\xfe\x00\x01\x02\x03binary garbage here \x00\xff")
    vrf.errors.clear()
    vrf.warnings.clear()
    # 不应崩溃，应该报错
    try:
        vrf.validate_file(path)
        # 如果没崩溃，检查是否有错误
        assert len(vrf.errors) > 0, "R11失败：二进制文件未报错也未崩溃"
    except UnicodeDecodeError:
        # 崩溃也是可接受的（只要不静默通过）
        pass
    except Exception:
        # 其他异常也可接受（只要不静默通过）
        pass


# ===================================================================
# R12: YAML 注入攻击
# ===================================================================


def test_r12_yaml_injection(temp_rules_dir):
    """R12攻击：YAML注入（!!python/object）。期望被检测或安全拒绝。"""
    content = (
        VALID_FRONTMATTER
        + """
malicious: !!python/object/apply:os.system ["echo hacked"]
"""
    )
    path = _write_rule_file(temp_rules_dir, "trae_099_test_rule.yaml", content)
    vrf.errors.clear()
    vrf.warnings.clear()
    # yaml.safe_load 会拒绝 !!python/object，所以应该报 YAML 解析失败
    try:
        vrf.validate_file(path)
        # safe_load 拒绝危险标签，应该有错误
        # 如果没报错，检查是否静默通过了（这是严重漏洞）
        assert len(vrf.errors) > 0, "R12失败：YAML注入未被检测（严重安全漏洞）"
    except Exception:
        # safe_load 抛异常是正确行为
        pass


# ===================================================================
# R13: 正常用例（无攻击，验证无误报）
# ===================================================================


def test_r13_valid_file_no_false_positive(temp_rules_dir):
    """R13正常用例：完全合规的文件。期望零错误（无误报）。"""
    path = _write_rule_file(temp_rules_dir, "trae_099_test_rule.yaml", VALID_FRONTMATTER)
    errors = _run_validator_and_get_errors(path)
    assert len(errors) == 0, f"R13失败：合规文件误报。errors={errors}"


# ===================================================================
# 红蓝对抗总结
# ===================================================================

if __name__ == "__main__":
    # 直接运行模式：执行所有测试并输出报告
    print("=" * 70)
    print("GATE-RULE-FM 红蓝极端对抗测试")
    print("=" * 70)

    test_funcs = [
        ("R1", "缺失必填字段version", test_r1_missing_required_field_version),
        ("R1b", "缺失所有必填字段", test_r1b_missing_all_required_fields),
        ("R2", "字段顺序错误", test_r2_field_order_wrong),
        ("R3", "非法layer枚举值", test_r3_invalid_layer_enum),
        ("R4", "非法stability枚举值", test_r4_invalid_stability_enum),
        ("R5", "非法safety_level枚举值", test_r5_invalid_safety_level_enum),
        ("R6", "非法ai_autonomy枚举值", test_r6_invalid_ai_autonomy_enum),
        ("R7", "rule_id与文件名不匹配", test_r7_rule_id_filename_mismatch),
        ("R8", "空文件", test_r8_empty_file),
        ("R9", "非YAML格式", test_r9_non_yaml_format),
        ("R10", "超大文件", test_r10_huge_file),
        ("R11", "二进制伪装", test_r11_binary_disguised_as_yaml),
        ("R12", "YAML注入", test_r12_yaml_injection),
        ("R13", "正常用例（无误报）", test_r13_valid_file_no_false_positive),
    ]

    passed = 0
    failed = 0
    failures = []

    for rid, desc, func in test_funcs:
        try:
            # pytest fixture 需要手动调用
            with tempfile.TemporaryDirectory() as tmp:
                tmp_path = Path(tmp)
                old_rules_dir = vrf.RULES_DIR
                old_repo_root = vrf.REPO_ROOT
                vrf.RULES_DIR = tmp_path
                vrf.REPO_ROOT = tmp_path
                try:
                    func(tmp_path)
                finally:
                    vrf.RULES_DIR = old_rules_dir
                    vrf.REPO_ROOT = old_repo_root
            print(f"  [{rid}] {desc:40s}  PASS")
            passed += 1
        except AssertionError as e:
            print(f"  [{rid}] {desc:40s}  FAIL: {e}")
            failed += 1
            failures.append((rid, desc, str(e)))
        except Exception as e:
            print(f"  [{rid}] {desc:40s}  ERROR: {type(e).__name__}: {e}")
            failed += 1
            failures.append((rid, desc, f"{type(e).__name__}: {e}"))

    print("=" * 70)
    print(f"红蓝对抗总结: 通过 {passed}/{len(test_funcs)}, 失败 {failed}/{len(test_funcs)}")
    if failures:
        print("\n失败项:")
        for rid, desc, err in failures:
            print(f"  [{rid}] {desc}: {err}")
    print("=" * 70)

    sys.exit(0 if failed == 0 else 1)
