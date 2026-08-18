# [BLUEPRINT] MOD-GOV_GENERATE_DOMAIN_INDEX
# [MODULE]# [MODULE] scripts.governance.d5_architecture.generators.generate_domain_index
# [DOMAIN]
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
"""G5: 从 depgraph (PostgreSQL) domains+nodes 表生成域总览索引MD文档

[BLUEPRINT] ARCHITECTURE-DIAGRAM-PLAN | docs/02_enterprise_architecture/architecture_diagram_construction_plan.md | §4.4
[MODULE] scripts.governance.d5_architecture.generators.generate_domain_index
[INVARIANTS] 输出幂等(相同输入→相同输出);只读depgraph (PostgreSQL);输出到generated/domain_index.md
[MODIFY-GUARD] 修改需通过DM-200911任务卡或后续维护任务卡
[CONSUMERS] CI自动触发;人工查看generated/domain_index.md
[STABILITY] evolving
[SAFETY] L
[AI_AUTONOMY] ai_modifiable
[ERROR_CONTRACT] depgraph (PostgreSQL)不存在→exit 1
[TESTS]
[DOMAIN] D_GOVERNANCE
"""

from __future__ import annotations

# _common.py 与本文件同目录（generators/），CLI 运行时 sys.path[0]=本目录，可直接 import。
from _common import DB_DISPLAY_NAME  # noqa: E402

# 治本（2026-08-18）：f-string manifest 生成器不识别（提取器仅认静态三引号 YAML），静态化。
__manifest__ = """
args: []
description: 'G5: 从 depgraph (PostgreSQL) domains+nodes 表生成域总览索引MD文档'
dimensions:
- D5
priority: P2
timeout_seconds: 60
warn_only: false
"""


import sys
from pathlib import Path

_THIS_FILE = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _THIS_FILE.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import PgConnExecuteWrapper, get_depgraph_pg_connection  # noqa: E402

from domain_name_mapping import get_domain_name_zh, get_domain_name_en, get_layer_name_bilingual
from zephyr.shared.io.paths import REPO_ROOT  # 仓库根真源（SSoT：zephyr.shared.io.paths）

# 治本（2026-07-06）：复用 generate_domain_doc 的编号映射，确保索引链接与文件名一致
_GENERATORS_DIR = _THIS_FILE.parent
if str(_GENERATORS_DIR) not in sys.path:
    sys.path.insert(0, str(_GENERATORS_DIR))
from generate_domain_doc import build_numbering_map  # noqa: E402

OUTPUT_PATH = REPO_ROOT / "docs" / "02_enterprise_architecture" / "02_domain_architecture_docs" / "domain_index.md"

# 治本（2026-07-31）：在域总览索引头部加大白话解释，让入口索引对非架构读者也友好。
# 覆盖读者高频疑问：依赖关系是什么、依赖图是什么、有什么用、为什么要看、这份索引主要看什么。
# 详细设计裁定见 dependency_path_panorama.md，此处只做入口式简短引导。
_PLAIN_LANGUAGE_INTRO = """\
## 这是什么？大白话讲依赖图

这份"域总览索引"背后是一张**依赖图**。在往下看清单之前，先用大白话讲清楚它是什么、有什么用、为什么要看。

### 一、依赖关系是什么意思？

一个模块要用到另一个模块，就叫"依赖"。
比如"订单中心"要调用"风控引擎"做风险检查，就说 **订单中心依赖风控引擎**——订单中心离不开风控引擎，箭头是 `订单中心 → 风控引擎`（"我需要你"）。

把项目里所有这种"谁离不开谁"的关系记下来，就是**依赖关系**。

### 二、依赖图是什么？

把项目里**所有模块**当成点，把**所有依赖关系**当成连线，画成一张大网，就是依赖图。

- 它不是一张图片，是存在数据库（`depgraph`）里的一张表
- 它记清楚了：项目有多少功能域、每个域有多少模块、模块之间谁依赖谁、哪些已经造好、哪些还在图纸上

### 三、依赖图有什么用？为什么要看它？

这个项目是 **100% AI 开发**，依赖图专门治 AI 的几个老毛病：

| 看依赖图 | 不看依赖图 |
|---|---|
| 造模块前先查：在不在图里？ | AI 自己编一个不存在的模块（幻觉） |
| 改模块前先查：谁依赖我？ | 改完才发现连累一片，返工 |
| 建文件前先查：放哪个域？容量够吗？ | 文件乱放，域越塞越乱 |
| 对着图走路 | 凭记忆瞎猜，做着做着跑偏 |

**一句话**：依赖图是这个项目的"地图"，AI 干活前必须先看图，不能凭感觉瞎走。

### 四、这份索引主要看什么？

这份"域总览索引"是依赖图的**入口**，主要看三件事：

1. **有多少域** —— 项目分成若干功能域（D_DATA 数据、D_RISK 风控、D_POSITION 仓位…），每个域管一类事
2. **每个域多大** —— 看"模块数"列，知道这个域塞了多少模块
3. **域的状态** —— 看"生产态/设计态"列：生产态 = 已经造好跑起来了，设计态 = 还在图纸上没动工

想看某个域的详细模块清单，点右边"📄 文档"链接进入该域的专属文档。

> 想深入了解依赖图的设计和裁定，看 [依赖与路径全景图能力定位书](../04_architecture_principles_decisions/panorama/dependency_path_panorama.md)。

---
"""


def get_all_domains(conn: PgConnExecuteWrapper) -> list[dict]:
    """查询所有域及其模块统计。"""
    cur = conn.execute(
        """SELECT d.domain_id, d.domain_name, d.layer_id, d.current_modules,
                  d.max_modules, d.description,
                  (SELECT COUNT(*) FROM nodes n WHERE n.domain_id = d.domain_id) as actual_nodes,
                  (SELECT COUNT(*) FROM nodes n WHERE n.domain_id = d.domain_id AND n.design_maturity = 'production') as production_count,
                  (SELECT COUNT(*) FROM nodes n WHERE n.domain_id = d.domain_id AND n.design_maturity = 'design') as design_count
           FROM domains d
           ORDER BY d.domain_id"""
    )
    return [
        {
            "domain_id": r["domain_id"],
            "domain_name": r["domain_name"] or "",
            "layer_id": r["layer_id"] or "",
            "current_modules": r["current_modules"] or 0,
            "max_modules": r["max_modules"] or 200,
            "description": r["description"] or "",
            "actual_nodes": r["actual_nodes"],
            "production_count": r["production_count"],
            "design_count": r["design_count"],
        }
        for r in cur.fetchall()
    ]


def generate_domain_index() -> str:
    """生成域总览索引MD文档。"""
    conn = get_depgraph_pg_connection(autocommit=True)
    try:
        domains = get_all_domains(conn)
        numbering_map = build_numbering_map(conn)
    finally:
        conn.close()

    lines = []
    # frontmatter
    lines.append("---")
    lines.append("doc_type: index")
    lines.append("title: 域总览索引")
    lines.append('version: "1.0"')
    lines.append("status: active")
    lines.append("date: auto-generated")
    lines.append("owner: auto-generator")
    lines.append("ttl: permanent")
    lines.append("---")
    lines.append("")
    lines.append("# 域总览索引")
    lines.append("")
    lines.append("> **文档作用 / Purpose**: 列出所有功能域的编号、ID、名称、层级、模块数等基本信息，是域架构文档的入口索引。")
    lines.append("")
    lines.append(f"> 本文档由 generate_domain_index.py 从 {DB_DISPLAY_NAME} 自动生成")
    lines.append("> 最后更新以 git log 为准")
    lines.append(f"> 数据源: {DB_DISPLAY_NAME} domains表 + nodes表")
    lines.append("")

    # 大白话解释依赖图（治本 2026-07-31）：让入口索引对非架构读者也友好
    lines.extend(_PLAIN_LANGUAGE_INTRO.splitlines())
    lines.append("")

    # 统计概览
    total_domains = len(domains)
    total_nodes = sum(d["actual_nodes"] for d in domains)
    total_production = sum(d["production_count"] for d in domains)
    total_design = sum(d["design_count"] for d in domains)

    lines.append("## 统计概览")
    lines.append("")
    lines.append("| 指标 / Metric | 值 / Value |")
    lines.append("|------|-----|")
    lines.append(f"| 域总数 | {total_domains} |")
    lines.append(f"| 模块总数 | {total_nodes} |")
    lines.append(f"| 生产态模块 | {total_production} |")
    lines.append(f"| 设计态模块 | {total_design} |")
    lines.append("")

    # 按架构层分组
    layers: dict[str, list[dict]] = {}
    for d in domains:
        layer = d["layer_id"] or "未分类"
        layers.setdefault(layer, []).append(d)

    lines.append("## 域清单（按架构层分组）")
    lines.append("")

    for layer in sorted(layers.keys()):
        layer_domains = layers[layer]
        layer_zh, layer_en = get_layer_name_bilingual(layer)
        lines.append(f"### {layer_zh} / {layer_en} ({len(layer_domains)} 个域 / {len(layer_domains)} domains)")
        lines.append("")
        lines.append("| 域ID / Domain ID | 域名称 / Domain Name | 模块数 / Modules | 生产态 / Production | 设计态 / Design | 容量 / Capacity | 文档 / Doc |")
        lines.append("|------|--------|:---:|:---:|:---:|------|------|")
        for d in layer_domains:
            capacity = f"{d['actual_nodes']}/{d['max_modules']}"
            capacity_status = "OK" if d["actual_nodes"] <= d["max_modules"] else "超容"
            safe_name = d["domain_id"].replace("-", "_").lower()
            number = numbering_map.get(d["domain_id"], 0)
            if number:
                # 治本（2026-07-19）：加 📄 图标让链接视觉更明显，点击跳转到对应域文档
                doc_link = f"[📄 {number:02d}_{safe_name}.md]({number:02d}_{safe_name}.md)"
            else:
                # 未编号域：无对应文档，纯文本提示（修复原 (未编号) 断链 bug）
                doc_link = "— 未编号"
            lines.append(
                f"| {d['domain_id']} | {get_domain_name_zh(d['domain_id'], d['domain_name'])} / {get_domain_name_en(d['domain_id'])} | {d['actual_nodes']} | "
                f"{d['production_count']} | {d['design_count']} | "
                f"{capacity} ({capacity_status}) | {doc_link} |"
            )
        lines.append("")

    return "\n".join(lines)


def main() -> None:
    """入口：生成域总览索引。"""
    content = generate_domain_index()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(content, encoding="utf-8", newline="\n")
    print(f"[OK] 生成 {OUTPUT_PATH} ({len(content)} 字符)")


if __name__ == "__main__":
    main()
