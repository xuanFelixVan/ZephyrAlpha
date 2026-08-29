---
ttl: task_bound
---

> **文档元信息**（_working 临时区豁免规范，EXEMPT-ZONE-FM）：doc_type=asset_ledger · owner=ZephyrAlpha-Owner · status=active · version=2.4.0 · date=2026-08-29 · topic=dashboard_asset_ledger · scope=dashboard。
>
> **姊妹篇**：[2026-08-22-backend-rich-frontend-blind-ledger.md](2026-08-22-backend-rich-frontend-blind-ledger.md)（反向账：后端业务模块→前端盲，40 项已裁定）；[2026-08-22-frontend-backend-gap-ledger.md](2026-08-22-frontend-backend-gap-ledger.md)（正向账：前端有→后端无，83 项）。本账=**全资产盘点扩展版**——不止业务模块，覆盖数据/图谱/因子/语料/注册表/治理工具/文档/执行运维八族。

# 仪表盘资产总账（全项目资产盘点与进/不进裁定底稿）

## 0. 缘起与用法

- **Owner 框架（2026-08-28 拍板）**：仪表盘承载四角色——①交易员盯盘 ②研究员回测与量化分析 ③数据（寻找/管理/治理/数据源监管）④系统（治理/管理/监察）；交易按市场拆 A股/币圈。盘点后发现的**第五角色候选=治理者/审批人**，连同风控/告警的落地形态，Owner 裁定**待本账盘点后统一再定**（见 §7）。
- **本账性质**：逐条打标底稿。每条标七个性质：角色域 / 市场域 / 活死 / 有数 / 前端现状 / 建议处置 / 证据。Owner 逐批复审裁定"进/不进"后，进者进入 IA 映射（既有 36 页扩或新页），再按逐页方法论施工。
- **领任务**：挑"建议=进"且 Owner 已批的项 → 读证据列确认真源 → 施工 → 销项。

## 1. 裁定刀（准入标准）

继承反向账 S1~S4，新增两把：

- **S1 决策相关性**：看了会改变操作/发现异常才占版面（注意力也是风险预算）。
- **S2 消费频率**：日频以上进监控；低频进档案；一次性不进。
- **S3 形态匹配**：监控→dashboard / 总结→推送+存档 / 调试→按需查询。
- **S4 成熟度**：testing 态上页必标"试验中"；candidate 未施工件一律不进（在候选注册表等着）。
- **S5 活死刀（新）**：**会随时间变化的"活状态"进；写完不变的"死文档"留 docs**，仪表盘最多给跳转链接。自动生成文档=构建产物，不进；其背后的**数据真源**（depgraph/注册表/ig 七表）才是进的对象。
- **S6 有数刀（新）**：后端有真源→接线；无真源→负反馈占位（badge/灰化+toast），**不造假数据**。

## 2. 盘点方法与真源

四路只读扫描（2026-08-28）：①数据资产（八表定义/ClickHouse 库表/provider/新闻/质量治理账）②图谱+因子+语料（ig_* 七表/因子注册表/81M 语料/情绪管道）③注册表与治理工具（46 注册表/网关/门禁/守护进程/741 脚本）④文档资产（02 架构域全目录性质判定）。前端现状列=原型 v3.7 36 页实读。所有计数附证据路径，可复核。

## 3. 纠偏记录（盘点抓出的口径错误，引用前必读）

| # | 流传口径 | 实测事实 | 证据 |
|---|---|---|---|
| J1 | "候选注册表 2,933 个模块" | **candidate_module_registry=618 条**；2,933=depgraph build_status=production 节点数（全库 7,809 节点/19,216 边/73 域） | registry_master_index.yaml；design_vs_production.md |
| J2 | 数据总览页"19.5 万新闻去重后" | **演示口径无实测背书**。实测：research_report 类 290,433 行/146,519 唯一 id（08-27）；08-28 重建 200 个月分区已完成，引用前须 `_data_inventory.py` 复测 | 67 号备忘 §1.1；scripts/ch/rebuild_news_data.py |
| J3 | IG 验收报告 INDUSTRY_GRAPH_001_report.md | **实体未寻获**（仓内/D盘/E盘均无）；验收数字以 [2026-08-28-industry-graph-frontend.md](2026-08-28-industry-graph-frontend.md) §1.1 为准 | 四路 Glob/Grep 实证 |
| J4 | BTRUN 实测报告 | 原件不在盘上（.runtime/construction_20260823 已不存在）；可引用锚点=代码头注（daban_board_event_deriver.py / event_sentiment_adapter.py）+ construction_backlog.md | 同上 |
| J5 | 供应链 lead-lag 传导因子"待接" | **已回测证伪**（月 IC=-0.029/周 -0.012），裁定不进因子框架；脚本 backtest_supply_leadlag.py 留档 | scripts/industry_graph/ |
| J6 | 模块总账页 KPI（6,912/3,986/43） | 与实测不符（7,809 节点/production 2,933/候选 618）——接线真源时一并纠偏 | mockup L2843-2847 vs design_vs_production.md |
| J7 | "治理闸 depgraph/creation_token/CAND" | creation_token **全仓零命中**（文件名+内容均无）——命名资产不存在，是字段、别名还是已废，待核实 | 全仓 Glob/Grep |

## 4. 资产总表

**列含义**：角色=交易员/研究员/数据/系统/治理者；市场=A股/币圈/共享；活死=活状态/死文档；有数=✅真源就绪 🟡部分或需实测 ❌无（演示/缺失）。

### 4.A 业务模块域（信号/选股/组合/风控/执行/归因/ML）——不重复盘点

反向账 40 项已全裁定（进 33/不进 7），落盘 8、部分 6、未施工 19。**本账不重列，施工派单以反向账 §5.1 为准。** 唯一增量：BFE 族全部标"角色=交易员或研究员、市场=A股为主"。

### 4.B 数据资产域（角色=数据；Owner 点名"数据的家底与健康"）

| 编号 | 资产（证据） | 规模/状态 | 市场 | 活死 | 有数 | 前端现状 | 建议 |
|---|---|---|---|---|---|---|---|
| DAL-B01 | 数据闸八表注册表（94 号备忘 L132：universe/benchmark/cost_model/risk_limit/strategy/factor/regime_cycle/event_calendar） | A股全量有数；crypto 4/8 已登记（candidate，08-28），strategy/factor/regime_cycle/event_calendar 币版未登记 | 双市场 | 活 | 🟡 | p-datainfo 八表地图=演示框架（与实测有出入，如 universe 演示"5,432 只"vs 注册表 UNI-RULE-001 4,500 只） | **进**：接线 catalogs 八表 yaml 真源，纠偏演示数 |
| DAL-B02 | c1_market 行情库（business_data_categories.yaml） | 90 品类；tick 日均 2,385 万行；库级基线 ~199 GiB | A股 | 活 | ✅ | 零呈现（仅数据总览 1 行 KPI 演示） | **进**：数据组"行情数据"深页（品类/行数/日期覆盖/缺口） |
| DAL-B03 | c3_fundamental 基本面+舆情库 | 23 品类；news_data 08-28 重建完成（旧表保留 news_data_corrupt_20260828 观察） | A股 | 活 | 🟡 | 同上 | **进**：数据组"新闻/基本面"深页；计数须复测（J2） |
| DAL-B04 | 数据源 15 家+监控族（data_asset_registry.yaml L162-569；source_health_check/source_sla_tracker/source_circuit_breaker/alerter） | 17 prod/5 testing/3 planned/1 skeleton/1 退役（iFind） | 共享 | 活 | ✅ | 零呈现 | **进**：数据组**数据源监管**页（Owner 点名）——源清单/SLA/熔断状态/告警流水 |
| DAL-B05 | 数据缺口账 known_data_gaps.yaml + backfill_checker/auto_backfiller | 10 条（completed/accepted/monitoring 三态） | 共享 | 活 | ✅ | 零呈现 | **进**：数据组缺口卡（断流日期/处置态） |
| DAL-B06 | 质量门禁族（quality_gate/integrity_checker/cross_source_validator/cleaning_rule_engine） | production 在码 | 共享 | 活 | ✅ | 零呈现 | **进**：数据治理区（拦截/清洗计数），形态同行不立卡 |
| DAL-B07 | 数据资产注册表 REG-DATAFLOW-001 | 206 条（源 15/数据集 108/作业 88）；CH 表层 154 任务/101 表登记为后续项 | 共享 | 活 | ✅ | 零呈现 | **进**：数据总览页真源（替代演示 KPI） |
| DAL-B08 | CH 健康探针 ch_health_probe（scripts/ops/） | 7×24，60s 间隔，ALIVE/DEAD 告警 | 共享 | 活 | ✅ | 零呈现 | **进**：系统组状态行 |
| DAL-B09 | 情绪打分产物 data/sentiment_batch/（predictions/daily_sentiment/benchmark） | ~12.1 万条；2015 段回填至 06-27、2025 段未开始、daily 聚合待重算（gitignored 本机数据） | A股 | 活 | 🟡 | 情绪页/新闻页演示数据 | **进**：接线时带"回填中"进度标注 |
| DAL-B10 | 研评级产物 data/research_rating/ | 146,519 行（含 2024-07 样本） | A股 | 活 | ✅ | 数据总览 KPI 演示 | **进**：同 B03 深页 |

### 4.C 图谱资产域（角色=研究员/数据）——**本次盘点最大发现**

| 编号 | 资产（证据） | 规模/状态 | 市场 | 活死 | 有数 | 前端现状 | 建议 |
|---|---|---|---|---|---|---|---|
| DAL-C01 | **产业链图谱 ig_* 七表**（PostgreSQL depgraph 库图谱域；DDL scripts/industry_graph/apply_industry_graph_ddl.py） | **686 链/2,911 节点/1,133 边/11,075 环节↔公司映射/1,970 源文档** | A股 | 活 | ✅ | **p-chainmap 仍是"待建设"占位页（08-22 裁定时的状态，后端已竣工前端不知道）** | **进 P0**：产业地图页接线——链浏览/环节节点/个股落位（ig_node_company 按 symbol 查） |
| DAL-C02 | 公司级供应链边+年度指标（ig_company_edge / ig_company_metric） | 58,029 边（三证据源，1,980 多源互证）/23.6 万条指标（客户 HHI/Top1/Top5/稳定性/韧性） | A股 | 活 | ✅ | 零呈现 | **进**：个股档案"供应链卡"（客户/供应商集中度）+产业地图公司层 |
| DAL-C03 | 主题联动监控（theme_linkage_daily.csv 声明产出口径） | 0.85 互证子集 24 链/523 家；**CSV 实体未寻获** | A股 | 活 | 🟡 | 零呈现 | **待定**：先核实产物落盘，再定板块页联动形态 |
| DAL-C04 | lead-lag 传导因子 | 回测证伪（J5） | — | 死 | — | — | **不进**：留档结论即可，不挂"待接"悬念 |
| DAL-C05 | 产业链 RAG 检索索引（chunks.sqlite+embeddings.npy，E:\ 外置） | 76,112 块 × 512 维本地向量；实证命中"光伏硅料四大天王" | 共享 | 活 | ✅ | 零呈现 | **进（远期）**：研究组检索入口；标注外置依赖路径 |

### 4.D 因子与语料/NLP 域（角色=研究员）

| 编号 | 资产（证据） | 规模/状态 | 市场 | 活死 | 有数 | 前端现状 | 建议 |
|---|---|---|---|---|---|---|---|
| DAL-D01 | 因子注册表 factor_registry.yaml（ROOR L583-591） | 140 条 7 类（潘潘课程 546 条入库主因漂移）；口径差异：施工 tracker 记 111 | A股 | 活 | ✅ | p-factor 因子档案页已建，badge 演示数据 | **进**：接线真源（BFE-19 裁定落点） |
| DAL-D02 | 因子产出物：FactorSignal 契约+Feature Store（feature_store_writer/offline_store） | production 在码 | A股 | 活 | ✅ | 零呈现 | **进**：因子档案"因子值/IC 衰减"视图（decay_monitor 有产出） |
| DAL-D03 | 81M 产业链语料（E:\数据下载\产业链数据_P2语料\，manifest.jsonl+DOC-*.md） | 数千文档；登记入口 ig_document 1,970 份 | 共享 | 活 | ✅ | 零呈现 | **进**：产业地图/数据组语料卡；标注外置路径 |
| DAL-D04 | NLP 情绪管道（src/zephyr/nlp/；金标 200 条 F1 0.787） | 推理后端 Ollama qwen3:8b 零样本 v2 | A股 | 活 | ✅ | 情绪页演示 | **进**：随 B09 接线；基线分入页脚说明 |
| DAL-D05 | CAND-NLP-003/004/005、CAND-DAT-021/022、CAND-RES-030 | 全 candidate 未施工 | — | — | ❌ | — | **不进**（S4：候选态一律不进） |
| DAL-D06 | 形态库 chart_pattern_registry.yaml + 识别引擎 unified_pattern_engine.py + 执行映射库 | 256 条 8 大类（candlestick 77/chart_pattern 62/缠论 15/elliott 8/structure 54 等） | A股 | 活 | ✅ | 技术分析页画线形态=演示 | **进**：形态命中真源化（G-四 人机共校通道的上游） |
| DAL-D07 | 纠错样本库（__fbQueue 后台） | **0 条未建库**，仅前端演示桩 | — | — | ❌ | 各页⚑报错按钮=演示 | **不进**（I-2/CAND 建了再说） |

### 4.E 注册表群（角色=数据/系统；46 表，registry_master_index 自动索引）

| 编号 | 资产簇 | 规模/状态 | 活死 | 有数 | 前端现状 | 建议 |
|---|---|---|---|---|---|---|
| DAL-E01 | **业务注册表 18 表**（ROOR L552：合计 1,268 条）——策略 146/模型 8/形态 256/风控限额/技术指标 41/事件日历 14/宏观 16/组合模型 11/席位 16/实验 5/字段字典 259 等 | catalogs/ 下 yaml SSoT 群 | 活 | ✅ | p-reglib 已建（网格+详情+搜索），**演示数据** badge | **进 P0**：接线 ROOR/registry_master_index 实测计数（接线成本最低、见效最快） |
| DAL-E02 | 候选模块注册表（618 条：promoted 332/candidate 177/deferred 31 等；CAND-CRYPTO ×10/CAND-DAT ×26 等族） | version 1.1.3 | 活 | ✅ | p-modledger 演示"候选 43"（J6 纠偏） | **进**：模块总账接线+计数纠偏 |
| DAL-E03 | depgraph 模块全景（7,809 节点/19,216 边/73 域；production 2,933） | PostgreSQL+depgraph.db 双载体 | 活 | ✅ | p-pano 架构全景+p-modledger KPI=演示口径 | **进**：两页接线真源 |
| DAL-E04 | 治理簇注册表（architecture_issue 713/cross_module_dependency 132/directory 87/gate 43） | catalogs/ | 活 | ✅ | 零呈现 | **进**：系统组"治理账"区（按 S1 只上计数与异常，不全文） |
| DAL-E05 | 密钥注册表 secret_registry.yaml | **82 keys**；90 天轮换（OKX 08-28 已登记） | 活 | ✅ | 零呈现 | **进（脱敏）**：系统组"密钥健康卡"——只显示数量/轮换到期日/缺失告警，**永不显示值** |
| DAL-E06 | 基础设施簇（scripts_registry 741 脚本/session_logs 29 sessions 等） | script-manifest.yaml | 活 | ✅ | 零呈现 | **进**：系统组计数行（低优先） |

### 4.F 治理与运维工具链（角色=系统）

| 编号 | 资产（证据） | 规模/状态 | 活死 | 有数 | 前端现状 | 建议 |
|---|---|---|---|---|---|---|
| DAL-F01 | GitCommitGateway 提交网关（scripts/git_commit.py；in-process 门禁 103 文件） | 队列回执 done 89/dead 42；串行锁 serializer.lease | 活 | ✅ | 零呈现 | **进**：系统组提交队列卡（dead 42 是关注点） |
| DAL-F02 | 门禁审计 .runtime/gate_audit/（15 个 jsonl：safe_rmtree/ops_guard_delete/protected_paths_bypass 等） | 持续追加 | 活 | ✅ | 零呈现 | **进**：系统组门禁命中流水（计数级） |
| DAL-F03 | pre-commit 门禁（.pre-commit-config.yaml 1,081 行 60+ hook） | 多数已转硬阻断 | 活 | ✅ | p-govana=OLAP 未配置 N/A | **进**：govana 页有真源后可接（G4 反误导规范沿用） |
| DAL-F04 | process_reaper（计划任务 10 分钟 one-shot）+ ghost_suspects.json 状态机 | 08-28 根治重启 | 活 | ✅ | 零呈现 | **进**：系统状态页守护进程区 |
| DAL-F05 | 守护进程族：drift_watchdog / write_audit / serve_8010_watchdog / governance_watchdog | 各带 pid/log | 活 | ✅ | 零呈现 | **进**：同上（存活/最近动作一行一个） |
| DAL-F06 | CloneGuard 克隆审计（.runtime/clone_guard_audit/） | 按触发产出 JSON | 活 | ✅ | 零呈现 | **进**：系统组一行状态 |
| DAL-F07 | compliance_scan.py 前端合规扫描器 | 手动工具，白名单 DS v3.5.1 | 活 | ✅ | 视觉会话领土 | **登记不进功能线**（视觉线自决） |

### 4.G 文档资产（S5 活死刀的主战场）

| 编号 | 资产簇 | 规模/性质 | 活死 | 建议 |
|---|---|---|---|---|
| DAL-G01 | 02 架构域自动派生文档（02 域文档 75+治理报告 71+决策架构 23+数据流 14+battle_map 13+算法全景 14+全局图 7+入口 2≈**219 份**） | 全 depgraph/dataflow/decision/battle_map 四库构建产物，禁手编 | 死（可再生） | **不进**：文档本体不进；其**数据真源**已由 E03 覆盖（仪表盘吃库不吃文档） |
| DAL-G02 | design_memos 64 份（active 53；1x 地基 11/2x Alpha 10/3x 组合风控 8/4x 执行 6/5x 验证 8/6x 治理 9/9x 远期 5） | 人工叙事文档 | 死（叙事） | **不进正文**；可在相关页面页脚给"设计依据"跳转链接（如风控页→31 号仓位备忘） |
| DAL-G03 | 09_ai_architecture 20 份+04 章程/手册+03_modules 蓝图 200+ | 人工设计/规范 | 死 | **不进**（docs 留档，仪表盘不做文档浏览器） |
| DAL-G04 | 施工进度跟踪 construction_progress_tracker.md（31+ 任务全 merge）+长城任务账 | 人工活账 | **活** | **进**：p-task 任务进度页真源候选（现为演示） |
| DAL-G05 | _archive 31 份+deprecated+一次性裁决报告 ~30 份 | 死档 | 死 | **不进** |

### 4.H 执行与交易资产（角色=交易员）

| 编号 | 资产（证据） | 规模/状态 | 市场 | 活死 | 有数 | 前端现状 | 建议 |
|---|---|---|---|---|---|---|---|
| DAL-H01 | QMT 桥文件双分区（E:\qmt_bridge_sim 模拟 / E:\qmt_bridge 实盘双账户） | orders/ack/quote CSV 实时导出，1s/10s 间隔 | A股 | 活 | ✅ | 全景总览 L3 账户灯=演示 | **进**：灯语义接线桥心跳+回执+持仓时间戳（I-2 已登记） |
| DAL-H02 | OKX provider（okx_provider.py+测试；MATURITY 仍 planned） | 代码就绪；**未接调度、CH 无 crypto K 线表** | 币圈 | 活 | 🟡 | 币圈各页演示+"待接入"badge | **进**：落库管道建成前维持负反馈（S6，不造假） |
| DAL-H03 | 交易规则参数 TradingRulePack（ex_core/rules/，CAND-CRYPTO-006 已 promoted）+风控阈值 | production | 双市场 | 活 | ✅ | 零呈现 | **进**：系统/数据组**配置只读视图**（参数看得见、改不了——编辑是后端事） |
| DAL-H04 | QMT 导出设置/指令文件规范（多账户分区） | 运维约定 | A股 | 死 | — | — | **不进**（S5：约定文档留 docs） |

### 4.I 告警与审批资产（形态**待定**——Owner 裁定盘点后再定，§7 决策入口）

| 编号 | 资产（证据） | 规模/状态 | 有数 | 现状 | 备注 |
|---|---|---|---|---|---|
| DAL-I01 | 告警管道 alerter.py（300s 冷却）+ ch_health_probe 告警 + source_circuit_breaker | production | ✅ | 告警落日志/推送，前端无流 | 统一告警流的供给端 |
| DAL-I02 | 自治门禁 autonomy_gate（.runtime/autonomy_gate/alerts.jsonl+queue ticket） | 在跑 | ✅ | 零呈现 | 审批候选 |
| DAL-I03 | 人工闸门操作点：实盘下单审批/距强平 <10% 强减审批/human_gated 族 | 规则在册 | ✅ | 零呈现 | "待我审批"收件箱的供给端 |
| DAL-I04 | CAND 评审流（618 条生命周期） | 在册 | ✅ | p-modledger 演示 | 治理者视角 |
| DAL-I05 | 提交队列回执（done 89/dead 42）+ gate_audit 异常 | 在跑 | ✅ | 零呈现 | 可归入系统组或统一告警流 |

### 4.J 可视化模块候选（全量扫描批 2026-08-28）

> **方法**：depgraph 扫描缓存 7,675 模块×73 域全量过滤→四路并行精读文件头（docstring+[MATURITY] 实证）→S1 铁律（人看了会改变操作才收；中间件/管道/运维件不收）→两账去重（反向账 40+正向账 97 已登记项不收）。**治理域按 Owner 裁定不收**（D_GOVERNANCE/AUTONOMY_CORE/FBL 等）；**D_CROSS_ASSET 实证为空壳域**（7 行全包骨架，C11 宏观比价雷达仍无后端）。
> **产出**：账外富矿 **192 件候选**（按目标页分组见下）+**反差件 8 件**（登记"需新建/缺"实则已落码，正向账 v2.4.0 已同步扩注）。成熟度以文件头 [MATURITY] 为准；testing 上页必标"试验中"、design 一律标"规划中"（S4）。

#### J-0 反差件 8 件（登记为缺、实则已落码——施工成本≈纯接线）

| 缺口账条目 | 实际后端（成熟度） | 说明 |
|---|---|---|
| C1 多指标共振置信度（标 P0 需新建） | `signal_ashare/index_resonance_scorer.py`（testing） | 七族投票+共振 x/7+置信度，文件头注明 GAP-F-31 |
| C8 蒙特卡洛压测 | `signal_ashare/mc_path_simulator.py`（testing） | GBM+bootstrap 双法，p5/p50/p95 分布带，自述"前端画扇形图用" |
| C18 情绪族（标"设计态未施工"） | MOD-SIG-033 接力情绪引擎（prod）+MOD-SIG-025 七维评分（prod）+`sentiment_cycle.py` 五阶段贝叶斯（new） | 三件套两件半现成 |
| C21 实验门控 DSR/PBO（标"planned 未建"） | DSR=`simulation/deflated_sharpe_calculator.py`（prod）+PBO=`backtest/core/cpcv.py`（prod）+裁定器+四层门禁 MOD-SIM-028（prod） | **假缺口**：真缺仅页面呈现+meta-labeling |
| C22 W4 多空辩论（缺口⑧） | `MOD-PLAN-013 trading_debate.py`（testing） | 四角色链+风控 veto 恒优先，已落码闭合 |
| D2 地缘数据（标"评估源"） | `MOD-ALT-014 geopolitical_risk_analyzer.py`（prod）+地缘→板块传导表 | 只剩采集源接线 |
| B26 板块页管线 | `counter_trend_board.py`（testing，逆势四卡后端）+`sector_detail_enricher.py`（testing，周期五态+拉升原因） | 与 R15 抗跌榜同族 |
| C25 明日推演（R13 登记新模块） | `MOD-SIG-037 next_day_8state_forecast.py`（**prod**）次日 8 态概率 | 核心上游已在码，新模块收窄为"联动层"（盘面→操作映射） |

#### J-1 作战指挥（15 件——W 族隐藏真源大批在码）

| 模块 | 产出物（形态） | 成熟度 |
|---|---|---|
| MOD-SIG-066 war_pool_generator | 今日作战池 2~3 票，主线×催化交集【卡组】 | testing |
| MOD-SIG-037 next_day_8state_forecast | 次日 8 态概率分布+置信度【8 格概率带】 | **prod** |
| MOD-PLAN-019 scenario_playbook | 9 情景模板库+盘中实时匹配+PROPOSED→CONFIRMED→EXECUTED 确认流【预案卡+状态机】 | **prod** |
| MOD-PLAN-003 closing_session_decision | 14:45 尾盘加减仓决策【决策卡】 | prod |
| MOD-PLAN-014 sit_out_list | 禁做清单三源合成（blackout/禁反手/不撬板）【警示条】 | testing |
| MOD-PLAN-011 daily_trade_plan | 今日交易计划（拟买/拟卖+8% 截断）【清单卡】 | testing |
| MOD-PLAN-009 scenario_attribution_stats | 预案三维归因：预测对≠执行对≠赚钱分开算【9 格×3 维矩阵】 | testing |
| MOD-PLAN-013 trading_debate | 四角色多空辩论+风控 veto【辩论台卡】 | testing |
| MOD-PLAN-015 auction_hit_recorder | 竞价三细节+10:00 命中格判定落库【9 格点亮】 | testing |
| MOD-PLAN-004 overnight_boundary_reviser | 隔夜三通道边界修正【通道明细表】 | testing |
| MOD-PLAN-007 llm_premarket_analysis | LLM 盘前注解（PIT 合规冻结）【注解卡】 | testing |
| MOD-SIG-038 cross_market_conduction_sensor | 外盘异动→A股传导系数+影响分档【KPI 卡】 | prod |
| MOD-SIG-117 overnight_conduction_model | 隔夜 β+30 分钟衰减+事件四类影响评分【评分+时长表】 | prod |
| MOD-POS-001 position_sizing_engine | 13 硬约束仓位方案（半 Kelly/参与率否决）【约束清单】 | prod |
| MOD-TRADING-011 manual_instruction_channel | 人工指令双闸+DRIFT 对账（人在环正规入口）【指令流水】 | design |

#### J-2 大盘分析（18 件——整页真源一夜可点亮）

| 模块 | 产出物（形态） | 成熟度 |
|---|---|---|
| MOD-REGIME-008 index_regime_panel+brief | 四指数 7 态 regime 概率面板+三腿简报【4×7 热力面板】 | testing |
| MOD-REGIME-014 style_regime_model | 大小盘×价值成长四象限风格态【四象限图】 | prod |
| MOD-SIG-036 market_state_sensor | 趋势×波动 9 网格市场状态【九宫格】 | prod |
| MOD-SIG-039 regime_change_detector | 牛熊切换相位（WATCH→TRIGGERED→CONFIRMED）+概率【状态灯+概率条】 | prod |
| MOD-SIG-041 market_lifecycle_phase | 春夏秋冬四季+操作约束（冬禁抄底/秋强制离场）【阶段带+约束灯】 | prod |
| MOD-REGIME-012 market_forecast_fusion | 多信号融合概率分布（只出分布不出点位）【分布条】 | prod |
| MOD-REGIME-013 volatility_squeeze_breakout | 波动挤压+突破方向概率【挤压灯】 | prod |
| MOD-REGIME-007 cross_sectional_features | 截面离散度/平均相关/波动离散/动量宽度【4 线图】 | testing |
| MOD-DATA-061 sector_intraday_aggregator | 盘中板块四榜（资金/涨跌结构/涨速/新开板）【四榜滚动】 | testing |
| MOD-DATA-062 market_breadth_collector | 分钟级宽度快照（涨停/炸板/封单/跌停/成交额）【宽度时序】 | testing |
| MOD-DATA-063 intraday_sentiment_loop | 盘中情绪分+加速度【情绪曲线】 | testing |
| MOD-L00-009 sector_report_builder | 板块盘后五维报告（Top10/五态/梯队/主线/虹吸）【报告卡】 | testing |
| MOD-L00-004 daban_board_event_deriver | 封板历史全史推导（封板时间/开板次数/连板，1990+ 可回溯）【封板直方图】 | testing |
| MOD-INT-EVENT-ANOMALY event_anomaly_detector | 异动雷达（脱钩+超额双条件，实证捕获 78% 重大事件前异动）【雷达流】 | design |
| MOD-INT-EVENT-IPO event_ipo_siphon | IPO 虹吸四级+仓位动作【预警卡】 | design |
| MOD-RK-10 ashare_systemic_risk_detector | 系统性风险 5 信号→三级+逃生指令【点亮板】 | prod |
| MOD-RK-34 systemic_risk_alert_state_machine | 组合侧绿黄橙红黑 5 级+减仓/禁开/清仓指令【五色带】 | prod |
| MOD-PF-011 exposure_manager | 行业主动敞口+轮动增减配建议【敞口条】 | design |

#### J-3 板块全景（5 件）

| 模块 | 产出物（形态） | 成熟度 |
|---|---|---|
| MOD-SIG-064 mainline_probability | 主线概率%（RRG/接力/资金/梯队四因子）【概率榜】 | testing |
| sector_rotation_score_mapping+sector_rrg/pullback | RRG 象限+强度+回踩→轮动综合评分【RRG 旋转图】 | new |
| counter_trend_board | 逆势榜四卡后端（逆势上涨/下跌段资金流入/率先反弹/最抗跌）【四卡】 | testing |
| sector_detail_enricher | 板块周期五态+拉升原因五类【详情维度】 | testing |
| MOD-RK-046 risk_contagion_modeler | 板块/产业链冲击传导路径+传染评分（Diebold-Yilmaz 轻量）【传导网络图】 | prod |

#### J-4 市场情绪（8 件）

| 模块 | 产出物（形态） | 成熟度 |
|---|---|---|
| MOD-SIG-114 crowd_game_simulator | 北向/公募/游资/散户四方合力+分歧熵【堆叠力图】 | prod |
| MOD-SIG-033 接力情绪引擎 | 6 因子+情绪周期 4+1 阶段【周期指针】 | prod |
| MOD-SIG-025 七维情绪评分 | 七维合成情绪分【仪表】 | prod |
| sentiment_cycle | 五阶段贝叶斯定位+3 策略×5 阶段部署矩阵【阶段图】 | new |
| MOD-INT-NEWS-NIGHT nightly_sentiment_window | 隔夜情绪窗落库（18:00→08:00 幂等）【读数卡】 | testing |
| MOD-INT-MKT-INTERPRETER llm_market_interpreter | 三路市场解读（主题/情感/影响/置信度）【解读卡】 | testing |
| MOD-L00-004 northbound_hold_analysis | 准北向季度净流入+增减仓双榜（港交所停发日频后唯一窗口）【曲线+双榜】 | prod |
| MOD-ALT-004 sentiment_engine | 三源复合情绪+252 日分位+冰点/过热判定【温度计】 | design |

#### J-5 技术分析/个股行情（4 件，另 2 件见 J-0）

| 模块 | 产出物（形态） | 成熟度 |
|---|---|---|
| MOD-SIG-124 fake_move_distribution | 假动作 6 模式概率+>85% 暂停追涨告警【预警卡】 | prod |
| MOD-ML-008 meta_learning_rsi | 按 regime 的 RSI 最优周期推荐（fail-closed 回默认）【KPI 卡】 | prod |
| overnight_return_expectancy | 开仓期望值三门槛（E>0.5%∧盈亏比>1.5∧成本>2ATR）【门槛灯】 | testing |
| extreme_sentiment_reversal_detector | 双冰点配对+Capitulation 百分打分卡【反转卡】 | testing |

#### J-6 持仓监控（11 件）

| 模块 | 产出物（形态） | 成熟度 |
|---|---|---|
| MOD-SIG-045 survival_time_predictor | 止盈止损"还有多久"生存分析（全库唯一时间维度）【生存曲线】 | prod |
| MOD-TRADING-002 pnl_calculator | 盈亏+A股三费（CTR-TRD-01 唯一口径真源）【瀑布卡】 | prod |
| MOD-RK-07 concentration_monitor | HHI/行业/个股三维集中度三级告警【仪表】 | prod |
| MOD-POS-003 position_drift_monitor | 组合±2%/单票±3% 两级漂移告警【偏离条】 | prod |
| MOD-POS-005 cross_strategy_position_merger | 跨策略净额合并权重簿【堆叠条】 | prod |
| MOD-POS-012 correlation_regime_monitor | 相关性三档+分散失效预警【档位灯】 | prod |
| MOD-POS-015 position_time_budget | 持仓时间预算三态【进度条】 | prod |
| MOD-POS-019 position_behavior_classifier | 持仓行为五分类（套牢/过早止盈/呆滞）【行为徽章】 | prod |
| MOD-POS-025 core_satellite_allocator | 核心/卫星分组+做T信号（仅卫星仓出）【环形图】 | prod |
| MOD-PF-002 multifactor_holding_drift_monitor | 持仓期因子/行业/权重三维偏差【热力条】 | prod |
| MOD-POS-013 position_risk_budget_allocator | ERC 风险贡献（实际 vs 预算）【条形图】 | prod |

#### J-7 盘中实时/执行监控（18 件）

| 模块 | 产出物（形态） | 成熟度 |
|---|---|---|
| 35 号 drawdown_state_machine | 回撤六态机+RECOVERY 阶梯+KILL 仅人工复位【档位灯+阶梯条】 | prod |
| 35 号 drawdown_attribution | 回撤五问诊断（行为性 vs 统计性，BIASED=停实盘修执行）【归因卡】 | prod |
| 35 号 drawdown_forced_rest | Level4 强制休息 5 交易日倒计时【倒计时徽条】 | prod |
| MOD-RK-24 risk_veto_engine | 下单前 7 硬规则否决+结构化理由【否决流水】 | prod |
| MOD-RK-05D var_intraday_recalc | VaR 盘中 7 触发重算（风控什么时候醒的全程可见）【触发时间线】 | evolving |
| MOD-RK-40 post_entry_instant_validator | 买后 T+5/15/30min 三档快速纠错（WATCH→REDUCE_HALF→EXIT_ALL）【时点验证条】 | design |
| MOD-TRIG-001 trigger_registry | 四类扳机注册表+优先级仲裁+冷却状态【扳机清单】 | prod |
| MOD-EX-024 pre_execution_checker | 下单前四级硬检查（默认拒绝）【四级闸灯】 | prod |
| MOD-L06-001 cancel_rate_guard | 撤单率双线+申报计数（程序化新规生存项）【双线仪表】 | prod |
| MOD-L06-001 rejection_action_handler | 拒单四动作+策略冻结表（只增，人工解冻）【冻结名单】 | evolving |
| MOD-L06-001 trading_halt_resolver | 停牌三场景处置+预占释放【警示条】 | prod |
| MOD-XS-005 algo_trading_engine | 6 算法切片执行（母单→子单）【切片进度】 | prod |
| MOD-POS-018 intraday_position_constraint | 盘中意图三校验（T+1 冻结量可视）【校验行】 | prod |
| MOD-POS-024 position_adjudication_center | 四层裁决漏斗+旁路阻断红标【漏斗图】 | prod |
| MOD-PA-002 signal_synthesis_combiner | 多策略投票+共振分级+冲突裁决【投票矩阵】 | prod |
| MOD-PA-006 batched_position_builder | 分批建仓计划+降级标记【甘特条】 | prod |
| MOD-PLAN-020 track_fusion | 四轨融合指令（应急>人工>自动，反向升 L6 不出指令）【信号面板】 | prod |
| MOD-PLAN-022 plan_deviation_monitor | 计划偏差 z 监控+计划外强信号三重闸【z 仪表】 | prod |

#### J-8 做T分析（3 件）

| 模块 | 产出物（形态） | 成熟度 |
|---|---|---|
| MOD-SIG-132 day_trade_pnl_estimator | 做T净盈亏预估（价差−佣金−印花税−冲击）【KPI 卡】 | prod |
| t0_point_analyzer | 做T点位+回验一体（A5/A6 专用件）【点位引擎】 | testing |
| t0_cost_model | 做T往返成本+0.3% 正期望门槛（最低 5 元佣金效应）【成本卡】 | testing |

#### J-9 盘后复盘（24 件）

| 模块 | 产出物（形态） | 成熟度 |
|---|---|---|
| MOD-TRADING-013 three_way_reconciliation | 三向对账台账状态机（OPEN→INVESTIGATING→RESOLVED）【台账看板】 | prod |
| MOD-TRADING-012 eod_processor | 日终 NAV/P&L 快照+漂移检测【快照卡】 | design |
| MOD-RK-23 strategy_deviation_monitor | 实盘 vs 回测偏离双口径+>50% 退役评估【偏离曲线】 | prod |
| MOD-RK-33 copula_garch_joint | 联合尾部 VaR/ES（多只持仓同时暴跌风险）【热力矩阵】 | prod |
| MOD-RPT-009 review_orchestrator | 日/周/月三频复盘编排（机器自动，人只看 FAIL）【复盘日历】 | prod |
| MOD-RPT-009 ai_review_summary | 一键战报 LLM 五段模板+降级兜底【战报卡】 | testing |
| MOD-RPT-026 ashare_performance_audit | 绩效审计五类+优化建议【审计表】 | prod |
| MOD-RPT-029 prediction_calibration_monitor | 参数校准评审工单（永不自治改参）【工单列表】 | testing |
| MOD-RPT-031 deviation_attribution_decomposer | 回测-实盘四因子分解（前瞻残留单列）【瀑布图】 | testing |
| MOD-RPT-033 decision_trace_chain | 决策链四段泳道反查（任意成交→最初信号）【泳道时间线】 | prod |
| MOD-RPT-034 trading_review_engine | 日终自我合规审查四模式（监管问询前自查证据）【审查卡】 | prod |
| MOD-RPT-035 strategy_explainability_reporter | SHAP+LIME 双归因+可解释性门控【重要性条】 | prod |
| MOD-RPT-006 regulatory_report_generator | 4 类监管报告+防篡改哈希【报告清单】 | prod |
| MOD-PF-007 performance_attribution_engine | Brinson 三因子+IC 降级检测+拥挤建议【瀑布图】 | prod |
| MOD-PF-002 multifactor_rebalance_trigger | 换仓 Inaction Cost 门控（为什么不换也有量化理由）【决策卡】 | prod |
| MOD-PF-014 rebalance_cost_analyzer | 调仓成本四拆解（含机会成本）【成本饼】 | prod |
| MOD-EX_SOR_EXT-001 slippage_analyzer | 滑点多基准+冲击/时机/价差三因子归因【归因条】 | prod |
| MOD-EX_SOR_EXT-002 execution_quality_scorer | 执行四维评分+历史追踪【雷达图】 | prod |
| MOD-EX_SOR_EXT-003 transaction_cost_optimizer | 成本六项分解+优化建议【分解条】 | prod |
| MOD-EX-062 execution_strategy_selector | ADV 分档算法选择记录【流水表】 | prod |
| MOD-EX-064 execution_param_optimizer | 执行参数优化提案+人工确认队列【确认队列】 | prod |
| MOD-CMP-011 intraday_manipulation_detector | 操纵三规则命中+零命中自证留痕（监管自证资产）【命中表】 | prod |
| MOD-CMP-014 info_asymmetry_manipulation_detector | 信息空窗+嫌疑评分+回避名单（供漏斗排除）【名单表】 | prod |
| MOD-PA-014 strategy_screener_3d | 新策略入库三维裁决【评分卡】 | prod |

#### J-10 实盘全景总览（9 件）

| 模块 | 产出物（形态） | 成熟度 |
|---|---|---|
| MOD-RK-KPI survival_line_monitor | 系统生存线三指标（超额>0∧MaxDD<15%∧Sharpe≥0.8，私募实证锚定）【生死灯】 | testing |
| MOD-POS-020 cold_start_progression | 新策略 30/60/100% 阶梯爬坡+回退【阶梯卡】 | prod |
| MOD-POS-023 live_nav_recorder | 实盘净值 vs 沪深300【净值曲线】 | testing |
| MOD-PA-003 multi_strategy_capital_allocator | 策略资金分配（MaxDD>15% 全线减半）【分配条】 | prod |
| MOD-PA-004 strategy_correlation_gate | 策略相关性门禁（同质化拦截）【矩阵】 | prod |
| MOD-PA-007 regime_meta_allocator | Regime 元分配（Shrinkage 只减不增节流）【占比条】 | prod |
| MOD-PA-013 maxdd_limit_allocator | 逐策略回撤预算三档（NORMAL/DERATE/SUSPEND）【预算条】 | prod |
| MOD-RPT-030 alert_aggregator | 三源统一告警流（风控/数据质量/回测）【告警卡】 | testing |
| MOD-PF-012 strategy_capacity_estimator | 策略容量+80% 利用率预警【容量仪表】 | design |

#### J-11 因子档案（12 件——"因子生命链"全 prod 除注明）

| 模块 | 产出物（形态） | 成熟度 |
|---|---|---|
| ic_ir_evaluator | 多因子批量 IC/IR/OOS 评估报告【表格】 | prod |
| ic_decay | IC 衰减曲线+半衰期【曲线】 | prod |
| decay_monitor | 半衰期阈值告警+轨道分位【状态灯】 | prod |
| multifactor_crowding_monitor | 拥挤度三代理综合分+REDUCE 分级动作（崩盘前兆）【KPI+灯】 | prod |
| multifactor_decay_lifecycle | 因子 6 态生命周期+权重乘数【状态灯+表】 | prod |
| layered_backtest | 五分层收益+多空 spread（单调性图形证据）【柱状+曲线】 | prod |
| three_level_judgment | 优秀/合格/淘汰三档【徽章】 | prod |
| factor_attribution | 时间+行业双维归因【热力图】 | prod |
| multifactor_pit_backtest | 5 层 PIT 断言回测逐日记录【曲线+表】 | prod |
| factor_pool_manager | 因子池水位+末位淘汰名单【KPI+表】 | prod |
| correlation_overfitting_audit | PDR/PSI/DFR 三指标+LIKELY_OVERFIT 裁定【状态灯】 | testing |
| factor_model_co_evaluator | 因子×模型双向贡献+淘汰清单【双向热力图】 | prod |

#### J-12 回测结果（16 件）

| 模块 | 产出物（形态） | 成熟度 |
|---|---|---|
| backtest/core/metrics | 全套绩效（Sharpe 10Y 修正/Sortino/MaxDD/胜率）【KPI 组】 | prod |
| decision_gate | IS→WFA→OOS 三阶段门控（不可跳级）【阶段进度条】 | prod |
| overfitting_detector+adjudicator | 三维过拟合检测+三检验裁定（DSR/参数扰动）【状态灯+表】 | prod |
| cpcv（compute_pbo） | PBO 回测过拟合概率单数字【KPI】 | prod |
| strategy_cpcv_matrix | 策略级 CPCV 稳健分排名【排名表】 | prod |
| regime_validation/c1_comparator | Shrinkage 开关四指标对比+一票否决【对比表】 | prod |
| backtest/services/decay_monitor | 策略衰减 4 级告警（STABLE→CRITICAL）【状态灯+曲线】 | prod |
| report_generator | 自包含 HTML 回测报告【报告卡】 | prod |
| param_analyzer | 参数敏感度+平台区选点（悬崖参数可见）【敏感性曲线】 | prod |
| anomaly_diagnoser | 回测异常诊断+逐条修复建议【诊断表】 | prod |
| result_comparator | 两回测差异+显著性检验【对比表】 | prod |
| simulation/risk_simulator | 三方法 VaR/CVaR+回撤恢复期【KPI+分布】 | prod |
| parameter_robustness_tester | 参数稳定区间（窄峰=高风险）【稳定区高亮】 | prod |
| look_ahead_bias_detector | 未来函数扫描（前瞻=回测作废）【问题表】 | prod |
| almgren_chriss_impact_model | 冲击成本报价（参与率选错直接亏钱）【成本曲线】 | prod |
| market_twin_simulator | ABM 市场孪生+统计特征校验【校验表】 | prod |

#### J-13 实验历史（6 件）

| 模块 | 产出物（形态） | 成熟度 |
|---|---|---|
| deflated_sharpe_calculator | DSR 多重测试修正 Sharpe（0.95 显著线）【KPI】 | prod |
| overfitting_protection_gate | 因子/策略/信号/ML 四层过拟合统一门禁【四层灯】 | prod |
| default_experiment_pipeline | A/B 对照效应量+p 值+显著性结论【对比表】 | prod |
| reproducibility_manager | 环境快照+种子+hash 复现核验（hash 不一致=不可信）【状态灯】 | prod |
| meta_learning_evolution | 跨任务经验库+历史最佳配置推荐【经验表】 | prod |
| prediction_calibration（见 J-9） | — | — |

#### J-14 模型页（新页候选，11 件）

| 模块 | 产出物（形态） | 成熟度 |
|---|---|---|
| MOD-ML-009 learning_effect_feedback | 上线后 IC+衰减+retrain 回喂【IC 曲线】 | prod |
| MOD-ML-005 adversarial_robustness_validator | 多档噪声扰动漂移+降级报告【扰动曲线】 | prod |
| MOD-ML-018 continual_learning_antiforget | 微调抗遗忘门禁（旧 regime 降>5% 拦截）【门禁表】 | prod |
| MOD-ML-004 gray_release_shadow_deployer | 影子部署观测记录（effective 恒 False 红线）【会话表】 | prod |
| MOD-ML-016 decision_tree_decision_architecture | 决策 GBM+SHAP 解释+人工干预留痕【解释卡】 | prod |
| MOD-ML-DENSITY density_quantile_trainer | 分位数密度头 pinball loss+覆盖率【覆盖率图】 | prod |
| MOD-ML-010 qnn_two_stage | 两阶段分位数预测+degraded 标记【扇形图】 | prod |
| MOD-MLS-001 model_drift_monitor | serving 四维漂移（PSI/JS/性能/IC）+事件【四维灯】 | prod |
| MOD-MLS-002 model_compression_accelerator | 三阶段压缩验证（不显著降才放行）【阶段条】 | prod |
| MOD-FAC-005 factor_model_co_evaluator | 因子×模型双向利用度（见 J-11）【热力图】 | prod |
| MOD-ML-020 reproducibility_manager | 见 J-13 | prod |

#### J-15 研评级（新页候选，14 件）

| 模块 | 产出物（形态） | 成熟度 |
|---|---|---|
| nlp/research_rating.py | 研报结构化提取：评级立场/变动/目标价【变动流】 | design |
| MOD-ALT-009 research_report_collector | 评级上调/下调事件流（快照 diff 检测）【事件流】 | prod |
| MOD-INT-LLM-FUND llm_fundamental_analysis | 三 Agent 基本面裁决（定量分+置信度）【裁决卡】 | testing |
| MOD-INT-RESEARCH-AGENT llm_research_agent | ReAct 研究助手（工具白名单+事实回查+advisory_only）【助手面板】 | prod |
| MOD-INT-FACT-LEDGER universal_fact_ledger | UFL 事实账本+双锁锚定（数字必须检索自账本）【锚定角标】 | prod |
| MOD-INT-EPISODIC-MEM episodic_memory_store | 相似历史案例检索（上次类似盘面怎么判对不对）【案例卡】 | testing |
| MOD-KNW-001 kb_engine | 八 Collection 知识库统一门面+FTS5【检索台】 | prod |
| MOD-KNW-002 knowledge_quality_assessor | 知识四维质量分+低分隔离【质量分布】 | prod |
| MOD-KNW-008 rag_pipeline | RAG 问答+引用溯源（chunk 回链）【问答卡】 | prod |
| MOD-KNW-011 research_project_aggregate | 研究项目四态看板（假设/证据/实验/因子挂载）【看板】 | prod |
| MOD-KNW-012 research_catalog | 研究资产目录+引用网络【目录+网络】 | prod |
| MOD-KNW-013 paper_tracker | arXiv 订阅+LLM 摘要+关键词趋势（学术→因子假说传送带）【趋势卡】 | prod |
| MOD-EVIDENCE_CHAIN evidence_chain+hypothesis_registry | 假设状态机+证据挂链+SHA-256 防篡改（证伪史不靠人脑）【假设账本】 | testing |
| MOD-ALT-013 alt_data_signal_extractor | 另类信号统一出口+IC 测试+正交化（alphalens 单机版）【IC 面板】 | prod |

#### J-16 新闻舆情（7 件）

| 模块 | 产出物（形态） | 成熟度 |
|---|---|---|
| MOD-NLP-DUALTAG-001 news_dual_tagger | 新闻双标签：可预测性+预期差（超/符合/低于）【双标签列】 | testing |
| MOD-NLP-IMPACT-001 news_impact_grader | 影响 A/B/C 三级+热点主题聚类+多源共振【分级签+主题榜】 | testing |
| MOD-INT-AISA news_sentiment_analyzer | 情绪打分+1h 窗口指数+突破阈值事件【指数曲线】 | design |
| MOD-INT-NEWS-LINK news_symbol_linker | 新闻→标的关联+ambiguous 统计【覆盖仪表】 | testing |
| MOD-INT-EVENT-CHAIN event_chain_causal_graph | 事件 Granger 因果+贝叶斯条件概率（降准→哪些板块动）【因果链图】 | prod |
| MOD-INT-EVENT-SCORE event_score | 事件影响评分（SUE+EAR+ORJ）+三道触发线【评分条】 | design |
| MOD-ALT-003 filing_nlp_engine | 公告事件 11 类分类+影响评分【事件流】 | design |

#### J-17 宏观分析/外盘速览（3 件）

| 模块 | 产出物（形态） | 成熟度 |
|---|---|---|
| MOD-ALT-005 policy_theme_mapper | 政策主题热度+主题→行业受益受损清单【热度榜】 | design |
| MOD-ALT-010 policy_expectation_analyzer | 政策预期差信号+ETF 份额异动（国家队腿，强制人审）【信号卡】 | prod |
| MOD-DAT-foreign_coverage | 外盘 12 标的 covered/stale/missing 三态核查（实测 4/12 有数）【健康灯】 | testing |

#### J-18 数据总览/数据源监管（22 件——治理深度最超预期一簇）

| 模块 | 产出物（形态） | 成熟度 |
|---|---|---|
| cleaning_anomaly_engine | 五维清洗检测+修复审计+人审队列【审计流水】 | prod |
| expectation_governance | 期望套件 BLOCK/DEGRADE/WARN 三档验证【报告卡】 | prod |
| incremental_update_engine | 增量三通道检测+对账偏差告警【告警条】 | testing |
| data_anomaly_alerter | 四维异常+AL-P1~P4 分级+抑制降噪（不吵的告警流）【分级流水】 | prod |
| quality_sla_breach_predictor | SLA 违约预测+burn-rate 四级（数据会断提前可见）【仪表盘】 | prod |
| data_lake_manager | 热/温/冷三层迁移保留裁决【三层水位图】 | prod |
| lineage_tracker | 表→因子→信号血缘 DAG+上下游查询【血缘图】 | prod |
| lineage_change_detector | 血缘快照 diff+下游影响集合【变更报告】 | prod |
| asset_auto_discovery | 三类资产自动发现+质量分卡片（防账实漂移）【卡片墙】 | prod |
| ml_lineage_tracker | 数据集→特征→模型→预测全链反查【链图】 | prod |
| metadata_registry | 表/因子/策略/信号元数据统一注册【目录树】 | prod |
| market_data_aggregates | 保留归档策略协调+恢复演练记录【策略表】 | prod |
| vendor_registry | 行情 vendor 注册表+状态【状态灯墙】 | prod |
| failover/manager | 主备切换执行+事件历史【切换时间线】 | prod |
| auction_data_manager | 竞价数据校验/去重/命中回放【质量条】 | design |
| raw_data_cache | 缓存命中率（命中率跌=上游异常早期信号）【仪表】 | prod |
| connectors/manager | 连接器批量健康检查【状态墙】 | prod |
| speed_tester | 数据源×能力测速+blocked 判定【性能排行】 | prod |
| fetch_perf_recorder | 任务级真实抓取流水（失败排查第一现场）【流水表】 | testing |
| alt_data_catalog | 另类源目录+生命周期+FTS5【目录卡墙】 | prod |
| alt_source_health_manager | 另类源健康+降级阶梯（比熔断更细）【阶梯灯】 | prod |
| alt_data_compliance_reviewer | 数据源合规台账+白名单/禁用清单【合规名单】 | prod |

#### J-19 系统状态（7 件）

| 模块 | 产出物（形态） | 成熟度 |
|---|---|---|
| MOD-TRADING-008 strategy_abnormal_exit_orchestrator | 策略异常退出五步编排+EXIT_FAILED 升级【五步进度】 | design |
| MOD-EX-035 live_simulation_switcher | 实盘/模拟模式大灯+切换留痕（资金安全证据链）【模式大灯】 | prod |
| MOD-EX-036 performance_monitor | 执行链路延迟 p95（变慢最早期信号）【小 multiples】 | prod |
| MOD-L06-002 broker_link_probe | miniQMT 链路健康三态+RTT【三灯+曲线】 | evolving |
| gpu_monitor | GPU 使用率/显存+压力分级【仪表卡】 | prod |
| MOD-CMP-016 compliance_drift_detector | 合规规则声明 vs 运行漂移+整改任务【diff 表】 | prod |
| MOD-CMP-017 regulatory_change_tracker | 监管变更采集+NLP 抽取+评审任务【变更时间线】 | prod |

#### J-20 产业地图（3 件）

| 模块 | 产出物（形态） | 成熟度 |
|---|---|---|
| MOD-KNW-003 financial_knowledge_graph | 六类实体图谱+N 跳邻域+最短路径（供应链/股东/概念图基座）【图谱可视】 | prod |
| MOD-ALT-006 concept_factor_mapper | 股票↔概念双向映射+质量校验+PIT 版本【覆盖仪表】 | design |
| MOD-RK-046 risk_contagion_modeler | 见 J-3（双挂） | prod |

## 5. 需求族（Owner 二批输入，2026-08-28）

> 性质：Owner 以主观交易员（非编程/非量化背景）视角提出的功能需求 10 条，逐条附专业叫法+后端原料+处置建议。与 §4 资产族的关系：资产族回答"项目有什么"，需求族回答"Owner 要什么"——两者在映射批汇合落点。核心定位（Owner 原话）：仪表盘替代同花顺，是小白交易员看整个项目的唯一窗口。

| 编号 | 需求（Owner 原话提炼） | 专业叫法 | 后端原料 | 处置建议 |
|---|---|---|---|---|
| R1 | 盯盘时给算法产出挑错，反馈落日志反推优化；固定计算（KDJ 等）不反馈，**判断类**（买卖点/形态/新闻定性/事件影响/相似日/强度评级/天气研判）全要反馈按钮 | 人机回环纠错（Human-in-the-loop，人参与算法修正的闭环） | ⚑按钮+__fbQueue 已 6 处演示（G-四.A 裁定泛化在案）；纠错样本库未建（DAL-D07）；形态库 256 规则=反馈进化终点 | **进·第一优先**（小白交易员与算法建立信任的核心机制）；配套产出《反馈点清单》（映射批逐页定哪些内容挂⚑） |
| R2 | 回测全套传导体系可视化：数据库→处理→入库→因子→…做菜流水线；每环节中文解释+算法对标（哪年算法/是否过时）+点击跳代码位置 | 数据血缘图（Data Lineage，数据从哪来到哪去的谱系） | depgraph 7,809 节点 19,216 依赖边（父子关系真源）；200+ 模块 blueprint 中文说明；算法出处在设计备忘录（如 11 号备忘 Hurst/ACSI 来历） | **进**（原料全，缺的是小白视角流水线导航页）；**新建「算法注册表」配套资产**（算法/出处/年份/对标/时效状态）；原型先显示代码路径，IDE 联动归正式版 |
| R3 | 回测页：进度条+回测对象可选（单因子可单独回测）+多策略按行情自动切换的全程拟真回测 | 对象化回测（因子 IC 回测/策略回测/组合回测）；组合层模拟（portfolio-level simulation） | 回测引擎 production；实验注册表 5 条；多策略投票合成在码 | **进**；对标机构回测页（参数面板+进度+结果分 Tab：收益/回撤/交易明细/归因） |
| R4 | 捋清单：哪些任务要进度条、哪些不要 | 异步任务进度上报 | 真实长任务：回测/数据回补/情绪打分/图谱构建/RAG 索引/模型训练 | **进**；配套产出《进度条清单》（映射批） |
| R5 | 一级导航加 AI 组：AI 对话框指挥本地 AI 干简单活+AI 状态页 | 本地大模型智能体（LLM Agent） | Ollama qwen3:8b 本机在跑（情绪打分后端）；09_ai_architecture 20 份设计（自治边界/执行层/模块工厂，GP0 代码已施工） | **进·附条件**：导航 5 组→6 组属 IA 变动，需 Owner 拍板；页面候选=AI 对话/AI 任务队列/模型与管道状态 |
| R6 | 新闻×股价联动：利好却跌=弱、利空不跌=强，单独分析 | 事件研究（Event Study，事件发生前后股价怎么动）+预期差（Expectation Gap，实际反应 vs 应有反应的差）；利好出尽=sell the news | **CAND-RES-030「利好出尽事件研究」候选在册**+情绪分数+新闻精确时间戳+行情——料全有缺施工 | **进**；先新闻舆情页加「市场反应」列（发布后 1h/当日涨跌对照），跑出样子再评估独立页 |
| R7 | 机构研究报告单独做页 | 研评级分析（Analyst Rating） | research_rating 14.6 万条在库（DAL-B10） | **进**（评级上调下调/目标价/金股池） |
| R8 | 板块渐变地图：进攻→防御光谱排列（小登→中登→老登），看资金往哪坨流；A股一张+全球一张，分钟级刷新 | 风险偏好光谱图（Risk Appetite Spectrum）；机构标准工具=RRG 相对旋转图（Relative Rotation Graph） | **RRG 算法已在码**（BM-SEL-08，反向账在册）；A股板块数据现成；全球板块数据缺（可用美国板块 ETF 代理，待接入） | **进·分两期**：一期 A股版（数据全有）；二期全球版（有数先上，缺标待接入不造假） |
| R9 | 市场天气排行榜加板块维度+每市场涨跌家数 | — | 天气三栏已建（v3.7） | **进升级，不改名**（天气=事实状态/情绪=心理预期，且避免与 A股「市场情绪」页撞词） |
| R10 | 每页施工前对标机构实践/量化社区 | 同位调研 | 逐页审查方法论第①步已内置 | **已内化**，无需单列 |
| R11 | 股权穿透：A股上市公司股东结构（谁持股/股东间什么关系），像天眼查；不知道能研究出什么，要求对照机构实践 | 股权结构分析（Equity Ownership Analysis）/受益所有人穿透（Beneficial Ownership，查到最终自然人老板） | **原料比预想多**：十大股东+十大流通股东**已在采集**（akshare+QMT 双通道，tasks.yaml top10_shareholders/top10_circulating 两增量任务）；股东户数表 c3_fundamental.shareholder_count；股权质押（equity_pledge_detail）+限售解禁 schema 已建；北向持仓 production。**缺**：股东间工商穿透关系（天眼查式全量图谱=商业付费数据） | **进·三件落地**：①个股档案「股权结构」卡（十大股东/户数趋势/质押比例/下次解禁日——纯接线）②筹码集中度因子（股东户数变化率→进因子库，走 R2 流水线可回测）③事件日历加股权事件（减持/质押/举牌，解禁已有）；**不做**：天眼查式全量穿透图（付费数据+尽调级用途，自营边际价值低）标待接入·远期——连同系族敞口聚合（同一实控人合并计敞口，银行风控做法）与股权边并产业图谱（ig_company_edge 第三种关系边）一起等数据源 |
| R12 | **全景总览重新定位=实盘全景总览**：只放实盘实时状态，回测/研究内容一律不放（研究去看专门页，回测不紧张不需要盯）；两大关注=①量化实时分析产出是否正确（如新闻定性利好与我判断一致吗）②项目是否健康（数据源断流/治理告警/系统卡顿，小列表/弹窗）；资金区最重要保留（含 L3 折叠账户灯=Owner 原创设计）；**硬约束=一屏看完不滚动** | 驾驶舱（Cockpit）设计；机构实践=**角色专属工作台**（彭博 Launchpad/交易台首页=持仓+行情+告警三样，绝不混研究内容；量化平台实盘与研究环境完全分离） | 现页 v3.7 已是实盘导向（资金区/研判/天气，本无回测内容），**缺两块=算法校验+健康告警** | **进·重构页 1**：①资金区不变 ②今日研判条保留 ③市场天气压缩让位 ④新增「算法实时校验」卡（最新 N 条量化产出+✓/✗ 快速反馈=R1 反馈体系首站，落日志反推优化）⑤新增「健康告警」条（数据源/治理/系统三合一，无告警=一行绿不占版面，有告警才展开=负反馈纪律）⑥一屏硬约束入册；**改名实盘全景总览**；连带=⑥审批/告警形态实质定为横切层方案；像素级压缩归视觉会话 |
| R13 | **作战指挥 v2：现页太复杂无主次，收敛为两个半板块**——①盘前预案（早 8:00-8:30 基于隔夜信息+外盘+期指+韩股开盘生成：今天预判+遇什么情况怎么做）②实时情景跟踪（盘中 1-5 分钟滚动：当前走势匹配预案哪格、支撑/阻力站稳没有、买盘力量、接下来时段怎么走）③明日推演（根据今日盘面推明天：如底部震荡收不上去→明天惯性下杀→今天不开仓或只打底仓等明天恐慌盘）；**情景矩阵升级讨论**：Owner 主观经验=走势按时间段组合（开盘前 5-15 分钟[量最高]/上午/下午），问 3×3×3？ | 机构实践：①盘前=**if-then 预案树**（PlayBook 方法论，矩阵只是摘要层）②盘中形态=**市场轮廓开盘类型学**（Market Profile：Open Drive/Open Test Drive/**Open Rejection Reverse=Owner 说的"下砸 5-15 分钟又拉回"**/Open Auction 四型+趋势日/平衡日）③开盘区间（Opening Range，前 15-30 分钟独立判定时段）④看今天推明天=**隔夜风险评估**（Overnight Risk，T+1 制度核心；学术对应 overnight momentum 尾盘预测次日） | 原料：明日边界 MOD-PLAN-001（prod）+相似日三档（BFE-06 testing）+13 参数风险信号（BFE-21）+prediction_log；**缺两个新模块**：时序分段状态机+明日推演联动（登记施工项） | **进·重构页 2**：①盘前预案区（3×3 矩阵保持 9 格摘要+隔夜依据折叠+韩股 8:00 开盘卡 8:30 前分析时点）②实时情景跟踪区=页面主角（**不做 3×3×3=27 格认知超载**，改**时序分段判定**：开盘段[前 15 分钟]/上午/下午各 3-4 互斥形态滚动判定，组合成全天）③明日推演区（今日盘面→明日情景概率→今日操作联动：不开仓/打底仓/延后）④其余现有卡降级折叠；新模块 2 件入施工清单 |
| R14 | **盘中实时改名「大盘分析」，页面目的唯一=分析大盘今天实时状态+接下来走势预期**——①四大指数状态（上证/深成/创业板/科创综指，分钟级，问四个还是一个）②情绪分析图+详细参数（涨停/跌停家数、涨停跌停各是哪些板块、涨跌家数、**涨幅分档分布**[0-3%/3-5%/5-7%/7%+，下跌同档——"跌 4000 家但多数只跌 0-3%"vs"3000 家跌 7%+"情绪完全不同]、**封板率/炸板率/开板数**）③市场状态由哪些数据哪些因子组成全部写进页面（小白可解释）④与作战指挥关系之问（是不是一个东西） | 市场宽度分析（Market Breadth，涨跌家数/分布/新高新低族）+涨跌分档直方图+封板质量（A股打板情绪温度计）+**分布尾部厚度**（Owner 洞察的专业词）+风格分化（四指数背离信号）；机构实践=**状态监控屏与决策手册分离**（感知层/决策层两层） | **基本零新模块全是接线件**：regime_detector prod（A16）+13 参数风险信号 prod（BFE-21=「状态由哪些因子组成」现成答案）+market_breadth_watch prod（A13）+limit_up_down/realtime_snapshot 在库（B27）+极端预警族 prod（BFE-23/A17）；唯一新供数件=分档分布+封板质量聚合（正向账 B31 登记） | **进·重构页 3**：①改名大盘分析 ②四指数=**一主三辅**（上证大版面+深成/创业板/科创小版面；机构从不四等分，四指数价值=风格分化信号）③情绪分析区=今日情绪快照（分档分布直方图+封板质量+涨跌停板块归属；**与情绪页分工**=本页管今天快照、情绪页管周期位置，不新开页）④因子构成面板（regime 结论+13 参数明细，每因子当前值/方向/中文解释=R2 可解释性落地）⑤与作战指挥=**感知层/决策层关系**：不合页，R13②实时跟踪区引用本页结论 ⑥现 p-live 决策链/风控实时/委托区映射时归队（决策类去作战指挥，本页只留状态感知） |
| R15 | **板块全景 v2：核心=今天资金去了哪些板块/持续流入哪些/哪些产生分歧**——①相对强度地图（分界=大盘实时涨速，右红=强于大盘[跌得慢/逆势涨]、左绿=弱于大盘，分钟刷新；下跌段=逆势抗跌图、上涨段=顺势领涨图，两图可合一）②下方两表（抗跌榜/领涨榜，**次数排序优先**+幅度排序辅助；**冲高回落型标注**=涨幅>大盘但一路向下=持续流出，过程>结果）③Owner 核心洞察：资金悄悄吸筹的板块全天涨幅不显眼，但**每次大盘下跌都跌得少一点**——全天数据看不出，分段对比才能抓 ④颜色方向之问（要求统一）⑤泛化：每页核心=给结果+全部因子证据，Owner 校验"分析对不对+数据全不全" | **相对强度**（Relative Strength，板块 vs 基准强弱差，机构最老牌工具）+**上行/下行捕获率**（Up/Downside Capture Ratio，晨星基金分析标准=涨时跟得上跌时跌得少）+**威科夫吸筹**（Wyckoff Accumulation：弱势中显强势=有人接筹——**项目有 Wyckoff 吸筹 FSM production 在码**，BFE-23 族）+RS 持续性（"次数"=相对强度的稳定性，一次抗跌是运气每次抗跌是习惯） | B26 已登记逆势四卡（最抗跌/率先反弹/分钟级资金流入演示）；money_flow 在库+sector_fund_flow_collector（testing）；板块分钟强度计算管线缺=B26 同族扩注；Wyckoff FSM prod 可借引擎 | **进·重构页 4**：①主图=相对强度光谱地图（分时双模式：大盘跌自动切抗跌视角/涨切领涨视角，分界=大盘实时涨速，分钟刷新）②抗跌榜/领涨榜双表（次数优先/幅度辅助+冲高回落形态标注）③证据链卡（资金流入/相对强度/抗跌次数/过程形态四因子全呈现）④B26 扩注升级（正向账 v2.3.2）⑤**随批裁定④⑤**：全站地图/光谱图颜色统一=右红左绿（右强左弱，A股红涨绿跌语义延伸，R8 同规）；**每页设计铁律=结果+证据链**（所有构成因子/数据呈现，Owner 校验"分析对不对+数据全不全"，R14 单页面板泛化为全局原则） |
| R16 | **市场情绪页 v2（同花顺截图 10 张对照输入）**：①涨停强度今昨对比卡（涨停板/封板率/涨停打开/跌停板/跌停封板率/跌停打开，今 vs 昨并排——同花顺标准件）②连板梯队升级=**连板天梯**（按 5/4/3/2 板分组+题材+今日表现[开板回封/一字板/涨停/负值]+最后涨停时间+龙头标）③**昨涨停今表现**→情绪回暖/退潮判断（涨停数量+质量+速度综合：开盘秒板家数 vs 10 点后板家数，同样 50 家 9:30 板 vs 10:00 板情绪完全不同）④涨停基因放个股页（封板成功率+成功后次日表现[高开概率/平均高开/上涨概率/平均涨幅]+近一年触及涨停分析表——G-四.A 已有雏形升级同花顺完整口径）⑤人气排行榜（数据源未知）⑥市场成交额对比（今日/昨日/历史序列/预测线，分时累计双线图）⑦情绪构成因子全展示+**每页"算法查看"小图标**（可折叠小模块，点击展开证据链，链接到 R2 算法展示区） | 涨停强度（Limit-up Strength）今昨对比+**连板天梯**（连板高度=短线情绪最敏感温度计）+**涨停质量三维**（数量/质量/速度——开盘秒板率=抢筹急迫度）+封板成功率（Board Sealing Rate）+涨停基因（Limit-up Gene，个股涨停历史统计）+**成交额对比**（量能是情绪的燃料：今日累计 vs 昨日同时段 vs 历史分位） | 原料：limit_up_down 表+B31（分档分布+封板质量已登记）+MOD-DATA-062 分钟快照（涨停/炸板/封单）+daban_board_event_deriver（连板推导 1990+ 全史）+MOD-SIG-033 接力情绪引擎（连板周期）+个股股性卡（G-四.A 已有涨停基因雏形）；**缺**：人气榜数据源（同花顺人气=东财股吧热度类，social_sentiment_collector design 在码） | **进·重构页 5**：①涨停强度今昨对比卡 ②连板天梯替现有梯队 ③昨今涨停对比=数量/质量/速度三维（秒板率/封板率/开板率）④涨停基因升级同花顺完整口径 ⑤成交额对比卡移入大盘分析页（量能属大盘状态，联动 R14）⑥情绪构成因子卡（13 参数情绪族+宽度+涨停族+量能全列）⑦**算法查看小图标泛化全站**（每页证据链折叠模块+R2 算法区链接）⑧人气榜=D 类数据源登记（正向账 D20） |
| R17 | **新闻舆情页 v2：重头=分析不是看新闻**——①新闻清单实时更新+**自动保持最近两天滚动窗**（从现在到 48h 前，可一直下滑）②新闻点击展开详情+分析（详情=库内全文；分析=情绪/影响/关联标的/双标签；来源采集方显示，原文 URL 无则负反馈不造假）③今日整体新闻分析（偏多/偏空分布+可预测/不可预测分布+影响分级）④**预期差分析**（新闻 vs 市场预期的差）⑤新闻推断未来走势（长周期产业趋势甘特图：机构提前定价逻辑——先出订单/需求预期→机构提前买预期→财报兑现时出货）⑥三季报/四季报+订单预测单独页候选（季报与订单深度绑定→反推下季度订单+行业景气度）⑦Owner 新闻观：新闻只是资本想让人看见的，突发事件看风险、非突发看未来判断；新鲜首次出现的产业信号（如粮食首次涨价预期）才有埋伏价值 | 新闻生命周期（News Lifecycle）+**叙事经济学**（Narrative Economics，Shiller：叙事传播本身影响市场）+预期差（Expectation Gap，R6 已立）+**订单前瞻**（Order Foresight：从订单/需求预期反推业绩）+盈利动量（Earnings Momentum）+PEAD（财报后漂移，MOD-SIG-110 在码） | 原料：news_data 表（时间戳精确）+**news_dual_tagger 双标签[可预测+预期差] testing 在码**+news_impact_grader（影响 A/B/C+热点主题）+analyst_forecast 一致预期表（预期锚）+MOD-SIG-110 PEAD（财报漂移统计）+event_score（事件评分）；**缺**：订单数据（无源，近似=分析师盈利预测修订趋势） | **进·重构页 6**：①两天滚动新闻清单（时间窗接口 B34 登记）②点击展开详情+分析卡（双标签/影响分级/关联标的）③今日新闻整体分析条（多空分布+可预测分布）④预期差列并入（R6 市场反应列同族）⑤**远期设计登记**：产业趋势甘特图+订单季报前瞻页（C29 登记，机构提前定价逻辑）⑥来源显示=采集源名（财联社/东财等），URL 无则负反馈 |
| R18 | **实盘全景总览二次再定位=项目全景驾驶舱**（Owner 三屏盯盘实证修正 R12）——①三屏多开场景下"什么都有但什么都不精"的综合首页=不会点开（盯盘软件首页从没打开过；机构首页=宣传/导航）②本页唯一不可替代功能=**全资产资金总览**（A股+币圈+模拟户跨市场整合，总资产实时变化——放哪个业务页都不合适，只能在这）③新主体=**项目全景地图**：全模块父子/子孙关系可视化，可缩放（鼠标滚轮）、可折叠展开、模块显示中文名（简介可折叠）、点击跳算法代码位置、**数据流动效果**（能看到哪些模块正在跑、数据往哪流）——实用兼美观，"点开一看非常好看" | **系统可观测性全景图**（System Observability Map——Grafana Node Graph/Datadog Service Map/K8s 拓扑图同族）；彭博 Launchpad 首页=空白等拼（证明"预设综合首页"是伪需求）；对 100% AI 开发项目=**项目驾驶舱**（Owner 核心焦虑="几千个模块在干啥、健不健康"，不是"再看一眼行情"） | **原料全有**：depgraph 7,675 模块×73 域父子依赖（2026-08-29 刚全量重建，含层级）+module_translation_registry 每模块中文名+人话简介（plain_zh 字段天生为此备）+算法注册表（R2 配套，出处/年份/时效）+运行时遥测（scheduler 任务态/CH 写入流=数据流动效的真源）+模块四段灯台账（E02/E03）；效果层=缩放/折叠/流动=前端图引擎件（elkjs 分层布局+d3-zoom/cytoscape 族），工程量=一张大图级非全站改造级 | **进·重构页 1 第二版**：①资金总览条压顶保留（跨市场唯一整合点）②页面主体换=项目全景地图（缩放/折叠/中文名+简介折叠/点击跳代码路径/模块运行灯+数据流遥测）③健康告警条保留（四合一横切条已落）④市场天气/算法校验卡**撤出首页**——天气归外盘/大盘页（已有），实时校验反馈点归各专业页（R1 全站⚑体系本就分散在各页，首页不再设集中校验卡）⑤快速导航=顶栏搜索已有，首页不背导航职责 |
| R19 | **全站模块化组合（自定义布局）**：每个页面的卡片模块可增删组合——右侧栏"加号"打开模块选择器（按分组：资产类/新闻类/情绪类…），模块有标准尺寸+可鼠标拖拉改大小；布局方案可保存/锁定/一键还原默认；Owner 警觉投产比——"如果工程量大于现有所有工程量就算了" | **模块化仪表板**（Modular Dashboard）/网格布局引擎；对标：Bloomberg Launchpad（模块化面板鼻祖）/同花顺自定义版面/TradingView 布局/Grafana 面板 | 引擎层便宜：gridstack.js 级轻量库（无依赖 ~12KB）或原生 CSS Grid+ResizeObserver；布局存储=localStorage 演示→后端 layout 表（施工期）；**贵在卡片化改造**——全站 41 页×均 5~8 卡≈250 张卡要全部变"独立组件+独立数据契约+标准尺寸" | **进·分两期，投产比可控**：①一期=布局机制+试点 1~2 页（首页[配合 R18]+作战指挥），工程量小（机制+两页改造）②二期=全站卡片化**不单独立项**——搭各页施工/重构的便车渐进做（改到哪页，哪页卡片化）③**明确不做**：一次性全站 250 卡突击改造（投入大且与"模板还在改"现状冲突，改了还要改）④布局方案存取/锁定/还原=机制内含 |
| R20 | **4K 屏适配+一屏密度**（视觉线输入，记录转达）：Owner 硬件=4K 27 寸×3 屏；现原型左右黑边大（内容区限宽未利用满）；内容块占位偏大导致要滚动；金融终端应**一屏展示全部关键内容** | 流体布局（fluid layout，去 max-width 死限宽）+**密度档位**（density compact/comfortable——彭博/路透终端密度远超消费网页）+金融终端一屏原则 | 纯视觉规范件（§DS 增补"断点与密度"章节：4K 断点 2560+/3840+ 流体化、compact 密度档、一屏优先） | **转视觉规范线施工**（不属功能线）；本账登记防丢——优先级=高（Owner 主力硬件就是 4K×3，当前原型在其主屏上体验受损） |
| R21 | **首页=全员结论汇报墙（"老板看员工一句话汇报"模式）+改名「全景总览」**（R18 同日追加批）——①首页第二任务=**快速浏览实盘所有页面的最终结论**：每页结论做成小卡片（突出标题+最多两行字），首页按**实盘交易顺序**排序聚合（例：大盘分析→[今天什么状态·实时更新]+[接下来走势预期] 两卡；作战指挥→[昨天预案是什么]+[今天匹配哪格+现在状态]+[明天大概怎么走] 三卡；讲几个东西就出几个结果卡）②**铁律扩展：每个页面自身必须有"结论区"**（结果一句话概括+两句阐述）——§8 裁定批④"每页一句话核心置顶"升级为**标准化结论卡（verdict card）**：结论卡=页面的标准化输出口，首页结论墙=各页结论卡的聚合抓取，不是另写一套 ③系统健康小卡+**AI 对话框常驻首页**（随时问问题）④**一屏硬约束**：结论卡墙+资金条+健康条+AI 框在一个屏幕高度内全放完，不许下滑（compact 小卡，4K 一屏可容 40+ 卡，实盘 ~10 页×1~3 结论≈20 卡容量富裕）⑤**改名：实盘全景总览→全景总览**（去掉"实盘"二字） | **Executive Summary 墙**/晨会简报（Morning Brief 一页纸）+新闻倒金字塔（结论先行）+**Verdict-as-API**（每页结论=标准化接口，首页=聚合消费方）；机构对标=彭博 TOP 页（结论聚合而非数据堆砌） | **原料现成**：各页"核心一句话"已在 §8 蓝图逐页定义（=结论卡文案真源）；R13 作战指挥三区天然就是三结果结构；健康条/AI 对话页已建（v4.1）；结论卡=纯前端呈现层改造（每页加 verdict 卡+首页聚合墙），**零新后端模块**；与 R18 项目全景地图的空间冲突裁定=**一屏给结论墙，全景地图为首页内"展开全屏"入口层**（点开展全屏浏览，平时收起只占一张卡位） | **进·并入页 1 第二版**：①页面骨架=资金总览条（顶）+结论卡墙（主体，按交易流程排序：作战指挥→大盘分析→板块全景→市场情绪→新闻舆情→政策资金→外盘→做T→持仓→币圈）+系统健康卡+AI 对话卡+全景地图入口卡 ②每页施工时同步落地该页 verdict 卡（**首页不另写文案，抓取各页结论卡**——真源唯一，防两处漂移）③改名全景总览 ④一屏硬约束延续 R12 |
| R22 | **原型拆分并正式迁入项目=拆分即转正**（Owner 三批讨论：多会话并发改同一文件不可行→拆分后永不合并→治理没设计好不敢搬的历史顾虑）——①**单文件不可真并发**（实证：视觉线整段覆盖 nav 块两起，写锁只能串行排队），拆分=并发施工与 R19 模块化的物理前置 ②**拆分即终态永不合并**（源码永拆；部署产物合并是构建工具自动行为，与源码无关）③**拆分即转正**：拆开的文件直接进正式位置（src/zephyr/frontend/dashboard/web/），从拆分那一刻起=在建正式仪表盘——"模板 vs 正式"的区别不在文件夹在数据真假（演示 badge→真源接线），避免二次搬迁 ④**旧版盘点**：Panel 旧版 14 Tab 中 11 个新版已覆盖且更强；**独有活资产仅 Tick 回放一件**（production，tick_replay 组件+50 万点降采样，新版缺——登记进盘后复盘/回测页）；知识库概览=空壳不搬（KB 2026-07 已退役，AI 知识检索是现代替代）；5 档盘口新版已有占位（D5）⑤**旧版处置=不删标 deprecated**（功能参考资产，尤其 Tick 回放实现逻辑） | 终局结构治理（治理先行，回应 Owner"文件臃肿/漂移/幻觉"历史痛点）：**trae_028 容量协议**（pages/ 封顶型 41≤60 合规，破 60 按导航组拆 pages/ashare/ 等子目录）+**目录契约门禁**（v1.3.0 已开 frontend/ web 资源白名单，commit 机器拦截放错位置）+**trae_024 单一类型**（assets=资源/styles=CSS/core=JS/pages=HTML 物理隔离）+**命名=页面 id 与 GRP_OF 机械映射**（蛇形小写，AI 不会起错名） | 终局结构：`frontend/dashboard/web/`——index.html（入口骨架）+assets/（字体图标，封顶）+styles/（tokens/density/kline，封顶）+core/（路由/搜索/反馈/布局，封顶）+pages/（41 页各一文件）；旧版 app.py/app_panel.py/components/ 原地标 deprecated | **进·执行序**：①Owner 拍板终局结构 → ②拆分手术（等视觉线 K 线引擎收尾后，41 section 机械切分内容一字不改）→ ③Tick 回放登记新版规划+旧版标 deprecated → ④设计迭代在正式结构上继续（四会话并行）→ ⑤数据契约敲定冻结后接通后端→总验收 |
| R23 | **旧版 Panel 细节向新模板融合三处（Owner 实测旧版后裁定："两个都要，一个都不落下"）**——①**作战指挥页=旧版清晰骨架+新版全部细节**：旧版四区呈现更清晰（①前日预案 ②实时走势分时段判定表[竞价段/开盘 30 分/上午段/下午段 逐段一行] ③今日→明日惯性推演[概率分布+8 态分布百分比+操作联动] ④四指数 regime 状态卡[各指数置信度+强弱位次+近 20 日收益]）——Owner 裁定旧版结构分得更清楚（该结构本就是 Owner 08-28 裁定落在旧版的，新版 R13 重构时未完全对齐）；**骨架取旧版四区，内容并集**：新版已有的 3×3 矩阵摘要/作战池/执行区/打板实时监控/禁做清单/W0 验证全部保留并入对应区 ②**回测页=旧版图表细节全量搬运**：顶部信息条（回测区间/期初资金/基准/状态/交易天数）+6 KPI 卡（累计收益/年化/最大回撤/夏普/胜率/盈亏比）+五子 Tab（绩效/持仓分析/交易统计/每日明细/信号分析）+收益图**三线**（策略/基准/超额收益）+**hover 十字线显示精确日期+三线数值**+回撤图（策略 vs 基准双色填充）+日收益率红绿柱——新版回测页保留其治理件（回测对象选择/进度条/门控三阶段/PBO/参数敏感），图表呈现层全部对齐旧版细腻度 ③**QMT 文件桥健康详细卡**→**系统状态页**（不进作战室——它是系统监控）：文件桥整体状态/分终端 degraded 原因/四个导出文件延迟秒数/在途挂单/持仓数/可用资金（新版现仅有心跳一行，信息颗粒度不足） | 旧版呈现层优势=Panel/HoloViz 图表 hover 交互成熟（十字线/精确读数）；新版=静态 HTML 需用 ECharts/轻量图表库补齐同等 hover 体验（K 线引擎线已有图表底座可复用）；**结构融合原则=信息架构取 Owner 体感更清晰者，内容与细节取并集** | 后端零新模块：作战室四区原料已在码（MOD-PLAN-017 概率引擎/MOD-PLAN-001/8 态/MOD-REGIME-008 四指数 regime）；回测图表数据源=回测产物 JSON（bt-*.json 已在落盘）；QMT 桥健康=fetch_qmt_bridge_health（production 在跑） | **进·三处融合入施工清单**：①作战室结构对齐旧版四区（R13 第三版修订，等视觉线收尾后施工）②回测页图表层对齐旧版（含 hover 十字线，一个不落）③QMT 桥健康详细卡补进系统状态页；均归入拆分后正式结构施工，不在旧单文件上重复投入 |


**随批裁定（Owner 讨论已决 5 项）**：①美联储/特朗普发言**不开单独页**——宏观分析页加「央行与政策」卡（FRED 美联储数据源 production）+新闻页加「央行」分类+FOMC 已在事件日历；②币圈**不做光谱地图**（板块生态太浅），作为全球一员进排名榜即可；③「市场天气」**不改名**；④**全站地图/光谱图颜色方向统一=右红左绿**（右强左弱，A股红涨绿跌语义延伸，R8 光谱图/R15 相对强度图同规）；⑤**每页设计铁律=结果+证据链**——所有构成因子/数据全量呈现，Owner 校验"分析对不对+数据全不全"（R14 因子构成面板泛化为全局原则）。

## 6. 统计速览

- **资产族（§4）建议"进"**：36 项（P0 三件=C01 产业地图接线/E01 注册表库接线/B01 八表真源）；**不进**：11 项（死文档族为主+候选态+证伪留档）；**待定**：0 项（原 2 项已于 2026-08-29 销账——C03 产物核实=真源在盘改"进"、I 族审批告警形态=横切条拍板，见 §7.A）。**§4.J 全量扫描批新增**：账外富矿 **192 件可视化候选**（J-1~J-20 按目标页分组，production 为主）+**反差件 8 件**（登记"需新建/缺"实则已落码：C1/C8/C18/C21[假缺口]/C22/D2/B26/C25——施工成本≈纯接线，正向账 v2.4.0 同步扩注）；D_CROSS_ASSET 实证空壳域。
- **需求族（§5）**：22 条（R1~R22）全"进"（R5 附 IA 第六组拍板条件→已拍板；R1 标第一优先；R11 含 1 项远期不做=全量穿透图；R12~R15=页 1~4 重构令；R16=页 5 情绪页重构令[涨停强度今昨对比/连板天梯/涨停质量三维/涨停基因/算法查看图标泛化]；R17=页 6 新闻页重构令[两天滚动窗/点击展开详情+分析/整体新闻分析/预期差/远期=产业趋势甘特图+订单季报前瞻页]；**R18=页 1 二次再定位**[项目全景驾驶舱]；**R19=全站模块化组合**[两期]；**R20=4K 屏密度**[转视觉线]；**R21=首页结论汇报墙+改名全景总览**[verdict 卡标准化+聚合抓取+一屏硬约束]；**R22=拆分即转正**[永不合并+终局结构治理先行+旧版 Tick 回放独迁+旧版 deprecated 保留]）；随批已决 5 项；新增配套资产 1 件（算法注册表，R2）+配套清单 2 件（反馈点清单 R1/进度条清单 R4，映射批产出）。
- **角色覆盖自检**：交易员（4.A+H+R1/R8）/研究员（4.C+D+R2/R3/R6/R7）/数据（4.B+E01）/系统（4.E 余+F）/AI（R5，✅已拍板第六组）/治理者（4.I，✅已定横切条形态）——五角色框架资产齐套，无空域。
- **前端 36 页覆盖率**：本账"进"项落点 70% 在既有页扩卡接线，新增页面已落 4 个（数据源监管页/研评级页 R7/模型页/AI 组两页——R5 已拍板成第六组）——**IA 骨架=五组+总览+AI 六组，局部增量**。

## 7. 下一步（Owner 裁定入口）

1. **逐批复审本账"建议"列**：§4 资产族（建议按 4.B→4.C→4.E→其余的顺序，P0 三件在前）+§5 需求族 R1~R10——回复"X 批按建议执行"或逐项改裁定。
2. ~~**审批/告警形态决策（盘点后兑现）**~~ → **✅ 已拍板（2026-08-29）**：横切层成立不独立成区——全景总览健康告警条升级为「待审批收件箱+数据源/治理/系统告警」四合一横切条（I03 实盘下单/强减审批+I02 autonomy_gate ticket+I01/I04/I05），审批永远 human_gated、AI 无权代批。**已施工落盘**（p-overview #ovx-health）。
3. ~~**R5 附条件拍板**~~ → **✅ 已拍板（2026-08-29）**：AI 组立为第六个一级导航——AI 对话页（p-aichat：指挥本地 qwen3:8b 干简单活+advisory_only 红线区）+AI 任务队列页（p-aitask：状态/产出/审计三件套+ReAct 助手/情景记忆/GPU 共识调度三卡）+模型与管道状态（共享页双挂，系统组主属）。**已施工落盘**。
4. 裁定完毕后进 IA 映射（哪些页扩、新页归属、mega 容量检验），同步产出反馈点清单+进度条清单，再按逐页方法论施工；接线批全程守 S6（无真源=负反馈，不造假）。

### 7.A Owner 待裁定 5 项 → 全部已拍板（2026-08-29，Owner 令"全部按倾向执行"）

| # | 待裁定项 | 拍板结果 | 落盘状态 |
|---|---|---|---|
| 1 | AI 第六导航（R5） | **成立**——AI 对话/AI 任务队列两新页+模型页共享双挂 | ✅ 已施工（导航第六组+GRP_OF+搜索索引+两页本体） |
| 2 | 打板 sleeve 启用（BFE-36 挂起） | **仿真启用**——信号全真跑、成交走模拟户、不碰实盘资金；转实盘需 Owner 二次拍板 | ✅ 已施工（作战指挥执行区·打板实时监控卡：信号/熔断/坑位/破板五件齐） |
| 3 | C03 主题联动产物核实 | **真源已核实**——`.runtime/industry_graph/theme_linkage_daily.csv` 在盘（24链/523家·08-25 交易日·manual 启动），与声明口径一致 | ✅ 已施工（板块全景·产业链联动日报卡，badge 真源已核实；I-2 接线后自动刷新） |
| 4 | 审批/告警形态 | **横切层**（见 §7-2） | ✅ 已施工 |
| 5 | 模型页归属 | **系统组**（导航"系统·运行与标准"区；AI 组共享双挂入口） | ✅ 已施工（J-14 全家 11 件补齐：学习回喂/解释留痕/压缩三阶段/因子利用度/可复现锚定+铁律证据链） |

## 8. 全页施工蓝图（长城任务·任务二裁定批+任务三缺失清单，2026-08-29 AI 自主裁定）

> **裁定依据**：铁律（每页=结果+全部因子证据，Owner 可校验"分析对不对+数据全不全"）+第一性原理（页面只答一个问题，答什么决定放什么）+100% AI 开发项目的战略（**仪表盘=可校验层**——Owner 非程序员，每个数字必须可溯源到模块/表，证据链模块是全站标配不是选配；演示 badge 恒可见、无源一律占位不造假）。**处置四档**：prod 即接 / testing 标"试验中" / design 标"规划中"灰化 / 无源标"待接入"。
>
> **裁定批 5 项**：①新页三成立——研评级页（A股研究 mega）、数据源监管页（数据组第 3 页）、模型页（系统组·模型与管道）；②订单季报前瞻页+产业趋势甘特图=远期（C29 登记）；③**算法查看小图标全站泛化**——每页证据链折叠模块（结论←哪些模块/因子/数据+代码路径），链接 R2 算法注册表；④presentation 原则=**每页一句话核心置顶，结果区在前、证据链区在后/可折叠**；⑤**Owner 待裁定清单**（AI 无法自决 5 项）：AI 第六导航（R5）/打板 sleeve 启用（BFE-36 挂起）/C03 主题联动产物核实/审批告警形态确认（R12 已实质定横切）/模型页归属（暂定系统组）。

| 页 | 核心一句话 | 施工内容（缺失清单→呈现设计） | 无源/占位 |
|---|---|---|---|
| 1 实盘全景总览 | 实盘驾驶舱：资金+算法对不对+系统健不健康 | R12 重构：L1/L2/L3 资金区不变+**算法实时校验卡**（最新 N 条量化产出+✓/✗ 反馈=C26）+**健康告警条**（无告警一行绿=C27）+天气压缩；一屏不滚动 | C26/C27 演示先行（反馈落 __fbQueue 演示桩） |
| 2 作战指挥 | 预案+现在匹配哪格+明天怎么办 | R13 重构三区：盘前预案（3×3 摘要+隔夜依据折叠+作战池 MOD-SIG-066）/实时情景跟踪（时序分段判定 C24+关键位验证）/明日推演（8 态 MOD-SIG-037+操作联动 C25）；旧卡降级折叠；尾盘决策/禁做清单/四轨融合入区 | C24/C25 演示先行（接线=I-2） |
| 3 大盘分析（原盘中实时改名） | 大盘今天什么状态+接下来预期 | R14 重构：四指数一主三辅（上证大版面+深成/创业板/科创小版+regime 面板 MOD-REGIME-008）/情绪快照（分档分布直方图+封板质量 B31+涨停强度今昨对比 B32）/**成交额对比卡**（今日/昨日/历史/预测 B33）/因子构成面板（13 参数+regime 结论+九网格+四季+风格四象限） | B31/B32/B33 演示先行；决策链/风控/委托区移作战指挥（R14⑥） |
| 4 板块全景 | 资金去了哪些板块/谁在持续流入/谁分歧 | R15 重构：RS 光谱地图（分时双模式，分界=大盘实时涨速，右红左绿）+抗跌榜/领涨榜（次数优先+冲高回落标注）+证据链卡（资金/RS/抗跌次数/形态）+Top10 接线标注（MOD-SIG-064/RRG） | B26 管线演示先行（counter_trend_board 后端在码待接） |
| 5 市场情绪 | 今天情绪什么状态、由什么构成 | R16 重构：涨停强度今昨对比卡+**连板天梯**（板数分组+题材+今日表现+龙头标）+涨停质量三维（数量/质量/速度=秒板率）+情绪温度+构成因子卡（情绪族+宽度+涨停族+量能）+算法查看图标 | B32 演示先行；人气榜占位（D20 源未接） |
| 6 新闻舆情 | 新闻的分析结果，不是新闻本身 | R17 重构：两天滚动窗清单（B34）+点击展开详情+分析（双标签/影响分级/关联标的）+今日整体分析条（多空+可预测分布）+预期差列+热点主题榜（MOD-NLP-IMPACT-001） | B34 演示先行；来源显示采集源名，URL 负反馈 |
| 7 政策资金 | 政策与资金的两路证据 | 政策预期差卡（MOD-ALT-010）+国家队持仓（B16）+护盘代理（D1 占位维持） | D14/D1 源未接 |
| 8 外盘速览 | 外盘对 A股的传导输入 | foreign_coverage 健康灯（4/12 有数）+隔夜传导卡（MOD-SIG-038/117）+美债深区（B17） | B4/D19 源部分缺 |
| 9 做T分析 | 做T点位+税后经济账 | t0_point_analyzer 接线标注+做T盈亏预估（MOD-SIG-132）+成本门槛（t0_cost_model） | 演示先行 |
| 10 盘后复盘 | 今天做得对不对+明天怎么改 | 三频编排（MOD-RPT-009）+三向对账台账+决策链泳道（RPT-033）+一键战报+归因瀑布 | 演示先行 |
| 11 持仓监控 | 持仓状态+卖出建议+风险暴露 | 卖出信号列（BFE-18）+生存曲线（MOD-SIG-045）+行为分类+集中度（MOD-RK-07）+盈亏真源标注 | B1/B2 供数待接 |
| 12 回测结果 | 回测可信吗+对象化回测 | R3 升级：回测对象选择（策略/单因子/组合）+**进度条**+门控三阶段（decision_gate）+PBO/过拟合+参数敏感+报告卡 | C19 发起通道待接 |
| 13 实验历史 | 实验可信吗 | DSR+四层门控（MOD-SIM-028）+A/B 对照+复现核验 | 演示先行 |
| 14 策略档案 | 策略是资产不是黑箱 | CPCV 稳健分+衰减 4 级+冷启动阶梯+容量仪表 | 演示先行 |
| 15 因子档案 | 因子生命链健康 | J-11 全家：IC/IR 总表+衰减曲线+拥挤度+生命周期 6 态+池水位+三档徽章 | A8 供数待接 |
| 16 个股档案 | 一只票的全部档案 | **股权结构卡**（R11：十大股东/户数趋势/质押/解禁）+**供应链卡**（DAL-C02：客户/供应商集中度）+研报卡（B29 交叉） | B7 档案供数待接 |
| 17 个股行情 | K 线工作台 | 涨停基因完整口径（R16：封板成功率+次日表现+近一年触及表）+假动作预警（MOD-SIG-124）+人气行占位+五档（D5） | D20/D5 源未接 |
| 18 条件选股 | 条件→候选池 | B22 引擎+评分卡列（BFE-02） | 引擎缺 |
| 19 事件日历 | 未来事件 PIT 日历 | 股权事件类型（R11：减持/质押/举牌）+币版事件（D18） | B5 供数待接 |
| 20 技术分析 | 技术分析工作台+系统综合观点 | C1 置信度接线（index_resonance_scorer）+形态库真源（DAL-D06）+RSI 自适应（MOD-ML-008）+蒙特卡洛扇形（C8 接线） | 演示先行 |
| 21 宏观分析 | 宏观流动性与政策 | 央行与政策卡（美联储裁定：FRED 在库）+政策主题热度（MOD-ALT-005）+宏观比价占位 | C11 无后端（D_CROSS_ASSET 空壳） |
| 22 产业地图 | 产业链传导图谱 | **C01 P0 接线**：686 链浏览+环节节点+个股落位（ig_node_company）+公司供应链层（58,029 边） | 页面从零建（原占位页替换） |
| 23 注册表库 | 18 业务注册表集中浏览 | **E01 P0 接线**：ROOR/master_index 实测计数替演示 | B11 导出待接 |
| 24 数据总览 | 数据的家底与健康 | B01 八表真源+B07 数据资产+质量监控计数（J2 纠偏 19.5 万演示数） | B30 供数待接 |
| 25 数据源监管（**新页**） | 数据从哪来、健康吗 | J-18 全家：源清单+SLA burn-rate+熔断+测速+告警流水+切换时间线 | 新页建（数据组第 3 页） |
| 26 研评级（**新页**） | 机构评级与 AI 独立观点 | J-15 全家：评级变动流+目标价+金股池+AI 深研（llm_research_agent）+可信度锚定（UFL） | B29 供数待接 |
| 27 模型页（**新页**） | 模型注册+质量双层监控 | J-14 全家：注册表视图（BFE-40）+训练态（密度/QNN 指标）+服务态（四维漂移）+影子部署 | 新页建（系统组） |
| 28 模块总账 | 全模块台账 | E02/E03 接线：depgraph 真源+候选 618 纠偏（J6） | 演示先行 |
| 29 系统状态 | 系统健不健康 | J-19+F 族：守护进程区（reaper/watchdog/8010）+提交队列（done 89/dead 42）+链路探针+GPU+实盘/模拟大灯 | 演示先行 |
| 30 治理分析 | 门禁统计 | F03 门禁命中流水真源（OLAP 未配置维持 N/A 反误导） | 真源待接 |
| 31 任务进度 | 施工/任务进度 | G04 tracker 接线+**进度条清单**（R4：回测/回补/情绪打分/图谱/RAG/训练六类长任务进度条规格） | 演示先行 |
| 32 架构全景 | 架构三视图 | E03 depgraph 三视图接线（B23） | 视图收编待接 |
| 33 适应评估 | （治理域） | 维持现状 | — |
| 34 币圈盘面/持仓/策略/回测/档案 | 币圈镜像 | C23/C28/D16 待接入占位维持（OKX 落库后接线，S6 不造假） | OKX 管道未建 |
| 35 设计规范 | （视觉会话领土） | 不动 | — |

**进度条清单（R4 落地）**：回测发起/数据回补/情绪打分回填/图谱重建/RAG 索引重建/模型训练——六类长任务统一进度条规格（浅蓝 #3D8BFF 单色+百分比+ETA+当前步名）；短任务（<3 秒）一律不出进度条（防闪烁）。

## 9. 修订记录

| 日期 | 版本 | 内容 | 理由/来源 |
|---|---|---|---|
| 2026-08-28 | 1.0.0 | 首版：四路只读盘点（数据/图谱语料/注册表治理/文档）→八族资产打标 49 条（进 36/不进 11/待定 2）+纠偏 7 项（候选 618≠2933/19.5 万演示口径/IG 报告缺失/BTRUN 断链/lead-lag 证伪/模块总账演示口径/creation_token 零命中）；最大发现=产业地图页"待建设"占位 vs ig_* 七表已竣工（DAL-C01 P0） | Owner 指令：盘点全项目模块/自动生成物/表格/数据库/因子库/图谱，裁定哪些进仪表盘；盘点方式=反向账扩展（Owner 拍板） |
| 2026-08-28 | 1.1.0 | **需求族批（§5 新增 R1~R10）**：Owner 以主观交易员（非编程/非量化）视角二批输入 10 条——R1 人机回环纠错（第一优先，⚑反馈按钮体系+反馈点清单）/R2 数据血缘流水线可视化（+新建算法注册表配套资产）/R3 回测对象化+进度条+多策略拟真/R4 进度条清单/R5 AI 第六组（附 IA 拍板条件）/R6 事件研究+预期差（CAND-RES-030 正中下怀）/R7 研评级独立页（14.6 万条在库）/R8 风险偏好光谱图（RRG 已在码，分两期）/R9 天气栏升级不改名/R10 同位调研已内化；随批裁定 3 项（美联储不开单独页/币圈不做光谱地图/天气不改名）；§6 统计并入需求族口径、§7 下一步增 R5 拍板项、原 §5~§7 顺延重编号 | Owner 指令：需求先全倒出→梳理落盘→批复→映射（流程拍板） |
| 2026-08-28 | 1.2.0 | **R11 股权穿透入册**：Owner 三批输入"股权穿透像天眼查，不知道有什么用"——机构实践对照（Wind/iFinD F10 标配=个股档案维度非独立页；量化社区=股东户数/机构持仓标准因子；银行风控=同一实控人合并敞口；天眼查=尽调工具非交易工具）；盘点惊喜=十大股东/十大流通股东已在采集（akshare+QMT 双通道）+股东户数表+质押/解禁 schema 全有，缺仅工商穿透关系（付费）；裁定建议=不开新页三落点（个股档案股权卡/筹码集中度因子/事件日历股权事件），全量穿透图+系族敞口+股权边并产业图谱=远期待数据源 | Owner 指令：股权穿透要不要单独页面+机构实践怎么做 |
| 2026-08-28 | 1.3.0 | **R12 页 1 重构令入册**：Owner 四批输入"全景总览=实盘全景总览，不会看的东西是废纸"——核心定位=只放实盘实时状态（回测/研究不放，研究去专门页）；两大关注=①量化实时分析产出正确性监督（新闻定性等 vs Owner 判断）②项目健康（数据源/治理/系统告警小列表）；机构实践验证=角色专属工作台（彭博 Launchpad/量化平台实盘研究分离），"什么都有"的首页是宣传截图非工作台；重构骨架=资金区不变（L3 折叠=Owner 原创）+研判保留+天气压缩+新增算法实时校验卡（✓/✗ 快速反馈=R1 首站）+新增健康告警条（无告警一行绿）；**一屏不滚动硬约束入册**；改名实盘全景总览；连带=⑥审批/告警形态实质定为横切层；像素压缩归视觉会话 | Owner 指令：全景总览说细（实盘定位+两关注+一屏约束） |
| 2026-08-28 | 1.4.0 | **R13 页 2 重构令入册**：Owner 五批输入"作战指挥太复杂无主次，就两个东西"——①盘前预案（8:00-8:30 隔夜+外盘+期指+韩股）②实时情景跟踪（1-5min 滚动匹配预案+关键位验证）③明日推演（今天盘面→明天惯性→今天仓位联动，T+1 隔夜风险）；情景矩阵升级讨论（Owner 问 3×3×3）——机构实践对照：if-then 预案树（PlayBook）/市场轮廓开盘类型学（Open Rejection Reverse=Owner"下砸又拉回"）/开盘区间前 15-30 分钟独立时段/隔夜风险评估；**裁定建议=不做 27 格认知超载，改时序分段判定**（开盘段/上午/下午各 3-4 互斥形态）；新施工模块 2 件（时序分段状态机+明日推演联动）；其余卡降级折叠 | Owner 指令：作战指挥说细（两板块+情景矩阵升级之问） |
| 2026-08-28 | 1.5.0 | **R14 页 3 重构令入册**：Owner 六批输入"盘中实时改名大盘分析"——页面目的唯一=分析大盘今天实时状态+走势预期；四问直答：①与作战指挥=感知层/决策层（不合页，R13②区引用本页结论）②四指数=一主三辅（机构从不四等分；四指数价值=风格分化信号）③情绪分析=市场宽度（Market Breadth）+分档分布直方图+封板质量，**分布尾部厚度**=Owner"跌 4000 家但多数只跌 0-3%"洞察的专业词；情绪不新开页（本页管今天快照/情绪页管周期位置）④**基本零新模块**（regime/13 参数/宽度/涨跌停/极端预警全 prod 在码，唯一新供数件=正向账 B31）；因子构成面板=R2 可解释性落地；现 p-live 决策链/风控/委托区映射时归队 | Owner 指令：盘中实时说细（改名+四指数+情绪分析图+因子构成） |
| 2026-08-28 | 1.6.0 | **R15 页 4 重构令入册**：Owner 七批输入"板块全景要两个地图+核心不是数据是分析结果"——专业靠山四件：相对强度 RS/上下行捕获率（晨星标准）/威科夫吸筹（弱势中显强势，**项目有 Wyckoff FSM prod 在码**）/RS 持续性（次数>幅度）；形态=相对强度光谱地图（分时双模式，分界=大盘实时涨速）+抗跌榜/领涨榜（次数优先+冲高回落形态标注）+证据链卡；**随批裁定两条升格**：④全站地图颜色统一=右红左绿 ⑤**每页设计铁律=结果+证据链**（R14 单页面板泛化为全局原则）；B26 扩注升级（正向账 v2.3.2） | Owner 指令：板块全景说细（逆势抗跌地图+资金悄悄吸筹洞察+每页核心方法论） |
| 2026-08-28 | 1.7.0 | **§4.J 全量可视化普查入册**：Owner 指令"几千个模块全部扫描一遍，哪些可放进页面"（缘起=Owner 不知项目有 Wyckoff 吸筹）——depgraph 缓存 7,675 模块×73 域四路并行精读文件头实证，S1 铁律过滤+两账去重：**账外富矿 192 件**（J-1~J-20 按目标页分组）；**反差件 8 件**（C1/C8/C18/C21 假缺口/C22/D2/B26/C25——登记为缺实则已落码，正向账 v2.4.0 扩注）；D_CROSS_ASSET 空壳域实证；最大亮点=35 号回撤协议 7 件套/生存线监控/作战室 W 族真源/研评级与数据源监管两新页素材齐套 | Owner 指令：全模块可视化普查 |
| 2026-08-29 | 1.8.0 | **R16/R17 入册（Owner 睡前补两页+同花顺截图 10 张对照）**：R16 情绪页 v2=涨停强度今昨对比卡/连板天梯/涨停质量三维/涨停基因完整口径/成交额对比卡/算法查看小图标泛化；R17 新闻页 v2=重头是分析不是看新闻——两天滚动窗清单/点击展开详情+分析/今日整体分析/预期差/远期=产业趋势甘特图+订单季报前瞻页；专业词=叙事经济学/订单前瞻/盈利动量/PEAD；缺模块记正向账 v2.5.0（D20 人气榜源/B32 涨停强度+天梯/B33 成交额对比/B34 新闻时间窗/C29 订单季报前瞻） | Owner 长城任务指令：新两页内容写入文档 |
| 2026-08-29 | 1.8.1 | **§8 全页施工蓝图（长城任务二裁定批+任务三缺失清单，AI 自主裁定）**：裁定依据=铁律+第一性原理+100% AI 开发战略（**仪表盘=可校验层**）；处置四档（prod 即接/testing 标"试验中"/design 标"规划中"/无源标"待接入"）；裁定批 5 项=新页三成立（研评级/数据源监管/模型页）+订单季报远期+算法查看图标泛化+每页一句话核心置顶+**Owner 待裁定 5 项**（AI 第六导航/打板 sleeve 启用/C03 产物核实/审批告警形态确认/模型页归属）；36+3 页逐页核心一句话+施工内容+无源占位；进度条清单六类长任务规格 | 长城任务二/三：全页面铁律检查升级 |
| 2026-08-29 | 1.9.0 | **长城任务四/五 全面施工闭环+灾后恢复实录**：§8 蓝图全落地（原型 v3.9→v4.0，36→39 页：页 1~6 重构令+新页 3 件+P0 接线纠偏+任务五修复包）；验收=browser_use 两轮 17 项全 PASS（39 页零 JS 错误）+合规 P0/P1/P2=0；备份 v4.0（869,707B，MD5 4F35C171AC5FA84D21728518C0785932）；写锁协议首次实战零冲突；**事故实录**：GitCommitGateway stash 隔离在门禁失败路径回滚未提交变更（v1.7.0~v1.8.1 一度丢失），按上下文快照重放恢复——教训=账本写完即提交+网关运行前 .runtime 快照 | 长城任务四/五：全面施工+全页审查+模板保全+灾后恢复 |
| 2026-08-29 | 2.0.0 | **五裁定落盘+Owner 三屏实证催生 R18~R20**：①原型 v4.1（41 页：AI 第六组两页+打板仿真监控+产业链联动日报卡+审批四合一横切条+模型页 J-14 全家）+目录契约 v1.3.0（.html 白名单，原型首入 git 追踪）②**R18 页 1 二次再定位**：Owner 三屏多开盯盘实证——综合首页"什么都有不精"不会点开，唯一不可替代=全资产资金总览；新主体=项目全景地图（depgraph 父子树+中文名简介+跳代码+数据流遥测，对标 Grafana Node Graph 非彭博）③**R19 模块化组合两期裁定**：引擎便宜（gridstack 级）贵在 250 卡组件化——一期机制+试点页，二期搭各页施工便车不突击 ④**R20 4K 屏密度**转视觉线（Owner 主力硬件 4K×3，流体布局+compact 密度+一屏原则）⑤数据契约层**改判不冻结**（Owner 指令：页面数据全敲定后才冻结施工，缺口账保持活登记账防返工） | Owner 指令：五裁定按倾向执行+三屏使用场景再讨论（只落盘文档不改仪表盘） |
| 2026-08-29 | 2.1.0 | **R21 入册（R18 同日追加批）——首页=全员结论汇报墙+改名「全景总览」**：Owner"老板看员工一句话汇报"模式——每页产出标准化 verdict 结论卡（突出标题+最多两行字，讲几个东西出几张卡），首页按实盘交易顺序聚合抓取（作战指挥=昨天预案/今天匹配/明天推演 三卡天然对应 R13 三区）；**铁律扩展**：§8 裁定批④"一句话核心置顶"升级为 verdict 卡=页面标准化输出口（Verdict-as-API），首页=聚合消费方不另写文案（真源唯一防漂移）；系统健康卡+AI 对话框常驻；一屏硬约束延续（4K compact 一屏 40+ 卡容量 vs 实盘 ~20 卡需求富裕）；空间冲突裁定=一屏给结论墙，项目全景地图（R18）降为首页内"展开全屏"入口层；改名去"实盘"二字 | Owner 指令：首页补充讨论（快速浏览全部结论+每页结论区+一屏不下滑+改名） |
| 2026-08-29 | 2.2.0 | **多会话并行协作方案入册（Owner 指令：讨论效率提速，一对话管一板块）**——①分工按导航组切：会话 A=实盘交易（A股组+币圈组）/会话 B=研究域/会话 C=数据组/会话 D=系统+AI 组+首页（R21 结论墙聚合机制归 D，各页结论卡内容由各板块会话自定）②纪律四条：**讨论期**各记各本子（docs/_working/2026-08-29-dash-{A实盘,B研究,C数据,D系统AI}.md），公共三本账由收口方统一合并（禁多会话同写一账）；**施工期**改原型 HTML 前必取 DASHBOARD_WRITE.lock（注明谁在用/改哪段）用完即还；改完立即 git add 暂存（实证：未暂存编辑会被并发网关 stash 周期吞噬）；全完工后单会话做全站一致性收口审查（导航/搜索索引/跨页引用/命名）③实证依据=本日功能线（本账）与视觉线（K 线引擎）并发一天，冲突两起均被锁协议兜住 | Owner 指令：多开对话并行讨论各板块，问冲突与可行性 |
| 2026-08-29 | 2.3.0 | **R22 入册——拆分即转正+终局结构治理先行**：①单文件不可真并发（实证 nav 覆盖两起），拆分=并发施工与 R19 物理前置 ②拆分即终态永不合并 ③拆分即转正：直接进 src/zephyr/frontend/dashboard/web/ 终局家（index.html+assets/styles/core/pages 五件套），避免二次搬迁 ④旧版 Panel 盘点：14 Tab 中 11 个新版已覆盖，**独有活资产仅 Tick 回放**（production，登记进复盘/回测页），知识库概览=空壳不搬（KB 已退役），旧版不删标 deprecated ⑤治理先行四件套：trae_028 容量（pages/ 41≤60 封顶，破 60 按组拆）+目录契约门禁（v1.3.0 白名单已开）+trae_024 单一类型+命名=页面 id 机械映射——正面回应 Owner"文件臃肿/漂移/幻觉"历史痛点 ⑥执行序：拍板结构→视觉线收尾后拆分手术→Tick 回放登记+旧版 deprecated→正式结构上四会话并行迭代→契约冻结后接通验收 | Owner 指令：拆分后是否合并+模板 vs 正式+搬迁治理顾虑讨论 |
| 2026-08-29 | 2.4.0 | **R23 入册——Owner 实测旧版 Panel 后的融合令（"两个都要，一个都不落下"）**：①作战指挥=旧版四区清晰骨架（前日预案/分时段判定表/惯性推演/四指数 regime 卡）+新版全部细节并集 ②回测页=旧版图表细节全量搬运（顶部信息条/6 KPI 卡/五子 Tab/三线收益图/hover 十字线精确读数/双色回撤图/日收益红绿柱）+新版治理件保留 ③QMT 文件桥健康详细卡→系统状态页（整体状态/分终端降级原因/四导出文件延迟秒数/在途挂单/持仓/可用资金）④修复旧版 app_panel.py QMT 周期回调重复注册崩会话 bug（同文档幂等守卫）+websocket 白名单——旧版服务已可跑通实测 ⑤融合原则入册=信息架构取 Owner 体感更清晰者，内容与细节取并集 | Owner 指令：实测旧版后的融合需求整理（先不忙执行） |
