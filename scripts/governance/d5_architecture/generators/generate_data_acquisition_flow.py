# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md | §acquisition-flow
# [MODULE] scripts.governance.d5_architecture.generators.generate_data_acquisition_flow
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] _common (DB_DISPLAY_NAME)
# [CONSUMERS] CI自动触发;人工查看generated/dataflows/data_acquisition_flow.md
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 输出幂等(相同输入→相同输出);只读data_acquisition_matrix.md;输出到05_dataflow_architecture/
# [MODIFY-GUARD] 修改需通过MOD-L00-004任务或后续维护任务
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 输入MD不存在→exit 1;矩阵明细为空→exit 2
# [TESTS]
# [TTL] permanent
"""G-acqflow: 从 data_acquisition_matrix.md 生成业务数据采集流图 MD（内嵌 Mermaid）

依据：与 generate_dataflow_diagram.py 正交——后者画"运行时业务系统流"（tick→因子→订单），
本生成器画"数据采集流"（外部源→采集Job→业务数据库表），互补关系。

功能：
  - 解析 data_acquisition_matrix.md 的"矩阵明细"表（61 任务 × 表 × 源 × 调度 × 行数 × 日期 × 状态）
  - 生成 3 张 Mermaid 图（按数据源 / 按调度时段 / 按数据库分组）
  - 自动判定数据新鲜度（基于最新日期 vs 运行日期）
  - 输出交叉矩阵（数据源×调度时段、数据源×状态、库×状态）+ 完整表清单

输出文件：
  - docs/02_enterprise_architecture/05_dataflow_architecture/data_acquisition_flow.md

真源链：
  data_acquisition_matrix.md（人类+扫描器维护）
    → 本生成器解析
    → data_acquisition_flow.md（自动派生产物，禁止手工编辑）

用法
----
    python scripts/governance/d5_architecture/generators/generate_data_acquisition_flow.py
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path

# 添加项目根到 sys.path（对齐 generate_dataflow_diagram.py）
_REPO_ROOT = Path(__file__).resolve().parents[4]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

try:
    from _common import DB_DISPLAY_NAME  # noqa: E402
except ImportError:
    DB_DISPLAY_NAME = "PostgreSQL depgraph"

__manifest__ = """
args: []
description: 'G-acqflow: 从 data_acquisition_matrix.md 生成业务数据采集流图 MD（内嵌 Mermaid）'
dimensions:
- D5
priority: P2
timeout_seconds: 60
warn_only: false
"""

INPUT_PATH = _REPO_ROOT / "docs" / "03_modules" / "_domain_data" / "data_acquisition_matrix.md"
OUTPUT_PATH = (
    _REPO_ROOT / "docs" / "02_enterprise_architecture" / "05_dataflow_architecture" / "data_acquisition_flow.md"
)
# tasks.yaml 真源：用于 task_id → 中文描述映射（Mermaid Job 节点双语 label）
TASKS_YAML = _REPO_ROOT / "src" / "zephyr" / "data" / "config" / "tasks.yaml"

# ============================================================
# 中文术语映射
# ============================================================
_SOURCE_ZH: dict[str, str] = {
    "ifind": "同花顺iFind",
    "miniqmt": "迅投QMT",
    "akshare": "AKShare",
    "baostock": "BaoStock",
    "tickflow": "TickFlow",
    "tushare": "Tushare",
    "rss": "RSS",
    "tdx": "通达信",
    "bdpan": "百度云",
}

_SLOT_ZH: dict[str, str] = {
    "盘后日K(16:30)": "盘后日K / 16:30 周一-五 (Post-close Daily K)",
    "盘后资金(17:00)": "盘后资金 / 17:00 周一-五 (Post-close Capital)",
    "盘后事件(18:00)": "盘后事件 / 18:00 周一-五 (Post-close Event)",
    "周末财务(周六10:00)": "周末财务 / 10:00 周六 (Weekend Financial)",
    "静态数据(月初09:00)": "静态数据 / 09:00 月初 (Static Data)",
}

# 状态中文
_STATUS_ZH: dict[str, str] = {
    "✅ 已配置定时": "已配置定时 / Scheduled",
    "🔴 已禁用": "已禁用 / Disabled",
    "🔵 待接入(空表)": "待接入(空表) / Pending",
}

# 矩阵明细表格行正则（8 列：#/task_id/表名/数据源/调度时段/行数/最新日期/状态）
_TABLE_ROW = re.compile(
    r"^\|\s*(\d+)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|"
    r"\s*([^|]*?)\s*\|\s*([^|]*?)\s*\|\s*([^|]+?)\s*\|$"
)


# ============================================================
# 解析
# ============================================================
def _parse_rows(md_text: str) -> list[dict]:
    """解析 data_acquisition_matrix.md 的"矩阵明细"表。

    Returns:
        list[dict]: 每行 {idx, task_id, table, source, slot, rows, latest, status}
    """
    rows: list[dict] = []
    in_table = False
    for line in md_text.splitlines():
        if line.startswith("## 矩阵明细"):
            in_table = True
            continue
        if in_table and line.startswith("## "):
            break  # 进入下一节
        if not in_table:
            continue
        m = _TABLE_ROW.match(line)
        if not m:
            continue
        idx, task_id, table, source, slot, rows_str, latest, status = m.groups()
        rows.append(
            {
                "idx": int(idx),
                "task_id": task_id.strip(),
                "table": table.strip(),
                "source": source.strip(),
                "slot": slot.strip(),
                "rows": rows_str.strip(),
                "latest": latest.strip(),
                "status": status.strip(),
            }
        )
    return rows


def _parse_row_count(s: str) -> int | None:
    """解析行数字符串为 int。N/A 或空返回 None。"""
    s = s.strip()
    if not s or s.upper() == "N/A":
        return None
    s = s.replace(",", "")
    try:
        return int(s)
    except ValueError:
        return None


def _fmt_rows(n: int | None) -> str:
    """行数格式化（万/亿为单位）。None 返回 '-'。"""
    if n is None:
        return "-"
    if n < 10000:
        return str(n)
    if n < 100_000_000:  # < 1亿
        return f"{n / 10000:.1f}万"
    return f"{n / 100_000_000:.2f}亿"


def _fmt_rows_en(n: int | None) -> str:
    """行数英文格式化（rows/K rows/M rows）。None 返回 '-'。

    阈值对齐中文万/亿体系：< 10K → 原数字；10K-1M → X.XXK；≥ 1M → X.XXXM。
    """
    if n is None:
        return "-"
    if n < 10000:
        return f"{n} rows"
    if n < 1_000_000:
        return f"{n / 1000:.2f}K rows"
    return f"{n / 1_000_000:.3f}M rows"


def _freshness(latest: str, today: date) -> tuple[str, str]:
    """判定数据新鲜度。返回 (图标, 文字描述)。"""
    if not latest:
        return "⚫", "未知(无日期)"
    try:
        d = datetime.strptime(latest, "%Y-%m-%d").date()
    except ValueError:
        return "⚫", f"日期格式异常({latest})"
    delta = (today - d).days
    if delta <= 1:
        return "🟢", f"当日({delta}天)"
    if delta <= 3:
        return "🟡", f"滞后{delta}天"
    if delta <= 7:
        return "🟠", f"滞后{delta}天"
    return "🔴", f"滞后{delta}天"


def _table_id(table: str) -> str:
    """表名转 Mermaid 合法节点 ID（c1_market.adj_factor → T_c1_market_adj_factor）。"""
    return "T_" + re.sub(r"[^a-zA-Z0-9_]", "_", table)


def _db_of(table: str) -> str:
    """表名 → 数据库名（c1_market.xxx → c1_market）。"""
    return table.split(".", 1)[0] if "." in table else "unknown"


def _en_zh(en: str, mapping: dict[str, str]) -> str:
    """英文 + 中文并列。无映射返回原值。"""
    zh = mapping.get(en, "")
    return f"{en} / {zh}" if zh else en


# 匹配末尾的括号技术备注（全角（）或半角()，内容不含嵌套括号）
_TRAILING_PAREN = re.compile(r"[（(][^（）()]*[)）]\s*$")


def _strip_tech_note(desc: str) -> str:
    """去除 description 末尾的技术备注括号内容，保留有意义的中文描述。

    例："复权因子增量（miniQMT get_divid_factors）" → "复权因子增量"
        "每日估值（PE/PB）增量（AKShare stock_zh_valuation_baidu）" → "每日估值（PE/PB）增量"
    """
    if not desc:
        return ""
    return _TRAILING_PAREN.sub("", desc).strip()


def _extract_desc_from_task(task: dict) -> str:
    """从单个 task dict 中提取 description，兼容 extra/policy/顶层三种位置。"""
    extra = task.get("extra") or {}
    if isinstance(extra, dict) and extra.get("description"):
        return str(extra["description"])
    policy = task.get("policy") or {}
    if isinstance(policy, dict) and policy.get("description"):
        return str(policy["description"])
    if task.get("description"):
        return str(task["description"])
    return ""


def _load_task_descriptions() -> dict[str, str]:
    """解析 tasks.yaml，返回 task_id → 中文描述（已去除末尾技术备注括号）。

    description 字段兼容两种位置：extra.description（当前真源）与 policy.description（向后兼容）。
    文件缺失或 PyYAML 不可用时返回空 dict（调用方按取不到处理：Job 节点只显示 task_id）。
    """
    try:
        import yaml  # type: ignore[import-untyped]
    except ImportError:
        return {}
    if not TASKS_YAML.exists():
        return {}
    try:
        data = yaml.safe_load(TASKS_YAML.read_text(encoding="utf-8"))
    except Exception:
        return {}
    if not isinstance(data, dict):
        return {}
    result: dict[str, str] = {}
    for task in data.get("tasks", []) or []:
        if not isinstance(task, dict):
            continue
        task_id = task.get("task_id")
        if not task_id:
            continue
        desc = _extract_desc_from_task(task)
        result[str(task_id)] = _strip_tech_note(desc)
    return result


# ============================================================
# Mermaid 图生成
# ============================================================
def _gen_mermaid_by_source(
    rows: list[dict], today: date, task_descs: dict[str, str] | None = None
) -> tuple[str, int, int, int]:
    """按数据源分组的 Mermaid 图（subgraph 按源，Job → 表节点）。"""
    task_descs = task_descs or {}
    lines = ["flowchart LR"]

    # 按数据源分组
    by_source: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        by_source[r["source"]].append(r)

    # 收集所有唯一表（同表多任务汇聚）
    tables_seen: dict[str, dict] = {}
    for r in rows:
        if r["table"] not in tables_seen:
            tables_seen[r["table"]] = {
                "rows": _parse_row_count(r["rows"]),
                "latest": r["latest"],
                "fresh_icon": _freshness(r["latest"], today)[0],
            }

    # 数据源 subgraph + Job 节点
    for src in sorted(by_source.keys()):
        src_zh = _SOURCE_ZH.get(src, src)
        src_rows = by_source[src]
        lines.append(f'    subgraph S_{src}["{src_zh}（{len(src_rows)} 任务 / {len(src_rows)} tasks）"]')
        for r in src_rows:
            desc = task_descs.get(r["task_id"], "")
            job_label = f'{r["task_id"]}<br/>{desc}' if desc else r["task_id"]
            lines.append(f'        J{r["idx"]}["{job_label}"]:::jobNode')
        lines.append("    end")

    # 表节点（按数据库分组）
    by_db: dict[str, list[str]] = defaultdict(list)
    for t in tables_seen:
        by_db[_db_of(t)].append(t)
    for db in sorted(by_db.keys()):
        lines.append(f'    subgraph DB_{db}["{db}（{len(by_db[db])} 表 / {len(by_db[db])} tables）"]')
        for t in sorted(by_db[db]):
            info = tables_seen[t]
            rows_str = _fmt_rows(info["rows"])
            rows_en = _fmt_rows_en(info["rows"])
            label = f'{info["fresh_icon"]} {t}<br/>{rows_str}行 / {rows_en}'
            if info["latest"]:
                label += f'<br/>{info["latest"]}'
            lines.append(f'        {_table_id(t)}["{label}"]:::dsNode')
        lines.append("    end")

    # Job → 表 边
    edge_count = 0
    for r in rows:
        lines.append(f'    J{r["idx"]} --> {_table_id(r["table"])}')
        edge_count += 1

    # 样式
    lines.append("")
    lines.append("    classDef jobNode fill:#c8e6c9,stroke:#2e7d32,stroke-width:2px,color:#1b5e20")
    lines.append("    classDef dsNode fill:#bbdefb,stroke:#1565c0,stroke-width:2px,color:#0d47a1")

    return "\n".join(lines) + "\n", len(by_source), len(tables_seen), edge_count


def _gen_mermaid_by_slot(
    rows: list[dict], today: date, task_descs: dict[str, str] | None = None
) -> tuple[str, int, int]:
    """按调度时段分组的 Mermaid 图（subgraph 按时段，Job → 表节点）。"""
    task_descs = task_descs or {}
    lines = ["flowchart LR"]

    by_slot: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        by_slot[r["slot"]].append(r)

    # 调度时段 subgraph + Job 节点
    for slot in sorted(by_slot.keys()):
        slot_zh = _SLOT_ZH.get(slot, slot)
        slot_rows = by_slot[slot]
        # subgraph ID 不能含特殊字符
        slot_id = "SL_" + re.sub(r"[^a-zA-Z0-9_]", "_", slot)
        lines.append(f'    subgraph {slot_id}["{slot_zh}（{len(slot_rows)} 任务 / {len(slot_rows)} tasks）"]')
        for r in slot_rows:
            desc = task_descs.get(r["task_id"], "")
            job_label = f'{r["task_id"]}<br/>{desc}' if desc else r["task_id"]
            lines.append(f'        J{r["idx"]}["{job_label}"]:::jobNode')
        lines.append("    end")

    # 表节点（扁平，不分组，避免图过密）
    tables_seen: set[str] = set()
    for r in rows:
        if r["table"] not in tables_seen:
            tables_seen.add(r["table"])
            info_rows = _parse_row_count(r["rows"])
            icon = _freshness(r["latest"], today)[0]
            label = f'{icon} {r["table"]}<br/>{_fmt_rows(info_rows)}行 / {_fmt_rows_en(info_rows)}'
            if r["latest"]:
                label += f'<br/>{r["latest"]}'
            lines.append(f'    {_table_id(r["table"])}["{label}"]:::dsNode')

    # Job → 表 边
    edge_count = 0
    for r in rows:
        lines.append(f'    J{r["idx"]} --> {_table_id(r["table"])}')
        edge_count += 1

    lines.append("")
    lines.append("    classDef jobNode fill:#fff9c4,stroke:#f9a825,stroke-width:2px,color:#f57f17")
    lines.append("    classDef dsNode fill:#bbdefb,stroke:#1565c0,stroke-width:2px,color:#0d47a1")

    return "\n".join(lines) + "\n", len(by_slot), edge_count


def _gen_mermaid_by_db(rows: list[dict], today: date) -> tuple[str, int, int]:
    """按数据库分组的 Mermaid 图（subgraph 按库，表节点按库分组，标注数据源）。"""
    lines = ["flowchart LR"]

    by_db: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        by_db[_db_of(r["table"])].append(r)

    # 外部数据源节点（左侧）
    sources_seen = sorted({r["source"] for r in rows})
    for src in sources_seen:
        src_zh = _SOURCE_ZH.get(src, src)
        lines.append(f'    SRC_{src}[("{src_zh}")]:::srcNode')

    # 数据库 subgraph + 表节点
    for db in sorted(by_db.keys()):
        db_rows = by_db[db]
        # 唯一表
        tables_in_db: dict[str, set[str]] = defaultdict(set)
        for r in db_rows:
            tables_in_db[r["table"]].add(r["source"])
        lines.append(f'    subgraph DB_{db}["{db}（{len(tables_in_db)} 表 / {len(tables_in_db)} tables）"]')
        for t in sorted(tables_in_db.keys()):
            # 取该表的代表行（第一个）用于行数/日期
            rep = next(r for r in db_rows if r["table"] == t)
            info_rows = _parse_row_count(rep["rows"])
            icon = _freshness(rep["latest"], today)[0]
            srcs = "/".join(sorted(tables_in_db[t]))
            label = f'{icon} {t}<br/>{_fmt_rows(info_rows)}行 / {_fmt_rows_en(info_rows)}<br/>源: {srcs}'
            if rep["latest"]:
                label += f'<br/>{rep["latest"]}'
            lines.append(f'        {_table_id(t)}["{label}"]:::dsNode')
        lines.append("    end")

    # 数据源 → 表 边（去重：同一 源→表 只画一次）
    edges_seen: set[tuple[str, str]] = set()
    edge_count = 0
    for r in rows:
        key = (r["source"], r["table"])
        if key in edges_seen:
            continue
        edges_seen.add(key)
        lines.append(f'    SRC_{r["source"]} --> {_table_id(r["table"])}')
        edge_count += 1

    lines.append("")
    lines.append("    classDef srcNode fill:#ffcdd2,stroke:#c62828,stroke-width:2px,color:#b71c1c")
    lines.append("    classDef dsNode fill:#bbdefb,stroke:#1565c0,stroke-width:2px,color:#0d47a1")

    return "\n".join(lines) + "\n", len(by_db), edge_count


# ============================================================
# 交叉矩阵
# ============================================================
def _gen_cross_source_slot(rows: list[dict]) -> str:
    """数据源 × 调度时段 交叉矩阵。"""
    by_pair: dict[tuple[str, str], int] = defaultdict(int)
    for r in rows:
        by_pair[(r["source"], r["slot"])] += 1
    sources = sorted({r["source"] for r in rows})
    slots = sorted({r["slot"] for r in rows})

    lines = []
    header = "| 数据源 \\ 调度时段 | " + " | ".join(_SLOT_ZH.get(s, s) for s in slots) + " | 合计 |"
    sep = "|" + "---|" * (len(slots) + 2)
    lines.append(header)
    lines.append(sep)
    for src in sources:
        src_zh = _SOURCE_ZH.get(src, src)
        counts = [by_pair.get((src, s), 0) for s in slots]
        total = sum(counts)
        cells = " | ".join(str(c) if c > 0 else "-" for c in counts)
        lines.append(f"| {src_zh} | {cells} | {total} |")
    # 合计行
    col_totals = [sum(by_pair.get((src, s), 0) for src in sources) for s in slots]
    cells = " | ".join(str(c) for c in col_totals)
    lines.append(f"| **合计** | {cells} | **{len(rows)}** |")
    return "\n".join(lines) + "\n"


def _gen_source_status(rows: list[dict]) -> str:
    """数据源 × 状态 统计表。"""
    by_pair: dict[tuple[str, str], int] = defaultdict(int)
    for r in rows:
        by_pair[(r["source"], r["status"])] += 1
    sources = sorted({r["source"] for r in rows})
    statuses = ["✅ 已配置定时", "🔴 已禁用", "🔵 待接入(空表)"]

    lines = []
    header = "| 数据源 / Source | " + " | ".join(_STATUS_ZH[s] for s in statuses) + " | 合计 / Total |"
    sep = "|" + "---|" * (len(statuses) + 2)
    lines.append(header)
    lines.append(sep)
    for src in sources:
        src_zh = _SOURCE_ZH.get(src, src)
        counts = [by_pair.get((src, s), 0) for s in statuses]
        total = sum(counts)
        cells = " | ".join(str(c) if c > 0 else "-" for c in counts)
        lines.append(f"| {src_zh} | {cells} | {total} |")
    return "\n".join(lines) + "\n"


# ============================================================
# 主文档生成
# ============================================================
def _gen_index_md(rows: list[dict], today: date, gen_timestamp: str) -> str:
    """生成完整 MD 文档。

    Args:
        rows: 解析后的矩阵行。
        today: 运行日期（用于新鲜度判定）。
        gen_timestamp: 生成时间戳（从输入文件 mtime 派生，保证幂等：输入不变→输出时间戳不变）。
    """
    # task_id → 中文描述映射（来自 tasks.yaml，用于 Mermaid Job 节点双语 label）
    task_descs = _load_task_descriptions()

    # 统计
    total = len(rows)
    by_status: dict[str, int] = defaultdict(int)
    by_source: dict[str, int] = defaultdict(int)
    by_slot: dict[str, int] = defaultdict(int)
    by_db: dict[str, int] = defaultdict(int)
    unique_tables: set[str] = set()
    for r in rows:
        by_status[r["status"]] += 1
        by_source[r["source"]] += 1
        by_slot[r["slot"]] += 1
        by_db[_db_of(r["table"])] += 1
        unique_tables.add(r["table"])

    # 新鲜度统计
    fresh_counts: dict[str, int] = defaultdict(int)
    for r in rows:
        icon, _ = _freshness(r["latest"], today)
        fresh_counts[icon] += 1

    lines = []
    # frontmatter
    lines.append("---")
    lines.append("doc_type: architecture_view")
    lines.append("title: 业务数据采集流图 / Data Acquisition Flow")
    lines.append('version: "1.0"')
    lines.append("status: active")
    lines.append(f"date: {today.isoformat()}")
    lines.append("owner: auto-generator")
    lines.append("ttl: permanent")
    lines.append("---")
    lines.append("")
    lines.append("# 业务数据采集流图 / Data Acquisition Flow")
    lines.append("")
    lines.append(f"> 生成时间: {gen_timestamp}")
    lines.append(f"> 运行日期: {today.isoformat()}")
    lines.append(f"> 输入真源: `docs/03_modules/_domain_data/data_acquisition_matrix.md`（人类+扫描器维护）")
    lines.append(f"> 输出: 本文档（自动派生产物，禁止手工编辑）")
    lines.append("")
    lines.append("## 概述 / Overview")
    lines.append("")
    lines.append("本文档展示**业务数据库表的数据采集流**——即外部数据源通过哪个采集 Job 把数据灌进哪张业务表。")
    lines.append("")
    lines.append("This document presents the **data acquisition flow of business database tables** — i.e., which external data source feeds which business table through which acquisition Job.")
    lines.append("")
    lines.append("**与 [dataflow_index.md](dataflow_index.md) 的关系 / Relationship with dataflow_index.md**：")
    lines.append("- `dataflow_index.md` 画**运行时业务系统流**（tick → K线 → 因子 → 信号 → 订单 → 成交 → 持仓） / draws the **runtime business system flow** (tick → K-line → factor → signal → order → trade → position)")
    lines.append("- 本文档画**数据采集流**（iFind/QMT/AKShare 等 → 采集 Job → ClickHouse 业务表） / this document draws the **data acquisition flow** (iFind/QMT/AKShare etc. → acquisition Job → ClickHouse business tables)")
    lines.append("- 两者正交互补，共同构成数据全景。 / The two are orthogonal and complementary, together forming the full data landscape.")
    lines.append("")
    lines.append("## 统计概览 / Statistics Overview")
    lines.append("")
    lines.append("| 指标 / Metric | 值 / Value |")
    lines.append("|------|-----|")
    lines.append(f"| 采集任务总数 / Total Tasks | {total} |")
    lines.append(f"| 唯一业务表数 / Unique Tables | {len(unique_tables)} |")
    lines.append(f"| 数据源数 / Data Sources | {len(by_source)} |")
    lines.append(f"| 调度时段数 / Schedule Slots | {len(by_slot)} |")
    lines.append(f"| 数据库数 / Databases | {len(by_db)} |")
    lines.append("")
    lines.append("### 按状态统计 / By Status")
    lines.append("")
    lines.append("| 状态 / Status | 任务数 / Tasks | 占比 / Ratio |")
    lines.append("|------|--------|------|")
    for s in ["✅ 已配置定时", "🔴 已禁用", "🔵 待接入(空表)"]:
        c = by_status.get(s, 0)
        pct = f"{c / total * 100:.1f}%" if total > 0 else "0%"
        lines.append(f"| {_STATUS_ZH[s]} | {c} | {pct} |")
    lines.append("")
    lines.append("### 按数据源统计 / By Data Source")
    lines.append("")
    lines.append("| 数据源 / Source | 任务数 / Tasks | 占比 / Ratio |")
    lines.append("|--------|--------|------|")
    for src in sorted(by_source.keys()):
        c = by_source[src]
        pct = f"{c / total * 100:.1f}%"
        lines.append(f"| {_SOURCE_ZH.get(src, src)} | {c} | {pct} |")
    lines.append("")
    lines.append("### 按调度时段统计 / By Schedule Slot")
    lines.append("")
    lines.append("| 调度时段 / Slot | 任务数 / Tasks | 占比 / Ratio |")
    lines.append("|----------|--------|------|")
    for slot in sorted(by_slot.keys()):
        c = by_slot[slot]
        pct = f"{c / total * 100:.1f}%"
        lines.append(f"| {_SLOT_ZH.get(slot, slot)} | {c} | {pct} |")
    lines.append("")
    lines.append("### 按数据库统计 / By Database")
    lines.append("")
    lines.append("| 数据库 / DB | 任务数 / Tasks | 唯一表数 / Unique Tables |")
    lines.append("|--------|--------|----------|")
    for db in sorted(by_db.keys()):
        db_tables = {r["table"] for r in rows if _db_of(r["table"]) == db}
        lines.append(f"| {db} | {by_db[db]} | {len(db_tables)} |")
    lines.append("")
    lines.append("### 数据新鲜度统计 / Data Freshness Statistics（基于最新日期 vs 运行日期 / Based on latest date vs run date）")
    lines.append("")
    lines.append("| 新鲜度 / Freshness | 任务数 / Tasks | 说明 / Note |")
    lines.append("|--------|--------|------|")
    lines.append(f"| 🟢 当日 / Today | {fresh_counts.get('🟢', 0)} | 滞后 ≤1 天 / Lag ≤1d |")
    lines.append(f"| 🟡 滞后1-3天 / Lag 1-3d | {fresh_counts.get('🟡', 0)} | 滞后 2-3 天 / Lag 2-3d |")
    lines.append(f"| 🟠 滞后4-7天 / Lag 4-7d | {fresh_counts.get('🟠', 0)} | 滞后 4-7 天 / Lag 4-7d |")
    lines.append(f"| 🔴 滞后>7天 / Lag >7d | {fresh_counts.get('🔴', 0)} | 滞后 >7 天 / Lag >7d |")
    lines.append(f"| ⚫ 未知 / Unknown | {fresh_counts.get('⚫', 0)} | 无最新日期 / No latest date |")
    lines.append("")

    # Mermaid 图
    lines.append("## Mermaid 图表 / Charts")
    lines.append("")
    lines.append("> **图例说明 / Legend**：")
    lines.append("> - **绿色圆角矩形 / Green rounded rect** = 采集 Job / Acquisition Job（jobNode）")
    lines.append("> - **蓝色矩形 / Blue rect** = 业务表 Dataset / Business Table（dsNode）")
    lines.append("> - **粉色圆角矩形 / Pink rounded rect** = 外部数据源 / External Source（srcNode）")
    lines.append("> - **黄色圆角矩形 / Yellow rounded rect** = 调度时段内的 Job / Job in schedule slot（按时段图 / by-slot chart）")
    lines.append("> - 表节点前缀图标 / Table node prefix icon 🟢/🟡/🟠/🔴/⚫ = 数据新鲜度 / Data freshness")
    lines.append("")

    # 图1：按数据源分组
    lines.append("### 图1：按数据源分组 / By Data Source（外部源 → 采集Job → 业务表 / Source → Job → Table）")
    lines.append("")
    mmd1, n_src, n_tbl, n_edge = _gen_mermaid_by_source(rows, today, task_descs)
    lines.append(f"> {n_src} 数据源 / Sources / {n_tbl} 业务表 / Tables / {n_edge} 采集边 / Edges")
    lines.append("")
    lines.append("```mermaid")
    lines.append(mmd1.rstrip())
    lines.append("```")
    lines.append("")

    # 图2：按调度时段分组
    lines.append("### 图2：按调度时段分组 / By Schedule Slot（5档时段 → 采集Job → 业务表 / Slots → Job → Table）")
    lines.append("")
    mmd2, n_slot, n_edge2 = _gen_mermaid_by_slot(rows, today, task_descs)
    lines.append(f"> {n_slot} 调度时段 / Slots / {n_edge2} 采集边 / Edges")
    lines.append("")
    lines.append("```mermaid")
    lines.append(mmd2.rstrip())
    lines.append("```")
    lines.append("")

    # 图3：按数据库分组
    lines.append("### 图3：按数据库分组 / By Database（外部源 → ClickHouse 库 → 业务表 / Source → DB → Table）")
    lines.append("")
    mmd3, n_db, n_edge3 = _gen_mermaid_by_db(rows, today)
    lines.append(f"> {n_db} 数据库 / DBs / {n_edge3} 源→表 边（去重）/ Source→Table edges (deduped)")
    lines.append("")
    lines.append("```mermaid")
    lines.append(mmd3.rstrip())
    lines.append("```")
    lines.append("")

    # 交叉矩阵
    lines.append("## 交叉矩阵 / Cross Matrix")
    lines.append("")
    lines.append("### 数据源 × 调度时段 / Source × Slot")
    lines.append("")
    lines.append(_gen_cross_source_slot(rows))
    lines.append("")
    lines.append("### 数据源 × 状态 / Source × Status")
    lines.append("")
    lines.append(_gen_source_status(rows))
    lines.append("")

    # 完整表清单
    lines.append("## 完整表清单 / Full Table List")
    lines.append("")
    lines.append("| # | task_id | 表名 / Table | 数据库 / DB | 数据源 / Source | 调度时段 / Slot | 行数 / Rows | 最新日期 / Latest | 新鲜度 / Freshness | 状态 / Status |")
    lines.append("|---|---------|------|--------|--------|---------|------|---------|--------|------|")
    for r in rows:
        icon, fresh_desc = _freshness(r["latest"], today)
        rows_n = _parse_row_count(r["rows"])
        rows_str = _fmt_rows(rows_n)
        latest = r["latest"] or "-"
        status_zh = _STATUS_ZH.get(r["status"], r["status"])
        lines.append(
            f"| {r['idx']} | {r['task_id']} | {r['table']} | {_db_of(r['table'])} | "
            f"{_SOURCE_ZH.get(r['source'], r['source'])} | {_SLOT_ZH.get(r['slot'], r['slot'])} | "
            f"{rows_str} | {latest} | {icon} {fresh_desc} | {status_zh} |"
        )
    lines.append("")

    # 变更历史
    lines.append("## 变更历史 / Changelog")
    lines.append("")
    lines.append(f"- **{today.isoformat()}**: 初次生成 / Initial generation（generate_data_acquisition_flow.py）")
    lines.append("")

    return "\n".join(lines) + "\n"


# ============================================================
# 入口
# ============================================================
def main() -> int:
    parser = argparse.ArgumentParser(
        description="从 data_acquisition_matrix.md 生成业务数据采集流图 MD（内嵌 Mermaid）",
    )
    parser.add_argument(
        "--input", type=str, default=str(INPUT_PATH), help="输入文件（data_acquisition_matrix.md 路径）"
    )
    parser.add_argument(
        "--output", type=str, default=str(OUTPUT_PATH), help="输出文件路径"
    )
    parser.add_argument(
        "--today", type=str, default="", help="覆盖运行日期（YYYY-MM-DD），默认系统日期"
    )
    args = parser.parse_args()

    in_path = Path(args.input)
    if not in_path.exists():
        print(f"[ERROR] 输入文件不存在: {in_path}", file=sys.stderr)
        return 1

    md_text = in_path.read_text(encoding="utf-8")
    rows = _parse_rows(md_text)
    if not rows:
        print(f"[ERROR] 未解析到矩阵明细行，请检查 {in_path} 的 '## 矩阵明细' 节", file=sys.stderr)
        return 2

    today = datetime.strptime(args.today, "%Y-%m-%d").date() if args.today else date.today()

    # 生成时间戳从输入文件 mtime 派生（幂等保证：输入不变→输出时间戳不变，对标 AGENTS.md §11.1.1）
    try:
        gen_timestamp = datetime.fromtimestamp(in_path.stat().st_mtime).isoformat(timespec="seconds")
    except OSError:
        gen_timestamp = today.isoformat()

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    md = _gen_index_md(rows, today, gen_timestamp)
    out_path.write_text(md, encoding="utf-8", newline="\n")

    print(f"[OK] 生成 {out_path}")
    print(f"     解析 {len(rows)} 个采集任务，覆盖 {len({r['table'] for r in rows})} 张唯一业务表")
    print(f"     运行日期: {today.isoformat()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
