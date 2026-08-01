# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md | §acquisition-flow
# [MODULE] scripts.governance.d5_architecture.generators.generate_data_acquisition_flow
# [DOMAIN] D_GOV_SCRIPTS
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
"""G-acqflow: 从 tasks.yaml 生成业务数据采集流图 MD + 可缩放 HTML（模板 V1.2 对齐）

真源链：
  tasks.yaml（61 个任务，真源）
    → 本生成器解析
    → data_acquisition_flow.md（自动派生产物，禁止手工编辑）
    → _zoomable_html/data_acquisition_flow.html（可缩放交互版，模板 V1.2 §9.1 #1 双产物）

模板 V1.2 对齐项：
  - 灰色主题头 + flowchart TD 竖排（§4.1/§4.2）
  - subgraph 透明背景（clusterBkg transparent + JS 后处理，§13）
  - 节点四要素标签（成熟度+双语名称+大白话+标识，§4.3）
  - 标签预折行 _wrap_label_text（§4.10 铁律）
  - 4-class classDef 始终启用（§4.7），外部数据源=external_prod，ClickHouse库=production
  - MD 顶部 HTML 跳转链接（§14 http:// 绝对路径）
  - MD 生成后联动生成 HTML（emit_zoomable_html）

输出结构（按数据源分组，大白话人类可读）：
  1. 一句话说清楚（8源/61任务/2库）
  2. 数据源分布总览（一张表）
  3. 各数据源详情（8个章节，每源一张明细表）
  4. 调度时段总览
  5. 数据流向图（Mermaid 总览图，模板 V1.2 四要素+灰色主题+TD+classDef）
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
# 治本：_shared 在 scripts/governance/_shared，须将其父目录加入 sys.path
_GOV_DIR = str(next(p for p in Path(__file__).resolve().parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
# 治本（2026-08-01 模板 V1.2 升级）：脚本自身目录加入 sys.path，使 `from zoomable_html import`
# 在 importlib 加载（tests）下也能解析——仅作为 script 运行时 sys.path[0] 自动是脚本目录，但 importlib 不会加。
_THIS_DIR = str(Path(__file__).resolve().parent)
if _THIS_DIR not in sys.path:
    sys.path.insert(0, _THIS_DIR)

from _shared.constants import EXIT_PASS, EXIT_ERROR
# 术语翻译真源（SSoT：terminology_glossary.yaml，禁止硬编码中文字典）
from _shared.terminology_loader import get_category_map
try:
    from _common import DB_DISPLAY_NAME  # noqa: E402
except ImportError:
    DB_DISPLAY_NAME = "PostgreSQL depgraph"
# 可缩放 HTML 联动生成（模板 V1.2 §9.1 #1：MD+HTML 双产物，md 刷新即 HTML 刷新）
from zoomable_html import emit_zoomable_html, HTML_SUBDIR  # noqa: E402

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
# 模板 V1.2 对齐：Mermaid 主题/样式/折行/转义/HTML 链接
# （真源：visualization_view_template.md V1.2；函数复制自 generate_dataflow_diagram.py）
# ============================================================

# 本地 HTTP 文档服务器基址（模板 §14：HTML 跳转链接必须 http:// 绝对路径）
# 启动：python -m http.server 8765 --bind 127.0.0.1 （仓库根目录执行）
_DOC_HTTP_BASE = "http://localhost:8765"
# HTML 集中子文件夹相对于仓库根的 posix 路径（用于拼 http 链接）
_HTML_REL_POSIX = (
    OUTPUT_PATH.parent.relative_to(_REPO_ROOT) / HTML_SUBDIR
).as_posix()

# Mermaid 灰色主题头（模板 §4.1，含 clusterBkg transparent §13 前向兼容）
_MERMAID_THEME = (
    "%%{init: {'theme': 'base', 'themeVariables': {"
    "'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', "
    "'primaryBorderColor': '#666666', 'lineColor': '#666666', "
    "'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', "
    "'clusterBkg': 'transparent', 'clusterBorder': 'transparent', "
    "'fontSize': '14px'}}}%%"
)

# 4 类 classDef（模板 §4.7：production/design/external_prod/external_design）
_CLASSDEF_PRODUCTION = "classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000"
_CLASSDEF_DESIGN = "classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5"
_CLASSDEF_EXTERNAL_PROD = "classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000"
_CLASSDEF_EXTERNAL_DESIGN = "classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5"


def _wrap_label_text(text: str, max_units: int = 48) -> str:
    """将长节点标签文本按显示宽度预折行（Mermaid 节点内显示用）。

    治本（模板 §4.10 铁律）：Mermaid 先按标签行数测量节点框宽高，若依赖 HTML 渲染层
    CSS max-width 二次折行，渲染行数 > 测量行数 → 框高不够、文字被上下裁剪。
    必须在生成端用 <br/> 显式预折行，使测量行数 = 渲染行数。
    原样复制自 generate_domain_doc.py（模板 §4.10 指示原样复制，不跨模块 import）。
    """
    if not text:
        return ""
    lines: list[str] = []
    remaining = text.strip()
    while remaining:
        width = 0
        cut = 0
        soft = -1
        for i, ch in enumerate(remaining):
            u = 2 if ord(ch) > 0x2E7F else 1
            if width + u > max_units:
                break
            width += u
            cut = i + 1
            if ch in " _":
                soft = i + 1
            elif ch in "（(/":
                soft = i if i > 0 else -1
        if cut >= len(remaining):
            lines.append(remaining)
            break
        if soft >= 8:
            cut = soft
        line = remaining[:cut].rstrip()
        if line:
            lines.append(line)
        remaining = remaining[cut:].lstrip(" ")
    return "<br/>".join(lines)


def _sanitize_mermaid_label(text: str) -> str:
    r"""清理 Mermaid 标签特殊字符（模板 §4.9：[\]"｜）。原样复制自 generate_domain_doc.py。"""
    if not text:
        return ""
    return text.replace("[", "(").replace("]", ")").replace('"', "'").replace("|", "/")


def _html_link_for(md_stem: str) -> str:
    """生成 _zoomable_html/{md_stem}.html 的 http 绝对跳转链接（模板 §14）。"""
    return f"{_DOC_HTTP_BASE}/{_HTML_REL_POSIX}/{md_stem}.html"

# ============================================================
# 术语映射
# ============================================================

# 数据源中文名（真源：terminology_glossary.yaml 的 data_source 类别）
_SOURCE_ZH: dict[str, str] = get_category_map("data_source")

# 数据源一句话总结
_SOURCE_SUMMARY: dict[str, str] = {
    "miniqmt": "主力数据源，采 A股/港股/期货的 K线行情（日/周/月/分钟级）和财务报表、股东数据、期权可转债等。",
    "akshare": "开源数据源，采估值、融资融券、龙虎榜、大宗交易、宏观数据、限售解禁等事件类数据。",
    "ifind": "付费数据源，采资金流向、股权质押、行业分类等 iFind 独有数据。",
    "tickflow": "美股数据源，采美股日K线和美股指数（ETF替代）。",
    "tqcenter": "880xxx板块数据源，采板块K线、板块实时快照、板块成分股映射；99只推送+584只轮询混合模式，动态5因子排名调整推送池。",
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
    "tqcenter": "板块K线、板块实时快照、板块成分股映射",
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
    "manual_script": "手动触发（独立脚本）",
}

# 调度时段 → 完整描述
_SCHEDULE_DESC: dict[str, str] = {
    "daily_kline": "16:30 周一-五",
    "daily_capital": "17:00 周一-五",
    "daily_event": "18:00 周一-五",
    "weekend_financial": "周六 10:00",
    "monthly_static": "月初 09:00",
    "manual_script": "独立脚本手动触发",
}

# 调度时段 → 说明
_SCHEDULE_NOTE: dict[str, str] = {
    "daily_kline": "日K线、周月K线、分钟K线、估值",
    "daily_capital": "融资融券、龙虎榜、期货、美股、港股、资金流向",
    "daily_event": "新闻、股东、分红、质押、解禁、分析师预期",
    "weekend_financial": "财务报表、板块、期权可转债、Tick快照",
    "monthly_static": "交易日历、股票列表、行业分类、全量刷新",
    "manual_script": "880xxx板块采集（tqcenter SDK需专用路径，独立脚本触发）",
}

# 调度时段排序优先级（用于排序）
_SCHEDULE_ORDER: dict[str, int] = {
    "daily_kline": 1,
    "daily_capital": 2,
    "daily_event": 3,
    "weekend_financial": 4,
    "monthly_static": 5,
    "manual_script": 99,
}

# 已知问题（硬编码，基于实测经验，稳定知识）
_KNOWN_ISSUES: list[dict[str, str]] = [
    {"issue": "下载极慢", "task": "adj_factor_incremental", "note": "每只约11秒，5204只约需16小时，建议夜间运行"},
    {"issue": "API限流", "task": "daily_valuation_incremental", "note": "百度股市通API高频返回空响应，每只休眠1秒"},
    {"issue": "分类不兼容", "task": "tdx板块 vs 东财/同花顺/申万", "note": "通达信880xxx体系与其他分类不兼容，无法混用"},
    {"issue": "SDK路径依赖", "task": "kline_sector_880_incremental", "note": "tqcenter SDK 需 E:\\tdx\\PYPlugins 专用路径，非 scheduler 自动调度，由独立脚本触发"},
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
    """生成 frontmatter + 头部说明（模板 V1.2 §14：顶部加 HTML 跳转链接）。"""
    html_link = _html_link_for("data_acquisition_flow")
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
        "> **自动下载命令**：`python -m zephyr.data run <task_id>` 手动触发任务，`python -m zephyr.data start` 启动常驻调度（见 [cli.py](../../../src/zephyr/data/cli.py)）。",
        "",
        f"> **[可缩放 HTML 版 / Zoomable HTML]({html_link})** — Ctrl+滚轮缩放 ｜ 双击重置 ｜ Ctrl+Shift+D 切换拖动/选择模式",
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
        "## 一句话说清楚（自动生成 · 生成器: generate_data_acquisition_flow.py）",
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
    lines += ["", "---", "", "## 数据源分布总览（自动生成 · 生成器: generate_data_acquisition_flow.py）", "",
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
    lines = ["## 各数据源详情（自动生成 · 生成器: generate_data_acquisition_flow.py）", ""]

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
        "## 调度时段总览（自动生成 · 生成器: generate_data_acquisition_flow.py）",
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


# ============================================================
# 模板 V1.2 节点标签：四要素（成熟度 + 双语名称 + 大白话 + 标识）
# ============================================================

# 数据库中文名 + 简介（c1_market/c3_fundamental 是 ZephyrAlpha 内部 ClickHouse 库）
_DB_ZH: dict[str, str] = {
    "c1_market": "行情库",
    "c3_fundamental": "基本面库",
}
_DB_DESC: dict[str, str] = {
    "c1_market": "K线、指数、期货、资金、估值等行情类数据",
    "c3_fundamental": "财务报表、新闻、股东、分红等基本面类数据",
}


def _source_node_label(src: str, task_count: int) -> str:
    """外部数据源节点四要素标签（模板 §4.3 适配采集流：外部数据源=external_prod）。

    ①成熟度（生产态 / production）②双语名称（src / 中文名）③大白话（_SOURCE_SUMMARY）
    ④标识（数据源 / data-source · N任务）。每行过 _wrap_label_text 预折行（§4.10）。
    """
    maturity = "生产态 / production"
    zh = _SOURCE_ZH.get(src, "")
    name_bi = f"{src} / {zh}" if zh and zh != src else src
    summary = _SOURCE_SUMMARY.get(src, "")
    identifier = f"数据源 / data-source（{task_count}任务）"
    parts = [f"({maturity}) {name_bi}"]
    if summary:
        parts.append(summary)
    parts.append(identifier)
    return _sanitize_mermaid_label("<br/>".join(_wrap_label_text(p) for p in parts))


def _db_node_label(db: str) -> str:
    """ClickHouse 库节点四要素标签（模板 §4.3 适配采集流：内部库=production）。

    ①成熟度（生产态 / production）②双语名称（db / 中文名）③大白话（_DB_DESC）
    ④标识（ClickHouse库 / database）。每行过 _wrap_label_text 预折行（§4.10）。
    """
    maturity = "生产态 / production"
    zh = _DB_ZH.get(db, "")
    name_bi = f"{db} / {zh}" if zh and zh != db else db
    desc = _DB_DESC.get(db, "")
    identifier = "ClickHouse库 / database"
    parts = [f"({maturity}) {name_bi}"]
    if desc:
        parts.append(desc)
    parts.append(identifier)
    return _sanitize_mermaid_label("<br/>".join(_wrap_label_text(p) for p in parts))


_LEGEND_BLOCK = """\
> **图例说明 / Legend**：
>
> - 🟦 **蓝色 = 生产态节点**（production，ZephyrAlpha 内部 ClickHouse 库，已上线运行）
> - 🟦更浅蓝 = 外部数据源（external_prod，系统外部第三方数据提供方）
> - **实线箭头 ``-->`` = 数据流向**（数据源 → ClickHouse 库）
> - 节点含四要素：成熟度 + 双语名称 + 大白话简介 + 标识（模板 V1.2 §4.3）
"""


def _gen_flow_diagram(tasks: list[dict]) -> list[str]:
    """生成'数据流向图' Mermaid 总览图（模板 V1.2 全面对齐）。

    模板 V1.2 强制项：①灰色主题头（含 clusterBkg transparent）②flowchart TD 竖排
    ③subgraph 透明背景（clusterBkg transparent + JS 后处理，模板 §13）④节点四要素标签
    （成熟度+双语名称+大白话+标识）⑤标签预折行 _wrap_label_text ⑥4-class classDef 始终启用
    ⑦class 应用（外部数据源=external_prod，ClickHouse库=production）⑧实线箭头（全 production 间）。
    """
    by_source: dict[str, int] = defaultdict(int)
    for t in tasks:
        by_source[t["source"]] += 1

    # 源 → 库映射
    src_to_dbs: dict[str, set[str]] = defaultdict(set)
    for t in tasks:
        src_to_dbs[t["source"]].add(_db_of(t["table"]))
    all_dbs = sorted({_db_of(t["table"]) for t in tasks})

    # Mermaid 节点 ID 映射（按任务数降序排源，库按名排）
    src_order = sorted(by_source.keys(), key=lambda s: -by_source[s])
    src_ids = {src: f"S{i}" for i, src in enumerate(src_order)}
    db_ids = {db: f"D{i}" for i, db in enumerate(all_dbs)}

    lines = [
        "## 数据流向图（自动生成 · 生成器: generate_data_acquisition_flow.py）",
        "",
        _LEGEND_BLOCK.rstrip(),
        "",
        "```mermaid",
        _MERMAID_THEME,
        "flowchart TD",
        '    subgraph ext_sources["外部数据源 / External Data Sources"]',
    ]
    for src in src_order:
        sid = src_ids[src]
        lines.append(f'        {sid}["{_source_node_label(src, by_source[src])}"]')
    lines.append("    end")
    lines.append("")
    lines.append('    subgraph clickhouse["ClickHouse 数据库 / Databases"]')
    for db in all_dbs:
        did = db_ids[db]
        lines.append(f'        {did}["{_db_node_label(db)}"]')
    lines.append("    end")
    lines.append("")

    # 边（去重，全部 production→production → 实线，模板 §4.5）
    edges_seen: set[tuple[str, str]] = set()
    for src in sorted(src_to_dbs.keys()):
        for db in sorted(src_to_dbs[src]):
            key = (src, db)
            if key in edges_seen:
                continue
            edges_seen.add(key)
            lines.append(f"    {src_ids[src]} -->|采集 / ingests| {db_ids[db]}")

    # 4-class classDef（模板 §4.7，始终启用）
    lines.append(f"    {_CLASSDEF_PRODUCTION}")
    lines.append(f"    {_CLASSDEF_DESIGN}")
    lines.append(f"    {_CLASSDEF_EXTERNAL_PROD}")
    lines.append(f"    {_CLASSDEF_EXTERNAL_DESIGN}")

    # class 应用（模板 §4.8）：外部数据源=external_prod，ClickHouse库=production
    all_src_ids = [src_ids[s] for s in src_order]
    all_db_ids = [db_ids[db] for db in all_dbs]
    if all_src_ids:
        lines.append(f"    class {','.join(all_src_ids)} external_prod")
    if all_db_ids:
        lines.append(f"    class {','.join(all_db_ids)} production")

    lines.append("```")
    lines += ["", "---", ""]
    return lines


def _gen_known_issues(tasks: list[dict]) -> list[str]:
    """生成'已知问题与注意事项'。

    来源：① tasks.yaml 中 disabled/requires_manual 的任务 ② 硬编码的实测经验。
    """
    lines = [
        "## 已知问题与注意事项（自动生成 · 生成器: generate_data_acquisition_flow.py）",
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
    """Entry point: parse args, run logic, return exit code."""
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
        return EXIT_ERROR
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

    # 模板 V1.2 §9.1 #1：MD+HTML 双产物，md 生成后联动生成可缩放 HTML
    html_path = emit_zoomable_html(out_path, md, out_path.parent / HTML_SUBDIR)
    if html_path:
        print(f"[OK] └ _zoomable_html/{out_path.stem}.html（可缩放交互版）")

    print(f"[OK] 生成 {out_path}")
    print(f"     解析 {len(tasks)} 个采集任务，覆盖 {len({t['table'] for t in tasks})} 张唯一业务表")
    print(f"     运行日期: {today.isoformat()}")
    return EXIT_PASS
if __name__ == "__main__":
    sys.exit(main())
