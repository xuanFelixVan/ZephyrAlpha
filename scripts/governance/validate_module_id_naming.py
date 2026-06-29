# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §3-§7
# [MODULE] scripts.governance.validate_module_id_naming
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] scripts.governance.__init__
# [CONSUMERS] check_naming_convention.py (GATE-11 N-06); apply_depgraph.py (cmd_rename_domain/cmd_insert_domain/NR-002)
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] module_id 必须符合 PS-STD-001 §5 命名规范; 禁止嵌套编号
# [MODIFY-GUARD] PS-STD-001 §5; PS-REG-012 frontmatter_field_registry.yaml; module_id_registry.yaml
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] returns (bool, str); 不抛异常
# [TESTS]
# [TTL] task_bound

r"""
module_id / domain_id 格式校验真源（裁定#208 三轨制）

本模块是 module_id / domain_id 格式校验的唯一责任点，被以下门禁/脚本 import 复用：
  - check_naming_convention.py（N-06 GATE-11 pre-commit 自动触发）
  - apply_depgraph.py（cmd_rename_domain / cmd_insert_domain / _validate_domain_naming NR-002）

三轨正则真源（本文件是唯一真源）:
  - MODULE_ID_LAYER_MASTER_RE: MOD-{LAYER_CODE}-{SEQ}（如 MOD-INF-005）
  - MODULE_ID_DOMAIN_DERIVED_RE: MOD-{DOMAIN_FRAGMENT}[-NNN]（如 MOD-SHARED-002）
  - MODULE_ID_D_PREFIX_RE: D-{DOMAIN}-NNN（如 D-GOVERNANCE-001）
  - MODULE_ID_SHARED_RE: SH-{ABBR}-{NNN}（如 SH-DB-001）
  - DOMAIN_ID_RE: D-{DOMAIN}（如 D_GOVERNANCE，无序号）

程序化校验（供其他脚本 import）:
  from validate_module_id_naming import is_valid_module_id, is_valid_domain_id
  ok, reason = is_valid_module_id("MOD-INF-005")  # (True, "")
  ok, reason = is_valid_domain_id("D_GOVERNANCE")  # (True, "")

注：CLI 手工模式已删除（GATE-11 pre-commit 已自动覆盖同等校验，消除冗余 + 真源分裂）。
    旧式单轨正则 VALID_MODULE_ID_PATTERN / NESTED_ID_PATTERN 一并删除（与三轨正则语义冲突）。
"""

import re

# ---------------------------------------------------------------------------
# 裁定#208 三轨制正则（真源：本文件）
# 被 check_naming_convention.py（N-06 GATE-11）和 apply_depgraph.py 复用
# ---------------------------------------------------------------------------
# 安全加固（红蓝对抗修复 P2-1~P2-4）：
#   [0-9] 替代 \d（防止全角数字 U+FF10-FF19 被 \d 匹配）
#   \Z 替代 $（防止尾部 \n 被 $ 匹配，$ 默认匹配换行前）
#   {1,20} 限制（防止超长输入如 10000 个 A 导致存储/日志膨胀）
#   SH- 轨支持 _ 下划线（与 D-/派生轨一致，如 SH-LLM_SEC-042）
MODULE_ID_LAYER_MASTER_RE = re.compile(r"^MOD-[A-Z][A-Z0-9]{1,5}-[0-9]+\Z")              # layer-master 轨: MOD-{LAYER_CODE}-{SEQ} 序号必填
MODULE_ID_DOMAIN_DERIVED_RE = re.compile(r"^MOD-[A-Z]{1,20}(?:_[A-Z]{1,20})*(?:-[0-9]+)?\Z")  # 派生轨: MOD-{DOMAIN_FRAGMENT}[-NNN] 序号可选
MODULE_ID_D_PREFIX_RE = re.compile(r"^D-[A-Z]{1,20}(?:_[A-Z]{1,20})*-[0-9]+\Z")          # 派生轨: D-{DOMAIN}-NNN
MODULE_ID_SHARED_RE = re.compile(r"^SH-[A-Z]{1,20}(?:_[A-Z]{1,20})*-[0-9]+\Z")           # 跨域共享轨: SH-{ABBR}-{NNN} 序号必填


def is_valid_module_id(bp_id: str) -> tuple[bool, str]:
    """校验 module_id/blueprint_id 格式是否符合裁定#208 三轨制。

    真源：本函数是 module_id 格式校验的唯一责任点，被 check_naming_convention.py
    和 apply_depgraph.py 复用，消除正则重复定义。

    三轨：
    - layer-master 轨: MOD-{LAYER_CODE}-{SEQ}（如 MOD-INF-005）
    - 派生轨: MOD-{DOMAIN_FRAGMENT}[-NNN]（如 MOD-SHARED-002）/ D-{DOMAIN}-NNN
    - 跨域共享轨: SH-{ABBR}-{NNN}（如 SH-DB-001）

    Args:
        bp_id: 待校验的 module_id 或 blueprint_id 字符串

    Returns:
        (是否合规, 失败原因)：合规时原因为空字符串，不合规时给出格式说明
    """
    if bp_id.startswith("SH-"):
        if MODULE_ID_SHARED_RE.match(bp_id):
            return True, ""
        return False, "SH- 前缀必须为 SH-{ABBR}-{NNN} 格式（如 SH-DB-001）"
    if bp_id.startswith("MOD-"):
        if MODULE_ID_LAYER_MASTER_RE.match(bp_id) or MODULE_ID_DOMAIN_DERIVED_RE.match(bp_id):
            return True, ""
        return False, "MOD- 前缀必须为 layer-master 轨 MOD-{LAYER}-NNN 或派生轨 MOD-{DOMAIN}[-NNN]"
    if bp_id.startswith("D-"):
        if MODULE_ID_D_PREFIX_RE.match(bp_id):
            return True, ""
        return False, "D- 前缀必须为 D-{DOMAIN}-NNN 格式"
    return False, "module_id 必须以 MOD-/SH-/D- 开头"


# domain_id 格式正则（D-{DOMAIN} 无序号，与 blueprint_id 的 D- 轨 D-{DOMAIN}-NNN 不同）
# 真源：本常量是 domain_id 格式校验的唯一正则，被 apply_depgraph.py 复用
#       （cmd_rename_domain + cmd_insert_domain + _validate_domain_naming NR-002 均复用本常量，消除硬编码分裂）
# 与 NR-002 YAML 真源（domain_naming_rules.yaml）语义一致：全大写字母+数字+下划线
# 安全加固：\Z 替代 $（换行安全，P2-2）+ {0,59} 长度限制（防超长输入，P2-3）
DOMAIN_ID_RE = re.compile(r"^D-[A-Z][A-Z0-9_]{0,59}\Z")


def is_valid_domain_id(domain_id: str) -> tuple[bool, str]:
    """校验 domain_id 格式是否符合 D-{DOMAIN} 规范（无序号）。

    真源：本函数是 domain_id 格式校验的唯一责任点，被 apply_depgraph.py 复用。

    与 is_valid_module_id 的 D- 轨区别：
    - domain_id: D-{DOMAIN}（无序号，如 D_GOVERNANCE）
    - blueprint_id D- 轨: D-{DOMAIN}-NNN（有序号，如 D-GOVERNANCE-001）

    Args:
        domain_id: 待校验的 domain_id 字符串

    Returns:
        (是否合规, 失败原因)
    """
    if DOMAIN_ID_RE.match(domain_id):
        return True, ""
    return False, "domain_id 必须为 D-{DOMAIN} 格式（如 D_GOVERNANCE），DOMAIN 为大写字母+数字+下划线，无序号"
