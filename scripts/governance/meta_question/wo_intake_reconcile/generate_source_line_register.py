#!/usr/bin/env python3
# [BLUEPRINT] MOD-CHAINPILE-METAQ | docs/_working/chain_piling_campaign/infra_mining/10_intake_gate_design.md | §3 要素1/要素5 命中真源（W4 源线谱机器可读册）
# [MODULE] scripts.governance.meta_question.wo001_003.generate_source_line_register
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] zephyr.shared.utils.time_utils (now_utc，禁裸 datetime.now)；zephyr.shared.io.file_utils (safe_write_text，机生落盘唯一通道)；PyYAML
# [CONSUMERS] src/zephyr/governance/meta_question/meta_question_registry.py（五要素机检要素1/要素5 真检命中册，WO-001② 补丁）；
#             《模板生成器设计》11§2 示例1 TPL-U-001 取值域 domain_ref=source_line_registry（line/signal_vocab 槽）；
#             tests/governance/meta_question/wo001_003/test_source_line_register_generator.py
# [STARTUP] manual
# [MATURITY] new
# [INVARIANTS] 单向派生：md=唯一真源、YAML=机生视图（禁双向同步/禁手改 YAML，宪法 §9.5 静态清单生成器产出红线）；
#              计数一律本器实算（md 自陈条数仅作对账靶，禁把 29/16/10/3 写进判据代码路径）；
#              逐条对账七项：①md 自陈条数=实解析条数 ②总表↔明细 id 集/档位/线名一致 ③档位字段完备性（A/B=U1-U6，C=U1+缺什么+U5+U6预设+状态）
#              ④§5 勾选表 ⊆ 全表且档位/挂接层与 U5 派生一致 ⑤每线 token 非空 ⑥盘上 YAML=再生内容（漂移即红）⑦每线 U 文本逐字回对 md；
#              源缺失/md 结构解析失败=fail-closed 退出 2，禁产半成品册（防降级桩误判"已建成"）；
#              时间只经 now_utc()（RULE-SCHEMA-TZ）
# [MODIFY-GUARD] docs/_working/chain_piling_campaign/02_source_line_registry.md（真源，改册先改 md）+ 10_intake_gate_design.md §3（判据契约）
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] EXIT 0=生成且自校验全过；EXIT 1=自校验对账不过（逐条差异打印，不落盘）；EXIT 2=异常（md 缺失/结构不可解析/YAML 读失败，fail-closed）
# [TESTS] tests/governance/meta_question/wo001_003/test_source_line_register_generator.py（真源 md 蓝腿 + 构造 md 红腿：删线/改档位/伪造计数必红）
# [TTL] permanent
"""generate_source_line_register — W4 源线谱机器可读册生成器（WO-001①，st-metaq-gc-20260924）。

真源：``docs/_working/chain_piling_campaign/02_source_line_registry.md``（29 线三档 + 每线 U1-U6）。
产物：``data/registers/metaq_source_line/source_line_registry.yaml``。

为什么存在（PQ-0004 根因）：入库闸五要素机检的要素 1「能被数据回答」与要素 5「PIT 安全」
的命中真源就是 W4 源线谱（《入库闸设计》§3 行 1/行 5），但 W4 只有人读 md、无机器可读面，
所以 registry.py 里的桩无条件降级（283/283 全带 ``degraded_check``）。本件把 md 生成器化，
使 registry 侧「查册命中→不降级」成为可机械复算的真检。

用法::

    python scripts/governance/meta_question/wo001_003/generate_source_line_register.py            # 生成+自校验+落盘
    python scripts/governance/meta_question/wo001_003/generate_source_line_register.py --check    # 只对账不落盘（漂移检测）
    python scripts/governance/meta_question/wo001_003/generate_source_line_register.py --print    # 打 YAML 到 stdout（零写，排雷用）

对账不过即 EXIT 1 且不落盘（宁缺毋滥：半成品册会让降级桩误判"册已建成"）。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Final

import yaml

_BOOT_ROOT = Path(__file__).resolve().parents[4]
from zephyr.shared.io.paths import REPO_ROOT  # noqa: E402  仓根唯一真源（原为本地重定义，SSOT-REDEFINITION 对症）

SOURCE_MD = REPO_ROOT / "docs" / "_working" / "chain_piling_campaign" / "02_source_line_registry.md"
OUTPUT_YAML = REPO_ROOT / "data" / "registers" / "metaq_source_line" / "source_line_registry.yaml"

GENERATOR_ID: Final = "scripts/governance/meta_question/wo001_003/generate_source_line_register.py"
SCHEMA_VERSION: Final = "1.0.0"

EXIT_OK: Final = 0
EXIT_DRIFT: Final = 1
EXIT_ERROR: Final = 2

# 线 id / 明细小节标题 / U 族字段行 / 其他字段行的机械形状（真源 md 格式）
_LINE_ID_RE: Final = re.compile(r"^SL-[ABC]\d{2}$")
_SECTION_RE: Final = re.compile(r"^### (SL-[ABC]\d{2})｜(.+?)（([ABC])）\s*$", re.M)
_BULLET_RE: Final = re.compile(r"^- ([^｜：\n]{1,12})[｜：]\s*(.*)$")
_C_PACKED_RE: Final = re.compile(r"^- (U[1-6][^｜：\n]*?)=(.*)$")
_U_KEY_RE: Final = re.compile(r"^U([1-6])$")
_DS_TOKEN_RE: Final = re.compile(r"DS-[A-Z0-9][A-Z0-9_\-]*")
_LATIN_TOKEN_RE: Final = re.compile(r"[A-Za-z][A-Za-z0-9_.]{2,}")
_LAYER_RE: Final = re.compile(r"\bL([0-6])\b")
_TIER_CLAIM_RE: Final = re.compile(r"^## §\d+\s*([ABC]) 档[·\s].*?（(\d+) 条", re.M)
_TOTAL_CLAIM_RE: Final = re.compile(r"^## §1[^\n]*?（(\d+) 条", re.M)

# A/B 档必具 U1-U6；C 档（无渠道）设计性缺 U2/U3/U4，必具 U1+缺什么+U5+U6 预设+状态
_REQUIRED_U: Final = frozenset({"U1", "U2", "U3", "U4", "U5", "U6"})
_C_REQUIRED_FIELDS: Final = frozenset({"U1", "缺什么", "U5", "U6 预设", "状态"})

# PIT as-of 声明词表（要素 5 真检的结构面：该线是否声明了可用的 as-of/公告/发布时戳机制）。
# 词表本身是本件源码常量（有版本、可审、随 md 变更走本件升级），md 文本为判定输入——不反向写 md。
_PIT_ASOF_VOCAB: Final = (
    "ann_date",
    "end_date",
    "notice_date",
    "HOLD_NOTICE_DATE",
    "trade_date",
    "as_of",
    "as-of",
    "timestamp",
    "发布时戳",
    "发布时间戳",
    "公告日",
    "披露",
    "发布即",
    "快照",
    "发布快照",
    "vintage",
    "修订",
    "不可回补",
    "不可改",
    "断档",
    "落定",
    "冻结",
)
# token 抽取噪声词（URL 主体/协议/占位），防把 https 域名当数据源锚
_TOKEN_NOISE: Final = frozenset(
    {
        "https",
        "http",
        "www",
        "com",
        "cn",
        "org",
        "Api",
        "API",
        "DS",
        "U1",
        "U2",
        "U3",
        "U4",
        "U5",
        "U6",
    }
)


@dataclass(frozen=True)
class SourceLineRow:
    """一条源线（总表行 + 明细小节字段 + 派生面）。"""

    line_id: str
    name: str
    tier: str
    freshness: str
    channel_cell: str
    fields: dict[str, str] = field(default_factory=dict)
    detail_name: str = ""
    ds_anchors: tuple[str, ...] = ()
    source_tokens: tuple[str, ...] = ()
    signal_vocab: tuple[str, ...] = ()
    declared_layers: tuple[str, ...] = ()
    pit_asof_terms: tuple[str, ...] = ()

    def as_entry(self) -> dict[str, Any]:
        """YAML 条目（字段序稳定，禁 dict 乱序造成再生漂移）。"""
        return {
            "line_id": self.line_id,
            "name": self.name,
            "detail_name": self.detail_name,
            "tier": self.tier,
            "freshness": self.freshness,
            "channel_cell": self.channel_cell,
            "expansion_eligible": self.tier in ("A", "B"),
            "ds_anchors": list(self.ds_anchors),
            "source_tokens": list(self.source_tokens),
            "signal_vocab": list(self.signal_vocab),
            "declared_layers": list(self.declared_layers),
            "pit_asof_terms": list(self.pit_asof_terms),
            "pit_asof_declared": bool(self.pit_asof_terms),
            "u_fields": {k: self.fields[k] for k in sorted(self.fields)},
        }


# ---------------------------------------------------------------------------
# md 解析（总表 + 明细小节）
# ---------------------------------------------------------------------------


def _split_table_row(line: str) -> list[str]:
    """markdown 表行 → 单元格列表（首尾空管切掉）。"""
    cells = [c.strip() for c in line.strip().strip("|").split("|")]
    return cells


def parse_summary_table(md: str) -> list[dict[str, str]]:
    """§1 三档总表 → 行清单（id/线名/档/渠道锚/新鲜度）。"""
    rows: list[dict[str, str]] = []
    for raw in md.splitlines():
        if not raw.strip().startswith("|"):
            continue
        cells = _split_table_row(raw)
        if len(cells) != 5 or not _LINE_ID_RE.match(cells[0]):
            continue
        rows.append(
            {
                "line_id": cells[0],
                "name": cells[1],
                "tier": cells[2],
                "channel_cell": cells[3],
                "freshness": cells[4],
            }
        )
    return rows


def parse_detail_sections(md: str) -> dict[str, dict[str, Any]]:
    """`### SL-xxx｜线名（档）` 小节 → {id: {name, tier, fields}}（字段按 `- K｜V` / `- K：V` 归并）。

    小节正文界定=下一个 `### SL-` 或下一个 `## ` 二级标题（先到为准）——防末条线正文
    吃掉 §5/§6 的编号列表行（前科：2026-09-24 本班实测，越界会把净零声明当 U 字段入册）。
    """
    sections: dict[str, dict[str, Any]] = {}
    matches = list(_SECTION_RE.finditer(md))
    h2_starts = [m.start() for m in re.finditer(r"^## ", md, re.M)]
    for idx, m in enumerate(matches):
        boundaries = [matches[idx + 1].start()] if idx + 1 < len(matches) else []
        boundaries += [h for h in h2_starts if h > m.start()]
        end = min(boundaries) if boundaries else len(md)
        body = md[m.end() : end]
        sections[m.group(1)] = {"name": m.group(2), "tier": m.group(3), "fields": _parse_bullets(body)}
    return sections


def _parse_bullets(body: str) -> dict[str, str]:
    """小节正文的 `- 键｜值` / `- 键：值` 行 → dict（U1-U6 与档别专用字段同层）。

    C 档专用紧凑行（`- U5=L3/L4；U6 预设=…；状态=**挂起**（…）`）按 ；切段逐对展开，
    与常规行同层入 dict（md 排版差异不改变字段语义）。
    """
    out: dict[str, str] = {}
    for raw in body.splitlines():
        stripped = raw.strip()
        m = _BULLET_RE.match(stripped)
        if m:
            key, value = m.group(1).strip(), m.group(2).strip()
            if value:
                out.setdefault(key, value)
            continue
        for segment in stripped.lstrip("- ").split("；"):
            key, sep, value = segment.partition("=")
            if sep and key.strip() and value.strip():
                out.setdefault(key.strip(), value.strip().rstrip("。"))
    return {k: _clean_value(v) for k, v in out.items()}


def _clean_value(value: str) -> str:
    """md 强调记号（**bold**）剥离，字段语义文本原样保留。"""
    return value.replace("**", "").strip()


def parse_checklist_table(md: str) -> list[dict[str, str]]:
    """§5 十条线勾选表 → {线, 档, 挂接层}（对账靶：W6 展开锚集合与 U5 派生层）。"""
    rows: list[dict[str, str]] = []
    started = False
    for raw in md.splitlines():
        if raw.startswith("## §5"):
            started = True
        elif raw.startswith("## §6"):
            started = False
        if not started or not raw.strip().startswith("|"):
            continue
        cells = _split_table_row(raw)
        if len(cells) != 6 or not cells[1].startswith("SL-"):
            continue
        line_id = cells[1].split()[0]
        rows.append({"line_id": line_id, "tier": cells[2], "layers": cells[3]})
    return rows


# ---------------------------------------------------------------------------
# 派生面（DS 锚 / token 宇宙 / 信号词 / 层 / PIT as-of）
# ---------------------------------------------------------------------------


def _ds_anchor_tuple(summary: dict[str, str], fields: dict[str, str]) -> tuple[str, ...]:
    """DS-* 锚：明细「DS 锚」行为主，总表渠道列为辅（含 DS-MINIQMT/TUSHARE 简写展开）。"""
    text = fields.get("DS 锚") or fields.get("渠道") or ""
    cell = summary.get("channel_cell") or ""
    anchors: list[str] = []
    for token in _DS_TOKEN_RE.findall(text):
        if token not in anchors:
            anchors.append(token)
    for token in _expand_compact_ds(cell):
        if token not in anchors:
            anchors.append(token)
    return tuple(anchors)


def _expand_compact_ds(cell: str) -> list[str]:
    """总表简写 `DS-A/ B /C`（后续段省 DS- 前缀）→ 补全为 DS-* 全集。"""
    out: list[str] = []
    for part in cell.split("/"):
        part = part.strip()
        if not part:
            continue
        if _LINE_ID_RE.match(part):
            continue
        token = part if part.startswith("DS-") else f"DS-{part}"
        if _DS_TOKEN_RE.fullmatch(token.replace(" ", "")):
            out.append(token)
    return out


def source_token_tuple(summary: dict[str, str], fields: dict[str, str]) -> tuple[str, ...]:
    """该线可命中 token 宇宙：DS 锚 + 渠道/DS 锚行的**具名短语** + 单词形标识符 + 中文渠道名。

    命中面=md 原文具名面（禁泛化匹配/禁子串包含判定——泛化会把命名漂移洗成命中，
    真检即失去牙齿；实测留证：登记侧写『东方财富股吧』而 md 写『东财股吧』必判不命中）。
    """
    text = " ".join(
        [
            summary.get("channel_cell") or "",
            fields.get("DS 锚") or "",
            fields.get("渠道") or "",
        ]
    )
    tokens: list[str] = list(_ds_anchor_tuple(summary, fields))
    # 具名短语逐源抽取（禁先拼接再切——拼接会把 cell 与明细行的同名渠道粘成 "X X" 脏 token，
    # 2026-09-24 本班实测 SL-B02『NWS API』因此判不命中）
    for part in (summary.get("channel_cell"), fields.get("DS 锚"), fields.get("渠道")):
        if part:
            tokens += _name_phrases(part)
    for token in _LATIN_TOKEN_RE.findall(text):
        if token in _TOKEN_NOISE or token.startswith("http"):
            continue
        tokens.append(token)
    for token in _cjk_channel_tokens(text):
        tokens.append(token)
    return tuple(_dedup(tokens))


_URL_STRIP_RE: Final = re.compile(r"<[^>]*>")
_PAREN_STRIP_RE: Final = re.compile(r"[（(][^（()）]*[)）]")
_PHRASE_SPLIT_RE: Final = re.compile(r"[；;。=、/]| 或 ")
# 定语截断词表：渠道行常写「<名称><定语短语>」（如『海关总署月度发布』『Mastercard
# SpendingPulse 官方汇总发布』），截出名称面入命中宇宙；截断词为本件源码常量（可审、
# 随 md 排版演进升级），非模糊包含匹配（登记侧写『东方财富股吧』而 md 写『东财股吧』
# 仍判不命中——命名漂移必显形，真检才有牙齿）。
_PHRASE_CUTOFFS: Final = (
    "官方",
    "免费",
    "商业",
    "付费",
    "会员",
    "订阅",
    "月度",
    "日度",
    "周度",
    "汇总",
    "发布",
    "数据服务",
    "平台",
    "抓取",
    "同类",
    " proxy",
    "proxy",
)


def _name_phrases(text: str) -> list[str]:
    """渠道/DS 锚行 → 具名短语集（含斜杠并列与定语截断两式派生）。"""
    out: list[str] = []
    for chunk in _PHRASE_SPLIT_RE.split(_PAREN_STRIP_RE.sub(" ", _strip_urls(text))):
        head = re.sub(r"\s{2,}", " ", chunk).strip(" ·-—*，,")
        if _phrase_acceptable(head):
            out.append(head)
        for cut in _cut_before_cutoff(head):
            out.append(cut)
    return [p for p in out if p]


def _phrase_acceptable(head: str) -> bool:
    return bool(head) and len(head) <= 40 and bool(re.search(r"[A-Za-z\u4e00-\u9fff]{2}", head))


def _cut_before_cutoff(head: str) -> list[str]:
    """按定语截断词表切出名称面（'海关总署月度发布' → '海关总署'）。"""
    positions = [head.find(word) for word in _PHRASE_CUTOFFS if head.find(word) > 0]
    if not positions:
        return []
    cut = head[: min(positions)].strip(" ·-—*，,")
    return [cut] if _phrase_acceptable(cut) else []


def _strip_urls(text: str) -> str:
    return _URL_STRIP_RE.sub(" ", text.replace("https://", " ").replace("http://", " "))


def _cjk_channel_tokens(text: str) -> list[str]:
    """中文渠道名（雪球/智联招聘/中国政府采购网…）：切分隔符后保留含 CJK 的短段。"""
    out: list[str] = []
    for chunk in re.split(r"[/、,，;；()（）\s]+", text):
        chunk = chunk.strip("·.-—*")
        if 2 <= len(chunk) <= 18 and re.search(r"[\u4e00-\u9fff]", chunk):
            out.append(chunk)
    return out


def _dedup(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        if item and item not in seen:
            seen.add(item)
            out.append(item)
    return out


def signal_vocab_tuple(fields: dict[str, str]) -> tuple[str, ...]:
    """U1 括号内「信号词：a/b/c」→ 该线信号词子集（TPL-U-001 signal 槽取值域）。"""
    u1 = fields.get("U1") or ""
    m = re.search(r"信号词[:：](.+?)）", u1)
    if not m:
        return ()
    return tuple(t.strip("·.。；;") for t in m.group(1).split("/") if t.strip("·.。；;"))


def declared_layer_tuple(fields: dict[str, str]) -> tuple[str, ...]:
    """U5（消费方=七层挂接）中点名的层码 L0-L6。"""
    u5 = fields.get("U5") or ""
    return tuple(f"L{n}" for n in dict.fromkeys(_LAYER_RE.findall(u5)))


def pit_asof_tuple(fields: dict[str, str]) -> tuple[str, ...]:
    """U3/U4 文本中机械命中的 as-of/公告/修订不可回补声明词（要素 5 结构面）。"""
    text = " ".join([fields.get("U4") or "", fields.get("U3") or ""])
    hits = [term for term in _PIT_ASOF_VOCAB if term in text]
    return tuple(hits)


# ---------------------------------------------------------------------------
# 组装
# ----------------------------------------------------------------


def build_lines(md: str) -> list[SourceLineRow]:
    """md → 逐线条目（总表定序，明细供字段；缺任一来源即抛错 fail-closed）。"""
    summary_rows = parse_summary_table(md)
    sections = parse_detail_sections(md)
    if not summary_rows or not sections:
        raise ValueError("源线谱 md 结构不可解析（总表或明细小节为空）")
    lines: list[SourceLineRow] = []
    for row in summary_rows:
        section = sections.get(row["line_id"])
        fields = dict(section["fields"]) if section else {}
        detail_name = str(section["name"]) if section else ""
        lines.append(
            SourceLineRow(
                line_id=row["line_id"],
                name=row["name"],
                tier=row["tier"],
                freshness=row["freshness"],
                channel_cell=row["channel_cell"],
                fields=fields,
                detail_name=detail_name,
                ds_anchors=_ds_anchor_tuple(row, fields),
                source_tokens=source_token_tuple(row, fields),
                signal_vocab=signal_vocab_tuple(fields),
                declared_layers=declared_layer_tuple(fields),
                pit_asof_terms=pit_asof_tuple(fields),
            )
        )
    return lines


def build_document(md: str, *, generated_at: str) -> dict[str, Any]:
    """完整册（header 计数全部实算，禁把条数写死）。"""
    lines = build_lines(md)
    tiers = {t: sum(1 for ln in lines if ln.tier == t) for t in ("A", "B", "C")}
    token_universe = _dedup([tok for ln in lines for tok in ln.source_tokens])
    ds_universe = _dedup([ds for ln in lines for ds in ln.ds_anchors])
    return {
        "schema_version": SCHEMA_VERSION,
        "registry_id": "REG-METAQ-SOURCE-LINE",
        "domain_ref": "source_line_registry",
        "name_zh": "W4 源线谱机器可读册（入库闸五要素要素1/要素5 命中真源）",
        "ttl": "permanent",
        "status": "active",
        "generated": {
            "by": GENERATOR_ID,
            "at": generated_at,
            "source_md": SOURCE_MD.relative_to(REPO_ROOT).as_posix(),
            "source_md_sha256": hashlib.sha256(md.encode("utf-8")).hexdigest(),
            "note_zh": "机生件禁手改：改册=改 md 真源后重跑生成器（宪法 §9.5）。",
        },
        "counts": {
            "lines": len(lines),
            "tier_A": tiers["A"],
            "tier_B": tiers["B"],
            "tier_C": tiers["C"],
            "ds_anchor_universe": len(ds_universe),
            "source_token_universe": len(token_universe),
        },
        "ds_anchor_universe": ds_universe,
        "source_token_universe": token_universe,
        "lines": [ln.as_entry() for ln in lines],
    }


# ---------------------------------------------------------------------------
# 自校验（逐条对账，全红打印；计数由本器实算）
# ---------------------------------------------------------------------------


def self_check(md: str, doc: dict[str, Any]) -> list[str]:
    """md ↔ 册 逐条对账，返回差异清单（空=全过）。"""
    findings: list[str] = []
    lines = build_lines(md)
    findings += _check_claimed_counts(md, lines)
    findings += _check_summary_vs_detail(md, lines)
    findings += _check_field_completeness(lines)
    findings += _check_vs_section5(md, lines)
    findings += _check_token_coverage(lines)
    findings += _check_doc_consistency(doc, lines)
    return findings


def _check_claimed_counts(md: str, lines: list[SourceLineRow]) -> list[str]:
    """md 自陈条数（§1 总条数 + §2/§3/§4 档位条数）vs 实解析条数。"""
    findings: list[str] = []
    total_claim = _TOTAL_CLAIM_RE.search(md)
    if not total_claim:
        return [f"md §1 自陈条数不可解析（防『对账靶消失=静默放行』）：实解析 {len(lines)} 条"]
    if int(total_claim.group(1)) != len(lines):
        findings.append(f"md §1 自陈 {total_claim.group(1)} 条 ≠ 实解析 {len(lines)} 条")
    claims = {m.group(1): int(m.group(2)) for m in _TIER_CLAIM_RE.finditer(md)}
    for tier in ("A", "B", "C"):
        actual = sum(1 for ln in lines if ln.tier == tier)
        if tier not in claims:
            findings.append(f"md 缺 §{tier} 档自陈条数（对账靶缺失）")
        elif claims[tier] != actual:
            findings.append(f"md 自陈 {tier} 档 {claims[tier]} 条 ≠ 实解析 {actual} 条")
    return findings


def _check_summary_vs_detail(md: str, lines: list[SourceLineRow]) -> list[str]:
    """总表行 ↔ 明细小节：id 集/档位/线名一致，且无孤儿小节。"""
    findings: list[str] = []
    sections = parse_detail_sections(md)
    summary_ids = {ln.line_id for ln in lines}
    for orphan in sorted(set(sections) - summary_ids):
        findings.append(f"明细小节 {orphan} 在 §1 总表无行")
    for line in lines:
        section = sections.get(line.line_id)
        if section is None:
            findings.append(f"{line.line_id} 总表有行但无明细小节")
            continue
        if section["tier"] != line.tier:
            findings.append(f"{line.line_id} 档位不一致：总表 {line.tier} vs 小节 {section['tier']}")
        coverage = _name_reconcilable(line.name, section)
        if coverage < _NAME_COVER_MIN:
            findings.append(
                f"{line.line_id} 线名不可调和：总表 {line.name!r} vs 小节 {section['name']!r}"
                f"（覆盖率 {coverage:.2f} < {_NAME_COVER_MIN}）"
            )
    return findings


_NAME_COVER_MIN: Final = 0.75


def _name_similarity(a: str, b: str) -> float:
    """线名机械可调和度=总表名（可含简称）字符集被「小节全称+小节正文」字符集覆盖的比率。

    md 总表列写简称（如『航运运价 BDI』）、小节写全称（『航运运价线』，正文含 BDI 序列），
    真改名（换语义线）必跌破阈值；逐字等值不在此判据内——全称由 detail_name 全存承担。
    """
    ca, cb = _name_chars(a), _name_chars(b)
    if not ca:
        return 0.0
    return len(ca & cb) / len(ca)


def _name_reconcilable(summary_name: str, section: dict[str, Any]) -> float:
    corpus = section["name"] + " " + " ".join(section["fields"].values())
    return _name_similarity(summary_name, corpus)


def _name_chars(name: str) -> set[str]:
    return {ch for ch in name.lower() if ch.isalnum() or "一" <= ch <= "鿿"}


def _check_field_completeness(lines: list[SourceLineRow]) -> list[str]:
    """档位字段完备性：A/B=U1-U6 全具，C=设计性缺 U2/U3/U4 但必具专用字段。"""
    findings: list[str] = []
    for line in lines:
        present = {k for k in line.fields if _U_KEY_RE.match(k)}
        if line.tier == "C":
            missing = sorted(_C_REQUIRED_FIELDS - set(line.fields))
            if missing:
                findings.append(f"{line.line_id}(C) 缺字段 {missing}")
            extra = sorted(present - {"U1", "U5", "U6"})
            if extra:
                findings.append(f"{line.line_id}(C) 出现设计外 U 字段 {extra}（md 结构漂移）")
            continue
        missing_u = sorted(_REQUIRED_U - present)
        if missing_u:
            findings.append(f"{line.line_id}({line.tier}) 缺 U 字段 {missing_u}")
        if line.tier == "A" and "DS 锚" not in line.fields:
            findings.append(f"{line.line_id}(A) 缺『DS 锚』行（A 档判定依据）")
        if line.tier == "B" and "渠道" not in line.fields:
            findings.append(f"{line.line_id}(B) 缺『渠道』行（B 档判定依据）")
        if not line.freshness or line.freshness == "—":
            findings.append(f"{line.line_id}({line.tier}) 新鲜度为空")
    return findings


def _check_vs_section5(md: str, lines: list[SourceLineRow]) -> list[str]:
    """§5 勾选表：线在册、档位一致、挂接层 ⊆ U5 派生层。"""
    findings: list[str] = []
    by_id = {ln.line_id: ln for ln in lines}
    rows = parse_checklist_table(md)
    if not rows:
        return ["md §5 勾选表不可解析（对账靶消失）"]
    for idx, row in enumerate(rows, start=1):
        line = by_id.get(row["line_id"])
        if line is None:
            findings.append(f"§5 第 {idx} 行 {row['line_id']} 不在源线谱")
            continue
        if row["tier"] != line.tier:
            findings.append(f"§5 {row['line_id']} 档位 {row['tier']} ≠ 谱内 {line.tier}")
        claimed = {f"L{n}" for n in _LAYER_RE.findall(row["layers"])}
        unlisted = sorted(claimed - set(line.declared_layers))
        if unlisted:
            findings.append(f"§5 {row['line_id']} 挂接层 {unlisted} 未在该线 U5 声明")
    return findings


def _check_token_coverage(lines: list[SourceLineRow]) -> list[str]:
    """命中面非空：每线 token 非空；A 档 DS 锚非空；A/B 档信号词与层码非空。

    C 档（无渠道挂起）设计性无信号词/无层码展开（md §5 落选说明+§6.4：C 档不入考试批，
    TPL-U-001 约束"线未上线=该线不展开"）→ 不判红，改由 expansion_eligible=False 表达。
    """
    findings: list[str] = []
    for line in lines:
        if not line.source_tokens:
            findings.append(f"{line.line_id} 无可命中 token 宇宙（要素1 真检必降级）")
        if line.tier == "A" and not line.ds_anchors:
            findings.append(f"{line.line_id}(A) DS 锚为空")
        if line.tier == "B" and not line.source_tokens:
            findings.append(f"{line.line_id}(B) 渠道 token 为空")
        if line.tier in ("A", "B"):
            if not line.signal_vocab:
                findings.append(f"{line.line_id}({line.tier}) U1 无信号词（TPL-U-001 signal 槽无取值域）")
            if not line.declared_layers:
                findings.append(f"{line.line_id}({line.tier}) U5 未点名任何层码")
    return findings


def _check_doc_consistency(doc: dict[str, Any], lines: list[SourceLineRow]) -> list[str]:
    """册内自洽：header 计数=条目实数，universe=条目并集。"""
    findings: list[str] = []
    entries = doc["lines"]
    if doc["counts"]["lines"] != len(entries):
        findings.append(f"counts.lines={doc['counts']['lines']} ≠ 条目数 {len(entries)}")
    for tier in ("A", "B", "C"):
        actual = sum(1 for e in entries if e["tier"] == tier)
        if doc["counts"][f"tier_{tier}"] != actual:
            findings.append(f"counts.tier_{tier}={doc['counts'][f'tier_{tier}']} ≠ 条目实数 {actual}")
    universe = _dedup([t for e in entries for t in e["source_tokens"]])
    if universe != doc["source_token_universe"]:
        findings.append("source_token_universe ≠ 条目 token 并集")
    ds = _dedup([d for e in entries for d in e["ds_anchors"]])
    if ds != doc["ds_anchor_universe"]:
        findings.append("ds_anchor_universe ≠ 条目 DS 锚并集")
    return findings


# ---------------------------------------------------------------------------
# 落盘 / CLI
# ---------------------------------------------------------------------------


def render_yaml(doc: dict[str, Any]) -> str:
    header = (
        f"# [GENERATED] 本文件由 {GENERATOR_ID} 产出，禁手工增删条目（宪法 §9.5 静态清单生成器产出红线）。\n"
        "# 真源=docs/_working/chain_piling_campaign/02_source_line_registry.md（W4 人读册）；"
        "本册是其机器可读视图，单向派生禁反向同步。\n"
        "# 消费方=src/zephyr/governance/meta_question/meta_question_registry.py 五要素机检（要素1 源线可解析 / 要素5 PIT 时戳结构）"
        "+《模板生成器设计》11§2 TPL-U-001 取值域 domain_ref=source_line_registry。\n"
        "# 再生=python scripts/governance/meta_question/wo001_003/generate_source_line_register.py"
        "（--check 只对账不落盘）。\n"
    )
    return header + yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=110)


def write_document(path: Path, text: str, *, expected_base_sha256: str | None) -> None:
    """机生落盘唯一通道：safe_write_text（CAS 基哈希，宪法硬规则 13）。"""
    from zephyr.shared.io.file_utils import safe_write_text

    path.parent.mkdir(parents=True, exist_ok=True)
    result = safe_write_text(path, text, expected_base_sha256=expected_base_sha256)
    if not getattr(result, "ok", True):
        raise RuntimeError(f"safe_write_text 拒写: {result}")


def load_disk_text(path: Path) -> str | None:
    return path.read_text(encoding="utf-8") if path.exists() else None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true", help="只跑对账+盘上漂移检测，不落盘")
    parser.add_argument("--print", dest="print_only", action="store_true", help="YAML 打到 stdout（零写）")
    parser.add_argument("--output", default=str(OUTPUT_YAML), help="产物路径（默认 data/registers/metaq_source_line/）")
    parser.add_argument("--source", default=str(SOURCE_MD), help="真源 md 路径（红腿用例可指向临时副本）")
    args = parser.parse_args(argv)

    try:
        from zephyr.shared.utils.time_utils import now_utc
    except Exception as exc:  # noqa: BLE001  环境异常也要 fail-closed 记红，禁裸抛断生成器
        print(f"[ERROR] time_utils 不可用（禁退化为 datetime.now）：{exc}", file=sys.stderr)
        return EXIT_ERROR

    source = Path(args.source)
    if not source.exists():
        print(f"[ERROR] 真源 md 不存在：{source}", file=sys.stderr)
        return EXIT_ERROR
    md = source.read_text(encoding="utf-8")
    output = Path(args.output)

    try:
        doc = build_document(md, generated_at=now_utc().isoformat())
    except ValueError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return EXIT_ERROR

    findings = self_check(md, doc)
    disk = load_disk_text(output)
    drift_only_check = args.check or args.print_only
    if drift_only_check and disk:
        fresh = yaml.safe_load(disk)
        if fresh and _strip_generated(fresh) != _strip_generated(doc):
            findings.append("盘上册与再生册内容不一致（漂移）：须重跑生成器落地")

    if findings:
        print(f"[RED] W4 册自校验不通过（{len(findings)} 条差异）：")
        for f in findings:
            print(f"  - {f}")
        return EXIT_DRIFT

    text = render_yaml(doc)
    if args.print_only:
        sys.stdout.write(text)
        _print_summary(doc)
        return EXIT_OK
    if args.check:
        print("[GREEN] W4 册自校验全过（对账靶逐条核毕，盘上无漂移）")
        _print_summary(doc)
        return EXIT_OK

    base = hashlib.sha256(disk.encode("utf-8")).hexdigest() if disk else None
    write_document(output, text, expected_base_sha256=base)
    print(f"[GREEN] 已生成 {output.relative_to(REPO_ROOT).as_posix()}（自校验全过）")
    _print_summary(doc)
    return EXIT_OK


def _strip_generated(doc: dict[str, Any]) -> dict[str, Any]:
    clone = json.loads(json.dumps(doc, ensure_ascii=False))
    clone.get("generated", {}).pop("at", None)
    return clone


def _print_summary(doc: dict[str, Any]) -> None:
    counts = doc["counts"]
    print(
        "  线数="
        + str(counts["lines"])
        + f"（A={counts['tier_A']} B={counts['tier_B']} C={counts['tier_C']}）"
        + f" DS锚={counts['ds_anchor_universe']} 命中token={counts['source_token_universe']}"
    )


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
