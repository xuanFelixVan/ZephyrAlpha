# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.io.frontmatter_utils
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-016 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
frontmatter_utils.py — Markdown/YAML frontmatter 解析 SSoT

根因修复：此前 frontmatter 解析逻辑在 src/zephyr/ 下 6 个文件中
重复实现（kb/ 五门禁 + dos_launcher），scripts/governance/ 下 10 个文件
手动实现 content.find("---", 3) + yaml.safe_load。

任何解析 bug（如 YAML 解析边界条件）需改 16+ 处。

对标：
  - Python markdown-frontmatter 库：统一解析接口
  - scripts/governance/_shared/frontmatter.py（治理脚本侧的 SSoT）
  - DRY principle: Don't Repeat Yourself

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: content 参数
#   fields: 参数 content，类型注解 str
#   code: frontmatter_utils.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: filepath 参数
#   fields: 参数 filepath，类型注解 Path | str
#   code: frontmatter_utils.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① parse_frontmatter
#   name_en: parse_frontmatter
#   intro: 解析 Markdown 文件的 YAML frontmatter。
#   desc: 解析 Markdown 文件的 YAML frontmatter。 Args: content: 文件完整内容字符串。 Returns: 解析后的 frontmatter 字典，…；源码 L98-L122
#   inputs: content
#   outputs: dict | None
# - id: A2
#   name_zh: ② parse_frontmatter_from_file
#   name_en: parse_frontmatter_from_file
#   intro: 从文件路径解析 frontmatter。
#   desc: 从文件路径解析 frontmatter。 Args: filepath: 文件路径。 Returns: 解析后的 frontmatter 字典，若文件不存在或无 frontmat…；源码 L125-L139
#   inputs: filepath
#   outputs: dict | None
# - id: A3
#   name_zh: ③ parse_yaml_header
#   name_en: parse_yaml_header
#   intro: 解析 YAML 文件的注释头 + 顶层字段。
#   desc: 解析 YAML 文件的注释头 + 顶层字段。 用于 .yaml/.yml 文件（无 --- 分隔符），提取顶层键值对。 Args: content: YAML 文件完整内容字符串…；源码 L142-L157
#   inputs: content
#   outputs: dict | None
# - id: A4
#   name_zh: ④ extract_body
#   name_en: extract_body
#   intro: 提取 Markdown 文件 frontmatter 之后的正文部分。
#   desc: 提取 Markdown 文件 frontmatter 之后的正文部分。 Args: content: 文件完整内容字符串。 Returns: frontmatter 之后的正文，…；源码 L160-L174
#   inputs: content
#   outputs: str
# 层: 输出
# - id: O1
#   name_zh: dict | None
#   name_en: dict | None
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 见模块头 [CONSUMERS]
# - id: O2
#   name_zh: str
#   name_en: str
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> A4
# A4 --> O1
"""

from pathlib import Path

import yaml


def parse_frontmatter(content: str) -> dict | None:
    """解析 Markdown 文件的 YAML frontmatter。

    Args:
        content: 文件完整内容字符串。

    Returns:
        解析后的 frontmatter 字典，若无 frontmatter 则返回 None。

    Example::

        >>> parse_frontmatter("---\\ntitle: Hello\\n---\\nBody")
        {'title': 'Hello'}
    """
    if not content.startswith("---"):
        return None
    end = content.find("\n---", 3)
    if end == -1:
        return None
    fm_text = content[3:end]
    try:
        result = yaml.safe_load(fm_text)
        return result if isinstance(result, dict) else None
    except yaml.YAMLError:
        return None


def parse_frontmatter_from_file(filepath: Path | str) -> dict | None:
    """从文件路径解析 frontmatter。

    Args:
        filepath: 文件路径。

    Returns:
        解析后的 frontmatter 字典，若文件不存在或无 frontmatter 则返回 None。
    """
    filepath = Path(filepath)
    try:
        content = filepath.read_text(encoding="utf-8")
    except (FileNotFoundError, UnicodeDecodeError):
        return None
    return parse_frontmatter(content)


def parse_yaml_header(content: str) -> dict | None:
    """解析 YAML 文件的注释头 + 顶层字段。

    用于 .yaml/.yml 文件（无 --- 分隔符），提取顶层键值对。

    Args:
        content: YAML 文件完整内容字符串。

    Returns:
        解析后的顶层字典，若解析失败则返回 None。
    """
    try:
        result = yaml.safe_load(content)
        return result if isinstance(result, dict) else None
    except yaml.YAMLError:
        return None


def extract_body(content: str) -> str:
    """提取 Markdown 文件 frontmatter 之后的正文部分。

    Args:
        content: 文件完整内容字符串。

    Returns:
        frontmatter 之后的正文，若无 frontmatter 则返回原始内容。
    """
    if not content.startswith("---"):
        return content
    end = content.find("\n---", 3)
    if end == -1:
        return content
    return content[end + 4 :].lstrip("\n")


__all__ = [
    "extract_body",
    "parse_frontmatter",
    "parse_frontmatter_from_file",
    "parse_yaml_header",
]
