# [BLUEPRINT] MOD-INF-005 | scripts/governance/check_blueprint_compliance.py | §
# [MODULE] scripts.governance.check_blueprint_compliance
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""
[BLUEPRINT] DOM-GOV-001 | D:\\ZephyrAlpha\\docs\03_modules\\_domain-governance\blueprint.md | §3
[MODULE] scripts.governance.check_blueprint_compliance
[INVARIANTS] REQUIRED_SECTIONS 必须与蓝图+施工图模板 v2.0.0 COMPLIANCE_CHECKLIST 一致
[MODIFY-GUARD] __init__.py;script_manifest.yaml;蓝图模板v2.0.0
[CONSUMERS] CI pipeline;governance gate
[STABILITY] stable
[SAFETY] M
[AI_AUTONOMY] ai_modifiable
[ERROR_CONTRACT] sys.exit(1)
[TESTS] tests/governance/test_governance.py
"""

__manifest__ = """
args: []
description: '[BLUEPRINT] DOM-GOV-001 | D:\\ZephyrAlpha\\docs\03_modules\\_domain-governance\blueprint.md
  | §3'
dimensions:
- D1
priority: P2
timeout_seconds: 60
warn_only: false
"""


import argparse
import re
import sys
from pathlib import Path

REQUIRED_SECTIONS = {
    "overview": ("概述", "前置章节"),
    "pre_1": ("Vibe Coding", "前置章节"),
    "pre_2": ("安全删除", "前置章节"),
    "pre_3": ("必备链接", "前置章节"),
    "pre_4": ("已有类似功能", "前置章节"),
    "pre_5": ("涉及的文件范围", "前置章节"),
    "§0": ("代码对齐验证", "主章节"),
    "§0.1": ("代码文件清单", "子章节"),
    "§0.2": ("对齐验证矩阵", "子章节"),
    "§0.3": ("版本-代码映射", "子章节"),
    "§0.4": ("SSoT与责任唯一性", "子章节"),  # v2.0.0 补齐
    "§0.5": ("代码目录唯一性", "子章节"),  # v2.0.0 补齐
    "§0.6": ("四图对齐视图", "子章节"),  # v2.0.0 新增
    "§1": ("设计背景与目标", "主章节"),
    "§1.1": ("背景", "子章节"),
    "§1.2": ("目标范围", "子章节"),
    "§1.4": ("运行场景约束", "子章节"),
    "§1.5": ("利益相关者", "子章节"),
    "§1.6": ("差距", "子章节"),
    "§1.7": ("典型场景", "子章节"),
    "§2": ("模块边界", "主章节"),
    "§2.1": ("职责边界", "子章节"),
    "§3": ("架构设计", "主章节"),
    "§3.1": ("组件架构", "子章节"),
    "§3.2": ("数据流", "子章节"),
    "§3.3": ("状态生命周期", "子章节"),
    "§4": ("接口契约", "主章节"),
    "§4.1": ("公共 API", "子章节"),
    "§4.2": ("数据模型", "子章节"),
    "§4.3": ("输入契约", "子章节"),
    "§4.4": ("输出契约", "子章节"),
    "§4.5": ("MCP 接口", "子章节"),
    "§4.6": ("契约版本", "子章节"),
    "§4.7": ("OCP 扩展点", "子章节"),
    "§5": ("约束条件", "主章节"),
    "§5.1": ("技术约束", "子章节"),
    "§5.2": ("容量估算", "子章节"),
    "§5.3": ("迁移", "子章节"),
    "§5.4": ("非功能需求与服务水平", "子章节"),
    "§5.5": ("自动化触发机制", "子章节"),  # v2.0.0 补齐
    "§5.7": ("禁止模式与导入约束", "子章节"),
    "§6": ("错误处理", "主章节"),
    "§6.1": ("可观测性", "子章节"),
    "§6.2": ("退化矩阵", "子章节"),
    "§8": ("安全考量", "主章节"),
    "§9": ("测试策略", "主章节"),
    "§10": ("依赖关系", "主章节"),
    "§10.5": ("概念重叠声明", "子章节"),  # v2.0.0 补齐
    "§10.6": ("依赖链风险评级", "子章节"),  # v2.0.0 补齐
    "§11": ("产出物", "主章节"),
    "§12": ("集成目标", "主章节"),
    "§13": ("需要更新", "主章节"),
    "§14": ("风险", "主章节"),
    "§16": ("施工指引", "主章节"),
    "§16.7": ("参考实现规格", "子章节"),
    "§16.8": ("施工参考卡", "子章节"),
    "§16.10": ("故障与操作", "子章节"),
    "§16.12": ("并发操作", "子章节"),
    "§17": ("容量升级", "主章节"),
    "§18": ("决策记录", "主章节"),
    "glossary": ("术语表", "主章节"),
    "blindspots": ("已知问题", "主章节"),
    "maturity": ("成熟度", "主章节"),
    "roadmap": ("版本演进路线图", "主章节"),
    "checklist": ("自检与闭合清单", "主章节"),
}

REQUIRED_FRONTMATTER = [
    "module_id",
    "title",
    "version",
    "status",
    "layer",
    "actual_disk_path",
    "construction_progress",
    "belongs_to",
]


def check_blueprint(blueprint_path: str, warn_only: bool = False) -> int:
    path = Path(blueprint_path)
    if not path.exists():
        print(f"ERROR: 文件不存在: {blueprint_path}")
        return 2

    content = path.read_text(encoding="utf-8")
    content_lower = content.lower()
    headings = re.findall(r"^##+\s+(.+)$", content, re.MULTILINE)

    errors = 0
    warnings = 0

    fm_missing = []
    for field in REQUIRED_FRONTMATTER:
        if f"{field}:" not in content and f"{field} :" not in content:
            fm_missing.append(field)

    if fm_missing:
        print(f"  ❌ Frontmatter 缺失字段: {', '.join(fm_missing)}")
        errors += len(fm_missing)
    else:
        print("  ✅ Frontmatter: 全部必填字段存在")

    missing_sections = []
    found_sections = []
    for sec_id, (keyword, sec_type) in REQUIRED_SECTIONS.items():
        found = False
        for h in headings:
            if keyword.lower() in h.lower():
                found = True
                break
        if not found and keyword.lower() not in content_lower:
            missing_sections.append((sec_id, keyword, sec_type))
        else:
            found_sections.append(sec_id)

    main_missing = [s for s in missing_sections if s[2] == "主章节"]
    sub_missing = [s for s in missing_sections if s[2] == "子章节"]
    pre_missing = [s for s in missing_sections if s[2] == "前置章节"]
    total_pre = sum(1 for v in REQUIRED_SECTIONS.values() if v[1] == "前置章节")

    if pre_missing:
        print(f"  ❌ 前置章节缺失 ({len(pre_missing)}/{total_pre}):")
        for sid, kw, _ in pre_missing:
            print(f"    ❌ {sid}: {kw}")
        errors += len(pre_missing)
    else:
        print(f"  ✅ 前置章节: {total_pre}/{total_pre}")

    if main_missing:
        print(f"  ❌ 主章节缺失 ({len(main_missing)}/19):")
        for sid, kw, _ in main_missing:
            print(f"    ❌ {sid}: {kw}")
        errors += len(main_missing)
    else:
        print("  ✅ 主章节: 19/19")

    if sub_missing:
        print(f"  ⚠️ 子章节缺失 ({len(sub_missing)}/22):")
        for sid, kw, _ in sub_missing:
            print(f"    ❌ {sid}: {kw}")
        warnings += len(sub_missing)
    else:
        print("  ✅ 子章节: 22/22")

    total = len(REQUIRED_SECTIONS) + len(REQUIRED_FRONTMATTER)
    passed = total - errors - warnings
    compliance = passed / total * 100 if total > 0 else 0

    print(f"\n  合规率: {compliance:.0f}% ({passed}/{total})")

    if errors > 0:
        print(f"  结果: ❌ FAIL ({errors} 错误, {warnings} 警告)")
        return 1 if not warn_only else 0
    elif warnings > 0:
        print(f"  结果: ⚠️ WARN ({warnings} 警告)")
        return 0
    else:
        print("  结果: ✅ PASS")
        return 0


def main():
    parser = argparse.ArgumentParser(description="蓝图模板合规检查门禁")
    parser.add_argument("blueprint", nargs="+", help="蓝图文件路径")
    parser.add_argument("--warn-only", action="store_true", help="仅警告，不阻断")
    args = parser.parse_args()

    total_exit = 0
    for bp in args.blueprint:
        print(f"\n{'=' * 60}")
        print(f"检查: {bp}")
        print(f"{'=' * 60}")
        exit_code = check_blueprint(bp, args.warn_only)
        if exit_code != 0:
            total_exit = 1

    sys.exit(total_exit)


if __name__ == "__main__":
    main()
