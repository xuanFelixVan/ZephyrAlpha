# [BLUEPRINT] MOD-INF-005 | scripts/governance/d3_metadata/add_module_translation.py | §
# [MODULE] scripts.governance.d3_metadata.add_module_translation
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance._shared.module_translation_loader (is_generic_plain_zh, is_generic_plain_suffix, get_module_translation); scripts.governance._shared.yaml_utils (load_responsibility_layer_map); docs/01_policies_and_standards/_registry/catalogs/module_translation_registry.yaml (机生只读投影，账本 REG-MODULE-TRANSLATION-001 的 render 产物); docs/01_policies_and_standards/_registry/catalogs/domain_responsibility_layer_mapping.yaml (responsibility_layer 唯一真源); zephyr.governance.registry_ledger.api (register/update/fetch，lazy); zephyr.governance.registry_ledger.baseline (publish_snapshot，lazy); zephyr.governance.registry_projection.projection_generator (run/render, _entry_index，lazy); zephyr.governance.registry_projection.pg_source (load_latest_snapshot，lazy); zephyr.infrastructure.database_service (账本只读面，lazy); zephyr.shared.utils.time_utils (now_utc，审计留痕)
# [CONSUMERS] AI 新建/更新模块时调用以合规登记大白话简介（意图 API 薄壳单口）；TRANSLATION-COVERAGE gate 修复指引引用本 CLI；scripts/governance/dead_letter_doctor.py:702（add_translation 函数级复用，签名兼容）；进程内测试=tests/gov/governance/d3_metadata/test_module_translation_ledger_channel.py
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 按 module_path 唯一键登记；写入前 MUST 通过 is_generic_plain_zh/is_generic_plain_suffix 校验（拒模板化简介，治本）；**登记唯一通道=意图 API 三步**（api.register/update 写 PG 账本 → baseline.publish_snapshot(带 repo_root) → registry_projection render），直写投影轨已退役（裁定#502 同款薄壳，本工具与 batch_creation_tokens 同病同治）；PG 不可达=登记失败（exit 2），绝不静默降级直写；**键集合差分幂等**：本次未声明的键（含空值参数）永不改动在册值，已存 module_path 永不整条覆盖（2026-09-27 字段级蒸发教训），删除集只能由 --clear-field 逐条点名或 responsibility_layer 重算派生，越界删除=拒写；responsibility_layer 唯一推导通道=域→职责层映射真源（裁定#335 结论⑥，禁从 layer_id/目录名直推），**映射真源故障时不派生也不删除**（在册值原样，防瞬时故障改写真源）；账本写后 MUST publish+render 并三方核验落地（PG 有该行 ∧ 盘上投影面 grep 命中该 module_path）；--legacy-disk-write 为显式逃生旗（缺省不走），直写条目会被下次 render 当非账本内容修剪=红色警告+JSONL 审计留痕；--dedupe/--sync-layer 是投影面手术（账本不认，render 后失效）已在帮助文本如实标注
# [MODIFY-GUARD] scripts/governance/d3_metadata/add_module_translation.py — 2026-10-11 st-maint2-20261011 直写轨退役（裁定#502 先例，无账本通道病根治）：add_translation 语义从"直写投影 YAML"改"意图 API 三步+三方核验"，签名兼容（entry, dry_run）不变，旧直写腿改名 _add_translation_via_disk_projection 仅服务 --legacy-disk-write/--dedupe/--sync-layer
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] exit 0=SUCCESS（登记/预演/审计零命中）, exit 1=VALIDATION_ERROR(简介不合规/字段缺失/子命令参数互斥/账本同键多 active 行/审计命中=投影面有而快照无), exit 2=IO/YAML_ERROR/LEDGER_UNREACHABLE（账本不可达=登记失败，不降级直写；投影册读写失败；快照不可取）
# [TESTS] tests/gov/governance/d3_metadata/test_module_translation_ledger_channel.py
# [A_module] module_id=MOD-INF-005 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""add_module_translation.py — 模块翻译条目合规登记工具（意图 API 薄壳，TRANSLATION-COVERAGE 配套）。

把"在哪里更新 / 怎么更新"落地为一条命令：AI 新建或更新模块时，调用本脚本向翻译账本
``REG-MODULE-TRANSLATION-001`` 登记一条 entry（含大白话 plain_zh），随后发布快照+重打投影。

真源边界（SSoT 分类铁律 TRAE-062 → 2026-10-04 cutover 后口径）
--------------------------------------------------------------
模块翻译条目的**真源是 PG registry_ledger 账本**，
``module_translation_registry.yaml`` 是机生只读投影（唯一合法写者=投影生成器）。
本工具因此不再是 YAML 写者：登记一律走意图 API 三步——

    1. api.register / api.update（写账本；幂等=键集合差分，未声明的键不动在册值）
    2. baseline.publish_snapshot(REGISTRY_ID, repo_root=...)（发布不可变快照，禁裸发布）
    3. registry_projection run(mode="render")（PG-wins 重打投影册）

死路三步（2026-10-11 定案，本工具曾经的病，与 batch_creation_tokens 同一条根）：
直写投影 YAML → 条目没入账本 → 下一次 render 按账本把它整块修剪掉（实测 v17→v18 期间
``scripts/backup/backup_reconciler_shadow.py`` 一条被 00:52/00:53 两次 render 剪掉）→
TRANSLATION-COVERAGE gate 读投影判缺失又指示跑本工具 = 死循环。现通道改道，循环断开。

账本不可达 = 登记失败（exit 2），**绝不静默降级直写投影**（降级=把死路重新接通）。
``--legacy-disk-write`` 是显式逃生旗：缺省不走，走则打红色警告（"直写条目会被下次 render
修剪"）并落一行 JSONL 审计留痕。

写入前校验（治本，非事后）
--------------------------
1. plain_zh 非空且 CJK≥8（与本次治理基线一致）
2. 复用 module_translation_loader.is_generic_plain_zh 拒全串通用模板
3. 复用 is_generic_plain_suffix 拒剥离 name 前缀后的通用后缀
任一不过 → exit 1，拒绝登记（防 AI 填"提供包入口和模块加载功能"糊弄）。

用法 / Usage::

    # 登记/更新一条大白话简介（缺省=账本通道：register→publish→render→三方核验）
    python scripts/governance/d3_metadata/add_module_translation.py \\
        --path src/zephyr/xxx/yyy.py \\
        --domain D_GOV_RULE \\
        --name-zh "中文名" --name-en "English Name" \\
        --desc-zh "技术简介" --desc-en "English desc" \\
        --plain-zh "大白话：做什么/解决什么/怎么做" \\
        --session my-session

    # 只看账不写（校验+派生+账本差分预演，零 PG 写/零发布/零 render）
    python ... --path ... --domain ... --name-zh ... --plain-zh ... --dry-run

    # 点名删除某字段（删除集必须逐条点名，未点名的键永不从在册 payload 消失）
    python ... --path ... --clear-field desc_en

    # 回填扫描（只读，零写）：报"投影面有而最新快照无"的条目（shadow 事故的机判形态）
    python scripts/governance/d3_metadata/add_module_translation.py --audit-projection-vs-ledger

    # 整表手术（投影面通道，账本不认——render 一到即被覆写，仅作过渡期对账预览用）
    python ... --dedupe [--dry-run]
    python ... --sync-layer [--dry-run]

responsibility_layer 派生铁律（裁定#335 结论⑥）
--------------------------------------------------
新条目登记时按 ``--domain`` 自动派生 ``responsibility_layer``，唯一推导通道是
域→职责层映射真源（经 ``yaml_utils.load_responsibility_layer_map``）；**禁从
layer_id/目录名直推**（争点 C1/C17）。映射查不到该域 → stderr WARNING + 该字段留空
（不阻断翻译登记）；映射可用而调用方塞了别的值 → 以真源为准覆盖。
派生字段永不从旧行继承（否则映射删域后旧值复活）；**映射真源本身不可用 → 该字段
不派生也不删除**（在册值原样——瞬时故障不该改写真源）。

Exit codes:
    0 = SUCCESS（账本登记+发布+重打+核验通过，或 dry-run 预演通过，或审计零命中）
    1 = VALIDATION_ERROR（简介不合规 / 必填字段缺失 / 子命令参数互斥 / 账本同键多
        active 行 / 审计命中"投影面有而快照无"）
    2 = IO / YAML_ERROR / LEDGER_UNREACHABLE（账本不可达=登记失败、投影册读写失败、
        快照不可取、CAS 拒写、解析失败）
"""

from __future__ import annotations

__manifest__ = """
args: []
description: add_module_translation.py — 模块翻译条目合规登记工具（意图 API 薄壳，TRANSLATION-COVERAGE 配套）。
dimensions:
- D3
priority: P2
timeout_seconds: 60
warn_only: false
"""


import argparse
import json
import re
import sys
from pathlib import Path

import yaml  # type: ignore[import-untyped]

# bootstrap _shared（与同目录其他 d3_metadata 脚本一致，使 module_translation_loader 可 import）
_THIS_FILE = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _THIS_FILE.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import REPO_ROOT  # noqa: E402
from _shared.module_translation_loader import (  # noqa: E402
    is_generic_plain_suffix,
    is_generic_plain_zh,
)
from _shared.yaml_utils import (  # noqa: E402 — re-export of SSoT src/zephyr/shared/io/yaml_utils
    DEFAULT_REGISTRY_CATALOG_DIR,
    RESPONSIBILITY_LAYER_MAP_FILE,
    load_responsibility_layer_map,
)

# 投影册路径（2026-10-04 cutover 后：机生只读投影，真源=PG 账本 REG-MODULE-TRANSLATION-001）
REGISTRY_ID = "REG-MODULE-TRANSLATION-001"
FAMILY_KEY = "entries"
REGISTRY_REL = "docs/01_policies_and_standards/_registry/catalogs/module_translation_registry.yaml"
REGISTRY_YAML = REPO_ROOT / REGISTRY_REL

# 发布/重打所用仓库根（=本工作树根）。测试与施工沙盘用注入点：改这一个名字 +
# REGISTRY_YAML 即可把整条通道（publish/render/落地核验）切到 tmp 仓，不写真仓。
PROJECTION_ROOT = REPO_ROOT

# 账本条目只读点查（§5.160.2 SQL 集中化：模块级 SQL_ 常量，参数化查询）
SQL_TRANSLATION_ROW_BY_MODULE_PATH = (
    "SELECT entry_key, payload, version, status FROM registry_ledger.registry_entry "
    "WHERE registry_id=%s AND family_key=%s AND payload->>'module_path'=%s ORDER BY version DESC"
)

# 登记缺省归因会话名（CLI --session 可覆盖；账本 created_by/updated_by 落此值）
DEFAULT_SESSION = "add_module_translation"

# 意图 API 返回码字面量（与 zephyr.governance.registry_ledger.api.OK/OK_NOOP/
# CONFLICT_DUPLICATE/CONFLICT_VERSION 同值）。此处刻意不 import api：前置校验与
# --dry-run 必须在缺 psycopg2/PG 的环境也能跑（api 模块级 import psycopg2）；
# 等值由 tests/gov/governance/d3_metadata/test_module_translation_ledger_channel.py 机械断言。
_CODE_OK = "OK"
_CODE_NOOP = "OK_NOOP"
_CODE_CONFLICT_DUPLICATE = "CONFLICT_DUPLICATE"
_CODE_CONFLICT_VERSION = "CONFLICT_VERSION"

# 逃生旗审计留痕（只追加；根宪法 §9.4 禁向 .runtime 根直写 → 走 gate_audit 子目录）
LEGACY_DISK_WRITE_AUDIT_PATH = REPO_ROOT / ".runtime" / "gate_audit" / "add_module_translation_legacy_disk_write.jsonl"

# 域→responsibility_layer 映射真源路径（路径公式单一来源在 yaml_utils；
# 本模块常量同时是测试注入点——monkeypatch 此名即可换成 tmp 假映射，不读真仓）
RESPONSIBILITY_LAYER_MAP_YAML = DEFAULT_REGISTRY_CATALOG_DIR / RESPONSIBILITY_LAYER_MAP_FILE

# 派生字段名（裁定#335 结论⑥ 钉名：新字段只可叫 responsibility_layer）
_LAYER_KEY = "responsibility_layer"
# 派生字段集合：只由映射重算，永不从旧块/重复块继承（防映射删域后旧值复活）
_DERIVED_KEYS: frozenset[str] = frozenset({_LAYER_KEY})

# plain_zh 最低 CJK 字符数（与本次治理基线一致，防过短无信息简介）
_MIN_CJK = 8

EXIT_SUCCESS = 0
EXIT_VALIDATION = 1
EXIT_IO = 2


def _cjk_len(s: str) -> int:
    """统计 CJK 字符数（大白话最低信息量基线）。"""
    return len(re.findall(r"[\u4e00-\u9fff]", s or ""))


def _yaml_quote(s: str) -> str:
    """YAML 双引号转义（治本：plain_zh 含冒号/引号/破折号时安全）。

    对标 tmp/_apply_handwritten.py 验证过的转义逻辑：反斜杠→双反斜杠，
    双引号→\\\\\"，控制字符→转义序列。始终用双引号包裹，确保含 ``: ``/``#``
    的值不被 YAML 误解析。
    """
    s = s.replace("\\", "\\\\").replace('"', '\\"')
    s = s.replace("\n", "\\n").replace("\r", "\\r").replace("\t", "\\t")
    return '"%s"' % s


def _normalize_path(p: str) -> str:
    """module_path 正斜杠归一化（Windows 反斜杠兼容）。"""
    return (p or "").replace("\\", "/").strip()


def _validate_plain(plain_zh: str, name_zh: str) -> tuple[bool, str]:
    """写入前校验 plain_zh 合规性（治本：拒模板化简介）。

    Returns:
        (ok, reason)——ok=True 合规；ok=False 时 reason 说明不合规原因。
    """
    if not plain_zh or not plain_zh.strip():
        return False, "plain_zh 为空"
    if _cjk_len(plain_zh) < _MIN_CJK:
        return False, f"plain_zh CJK 字符数 {_cjk_len(plain_zh)} < {_MIN_CJK}（信息量不足）"
    if is_generic_plain_zh(plain_zh):
        return False, "plain_zh 是多模块共用的通用模板（is_generic_plain_zh 命中），需写模块特异简介"
    if name_zh and is_generic_plain_suffix(plain_zh, name_zh):
        return False, "plain_zh 剥离 name_zh 前缀后的后缀是通用模板（is_generic_plain_suffix 命中），需写模块特异简介"
    return True, ""


# ============================================================================
# responsibility_layer 派生（裁定#335 结论⑥，战役 st-vocabconsol-20260918 W4b）
# ============================================================================
# 唯一推导通道 = domain_responsibility_layer_mapping.yaml（经 yaml_utils SSoT 加载器）。
# 禁从 layer_id / 目录名 / 模块路径直推（争点 C1 运行时栈≠职责层、C17 目录≠域≠层）。


def _read_layer_map() -> dict[str, str]:
    """读域→responsibility_layer 映射真源（strict=True：误拼/损坏 fail-fast，勿静默丢层）。"""
    return load_responsibility_layer_map(RESPONSIBILITY_LAYER_MAP_YAML)


def _layer_for_domain(domain: str, layer_map: dict[str, str]) -> str | None:
    """按 domain_id 查映射取层；查不到返回 None（无退化路径——直推即违规）。"""
    return layer_map.get((domain or "").strip())


def _fill_responsibility_layer(entry: dict, layer_map: dict[str, str] | None) -> dict:
    """按 ``domain_id`` 自动填 ``responsibility_layer``（不改调用方传入的 dict）。

    三种姿态（裁定#335 结论⑥）：
      - 映射命中 → 写真源值；调用方塞了不一致的值 → stderr WARNING 后以真源为准
      - 映射可用但缺该域 → stderr WARNING + 该字段留空（不阻断翻译写入）
      - 映射真源不可用（``layer_map=None``，上游已告警）→ 静默留空，不重复刷屏

    留空 = 移除键而非写空串：扩展字段缺失即"未派生"，写空串会被 ``--sync-layer``
    与消费侧误读成"已派生为空层"。
    """
    new_entry = dict(entry)
    domain = str(new_entry.get("domain_id") or "").strip()
    layer = None if layer_map is None else _layer_for_domain(domain, layer_map)
    if layer:
        prior = str(new_entry.get(_LAYER_KEY) or "").strip()
        if prior and prior != layer:
            print(
                f"[add_module_translation] WARNING: 传入 {_LAYER_KEY}={prior!r} 与映射真源"
                f"（{domain}→{layer!r}）不一致，已以真源为准",
                file=sys.stderr,
            )
        new_entry[_LAYER_KEY] = layer
        return new_entry
    if layer_map is not None and domain:
        print(
            f"[add_module_translation] WARNING: 映射真源缺域 {domain}，{_LAYER_KEY} 留空"
            "（不阻断写入；补映射后跑 --sync-layer 收敛）",
            file=sys.stderr,
        )
    new_entry.pop(_LAYER_KEY, None)
    return new_entry


# 规范 7 字段（写手输出的固定键序）；其余键 = 未知扩展字段，重写时必须保留
_CANONICAL_KEYS: tuple[str, ...] = (
    "module_path",
    "domain_id",
    "name_zh",
    "name_en",
    "desc_zh",
    "desc_en",
    "plain_zh",
)

# 标识符形态字段：安全字符集值裸写（匹配存量条目字节风格，如 MOD-PG_PROBE / dormant / D_DATA）
# responsibility_layer 入列理由：--sync-layer 的行级外科编辑同样写裸值，两条通道必须
# 同一字面风格，否则每次 upsert 都会把同步落好的行翻成带引号形态（无意义 diff 抖动）。
_BARE_KEYS = frozenset({"domain_id", "module_id", "build_status", "domain", _LAYER_KEY})
_BARE_VALUE_RE = re.compile(r"[A-Za-z0-9_][A-Za-z0-9_.\-]*")


def _is_empty_value(v: object) -> bool:
    """字段值是否"无信息"（None/空串/纯空白）——去重合并时判定谁填充。"""
    if v is None:
        return True
    if isinstance(v, str):
        return not v.strip()
    return False


def _entry_info_score(entry: dict) -> int:
    """条目信息量分数 = 非空字段数（重复条目仲裁：信息最全者胜出）。"""
    return sum(1 for v in entry.values() if not _is_empty_value(v))


def _format_scalar_value(key: str, value: object) -> str:
    """单字段值序列化：标识符字段安全值裸写；文本字段强制双引号转义；
    None→null、数字/布尔原样——保证扩展字段 round-trip（safe_load 读回同值）。"""
    if value is None:
        return "null"
    if isinstance(value, str):
        if key in _BARE_KEYS and _BARE_VALUE_RE.fullmatch(value):
            return value
        return _yaml_quote(value)
    return str(value)


def _block_module_path(block: str) -> str | None:
    """从 entries 列表块文本提取归一化 module_path（首行 `- module_path:`），无则 None。"""
    m = re.match(r"- module_path:\s*(\S+)", block)
    return _normalize_path(m.group(1)) if m else None


def _parse_block_entry(block: str) -> dict | None:
    """把 entries 列表的一个块文本解析为 dict（独立文档安全：块即单元素序列）。
    解析失败/形态异常返回 None，调用方保守处理（不动该块）。"""
    try:
        loaded = yaml.safe_load(block)
    except Exception:  # noqa: BLE001 — 单块解析失败走保守路径
        return None
    if isinstance(loaded, list) and len(loaded) == 1 and isinstance(loaded[0], dict):
        return loaded[0]
    return None


def _format_entry_block(entry: dict) -> str:
    """格式化一条 entry 为 YAML 块字符串（2 空格缩进，与现有条目风格一致）。

    规范 7 字段按固定顺序先出（module_path 归一化不转义；5 个文本字段强制
    双引号转义；domain_id 等标识符字段安全值裸写）；其余未知扩展字段
    （module_id/build_status/domain 及未来新增字段）按原键序跟随输出——
    治本（裁定#335 结论7）：旧版固定 7 行输出即"字段吞噬器"，整块重写会
    抹掉条目上的扩展字段，破坏 schema 演进的 round-trip 安全。
    """
    lines = [f"- module_path: {_normalize_path(entry['module_path'])}"]
    for k in _CANONICAL_KEYS[1:]:
        lines.append(f"  {k}: {_format_scalar_value(k, entry.get(k, ''))}")
    for k, v in entry.items():
        if k not in _CANONICAL_KEYS:
            lines.append(f"  {k}: {_format_scalar_value(k, v)}")
    return "\n".join(lines)


def _split_entries_section(yaml_text: str) -> tuple[str, str, str]:
    """把 YAML 文本切成 (前导, entries 列表区, 后续段落) 三段。

    真源 YAML 结构：顶层含 ``entries:`` 列表，其后还有 ``battle_map_steps:`` /
    ``battle_map_cross_cutting:`` 等同顶层段落。新增条目 MUST 落在 entries 列表区内，
    追加到文件末尾会脱离 entries 作用域导致 YAML 解析失败（治本：2026-08-02 首版
    误追加到文件尾损坏真源，git checkout 回滚后改为段落感知切分）。

    Returns:
        ``(preamble, entries_body, tail)``——preamble 含 ``entries:`` 行及之前所有内容；
        entries_body 为列表项文本（不含 ``entries:`` 行，不含尾随段落）；tail 为
        ``battle_map_steps:`` 及之后所有内容。无 entries 段时 entries_body 为空、
        tail 为空。
    """
    lines = yaml_text.split("\n")
    # 定位 entries: 行（列 0 顶层键）
    entries_idx = None
    for i, ln in enumerate(lines):
        if ln.startswith("entries:") and ln.rstrip() == "entries:":
            entries_idx = i
            break
    if entries_idx is None:
        # 无 entries 段——整体当 preamble，无法 upsert（调用方会报错）
        return yaml_text, "", ""

    # 定位 entries 之后的下一个顶层键（列 0 的 `word:` 形式，非列表项 `-`/缩进）
    next_section_idx = None
    for j in range(entries_idx + 1, len(lines)):
        ln = lines[j]
        if ln and not ln[0].isspace() and not ln.startswith("-") and not ln.startswith("#"):
            # 顶层键：形如 `battle_map_steps:` ——冒号在前半段
            if re.match(r"^[A-Za-z_][A-Za-z0-9_]*:", ln):
                next_section_idx = j
                break

    if next_section_idx is None:
        # entries 是最后一个段落
        preamble = "\n".join(lines[: entries_idx + 1])
        entries_body = "\n".join(lines[entries_idx + 1 :])
        return preamble, entries_body, ""

    preamble = "\n".join(lines[: entries_idx + 1])
    entries_body = "\n".join(lines[entries_idx + 1 : next_section_idx])
    tail = "\n".join(lines[next_section_idx:])
    return preamble, entries_body, tail


def _entries_body_regions(entries_body: str) -> list[tuple[int, int]]:
    """返回 entries 列表区内各 `- module_path:` 块的 [start, end) 区间（body 内相对偏移）。

    块边界=列 0 的列表项起始行；区域含块后的分隔换行/空行，保证外科手术式
    替换时未触碰字节原样保留（对标 algo_flow_translation_sync 的"段级文本
    替换保人工段字节，禁整文件重序列化"套路）。
    """
    starts = [m.start() for m in re.finditer(r"(?m)^- module_path:", entries_body)]
    return [(s, starts[i + 1] if i + 1 < len(starts) else len(entries_body)) for i, s in enumerate(starts)]


def _apply_body_edits(entries_body: str, edits: list[tuple[int, int, str]]) -> str:
    """对 entries 列表区应用 [(start, end, replacement)] 区间编辑（未覆盖区字节不动）。"""
    parts: list[str] = []
    pos = 0
    for s, e, repl in sorted(edits):
        if s < pos:
            raise ValueError("entries 区块编辑区间重叠")
        parts.append(entries_body[pos:s])
        parts.append(repl)
        pos = e
    parts.append(entries_body[pos:])
    return "".join(parts)


def _join_sections(preamble: str, entries_body: str, tail: str) -> str:
    """三段重组：preamble + entries 列表区 + 后续段落（与 _split_entries_section 严格互逆）。"""
    text = preamble + "\n" + entries_body
    if tail:
        text += "\n" + tail
    if not text.endswith("\n"):
        text += "\n"
    return text


def _upsert_entry(yaml_text: str, entry: dict) -> tuple[str, bool]:
    """按 module_path 唯一键 upsert 一条 entry，返回 (新文本, 是否新增)。

    段落感知（治本）：只在 ``entries:`` 列表区内做区间级编辑，其余字节不动。
    命中（可能多块）→ 首个命中块替换为新块，其余同路径重复块删除（自愈），
    并把所有命中块上的未知扩展字段合并进新条目（信息不丢）；未命中→插到
    entries 列表末尾（下一个顶层段落之前），绝不追加到文件尾。
    治本（裁定#335 结论7）：旧版只替换首个命中块→存量重复无法靠本工具收敛。
    """
    norm_path = _normalize_path(entry["module_path"])
    preamble, entries_body, tail = _split_entries_section(yaml_text)
    if _has_no_entries_section(yaml_text, preamble):
        raise ValueError("YAML 中未找到 `entries:` 顶层段，无法 upsert")

    regions = _entries_body_regions(entries_body)
    matches = [(s, e) for s, e in regions if _block_module_path(entries_body[s:e]) == norm_path]

    if matches:
        new_entry = dict(entry)
        # 旧块先按 --dedupe 的同一份仲裁语义合成一份"在册最优视图"（不另发明第二套合并）。
        old_parsed = [p for p in (_parse_block_entry(entries_body[s:e]) or {} for s, e in matches) if p]
        old_merged = _merge_duplicate_blocks(old_parsed) if old_parsed else {}
        # 合并范围＝**全部字段（含规范 7 字段）**，非空优先、调用方给值不覆盖。
        # 治本（2026-09-27 字段级蒸发）：旧版在此处 `continue` 掉 _CANONICAL_KEYS，
        # 而 _format_entry_block 对规范字段用 entry.get(k, '')，于是"只改大白话句"的
        # 常规重登记会把在册 name_en/desc_zh/desc_en 静默清空成 ""（已复现，见案卷）。
        # 仍不继承的两类：_DERIVED_KEYS（只认 --sync-layer 重算，继承会让"映射已删域"
        # 的陈旧层值复活，破坏收敛语义）与 module_path（身份键，取调用方归一值）。
        for k, v in old_merged.items():
            if k in _DERIVED_KEYS or k == "module_path":
                continue
            if _is_empty_value(new_entry.get(k)) and not _is_empty_value(v):
                new_entry[k] = v
        new_block = _format_entry_block(new_entry)
        edits: list[tuple[int, int, str]] = []
        for rank, (s, e) in enumerate(matches):
            if rank == 0:
                orig = entries_body[s:e]
                trail = orig[len(orig.rstrip("\n")) :] or "\n"  # 保留原块后的分隔空白
                edits.append((s, e, new_block + trail))
            else:
                edits.append((s, e, ""))  # 重复块整体删除（含分隔换行）
        new_body = _apply_body_edits(entries_body, edits)
        return _join_sections(preamble, new_body, tail), False  # 更新（含自愈去重）

    # 未命中 → 追加到 entries 列表末尾（tail 段落之前）。分隔规则：body 以 \n 结尾
    # （真实条目行后还有空行分隔下一顶层段）时，新块自带尾 \n，重组的 "\n"+tail
    # 仍产出空行；body 无尾 \n 时新块不加尾 \n，由重组补行尾——两种形态均零附带漂移。
    addition = _format_entry_block(entry)
    if entries_body.endswith("\n"):
        new_body = entries_body + addition + "\n"
    else:
        new_body = (entries_body + "\n" if entries_body else "") + addition
    return _join_sections(preamble, new_body, tail), True  # 新增


def _has_no_entries_section(yaml_text: str, preamble: str) -> bool:
    """_split_entries_section 无 entries 段时把整文当 preamble——据此判定段缺失。"""
    return preamble == yaml_text and not preamble.rstrip("\n").endswith("entries:")


def _invalidate_loader_cache() -> None:
    """写入后失效 module_translation_loader 缓存，使同进程后续读取看到新条目。

    loader 用模块级 _PATH_CACHE 缓存；CLI 一次性进程不严格需要，但批量场景
    /测试场景下避免脏读。fail-open：失效失败不阻断（只是缓存陈旧，下次进程自然刷新）。
    """
    try:
        import _shared.module_translation_loader as mtl  # noqa: WPS433

        mtl._PATH_CACHE = None
        mtl._GENERIC_PLAIN_CACHE = None
        mtl._GENERIC_DESC_CACHE = None
        mtl._GENERIC_SUFFIX_CACHE = None
    except Exception:  # noqa: BLE001 — 缓存失效失败不阻断写入
        pass


def _write_registry(new_text: str, base_text: str) -> None:
    """热文件 CAS 写入（AGENTS 硬规则 13 / 裁定#335 结论7）。

    ``module_translation_registry.yaml`` 是 ``DEFAULT_HOT_FILES`` 成员，禁裸
    write_text——走 ``safe_write_text``：以调用方读到的原文（base_text）算
    expected_base_sha256，磁盘已被他会话推进时 StaleWriteRefused 拒写不落盘
    （治本陈旧快照覆写通道，疑即 2026-08-23 curated 重复带的成因）；
    ``newline="\\n"`` 保 .gitattributes eol=lf 钉定的 LF 字节级行尾约定
    （旧裸写经 Windows 文本模式把全文件翻成 CRLF，即"写手翻转行尾"污染）。

    Raises:
        StaleWriteRefused / WriteVerificationError / OSError（由调用方映射 exit 2）。
    """
    from zephyr.shared.io.file_utils import content_sha256, safe_write_text  # noqa: PLC0415

    safe_write_text(
        REGISTRY_YAML,
        new_text,
        expected_base_sha256=content_sha256(base_text),
        repo_root=REPO_ROOT,
        newline="\n",
    )


def _validate_and_derive(entry: dict) -> tuple[int | None, str, dict, dict | None]:
    """必填字段 + 大白话合规校验 + responsibility_layer 派生（账本/逃生旗两条通道共用前置）。

    Returns:
        ``(err_code, message, entry_with_layer, layer_map)``——``err_code`` 非 None 时调用方
        MUST 直接返回该码；``layer_map is None`` 表示映射真源本身不可用（已 stderr WARNING），
        账本通道据此**不派生也不删除** ``_LAYER_KEY``（在册值原样——瞬时故障不该改写真源）。
    """
    required = ["module_path", "domain_id", "name_zh", "plain_zh"]
    missing = [f for f in required if not (entry.get(f) or "").strip()]
    if missing:
        return EXIT_VALIDATION, f"必填字段缺失: {missing}", entry, None

    ok, reason = _validate_plain(entry["plain_zh"], entry["name_zh"])
    if not ok:
        return EXIT_VALIDATION, f"plain_zh 校验失败: {reason}", entry, None

    # 层派生（裁定#335 结论⑥）：唯一通道=域→层映射真源；真源不可用只降级"不填"。
    try:
        layer_map: dict[str, str] | None = _read_layer_map()
    except Exception as e:  # noqa: BLE001 — 层真源故障不阻断翻译登记
        print(
            f"[add_module_translation] WARNING: {_LAYER_KEY} 映射真源不可用（{type(e).__name__}: {e}），本次不派生该字段",
            file=sys.stderr,
        )
        layer_map = None
    return None, "", _fill_responsibility_layer(entry, layer_map), layer_map


def _add_translation_via_disk_projection(entry: dict, *, dry_run: bool = False) -> tuple[int, str]:
    """旧直写腿（写盘上投影 YAML）——仅供 --legacy-disk-write 逃生旗与整表手术复用。

    病（2026-10-11 定案）：投影册已被投影器接管，直写条目没入账本 → 下一次 render 按
    PG-wins 把它整块修剪掉（实录：scripts/backup/backup_reconciler_shadow.py 在 v17 快照
    缺该行，00:52/00:53 两次 render 剪除）。**登记正路是 ``register_via_ledger``**，
    本函数只在显式逃生旗或 --dedupe/--sync-layer 整表手术下被调用。

    流程不变（合规校验 + 派生 + 段落感知 upsert（含重复自愈）+ CAS 写盘 + 解析校验）。
    """
    # 1-2. 必填/合规校验 + 层派生
    err_code, msg, entry, _layer_map = _validate_and_derive(entry)
    if err_code is not None:
        return err_code, msg

    # 3. 读取真源（base_text 兼作 CAS 基线）
    try:
        yaml_text = REGISTRY_YAML.read_text(encoding="utf-8")
    except Exception as e:  # noqa: BLE001
        return EXIT_IO, f"读取翻译真源失败: {type(e).__name__}: {e}"

    # 4. upsert
    try:
        new_text, is_new = _upsert_entry(yaml_text, entry)
    except ValueError as e:
        return EXIT_IO, str(e)

    if dry_run:
        action = "新增" if is_new else "更新"
        return EXIT_SUCCESS, f"[dry-run] {action} {entry['module_path']} 校验通过"

    # 5. CAS 写盘（热文件禁裸写；base 陈旧=他会话已推进→拒写，不部分落盘）
    try:
        _write_registry(new_text, yaml_text)
    except Exception as e:  # noqa: BLE001 — 含 StaleWriteRefused/WriteVerificationError
        return EXIT_IO, f"写入翻译真源失败（CAS/IO）: {type(e).__name__}: {e}"

    # 6. 写后 YAML 解析校验（防写入损坏真源；且验证唯一性——重复条目不得通过）
    try:
        data = yaml.safe_load(REGISTRY_YAML.read_text(encoding="utf-8"))
        entries = (data or {}).get("entries", []) or []
        norm_path = _normalize_path(entry["module_path"])
        hits = sum(1 for e in entries if isinstance(e, dict) and _normalize_path(e.get("module_path", "")) == norm_path)
        if hits == 0:
            return EXIT_IO, f"写后校验失败：entries 中未找到 {norm_path}"
        if hits > 1:
            return EXIT_IO, f"写后校验失败：{norm_path} 存在 {hits} 条重复（唯一键自愈未生效）"
    except Exception as e:  # noqa: BLE001
        return EXIT_IO, f"写后 YAML 解析失败（真源可能损坏）: {type(e).__name__}: {e}"

    # 7. 失效 loader 缓存
    _invalidate_loader_cache()

    action = "新增" if is_new else "更新"
    return (
        EXIT_SUCCESS,
        f"{action} 翻译条目（投影面直写，账本未记）: {entry['module_path']}（entries 共 {len(entries)} 条）",
    )


# ============================================================================
# 意图 API 薄壳通道（裁定#502 同款）：register/update → publish_snapshot → render
# ----------------------------------------------------------------------------
# 三条腿各有一个模块级包装，既让生产代码零散 SQL/零全局状态，也给测试留注入点。
# ============================================================================


def _declared_fields(entry: dict) -> dict[str, object]:
    """本次调用**真正声明**的键值（module_path 恒置首=身份键；空值=未声明）。

    治本（2026-09-27 字段级蒸发 + 已裁教训"整条覆盖他人字段"）：调用方没给值的键
    （空串/None）不进声明集，于是既不会被写空、也不会从在册 payload 消失。
    """
    declared: dict[str, object] = {"module_path": _normalize_path(str(entry.get("module_path") or ""))}
    for k, v in entry.items():
        if k == "module_path" or _is_empty_value(v):
            continue
        declared[k] = v
    return declared


def _merge_payload(existing: dict | None, declared: dict, named_removals: set[str]) -> dict:
    """键集合差分合成新 payload：在册键原样保留，本次声明的键覆盖，仅点名删除的键移除。

    身份键 ``module_path`` 恒置首且**永不可删**（PG jsonb 按（键长,字节序）重排，
    api.update 会用 ``entry_composite_key`` 复核身份，首字段不稳=身份漂移被拒）。
    点名删除在最后执行：显式 ``--clear-field`` 的意图高于同键的声明值。
    """
    merged: dict[str, object] = {"module_path": declared["module_path"]}
    for k, v in (existing or {}).items():
        if k == "module_path":
            continue
        merged[k] = v
    for k, v in declared.items():
        if k != "module_path":
            merged[k] = v
    for k in named_removals:
        if k != "module_path":
            merged.pop(k, None)
    return merged


def _unauthorized_removals(existing: dict | None, merged: dict, named_removals: set[str]) -> set[str]:
    """删除集守卫：从在册 payload 消失的键必须逐条点名（越界删除=拒写，fail-closed）。"""
    removed = {k for k in (existing or {}) if k not in merged}
    removed.discard("module_path")
    return removed - named_removals


def _payload_delta_keys(existing: dict | None, merged: dict) -> tuple[list[str], list[str]]:
    """(变化键, 删除键)——dry-run 与幂等判定共用（无变化即账本已到位）。"""
    changed = sorted(k for k in merged if (existing or {}).get(k) != merged[k])
    removed = sorted(k for k in (existing or {}) if k not in merged)
    return changed, removed


def _ledger_rows(module_path: str) -> list[dict]:
    """账本只读点查该 module_path 的全部条目行（entry_key/payload/version/status）。

    按 ``payload->>'module_path'`` 查而非按拼装的 entry_key 查——存量有 613 行身份键
    漂到 ``desc_en=...``（jsonb 键序历史病），只认拼出来的键会漏判"已存在"进而插重复行，
    render 自校验随即以"声明族身份坍缩"拒写（把病推给下一个受害者）。
    """
    from zephyr.infrastructure.database_service import DatabaseService  # noqa: PLC0415

    conn = DatabaseService().get_depgraph_conn(read_only=True)
    try:
        with conn.cursor() as cur:
            cur.execute(
                SQL_TRANSLATION_ROW_BY_MODULE_PATH,
                (REGISTRY_ID, FAMILY_KEY, _normalize_path(module_path)),
            )
            rows = cur.fetchall()
    finally:
        conn.close()
    out: list[dict] = []
    for row in rows:
        item = dict(row)
        payload = item.get("payload")
        if isinstance(payload, str):
            payload = json.loads(payload)
        item["payload"] = payload or {}
        out.append(item)
    return out


def _ledger_register(payload: dict, *, reason: str, session_id: str) -> object:
    """意图 API 登记新行（同键同指纹=OK_NOOP，同键异指纹=CONFLICT_DUPLICATE）。"""
    from zephyr.governance.registry_ledger import api  # noqa: PLC0415

    return api.register(REGISTRY_ID, FAMILY_KEY, payload, reason=reason, session_id=session_id, actor_kind="agent")


def _ledger_update(entry_key: str, expected_version: int, payload: dict, *, reason: str, session_id: str) -> object:
    """意图 API CAS 更新在册行（expected_version 不匹配=CONFLICT_VERSION，由调用方重读重试）。"""
    from zephyr.governance.registry_ledger import api  # noqa: PLC0415

    return api.update(
        REGISTRY_ID, FAMILY_KEY, entry_key, expected_version, payload, reason=reason, session_id=session_id
    )


def _publish_and_render(session_id: str) -> tuple[int | None, str]:
    """发布快照（禁裸发布：MUST 带 repo_root）+ 重打本册投影（唯一合法写者=生成器）。"""
    from zephyr.governance.registry_ledger.baseline import publish_snapshot  # noqa: PLC0415
    from zephyr.governance.registry_projection.projection_generator import run as projection_run  # noqa: PLC0415

    try:
        published = publish_snapshot(REGISTRY_ID, repo_root=PROJECTION_ROOT, session_id=session_id)
    except Exception as e:  # noqa: BLE001 — 发布失败=落地未证实，绝不降级直写
        return EXIT_IO, f"快照发布失败: {type(e).__name__}: {e}"
    report = projection_run(
        PROJECTION_ROOT,
        mode="render",
        registry_id=REGISTRY_ID,
        physical_path=REGISTRY_REL,
        actor_session=session_id,
    )
    if not report.ok and report.quadrant not in ("clean", "armed_initial"):
        return EXIT_IO, (f"投影重打未过（quadrant={report.quadrant}）: {report.detail}；证据={report.evidence_path}")
    return None, (
        f"publish v{published.get('snapshot_version')}(noop={published.get('noop')}) "
        f"render quadrant={report.quadrant} wrote={report.wrote}"
    )


def _projection_entry(module_path: str) -> dict | None:
    """只读：从盘上投影册取该 module_path 的 entries 条目（未命中=None）。

    段落感知区间扫描（不整册 safe_load，68k 行册子秒级返回），字节级复用旧直写腿的
    解析器——读侧用途，无任何写盘动作。
    """
    norm_path = _normalize_path(module_path)
    try:
        text = REGISTRY_YAML.read_text(encoding="utf-8")
    except Exception:  # noqa: BLE001 — 投影面不可读由调用方核验分支报红
        return None
    _preamble, entries_body, _tail = _split_entries_section(text)
    for s, e in _entries_body_regions(entries_body):
        if _block_module_path(entries_body[s:e]) == norm_path:
            parsed = _parse_block_entry(entries_body[s:e])
            if parsed is not None:
                return parsed
    return None


def _verify_landing(module_path: str, declared: dict) -> tuple[bool, str]:
    """三方核验落地：PG 有该行且值已到位 ∧ 盘上投影面 grep 命中同一 module_path。

    第三面（``git show dev:``）不在此要求——入账本与落地是两件事（落地归提交队列/总包）。
    """
    try:
        rows = [r for r in _ledger_rows(module_path) if r.get("status") == "active"]
    except Exception as e:  # noqa: BLE001
        return False, f"账本复核不可达（{type(e).__name__}: {e}）——登记结果未证实"
    if not rows:
        return False, "PG 账本无该 module_path 的 active 行"
    payload = rows[0]["payload"]
    mismatched = sorted(k for k in declared if str(payload.get(k, "")) != str(declared[k]))
    proj = _projection_entry(module_path)
    if proj is None:
        return False, f"盘上投影册未出现该条目（PG 有、投影面无）：{payload.get('module_path')}"
    proj_mismatched = sorted(k for k in declared if str(proj.get(k, "")) != str(declared[k]))
    if mismatched or proj_mismatched:
        return False, (f"落地值与登记值不一致 PG={mismatched} 投影={proj_mismatched}")
    return True, f"PG active 行 version={rows[0].get('version')} + 投影面命中（共 {len(rows)} 行）"


def register_via_ledger(
    entry: dict,
    *,
    session_id: str = "",
    dry_run: bool = False,
    clear_fields: tuple[str, ...] = (),
) -> tuple[int, str]:
    """登记正路：校验 → 账本 register/update（键集合差分幂等）→ publish → render → 三方核验。

    幂等与"不清他人字段"的机械保证：
      - 声明集=本次真正给了值的键（空值不入声明集）→ 未声明键从在册 payload 原样带过；
      - 删除集=``--clear-field`` 点名 + ``responsibility_layer`` 重算（映射真源不可用时
        连点名删除都不做）；未点名的键若从 payload 消失 → 拒写（fail-closed）。
    PG 不可达=登记失败 exit 2，**绝不降级直写投影**（直写=重新接通死路）。
    """
    err_code, msg, entry, layer_map = _validate_and_derive(entry)
    if err_code is not None:
        return err_code, msg

    sid = (session_id or DEFAULT_SESSION).strip() or DEFAULT_SESSION
    norm_path = _normalize_path(entry["module_path"])
    declared = _declared_fields(entry)
    named_removals = {f.strip() for f in clear_fields if f and f.strip()}
    if _LAYER_KEY not in declared and layer_map is not None:
        # 映射可用而该域查不到 → 在册派生值随真源收敛（裁定#335 结论⑥"永不继承"）；
        # 映射真源不可用（layer_map=None）→ 不派生也不删除，在册值原样。
        named_removals.add(_LAYER_KEY)

    try:
        rows = _ledger_rows(norm_path)
    except Exception as e:  # noqa: BLE001 — 账本不可达 fail-closed，不降级直写
        return EXIT_IO, (
            f"账本不可达，登记失败（绝不降级直写投影）: {type(e).__name__}: {e}；"
            f"应急直写需显式 --legacy-disk-write（后果：下次 render 修剪）"
        )
    actives = [r for r in rows if r.get("status") == "active"]
    if len(actives) > 1:
        return EXIT_VALIDATION, (
            f"账本该 module_path 有 {len(actives)} 条 active 行（身份漂移，回灌/清理班处置）："
            f"{[r.get('entry_key') for r in actives][:3]}——本次不登记，防再插一条同键副本"
        )
    existing = actives[0]["payload"] if actives else None
    merged = _merge_payload(existing, declared, named_removals)
    illegal = _unauthorized_removals(existing, merged, named_removals)
    if illegal:
        return EXIT_VALIDATION, f"删除集越界（未点名即不得删除）: {sorted(illegal)}——拒写"
    changed, removed = _payload_delta_keys(existing, merged)
    reason = f"模块大白话简介经意图 API 登记 {REGISTRY_ID}/{FAMILY_KEY}（薄壳通道=裁定#502 同款）"

    if dry_run:
        action = (
            "register（新增行）"
            if not actives
            else ("update（改动键）" if (changed or removed) else "noop（账本已到位）")
        )
        return EXIT_SUCCESS, (
            f"[dry-run] {norm_path} → {action}；声明键 {sorted(declared)} / 变化键 {changed} / "
            f"点名删除 {removed} / 在册其余键原样 {sorted(set(existing or {}) - set(changed) - set(removed))}"
        )

    if not actives:
        res = _ledger_register(merged, reason=reason, session_id=sid)
        if res.code == _CODE_CONFLICT_DUPLICATE:  # 同键异指纹（并发他人已登记）→ 重读走 update 差分
            try:
                rows = _ledger_rows(norm_path)
            except Exception as e:  # noqa: BLE001
                return EXIT_IO, f"冲突后账本复核不可达（{type(e).__name__}: {e}）——登记结果未证实"
            actives = [r for r in rows if r.get("status") == "active"]
            if not actives:
                return EXIT_VALIDATION, f"账本冲突且无可更新行: {res.code} {res.detail}"
            existing = actives[0]["payload"]
            merged = _merge_payload(existing, declared, named_removals)
            res = _ledger_update(
                actives[0]["entry_key"], int(actives[0]["version"]), merged, reason=reason, session_id=sid
            )
    elif not changed and not removed:
        res = None  # 幂等：账本已到位，仍继续 publish+render（投影面落后于账本时由此自愈）
    else:
        res = None
        for _attempt in range(3):
            target = actives[0]
            res = _ledger_update(target["entry_key"], int(target["version"]), merged, reason=reason, session_id=sid)
            if res.code == _CODE_CONFLICT_VERSION:  # 他人已推进 CAS 版本 → 重读再差分
                try:
                    rows = _ledger_rows(norm_path)
                except Exception as e:  # noqa: BLE001
                    return EXIT_IO, f"CAS 冲突后账本复核不可达（{type(e).__name__}: {e}）——登记结果未证实"
                actives = [r for r in rows if r.get("status") == "active"]
                if not actives:
                    return EXIT_VALIDATION, f"账本行消失，无法更新: {res.detail}"
                existing = actives[0]["payload"]
                merged = _merge_payload(existing, declared, named_removals)
                illegal = _unauthorized_removals(existing, merged, named_removals)
                if illegal:
                    return EXIT_VALIDATION, f"重试后删除集越界（未点名即不得删除）: {sorted(illegal)}——拒写"
                changed, removed = _payload_delta_keys(existing, merged)
                if not changed and not removed:
                    res = None  # 已收敛到目标态
                    break
                continue
            break
    if res is not None and res.code not in (_CODE_OK, _CODE_NOOP):
        return EXIT_VALIDATION, f"账本写入失败: {res.code} {res.detail}"

    pub_code, pub_msg = _publish_and_render(sid)
    if pub_code is not None:
        return pub_code, pub_msg

    ok, detail = _verify_landing(norm_path, {k: v for k, v in declared.items() if k not in named_removals})
    wrote = "noop（账本已到位）" if res is None else f"{res.code}"
    if not ok:
        return EXIT_IO, f"三方核验未过 {norm_path}: {detail}；通道腿={pub_msg}"
    return EXIT_SUCCESS, (
        f"账本登记 {wrote}: {norm_path}（会话={sid}，声明键 {sorted(declared)}，改动键 {changed or '无'}，"
        f"点名删除 {removed or '无'}）；{pub_msg}；落地核验={detail}"
    )


def add_translation(
    entry: dict,
    *,
    dry_run: bool = False,
    session_id: str = "",
    legacy_disk_write: bool = False,
    clear_fields: tuple[str, ...] = (),
) -> tuple[int, str]:
    """主入口（兼容面）：缺省=意图 API 账本通道；显式 ``legacy_disk_write`` 才走旧直写腿。

    签名向后兼容 ``scripts/governance/dead_letter_doctor.py:702``（位置 entry + dry_run）。
    直写腿会打红色警告并落一行 JSONL 审计留痕（条目不进账本 ⇒ 下次 render 修剪）。
    """
    if legacy_disk_write:
        _warn_legacy_disk_write(entry.get("module_path", ""))
        _record_legacy_disk_write(entry.get("module_path", ""), session_id or DEFAULT_SESSION, dry_run=dry_run)
        return _add_translation_via_disk_projection(entry, dry_run=dry_run)
    return register_via_ledger(entry, session_id=session_id, dry_run=dry_run, clear_fields=clear_fields)


def _warn_legacy_disk_write(module_path: str) -> None:
    """逃生旗红色警告（stderr，ANSI 31）：直写条目不进账本，会被下次 render 修剪。"""
    print(
        "\033[31m[add_module_translation][LEGACY-DISK-WRITE 红色警告] "
        f"{module_path} 正在直写投影册 module_translation_registry.yaml——该条目不会进入 "
        f"PG 账本（{REGISTRY_ID}），下一次 render（PG-wins）会把它当非账本内容修剪掉，"
        "TRANSLATION-COVERAGE 随即复现缺失。正路=去掉 --legacy-disk-write 走账本通道"
        "（register→publish→render）。已落审计留痕。\033[0m",
        file=sys.stderr,
    )


def _record_legacy_disk_write(module_path: str, session_id: str, *, dry_run: bool) -> None:
    """逃生旗审计留痕（fail-open：留痕失败不阻断，但醒目报出）。"""
    try:
        from zephyr.shared.utils.time_utils import now_utc  # noqa: PLC0415

        path = LEGACY_DISK_WRITE_AUDIT_PATH
        path.parent.mkdir(parents=True, exist_ok=True)
        line = json.dumps(
            {
                "ts": now_utc().isoformat(),
                "actor_session": session_id,
                "module_path": _normalize_path(module_path),
                "dry_run": bool(dry_run),
                "channel": "legacy_disk_write",
                "note": "直写投影不进账本，下次 render 修剪（裁定#502 同款退役轨）",
            },
            ensure_ascii=False,
        )
        with path.open("a", encoding="utf-8", newline="\n") as fh:
            fh.write(line + "\n")
    except Exception as e:  # noqa: BLE001 — 留痕故障醒目但不断链
        print(f"[add_module_translation] WARNING: 逃生旗审计留痕失败（{type(e).__name__}: {e}）", file=sys.stderr)


# ============================================================================
# 回填扫描（D 项，只读零写）：投影面有而最新快照无 = shadow 事故的机判形态
# ============================================================================


def _latest_snapshot(registry_id: str, physical_path: str, snapshot_file: str | None):
    """最新已发布快照（PG registry_snapshot 最新版；``snapshot_file`` 走 JSON 影子通道）。"""
    if snapshot_file:
        from zephyr.governance.registry_projection.pg_source import snapshot_from_json_file  # noqa: PLC0415

        return snapshot_from_json_file(snapshot_file)
    from zephyr.governance.registry_projection.pg_source import load_latest_snapshot  # noqa: PLC0415

    return load_latest_snapshot(registry_id, physical_path)


def audit_projection_vs_ledger(
    *,
    registry_id: str = REGISTRY_ID,
    physical_path: str = REGISTRY_REL,
    repo_root: Path | None = None,
    snapshot_file: str | None = None,
) -> tuple[int, str]:
    """只读回填扫描：报"投影面有而最新快照无"的条目（会被下次 render 修剪的存量）。

    族集合与身份键口径与生成器完全同源（``projection_generator._entry_index``：册声明
    身份字段优先，无声明退 (file,token) legacy/首标量）——本函数不另发明一套身份判据。
    零写：不碰盘、不碰账本、不发快照（PG 侧只 ``load_latest_snapshot`` 读面）。

    Returns:
        ``(exit_code, message)``——命中 > 0 → exit 1（"投影面有而快照无"就是校验失败本体），
        命中 = 0 → exit 0；快照/投影不可取 → exit 2。
    """
    from zephyr.governance.registry_projection.model import snapshot_from_yaml  # noqa: PLC0415
    from zephyr.governance.registry_projection.projection_generator import _entry_index  # noqa: PLC0415

    root = Path(repo_root or PROJECTION_ROOT)
    target = root / physical_path
    try:
        disk_text = target.read_text(encoding="utf-8")
    except Exception as e:  # noqa: BLE001
        return EXIT_IO, f"读取投影册失败: {type(e).__name__}: {e}"
    try:
        disk_snap = snapshot_from_yaml(disk_text, registry_id=registry_id, physical_path=physical_path)
    except Exception as e:  # noqa: BLE001
        return EXIT_IO, f"投影册解析失败: {type(e).__name__}: {e}"
    try:
        ledger_snap = _latest_snapshot(registry_id, physical_path, snapshot_file)
    except Exception as e:  # noqa: BLE001
        return EXIT_IO, f"最新快照不可取（PG 只读面/JSON 源均失败）: {type(e).__name__}: {e}"

    hits: dict[str, list[str]] = {}
    ghosts: dict[str, list[str]] = {}
    for root_key in sorted(
        {sec.root_key for sec in disk_snap.sections} | {sec.root_key for sec in ledger_snap.sections}
    ):
        disk_ids = set(_entry_index(disk_snap, root_key))
        ledger_ids = set(_entry_index(ledger_snap, root_key))
        missing = sorted("|".join(x) for x in (disk_ids - ledger_ids))
        extra = sorted("|".join(x) for x in (ledger_ids - disk_ids))
        if missing:
            hits[root_key] = missing
        if extra:
            ghosts[root_key] = extra
    total = sum(len(v) for v in hits.values())
    sample = [(k, v) for k, vs in hits.items() for v in vs[:20]]
    lines = [
        f"回填扫描 {registry_id}（投影面={physical_path}，快照 version={getattr(ledger_snap, 'snapshot_version', '?')}，"
        f"零写只读）：投影面有而快照无 = {total} 条"
    ]
    for fam, vals in sorted(hits.items()):
        lines.append(f"  族 {fam}: {len(vals)} 条，样例 {vals[:5]}")
    if not hits:
        lines.append("  无命中（投影面内容与账本快照一致）")
    backfill = {k: len(v) for k, v in sorted(ghosts.items())}
    lines.append(f"  反向（快照有而投影面无，render 会补上）={backfill or '无'}；逐条清单样例={sample[:5]}")
    return (EXIT_VALIDATION if total else EXIT_SUCCESS), "\n".join(lines)


def _duplicate_regions_by_path(entries_body: str, regions: list[tuple[int, int]]) -> dict[str, list[tuple[int, int]]]:
    """按归一化 module_path 归组 entries 区块区间，只留重复组（同键 ≥2 块）。"""
    groups: dict[str, list[tuple[int, int]]] = {}
    for s, e in regions:
        p = _block_module_path(entries_body[s:e])
        if p is not None:
            groups.setdefault(p, []).append((s, e))
    return {p: rs for p, rs in groups.items() if len(rs) > 1}


def _merge_duplicate_blocks(parsed: list[dict]) -> dict:
    """重复组仲裁：信息最全条目胜出（平分时后登记者优先），其余非派生扩展字段并入胜出者。"""
    winner = max(enumerate(parsed), key=lambda t: (_entry_info_score(t[1]), t[0]))[1]
    merged = dict(winner)
    for other in parsed:
        if other is winner:
            continue
        for k, v in other.items():
            if k in _DERIVED_KEYS:
                continue  # 派生字段只认 --sync-layer 重算，不从重复段继承陈旧层
            if _is_empty_value(merged.get(k)) and not _is_empty_value(v):
                merged[k] = v
    return merged


def _dedupe_group_edits(entries_body: str, rs: list[tuple[int, int]], new_block: str) -> list[tuple[int, int, str]]:
    """单组区间编辑：胜出块落在该组首个出现位置（未触碰字节原样），后续重复块整块删除。"""
    edits: list[tuple[int, int, str]] = []
    for rank, (s, e) in enumerate(rs):
        if rank == 0:
            orig = entries_body[s:e]
            trail = orig[len(orig.rstrip("\n")) :] or "\n"
            edits.append((s, e, new_block + trail))
        else:
            edits.append((s, e, ""))
    return edits


def _plan_dedupe_edits(
    entries_body: str, dup_groups: dict[str, list[tuple[int, int]]]
) -> tuple[list[tuple[int, int, str]], list[str]]:
    """逐重复组仲裁+合并，产出 ``(edits, healed_samples)``（样例最多 5 条）。"""
    edits: list[tuple[int, int, str]] = []
    healed_samples: list[str] = []
    for p, rs in sorted(dup_groups.items()):
        parsed = [x for x in (_parse_block_entry(entries_body[s:e]) for s, e in rs) if x]
        if not parsed:
            continue  # 全部不可解析——保守跳过（写前 safe_load 自检仍兜底）
        merged = _merge_duplicate_blocks(parsed)
        merged["module_path"] = merged.get("module_path") or p
        edits.extend(_dedupe_group_edits(entries_body, rs, _format_entry_block(merged)))
        if len(healed_samples) < 5:
            healed_samples.append(p)
    return edits, healed_samples


def _count_duplicate_entries(new_text: str) -> int:
    """实测唯一性自检：返回产物中 module_path 重复的条目数（解析异常由调用方兜）。"""
    data = yaml.safe_load(new_text)
    entries = (data or {}).get("entries", []) or []
    seen: set[str] = set()
    dup_after = 0
    for e in entries:
        if not isinstance(e, dict):
            continue
        p = _normalize_path(str(e.get("module_path", "")))
        if p in seen:
            dup_after += 1
        seen.add(p)
    return dup_after


def dedupe_registry(*, dry_run: bool = False) -> tuple[int, str]:
    """整表去重（裁定#335 结论7，复发型病灶的常驻自愈通道）。

    全量扫描 entries 段同 module_path 重复组：每组保留信息最全条目
    （非空字段数最多；平分时后登记者优先=维持既有消费可见语义），其余条目
    的非空扩展字段并入胜出者；胜出块落在该组首个出现位置（未触碰字节原样），
    后续重复块整块删除。幂等：无重复时报告 0 组且不改文件。

    写盘走 _write_registry（safe_write_text CAS + 写前 safe_load 自检）。

    Returns:
        (exit_code, message)。
    """
    try:
        yaml_text = REGISTRY_YAML.read_text(encoding="utf-8")
    except Exception as e:  # noqa: BLE001
        return EXIT_IO, f"读取翻译真源失败: {type(e).__name__}: {e}"

    preamble, entries_body, tail = _split_entries_section(yaml_text)
    if _has_no_entries_section(yaml_text, preamble):
        return EXIT_IO, "YAML 中未找到 `entries:` 顶层段，无法去重"

    regions = _entries_body_regions(entries_body)
    dup_groups = _duplicate_regions_by_path(entries_body, regions)
    if not dup_groups:
        return EXIT_SUCCESS, f"去重检查：entries 无重复 module_path（0 组 / {len(regions)} 条），文件未改动"

    edits, healed_samples = _plan_dedupe_edits(entries_body, dup_groups)

    new_body = _apply_body_edits(entries_body, edits)
    new_text = _join_sections(preamble, new_body, tail)
    remaining = len(_entries_body_regions(new_body))
    removed = len(regions) - remaining

    # 写前自检：新文本必须可解析且实测唯一（"unique_key 声明→实测"落地）
    try:
        dup_after = _count_duplicate_entries(new_text)
    except Exception as e:  # noqa: BLE001
        return EXIT_IO, f"去重产物 YAML 解析失败，拒写: {type(e).__name__}: {e}"
    if dup_after:
        return EXIT_IO, f"去重后仍检出 {dup_after} 条重复（解析/区块边界异常），拒写"

    if dry_run:
        return EXIT_SUCCESS, (
            f"[dry-run] 去重预演：{len(dup_groups)} 组重复 / 拟删 {removed} 条，"
            f"entries {len(regions)}→{remaining}（样例: {', '.join(healed_samples)}）"
        )

    try:
        _write_registry(new_text, yaml_text)
    except Exception as e:  # noqa: BLE001 — 含 StaleWriteRefused/WriteVerificationError
        return EXIT_IO, f"写入翻译真源失败（CAS/IO）: {type(e).__name__}: {e}"

    _invalidate_loader_cache()
    return EXIT_SUCCESS, (
        f"去重完成：{len(dup_groups)} 组重复 / 删除 {removed} 条冗余（信息最全条目胜出+扩展字段已合并），"
        f"entries {len(regions)}→{remaining}（样例: {', '.join(healed_samples)}）"
    )


# 条目直接子键行=恰好 2 空格缩进（更深缩进是多行标量续行，永不匹配，故可安全行级定位）
_LAYER_LINE_RE = re.compile(r"^  %s:[^\n]*$" % _LAYER_KEY, re.M)


def _block_layer_value(parsed: dict | None) -> str:
    """读已解析条目的 responsibility_layer 现值（缺失/空 → 空串）。"""
    if not parsed:
        return ""
    v = parsed.get(_LAYER_KEY)
    return str(v).strip() if v is not None else ""


def _set_layer_line(block: str, layer: str | None) -> str:
    """块内 ``responsibility_layer`` 行级外科手术：有则改 / 无则加 / None 则删。

    为什么不走 ``_format_entry_block`` 整块重写：真源存量条目文本字段是裸写风格
    （``name_zh: 盘后全量对账器``），整块格式化会给数千条目加引号并把缺失的规范字段
    补成空串——一次层同步制造巨幅无语义 diff（改动面应等于语义面）。行级编辑把变更
    严格限制在该字段本身，幂等更好保证，未触碰字节原样保留。
    """
    lines = block.split("\n")
    out: list[str] = []
    seen = False
    for ln in lines:
        if _LAYER_LINE_RE.match(ln):
            if seen or layer is None:
                continue  # 删除姿态丢弃命中行；罕见的重复行一并丢弃
            out.append(f"  {_LAYER_KEY}: {layer}")
            seen = True
            continue
        out.append(ln)
    if layer is not None and not seen:
        insert_at = len(out)
        while insert_at > 0 and not out[insert_at - 1].strip():
            insert_at -= 1  # 越过块尾分隔空行，新行紧贴最后一个字段（扩展字段位）
        out.insert(insert_at, f"  {_LAYER_KEY}: {layer}")
    return "\n".join(out)


# 层同步逐块处置的计数键（顺序即 stats 文案语义，勿改名）
_LAYER_SYNC_OPS: tuple[str, ...] = (
    "added",
    "overwritten",
    "removed",
    "unchanged",
    "no_domain",
    "not_in_map",
    "unparsable",
)
# 映射查不到该域的两种处置（removed=字段被删 / not_in_map=本就无字段）都计入缺域样例
_LAYER_MISSING_OPS: frozenset[str] = frozenset({"not_in_map", "removed"})


def _layer_edit_guard_broken(check: dict | None, expected_path: str, layer: str | None) -> bool:
    """行级编辑护栏：编辑后块必须仍可独立解析、键未被破坏、字段值恰为期望。"""
    return (
        check is None
        or str(check.get("module_path") or "") != expected_path
        or _block_layer_value(check) != (layer or "")
    )


def _sync_layer_decide(block: str, layer_map: dict) -> tuple[str, str | None, str, str | None]:
    """单块层同步决策（原循环体逐行搬移，判定/文案一字不动）。

    Returns:
        ``(op, new_block, domain, error)``——op 是 ``_LAYER_SYNC_OPS`` 计数键；
        new_block 非 None 时为该块替换文本；error 非 None 时调用方 MUST 中止同步。
    """
    parsed = _parse_block_entry(block)
    if parsed is None:
        return "unparsable", None, "", None  # 形态异常块保守不动（整文件 safe_load 自检仍兜底）
    domain = str(parsed.get("domain_id") or "").strip()
    if not domain:
        return "no_domain", None, "", None  # 无从推导——不写不删，等 domain 补标后放量
    current = _block_layer_value(parsed)
    layer = _layer_for_domain(domain, layer_map)
    if layer is None:
        if not current:
            return "not_in_map", None, domain, None
        new_block = _set_layer_line(block, None)  # 映射已删该域 → 移除字段
        op = "removed"
    elif current == layer:
        return "unchanged", None, domain, None  # 幂等：第二次运行零变更
    else:
        new_block = _set_layer_line(block, layer)
        op = "added" if not current else "overwritten"
    check = _parse_block_entry(new_block)
    expected_path = str(parsed.get("module_path") or "")
    if _layer_edit_guard_broken(check, expected_path, layer):
        return op, None, domain, f"{_LAYER_KEY} 行级编辑自检失败（条目 {expected_path}），拒写"
    return op, new_block, domain, None


def _sync_layer_regions(
    entries_body: str, regions: list[tuple[int, int]], layer_map: dict
) -> tuple[list[tuple[int, int, str]], dict[str, int], set[str], str | None]:
    """逐块决策累计 ``(edits, counters, missing_domains, error)``；error 非 None 即中止。"""
    counters = dict.fromkeys(_LAYER_SYNC_OPS, 0)
    missing_domains: set[str] = set()
    edits: list[tuple[int, int, str]] = []
    for s, e in regions:
        op, new_block, domain, err = _sync_layer_decide(entries_body[s:e], layer_map)
        if err is not None:
            return [], counters, missing_domains, err
        counters[op] += 1
        if op in _LAYER_MISSING_OPS:
            missing_domains.add(domain)
        if new_block is not None:
            edits.append((s, e, new_block))
    return edits, counters, missing_domains, None


def _layer_sync_stats_message(total: int, counters: dict[str, int], missing_domains: set[str]) -> str:
    """逐项变更统计文案（写入/覆盖/移除/未变/无 domain 跳过/映射缺域跳过/不可解析）。"""
    stats = (
        f"entries {total} 条：写入 {counters['added']} / 覆盖 {counters['overwritten']} / 移除 {counters['removed']}"
        f" / 未变 {counters['unchanged']} / 无 domain 跳过 {counters['no_domain']} / 映射缺域跳过 {counters['not_in_map']}"
        f"（{len(missing_domains)} 个域）/ 不可解析 {counters['unparsable']}"
    )
    if missing_domains:
        stats += f"；映射缺域样例: {', '.join(sorted(missing_domains)[:10])}"
    return stats


def sync_layer_registry(*, dry_run: bool = False) -> tuple[int, str]:
    """整表重算/覆盖 ``responsibility_layer``（裁定#335 结论⑥，W4b；幂等）。

    逐条目按 ``domain_id`` 查映射真源（**唯一推导通道**，禁从 layer_id/目录名直推）：
      - 命中且与现值不同（含字段原本缺失）→ 写入
      - 命中且与现值相同 → 不动（幂等：第二次运行零变更）
      - ``domain_id`` 缺失/为空 → 跳过（不写不删——无从推导，等 domain 补标后放量）
      - 有 ``domain_id`` 但映射查不到 → 不写该字段；条目原本已写 → 移除（映射删行）

    映射真源不可用 → 直接 EXIT_IO 拒绝同步（空映射若放行会把全表字段抹成"未派生"）。
    写盘走 ``_write_registry``（safe_write_text CAS + ``newline="\\n"``），写前对每次
    行级编辑做块级回读自检 + 整文件 safe_load 自检。

    Returns:
        ``(exit_code, message)``——message 含逐项变更统计（写入/覆盖/移除/未变/
        无 domain 跳过/映射缺域跳过/不可解析）。
    """
    try:
        layer_map = _read_layer_map()
    except Exception as e:  # noqa: BLE001 — 源不可用必须 fail-fast，禁按空映射抹表
        return EXIT_IO, f"{_LAYER_KEY} 映射真源不可用，拒绝同步: {type(e).__name__}: {e}"
    try:
        yaml_text = REGISTRY_YAML.read_text(encoding="utf-8")
    except Exception as e:  # noqa: BLE001
        return EXIT_IO, f"读取翻译真源失败: {type(e).__name__}: {e}"

    preamble, entries_body, tail = _split_entries_section(yaml_text)
    if _has_no_entries_section(yaml_text, preamble):
        return EXIT_IO, f"YAML 中未找到 `entries:` 顶层段，无法同步 {_LAYER_KEY}"

    regions = _entries_body_regions(entries_body)
    edits, counters, missing_domains, err = _sync_layer_regions(entries_body, regions, layer_map)
    if err is not None:
        return EXIT_IO, err

    stats = _layer_sync_stats_message(len(regions), counters, missing_domains)
    if not edits:
        return EXIT_SUCCESS, f"{_LAYER_KEY} 同步：{stats}（已幂等收敛，文件未改动）"

    new_body = _apply_body_edits(entries_body, edits)
    new_text = _join_sections(preamble, new_body, tail)
    try:
        yaml.safe_load(new_text)
    except Exception as e:  # noqa: BLE001
        return EXIT_IO, f"同步产物 YAML 解析失败，拒写: {type(e).__name__}: {e}"

    if dry_run:
        return EXIT_SUCCESS, f"[dry-run] {_LAYER_KEY} 同步预演：{stats}；拟改 {len(edits)} 块（零写盘）"

    try:
        _write_registry(new_text, yaml_text)
    except Exception as e:  # noqa: BLE001 — 含 StaleWriteRefused/WriteVerificationError
        return EXIT_IO, f"写入翻译真源失败（CAS/IO）: {type(e).__name__}: {e}"

    _invalidate_loader_cache()
    return EXIT_SUCCESS, f"{_LAYER_KEY} 同步完成：{stats}；实改 {len(edits)} 块"


def _build_argparser() -> argparse.ArgumentParser:
    """_build_argparser implementation."""
    p = argparse.ArgumentParser(
        prog="add_module_translation.py",
        description=(
            "模块翻译条目合规登记工具（TRANSLATION-COVERAGE 配套=意图 API 薄壳）。按 module_path 向 "
            f"PG 账本 {REGISTRY_ID}/{FAMILY_KEY} 登记一条含大白话 plain_zh 的翻译条目，"
            "随后 publish_snapshot + 投影 render + 三方核验落地（responsibility_layer 由域→层映射真源自动派生）；"
            "--audit-projection-vs-ledger 只读回填扫描；--dedupe/--sync-layer 是投影面整表手术（账本不认）；"
            "--legacy-disk-write 是退役直写逃生旗（缺省不走）。"
        ),
    )
    p.add_argument("--path", default="", help="模块相对路径（如 src/zephyr/.../m.py）")
    p.add_argument("--domain", default="", help="域 ID（如 D_GOV_RULE）")
    p.add_argument("--name-zh", default="", help="模块中文名")
    p.add_argument("--name-en", default="", help="模块英文名（可选）")
    p.add_argument("--desc-zh", default="", help="技术简介中文（可选）")
    p.add_argument("--desc-en", default="", help="技术简介英文（可选）")
    p.add_argument("--plain-zh", default="", help="大白话简介（做什么/解决什么/怎么做，CJK≥8，禁模板化）")
    p.add_argument(
        "--session", default="", help=f"登记归因会话名（账本 created_by/updated_by；缺省 {DEFAULT_SESSION}）"
    )
    p.add_argument(
        "--clear-field",
        action="append",
        default=None,
        metavar="FIELD",
        help="点名删除在册某字段（可重复）。删除集只能逐条点名——未点名的键永不从在册 payload 消失",
    )
    p.add_argument("--dry-run", action="store_true", help="只校验+差分预演（零账本写/零发布/零 render/零直写）")
    p.add_argument(
        "--audit-projection-vs-ledger",
        action="store_true",
        help=(
            "只读回填扫描：报「投影面有而最新快照无」的条目（就是 2026-10-11 backup_reconciler_shadow "
            "被 render 修剪的机判形态）。零写；命中>0 → exit 1。可配 --registry-id/--physical-path/"
            "--snapshot-file 扫别的册或走 JSON 影子快照通道"
        ),
    )
    p.add_argument("--registry-id", default=REGISTRY_ID, help=f"审计扫描目标册账本号（缺省 {REGISTRY_ID}）")
    p.add_argument("--physical-path", default=REGISTRY_REL, help="审计扫描目标册投影路径（相对仓根，缺省本翻译册）")
    p.add_argument(
        "--snapshot-file",
        default=None,
        help="审计用快照 JSON 文件源（缺省=PG registry_snapshot 最新版；影子期/红蓝通道同 CLI 正门）",
    )
    p.add_argument(
        "--legacy-disk-write",
        action="store_true",
        help=(
            "退役直写逃生旗：跳过账本，直接 CAS 写投影 YAML。缺省不走；"
            "后果=该条目不进账本，下一次 render（PG-wins）会把它修剪掉（本工具会打红色警告+落审计留痕）"
        ),
    )
    p.add_argument(
        "--dedupe",
        action="store_true",
        help=(
            "整表去重（**投影面手术**：账本不认，下一次 render 即被覆写，仅作过渡期对账预览用；可配 --dry-run 预演）"
        ),
    )
    p.add_argument(
        "--sync-layer",
        action="store_true",
        help=(
            "整表重算 responsibility_layer（**投影面手术**：账本不认，render 后失效；日常登记走 "
            "domain_id 派生即可；幂等；可配 --dry-run 只看账）"
        ),
    )
    return p


_TABLE_OPS = ("dedupe", "sync_layer", "audit_projection_vs_ledger")


def _has_upsert_args(args: argparse.Namespace) -> bool:
    """是否带了单条目登记参数（整表操作与它互斥）。"""
    return any(
        (
            (args.path or "").strip(),
            (args.domain or "").strip(),
            (args.name_zh or "").strip(),
            (args.plain_zh or "").strip(),
        )
    )


def main(argv: list[str] | None = None) -> int:
    """Entry point: parse args, run logic, return exit code."""
    args = _build_argparser().parse_args(argv)

    if sum(1 for op in _TABLE_OPS if getattr(args, op)) > 1:
        print("--dedupe / --sync-layer / --audit-projection-vs-ledger 互斥（整表操作一次只做一种）")
        return EXIT_VALIDATION

    if args.audit_projection_vs_ledger:
        if _has_upsert_args(args):
            print("--audit-projection-vs-ledger 与单条目登记参数互斥（审计是只读整册操作）")
            return EXIT_VALIDATION
        code, msg = audit_projection_vs_ledger(
            registry_id=args.registry_id,
            physical_path=args.physical_path,
            snapshot_file=args.snapshot_file,
        )
        print(msg)
        return code

    if args.dedupe:
        if _has_upsert_args(args):
            print("--dedupe 与 upsert 参数互斥（去重是整表操作，不接受单条目字段）")
            return EXIT_VALIDATION
        code, msg = dedupe_registry(dry_run=args.dry_run)
        print(msg)
        return code

    if args.sync_layer:
        if _has_upsert_args(args):
            print("--sync-layer 与 upsert 参数互斥（层同步是整表操作，不接受单条目字段）")
            return EXIT_VALIDATION
        code, msg = sync_layer_registry(dry_run=args.dry_run)
        print(msg)
        return code

    missing = [
        flag
        for flag, val in (
            ("--path", args.path),
            ("--domain", args.domain),
            ("--name-zh", args.name_zh),
            ("--plain-zh", args.plain_zh),
        )
        if not (val or "").strip()
    ]
    if missing:
        print(
            f"必填参数缺失: {missing}（或改用 --audit-projection-vs-ledger 做只读回填扫描 / "
            "--dedupe 整表去重 / --sync-layer 整表层同步）"
        )
        return EXIT_VALIDATION

    entry = {
        "module_path": _normalize_path(args.path),
        "domain_id": args.domain,
        "name_zh": args.name_zh,
        "name_en": args.name_en,
        "desc_zh": args.desc_zh,
        "desc_en": args.desc_en,
        "plain_zh": args.plain_zh,
    }
    code, msg = add_translation(
        entry,
        dry_run=args.dry_run,
        session_id=args.session,
        legacy_disk_write=args.legacy_disk_write,
        clear_fields=tuple(args.clear_field or ()),
    )
    print(msg)
    return code


if __name__ == "__main__":
    sys.exit(main())
