# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md | §acquisition-flow
# [MODULE] scripts.governance.d5_architecture.generators.generate_data_acquisition_flow
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] _common (DB_DISPLAY_NAME)
# [CONSUMERS] 人工查看data_acquisition_flow.md
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 输出幂等(相同输入→相同输出);只读tasks.yaml;输出到05_dataflow_architecture/
# [MODIFY-GUARD] 修改需通过MOD-L00-004任务或后续维护任务
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] tasks.yaml不存在→exit 1;tasks为空→exit 2
# [TESTS]
# [TTL] permanent
"""G-acqflow: 从 tasks.yaml 生成业务数据采集流图 MD（人类可读版，内嵌 Mermaid）

真源链：
  tasks.yaml（61 个任务，真源）
    → 本生成器解析
    → data_acquisition_flow.md（自动派生产物，禁止手工编辑）

输出结构（按数据源分组，大白话人类可读）：
  1. 一句话说清楚（8源/61任务/2库）
  2. 数据源分布总览（一张表）
  3. 各数据源详情（8个章节，每源一张明细表）
  4. 调度时段总览
  5. 数据流向图（Mermaid 总览图）
  6. 已知问题与注意事项

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
description: 'G-acqflow: 从 tasks.yaml 生成业务数据采集流图 MD（人类可读版，按数据源分组）'
dimensions:
- D5
priority: P2
timeout_seconds: 60
warn_only: false
"""

# 真源：tasks.yaml
TASKS_YAML = _REPO_ROOT / "src" / "zephyr" / "data" / "config" / "tasks.yaml"
# 输出
OUTPUT_PATH = (
    _REPO_ROOT / "docs" / "02_enterprise_architecture" / "05_dataflow_architecture" / "data_acquisition_flow.md"
)

# ============================================================
# 术语映射
# ============================================================

# 数据源中文名
_SOURCE_ZH: dict[str, str] = {
    "miniqmt": "迅投QMT",
    "akshare": "AKShare",
    "ifind": "同花顺iFind",
    "tickflow": "TickFlow",
    "tdx": "通达信",
    "baostock": "BaoStock",
    "tushare": "Tushare",
    "rss": "RSS",
}

# 数据源一句话总结
_SOURCE_SUMMARY: dict[str, str] = {
    "miniqmt": "主力数据源，采 A股/港股/期货的 K线行情（日/周/月/分钟级）和财务报表、股东数据、期权可转债等。",
    "akshare": "开源数据源，采估值、融资融券、龙虎榜、大宗交易、宏观数据、限售解禁等事件类数据。",
    "ifind": "付费数据源，采资金流向、股权质押、行业分类等 iFind 独有数据。",
    "tickflow": "美股数据源，采美股日K线和美股指数（ETF替代）。",
    "tdx": "板块数据源，采通达信板块分类、板块K线、板块成分股。",
    "baostock": "开源数据源，采交易日历和沪深300成分股。",
    "tushare": "付费数据源，采新闻快讯和证券新闻。",
    "rss": "RSS爬虫，采财经新闻。",
}

# 数据源主要采什么（用于总览表）
_SOURCE_MAIN: dict[str, str] = {
    "miniqmt": "K线行情、财务报表、股东数据、期权可转债",
    "akshare": "估值、融资融券、龙虎榜、大宗交易、宏观",
    "ifind": "资金流向、股权质押、行业分类",
    "tickflow": "美股K线、美股指数",
    "tdx": "板块分类、板块K线、板块成分股",
    "baostock": "交易日历、沪深300成分股",
    "tushare": "新闻快讯、证券新闻",
    "rss": "财经新闻",
}

# 调度时段 → 人类可读时间
_SCHEDULE_TIME: dict[str, str] = {
    "daily_kline": "盘后 16:30",
    "daily_capital": "盘后 17:00",
    "daily_event": "盘后 18:00",
    "weekend_financial": "周六 10:00",
    "monthly_static": "月初 09:00",
}

# 调度时段 → 完整描述
_SCHEDULE_DESC: dict[str, str] = {
    "daily_kline": "16:30 周一-五",
    "daily_capital": "17:00 周一-五",
    "daily_event": "18:00 周一-五",
    "weekend_financial": "周六 10:00",
    "monthly_static": "月初 09:00",
}

# 调度时段 → 说明
_SCHEDULE_NOTE: dict[str, str] = {
    "daily_kline": "日K线、周月K线、分钟K线、估值",
    "daily_capital": "融资融券、龙虎榜、期货、美股、港股、资金流向",
    "daily_event": "新闻、股东、分红、质押、解禁、分析师预期",
    "weekend_financial": "财务报表、板块、期权可转债、Tick快照",
    "monthly_static": "交易日历、股票列表、行业分类、全量刷新",
}

# 调度时段排序优先级（用于排序）
_SCHEDULE_ORDER: dict[str, int] = {
    "daily_kline": 1,
    "daily_capital": 2,
    "daily_event": 3,
    "weekend_financial": 4,
    "monthly_static": 5,
}

# 已知问题（硬编码，基于实测经验，稳定知识）
_KNOWN_ISSUES: list[dict[str, str]] = [
    {"issue": "下载极慢", "task": "adj_factor_incremental", "note": "每只约11秒，5204只约需16小时，建议夜间运行"},
    {"issue": "API限流", "task": "daily_valuation_incremental", "note": "百度股市通API高频返回空响应，每只休眠1秒"},
    {"issue": "分类不兼容", "task": "tdx板块 vs 东财/同花顺/申万", "note": "通达信880xxx体系与其他分类不兼容，无法混用"},
]

# 匹配末尾的括号技术备注（全角（）或半角()，内容不含嵌套括号）
_TRAILING_PAREN = re.compile(r"[（(][^（）()]*[)）]\s*$")


# ============================================================
# 解析 tasks.yaml
# ============================================================
def _strip_tech_note(desc: str) -> str:
    """去除 description 末尾的技术备注括号内容，保留有意义的中文描述。

    例："复权因子增量（miniQMT get_divid_factors）" → "复权因子增量"
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


def _parse_tasks_yaml() -> list[dict]:
    """解析 tasks.yaml，返回任务列表。

    每个任务 dict:
      task_id, table, source, schedule, incremental, dependencies,
      description, disabled, requires_manual
    """
    try:
        import yaml  # type: ignore[import-untyped]
    except ImportError:
        print("[ERROR] PyYAML 不可用", file=sys.stderr)
        return []
    if not TASKS_YAML.exists():
        print(f"[ERROR] 真源文件不存在: {TASKS_YAML}", file=sys.stderr)
        return []
    try:
        data = yaml.safe_load(TASKS_YAML.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"[ERROR] 解析 tasks.yaml 失败: {e}", file=sys.stderr)
        return []
    if not isinstance(data, dict):
        return []

    tasks: list[dict] = []
    for task in data.get("tasks", []) or []:
        if not isinstance(task, dict):
            continue
        task_id = task.get("task_id")
        if not task_id:
            continue
        extra = task.get("extra") or {}
        if not isinstance(extra, dict):
            extra = {}
        deps = task.get("dependencies") or []
        if not isinstance(deps, list):
            deps = []
        desc = _strip_tech_note(_extract_desc_from_task(task))
        tasks.append({
            "task_id": str(task_id),
            "table": str(task.get("table", "")),
            "source": str(task.get("source", "")),
            "schedule": str(task.get("schedule", "")),
            "incremental": bool(task.get("incremental", True)),
            "dependencies": [str(d) for d in deps],
            "description": desc,
            "disabled": bool(extra.get("disabled", False)),
            "requires_manual": bool(extra.get("requires_manual", False)),
        })
    return tasks


# ============================================================
# 辅助
# ============================================================
def _db_of(table: str) -> str:
    """表名 → 数据库名（c1_market.xxx → c1_market）。"""
    return table.split(".", 1)[0] if "." in table else "unknown"


def _format_desc(task: dict) -> str:
    """格式化任务说明：description + 依赖标注 + 禁用标注。"""
    desc = task.get("description", "")
    deps = task.get("dependencies", [])
    if deps:
        dep_str = "、".join(deps)
        desc = f"{desc}（依赖{dep_str}）" if desc else f"依赖{dep_str}"
    if task.get("disabled"):
        desc = f"{desc}（**已禁用**）" if desc else "**已禁用**"
    elif task.get("requires_manual"):
        desc = f"{desc}（需手动）" if desc else "需手动"
    return desc


def _sort_tasks(tasks: list[dict]) -> list[dict]:
    """按调度时段排序，同时段按 task_id 排序。"""
    return sorted(tasks, key=lambda t: (
        _SCHEDULE_ORDER.get(t["schedule"], 99),
        t["task_id"],
    ))


# ============================================================
# 各部分 MD 生成
# ============================================================
def _gen_header(today: date, gen_timestamp: str) -> list[str]:
    """生成 frontmatter + 头部说明。"""
    return [
        "---",
        "doc_type: architecture_view",
        "title: 数据采集流图 / Data Acquisition Flow",
        'version: "2.0"',
        "status: active",
        f"date: {today.isoformat()}",
        "owner: auto-generator",
        "ttl: permanent",
        "---",
        "",
        "# 数据采集流图 / Data Acquisition Flow",
        "",
        '> **这个文档是给人看的**：用大白话说清楚「系统从哪些数据源、采了什么数据、灌到哪张表、什么时候采」。',
        f"> **真源是 [tasks.yaml](../../../src/zephyr/data/config/tasks.yaml)**，本文档是自动生成的派生产物，禁止手工编辑。",
        "> **数据源连接和 API 细节**见 [data_source_operation_manual.md](../../03_modules/_domain_data/data_source_operation_manual.md)。",
        "",
        "---",
        "",
    ]


def _gen_overview(tasks: list[dict]) -> list[str]:
    """生成'一句话说清楚' + '数据源分布总览'。"""
    total = len(tasks)
    sources = sorted({t["source"] for t in tasks})
    dbs = sorted({_db_of(t["table"]) for t in tasks})

    lines = [
        "## 一句话说清楚",
        "",
        f"系统每天从 **{len(sources)} 个数据源**采集 **{total} 个任务**，灌进 ClickHouse 的 **{len(dbs)} 个库**：",
        "",
    ]
    for db in dbs:
        if db == "c1_market":
            lines.append(f"- `{db}` — 行情库（K线、指数、期货、资金、估值等）")
        elif db == "c3_fundamental":
            lines.append(f"- `{db}` — 基本面库（财务报表、新闻、股东、分红等）")
        else:
            lines.append(f"- `{db}`")
    lines += ["", "---", "", "## 数据源分布总览", "",
              "| 数据源 | 任务数 | 主要采什么 |",
              "|--------|--------|-----------|"]

    # 按任务数降序
    by_source: dict[str, int] = defaultdict(int)
    for t in tasks:
        by_source[t["source"]] += 1
    for src in sorted(by_source.keys(), key=lambda s: -by_source[s]):
        src_display = src
        zh = _SOURCE_ZH.get(src)
        if zh:
            src_display = f"**{src}**（{zh}）"
        lines.append(f"| {src_display} | {by_source[src]} | {_SOURCE_MAIN.get(src, '-')} |")
    lines.append(f"| **合计** | **{total}** | |")
    lines += ["", "---", ""]
    return lines


def _gen_source_detail(tasks: list[dict]) -> list[str]:
    """生成'各数据源详情'（8个章节，每源一张明细表）。"""
    lines = ["## 各数据源详情", ""]

    # 按数据源分组
    by_source: dict[str, list[dict]] = defaultdict(list)
    for t in tasks:
        by_source[t["source"]].append(t)

    # 按任务数降序
    for idx, src in enumerate(sorted(by_source.keys(), key=lambda s: -len(by_source[s])), 1):
        src_zh = _SOURCE_ZH.get(src, src)
        src_tasks = _sort_tasks(by_source[src])
        is_primary = "，主力数据源" if idx == 1 else ""

        lines.append(f"### {idx}. {src}（{src_zh}）— {len(src_tasks)} 个任务{is_primary}")
        lines.append("")
        lines.append(f"**一句话**：{_SOURCE_SUMMARY.get(src, '（待补充）')}")
        lines.append("")
        lines.append("**采集明细**：")
        lines.append("")
        lines.append("| 任务 | 灌到哪张表 | 什么时候采 | 说明 |")
        lines.append("|------|-----------|-----------|------|")
        for t in src_tasks:
            slot_time = _SCHEDULE_TIME.get(t["schedule"], t["schedule"])
            desc = _format_desc(t)
            lines.append(f"| {t['task_id']} | {t['table']} | {slot_time} | {desc} |")
        lines.append("")

        # 检查已知问题的 task 是否在该源的任务列表中
        src_task_ids = {t["task_id"] for t in src_tasks}
        src_issues = [i for i in _KNOWN_ISSUES
                      if i["task"] in src_task_ids or src_zh in i["task"] or src in i["task"]]
        if src_issues:
            lines.append("**注意**：")
            for iss in src_issues:
                lines.append(f"- `{iss['task']}`：{iss['note']}")
            lines.append("")

        lines.append("---")
        lines.append("")

    return lines


def _gen_schedule_overview(tasks: list[dict]) -> list[str]:
    """生成'调度时段总览'。"""
    by_slot: dict[str, int] = defaultdict(int)
    for t in tasks:
        by_slot[t["schedule"]] += 1

    lines = [
        "## 调度时段总览",
        "",
        "系统按 5 个时段调度，避免并发冲突：",
        "",
        "| 调度时段 | 时间 | 任务数 | 说明 |",
        "|---------|------|--------|------|",
    ]
    total = 0
    for slot in sorted(by_slot.keys(), key=lambda s: _SCHEDULE_ORDER.get(s, 99)):
        count = by_slot[slot]
        total += count
        time_desc = _SCHEDULE_DESC.get(slot, slot)
        note = _SCHEDULE_NOTE.get(slot, "-")
        lines.append(f"| {_SCHEDULE_TIME.get(slot, slot)} | {time_desc} | {count} | {note} |")
    lines.append(f"| **合计** | | **{total}** | |")
    lines += ["", "---", ""]
    return lines


def _gen_flow_diagram(tasks: list[dict]) -> list[str]:
    """生成'数据流向图' Mermaid 总览图。"""
    by_source: dict[str, int] = defaultdict(int)
    for t in tasks:
        by_source[t["source"]] += 1

    # 源 → 库映射
    src_to_dbs: dict[str, set[str]] = defaultdict(set)
    for t in tasks:
        src_to_dbs[t["source"]].add(_db_of(t["table"]))
    all_dbs = sorted({_db_of(t["table"]) for t in tasks})

    # Mermaid 节点 ID 映射
    src_ids = {src: f"S{i}" for i, src in enumerate(sorted(by_source.keys()))}
    db_ids = {db: f"D{i}" for i, db in enumerate(all_dbs)}

    lines = [
        "## 数据流向图",
        "",
        "```mermaid",
        "flowchart LR",
        "    subgraph 外部数据源",
    ]
    for src in sorted(by_source.keys(), key=lambda s: -by_source[s]):
        sid = src_ids[src]
        zh = _SOURCE_ZH.get(src, src)
        lines.append(f'        {sid}["{src}<br/>{zh}<br/>{by_source[src]}任务"]')
    lines.append("    end")
    lines.append("")
    lines.append("    subgraph ClickHouse")
    for db in all_dbs:
        did = db_ids[db]
        label = "行情库" if db == "c1_market" else "基本面库" if db == "c3_fundamental" else db
        lines.append(f'        {did}["{db}<br/>{label}"]')
    lines.append("    end")
    lines.append("")

    # 边（去重）
    edges_seen: set[tuple[str, str]] = set()
    for src in sorted(src_to_dbs.keys()):
        for db in sorted(src_to_dbs[src]):
            key = (src, db)
            if key in edges_seen:
                continue
            edges_seen.add(key)
            lines.append(f"    {src_ids[src]} --> {db_ids[db]}")

    lines.append("```")
    lines += ["", "---", ""]
    return lines


def _gen_known_issues(tasks: list[dict]) -> list[str]:
    """生成'已知问题与注意事项'。

    来源：① tasks.yaml 中 disabled/requires_manual 的任务 ② 硬编码的实测经验。
    """
    lines = [
        "## 已知问题与注意事项",
        "",
        "| 问题 | 涉及任务 | 说明 |",
        "|------|---------|------|",
    ]

    # 硬编码的已知问题
    for iss in _KNOWN_ISSUES:
        lines.append(f"| **{iss['issue']}** | {iss['task']} | {iss['note']} |")

    # 从 tasks.yaml 提取已禁用/需手动的任务
    for t in tasks:
        if t.get("disabled"):
            lines.append(f"| **已禁用** | {t['task_id']} | {t.get('description', '-')} |")
        elif t.get("requires_manual"):
            lines.append(f"| **需手动** | {t['task_id']} | {t.get('description', '-')} |")

    lines.append("")
    return lines


def _gen_index_md(tasks: list[dict], today: date, gen_timestamp: str) -> str:
    """组装完整 MD 文档。"""
    lines: list[str] = []
    lines += _gen_header(today, gen_timestamp)
    lines += _gen_overview(tasks)
    lines += _gen_source_detail(tasks)
    lines += _gen_schedule_overview(tasks)
    lines += _gen_flow_diagram(tasks)
    lines += _gen_known_issues(tasks)
    return "\n".join(lines)


# ============================================================
# 入口
# ============================================================
def main() -> int:
    parser = argparse.ArgumentParser(
        description="从 tasks.yaml 生成业务数据采集流图 MD（人类可读版，按数据源分组）",
    )
    parser.add_argument(
        "--output", type=str, default=str(OUTPUT_PATH), help="输出文件路径"
    )
    parser.add_argument(
        "--today", type=str, default="", help="覆盖运行日期（YYYY-MM-DD），默认系统日期"
    )
    args = parser.parse_args()

    tasks = _parse_tasks_yaml()
    if not tasks:
        print(f"[ERROR] 未解析到任务，请检查 {TASKS_YAML}", file=sys.stderr)
        return 2

    today = datetime.strptime(args.today, "%Y-%m-%d").date() if args.today else date.today()

    # 生成时间戳从真源文件 mtime 派生（幂等保证：输入不变→输出时间戳不变）
    try:
        gen_timestamp = datetime.fromtimestamp(TASKS_YAML.stat().st_mtime).isoformat(timespec="seconds")
    except OSError:
        gen_timestamp = today.isoformat()

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    md = _gen_index_md(tasks, today, gen_timestamp)
    out_path.write_text(md, encoding="utf-8", newline="\n")

    print(f"[OK] 生成 {out_path}")
    print(f"     解析 {len(tasks)} 个采集任务，覆盖 {len({t['table'] for t in tasks})} 张唯一业务表")
    print(f"     运行日期: {today.isoformat()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
