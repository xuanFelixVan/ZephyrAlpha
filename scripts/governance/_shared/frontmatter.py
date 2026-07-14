# [BLUEPRINT] MOD-GOV-SCRIPTS
# [MODULE] scripts.governance._shared.frontmatter
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES]
# [CONSUMERS] scripts.governance.d5_architecture.validators.validate_ssot; scripts.ops.verify_header_completeness; scripts.governance.d3_metadata.check_frontmatter_metadata; scripts.governance.d3_metadata.backfill_ttl_metadata
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 本文件是所有文件头部格式解析的唯一真源（SSoT）；6 格式：.md→parse_frontmatter / .py+.sh+.ps1+.mmd→parse_py_header / .yaml→parse_byaml_anchor / .json→parse_json_meta；PY_HEADER_PATTERN 正则也在此定义；新 AI 想解析任何文件头部格式前必须先查本文件——扩展已有函数，勿新建解析器
# [MODIFY-GUARD] trae_047_engineering_file_header.yaml; capability_canonical_file_registry.yaml capability_id=file_header_parser
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 解析失败返回 None（不抛异常）；文件不存在返回 None
# [TESTS] tests/test_frontmatter_ssot.py
# [TTL] task_bound
"""文件头部格式解析 SSoT（Single Source of Truth）

6 种文件头部格式的统一解析入口（对标 trae_047 GOV-ENG-002）：

| 格式    | 适用扩展名              | 解析器                | 字段形式                |
|---------|------------------------|----------------------|------------------------|
| D_md    | .md                    | parse_frontmatter    | YAML frontmatter       |
| A_full  | .py（code/script）     | parse_py_header      | # [FIELD] value 注释行 |
| A_test  | .py（test）            | parse_py_header      | # [FIELD] value 注释行 |
| E_shell | .sh / .ps1 / .mmd      | parse_py_header      | # [FIELD] value 注释行 |
| B_yaml  | .yaml                  | parse_byaml_anchor   | # --- 治理锚定 --- 块  |
| C_json  | .json（contract/schema）| parse_json_meta     | {"_meta": {...}} 字段  |

A_full/A_test/E_shell 共用 parse_py_header——三者都是 `# [FIELD] value` 注释行格式，
仅字段数不同（A_full=15, A_test=7, E_shell=5），正则 `PY_HEADER_PATTERN` 统一匹配。

新 AI 想解析任何文件头部格式前，必须先查本文件——扩展已有函数，勿新建解析器。
"""
import json
import re

import yaml

# frontmatter 结束符正则：行首 --- 后跟可选空格和换行
# 不能用 text.find("---", 3)，因为 frontmatter 值里可能包含 ---（如 module_id: KE-005---audit）
_FM_END_PATTERN = re.compile(r"\n---[ \t]*\n?")


def parse_frontmatter(text_or_path):
    """解析 .md 文件的 YAML frontmatter（D_md 格式）。

    Args:
        text_or_path: 文件内容字符串，或文件路径（短字符串无换行时按路径处理）。

    Returns:
        (metadata, body) 元组：metadata 为 dict（无 frontmatter 时为空 dict），
        body 为 frontmatter 之后的正文。
    """
    if isinstance(text_or_path, str) and len(text_or_path) < 260 and "\n" not in text_or_path:
        try:
            with open(text_or_path, encoding="utf-8") as f:
                text = f.read()
        except OSError:
            text = str(text_or_path)
    else:
        text = str(text_or_path)
    metadata = {}
    body = text
    if text.startswith("---"):
        # 查找行首 --- 作为 frontmatter 结束符
        fm_match = _FM_END_PATTERN.search(text[3:])
        if fm_match:
            end = 3 + fm_match.start()
            try:
                metadata = yaml.safe_load(text[3:end]) or {}
            except Exception:
                metadata = {}
            body = text[3 + fm_match.end() :].lstrip("\n")
    return metadata, body


def parse_frontmatter_from_file(filepath):
    """从文件读取并解析 .md frontmatter（D_md 格式）。"""
    with open(filepath, encoding="utf-8") as f:
        text = f.read()
    return parse_frontmatter(text)


# ── .py / .sh / .ps1 / .mmd 文件注释行头部解析（A_full / A_test / E_shell 格式）──
# 公开名（无下划线前缀）：允许 verify_header_completeness.py 等同包脚本 import 复用
# 格式：# [FIELD] value（如 # [BLUEPRINT] MOD-INF-005 | path | §）
# A_full 15字段 / A_test 7字段 / E_shell 5字段——仅字段数不同，正则统一
PY_HEADER_PATTERN = re.compile(r"^#\s*\[([\w-]+)\]\s?(.*)")


def parse_py_header(content: str) -> dict | None:
    """解析 .py/.sh/.ps1/.mmd 文件的注释行头部（A_full/A_test/E_shell 格式）。

    扫描前 30 行，匹配 `# [FIELD] value` 注释行，返回字段名→值的 dict。
    键名统一小写化（如 BLUEPRINT→blueprint）。

    Args:
        content: 文件内容字符串。

    Returns:
        字段 dict（无匹配时返回 None）。
    """
    fields: dict[str, str] = {}
    for line in content.splitlines()[:30]:
        m = PY_HEADER_PATTERN.match(line.rstrip())
        if m:
            fields[m.group(1).lower()] = m.group(2).strip()
    return fields if fields else None


def parse_py_header_from_file(filepath) -> dict | None:
    """从文件读取并解析 .py/.sh/.ps1/.mmd 注释行头部。"""
    with open(filepath, encoding="utf-8") as f:
        content = f.read()
    return parse_py_header(content)


# ── .yaml 文件治理锚定块解析（B_yaml 格式）──
# 格式：
#   # --- 治理锚定 ---
#   # blueprint: {module_id} | {blueprint_path} | §{N}
#   # module_id: {module_id}
#   # stability: {frozen|stable|evolving|volatile}
#   # safety_level: {H|M|L}
#   # ai_autonomy: {immutable_core|human_gated|ai_modifiable}
#   # ttl: {permanent|task_bound}
#   # --- 治理锚定结束 ---
_BYAML_ANCHOR_START = "治理锚定"
_BYAML_ANCHOR_END = "治理锚定结束"


def parse_byaml_anchor(content: str) -> dict | None:
    """解析 .yaml 文件的治理锚定块（B_yaml 格式）。

    扫描前 30 行，定位 `# --- 治理锚定 ---` 到 `# --- 治理锚定结束 ---` 之间的注释块，
    提取 blueprint/module_id/stability/safety_level/ai_autonomy/ttl 字段。

    注意：必须先检查 END 再检查 START——"治理锚定"是"治理锚定结束"的子串，
    若先检查 START 会把结束行误判为开始行（子串 bug 修复）。

    Args:
        content: 文件内容字符串。

    Returns:
        字段 dict（无锚定块时返回 None）。
    """
    info: dict[str, str] = {}
    in_anchor = False
    for line in content.splitlines()[:30]:
        # 必须先检查 END——"治理锚定"是"治理锚定结束"的子串
        if in_anchor and _BYAML_ANCHOR_END in line:
            break
        if _BYAML_ANCHOR_START in line:
            in_anchor = True
            continue
        if not in_anchor:
            continue
        # blueprint: module_id | path | §N（支持多段 | 分隔，取前两段）
        m = re.match(r"#\s*blueprint:\s*(.+?)(?:\s*\|\s*(.+?))?(?:\s*\|\s*.+)?$", line)
        if m:
            info["blueprint_id"] = m.group(1).strip()
            if m.group(2):
                info["blueprint_path"] = m.group(2).strip()
            continue
        # module_id / stability / safety_level / ai_autonomy / ttl
        m = re.match(r"#\s*(\w+):\s*(.+)$", line)
        if m:
            key = m.group(1).strip()
            val = m.group(2).strip()
            if key in ("module_id", "stability", "safety_level", "ai_autonomy", "ttl"):
                info[key] = val
    return info if info else None


def parse_byaml_anchor_from_file(filepath) -> dict | None:
    """从文件读取并解析 .yaml 治理锚定块（B_yaml 格式）。"""
    with open(filepath, encoding="utf-8") as f:
        content = f.read()
    return parse_byaml_anchor(content)


# ── .json 文件 _meta 字段解析（C_json 格式）──
# 格式：{"_meta": {"blueprint": "...", "module_id": "...", "stability": "...",
#          "safety_level": "...", "ai_autonomy": "...", "ttl": "..."}, ...}


def parse_json_meta(content: str) -> dict | None:
    """解析 .json 文件的 _meta 字段（C_json 格式）。

    用 json.loads 解析整个文件，提取顶层 `_meta` 键的值。
    _meta 包含 blueprint/module_id/stability/safety_level/ai_autonomy/ttl 字段。

    Args:
        content: JSON 文件内容字符串。

    Returns:
        _meta 字段 dict（无 _meta 或解析失败时返回 None）。
    """
    try:
        data = json.loads(content)
    except (json.JSONDecodeError, TypeError):
        return None
    if not isinstance(data, dict):
        return None
    meta = data.get("_meta")
    if not isinstance(meta, dict):
        return None
    return meta


def parse_json_meta_from_file(filepath) -> dict | None:
    """从文件读取并解析 .json _meta 字段（C_json 格式）。"""
    with open(filepath, encoding="utf-8") as f:
        content = f.read()
    return parse_json_meta(content)
