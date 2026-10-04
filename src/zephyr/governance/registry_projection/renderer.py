# [MODULE] zephyr.governance.registry_projection.renderer
# [DOMAIN] D_GOV_CODE_QUALITY
# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §W-M1
# [TTL] permanent
# [DEPENDENCIES] yaml；zephyr.governance.registry_projection.model (ProjectionSnapshot)
# [CONSUMERS] zephyr.governance.registry_projection.generator / generator CLI
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] render(snapshot) 是纯函数：无时钟/无随机/无环境依赖，同快照永远同字节；
#   零 volatile 字段（生成元数据只进状态文件与账本审计，不进产物）；UTF-8 无 BOM+
#   LF+文件尾单换行；写盘前语义等值断言（safe_load 回读 vs 快照）不等即拒写；
#   身份键往返不变断言（快照身份集==渲染重扫身份集，声明族零坍缩）——st-sI-identity-20261004
# [MODIFY-GUARD] 新建 2026-09-23 st-wm1-buildB-20260923（W-M1 波0 车道B）；
#   2026-10-04 st-sI-identity-20261004 补身份断言（f10 §3 盲区封死）
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] SemanticMismatch（自校验失败）=调用方拒写；渲染本身对任何快照可判定（不抛=有产物）
# [TESTS] tests/governance/registry_projection/test_projection_renderer.py
"""renderer.py — YAML := render(snapshot) 纯函数投影器。

发射规则（丙号文 §2.3 确定性规范）：
- 头部元行 verbatim；条目字段按快照对序直出；尾部标量（di_seam_exemptions）居末；
- 标量引号：merge_evaluation 恒双引号（_yaml_quote 法系/现文件主流形态），其余标量
  含 YAML 保留字才双引号；非标量值（aliases/内嵌结构）经固定参数 yaml.dump 子树发射；
- 排序不在 render 内做：render 严格保快照序，规范化序=(file,token) 字节序由快照契约
  （publish 侧 canonicalize）保证——排序与合并器复合身份同构。

与遗留手工文件的字节残差（折行点/整批引号方言/空行）是 cutover 一次性归一噪音
（丙号文 §5 W4 预算项），不属本函数的验收口径；本函数验收=字节确定性+语义等值。


# [ALGO_FLOW]
层: 渲染 → 自校验
- 渲染: 排序键 (file, token) 字节序全量重打，标量引号规则确定性，零 volatile 字段
- 自校验: safe_load 回读与输入语义等值断言，不等拒写"""

from __future__ import annotations

from typing import Final

__all__: Final = ["SemanticMismatch", "render", "render_field", "semantic_model"]

_FOLD_WIDTH = 120

# YAML 保留字触发双引号的判定（plain style 不安全面）
_PLAIN_UNSAFE_PREFIX = "-?:,[]{}#&*!|>'\"%@` \t"
_ALWAYS_QUOTE_KEYS: Final = {"merge_evaluation"}


class SemanticMismatch(AssertionError):
    """渲染自校验失败（safe_load 回读 vs 快照语义不等）——拒写。"""


def _needs_quoting(text: str) -> bool:
    if text == "":
        return True
    if text != text.strip():
        return True
    if any(c in text for c in ("\n", "\t", "\x00")):
        return True
    if ": " in text or " #" in text:
        return True
    if text[0] in _PLAIN_UNSAFE_PREFIX:
        return True
    # 解析歧义防呆：裸发射会变型的标量（007→int、true→bool、1.5→float 等）必须加引号——
    # 渲染必须无损（safe_load 回读 == 原字符串）
    import yaml

    try:
        parsed = yaml.safe_load(text)
    except Exception:  # noqa: BLE001 — 解析不了=必须引
        return True
    if not isinstance(parsed, str) or parsed != text:
        return True
    return False


def _quote(text: str) -> str:
    escaped = text.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n").replace("\t", "\\t")
    return f'"{escaped}"'


def _emit_scalar_value(value: object, *, key: str = "") -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    text = str(value)
    if key in _ALWAYS_QUOTE_KEYS:
        return _quote(" ".join(text.split()) if "\n" in text else text)
    if _needs_quoting(text):
        return _quote(text)
    return text


def _dump_subtree(value: object) -> list[str]:
    """非标量值经固定参数 yaml.dump 发射（width 无关化→无折行，确定性由参数钉死）。"""
    import yaml

    dumped = yaml.dump(
        value,
        allow_unicode=True,
        default_flow_style=False,
        sort_keys=False,
        width=10**6,
        indent=2,
    )
    return dumped.split("\n")[:-1] if dumped.endswith("\n") else dumped.split("\n")


def render_field(key: str, value: object, indent: int) -> list[str]:
    """单字段 → 行片（不含条目首行的 '- ' 前缀，调用方拼装）。"""
    pad = " " * indent
    if value == [] or value == {}:
        return [f"{pad}{key}: {'[]' if isinstance(value, list) else '{}'}"]
    if isinstance(value, list) and value and all(isinstance(v, (str, int, float, bool)) or v is None for v in value):
        # 纯标量序列：块式（dash 与键同列，现文件形态）
        return [f"{pad}{key}:"] + [f"{pad}- {_emit_scalar_value(v)}" for v in value]
    if isinstance(value, (dict, list)):
        sub = _dump_subtree(value)
        # dict 子树必须比键再进 2 格才是合法嵌套映射（list 的 dash 序列在键同级合法）；
        # 2026-10-03 治本：此前只垫 pad → dict 值子键漏成条目兄弟键（overlay_mode 拍扁=dataflowgraph 假键同根因）
        return [f"{pad}{key}:"] + [f"{pad}  {line}" if isinstance(value, dict) else f"{pad}{line}" for line in sub]
    return [f"{pad}{key}: {_emit_scalar_value(value, key=key)}"]


def _render_entry(entry: list[tuple[str, object]], indent: int, first_prefix: str) -> list[str]:
    lines: list[str] = []
    for i, (key, value) in enumerate(entry):
        field_lines = render_field(key, value, indent)
        if i == 0:
            field_lines[0] = first_prefix + field_lines[0].lstrip()
        lines.extend(field_lines)
    return lines


def render(snapshot) -> str:
    """ProjectionSnapshot → 字节流（纯函数，同快照永远同字节）。"""
    out: list[str] = list(snapshot.header_lines)
    for sec in snapshot.sections:
        out.append(f"{sec.root_key}:")
        for entry in sec.entries:
            out.extend(_render_entry(entry, indent=2, first_prefix="- "))
    for key, value in snapshot.trailing_scalars:
        out.extend(render_field(key, value, indent=0))
    return "\n".join(out) + "\n"


def semantic_model(snapshot) -> dict[str, object]:
    """快照 → safe_load 等价形态（头部标量解析+节段条目折叠重复键=取后值）。"""
    import yaml

    header = yaml.safe_load("\n".join(snapshot.header_lines)) or {}
    model: dict[str, object] = dict(header)
    for sec in snapshot.sections:
        model[sec.root_key] = [{k: v for k, v in entry} for entry in sec.entries]
    for key, value in snapshot.trailing_scalars:
        model[key] = value
    return model


def _identity_str(entry: list[tuple[str, object]], declared_fields: tuple[str, ...] | None) -> str | None:
    """条目（有序对列表）→ 身份键串（ledger entry_composite_key 同源：声明优先/位置回退）。"""
    from zephyr.governance.registry_ledger.ledger_identity import entry_composite_key  # noqa: PLC0415

    payload: dict[str, object] = {}
    for k, v in entry:  # 重复键取后值（safe_load 同判据）
        payload[k] = v
    return entry_composite_key(payload, declared_fields)


def _rescan_family_blocks(rendered: str) -> dict[object, list[object]]:
    """渲染产物重扫（与账本盘面扫描同一切分真源）→ {族键: 条目 blk.data 序}。"""
    from scripts.governance.commit_queue_landing import _split_registry_entries  # noqa: PLC0415

    families, err = _split_registry_entries(rendered)
    if err:
        raise SemanticMismatch(f"渲染产物重扫失败（切分器报错）: {err}")
    return {fam_key: [blk.data for blk in fam.blocks] for fam_key, fam in families.items()}


def self_check(rendered: str, snapshot) -> None:
    """写盘前语义等值断言（丙号文 §2.3.5）：不等即 SemanticMismatch 拒写。

    st-sI-identity-20261004 补身份断言（f10 §3 守卫盲区实证封死）：safe_load 等值
    断言序不敏感，测不出身份口径漂移（B3 期七册全 PASS 而身份坍缩 7749）——增判
    ①身份键往返不变：快照节段身份集 == 渲染重扫同族身份集（同声明口径，序不敏感盲区封死）；
    ②声明族身份零坍缩：有 unique_key 声明的族，唯一身份数==条目数（撞并即拒写）。
    """
    import yaml

    rendered_model = yaml.safe_load(rendered)
    if rendered_model != semantic_model(snapshot):
        raise SemanticMismatch("渲染回读语义与快照不等（键集/字段级/段序断言失败）——拒写")

    rescan_blocks = _rescan_family_blocks(rendered)
    for sec in snapshot.sections:
        declared = snapshot.declared_fields_for(sec.root_key)
        snap_ids = [_identity_str(entry, declared) for entry in sec.entries]
        rescan_ids = [
            _identity_str(list(data.items()), declared) if isinstance(data, dict) else None
            for data in rescan_blocks.get(sec.root_key, [])
        ]
        # ① 身份键往返不变：集合相等（None=passthrough 边界，两侧同判据剔除）
        snap_set = {i for i in snap_ids if i is not None}
        rescan_set = {i for i in rescan_ids if i is not None}
        if snap_set != rescan_set:
            lost = sorted(snap_set - rescan_set)[:3]
            gained = sorted(rescan_set - snap_set)[:3]
            raise SemanticMismatch(f"身份键往返漂移（族 {sec.root_key}）：渲染重扫丢 {lost} / 增 {gained}——拒写")
        # ② 声明族零坍缩：声明 unique_key 即唯一性契约，撞并=身份口径漂移（B3 病灶形态）
        if declared:
            valid = [i for i in snap_ids if i is not None]
            if len(set(valid)) < len(valid):
                seen: set[str] = set()
                dupes = sorted({i for i in valid if (i in seen or seen.add(i))})[:3]
                raise SemanticMismatch(f"声明族 {sec.root_key} 身份坍缩（声明唯一键撞并 {dupes}）——拒写")
