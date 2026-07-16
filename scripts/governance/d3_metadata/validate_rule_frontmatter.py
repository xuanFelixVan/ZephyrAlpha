# [BLUEPRINT] MOD-INF-005 | scripts/governance/d3_metadata/validate_rule_frontmatter.py | §
# [MODULE] scripts.governance.d3_metadata.validate_rule_frontmatter
# [DOMAIN]
# [DEPENDENCIES]
# [CONSUMERS] phase_manager;pre_commit
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 7标准字段必填;字段顺序固定;枚举值合法
# [MODIFY-GUARD] 修改前MUST确认与scaffold.py的RULE_TEMPLATE一致
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] exit 0=PASS;exit 1=FINDINGS;exit 2=ERROR
# [TESTS] tests/test_validate_rule_frontmatter.py
# [TTL] permanent
"""
GATE-RULE-FM: 校验所有 trae_XXX.yaml 的 frontmatter 7标准字段+顺序+枚举值合法性。

防止规则文件 frontmatter 漂移——配合 scaffold.py rule 模式的模板，
形成"出生防缺陷 + 后天防漂移"双重保险。

Dimensions:
  DIM-1: 7标准字段存在性 (rule_id/title/version/layer/module_id/depends_on/tags/stability/safety_level/ai_autonomy/provenance)
  DIM-2: 字段顺序 (标准顺序固定)
  DIM-3: 枚举值合法性 (layer/stability/safety_level/ai_autonomy)
  DIM-4: rule_id 与文件名一致性 (trae_XXX.yaml ↔ rule_id: TRAE-XXX)
  DIM-5: 文件名主题前缀 (ARCH-037, trae_NNN_<主题>_<描述>.yaml, 单段name=缺主题前缀)

Exit 1 on any FAIL -> pre_commit blocks the commit.
"""

from __future__ import annotations

__manifest__ = """
args: []
description: GATE-RULE-FM — trae_XXX.yaml frontmatter 7标准字段+顺序+枚举值校验
dimensions:
- D3
- D5
priority: P0
timeout_seconds: 30
warn_only: false
"""


import argparse
import re
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

import yaml

from _shared.constants import EXIT_FINDINGS, EXIT_PASS, GOV_DOCS_DIR, REPO_ROOT
from _shared.encoding import ensure_utf8_stdout
from _shared.yaml_utils import load_vocabulary_values  # 词表加载 SSoT（D-D-05：禁止复制 _load_xxx）

ensure_utf8_stdout()


# 规则文件目录
RULES_DIR = REPO_ROOT / "docs" / "01_policies_and_standards" / "rules"

# 7标准字段（必填）+ 完整标准顺序
STANDARD_FIELDS = [
    "rule_id",
    "title",
    "version",
    "layer",
    "module_id",
    "depends_on",
    "tags",
    "stability",
    "safety_level",
    "ai_autonomy",
    "aliases",
    "severity",
    "scope",
    "domain",
    "triggers",
    "sections",
    "references",
    "enforcement",
    "metadata",
    "provenance",
]

REQUIRED_FIELDS = [
    "rule_id",
    "title",
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

VALID_LAYER = load_vocabulary_values("layer_vocabulary.yaml", fallback_key="id", strict=False)
VALID_STABILITY = load_vocabulary_values("stability_vocabulary.yaml", fallback_key="id", strict=False)
VALID_SAFETY = load_vocabulary_values("safety_level_vocabulary.yaml", fallback_key="id", strict=False)
VALID_AUTONOMY = load_vocabulary_values("ai_autonomy_vocabulary.yaml", fallback_key="id", strict=False)

# 顶层字段行：行首不含空格的 key: 形式
_TOP_KEY_RE = re.compile(r"^([a-z_][a-z0-9_]*)\s*:")

_errors: list[str] = []
_warnings: list[str] = []


def _extract_top_fields(text: str) -> list[str]:
    """从 YAML 文本提取顶层字段顺序（仅行首无缩进的 key: 行）。"""
    fields: list[str] = []
    in_frontmatter = True
    for line in text.splitlines():
        # 跳过空行和注释
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        # 遇到文档主体（非 frontmatter）则停止——规则文件整体是 YAML，无 --- 分隔
        if not in_frontmatter:
            break
        # 顶层字段：行首无缩进
        if not line.startswith((" ", "\t")):
            m = _TOP_KEY_RE.match(line)
            if m:
                fields.append(m.group(1))
            else:
                # 非标准顶层行，可能是文档内容，停止
                pass
    return fields


def _validate_file(path: Path) -> None:
    """校验单个规则文件。"""
    rel = path.relative_to(REPO_ROOT).as_posix()
    try:
        text = path.read_text(encoding="utf-8")
    except Exception as exc:
        _errors.append(f"{rel}: 读取失败 - {exc}")
        return

    # 提取顶层字段顺序
    top_fields = _extract_top_fields(text)
    if not top_fields:
        _errors.append(f"{rel}: 无法提取 frontmatter 字段（文件为空或格式错误）")
        return

    # DIM-1: 必填字段存在性
    field_set = set(top_fields)
    for req in REQUIRED_FIELDS:
        if req not in field_set:
            _errors.append(f"{rel}: 缺少必填字段 '{req}'")

    # DIM-2: 字段顺序（仅校验已存在字段之间的相对顺序符合 STANDARD_FIELDS）
    # 提取实际顺序中属于 STANDARD_FIELDS 的子集
    actual_ordered = [f for f in top_fields if f in STANDARD_FIELDS]
    # 期望顺序：STANDARD_FIELDS 中实际存在的字段，按 STANDARD_FIELDS 顺序
    expected_ordered = [f for f in STANDARD_FIELDS if f in field_set]
    if actual_ordered != expected_ordered:
        _errors.append(f"{rel}: 字段顺序错误\n  期望: {expected_ordered}\n  实际: {actual_ordered}")

    # DIM-3: 枚举值合法性（用 yaml.safe_load 解析值）
    try:
        import yaml

        data = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        _errors.append(f"{rel}: YAML 解析失败 - {exc}")
        return
    if not isinstance(data, dict):
        _errors.append(f"{rel}: frontmatter 不是 dict")
        return

    layer = data.get("layer")
    if layer is not None and layer not in VALID_LAYER:
        _errors.append(f"{rel}: layer='{layer}' 非法，合法值: {sorted(VALID_LAYER)}")

    stability = data.get("stability")
    if stability is not None and stability not in VALID_STABILITY:
        _errors.append(f"{rel}: stability='{stability}' 非法，合法值: {sorted(VALID_STABILITY)}")

    safety = data.get("safety_level")
    if safety is not None and safety not in VALID_SAFETY:
        _errors.append(f"{rel}: safety_level='{safety}' 非法，合法值: {sorted(VALID_SAFETY)}")

    autonomy = data.get("ai_autonomy")
    if autonomy is not None and autonomy not in VALID_AUTONOMY:
        _errors.append(f"{rel}: ai_autonomy='{autonomy}' 非法，合法值: {sorted(VALID_AUTONOMY)}")

    # DIM-4: rule_id 与文件名一致性
    rule_id = data.get("rule_id", "")
    # 文件名 trae_XXX.yaml ↔ rule_id: TRAE-XXX
    m = re.match(r"^trae_(\d+)_.*\.yaml$", path.name)
    if m and rule_id:
        expected_rule_id = f"TRAE-{m.group(1)}"
        if rule_id != expected_rule_id:
            _errors.append(f"{rel}: rule_id='{rule_id}' 与文件名不匹配，期望 '{expected_rule_id}'")

    # DIM-5: 文件名主题前缀（ARCH-037，trae_NNN_<主题>_<描述>.yaml）
    # name 段（trae_NNN_ 之后）必须含下划线——单段=缺主题前缀（后天防漂移）
    m_name = re.match(r"^trae_\d+_(.+)\.yaml$", path.name)
    if m_name and "_" not in m_name.group(1):
        _errors.append(
            f"{rel}: 文件名缺主题前缀(ARCH-037)—name段'{m_name.group(1)}'为单段；"
            f"命名约定: trae_NNN_<主题>_<描述>.yaml（见 trae_028 GOV-DOC-003）"
        )


def main() -> int:
    """入口：扫描所有 trae_XXX.yaml 并校验。"""
    parser = argparse.ArgumentParser(description="GATE-RULE-FM: 规则文件 frontmatter 校验")
    parser.add_argument("--warn-only", action="store_true", help="仅警告，不阻断（exit 0）")
    parser.add_argument("--file", help="只校验指定文件（相对路径）")
    args = parser.parse_args()

    if args.file:
        files = [RULES_DIR / args.file]
    else:
        files = sorted(RULES_DIR.glob("trae_*.yaml"))

    if not files:
        print("  WARN: 未找到 trae_*.yaml 文件")
        return EXIT_PASS

    print(f"  GATE-RULE-FM: 校验 {len(files)} 个规则文件")
    for f in files:
        if not f.exists():
            _errors.append(f"{f}: 文件不存在")
            continue
        _validate_file(f)

    # 输出结果
    if _warnings:
        for w in _warnings:
            print(f"  WARN: {w}")
    if _errors:
        for e in _errors:
            print(f"  FAIL: {e}")
        total = len(_errors)
        if args.warn_only:
            print(f"\n  WARN-ONLY: {total} 个问题（不阻断）")
            return EXIT_PASS
        print(f"\n  RESULT: FAIL ({total} 个问题)")
        return EXIT_FINDINGS

    print(f"\n  RESULT: PASS ({len(files)} 个文件全部合规)")
    return EXIT_PASS


if __name__ == "__main__":
    sys.exit(main())
