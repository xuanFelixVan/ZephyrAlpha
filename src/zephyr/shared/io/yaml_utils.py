# [BLUEPRINT] MOD-SHR-io-yaml | src/zephyr/shared/io/yaml_utils.py | §
# [MODULE] zephyr.shared.io.yaml_utils
# [DOMAIN] D_SHARED
# [DEPENDENCIES] zephyr.shared.io.paths
# [CONSUMERS] scripts/governance/_shared/yaml_utils.py(重新导出); src/zephyr/governance/triage.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] load_vocabulary_values 是 vocabulary YAML 合法值加载的唯一真源；strict=True fail-fast
# [MODIFY-GUARD]
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] FileNotFoundError(strict=True且文件不存在)
# [TESTS] 手动测试：load_vocabulary_values("status_vocabulary.yaml") 返回3值
# [A_module] module_id=MOD-SHR-io-yaml | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""yaml_utils.py — vocabulary YAML 加载公共工具（SSoT 真源）

对标 SCRIPT-QUALITY-001 D-D-05（禁止跨脚本复制粘贴逻辑）
     trae_060 §2（词表唯一真源，直接消费不复制）

本文件是 ``load_vocabulary_values`` 的唯一真源实现。
- ``src/zephyr/`` 下代码：``from zephyr.shared.io.yaml_utils import load_vocabulary_values``
- ``scripts/`` 下代码：``from _shared.yaml_utils import load_vocabulary_values``（scripts/_shared/yaml_utils.py 重新导出）

capability_id: vocabulary_values_loader
canonical: src/zephyr/shared/io/yaml_utils.py
"""

from __future__ import annotations

from typing import Final
from pathlib import Path

import yaml

from zephyr.shared.io.paths import REPO_ROOT

# vocabulary YAML 默认目录（SSoT 真源目录）
DEFAULT_VOCAB_DIR: Final[Path] = (
    REPO_ROOT
    / "docs"
    / "01_policies_and_standards"
    / "_registry"
    / "vocabularies"
)


def load_vocabulary_values(
    vocab_file: str | Path,
    *,
    vocab_dir: str | Path | None = None,
    fallback_key: str | None = None,
    strict: bool = True,
) -> set[str]:
    """从 vocabulary YAML 动态加载合法值集合（SSoT 唯一真源，禁止硬编码）。

    对标 SCRIPT-QUALITY-001 D-D-05（禁止跨脚本复制粘贴逻辑）。
    所有词表合法值加载集中在此，禁止各脚本/模块复制 _load_xxx() 函数。

    YAML 结构约定：顶层 ``values`` 列表，每个 entry 为 dict，取 ``value`` 键。

    失败模式（v1.1.0 fail-fast + R6 治本 2026-06-30）:
        - ``strict=True``（默认）: fail-fast——文件不存在/YAML 解析错误/非 dict 结构
          均抛异常。理由：静默返回空 set 会导致合规检查变空集（"全部不合法"或"全部通过"），
          是 DoS 漂移源。AI 误拼 yaml 名应立即崩溃而非静默漂移。
        - ``strict=False``: 宽容模式——文件不存在/YAML 解析错误/非 dict 结构
          均返回空 set。用于 warn-only 检测工具（如 check_vocab_hardcode）和测试隔离，
          避免词表数据问题导致检测工具崩溃卡住 commit 流水线。

    Args:
        vocab_file: YAML 文件名（如 ``"status_vocabulary.yaml"``）或绝对路径
        vocab_dir: YAML 所在目录；默认 ``docs/01_policies_and_standards/_registry/vocabularies``
        fallback_key: entry 缺少 ``value`` 键时的回退键（如 ``"id"``）；None 表示不回退
        strict: True=fail-fast（默认）；False=宽容模式（返回空 set 而非崩溃）

    Returns:
        合法值 ``set[str]``

    Raises:
        FileNotFoundError: ``strict=True`` 且文件不存在
        yaml.YAMLError: ``strict=True`` 且 YAML 解析失败
        ValueError: ``strict=True`` 且 YAML 顶层非 dict 结构
    """
    vdir = Path(vocab_dir) if vocab_dir else DEFAULT_VOCAB_DIR
    p = Path(vocab_file)
    if not p.is_absolute():
        p = vdir / p
    if not p.exists():
        if strict:
            raise FileNotFoundError(
                f"vocabulary YAML 不存在: {p}\n"
                f"提示：检查文件名拼写（误拼会导致合规检查变空集→DoS漂移）。"
                f"如需测试隔离/渐进迁移，传 strict=False。"
            )
        return set()
    try:
        data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError:
        if strict:
            raise
        return set()  # R6: strict=False 宽容模式，YAML 格式错误返回空 set
    if not isinstance(data, dict):
        if strict:
            raise ValueError(f"vocabulary YAML 顶层非 dict 结构: {p}")
        return set()  # R6: strict=False 宽容模式
    result: set[str] = set()
    for entry in data.get("values", []) or []:
        if not isinstance(entry, dict):
            continue
        val = entry.get("value")
        if not val and fallback_key:
            val = entry.get(fallback_key)
        if val is not None:
            result.add(str(val))
    return result


def load_vocabulary_entries(
    vocab_file: str | Path,
    *,
    vocab_dir: str | Path | None = None,
    fallback_key: str | None = None,
    strict: bool = True,
) -> list[dict]:
    """从 vocabulary YAML 加载有效值+定义列表（SSoT 唯一真源，禁止硬编码）。

    治本（2026-06-30）：与 ``load_vocabulary_values`` 配对，返回更丰富结构。
    ``load_vocabulary_values`` 返回 ``set[str]``（只需值集合时用），
    本函数返回 ``list[dict]``（需要 value + definition 时用，如 schema.json
    双向同步填充新增 oneOf+const 项的 description）。

    Args:
        vocab_file: YAML 文件名（如 ``"status_vocabulary.yaml"``）或绝对路径
        vocab_dir: YAML 所在目录；默认 ``docs/01_policies_and_standards/_registry/vocabularies``
        fallback_key: entry 缺少 ``value`` 键时的回退键（如 ``"id"``）；None 表示不回退
        strict: True=fail-fast（默认）；False=宽容模式（返回空 list 而非崩溃）

    Returns:
        ``[{"value": "frozen", "definition": "冻结——不可修改"}, ...]``
        definition 可能为空字符串（词表无 definition 字段时）。

    Raises:
        FileNotFoundError: ``strict=True`` 且文件不存在
        yaml.YAMLError: ``strict=True`` 且 YAML 解析失败
        ValueError: ``strict=True`` 且 YAML 顶层非 dict 结构
    """
    vdir = Path(vocab_dir) if vocab_dir else DEFAULT_VOCAB_DIR
    p = Path(vocab_file)
    if not p.is_absolute():
        p = vdir / p
    if not p.exists():
        if strict:
            raise FileNotFoundError(
                f"vocabulary YAML 不存在: {p}\n"
                f"提示：检查文件名拼写。如需测试隔离/渐进迁移，传 strict=False。"
            )
        return []
    try:
        data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError:
        if strict:
            raise
        return []
    if not isinstance(data, dict):
        if strict:
            raise ValueError(f"vocabulary YAML 顶层非 dict 结构: {p}")
        return []
    entries: list[dict] = []
    for entry in data.get("values", []) or []:
        if not isinstance(entry, dict):
            continue
        val = entry.get("value")
        if not val and fallback_key:
            val = entry.get(fallback_key)
        if val is not None:
            entries.append({
                "value": str(val),
                "definition": str(entry.get("definition", "")),
            })
    return entries


def load_vocabulary_deprecated_map(
    vocab_file: str | Path,
    *,
    vocab_dir: str | Path | None = None,
    deprecated_key: str = "deprecated_values",
    migrated_to_key: str = "migrated_to",
) -> dict[str, str | None]:
    """从 vocabulary YAML 加载废弃值→迁移目标映射（SSoT 唯一真源）。

    收拢 check_frontmatter_metadata._load_deprecated_values 和
    migrate_illegal_doctype._load_deprecated_map 的重复逻辑。

    Args:
        vocab_file: YAML 文件名或绝对路径
        vocab_dir: YAML 所在目录；默认词表目录
        deprecated_key: 废弃值列表的 YAML 键名（默认 ``deprecated_values``）
        migrated_to_key: 迁移目标的 YAML 键名（默认 ``migrated_to``）

    Returns:
        ``{废弃值: 迁移目标|None}`` 字典。
        单值迁移 → 目标字符串；多值/N/A → None（需人工判定）。

    Raises:
        FileNotFoundError: 文件不存在
    """
    vdir = Path(vocab_dir) if vocab_dir else DEFAULT_VOCAB_DIR
    p = Path(vocab_file)
    if not p.is_absolute():
        p = vdir / p
    if not p.exists():
        raise FileNotFoundError(f"vocabulary YAML 不存在: {p}")
    data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    result: dict[str, str | None] = {}
    for v in data.get(deprecated_key, []) or []:
        if not isinstance(v, dict):
            continue
        val = v.get("value", "")
        if not val:
            continue
        mt = v.get(migrated_to_key)
        if isinstance(mt, str) and mt and not mt.startswith("N/A"):
            result[str(val)] = str(mt)
        elif isinstance(mt, list) and len(mt) == 1 and mt[0] and not str(mt[0]).startswith("N/A"):
            result[str(val)] = str(mt[0])
        else:
            result[str(val)] = None  # 多值/N/A → 需人工判定
    return result


def load_decision_tree(
    vocab_file: str | Path,
    *,
    vocab_dir: str | Path | None = None,
    strict: bool = True,
) -> dict:
    """从 vocabulary YAML 加载 decision_tree 结构（SSoT 唯一真源）。

    用于 ttl 等 vocabulary 的机器可读判定树。
    criteria 结构：{signal, value, operator}，供 evaluate_ttl 消费。

    支持 criteria_source 引用（治本 2026-06-29）：
        节点可声明 criteria_source 引用外部 YAML 的 section（如 directory_contract.yaml
        的 directory_zones.permanent.paths），本函数加载时自动展开为 criteria 列表，
        对 evaluate_ttl 透明。消除路径列表副本，路径变更只需改契约一处。

    对标 trae_060 §2（词表唯一真源，直接消费不复制）。
    替换 backfill_ttl_metadata._PERMANENT_ZONE_PREFIXES / git_commit_gateway._PERMANENT_ZONE_DIRS 等硬编码。

    Args:
        vocab_file: YAML 文件名（如 ``"ttl_vocabulary.yaml"``）或绝对路径
        vocab_dir: YAML 所在目录；默认词表目录
        strict: 文件不存在时是否抛异常（默认 True，fail-fast）

    Returns:
        decision_tree dict（含 root, nodes）；无 decision_tree 键时返回空 dict

    Raises:
        FileNotFoundError: strict=True 且文件不存在
    """
    vdir = Path(vocab_dir) if vocab_dir else DEFAULT_VOCAB_DIR
    p = Path(vocab_file)
    if not p.is_absolute():
        p = vdir / p
    if not p.exists():
        if strict:
            raise FileNotFoundError(
                f"vocabulary YAML 不存在: {p}\n"
                f"提示：检查文件名拼写。如需测试隔离，传 strict=False。"
            )
        return {}
    data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    tree = data.get("decision_tree") or {}
    _expand_criteria_sources(tree, strict=strict)
    return tree


def _expand_criteria_sources(tree: dict, *, strict: bool = True) -> None:
    """展开 decision_tree 节点中的 criteria_source 引用为 criteria 列表（原地修改）。

    criteria_source 结构::

        criteria_source:
          target: directory_contract.yaml
          path: docs/01_policies_and_standards/_registry/contracts/directory_contract.yaml  # 相对 REPO_ROOT
          section: directory_zones.permanent.paths  # 点分隔的 YAML 路径
          signal: path
          operator: startswith

    展开后：node["criteria"] = [{"signal": ..., "value": <每个 path>, "operator": ...}, ...]

    约束：向内收——路径列表真源在外部 YAML，本函数加载时展开，evaluate_ttl 零感知。
    """
    nodes = tree.get("nodes") or {}
    for node in nodes.values():
        if not isinstance(node, dict):
            continue
        cs = node.get("criteria_source")
        if not cs or not isinstance(cs, dict):
            continue
        ext_path = cs.get("path")
        section = cs.get("section")
        signal = cs.get("signal", "path")
        operator = cs.get("operator", "startswith")
        if not ext_path or not section:
            continue
        ext_file = REPO_ROOT / ext_path
        if not ext_file.exists():
            if strict:
                raise FileNotFoundError(
                    f"criteria_source 引用的 YAML 不存在: {ext_file}"
                )
            node["criteria"] = []
            continue
        ext_data = yaml.safe_load(ext_file.read_text(encoding="utf-8")) or {}
        # 按 section 点分隔路径取值
        value = ext_data
        for key in section.split("."):
            if not isinstance(value, dict):
                value = None
                break
            value = value.get(key)
        if not isinstance(value, list):
            if strict:
                raise ValueError(
                    f"criteria_source section '{section}' 不是列表: {ext_path}"
                )
            node["criteria"] = []
            continue
        node["criteria"] = [
            {"signal": signal, "value": str(v), "operator": operator}
            for v in value
        ]


def evaluate_ttl(
    rel_path: str,
    frontmatter: dict | None,
    decision_tree: dict | None,
) -> str:
    """根据 decision_tree 判定 ttl 值（机器可读 criteria 消费器）。

    约束：decision_tree 来自 load_decision_tree，criteria 结构为 {signal, value, operator}。
    替换 backfill_ttl_metadata._infer_ttl / git_commit_gateway._PERMANENT_ZONE_DIRS 等硬编码。
    向内收：判定逻辑唯一真源为 ttl_vocabulary.yaml decision_tree，脚本零硬编码。

    支持的 signal：
        - ``path``: 用 rel_path 判定（operator: startswith/contains）
        - ``frontmatter.doc_type``: 用 frontmatter doc_type 判定（operator: equals）

    Args:
        rel_path: 相对仓库根的路径（正斜杠，如 ``docs/03_modules/_system_master/changes/index.md``）
        frontmatter: 文件 frontmatter dict（可为 None）
        decision_tree: decision_tree 结构（可为 None，回退 task_bound）

    Returns:
        ``"permanent"`` 或 ``"task_bound"``；无判定树时回退 task_bound（安全默认）
    """
    if not decision_tree or not decision_tree.get("nodes"):
        return "task_bound"  # 无判定树，默认 task_bound（安全回退）

    nodes = decision_tree["nodes"]
    current = decision_tree.get("root")
    visited: set[str] = set()  # 防循环

    while current and current in nodes and current not in visited:
        visited.add(current)
        node = nodes[current]
        criteria = node.get("criteria", [])
        match_mode = node.get("match", "any")

        results = [
            _eval_criterion(c.get("signal", ""), c.get("value", ""),
                            c.get("operator", "equals"), rel_path, frontmatter)
            for c in criteria if isinstance(c, dict)
        ]
        matched = any(results) if match_mode == "any" else all(results)
        # YAML 1.1 (PyYAML) 将裸 yes/no 解析为 True/False，必须兼容两种键名
        # 约束：禁止简化为 node.get("yes")——会导致 yes: 被解析为 True 键时取不到值
        if matched:
            current = node.get("yes") or node.get(True)
        else:
            current = node.get("no") or node.get(False)

    if current in ("permanent", "task_bound"):
        return current
    return "task_bound"  # 安全回退


def _eval_criterion(
    signal: str,
    value: str,
    operator: str,
    rel_path: str,
    frontmatter: dict | None,
) -> bool:
    """评估单个 criterion（内部辅助函数，禁止外部调用）。

    约束：新增 signal 类型必须在此函数扩展，禁止在调用方硬编码判定逻辑。
    """
    if signal == "path":
        if operator == "startswith":
            return rel_path.startswith(value)
        if operator == "contains":
            return value in rel_path
        return False
    if signal == "frontmatter.doc_type":
        dt = (frontmatter or {}).get("doc_type", "")
        if operator == "equals":
            return str(dt) == value
        return False
    return False
