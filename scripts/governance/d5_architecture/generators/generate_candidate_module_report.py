# [BLUEPRINT] MOD-GOV_GENERATE_CANDIDATE_MODULE_REPORT
# [MODULE] scripts.governance.d5_architecture.generators.generate_candidate_module_report
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""从 candidate_module_registry.yaml 生成候选模块清单报告（分片：索引 + 每域一个文件）

治本(2026-08-01): 单文件 5301 条/3.57MB 卡死 IDE → 按功能域分文件输出。
输出目录: 03_governance_reports/candidate_modules/
  - index.md          索引页（总览统计 + 全景图 + harvest 概览 + 域索引表）
  - {domain}.md       各域候选清单（完整清单表 + 四问卡点分组 + 复查时间表）

[BLUEPRINT] candidate_module_report_generator | .trae/documents/candidate_module_report_generator.md
[MODULE] scripts.governance.d5_architecture.generators.generate_candidate_module_report
[INVARIANTS] 输出幂等(相同输入→相同输出);只读 candidate_module_registry.yaml(规则数据真源);不依赖 depgraph
[MODIFY-GUARD] 修改需通过任务卡
[CONSUMERS] 人工查看 03_governance_reports/candidate_modules/index.md 及各域文件
[STABILITY] evolving
[SAFETY] L
[AI_AUTONOMY] ai_modifiable
[ERROR_CONTRACT] candidate_module_registry.yaml 不存在→exit 1
[TESTS]
[DOMAIN] D_GOV_SCRIPTS
"""

from __future__ import annotations

__manifest__ = """
args: []
description: '从 candidate_module_registry.yaml 生成候选模块清单报告MD文档'
dimensions:
- D5
priority: P2
timeout_seconds: 60
warn_only: false
"""


import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("[ERROR] PyYAML 未安装")
    sys.exit(1)

# sys.path 注入 _GOV_DIR（与同目录其他生成器一致，便于复用 _shared）
_THIS_FILE = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _THIS_FILE.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.module_translation_loader import get_module_translation  # 模块级翻译真源（plain_zh 大白话）

from zephyr.shared.io.paths import REPO_ROOT  # 仓库根真源（SSoT：zephyr.shared.io.paths）

SOURCE_YAML = (
    REPO_ROOT / "docs" / "01_policies_and_standards" / "_registry" / "catalogs" / "candidate_module_registry.yaml"
)
# 分片输出目录（治本 2026-08-01：单文件 3.57MB/5301条卡死 IDE → 按域分文件）
OUTPUT_DIR = REPO_ROOT / "docs" / "02_enterprise_architecture" / "03_governance_reports" / "candidate_modules"
INDEX_PATH = OUTPUT_DIR / "index.md"

# --- 展示用映射 ----------------------------------------------------------

STATUS_LABEL = {
    "deferred": "延后（deferred）",
    "rejected": "否决（rejected）",
    "candidate": "候选待评（candidate）",
    "approved": "已批准（approved）",
    "promoted": "已晋升（promoted）",
}

BLOCKING_LABEL = {
    "q1": "q1 已实现/重复",
    "q2": "q2 无需求驱动",
    "q3": "q3 域已死",
    "q4": "q4 AI 可替代",
    "pending": "待评估",
    "none": "四问全过",
    "": "未标注",
}

# Mermaid 状态着色（classDef 名 = 状态）
STATUS_CLASS = {
    "deferred": "deferred",
    "rejected": "rejected",
    "candidate": "candidate",
    "approved": "approved",
    "promoted": "promoted",
}


def load_candidates() -> list[dict]:
    """从 candidate_module_registry.yaml 加载候选条目。

    Returns:
        list[dict]: entries 列表（每条含 id/name/domain/status/four_question 等字段）

    Raises:
        SystemExit(1): 真源 YAML 不存在
    """
    if not SOURCE_YAML.exists():
        print(f"[ERROR] 真源不存在: {SOURCE_YAML}")
        sys.exit(1)
    with open(SOURCE_YAML, encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return data.get("entries", []) or []


def _mermaid_safe(text: str) -> str:
    """清洗 Mermaid 节点文本中易破坏语法的字符。"""
    if not text:
        return ""
    for ch in ("&", "(", ")", "[", "]", "{", "}", '"', "<", ">", "|"):
        text = text.replace(ch, "")
    return text.strip()


def _short_name(name: str) -> str:
    """取候选名称的中文短称（" / " 分割取末段），清洗 Mermaid 不友好字符。"""
    if not name:
        return ""
    # "Black Swan Pattern Library / 黑天鹅模式库" → "黑天鹅模式库"
    short = name.split(" / ")[-1] if " / " in name else name
    return _mermaid_safe(short)[:24]


def _plain_zh(entry: dict) -> str:
    """取候选模块的大白话解释（plain_zh）。

    真源: module_translation_registry.yaml（通过 module_translation_loader 加载，
    key=候选ID CAND-xxx，HCS-14/Feature-Flag 实践：候选用稳定ID作key非路径）。
    回退: 无翻译时用 problem_it_solves，再无则空串。
    """
    cid = entry.get("id", "")
    trans = get_module_translation(cid) or {}
    plain = trans.get("plain_zh", "")
    if plain:
        return plain
    return entry.get("problem_it_solves", "") or ""


def _node_id(cand_id: str) -> str:
    """候选 ID → Mermaid 合法节点 ID（- → _）。"""
    return cand_id.replace("-", "_")


def _blocking_question(entry: dict) -> str:
    """取四问卡点（blocking_question 字段，空则 '未标注'）。"""
    fq = entry.get("four_question") or {}
    bq = fq.get("blocking_question") or ""
    return bq if bq else ""


def _trigger_summary(entry: dict) -> str:
    """触发信号摘要：首条 + 省略号。"""
    ts = entry.get("trigger_signals") or []
    if not ts:
        return "—"
    first = str(ts[0]).replace("|", "/")
    if len(ts) > 1:
        return f"{first} 等{len(ts)}条"
    return first


def render_frontmatter() -> list[str]:
    """frontmatter（doc_type=audit_report，满足 DCR-003 ttl=permanent）。"""
    return [
        "---",
        "doc_type: audit_report",
        "title: 候选模块清单报告",
        'version: "1.0"',
        "status: active",
        "date: auto-generated",
        "owner: auto-generator",
        "ttl: permanent",
        "---",
        "",
    ]


def render_header(entries: list[dict]) -> list[str]:
    """页头：文档作用 + 生成器 + 数据源声明（标明规则数据，非 depgraph）。"""
    lines = []
    lines.append("# 候选模块清单报告（索引）")
    lines.append("")
    lines.append(
        "> **文档作用 / Purpose**: 展示候选模块登记表中储备的未开发/过度工程候选模块清单，"
        "按状态、四问卡点、优先级、域分类，使其可检索、可定位、可追溯。"
        "与 design_vs_production 互补——后者看已进 depgraph 设计态的待开发模块，本报告看"
        "四问未全过、尚未进入设计态的储备点子。"
    )
    lines.append("")
    lines.append("> 本索引由 generate_candidate_module_report.py 从 candidate_module_registry.yaml 自动生成")
    lines.append("> 最后更新以 git log 为准")
    lines.append(
        "> 数据源: candidate_module_registry.yaml（规则数据真源，TRAE-062：候选库是治理注册表，"
        "真源为 YAML，不进 PostgreSQL。本报告与 03_governance_reports 其他 depgraph 数据源报告不同）"
    )
    lines.append("> 真源文件: docs/01_policies_and_standards/_registry/catalogs/candidate_module_registry.yaml")
    lines.append("")
    lines.append(
        "> **分片结构**（治本 2026-08-01：单文件 5301 条卡死 IDE → 按域分文件）: "
        "本索引含总览统计 + 全景图 + harvest 概览 + 域索引表；"
        "各域候选清单见同目录下 `{域名}.md` 文件。"
    )
    lines.append("")
    return lines


def _count_by(entries: list[dict], key_fn) -> dict[str, int]:
    """统计 entries 按 key_fn 分组的计数（拆出自 render_stats 降圈复杂度 17→11）。"""
    counts: dict[str, int] = {}
    for e in entries:
        k = key_fn(e)
        counts[k] = counts.get(k, 0) + 1
    return counts


def render_stats(entries: list[dict]) -> list[str]:
    """统计概览：总数 + 按状态/四问卡点/优先级分布。"""
    lines = []
    lines.append("## 统计概览")
    lines.append("")

    by_status = _count_by(entries, lambda e: e.get("status", ""))
    by_bq = _count_by(entries, lambda e: _blocking_question(e) or "未标注")
    by_prio = _count_by(entries, lambda e: e.get("priority", "") or "未标注")
    by_domain = _count_by(entries, lambda e: e.get("domain", "") or "未标注")

    lines.append("| 指标 / Metric | 值 / Value |")
    lines.append("|------|-----|")
    lines.append(f"| 候选总数 | {len(entries)} |")
    lines.append(f"| 涉及域数 | {len(by_domain)} |")
    lines.append("")

    lines.append("### 按状态分布")
    lines.append("")
    lines.append("| 状态 / Status | 数量 / Count | 占比 / Ratio |")
    lines.append("|------|:---:|:---:|")
    for s in ("deferred", "rejected", "candidate", "approved", "promoted"):
        cnt = by_status.get(s, 0)
        if cnt == 0:
            continue
        ratio = cnt / len(entries) * 100 if entries else 0
        lines.append(f"| {STATUS_LABEL.get(s, s)} | {cnt} | {ratio:.1f}% |")
    lines.append("")

    lines.append("### 按四问卡点分布")
    lines.append("")
    lines.append("| 卡点 / Blocking | 数量 / Count | 占比 / Ratio |")
    lines.append("|------|:---:|:---:|")
    for bq in ("q1", "q2", "q3", "q4", "pending", "none", "未标注"):
        cnt = by_bq.get(bq, 0)
        if cnt == 0:
            continue
        ratio = cnt / len(entries) * 100 if entries else 0
        lines.append(f"| {BLOCKING_LABEL.get(bq, bq)} | {cnt} | {ratio:.1f}% |")
    lines.append("")

    lines.append("### 按优先级分布")
    lines.append("")
    lines.append("| 优先级 / Priority | 数量 / Count |")
    lines.append("|------|:---:|")
    for p in ("P0", "P1", "P2", "P3", "未标注"):
        cnt = by_prio.get(p, 0)
        if cnt == 0:
            continue
        lines.append(f"| {p} | {cnt} |")
    lines.append("")

    lines.append("### 按域分布")
    lines.append("")
    lines.append("| 域 / Domain | 数量 / Count |")
    lines.append("|------|:---:|")
    for d in sorted(by_domain):
        lines.append(f"| {d} | {by_domain[d]} |")
    lines.append("")
    return lines


def render_status_legend(entries: list[dict]) -> list[str]:
    """状态说明：三态含义 + 数量。"""
    by_status: dict[str, int] = {}
    for e in entries:
        s = e.get("status", "")
        by_status[s] = by_status.get(s, 0) + 1

    lines = []
    lines.append("## 状态说明")
    lines.append("")
    lines.append("| 状态 | 含义 | 数量 |")
    lines.append("|------|------|:---:|")
    lines.append(
        f"| deferred（延后） | 四问未全过但域活着、功能有价值——等触发信号命中再重新过四问晋升到 depgraph 设计态 | {by_status.get('deferred', 0)} |"
    )
    lines.append(f"| rejected（否决） | 四问否决或用户推翻，登记仅为防误重新设计 | {by_status.get('rejected', 0)} |")
    lines.append(f"| candidate（候选待评） | 四问仍在 pending，未拍板 | {by_status.get('candidate', 0)} |")
    lines.append("")
    return lines


def render_mermaid_pie(entries: list[dict]) -> list[str]:
    """Mermaid pie：状态分布。"""
    by_status: dict[str, int] = {}
    for e in entries:
        s = e.get("status", "")
        by_status[s] = by_status.get(s, 0) + 1

    lines = []
    lines.append("## 候选模块全景")
    lines.append("")
    lines.append("### 状态分布")
    lines.append("")
    lines.append("```mermaid")
    lines.append("pie title 候选模块状态分布")
    for s in ("deferred", "rejected", "candidate", "approved", "promoted"):
        cnt = by_status.get(s, 0)
        if cnt == 0:
            continue
        lines.append(f'    "{STATUS_LABEL.get(s, s)}" : {cnt}')
    lines.append("```")
    lines.append("")
    return lines


def render_mermaid_flowchart(entries: list[dict]) -> list[str]:
    """Mermaid flowchart：按四问卡点（受限原因）分组，节点含大白话简述。

    响应需求:全景图一眼看到"每个候选卡在哪问(受限原因)+ 它是干什么的(大白话)"。
    节点文本: 候选ID 中文名 + 大白话简述(截断30字)；颜色=状态。
    """
    # harvest 候选四问全 pending 且数量大，单独在 harvest概览展示；全景图只画原有候选
    non_harvest = [e for e in entries if not str(e.get("id", "")).startswith("CAND-HARVEST")]
    # 按四问卡点分组（受限原因）
    by_bq: dict[str, list[dict]] = {}
    for e in non_harvest:
        bq = _blocking_question(e) or "未标注"
        by_bq.setdefault(bq, []).append(e)

    lines = []
    lines.append("### 按四问卡点分布（受限原因 · 颜色=状态，节点含大白话简述）")
    lines.append("")
    lines.append(f"> 仅展示原有候选 {len(non_harvest)} 条；harvest 候选见下方「Harvest 候选概览」。")
    lines.append("")
    lines.append("```mermaid")
    lines.append("flowchart LR")
    for bq in ("q2", "q1", "q3", "q4", "pending", "none", "未标注"):
        items = by_bq.get(bq, [])
        if not items:
            continue
        label = BLOCKING_LABEL.get(bq, bq)
        gid = f"g_{bq}"
        lines.append(f'  subgraph {gid}["{label}（{len(items)} 条）"]')
        for e in sorted(items, key=lambda x: x.get("id", "")):
            nid = _node_id(e.get("id", ""))
            short = _short_name(e.get("name", ""))
            full_plain = _plain_zh(e)
            plain_short = _mermaid_safe(full_plain)[:30]
            suffix = "…" if len(full_plain) > 30 else ""
            lines.append(f'    {nid}["{e.get("id", "")} {short}<br/>{plain_short}{suffix}"]')
        lines.append("  end")
    # 着色（按状态）
    lines.append("  classDef deferred fill:#fef3c7,stroke:#d97706,color:#000")
    lines.append("  classDef rejected fill:#e5e7eb,stroke:#6b7280,color:#000")
    lines.append("  classDef candidate fill:#dbeafe,stroke:#2563eb,color:#000")
    lines.append("  classDef approved fill:#d1fae5,stroke:#059669,color:#000")
    lines.append("  classDef promoted fill:#ede9fe,stroke:#7c3aed,color:#000")
    for e in non_harvest:
        nid = _node_id(e.get("id", ""))
        cls = STATUS_CLASS.get(e.get("status", ""), "deferred")
        lines.append(f"  class {nid} {cls}")
    lines.append("```")
    lines.append("")
    return lines


def _likely_status(e: dict) -> str:
    """从 tech_notes 解析 harvest 候选的 likely_status。"""
    tn = e.get("tech_notes", "") or ""
    for s in ("likely_new", "likely_implemented", "likely_planned", "likely_misplaced", "uncertain"):
        if f"likely_status={s}" in tn:
            return s
    return "unknown"


def render_harvest_overview(entries: list[dict]) -> list[str]:
    """harvest 候选概览（仅统计，不含清单——清单在各域文件中）。

    治本(2026-08-01): 原 render_harvest_overview 含 5283 行清单表导致单文件 3.57MB 卡死 IDE。
    现索引只保留统计概览，清单移至各域 `{domain}.md` 文件。
    """
    harvest = [e for e in entries if str(e.get("id", "")).startswith("CAND-HARVEST")]
    if not harvest:
        return []
    from collections import Counter

    by_likely = Counter(_likely_status(e) for e in harvest)
    by_dom = Counter(e.get("domain", "") for e in harvest)

    lines = []
    lines.append("## Harvest 候选概览（场外草稿抓取）")
    lines.append("")
    lines.append(f"> 从场外草稿 CSV 抓取的候选，共 {len(harvest)} 条，status=candidate，四问 pending 待评估。")
    lines.append(
        "> 去重四态（区分运营态/设计态）：likely_new(真候选) / likely_implemented(运营态已有) / likely_planned(设计态已有) / likely_misplaced(域错标已校准)。"
    )
    lines.append("> 各域 harvest 候选清单见同目录下对应 `{域名}.md` 文件。")
    lines.append("")
    lines.append("### 按 likely_status 分布")
    lines.append("")
    lines.append("| likely_status | 含义 | 数量 |")
    lines.append("|------|------|:---:|")
    lines.append(f"| likely_new | 该域 depgraph 无 path 命中，疑真候选 | {by_likely.get('likely_new', 0)} |")
    lines.append(
        f"| likely_implemented | 该域**运营态**(stable/generated)path 命中，疑已实现 | {by_likely.get('likely_implemented', 0)} |"
    )
    lines.append(
        f"| likely_planned | 该域**设计态**(planned)path 命中，已在 depgraph 设计管道，勿重复登记 | {by_likely.get('likely_planned', 0)} |"
    )
    lines.append(
        f"| likely_misplaced | 含 infra 通用词且域错标，已校准到 D_INFRA_RUNTIME | {by_likely.get('likely_misplaced', 0)} |"
    )
    lines.append(f"| uncertain | 无法提取关键词（如纯中文能力名），待人工判定 | {by_likely.get('uncertain', 0)} |")
    lines.append("")
    lines.append("### 按域分布（含域校准结果）")
    lines.append("")
    lines.append("| 域 | 数量 |")
    lines.append("|------|:---:|")
    for dom, cnt in by_dom.most_common():
        lines.append(f"| [{dom}]({dom}.md) | {cnt} |")
    lines.append("")
    return lines


def render_domain_index(entries: list[dict]) -> list[str]:
    """域索引表：每域一行，含候选数 + harvest 数 + 链接到域文件。"""
    from collections import Counter

    by_dom = Counter(e.get("domain", "") or "未标注" for e in entries)
    harvest_by_dom = Counter(
        e.get("domain", "") or "未标注" for e in entries if str(e.get("id", "")).startswith("CAND-HARVEST")
    )

    lines = []
    lines.append("## 域索引")
    lines.append("")
    lines.append("> 点击域名跳转到该域的候选清单文件。")
    lines.append("")
    lines.append("| 域 / Domain | 候选总数 | 其中 harvest | 域文件 |")
    lines.append("|------|:---:|:---:|------|")
    for dom, cnt in by_dom.most_common():
        hcnt = harvest_by_dom.get(dom, 0)
        lines.append(f"| {dom} | {cnt} | {hcnt} | [{dom}.md]({dom}.md) |")
    lines.append("")
    return lines


def render_full_table(entries: list[dict]) -> list[str]:
    """完整清单表：18条核心字段。"""
    lines = []
    lines.append("## 完整清单")
    lines.append("")
    lines.append("| ID | 名称 / Name | 大白话（干什么用） | 域 | 状态 | 四问卡点 | 优先级 | 触发信号摘要 | 下次复查 |")
    lines.append("|------|------|------|------|------|------|:---:|------|------|")
    # 按状态（deferred→candidate→rejected）再按 id 排序，让"可能开发"的排前面
    status_order = {"candidate": 0, "deferred": 1, "approved": 2, "promoted": 3, "rejected": 4}

    def _sort_key(e: dict) -> tuple:
        return (status_order.get(e.get("status", ""), 9), e.get("id", ""))

    for e in sorted(entries, key=_sort_key):
        cid = e.get("id", "")
        name = e.get("name", "")
        domain = e.get("domain", "")
        status = STATUS_LABEL.get(e.get("status", ""), e.get("status", ""))
        bq = BLOCKING_LABEL.get(_blocking_question(e), _blocking_question(e) or "未标注")
        prio = e.get("priority", "") or "—"
        trigger = _trigger_summary(e)
        review = e.get("next_review_date", "") or "—"
        # 名称/大白话里的 | 会破坏表格，替换
        safe_name = name.replace("|", "/")
        plain = _plain_zh(e).replace("|", "/")
        lines.append(f"| {cid} | {safe_name} | {plain} | {domain} | {status} | {bq} | {prio} | {trigger} | {review} |")
    lines.append("")
    return lines


def render_by_blocking(entries: list[dict]) -> list[str]:
    """按四问卡点分组，列条目 + 卡点理由（让读者明白为什么没开发）。"""
    lines = []
    lines.append("## 按四问卡点分组（为什么没开发）")
    lines.append("")
    lines.append(
        "> 四问过滤：q1已实现 / q2需求驱动 / q3域活着 / q4 AI替代。任一问「否」即不进 depgraph 设计态，登记在候选库。"
    )
    lines.append("")

    groups: dict[str, list[dict]] = {}
    for e in entries:
        bq = _blocking_question(e) or "未标注"
        groups.setdefault(bq, []).append(e)

    for bq in ("q1", "q2", "q3", "q4", "pending", "none", "未标注"):
        items = groups.get(bq, [])
        if not items:
            continue
        label = BLOCKING_LABEL.get(bq, bq)
        lines.append(f"### {label}（{len(items)} 条）")
        lines.append("")
        lines.append("| ID | 名称 | 大白话（干什么用） | 域 | 卡点理由 | 替代方案 |")
        lines.append("|------|------|------|------|------|------|")
        for e in sorted(items, key=lambda x: x.get("id", "")):
            cid = e.get("id", "")
            name = (e.get("name", "") or "").replace("|", "/")
            plain = _plain_zh(e).replace("|", "/")
            domain = e.get("domain", "")
            fq = e.get("four_question") or {}
            # 卡点理由：取 blocking_question 对应 q 的 evidence，无则 last_review_outcome
            bq_evidence = ""
            if bq in ("q1", "q2", "q3", "q4"):
                qkey = f"q{bq[-1]}" if bq.startswith("q") else bq
                qobj = fq.get(qkey, {}) or {}
                bq_evidence = (qobj.get("evidence") or "").replace("|", "/")
            if not bq_evidence:
                bq_evidence = (e.get("last_review_outcome") or "").replace("|", "/")
            alt = (e.get("alternatives") or "").replace("|", "/")
            lines.append(f"| {cid} | {name} | {plain} | {domain} | {bq_evidence} | {alt} |")
        lines.append("")
    return lines


def render_review_schedule(entries: list[dict]) -> list[str]:
    """复查时间表：按 next_review_date 升序。"""
    lines = []
    lines.append("## 复查时间表")
    lines.append("")
    lines.append("> 按 next_review_date 升序。复查时重新过四问，触发信号命中则晋升到 depgraph 设计态。")
    lines.append("")
    lines.append("| 下次复查 | 复查频率 | ID | 名称 | 域 | 状态 | 上次复查结论 |")
    lines.append("|------|------|------|------|------|------|------|")
    reviewed = [e for e in entries if e.get("next_review_date")]
    for e in sorted(reviewed, key=lambda x: x.get("next_review_date", "")):
        nr = e.get("next_review_date", "")
        freq = e.get("review_frequency", "") or "—"
        cid = e.get("id", "")
        name = (e.get("name", "") or "").replace("|", "/")
        domain = e.get("domain", "")
        status = STATUS_LABEL.get(e.get("status", ""), e.get("status", ""))
        outcome = (e.get("last_review_outcome") or "").replace("|", "/")
        lines.append(f"| {nr} | {freq} | {cid} | {name} | {domain} | {status} | {outcome} |")
    lines.append("")
    return lines


def generate_index(entries: list[dict]) -> str:
    """生成索引页：总览统计 + 全景图 + harvest 概览 + 域索引表。

    治本(2026-08-01): 单文件 5301 条卡死 IDE → 索引只含统计/全景图/域索引，
    各域候选清单移至 `{domain}.md` 文件。
    """
    lines: list[str] = []
    lines.extend(render_frontmatter())
    lines.extend(render_header(entries))
    lines.extend(render_stats(entries))
    lines.extend(render_status_legend(entries))
    lines.extend(render_mermaid_pie(entries))
    lines.extend(render_mermaid_flowchart(entries))
    lines.extend(render_harvest_overview(entries))
    lines.extend(render_domain_index(entries))
    return "\n".join(lines)


def _render_domain_header(domain: str, dom_entries: list[dict]) -> list[str]:
    """域文件页头：域名 + 候选数 + 返回索引链接。"""
    from collections import Counter

    harvest_cnt = sum(1 for e in dom_entries if str(e.get("id", "")).startswith("CAND-HARVEST"))
    non_harvest_cnt = len(dom_entries) - harvest_cnt
    by_likely = Counter(_likely_status(e) for e in dom_entries if str(e.get("id", "")).startswith("CAND-HARVEST"))

    lines = []
    lines.append("---")
    lines.append("doc_type: audit_report")
    lines.append(f"title: 候选模块清单 — {domain}")
    lines.append('version: "1.0"')
    lines.append("status: active")
    lines.append("date: auto-generated")
    lines.append("owner: auto-generator")
    lines.append("ttl: permanent")
    lines.append("---")
    lines.append("")
    lines.append(f"# {domain} 候选模块清单")
    lines.append("")
    lines.append("> [← 返回索引](index.md)")
    lines.append("")
    lines.append(f"> 本域候选 **{len(dom_entries)}** 条（原有 {non_harvest_cnt} + harvest {harvest_cnt}）。")
    if harvest_cnt > 0:
        parts = []
        for s in ("likely_new", "likely_implemented", "likely_planned", "likely_misplaced", "uncertain"):
            c = by_likely.get(s, 0)
            if c:
                parts.append(f"{s}={c}")
        if parts:
            lines.append(f"> harvest 去重四态: {' / '.join(parts)}")
    lines.append("")
    return lines


def generate_domain_file(domain: str, dom_entries: list[dict]) -> str:
    """生成单个域的候选清单 MD 文件。

    复用 render_full_table / render_by_blocking / render_review_schedule，
    传入域过滤后的 entries 即可。
    """
    lines: list[str] = []
    lines.extend(_render_domain_header(domain, dom_entries))
    lines.extend(render_full_table(dom_entries))
    lines.extend(render_by_blocking(dom_entries))
    lines.extend(render_review_schedule(dom_entries))
    return "\n".join(lines)


def main() -> None:
    """入口：生成候选模块清单报告（分片：索引 + 每域一个文件）。"""
    entries = load_candidates()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 清理旧的单文件（如存在）
    old_single = OUTPUT_DIR.parent / "candidate_module_report.md"
    if old_single.exists():
        old_single.unlink()

    # 1. 生成索引
    index_content = generate_index(entries)
    INDEX_PATH.write_text(index_content, encoding="utf-8", newline="\n")
    print(f"[OK] 索引 {INDEX_PATH.name} ({len(index_content)} 字符)")

    # 2. 按域分文件
    from collections import defaultdict

    by_domain: dict[str, list[dict]] = defaultdict(list)
    for e in entries:
        dom = e.get("domain", "") or "未标注"
        by_domain[dom].append(e)

    for dom, dom_entries in sorted(by_domain.items()):
        content = generate_domain_file(dom, dom_entries)
        out_path = OUTPUT_DIR / f"{dom}.md"
        out_path.write_text(content, encoding="utf-8", newline="\n")
        harvest_cnt = sum(1 for e in dom_entries if str(e.get("id", "")).startswith("CAND-HARVEST"))
        print(f"[OK] {dom}.md ({len(dom_entries)} 条, harvest {harvest_cnt}, {len(content)} 字符)")

    print(f"\n[DONE] 共 {len(entries)} 条候选 → 索引 1 + 域文件 {len(by_domain)} 个")


if __name__ == "__main__":
    main()
