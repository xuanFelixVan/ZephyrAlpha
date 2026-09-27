# [BLUEPRINT] MOD-LIB-004 | docs/03_modules/_domain_library/blueprint.md | §4
# [MODULE] zephyr.library.collectors.store_collector
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.library.ledger_schema (derive_asset_id); yaml (只读真源解析)
# [CONSUMERS] zephyr.library.collectors; scripts/governance/generators/generate_library_index.py
# [STARTUP] imported
# [MATURITY] experimental
# [INVARIANTS] 第 7 路采集器：基建与备份馆入馆谓词只认 kind∈{backup,infra}，六路采集器零产出⇒馆空是数学必然（案卷=docs/_working/fms_overhaul/95_external_review/library_naming_and_local_mcp.md A4），本模块补产出端不新增馆/kind/册；只读三真源（INFRA-STORE-* / offrepo_assets / backup_config 盘位键）；一条登记条目=一条资产（族级，禁逐件枚举冷储大盘）；home 一律登记册条目锚定 `<真源相对路径>#<条目号>`（照抄 logs_collector 先例），仓外绝对路径永不进 home——历史唯一 F 盘 FILE: 资产正因 home=盘路径被 coverage 判 ghost 自裁；盘符真源=三本 config/YAML 内容，代码零盘路径常量；四态盘位判定（present/ghost_registered/disk_unreachable/no_physical_location）落 fingerprint_aux+tags+status（status 在 register_batch 通道被 COALESCE(%s,'active') 归 active，故判定不独赖 status）；拔盘≠幽灵（不可观测不得判缺失）；盘不可达只标 degraded 不抛穿；零 SQL 零写
# [MODIFY-GUARD] gate_id 不适用
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 任一真源缺失/解析失败 → [{"error": ...}]（collect_all 兜底）；F/G 盘不可达不是错误，照常产出资产并标 disk_unreachable
# [TESTS] tests/library/test_store_collector.py
# [A_module] module_id=MOD-LIB-004 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""store_collector — 图书馆第 7 采集器（MOD-LIB-004，只读）：F/G 冷储与备份资产入册。

馆为什么空：`generate_library_index.py` 的"基建与备份馆"入馆谓词是
`kind in ("backup","infra")`，而既有六路采集器（fs/pg/ch/schtasks/mcp/logs）
无一产出这两个 kind ⇒ 该馆恒 0 条。补齐产出端即接入，不新建馆（根宪法 §4 净零）。

真源三本（本模块只读，不改写）：
  1. `docs/01_policies_and_standards/_registry/catalogs/infrastructure_registry.yaml`
     的 `INFRA-STORE-*` 条目 → `INF:`（基建登记条目）
  2. `config/asset_inventory.yaml` 的 `offrepo_assets` → 有镜像备份=`BAK:`、无备份覆盖=`INF:`
  3. `scripts/backup/backup_config.yaml` 的 `base`/`target` 盘位 → `BAK:`（备份落点）

姿势：登记册条目锚定（同 logs_collector），一条目一资产，明细进大盘自查；
盘位只 stat 不读写，拔盘态显式 degraded，绝不抛穿拖垮整馆。
# [ALGO_FLOW] external: docs/03_modules/_domain_library/algo_flow/collectors/store_collector.yaml
"""

from __future__ import annotations

from pathlib import Path, PureWindowsPath
from typing import Any, Final, NamedTuple

import yaml

from zephyr.library.ledger_schema import derive_asset_id

__all__: Final = ["collect"]

INFRA_REGISTRY_REL: Final[str] = "docs/01_policies_and_standards/_registry/catalogs/infrastructure_registry.yaml"
ASSET_INVENTORY_REL: Final[str] = "config/asset_inventory.yaml"
BACKUP_CONFIG_REL: Final[str] = "scripts/backup/backup_config.yaml"

# 存储族条目号前缀（本批纳入面；其余 infra 族不属冷储/备份，不扩权）
_STORE_ID_PREFIX: Final[str] = "INFRA-STORE-"
# backup_config 中"备份落点"的键名书写约定（只认这两键，不猜语义）
_POSITION_KEYS: Final[frozenset[str]] = frozenset({"base", "target"})
# 含占位/模板/注释字符的串不是可定位盘位（logs_collector placeholder 同法）
_UNLOCATABLE_CHARS: Final[str] = "{}<>（"

OBS_PRESENT: Final[str] = "present"
OBS_GHOST: Final[str] = "ghost_registered"
OBS_UNREACHABLE: Final[str] = "disk_unreachable"
OBS_NO_PATH: Final[str] = "no_physical_location"

_OBS_STATUS: Final[dict[str, str]] = {
    OBS_PRESENT: "active",
    OBS_GHOST: "ghost",
    OBS_UNREACHABLE: "blind",
    OBS_NO_PATH: "active",
}
# 判定态同时进 tags：register_batch 通道 status 被 COALESCE 归 active，tags 才是落账后可查面
_OBS_TAG: Final[dict[str, str]] = {OBS_GHOST: "幽灵登记", OBS_UNREACHABLE: "盘不可达"}
_KIND_TAGS: Final[dict[str, tuple[str, ...]]] = {
    "infra": ("外溢资产", "冷储基建"),
    "backup": ("外溢资产", "备份落点"),
}


class _Spec(NamedTuple):
    """一条登记条目 → 一条资产的中间表示（真源指针随条目走）。"""

    kind: str
    source_rel: str
    anchor: str
    title: str
    locations: tuple[str, ...]
    raw: str
    register_status: str
    line: int | None
    note: str


def _load(rel: str, root: Path) -> tuple[dict[str, Any], str]:
    """读一本真源（缺盘/坏档抛错，由 collect 折叠为 error 记录）。

    Args:
        rel: 真源相对路径。
        root: 仓库根。

    Returns:
        (解析后的 YAML, 原文文本)。

    Raises:
        FileNotFoundError: 真源不存在（在册真源缺失不许静默）。
    """
    path = root / rel
    if not path.exists():
        raise FileNotFoundError(rel)
    text = path.read_text(encoding="utf-8")
    return (yaml.safe_load(text) or {}), text


def _locations_of(raw: str) -> tuple[str, ...]:
    """从登记串里切出可定位盘位（多盘串 "F:/a + G:/b"、分号、反斜杠皆吃）。"""
    parts: list[str] = []
    for chunk in raw.replace(";", "+").replace("\n", "+").split("+"):
        seg = chunk.strip().strip("\"'")
        if not seg or any(ch in seg for ch in _UNLOCATABLE_CHARS):
            continue
        parts.append(seg)
    return tuple(parts)


def _norm(loc: str) -> str:
    """盘位串 → 统一正斜杠可判定形态（重复分隔符一并收掉）。"""
    return PureWindowsPath(loc).as_posix()


def _drive_of(loc: str) -> str:
    """取盘符（来自真源内容，禁代码常量）；仓内相对路径返回空串。"""
    return PureWindowsPath(loc).drive


def _drive_root(drive: str) -> Path | None:
    """盘符 → 可探测盘根；未挂载/拔盘返回 None（测试 monkeypatch 本缝造假盘根）。"""
    try:
        base = Path(f"{drive}/")
        return base if base.is_dir() else None
    except OSError:  # pragma: no cover — 只读探测，异常按不可达处理
        return None


_PROBE_MISSING: Final[str] = "location_missing"


def _probe(loc: str, root: Path) -> str:
    """单盘位三态：unreachable / location_missing / present（只 stat，零读写内容）。"""
    drive = _drive_of(loc)
    base = root if not drive else _drive_root(drive)
    if base is None:
        return OBS_UNREACHABLE
    rel = _norm(loc)[len(drive) :].strip("/") if drive else _norm(loc)
    return OBS_PRESENT if (base / rel).exists() else _PROBE_MISSING


def _observe(locations: tuple[str, ...], root: Path) -> dict[str, Any]:
    """盘位聚合判定（拔盘优先：不可观测不得判成缺失）。"""
    if not locations:
        return {"state": OBS_NO_PATH, "missing": [], "unreachable": []}
    missing: list[str] = []
    unreachable: list[str] = []
    for loc in locations:
        verdict = _probe(loc, root)
        if verdict == OBS_UNREACHABLE:
            unreachable.append(_drive_of(loc) or ".")
        elif verdict == _PROBE_MISSING:
            missing.append(_norm(loc))
    if unreachable:
        state = OBS_UNREACHABLE
    elif missing and len(missing) == len(locations):
        state = OBS_GHOST
    else:
        state = OBS_PRESENT
    return {"state": state, "missing": missing, "unreachable": sorted(set(unreachable))}


def _id_line(text: str, needle: str) -> int | None:
    """登记册条目定位：返回首个含 needle 的行号（1 基，可 grep 复核）。"""
    for idx, line in enumerate(text.splitlines(), start=1):
        if needle in line:
            return idx
    return None


def _key_line(text: str, section: str, leaf: str) -> int | None:
    """backup_config 定位：先找顶层节标题行，再在节内找键行或 `- id:` 条目行。"""
    lines = text.splitlines()
    start = 0
    for idx, line in enumerate(lines):
        if line.rstrip() == f"{section}:":
            start = idx + 1
            break
    else:
        return None
    for idx in range(start, len(lines)):
        line = lines[idx]
        if line and not line[0].isspace():
            break
        stripped = line.strip()
        if stripped.startswith(f"{leaf}:") or stripped.endswith(f"id: {leaf}"):
            return idx + 1
    return None


def _from_infra_registry(data: dict[str, Any], text: str) -> list[_Spec]:
    """真源 1：infrastructure_registry 的 INFRA-STORE-* 条目 → INF:。"""
    specs: list[_Spec] = []
    for entry in data.get("infrastructure") or []:
        infra_id = str(entry.get("infra_id") or "")
        if not infra_id.startswith(_STORE_ID_PREFIX):
            continue
        raw = str(entry.get("host") or "")
        specs.append(
            _Spec(
                kind="infra",
                source_rel=INFRA_REGISTRY_REL,
                anchor=infra_id,
                title=str(entry.get("name") or infra_id),
                locations=_locations_of(raw),
                raw=raw,
                register_status=str(entry.get("status") or ""),
                line=_id_line(text, infra_id),
                note=str(entry.get("description") or ""),
            )
        )
    return specs


def _from_asset_inventory(data: dict[str, Any], text: str) -> list[_Spec]:
    """真源 2：asset_inventory offrepo_assets → 有镜像=BAK:、无备份覆盖=INF:。"""
    specs: list[_Spec] = []
    for entry in data.get("offrepo_assets") or []:
        asset_id = str(entry.get("id") or "")
        if not asset_id:
            continue
        backup_policy = str(entry.get("backup") or "")
        raw = str(entry.get("path") or "")
        specs.append(
            _Spec(
                kind="backup" if backup_policy == "mirror" else "infra",
                source_rel=ASSET_INVENTORY_REL,
                anchor=asset_id,
                title=f"{entry.get('type', '仓外资产')}｜{asset_id}",
                locations=_locations_of(raw),
                raw=raw,
                register_status=backup_policy,
                line=_id_line(text, asset_id),
                note=str(entry.get("notes") or ""),
            )
        )
    return specs


def _walk_positions(node: object, prefix: str) -> list[tuple[str, str, str]]:
    """深搜备份配置盘位键，产 (锚点, 顶层节名, 盘位串)；列表项以自身 id 入锚点。"""
    found: list[tuple[str, str, str]] = []
    if isinstance(node, list):
        for item in node:
            if isinstance(item, dict) and item.get("id"):
                ident = str(item["id"])
                found.extend(_walk_positions(item, f"{prefix}{ident}."))
            else:
                found.extend(_walk_positions(item, prefix))
        return found
    if not isinstance(node, dict):
        return found
    for key, value in node.items():
        if isinstance(value, str) and key in _POSITION_KEYS:
            found.append((f"{prefix}{key}", prefix.split(".")[0], value))
        elif isinstance(value, (dict, list)):
            found.extend(_walk_positions(value, f"{prefix}{key}."))
    return found


def _from_backup_config(data: dict[str, Any], text: str) -> list[_Spec]:
    """真源 3：backup_config 的 base/target 盘位 → BAK:（备份落点）。"""
    specs: list[_Spec] = []
    for anchor, section, raw in _walk_positions(data, ""):
        leaf = anchor.split(".")[-1]
        loc = raw.replace("\\", "/")
        specs.append(
            _Spec(
                kind="backup",
                source_rel=BACKUP_CONFIG_REL,
                anchor=anchor,
                title=f"备份落点 {anchor}",
                locations=_locations_of(loc),
                raw=raw,
                register_status=str(data.get("version") or ""),
                line=_key_line(text, section, leaf),
                note="备份脚本落点（backup.ps1/backup_reconciler.py 消费）",
            )
        )
    return specs


def _asset(spec: _Spec, root: Path) -> dict[str, Any]:
    """条目 → 总账资产字典（真源指针 + 四态盘位判定）。"""
    obs = _observe(spec.locations, root)
    state = obs["state"]
    home = f"{spec.source_rel}#{spec.anchor}"
    source_ref = f"{spec.source_rel}:{spec.line}" if spec.line else home
    tags = list(_KIND_TAGS[spec.kind])
    extra_tag = _OBS_TAG.get(state)
    if extra_tag:
        tags.append(extra_tag)
    ai_contract = (
        f"仓外基建/备份资产（族级入册，登记册条目锚定）：真源指针={source_ref}；"
        f"登记盘位={_norm_list(spec.locations) or '未登记（规划项/占位串）'}；"
        f"盘态={state}；在册但盘上无={_norm_list(obs['missing']) or '无'}；"
        f"不可达盘={', '.join(obs['unreachable']) or '无'}；登记状态={spec.register_status}。"
        "物理位在仓外盘，本采集器只 stat 不读写，明细大盘自查；"
        "盘不可达=拔盘态 degraded，不得据本条判缺失或删除。"
    )
    return {
        "asset_id": derive_asset_id(spec.kind, home),
        "kind": spec.kind,
        "home": home,
        "status": _OBS_STATUS[state],
        "title": spec.title,
        "one_liner": spec.note[:200],
        "ai_contract": ai_contract,
        "owner_domain": None,
        "retention_class": "long",
        "tags": tags,
        "fingerprint_aux": {
            "source_file": spec.source_rel,
            "source_anchor": spec.anchor,
            "source_ref": source_ref,
            "source_line": spec.line,
            "register_status": spec.register_status,
            "raw_locations": spec.raw,
            "physical_locations": [_norm(loc) for loc in spec.locations],
            "obs_state": state,
            "missing_locations": obs["missing"],
            "unreachable_drives": obs["unreachable"],
            "degraded": state in (OBS_GHOST, OBS_UNREACHABLE),
        },
    }


def _norm_list(locations: tuple[str, ...] | list[str]) -> str:
    """盘位列表 → 可读串（ai_contract 用，正斜杠统一）。"""
    return ", ".join(_norm(str(loc)) for loc in locations)


def collect(root: str = ".") -> list[dict[str, Any]]:
    """三真源派生 `INF:`/`BAK:` 资产（fail-soft，拔盘不抛穿）。

    Args:
        root: 仓库根（测试注入 tmp_path；盘符来自真源内容）。

    Returns:
        资产列表；真源缺失/解析失败折叠为 [{"error": ...}]。
    """
    try:
        base = Path(root)
        infra_data, infra_text = _load(INFRA_REGISTRY_REL, base)
        inventory_data, inventory_text = _load(ASSET_INVENTORY_REL, base)
        backup_data, backup_text = _load(BACKUP_CONFIG_REL, base)
        specs = [
            *_from_infra_registry(infra_data, infra_text),
            *_from_asset_inventory(inventory_data, inventory_text),
            *_from_backup_config(backup_data, backup_text),
        ]
        return [_asset(spec, base) for spec in specs]
    except Exception as exc:  # noqa: BLE001 — fail-soft（collect_all 兜底口径）
        return [{"error": f"{type(exc).__name__}: {exc}"}]
