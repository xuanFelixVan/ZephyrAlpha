# [BLUEPRINT] MOD-INF-005 | scripts/governance/d3_metadata/add_module_translation.py | §
# [MODULE] scripts.governance.d3_metadata.add_module_translation
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance._shared.module_translation_loader (is_generic_plain_zh, is_generic_plain_suffix, get_module_translation); scripts.governance._shared.yaml_utils (load_responsibility_layer_map); docs/01_policies_and_standards/_registry/catalogs/module_translation_registry.yaml (翻译真源); docs/01_policies_and_standards/_registry/catalogs/domain_responsibility_layer_mapping.yaml (responsibility_layer 唯一真源)
# [CONSUMERS] AI 新建/更新模块时调用以合规写入大白话简介；TRANSLATION-COVERAGE gate 修复指引引用
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 按 module_path 唯一键 upsert；写入前 MUST 通过 is_generic_plain_zh/is_generic_plain_suffix 校验（拒模板化简介，治本）；强制双引号转义；写后 YAML 解析校验；写入后失效 module_translation_loader 缓存；module_path 正斜杠归一化；responsibility_layer 只准从 domain_responsibility_layer_mapping.yaml 按 domain_id 推导（裁定#335 结论⑥，禁从 layer_id/目录名直推），映射缺域=WARNING 留空不阻断，派生字段永不从旧块/重复块继承
# [MODIFY-GUARD] scripts/governance/d3_metadata/add_module_translation.py
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] exit 0=SUCCESS, exit 1=VALIDATION_ERROR(简介不合规/字段缺失), exit 2=IO/YAML_ERROR
# [TESTS] tests/governance/d3_metadata/test_add_module_translation.py
# [A_module] module_id=MOD-INF-005 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""add_module_translation.py — 模块翻译条目合规写入工具（TRANSLATION-COVERAGE 配套）。

把"在哪里更新 / 怎么更新"落地为一条命令：AI 新建或更新模块时，调用本脚本向
翻译真源 ``module_translation_registry.yaml`` upsert 一条 entry（含大白话 plain_zh）。

真源边界（SSoT 分类铁律 TRAE-062）
----------------------------------
模块翻译属**规则数据** → 真源是 YAML 文件。本脚本是 YAML 的合规写入入口，
禁止在生成器代码/DB 里硬编码模块翻译。与 ``apply_depgraph.py``（写 DB 架构数据）
是正交真源，互不写入，只能校验对方。

治本（防蔓延闭环）
------------------
病根：此前大白话简介靠事后治理（审计→批量修→提交），新模块仍会持续制造缺口。
本工具 + TRANSLATION-COVERAGE gate + reconciler 构成"写入入口→提交阻断→存量对账"
三层闭环：AI 创新模块后跑本命令合规写入，gate 在提交时校验，reconciler 持续对账。

写入前校验（治本，非事后）
--------------------------
1. plain_zh 非空且 CJK≥8（与本次治理基线一致）
2. 复用 module_translation_loader.is_generic_plain_zh 拒全串通用模板
3. 复用 is_generic_plain_suffix 拒剥离 name 前缀后的通用后缀
任一不过 → exit 1，拒绝写入（防 AI 填"提供包入口和模块加载功能"糊弄）。

用法 / Usage::

    python scripts/governance/d3_metadata/add_module_translation.py \\
        --path src/zephyr/xxx/yyy.py \\
        --domain D_GOV_RULE \\
        --name-zh "中文名" --name-en "English Name" \\
        --desc-zh "技术简介" --desc-en "English desc" \\
        --plain-zh "大白话：做什么/解决什么/怎么做"

    # 整表去重（裁定#335 结论7，复发型病灶的常驻自愈通道）：扫描 entries 段全部
    # 同 module_path 重复条目→保留信息最全条目并合并扩展字段→CAS 写回；幂等，
    # 可配 --dry-run 先看账不写盘
    python scripts/governance/d3_metadata/add_module_translation.py --dedupe [--dry-run]

    # 整表重算 responsibility_layer（裁定#335 结论⑥，W4b）：逐条目按 domain_id 从
    # domain_responsibility_layer_mapping.yaml 覆盖该字段（幂等收敛；映射删域→移除字段）
    # 默认放量由主会话执行，日常先 --dry-run 看账
    python scripts/governance/d3_metadata/add_module_translation.py --sync-layer [--dry-run]

responsibility_layer 派生铁律（裁定#335 结论⑥）
--------------------------------------------------
新条目 upsert 时按 ``--domain`` 自动填 ``responsibility_layer``，唯一推导通道是
域→职责层映射真源（经 ``yaml_utils.load_responsibility_layer_map``）；**禁从
layer_id/目录名直推**（争点 C1/C17）。映射查不到该域 → stderr WARNING + 该字段留空
（不阻断翻译写入，翻译与层是两件事）；映射可用而调用方塞了别的值 → 以真源为准覆盖。
派生字段永不从旧块/重复块继承（否则映射删域后旧值会被 upsert 复活）。

Exit codes:
    0 = SUCCESS（upsert / 去重 / 层同步成功，或 dry-run 校验通过）
    1 = VALIDATION_ERROR（简介不合规 / 必填字段缺失 / --dedupe、--sync-layer 与 upsert 参数互斥）
    2 = IO/YAML_ERROR（文件读写/CAS 拒写/解析失败/层映射真源不可用）
"""

from __future__ import annotations

__manifest__ = """
args: []
description: add_module_translation.py — 模块翻译条目合规写入工具（TRANSLATION-COVERAGE 配套）。
dimensions:
- D3
priority: P2
timeout_seconds: 60
warn_only: false
"""


import argparse
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

# 翻译真源路径（SSoT：规则数据真源是 YAML 文件）
REGISTRY_YAML = (
    REPO_ROOT / "docs" / "01_policies_and_standards" / "_registry" / "catalogs" / "module_translation_registry.yaml"
)

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
    return [
        (s, starts[i + 1] if i + 1 < len(starts) else len(entries_body))
        for i, s in enumerate(starts)
    ]


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
        # 合并全部命中块的扩展字段（非空优先，先到先得不覆盖已有非空值）
        # 派生字段（_DERIVED_KEYS）除外：它只由映射真源重算，继承旧块会让"映射已删域"
        # 的陈旧层值在 upsert 时复活，破坏 --sync-layer 的收敛语义。
        for s, e in matches:
            parsed = _parse_block_entry(entries_body[s:e]) or {}
            for k, v in parsed.items():
                if k in _CANONICAL_KEYS or k in _DERIVED_KEYS:
                    continue
                if _is_empty_value(new_entry.get(k)) and not _is_empty_value(v):
                    new_entry[k] = v
        new_block = _format_entry_block(new_entry)
        edits: list[tuple[int, int, str]] = []
        for rank, (s, e) in enumerate(matches):
            if rank == 0:
                orig = entries_body[s:e]
                trail = orig[len(orig.rstrip("\n")):] or "\n"  # 保留原块后的分隔空白
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


def add_translation(entry: dict, *, dry_run: bool = False) -> tuple[int, str]:
    """主入口：校验 + 派生 responsibility_layer + upsert（含重复自愈）+ CAS 写盘 + 解析校验。

    Args:
        entry: 含 module_path/domain_id/name_zh/name_en/desc_zh/desc_en/plain_zh 的 dict；
            ``responsibility_layer`` 无需调用方提供——按 domain_id 从映射真源自动派生
            （映射缺域则留空，见裁定#335 结论⑥）。
        dry_run: True 只校验不写盘。

    Returns:
        (exit_code, message)。
    """
    # 1. 必填字段校验
    required = ["module_path", "domain_id", "name_zh", "plain_zh"]
    missing = [f for f in required if not (entry.get(f) or "").strip()]
    if missing:
        return EXIT_VALIDATION, f"必填字段缺失: {missing}"

    # 2. plain_zh 合规校验（写入前治本）
    ok, reason = _validate_plain(entry["plain_zh"], entry["name_zh"])
    if not ok:
        return EXIT_VALIDATION, f"plain_zh 校验失败: {reason}"

    # 2.5 responsibility_layer 派生（裁定#335 结论⑥）：唯一通道=域→层映射真源。
    # 真源自身不可用只降级"不填"（翻译写入与层是两件事，不连坐），映射缺该域由
    # _fill_responsibility_layer 逐条 WARNING。
    try:
        layer_map: dict[str, str] | None = _read_layer_map()
    except Exception as e:  # noqa: BLE001 — 层真源故障不阻断翻译写入
        print(
            f"[add_module_translation] WARNING: {_LAYER_KEY} 映射真源不可用"
            f"（{type(e).__name__}: {e}），本次不填该字段",
            file=sys.stderr,
        )
        layer_map = None
    entry = _fill_responsibility_layer(entry, layer_map)

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
    return EXIT_SUCCESS, f"{action} 翻译条目: {entry['module_path']}（entries 共 {len(entries)} 条）"


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


def _dedupe_group_edits(
    entries_body: str, rs: list[tuple[int, int]], new_block: str
) -> list[tuple[int, int, str]]:
    """单组区间编辑：胜出块落在该组首个出现位置（未触碰字节原样），后续重复块整块删除。"""
    edits: list[tuple[int, int, str]] = []
    for rank, (s, e) in enumerate(rs):
        if rank == 0:
            orig = entries_body[s:e]
            trail = orig[len(orig.rstrip("\n")):] or "\n"
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
        description="模块翻译条目合规写入工具（TRANSLATION-COVERAGE 配套）。按 module_path upsert 一条含大白话 plain_zh 的翻译条目（responsibility_layer 由域→层映射真源自动派生）；--dedupe 整表去重；--sync-layer 整表重算 responsibility_layer。",
    )
    p.add_argument("--path", default="", help="模块相对路径（如 src/zephyr/.../m.py）")
    p.add_argument("--domain", default="", help="域 ID（如 D_GOV_RULE）")
    p.add_argument("--name-zh", default="", help="模块中文名")
    p.add_argument("--name-en", default="", help="模块英文名（可选）")
    p.add_argument("--desc-zh", default="", help="技术简介中文（可选）")
    p.add_argument("--desc-en", default="", help="技术简介英文（可选）")
    p.add_argument("--plain-zh", default="", help="大白话简介（做什么/解决什么/怎么做，CJK≥8，禁模板化）")
    p.add_argument("--dry-run", action="store_true", help="只校验不写盘")
    p.add_argument(
        "--dedupe",
        action="store_true",
        help="整表去重：扫描 entries 段全部同 module_path 重复条目，保留信息最全条目并合并扩展字段后 CAS 写回（幂等；可配 --dry-run 预演）",
    )
    p.add_argument(
        "--sync-layer",
        action="store_true",
        help="整表重算 responsibility_layer：逐条目按 domain_id 从 domain_responsibility_layer_mapping.yaml 覆盖该字段（唯一推导通道，禁从 layer_id/目录名直推；幂等；可配 --dry-run 只看账）",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    """Entry point: parse args, run logic, return exit code."""
    args = _build_argparser().parse_args(argv)

    if args.dedupe and args.sync_layer:
        print("--dedupe 与 --sync-layer 互斥（都是整表操作，一次只做一种）")
        return EXIT_VALIDATION

    if args.dedupe:
        if any(((args.path or "").strip(), (args.domain or "").strip(), (args.name_zh or "").strip(), (args.plain_zh or "").strip())):
            print("--dedupe 与 upsert 参数互斥（去重是整表操作，不接受单条目字段）")
            return EXIT_VALIDATION
        code, msg = dedupe_registry(dry_run=args.dry_run)
        print(msg)
        return code

    if args.sync_layer:
        if any(((args.path or "").strip(), (args.domain or "").strip(), (args.name_zh or "").strip(), (args.plain_zh or "").strip())):
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
        print(f"必填参数缺失: {missing}（或改用 --dedupe 做整表去重 / --sync-layer 做整表层同步）")
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
    code, msg = add_translation(entry, dry_run=args.dry_run)
    print(msg)
    return code


if __name__ == "__main__":
    sys.exit(main())
