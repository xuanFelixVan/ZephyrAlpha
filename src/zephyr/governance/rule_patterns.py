# [BLUEPRINT] MOD-GOV-rule_patterns | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md
# [MODULE] zephyr.governance.rule_patterns
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] (none — pure constants module)
# [CONSUMERS] zephyr.governance.commit_gates.r5_digit_suffix_gate; zephyr.governance.commit_gates.create_guard; scripts/governance/d5_architecture/validators/validate_directory_structure.py; scripts/governance/d3_metadata/validate_rule_frontmatter.py; scripts/generate_pathway_registry.py; scripts/governance/generators/generate_path_ownership_map.py; scripts/governance/d5_architecture/validators/validate_ssot_construction_progress.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 治理规则正则模式唯一真源——gate 与 validator 共同 import,禁止在其他文件重新定义同类正则;每个正则标注 trae_028 规则来源
# [MODIFY-GUARD] 正则模式变更 MUST 同步更新 trae_028 YAML 真源定义
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 无运行时错误(纯常量模块)
# [TESTS] tests/governance/test_rule_patterns.py
# [A_module] module_id=MOD-GOV-rule_patterns | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""rule_patterns.py — 治理规则正则模式唯一真源 (SSoT)

病根 (2026-07-02 SSoT 审计发现):
- _DIGIT_SUFFIX_RE 在 r5_digit_suffix_gate.py 和 validate_directory_structure.py 各定义一次
- _RULE_NAME_RE (DIM-5) 在 create_guard.py 和 validate_rule_frontmatter.py 各定义一次
- 无共享正则模块, gate 与 validator 各自复制, 正则变更无法同步

治本:
- 本模块集中定义治理规则正则, gate (src/) 和 validator (scripts/) 共同 import
- 每个正则标注 trae_028 规则来源, 确保可追溯
- 对标 SCRIPT-QUALITY-001 D-D-04 (同一概念只在一处定义)

架构边界:
- src/zephyr/ 是 runtime 代码 (importable as zephyr.*)
- scripts/ 是治理脚本 (可 import src/, 反之不可)
- 本模块在 src/ 下, 两边均可 import (scripts/ 通过 _shared.constants bootstrap sys.path)

Usage::

    from zephyr.governance.rule_patterns import DIGIT_SUFFIX_RE, RULE_NAME_RE
"""

from __future__ import annotations

import re

__all__ = [
    "DIGIT_SUFFIX_RE",
    "RULE_NAME_RE",
    "MODULE_ID_RE",
]

# R5 数字后缀禁止——_\d+ 结尾
# 真源: trae_028_doc_structure_naming.yaml L1224-1228 gov_doc_003_directory_semantics R5
# 消费者: r5_digit_suffix_gate.py (commit-time 硬阻断) + validate_directory_structure.py (全量 warning-only)
DIGIT_SUFFIX_RE = re.compile(r"_\d+$")

# DIM-5 规则文件名主题前缀——trae_NNN_<主题>_<描述>.yaml
# 真源: trae_028_doc_structure_naming.yaml DIM-5 + ARCH-037
# 消费者: create_guard.py (commit-time 新规则文件名校验) + validate_rule_frontmatter.py (全量 frontmatter 校验)
RULE_NAME_RE = re.compile(r"^trae_\d+_(.+)\.yaml$")


# blueprint.md module_id 字段提取——^module_id:\s*(.+)$
# 真源: trae_028_doc_structure_naming.yaml (module_id 字段格式)
# 消费者: generate_pathway_registry.py + generate_path_ownership_map.py + validate_ssot_construction_progress.py
# (ARCH-033 Phase 7 SSoT 收敛 2026-07-02: 3处真重复集中到此处)
MODULE_ID_RE = re.compile(r"^module_id:\s*(.+)$", re.MULTILINE)
