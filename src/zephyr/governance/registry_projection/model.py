# [MODULE] zephyr.governance.registry_projection.model
# [DOMAIN] D_GOV_CODE_QUALITY
# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §W-M1
# [TTL] permanent
# [DEPENDENCIES] yaml（compose 节点树）
# [CONSUMERS] zephyr.governance.registry_projection.renderer / state / pg_source / generator
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 快照模型是生成器唯一输入形态：条目=有序 (key,value) 对（保序+保留重复键，
#   compose 级提取，safe_load 无法表达的遗留脏数据零丢失）；规范化序=声明身份字段
#   （册头 unique_key，无声明退 (file,token) legacy 映射/首字段）字节序，与
#   commit_queue_landing._merge_entry_identity 同构；身份声明制=st-sI-identity-20261004
# [MODIFY-GUARD] 新建 2026-09-23 st-wm1-buildB-20260923（W-M1 波0 车道B）；
#   2026-10-04 st-sI-identity-20261004 身份声明制（F10 治本手术1）
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] snapshot_from_yaml 对解析失败 raise YAMLExtractError（调用方 fail-open）；永不静默吞脏数据
# [TESTS] tests/governance/registry_projection/test_projection_model.py
"""model.py — 投影快照模型与提取器（capability_canonical_file_registry 先行）。

快照=账本发布态的内存形态（乙号文 registry_snapshot.bundle 的对应物）：
- header_lines：头部元行 verbatim（生成器不重排头部散文）；
- sections：条目族（capabilities / creation_tokens），每条=有序 (key, value) 对；
- 尾部标量键（di_seam_exemptions）保序记录。

提取器 snapshot_from_yaml 用 yaml.compose 节点树保序+保留条目内重复键——这是
Phase-0 回填预览/影子期对账/红蓝测试的共同输入通道；生产路径由 pg_source 从
registry_snapshot.bundle 还原同一模型。


# [ALGO_FLOW]
层: 输入 → 提取
- 输入: 账本快照 dict/盘上 YAML 文本
- 提取: yaml.compose 保序提取头部元行与条目块，重复键原样保留为字段对列表"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Final

__all__: Final = [
    "ProjectionSnapshot",
    "Section",
    "YAMLExtractError",
    "canonicalize",
    "entry_identity_key",
    "snapshot_from_yaml",
]


class YAMLExtractError(ValueError):
    """快照提取失败（解析炸/结构走样）。"""


@dataclass
class Section:
    """条目族：根键+条目列表（每条=有序 (key, value) 对，重复键保留）。"""

    root_key: str
    entries: list[list[tuple[str, object]]] = field(default_factory=list)


@dataclass
class ProjectionSnapshot:
    """生成器唯一输入形态（纯数据，零行为）。"""

    registry_id: str
    physical_path: str
    header_lines: list[str]
    sections: list[Section]
    trailing_scalars: list[tuple[str, object]]
    ledger_revision: int = 0
    snapshot_version: int = 0
    content_sha256: str = ""
    # 身份声明制（st-sI-identity-20261004）：{族键: 声明身份字段元组}（"*"=全族默认）。
    # 空dict=无声明（消费面退位置首标量口径，fdfe8fe302 语义）。bundle 契约新增可选键
    # unique_key_fields 由此还原；snapshot_from_yaml 从根 unique_key 声明提取。
    unique_key_fields: dict[str, tuple[str, ...]] = field(default_factory=dict)

    def section(self, root_key: str) -> Section | None:
        for sec in self.sections:
            if sec.root_key == root_key:
                return sec
        return None

    def entry_counts(self) -> dict[str, int]:
        return {sec.root_key: len(sec.entries) for sec in self.sections}

    def declared_fields_for(self, root_key: str) -> tuple[str, ...] | None:
        """族声明身份字段（族键直查 → "*" 通配 → None=无声明）。"""
        fields = self.unique_key_fields.get(root_key) or self.unique_key_fields.get("*")
        return fields or None


def _scalar_tag_value(node: object) -> object:
    """ScalarNode → python 值（按 resolve tag，不重扫文本）。"""
    tag = getattr(node, "tag", "") or ""
    value = getattr(node, "value", "")
    style = getattr(node, "style", None)
    if tag == "tag:yaml.org,2002:null":
        return None
    if tag == "tag:yaml.org,2002:bool":
        return value.lower() in ("true", "yes", "on")
    if tag == "tag:yaml.org,2002:int":
        return int(value.replace("_", ""), 0) if not value.lower().startswith(("0x", "0o", "0b")) else int(value, 0)
    if tag == "tag:yaml.org,2002:float":
        return float(value.replace("_", ""))
    if tag == "tag:yaml.org,2002:str":
        return value
    # 未知 tag/带引号标量：compose 已解析引号内容，style 仅是发射形态痕迹
    if style in ('"', "'"):
        return value
    return value


def _node_to_value(node: object) -> object:
    type_name = type(node).__name__
    if type_name == "ScalarNode":
        return _scalar_tag_value(node)
    if type_name == "SequenceNode":
        return [_node_to_value(child) for child in node.value]
    if type_name == "MappingNode":
        # 嵌套 mapping 还原为 dict（重复键=取后值，safe_load 同判据）；条目级有序对
        # 由 _entries_from_sequence 直接走 _pair_from_node 保序保留
        out: dict[str, object] = {}
        for item in node.value:
            k, v = _pair_from_node(item)
            out[k] = v
        return out
    raise YAMLExtractError(f"未知节点类型 {type_name}")


def _pair_from_node(pair: object) -> tuple[str, object]:
    key_node, value_node = pair
    key = _scalar_tag_value(key_node)
    return str(key), _node_to_value(value_node)


def _entries_from_sequence(seq_node: object) -> list[list[tuple[str, object]]]:
    if type(seq_node.value) is not list:
        raise YAMLExtractError("节段值不是序列")
    entries = []
    for item in seq_node.value:
        if type(item).__name__ != "MappingNode":
            raise YAMLExtractError("条目不是 mapping（纯标量族不入投影账本，乙号文 §4 Phase0 判据）")
        entries.append([_pair_from_node(p) for p in item.value])
    return entries


def _normalize_unique_key_decl(raw: object) -> dict[str, tuple[str, ...]]:
    """根 unique_key 声明 → {族键: 字段元组} 归一（list=全族默认"*"，dict=按族）。

    与 commit_queue_landing._unique_key_decl 同一声明规范（QMine A1 件③ L1 SSOT）；
    退化形态（空/含非字符串段）静默丢弃该段——声明无效=无声明，退位置口径。
    """

    def _fields(items: object) -> tuple[str, ...] | None:
        if not isinstance(items, list) or not items:
            return None
        if not all(isinstance(f, str) and f for f in items):
            return None
        return tuple(items)

    out: dict[str, tuple[str, ...]] = {}
    if isinstance(raw, list):
        fields = _fields(raw)
        if fields:
            out["*"] = fields
    elif isinstance(raw, dict):
        for fam, items in raw.items():
            fields = _fields(items)
            if fields:
                out[str(fam)] = fields
    return out


def snapshot_from_yaml(text: str, *, registry_id: str, physical_path: str) -> ProjectionSnapshot:
    """compose 级提取：保序+保留条目内重复键（safe_load 盲区零丢失）。"""
    import yaml

    try:
        root = yaml.compose(text)
    except Exception as exc:  # noqa: BLE001 — 解析失败=提取失败本体
        raise YAMLExtractError(f"yaml.compose 失败: {exc}") from exc
    if type(root).__name__ != "MappingNode":
        raise YAMLExtractError("顶层不是 mapping")
    lines = text.split("\n")
    header_lines: list[str] = []
    sections: list[Section] = []
    trailing: list[tuple[str, object]] = []
    seen_section = False
    unique_key_decl: dict[str, tuple[str, ...]] = {}
    for key_node, value_node in root.value:
        key = str(_scalar_tag_value(key_node))
        if key == "unique_key":  # 身份声明提取（位置无关：头部/尾部均收）
            unique_key_decl = _normalize_unique_key_decl(_node_to_value(value_node))
        if type(value_node).__name__ == "SequenceNode" and value_node.value:
            first = value_node.value[0]
            if type(first).__name__ == "MappingNode" and not seen_section:
                header_lines = lines[: key_node.start_mark.line]
                seen_section = True
            if seen_section:
                sections.append(Section(root_key=key, entries=_entries_from_sequence(value_node)))
                continue
        if not seen_section:
            # 首个节段前的标量留在 header verbatim（compose 行号已定位节段起点）
            continue
        trailing.append((key, _node_to_value(value_node)))
    if not sections:
        raise YAMLExtractError("未发现条目节段（根序列缺失）")
    return ProjectionSnapshot(
        registry_id=registry_id,
        physical_path=physical_path,
        header_lines=header_lines,
        sections=sections,
        trailing_scalars=trailing,
        unique_key_fields=unique_key_decl,
    )


def entry_field(entry: list[tuple[str, object]], key: str) -> object:
    for k, v in entry:
        if k == key:
            return v
    return None


def entry_identity_key(
    entry: list[tuple[str, object]], declared_fields: tuple[str, ...] | None = None
) -> tuple[str, ...]:
    """复合身份元组（排序键形态）——声明字段优先，无声明退首个标量字段。

    st-sI-identity-20261004 身份声明制（f10 §6.1）：declared_fields 给定时按声明
    序取字段值元组（与册内 unique_key 声明一致）；缺失字段以 "" 占位（与既有
    (file, token) 排序键同容错口径）。无声明 → 向后扫描首个标量字段（fdfe8fe302
    同义）；条目无任何标量字段 → ("",)。调用方对 (file, token) 族（creation_tokens）
    显式传声明或沿用 _IDENTITY_SORT_KEY 兜底，禁盲调。
    """
    if declared_fields:
        return tuple("" if entry_field(entry, f) is None else str(entry_field(entry, f)) for f in declared_fields)
    for k, v in entry:
        if isinstance(v, (str, int, float, bool)):
            return (str(v),)
    return ("",)


_IDENTITY_SORT_KEY: dict[str, tuple[str, str]] = {
    "creation_tokens": ("file", "token"),
}


def _identity_key_for(
    root_key: str, entry: list[tuple[str, object]], declared_fields: tuple[str, ...] | None = None
) -> tuple[str, ...]:
    fields = declared_fields or _IDENTITY_SORT_KEY.get(root_key)
    if fields is None:
        first = entry[0][0] if entry else ""
        return ("" if entry_field(entry, first) is None else str(entry_field(entry, first)),)
    return tuple("" if entry_field(entry, f) is None else str(entry_field(entry, f)) for f in fields)


def canonicalize(snapshot: ProjectionSnapshot) -> ProjectionSnapshot:
    """规范化序：按册声明身份字段（无声明退 legacy 映射/首字段）字节序重排条目。

    发布侧（registry_snapshot.publish）必须先规范化再落 bundle——render 本身保序，
    字节确定性由「同快照同字节」保证，规范化序由快照契约保证。
    """
    import copy

    out = copy.copy(snapshot)
    out.sections = []
    for sec in snapshot.sections:
        declared = snapshot.declared_fields_for(sec.root_key)
        out.sections.append(
            Section(
                root_key=sec.root_key,
                entries=sorted(sec.entries, key=lambda e: _identity_key_for(sec.root_key, e, declared)),
            )
        )
    return out
