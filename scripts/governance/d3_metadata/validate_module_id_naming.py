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
module_id / domain_id / submodule_id 格式校验真源（裁定#208 双轨制 + R2 治本修订）

本模块是 module_id / domain_id / submodule_id 格式校验的唯一责任点，被以下门禁/脚本 import 复用：
  - check_naming_convention.py（N-06 GATE-11 pre-commit 自动触发）
  - apply_depgraph.py（cmd_rename_domain / cmd_insert_domain / _validate_domain_naming NR-002）

治本修订历史（2026-07-05 R2）：
  - 废除 D-XXX-NNN 作为 module_id 派生轨的合法地位（原裁定#208 R1 旧派生轨之一，R2 修订前）
  - D-XXX-NNN 重定义为 submodule_id 专用（蓝图内部子模块编号，见 trae_028 gov_doc_009）
  - module_id 仅保留双轨：layer-master 轨 + domain-functional 派生轨（均为 MOD- 前缀）

正则真源（本文件是唯一真源）:
  - MODULE_ID_LAYER_MASTER_RE: MOD-{LAYER_CODE}-{SEQ}（如 MOD-INF-005）
  - MODULE_ID_DOMAIN_DERIVED_RE: MOD-{DOMAIN_FRAGMENT}[-NNN]（如 MOD-SHARED-002）
  - MODULE_ID_SHARED_RE: SH-{ABBR}-{NNN}（如 SH-DB-001）
  - SUBMODULE_ID_RE: D-{DOMAIN}-NNN（如 D-FACTOR-01，仅用于蓝图内部子模块编号）
  - DOMAIN_ID_RE: D_{DOMAIN}（如 D_GOVERNANCE，无序号）

程序化校验（供其他脚本 import）:
  from validate_module_id_naming import is_valid_module_id, is_valid_domain_id, is_valid_submodule_id
  ok, reason = is_valid_module_id("MOD-INF-005")        # (True, "")
  ok, reason = is_valid_domain_id("D_GOVERNANCE")      # (True, "")
  ok, reason = is_valid_submodule_id("D-FACTOR-01")    # (True, "")

注：CLI 手工模式已删除（GATE-11 pre-commit 已自动覆盖同等校验，消除冗余 + 真源分裂）。
    旧式单轨正则 VALID_MODULE_ID_PATTERN / NESTED_ID_PATTERN 一并删除（与三轨正则语义冲突）。
    R2 治本修订：MODULE_ID_D_PREFIX_RE 重命名为 SUBMODULE_ID_RE，作用域缩小至 submodule_id 校验。
"""

__manifest__ = """
args: []
description: module_id / domain_id / submodule_id 格式校验真源（裁定#208 双轨制 + R2 治本修订）
dimensions:
- D1
priority: P2
timeout_seconds: 60
warn_only: false
"""


import re

# ---------------------------------------------------------------------------
# 裁定#208 双轨制正则（真源：本文件）
# 被 check_naming_convention.py（N-06 GATE-11）和 apply_depgraph.py 复用
# ---------------------------------------------------------------------------
# 安全加固（红蓝对抗修复 P2-1~P2-4）：
#   [0-9] 替代 \d（防止全角数字 U+FF10-FF19 被 \d 匹配）
#   \Z 替代 $（防止尾部 \n 被 $ 匹配，$ 默认匹配换行前）
#   {1,20} 限制（防止超长输入如 10000 个 A 导致存储/日志膨胀）
#   SH- 轨支持 _ 下划线（与派生轨一致，如 SH-LLM_SEC-042）
MODULE_ID_LAYER_MASTER_RE = re.compile(r"^MOD-[A-Z][A-Z0-9]{1,5}-[0-9]+\Z")              # layer-master 轨: MOD-{LAYER_CODE}-{SEQ} 序号必填
MODULE_ID_DOMAIN_DERIVED_RE = re.compile(r"^MOD-[A-Z]{1,20}(?:_[A-Z]{1,20})*(?:-[0-9]+)?\Z")  # 派生轨: MOD-{DOMAIN_FRAGMENT}[-NNN] 序号可选
MODULE_ID_SHARED_RE = re.compile(r"^SH-[A-Z]{1,20}(?:_[A-Z]{1,20})*-[0-9]+\Z")           # 跨域共享轨: SH-{ABBR}-{NNN} 序号必填

# ---------------------------------------------------------------------------
# submodule_id 正则（R2 治本修订，2026-07-05）
# ---------------------------------------------------------------------------
# 历史：原 MODULE_ID_D_PREFIX_RE 作为 module_id 派生轨之一（裁定#208 R1 旧制，R2 修订前）
# 废除原因：D-XXX-NNN 与 MOD-{DOMAIN_FRAGMENT}[-NNN] 语义重叠导致 module_id 与
#           submodule_id 混淆，depgraph.realization_detection 通过 blueprint_id 关联
#           设计态与运营态时可能将子模块编号误识别为顶层蓝图
# 重定义：D-XXX-NNN 重定义为 submodule_id 专用（蓝图内部子模块编号，不进入
#         depgraph.nodes.blueprint_id，不进入 blueprint frontmatter module_id 字段）
# 真源：trae_028 gov_doc_009_submodule_id_convention
SUBMODULE_ID_RE = re.compile(r"^D-[A-Z]{1,20}(?:_[A-Z]{1,20})*-[0-9]+\Z")               # submodule_id: D-{DOMAIN}-NNN（蓝图内部子模块编号）


def is_valid_module_id(bp_id: str) -> tuple[bool, str]:
    """校验 module_id/blueprint_id 格式是否符合裁定#208 双轨制（R2 治本修订后）。

    真源：本函数是 module_id 格式校验的唯一责任点，被 check_naming_convention.py
    和 apply_depgraph.py 复用，消除正则重复定义。

    双轨（R2 治本修订后，2026-07-05）：
    - layer-master 轨: MOD-{LAYER_CODE}-{SEQ}（如 MOD-INF-005）
    - 派生轨: MOD-{DOMAIN_FRAGMENT}[-NNN]（如 MOD-SHARED-002）
    - 跨域共享轨: SH-{ABBR}-{NNN}（如 SH-DB-001）

    废除项（R2 治本修订）：
    - D-XXX-NNN 已不再作为 module_id 合法格式（重定义为 submodule_id 专用，
      见 is_valid_submodule_id 和 trae_028 gov_doc_009）

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
        return False, "D-XXX-NNN 已废弃为 module_id 派生轨（R2 治本修订，2026-07-05），重定义为 submodule_id 专用；module_id 必须使用 MOD- 或 SH- 前缀"
    return False, "module_id 必须以 MOD-/SH- 开头"


def is_valid_submodule_id(submodule_id: str) -> tuple[bool, str]:
    """校验 submodule_id 格式是否符合 D-{DOMAIN}-NNN 规范。

    真源：本函数是 submodule_id 格式校验的唯一责任点（R2 治本修订新增，2026-07-05）。

    submodule_id 作用域（见 trae_028 gov_doc_009）：
    - 仅用于蓝图正文 §sections/§modules/§lifecycle 等章节的引用
    - 不进入 blueprint frontmatter 的 module_id 字段
    - 不进入 depgraph.nodes.blueprint_id

    与 is_valid_module_id 的区别：
    - module_id:    MOD-{LAYER}-{SEQ} / MOD-{DOMAIN}[-NNN] / SH-{ABBR}-{NNN}
    - submodule_id: D-{DOMAIN}-NNN（如 D-FACTOR-01，仅蓝图内部引用）

    与 is_valid_domain_id 的区别：
    - domain_id:    D_{DOMAIN}（下划线+无序号，如 D_GOVERNANCE）
    - submodule_id: D-{DOMAIN}-NNN（连字符+序号，如 D-FACTOR-01）

    Args:
        submodule_id: 待校验的 submodule_id 字符串

    Returns:
        (是否合规, 失败原因)
    """
    if SUBMODULE_ID_RE.match(submodule_id):
        return True, ""
    return False, "submodule_id 必须为 D-{DOMAIN}-NNN 格式（如 D-FACTOR-01），DOMAIN 为大写字母+下划线片段，NNN 为数字序号"


# domain_id 格式正则（D_{DOMAIN} 无序号，与 submodule_id 的 D-{DOMAIN}-NNN 不同）
# 真源：本常量是 domain_id 格式校验的唯一正则，被 apply_depgraph.py 复用
#       （cmd_rename_domain + cmd_merge_domain + cmd_insert_domain + _validate_domain_naming NR-002 均复用本常量，消除硬编码分裂）
# 与 NR-002 YAML 真源（domain_naming_rules.yaml）语义一致：全大写字母+数字+下划线
# 项目标准（裁定#ARCH-target_layer_v1.0.0）：D_ 前缀（下划线），禁止 D- 连字符
# 安全加固：\Z 替代 $（换行安全，P2-2）+ {0,59} 长度限制（防超长输入，P2-3）
DOMAIN_ID_RE = re.compile(r"^D_[A-Z][A-Z0-9_]{0,59}\Z")


def is_valid_domain_id(domain_id: str) -> tuple[bool, str]:
    """校验 domain_id 格式是否符合 D_{DOMAIN} 规范（无序号）。

    真源：本函数是 domain_id 格式校验的唯一责任点，被 apply_depgraph.py 复用。

    与 is_valid_module_id / is_valid_submodule_id 的区别：
    - domain_id:    D_{DOMAIN}（下划线+无序号，如 D_GOVERNANCE）
    - module_id:    MOD-{LAYER}-{SEQ} / MOD-{DOMAIN}[-NNN] / SH-{ABBR}-{NNN}
    - submodule_id: D-{DOMAIN}-NNN（连字符+序号，如 D-FACTOR-01，R2 治本修订后）

    Args:
        domain_id: 待校验的 domain_id 字符串

    Returns:
        (是否合规, 失败原因)
    """
    if DOMAIN_ID_RE.match(domain_id):
        return True, ""
    return False, "domain_id 必须为 D_{DOMAIN} 格式（如 D_GOVERNANCE），DOMAIN 为大写字母+数字+下划线，无序号"
