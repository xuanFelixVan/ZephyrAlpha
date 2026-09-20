---
title: "终极图书馆 · 终极全貌 v1.0（终局方案定稿）"
ttl: task_bound
completes_when: Owner 批终局方案→今夜总攻验收通过后转正入 docs
date: "2026-09-21"
owner: "ZephyrAlpha-Owner"
session: "st-ulib-20260921"
---

# 终极全貌 v1.0 —— 资产主权系统（终局方案）

> **一句话**：存储分布化，主权集中化——**家可以各自住，户口只有一个；出生、迁移、死亡、查询，只走图书馆一道门。**

## §1 第一性原理（为什么是一道门，不是一个仓库）

100% AI 开发运维的项目只有两种根病：
1. **漂移**=现实≠记录（本战役实证 12 条：台账过期/口径打架/假活任务/同名异构双胞胎/契约双向漂移）；
2. **幻觉**=AI 断言无接地（无验证记忆库退化为幻觉源，学术共识）。
两病同根：**变更绕过了记录**（未登记的新建/删除/搬家）+**读取绕过了总目**（AI grep 到陈旧副本就当真）。治本不是换存储介质，是把这两个口堵死：**一切变更必登记，一切查询必经口。** 规模已到临界（PG 实测 12,107 节点/3,854 模块/83 域/44+ 计划任务），不装闸只会越来越贵。

## §2 终态四件套（95% 收编现成件，真正新造只有一件半）

| 件 | 终态定义 | 收编自（现成件，全部实证在册） | 今夜缺口 |
|---|---|---|---|
| **总账** Catalog | 全项目每资产一条户籍，100% 生成器产出，零手填 | ROOR 75 + unified-asset-index 33,249 + CAPCAN 378 + registry_master_index 55 + script-manifest 991 + PG 73 表 + CH system.tables + schtasks 45 | 户籍 schema 统一、PG 落三表、五采集器（fs/PG/CH/schtasks/MCP）、INDEX 树生成器 |
| **总闸** Gate | 六个生命周期动作全过闸 | CREATE-GUARD(creation_token)/RENAME-DEPGRAPH-SYNC/GATE-DELETE-AUDIT/depgraph gate/TRANSLATION-COVERAGE/HOT-FILE-FRESHNESS | LIBRARY-COVERAGE 双向 gate（唯一新造闸）+既有闸接线总账 |
| **总口** Entry | 三视图一体的唯一查询口 | capability_lookup API（378 能力+查询留审计）/MCP 19 server（rule_discovery/blueprint_search/vector_memory 8 collections）/AGENTS.md 冷启动链 | library_lookup 统一 MCP 口 + INDEX 树 v1 |
| **对齐** Align | 事件驱动增量+低频全量兜底 | reconcile_generators 26 条 / align_all 十图 / supply_sentinel / generate_skeleton_health / d8 六 reconciler / REG-DRIFT-001 30 检测器 | 统一调度登记+指纹回写总账 |

## §3 资产户籍 schema v1（总账最小字段集）

```
asset_id      稳定 ID（kind 前缀+稳定派生；改名/搬家不改 ID，只改 home）
kind          module|file|table|registry|doc|task|mcp_tool|backup|pipeline_node|factor|strategy
home          物理真源定位（路径 / conn+表 / 任务计划名）——file|PG|CH|schtasks|startup
fingerprint   sha256(规范形内容)+size+mtime+HEAD+条目数
freshness     built_at+scan_generation（无指纹的馆页=不可引用）
owner_domain  functional_domain（83 域注册表对齐）
status        active|stale|orphan|archived|ghost(馆有盘无)|blind(盘有馆无)
ai_contract   "这是什么+怎么读+读取成本"（能自动填充的自动填，富化长尾分周推进）
```

登记制三条：**出生即有籍**（CREATE 发 asset_id 预登记）、**死亡必销户**（DELETE 先销籍）、**搬家必改籍**（RENAME 同步 home）。

## §4 总闸契约（六个动作，六道闸，全是既有件扩面）

| 动作 | 闸 | 实现路径 |
|---|---|---|
| 新建 | 未登记不得出生 | CREATE-GUARD 扩面：token 之外同步发 asset_id 预登记 |
| 删除 | 未销户不得删除 | GATE-DELETE-AUDIT 扩面=对总账销户 |
| 改名/搬家 | 籍随家动 | RENAME-DEPGRAPH-SYNC 扩面=同步 home 字段 |
| 修改 | 指纹过期即陈旧 | W+1 接 post-commit 钩子；首版=regen 命令+周对账兜底 |
| 查询 | 引用必经总口 | capability_lookup 审计模式推广（软闸）；程序化路径硬闸 |
| 巡检 | 双向对齐即红 | **LIBRARY-COVERAGE（唯一新造闸）**：盘有馆无=blind 红，馆有盘无=ghost 红 |

净零声明：新 gate 仅 LIBRARY-COVERAGE 一件；其数据源收编 detect_orphan_py/depgraph 孤儿检测/audit_directory_integrity。

## §5 单入口三视图（一个门，三种开法）

1. **INDEX 树（启动介质）**：AGENTS.md→ROOR（升级为馆总目）→七馆 L1→域 L2→资产卡 L3；RAPTOR 式分层摘要；零依赖冷启动（服务全挂也能导航）。
2. **library_lookup（运行时口）**：MCP 工具，"X 在哪/是什么/新鲜吗"一次调用；后端=capability_lookup+vector_memory 语义检索；调用全留审计。
3. **仪表盘馆页（人视口）**：照抄 TDM 页交互（P3 殿后）。

## §6 真源 homes 定家表（回应"为什么不全进 DB"）

| 家 | 管什么 | 定家判据 | 搬家触发条件 |
|---|---|---|---|
| 文件（YAML/MD/代码） | 规则/文档/代码/小注册表 | 低频写+强评审+需全文 diff/grep | **不搬**（文件是契约本体） |
| PostgreSQL | 图谱/依赖/血缘/高并发关系型 | 高频写+关系查询+大 N | 73 表继续生长；YAML 注册表"漂移率×消费频率"超阈值逐个搬，由总账记账 |
| ClickHouse | 行情/因子/日志事实 | 大时序事实 | 已在那 |
| schtasks/Startup | 计划任务/登录自启 | 系统层执行面 | 台账化（resource_profile_registry 收编） |

**原则：视图先行（图书馆今夜上线），引擎渐进（搬家按触发条件、由总账记账）。** 搬家不另设里程碑——门装上之后它就是普通施工。

## §7 诚实边界（今夜不解决什么）

1. 12 条既有漂移现行：全部登记进总账（status=orphan/ghost），修复走长尾，部分随施工顺带；
2. 逐资产 ai_contract 富化：首批自动填充，长尾分周；
3. 真源搬家：按 §6 触发条件另立常规批次；
4. 门禁调优：LIBRARY-COVERAGE 首周 warn-only（W+1 收紧为硬闸）；
5. post-commit 指纹钩子：W+1 接线（首版 regen+周对账兜底）。

## §8 成功判据（端到端）

任取一资产（跨七馆）30 秒内经总口定位+指纹核验通过；随机删一文件下轮对齐必红；AGENTS.md 冷启动 5 跳内达任意馆页；红蓝两轮第二轮零缺陷；七馆首轮双向对齐全绿。
