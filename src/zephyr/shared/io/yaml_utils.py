# [BLUEPRINT] MOD-SHR_IO_YAML | src/zephyr/shared/io/yaml_utils.py | §
# [MODULE] zephyr.shared.io.yaml_utils
# [DOMAIN] D_SHARED
# [DEPENDENCIES] zephyr.shared.io.paths
# [CONSUMERS] scripts/governance/_shared/yaml_utils.py(重新导出)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] load_vocabulary_values 是 vocabulary YAML 合法值加载的唯一真源；strict=True fail-fast
# [MODIFY-GUARD]
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] FileNotFoundError(strict=True且文件不存在)
# [TESTS] 手动测试：load_vocabulary_values("status_vocabulary.yaml") 返回3值
# [A_module] module_id=MOD-SHR_IO_YAML | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""

yaml_utils.py — vocabulary YAML 加载公共工具（SSoT 真源）

对标 SCRIPT-QUALITY-001 D-D-05（禁止跨脚本复制粘贴逻辑）
     trae_060 §2（词表唯一真源，直接消费不复制）

本文件是 ``load_vocabulary_values`` 的唯一真源实现。
- ``src/zephyr/`` 下代码：``from zephyr.shared.io.yaml_utils import load_vocabulary_values``
- ``scripts/`` 下代码：``from _shared.yaml_utils import load_vocabulary_values``（scripts/_shared/yaml_utils.py 重新导出）

capability_id: vocabulary_values_loader
canonical: src/zephyr/shared/io/yaml_utils.py

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: vocabulary 词表YAML文件
#   fields: 顶层values列表(entry含value/definition) + deprecated_values + decision_tree + 顶层列表段(如foundation_domains)
#   code: docs/01_policies_and_standards/_registry/vocabularies/*_vocabulary.yaml
# - id: I2
#   name: 外部契约YAML criteria_source引用
#   fields: 被decision_tree节点criteria_source引用的外部YAML(含path/section点分隔路径)
#   code: directory_contract.yaml 等, 相对 REPO_ROOT
# - id: I3
#   name: TTL判定输入
#   fields: rel_path相对路径(正斜杠) + frontmatter dict(含doc_type)
#   code: evaluate_ttl(rel_path, frontmatter, decision_tree)
# 层: 算法
# - id: A1
#   name_zh: ① 词表路径解析与加载校验
#   name_en: _resolve_vocab_path / _load_vocab_data
#   intro: 拼好词表文件路径读YAML，strict模式文件没了直接崩，宽容模式安静返回None
#   desc: 非绝对路径拼接vocab_dir(默认词表目录) → yaml.safe_load; strict=True时缺失/解析错/非dict均抛异常fail-fast, strict=False返回None
#   inputs: I1
#   outputs: 词表data dict 或 None
#   invariant: strict=True fail-fast
# - id: A2
#   name_zh: ② 合法值与条目收集
#   name_en: load_vocabulary_values / load_vocabulary_entries / load_all_vocabulary_values / load_vocabulary_section_list
#   intro: 从values列表抠出合法值集合或值+定义列表，也能批量扫全部词表或读顶层列表段
#   desc: 遍历data[values]取entry[value](缺则回退fallback_key)集合成set; entries版附definition; 批量版glob *_vocabulary.yaml跳过空词表; section_list版读顶层列表段裸字符串
#   inputs: A1
#   outputs: set[str]合法值 / list[dict]条目 / {vocab_name: set}
#   invariant: load_vocabulary_values 是 vocabulary YAML 合法值加载的唯一真源
# - id: A3
#   name_zh: ③ 废弃值迁移映射加载
#   name_en: load_vocabulary_deprecated_map / _collect_deprecated_map
#   intro: 把废弃值到迁移目标的映射抠出来，多值或N/A的标None留人工判
#   desc: 遍历deprecated_values取value→migrated_to; 单值字符串或单元素list→目标字符串; 多值/N/A开头→None
#   inputs: I1
#   outputs: {废弃值: 迁移目标|None}
# - id: A4
#   name_zh: ④ 决策树加载与criteria_source展开
#   name_en: load_decision_tree / _expand_criteria_sources
#   intro: 读decision_tree并把引用外部YAML的路径列表就地展开成criteria，消费者零感知
#   desc: 取data[decision_tree] → 遍历nodes, 有criteria_source则读外部YAML按section点路径取list → node[criteria]=[{signal,value,operator}...] 原地展开
#   inputs: I1 I2
#   outputs: decision_tree dict(含root/nodes)
# - id: A5
#   name_zh: ⑤ TTL决策树判定
#   name_en: evaluate_ttl / _eval_criterion
#   intro: 拿文件路径和frontmatter沿判定树走，走到叶子得出permanent还是task_bound
#   desc: 从root沿nodes走(visited防循环): criteria按match=any/all评估(path:startswith/contains, frontmatter.doc_type:equals) → yes/no分支(兼容PyYAML布尔键) → 终值须在ttl合法值集否则回退task_bound
#   inputs: I3 A4
#   outputs: "permanent" 或 "task_bound"
#   invariant: 无判定树或终值非法时安全回退task_bound
# 层: 输出
# - id: O1
#   name_zh: 词表合法值集合与结构
#   name_en: set[str] / list[dict] / deprecated map / decision_tree
#   intro: 词表合法值、值+定义条目、废弃迁移映射与决策树，是各治理脚本的词表唯一真源
#   downstream: scripts/governance/_shared/yaml_utils.py(重新导出) ; 各治理检测脚本
# - id: O2
#   name_zh: TTL判定结果
#   name_en: evaluate_ttl -> str
#   intro: 文件生命周期判定permanent/task_bound，喂给ttl元数据回填与提交网关
#   invariant: 返回值∈ttl_vocabulary.yaml合法值集
#   downstream: 治理脚本(backfill_ttl_metadata / git_commit_gateway 等)
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# I1 --> A3
# I1 --> A4
# I2 --> A4
# I3 --> A5
# A4 --> A5
# A2 --> O1
# A3 --> O1
# A4 --> O1
# A5 --> O2
"""

from __future__ import annotations

from pathlib import Path
from typing import Final

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


def _resolve_vocab_path(vocab_file, vocab_dir):
    """解析 vocabulary YAML 路径：vocab_file 非绝对路径时拼接 vocab_dir/DEFAULT_VOCAB_DIR。"""
    vdir = Path(vocab_dir) if vocab_dir else DEFAULT_VOCAB_DIR
    p = Path(vocab_file)
    if not p.is_absolute():
        p = vdir / p
    return p


def _load_vocab_data(p, strict, missing_msg, non_dict_msg):
    """加载 vocabulary YAML 并校验顶层 dict 结构。

    strict=True 时 fail-fast（FileNotFoundError/yaml.YAMLError/ValueError）；
    strict=False 时宽容返回 None（调用方据 None 返回空集合）。
    """
    if not p.exists():
        if strict:
            raise FileNotFoundError(missing_msg)
        return None
    try:
        data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError:
        if strict:
            raise
        return None
    if not isinstance(data, dict):
        if strict:
            raise ValueError(non_dict_msg)
        return None
    return data


def _collect_vocab_values(data, fallback_key):
    """从 vocabulary YAML data 收集合法值集合（value 键，缺则回退 fallback_key）。"""
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


def _collect_vocab_entries(data, fallback_key):
    """从 vocabulary YAML data 收集 value+definition 列表（缺 definition 回退空串）。"""
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


def _collect_deprecated_map(data, deprecated_key, migrated_to_key):
    """从 vocabulary YAML data 收集废弃值->迁移目标映射。"""
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
            result[str(val)] = None
    return result


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
    p = _resolve_vocab_path(vocab_file, vocab_dir)
    data = _load_vocab_data(
        p, strict,
        f"vocabulary YAML 不存在: {p}\n"
        f"提示：检查文件名拼写（误拼会导致合规检查变空集->DoS漂移）。"
        f"如需测试隔离/渐进迁移，传 strict=False。",
        f"vocabulary YAML 顶层非 dict 结构: {p}",
    )
    if data is None:
        return set()
    return _collect_vocab_values(data, fallback_key)


def load_all_vocabulary_values(
    *,
    vocab_dir: str | Path | None = None,
    strict: bool = False,
) -> dict[str, set[str]]:
    """批量加载所有 ``*_vocabulary.yaml`` 的合法值，构建 vocab_name → set[value] 映射。

    治本（#ARCH-VOCAB-NOQA-CONVERGENCE-001 Phase 2）：SSoT 现支持批量加载，
    消除消费者（如 ``check_vocab_hardcode._load_all_vocab_values``）复制
    ``yaml.safe_load + glob`` 逻辑的 noqa 豁免需求。对标 D-D-05
    （禁止跨脚本复制粘贴逻辑）——批量加载场景此前 SSoT 缺失，迫使消费者
    自己用 ``yaml.safe_load`` 触发 gate-vocab 检测；本函数补齐 SSoT 缺口。

    与 ``load_vocabulary_values`` 的关系：
        - ``load_vocabulary_values("status_vocabulary.yaml")`` → 单个词表 ``set[str]``
        - ``load_all_vocabulary_values()`` → 全部词表 ``{vocab_name: set[str]}``

    返回原始值集合（不过滤数字/长度），消费者按需后处理（如过滤纯数字值）。
    过滤逻辑属业务策略（不同消费者有不同过滤需求），不属 SSoT 加载层。

    失败模式（与 ``load_vocabulary_values`` 对齐）:
        - ``strict=True``: 任一词表加载失败 fail-fast（FileNotFoundError/yaml.YAMLError/ValueError）
        - ``strict=False``（默认）: 跳过失败词表（warn-only，不崩溃）——适合
          检测工具场景，避免单词表数据问题导致整个工具崩溃

    Args:
        vocab_dir: YAML 所在目录；默认 ``DEFAULT_VOCAB_DIR``
        strict: True=任一词表加载失败 fail-fast；False（默认）=跳过失败词表

    Returns:
        ``{vocab_name: {value, ...}}``；vocab_name 不含 ``_vocabulary.yaml`` 后缀。
        空字典如果 vocab_dir 不存在或无 ``*_vocabulary.yaml`` 文件。
        仅含 ``values`` 列表非空的词表（空词表不进入结果）。

    Raises:
        FileNotFoundError: ``strict=True`` 且某词表文件不存在
        yaml.YAMLError: ``strict=True`` 且某词表 YAML 解析失败
        ValueError: ``strict=True`` 且某词表顶层非 dict 结构
    """
    vdir = Path(vocab_dir) if vocab_dir else DEFAULT_VOCAB_DIR
    result: dict[str, set[str]] = {}
    for p in sorted(vdir.glob("*_vocabulary.yaml")):
        vocab_name = p.name.removesuffix("_vocabulary.yaml")
        data = _load_vocab_data(
            p, strict,
            f"vocabulary YAML 不存在: {p}\n"
            f"提示：批量加载时某词表文件缺失（strict=True fail-fast）。",
            f"vocabulary YAML 顶层非 dict 结构: {p}",
        )
        if data is None:
            continue
        values = _collect_vocab_values(data, None)
        if values:
            result[vocab_name] = values
    return result


# 治本(2026-07-17): ttl 合法值真源是 ttl_vocabulary.yaml，禁止代码硬编码字面量集合。
# strict=False 容错：词表缺失时返回空 set，evaluate_ttl 回退 task_bound（安全默认）。
_TTL_VALID_VALUES: Final[set[str]] = load_vocabulary_values(
    "ttl_vocabulary.yaml", strict=False
)


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
    p = _resolve_vocab_path(vocab_file, vocab_dir)
    data = _load_vocab_data(
        p, strict,
        f"vocabulary YAML 不存在: {p}\n"
        f"提示：检查文件名拼写。如需测试隔离/渐进迁移，传 strict=False。",
        f"vocabulary YAML 顶层非 dict 结构: {p}",
    )
    if data is None:
        return []
    return _collect_vocab_entries(data, fallback_key)


def load_vocabulary_section_list(
    vocab_file: str | Path,
    section_key: str,
    *,
    vocab_dir: str | Path | None = None,
    strict: bool = True,
) -> set[str]:
    """从 vocabulary YAML 加载顶层列表段（如 foundation_domains）为字符串集合（SSoT 唯一真源）。

    治本（M01 #3/#4，2026-07-17）：补充 load_vocabulary_values 不支持顶层列表段的缺口。
    load_vocabulary_values 只加载 ``values:`` 列表（取 ``value`` 键），
    本函数加载其他顶层列表段（如 ``foundation_domains:``）——列表项为裸字符串。

    替换 ct_pipe_routing._FOUNDATION_LAYERS / routing_plugins._FOUNDATION_LAYERS 硬编码。

    Args:
        vocab_file: YAML 文件名（如 ``"target_layer_vocabulary.yaml"``）或绝对路径
        section_key: 顶层列表段键名（如 ``"foundation_domains"``）
        vocab_dir: YAML 所在目录；默认词表目录
        strict: True=fail-fast（默认）；False=宽容模式（返回空 set 而非崩溃）

    Returns:
        合法值 ``set[str]``；段不存在或为空时返回空 set

    Raises:
        FileNotFoundError: ``strict=True`` 且文件不存在
        yaml.YAMLError: ``strict=True`` 且 YAML 解析失败
        ValueError: ``strict=True`` 且 YAML 顶层非 dict 结构或段非列表
    """
    p = _resolve_vocab_path(vocab_file, vocab_dir)
    data = _load_vocab_data(
        p, strict,
        f"vocabulary YAML 不存在: {p}\n"
        f"提示：检查文件名拼写。如需测试隔离，传 strict=False。",
        f"vocabulary YAML 顶层非 dict 结构: {p}",
    )
    if data is None:
        return set()
    section = data.get(section_key) or []
    if not isinstance(section, list):
        if strict:
            raise ValueError(
                f"vocabulary YAML 段 '{section_key}' 不是列表: {p}"
            )
        return set()
    return {str(v) for v in section if v}


def load_vocabulary_deprecated_map(
    vocab_file: str | Path,
    *,
    vocab_dir: str | Path | None = None,
    deprecated_key: str = "deprecated_values",
    migrated_to_key: str = "migrated_to",
) -> dict[str, str | None]:
    """从 vocabulary YAML 加载废弃值->迁移目标映射（SSoT 唯一真源）。

    收拢 check_frontmatter_metadata._load_deprecated_values 和
    migrate_illegal_doctype._load_deprecated_map 的重复逻辑。

    Args:
        vocab_file: YAML 文件名或绝对路径
        vocab_dir: YAML 所在目录；默认词表目录
        deprecated_key: 废弃值列表的 YAML 键名（默认 ``deprecated_values``）
        migrated_to_key: 迁移目标的 YAML 键名（默认 ``migrated_to``）

    Returns:
        ``{废弃值: 迁移目标|None}`` 字典。
        单值迁移 -> 目标字符串；多值/N/A -> None（需人工判定）。

    Raises:
        FileNotFoundError: 文件不存在
    """
    p = _resolve_vocab_path(vocab_file, vocab_dir)
    if not p.exists():
        raise FileNotFoundError(f"vocabulary YAML 不存在: {p}")
    data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    return _collect_deprecated_map(data, deprecated_key, migrated_to_key)


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

    if current in _TTL_VALID_VALUES:
        return current
    return "task_bound"  # 安全回退（task_bound 是 ttl_vocabulary.yaml 默认值）


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
