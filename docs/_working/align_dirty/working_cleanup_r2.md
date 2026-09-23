---
status: active
title: "_working 全清第二轮 — 四态总账与三清单（R2）"
module_id: ""
blueprint_id: ""
version: "1.0.0"
created: "2026-09-24"
updated: "2026-09-24"
ttl: "task_bound"
---

# _working 全清第二轮 — 四态总账 + 三清单 + 归档执行记录

> 依据=docs/_working/align_dirty/align_dirty_ledger.md【总指挥批注 R2·03:45】 · 本文件为**派生产物**（生成器=`.runtime/tmp/working_cleanup_r2/assemble_r2.py`），禁手改
> generated_at=2026-09-24 07:43:11 · 已回收分片=['shard_02.yaml', 'shard_03.yaml', 'shard_04.yaml', 'shard_05.yaml', 'shard_06.yaml', 'shard_07.yaml', 'shard_08.yaml', 'shard_a.yaml']

## 0. 口径与分母（先给尺子，再给数）
- 单位集=docs/_working 顶层 57 目录 + 112 散件 = **169 unit**（权威枚举=Python `Path.iterdir`）。
- 尺子坑（承本包 D7 同族）：`bash find` 在本 shell 下因中文目录名（`同花顺资料`）GBK 崩 → 少算 1，故分母不取 find 口径。
- Owner 点名面 `docs/02_.../07_trading_decision_architecture/design_memos/`：现场 2 件、归档侧 49 件（见 §6）。
- 三查=①HEAD 最后提交 ②在飞占用（worktree/staged 脏 + 磁盘 mtime<4h + 他会话 claim + 会话 worktree 同名）③内容施工态（关键词粗筛 + 分片读原文终判）。
- 四态归一：分片终判 ①②③ 优先（承 W8 先例：围栏是过程筛不是终态）；只有机械围栏证据而无终判者记 ④。
- 机械标记（结案词/待裁词命中数）只是粗筛，终判以分片读原文为准；不一致处自动登记 §1.2 供抽查。
- **双活判据自纠**：第一版只查 `archive/<月>/<同名>` 顶层 → 漏判嵌套归档子目录（`c_class_scattered/`、`factory/` 等），经 shard_04/07 两代理独立指出后改递归 basename 比对；twin 由 23→118、其中**字节等值 9→108**（泛用名 index.md/README.md 零命中，非撞名假阳）。含义：第二轮的**主活是「去双活」而非「再归档」**。
- **附加发现（非四态，由本任务分片揪出，详见 §8c）**：`docs/_working` 存在明文 API 凭证件，归档侧同内容双份、两份均已入 git 历史。

## 1. 四态总账

| 态 | 件数 | 去向 |
|---|---|---|
| ①施工完毕 | 105 | §3 结案报告 + §7 归档/去重处置 |
| ②应进蓝图未进 | 14 | §4 待升级条目清单（交总指挥裁） |
| ③未施工 | 18 | §5 未施工清单（交总指挥分派） |
| ④在飞围栏 | 32 | 本轮零触碰，落地后复跑 |
| 待问 ask | 0 | §8 |
| 未判 | 0 | 分片未回收 |

### 1.1 逐件台账

| unit | 类 | 件数 | HEAD末次 | 态 | 态来源 | 归档双活 | 标记(结案/待裁) | 置信 | 在飞证据 / 一句话 |
|---|---|---|---|---|---|---|---|---|---|
| `2026-08-22-frontend-backend-gap-ledger.md` | file | 1 | 2026-09-15 | 1 | 分片 | 等值 1/1 | 6/17 | mid | 「前端有、后端没有」手工缺口总账 v2.0→v2.5.0：101 项（A 接线/B 供数/C 能力/D 数据源）四分类登记 + 施工顺序 + Owner 2026-08-25 登记纪律，v1（33 项，被误删）按 Own |
| `2026-08-24-aiarch-construction-list.md` | file | 1 | 2026-09-15 | 1 | 分片 | 等值 1/1 | 7/8 | high | 09 号 AI 架构层 21 份文档全量审查（T3）产出的「未施工/部分落地」清单：P0 Owner 窗口 5 件 + P1 7 件 + P2 9 件 + P3 14 件，逐件给来源文档/建议落点/建议 MOD 号/验收 |
| `2026-08-24-designmemos-construction-list.md` | file | 1 | 2026-09-15 | 1 | 分片 | 等值 1/1 | 17/5 | high | design_memos 61 份全量审查（T3）产出的待施工清单 28 项（P0 1/P1 6/P2 11/P3 6/Owner 窗口 4），逐件带来源 memo、建议落点、号段顺延纪律与验收标准 |
| `2026-08-28-remaining-construction-roadmap.md` | file | 1 | 2026-09-15 | 1 | 分片 | 等值 1/1 | 6/6 | mid | 2026-08-28 全量审查批（85 篇设计文档 × 代码实证）的统一派单真源：A 类可立即排期 22 项 / B 类外部阻塞 21 项 / C 类裁定不施工 10 项 / 09 域 GP1+ 13 项，附波 0-5  |
| `2026-08-30-b16-feed-exploration.md` | file | 1 | 2026-09-15 | 1 | 分片 | 等值 1/1 | 15/6 | mid | B16 勘探裁定：26 号文六因子矩阵中 dReport / Jump on PEAD 两因子的输入数据可得性 grep 实证（daily_event 族 + DDL-as-Code + 计算件落码状态），结论=GO |
| `2026-08-31-frontend-governance-four-piece-drafts.md` | file | 1 | 2026-09-15 | 1 | 分片 | 等值 1/1 | 6/3 | high | 前端治理四件套设计（技术手册/功能验收单/前端模块契约/frontend_map 第六全景图）+ 六项 Owner 裁定 + 统一对账字段设计（has_frontend/no_frontend_reason/fronte |
| `2026-09-04-trading-decision-map-discussion.md` | file | 1 | 2026-09-15 | 1 | 分片 | 等值 1/1 | 2/9 | high | 交易决策地图（第 7 张地图）43 轮讨论裁定录：D1-D122 全部终裁（三流骨架+四路传感器阵列+环节×状态矩阵+proposed/verified 置信度管道+知识层 PIT effective_from），逐轮带 |
| `2026-09-05-audit-greatwall-report.md` | file | 1 | 2026-09-15 | 1 | 分片 | 等值 1/1 | 4/5 | high | 二十一域无人值守全仓审计总报告：6 修复波 + 复审 2 波 + 机械专项，发现 1548 → 修复 893 + 618 登记台账 + 37 跨域移交，align_all 七图硬问题清零，最终判定=通过；附 A 类代码级 |
| `2026-09-05-steward-b-class-owner-book.md` | file | 1 | 2026-09-15 | 1 | 分片 | 等值 1/1 | 2/5 | mid | STEWARD-20260905 总管 B 类 24 项处置书：已施工 8 commit 备案 + 逐项「事实基线→总管核实→建议」的 Owner 裁定入口（错误码四族/silent except/运行时装配批/ROOR |
| `2026-09-06-flash-execution-report.md` | file | 1 | 2026-09-15 | 1 | 分片 | 等值 1/1 | 2/9 | high | Owner 裁定执行批二（Flash 无人值守施工报告）：A 41 前缀 183 类占位码转正 / B 34 契约码 B21 落码+C6 deferred / C orchestrator 接线 / D pre_writ |
| `2026-09-07-tdm-internal-factpack.md` | file | 1 | 2026-09-15 | 1 | 分片 | 等值 1/1 | 2/4 | high | TDM 拼装回测前置审查材料⑤（内审事实包）：脚本解析真源 YAML 对 62 条交叉引用逐条语义核对 + 33 模块锚定接线状态 + 10 个 DS 回测可得性 + PP-001 对齐 + 13 个 paper 节点清 |
| `2026-09-07-tdm-pre-backtest-review-checklist.md` | file | 1 | 2026-09-15 | 1 | 分片 | 等值 1/1 | 2/13 | high | TDM 拼装回测前全面审查清单 v1.3.0（外部模型用）：九维 A-J 检查点 + 循环收敛协议（硬门槛 B=0/M=0、软门槛连续一轮零新增、上限 5 轮）+ 多子代理并行分派矩阵 + §5 已知边界 11 条勿报声 |
| `2026-09-07-tdm-review-round-report.md` | file | 1 | 2026-09-15 | 1 | 分片 | 等值 1/1 | 2/17 | high | TDM 外审 Round 1 + Round 2 问题报告归档：Blocker 13/Major 61/Minor 60/Suggestion 22/J 新增 30 全编号留档，修复记录（地图 132→166 边 + 2 |
| `2026-09-09-clearance-night-report.md` | file | 1 | 2026-09-15 | 1 | 分片 | 等值 1/1 | 2/8 | high | 治理清偿六连（环境欠账清偿+门禁加固）施工晨报：T1 reaper keep 行清理 / T2 测试缓存权限（验收达成）/ T3 面板超时加固（并发规则跳过登记）/ T4 提交门禁「只查自己」改造 / T5 登记表批量修 |
| `2026-09-09-greatwall-quality-task-brief.md` | file | 1 | 2026-09-15 | 1 | 分片 | 等值 1/1 | 2/4 | mid | 2026-09-09 夜产业链图谱「全量质量修复+扩产」六线并发长城任务指令书（SOP v1.5.0 时间盒 10h）：DDL v4 十三表部署、股权穿透 ig_equity_edge、供应边两列、指标层 PIT 化、t |
| `2026-09-09-news-industry-wiring-directive.md` | file | 1 | 2026-09-15 | 1 | 分片 | 等值 1/1 | 2/3 | high | 「实时新闻+产业链→盘中决策」后端接线施工指令：W1 图谱查询服务化/W2 新闻实时性核对/W3 事件图谱传导器/W4 冲击标的生成器/W5 盘中消费端点/W6 DS 登记，入图交增长轨 |
| `2026-09-09-node-backtest-governance.md` | file | 1 | 2026-09-15 | 1 | 分片 | 等值 1/1 | 2/5 | high | 节点级可回测治理全量问题清单 PB-01~PB-16（含业界对照调研）→ Owner 2026-09-09 精简裁定（10 保/3 降/3 砍）→ §八 三期施工方案（P0 地基 3/P1 验证 6/P2 闭环 3 落盘 |
| `2026-09-09-node-template-draft.md` | file | 1 | 2026-09-15 | 1 | 分片 | 等值 1/1 | 1/7 | high | 链/环节/公司三层节点模板草案与 17 项决策点终态（Owner 2026-09-09「按建议」全裁定），含 ig_equity_edge 股权穿透表设计与专业名词对照表 |
| `2026-09-09-tdm-growth-blueprint.md` | file | 1 | 2026-09-15 | 1 | 分片 | 等值 1/1 | 8/4 | high | TDM 病菌寻路增长轨施工文档：五步循环+六向寻路作业矩阵+防噪音四道闸+职能完备性对照+增长台账（G1~G6 三态销账）+§6 晨审指令+§7 批3（G3 币圈六向+八树枝锚提案） |
| `2026-09-09-tdm-missing-modules-construction.md` | file | 1 | 2026-09-15 | 1 | 分片 | 等值 1/1 | 3/3 | high | TDM 缺失模块全面施工总纲（C 类 12/B 类 10/A 类回填 41/D 类不建）+ 连续六轮执行台账（夜班1/夜班2/四批开工令/全景图体检/落库终态/自裁批/S24 下架链审查/L2-01-L2-04 复核） |
| `2026-09-09-tdm-night-greatwall-directive.md` | file | 1 | 2026-09-15 | 1 | 分片 | 等值 1/1 | 2/3 | mid | TDM 缺失模块夜班长城任务指令（23:00→09:00）：模型与角色分工、开工序列、单模块 8 步微循环、机械审查循环协议、红蓝对抗 ≥3 手法、CORE-ALGORITHM 标记清单、交接包契约、夜班禁令 |
| `2026-09-10-chainmap-frontend-batch-plan.md` | file | 1 | 2026-09-15 | 1 | 分片 | 等值 1/1 | 2/6 | mid | 产业链前端（chainmap 页）3D 三期+收尾批次计划 B1~B8：B1 加载态/B2 族级星云/B3 链群小星云（REVOKED）/B4 单链甬道 TDM 化/B5 下钻树/B6 缩放打磨/B7 S21 断链标注/ |
| `2026-09-10-legacy-clear-night-report.md` | file | 1 | 2026-09-15 | 1 | 分片 | 等值 1/1 | 2/7 | mid | 治理清偿遗留收尾+门禁加固推广晨报：T0 晨报收尾/T2 pytest_cache 权限验收级修复/T3 registrar 演进断言治本/T4 .runtime 残留清理/T5「只查自己」gate 推广（3 gate+ |
| `2026-09-10-nodebt-night-report.md` | file | 1 | 2026-09-15 | 1 | 分片 | 等值 1/1 | 4/5 | high | 节点级可回测治理 P0→P1→P2 过夜施工晨报：c1_backtest 台账新建、验证方法学与 DAL 登记、param_origin、holdout 节、前端验证档案区+画布徽章、衰减巡检尾随事件，10 条自行裁定留 |
| `2026-09-10-xflow-batch-report.md` | file | 1 | 2026-09-15 | 1 | 分片 | 等值 1/1 | 2/5 | high | X 流验证批（节点级可回测治理第二期风控批）收尾报告：T1 决策价+订单类型入流水、T2 信号消融对照器、T3 验证批接线与首跑，附 7 条自裁与提交链 |
| `2026-09-10-xflow-followup-design.md` | file | 1 | 2026-09-15 | 1 | 分片 | 等值 1/1 | 2/6 | high | X 流验证批遗留四项分诊跟进：④exec 滑点 v2 口径与③SellSignal→XFlowAction 转换助手（两件已施工+单测）、①holdout 定稿锚点方案（设计稿→后经 Owner 裁定施工）、②消融实弹执 |
| `2026-09-11-backtest-evidence-log-discussion.md` | file | 1 | 2026-09-15 | 1 | 分片 | 等值 1/1 | 2/4 | high | 回测证据链与验证档案讨论稿：现状防撞车盘点（node_verdict 台账/五类方法学已施工）+增量缺口 G1-G3+三层证据体系设计+命名规范+除日志外回测需规范清单，Owner 2026-09-11 R1-R5 全认 |
| `2026-09-11-backtest-system-sop-discussion.md` | file | 1 | 2026-09-15 | 1 | 分片 | 等值 1/1 | 2/3 | high | 回测体系全链路 SOP 讨论定稿：分级回测颗粒度、AI 自驱回测 SOP、聚宽 600 条策略植入路径三问定稿+七步打通顺序+D1-D4 决策记录（基准区间/预注册禁挪门柱/10 条 shim 试点/盘中日线近似降级） |
| `2026-09-11-chainmap-final-batch-report.md` | file | 1 | 2026-09-15 | 1 | 分片 | 等值 1/1 | 2/4 | high | 产业地图（chainmap）收尾批报告：字遮挡根因治理（墓碑名剥离+卡高/行高钉死）+重心法拓扑排序+两指令对账收口+四件套 ACC rev6，末段附 2026-09-14「全部开工」复启批销账 |
| `2026-09-11-commit-queue-dead-zero-closure.md` | file | 1 | 2026-09-15 | 1 | 分片 | 不等值 | 5/3 | mid | commit_queue 死信清零收尾+死信率告警最小落地：952 项死信全量甄别（REQUEUE 757/PURGE 184/REVIEW 5）、保护路径死循环治本选 A、THD-ALERT-003/004 阈值入 R |
| `2026-09-11-crypto-shadow-mvp.md` | file | 1 | 2026-09-15 | 1 | 分片 | 不等值 | 3/3 | mid | 币圈影子 MVP 收尾报告（doc_type: audit_report）：交付清单与状态、B-1/B-2 registry 口径修复、采集器 3 处运行时 bug 修复、合成样本烟测（如实声明非真实数据）、OKX 端点 |
| `2026-09-11-l308-aggregator-construction.md` | file | 1 | 2026-09-15 | 1 | 分片 | 等值 1/1 | 1/3 | high | TDM-E-L3-08 候选池汇总件施工文档：按 C13 纯函数核范式落码 candidate_pool_aggregator.py+37 测试+门面接线，并给增长轨落图规格（module_ref/algo_refs/边 |
| `2026-09-11-news-chain-wiring-spec-cards.md` | file | 1 | 2026-09-15 | 1 | 分片 | 等值 1/1 | 3/3 | high | 「实时新闻+产业链→盘中决策」后端接线交付包（wiring-news-ig-001）：W3/W4/W5 三张节点规格卡（坑位回填材料）+W1/W2 反查核对结论+24h 窗 800 条新闻端到端 dry-run+深夜批（ |
| `2026-09-11-tdm-morning-review-report.md` | file | 1 | 2026-09-15 | 1 | 分片 | 等值 1/1 | 2/3 | high | TDM 全景晨审：A 施工轨 10 模块六点复检（9 测试套 241 绿）+ B 增长批2 四项 + C 8890 实测 138 节点/194 边与真源一致、40 红节点全判预期红 + D 六项裁定落笔 + 批3 八树枝 |
| `2026-09-12-alt-data-batch1-construction-report.md` | file | 1 | 2026-09-15 | 1 | 分片 | 等值 1/1 | 2/5 | high | 另类数据第 1 批施工报告：千股千评全表日快照 + 航运运价长表（BDI 1988 起）两源落地，三任务实弹 5,196/22,274/33 行、测试 14/14 绿；票房断供缺口登记；alt_data 治理三件首次实弹 |
| `2026-09-12-expectation-consumption-design.md` | file | 1 | 2026-09-17 | 1 | 分片 | 等值 1/1 | 2/5 | high | 研报/一致预期消费端设计 v1.0：第一性原理定性质（预期侧）+ 机构/学术调研 + M1-M5 五模块 + 分期施工 + EXP 族 IS/OOS 预注册（§8，冻结禁挪）+ research_report 预测槽位= |
| `2026-09-12-fundamental-consumption-design.md` | file | 1 | 2026-09-15 | 1 | 分片 | 等值 1/1 | 6/5 | high | 财报事实侧消费端设计 v1.0：Owner 两问大白话作答 + 机构/开源调研 + 字段可行性实测 + M0 质量闸门/M1 派生层/M2 八因子/M3 事件族/M4 LLM 深读/M5 挂接六模块 + F1-F5 分期 |
| `2026-09-12-handoff-c3-zcode.md` | file | 1 | 2026-09-15 | 1 | 分片 | 等值 1/1 | 6/3 | mid | 晚班收官交接：P0 印教材+检验批、C2 成绩灌表 597 行、因子准入判据成文、红蓝 3 修复 9 用例的证据位置交底；C3 翻译试点三件验证三形态 + 翻译方法论；§五 列四项未入库挂起；§六 列批量翻译→C4 快筛 |
| `2026-09-12-igfact-ckg2021-data-asset-analysis.md` | file | 1 | 2026-09-15 | 1 | 分片 | 等值 1/1 | 1/3 | mid | ig_fact CKG2021 资产定性：264,072 条不是重复数据，而是 205,789 条未入图供应链关系 + 95,383 个未入图产品名（仅 46 条有 ig_edge 对应、184 个已入图）；按四桶给处置 |
| `2026-09-12-research-report-data-plan.md` | file | 1 | 2026-09-15 | 1 | 分片 | 等值 1/1 | 2/5 | high | 研报+分析师预测数据侧施工方案定稿：新建 c3_fundamental.research_report 明细表（替代把研报元数据塞 news_data 丢字段的旧路）+ 回补器 + 五处共享文件接线（provider c |
| `2026-09-12-research-report-handoff.md` | file | 1 | 2026-09-15 | 1 | 分片 | 等值 1/1 | 2/3 | mid | 研报/一致预期消费端交接包：一句话现状（数据侧+派生层+因子函数库全落地入库）+ 已完成可审计清单 + 有意分期排队表 C1.5/C2/C3/C4/C5 + 新会话必读序 + 相关工作文件全路径 |
| `2026-09-13-c5-cluster-differentiation-report.md` | file | 1 | 2026-09-15 | 1 | 分片 | 等值 1/1 | 2/3 | high | C5 差异化对质与正式入库：37→45 条已批测策略聚类对质（v1/v2/v3 三轮）、RSRS 升级寻路穷举至噪音断崖封矿、双版本 PB-POE 处置与 bothwin 升文件粒度、附六按 SOP-C §6/§8 转正 |
| `2026-09-13-factory-gate-review.md` | file | 1 | 2026-09-15 | 1 | 分片 | 等值 1/1 | 6/3 | high | 策略工厂图门禁任务审查（交接指令 v2 第零段）：结论 B（通过但需修正）——纠正五件套 3/5 已落地而指令按未建规划、发现 HEAD 断链与上班遗留脏工作区、裁剪 field_dictionary、给 §6 批0+批 |
| `2026-09-13-io-structure-anchor-plan.md` | file | 1 | 2026-09-15 | 1 | 分片 | 等值 1/1 | 1/3 | high | 投入产出表结构锚薄方案：以 2020 年全国 IO 表直接消耗系数为产业链图谱引入官方结构真源（补 tier 退役遗留的判定依据缺口），四条口径裁定 D1-D4（主锚 153 部门/降级锚 42 部门、映射规则=YAML |
| `2026-09-13-p002-semantic-review.md` | file | 1 | 2026-09-15 | 1 | 分片 | 等值 1/1 | 2/3 | high | P0-002 状态语义复核（Owner 三步序第①步）：以两个 VAL run 档案做 IS/OOS/全样本三段对照，判定「档位方向样本外整体反转，牛市态 OOS 最亏、低波/熊市态反而最赚」=态标签语义失效而非分辨力不 |
| `2026-09-13-panic-rebound-sim-paper.md` | file | 1 | 2026-09-15 | 1 | 分片 | 等值 1/1 | 1/3 | mid | 恐慌反弹（CAND-e3da6fa71af1）sim/paper 前哨建图：策略出生证+身份证字段化、三窗口成绩单（IS 1.15/OOS 0.83/S3 0.98，唯一三窗全绿）、前哨配置（≥20 交易日、UP-1 波 |
| `2026-09-13-strategy-factory-pipeline-discussion.md` | file | 1 | 2026-09-15 | 1 | 分片 | 等值 1/1 | 2/5 | mid | 策略工厂流水线讨论稿 v1→v10 累加：五车道（含 E4 考试咽喉=已建 C4/DSR/OOS/年衰减）+ 产品清单与字段定稿（身份证+出生证，对标 C2PA/HF Model Card，AI 禁手填）+ 防幻觉/防漂 |
| `2026-09-13-tdm-upgrade-blueprint.md` | file | 1 | 2026-09-15 | 1 | 分片 | 等值 1/1 | 2/3 | mid | TDM 升级蓝图 v0.1→v0.2：分布预测（车道 E）嵌入交易决策五候选 UP-1 凯利/波动率目标仓位、UP-2 前瞻概率止损、UP-3 前瞻风险预算、UP-4 板块分布比较选优、UP-5 尾部对冲指令，按四道闸逐 |
| `2026-09-13-xtreme-redblue-retest.md` | file | 1 | 2026-09-15 | 1 | 分片 | 等值 1/1 | 2/7 | mid | 极限红蓝对抗复测：堵点总账根治批（F3/F5/F1/D5）之后，按上轮同构方法重跑串行计时+5 路子代理并发（1 拆分者+3 编辑者+1 坏图攻击者），总判定=历史事故形态 100% 防住、堵点 1/2/3/溯源观测全闭 |
| `2026-09-13-xtreme-redblue-v3-log.md` | file | 1 | 2026-09-15 | 1 | 分片 | 等值 1/1 | 2/16 | high | 极限红蓝对抗 v3 逐场景执行日志（GLM 5.3 Flash 红方，基线 HEAD=7a4efc8113）：裸 commit/`--no-verify` 拦截实证、worktree 落账三要素、并发五路、blackou |
| `2026-09-13-xtreme-redblue-v3-plan.md` | file | 1 | 2026-09-15 | 1 | 分片 | 不等值 | 2/11 | high | 极限红蓝对抗 v3 测试方案（低能力模型执行版）：场景矩阵 S1-S4、铁律（只记录不修复/禁 push/禁区不碰）、日志格式规定 |
| `2026-09-13-xtreme-redblue-v3-report.md` | file | 1 | 2026-09-15 | 1 | 分片 | 等值 1/1 | 2/8 | high | 红蓝 v3 结果报告：总判定「有条件通过」，1 个 P0 候选+4 个 P1+9 条 P2 缺陷清单、堵点对账表（主网关 10/10 精确、worktree 六类外 4/4 落 UNKNOWN）、§5 修复建议（只建议不 |
| `2026-09-14-agg-switch-design.md` | file | 1 | 2026-09-15 | 1 | 分片 | 等值 1/1 | 1/3 | high | TDM AGG 消费切换设计：把 AGG 状态输入源从 HMM dominant 换为锚定风险四档；核心决策=仓位数字与状态路由分家（连续 cap 灰度曲线，min 结构去双重计算），并锁 FQ-01 应计剔除器接线点 |
| `2026-09-14-auto-mount-research.md` | file | 1 | 2026-09-15 | 1 | 分片 | 等值 1/1 | 2/5 | high | 策略自动挂图可行性调研（三轮全网挖矿）+ 立项登记：裁定建 auto_mount 自动挂图器，全自动 only-add（只新增挂载，永不自动删/挪），五步管线+验收五条+净零声明 |
| `2026-09-14-c4-history-repair-plan.md` | file | 1 | 2026-09-15 | 1 | 分片 | 等值 1/1 | 2/3 | high | C4 历史修复工程方案 v1.0：用 research_report 自带 PDF 原文提取发布时点盈利预测，四层架构（c4_fetcher 下载→PyMuPDF 文本→启发式+LLM 两层提取→新表落层）+验证三层+验 |
| `2026-09-14-ch-connection-handoff.md` | file | 1 | 2026-09-15 | 1 | 分片 | 等值 1/1 | 2/3 | high | CH 连接统一治本交接文档：根因=各模块自建裸 clickhouse_driver.Client 致 Code:181 间歇断连；方案=一律走 DatabaseService.get_clickhouse_conn()， |
| `2026-09-14-chart-pattern-mining-report.md` | file | 1 | 2026-09-15 | 1 | 分片 | 等值 1/1 | 6/6 | high | 图形库病菌寻路挖矿报告两批：批一登记 19 条（256→275，v2.16.0）+驳回 2+长尾清单；批二登记 12 条（→287，v2.17.0）+长岛驳回终态；§十 schema v2.2 新增 refinement |
| `2026-09-14-combination-layer-exhaustive-charter.md` | file | 1 | 2026-09-15 | 1 | 分片 | 等值 1/1 | 2/5 | mid | F-06 组合层穷尽网格立项稿 v1+v2：八维→十三维 schema（含 active_if 折叠）、N→N_eff 双口径记账、两批次执行策略（A 普查→fANOVA 结构知识→B 子空间穷尽）、验收口径修订、裁定记 |
| `2026-09-14-dsr-enable-impact-assessment.md` | file | 1 | 2026-09-15 | 1 | 分片 | 等值 1/1 | 2/3 | high | DSR 默认开启冲击面评估：纠正「DSR 是概率不是夏普」、台账 1102 行实测分布、三坑（num_trials 口径/阈值口径/fail-closed 误杀）、2.69σ 数值勘误、三步走建议+Owner 待裁五项； |
| `2026-09-14-fac-e1c-formula-mining-design.md` | file | 1 | 2026-09-15 | 1 | 分片 | 等值 1/1 | 2/6 | high | FAC-E1C 公式挖掘机设计稿 v1：AlphaGen/gplearn/双轨选型对比、与 E0-E5 工厂咬合数据流、防过拟合四件套对接、四项开放决策；附 Owner 全批裁定与 gplearn 轨 MVP 施工实绩（ |
| `2026-09-14-handoff-market-data-repair.md` | file | 1 | 2026-09-17 | 1 | 分片 | 等值 1/1 | 5/5 | high | 行情数据时区修复+tick 补数的会话交接包：已完成清单（5min/1min 六月-七月偏移回正、tick 下载验证、管线复活）、P0-2/P0-3 待办、环境与表结构铁律、关键实测数据、工作文件清单 |
| `2026-09-14-indicator-mining-batch4.md` | file | 1 | 2026-09-15 | 1 | 分片 | 等值 1/1 | 1/3 | high | 技术指标库批 4 挖矿报告（mining_sop 首次用于指标域）：R1-R5 五轮日志、防噪音四闸、立卡 3 张（STOCH 本体/TA-Lib 动量清偿/BRAR+CR 能量族）、长尾 M-L1~L6、停挖转施工建议 |
| `2026-09-14-lane-c-agentic-mining-charter.md` | file | 1 | 2026-09-15 | 1 | 分片 | 等值 1/1 | 2/3 | high | 车道C 二轨立项申请书（LLM 智能体挖矿轨，取代原 AlphaGen 立项划界）：三代际检索结论、P0/P1/P2 范围、与 gplearn 轨互补关系；附 Owner 全批裁定与 P0 试驾对照笔记（AlphaAge |
| `2026-09-14-market-data-gap-report.md` | file | 1 | 2026-09-16 | 1 | 分片 | 不等值 | 6/2 | mid | 行情数据缺口修复主报告（v2 重建版）：五张分钟表时区偏移修复口径与天级判定升级、tick 三天批量补数终验、采集管线退化三层根因复活、P0-2 全历史 15.6 亿行重写、晚间批与 09-15 晨班闭环、验证口径速查 |
| `2026-09-14-p0-syntax-gate.md` | file | 1 | 2026-09-15 | 1 | 分片 | 等值 1/1 | 2/3 | high | 红蓝 v3 P0-1 语法门禁修复工作日志（批 2）：SYNTAX-VALIDATION gate 本体+单测+接线登记，扫描源语义改为本 commit files 参数、fail-closed/fail-open 分界 |
| `2026-09-14-p002-reprint-result.md` | file | 1 | 2026-09-15 | 1 | 分片 | 等值 1/1 | 6/3 | high | P0-002 判定器重印批结果报告（裁定#229 第②步）：v1 趋势双确认否决→探针→v2 vol_pct 风险四档定稿，收益判别如实 pending、风险判别双段全过，裁定#230 判据对象切换自裁并执行→P0-00 |
| `2026-09-14-pattern-consumer-plan.md` | file | 1 | 2026-09-15 | 1 | 分片 | 等值 1/1 | 2/3 | high | 图形库消费端方案 v1.0（冻结待施工）：内部断点盘点、C1 装配根/C2 信号管线+meta 门/C3 纯消费调权/C4 三端点+页/C5 边界登记/C6 不做，§四挖矿六向日志，§五 W-C1~W-C4 批切分 |
| `2026-09-14-sim-partition-discussion.md` | file | 1 | 2026-09-15 | 1 | 分片 | 等值 1/1 | 1/3 | mid | 模拟盘分仓专题讨论材料（Owner「钱混一起无法归因」直答）：分仓三方案对比并推荐先 C（账本模拟）后 A（虚拟子仓）、资金分档额度规则、归因四条口径、QMT 桥对接、施工路径两步、三决策点；附录=模拟盘→实盘晋升规则  |
| `2026-09-14-supply483-verification-report.md` | file | 1 | 2026-09-15 | 1 | 分片 | 等值 1/1 | 4/3 | mid | 前五大供应商/客户（483 层）全量重验报告：A 组 7,337 行五重机检、17 对方向矛盾按申万行业+产业常识仲裁（3 条错向 edge_close）、§3 B 组 44,008 行二次代码化立项建议、§4 详情页上 |
| `2026-09-14-tdm-consumption-sop-draft.md` | file | 1 | 2026-09-15 | 1 | 分片 | 等值 1/1 | 2/3 | high | TDM 消费场景规程草案 v0.1：地图五大功能、S1-S6 消费场景表、落地方式（升 permanent+门禁化建议）；附寻路批次1（S3 知识漂移 arXiv Look-Ahead-Bench 支撑）、批次2（SR  |
| `2026-09-14-tilib-batch6-plan.md` | file | 1 | 2026-09-15 | 1 | 分片 | 等值 1/1 | 1/3 | high | 技术指标库批6 施工方案：RV 波动率族 4+BBI+动量族 7+BRAR/CR 共 14 指标/19 列（REG-IND-001 78→92、DDL 116→135），含五轮方案挖矿、逐指标测试计划、已知坑清单与 15 |
| `2026-09-14-tilib-batch7-wiring-plan.md` | file | 1 | 2026-09-15 | 1 | 分片 | 等值 1/1 | 1/3 | high | 批7 消费端接线开工方案：块A 新建 indicator_reader PIT 读取 API、块B 两个真实消费样板（波动率止损/超买超卖因子输入）、块C REG-IND-001 used_by_factors 双向锚点 |
| `2026-09-14-typhoon-bdi-factor-mining-plan.md` | file | 1 | 2026-09-15 | 1 | 分片 | 等值 1/1 | 1/3 | high | 台风×BDI 事件因子挖矿总账（六向寻路 R1-R6、防噪音四闸、EVT-TYPHOON-BDI-001 立卡草案+P0/P0-002/A/B/C/F5/F6/F10/F11 逐批实弹结果与封矿判定），文末附深圳开放数据 |
| `2026-09-14-xtreme-redblue-v4-report.md` | file | 1 | 2026-09-15 | 1 | 分片 | 不等值 | 2/9 | high | 红蓝对抗 v4 修复面复测工作日志（F1-F10 十场景对账）+ 修复批附录：F1 worktree 语法门禁失效治本、F2 并发搭便车 HELD-OVERLAP 补 .ailocks 第二轨、F9 不重复施工认定、裁定 |
| `2026-09-15-c4-acceptance-interim.md` | file | 1 | 2026-09-15 | 1 | 分片 | 等值 1/1 | 2/3 | mid | C4 历史研报一致预期修复原型验收报告（阶段版）：四批实绩表（4,259 行分置信层）、15/30 份人工抽核目视台账（报告级 14/15=93.3% 达标）、三类提取缺陷治本、high-only 收紧结论与剩余协议/全 |
| `2026-09-15-c5-cluster-refresh.md` | file | 1 | 2026-09-15 | 1 | 分片 | 等值 1/1 | 0/0 | mid | C5 聚类复检刷新报告（夜班）：22 件估值/市值族按因子主导+参数形状聚成 7 簇出簇首与 redundant 建议；总结论=全族无一具备 sim 晋级资格、小市值成长门族 IS 有效性属风格β；工具化裁定=不新建常驻 |
| `2026-09-15-four-big-items-blueprint.md` | file | 1 | 2026-09-16 | 1 | 分片 | 等值 1/1 | 0/0 | high | 四大件施工图：MOD-BT-201 E7 前哨对账器 / 202 MCTS 表达式第三轨 / 203 图谱增补入图（--approve 门）/ 204 Kronos 微调数据管线，每件含核心逻辑步骤、依赖、测试、验收与执 |
| `2026-09-15-full-automation-night-plan.md` | file | 1 | 2026-09-15 | 1 | 分片 | 等值 1/1 | 0/0 | high | 全自动化夜班总方案 + §5 执行结果与裁定记录：挖矿两轮回外部实践对照表、Owner 17 项清单映射 N1-N10、自裁记录与验收线，末节逐销项（N1-N10 全出结果，含两项登记跳过） |
| `2026-09-15-governance-module-mining-sop-map.md` | file | 1 | 2026-09-16 | 1 | 分片 | 等值 1/1 | 3/2 | high | 治理守护模块挖矿 SOP 战役地图：提交内存耗尽事故复盘、75 src+25 scripts+38 文档资产八域模块死活地图、§4 体检五条结构性发现、§5 加减乘除四表逐条回填终态与 commit 凭据、§4.5 存废 |
| `2026-09-15-gutters-eoc3-verification-deadend.md` | file | 1 | 2026-09-15 | 1 | 分片 | 等值 1/1 | 0/2 | high | 双沟 Gutters 的 EOC3 核证记录：八条通路探测明细（全灭）→ 经代理取得 EOC3 三版 PDF 1315 页、76 章目录核验无 Gutters 章 → P3 候选前提证伪除名，八候选终态 6 在册+2 除 |
| `2026-09-15-handoff-factory-docs-discussion.md` | file | 1 | 2026-09-15 | 1 | 分片 | 等值 1/1 | 2/3 | mid | 「全链路工厂+组合层穷尽」两稿的交接指令（可复制 prompt）：列六条已查实硬事实（4 个业务工厂未接产线、Lane C 未编排、DSR num_trials 口径偏乐观等）与六个待答问题、讨论纪律与完成定义 |
| `2026-09-15-neff-estimator-preregistration.md` | file | 1 | 2026-09-15 | 1 | 分片 | 等值 1/1 | 0/0 | high | 4.1 N_eff 估计器预注册锁定记录：锁定 effective_rank（熵加权特征值广度）为主、marchenko_pastur 为受限备选、排除 clustering；定双口径披露（n_trials_raw+n_ |
| `2026-09-15-szopen-pipeline-handoff.md` | file | 1 | 2026-09-15 | 1 | 分片 | 等值 1/1 | 4/3 | high | 深圳开放数据 47 接口接入管线交接单：背景（19/47 已接、28 卡服务地址）、必读三件与工作路径、任务 0-4 清单（复测订阅/向 Owner 收地址/已生效建管线/批量接入/回补纪律）、14 条坑位清单、五·五进 |
| `2026-09-15-tilib-handoff.md` | file | 1 | 2026-09-15 | 1 | 分片 | 等值 1/1 | 0/0 | high | 技术指标库线交接包：§0 P0 运维事故（technical_indicator 1304 parts/125GB 致 Code 241）与恢复三选一、九批总账表、批9 数据批+批10 筹码族施工清单、必读文件七件、配方 |
| `2026-09-18-gate-identity-root-fix-plan.md` | file | 1 | 2026-09-19 | 1 | 分片 | - | 0/5 | mid | 门禁身份与触发台账治本施工方案（B′ 方案）：五身份面+第六面普查实测、触发记录载体致命限制、已定位坏写入端与破坏性地雷、WP1-WP7 七工作包定义与依赖序、禁止事项六条与误差分级声明 |
| `2026-09-18-landing-anchor-algo-flow-closeout` | dir | 7 | 2026-09-18 | 1 | 分片 | 等值 7/7 | 3/1 | high | 落地面锚定态战役：W1 worktree→主仓判定收敛单源治本（2ac7d910ed）+ B6 反向孤件 reconciler 检测面与 Owner 授权退役面落地（562320d091），镜像退役经裁定#336 执行（ |
| `2026-09-18-rule-audit-master-construction-plan.md` | file | 1 | 2026-09-19 | 1 | 分片 | - | 0/3 | mid | 规则与审计一条龙施工总方案：全局纪律十条、裁定 D-1~D-18（B′ 方案、放行入账、死数据顺序、第四册生成器、对价退役、判据收窄、两轴风险档、A/B 双盲法、D-14 rules/ 冻结、D-15 队列正门、D-17 |
| `2026-09-18_vocab_consolidation_campaign` | dir | 26 | 2026-09-22 | 1 | 分片 | 不等值 | 3/1 | high | target_layer 词表收编战役 W1-W8：五真源挖矿（消费者/生成器/门禁/分层）+裁定#335 三段式自裁+词表 v1.1.0→v1.2.0 收编 17+8+10 值/校验器正则归位+[DOMAIN] 头字段 |
| `2026-09-19-overnight-handover-max-shift.md` | file | 1 | 2026-09-20 | 1 | 分片 | - | 1/5 | high | 通宵 Flash 班→Max 日班交接令：真源分工指针、面 A/面 B 二分、前夜不得重开的裁定表（D-1~D-18）、夜班八笔落地 commit 表、七项主动否决清单、夜裁-01..24 四梯队待裁册、W1-W6 后续 |
| `2026-09-19-overnight-scope-lock-report.md` | file | 1 | 2026-09-20 | 1 | 分片 | - | 0/1 | high | 通宵 Flash 班范围锁定回执：19 张 T0 卡可用性实测表、三笔治本落地、七项 P0 结构性发现（55 台 pre-commit 零执行权、装载器 fail-open、三台缺 --ci、扫描口径白名单病、9 台存量 |
| `altdata_night` | dir | 2 | 2026-09-18 | 1 | 分片 | 等值 2/2 | 1/1 | mid | 通宵双分包战役总统筹（E0-E17）：产业链 T1-T6/T10、数据线 D1-D8 三波、图谱 Alpha T7-T9 并入、D9 存量迁移 90,243 件、红蓝三轮验收与六要素晨报落盘 |
| `auction_bridge_switch_mining_2026_09_17.md` | file | 1 | 2026-09-17 | 1 | 分片 | 等值 1/1 | 1/0 | mid | 竞价族桥接切换的挖矿盘点与施工终态：9/18 miniQMT 关停前两表 source 切 qmt_bridge 的方案 A′（ch_auction_derive 对 tick_depth_5 派生）、三项实证、六个裁决 |
| `audit_integrity` | dir | 2 | 2026-09-16 | 1 | 分片 | 等值 2/2 | 1/0 | high | 审计链三维损伤取证（prev 断链 5,595/内容失配 5,343/HMAC 不可验 26,909）+ 多写方互踩治本（跨进程 append 锁+锁内实时尾读，裁定#266）+ HMAC 密钥分期验证基建与 256-b |
| `code_doc_gov_campaign` | dir | 13 | 2026-09-22 | 1 | 分片 | - | 22/3 | high | 丙线代码文档治理五分包端到端交付：WO-12 疑似 bug 九条全终态（6 修+3 证伪留痕）／WO-13 测试真账六族闭环+A14 资产册 32 表登记（264→296）／WO-14 企架文档归置（裁定#384，66  |
| `data_fix_campaign` | dir | 11 | 2026-09-23 | 1 | 分片 | - | 21/4 | high | 甲线数据正确性战役：分包0-6（09-17 tick+五档找回 28,327,322 行、估值双修、断供止血六链、哨兵 55→58 腿、批10 筹码族代码层、SCD2 定性=测试病、1970 A 族 398,740 格  |
| `dsr-recalc` | dir | 2 | 2026-09-15 | 1 | 分片 | 等值 2/2 | 0/0 | high | DSR 口径 A2+A3 交付：23 个 run 的 num_trials 可考证回填、存量 261 行按累计 N=4481 重算（refold/normal_approx 两路径）、锚点行翻案 0.9809→0.051 |
| `flash_speedup` | dir | 22 | 2026-09-24 | 1 | 分片 | - | 36/8 | mid | Flash 提交链提速战役（24/h→100+ 目标）：F1 衍生提交折叠、F4 生成器并发（57.4s→~28s）、F9 队列 untracked 新件死信治本、F5 DC 预检快败、F2 前置四件+H harness |
| `forensics` | dir | 1 | 2026-09-17 | 1 | 分片 | 等值 1/1 | 2/4 | high | llama-server 崩溃族溯源（8 例/3 签名族/AV@libllama.dll+0x2a230 确定性缺陷+VRAM 超订归因）→ VRAM 预算门+M1 登记/M2 水位/M3 超寿收割落地 → §7 Oll |
| `guides` | dir | 2 | 2026-09-21 | 1 | 分片 | - | 1/0 | high | 统一进程孵化入口（MOD-INF-PROC-INCUBATOR 治理战役 M1+M2+M3）迁移指南：孵化即登记/水位门禁/收割闭环三件口径+一行改法+参数口径表+首批 5 消费方迁移实录 |
| `index.md` | file | 1 | 2026-09-21 | 1 | 分片 | 不等值 | 0/0 | mid | docs/_working 顶层目录索引（generate_missing_index_md.py 机生，2026-09-21 生成），列 2 件施工卡+2 件夜班件+25 个下级目录导航 |
| `oddjobs_night` | dir | 3 | 2026-09-23 | 1 | 分片 | - | 2/0 | high | 通宵杂项班七件逐件落地并交回执：件2 .gitignore 止血+假 governance.db 三件删除（cb7786e75d）、件3 A-2 两段接线核验+红证 4 用例（f7d687ce6c，裁定#403 随批）、 |
| `p21_contract_header_slimming_proposal.md` | file | 1 | 2026-09-15 | 1 | 分片 | 等值 1/1 | 1/3 | high | P2-1 契约头减负设计稿：逐标记消费方实查（哪些必留守、哪些机器可再生可出仓）+ 方案=ALGO_FLOW 块 generate→externalize→gate 校验替代源码驻留 + 试点 event_driven_ |
| `redblue` | dir | 1 | 2026-09-15 | 1 | 分片 | 等值 1/1 | 4/5 | mid | 红蓝对抗 v5 复测（裁定#252 全链路 7/7、gate 双格式判活 6/6、搭便车重放 4/4、F1 回归 2/2=17/17 PASS）+ v6 独立复核与分域猎红清偿（9+5 处孤儿红：stub 绕过治本/ba |
| `unified_campaign` | dir | 17 | 2026-09-22 | 1 | 分片 | - | 17/10 | mid | 四包合流的全项目统一施工方案 v1.0（三总包甲/乙/丙并行+三档停机时序制）：交付派工单集 WO-1..16、四路总台账、数据库修复总方案 19 病条、Owner 签字单与停机声明板 |
| `同花顺资料` | dir | 2 | 2026-09-09 | 1 | 分片 | - | 0/0 | mid | ths_import.py 于 2026-09-08 生成的 THS 被投清单登记台账（893 行表）落盘留档，文件头自述用途=供将来股权穿透表消费、禁入 ig_company_edge；2026-09-09 卫生批按  |
| `2026-08-25-page-by-page-review.md` | file | 1 | 2026-09-15 | 2 | 分片 | 等值 1/1 | 2/17 | mid | Dashboard 逐页审查开册（28 页队列）+ §G 全局设计语言四件裁定（ticker 横条/欧易皮肤只抄皮不换红涨绿跌语义/导航移顶/个股二级页 A-B-C 三档）+ §C 币圈第 6 域架构裁定 + §F 框架 |
| `2026-09-07-tdm-backtest-protocol.md` | file | 1 | 2026-09-15 | 2 | 分片 | 等值 1/1 | 2/14 | mid | 拼装回测协议 V0（TDMAP-001）：外审 Round 1 十三 Blocker 的协议级修复承载件——§1 合成期忽略交互清单、§2 启动闸门 G1-G10、§3 fill 三档敏感性、§4 数据降级矩阵+PIT  |
| `2026-09-09-tdm-field-upgrade-discussion.md` | file | 1 | 2026-09-15 | 2 | 分片 | 等值 1/1 | 2/3 | mid | TDM 地图字段升级六路业界调研+A/B/C 档候选，Owner 2026-09-10 逐条裁定（A1 owner/A2 risk_tier/A3 review_frequency 不做，A4 tags+A5 laten |
| `2026-09-10-commit-pipeline-perf-plan.md` | file | 1 | 2026-09-15 | 2 | 分片 | 等值 1/1 | 6/8 | mid | 提交通道性能调研方案：三条根因实测（锁等待/门禁全量重扫/子进程 spawn 税）+六项调研+106 gate 计时与扫描类型分级表（§2.6）+功能等价性审计（§2.7）+P0/P1/P2 九项施工清单与两夜施工状态总 |
| `2026-09-11-g07-sentiment-validation.md` | file | 1 | 2026-09-15 | 2 | 分片 | 不等值 | 1/3 | high | G07 情绪分层相关性验证（一次性验证批，代理收益口径，5713 只/954 交易日）：分层两两相关矩阵主判据+block-bootstrap/Hawkes 增补项，产出三态裁定与三条处置建议 |
| `2026-09-12-data-layer-gap-analysis.md` | file | 1 | 2026-09-15 | 2 | 分片 | 等值 1/1 | 6/3 | mid | 数据分层体检：以机构三轴（内容轴/加工轴/延迟轴）对照 Owner 的 L1/L2/L3 分法，逐层给分（L1≈95%、L2 数据≈70%/消费≈30%、L3 另类≈15%、治理轴≈90%）并产出 P1-A/P1-B/P |
| `2026-09-13-knowledge-reserve-nonpipeline.md` | file | 1 | 2026-09-15 | 2 | 分片 | 等值 1/1 | 4/3 | mid | 量化知识储备库（流水线外有价值内容六板块归档）：板块一 风险与仓位五件（前瞻 VaR/CVaR、凯利动态仓位、尾部对冲、风险预算）、板块二 执行算法与冲击成本、板块三 微观结构因子、板块四 Owner 人机协作五原则、板 |
| `2026-09-14-full-chain-factory-blueprint.md` | file | 1 | 2026-09-15 | 2 | 分片 | 等值 1/1 | 2/5 | mid | 全链路工厂终局方案：九环节家底实读盘点（四个工厂全「有厂房没接产线」）、工厂裁决三问判据、F-01~F-09 工厂矩阵、五部件+一回路终局形态（D/C/E/M/G）、三条设计铁律、L1-L3 路线图、附录 A 两轮挖矿与 |
| `board_synthesis` | dir | 3 | 2026-09-15 | 2 | 分片 | 等值 3/3 | 0/0 | mid | 板块指数自建合成方案 J 立项并推进 Phase 2/3：sector_constituent_snapshot 建表首灌、circ_mv 断供回填 297,003 行、三口径双真值日对拍定案、逆势榜板块腿恢复出榜 |
| `full-auto-chain` | dir | 63 | 2026-09-22 | 2 | 分片 | - | 30/19 | mid | 全自动链路挖矿总纲 S01-S15 环节清单+每环节封矿文档+施工班状态回填：C0 OOS 复测自动化／C1 模拟盘自动开户／C2 四件套排班／C3 整装回测接线（实弹 ok）／C4 转正建议包+OwnerTokenGu |
| `live_readiness` | dir | 5 | 2026-09-22 | 2 | 分片 | - | 1/1 | mid | 小资金实盘准入四件套成稿（六面检查表 25 项判据+现状实测 绿17/黄8/红7/白1／pilot 档 SOP 草案／异常处置手册 E1-E8／准入门禁 G1-G12+只读检查器设计），全程零实盘触碰 |
| `resource_schedule` | dir | 14 | 2026-09-22 | 2 | 分片 | - | 3/1 | mid | v1 资源排班全景四件套（库=config/resource_profile_registry.yaml、器=零侵入采样器、闸=排班冲突 gate、图=周历视图）B1-B4+E2E 六环节全 PASS；v2 战役（挖净联 |
| `tdm20_campaign` | dir | 8 | 2026-09-23 | 2 | 分片 | - | 2/0 | mid | TDM 2.0 扩容+排班表对齐班：图 138→182 节点、194→254 边（60 真 PIT 陈述+194 legacy-unaudited 机械回填）、新增 L9 知识供给层吸收 chainpile 283 问、 |
| `trading_vision` | dir | 9 | 2026-09-21 | 2 | 分片 | - | 4/9 | mid | Owner 交易愿景→系统五层级联映射＋日度编排器蓝图 v1＋判定台账标准 v0.1＋数据够用性矩阵＋骨架覆盖审计，W8 第二圈结案报告自述『四件蓝图定稿在册、本目录整目录=活蓝图，禁止归档』 |
| `2026-08-28-d-disk-cleanup-plan.md` | file | 1 | 2026-09-15 | 3 | 分片 | 等值 1/1 | 6/3 | high | D 盘空间清理方案（预期释放 ~22GB）：models 迁 E 盘 / 删或迁 .git.backup.20260803 / 选择性清 tmp+echo-guard，附前置检查与执行后验证口径，并否决「语料迁 PG 压 |
| `2026-08-30-b4-six-factor-construction-breakdown.md` | file | 1 | 2026-09-15 | 3 | 分片 | 等值 1/1 | 9/3 | high | B4 六因子矩阵施工条件评估 + 分解框架：实证「具备施工条件、不登记 ARCH-299」，把剩余工作切成 S1 因子值产出接线 / S2 z-score+event_impact_score 融合 / S3 漏斗与 s |
| `2026-08-30-b7-batch-bc-doc-supplement-checklist.md` | file | 1 | 2026-09-15 | 3 | 分片 | 等值 1/1 | 4/3 | high | B7（63 号文批次 B/C）评估结论 + 补文档清单：25 张表逐表 ClickHouse 行数实证（14 有数据 / 3 配置在位但 0 行→登记 ARCH-300 / 5 dormant 待 Q8），并按目标文档给 |
| `2026-09-01-stockq-component-split-inventory-v2.md` | file | 1 | 2026-09-15 | 3 | 分片 | 等值 1/1 | 2/3 | mid | 个股行情页（stockq）积木级拆分清单 v2：26 features + 6 widgets + 8 services 逐件给文件名/功能语义/数据源/交互/验收单号，附拆分哲学五判据、manifest 14 字段与数 |
| `2026-09-08-qmt-bridge-migration-ledger.md` | file | 1 | 2026-09-15 | 3 | 分片 | 等值 1/1 | 2/6 | high | miniQMT→QMT 文件桥替换施工台账：摸排 59 个主源 miniqmt 任务（26 有 fallback/17 无 fallback 在产/6 周边/4 占位/6 仅作 fallback）+ 后端 12 处代码改 |
| `2026-09-12-alt-data-construction-plan.md` | file | 1 | 2026-09-15 | 3 | 分片 | 等值 1/1 | 2/3 | mid | 另类数据施工图 v2：五条既有管线可持续性审计（代码实证）+ 电商爬虫不碰裁定复核 + web注意度/社媒情绪/监管文件三块施工图 + 政府/国际宏观免费路径清单 + 四批施工规划与 15 条需注册源 URL |
| `2026-09-12-alt-data-handoff.md` | file | 1 | 2026-09-15 | 3 | 分片 | 等值 1/1 | 2/7 | high | 另类数据线交接工单：任务背景/Owner 已申请密钥入库状态/各平台 API 入口核实/SH-SZ 申请话术/已建自动化（北京平台 token 续期提醒）/接手会话按序待办五步/关键路径总表 |
| `2026-09-12-work-roadmap.md` | file | 1 | 2026-09-15 | 3 | 分片 | 等值 1/1 | 3/3 | mid | 2026-09-12 深夜全景工作地图：回答「数据源搞定了吗」+ 六泳道排期（泳道0 P0 生死线 / 泳道1 9-18 miniQMT 退役前数据冲刺六件 / 泳道2 财报事实侧 F1-F5 / 泳道3 研报预期侧 C |
| `2026-09-13-dedup-analysis.md` | file | 1 | 2026-09-15 | 3 | 分片 | 等值 1/1 | 1/3 | mid | DEDUP 专项批分析：对 CloneGuard 18 对豁免克隆做 AST 级实证分级（A 组 AST 全同 6 组 15 副本/B 组语义等价 4 组/C 组真语义差异 2 组），产出落点+方法绑定+穿行成本预算的合 |
| `alt_data_consumption_plan.md` | file | 1 | 2026-09-15 | 3 | 分片 | 等值 1/1 | 4/3 | mid | 另类数据消费端施工方案 v1（F1-F27 逐源消费设计卡+三层消费架构+按历史深度排序铁律）与 Batch1-3 挖矿增补；§7.2 三批 20 轮双噪音触发封矿、§7.3 定稿 C-1..C-5 施工排序 |
| `altdata_line` | dir | 15 | 2026-09-21 | 3 | 分片 | - | 1/8 | mid | 另类数据线总索引+骨架/路线图/工单作业区：07 修复工单与 09 数据子分包清单已由 2026-09-18 通宵双分包战役执行（01 骨架多处叶位标注夜班落地面+commit 锚），08 全链路路线图 P0-P8 为总 |
| `bizmine_chain_mining` | dir | 6 | 2026-09-21 | 3 | 分片 | - | 2/1 | mid | 业务层 Alpha 挖掘全链路战役的方案件+台账+环节骨架（16 环节路由表）+五真源差集矩阵：B0 冷启动与 B1 四源差集已出，战役定位=先挖环节骨架后施工 |
| `cold_backup_automation` | dir | 4 | 2026-09-21 | 3 | 分片 | - | 10/8 | mid | 冷储+备份自动化 13 章方案册（六项需求+三条追加裁定，§10 执行批次 0-8 带验收标准）+ 挖矿发现册（九域缺口/566.5G 家底/八项意外/十九项可复现读取清单）+ 只读结案报告一份 |
| `construction_backlog.md` | file | 1 | 2026-09-15 | 3 | 分片 | 等值 1/1 | 4/5 | mid | 回测启动施工待办总账（2026-08-21 生成，2026-08-30 长城批复核）：阶段 A 五项纯历史回测前置逐条实证勾销、阶段 B 六项对账闭环（B1/B2/B5 已核销）、阶段 C 测试债与 P0-2 残余两条并 |
| `daily_loop_campaign` | dir | 15 | 2026-09-22 | 3 | 分片 | - | 0/4 | mid | 丁线日循环通电：9 棒事件链对账改判（3 件 REUSE 免接线）+手动总扳手 MOD-PLAN-033 落地（11 段薄委托）+验证环历史首行（judgment_plan_verification 0→1）+两圈 E2 |
| `datavein` | dir | 1 | 2026-09-17 | 3 | 分片 | 等值 1/1 | 0/0 | high | kline_etf_60min 深史覆盖矩阵盘点+定损（四段结构缺口约 9.0 万 bar、~95% 可由 CH 内 etf_1min 合成救回）+通道 A-D 实证评估+补深工单移交数据线，同批登记 known_dat |
| `fullflow_campaign` | dir | 113 | 2026-09-21 | 3 | 分片 | - | 82/891 | high | 全流通战役总包交付：16 环节骨架+85 条断点全部独立复跑（57 仍成立/14 闭合/13 口径错/1 不可判）+六向验收尺子+四条最要命缺陷治本（regime 断供 fail-open、告警外发出口、判定四表停更哨兵 |
| `industry_chain_alpha` | dir | 10 | 2026-09-18 | 3 | 分片 | 等值 10/10 | 2/14 | mid | 产业链图谱×交易体系纳入方案+四线挖矿作业区建账（34 场景总账+五裁一判裁决书+施工四批次建议），并完成批1 部分施工（D6 链暴露矩阵构造器、A3 生猪链快检出证、B 线期货/现货两表通电、C 线研报 50 篇暂存台 |
| `2026-08-31-frontend-gap-views-derived.md` | file | 1 | 2026-09-17 | 4 | 分片 | 不等值 | 0/0 | high | 无施工行为：本件由 scripts/governance/d5_architecture/generators/generate_frontend_gap_views.py 自动生成的前端缺口派生视图（真源=fronte |
| `ai_layer_vision` | dir | 57 | 2026-09-23 | 4 | 机械围栏 | - | 50/49 |  | worktree/staged 脏 14 件; 磁盘 mtime 21.9min 前 |
| `align_dirty` | dir | 2 | 未提交 | 4 | 机械围栏 | - | 230/174 |  | worktree/staged 脏 2 件; 磁盘 mtime 1.9min 前 |
| `audit_all` | dir | 2 | 2026-09-24 | 4 | 机械围栏 | - | 88/21 |  | worktree/staged 脏 2 件; 磁盘 mtime -0.6min 前 |
| `automation` | dir | 51 | 2026-09-21 | 4 | 机械围栏 | - | 12/23 |  | worktree/staged 脏 2 件 |
| `chain_piling_campaign` | dir | 22 | 2026-09-24 | 4 | 机械围栏 | - | 3/74 |  | worktree/staged 脏 8 件; 磁盘 mtime 204.4min 前 |
| `commit_chain_mining` | dir | 14 | 2026-09-22 | 4 | 机械围栏 | - | 2/2 |  | worktree/staged 脏 1 件 |
| `commit_system_opt` | dir | 5 | 2026-09-24 | 4 | 机械围栏 | - | 6/11 |  | worktree/staged 脏 2 件; 磁盘 mtime 2.4min 前 |
| `datatail` | dir | 2 | 未提交 | 4 | 机械围栏 | - | 1/4 |  | worktree/staged 脏 2 件 |
| `disk_reorg_campaign` | dir | 19 | 2026-09-24 | 4 | 机械围栏 | - | 19/17 |  | 磁盘 mtime 81.9min 前 |
| `e2e_integration` | dir | 5 | 2026-09-23 | 4 | 机械围栏 | - | 1/0 |  | worktree/staged 脏 2 件; 磁盘 mtime 161.0min 前 |
| `emotion_line` | dir | 8 | 2026-09-23 | 4 | 机械围栏 | - | 0/2 |  | worktree/staged 脏 1 件 |
| `gov_closeout` | dir | 3 | 2026-09-22 | 4 | 机械围栏 | - | 6/0 |  | worktree/staged 脏 1 件 |
| `integrated_backtest` | dir | 52 | 2026-09-23 | 4 | 机械围栏 | - | 22/3 |  | worktree/staged 脏 30 件 |
| `kimi_audit` | dir | 1 | 2026-09-21 | 4 | 机械围栏 | 不等值 | 0/0 |  | worktree/staged 脏 1 件 |
| `map_census` | dir | 1 | 未提交 | 4 | 机械围栏 | - | 0/0 |  | worktree/staged 脏 1 件; 磁盘 mtime 28.2min 前 |
| `meta_question_answers` | dir | 311 | 未提交 | 4 | 机械围栏 | - | 17/2 |  | worktree/staged 脏 311 件; 磁盘 mtime 10.9min 前 |
| `oddjobs_final` | dir | 1 | 未提交 | 4 | 机械围栏 | - | 4/2 |  | worktree/staged 脏 1 件; 磁盘 mtime -0.5min 前 |
| `pipeline-research` | dir | 11 | 2026-09-22 | 4 | 机械围栏 | - | 0/0 |  | worktree/staged 脏 3 件 |
| `pipeline_final` | dir | 1 | 未提交 | 4 | 机械围栏 | - | 4/1 |  | worktree/staged 脏 1 件; 磁盘 mtime 9.5min 前 |
| `recovered_task_cards` | dir | 26 | 2026-09-22 | 4 | 机械围栏 | - | 52/42 |  | worktree/staged 脏 1 件 |
| `registry_incident_20260922` | dir | 35 | 未提交 | 4 | 机械围栏 | - | 44/14 |  | worktree/staged 脏 35 件; 磁盘 mtime 7.0min 前 |
| `registry_migration` | dir | 42 | 2026-09-23 | 4 | 机械围栏 | - | 1/9 |  | worktree/staged 脏 5 件 |
| `residual_resume` | dir | 3 | 2026-09-22 | 4 | 机械围栏 | - | 2/1 |  | worktree/staged 脏 1 件 |
| `rule_audit_campaign` | dir | 17 | 2026-09-22 | 4 | 机械围栏 | - | 22/71 |  | worktree/staged 脏 1 件 |
| `sector_line` | dir | 12 | 2026-09-22 | 4 | 机械围栏 | - | 0/6 |  | worktree/staged 脏 6 件 |
| `sim_launch` | dir | 9 | 2026-09-22 | 4 | 机械围栏 | - | 1/4 |  | worktree/staged 脏 4 件 |
| `sweep_tail` | dir | 2 | 2026-09-23 | 4 | 机械围栏 | - | 3/1 |  | worktree/staged 脏 1 件 |
| `t0_matrix` | dir | 1 | 未提交 | 4 | 机械围栏 | - | 10/8 |  | worktree/staged 脏 1 件; 磁盘 mtime 17.5min 前 |
| `t0_merge_status.md` | file | 1 | 未提交 | 4 | 机械围栏 | - | 1/0 |  | worktree/staged 脏 1 件 |
| `ultimate_library` | dir | 25 | 2026-09-23 | 4 | 机械围栏 | - | 8/14 |  | worktree/staged 脏 10 件; 磁盘 mtime 103.9min 前 |
| `xhs_full_construction` | dir | 13 | 2026-09-23 | 4 | 机械围栏 | - | 14/2 |  | worktree/staged 脏 3 件 |

### 1.2 机械标记 ↔ 分片终判 失证登记（自动算）

| unit | 分片态 | 机械侧疑点 | 分片所记剩余欠账 |
|---|---|---|---|
| `2026-08-22-frontend-backend-gap-ledger.md` | 1 | 含待裁词 17 次却判 1 | twin 判据：与 archive/2026-09/c_class_scattered/ 同名件 **字节等值**（cmp 无差、sha256 同 7e4d6b38cb83b13c…、size 均 4 |
| `2026-08-22-frontend-backend-gap-ledger.md` | 1 | 末笔 6aae9a7439 只动 _working，①依据只剩台账自述 | twin 判据：与 archive/2026-09/c_class_scattered/ 同名件 **字节等值**（cmp 无差、sha256 同 7e4d6b38cb83b13c…、size 均 4 |
| `2026-08-22-frontend-backend-gap-ledger.md` | 1 | 已与 `docs/_working/archive/2026-09/c_class_scattered/2026-08-22-frontend-backend-gap-ledger.md` 字节等值 → 处置=删 live 重复份，非二次归档 | twin 判据：与 archive/2026-09/c_class_scattered/ 同名件 **字节等值**（cmp 无差、sha256 同 7e4d6b38cb83b13c…、size 均 4 |
| `2026-08-24-aiarch-construction-list.md` | 1 | 含待裁词 8 次却判 1 | twin 判据：与 c_class_scattered/ 同名件 **字节等值**（sha256 同 4425ba1f9fe3d4d5…/31883B，cmp 无差，git blob 同一 713bb |
| `2026-08-24-aiarch-construction-list.md` | 1 | 末笔 6aae9a7439 只动 _working，①依据只剩台账自述 | twin 判据：与 c_class_scattered/ 同名件 **字节等值**（sha256 同 4425ba1f9fe3d4d5…/31883B，cmp 无差，git blob 同一 713bb |
| `2026-08-24-aiarch-construction-list.md` | 1 | 已与 `docs/_working/archive/2026-09/c_class_scattered/2026-08-24-aiarch-construction-list.md` 字节等值 → 处置=删 live 重复份，非二次归档 | twin 判据：与 c_class_scattered/ 同名件 **字节等值**（sha256 同 4425ba1f9fe3d4d5…/31883B，cmp 无差，git blob 同一 713bb |
| `2026-08-24-designmemos-construction-list.md` | 1 | 含待裁词 5 次却判 1 | twin 判据：与 c_class_scattered/ 同名件 **字节等值**（sha256 同 79d3db560047c1ff…/29776B，cmp 无差，git blob 同一 29fe4 |
| `2026-08-24-designmemos-construction-list.md` | 1 | 末笔 6aae9a7439 只动 _working，①依据只剩台账自述 | twin 判据：与 c_class_scattered/ 同名件 **字节等值**（sha256 同 79d3db560047c1ff…/29776B，cmp 无差，git blob 同一 29fe4 |
| `2026-08-24-designmemos-construction-list.md` | 1 | 已与 `docs/_working/archive/2026-09/c_class_scattered/2026-08-24-designmemos-construction-list.md` 字节等值 → 处置=删 live 重复份，非二次归档 | twin 判据：与 c_class_scattered/ 同名件 **字节等值**（sha256 同 79d3db560047c1ff…/29776B，cmp 无差，git blob 同一 29fe4 |
| `2026-08-25-page-by-page-review.md` | 2 | 含待裁词 17 次却判 2 | twin 判据：与 c_class_scattered/ 同名件 **字节等值**（sha256 同 8df58ef58b758e04…/64427B，cmp 无差，git blob 同一 39793 |
| `2026-08-28-d-disk-cleanup-plan.md` | 3 | 含结案词 6 次却判 3 | twin 判据：与 c_class_scattered/ 同名件 **字节等值**（sha256 同 164ee61830295402…/4568B，cmp 无差，git blob 同一 b6037f |
| `2026-08-28-remaining-construction-roadmap.md` | 1 | 含待裁词 6 次却判 1 | twin 判据：与 c_class_scattered/ 同名件 **字节等值**（sha256 同 80b38756ad819377…/38017B，cmp 无差，git blob 同一 9429d |
| `2026-08-28-remaining-construction-roadmap.md` | 1 | 末笔 6aae9a7439 只动 _working，①依据只剩台账自述 | twin 判据：与 c_class_scattered/ 同名件 **字节等值**（sha256 同 80b38756ad819377…/38017B，cmp 无差，git blob 同一 9429d |
| `2026-08-28-remaining-construction-roadmap.md` | 1 | 已与 `docs/_working/archive/2026-09/c_class_scattered/2026-08-28-remaining-construction-roadmap.md` 字节等值 → 处置=删 live 重复份，非二次归档 | twin 判据：与 c_class_scattered/ 同名件 **字节等值**（sha256 同 80b38756ad819377…/38017B，cmp 无差，git blob 同一 9429d |
| `2026-08-30-b16-feed-exploration.md` | 1 | 含待裁词 6 次却判 1 | twin 判据：与 c_class_scattered/ 同名件 **字节等值**（sha256 同 2ff2fada2c6aa17c…/7082B，cmp 无差，git blob 同一 686449 |
| `2026-08-30-b16-feed-exploration.md` | 1 | 末笔 6aae9a7439 只动 _working，①依据只剩台账自述 | twin 判据：与 c_class_scattered/ 同名件 **字节等值**（sha256 同 2ff2fada2c6aa17c…/7082B，cmp 无差，git blob 同一 686449 |
| `2026-08-30-b16-feed-exploration.md` | 1 | 已与 `docs/_working/archive/2026-09/c_class_scattered/2026-08-30-b16-feed-exploration.md` 字节等值 → 处置=删 live 重复份，非二次归档 | twin 判据：与 c_class_scattered/ 同名件 **字节等值**（sha256 同 2ff2fada2c6aa17c…/7082B，cmp 无差，git blob 同一 686449 |
| `2026-08-30-b4-six-factor-construction-breakdown.md` | 3 | 含结案词 9 次却判 3 | twin 判据：与 c_class_scattered/ 同名件 **字节等值**（sha256 同 ef99801f2d2bffda…/6561B，cmp 无差，git blob 同一 41bdd0 |
| `2026-08-30-b7-batch-bc-doc-supplement-checklist.md` | 3 | 含结案词 4 次却判 3 | twin 判据：与 c_class_scattered/ 同名件 **字节等值**（sha256 同 098bf4aa539d738a…/9992B，cmp 无差，git blob 同一 76de3b |
| `2026-08-31-frontend-governance-four-piece-drafts.md` | 1 | 含待裁词 3 次却判 1 | twin 判据：与 c_class_scattered/ 同名件 **字节等值**（sha256 同 b77252accb82c4f8…/29233B，cmp 无差，git blob 同一 e6f57 |
| `2026-08-31-frontend-governance-four-piece-drafts.md` | 1 | 末笔 6aae9a7439 只动 _working，①依据只剩台账自述 | twin 判据：与 c_class_scattered/ 同名件 **字节等值**（sha256 同 b77252accb82c4f8…/29233B，cmp 无差，git blob 同一 e6f57 |
| `2026-08-31-frontend-governance-four-piece-drafts.md` | 1 | 已与 `docs/_working/archive/2026-09/c_class_scattered/2026-08-31-frontend-governance-four-piece-drafts.md` 字节等值 → 处置=删 live 重复份，非二次归档 | twin 判据：与 c_class_scattered/ 同名件 **字节等值**（sha256 同 b77252accb82c4f8…/29233B，cmp 无差，git blob 同一 e6f57 |
| `2026-09-04-trading-decision-map-discussion.md` | 1 | 含待裁词 9 次却判 1 | 底座 twin=- 有误：c_class_scattered/ 有同名件且 **字节等值**（cmp 无差，两侧 sha256 一致）。文尾自述「讨论收敛并裁定后，正式设计应迁入 architectu |
| `2026-09-04-trading-decision-map-discussion.md` | 1 | 末笔 6aae9a7439 只动 _working，①依据只剩台账自述 | 底座 twin=- 有误：c_class_scattered/ 有同名件且 **字节等值**（cmp 无差，两侧 sha256 一致）。文尾自述「讨论收敛并裁定后，正式设计应迁入 architectu |
| `2026-09-04-trading-decision-map-discussion.md` | 1 | 已与 `docs/_working/archive/2026-09/c_class_scattered/2026-09-04-trading-decision-map-discussion.md` 字节等值 → 处置=删 live 重复份，非二次归档 | 底座 twin=- 有误：c_class_scattered/ 有同名件且 **字节等值**（cmp 无差，两侧 sha256 一致）。文尾自述「讨论收敛并裁定后，正式设计应迁入 architectu |
| `2026-09-05-audit-greatwall-report.md` | 1 | 含待裁词 5 次却判 1 | 底座 twin=- 有误：c_class_scattered/ 有同名件且 **字节等值**（cmp 无差，sha256 两侧一致）。文内 §六 待 Owner 裁定 18 项 + §九 B 类 24 |
| `2026-09-05-audit-greatwall-report.md` | 1 | 末笔 6aae9a7439 只动 _working，①依据只剩台账自述 | 底座 twin=- 有误：c_class_scattered/ 有同名件且 **字节等值**（cmp 无差，sha256 两侧一致）。文内 §六 待 Owner 裁定 18 项 + §九 B 类 24 |
| `2026-09-05-audit-greatwall-report.md` | 1 | 已与 `docs/_working/archive/2026-09/c_class_scattered/2026-09-05-audit-greatwall-report.md` 字节等值 → 处置=删 live 重复份，非二次归档 | 底座 twin=- 有误：c_class_scattered/ 有同名件且 **字节等值**（cmp 无差，sha256 两侧一致）。文内 §六 待 Owner 裁定 18 项 + §九 B 类 24 |
| `2026-09-05-steward-b-class-owner-book.md` | 1 | 含待裁词 5 次却判 1 | 底座 twin=- 有误：c_class_scattered/ 有同名件且 **字节等值**（cmp 无差，sha256 两侧一致）。§十四 自述总账 8 commit 落地；其 11 项「待裁」由  |
| `2026-09-05-steward-b-class-owner-book.md` | 1 | 末笔 6aae9a7439 只动 _working，①依据只剩台账自述 | 底座 twin=- 有误：c_class_scattered/ 有同名件且 **字节等值**（cmp 无差，sha256 两侧一致）。§十四 自述总账 8 commit 落地；其 11 项「待裁」由  |
| `2026-09-05-steward-b-class-owner-book.md` | 1 | 已与 `docs/_working/archive/2026-09/c_class_scattered/2026-09-05-steward-b-class-owner-book.md` 字节等值 → 处置=删 live 重复份，非二次归档 | 底座 twin=- 有误：c_class_scattered/ 有同名件且 **字节等值**（cmp 无差，sha256 两侧一致）。§十四 自述总账 8 commit 落地；其 11 项「待裁」由  |
| `2026-09-06-flash-execution-report.md` | 1 | 含待裁词 9 次却判 1 | 底座 twin=- 有误：c_class_scattered/ 有同名件且 **字节等值**（cmp 无差，sha256 两侧一致）。文首自述性质=「无人值守施工报告，施工完成即失效」→ 天然结案。仍 |
| `2026-09-06-flash-execution-report.md` | 1 | 末笔 6aae9a7439 只动 _working，①依据只剩台账自述 | 底座 twin=- 有误：c_class_scattered/ 有同名件且 **字节等值**（cmp 无差，sha256 两侧一致）。文首自述性质=「无人值守施工报告，施工完成即失效」→ 天然结案。仍 |
| `2026-09-06-flash-execution-report.md` | 1 | 已与 `docs/_working/archive/2026-09/c_class_scattered/2026-09-06-flash-execution-report.md` 字节等值 → 处置=删 live 重复份，非二次归档 | 底座 twin=- 有误：c_class_scattered/ 有同名件且 **字节等值**（cmp 无差，sha256 两侧一致）。文首自述性质=「无人值守施工报告，施工完成即失效」→ 天然结案。仍 |
| `2026-09-07-tdm-backtest-protocol.md` | 2 | 含待裁词 14 次却判 2 | 底座 twin=- 有误：c_class_scattered/ 有同名件且 **字节等值**（cmp 无差，sha256 两侧一致）。协议仍活着且被上层引用：docs/_working/integra |
| `2026-09-07-tdm-internal-factpack.md` | 1 | 含待裁词 4 次却判 1 | 底座 twin=- 有误：c_class_scattered/ 有同名件且 **字节等值**（cmp 无差，sha256 两侧一致）。front-matter task_context 自述「审查闭环 |
| `2026-09-07-tdm-internal-factpack.md` | 1 | 末笔 6aae9a7439 只动 _working，①依据只剩台账自述 | 底座 twin=- 有误：c_class_scattered/ 有同名件且 **字节等值**（cmp 无差，sha256 两侧一致）。front-matter task_context 自述「审查闭环 |
| `2026-09-07-tdm-internal-factpack.md` | 1 | 已与 `docs/_working/archive/2026-09/c_class_scattered/2026-09-07-tdm-internal-factpack.md` 字节等值 → 处置=删 live 重复份，非二次归档 | 底座 twin=- 有误：c_class_scattered/ 有同名件且 **字节等值**（cmp 无差，sha256 两侧一致）。front-matter task_context 自述「审查闭环 |
| `2026-09-07-tdm-pre-backtest-review-checklist.md` | 1 | 含待裁词 13 次却判 1 | 底座 twin=- 有误：c_class_scattered/ 有同名件且 **字节等值**（cmp 无差，sha256 两侧一致）。task_context 自述「审查闭环后归档」；Round 1（ |
| `2026-09-07-tdm-pre-backtest-review-checklist.md` | 1 | 末笔 6aae9a7439 只动 _working，①依据只剩台账自述 | 底座 twin=- 有误：c_class_scattered/ 有同名件且 **字节等值**（cmp 无差，sha256 两侧一致）。task_context 自述「审查闭环后归档」；Round 1（ |
| `2026-09-07-tdm-pre-backtest-review-checklist.md` | 1 | 已与 `docs/_working/archive/2026-09/c_class_scattered/2026-09-07-tdm-pre-backtest-review-checklist.md` 字节等值 → 处置=删 live 重复份，非二次归档 | 底座 twin=- 有误：c_class_scattered/ 有同名件且 **字节等值**（cmp 无差，sha256 两侧一致）。task_context 自述「审查闭环后归档」；Round 1（ |
| `2026-09-07-tdm-review-round-report.md` | 1 | 含待裁词 17 次却判 1 | 底座 twin=- 有误：c_class_scattered/ 有同名件且 **字节等值**（cmp 无差，sha256 两侧一致）。§五 终态：图面缺陷硬门槛 B=0/M=0 已达，悬挂项=17 项 |
| `2026-09-07-tdm-review-round-report.md` | 1 | 末笔 6aae9a7439 只动 _working，①依据只剩台账自述 | 底座 twin=- 有误：c_class_scattered/ 有同名件且 **字节等值**（cmp 无差，sha256 两侧一致）。§五 终态：图面缺陷硬门槛 B=0/M=0 已达，悬挂项=17 项 |
| `2026-09-07-tdm-review-round-report.md` | 1 | 已与 `docs/_working/archive/2026-09/c_class_scattered/2026-09-07-tdm-review-round-report.md` 字节等值 → 处置=删 live 重复份，非二次归档 | 底座 twin=- 有误：c_class_scattered/ 有同名件且 **字节等值**（cmp 无差，sha256 两侧一致）。§五 终态：图面缺陷硬门槛 B=0/M=0 已达，悬挂项=17 项 |
| `2026-09-09-clearance-night-report.md` | 1 | 含待裁词 8 次却判 1 | 底座 twin=- 有误：c_class_scattered/ 有同名件且 **字节等值**（cmp 无差，sha256 两侧一致）。§四 自述「无其他未完成——六件全部收口」。§三 遗留 7 条待  |
| `2026-09-09-clearance-night-report.md` | 1 | 末笔 6aae9a7439 只动 _working，①依据只剩台账自述 | 底座 twin=- 有误：c_class_scattered/ 有同名件且 **字节等值**（cmp 无差，sha256 两侧一致）。§四 自述「无其他未完成——六件全部收口」。§三 遗留 7 条待  |
| `2026-09-09-clearance-night-report.md` | 1 | 已与 `docs/_working/archive/2026-09/c_class_scattered/2026-09-09-clearance-night-report.md` 字节等值 → 处置=删 live 重复份，非二次归档 | 底座 twin=- 有误：c_class_scattered/ 有同名件且 **字节等值**（cmp 无差，sha256 两侧一致）。§四 自述「无其他未完成——六件全部收口」。§三 遗留 7 条待  |
| `2026-09-09-greatwall-quality-task-brief.md` | 1 | 含待裁词 4 次却判 1 | ①清理批结案报告判「未结案」的两条欠账（S6 306 条 unspecified 甄别/超阈值清单待 Owner）已在真源销案：docs/01_policies_and_standards/polic |
| `2026-09-09-greatwall-quality-task-brief.md` | 1 | 末笔 6aae9a7439 只动 _working，①依据只剩台账自述 | ①清理批结案报告判「未结案」的两条欠账（S6 306 条 unspecified 甄别/超阈值清单待 Owner）已在真源销案：docs/01_policies_and_standards/polic |
| `2026-09-09-greatwall-quality-task-brief.md` | 1 | 已与 `docs/_working/archive/2026-09/c_class_scattered/2026-09-09-greatwall-quality-task-brief.md` 字节等值 → 处置=删 live 重复份，非二次归档 | ①清理批结案报告判「未结案」的两条欠账（S6 306 条 unspecified 甄别/超阈值清单待 Owner）已在真源销案：docs/01_policies_and_standards/polic |
| `2026-09-09-news-industry-wiring-directive.md` | 1 | 含待裁词 3 次却判 1 | 六项 W 全部有落地面（见 closure_report），本件无自身欠账；§3 入图交接协议由 2026-09-11-news-chain-wiring-spec-cards.md 交付并已由增长轨 |
| `2026-09-09-news-industry-wiring-directive.md` | 1 | 末笔 6aae9a7439 只动 _working，①依据只剩台账自述 | 六项 W 全部有落地面（见 closure_report），本件无自身欠账；§3 入图交接协议由 2026-09-11-news-chain-wiring-spec-cards.md 交付并已由增长轨 |
| `2026-09-09-news-industry-wiring-directive.md` | 1 | 已与 `docs/_working/archive/2026-09/c_class_scattered/2026-09-09-news-industry-wiring-directive.md` 字节等值 → 处置=删 live 重复份，非二次归档 | 六项 W 全部有落地面（见 closure_report），本件无自身欠账；§3 入图交接协议由 2026-09-11-news-chain-wiring-spec-cards.md 交付并已由增长轨 |
| `2026-09-09-node-backtest-governance.md` | 1 | 含待裁词 5 次却判 1 | 本件判据已整体迁入真源（见 already_in_truth_source），残留「待裁定汇总 §五/§六调研来源」为历史过程记录；正文含「Owner 原话→治理语言」样式引文=数据，未执行；twin |
| `2026-09-09-node-backtest-governance.md` | 1 | 末笔 6aae9a7439 只动 _working，①依据只剩台账自述 | 本件判据已整体迁入真源（见 already_in_truth_source），残留「待裁定汇总 §五/§六调研来源」为历史过程记录；正文含「Owner 原话→治理语言」样式引文=数据，未执行；twin |
| `2026-09-09-node-backtest-governance.md` | 1 | 已与 `docs/_working/archive/2026-09/c_class_scattered/2026-09-09-node-backtest-governance.md` 字节等值 → 处置=删 live 重复份，非二次归档 | 本件判据已整体迁入真源（见 already_in_truth_source），残留「待裁定汇总 §五/§六调研来源」为历史过程记录；正文含「Owner 原话→治理语言」样式引文=数据，未执行；twin |
| `2026-09-09-node-template-draft.md` | 1 | 含待裁词 7 次却判 1 | 本件 front-matter 自述 status=RETIRED（2026-09-10）+migrated_to=industry_graph_field_dictionary.yaml，但文件仍留 |
| `2026-09-09-node-template-draft.md` | 1 | 末笔 6aae9a7439 只动 _working，①依据只剩台账自述 | 本件 front-matter 自述 status=RETIRED（2026-09-10）+migrated_to=industry_graph_field_dictionary.yaml，但文件仍留 |
| `2026-09-09-node-template-draft.md` | 1 | 已与 `docs/_working/archive/2026-09/c_class_scattered/2026-09-09-node-template-draft.md` 字节等值 → 处置=删 live 重复份，非二次归档 | 本件 front-matter 自述 status=RETIRED（2026-09-10）+migrated_to=industry_graph_field_dictionary.yaml，但文件仍留 |
| `2026-09-09-tdm-field-upgrade-discussion.md` | 2 | 含待裁词 3 次却判 2 | 裁定落地部分已在真源（config/trading_decision_map.yaml:4299 起逐节点 latency_budget 取值，:260 综合实测口径行），但 §七「字段空间已饱和+新 |
| `2026-09-09-tdm-growth-blueprint.md` | 1 | 含待裁词 4 次却判 1 | 方法论部分已升 permanent 真源（见 already_in_truth_source，冲突时以 SOP 为准）；本件剩 §5/§7 台账类挂起项（G3 币圈待 Owner 立项 95 号 Ph |
| `2026-09-09-tdm-growth-blueprint.md` | 1 | 末笔 6aae9a7439 只动 _working，①依据只剩台账自述 | 方法论部分已升 permanent 真源（见 already_in_truth_source，冲突时以 SOP 为准）；本件剩 §5/§7 台账类挂起项（G3 币圈待 Owner 立项 95 号 Ph |
| `2026-09-09-tdm-growth-blueprint.md` | 1 | 已与 `docs/_working/archive/2026-09/c_class_scattered/2026-09-09-tdm-growth-blueprint.md` 字节等值 → 处置=删 live 重复份，非二次归档 | 方法论部分已升 permanent 真源（见 already_in_truth_source，冲突时以 SOP 为准）；本件剩 §5/§7 台账类挂起项（G3 币圈待 Owner 立项 95 号 Ph |
| `2026-09-09-tdm-missing-modules-construction.md` | 1 | 含待裁词 3 次却判 1 | §七 两项 Owner 结构项均已收口（流根四节点=文内自述他会话合并入图；改名拆细=D108 三条件随批）；§十四/§十五 记 22/22 LANDED 落库终态；清理批结案报告列的 3 条「未完成 |
| `2026-09-09-tdm-missing-modules-construction.md` | 1 | 末笔 6aae9a7439 只动 _working，①依据只剩台账自述 | §七 两项 Owner 结构项均已收口（流根四节点=文内自述他会话合并入图；改名拆细=D108 三条件随批）；§十四/§十五 记 22/22 LANDED 落库终态；清理批结案报告列的 3 条「未完成 |
| `2026-09-09-tdm-missing-modules-construction.md` | 1 | 已与 `docs/_working/archive/2026-09/c_class_scattered/2026-09-09-tdm-missing-modules-construction.md` 字节等值 → 处置=删 live 重复份，非二次归档 | §七 两项 Owner 结构项均已收口（流根四节点=文内自述他会话合并入图；改名拆细=D108 三条件随批）；§十四/§十五 记 22/22 LANDED 落库终态；清理批结案报告列的 3 条「未完成 |
| `2026-09-09-tdm-night-greatwall-directive.md` | 1 | 含待裁词 3 次却判 1 | 本件是一次性派单指令，执行结果全部记在 2026-09-09-tdm-missing-modules-construction.md §十~§十三（night-gw-2300 台账）；正文的指令样式文 |
| `2026-09-09-tdm-night-greatwall-directive.md` | 1 | 末笔 6aae9a7439 只动 _working，①依据只剩台账自述 | 本件是一次性派单指令，执行结果全部记在 2026-09-09-tdm-missing-modules-construction.md §十~§十三（night-gw-2300 台账）；正文的指令样式文 |
| `2026-09-09-tdm-night-greatwall-directive.md` | 1 | 已与 `docs/_working/archive/2026-09/c_class_scattered/2026-09-09-tdm-night-greatwall-directive.md` 字节等值 → 处置=删 live 重复份，非二次归档 | 本件是一次性派单指令，执行结果全部记在 2026-09-09-tdm-missing-modules-construction.md §十~§十三（night-gw-2300 台账）；正文的指令样式文 |
| `2026-09-10-chainmap-frontend-batch-plan.md` | 1 | 含待裁词 6 次却判 1 | 批次表 B5 行状态仍写 PENDING，与标题行「复启批 2026-09-14 全部开工：…+B5 下钻点亮（10 节点）」及收尾批复启附记矛盾——真源以 13076db39b 为准（B5 已点亮） |
| `2026-09-10-chainmap-frontend-batch-plan.md` | 1 | 末笔 6aae9a7439 只动 _working，①依据只剩台账自述 | 批次表 B5 行状态仍写 PENDING，与标题行「复启批 2026-09-14 全部开工：…+B5 下钻点亮（10 节点）」及收尾批复启附记矛盾——真源以 13076db39b 为准（B5 已点亮） |
| `2026-09-10-chainmap-frontend-batch-plan.md` | 1 | 已与 `docs/_working/archive/2026-09/c_class_scattered/2026-09-10-chainmap-frontend-batch-plan.md` 字节等值 → 处置=删 live 重复份，非二次归档 | 批次表 B5 行状态仍写 PENDING，与标题行「复启批 2026-09-14 全部开工：…+B5 下钻点亮（10 节点）」及收尾批复启附记矛盾——真源以 13076db39b 为准（B5 已点亮） |
| `2026-09-10-commit-pipeline-perf-plan.md` | 2 | 含待裁词 8 次却判 2 | 施工侧九项全部落地（见 closure_report，含 2026-09-11 第二夜 Owner「剩余活儿全部做」总账与 a95113c0ae 三 flag 实战验证），判 ② 仅因 §2.6 分级 |
| `2026-09-10-legacy-clear-night-report.md` | 1 | 含待裁词 7 次却判 1 | 文内 §四 自述「无其他未完成——T0/T2/T3/T4/T5(主体)/T6 全部收口」；§三 七条遗留全为 Owner 门位/权限项（管理员 takeown、8890 elevated 重启、R21 |
| `2026-09-10-legacy-clear-night-report.md` | 1 | 末笔 6aae9a7439 只动 _working，①依据只剩台账自述 | 文内 §四 自述「无其他未完成——T0/T2/T3/T4/T5(主体)/T6 全部收口」；§三 七条遗留全为 Owner 门位/权限项（管理员 takeown、8890 elevated 重启、R21 |
| `2026-09-10-legacy-clear-night-report.md` | 1 | 已与 `docs/_working/archive/2026-09/c_class_scattered/2026-09-10-legacy-clear-night-report.md` 字节等值 → 处置=删 live 重复份，非二次归档 | 文内 §四 自述「无其他未完成——T0/T2/T3/T4/T5(主体)/T6 全部收口」；§三 七条遗留全为 Owner 门位/权限项（管理员 takeown、8890 elevated 重启、R21 |
| `2026-09-10-nodebt-night-report.md` | 1 | 含待裁词 5 次却判 1 | §四 记「三期落盘物全部完成并通过验收」+P0/P1/P2 提交终态逐笔列明；唯一登记遗留=P2-3 反事实对照（文内标注真源 §8.3 授权「按需可延」，方法学已在 P1-1 落好），后续由 X 流 |
| `2026-09-10-nodebt-night-report.md` | 1 | 末笔 6aae9a7439 只动 _working，①依据只剩台账自述 | §四 记「三期落盘物全部完成并通过验收」+P0/P1/P2 提交终态逐笔列明；唯一登记遗留=P2-3 反事实对照（文内标注真源 §8.3 授权「按需可延」，方法学已在 P1-1 落好），后续由 X 流 |
| `2026-09-10-nodebt-night-report.md` | 1 | 已与 `docs/_working/archive/2026-09/c_class_scattered/2026-09-10-nodebt-night-report.md` 字节等值 → 处置=删 live 重复份，非二次归档 | §四 记「三期落盘物全部完成并通过验收」+P0/P1/P2 提交终态逐笔列明；唯一登记遗留=P2-3 反事实对照（文内标注真源 §8.3 授权「按需可延」，方法学已在 P1-1 落好），后续由 X 流 |
| `2026-09-10-xflow-batch-report.md` | 1 | 含待裁词 5 次却判 1 | §三 八条遗留：1/2 为「待 Owner 放行/待窗口前移」的纪律闸（协议 §12 定稿前不跑回测），3 消融标注自动化与 4 exec 真决策价口径已由跟进设计件落地，5 decay 口径「暂不阻 |
| `2026-09-10-xflow-batch-report.md` | 1 | 末笔 6aae9a7439 只动 _working，①依据只剩台账自述 | §三 八条遗留：1/2 为「待 Owner 放行/待窗口前移」的纪律闸（协议 §12 定稿前不跑回测），3 消融标注自动化与 4 exec 真决策价口径已由跟进设计件落地，5 decay 口径「暂不阻 |
| `2026-09-10-xflow-batch-report.md` | 1 | 已与 `docs/_working/archive/2026-09/c_class_scattered/2026-09-10-xflow-batch-report.md` 字节等值 → 处置=删 live 重复份，非二次归档 | §三 八条遗留：1/2 为「待 Owner 放行/待窗口前移」的纪律闸（协议 §12 定稿前不跑回测），3 消融标注自动化与 4 exec 真决策价口径已由跟进设计件落地，5 decay 口径「暂不阻 |
| `2026-09-10-xflow-followup-design.md` | 1 | 含待裁词 6 次却判 1 | §三 定稿锚点已由 Owner 裁定「同意，开工」并落地（runner.py:82 finalized_at=2026-09-09，语义另固化于 validation_method_registry. |
| `2026-09-10-xflow-followup-design.md` | 1 | 末笔 6aae9a7439 只动 _working，①依据只剩台账自述 | §三 定稿锚点已由 Owner 裁定「同意，开工」并落地（runner.py:82 finalized_at=2026-09-09，语义另固化于 validation_method_registry. |
| `2026-09-10-xflow-followup-design.md` | 1 | 已与 `docs/_working/archive/2026-09/c_class_scattered/2026-09-10-xflow-followup-design.md` 字节等值 → 处置=删 live 重复份，非二次归档 | §三 定稿锚点已由 Owner 裁定「同意，开工」并落地（runner.py:82 finalized_at=2026-09-09，语义另固化于 validation_method_registry. |
| `2026-09-11-backtest-evidence-log-discussion.md` | 1 | 含待裁词 4 次却判 1 | R1-R5 裁定已整体入库为 SOP-D（sop_d_run_archive_naming.md）；文内「关键发现：data/backtest_artifacts/ 已 .gitignore、预注册阈 |
| `2026-09-11-backtest-evidence-log-discussion.md` | 1 | 末笔 6aae9a7439 只动 _working，①依据只剩台账自述 | R1-R5 裁定已整体入库为 SOP-D（sop_d_run_archive_naming.md）；文内「关键发现：data/backtest_artifacts/ 已 .gitignore、预注册阈 |
| `2026-09-11-backtest-evidence-log-discussion.md` | 1 | 已与 `docs/_working/archive/2026-09/c_class_scattered/2026-09-11-backtest-evidence-log-discussion.md` 字节等值 → 处置=删 live 重复份，非二次归档 | R1-R5 裁定已整体入库为 SOP-D（sop_d_run_archive_naming.md）；文内「关键发现：data/backtest_artifacts/ 已 .gitignore、预注册阈 |
| `2026-09-11-backtest-system-sop-discussion.md` | 1 | 含待裁词 3 次却判 1 | §5「下一步」三条（启动 P0 批次/SOP-C Step C1 盘点 600 条/每批回写本文件进度小节）属后续批次的执行编排，未在本件续写——本件定稿内容整体已由 SOP-A/B/C 三件套承载为 |
| `2026-09-11-backtest-system-sop-discussion.md` | 1 | 末笔 6aae9a7439 只动 _working，①依据只剩台账自述 | §5「下一步」三条（启动 P0 批次/SOP-C Step C1 盘点 600 条/每批回写本文件进度小节）属后续批次的执行编排，未在本件续写——本件定稿内容整体已由 SOP-A/B/C 三件套承载为 |
| `2026-09-11-backtest-system-sop-discussion.md` | 1 | 已与 `docs/_working/archive/2026-09/c_class_scattered/2026-09-11-backtest-system-sop-discussion.md` 字节等值 → 处置=删 live 重复份，非二次归档 | §5「下一步」三条（启动 P0 批次/SOP-C Step C1 盘点 600 条/每批回写本文件进度小节）属后续批次的执行编排，未在本件续写——本件定稿内容整体已由 SOP-A/B/C 三件套承载为 |
| `2026-09-11-chainmap-final-batch-report.md` | 1 | 含待裁词 4 次却判 1 | §七 五条挂账中 1/3/5 已由复启附记（B7/B8/B5）销账，仍开放三条：aliases/facilities 域「建设中」留位、profile.country 值缺失（数据侧非前端）、浅色主题 |
| `2026-09-11-chainmap-final-batch-report.md` | 1 | 末笔 6aae9a7439 只动 _working，①依据只剩台账自述 | §七 五条挂账中 1/3/5 已由复启附记（B7/B8/B5）销账，仍开放三条：aliases/facilities 域「建设中」留位、profile.country 值缺失（数据侧非前端）、浅色主题 |
| `2026-09-11-chainmap-final-batch-report.md` | 1 | 已与 `docs/_working/archive/2026-09/c_class_scattered/2026-09-11-chainmap-final-batch-report.md` 字节等值 → 处置=删 live 重复份，非二次归档 | §七 五条挂账中 1/3/5 已由复启附记（B7/B8/B5）销账，仍开放三条：aliases/facilities 域「建设中」留位、profile.country 值缺失（数据侧非前端）、浅色主题 |
| `2026-09-11-commit-queue-dead-zero-closure.md` | 1 | 含待裁词 3 次却判 1 | 文内自相矛盾一处须总指挥知悉：§6 首行「全部落地（commit 见 git log st-perf-plan-20260910 链）」（L75）与同节 L78「P1⑤ A1/A2、P1⑥、P2⑦⑧⑨ |
| `2026-09-11-commit-queue-dead-zero-closure.md` | 1 | 末笔 6aae9a7439 只动 _working，①依据只剩台账自述 | 文内自相矛盾一处须总指挥知悉：§6 首行「全部落地（commit 见 git log st-perf-plan-20260910 链）」（L75）与同节 L78「P1⑤ A1/A2、P1⑥、P2⑦⑧⑨ |
| `2026-09-11-crypto-shadow-mvp.md` | 1 | 含待裁词 3 次却判 1 | 唯一未闭环=真实首跑（§5 定性为环境级 DNS 污染+SNI 干扰全域封锁，四备用端点实测全灭；§6 首跑指令与 §8 解锁清单（Cloudflare 反代最小成本路径、币安换源属设计变更须 Own |
| `2026-09-11-crypto-shadow-mvp.md` | 1 | 末笔 6aae9a7439 只动 _working，①依据只剩台账自述 | 唯一未闭环=真实首跑（§5 定性为环境级 DNS 污染+SNI 干扰全域封锁，四备用端点实测全灭；§6 首跑指令与 §8 解锁清单（Cloudflare 反代最小成本路径、币安换源属设计变更须 Own |
| `2026-09-11-g07-sentiment-validation.md` | 2 | 含待裁词 3 次却判 2 | 验证结论未进任何真源且真源现状与本件结论矛盾：docs/03_modules/_domain_signal/sentiment_cycle/blueprint.md:32 与 algo_flow/se |
| `2026-09-11-l308-aggregator-construction.md` | 1 | 含待裁词 3 次却判 1 | 落图已由增长轨执行：config/trading_decision_map.yaml:1818 node_id: TDM-E-L3-08 → :1821 module_id: MOD-SIG-142  |
| `2026-09-11-l308-aggregator-construction.md` | 1 | 末笔 6aae9a7439 只动 _working，①依据只剩台账自述 | 落图已由增长轨执行：config/trading_decision_map.yaml:1818 node_id: TDM-E-L3-08 → :1821 module_id: MOD-SIG-142  |
| `2026-09-11-l308-aggregator-construction.md` | 1 | 已与 `docs/_working/archive/2026-09/c_class_scattered/2026-09-11-l308-aggregator-construction.md` 字节等值 → 处置=删 live 重复份，非二次归档 | 落图已由增长轨执行：config/trading_decision_map.yaml:1818 node_id: TDM-E-L3-08 → :1821 module_id: MOD-SIG-142  |
| `2026-09-11-news-chain-wiring-spec-cards.md` | 1 | 含待裁词 3 次却判 1 | 交付已被增长轨消化：config/trading_decision_map.yaml:1311 node_id: TDM-E-L2-09-1（及 :5491-5492 入边/出边）与 :1043 TD |
| `2026-09-11-news-chain-wiring-spec-cards.md` | 1 | 末笔 6aae9a7439 只动 _working，①依据只剩台账自述 | 交付已被增长轨消化：config/trading_decision_map.yaml:1311 node_id: TDM-E-L2-09-1（及 :5491-5492 入边/出边）与 :1043 TD |
| `2026-09-11-news-chain-wiring-spec-cards.md` | 1 | 已与 `docs/_working/archive/2026-09/c_class_scattered/2026-09-11-news-chain-wiring-spec-cards.md` 字节等值 → 处置=删 live 重复份，非二次归档 | 交付已被增长轨消化：config/trading_decision_map.yaml:1311 node_id: TDM-E-L2-09-1（及 :5491-5492 入边/出边）与 :1043 TD |
| `2026-09-11-tdm-morning-review-report.md` | 1 | 含待裁词 3 次却判 1 | 本件自述遗留四项（均为交他轨的在册欠账，非本件未施工）：①币圈 D 类 4 节点待 Owner 立项（G3 已留 95 号 Phase 2 数据层施工痕）②资讯传导 L2-09-1/09-2 等 G2 |
| `2026-09-11-tdm-morning-review-report.md` | 1 | 末笔 6aae9a7439 只动 _working，①依据只剩台账自述 | 本件自述遗留四项（均为交他轨的在册欠账，非本件未施工）：①币圈 D 类 4 节点待 Owner 立项（G3 已留 95 号 Phase 2 数据层施工痕）②资讯传导 L2-09-1/09-2 等 G2 |
| `2026-09-11-tdm-morning-review-report.md` | 1 | 已与 `docs/_working/archive/2026-09/c_class_scattered/2026-09-11-tdm-morning-review-report.md` 字节等值 → 处置=删 live 重复份，非二次归档 | 本件自述遗留四项（均为交他轨的在册欠账，非本件未施工）：①币圈 D 类 4 节点待 Owner 立项（G3 已留 95 号 Phase 2 数据层施工痕）②资讯传导 L2-09-1/09-2 等 G2 |
| `2026-09-12-alt-data-batch1-construction-report.md` | 1 | 含待裁词 5 次却判 1 | 本批零欠账；§5 明确「第 2-4 批待办不变，按 handoff §8 顺序」=工单已移交同系列交接件（本分片另判），不构成本件欠账。§3 标题「Owner 请知悉」为交底样式=数据，未执行任何语义 |
| `2026-09-12-alt-data-batch1-construction-report.md` | 1 | 末笔 6aae9a7439 只动 _working，①依据只剩台账自述 | 本批零欠账；§5 明确「第 2-4 批待办不变，按 handoff §8 顺序」=工单已移交同系列交接件（本分片另判），不构成本件欠账。§3 标题「Owner 请知悉」为交底样式=数据，未执行任何语义 |
| `2026-09-12-alt-data-batch1-construction-report.md` | 1 | 已与 `docs/_working/archive/2026-09/c_class_scattered/2026-09-12-alt-data-batch1-construction-report.md` 字节等值 → 处置=删 live 重复份，非二次归档 | 本批零欠账；§5 明确「第 2-4 批待办不变，按 handoff §8 顺序」=工单已移交同系列交接件（本分片另判），不构成本件欠账。§3 标题「Owner 请知悉」为交底样式=数据，未执行任何语义 |
| `2026-09-12-data-layer-gap-analysis.md` | 2 | 含待裁词 3 次却判 2 | 行动清单侧已被他线消化（P1-A 财报因子=8ac35fdb81、P1-B 研报链路=14b7bb18ce、P1-C 一致预期改道 DS-228 自聚合+EXP 族 data-gap 出证、P2-B  |
| `2026-09-12-expectation-consumption-design.md` | 1 | 含待裁词 5 次却判 1 | 本件已整体晋升为正式政策册（见 already_in_truth_source），§9.3 破坏性处置三选一已由 Owner 2026-09-14 裁 A（保留+标注）并回写，裁定#323 在册消除「 |
| `2026-09-12-expectation-consumption-design.md` | 1 | 已与 `docs/_working/archive/2026-09/c_class_scattered/2026-09-12-expectation-consumption-design.md` 字节等值 → 处置=删 live 重复份，非二次归档 | 本件已整体晋升为正式政策册（见 already_in_truth_source），§9.3 破坏性处置三选一已由 Owner 2026-09-14 裁 A（保留+标注）并回写，裁定#323 在册消除「 |
| `2026-09-12-fundamental-consumption-design.md` | 1 | 含待裁词 5 次却判 1 | D1-D6 已按 RULE-RULING 入册（裁定#228）；F1-M1/F2 已落地，F3/F4/F5 与 §待办移交四项（中报全科目缺口、disclosure_plan 哨兵 11%、三表 19 |
| `2026-09-12-fundamental-consumption-design.md` | 1 | 末笔 4f804539d5 只动 _working，①依据只剩台账自述 | D1-D6 已按 RULE-RULING 入册（裁定#228）；F1-M1/F2 已落地，F3/F4/F5 与 §待办移交四项（中报全科目缺口、disclosure_plan 哨兵 11%、三表 19 |
| `2026-09-12-fundamental-consumption-design.md` | 1 | 已与 `docs/_working/archive/2026-09/c_class_scattered/2026-09-12-fundamental-consumption-design.md` 字节等值 → 处置=删 live 重复份，非二次归档 | D1-D6 已按 RULE-RULING 入册（裁定#228）；F1-M1/F2 已落地，F3/F4/F5 与 §待办移交四项（中报全科目缺口、disclosure_plan 哨兵 11%、三表 19 |
| `2026-09-12-handoff-c3-zcode.md` | 1 | 含待裁词 3 次却判 1 | §五 四项挂起已全部入 HEAD（translated 目录含 pilot_001/002/003 与 c4_* 全量在册；daily_valuation degraded 已登记 data_asse |
| `2026-09-12-handoff-c3-zcode.md` | 1 | 末笔 4f804539d5 只动 _working，①依据只剩台账自述 | §五 四项挂起已全部入 HEAD（translated 目录含 pilot_001/002/003 与 c4_* 全量在册；daily_valuation degraded 已登记 data_asse |
| `2026-09-12-handoff-c3-zcode.md` | 1 | 已与 `docs/_working/archive/2026-09/c_class_scattered/2026-09-12-handoff-c3-zcode.md` 字节等值 → 处置=删 live 重复份，非二次归档 | §五 四项挂起已全部入 HEAD（translated 目录含 pilot_001/002/003 与 c4_* 全量在册；daily_valuation degraded 已登记 data_asse |
| `2026-09-12-igfact-ckg2021-data-asset-analysis.md` | 1 | 含待裁词 3 次却判 1 | 施工方案主体已在 HEAD 侧承接（见 closure_report）；本件「前置依赖：ig_fact 无 valid_to 列」一句已被真源推翻（apply_industry_graph_ddl.p |
| `2026-09-12-igfact-ckg2021-data-asset-analysis.md` | 1 | 末笔 4f804539d5 只动 _working，①依据只剩台账自述 | 施工方案主体已在 HEAD 侧承接（见 closure_report）；本件「前置依赖：ig_fact 无 valid_to 列」一句已被真源推翻（apply_industry_graph_ddl.p |
| `2026-09-12-igfact-ckg2021-data-asset-analysis.md` | 1 | 已与 `docs/_working/archive/2026-09/c_class_scattered/2026-09-12-igfact-ckg2021-data-asset-analysis.md` 字节等值 → 处置=删 live 重复份，非二次归档 | 施工方案主体已在 HEAD 侧承接（见 closure_report）；本件「前置依赖：ig_fact 无 valid_to 列」一句已被真源推翻（apply_industry_graph_ddl.p |
| `2026-09-12-research-report-data-plan.md` | 1 | 含待裁词 5 次却判 1 | §3 五处接线与 §6 验收全部落地（见 closure_report）；DS-228 后续 PIT 价值限制标注已在 DS 条目回写（姊妹件 §9.3 Owner 裁 A 同日执行），本件无自身欠账 |
| `2026-09-12-research-report-data-plan.md` | 1 | 末笔 4f804539d5 只动 _working，①依据只剩台账自述 | §3 五处接线与 §6 验收全部落地（见 closure_report）；DS-228 后续 PIT 价值限制标注已在 DS 条目回写（姊妹件 §9.3 Owner 裁 A 同日执行），本件无自身欠账 |
| `2026-09-12-research-report-data-plan.md` | 1 | 已与 `docs/_working/archive/2026-09/c_class_scattered/2026-09-12-research-report-data-plan.md` 字节等值 → 处置=删 live 重复份，非二次归档 | §3 五处接线与 §6 验收全部落地（见 closure_report）；DS-228 后续 PIT 价值限制标注已在 DS 条目回写（姊妹件 §9.3 Owner 裁 A 同日执行），本件无自身欠账 |
| `2026-09-12-research-report-handoff.md` | 1 | 含待裁词 3 次却判 1 | §3 排队项中 C1.5（consensus 重建挂夜间调度+真源互查）与 C2（expectations 族预注册+首跑出证）已落地，C2 结果为 data-gap 归档（源槽位无 PIT）；C3/ |
| `2026-09-12-research-report-handoff.md` | 1 | 末笔 4f804539d5 只动 _working，①依据只剩台账自述 | §3 排队项中 C1.5（consensus 重建挂夜间调度+真源互查）与 C2（expectations 族预注册+首跑出证）已落地，C2 结果为 data-gap 归档（源槽位无 PIT）；C3/ |
| `2026-09-12-research-report-handoff.md` | 1 | 已与 `docs/_working/archive/2026-09/c_class_scattered/2026-09-12-research-report-handoff.md` 字节等值 → 处置=删 live 重复份，非二次归档 | §3 排队项中 C1.5（consensus 重建挂夜间调度+真源互查）与 C2（expectations 族预注册+首跑出证）已落地，C2 结果为 data-gap 归档（源槽位无 PIT）；C3/ |
| `2026-09-12-work-roadmap.md` | 3 | 含结案词 3 次却判 3 | 本件是时点看板而非判据，多数泳道已被后续会话落地或改道（F1-M1=e7c3a41b9c、F2=8ac35fdb81、C1=14b7bb18ce、C2=2f65e0043a/72362d5a25、P0 |
| `2026-09-13-c5-cluster-differentiation-report.md` | 1 | 含待裁词 3 次却判 1 | 唯一显式欠账「挂图（TDM 节点 strategies+state_matrix）与 PP-001 配比语义留专项一次做齐」已由 fa53723fb2（2026-09-14 23:41）收口；本件另含 |
| `2026-09-13-c5-cluster-differentiation-report.md` | 1 | 末笔 4f804539d5 只动 _working，①依据只剩台账自述 | 唯一显式欠账「挂图（TDM 节点 strategies+state_matrix）与 PP-001 配比语义留专项一次做齐」已由 fa53723fb2（2026-09-14 23:41）收口；本件另含 |
| `2026-09-13-c5-cluster-differentiation-report.md` | 1 | 已与 `docs/_working/archive/2026-09/c_class_scattered/2026-09-13-c5-cluster-differentiation-report.md` 字节等值 → 处置=删 live 重复份，非二次归档 | 唯一显式欠账「挂图（TDM 节点 strategies+state_matrix）与 PP-001 配比语义留专项一次做齐」已由 fa53723fb2（2026-09-14 23:41）收口；本件另含 |
| `2026-09-13-factory-gate-review.md` | 1 | 含待裁词 3 次却判 1 | §6 施工清单已由 b88b8fec5d 全批落地（见 closure_report）；两项显式留待 Owner 追认：field_dictionary 裁剪缓办、18 个空 __init__.py  |
| `2026-09-13-factory-gate-review.md` | 1 | 末笔 4f804539d5 只动 _working，①依据只剩台账自述 | §6 施工清单已由 b88b8fec5d 全批落地（见 closure_report）；两项显式留待 Owner 追认：field_dictionary 裁剪缓办、18 个空 __init__.py  |
| `2026-09-13-factory-gate-review.md` | 1 | 已与 `docs/_working/archive/2026-09/c_class_scattered/2026-09-13-factory-gate-review.md` 字节等值 → 处置=删 live 重复份，非二次归档 | §6 施工清单已由 b88b8fec5d 全批落地（见 closure_report）；两项显式留待 Owner 追认：field_dictionary 裁剪缓办、18 个空 __init__.py  |
| `2026-09-13-io-structure-anchor-plan.md` | 1 | 含待裁词 3 次却判 1 | §3 验收线由落地批一并交付（42/153 部门入库+映射覆盖率报告+对照样本校准报告）；§5 防蔓延清单四项留作后续候选：年报前五大供应商解析（第二施工件，iFinD 供应链模块盘点先行）、链长制图 |
| `2026-09-13-io-structure-anchor-plan.md` | 1 | 末笔 4f804539d5 只动 _working，①依据只剩台账自述 | §3 验收线由落地批一并交付（42/153 部门入库+映射覆盖率报告+对照样本校准报告）；§5 防蔓延清单四项留作后续候选：年报前五大供应商解析（第二施工件，iFinD 供应链模块盘点先行）、链长制图 |
| `2026-09-13-io-structure-anchor-plan.md` | 1 | 已与 `docs/_working/archive/2026-09/c_class_scattered/2026-09-13-io-structure-anchor-plan.md` 字节等值 → 处置=删 live 重复份，非二次归档 | §3 验收线由落地批一并交付（42/153 部门入库+映射覆盖率报告+对照样本校准报告）；§5 防蔓延清单四项留作后续候选：年报前五大供应商解析（第二施工件，iFinD 供应链模块盘点先行）、链长制图 |
| `2026-09-13-knowledge-reserve-nonpipeline.md` | 2 | 含待裁词 3 次却判 2 | 六板块中四条已被真源承接（见 already_in_truth_source，属部分命中）：板块一由 TDM 升级蓝图归口并建成 UP-1..UP-5 且入 decision_algo_registr |
| `2026-09-13-p002-semantic-review.md` | 1 | 含待裁词 3 次却判 1 | 三步序后续：②重印已落地（见 closure_report），③重训（同语义换窗）按本件结论押后；本件 §3/裁定在册的遗留待裁项=r11/r12 死态（1/6 日）合并建议——枚举变更属生产门位，留 |
| `2026-09-13-p002-semantic-review.md` | 1 | 末笔 4f804539d5 只动 _working，①依据只剩台账自述 | 三步序后续：②重印已落地（见 closure_report），③重训（同语义换窗）按本件结论押后；本件 §3/裁定在册的遗留待裁项=r11/r12 死态（1/6 日）合并建议——枚举变更属生产门位，留 |
| `2026-09-13-p002-semantic-review.md` | 1 | 已与 `docs/_working/archive/2026-09/c_class_scattered/2026-09-13-p002-semantic-review.md` 字节等值 → 处置=删 live 重复份，非二次归档 | 三步序后续：②重印已落地（见 closure_report），③重训（同语义换窗）按本件结论押后；本件 §3/裁定在册的遗留待裁项=r11/r12 死态（1/6 日）合并建议——枚举变更属生产门位，留 |
| `2026-09-13-panic-rebound-sim-paper.md` | 1 | 含待裁词 3 次却判 1 | 施工清单六项未逐项销项（复选框原文均未勾），但主体已由后续批次落地：registry 在册且 lifecycle_status=sim、挂图与 PP-001 配比已做齐（fa53723fb2）；未落地 |
| `2026-09-13-panic-rebound-sim-paper.md` | 1 | 末笔 275bc860dc 只动 _working，①依据只剩台账自述 | 施工清单六项未逐项销项（复选框原文均未勾），但主体已由后续批次落地：registry 在册且 lifecycle_status=sim、挂图与 PP-001 配比已做齐（fa53723fb2）；未落地 |
| `2026-09-13-panic-rebound-sim-paper.md` | 1 | 已与 `docs/_working/archive/2026-09/c_class_scattered/2026-09-13-panic-rebound-sim-paper.md` 字节等值 → 处置=删 live 重复份，非二次归档 | 施工清单六项未逐项销项（复选框原文均未勾），但主体已由后续批次落地：registry 在册且 lifecycle_status=sim、挂图与 PP-001 配比已做齐（fa53723fb2）；未落地 |
| `2026-09-13-strategy-factory-pipeline-discussion.md` | 1 | 含待裁词 5 次却判 1 | v10 自述「本讨论稿历史使命完成，全部讨论已消化为正式结构稿 config/strategy_production_map.yaml（489f433165），本稿转为背景设计文集不再追加」→ 按合同 |
| `2026-09-13-strategy-factory-pipeline-discussion.md` | 1 | 末笔 4f804539d5 只动 _working，①依据只剩台账自述 | v10 自述「本讨论稿历史使命完成，全部讨论已消化为正式结构稿 config/strategy_production_map.yaml（489f433165），本稿转为背景设计文集不再追加」→ 按合同 |
| `2026-09-13-strategy-factory-pipeline-discussion.md` | 1 | 已与 `docs/_working/archive/2026-09/c_class_scattered/2026-09-13-strategy-factory-pipeline-discussion.md` 字节等值 → 处置=删 live 重复份，非二次归档 | v10 自述「本讨论稿历史使命完成，全部讨论已消化为正式结构稿 config/strategy_production_map.yaml（489f433165），本稿转为背景设计文集不再追加」→ 按合同 |
| `2026-09-13-tdm-upgrade-blueprint.md` | 1 | 含待裁词 3 次却判 1 | 本件判据已入真源（decision_algo_registry 五条 DAL 条目含 UP-2 P(跌)≥0.65/尾比≥0.60、UP-5 CVaR(5%) 阈 -3% 日损阈值冻结；trading |
| `2026-09-13-tdm-upgrade-blueprint.md` | 1 | 末笔 4f804539d5 只动 _working，①依据只剩台账自述 | 本件判据已入真源（decision_algo_registry 五条 DAL 条目含 UP-2 P(跌)≥0.65/尾比≥0.60、UP-5 CVaR(5%) 阈 -3% 日损阈值冻结；trading |
| `2026-09-13-tdm-upgrade-blueprint.md` | 1 | 已与 `docs/_working/archive/2026-09/c_class_scattered/2026-09-13-tdm-upgrade-blueprint.md` 字节等值 → 处置=删 live 重复份，非二次归档 | 本件判据已入真源（decision_algo_registry 五条 DAL 条目含 UP-2 P(跌)≥0.65/尾比≥0.60、UP-5 CVaR(5%) 阈 -3% 日损阈值冻结；trading |
| `2026-09-13-xtreme-redblue-retest.md` | 1 | 含待裁词 7 次却判 1 | §4 四条新发现均为交他轨的在册欠账，不属本件未施工：①阻断消息 new_root 单值指针多目录场景误导（P3 小瑕疵）②被拦提交预暂存 AD 幻影不自动回滚（P3 待办）③GATE-TRACKED |
| `2026-09-13-xtreme-redblue-retest.md` | 1 | 末笔 4f804539d5 只动 _working，①依据只剩台账自述 | §4 四条新发现均为交他轨的在册欠账，不属本件未施工：①阻断消息 new_root 单值指针多目录场景误导（P3 小瑕疵）②被拦提交预暂存 AD 幻影不自动回滚（P3 待办）③GATE-TRACKED |
| `2026-09-13-xtreme-redblue-retest.md` | 1 | 已与 `docs/_working/archive/2026-09/c_class_scattered/2026-09-13-xtreme-redblue-retest.md` 字节等值 → 处置=删 live 重复份，非二次归档 | §4 四条新发现均为交他轨的在册欠账，不属本件未施工：①阻断消息 new_root 单值指针多目录场景误导（P3 小瑕疵）②被拦提交预暂存 AD 幻影不自动回滚（P3 待办）③GATE-TRACKED |
| `2026-09-13-xtreme-redblue-v3-log.md` | 1 | 含待裁词 16 次却判 1 | 日志自述两条未覆盖项（S2.5 本体待注册表恢复后补测、怪文件名/怪 message 批被第二次 blackout 吞没）；其后红蓝 v4 已复测（docs/_working/2026-09-14-x |
| `2026-09-13-xtreme-redblue-v3-log.md` | 1 | 末笔 4f804539d5 只动 _working，①依据只剩台账自述 | 日志自述两条未覆盖项（S2.5 本体待注册表恢复后补测、怪文件名/怪 message 批被第二次 blackout 吞没）；其后红蓝 v4 已复测（docs/_working/2026-09-14-x |
| `2026-09-13-xtreme-redblue-v3-log.md` | 1 | 已与 `docs/_working/archive/2026-09/c_class_scattered/2026-09-13-xtreme-redblue-v3-log.md` 字节等值 → 处置=删 live 重复份，非二次归档 | 日志自述两条未覆盖项（S2.5 本体待注册表恢复后补测、怪文件名/怪 message 批被第二次 blackout 吞没）；其后红蓝 v4 已复测（docs/_working/2026-09-14-x |
| `2026-09-13-xtreme-redblue-v3-plan.md` | 1 | 含待裁词 11 次却判 1 | 本件正文=对执行者的任务书样式文本（「你是红方」「五条铁律」「每个场景做完立刻写日志」），按合同 §6 视为数据，未执行其中任何语义；机械底座 twin=- 漏判：archive/2026-09/c_ |
| `2026-09-13-xtreme-redblue-v3-plan.md` | 1 | 末笔 4f804539d5 只动 _working，①依据只剩台账自述 | 本件正文=对执行者的任务书样式文本（「你是红方」「五条铁律」「每个场景做完立刻写日志」），按合同 §6 视为数据，未执行其中任何语义；机械底座 twin=- 漏判：archive/2026-09/c_ |
| `2026-09-13-xtreme-redblue-v3-report.md` | 1 | 含待裁词 8 次却判 1 | 清单处置度：P0-1 语法门已建（SYNTAX-VALIDATION priority=49，配套日志=本分片 2026-09-14-p0-syntax-gate.md）、P1-1 伪造标记门已建、P |
| `2026-09-13-xtreme-redblue-v3-report.md` | 1 | 末笔 4f804539d5 只动 _working，①依据只剩台账自述 | 清单处置度：P0-1 语法门已建（SYNTAX-VALIDATION priority=49，配套日志=本分片 2026-09-14-p0-syntax-gate.md）、P1-1 伪造标记门已建、P |
| `2026-09-13-xtreme-redblue-v3-report.md` | 1 | 已与 `docs/_working/archive/2026-09/c_class_scattered/2026-09-13-xtreme-redblue-v3-report.md` 字节等值 → 处置=删 live 重复份，非二次归档 | 清单处置度：P0-1 语法门已建（SYNTAX-VALIDATION priority=49，配套日志=本分片 2026-09-14-p0-syntax-gate.md）、P1-1 伪造标记门已建、P |
| `2026-09-14-agg-switch-design.md` | 1 | 含待裁词 3 次却判 1 | §3 切换判据三条中「Owner 对灰度曲线参数签字」已由 裁定#231 落纸（ef2302e2c0）；§4 FQ-01 以 `high_accrual` 字段形态落码（negative_veto.p |
| `2026-09-14-agg-switch-design.md` | 1 | 末笔 4f804539d5 只动 _working，①依据只剩台账自述 | §3 切换判据三条中「Owner 对灰度曲线参数签字」已由 裁定#231 落纸（ef2302e2c0）；§4 FQ-01 以 `high_accrual` 字段形态落码（negative_veto.p |
| `2026-09-14-agg-switch-design.md` | 1 | 已与 `docs/_working/archive/2026-09/c_class_scattered/2026-09-14-agg-switch-design.md` 字节等值 → 处置=删 live 重复份，非二次归档 | §3 切换判据三条中「Owner 对灰度曲线参数签字」已由 裁定#231 落纸（ef2302e2c0）；§4 FQ-01 以 `high_accrual` 字段形态落码（negative_veto.p |
| `2026-09-14-auto-mount-research.md` | 1 | 含待裁词 5 次却判 1 | 本件自述「未施工，等排期」已被后续批销案：MOD-BT-171 已建并转 production、验收五条全过、Owner 2026-09-15 02:03 批复「通过」（结案报告 docs/_work |
| `2026-09-14-auto-mount-research.md` | 1 | 末笔 4f804539d5 只动 _working，①依据只剩台账自述 | 本件自述「未施工，等排期」已被后续批销案：MOD-BT-171 已建并转 production、验收五条全过、Owner 2026-09-15 02:03 批复「通过」（结案报告 docs/_work |
| `2026-09-14-auto-mount-research.md` | 1 | 已与 `docs/_working/archive/2026-09/c_class_scattered/2026-09-14-auto-mount-research.md` 字节等值 → 处置=删 live 重复份，非二次归档 | 本件自述「未施工，等排期」已被后续批销案：MOD-BT-171 已建并转 production、验收五条全过、Owner 2026-09-15 02:03 批复「通过」（结案报告 docs/_work |
| `2026-09-14-c4-history-repair-plan.md` | 1 | 含待裁词 3 次却判 1 | 本件边界内 2017-2021 段已落表并定稿（净段 FINAL 1,563,996 行，2022-2025 断供段=本件明示「独立子工程，本方案不含」）；原型验收为阶段版（人工抽核协议 15/30  |
| `2026-09-14-c4-history-repair-plan.md` | 1 | 末笔 4f804539d5 只动 _working，①依据只剩台账自述 | 本件边界内 2017-2021 段已落表并定稿（净段 FINAL 1,563,996 行，2022-2025 断供段=本件明示「独立子工程，本方案不含」）；原型验收为阶段版（人工抽核协议 15/30  |
| `2026-09-14-c4-history-repair-plan.md` | 1 | 已与 `docs/_working/archive/2026-09/c_class_scattered/2026-09-14-c4-history-repair-plan.md` 字节等值 → 处置=删 live 重复份，非二次归档 | 本件边界内 2017-2021 段已落表并定稿（净段 FINAL 1,563,996 行，2022-2025 断供段=本件明示「独立子工程，本方案不含」）；原型验收为阶段版（人工抽核协议 15/30  |
| `2026-09-14-ch-connection-handoff.md` | 1 | 含待裁词 3 次却判 1 | 本件 §四「完成」判据第 3 条（多会话并发零断连）由结案报告以实测承载（6 程序并发 25 秒 47,210 查询零错误、连接数精确 +6）；本件列出的引用件 c4_deferrals.csv/si |
| `2026-09-14-ch-connection-handoff.md` | 1 | 末笔 4f804539d5 只动 _working，①依据只剩台账自述 | 本件 §四「完成」判据第 3 条（多会话并发零断连）由结案报告以实测承载（6 程序并发 25 秒 47,210 查询零错误、连接数精确 +6）；本件列出的引用件 c4_deferrals.csv/si |
| `2026-09-14-ch-connection-handoff.md` | 1 | 已与 `docs/_working/archive/2026-09/c_class_scattered/2026-09-14-ch-connection-handoff.md` 字节等值 → 处置=删 live 重复份，非二次归档 | 本件 §四「完成」判据第 3 条（多会话并发零断连）由结案报告以实测承载（6 程序并发 25 秒 47,210 查询零错误、连接数精确 +6）；本件列出的引用件 c4_deferrals.csv/si |
| `2026-09-14-chart-pattern-mining-report.md` | 1 | 含待裁词 6 次却判 1 | 登记类结论已全部入注册表真源（现 version 2.18.0，schema_version 2.2），本件退化为挖矿过程记录；仍欠两项：①§六 P1/P2/P3 实现候选（检测器施工）②§十自述「未 |
| `2026-09-14-chart-pattern-mining-report.md` | 1 | 末笔 4f804539d5 只动 _working，①依据只剩台账自述 | 登记类结论已全部入注册表真源（现 version 2.18.0，schema_version 2.2），本件退化为挖矿过程记录；仍欠两项：①§六 P1/P2/P3 实现候选（检测器施工）②§十自述「未 |
| `2026-09-14-chart-pattern-mining-report.md` | 1 | 已与 `docs/_working/archive/2026-09/c_class_scattered/2026-09-14-chart-pattern-mining-report.md` 字节等值 → 处置=删 live 重复份，非二次归档 | 登记类结论已全部入注册表真源（现 version 2.18.0，schema_version 2.2），本件退化为挖矿过程记录；仍欠两项：①§六 P1/P2/P3 实现候选（检测器施工）②§十自述「未 |
| `2026-09-14-combination-layer-exhaustive-charter.md` | 1 | 含待裁词 5 次却判 1 | 立项/裁定/schema 结论已进正式真源（见 already_in_truth_source），本件退化为立项过程件；施工侧欠账按排产总览自述：批次 A 实跑 2000 条当时「发射运行中」、3.3 |
| `2026-09-14-combination-layer-exhaustive-charter.md` | 1 | 末笔 03becdf2e7 只动 _working，①依据只剩台账自述 | 立项/裁定/schema 结论已进正式真源（见 already_in_truth_source），本件退化为立项过程件；施工侧欠账按排产总览自述：批次 A 实跑 2000 条当时「发射运行中」、3.3 |
| `2026-09-14-combination-layer-exhaustive-charter.md` | 1 | 已与 `docs/_working/archive/2026-09/c_class_scattered/2026-09-14-combination-layer-exhaustive-charter.md` 字节等值 → 处置=删 live 重复份，非二次归档 | 立项/裁定/schema 结论已进正式真源（见 already_in_truth_source），本件退化为立项过程件；施工侧欠账按排产总览自述：批次 A 实跑 2000 条当时「发射运行中」、3.3 |
| `2026-09-14-dsr-enable-impact-assessment.md` | 1 | 含待裁词 3 次却判 1 | §七 五项裁定已自裁并在文内；后续三步走第②③步（阈值三线统一、开关只对新批次+未注入记 not_tested）按文内记载由本班及后续班执行，代码侧现为默认开启态（见 already_in_truth |
| `2026-09-14-dsr-enable-impact-assessment.md` | 1 | 已与 `docs/_working/archive/2026-09/c_class_scattered/2026-09-14-dsr-enable-impact-assessment.md` 字节等值 → 处置=删 live 重复份，非二次归档 | §七 五项裁定已自裁并在文内；后续三步走第②③步（阈值三线统一、开关只对新批次+未注入记 not_tested）按文内记载由本班及后续班执行，代码侧现为默认开启态（见 already_in_truth |
| `2026-09-14-fac-e1c-formula-mining-design.md` | 1 | 含待裁词 6 次却判 1 | 文内 §七 待办四项中 ①白名单过审→status=active、②正式档自动化（计划任务 ZephyrAlpha_FactoryLaneC）已落，③v2 自定义算子批、④AlphaGen 立项两项后 |
| `2026-09-14-fac-e1c-formula-mining-design.md` | 1 | 末笔 4f804539d5 只动 _working，①依据只剩台账自述 | 文内 §七 待办四项中 ①白名单过审→status=active、②正式档自动化（计划任务 ZephyrAlpha_FactoryLaneC）已落，③v2 自定义算子批、④AlphaGen 立项两项后 |
| `2026-09-14-fac-e1c-formula-mining-design.md` | 1 | 已与 `docs/_working/archive/2026-09/c_class_scattered/2026-09-14-fac-e1c-formula-mining-design.md` 字节等值 → 处置=删 live 重复份，非二次归档 | 文内 §七 待办四项中 ①白名单过审→status=active、②正式档自动化（计划任务 ZephyrAlpha_FactoryLaneC）已落，③v2 自定义算子批、④AlphaGen 立项两项后 |
| `2026-09-14-full-chain-factory-blueprint.md` | 2 | 含待裁词 5 次却判 2 | 部分结论已被吸收（§十 活性谓词=MOD-POS-029 蓝图设计真源之一、config/position_recipe_grid_schema.yaml；§九-4 N 账本已建），但**顶层判据未进 |
| `2026-09-14-handoff-market-data-repair.md` | 1 | 含待裁词 5 次却判 1 | 待办四项中 P0-1/P0-2/P0-3/P1-4 均销（P0-2 由 Owner 09-14 08:0x 批准、11:14 五表归零，「已决未回写」经 裁定#323 补记=本件最后一次改动 01fb |
| `2026-09-14-handoff-market-data-repair.md` | 1 | 已与 `docs/_working/archive/2026-09/c_class_scattered/2026-09-14-handoff-market-data-repair.md` 字节等值 → 处置=删 live 重复份，非二次归档 | 待办四项中 P0-1/P0-2/P0-3/P1-4 均销（P0-2 由 Owner 09-14 08:0x 批准、11:14 五表归零，「已决未回写」经 裁定#323 补记=本件最后一次改动 01fb |
| `2026-09-14-indicator-mining-batch4.md` | 1 | 含待裁词 3 次却判 1 | 立卡与长尾均已被后续批清偿（真源描述逐批点名本件「挖矿立卡 1/2/3」，见 already_in_truth_source）；唯一未落项=本件「不做边界」中 SCR/CYQ 筹码族挂 Owner 裁 |
| `2026-09-14-indicator-mining-batch4.md` | 1 | 末笔 4f804539d5 只动 _working，①依据只剩台账自述 | 立卡与长尾均已被后续批清偿（真源描述逐批点名本件「挖矿立卡 1/2/3」，见 already_in_truth_source）；唯一未落项=本件「不做边界」中 SCR/CYQ 筹码族挂 Owner 裁 |
| `2026-09-14-indicator-mining-batch4.md` | 1 | 已与 `docs/_working/archive/2026-09/c_class_scattered/2026-09-14-indicator-mining-batch4.md` 字节等值 → 处置=删 live 重复份，非二次归档 | 立卡与长尾均已被后续批清偿（真源描述逐批点名本件「挖矿立卡 1/2/3」，见 already_in_truth_source）；唯一未落项=本件「不做边界」中 SCR/CYQ 筹码族挂 Owner 裁 |
| `2026-09-14-lane-c-agentic-mining-charter.md` | 1 | 含待裁词 3 次却判 1 | §六 开放三项未见本件内销案：本机代理恢复后补 `git clone --depth 1` 实跑、AST 相似度实现选型（自研 vs 现成库）、deepseek-r1:8b 消融档是否首班双模型对比； |
| `2026-09-14-lane-c-agentic-mining-charter.md` | 1 | 末笔 4f804539d5 只动 _working，①依据只剩台账自述 | §六 开放三项未见本件内销案：本机代理恢复后补 `git clone --depth 1` 实跑、AST 相似度实现选型（自研 vs 现成库）、deepseek-r1:8b 消融档是否首班双模型对比； |
| `2026-09-14-lane-c-agentic-mining-charter.md` | 1 | 已与 `docs/_working/archive/2026-09/c_class_scattered/2026-09-14-lane-c-agentic-mining-charter.md` 字节等值 → 处置=删 live 重复份，非二次归档 | §六 开放三项未见本件内销案：本机代理恢复后补 `git clone --depth 1` 实跑、AST 相似度实现选型（自研 vs 现成库）、deepseek-r1:8b 消融档是否首班双模型对比； |
| `2026-09-14-market-data-gap-report.md` | 1 | 末笔 8e2a1561d5 只动 _working，①依据只剩台账自述 | 文内结案块自列 4 项遗留，本分片复验后状态：①防复发四件套「待立项」——其中 ②ch_writer 表列缓存失效已落（ch_writer.py:716 table_cols_cache.pop /  |
| `2026-09-14-p0-syntax-gate.md` | 1 | 含待裁词 3 次却判 1 | §5 遗留四项：①磁盘残留探针 tests/governance/rule_bridge/xt_p01_syntaxerr.py 待 Owner 手动删（本分片复验：该路径现不存在=清库已执行）；②` |
| `2026-09-14-p0-syntax-gate.md` | 1 | 末笔 4f804539d5 只动 _working，①依据只剩台账自述 | §5 遗留四项：①磁盘残留探针 tests/governance/rule_bridge/xt_p01_syntaxerr.py 待 Owner 手动删（本分片复验：该路径现不存在=清库已执行）；②` |
| `2026-09-14-p0-syntax-gate.md` | 1 | 已与 `docs/_working/archive/2026-09/c_class_scattered/2026-09-14-p0-syntax-gate.md` 字节等值 → 处置=删 live 重复份，非二次归档 | §5 遗留四项：①磁盘残留探针 tests/governance/rule_bridge/xt_p01_syntaxerr.py 待 Owner 手动删（本分片复验：该路径现不存在=清库已执行）；②` |
| `2026-09-14-p002-reprint-result.md` | 1 | 含待裁词 3 次却判 1 | §5「明确不做（待 Owner/后续批）」三件：TDM 生产消费切换（已由同分片 2026-09-14-agg-switch-design.md 落地，cap 在产）、判据契约变更（本件 §四 已自裁 |
| `2026-09-14-p002-reprint-result.md` | 1 | 末笔 4f804539d5 只动 _working，①依据只剩台账自述 | §5「明确不做（待 Owner/后续批）」三件：TDM 生产消费切换（已由同分片 2026-09-14-agg-switch-design.md 落地，cap 在产）、判据契约变更（本件 §四 已自裁 |
| `2026-09-14-p002-reprint-result.md` | 1 | 已与 `docs/_working/archive/2026-09/c_class_scattered/2026-09-14-p002-reprint-result.md` 字节等值 → 处置=删 live 重复份，非二次归档 | §5「明确不做（待 Owner/后续批）」三件：TDM 生产消费切换（已由同分片 2026-09-14-agg-switch-design.md 落地，cap 在产）、判据契约变更（本件 §四 已自裁 |
| `2026-09-14-pattern-consumer-plan.md` | 1 | 含待裁词 3 次却判 1 | C1-C4 均有落地面（见 already_in_truth_source）；C5 边界登记三件（回测 screen/lane_c 形态条件、TDM 形态→信号边、pattern breadth 因子 |
| `2026-09-14-pattern-consumer-plan.md` | 1 | 末笔 4f804539d5 只动 _working，①依据只剩台账自述 | C1-C4 均有落地面（见 already_in_truth_source）；C5 边界登记三件（回测 screen/lane_c 形态条件、TDM 形态→信号边、pattern breadth 因子 |
| `2026-09-14-pattern-consumer-plan.md` | 1 | 已与 `docs/_working/archive/2026-09/c_class_scattered/2026-09-14-pattern-consumer-plan.md` 字节等值 → 处置=删 live 重复份，非二次归档 | C1-C4 均有落地面（见 already_in_truth_source）；C5 边界登记三件（回测 screen/lane_c 形态条件、TDM 形态→信号边、pattern breadth 因子 |
| `2026-09-14-sim-partition-discussion.md` | 1 | 含待裁词 3 次却判 1 | 决策点①②：先 C 已落（sim_paper_ledger+sim_pocket_daily+日链自动化），第二步方案 A（虚拟子仓+真实撮合，桥接层改造）本件明示「另立批次」，本分片未见其落地面；晋 |
| `2026-09-14-sim-partition-discussion.md` | 1 | 末笔 4f804539d5 只动 _working，①依据只剩台账自述 | 决策点①②：先 C 已落（sim_paper_ledger+sim_pocket_daily+日链自动化），第二步方案 A（虚拟子仓+真实撮合，桥接层改造）本件明示「另立批次」，本分片未见其落地面；晋 |
| `2026-09-14-sim-partition-discussion.md` | 1 | 已与 `docs/_working/archive/2026-09/c_class_scattered/2026-09-14-sim-partition-discussion.md` 字节等值 → 处置=删 live 重复份，非二次归档 | 决策点①②：先 C 已落（sim_paper_ledger+sim_pocket_daily+日链自动化），第二步方案 A（虚拟子仓+真实撮合，桥接层改造）本件明示「另立批次」，本分片未见其落地面；晋 |
| `2026-09-14-supply483-verification-report.md` | 1 | 含待裁词 3 次却判 1 | 本件自列两项「他批/他会话」欠账，本分片复验未见落地面：①§3 B 组剩余客户名→代码匹配器（模糊匹配+拼音/简称库+人工复核队列；scripts/industry_graph/ 下无 name→co |
| `2026-09-14-supply483-verification-report.md` | 1 | 末笔 4f804539d5 只动 _working，①依据只剩台账自述 | 本件自列两项「他批/他会话」欠账，本分片复验未见落地面：①§3 B 组剩余客户名→代码匹配器（模糊匹配+拼音/简称库+人工复核队列；scripts/industry_graph/ 下无 name→co |
| `2026-09-14-supply483-verification-report.md` | 1 | 已与 `docs/_working/archive/2026-09/c_class_scattered/2026-09-14-supply483-verification-report.md` 字节等值 → 处置=删 live 重复份，非二次归档 | 本件自列两项「他批/他会话」欠账，本分片复验未见落地面：①§3 B 组剩余客户名→代码匹配器（模糊匹配+拼音/简称库+人工复核队列；scripts/industry_graph/ 下无 name→co |
| `2026-09-14-tdm-consumption-sop-draft.md` | 1 | 含待裁词 3 次却判 1 | 草案→permanent 已升卷，S7-S9 与知识生效日哨兵已入正式条款；TDM v1.3 施工件亦已 production（upgrade_tdm_v13_metadata.py，material |
| `2026-09-14-tdm-consumption-sop-draft.md` | 1 | 末笔 4f804539d5 只动 _working，①依据只剩台账自述 | 草案→permanent 已升卷，S7-S9 与知识生效日哨兵已入正式条款；TDM v1.3 施工件亦已 production（upgrade_tdm_v13_metadata.py，material |
| `2026-09-14-tdm-consumption-sop-draft.md` | 1 | 已与 `docs/_working/archive/2026-09/c_class_scattered/2026-09-14-tdm-consumption-sop-draft.md` 字节等值 → 处置=删 live 重复份，非二次归档 | 草案→permanent 已升卷，S7-S9 与知识生效日哨兵已入正式条款；TDM v1.3 施工件亦已 production（upgrade_tdm_v13_metadata.py，material |
| `2026-09-14-tilib-batch6-plan.md` | 1 | 含待裁词 3 次却判 1 | ①§1 末尾指标分类合计自述 91≠92 的算术存疑段未清理（文内已声明以代码实测为准）；②§5 消费端接线批已由批7 件展开；③本件头部清理批自动结案报告判「设计/计划类且无落地证据·保守保留」与事 |
| `2026-09-14-tilib-batch6-plan.md` | 1 | 末笔 4f804539d5 只动 _working，①依据只剩台账自述 | ①§1 末尾指标分类合计自述 91≠92 的算术存疑段未清理（文内已声明以代码实测为准）；②§5 消费端接线批已由批7 件展开；③本件头部清理批自动结案报告判「设计/计划类且无落地证据·保守保留」与事 |
| `2026-09-14-tilib-batch6-plan.md` | 1 | 已与 `docs/_working/archive/2026-09/c_class_scattered/2026-09-14-tilib-batch6-plan.md` 字节等值 → 处置=删 live 重复份，非二次归档 | ①§1 末尾指标分类合计自述 91≠92 的算术存疑段未清理（文内已声明以代码实测为准）；②§5 消费端接线批已由批7 件展开；③本件头部清理批自动结案报告判「设计/计划类且无落地证据·保守保留」与事 |
| `2026-09-14-tilib-batch7-wiring-plan.md` | 1 | 含待裁词 3 次却判 1 | ①§4 回填链快照（daily 新列等四轮）发布时点已过时，由后续 tilib 清欠班收口；②块C used_by_factors 逐条回填无本件内回执；③头部自动结案报告同样判「无落地证据」，与 5 |
| `2026-09-14-tilib-batch7-wiring-plan.md` | 1 | 末笔 4f804539d5 只动 _working，①依据只剩台账自述 | ①§4 回填链快照（daily 新列等四轮）发布时点已过时，由后续 tilib 清欠班收口；②块C used_by_factors 逐条回填无本件内回执；③头部自动结案报告同样判「无落地证据」，与 5 |
| `2026-09-14-tilib-batch7-wiring-plan.md` | 1 | 已与 `docs/_working/archive/2026-09/c_class_scattered/2026-09-14-tilib-batch7-wiring-plan.md` 字节等值 → 处置=删 live 重复份，非二次归档 | ①§4 回填链快照（daily 新列等四轮）发布时点已过时，由后续 tilib 清欠班收口；②块C used_by_factors 逐条回填无本件内回执；③头部自动结案报告同样判「无落地证据」，与 5 |
| `2026-09-14-typhoon-bdi-factor-mining-plan.md` | 1 | 含待裁词 3 次却判 1 | ①GAP 积累中卡位 6 项（F1-F3、F10、F12、F8/F9）与 CNKI 中文文献「受阻」项在册未复验；②本件自述「季节性基线先行写入事件类因子研究的默认动作」——按合同 §3 机械查真源： |
| `2026-09-14-typhoon-bdi-factor-mining-plan.md` | 1 | 末笔 4f804539d5 只动 _working，①依据只剩台账自述 | ①GAP 积累中卡位 6 项（F1-F3、F10、F12、F8/F9）与 CNKI 中文文献「受阻」项在册未复验；②本件自述「季节性基线先行写入事件类因子研究的默认动作」——按合同 §3 机械查真源： |
| `2026-09-14-typhoon-bdi-factor-mining-plan.md` | 1 | 已与 `docs/_working/archive/2026-09/c_class_scattered/2026-09-14-typhoon-bdi-factor-mining-plan.md` 字节等值 → 处置=删 live 重复份，非二次归档 | ①GAP 积累中卡位 6 项（F1-F3、F10、F12、F8/F9）与 CNKI 中文文献「受阻」项在册未复验；②本件自述「季节性基线先行写入事件类因子研究的默认动作」——按合同 §3 机械查真源： |
| `2026-09-14-xtreme-redblue-v4-report.md` | 1 | 含待裁词 9 次却判 1 | ①留 v5 项（P1-1② 自身标记放行未取证、并发同时性场景）——v5 报告已产并归档于 docs/_working/archive/2026-09/redblue/2026-09-15-xtrem |
| `2026-09-14-xtreme-redblue-v4-report.md` | 1 | 末笔 4f804539d5 只动 _working，①依据只剩台账自述 | ①留 v5 项（P1-1② 自身标记放行未取证、并发同时性场景）——v5 报告已产并归档于 docs/_working/archive/2026-09/redblue/2026-09-15-xtrem |
| `2026-09-15-c4-acceptance-interim.md` | 1 | 含待裁词 3 次却判 1 | ①本件自述为阶段版：抽核协议余 15 份的逐夜滚动目视无后续回执件；②mid 层 344 行「留档待复核升级」未见销案；③全量批 ~60,477 份的完成度以缓存盘实测间接佐证（cb7786e75d  |
| `2026-09-15-c4-acceptance-interim.md` | 1 | 末笔 275bc860dc 只动 _working，①依据只剩台账自述 | ①本件自述为阶段版：抽核协议余 15 份的逐夜滚动目视无后续回执件；②mid 层 344 行「留档待复核升级」未见销案；③全量批 ~60,477 份的完成度以缓存盘实测间接佐证（cb7786e75d  |
| `2026-09-15-c4-acceptance-interim.md` | 1 | 已与 `docs/_working/archive/2026-09/c_class_scattered/2026-09-15-c4-acceptance-interim.md` 字节等值 → 处置=删 live 重复份，非二次归档 | ①本件自述为阶段版：抽核协议余 15 份的逐夜滚动目视无后续回执件；②mid 层 344 行「留档待复核升级」未见销案；③全量批 ~60,477 份的完成度以缓存盘实测间接佐证（cb7786e75d  |
| `2026-09-15-c5-cluster-refresh.md` | 1 | 已与 `docs/_working/archive/2026-09/c_class_scattered/2026-09-15-c5-cluster-refresh.md` 字节等值 → 处置=删 live 重复份，非二次归档 | ①§3 后续两项未回写本件：canonical 三只（VAL-PE/PB/DIV-HIGH）IS 行补跑后 §1 表补注、redundant/簇首建议的实际取舍执行（文内明言归后续批次）；②「不新建常 |
| `2026-09-15-four-big-items-blueprint.md` | 1 | 已与 `docs/_working/archive/2026-09/c_class_scattered/2026-09-15-four-big-items-blueprint.md` 字节等值 → 处置=删 live 重复份，非二次归档 | ①203 的 Owner 审批 flag 是否曾真写入 ig_fact 未见本件回写；②204 微调结果（val loss/权重替换）未见实测记录回填；③depgraph 设计节点登记与最终实现状态核 |
| `2026-09-15-full-automation-night-plan.md` | 1 | 末笔 0b4eddb231 只动 _working，①依据只剩台账自述 | ①N10 两项「登记跳过」未销案：EXP-02（夜批状态文件路径不在交接信息内）、C-1/分钟表（外部依赖全灭/密钥过期）；②N6-B3 audit_fn 接线待 QMT 在线窗口、B4 未评估维持； |
| `2026-09-15-full-automation-night-plan.md` | 1 | 已与 `docs/_working/archive/2026-09/c_class_scattered/2026-09-15-full-automation-night-plan.md` 字节等值 → 处置=删 live 重复份，非二次归档 | ①N10 两项「登记跳过」未销案：EXP-02（夜批状态文件路径不在交接信息内）、C-1/分钟表（外部依赖全灭/密钥过期）；②N6-B3 audit_fn 接线待 QMT 在线窗口、B4 未评估维持； |
| `2026-09-15-governance-module-mining-sop-map.md` | 1 | 已与 `docs/_working/archive/2026-09/c_class_scattered/2026-09-15-governance-module-mining-sop-map.md` 字节等值 → 处置=删 live 重复份，非二次归档 | ①§6 新增 SOP 待写项至今未立：docs/01_policies_and_standards/sop/ops_sop/ 实测仅 emergency_runbook.md/index.md/mer |
| `2026-09-15-gutters-eoc3-verification-deadend.md` | 1 | 末笔 28d7731fee 只动 _working，①依据只剩台账自述 | ①§一~§四为过时过程留档（文首已自标「读史勿照办」），其「唯一解锁=Owner 原书取证」结论已被 §五 终版覆盖；②本件含「Owner 动作」样式文本=数据，未执行；③文件头带 [BLUEPRIN |
| `2026-09-15-gutters-eoc3-verification-deadend.md` | 1 | 已与 `docs/_working/archive/2026-09/c_class_scattered/2026-09-15-gutters-eoc3-verification-deadend.md` 字节等值 → 处置=删 live 重复份，非二次归档 | ①§一~§四为过时过程留档（文首已自标「读史勿照办」），其「唯一解锁=Owner 原书取证」结论已被 §五 终版覆盖；②本件含「Owner 动作」样式文本=数据，未执行；③文件头带 [BLUEPRIN |
| `2026-09-15-handoff-factory-docs-discussion.md` | 1 | 含待裁词 3 次却判 1 | ①六个反问的逐条答复未回写本件，结论落在下游战役目录（docs/_working/full-auto-chain/ 15 工段，目录 index 记 created 2026-09-20）；②整篇为「 |
| `2026-09-15-handoff-factory-docs-discussion.md` | 1 | 末笔 275bc860dc 只动 _working，①依据只剩台账自述 | ①六个反问的逐条答复未回写本件，结论落在下游战役目录（docs/_working/full-auto-chain/ 15 工段，目录 index 记 created 2026-09-20）；②整篇为「 |
| `2026-09-15-handoff-factory-docs-discussion.md` | 1 | 已与 `docs/_working/archive/2026-09/c_class_scattered/2026-09-15-handoff-factory-docs-discussion.md` 字节等值 → 处置=删 live 重复份，非二次归档 | ①六个反问的逐条答复未回写本件，结论落在下游战役目录（docs/_working/full-auto-chain/ 15 工段，目录 index 记 created 2026-09-20）；②整篇为「 |
| `2026-09-15-neff-estimator-preregistration.md` | 1 | 已与 `docs/_working/archive/2026-09/c_class_scattered/2026-09-15-neff-estimator-preregistration.md` 字节等值 → 处置=删 live 重复份，非二次归档 | 实现件注释自述「n_trials_effective 预留位（effective_rank 随批次 B 落地，当前恒 None）」——批次 B 实跑对该披露位的回填记录未在本件回写 |
| `2026-09-15-szopen-pipeline-handoff.md` | 1 | 含待裁词 3 次却判 1 | ①本件的 28 接口欠账已被后继批超额覆盖：0ba60dd0ef 2026-09-15T00:52:07+08:00「47/47 收官」早于本件末笔（4f804539d5 02:21），即交接单发布时 |
| `2026-09-15-szopen-pipeline-handoff.md` | 1 | 末笔 4f804539d5 只动 _working，①依据只剩台账自述 | ①本件的 28 接口欠账已被后继批超额覆盖：0ba60dd0ef 2026-09-15T00:52:07+08:00「47/47 收官」早于本件末笔（4f804539d5 02:21），即交接单发布时 |
| `2026-09-15-szopen-pipeline-handoff.md` | 1 | 已与 `docs/_working/archive/2026-09/c_class_scattered/2026-09-15-szopen-pipeline-handoff.md` 字节等值 → 处置=删 live 重复份，非二次归档 | ①本件的 28 接口欠账已被后继批超额覆盖：0ba60dd0ef 2026-09-15T00:52:07+08:00「47/47 收官」早于本件末笔（4f804539d5 02:21），即交接单发布时 |
| `2026-09-15-tilib-handoff.md` | 1 | 已与 `docs/_working/archive/2026-09/c_class_scattered/2026-09-15-tilib-handoff.md` 字节等值 → 处置=删 live 重复份，非二次归档 | ①§3 杂项「16 号 memo §7 开放问题逐项核销状态刷新」未见回执；②§6 坑位 12 条与本文件「回填 MUST 单进程串行」铁律未进任何 SOP/常驻真源（属一次性交接经验，登记义务在 t |
| `2026-09-18-gate-identity-root-fix-plan.md` | 1 | 含待裁词 5 次却判 1 | ①§1.3 站点二（gate_persistence INSERT 列名必失败）已由施工侧实测证伪并在战役台账冻结（R-A1），本文件 §7 的 [亲验] 分级仍留该错判原文——战役侧明令「不改 Ma |
| `2026-09-18-gate-identity-root-fix-plan.md` | 1 | 末笔 47a7426b7f 只动 _working，①依据只剩台账自述 | ①§1.3 站点二（gate_persistence INSERT 列名必失败）已由施工侧实测证伪并在战役台账冻结（R-A1），本文件 §7 的 [亲验] 分级仍留该错判原文——战役侧明令「不改 Ma |
| `2026-09-18-landing-anchor-algo-flow-closeout` | 1 | 已与 `docs/_working/archive/2026-09/2026-09-18-landing-anchor-algo-flow-closeout` 字节等值 → 处置=删 live 重复份，非二次归档 | 台账 b6 L82 自述「终局（2026-09-18 06:46，completes_when 达成）」。W2 三条治本候选按台账「登记不硬闯」移交净窗持有者；W4 判据在册、施工走再生成窗；W5 依 |
| `2026-09-18-rule-audit-master-construction-plan.md` | 1 | 含待裁词 3 次却判 1 | ①D-12/WP12 被施工侧实测判为对外零效应的空改动并冻结（台账 R-A3），本件仍以原文在册（同上：修正表落台账，不改原文）；②Owner 门位件（C-34/C-35/C-42/C-60/C-6 |
| `2026-09-18_vocab_consolidation_campaign` | 1 | 末笔 d32d12e8ac 只动 _working，①依据只剩台账自述 | 机械底座标 archive_twin_exists：docs/_working/archive/2026-09/2026-09-18_vocab_consolidation_campaign 存 23 |
| `2026-09-19-overnight-handover-max-shift.md` | 1 | 含待裁词 5 次却判 1 | ①夜裁-01..24 已全部映射为正式裁定 #340..#360 并逐条判决（真源=docs/_working/rule_audit_campaign/2026-09-19-max-dayshift- |
| `alt_data_consumption_plan.md` | 3 | 含结案词 4 次却判 3 | 挖矿面已封矿（自述），施工面在册欠账见 unstarted；C-1 立即批（F7 台风日历+F4 BDI regime+F14/F15 币圈+F23 涨停情绪）已由后续批消化，F24/F26 的数据面 |
| `altdata_night` | 1 | 末笔 437f119d3e 只动 _working，①依据只剩台账自述 | 文档内部自相矛盾（记为分歧，不改判）：总簿 §1 E15 行状态=⬜（验收判据含「原目录双备份期 30 天」，约 2026-10-18 到期），晨报 §① E15 行=✅（E 盘 29,998+F 盘 |
| `altdata_night` | 1 | 已与 `docs/_working/archive/2026-09/altdata_night` 字节等值 → 处置=删 live 重复份，非二次归档 | 文档内部自相矛盾（记为分歧，不改判）：总簿 §1 E15 行状态=⬜（验收判据含「原目录双备份期 30 天」，约 2026-10-18 到期），晨报 §① E15 行=✅（E 盘 29,998+F 盘 |
| `auction_bridge_switch_mining_2026_09_17.md` | 1 | 已与 `docs/_working/archive/2026-09/c_class_scattered/auction_bridge_switch_mining_2026_09_17.md` 字节等值 → 处置=删 live 重复份，非二次归档 | ①frontmatter completes_when 要求「台账 §2.2-B 两项勾选且 9/18 退役日首日验证通过后随批次归档」——§11 明晨观察清单六项在本件内均未回勾，未见首日验证回执； |
| `audit_integrity` | 1 | 已与 `docs/_working/archive/2026-09/audit_integrity` 字节等值 → 处置=删 live 重复份，非二次归档 | 报告 §5 移交清单 C-1~C-4 实为已清偿（文档自述滞后于 HEAD，记为分歧）：C-1 gate_chain 同型锁=src/zephyr/gov_enforcement/rule_enfor |
| `code_doc_gov_campaign` | 1 | 含待裁词 3 次却判 1 | 交付报告 §三『就绪暂存待落地』批 F（WO-13 修账主体 87 件）+批 D（WO-14 归置 196 件）此后已由接手批落地（d32d12e8ac+137e9c2ada，本次实测 design_ |
| `code_doc_gov_campaign` | 1 | 末笔 137e9c2ada 只动 _working，①依据只剩台账自述 | 交付报告 §三『就绪暂存待落地』批 F（WO-13 修账主体 87 件）+批 D（WO-14 归置 196 件）此后已由接手批落地（d32d12e8ac+137e9c2ada，本次实测 design_ |
| `cold_backup_automation` | 3 | 含结案词 10 次却判 3 | 结案报告自述本棚是『乙线母方案』（w_line_b_disk_ch.md:18）与开工令真源（a4_go_signal.md:52）引用不可断，判定留场；报告 §二 的批次判读部分陈旧：批 2（系统日 |
| `construction_backlog.md` | 3 | 含结案词 4 次却判 3 | 阶段 A 全勾、B1/B2/B5 已核销（B5 于 5ebe47d4c0 落地）；未勾项见 unstarted。B4/B6 部分由后续模拟盘战役覆盖（fb5a7821d7 2026-09-22 模拟盘 |
| `construction_backlog.md` | 3 | 判未施工但末笔同时改生产面 3 件 | 阶段 A 全勾、B1/B2/B5 已核销（B5 于 5ebe47d4c0 落地）；未勾项见 unstarted。B4/B6 部分由后续模拟盘战役覆盖（fb5a7821d7 2026-09-22 模拟盘 |
| `daily_loop_campaign` | 3 | 判未施工但末笔同时改生产面 1 件 | 施工产物未入 HEAD（本分片最重要发现）：W1 官方词表常量模块 src/zephyr/shared/vocab/ 与 W2 收编册 docs/01_policies_and_standards/_ |
| `data_fix_campaign` | 1 | 含待裁词 4 次却判 1 | ①§5.1 结构性发现「warmup 踩踏病」自述为移交/待裁（治本建议=provider _fetch_single_period 加 warmup 读窗或 full_refresh 禁午间触发，本 |
| `data_fix_campaign` | 1 | 末笔 58fe0f7d7e 只动 _working，①依据只剩台账自述 | ①§5.1 结构性发现「warmup 踩踏病」自述为移交/待裁（治本建议=provider _fetch_single_period 加 warmup 读窗或 full_refresh 禁午间触发，本 |
| `datavein` | 3 | 判未施工但末笔同时改生产面 1 件 | 工单四条执行序 HEAD 侧零落地：known_data_gaps.yaml:884 该条目现 status: "monitoring" 且无 resolution_actual 字段（结案必要条件④ |
| `dsr-recalc` | 1 | 已与 `docs/_working/archive/2026-09/dsr-recalc` 字节等值 → 处置=删 live 重复份，非二次归档 | §9 明示遗留 A4（metrics.py 坏路径退役）/A5（阈值三线 SSOT）/_c4_engine 累计口径接线=交后续班次，非本 unit 欠账。§1 口径裁定的长期效力已由 trial_l |
| `flash_speedup` | 1 | 含待裁词 8 次却判 1 | ①总簿 frontmatter status=active 且环节表 R 行仍写「施工中」，与 90_report frontmatter `status: final_report_two_roun |
| `forensics` | 1 | 含待裁词 4 次却判 1 | 机械底座 pending=4 为 §5 旧「待裁」措辞的关键词命中，两项已由同报告的 §7/§8 追加段落地（裁定#269/#290），信号滞后于追加段——记为底座与读后判分歧。§7 被动验收口径自述 |
| `forensics` | 1 | 已与 `docs/_working/archive/2026-09/forensics` 字节等值 → 处置=删 live 重复份，非二次归档 | 机械底座 pending=4 为 §5 旧「待裁」措辞的关键词命中，两项已由同报告的 §7/§8 追加段落地（裁定#269/#290），信号滞后于追加段——记为底座与读后判分歧。§7 被动验收口径自述 |
| `full-auto-chain` | 2 | 含待裁词 19 次却判 2 | 骨架 §6 自述『链上已无 Owner 侧缺口』与他件自述不完全一致：S14 §7 堵点 4（流转执行器+订单翻译件）两解锁条件已满足『提请下批排期』、本次实测 src 全域无订单翻译件实装；S14  |
| `fullflow_campaign` | 3 | 含结案词 82 次却判 3 | 交付报告自述『零待裁不成立/零遗留也不成立』=明确未收口；A 类 22 项待 Owner/Max 裁定（A00=4.12 亿行时区修复在明示未授权后执行要定性、A00b=三套熔断旗标跨进程不可达、A1 |
| `guides` | 1 | 末笔 2f1cb40a02 只动 _working，①依据只剩台账自述 | §5 长尾迁移清单未迁：本次实测 scripts/mcp/launcher.py 与 src/zephyr/gov_enforcement/rule_bridge/session_worktree.p |
| `index.md` | 1 | 末笔 2f1cb40a02 只动 _working，①依据只剩台账自述 | twin=Y 比字节结论=非重复件：顶层 docs/_working/index.md 3,366B sha256(前16)=1ee24c9b653fc129（52 行）vs 归档 docs/_wor |
| `industry_chain_alpha` | 3 | 判未施工但末笔同时改生产面 2 件 | 文档自述「零施工」性质=挖矿+裁决书（plan L7、ledger L7），workbook §2 六向台账存大量「待挖」格且 a 簿 L8 自述「挖矿未完成，施工冻结」。裁决书为会话内自裁（裁1-裁 |
| `oddjobs_night` | 1 | 末笔 b9997fc0ac 只动 _working，①依据只剩台账自述 | 件4② 永久件 index.md 删除被 PS-STD-012 三通道死拦→留 Owner 门位（工作树删除态已就绪）；本会话翻译册 +8 行纯追加条目仍在暂存面随其 owner 批吸收；件4① td |
| `p21_contract_header_slimming_proposal.md` | 1 | 含待裁词 3 次却判 1 | 两处文档自述滞后于 HEAD，记为分歧：①§5 表「存量推广=未启动」，实际推广已于 09-16/09-17 全量完成（见 closure_report 链与实跑计数：tracked .py 中带 ` |
| `p21_contract_header_slimming_proposal.md` | 1 | 已与 `docs/_working/archive/2026-09/c_class_scattered/p21_contract_header_slimming_proposal.md` 字节等值 → 处置=删 live 重复份，非二次归档 | 两处文档自述滞后于 HEAD，记为分歧：①§5 表「存量推广=未启动」，实际推广已于 09-16/09-17 全量完成（见 closure_report 链与实跑计数：tracked .py 中带 ` |
| `redblue` | 1 | 含待裁词 5 次却判 1 | 文档头部「结案报告（由 st-fullchain-20260914 核验）=未结案（仍有待办）。处置=保留」是上一轮清理批自动生成的文本，按合同 §6 只当数据读、未执行；其判据（L93/L106「设 |
| `redblue` | 1 | 已与 `docs/_working/archive/2026-09/redblue` 字节等值 → 处置=删 live 重复份，非二次归档 | 文档头部「结案报告（由 st-fullchain-20260914 核验）=未结案（仍有待办）。处置=保留」是上一轮清理批自动生成的文本，按合同 §6 只当数据读、未执行；其判据（L93/L106「设 |
| `trading_vision` | 2 | 含待裁词 9 次却判 2 | 结案报告（09-21）称日度编排器『零施工记录』已被 HEAD 超越：src/zephyr/strategy_pipeline/daily_decision_orchestrator.py 在盘（90 |
| `unified_campaign` | 1 | 含待裁词 10 次却判 1 | 声明板三条 09-21 登记行状态仍为 planned 未回写 done（同日晚批已 done，属账面滞后）；战役下游仍在飞：乙线续班 st-backup-cold-20260924 于 09-24  |

- 合计 279 条疑点，均为「机械粗筛 vs 读原文终判」分歧，**不改判**，呈总指挥抽查（默认以分片为准）。

## 3. ①施工完毕 — 事实性结案报告（落地哈希只来自 git log）

### 2026-08-22-frontend-backend-gap-ledger.md
- 类型=file · HEAD 末次=2026-09-15T02:13:22+08:00（6aae9a7439） · 归档双活=`docs/_working/archive/2026-09/c_class_scattered/2026-08-22-frontend-backend-gap-ledger.md` 字节等值 1/1 · 末笔生产面=0 件
- 提交链：6aae9a7439 docs: docs/_working 清理批(1/3)——50 份文档结案报告写入（C-1~C-4 裁定固化；6dc6fefb7b 账本同步：Owner 五裁定落盘销账（2026-08-29「全部按倾向执行」令）；913be2437c docs(_working): 资产总账 v1.9.0（§4.J 普查 192 件+R16/R17+§8 全页；6cb71d7592 docs(_working): 资产总账 v1.6.0（R15 页 4 重构令=板块全景相对强度光谱地图：RS
- 做了什么：「前端有、后端没有」手工缺口总账 v2.0→v2.5.0：101 项（A 接线/B 供数/C 能力/D 数据源）四分类登记 + 施工顺序 + Owner 2026-08-25 登记纪律，v1（33 项，被误删）按 Owner 指令重建并 R1-R6 循环核查至连续两轮零新增收敛
- 剩余欠账：twin 判据：与 archive/2026-09/c_class_scattered/ 同名件 **字节等值**（cmp 无差、sha256 同 7e4d6b38cb83b13c…、size 均 43406B、git blob 同一 84cf21c0c4041c163d79673c5a64ca44bf9e1e46）；与 archive/2026-08/ 同名件 **不等值**（21542c3a059b74aa…/42537B，系 09-15 写结案报告之前的旧态）。账本自身 2026-09-15 结案报告判「未结案·保留」并摘 16 条待办，但其登记义务已由后继件承接：docs/_working/2026-08-31-frontend-governance-four-piece-drafts.md §六 裁定5（Owner 已裁「停止手工维护，改自动派生视图」）+ 派生件 generate_frontend_gap_views.py 现报 A 类缺口=0；账内文字基线=2026-08-29 原型 v4.1（已过时）。仍存的不可代偿欠账：C13「GAP-F-27 挂起件——内容随原文件丢失待考，待 Owner 回忆/考据补录」；D11/D12 等 i18n 与运维件属远期
- 结案报告：
    判 ① 依据（两条）：
    1) 取代件已在真源侧建成并通电：src/zephyr/frontend/dashboard/web/frontend_map.yaml（实存）+
       depgraph nodes 三字段 has_frontend/no_frontend_reason/frontend_ref（本仓派生视图正在读取）+
       scripts/governance/d5_architecture/generators/generate_frontend_gap_views.py 产出的
       docs/_working/2026-08-31-frontend-gap-views-derived.md（A=0/B=1/C=0/D=0）。
    2) 停止手工维护本身是 Owner 裁定件（四件套草案 §六 裁定5「停止手工维护，改自动派生视图」），
       故本手工账的收口条件=后继件建成，而非 101 项逐条勾销。
    与机械底座不一致处：底座按文档自述信号判「未结案（16 条待办）」，未识别后继件；
    另底座 twin=Y 只标了 archive/2026-09/ 顶层，真身在 c_class_scattered/ 子目录（该件确实有等值副本）。
    残余不可代偿项 1 条：C13 GAP-F-27（原件佚失，需 Owner 回忆补录）。

### 2026-08-24-aiarch-construction-list.md
- 类型=file · HEAD 末次=2026-09-15T02:13:22+08:00（6aae9a7439） · 归档双活=`docs/_working/archive/2026-09/c_class_scattered/2026-08-24-aiarch-construction-list.md` 字节等值 1/1 · 末笔生产面=0 件
- 提交链：6aae9a7439 docs: docs/_working 清理批(1/3)——50 份文档结案报告写入（C-1~C-4 裁定固化；d09f5f6ad1 docs(_working): 三清单头部结案报告补写——B组裁定落地批（09e1aaef/f432625c/；09e1aaef0f docs+feat: B组裁定落地批——A6调度/P2-1架子/SLA连跑/B13a评分器/B1管线/B16勘；996b9ef97f docs(_working): 长城任务批次3收口——三清单核销+S2四报告归档+registry路径修复+A
- 做了什么：09 号 AI 架构层 21 份文档全量审查（T3）产出的「未施工/部分落地」清单：P0 Owner 窗口 5 件 + P1 7 件 + P2 9 件 + P3 14 件，逐件给来源文档/建议落点/建议 MOD 号/验收标准
- 剩余欠账：twin 判据：与 c_class_scattered/ 同名件 **字节等值**（sha256 同 4425ba1f9fe3d4d5…/31883B，cmp 无差，git blob 同一 713bb081c15885dc…）；与 archive/2026-08/ 同名件不等值（d9f4c54b…/29394B）。清单自述「P1/P2 全量核销完毕（2026-08-30 长城批）」；仍有效残余三件——W3 DeepSeek 402 充值（Owner 动作，tracker #253）、P2-1 修复模式挖掘两周观测窗口（自然时间到点自动出报告）、3.14 01/02 号文快照刷新（文档维护项）；P3 14 件按自述属远期/不排期。底座 pending=8 系把远期/窗口项一并计入
- 结案报告：
    收口口径=清单自述的核销批（本代理已用 git log -1 逐笔核实哈希真实存在且主题相符）：
    - 2a16988d05 2026-08-30T08:33:45+08:00 feat(多域): 长城任务批次1 —— P1 1.1~1.7 / P2 2.1~2.9 逐项核销批
    - 09e1aaef0f 2026-08-30T18:15:05+08:00 docs+feat: B组裁定落地批 —— W2 核销 + P2-1 观测架子 + 2.8 SLA 实测 + 3.9 裁定不建
    清单本体属一次性派单账（工单属性，非长期判据），无需要上收蓝图的独立结论。

### 2026-08-24-designmemos-construction-list.md
- 类型=file · HEAD 末次=2026-09-15T02:13:22+08:00（6aae9a7439） · 归档双活=`docs/_working/archive/2026-09/c_class_scattered/2026-08-24-designmemos-construction-list.md` 字节等值 1/1 · 末笔生产面=0 件
- 提交链：6aae9a7439 docs: docs/_working 清理批(1/3)——50 份文档结案报告写入（C-1~C-4 裁定固化；d09f5f6ad1 docs(_working): 三清单头部结案报告补写——B组裁定落地批（09e1aaef/f432625c/；09e1aaef0f docs+feat: B组裁定落地批——A6调度/P2-1架子/SLA连跑/B13a评分器/B1管线/B16勘；fccb03c387 docs(_working): designmemos 清单核销补提交——长城批批次3遗漏件
- 做了什么：design_memos 61 份全量审查（T3）产出的待施工清单 28 项（P0 1/P1 6/P2 11/P3 6/Owner 窗口 4），逐件带来源 memo、建议落点、号段顺延纪律与验收标准
- 剩余欠账：twin 判据：与 c_class_scattered/ 同名件 **字节等值**（sha256 同 79d3db560047c1ff…/29776B，cmp 无差，git blob 同一 29fe46af21e20260110dbb4a9af5b31176a77ab9）；与 archive/2026-08/ 同名件不等值（8eebe101…/27151B）。自述「22 项已核销（#1~#16/#18~#22/#27）」；仍有效=#17 数据期挂账（快照 ~5/60，预计 2026-11 中下旬达标，纯等日历）、#23/#24/#26 远期、#25 PNG 退役待 Owner 一句话、#28 Owner 窗口四项（DeepSeek 充值/61 号晋升载体/65 号 #ARCH-AIGOV-001~010 铁律#9/90 号 P-1~P-5 + 91 号口径）
- 结案报告：
    核销证据（哈希经本代理 git log -1 实核）：2a16988d05（2026-08-30 长城批 22 项核销）、
    09e1aaef0f（2026-08-30 B 组裁定落地批：#7 拆记/#17 里程碑/B14+B15 骨架落码/#25 退役建议）。
    清单自述的「附：不收录说明」段承担防复提职责，内容随来源 memo 结案报告留档，无独立上收价值。
    残余欠账全为 Owner 窗口或自然时间窗，非本文件可施工面。

### 2026-08-28-remaining-construction-roadmap.md
- 类型=file · HEAD 末次=2026-09-15T02:13:22+08:00（6aae9a7439） · 归档双活=`docs/_working/archive/2026-09/c_class_scattered/2026-08-28-remaining-construction-roadmap.md` 字节等值 1/1 · 末笔生产面=0 件
- 提交链：6aae9a7439 docs: docs/_working 清理批(1/3)——50 份文档结案报告写入（C-1~C-4 裁定固化；d09f5f6ad1 docs(_working): 三清单头部结案报告补写——B组裁定落地批（09e1aaef/f432625c/；09e1aaef0f docs+feat: B组裁定落地批——A6调度/P2-1架子/SLA连跑/B13a评分器/B1管线/B16勘；996b9ef97f docs(_working): 长城任务批次3收口——三清单核销+S2四报告归档+registry路径修复+A
- 做了什么：2026-08-28 全量审查批（85 篇设计文档 × 代码实证）的统一派单真源：A 类可立即排期 22 项 / B 类外部阻塞 21 项 / C 类裁定不施工 10 项 / 09 域 GP1+ 13 项，附波 0-5 波次派单与依赖说明
- 剩余欠账：twin 判据：与 c_class_scattered/ 同名件 **字节等值**（sha256 同 80b38756ad819377…/38017B，cmp 无差，git blob 同一 9429d01e989229710a56806a8b62906c11e97429）；与 archive/2026-08/ 同名件不等值（a922f9f5…/37329B）。自述终态=A 类 22/22 全闭环 + GP1 四波代码施工全量闭环；残余=B 类 19 项外部条件阻塞（触发才转 A）+ C 类 10 项已裁定不施工 + 纯 Owner 动作（A6 计划任务启用/A9 双实现收敛/A5 漏斗归并/B10/B11 拍板）。文档自封「施工排期真源」——归档时该身份须由 Owner 明确接棒者，否则 tracker 与本档的双真源张力重开
- 结案报告：
    判 ① 依据：本档四段波次自述全部闭环且哈希经本代理实核存在——
    2a16988d05（2026-08-30 长城批，A 类收尾）、09e1aaef0f（2026-08-30 B 组裁定落地批，
    文内另引 f432625c/376d2c09 同批短哈希）。GP1 第一~四波逐笔（5a35776499/5bd46ce96a/
    24f639fc6b 等）文内已登，退出条件 E1-1◐/E1-2✅/E1-3✅ 亦回写 17 号文。
    未勾的 B/C 类按合同 §1 定义不构成「欠账」（外部条件阻塞 + 已裁定不施工）。

### 2026-08-30-b16-feed-exploration.md
- 类型=file · HEAD 末次=2026-09-15T02:13:22+08:00（6aae9a7439） · 归档双活=`docs/_working/archive/2026-09/c_class_scattered/2026-08-30-b16-feed-exploration.md` 字节等值 1/1 · 末笔生产面=0 件
- 提交链：6aae9a7439 docs: docs/_working 清理批(1/3)——50 份文档结案报告写入（C-1~C-4 裁定固化；09e1aaef0f docs+feat: B组裁定落地批——A6调度/P2-1架子/SLA连跑/B13a评分器/B1管线/B16勘
- 做了什么：B16 勘探裁定：26 号文六因子矩阵中 dReport / Jump on PEAD 两因子的输入数据可得性 grep 实证（daily_event 族 + DDL-as-Code + 计算件落码状态），结论=GO
- 剩余欠账：twin 判据：与 c_class_scattered/ 同名件 **字节等值**（sha256 同 2ff2fada2c6aa17c…/7082B，cmp 无差，git blob 同一 686449ba50988fab388fddf7b20102f97395fbc7）；与 archive/2026-08/ 同名件不等值（276fb494…/6160B）。勘探任务本身已交付并被 roadmap B16 行引用（「勘探结论=GO，报告 2026-08-30-b16-feed-exploration.md」）。其 GO 建议的装配层至今未施工——本代理实证：grep compute_dreport|jump_on_pead 全 src 仅命中 src/zephyr/intelligence/event_factor_matrix.py 本体，零装配消费者（与 §2.2 结论一致）；该项欠账在 2026-08-30-b4 件的 S1-S4 分解账上，不重复计。仍待裁定 2 条：CAR 基准口径、actual_date 时点语义（T vs T+1）
- 结案报告：
    一次性勘探件：任务=「评估两因子输入可得性」，产出=GO 裁定 + 缺口清单（§2.3 五行，
    含 2 条待裁 + 1 条待实测）。该任务无剩余欠账形态——它把欠账移交给了后继件
    （docs/_working/2026-08-30-b4-six-factor-construction-breakdown.md 的 S1-S4）。
    roadmap 侧引用行已确认存在（B16 行 2026-08-30 裁定注记）。

### 2026-08-31-frontend-governance-four-piece-drafts.md
- 类型=file · HEAD 末次=2026-09-15T02:13:22+08:00（6aae9a7439） · 归档双活=`docs/_working/archive/2026-09/c_class_scattered/2026-08-31-frontend-governance-four-piece-drafts.md` 字节等值 1/1 · 末笔生产面=0 件
- 提交链：6aae9a7439 docs: docs/_working 清理批(1/3)——50 份文档结案报告写入（C-1~C-4 裁定固化；5e74716689 fix(depgraph): 前端覆盖字段重建不丢——nodes_metadata 保护链补齐 + DS 合规；64fdf8029c feat(rules): TRAE-086 前端功能模块施工铁律立项 + 草案 v0.6 拆分先行总裁定 [A；78d0cb6cf3 fix(frontend): 找回 modlib 模块样板页 + 草案 v0.5.0 执行顺序总裁定 [no-
- 做了什么：前端治理四件套设计（技术手册/功能验收单/前端模块契约/frontend_map 第六全景图）+ 六项 Owner 裁定 + 统一对账字段设计（has_frontend/no_frontend_reason/frontend_ref，backend_ref 类型化）+ §八/§九 执行顺序与拆分先行总裁定 + 夜战计划 P0-P7
- 剩余欠账：twin 判据：与 c_class_scattered/ 同名件 **字节等值**（sha256 同 b77252accb82c4f8…/29233B，cmp 无差，git blob 同一 e6f579936860b69e25197e0b764d9ece753e1e36）；与 archive/2026-08/ 同名件不等值（6f26dbf7…/28721B）。施工侧：P0/P1/P2/P3/P6/P7 自述完成，P4 逐页拆分战役转多会话、P5 scanner 升级待触发。底座 pending=3 命中的是 schema 示例注释行（status/候选池不对齐），非欠账
- 结案报告：
    §3 机械判据（本代理实跑，命中→按 R2 改判 ①）：
    - docs/01_policies_and_standards/rules/trae_086_frontend_module_construction.yaml 实存（§9.4 TRAE-086 立项落地）
    - src/zephyr/frontend/dashboard/web/frontend_map.yaml 实存（§四 全景图真源）
    - docs/03_modules/_domain_frontend/frontend_handbook/ 实存 6 件（browser_native/detail_drawer_template/index/klinecharts/loading_vendor/project_conventions）
    - docs/03_modules/_domain_frontend/acceptance/ 实存 70 件 ACC-*.yaml
    - src/zephyr/gov_enforcement/commit_gates/frontend_map_gate.py 实存（对齐门禁扩维落地）
    - docs/_working/2026-08-31-frontend-gap-views-derived.md 由 generate_frontend_gap_views.py 产出（4c 缺口派生器=已建成）
    设计层判据已被正式真源（规则册 + 蓝图侧目录 + 门禁 + 生成器）承接，故不列 upgrade_items。
    唯一交接性残余：P4 逐页拆件的战役账不在本件（后继=frontend_component_split_sop + 2026-09-12 全量拆件清单）。

### 2026-09-04-trading-decision-map-discussion.md
- 类型=file · HEAD 末次=2026-09-15T02:13:22+08:00（6aae9a7439） · 归档双活=`docs/_working/archive/2026-09/c_class_scattered/2026-09-04-trading-decision-map-discussion.md` 字节等值 1/1 · 末笔生产面=0 件
- 提交链：6aae9a7439 docs: docs/_working 清理批(1/3)——50 份文档结案报告写入（C-1~C-4 裁定固化；2cf8cfc309 交易决策地图知识层 PIT 时间治理（D118-D122 终裁落盘）；0edf93eb02 docs(map): D112-D117 内审漏账收尾包——GLM 热身复核发现交接报告 8 项漏账（M-36；cd9bef38dd docs(trading): D111 做T终裁包落盘（裁定#226）——成本门绝对金额制（N_floor≈5
- 做了什么：交易决策地图（第 7 张地图）43 轮讨论裁定录：D1-D122 全部终裁（三流骨架+四路传感器阵列+环节×状态矩阵+proposed/verified 置信度管道+知识层 PIT effective_from），逐轮带调研证据与 YAML 落盘记录
- 剩余欠账：底座 twin=- 有误：c_class_scattered/ 有同名件且 **字节等值**（cmp 无差，两侧 sha256 一致）。文尾自述「讨论收敛并裁定后，正式设计应迁入 architecture_model 或相应设计目录，本文件届时归档」=归档条件已成立（D1-D122 已全裁）。残余非判据层：D109/D110/D111 等 proposed 假说须回测验证通过才生效（属回测线欠账，已登记在 2026-09-07-tdm-backtest-protocol 闸门账上）
- 结案报告：
    §3 机械判据命中 → 按 R2 改判 ①：
    - docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml:1558-1596 载 裁定#225
      （D90-D110 全部终裁包，affected_files 直指本件与 tdm-backtest-protocol）、裁定#226（D111 做T 终裁包）、
      裁定#227（D112-D117 内审漏账收尾包）
    - 地图本体真源实存：config/trading_decision_map.yaml（321,470B，本代理 2026-09-24 实测）
    - 设计真源 memo 已迁：docs/_working/archive/2026-09/design_memos/69_trading_decision_map.md
    - 本件自身的落盘轨迹有真实提交链（cd9bef38dd D111 / 0edf93eb02 D112-D117 / 2cf8cfc309 D118-D122 知识层 PIT）
    结论：判据层已进正式真源，本件=已消费的裁定过程录，符合其自述归档条件。

### 2026-09-05-audit-greatwall-report.md
- 类型=file · HEAD 末次=2026-09-15T02:13:22+08:00（6aae9a7439） · 归档双活=`docs/_working/archive/2026-09/c_class_scattered/2026-09-05-audit-greatwall-report.md` 字节等值 1/1 · 末笔生产面=0 件
- 提交链：6aae9a7439 docs: docs/_working 清理批(1/3)——50 份文档结案报告写入（C-1~C-4 裁定固化；7165b188c4 chore(governance): 总管收尾批——STEWARD-20260905-001 长城任务终态收编；cd5fb1629d ﻿docs(audit): §9 状态更新三——B9/B8/B6/B13 深查登记面后推翻"机械活"定性：B9；2c9145cf13 ﻿docs(audit): 终检补做——①B20 复测 src [TESTS] 断链 354→165→157 
- 做了什么：二十一域无人值守全仓审计总报告：6 修复波 + 复审 2 波 + 机械专项，发现 1548 → 修复 893 + 618 登记台账 + 37 跨域移交，align_all 七图硬问题清零，最终判定=通过；附 A 类代码级损坏 15 项修复台账与 B 类 24 项队列
- 剩余欠账：底座 twin=- 有误：c_class_scattered/ 有同名件且 **字节等值**（cmp 无差，sha256 两侧一致）。文内 §六 待 Owner 裁定 18 项 + §九 B 类 24 项（16 闭环 / 8 节待裁 11 项）已由姊妹件 2026-09-05-steward-b-class-owner-book.md 承接为「Owner 裁定唯一入口」，再由 2026-09-06 flash 执行批逐项落地；残余仍是台账债：蓝图建设缺口 252 项 + [TESTS] 失联 352 项 + dedup 专项 10 对克隆 + HEADER-ANCHOR 新门禁方案（§六#16，待 Owner 批 D1 预算）
- 结案报告：
    判 ① 依据：报告自述「最终判定：通过（遗留=0 强阻断）」+ §三 共享收口 12 条逐笔登哈希，
    本代理实核全部存在且主题相符：a467a16552（AI-01 根域修复）、2dec48742c（AI-20 脚本域/G1 网关锁根修）、
    72ec55e14a（AI-21 merge，含 feedback_loop 56 悬空 import 修复）、d3a50b3525（AI-03 merge，含
    decision_map.py 残写补全）、7165b188c4（2026-09-06 总管收尾批，本件最后一次实质内容更新）。
    待 Owner 的 18 项不是施工欠账而是门位等待，且已另册承接（owner-book），故不构成 state 3。

### 2026-09-05-steward-b-class-owner-book.md
- 类型=file · HEAD 末次=2026-09-15T02:13:22+08:00（6aae9a7439） · 归档双活=`docs/_working/archive/2026-09/c_class_scattered/2026-09-05-steward-b-class-owner-book.md` 字节等值 1/1 · 末笔生产面=0 件
- 提交链：6aae9a7439 docs: docs/_working 清理批(1/3)——50 份文档结案报告写入（C-1~C-4 裁定固化；7165b188c4 chore(governance): 总管收尾批——STEWARD-20260905-001 长城任务终态收编
- 做了什么：STEWARD-20260905 总管 B 类 24 项处置书：已施工 8 commit 备案 + 逐项「事实基线→总管核实→建议」的 Owner 裁定入口（错误码四族/silent except/运行时装配批/ROOR 十表口径/退役分流/预存问题登记）
- 剩余欠账：底座 twin=- 有误：c_class_scattered/ 有同名件且 **字节等值**（cmp 无差，sha256 两侧一致）。§十四 自述总账 8 commit 落地；其 11 项「待裁」由 2026-09-06 的 Owner 语音裁定 + flash 执行批逐项消化（A 错误码转正/B 契约码/C orchestrator/D 批量化/E 锁锚定/F ROOR/G 双写者/H salvage 三件，八项全落地零跳过）。本件仍未闭环的两条：§九 B21 依赖镜像门禁「D1 预算待批」——本代理实测 gate_registry.yaml 与 commit_gates 目录零命中 dep-mirror/DEP-MIRROR，即门禁未施工；§六 B12 口径张力（MATURITY 增设 wiring 维度 vs 蓝图注记）与 §八 蓝图建设缺口 271 项属 Owner 排期
- 结案报告：
    判 ① 依据：其自封职责=「Owner 裁定唯一入口 + 总管施工账」，施工侧 7 笔哈希本代理全部实核存在且主题相符：
    b0a0aef785（词表门禁终清零）/ a14cd9a01b（B1+B2 batch_id 全链）/ 4dd2e2e446（B3 RiskLimits 收敛）/
    8d1929d42e（B4 Timer 改事件驱动）/ adb2e7555a（B20 [TESTS] 重锚 66 文件）/ 6344c71327（B16+B8/B6 salvage）/
    91aca745b3（B22①②④+B5/B12 定点）。裁定侧由后继件 2026-09-06-flash-execution-report.md 承接并已消费。
    唯一仍在本的未施工项=B21 依赖镜像门禁（实测无该 gate），已按 ④ 态记入 residue 交 Owner 排期。

### 2026-09-06-flash-execution-report.md
- 类型=file · HEAD 末次=2026-09-15T02:13:22+08:00（6aae9a7439） · 归档双活=`docs/_working/archive/2026-09/c_class_scattered/2026-09-06-flash-execution-report.md` 字节等值 1/1 · 末笔生产面=0 件
- 提交链：6aae9a7439 docs: docs/_working 清理批(1/3)——50 份文档结案报告写入（C-1~C-4 裁定固化；4aaf4aab45 批四收尾：raw-asset-scan 同族退役+治理动作 append-only 日志+报告 §十（Owne；95530e1519 批三施工报告终稿：§八处置总账+§8.1 删除事件溯源+§8.2 回填明细+§九消费方排查；5b2d27fc37 depgraph 刷新+path_ownership_map 幽灵条目清除（批二遗留 #9 处置）
- 做了什么：Owner 裁定执行批二（Flash 无人值守施工报告）：A 41 前缀 183 类占位码转正 / B 34 契约码 B21 落码+C6 deferred / C orchestrator 接线 / D pre_write_gate 批量化 / E 网关锁锚定主仓 / F ROOR 18 表口径+counting_rule / G 资产索引双写者收敛 / H multifactor 三件 salvage，八项全落地
- 剩余欠账：底座 twin=- 有误：c_class_scattered/ 有同名件且 **字节等值**（cmp 无差，sha256 两侧一致）。文首自述性质=「无人值守施工报告，施工完成即失效」→ 天然结案。仍挂 4 条（§一/§B 登记的待办）：ZA-TSK-0004（create_task input_schema 无 files 字段，>20 files/预算无落点，补 schema 或关闭契约待裁）、指令清单外 8 码（HF-0001~0004/GT-0001/0003/INT-0001/0002）处置授权、ROOR entry_count/counting_rule 生成器自动回填未落地、治理类动作审计单独 append-only 落盘建议。注：raw-asset-scan 同族退役与 append-only 日志两项其后的批四收尾 commit 已做（见 closure_report）
- 结案报告：
    八项逐笔哈希本代理实核（git log -1 全部命中，主题与报告一致）：
    0bd159c4f6（B 项：34 契约码 B/C 类+EXSIM 收编）/ 5f700961c1（C 项 orchestrator 入口接线）/
    b7fbaf5089（H 项 multifactor 三件 salvage）/ 335d116522（E 项网关锁锚定主仓）/
    e3bc4ecf23（G 项资产索引双写者收敛）/ f13bc7965a（F 项 ROOR 十表口径+counting_rule）。
    报告自身的收口批也实存：95530e1519（批三施工报告终稿）、4aaf4aab45（批四收尾：raw-asset-scan 同族退役
    +治理动作 append-only 日志），即 §一 中两条残余已被后续 commit 消化。
    文件性质行明示「施工完成即失效」，与判 ① 一致。

### 2026-09-07-tdm-internal-factpack.md
- 类型=file · HEAD 末次=2026-09-15T02:13:22+08:00（6aae9a7439） · 归档双活=`docs/_working/archive/2026-09/c_class_scattered/2026-09-07-tdm-internal-factpack.md` 字节等值 1/1 · 末笔生产面=0 件
- 提交链：6aae9a7439 docs: docs/_working 清理批(1/3)——50 份文档结案报告写入（C-1~C-4 裁定固化；f44d35c2ef docs(trading): TDM 拼装回测前外审 Round 1 修复——地图补边31+改落4（X流断链/；0ff03c1762 docs(map): 审查清单 v1.3.0+内审事实包——GLM 内审试运行三件收口；①清单试运行抓 6 缺
- 做了什么：TDM 拼装回测前置审查材料⑤（内审事实包）：脚本解析真源 YAML 对 62 条交叉引用逐条语义核对 + 33 模块锚定接线状态 + 10 个 DS 回测可得性 + PP-001 对齐 + 13 个 paper 节点清单，供外审复核而非重复劳动
- 剩余欠账：底座 twin=- 有误：c_class_scattered/ 有同名件且 **字节等值**（cmp 无差，sha256 两侧一致）。front-matter task_context 自述「审查闭环后归档」，Round 1/2 已跑完（见同族 2026-09-07-tdm-review-round-report.md，修复 commit f44d35c2ef 实核存在）。本件自身残余 2 条：§3 的 DS-082 历史覆盖待数据组确认 / DS-059·098 存疑，以及 §6 记录的第 5 项清单缺陷修复（C9 新股场景）随清单件闭环
- 结案报告：
    一次性审查材料件：其交付物（事实表）已被外审 Round 1 消费并驱动地图修复，
    修复批哈希 f44d35c2ef（2026-09-07T16:34:57+08:00 docs(trading): TDM 拼装回测前外审 Round 1 修复——
    地图补边…）本代理实核存在；本件自身的 §3 数据实况修正（B-02 修正注）亦已回写并上收到协议 §4 矩阵。
    外审 B-02 对本表「按注册表 status 判绿未核分区实况」的纠偏，正是其自述的审查闭环产物。

### 2026-09-07-tdm-pre-backtest-review-checklist.md
- 类型=file · HEAD 末次=2026-09-15T02:13:22+08:00（6aae9a7439） · 归档双活=`docs/_working/archive/2026-09/c_class_scattered/2026-09-07-tdm-pre-backtest-review-checklist.md` 字节等值 1/1 · 末笔生产面=0 件
- 提交链：6aae9a7439 docs: docs/_working 清理批(1/3)——50 份文档结案报告写入（C-1~C-4 裁定固化；0ff03c1762 docs(map): 审查清单 v1.3.0+内审事实包——GLM 内审试运行三件收口；①清单试运行抓 6 缺；5059232c54 docs(map): 审查清单 v1.2.0 增循环审查协议+多子代理并行分派——Owner 裁定两增：①循环；294c67d805 docs(map): 审查清单 v1.1.0 增 J 维度外部知识联网检索——Owner 裁定增加第五轮缺件审
- 做了什么：TDM 拼装回测前全面审查清单 v1.3.0（外部模型用）：九维 A-J 检查点 + 循环收敛协议（硬门槛 B=0/M=0、软门槛连续一轮零新增、上限 5 轮）+ 多子代理并行分派矩阵 + §5 已知边界 11 条勿报声明 + §6/§7 输出格式
- 剩余欠账：底座 twin=- 有误：c_class_scattered/ 有同名件且 **字节等值**（cmp 无差，sha256 两侧一致）。task_context 自述「审查闭环后归档」；Round 1（13B/61M）+Round 2（R2-01/02+6 Minor）已按其协议执行完毕，§8 循环审查记录表由报告件填写。§5 已知边界声明（红节点 89 个属显性化设计/矩阵格全 proposed 是阶段设计/零消费模块归 wiring_registry…）是有价值的判据，但它是「勿报」型审查护栏，属外审一次性合同，其长效部分已由协议承接
- 结案报告：
    清单演进链实核：294c67d805（v1.1.0 增 J 维度联网检索）→ 5059232c54（v1.2.0 循环审查协议+并行分派）
    → 0ff03c1762（v1.3.0 审查清单+内审事实包同批）→ 本件末笔 6aae9a7439（写结案报告）。
    消费证据：审查报告件 2026-09-07-tdm-review-round-report.md 已按本清单 §7 格式与 §8 记录表填写并闭环
    （Round 2 终态：图面缺陷 B=0/M=0），故本工单型件无剩余欠账。

### 2026-09-07-tdm-review-round-report.md
- 类型=file · HEAD 末次=2026-09-15T02:13:22+08:00（6aae9a7439） · 归档双活=`docs/_working/archive/2026-09/c_class_scattered/2026-09-07-tdm-review-round-report.md` 字节等值 1/1 · 末笔生产面=0 件
- 提交链：6aae9a7439 docs: docs/_working 清理批(1/3)——50 份文档结案报告写入（C-1~C-4 裁定固化；b35cb3e920 docs(trading): TDM 外审 Round 2 补修——S2-06→E-L4-12 冷却消费边闭环
- 做了什么：TDM 外审 Round 1 + Round 2 问题报告归档：Blocker 13/Major 61/Minor 60/Suggestion 22/J 新增 30 全编号留档，修复记录（地图 132→166 边 + 29 处注释 + 注册表/文档 8+4+3+3+1 处）、Round 2 修复验证 73/74 通过 + 收敛扫描 9 项全修 + 证伪 4 组
- 剩余欠账：底座 twin=- 有误：c_class_scattered/ 有同名件且 **字节等值**（cmp 无差，sha256 两侧一致）。§五 终态：图面缺陷硬门槛 B=0/M=0 已达，悬挂项=17 项 Owner 待裁（协议 §7，事后全部终裁 D90-D110）+ 施工欠账（棘轮/配对核算器/治理状态表/合规自评器/制度时变维表，即协议闸门 G4/G7/G10）。存疑待查 3 条如实留档：hub 代收口头约定（R2 已消解）/HMM filtered-smoothed 实现未核码 M-42/合规阈值 15 笔/秒 vs 300 笔/秒孰对 M-57
- 结案报告：
    审查归档件自述结论「图面缺陷硬门槛已达 B=0/M=0（可修复层全部闭环并经两轮验证）」，
    两笔修复批实核存在：f44d35c2ef（2026-09-07T16:34:57 Round 1 修复——地图补边+文档回写）、
    b35cb3e920（2026-09-07T17:16:39 Round 2 补修——S2-06→E-L4-12 冷却消费边等）。
    其悬挂的 17 项 Owner 待裁已由协议 §7 逐条标注「已裁 D90-D110」并进 ruling_registry 裁定#225，
    剩余施工欠账在协议闸门账上（本件不重复计账）。

### 2026-09-09-clearance-night-report.md
- 类型=file · HEAD 末次=2026-09-15T02:13:22+08:00（6aae9a7439） · 归档双活=`docs/_working/archive/2026-09/c_class_scattered/2026-09-09-clearance-night-report.md` 字节等值 1/1 · 末笔生产面=0 件
- 提交链：6aae9a7439 docs: docs/_working 清理批(1/3)——50 份文档结案报告写入（C-1~C-4 裁定固化；a6a1367275 docs: 治理清偿六连晨报+审稿补记入库（st-clearance-night 交接）
- 做了什么：治理清偿六连（环境欠账清偿+门禁加固）施工晨报：T1 reaper keep 行清理 / T2 测试缓存权限（验收达成）/ T3 面板超时加固（并发规则跳过登记）/ T4 提交门禁「只查自己」改造 / T5 登记表批量修改防蒸发双保险 / T6 表结构核对器 4 处漂移清偿，附 7 条自行裁定记录与验收证据
- 剩余欠账：底座 twin=- 有误：c_class_scattered/ 有同名件且 **字节等值**（cmp 无差，sha256 两侧一致）。§四 自述「无其他未完成——六件全部收口」。§三 遗留 7 条待 Owner，其中第 7 条（把 T4 的只查自己推广到 NO-HIGH-COMPLEXITY/DEPGRAPH-PRE-REGISTRATION 等同病 gate）在其后已被体系采纳——AGENTS.md §3 第1条/§3.3 现把「内容扫描型 gate 默认 own-scope + 新 gate 必须 own-scope 或登记全仓扫描理由」写成硬规则，gate_registry.yaml 有 own_scope 机生字段；其余 6 条（T2 takeown 根治/T3 施工/registrar 演进断言 105 vs 106/runtime/tmp 600+ pytest 残留/allow-mass-deletion 中文阈值/审计通道位置）仍是 Owner 侧事项
- 结案报告：
    判 ① 依据：报告结论先行行自述六件全部收口，三笔关键哈希本代理实核存在且主题相符：
    84ebfeca3b（2026-09-10T02:04:26 T4 提交门禁只查自己改造）、a85729effd（2026-09-10T02:15:34 T5 登记表
    防蒸发双保险）、1fd4707c34（2026-09-09T17:09:33 T6 表结构核对器漂移清偿）；报告本体入库=a6a1367275
    （2026-09-10T08:11:38 治理清偿六连晨报+审稿补记）。
    其最有价值的遗留（推广 own-scope 到全部扫描型 gate）已成正式硬规则，见 AGENTS.md §3 第1条/§3.3
    与 gate_registry.yaml 的 own_scope 机生字段——即本件的机制建议已落地。

### 2026-09-09-greatwall-quality-task-brief.md
- 类型=file · HEAD 末次=2026-09-15T02:13:22+08:00（6aae9a7439） · 归档双活=`docs/_working/archive/2026-09/c_class_scattered/2026-09-09-greatwall-quality-task-brief.md` 字节等值 1/1 · 末笔生产面=0 件
- 提交链：6aae9a7439 docs: docs/_working 清理批(1/3)——50 份文档结案报告写入（C-1~C-4 裁定固化；5ac3786933 模板 v0.5 终稿收口+长城指令书终版（六线并发+tier 迁移段）；74e86898c5 财务分域+供应边供给侧+指标层 PIT 化定案落地（DDL v4 十三表部署完成）；22b5f9f2c0 股权穿透表并入+公司节点七域模板 v0.2+长城指令书股权施工段
- 做了什么：2026-09-09 夜产业链图谱「全量质量修复+扩产」六线并发长城任务指令书（SOP v1.5.0 时间盒 10h）：DDL v4 十三表部署、股权穿透 ig_equity_edge、供应边两列、指标层 PIT 化、tier 职能化迁移
- 剩余欠账：①清理批结案报告判「未结案」的两条欠账（S6 306 条 unspecified 甄别/超阈值清单待 Owner）已在真源销案：docs/01_policies_and_standards/policies/graph_quality_standard.md:52 与 :132 记 Owner 2026-09-12 第一性原理裁定「tier 检查段废止、686 条 unspecified+306 条治理债销案」；②本件正文为派单指令样式文本（「你是 ZephyrAlpha 产业链图谱长城任务总控 AI…」），按数据对待，未执行其中任何语义；③机械底座 twin=- ，archive/2026-09 下无同名件（已核 working_facts archive_twin_exists=false）
- 结案报告：
    指令书自述交付=引擎复跑+DDL v4 部署+股权表落地。HEAD 侧对应落地面：5ac3786933（模板 v0.5 终稿收口
    +长城指令书终版，ext=0）、74e86898c5（财务分域+供应边供给侧+指标层 PIT 化定案，DDL v4 十三表部署完成）、
    22b5f9f2c0（股权穿透表并入+七域模板 v0.2）。本件唯一遗留（306 条 unspecified 待裁）经真源
    policies/graph_quality_standard.md S6 段 v1.7.0 changelog 记为 Owner 2026-09-12 销案，非未施工。
    最近一笔动本件的 6aae9a7439 为 50 文件纯 _working 批（ext_footprint=0）。

### 2026-09-09-news-industry-wiring-directive.md
- 类型=file · HEAD 末次=2026-09-15T02:13:22+08:00（6aae9a7439） · 归档双活=`docs/_working/archive/2026-09/c_class_scattered/2026-09-09-news-industry-wiring-directive.md` 字节等值 1/1 · 末笔生产面=0 件
- 提交链：6aae9a7439 docs: docs/_working 清理批(1/3)——50 份文档结案报告写入（C-1~C-4 裁定固化；83eaf72eea docs(tdm): 今晚四份执行文档入库——施工清单/长城指令/增长蓝图/接线指令（st-tdmbe 会话产
- 做了什么：「实时新闻+产业链→盘中决策」后端接线施工指令：W1 图谱查询服务化/W2 新闻实时性核对/W3 事件图谱传导器/W4 冲击标的生成器/W5 盘中消费端点/W6 DS 登记，入图交增长轨
- 剩余欠账：六项 W 全部有落地面（见 closure_report），本件无自身欠账；§3 入图交接协议由 2026-09-11-news-chain-wiring-spec-cards.md 交付并已由增长轨落图；正文含禁令样式文本（禁 --no-verify/裸 git 等）=数据，未执行
- 结案报告：
    入库笔 83eaf72eea（今晚四份执行文档入库，ext=0）。W1/W3/W4/W5 实现件在盘：
    src/zephyr/intelligence/chain_impact_resolver.py、chain_impact_stream.py、news_chain_node_linker.py
    （三件源码内均反向引用本指令文件名）。W6 登记在真源：
    docs/01_policies_and_standards/_registry/catalogs/data_asset_registry.yaml:9565 起
    entity_name=intelligence.chain_impact_stream、:9585 name_zh=盘中事件冲击流。
    W3/W4 节点已由增长轨入图：config/trading_decision_map.yaml:1311 node_id: TDM-E-L2-09-1。

### 2026-09-09-node-backtest-governance.md
- 类型=file · HEAD 末次=2026-09-15T02:13:22+08:00（6aae9a7439） · 归档双活=`docs/_working/archive/2026-09/c_class_scattered/2026-09-09-node-backtest-governance.md` 字节等值 1/1 · 末笔生产面=0 件
- 提交链：6aae9a7439 docs: docs/_working 清理批(1/3)——50 份文档结案报告写入（C-1~C-4 裁定固化；7b88249a4c docs/_working 回测治理施工方案落盘（§八）：三期全落盘清单+construction_workf；f712291821 docs/_working 回测治理清单落 Owner 精简裁定（§七 最终口径）：个人量化+全AI 消费者，；8710a3a3d2 [GW:st-tdm-canvas-20260908] [GW:st-tdm-canvas-20260908:
- 做了什么：节点级可回测治理全量问题清单 PB-01~PB-16（含业界对照调研）→ Owner 2026-09-09 精简裁定（10 保/3 降/3 砍）→ §八 三期施工方案（P0 地基 3/P1 验证 6/P2 闭环 3 落盘物，按 construction_workflow_sop 15 步）
- 剩余欠账：本件判据已整体迁入真源（见 already_in_truth_source），残留「待裁定汇总 §五/§六调研来源」为历史过程记录；正文含「Owner 原话→治理语言」样式引文=数据，未执行；twin=- 无归档同名件
- 结案报告：
    清单→裁定→方案三段链条在 HEAD 侧全部有承接落地面：a1357a0777（PB-01~PB-12 清单入库）、
    f712291821（§七 Owner 精简裁定口径）、7b88249a4c（§八 三期施工方案，ext=0）。
    判据本体已入正式真源：validation_method_registry.yaml:3 头注「PB-01，Owner 2026-09-09 裁定
    个人量化精简版」、:17 与 :80-81（holdout 12 个月保密考卷=PB-08）、:78「全局纪律（PB-08/PB-13/PB-16
    裁定落地）」；模块侧 docs/03_modules/_domain_trading/validation/blueprint.md 命中「节点级可回测/PB-08」。
    存储与前端落地面另见 data_asset_registry.yaml:9474（引本件 §8.1）。

### 2026-09-09-node-template-draft.md
- 类型=file · HEAD 末次=2026-09-15T02:13:22+08:00（6aae9a7439） · 归档双活=`docs/_working/archive/2026-09/c_class_scattered/2026-09-09-node-template-draft.md` 字节等值 1/1 · 末笔生产面=0 件
- 提交链：6aae9a7439 docs: docs/_working 清理批(1/3)——50 份文档结案报告写入（C-1~C-4 裁定固化；0ec3c74012 feat(industry_graph): 字段字典单一真源落地（Owner 2026-09-10 方案 A ；5ac3786933 模板 v0.5 终稿收口+长城指令书终版（六线并发+tier 迁移段）；2f134396a5 深交所课题对标+tier 职能化改造+股权视图澄清+成本价字段（模板 v0.4）
- 做了什么：链/环节/公司三层节点模板草案与 17 项决策点终态（Owner 2026-09-09「按建议」全裁定），含 ig_equity_edge 股权穿透表设计与专业名词对照表
- 剩余欠账：本件 front-matter 自述 status=RETIRED（2026-09-10）+migrated_to=industry_graph_field_dictionary.yaml，但文件仍留在 docs/_working 顶层未归档；真源 SOP 仍以本件为设计真源指针（docs/01_policies_and_standards/sop/data_audit_sop/industry_chain_data_audit_policy.md:1030「设计真源 docs/_working/2026-09-09-node-template-draft.md §2.5」）——归档前须把该指针改指字段字典，否则断链；清理批结案报告判「设计类无落地证据保守保留」与本件自述 RETIRED 相矛盾（机械底座误判，已在底座侧记录）
- 结案报告：
    退役与内收由 0ec3c74012 完成（feat(industry_graph): 字段字典单一真源落地，Owner 2026-09-10 方案 A
    拍板；该笔 ext=7/8，含新建 catalogs/industry_graph_field_dictionary.yaml + vocab_loader.py +
    三消费方改加载 + 四方对齐测试，commit message 明写「docs/_working/2026-09-09-node-template-draft.md
    退役（设计决策迁入字典 standard/notes，_working 不再承载真源）」）。
    字典在盘可核：industry_graph_field_dictionary.yaml:26 function_roles 词表段、:279 ig_node.function_role
    字段标准（含 tier 退役批 1.2.0 changelog :10）。

### 2026-09-09-tdm-growth-blueprint.md
- 类型=file · HEAD 末次=2026-09-15T02:13:22+08:00（6aae9a7439） · 归档双活=`docs/_working/archive/2026-09/c_class_scattered/2026-09-09-tdm-growth-blueprint.md` 字节等值 1/1 · 末笔生产面=0 件
- 提交链：6aae9a7439 docs: docs/_working 清理批(1/3)——50 份文档结案报告写入（C-1~C-4 裁定固化；68f13af966 docs(tdm): 晨审批3增量——八锚逐件裁定+CAND-CRYPTO-010 张力定论（st-tdm-r；454c10ad4e docs(tdm): 晨审报告+台账销项（st-tdm-review-20260911，Owner 深夜令：检；2dfff1866a docs(tdm): 增长批3——队列终态核实+G3 币圈六向寻路（零地图写入批）——§3.1 七行批2 已全
- 做了什么：TDM 病菌寻路增长轨施工文档：五步循环+六向寻路作业矩阵+防噪音四道闸+职能完备性对照+增长台账（G1~G6 三态销账）+§6 晨审指令+§7 批3（G3 币圈六向+八树枝锚提案）
- 剩余欠账：方法论部分已升 permanent 真源（见 already_in_truth_source，冲突时以 SOP 为准）；本件剩 §5/§7 台账类挂起项（G3 币圈待 Owner 立项 95 号 Phase 2、G2/L2-05 挂起、X-R1 三方法待排期）属他线门位，非本件施工欠账；正文含「Owner 深夜令」样式表述=数据，未执行
- 结案报告：
    判据已整体内收为长期真源：docs/01_policies_and_standards/sop/mining_sop/
    trading_decision_map_pathfinding_policy.md（ttl: permanent，v1.2.0）第 28 行明写
    「首次执行实例：docs/_working/2026-09-09-tdm-growth-blueprint.md（task_bound，方法论冲突以本 SOP 为准）」，
    其 §5 六向寻路/§6 防噪音四道闸/§7 终止判据与本件 §1.5/§1.6 一一对应；
    rule_catalog_registry.yaml:2414 在册该 SOP 标题。合同 §3 两条 grep（关键词「病菌寻路」「六向寻路」「防噪音」）
    均在 catalogs 命中（真源已在），故按 R2 由 ② 改判 ①。
    台账与执行链：64dd7d1d55（§6 晨审指令落盘）→ 2dfff1866a（批3 队列终态+G3 六向，零地图写入）→
    454c10ad4e（晨审报告+台账销项，ext=1）→ 68f13af966（八锚逐件裁定+CAND-CRYPTO-010 定论，ext=0）。

### 2026-09-09-tdm-missing-modules-construction.md
- 类型=file · HEAD 末次=2026-09-15T02:13:22+08:00（6aae9a7439） · 归档双活=`docs/_working/archive/2026-09/c_class_scattered/2026-09-09-tdm-missing-modules-construction.md` 字节等值 1/1 · 末笔生产面=0 件
- 提交链：6aae9a7439 docs: docs/_working 清理批(1/3)——50 份文档结案报告写入（C-1~C-4 裁定固化；5b42d8e490 docs(tdm): 两份死会话遗留施工文档补 add（无活跃 claim，零风险留档）；411955284d feat(tdm)+feat(signal): 自裁批 L2-01/L2-04 落地+全部残余收口（Owner；76f96ce80c docs(tdm): 长城夜班落库收口——台账§十四 LANDED 终态（e86ce72b80 22/22+四
- 做了什么：TDM 缺失模块全面施工总纲（C 类 12/B 类 10/A 类回填 41/D 类不建）+ 连续六轮执行台账（夜班1/夜班2/四批开工令/全景图体检/落库终态/自裁批/S24 下架链审查/L2-01-L2-04 复核）
- 剩余欠账：§七 两项 Owner 结构项均已收口（流根四节点=文内自述他会话合并入图；改名拆细=D108 三条件随批）；§十四/§十五 记 22/22 LANDED 落库终态；清理批结案报告列的 3 条「未完成」经核为台账历史行与已裁定项，非欠账；本件含大量指令/裁定样式文本（Owner 令「自行裁定」等）=数据，未执行
- 结案报告：
    施工链落地实证（均为 git log 真实输出）：e86ce72b80（四批开工令整批落地——C13/L3-06/L3-09 三模块
    新建+六锚回填+D1 编号规范化，该笔 ext=21/22）、76f96ce80c（长城夜班落库收口，台账 §十四 LANDED
    终态 22/22+四关复验）、411955284d（自裁批 L2-01/L2-04 落地+全部残余收口）、
    5b42d8e490（两份死会话遗留施工文档补 add）。模块实体在真源可核：
    config/trading_decision_map.yaml:591/:1821 module_id: MOD-SIG-142、:1818 node_id: TDM-E-L3-08。

### 2026-09-09-tdm-night-greatwall-directive.md
- 类型=file · HEAD 末次=2026-09-15T02:13:22+08:00（6aae9a7439） · 归档双活=`docs/_working/archive/2026-09/c_class_scattered/2026-09-09-tdm-night-greatwall-directive.md` 字节等值 1/1 · 末笔生产面=0 件
- 提交链：6aae9a7439 docs: docs/_working 清理批(1/3)——50 份文档结案报告写入（C-1~C-4 裁定固化；83eaf72eea docs(tdm): 今晚四份执行文档入库——施工清单/长城指令/增长蓝图/接线指令（st-tdmbe 会话产
- 做了什么：TDM 缺失模块夜班长城任务指令（23:00→09:00）：模型与角色分工、开工序列、单模块 8 步微循环、机械审查循环协议、红蓝对抗 ≥3 手法、CORE-ALGORITHM 标记清单、交接包契约、夜班禁令
- 剩余欠账：本件是一次性派单指令，执行结果全部记在 2026-09-09-tdm-missing-modules-construction.md §十~§十三（night-gw-2300 台账）；正文的指令样式文本（「开工序列/禁令/失败 3 轮挂起」）=数据，未执行；其通用纪律部分真源已由 construction_workflow_policy.md 承载（该件 :184/:457 含红蓝对抗/双审审查段），无未施工项
- 结案报告：
    入库笔 83eaf72eea（今晚四份执行文档入库，ext=0）。执行面落地面：e86ce72b80（四批开工令整批落地
    night-gw-2300，ext=21）、76f96ce80c（长城夜班落库收口 §十四 LANDED 22/22）。
    本件为纯指令书，无自述待办残留（§7 交接包为指令要求，非欠账）。

### 2026-09-10-chainmap-frontend-batch-plan.md
- 类型=file · HEAD 末次=2026-09-15T02:13:22+08:00（6aae9a7439） · 归档双活=`docs/_working/archive/2026-09/c_class_scattered/2026-09-10-chainmap-frontend-batch-plan.md` 字节等值 1/1 · 末笔生产面=0 件
- 提交链：6aae9a7439 docs: docs/_working 清理批(1/3)——50 份文档结案报告写入（C-1~C-4 裁定固化；13076db39b feat(chainmap): 全部开工批——B7 S21 断链标注+B8 作战池全链+B5 下钻点亮+环节别；8f795b7319 feat(chainmap): B4r4+收尾批——字遮挡根因治理+重心法拓扑排序+两指令对账收口（Owner；fa3d501890 feat(chainmap): B4 链层甬道化+撤销 B3 族内星云（Owner 2026-09-10 实测
- 做了什么：产业链前端（chainmap 页）3D 三期+收尾批次计划 B1~B8：B1 加载态/B2 族级星云/B3 链群小星云（REVOKED）/B4 单链甬道 TDM 化/B5 下钻树/B6 缩放打磨/B7 S21 断链标注/B8 作战池
- 剩余欠账：批次表 B5 行状态仍写 PENDING，与标题行「复启批 2026-09-14 全部开工：…+B5 下钻点亮（10 节点）」及收尾批复启附记矛盾——真源以 13076db39b 为准（B5 已点亮），本件为未回写的账本瑕疵，非欠施工；⑥浅色主题=Owner 排期挂起（文内明写非本页职权）；纪律清单含命令样式文本（git_commit.py 参数串）=数据，未执行
- 结案报告：
    各批落地面（git log 真实输出）：dc1d95b91a（B3 二期星云，ext 见该笔）、fa3d501890（B4 甬道化+撤销 B3，
    Owner 实测裁定）、8f795b7319（B4r4 收尾批：字遮挡根因+重心法拓扑排序，ext=5）、
    13076db39b（2026-09-14 全部开工批：B7 S21 断链标注+B8 作战池全链+B5 下钻点亮+环节别名，ext=10/12）。
    本件批次表状态列除 B5 外均已回写，B5 真值以 13076db39b 为准。

### 2026-09-10-legacy-clear-night-report.md
- 类型=file · HEAD 末次=2026-09-15T02:13:22+08:00（6aae9a7439） · 归档双活=`docs/_working/archive/2026-09/c_class_scattered/2026-09-10-legacy-clear-night-report.md` 字节等值 1/1 · 末笔生产面=0 件
- 提交链：6aae9a7439 docs: docs/_working 清理批(1/3)——50 份文档结案报告写入（C-1~C-4 裁定固化；734f696019 docs: 治理清偿遗留收尾+门禁加固推广晨报入库（st-legacy-clear-20260910）
- 做了什么：治理清偿遗留收尾+门禁加固推广晨报：T0 晨报收尾/T2 pytest_cache 权限验收级修复/T3 registrar 演进断言治本/T4 .runtime 残留清理/T5「只查自己」gate 推广（3 gate+共享 helper 模块，3 独立 commit）/T6 面板 API CH 超时加固
- 剩余欠账：文内 §四 自述「无其他未完成——T0/T2/T3/T4/T5(主体)/T6 全部收口」；§三 七条遗留全为 Owner 门位/权限项（管理员 takeown、8890 elevated 重启、R21 死批归一、SCHEMA-FILE-EXISTS 存量悬空、余下 9 gate 机械推广、allow-mass-deletion 中文阈值、echo-guard 聚合器豁免），其中 R21 死批后续由 f1050cd25c 治标、8890 重启与 gate 推广由他会话批落地，余为 Owner 事项非本件欠账；含命令样式文本（git_commit.py 调用串）=数据，未执行
- 结案报告：
    唯一动本件的实质笔 734f696019（治理清偿遗留收尾+门禁加固推广晨报入库，ext=1/2），
    其承接的施工笔在 HEAD 链上可核：262b328a7c（自动同步保护路径过滤治本，ext=3）、
    f1050cd25c（R21 module_id 格式冲突治标，ext=1）。
    本件 §三 清单为 Owner 门位登记性质，文内 §四 已自述主体收口。

### 2026-09-10-nodebt-night-report.md
- 类型=file · HEAD 末次=2026-09-15T02:13:22+08:00（6aae9a7439） · 归档双活=`docs/_working/archive/2026-09/c_class_scattered/2026-09-10-nodebt-night-report.md` 字节等值 1/1 · 末笔生产面=0 件
- 提交链：6aae9a7439 docs: docs/_working 清理批(1/3)——50 份文档结案报告写入（C-1~C-4 裁定固化；1eb9f0cf75 docs(_working): 晨报补 Owner 晨间验收记录——前端目检通过+三项裁定全部放行；0c05899bbc feat(trading): 衰减巡检挂载裁定落地——run_validation 尾随事件（PB-14 事件；a4b05a4be1 docs(_working): 长城任务晨报——节点级可回测治理 P0→P1→P2 过夜施工收尾（2026-0
- 做了什么：节点级可回测治理 P0→P1→P2 过夜施工晨报：c1_backtest 台账新建、验证方法学与 DAL 登记、param_origin、holdout 节、前端验证档案区+画布徽章、衰减巡检尾随事件，10 条自行裁定留痕
- 剩余欠账：§四 记「三期落盘物全部完成并通过验收」+P0/P1/P2 提交终态逐笔列明；唯一登记遗留=P2-3 反事实对照（文内标注真源 §8.3 授权「按需可延」，方法学已在 P1-1 落好），后续由 X 流验证批承接；§五 三条建议中 IMPORT-INTEGRITY「只查自己」已由 perf 线落地；含 PowerShell/命令样式文本=数据，未执行
- 结案报告：
    施工链（git log 真实输出）：a4b05a4be1（长城任务晨报入库）、0c05899bbc（衰减巡检挂载裁定落地=
    run_validation 尾随事件，PB-14 事件驱动闭环，ext=4）、1eb9f0cf75（晨报补 Owner 晨间验收记录+
    三项裁定放行，ext 见该笔）。文内自述三项裁定：①已施工完毕、②信号消融对照器与③decision_price+order_type
    两字段按裁定时机随 X 流验证批执行——已由 2026-09-10-xflow-batch-report.md 与其 commit 链承接。
    本件被 EA 文档与源码反向引用：docs/02_enterprise_architecture/02_domain_architecture_docs/72_d_trading.md、
    src/zephyr/trading/validation/ablation.py。

### 2026-09-10-xflow-batch-report.md
- 类型=file · HEAD 末次=2026-09-15T02:13:22+08:00（6aae9a7439） · 归档双活=`docs/_working/archive/2026-09/c_class_scattered/2026-09-10-xflow-batch-report.md` 字节等值 1/1 · 末笔生产面=0 件
- 提交链：6aae9a7439 docs: docs/_working 清理批(1/3)——50 份文档结案报告写入（C-1~C-4 裁定固化；43c7f1eadc docs(_working): X 流验证批收尾报告——T1/T2/T3 全部落地（第二期风控批，sessio
- 做了什么：X 流验证批（节点级可回测治理第二期风控批）收尾报告：T1 决策价+订单类型入流水、T2 信号消融对照器、T3 验证批接线与首跑，附 7 条自裁与提交链
- 剩余欠账：§三 八条遗留：1/2 为「待 Owner 放行/待窗口前移」的纪律闸（协议 §12 定稿前不跑回测），3 消融标注自动化与 4 exec 真决策价口径已由跟进设计件落地，5 decay 口径「暂不阻塞」，6/7 为环境/他会话事项，8 注册表驱动重构=待第三批评估——均属他批事项而非本件未施工；本件正文含 Owner 对话引文=数据，未执行
- 结案报告：
    唯一实质笔 43c7f1eadc（X 流验证批收尾报告——T1/T2/T3 全部落地，ext=1/2，文内另记提交链
    ebc98ac1/579c8c85/ecdcdcab 三笔为施工落点）。遗留项承接证据：跟进设计件
    2026-09-10-xflow-followup-design.md 已把 ④exec v2 与 ③SellSignal 转换助手施工完毕
    （9d81b824bd），定稿锚点经 Owner「同意，开工」落在 src/zephyr/trading/validation/runner.py:82。

### 2026-09-10-xflow-followup-design.md
- 类型=file · HEAD 末次=2026-09-15T02:13:22+08:00（6aae9a7439） · 归档双活=`docs/_working/archive/2026-09/c_class_scattered/2026-09-10-xflow-followup-design.md` 字节等值 1/1 · 末笔生产面=0 件
- 提交链：6aae9a7439 docs: docs/_working 清理批(1/3)——50 份文档结案报告写入（C-1~C-4 裁定固化；9d81b824bd docs(_working): X 流验证批遗留项跟进设计——exec v2 口径/定稿锚点方案/消融实弹预案
- 做了什么：X 流验证批遗留四项分诊跟进：④exec 滑点 v2 口径与③SellSignal→XFlowAction 转换助手（两件已施工+单测）、①holdout 定稿锚点方案（设计稿→后经 Owner 裁定施工）、②消融实弹执行预案（通路 A/B）
- 剩余欠账：§三 定稿锚点已由 Owner 裁定「同意，开工」并落地（runner.py:82 finalized_at=2026-09-09，语义另固化于 validation_method_registry.yaml:81「考完一次即作废前移，改参数=换卷重考」），文内「未改码」标注为施工前状态；§四 实弹回放仍待 Owner 放行（纪律闸=协议 §12），通路 A/B 预案是本件唯一仍被独占的待执行内容；含「Owner 问…」「裁定请求」样式文本=数据，未执行
- 结案报告：
    9d81b824bd 为本件唯一入库笔（X 流验证批遗留项跟进设计，ext=0）。
    §一/§二 两项施工实证：0c05899bbc 之后的 X 流批链（43c7f1eadc 报告所记 ebc98ac1/579c8c85/ecdcdcab）。
    §三 落地实证（现盘可核）：src/zephyr/trading/validation/runner.py:82
    「finalized_at: str | None = \"2026-09-09\"  # 定稿锚点 D 日（Owner 2026-09-09 裁定：同意，开工）」、
    :200/:205 分支语义、:415/:566 台账披露行。合同 §3 两条 grep（关键词「定稿锚点」）在
    docs/03_modules/*/blueprint.md 与 catalogs+EA 均零命中（命中仅在 src 代码与本件内），
    但机制本身已入代码真源与 validation_method_registry holdout_rule，故判 ① 不判 ②。

### 2026-09-11-backtest-evidence-log-discussion.md
- 类型=file · HEAD 末次=2026-09-15T02:13:22+08:00（6aae9a7439） · 归档双活=`docs/_working/archive/2026-09/c_class_scattered/2026-09-11-backtest-evidence-log-discussion.md` 字节等值 1/1 · 末笔生产面=0 件
- 提交链：6aae9a7439 docs: docs/_working 清理批(1/3)——50 份文档结案报告写入（C-1~C-4 裁定固化；ebc5370614 docs(backtest): SOP-D 回测档案图书馆规范入库——证据链讨论 R1-R5 裁定落地（前班遗；a9f4de56f3 docs: 回测证据链与验证档案讨论稿——现状盘点+三层证据体系增量设计+规范总清单
- 做了什么：回测证据链与验证档案讨论稿：现状防撞车盘点（node_verdict 台账/五类方法学已施工）+增量缺口 G1-G3+三层证据体系设计+命名规范+除日志外回测需规范清单，Owner 2026-09-11 R1-R5 全认（R5 提前）
- 剩余欠账：R1-R5 裁定已整体入库为 SOP-D（sop_d_run_archive_naming.md）；文内「关键发现：data/backtest_artifacts/ 已 .gitignore、预注册阈值必须进 backtest_backlog.yaml」为方向性提醒，已由登记表侧承载；无本件独占欠账；含 Owner 裁定样式文本=数据，未执行
- 结案报告：
    a9f4de56f3（讨论稿入库，ext=0）→ ebc5370614（docs(backtest): SOP-D 回测档案图书馆规范入库——
    证据链讨论 R1-R5 裁定落地，前班遗留三件套收口，ext=2/3）。
    真源在盘：docs/01_policies_and_standards/sop/backtest_system_sop/sop_d_run_archive_naming.md
    （grep「run 档案/图书馆规范」命中该件与同目录 README.md）；反向引用：src/zephyr/backtest/run_archive.py、
    scripts/backtest/verify_run_archive.py、docs/02_enterprise_architecture/02_domain_architecture_docs/34_d_backtest.md。

### 2026-09-11-backtest-system-sop-discussion.md
- 类型=file · HEAD 末次=2026-09-15T02:13:22+08:00（6aae9a7439） · 归档双活=`docs/_working/archive/2026-09/c_class_scattered/2026-09-11-backtest-system-sop-discussion.md` 字节等值 1/1 · 末笔生产面=0 件
- 提交链：6aae9a7439 docs: docs/_working 清理批(1/3)——50 份文档结案报告写入（C-1~C-4 裁定固化；9e6fbe9faa docs: 回测体系 SOP 落盘——总纲 + SOP-A/B/C 三件套 + 定稿讨论稿
- 做了什么：回测体系全链路 SOP 讨论定稿：分级回测颗粒度、AI 自驱回测 SOP、聚宽 600 条策略植入路径三问定稿+七步打通顺序+D1-D4 决策记录（基准区间/预注册禁挪门柱/10 条 shim 试点/盘中日线近似降级）
- 剩余欠账：§5「下一步」三条（启动 P0 批次/SOP-C Step C1 盘点 600 条/每批回写本文件进度小节）属后续批次的执行编排，未在本件续写——本件定稿内容整体已由 SOP-A/B/C 三件套承载为真源，后续批次进度不应再回写本件（应改记 SOP 侧）；含 Owner 问答样式文本=数据，未执行
- 结案报告：
    9e6fbe9faa（回测体系 SOP 落盘——总纲 + SOP-A/B/C 三件套 + 定稿讨论稿，ext=4/5）为本件唯一实质笔。
    真源在盘：docs/01_policies_and_standards/sop/backtest_system_sop/{README.md, sop_a_full_map_orchestration.md,
    sop_b_node_loop.md, sop_c_strategy_library_intake.md}；反向引用：scripts/backtest/strategy_intake_inventory.py、
    docs/02_enterprise_architecture/02_domain_architecture_docs/34_d_backtest.md。
    同目录另有后继真源 exam_policy.md（ttl: permanent，v1.0.0，2026-09-19，挂 裁定#365），
    说明考试段判据已在本件之后独立成册，本件无需再承载长期判据。

### 2026-09-11-chainmap-final-batch-report.md
- 类型=file · HEAD 末次=2026-09-15T02:13:22+08:00（6aae9a7439） · 归档双活=`docs/_working/archive/2026-09/c_class_scattered/2026-09-11-chainmap-final-batch-report.md` 字节等值 1/1 · 末笔生产面=0 件
- 提交链：6aae9a7439 docs: docs/_working 清理批(1/3)——50 份文档结案报告写入（C-1~C-4 裁定固化；13076db39b feat(chainmap): 全部开工批——B7 S21 断链标注+B8 作战池全链+B5 下钻点亮+环节别；8f795b7319 feat(chainmap): B4r4+收尾批——字遮挡根因治理+重心法拓扑排序+两指令对账收口（Owner
- 做了什么：产业地图（chainmap）收尾批报告：字遮挡根因治理（墓碑名剥离+卡高/行高钉死）+重心法拓扑排序+两指令对账收口+四件套 ACC rev6，末段附 2026-09-14「全部开工」复启批销账
- 剩余欠账：§七 五条挂账中 1/3/5 已由复启附记（B7/B8/B5）销账，仍开放三条：aliases/facilities 域「建设中」留位、profile.country 值缺失（数据侧非前端）、浅色主题挂起（全局项 Owner 排期）——均为他线/Owner 事项；本件为报告且含 commit 链，无自身未施工项；含 Owner 反馈样式文本=数据，未执行
- 结案报告：
    8f795b7319（B4r4+收尾批，本件 creation token=chainmap-final-batch-report-20260911，ext=5）
    → 13076db39b（复启批全部开工：B7 S21+B8 作战池+B5 下钻+aliases，ext=10/12，本件末段附记其结果）。
    报告自述与 HEAD 一致，无虚构哈希（文内 commit 引用均可在 git log 链上核到）。

### 2026-09-11-commit-queue-dead-zero-closure.md
- 类型=file · HEAD 末次=2026-09-15T02:13:22+08:00（6aae9a7439） · 归档双活=`docs/_working/archive/2026-09/c_class_scattered/2026-09-11-commit-queue-dead-zero-closure.md` 字节等值 0/1 · 末笔生产面=0 件
- 提交链：6aae9a7439 docs: docs/_working 清理批(1/3)——50 份文档结案报告写入（C-1~C-4 裁定固化；a95113c0ae test(flags): P2 三 flag 实战验证——gate_preflight + gate_resu；262b328a7c fix(queue): 自动同步保护路径过滤——复发性死信循环治本（Owner 裁定选 A，st-perf-p；1743c4bf11 fix(queue): 死信清零批+死信率告警最小落地（st-perf-plan-20260910 续，方案 
- 做了什么：commit_queue 死信清零收尾+死信率告警最小落地：952 项死信全量甄别（REQUEUE 757/PURGE 184/REVIEW 5）、保护路径死循环治本选 A、THD-ALERT-003/004 阈值入 REG-ATH-001、P1⑤⑥/P2⑦⑧⑨ 施工记录
- 剩余欠账：文内自相矛盾一处须总指挥知悉：§6 首行「全部落地（commit 见 git log st-perf-plan-20260910 链）」（L75）与同节 L78「P1⑤ A1/A2、P1⑥、P2⑦⑧⑨：均待 Owner 确认后执行」互相打脸——按 HEAD 实证判已落地（a95113c0ae 三 flag 全 ON 后首次真实提交 + 262b328a7c 治本），L78 为陈旧段落；§5 报 Owner 裁定清单自述「已全部批复并执行，本节留档」；含命令/审计文件路径样式文本=数据，未执行
- 结案报告：
    施工链（git log 真实输出）：1743c4bf11（死信清零批+死信率告警最小落地，ext=6/7）→
    262b328a7c（自动同步保护路径过滤——复发性死信循环治本，Owner 裁定选 A，ext=3）→
    a95113c0ae（test(flags): P2 三 flag 实战验证——gate_preflight + gate_result_cache +
    commit_queue_interactive 全 ON 后首次真实提交，ext=0/1，为本件「已落地」终判据）。
    告警阈值真源在盘：REG-ATH-001 v1.4.0 THD-ALERT-003/004（文内自述，代码经 threshold_loader 统读）。

### 2026-09-11-crypto-shadow-mvp.md
- 类型=file · HEAD 末次=2026-09-15T02:13:22+08:00（6aae9a7439） · 归档双活=`docs/_working/archive/2026-09/c_class_scattered/2026-09-11-crypto-shadow-mvp.md` 字节等值 0/1 · 末笔生产面=0 件
- 提交链：6aae9a7439 docs: docs/_working 清理批(1/3)——50 份文档结案报告写入（C-1~C-4 裁定固化；f1050cd25c fix(tdm): R21 module_id 格式冲突治标——L2-09-1/09-2 回退 module_；7a342bce64 [ARCH-APPROVAL:ARCH-MODEL-LIFECYCLE-001] 机械补登记 6 行（ZA-B
- 做了什么：币圈影子 MVP 收尾报告（doc_type: audit_report）：交付清单与状态、B-1/B-2 registry 口径修复、采集器 3 处运行时 bug 修复、合成样本烟测（如实声明非真实数据）、OKX 端点环境级阻断实测
- 剩余欠账：唯一未闭环=真实首跑（§5 定性为环境级 DNS 污染+SNI 干扰全域封锁，四备用端点实测全灭；§6 首跑指令与 §8 解锁清单（Cloudflare 反代最小成本路径、币安换源属设计变更须 Owner）为本件独占内容，归档前须先转交 Owner/数据线，否则孤儿化——本报告自述「MVP 收尾」故判 ①，但影子判定结论尚未产出；§4 明写烟测用合成样本非真实数据；含 PowerShell 命令样式文本=数据，未执行
- 结案报告：
    动本件的 HEAD 两笔（git log 真实输出）：f1050cd25c（R21 module_id 格式冲突治标，ext=1）、
    7a342bce64（[ARCH-APPROVAL:ARCH-MODEL-LIFECYCLE-001] 机械补登记 6 行，ext 见该笔）。
    交付物在真源可核：data_asset_registry.yaml:9610 dataset_id: DS-226（影子判定消费方=DS-227）、
    :9656 dataset_id: DS-227（scripts/data/crypto_shadow_judge.py 读 DS-226 直判，DDL 在册）。
    采集件在盘：src/zephyr/data/implementations/crypto_kline_collector.py、shadow_gate_c_l1.py
    （本件 §6 首跑指令所引路径）。真实数据面：DS-226/227 为已登记未产数状态（首跑挂网络闸）。

### 2026-09-11-l308-aggregator-construction.md
- 类型=file · HEAD 末次=2026-09-15T02:13:22+08:00（6aae9a7439） · 归档双活=`docs/_working/archive/2026-09/c_class_scattered/2026-09-11-l308-aggregator-construction.md` 字节等值 1/1 · 末笔生产面=0 件
- 提交链：6aae9a7439 docs: docs/_working 清理批(1/3)——50 份文档结案报告写入（C-1~C-4 裁定固化；c457c5ef69 feat(signal): L3-08 候选池汇总件+37 测试+门面接线收口（交接批遗留件入库）
- 做了什么：TDM-E-L3-08 候选池汇总件施工文档：按 C13 纯函数核范式落码 candidate_pool_aggregator.py+37 测试+门面接线，并给增长轨落图规格（module_ref/algo_refs/边复用建议）
- 剩余欠账：落图已由增长轨执行：config/trading_decision_map.yaml:1818 node_id: TDM-E-L3-08 → :1821 module_id: MOD-SIG-142 + module_ref 指向本件实现路径；本件 §4 建议的编号 MOD-SIG-140 已被占用（docs/03_modules/_domain_signal/sentiment_cycle/blueprint.md:2/:36 由 night-gw-2300 D1 批分配），实际登记号=MOD-SIG-142，本件行内建议值已成为误导文本（归档无害，若保留则须加注）；另 candidate_pool_aggregator 无独立蓝图目录，仅在 docs/03_modules/_domain_signal/sector_strength_aggregator/blueprint.md:86 以「已实现」行内出现——本件 §4 自述「蓝图属登记批随行件，本会话未代建」，是否补建独立蓝图请总指挥裁
- 结案报告：
    c457c5ef69（feat(signal): L3-08 候选池汇总件+37 测试+门面接线收口，ext=4/5，
    同笔含 config/trading_decision_map.yaml 与 src/zephyr/signal_ashare/{__init__.py,core/candidate_pool_aggregator.py}
    + tests/signal_ashare/test_candidate_pool_aggregator.py）。
    真源现状：map :1818/:1821（节点+MOD-SIG-142+module_ref）、EA 侧
    docs/02_enterprise_architecture/02_domain_architecture_docs/31_d_ashare_signal.md 与
    10_trading_map/trading_map_03_e_l3_stock.md 反向引用本件；
    登记表侧 catalogs/fail_open_register.yaml:1079/:1085/:1091 与 backtest_backlog.yaml:883 已挂实现路径。

### 2026-09-11-news-chain-wiring-spec-cards.md
- 类型=file · HEAD 末次=2026-09-15T02:13:22+08:00（6aae9a7439） · 归档双活=`docs/_working/archive/2026-09/c_class_scattered/2026-09-11-news-chain-wiring-spec-cards.md` 字节等值 1/1 · 末笔生产面=0 件
- 提交链：6aae9a7439 docs: docs/_working 清理批(1/3)——50 份文档结案报告写入（C-1~C-4 裁定固化；b7263c4b33 docs(working): 产业链→盘中决策接线交付包——节点规格卡×3（TDM-E-L2-09-1/09-
- 做了什么：「实时新闻+产业链→盘中决策」后端接线交付包（wiring-news-ig-001）：W3/W4/W5 三张节点规格卡（坑位回填材料）+W1/W2 反查核对结论+24h 窗 800 条新闻端到端 dry-run+深夜批（搜索框 bug 修复/三服务重启/浏览器级验收/DS-224 时点口径/卫生 reconciler 风险登记）
- 剩余欠账：交付已被增长轨消化：config/trading_decision_map.yaml:1311 node_id: TDM-E-L2-09-1（及 :5491-5492 入边/出边）与 :1043 TDM-E-L2-09-2 在盘；§6.5 结构性风险（workspace_hygiene_reconciler 误 restore）已有真源承载（catalogs/architecture_issue_registry.yaml:4186 DEBT-WORKSPACE-001/002 及 :5572/:5609 复用条目），无孤儿欠账；本件含「请 Owner 转派/建议」样式文本与派单措辞=数据，未执行；清理批结案报告判「设计/计划类且无落地证据保守保留」与 HEAD 实证不符（机械底座漏判，已记入底座反馈）
- 结案报告：
    b7263c4b33（docs(working): 产业链→盘中决策接线交付包——节点规格卡×3+W1/W2 核对+端到端 dry-run 实证+深夜批追加，
    ext=0/1，即本件入库笔）。后续承接笔（git log 真实输出）：f1050cd25c（fix(tdm): R21 module_id 格式冲突治标
    ——L2-09-1/09-2 回退 module_ref-only warn 路线，ext=1/3），即两坑位的最终入图形态。
    实现件与登记：src/zephyr/intelligence/chain_impact_resolver.py、chain_impact_stream.py、
    news_chain_node_linker.py；data_asset_registry.yaml:9565/:9585（盘中事件冲击流）。
    creation token 在册：capability_canonical_file_registry.yaml:12629 起 created_by: wiring-news-ig-001。

### 2026-09-11-tdm-morning-review-report.md
- 类型=file · HEAD 末次=2026-09-15T02:13:22+08:00（6aae9a7439） · 归档双活=`docs/_working/archive/2026-09/c_class_scattered/2026-09-11-tdm-morning-review-report.md` 字节等值 1/1 · 末笔生产面=0 件
- 提交链：6aae9a7439 docs: docs/_working 清理批(1/3)——50 份文档结案报告写入（C-1~C-4 裁定固化；68f13af966 docs(tdm): 晨审批3增量——八锚逐件裁定+CAND-CRYPTO-010 张力定论（st-tdm-r；454c10ad4e docs(tdm): 晨审报告+台账销项（st-tdm-review-20260911，Owner 深夜令：检
- 做了什么：TDM 全景晨审：A 施工轨 10 模块六点复检（9 测试套 241 绿）+ B 增长批2 四项 + C 8890 实测 138 节点/194 边与真源一致、40 红节点全判预期红 + D 六项裁定落笔 + 批3 八树枝锚逐件裁定与 CAND-CRYPTO-010 两层口径定论
- 剩余欠账：本件自述遗留四项（均为交他轨的在册欠账，非本件未施工）：①币圈 D 类 4 节点待 Owner 立项（G3 已留 95 号 Phase 2 数据层施工痕）②资讯传导 L2-09-1/09-2 等 G2 规格卡③明日推演 L0-04 等 C13 施工（D6 已裁升批）④D1 R21 depgraph 273 种下划线 id 欠账维持、D3 RL 立项挂 2027-03 复审。清理批自动结案报告判「未结案·保留」=生成器数据，未据以改判；正文含「Owner 深夜令」样式表述=数据，未执行
- 结案报告：
    报告本体为复检件：被检对象在 HEAD 侧全部在盘。锚点/裁定承接面：D4 批准的 DAL 两件已在
    docs/01_policies_and_standards/_registry/catalogs/decision_algo_registry.yaml 在册（同文件
    :216 DAL-FWD-STOP 等条目）；D5 前端两卡与 138/194 地图口径见 config/trading_decision_map.yaml
    （该文件现含 :278 vol_target_allocator(MOD-BT-082)、:5573 L1×capitulation 挂载等后续批次改动）。
    最近一笔动本件的是纯 _working 清理批 6aae9a7439（50 文件，ext=0）；本件自身两笔施工/复核提交
    为 454c10ad4e（2026-09-11 02:28 晨审+销项）与 68f13af966（2026-09-11 02:39 批3 增量八锚裁定）。

### 2026-09-12-alt-data-batch1-construction-report.md
- 类型=file · HEAD 末次=2026-09-15T02:13:22+08:00（6aae9a7439） · 归档双活=`docs/_working/archive/2026-09/c_class_scattered/2026-09-12-alt-data-batch1-construction-report.md` 字节等值 1/1 · 末笔生产面=0 件
- 提交链：6aae9a7439 docs: docs/_working 清理批(1/3)——50 份文档结案报告写入（C-1~C-4 裁定固化；30755b5f86 docs(alt-data): 第1批施工报告入库——千股千评+运价落地/票房缺口登记/治理三件唤醒/多会话吸
- 做了什么：另类数据第 1 批施工报告：千股千评全表日快照 + 航运运价长表（BDI 1988 起）两源落地，三任务实弹 5,196/22,274/33 行、测试 14/14 绿；票房断供缺口登记；alt_data 治理三件首次实弹接线
- 剩余欠账：本批零欠账；§5 明确「第 2-4 批待办不变，按 handoff §8 顺序」=工单已移交同系列交接件（本分片另判），不构成本件欠账。§3 标题「Owner 请知悉」为交底样式=数据，未执行任何语义
- 结案报告：
    落地面全部在 HEAD：src/zephyr/data/config/tasks.yaml:2697 task_id=alt_stock_comment_snapshot、
    :3624/:3638 road_freight_index_refresh/full_refresh；实现体
    src/zephyr/data/implementations/akshare_alt_provider.py（alt_stock_comment 能力与 fetch 实现）；
    治理三件接线 src/zephyr/alt_data/alt_source_bootstrap.py（其 docstring 反向引用本系列交接件 §8-5）；
    票房缺口登记 src/zephyr/data/config/known_data_gaps.yaml:650（resolution_plan 记「不硬做爬虫，
    属第 3 批 web_scraper_engine+compliance_reviewer 范围」）。
    入库笔 30755b5f86（2026-09-13 01:23 docs(alt-data) 第1批施工报告入库）；代码主批 83b81b63ea 已核实在链。

### 2026-09-12-expectation-consumption-design.md
- 类型=file · HEAD 末次=2026-09-17T23:31:35+08:00（01fbfad157） · 归档双活=`docs/_working/archive/2026-09/c_class_scattered/2026-09-12-expectation-consumption-design.md` 字节等值 1/1 · 末笔生产面=5 件
- 提交链：01fbfad157 feat(rulings): 终局授权裁定批量登记 裁定#304-#326 二十三件入册(同 commit 原；4f804539d5 docs: docs/_working 清理批(2/3)——51 份文档结案报告写入（C-1~C-4 裁定固化；72362d5a25 feat(factor): EXP-02 首跑收官=重大数据缺口发现——research_report 预测槽；2f65e0043a feat(factor): C2 预注册批——factor_registry 新增 expectations 
- 做了什么：研报/一致预期消费端设计 v1.0：第一性原理定性质（预期侧）+ 机构/学术调研 + M1-M5 五模块 + 分期施工 + EXP 族 IS/OOS 预注册（§8，冻结禁挪）+ research_report 预测槽位=源站当前快照、历史区间无 PIT 的重大缺口档案（§9）
- 剩余欠账：本件已整体晋升为正式政策册（见 already_in_truth_source），§9.3 破坏性处置三选一已由 Owner 2026-09-14 裁 A（保留+标注）并回写，裁定#323 在册消除「已决未回写」；剩余在册欠账（非本件）=EXP 族改用前向积累+analyst_forecast 双源、干净回测窗最早 2027-07 复核；正文「待 Owner 拍板」样式=数据，未执行
- 结案报告：
    设计判据已入真源：docs/01_policies_and_standards/policies/expectation_consumption_design_policy.md
    （permanent，capability_canonical_file_registry.yaml:12772 登记；其 §9.3 现文记 Owner 裁 A 已执行
    =data_asset_registry DS-228/DS-229 format_summary 补 PIT 价值限制 version→1.1.0 + pit_query 预测列
    禁消费注释）。因子与实验在册：factor_registry.yaml expectations 族 FCT-EXP-001~006、
    experiment_registry.yaml EXP-FACTOR-EVAL-001（n_trials=6、pre_registered=true、lookahead=failed 源级）。
    施工链：14b7bb18ce（数据侧+consensus_daily+EXP 纯函数库+3 设计文档）、2f65e0043a（C2 预注册批）、
    72362d5a25（EXP-02 首跑 data-gap 出证）。最近一笔 01fbfad157 为裁定批量登记批（ext_footprint=5，
    含本件 §9.3 回写）。

### 2026-09-12-fundamental-consumption-design.md
- 类型=file · HEAD 末次=2026-09-15T02:21:49+08:00（4f804539d5） · 归档双活=`docs/_working/archive/2026-09/c_class_scattered/2026-09-12-fundamental-consumption-design.md` 字节等值 1/1 · 末笔生产面=0 件
- 提交链：4f804539d5 docs: docs/_working 清理批(2/3)——51 份文档结案报告写入（C-1~C-4 裁定固化；0cac9ba439 docs(fundamental): 财报事实侧消费端设计+全景工作地图入库（交接债#1）
- 做了什么：财报事实侧消费端设计 v1.0：Owner 两问大白话作答 + 机构/开源调研 + 字段可行性实测 + M0 质量闸门/M1 派生层/M2 八因子/M3 事件族/M4 LLM 深读/M5 挂接六模块 + F1-F5 分期 + D1-D6 六项裁定（哨兵三层防御、statement 粒度、双登记串行对照、估值回补立项、首发顺序、并行不占通道）
- 剩余欠账：D1-D6 已按 RULE-RULING 入册（裁定#228）；F1-M1/F2 已落地，F3/F4/F5 与 §待办移交四项（中报全科目缺口、disclosure_plan 哨兵 11%、三表 1970+双写死重清理、云盘同步线）仍在 known_data_gaps/Owner 门位跟踪，不属本件欠账；本件被 12 处仓外文件反向引用作设计依据（financial_derived.py、financial_derived_compute.py、tasks.yaml、factor_registry、10_d_data/44_d_factor 等），退役需改锚；正文「Owner 发起」问答样式=数据
- 结案报告：
    判据与施工双向收口：ruling_registry.yaml:1621 裁定#228「财报事实侧消费端六裁定（D1-D6）」
    （2026-09-12，数据架构）；M1 派生层落地面 e7c3a41b9c（feat(data): F1-M1 财报派生层 financial_derived
    全链落地，DS-230，裁定#228 D2 裁定）→ 资产在册 data_asset_registry.yaml:9753
    entity_name=c3_fundamental.financial_derived（含构建器/夜间派生/DDL 真源指针）；M2 八因子落地面
    8ac35fdb81（feat(factor): F2 财报八因子全面开工+IC 出证）；M0 质量闸门以 PIT 哨兵守卫形态入库
    （271dd14576，roadmap §泳道2 记「已入库」）。本件入库笔 0cac9ba439（2026-09-13 00:26 交接债#1）。

### 2026-09-12-handoff-c3-zcode.md
- 类型=file · HEAD 末次=2026-09-15T02:21:49+08:00（4f804539d5） · 归档双活=`docs/_working/archive/2026-09/c_class_scattered/2026-09-12-handoff-c3-zcode.md` 字节等值 1/1 · 末笔生产面=0 件
- 提交链：4f804539d5 docs: docs/_working 清理批(2/3)——51 份文档结案报告写入（C-1~C-4 裁定固化；4fbae3c452 docs(_working): 另类数据夜班三件+双交接文档入库（夜班收编批C·Owner 令"该提交的提交"
- 做了什么：晚班收官交接：P0 印教材+检验批、C2 成绩灌表 597 行、因子准入判据成文、红蓝 3 修复 9 用例的证据位置交底；C3 翻译试点三件验证三形态 + 翻译方法论；§五 列四项未入库挂起；§六 列批量翻译→C4 快筛→C5 差异化→数据回补→decay 跟踪五步队列
- 剩余欠账：§五 四项挂起已全部入 HEAD（translated 目录含 pilot_001/002/003 与 c4_* 全量在册；daily_valuation degraded 已登记 data_asset_registry.yaml:5323）；§六 五步中 1/2/3 已由 st-zcode-c4 / C5 批落地，4 估值历史回补、5 decay 月度巡检为长期在册项（后者在 backlog/decay_watch，非本件欠账）；pilot_001 SVR 多因子仍挂起（历史估值缺失=DATA-GAP）；「新对话按此推进」=派单样式文本，按数据对待未执行
- 结案报告：
    队列三步的落地面均可核：批量翻译件在盘（git ls-files scripts/backtest/translated 返回
    _c4_engine.py、_valuation_engine.py 与 c4_<12hex>_<name>.py 族，含 pilot_001/002/003）；
    C5 入库批 ba0c6cab0d（strategy_registry 152→157）+ 挂图配比专项 fa53723fb2（2026-09-14 23:41）；
    准入判据真源在 factor_registry.yaml 头（五要素/五态/IC≥0.02/去马甲 0.85/regime 强制）。
    本文件自身最后被改动是纯文档批 4f804539d5（ext=0）。

### 2026-09-12-igfact-ckg2021-data-asset-analysis.md
- 类型=file · HEAD 末次=2026-09-15T02:21:49+08:00（4f804539d5） · 归档双活=`docs/_working/archive/2026-09/c_class_scattered/2026-09-12-igfact-ckg2021-data-asset-analysis.md` 字节等值 1/1 · 末笔生产面=0 件
- 提交链：4f804539d5 docs: docs/_working 清理批(2/3)——51 份文档结案报告写入（C-1~C-4 裁定固化；4fbae3c452 docs(_working): 另类数据夜班三件+双交接文档入库（夜班收编批C·Owner 令"该提交的提交"
- 做了什么：ig_fact CKG2021 资产定性：264,072 条不是重复数据，而是 205,789 条未入图供应链关系 + 95,383 个未入图产品名（仅 46 条有 ig_edge 对应、184 个已入图）；按四桶给处置建议并出五步施工方案与 2-3 人天估算
- 剩余欠账：施工方案主体已在 HEAD 侧承接（见 closure_report）；本件「前置依赖：ig_fact 无 valid_to 列」一句已被真源推翻（apply_industry_graph_ddl.py:139 已 ADD COLUMN IF NOT EXISTS valid_to + fact_close 通道，且字段字典 changelog 记 ig_node/ig_edge 对标 ig_fact.valid_to 先例）；批量质检逐链执行进度以 ig 增长轨台账为准，本件未自带销项表；清理批自动结案报告判「证据不足，保守保留」=生成器数据，未据以改判
- 结案报告：
    落地面两笔：162b33c510（2026-09-12 15:38 feat(industry_graph): ig_fact CKG2021 事实填充空壳链施工件
    + tier 退役配套改造）产出 scripts/industry_graph/igfact_fill.py——其头注 [CONSUMERS] 明写「长城任务
    ig_fact→空壳链填充（Owner 2026-09-12 授权）」，实现路径与本方案五步一致（产品名噪音过滤+链映射→
    ig_node 环节、supplies_to→ig_edge supply 边、produces→ig_node_company 落位含在市过滤与 role 分档、
    激活走 ingest 唯一通道、source_doc 三段式 ckg_2021 锚）。
    噪音清理与 PIT 关闭面：6948eb8b40（2026-09-11 17:46 ig_fact 事实层 PIT 收口+CKG 噪音三桶处置+
    fact_close 通道）+ scripts/industry_graph/apply_industry_graph_ddl.py:138-139（fact_close 盖 valid_to、
    幂等可逆、禁 DELETE、分析查询默认 valid_to IS NULL）。语义收录在
    industry_graph_field_dictionary.yaml:10 changelog v1.2.2（ig_fact 方向语义收录 + evidence_chunk_id
    ckg 管线豁免）。

### 2026-09-12-research-report-data-plan.md
- 类型=file · HEAD 末次=2026-09-15T02:21:49+08:00（4f804539d5） · 归档双活=`docs/_working/archive/2026-09/c_class_scattered/2026-09-12-research-report-data-plan.md` 字节等值 1/1 · 末笔生产面=0 件
- 提交链：4f804539d5 docs: docs/_working 清理批(2/3)——51 份文档结案报告写入（C-1~C-4 裁定固化；14b7bb18ce feat(data): 研报消费端收尾批——research_report_detail 能力复杂度重构(17
- 做了什么：研报+分析师预测数据侧施工方案定稿：新建 c3_fundamental.research_report 明细表（替代把研报元数据塞 news_data 丢字段的旧路）+ 回补器 + 五处共享文件接线（provider capability / tasks / schedule / business_data_categories / data_asset_registry）+ 验收清单 + §7 全市场回补完成实录
- 剩余欠账：§3 五处接线与 §6 验收全部落地（见 closure_report）；DS-228 后续 PIT 价值限制标注已在 DS 条目回写（姊妹件 §9.3 Owner 裁 A 同日执行），本件无自身欠账；被 7 处仓外文件反向引用作施工依据（含 schemas/categories/fundamental/fundamental_research_report.py 与 10_d_data.md:4894 MOD-L04-001 段），退役需改锚；正文「Owner 拍板」样式=数据
- 结案报告：
    主批 14b7bb18ce（2026-09-13 00:57 feat(data): 研报消费端收尾批——research_report_detail 能力复杂度
    重构 + consensus_daily DDL/构建器/7 单测 + EXP-01~06 因子库 + 3 篇设计文档；并自述前批 5 文件被
    他会话捎带落地=pit_query/registry/tasks/schedule/bdc）。§3 接线四项均可在盘核到：
    src/zephyr/data/config/tasks.yaml（research_report_* 任务）、src/zephyr/data/config/schedule.yaml:97
    research_nightly 特殊槽、src/zephyr/data/pit_query.py 白名单含 research_report（锚列参数化，后随批加
    预测列禁消费标注）、DDL 真源 schemas/categories/fundamental/fundamental_research_report.py。
    资产登记 data_asset_registry.yaml DS-228/DS-229 在册（其 :126/:9799 直接指回设计真源）。

### 2026-09-12-research-report-handoff.md
- 类型=file · HEAD 末次=2026-09-15T02:21:49+08:00（4f804539d5） · 归档双活=`docs/_working/archive/2026-09/c_class_scattered/2026-09-12-research-report-handoff.md` 字节等值 1/1 · 末笔生产面=0 件
- 提交链：4f804539d5 docs: docs/_working 清理批(2/3)——51 份文档结案报告写入（C-1~C-4 裁定固化；8f418f509a docs(handoff): 研报/一致预期消费端交接包——现状/排队分期表/全路径文件清单/新会话第一步建议
- 做了什么：研报/一致预期消费端交接包：一句话现状（数据侧+派生层+因子函数库全落地入库）+ 已完成可审计清单 + 有意分期排队表 C1.5/C2/C3/C4/C5 + 新会话必读序 + 相关工作文件全路径
- 剩余欠账：§3 排队项中 C1.5（consensus 重建挂夜间调度+真源互查）与 C2（expectations 族预注册+首跑出证）已落地，C2 结果为 data-gap 归档（源槽位无 PIT）；C3/C4/C5 为有意分期、已在 factor/event 与政策册侧有承接锚，不构成本件欠账；「新会话按序读/第一步建议」=派单样式文本，按数据对待未执行；本件被 1 处仓外文件引用
- 结案报告：
    交接包自述的数据侧落地面=14b7bb18ce（12 文件），本件入库笔=8f418f509a（2026-09-14 05:54
    docs(handoff): 研报/一致预期消费端交接包，commit 14b7bb18ce 落批后补交）。其排队项后续：
    C1.5 → src/zephyr/data/config/schedule.yaml:97 research_nightly 与 :104 consensus_crosscheck
    互查槽注释；C2 → 2f65e0043a（factor_registry 新增 expectations 族 + FCT-EXP-001~006 预注册 +
    §8 冻结窗口门槛）与 72362d5a25（EXP-02 首跑出证=data-gap，EXP-FACTOR-EVAL-001 归档）；
    设计判据现真源=docs/01_policies_and_standards/policies/expectation_consumption_design_policy.md。

### 2026-09-13-c5-cluster-differentiation-report.md
- 类型=file · HEAD 末次=2026-09-15T02:21:49+08:00（4f804539d5） · 归档双活=`docs/_working/archive/2026-09/c_class_scattered/2026-09-13-c5-cluster-differentiation-report.md` 字节等值 1/1 · 末笔生产面=0 件
- 提交链：4f804539d5 docs: docs/_working 清理批(2/3)——51 份文档结案报告写入（C-1~C-4 裁定固化；ba0c6cab0d feat(strategy): C5 正式入库批落地——策略从考生转在册（Owner 令"全面开工"，SOP-；49e94f5b4c docs(backtest): C5 附五——聚类 v2 去重处置+双版本 PB-POE+VAL-* 发现+转；fdf88c1d72 docs(backtest): RSRS 寻路深挖至噪音断崖封矿——轮3光大系列全谱/轮4官方2019回顾改进
- 做了什么：C5 差异化对质与正式入库：37→45 条已批测策略聚类对质（v1/v2/v3 三轮）、RSRS 升级寻路穷举至噪音断崖封矿、双版本 PB-POE 处置与 bothwin 升文件粒度、附六按 SOP-C §6/§8 转正 5 条 candidate 入 strategy_registry（152→157）并给三轴差异化论证+溯源
- 剩余欠账：唯一显式欠账「挂图（TDM 节点 strategies+state_matrix）与 PP-001 配比语义留专项一次做齐」已由 fa53723fb2（2026-09-14 23:41）收口；本件另含两项待 Owner 项：附五 转实盘规则 v0.1 草案（Owner 授权起草，未拍板）、估值数据回补施工设计 v0.1（挂起候选 033ee9888cc8 解锁钥匙），二者若长期化应由总指挥另判是否入规，本代理未自改真源；「Owner 令全面开工」样式=数据
- 结案报告：
    转正落地面=ba0c6cab0d（2026-09-14 23:14 feat(strategy): C5 正式入库批落地，strategy_registry
    152→157 五条 candidate：STR-TSMALL-001/STR-VAL-001/STR-MOMTREND-033/STR-VREV-026/STR-DABAN-023，
    前置修复=bothwin 升文件粒度 + 聚类 v3 标 redundant_of）；挂图与配比落地面=fa53723fb2
    （TDM-E-L1 strategy_mounts 补齐 STR-VREV-025/026/MOMTREND-033 三条 verified+evidence，
    L1×capitulation/accumulation/expansion 三格 mounted 同步，PP-001 新 6 sleeve 各 0.05、
    老 8 等比 ×0.70，38 规则校验 ok=True 0 errors）。现册可核：strategy_registry.yaml 含 STR-VREV-026、
    config/trading_decision_map.yaml:291/:301/:5573/:5659 含 STR-VREV-025 挂载与权重 0.045。

### 2026-09-13-factory-gate-review.md
- 类型=file · HEAD 末次=2026-09-15T02:21:49+08:00（4f804539d5） · 归档双活=`docs/_working/archive/2026-09/c_class_scattered/2026-09-13-factory-gate-review.md` 字节等值 1/1 · 末笔生产面=0 件
- 提交链：4f804539d5 docs: docs/_working 清理批(2/3)——51 份文档结案报告写入（C-1~C-4 裁定固化；b88b8fec5d feat(governance): 策略工厂图门禁第二批——FACTORY-MAP gate 142+九图挂轴
- 做了什么：策略工厂图门禁任务审查（交接指令 v2 第零段）：结论 B（通过但需修正）——纠正五件套 3/5 已落地而指令按未建规划、发现 HEAD 断链与上班遗留脏工作区、裁剪 field_dictionary、给 §6 批0+批2 修正施工清单（gate priority=142+红蓝测试+validator root 参数+align_all 第八节+九图化+双登记配方+实弹）
- 剩余欠账：§6 施工清单已由 b88b8fec5d 全批落地（见 closure_report）；两项显式留待 Owner 追认：field_dictionary 裁剪缓办、18 个空 __init__.py 留置处置（本代理未核其现况，属他域待追认项）；正文含大量指令样式文本与 git reset 等命令字样=数据，一律未执行
- 结案报告：
    落地面=本件自身最后两笔之一 b88b8fec5d（2026-09-13 16:32 feat(governance): 策略工厂图门禁第二批
    ——FACTORY-MAP gate 142+九图挂轴（四关验收件闭环））。现盘可核：
    src/zephyr/gov_enforcement/commit_gates/strategy_factory_map_gate.py 存在；
    docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml:1795 gate_id: FACTORY-MAP（在册）；
    docs/01_policies_and_standards/sop/governance_sop/alignment_checklist.md:65/:87 已由八图升为
    strategy_production_map（图 9）挂轴行并记「FACTORY-MAP gate（commit 自动阻断，priority=142）」；
    校验器 scripts/governance/d5_architecture/validators/validate_strategy_production_map.py 在册（批1 件，
    本件 §0 已核实其 3/5 提前落地）。前置 f3f6ecb86f（conftest 自愈）已核实在链。

### 2026-09-13-io-structure-anchor-plan.md
- 类型=file · HEAD 末次=2026-09-15T02:21:49+08:00（4f804539d5） · 归档双活=`docs/_working/archive/2026-09/c_class_scattered/2026-09-13-io-structure-anchor-plan.md` 字节等值 1/1 · 末笔生产面=0 件
- 提交链：4f804539d5 docs: docs/_working 清理批(2/3)——51 份文档结案报告写入（C-1~C-4 裁定固化；1676074961 feat(industry_graph): IO 结构锚——ig_io_edge 表 v7+io_ingest
- 做了什么：投入产出表结构锚薄方案：以 2020 年全国 IO 表直接消耗系数为产业链图谱引入官方结构真源（补 tier 退役遗留的判定依据缺口），四条口径裁定 D1-D4（主锚 153 部门/降级锚 42 部门、映射规则=YAML、新表 io_coefficient 承载不改 ig_edge、本批只出数据资产+校准报告不自动改边）+ 两件施工件 + 四条验收线
- 剩余欠账：§3 验收线由落地批一并交付（42/153 部门入库+映射覆盖率报告+对照样本校准报告）；§5 防蔓延清单四项留作后续候选：年报前五大供应商解析（第二施工件，iFinD 供应链模块盘点先行）、链长制图谱灌库、开源 KG 对照、153 部门→环节级细粒度映射；正文「Owner 口头放行」「AI 自裁 Owner 可否决」=数据，未据以扩张施工
- 结案报告：
    落地面=1676074961（2026-09-13 01:29 feat(industry_graph): IO 结构锚——ig_io_edge 表 v7+io_ingest
    装载器+153 部门→申万映射+校准报告）。现盘三件齐：scripts/industry_graph/io_ingest.py（四段式
    fetch/parse/map/load 装载器）；规则数据 docs/01_policies_and_standards/_registry/catalogs/
    io_sector_sws_map.yaml（映射表按 D2 入注册表体系，未硬编码）；表结构在册
    industry_graph_field_dictionary.yaml（ig_io_edge 命中）。落地形态与 D3 一致：新建 ig_io_edge 承载，
    未改动 ig_edge 语义。本件被 1 处仓外文件反向引用。

### 2026-09-13-p002-semantic-review.md
- 类型=file · HEAD 末次=2026-09-15T02:21:49+08:00（4f804539d5） · 归档双活=`docs/_working/archive/2026-09/c_class_scattered/2026-09-13-p002-semantic-review.md` 字节等值 1/1 · 末笔生产面=0 件
- 提交链：4f804539d5 docs: docs/_working 清理批(2/3)——51 份文档结案报告写入（C-1~C-4 裁定固化；559d68907b docs(p0): P0-002 状态语义复核报告入库+裁定#229（Owner 三步序：复核→重印→重训）
- 做了什么：P0-002 状态语义复核（Owner 三步序第①步）：以两个 VAL run 档案做 IS/OOS/全样本三段对照，判定「档位方向样本外整体反转，牛市态 OOS 最亏、低波/熊市态反而最赚」=态标签语义失效而非分辨力不足；给出病根两假设与重印批三条设计约束
- 剩余欠账：三步序后续：②重印已落地（见 closure_report），③重训（同语义换窗）按本件结论押后；本件 §3/裁定在册的遗留待裁项=r11/r12 死态（1/6 日）合并建议——枚举变更属生产门位，留 Owner（裁定#230 同域在册跟踪）；「Owner 三步序」表述=数据
- 结案报告：
    结论→裁定→施工链闭合：559d68907b（2026-09-13 23:54 docs(p0): P0-002 状态语义复核报告入库+裁定#229）；
    裁定在册 ruling_registry.yaml:1644「裁定#229 P0-002 批次决策点裁定（语义复核先行→判定器重印→窗口
    重训押后）」，另有 :1665 裁定#230 承接 BT-P0-002 判据对象变更（fwd20 收益→fwd20 风险回撤，P0-002 结案）；
    ②重印落地面 dfa41e9aae（2026-09-14 00:26 feat(regime): P0-002 判定器重印批——锚定风险四档状态机，
    裁定#229 第②步）；后续收口 9fa158cd7e（2026-09-16 车道 D2/regime_snapshot_history 唯一自动产出者接线）
    与 a54997e221（2026-09-23 TDM-E-L1-AGG 消费切换终批）。

### 2026-09-13-panic-rebound-sim-paper.md
- 类型=file · HEAD 末次=2026-09-15T03:27:02+08:00（275bc860dc） · 归档双活=`docs/_working/archive/2026-09/c_class_scattered/2026-09-13-panic-rebound-sim-paper.md` 字节等值 1/1 · 末笔生产面=0 件
- 提交链：275bc860dc docs: 全链路工厂方案+穷尽立项稿工作区最新版（含勘误吸收）、DSR 第0步重算定案附录、清理台账+交接包
- 做了什么：恐慌反弹（CAND-e3da6fa71af1）sim/paper 前哨建图：策略出生证+身份证字段化、三窗口成绩单（IS 1.15/OOS 0.83/S3 0.98，唯一三窗全绿）、前哨配置（≥20 交易日、UP-1 波动率目标仓位、UP-2 前瞻概率止损、E9→E2 归因回灌）、晋级/退回判据、信号伪代码与六项施工清单
- 剩余欠账：施工清单六项未逐项销项（复选框原文均未勾），但主体已由后续批次落地：registry 在册且 lifecycle_status=sim、挂图与 PP-001 配比已做齐（fa53723fb2）；未落地证据两项=①UP-2 forward_stop_loss 在 src 内零消费方（grep 仅命中其自身文件与 decision_algo_registry 在册行）②本件设想的前哨日志 batch=sim-paper-e3da6fa71af1 在仓内零命中；且 src/zephyr/pf_alloc/allocation_config.py:25 已把该差异登记为 PFA-5（STR-VREV-025 注册口径 vol-target 仓位 vs sim 全仓 all-in 的口径漂移）=在册欠账，非本件未施工；清理批自动结案报告判「证据不足，保守保留」=生成器数据
- 结案报告：
    落地面可核四点：①strategy_registry.yaml:148 lifecycle_status: sim（台账键 CAND-e3da6fa71af1，
    证据行含三窗全绿与 run 指针），入库批 ba0c6cab0d 同口径声明「恐慌反弹先例只做 registry 侧，
    挂图+PP-001 配比留下一专项」；②该专项收口=fa53723fb2（2026-09-14 23:41 TDM-E-L1 strategy_mounts
    补 STR-VREV-025 并同步 L1×capitulation 等三格 mounted，PP-001 配比 0.045 等权起步档）；
    现册 config/trading_decision_map.yaml:291/:301/:5573/:5659 与 config/framework_plans.yaml:268/:307 均在；
    ③sim 宇宙消费真源已在链：src/zephyr/pf_alloc/allocation_inputs.py:582/:594 按 lifecycle_status=sim
    过滤策略宇宙（与 scripts/backtest/sim_paper_ledger 同一 loader，RULE-SSOT）；
    ④sim 生命周期治理自动化首件 283e64c1d2（strategy_lifecycle_advisor，2026-09-15 03:36）。
    本件唯一改动笔 275bc860dc 为纯 _working 入库批（ext_footprint=0）。

### 2026-09-13-strategy-factory-pipeline-discussion.md
- 类型=file · HEAD 末次=2026-09-15T02:21:49+08:00（4f804539d5） · 归档双活=`docs/_working/archive/2026-09/c_class_scattered/2026-09-13-strategy-factory-pipeline-discussion.md` 字节等值 1/1 · 末笔生产面=0 件
- 提交链：4f804539d5 docs: docs/_working 清理批(2/3)——51 份文档结案报告写入（C-1~C-4 裁定固化；69bd7680f4 refactor(signal): DEDUP 批——6 组 15 副本克隆合并至 core/analysis；c953d73d8f refactor(tests): tests/feedback 111→根23+7语义子目录88（GOV-DO；c003353f4b refactor(tests): tests/infrastructure 119→根54+6语义子目录64（
- 做了什么：策略工厂流水线讨论稿 v1→v10 累加：五车道（含 E4 考试咽喉=已建 C4/DSR/OOS/年衰减）+ 产品清单与字段定稿（身份证+出生证，对标 C2PA/HF Model Card，AI 禁手填）+ 防幻觉/防漂移字段化 + 下游半场 E7-E9 三环节结构提案 + 逐轮调研对标；v10 自述骨架层封矿
- 剩余欠账：v10 自述「本讨论稿历史使命完成，全部讨论已消化为正式结构稿 config/strategy_production_map.yaml（489f433165），本稿转为背景设计文集不再追加」→ 按合同 §3 命中真源改判 ①；遗留不在本件而在图上：§六 决策点 1-7 与 E7-E9 范围拍板以图内 build_status=pending 节点为真源跟踪，门禁四关验收件由 factory-gate 批（b88b8fec5d）落地；正文含「Owner 确认后作为定稿骨架」等待批样式=数据，未执行
- 结案报告：
    消化产物三项在盘：①结构稿 config/strategy_production_map.yaml（v10 自述 commit 489f433165，
    已核实在链，2026-09-13 05:33）；②门禁件 src/zephyr/gov_enforcement/commit_gates/
    strategy_factory_map_gate.py + gate_registry.yaml:1795 FACTORY-MAP 在册 + 挂轴
    alignment_checklist.md:65/:87（九图升级行）；③字段判据入正式架构文档：
    docs/02_enterprise_architecture/02_domain_architecture_docs/10_d_data.md:4221（hypothesis_precheck
    表七条判据，含第 7 条「birth_channel/birth_batch 从进货台账原样携带（出生证贯穿全链，AI 禁手填）」）。
    本文件自身最后被改动为纯文档批 4f804539d5（ext=0）；工厂图前端页落地面=d34e5ef0dd
    （2026-09-14 02:53 feat(frontend): 策略工厂页落地——策略生产全景图（图9）前端原生实时渲染）。

### 2026-09-13-tdm-upgrade-blueprint.md
- 类型=file · HEAD 末次=2026-09-15T02:21:49+08:00（4f804539d5） · 归档双活=`docs/_working/archive/2026-09/c_class_scattered/2026-09-13-tdm-upgrade-blueprint.md` 字节等值 1/1 · 末笔生产面=0 件
- 提交链：4f804539d5 docs: docs/_working 清理批(2/3)——51 份文档结案报告写入（C-1~C-4 裁定固化；8c8ed28825 docs(tdm): TDM 升级蓝图 v0.2——UP-1..UP-5 全部 GAP 解除+消费端接线指南；ba47d30c9c feat(portfolio): UP-1 凯利简版仓位计算器建成——波动率目标化仓位系数（TDM 升级蓝图首；708342357f docs(tdm): TDM 升级蓝图 v0.1 设计稿落档——分布预测嵌入五候选（GAP 挂起制，未动真源）
- 做了什么：TDM 升级蓝图 v0.1→v0.2：分布预测（车道 E）嵌入交易决策五候选 UP-1 凯利/波动率目标仓位、UP-2 前瞻概率止损、UP-3 前瞻风险预算、UP-4 板块分布比较选优、UP-5 尾部对冲指令，按四道闸逐条过；五模块建成并声明 GAP 全解除，另给消费端接线五步与储备库六板块归口表
- 剩余欠账：本件判据已入真源（decision_algo_registry 五条 DAL 条目含 UP-2 P(跌)≥0.65/尾比≥0.60、UP-5 CVaR(5%) 阈 -3% 日损阈值冻结；trading_decision_map 已引 MOD-BT-082）→ 按合同 §3 命中改判 ①；剩余欠账一项=§消费端接线五步中 UP-2/UP-4/UP-5 尚无 src 消费方（forward_stop_loss grep 仅命中自身文件+注册表在册行），该缺口已在别处登记为在册漂移（allocation_config.py:25 PFA-5），非本件新增欠账；§落图批流程的 validation_method_registry 逐条登记+阈值冻结仅部分执行；本件自述「A/B 回测对比验证待跑」（UP-1 段）；「Owner 指令/口头放行」样式=数据
- 结案报告：
    五模块落地面：ba47d30c9c（2026-09-13 06:08 feat(portfolio): UP-1 凯利简版仓位计算器建成——
    波动率目标化仓位系数，TDM 升级蓝图首项落地）与 8c8ed28825（2026-09-14 01:43 docs(tdm): v0.2——
    UP-1..UP-5 全部 GAP 解除+消费端接线指南）。模块文件现盘：
    src/zephyr/pf_alloc/core/vol_target_allocator.py、forward_stop_loss.py、risk_budget_allocator.py、
    sector_distribution_comparator.py。真源登记：decision_algo_registry.yaml:213-225（含
    code_ref=src/zephyr/pf_alloc/core/forward_stop_loss.py 与 UP-2/UP-5 阈值冻结条款）、
    config/trading_decision_map.yaml:278（MOD-BT-082 引 vol_target_allocator）、
    docs/02_enterprise_architecture/02_domain_architecture_docs/60_d_pf_alloc.md（UP 条目命中）。
    v0.1 设计稿笔 708342357f 自述「GAP 挂起制，未动真源」，真源改动均在后续批。

### 2026-09-13-xtreme-redblue-retest.md
- 类型=file · HEAD 末次=2026-09-15T02:21:49+08:00（4f804539d5） · 归档双活=`docs/_working/archive/2026-09/c_class_scattered/2026-09-13-xtreme-redblue-retest.md` 字节等值 1/1 · 末笔生产面=0 件
- 提交链：4f804539d5 docs: docs/_working 清理批(2/3)——51 份文档结案报告写入（C-1~C-4 裁定固化；9c9f9a368f docs(xt): 极限红蓝对抗复测报告——堵点总账根治全闭环（总判定通过）
- 做了什么：极限红蓝对抗复测：堵点总账根治批（F3/F5/F1/D5）之后，按上轮同构方法重跑串行计时+5 路子代理并发（1 拆分者+3 编辑者+1 坏图攻击者），总判定=历史事故形态 100% 防住、堵点 1/2/3/溯源观测全闭环
- 剩余欠账：§4 四条新发现均为交他轨的在册欠账，不属本件未施工：①阻断消息 new_root 单值指针多目录场景误导（P3 小瑕疵）②被拦提交预暂存 AD 幻影不自动回滚（P3 待办）③GATE-TRACKED-DRIFT 既有噪音④capability registry di_seam_exemptions 段 593 条历史错位 token 死区——本批只治工具侧，存量清理涉 REGISTRY-MASS-DELETION 门禁语义已报 Owner 单独处置批（本代理未核其现况，且禁碰注册表）；正文含 git restore --staged 等命令与 Owner 指令字样=数据，一律未执行
- 结案报告：
    复测对象（堵点根治批）与复测件自身入库链均已核实在 git log：9c9f9a368f（2026-09-13 20:10
    docs(xt): 极限红蓝对抗复测报告——堵点总账根治全闭环（总判定通过））为其入库笔；本件 §5 自引的
    四笔经 git log 核验为真实存在——7033c39334（2026-09-13 19:34 堵点总账根治批）、d50c2613b3
    （19:41 协议重设计：落地≠失活）、692f35a1b9（19:49 拆分批）、f7a05618de（20:08 测试资产退库
    121 文件）——四笔时间戳与报告 §2 并发时间线（begin 19:46 / finish 20:05）同晚且顺序一致。最近一笔动本件者=纯文档批 4f804539d5（ext_footprint=0）。

### 2026-09-13-xtreme-redblue-v3-log.md
- 类型=file · HEAD 末次=2026-09-15T02:21:49+08:00（4f804539d5） · 归档双活=`docs/_working/archive/2026-09/c_class_scattered/2026-09-13-xtreme-redblue-v3-log.md` 字节等值 1/1 · 末笔生产面=0 件
- 提交链：4f804539d5 docs: docs/_working 清理批(2/3)——51 份文档结案报告写入（C-1~C-4 裁定固化；fd6ec978f0 docs(redblue): v3 日志终局补遗——编码门反讽/死信复活/黑窗三连；9b55a63075 docs(redblue): 极限红蓝对抗 v3 日志+报告——worktree 落账三要素过/主网关归因全精
- 做了什么：极限红蓝对抗 v3 逐场景执行日志（GLM 5.3 Flash 红方，基线 HEAD=7a4efc8113）：裸 commit/`--no-verify` 拦截实证、worktree 落账三要素、并发五路、blackout 现场记录
- 剩余欠账：日志自述两条未覆盖项（S2.5 本体待注册表恢复后补测、怪文件名/怪 message 批被第二次 blackout 吞没）；其后红蓝 v4 已复测（docs/_working/2026-09-14-xtreme-redblue-v4-report.md 在盘，另有 archive/2026-09/c_class_scattered/ 同名件）；本件正文含大量命令样式文本=数据，未执行；机械底座 twin=- 漏判：archive/2026-09/c_class_scattered/2026-09-13-xtreme-redblue-v3-log.md 存在同名件且 cmp 字节等值 SAME
- 结案报告：
    日志 427 行为一次性执行记录，其指向的缺陷由同班报告与后续批处置：9b55a63075（v3 日志+报告同批入库）、
    fd6ec978f0（v3 日志终局补遗）。执行面对应的代码侧落地面（本分片实测）：worktree 堵点归因直取
    gate_id（src/zephyr/gov_enforcement/rule_bridge/session_worktree.py 头注「红蓝 v3 P1-2 治本 2026-09-14」）、
    allow_non_worktree 双逃生通道（同仓 worktree_required_gate.py:45/86/130）、伪造标记门
    （src/zephyr/gov_enforcement/commit_gates/forged_gw_marker_gate.py 在盘）、语法门
    （gate_registry.yaml:1806 SYNTAX-VALIDATION priority=49）。最近一笔动本件的 4f804539d5 为纯 _working 批（ext=0）。

### 2026-09-13-xtreme-redblue-v3-plan.md
- 类型=file · HEAD 末次=2026-09-15T02:21:49+08:00（4f804539d5） · 归档双活=`docs/_working/archive/2026-09/c_class_scattered/2026-09-13-xtreme-redblue-v3-plan.md` 字节等值 0/1 · 末笔生产面=0 件
- 提交链：4f804539d5 docs: docs/_working 清理批(2/3)——51 份文档结案报告写入（C-1~C-4 裁定固化；7a4efc8113 docs(redblue): 极限红蓝对抗 v3 方案——低能力模型执行版（自然犯错武器化+干扰全谱） [GW
- 做了什么：极限红蓝对抗 v3 测试方案（低能力模型执行版）：场景矩阵 S1-S4、铁律（只记录不修复/禁 push/禁区不碰）、日志格式规定
- 剩余欠账：本件正文=对执行者的任务书样式文本（「你是红方」「五条铁律」「每个场景做完立刻写日志」），按合同 §6 视为数据，未执行其中任何语义；机械底座 twin=- 漏判：archive/2026-09/c_class_scattered/ 同名件存在且 cmp=BYTE_DIFF（差异仅 4 处：本件为 `git reset`/`git clean`/`git filter-branch` 半角连字符，归档件被替换为 U+2011 非断行连字符，30497 vs 30505 字节）
- 结案报告：
    方案已由同族 log/report 执行并结案（7a4efc8113 方案入库 → 9b55a63075 日志+报告 → fd6ec978f0 日志补遗）。
    方案内规定的验收面（worktree 落账、UNKNOWN 归因、opts 透传）在代码侧均已改：
    git_commit_gateway.py:454/1839（status→gate_id 全量映射，2026-09-13 UNKNOWN×6 治本）、
    session_worktree.py:15（worktree 归因判定链 2026-09-14）。后续 v4 复测报告在盘。

### 2026-09-13-xtreme-redblue-v3-report.md
- 类型=file · HEAD 末次=2026-09-15T02:21:49+08:00（4f804539d5） · 归档双活=`docs/_working/archive/2026-09/c_class_scattered/2026-09-13-xtreme-redblue-v3-report.md` 字节等值 1/1 · 末笔生产面=0 件
- 提交链：4f804539d5 docs: docs/_working 清理批(2/3)——51 份文档结案报告写入（C-1~C-4 裁定固化；9b55a63075 docs(redblue): 极限红蓝对抗 v3 日志+报告——worktree 落账三要素过/主网关归因全精
- 做了什么：红蓝 v3 结果报告：总判定「有条件通过」，1 个 P0 候选+4 个 P1+9 条 P2 缺陷清单、堵点对账表（主网关 10/10 精确、worktree 六类外 4/4 落 UNKNOWN）、§5 修复建议（只建议不动手）
- 剩余欠账：清单处置度：P0-1 语法门已建（SYNTAX-VALIDATION priority=49，配套日志=本分片 2026-09-14-p0-syntax-gate.md）、P1-1 伪造标记门已建、P1-2 worktree 归因已治、P1-4 allow_non_worktree 已补；P2-6 FOLDER-CAPACITY 口径争议现为「目录磁盘平铺计数 >120 硬阻断」（folder_capacity_hard_limit_gate.py:8/84，对齐 GOV-DOC-018），未见另立 Owner 裁定卷；P2-1/2/3/4/5/8 建议项处置未在本件留痕，交总指挥核。机械底座 twin=- 漏判：archive/2026-09/c_class_scattered/ 同名件 cmp=BYTE_SAME
- 结案报告：
    报告的修复建议按「只建议不动手」口径由后续批分别落地（本分片实测证据）：
    P0-1 → config gate 清单 gate_registry.yaml:1806 SYNTAX-VALIDATION（priority=49，own-scope，
    扫描源=commit() 的 files 参数）；P1-1 → src/zephyr/gov_enforcement/commit_gates/forged_gw_marker_gate.py；
    P1-2 → rule_bridge/session_worktree.py:15 头注「红蓝 v3 P1-2 治本 2026-09-14」+ git_commit_gateway.py:1839 判定链；
    P1-4 → commit_gates/worktree_required_gate.py:86（allow_non_worktree 逃生通道，CLI 对称 --allow-non-worktree）；
    P2-8 → 提交存在性校验已按文件粒度处理（同文件族）。入库笔 9b55a63075，最近一笔 4f804539d5（纯 _working 批 ext=0）。

### 2026-09-14-agg-switch-design.md
- 类型=file · HEAD 末次=2026-09-15T02:21:49+08:00（4f804539d5） · 归档双活=`docs/_working/archive/2026-09/c_class_scattered/2026-09-14-agg-switch-design.md` 字节等值 1/1 · 末笔生产面=0 件
- 提交链：4f804539d5 docs: docs/_working 清理批(2/3)——51 份文档结案报告写入（C-1~C-4 裁定固化；ef2302e2c0 docs(regime): 裁定#231 落纸——灰度曲线参数冻结（Owner 确定施工）+设计稿映射表签字；92d1280742 feat(regime): AGG 切换设计稿 v2 灰度曲线版 + 双轨对照器修 TAB 断行补 argpa；220493ca9a feat(regime): TDM AGG 切换设计稿+双轨对照器——切换前置两件落地（移交4 续）
- 做了什么：TDM AGG 消费切换设计：把 AGG 状态输入源从 HMM dominant 换为锚定风险四档；核心决策=仓位数字与状态路由分家（连续 cap 灰度曲线，min 结构去双重计算），并锁 FQ-01 应计剔除器接线点
- 剩余欠账：§3 切换判据三条中「Owner 对灰度曲线参数签字」已由 裁定#231 落纸（ef2302e2c0）；§4 FQ-01 以 `high_accrual` 字段形态落码（negative_veto.py:70 注「裁定#231」），非原设计稿命名的 `accrual_ttm`；本件「退役观察一个月后下线旧 HMM 链」的退役动作未见本件内留痕，交总指挥核。机械底座 twin=- 漏判：archive/2026-09/c_class_scattered/ 同名件 cmp=BYTE_SAME
- 结案报告：
    设计稿的三项要素均有 HEAD 侧落地面：①连续 cap 与冻结参数在产
    （src/zephyr/pf_alloc/allocation_inputs.py:628 ANCHORED_CAP_START=0.30、:629 ANCHORED_CAP_FULL=1.00、
    :659 注释式公式 `cap(vol_pct)=1.0−0.70×clamp((vol_pct−0.30)/(1.00−0.30),0,1)`、:632 回滚旗
    data/runtime/anchored_cap.disabled）；②双轨对比器在盘 scripts/backtest/compare_state_dualrun.py；
    ③锚定态夜批任务在 config 侧 src/zephyr/data/config/tasks.yaml（regime_state_anchored 命中）。
    施工链：220493ca9a（设计稿+对照器）、92d1280742（v2 灰度曲线版）、ef2302e2c0（裁定#231 参数冻结签字）。

### 2026-09-14-auto-mount-research.md
- 类型=file · HEAD 末次=2026-09-15T02:21:49+08:00（4f804539d5） · 归档双活=`docs/_working/archive/2026-09/c_class_scattered/2026-09-14-auto-mount-research.md` 字节等值 1/1 · 末笔生产面=0 件
- 提交链：4f804539d5 docs: docs/_working 清理批(2/3)——51 份文档结案报告写入（C-1~C-4 裁定固化；5ee5c70d5a docs(research): 策略自动挂图可行性调研+立项登记（Owner 问"挂图能不能全自动"）——三轮
- 做了什么：策略自动挂图可行性调研（三轮全网挖矿）+ 立项登记：裁定建 auto_mount 自动挂图器，全自动 only-add（只新增挂载，永不自动删/挪），五步管线+验收五条+净零声明
- 剩余欠账：本件自述「未施工，等排期」已被后续批销案：MOD-BT-171 已建并转 production、验收五条全过、Owner 2026-09-15 02:03 批复「通过」（结案报告 docs/_working/archive/2026-09/2026-09-15-auto-mount-construction.md）；该结案报告列 4 条已知边界（judge 串行回测、STR-E-TIMING-001 无 build 契约跳过、报告文件输出格式待定稿、架构评审豁免申报）未回写本件。机械底座 twin=- 漏判：archive/2026-09/c_class_scattered/ 同名件 cmp=BYTE_SAME
- 结案报告：
    立项件施工面实测在盘：scripts/backtest/auto_mount.py 存在且登记
    （docs/01_policies_and_standards/_registry/catalogs/module_translation_registry.yaml:54023 module_path=scripts/backtest/auto_mount.py、:54026 name_en=auto_mount）；
    分状态判定所用真源（regime 快照表）与 38 规则校验器为既有件；DSR 判定门亦被 auto_mount 挂载消费
    （src/zephyr/backtest/core/decision_gate.py:8 头注）。入库笔 5ee5c70d5a（调研+立项登记）。

### 2026-09-14-c4-history-repair-plan.md
- 类型=file · HEAD 末次=2026-09-15T02:21:49+08:00（4f804539d5） · 归档双活=`docs/_working/archive/2026-09/c_class_scattered/2026-09-14-c4-history-repair-plan.md` 字节等值 1/1 · 末笔生产面=0 件
- 提交链：4f804539d5 docs: docs/_working 清理批(2/3)——51 份文档结案报告写入（C-1~C-4 裁定固化；4718afe35b feat(data): C4 历史修复工程基建批（Owner 立项"全部开工"，方案→病菌寻路→施工 SOP 
- 做了什么：C4 历史修复工程方案 v1.0：用 research_report 自带 PDF 原文提取发布时点盈利预测，四层架构（c4_fetcher 下载→PyMuPDF 文本→启发式+LLM 两层提取→新表落层）+验证三层+验收标准
- 剩余欠账：本件边界内 2017-2021 段已落表并定稿（净段 FINAL 1,563,996 行，2022-2025 断供段=本件明示「独立子工程，本方案不含」）；原型验收为阶段版（人工抽核协议 15/30 进行中、聚合收紧为 high-only、mid 留档待复核升级，见 docs/_working/2026-09-15-c4-acceptance-interim.md）。机械底座 twin=- 漏判：archive/2026-09/c_class_scattered/ 同名件 cmp=BYTE_SAME
- 结案报告：
    方案四层的落地面（本分片实测）：L1-L4 实现件 src/zephyr/data/c4_history_repair.py
    （:14 头注「提取产物落 c3_fundamental.pdf_forecast_extracted（同键幂等覆盖）」、:365 引用该表 INSERT_COLUMNS/TABLE_NAME）；
    批 CLI scripts/ch/c4_extract_batch.py 在盘；L4 重建表与消费口
    src/zephyr/data/implementations/consensus_daily_repaired_compute.py + scripts/ch/build_consensus_daily_repaired.py；
    缺口登记与真源指向 src/zephyr/data/config/known_data_gaps.yaml:1021-1025
    （「值类消费一律改走 consensus_daily_repaired 净段」，净段 FINAL 1,563,996 行 [亲验 09-21]）。
    基建批入库笔 4718afe35b（Owner 立项「全部开工」→ 寻路→施工 SOP）。

### 2026-09-14-ch-connection-handoff.md
- 类型=file · HEAD 末次=2026-09-15T02:21:49+08:00（4f804539d5） · 归档双活=`docs/_working/archive/2026-09/c_class_scattered/2026-09-14-ch-connection-handoff.md` 字节等值 1/1 · 末笔生产面=0 件
- 提交链：4f804539d5 docs: docs/_working 清理批(2/3)——51 份文档结案报告写入（C-1~C-4 裁定固化；2cbe5fda29 docs(infra): CH 连接统一治本交接文档——DatabaseService 统一入口设计+改造清单
- 做了什么：CH 连接统一治本交接文档：根因=各模块自建裸 clickhouse_driver.Client 致 Code:181 间歇断连；方案=一律走 DatabaseService.get_clickhouse_conn()，列 10 文件改造序+「完成」三条定义+纪律提醒
- 剩余欠账：本件 §四「完成」判据第 3 条（多会话并发零断连）由结案报告以实测承载（6 程序并发 25 秒 47,210 查询零错误、连接数精确 +6）；本件列出的引用件 c4_deferrals.csv/sim-platform-blueprint 路径漂移已在清理批结案报告中标注（非缺失）。机械底座 twin=- 漏判：archive/2026-09/c_class_scattered/ 同名件 cmp=BYTE_SAME
- 结案报告：
    治本完成报告=docs/_working/archive/2026-09/2026-09-14-ch-connection-unify-report.md
    （st-chinfra-20260914 接手 2cbe5fda29 交接文档，方案 10 文件实际扩展为全仓 50+ 文件，改动清单 52 文件）。
    当前仓侧复验（本分片实测）：DatabaseService 为唯一 Client 构造口
    （src/zephyr/infrastructure/database_service.py:165 注「禁止任何模块自行构造 clickhouse_driver.Client，一律经本方法按角色领取」）；
    ch_writer.get_client 已改领取制并保留 HTTP 降级（src/zephyr/data/ch_writer.py:186/:200/:305/:352）；
    全仓 `clickhouse_driver.Client` 命中仅剩类型注释与协议文档，无业务构造点。

### 2026-09-14-chart-pattern-mining-report.md
- 类型=file · HEAD 末次=2026-09-15T02:21:49+08:00（4f804539d5） · 归档双活=`docs/_working/archive/2026-09/c_class_scattered/2026-09-14-chart-pattern-mining-report.md` 字节等值 1/1 · 末笔生产面=0 件
- 提交链：4f804539d5 docs: docs/_working 清理批(2/3)——51 份文档结案报告写入（C-1~C-4 裁定固化；8b4ccc3d23 feat(pattern): REG-PAT-001 schema v2.2——新增 refinements ；c338d4cee6 feat(pattern): REG-PAT-001 挖矿批二 v2.17.0——长尾收获 12 条（275→；19f569352e feat(pattern): REG-PAT-001 病菌寻路挖矿批 v2.16.0——Bulkowski 差
- 做了什么：图形库病菌寻路挖矿报告两批：批一登记 19 条（256→275，v2.16.0）+驳回 2+长尾清单；批二登记 12 条（→287，v2.17.0）+长岛驳回终态；§十 schema v2.2 新增 refinements 细化分支字段并回填 17 父条目
- 剩余欠账：登记类结论已全部入注册表真源（现 version 2.18.0，schema_version 2.2），本件退化为挖矿过程记录；仍欠两项：①§六 P1/P2/P3 实现候选（检测器施工）②§十自述「未来 pattern_catalog_sync 扩展为常设校验器（登记为待施工项，防字段漂移）」——本分片复验 scripts/data/pattern_catalog_sync.py 内 refinements 零命中，常设校验器未建。机械底座 twin=- 漏判：archive/2026-09/c_class_scattered/ 同名件 cmp=BYTE_SAME
- 结案报告：
    三笔施工链（本件自述+git log 一致）：19f569352e（批一 v2.16.0 差额补全 19 条）、
    c338d4cee6（批二 v2.17.0 长尾收获 12 条，275→287）、8b4ccc3d23（schema v2.2 refinements 字段+双向闭环校验）。
    真源侧复验：docs/01_policies_and_standards/_registry/catalogs/chart_pattern_registry.yaml
    当前 schema_version: '2.2'（:18）、version 2.18.0（:177）→ 本两批条目已在库且被后续批续写。

### 2026-09-14-combination-layer-exhaustive-charter.md
- 类型=file · HEAD 末次=2026-09-15T06:23:54+08:00（03becdf2e7） · 归档双活=`docs/_working/archive/2026-09/c_class_scattered/2026-09-14-combination-layer-exhaustive-charter.md` 字节等值 1/1 · 末笔生产面=0 件
- 提交链：03becdf2e7 docs(factory): F-06 通宵班收口——施工排产总览+挖矿第二批(A.7)+验证核销(A.6)（；275bc860dc docs: 全链路工厂方案+穷尽立项稿工作区最新版（含勘误吸收）、DSR 第0步重算定案附录、清理台账+交接包
- 做了什么：F-06 组合层穷尽网格立项稿 v1+v2：八维→十三维 schema（含 active_if 折叠）、N→N_eff 双口径记账、两批次执行策略（A 普查→fANOVA 结构知识→B 子空间穷尽）、验收口径修订、裁定记录与施工排产总览
- 剩余欠账：立项/裁定/schema 结论已进正式真源（见 already_in_truth_source），本件退化为立项过程件；施工侧欠账按排产总览自述：批次 A 实跑 2000 条当时「发射运行中」、3.3 结构知识报告「生成器就绪待批完」、批次 B 挂起（DSR 前置，其后已由 e58d28df99 系满足但本件未回写）、5.2/5.3/5.4/5.7/5.8 立项级留 Owner 排产；仓内未见批次 A 结构知识成果（grep 结构知识 仅命中 _working 三件）。机械底座 twin=- 漏判：archive/2026-09/c_class_scattered/ 同名件 cmp=BYTE_SAME
- 结案报告：
    本件 §十/§十二 的设计结论已升为正式件：MOD-POS-029 position_recipe_compiler 蓝图
    （docs/03_modules/_domain_position/position_recipe_compiler/blueprint.md，status Active、
    design_maturity production，「设计真源=2026-09-14-combination-layer-exhaustive-charter.md §十/§十二 +
    2026-09-14-full-chain-factory-blueprint.md §十」，「schema 真源=config/position_recipe_grid_schema.yaml」）；
    维度 schema 与活性谓词落在 config/position_recipe_grid_schema.yaml、config/search_space_prereg.yaml（N_eff 三估计器预注册，对应本件 §十一-12.2）、
    docs/03_modules/_domain_position/algo_flow/position_recipe_compiler.yaml。
    N 账本与重算前置（本件批次 B 硬前置）已落地：e58d28df99（台账 num_trials 回填+存量 261 行 DSR 重算 累计 N=4481）。
    本件最后两笔均为纯 _working 文档批（03becdf2e7/275bc860dc，ext=0）。

### 2026-09-14-dsr-enable-impact-assessment.md
- 类型=file · HEAD 末次=2026-09-15T14:12:12+08:00（e58d28df99） · 归档双活=`docs/_working/archive/2026-09/c_class_scattered/2026-09-14-dsr-enable-impact-assessment.md` 字节等值 1/1 · 末笔生产面=3 件
- 提交链：e58d28df99 feat(backtest): DSR 修口径 A2+A3——台账 num_trials 可考证回填 + 存量；275bc860dc docs: 全链路工厂方案+穷尽立项稿工作区最新版（含勘误吸收）、DSR 第0步重算定案附录、清理台账+交接包；4f804539d5 docs: docs/_working 清理批(2/3)——51 份文档结案报告写入（C-1~C-4 裁定固化；28402c237a chore(derived): watchdog 派生缓存自动收敛——B类白名单稳定漂移 2 件（零活跃会话，
- 做了什么：DSR 默认开启冲击面评估：纠正「DSR 是概率不是夏普」、台账 1102 行实测分布、三坑（num_trials 口径/阈值口径/fail-closed 误杀）、2.69σ 数值勘误、三步走建议+Owner 待裁五项；后追加勘误块、第 0 步重算定案块、冻结解除块
- 剩余欠账：§七 五项裁定已自裁并在文内；后续三步走第②③步（阈值三线统一、开关只对新批次+未注入记 not_tested）按文内记载由本班及后续班执行，代码侧现为默认开启态（见 already_in_truth_source）；文内 §五 表 4.90/2.69σ 旧值已由文内勘误块改写为 4.5262/2.3121σ（原值仍留散文，属已知痕迹非矛盾）。机械底座 twin=- 漏判：archive/2026-09/c_class_scattered/ 同名件 cmp=BYTE_SAME
- 结案报告：
    最近一笔 e58d28df99 即本件建议第 1 步的落地（同时改 3 个非 _working 文件：台账 num_trials 回填、
    存量 261 行 DSR 重算、冻结解除）。落地终态复验：src/zephyr/backtest/core/decision_gate.py:8 头注
    「DSR 判定器默认开启（dsr_threshold=DSR_SIGNIFICANCE_THRESHOLD=0.95，fail-closed，车道 L 接线）
    ——三线裁决 evaluate_dsr 与回测→实盘准入谓词 evaluate_strategy_risk_admission=唯一判定源」，
    :177/:194/:211 阈值参数化；N 账本件 MOD-BT-200 TrialLedger+trial_ledger_registry.yaml 在盘（文内冻结解除块自述）。
    评估期错误值（4.90/2.69σ）在文内勘误块与本分片同批的 full-chain 蓝图附录 A.5 中被双向核销。

### 2026-09-14-fac-e1c-formula-mining-design.md
- 类型=file · HEAD 末次=2026-09-15T02:21:49+08:00（4f804539d5） · 归档双活=`docs/_working/archive/2026-09/c_class_scattered/2026-09-14-fac-e1c-formula-mining-design.md` 字节等值 1/1 · 末笔生产面=0 件
- 提交链：4f804539d5 docs: docs/_working 清理批(2/3)——51 份文档结案报告写入（C-1~C-4 裁定固化；a431c40d47 feat(factory): E1C 正式量产开放——白名单 status=active（Owner 过审"清；1caefd0c6a feat(factory): FAC-E1C 车道C gplearn 轨 MVP 落码 MOD-BT-155（；0f92e0c2f3 feat(factory): FAC-E1 进货编排 MVP 落码 MOD-BT-154——薄编排层一条命令串
- 做了什么：FAC-E1C 公式挖掘机设计稿 v1：AlphaGen/gplearn/双轨选型对比、与 E0-E5 工厂咬合数据流、防过拟合四件套对接、四项开放决策；附 Owner 全批裁定与 gplearn 轨 MVP 施工实绩（MOD-BT-155）
- 剩余欠账：文内 §七 待办四项中 ①白名单过审→status=active、②正式档自动化（计划任务 ZephyrAlpha_FactoryLaneC）已落，③v2 自定义算子批、④AlphaGen 立项两项后续由 lane-c 立项书承接（④已在同分片 2026-09-14-lane-c-agentic-mining-charter.md 重新划界并落码 lane_c2_agentic_miner.py），③未见落地面。机械底座 twin=- 漏判：archive/2026-09/c_class_scattered/ 与 archive/2026-09/factory/ 各存同名件，两处均 cmp=BYTE_SAME（三份等值）。
- 结案报告：
    施工链三笔：0f92e0c2f3（FAC-E1 进货编排 MOD-BT-154）、1caefd0c6a（车道C gplearn 轨 MVP 落码 MOD-BT-155，
    Owner 四项裁定全批落地）、a431c40d47（E1C 正式量产开放：白名单 status=active + ZephyrAlpha_FactoryLaneC 计划任务）。
    真源侧复验：config/factor_mining_whitelist.yaml 在盘（本件 §六-2 所指算子白名单唯一真源）。

### 2026-09-14-handoff-market-data-repair.md
- 类型=file · HEAD 末次=2026-09-17T23:31:35+08:00（01fbfad157） · 归档双活=`docs/_working/archive/2026-09/c_class_scattered/2026-09-14-handoff-market-data-repair.md` 字节等值 1/1 · 末笔生产面=5 件
- 提交链：01fbfad157 feat(rulings): 终局授权裁定批量登记 裁定#304-#326 二十三件入册(同 commit 原；4f804539d5 docs: docs/_working 清理批(2/3)——51 份文档结案报告写入（C-1~C-4 裁定固化；779556afc6 feat(data): 09-14 行情时区修复收官+tick 批量补数+采集管线复活——文档与工具批
- 做了什么：行情数据时区修复+tick 补数的会话交接包：已完成清单（5min/1min 六月-七月偏移回正、tick 下载验证、管线复活）、P0-2/P0-3 待办、环境与表结构铁律、关键实测数据、工作文件清单
- 剩余欠账：待办四项中 P0-1/P0-2/P0-3/P1-4 均销（P0-2 由 Owner 09-14 08:0x 批准、11:14 五表归零，「已决未回写」经 裁定#323 补记=本件最后一次改动 01fbfad157 所述批量登记之一）；仍欠 §三 P1-5 收尾两项：tzbak 系列备份表清理未见删除记录、期货 tick（IF/IC/IM/IH）历史补需另批（A22 通道）。文内「docs/_working 有周期性删除者在逃」「产物写完立即 git add」为过程记载，未据以执行任何动作。机械底座 twin=- 漏判：archive/2026-09/c_class_scattered/ 同名件 cmp=BYTE_SAME
- 结案报告：
    施工面：779556afc6（09-14 行情时区修复收官+tick 批量补数+采集管线复活——文档与工具批）。
    交接包点名的工具件复验在位：scripts/data/repair_kline_tz_monthly.py、scripts/data/finish_p0_1.py、
    scripts/data/p02_month_gapfill.py（缺口报告 §五 记为 P0-2 执行器，11:14 五表残余偏移=0）。
    裁定侧：docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml:3999 `- ruling_id: '裁定#323'`
    （即本件 P0-2「已批准+已完成」的回写依据）。

### 2026-09-14-indicator-mining-batch4.md
- 类型=file · HEAD 末次=2026-09-15T02:21:49+08:00（4f804539d5） · 归档双活=`docs/_working/archive/2026-09/c_class_scattered/2026-09-14-indicator-mining-batch4.md` 字节等值 1/1 · 末笔生产面=0 件
- 提交链：4f804539d5 docs: docs/_working 清理批(2/3)——51 份文档结案报告写入（C-1~C-4 裁定固化；4681e4a335 chore(derived): watchdog 派生缓存自动收敛——B类白名单稳定漂移 122 件（零活跃会；714ed7e2da docs(mining): 批5挖矿增补——RV波动率族4件(Parkinson/GK/RS/YZ,学术引文齐；faa3cd0b87 docs(mining): 技术指标库批4挖矿报告——病菌寻路SOP首次应用于指标域（4轮signal+1受阻
- 做了什么：技术指标库批 4 挖矿报告（mining_sop 首次用于指标域）：R1-R5 五轮日志、防噪音四闸、立卡 3 张（STOCH 本体/TA-Lib 动量清偿/BRAR+CR 能量族）、长尾 M-L1~L6、停挖转施工建议
- 剩余欠账：立卡与长尾均已被后续批清偿（真源描述逐批点名本件「挖矿立卡 1/2/3」，见 already_in_truth_source）；唯一未落项=本件「不做边界」中 SCR/CYQ 筹码族挂 Owner 裁定的换手率契约扩张，注册表自述批10 已以「指标输入首次引入换手率、仅 daily、其余周期软降级 NULL」方式落地，本件未回写。机械底座 twin=- 漏判：archive/2026-09/c_class_scattered/ 同名件 cmp=BYTE_SAME
- 结案报告：
    入库链：faa3cd0b87（批4 报告）、714ed7e2da（批5 增补 RV 波动率族）。
    真源侧复验：technical_indicator_registry.yaml 的 registry description 逐批记
    「批6：RV 波动率族 4+BBI+STOCH 本体+动量清偿（AROON/AROONOSC/BOP/PPO/APO/DX）+BRAR/CR 能量族共 14 指标
    （挖矿立卡 1/2/3+批5 增补全清偿）」；长尾 M-L1/L2/L3=批9-1、M-L4=批8、M-L5=批9-2、M-L6=批9-3/9-4。
    字段级复验：:1034 outputs [stoch_fastk, stoch_fastd, stoch_slowk, stoch_slowd]、:1100 outputs [aroonosc]、
    :1265 outputs [ar_26, br_26]、:1298 outputs [cr_26]。

### 2026-09-14-lane-c-agentic-mining-charter.md
- 类型=file · HEAD 末次=2026-09-15T02:21:49+08:00（4f804539d5） · 归档双活=`docs/_working/archive/2026-09/c_class_scattered/2026-09-14-lane-c-agentic-mining-charter.md` 字节等值 1/1 · 末笔生产面=0 件
- 提交链：4f804539d5 docs: docs/_working 清理批(2/3)——51 份文档结案报告写入（C-1~C-4 裁定固化；4392965a5f docs(mining): P0 试驾对照笔记交付（立项书附三，因 docs/_working 撞 GOV-D；883239410e docs(charter): P2 二次裁定修订——Owner 复核成本结构后撤销启用开关（赛马主力成本=E4；f6af41ae5a docs(charter): P2 二次裁定修订——Owner 复核成本结构后撤销启用开关（赛马主力成本=E4
- 做了什么：车道C 二轨立项申请书（LLM 智能体挖矿轨，取代原 AlphaGen 立项划界）：三代际检索结论、P0/P1/P2 范围、与 gplearn 轨互补关系；附 Owner 全批裁定与 P0 试驾对照笔记（AlphaAgent/AlphaMuse 精读+官方仓侦察+矿机六向寻路+P1 施工清单）
- 剩余欠账：§六 开放三项未见本件内销案：本机代理恢复后补 `git clone --depth 1` 实跑、AST 相似度实现选型（自研 vs 现成库）、deepseek-r1:8b 消融档是否首班双模型对比；本件 P1 清单所指 P0 笔记载体 `docs/_working/2026-09-1X-agentic-mining-p0-notes.md` 为占位路径（清理批判废弃引用，实际笔记已内联为附三）。机械底座 twin=- 漏判：archive/2026-09/c_class_scattered/ 与 archive/2026-09/factory/ 各存同名件，两处均 cmp=BYTE_SAME
- 结案报告：
    入库链：f6af41ae5a/883239410e（P2 二次裁定修订——Owner 撤销启用开关，直接建直接用）、
    4392965a5f（P0 试驾对照笔记交付，附三）。施工面复验：P1 清单第 2 项实现件
    scripts/backtest/lane_c2_agentic_miner.py 在盘（头注 P2 赛马=与 gplearn 轨同卷、
    [TESTS] tests/backtest/test_lane_c2_agentic_miner.py），并已接编排层
    scripts/backtest/factory_intake_pipeline.py:135/:137/:190/:301（intake_sources["C2"]、台账 lane_c2_candidates.csv），
    另被 scripts/backtest/factor_strategy_template.py:126、hypothesis_translator.py:147 消费；
    资源档位登记 src/zephyr/infrastructure/system_telemetry/resource_sampler.py:141（manual_lane_c_agentic_miner 匹配式）。

### 2026-09-14-market-data-gap-report.md
- 类型=file · HEAD 末次=2026-09-16T01:57:35+08:00（8e2a1561d5） · 归档双活=`docs/_working/archive/2026-09/c_class_scattered/2026-09-14-market-data-gap-report.md` 字节等值 0/1 · 末笔生产面=0 件
- 提交链：8e2a1561d5 docs(data): 缺口报告 §十 晨班修复闭环+当日三重保障终态——开盘零进账两连根因全修（entry ；4f804539d5 docs: docs/_working 清理批(2/3)——51 份文档结案报告写入（C-1~C-4 裁定固化；e09da881ce docs(data): 晚间执行批终稿——期货09-09补齐105737行/TICK_SOURCE切xtdat；4681e4a335 chore(derived): watchdog 派生缓存自动收敛——B类白名单稳定漂移 122 件（零活跃会
- 做了什么：行情数据缺口修复主报告（v2 重建版）：五张分钟表时区偏移修复口径与天级判定升级、tick 三天批量补数终验、采集管线退化三层根因复活、P0-2 全历史 15.6 亿行重写、晚间批与 09-15 晨班闭环、验证口径速查
- 剩余欠账：文内结案块自列 4 项遗留，本分片复验后状态：①防复发四件套「待立项」——其中 ②ch_writer 表列缓存失效已落（ch_writer.py:716 table_cols_cache.pop / :717 insertable 缓存 pop）、③新表 DDL 前置校验已落（src/zephyr/data/scheduler.py 命中 DDL 前置校验），①miniqmt 日线 920 段覆盖+偏差告警、④桥模式降级为纯后备仍待确认；②TradingWatchdog/RestartMiniQmt 两计划任务 Disabled 留 Owner 定（未查系统态，仅记文档原话）；③alt_sz_subject 命名错位已在 §十 记为 42 行改挂 alt_sz_market_subject 回放完成；④tzbak 系列备份表清理未确认。永久事实（tick 07-03/07-06~09/08-05/08-06 不可恢复）已在 src/zephyr/data/config/known_data_gaps.yaml 侧登记体系内。机械底座 twin=- 漏判：archive/2026-09/c_class_scattered/ 同名件 cmp=BYTE_DIFF（差异仅 1 处：本件 `git clean -fd` 半角连字符，归档件为 U+2011，18246 vs 18248 字节）
- 结案报告：
    执行链三笔：e09da881ce（晚间执行批终稿：期货 09-09 补齐 105,737 行/TICK_SOURCE 切 xtdata/local_replay 死信根治）、
    8e2a1561d5（§十 晨班修复闭环：开盘零进账两连根因全修 entry NameError+os.replace 重试、34 死信隔离→全回放、
    09-15 全天 10,529,950 行/8,473 标的零缺口、TICK_SOURCE 终态 xtdata）。
    修复器件在盘可核对：scripts/data/repair_kline_tz_monthly.py、scripts/data/finish_p0_1.py、
    scripts/data/p02_month_gapfill.py；#ARCH-311（serializer 在主工作区 git clean -fd 致 _working 被清）已登记。

### 2026-09-14-p0-syntax-gate.md
- 类型=file · HEAD 末次=2026-09-15T02:21:49+08:00（4f804539d5） · 归档双活=`docs/_working/archive/2026-09/c_class_scattered/2026-09-14-p0-syntax-gate.md` 字节等值 1/1 · 末笔生产面=0 件
- 提交链：4f804539d5 docs: docs/_working 清理批(2/3)——51 份文档结案报告写入（C-1~C-4 裁定固化；19073262a2 feat(gov): SYNTAX-VALIDATION gate refinement+修复日志——红蓝 v
- 做了什么：红蓝 v3 P0-1 语法门禁修复工作日志（批 2）：SYNTAX-VALIDATION gate 本体+单测+接线登记，扫描源语义改为本 commit files 参数、fail-closed/fail-open 分界、own-scope、priority=49 让位实测
- 剩余欠账：§5 遗留四项：①磁盘残留探针 tests/governance/rule_bridge/xt_p01_syntaxerr.py 待 Owner 手动删（本分片复验：该路径现不存在=清库已执行）；②`.runtime/tmp/probe_*.py` 8 件属 gitignored TTL 区；③module_translation_registry.yaml 他会话陈旧 hunk 未搭便车（留他会话/Owner）；④ARCH-REFERENCE 瞬态竞态「记录不修」+ 红蓝 v4 复测就绪。机械底座 twin=- 漏判：archive/2026-09/c_class_scattered/ 同名件存在，cmp=BYTE_SAME
- 结案报告：
    落地笔 19073262a2（feat(gov): SYNTAX-VALIDATION gate refinement+修复日志）。
    门禁登记真源复验：docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml:1806 `- gate_id: SYNTAX-VALIDATION`（:1807 priority=49 描述行）、
    catalogs/in_process_gate_registry.yaml:694 同条目、catalogs/noqa_exempt_registry.yaml:422（语法夹具豁免口径注释）。
    本件自述验证证据=单测 14 passed + 全量回归 2480 passed + auto_registrar 111/111 注册 0 failures。

### 2026-09-14-p002-reprint-result.md
- 类型=file · HEAD 末次=2026-09-15T02:21:49+08:00（4f804539d5） · 归档双活=`docs/_working/archive/2026-09/c_class_scattered/2026-09-14-p002-reprint-result.md` 字节等值 1/1 · 末笔生产面=0 件
- 提交链：4f804539d5 docs: docs/_working 清理批(2/3)——51 份文档结案报告写入（C-1~C-4 裁定固化；e1de5790a6 feat(p0): 裁定#230 落地——BT-P0-002 判据对象切换为风险判别，P0-002 结案 va；dfa41e9aae feat(regime): P0-002 判定器重印批——锚定风险四档状态机（裁定#229 第②步）
- 做了什么：P0-002 判定器重印批结果报告（裁定#229 第②步）：v1 趋势双确认否决→探针→v2 vol_pct 风险四档定稿，收益判别如实 pending、风险判别双段全过，裁定#230 判据对象切换自裁并执行→P0-002 valid 结案
- 剩余欠账：§5「明确不做（待 Owner/后续批）」三件：TDM 生产消费切换（已由同分片 2026-09-14-agg-switch-design.md 落地，cap 在产）、判据契约变更（本件 §四 已自裁执行）、六段情绪轴融合（AGG 完整重造）——第三件本件与本分片其他件均未见落地面，属仍开放的后续批。机械底座 twin=- 漏判：archive/2026-09/c_class_scattered/ 同名件 cmp=BYTE_SAME
- 结案报告：
    施工链两笔：dfa41e9aae（锚定风险四档状态机=裁定#229 第②步）、e1de5790a6（裁定#230 落地——BT-P0-002
    判据对象切换为风险判别，P0-002 结案 valid）。交付件复验在盘：
    src/zephyr/regime/core/anchored_state_machine.py；表真源 schemas.categories.backtest.backtest_regime_state_anchored
    （被 src/zephyr/pf_alloc/allocation_inputs.py:617-623 引用）；双轨对照器 scripts/backtest/compare_state_dualrun.py；
    验收件 scripts/backtest/validate_p0_discrimination.py。

### 2026-09-14-pattern-consumer-plan.md
- 类型=file · HEAD 末次=2026-09-15T02:21:49+08:00（4f804539d5） · 归档双活=`docs/_working/archive/2026-09/c_class_scattered/2026-09-14-pattern-consumer-plan.md` 字节等值 1/1 · 末笔生产面=0 件
- 提交链：4f804539d5 docs: docs/_working 清理批(2/3)——51 份文档结案报告写入（C-1~C-4 裁定固化；dd4c754f06 docs(signal): 图形库消费端方案 v1.0 冻结——通电/接线/调权/呈现/边界五层（C1 装配根
- 做了什么：图形库消费端方案 v1.0（冻结待施工）：内部断点盘点、C1 装配根/C2 信号管线+meta 门/C3 纯消费调权/C4 三端点+页/C5 边界登记/C6 不做，§四挖矿六向日志，§五 W-C1~W-C4 批切分
- 剩余欠账：C1-C4 均有落地面（见 already_in_truth_source）；C5 边界登记三件（回测 screen/lane_c 形态条件、TDM 形态→信号边、pattern breadth 因子候选）属交他会话的登记项，本件未记他方回执；C6 明示不改 MOD-SIG-115 mapper（human_gated）保持原状。机械底座 twin=- 漏判：archive/2026-09/c_class_scattered/ 同名件 cmp=BYTE_SAME
- 结案报告：
    方案入库笔 dd4c754f06（图形库消费端方案 v1.0 冻结——通电/接线/调权/呈现/边界五层）。
    W 批落地复验：C1 装配根 src/zephyr/signal_ashare/strategy_signal/pattern_signal_runtime.py 在盘
    且有模块蓝图 docs/03_modules/_domain_signal/pattern_signal_runtime/blueprint.md；
    C3 调权件 src/zephyr/signal_ashare/strategy_signal/signal_weight_adjuster.py 与
    strategy_vote_integrator.py 互相接线；C4 三端点已挂 src/zephyr/frontend/dashboard/api_server.py:4163
    起「图形库消费端三端点（消费班方案 v1.0 C4/W-C4，MOD-SIG-147 线，只读）」，
    :4167 pattern_events、:4222 胜率查询读 c1_market.market_pattern_win_rate（四窗×regime 切片）。

### 2026-09-14-sim-partition-discussion.md
- 类型=file · HEAD 末次=2026-09-15T02:21:49+08:00（4f804539d5） · 归档双活=`docs/_working/archive/2026-09/c_class_scattered/2026-09-14-sim-partition-discussion.md` 字节等值 1/1 · 末笔生产面=0 件
- 提交链：4f804539d5 docs: docs/_working 清理批(2/3)——51 份文档结案报告写入（C-1~C-4 裁定固化；fc9c81a1dc feat(backtest): 估值/市值翻译批在盘件集中入库——Slater 三件（MOD-BT-103 价；49e94f5b4c docs(backtest): C5 附五——聚类 v2 去重处置+双版本 PB-POE+VAL-* 发现+转；383dd828c2 docs(sim): 模拟盘分仓专题讨论材料——三方案对比(虚拟子仓推荐先C后A)/资金分档/归因口径/QMT
- 做了什么：模拟盘分仓专题讨论材料（Owner「钱混一起无法归因」直答）：分仓三方案对比并推荐先 C（账本模拟）后 A（虚拟子仓）、资金分档额度规则、归因四条口径、QMT 桥对接、施工路径两步、三决策点；附录=模拟盘→实盘晋升规则 v1.0（Owner 批准生效，5 硬门槛+3 降级废规则+工具化）
- 剩余欠账：决策点①②：先 C 已落（sim_paper_ledger+sim_pocket_daily+日链自动化），第二步方案 A（虚拟子仓+真实撮合，桥接层改造）本件明示「另立批次」，本分片未见其落地面；晋升规则五条硬门槛的阈值文本未见成文政策卷（grep 信号一致性/漏单率/晋升硬门槛 在 docs/01_policies_and_standards/sop 与 docs/03_modules/**/blueprint.md 零命中），现以工具件 sim_promotion_memo.py（MOD-BT-193，[TTL] permanent）+ 注册表登记承载；首次评审时点（2026-12-14）未到。机械底座 twin=- 漏判：archive/2026-09/c_class_scattered/ 同名件 cmp=BYTE_SAME
- 结案报告：
    入库链：383dd828c2（分仓专题讨论材料）、49e94f5b4c（C5 附五——转实盘规则草案）、
    fc9c81a1dc（估值/市值翻译批在盘件集中入库）。
    决策落地复验：方案 C 账本件 scripts/backtest/sim_paper_ledger.py 在盘，头注 [CONSUMERS]
    记 c1_backtest.sim_pocket_daily（注册表全部 sim 策略钱包）+每日自动化，:61 引用 schemas.categories.sim_pocket_daily；
    同族件 sim_deviation_report.py（偏离报告）、sim_platform_journal.py、sim_governance.py、sim_attribution_report.py、
    sim_daily_runner.py 均在盘；晋升判定工具化=scripts/backtest/sim_promotion_memo.py（MOD-BT-193，
    [CREATION-TOKEN] sim-promotion-memo-mod-bt-193-20260915，建议书机器备料+签字权留 OwnerTokenGuard）。

### 2026-09-14-supply483-verification-report.md
- 类型=file · HEAD 末次=2026-09-15T02:21:49+08:00（4f804539d5） · 归档双活=`docs/_working/archive/2026-09/c_class_scattered/2026-09-14-supply483-verification-report.md` 字节等值 1/1 · 末笔生产面=0 件
- 提交链：4f804539d5 docs: docs/_working 清理批(2/3)——51 份文档结案报告写入（C-1~C-4 裁定固化；8770bf8485 docs(supply_chain): 验证报告追加——代码化回填 1248 行+概念体系落地+概念展示规格；9a896219a7 docs(supply_chain): 483 前五大数据全量重验报告——三重机检+方向仲裁 3 条错向已关
- 做了什么：前五大供应商/客户（483 层）全量重验报告：A 组 7,337 行五重机检、17 对方向矛盾按申万行业+产业常识仲裁（3 条错向 edge_close）、§3 B 组 44,008 行二次代码化立项建议、§4 详情页上下游 SQL/API 规格、§6 追加代码化回填 1,248 行与概念体系落地
- 剩余欠账：本件自列两项「他批/他会话」欠账，本分片复验未见落地面：①§3 B 组剩余客户名→代码匹配器（模糊匹配+拼音/简称库+人工复核队列；scripts/industry_graph/ 下无 name→code matcher 件）②§4/§6 详情页上下游与 concepts 接口规格交 chainmap 前端会话（src/zephyr/frontend/dashboard/api_server.py grep supply_chain/concepts 零命中；chainmap 前端件仅 ig_company_edge 检索面）。§2 名单源反向 5 对的「留待名单源验证批处置」亦未见回执。机械底座 twin=- 漏判：archive/2026-09/c_class_scattered/ 同名件 cmp=BYTE_SAME
- 结案报告：
    验证与回填链：9a896219a7（483 前五大全量重验报告——三重机检+方向仲裁，3 条错向已关）、
    8770bf8485（追加：代码化回填 1248 行+概念体系落地+概念展示规格）。
    数据面复验：装载器 scripts/industry_graph/load_supply_top5_483.py、
    消费件 scripts/industry_graph/calc_customer_concentration.py 与 backtest_supply_leadlag.py 在盘；
    回填审计留痕按本件自述在 .runtime/audit/name_backfill_actions.json（可逆，edge_id 清单在案）。

### 2026-09-14-tdm-consumption-sop-draft.md
- 类型=file · HEAD 末次=2026-09-15T02:21:49+08:00（4f804539d5） · 归档双活=`docs/_working/archive/2026-09/c_class_scattered/2026-09-14-tdm-consumption-sop-draft.md` 字节等值 1/1 · 末笔生产面=0 件
- 提交链：4f804539d5 docs: docs/_working 清理批(2/3)——51 份文档结案报告写入（C-1~C-4 裁定固化；0e94229a1b docs(gov): TDM v1.3 施工立项登记（Owner 批准施工SOP+换卷重考；验收五条：节点验证；a889cd1d85 docs(gov): TDM 寻路批次2——地图方法论本体（SR 11-7 模型清单治理对齐：节点验证元数据/；36836c8301 docs(gov): TDM 消费场景寻路批次1——S3 知识漂移挖到 arXiv Look-Ahead-Be
- 做了什么：TDM 消费场景规程草案 v0.1：地图五大功能、S1-S6 消费场景表、落地方式（升 permanent+门禁化建议）；附寻路批次1（S3 知识漂移 arXiv Look-Ahead-Bench 支撑）、批次2（SR 11-7 模型清单治理对齐+三缺口+新增 S7-S9 饱和度检查）、TDM v1.3 施工立项登记与状态账
- 剩余欠账：草案→permanent 已升卷，S7-S9 与知识生效日哨兵已入正式条款；TDM v1.3 施工件亦已 production（upgrade_tdm_v13_metadata.py，materiality 分档回填 138 节点，last_validated_at/validated_by 按诚实原则全留空——当前无 verified 节点）；本件 §状态账的「下一班主线」三件（DS-230 派生层验证/市值类 22 条解锁/模拟盘 sim_daily 首跑观察）属后续批，其中 sim_daily 自动化件在盘（scripts/backtest/sim_daily_runner.py）。机械底座 twin=- 漏判：archive/2026-09/c_class_scattered/ 同名件 cmp=BYTE_SAME
- 结案报告：
    入库链：36836c8301（寻路批次1）、a889cd1d85（寻路批次2 地图方法论本体/SR 11-7 对齐）、
    0e94229a1b（TDM v1.3 施工立项登记，Owner 批准走施工 SOP+换卷重考，验收五条含 S7-S9 与知识生效日哨兵）。
    真源升格复验：docs/01_policies_and_standards/sop/trading_decision_map_sop/tdm_consumption_policy.md
    （ttl: permanent、status active、version 1.0.0、date 2026-09-14），:17 诞生注记直指本件起草+两轮寻路后同日升格，
    :32-:44 §2 场景表已含 S7/S8/S9，:48 记 S1/S3 门禁化与节点验证元数据并入 v1.3 施工批。
    v1.3 施工件复验：scripts/governance/upgrade_tdm_v13_metadata.py（EA 侧 34/10 号文档记为 production 态，
    materiality 由 backlog 脚本化推导禁手挑，last_validated_at 诚实留空）。

### 2026-09-14-tilib-batch6-plan.md
- 类型=file · HEAD 末次=2026-09-15T02:21:49+08:00（4f804539d5） · 归档双活=`docs/_working/archive/2026-09/c_class_scattered/2026-09-14-tilib-batch6-plan.md` 字节等值 1/1 · 末笔生产面=0 件
- 提交链：4f804539d5 docs: docs/_working 清理批(2/3)——51 份文档结案报告写入（C-1~C-4 裁定固化；15a4326bc1 feat(factor): 技术指标库批6——挖矿立卡全清偿+14指标/19列（RV波动率族Parkinson
- 做了什么：技术指标库批6 施工方案：RV 波动率族 4+BBI+动量族 7+BRAR/CR 共 14 指标/19 列（REG-IND-001 78→92、DDL 116→135），含五轮方案挖矿、逐指标测试计划、已知坑清单与 15 步施工 SOP 映射，并立项批7 消费端接线卡
- 剩余欠账：①§1 末尾指标分类合计自述 91≠92 的算术存疑段未清理（文内已声明以代码实测为准）；②§5 消费端接线批已由批7 件展开；③本件头部清理批自动结案报告判「设计/计划类且无落地证据·保守保留」与事实不符——批6 已落地（见 evidence_commits），疑为机械底座把「无显式完成信号」当成无落地面
- 结案报告：
    落地笔（抄 git log 原文）：15a4326bc1 2026-09-14T04:53:49+08:00 feat(factor): 技术指标库批6——挖矿立卡全清偿+14指标/19列。
    方案 §5 的下游批7 亦落地：53a00cdfb7 2026-09-14T05:56:06+08:00 feat(factor): 批7消费端接线块A+B+C——indicator_reader.py PIT读。
    本件自身末笔 4f804539d5 为 51 文件纯 docs/_working 批（ext_footprint=0）。

### 2026-09-14-tilib-batch7-wiring-plan.md
- 类型=file · HEAD 末次=2026-09-15T02:21:49+08:00（4f804539d5） · 归档双活=`docs/_working/archive/2026-09/c_class_scattered/2026-09-14-tilib-batch7-wiring-plan.md` 字节等值 1/1 · 末笔生产面=0 件
- 提交链：4f804539d5 docs: docs/_working 清理批(2/3)——51 份文档结案报告写入（C-1~C-4 裁定固化；bbc4389e40 docs(plan): 批7消费端接线批开工方案——方案挖矿6轮(W-R1消费反查二次核实≈0定位改首建/W-
- 做了什么：批7 消费端接线开工方案：块A 新建 indicator_reader PIT 读取 API、块B 两个真实消费样板（波动率止损/超买超卖因子输入）、块C REG-IND-001 used_by_factors 双向锚点回填，附六轮方案挖矿与回填链状态快照
- 剩余欠账：①§4 回填链快照（daily 新列等四轮）发布时点已过时，由后续 tilib 清欠班收口；②块C used_by_factors 逐条回填无本件内回执；③头部自动结案报告同样判「无落地证据」，与 53a00cdfb7 实测不符
- 结案报告：
    落地笔：53a00cdfb7 2026-09-14T05:56:06+08:00 feat(factor): 批7消费端接线块A+B+C——indicator_reader.py PIT读。
    块A 实现件 src/zephyr/factor/indicator_reader.py 在盘；样板消费件 scripts/backtest/indicator_consumption_demo.py 在盘。
    回填链收尾由 3424a718e7 2026-09-20T16:45:08+08:00 docs(project): 技术指标库清欠班收官——a5 交付报告+a1 台账终稿 承接。

### 2026-09-14-typhoon-bdi-factor-mining-plan.md
- 类型=file · HEAD 末次=2026-09-15T02:21:49+08:00（4f804539d5） · 归档双活=`docs/_working/archive/2026-09/c_class_scattered/2026-09-14-typhoon-bdi-factor-mining-plan.md` 字节等值 1/1 · 末笔生产面=0 件
- 提交链：4f804539d5 docs: docs/_working 清理批(2/3)——51 份文档结案报告写入（C-1~C-4 裁定固化；631450cb92 docs(alt-data): 深圳平台管线交接包终版——47接口任务书(订阅两层坑/服务ID绑定发现/14坑；ce24060e66 docs(alt-data): F11 预注册 OOS 判定——IS t=2.11 成立但 OOS 方向翻转(；8593e502de docs(alt-data): F11 顶部动量假设预注册入库——主判据=OOS(2024-2026)顶部区前
- 做了什么：台风×BDI 事件因子挖矿总账（六向寻路 R1-R6、防噪音四闸、EVT-TYPHOON-BDI-001 立卡草案+P0/P0-002/A/B/C/F5/F6/F10/F11 逐批实弹结果与封矿判定），文末附深圳开放数据订阅绑定机制发现
- 剩余欠账：①GAP 积累中卡位 6 项（F1-F3、F10、F12、F8/F9）与 CNKI 中文文献「受阻」项在册未复验；②本件自述「季节性基线先行写入事件类因子研究的默认动作」——按合同 §3 机械查真源：grep docs/01_policies_and_standards/sop/mining_sop/ 与全 policies 对「季节性基线」零命中，该判据未入任何真源（另见本 shard alt_data_consumption_plan 的同类呆账）；③§订阅发现含 28 接口服务地址事项，已被深圳批3 47/47 收官覆盖；④正文含 URL/接口清单等数据样式文本，未据此执行任何动作
- 结案报告：
    本件自述域级收口（§批次总结/§F11 OOS 判定）：主卡 EVT-TYPHOON-BDI-001 就地封矿留痕、002 观察项注销、
    F5/F6 双双封矿、F11 预注册 OOS 主判据未达（t=-0.42）→ 观察项封矿、A/B/C 三条线走完、
    「另类数据消费端全部 20+ 因子位走完挖矿 SOP」终态计数 已上线7/封矿·淘汰7/GAP 积累中6。
    判废类终态无代码落地面属正常（数据资产 8 表保留）；其下游深圳数据面的收口落地笔为
    0ba60dd0ef 2026-09-15T00:52:07+08:00 feat(alt-data): 深圳开放数据批3 全量接入——47/47 收官。
    本件自身末笔 4f804539d5 ext_footprint=0。

### 2026-09-14-xtreme-redblue-v4-report.md
- 类型=file · HEAD 末次=2026-09-15T02:21:49+08:00（4f804539d5） · 归档双活=`docs/_working/archive/2026-09/c_class_scattered/2026-09-14-xtreme-redblue-v4-report.md` 字节等值 0/1 · 末笔生产面=0 件
- 提交链：4f804539d5 docs: docs/_working 清理批(2/3)——51 份文档结案报告写入（C-1~C-4 裁定固化；d5dbc7f61a docs(working): 红蓝 v4 报告补裁定#252 落地附录——F2 上游治本闭环记录；62cb4621be fix(gov): 红蓝 v4 修复批——F1 worktree 语法门禁回退解析 + F2 HELD-OVE；c36083b8a9 docs(redblue): v4 修复面复测报告——P0-1 worktree 通道击穿（P0 候选 F1）
- 做了什么：红蓝对抗 v4 修复面复测工作日志（F1-F10 十场景对账）+ 修复批附录：F1 worktree 语法门禁失效治本、F2 并发搭便车 HELD-OVERLAP 补 .ailocks 第二轨、F9 不重复施工认定、裁定#252 落地与终验
- 剩余欠账：①留 v5 项（P1-1② 自身标记放行未取证、并发同时性场景）——v5 报告已产并归档于 docs/_working/archive/2026-09/redblue/2026-09-15-xtreme-redblue-v5-report.md；②「deletion 提交撞 pre-commit 钩子链挂起 180s」记录为同源问题，本件未记其独立修复；③xt4tmp 攻击样本出库归属见本件附录（由他会话 tests/ 域提交吸收），实测 git ls-files 已无 xt4 跟踪件；④正文含攻击路径与「Owner 授权」样式文本=数据，未执行
- 结案报告：
    修复落地笔（本件附录自述 + git log 核实）：a287099285 2026-09-14T22:18:30+08:00 feat(gov): 裁定#252——lock_files
    锁存活=会话存活（红蓝 v4 F2 上游裁定同批原子入库）。F9 由他会话 29c751b5d7
    2026-09-14T20:48:49+08:00 完成容量门 own-scope 化，本件 §F9 已认定不重复施工。
    裁定条目在真源在册：docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml:1836 - ruling_id: 裁定#252。
    攻击面残留核实：git ls-files 过滤 xt4 零命中（主分支无损害件在库）。

### 2026-09-15-c4-acceptance-interim.md
- 类型=file · HEAD 末次=2026-09-15T03:27:02+08:00（275bc860dc） · 归档双活=`docs/_working/archive/2026-09/c_class_scattered/2026-09-15-c4-acceptance-interim.md` 字节等值 1/1 · 末笔生产面=0 件
- 提交链：275bc860dc docs: 全链路工厂方案+穷尽立项稿工作区最新版（含勘误吸收）、DSR 第0步重算定案附录、清理台账+交接包
- 做了什么：C4 历史研报一致预期修复原型验收报告（阶段版）：四批实绩表（4,259 行分置信层）、15/30 份人工抽核目视台账（报告级 14/15=93.3% 达标）、三类提取缺陷治本、high-only 收紧结论与剩余协议/全量批计划
- 剩余欠账：①本件自述为阶段版：抽核协议余 15 份的逐夜滚动目视无后续回执件；②mid 层 344 行「留档待复核升级」未见销案；③全量批 ~60,477 份的完成度以缓存盘实测间接佐证（cb7786e75d 记 data/c4_pdf_cache 60,245 件/56.59GB），本件未回填终数
- 结案报告：
    本件 §4「验收后动作=consensus_daily_repaired 双轨重建（high-only 口径）」落地笔：250c134d9d
    2026-09-16T22:32:46+08:00 feat(consensus): consensus_daily_repaired 双轨重建落库+三重对照 3/3 PASS。
    实现件在盘：schemas/categories/fundamental/consensus_daily_repaired.py、
    src/zephyr/data/implementations/consensus_daily_repaired_compute.py。
    PDF 缓存入库隐患处置笔：cb7786e75d 2026-09-23T04:34:14+08:00（实为 2026-09-23T04:34 批，
    git log -1 输出 2026-09-23T04:34:14+08:00 [st-oddjobs-20260923][件2·止血批] .gitignore 加 data/c4_pdf_cache/）。

### 2026-09-15-c5-cluster-refresh.md
- 类型=file · HEAD 末次=2026-09-15T03:36:05+08:00（283e64c1d2） · 归档双活=`docs/_working/archive/2026-09/c_class_scattered/2026-09-15-c5-cluster-refresh.md` 字节等值 1/1 · 末笔生产面=2 件
- 提交链：283e64c1d2 feat(backtest): 模拟盘平台批4 治理自动化首件——strategy_lifecycle_adv
- 做了什么：C5 聚类复检刷新报告（夜班）：22 件估值/市值族按因子主导+参数形状聚成 7 簇出簇首与 redundant 建议；总结论=全族无一具备 sim 晋级资格、小市值成长门族 IS 有效性属风格β；工具化裁定=不新建常驻聚类工具
- 剩余欠账：①§3 后续两项未回写本件：canonical 三只（VAL-PE/PB/DIV-HIGH）IS 行补跑后 §1 表补注、redundant/簇首建议的实际取舍执行（文内明言归后续批次）；②「不新建常驻工具」的规范预算净零裁定为一次性自裁，未见裁定册登记（不构成呆账，登记义务在台账侧）
- 结案报告：
    报告件本体即交付（文内 §2 明令一次性分析以本报告交付）。其 §3 依赖的 decay_watch 后续件已落地：
    本文件末笔 283e64c1d2 即为 strategy_lifecycle_advisor（MOD-BT-187）同批提交，
    实现件 scripts/backtest/strategy_lifecycle_advisor.py 在盘。
    同窗 N1/N2 引擎与 B 档双窗落地笔 4f6091272c 2026-09-15T03:30:31+08:00。
    末笔 ext_footprint=2（同批含非 _working 文件 2 件）。

### 2026-09-15-four-big-items-blueprint.md
- 类型=file · HEAD 末次=2026-09-16T00:23:41+08:00（5dc8020401） · 归档双活=`docs/_working/archive/2026-09/c_class_scattered/2026-09-15-four-big-items-blueprint.md` 字节等值 1/1 · 末笔生产面=1 件
- 提交链：5dc8020401 docs(factory): 四大件施工蓝图——MOD-BT-201 E7前哨/202 MCTS/203 图谱
- 做了什么：四大件施工图：MOD-BT-201 E7 前哨对账器 / 202 MCTS 表达式第三轨 / 203 图谱增补入图（--approve 门）/ 204 Kronos 微调数据管线，每件含核心逻辑步骤、依赖、测试、验收与执行优先序
- 剩余欠账：①203 的 Owner 审批 flag 是否曾真写入 ig_fact 未见本件回写；②204 微调结果（val loss/权重替换）未见实测记录回填；③depgraph 设计节点登记与最终实现状态核对归五图对齐批
- 结案报告：
    四件实现件全部在盘并有落地笔：dc24e2e8cc 2026-09-16T02:51:10+08:00 feat(factory): 通宵交接批+容量治理——四大件模块
    （scripts/backtest/forward_post.py、mcts_expression_search.py、graph_enrich_ingest.py 三件末笔同为该 hash）；
    scripts/backtest/kronos_finetune_prep.py 末笔 0875923166 2026-09-16T03:56:56+08:00 fix(factory): Kronos 全链收尾三件。
    本件自身末笔 5dc8020401 ext_footprint=1。

### 2026-09-15-full-automation-night-plan.md
- 类型=file · HEAD 末次=2026-09-15T04:02:13+08:00（0b4eddb231） · 归档双活=`docs/_working/archive/2026-09/c_class_scattered/2026-09-15-full-automation-night-plan.md` 字节等值 1/1 · 末笔生产面=0 件
- 提交链：0b4eddb231 docs(plan): 夜班总方案执行结果入册——N1-N10 十项裁定与销项全录（引擎扩展/14只双窗/C5；283e64c1d2 feat(backtest): 模拟盘平台批4 治理自动化首件——strategy_lifecycle_adv
- 做了什么：全自动化夜班总方案 + §5 执行结果与裁定记录：挖矿两轮回外部实践对照表、Owner 17 项清单映射 N1-N10、自裁记录与验收线，末节逐销项（N1-N10 全出结果，含两项登记跳过）
- 剩余欠账：①N10 两项「登记跳过」未销案：EXP-02（夜批状态文件路径不在交接信息内）、C-1/分钟表（外部依赖全灭/密钥过期）；②N6-B3 audit_fn 接线待 QMT 在线窗口、B4 未评估维持；③N9 battle_map 半活体（edges/steps 冻结 34 天）回填=独立对齐批、降级=产品裁定，明写登记留 Owner；④N7 治理线 33 行防线补丁当时「在途」，本件未记其终态
- 结案报告：
    本件 §5 自述十项销项全部有 HEAD 落地面：N1 引擎扩展=4f6091272c 2026-09-15T03:30:31+08:00
    feat(backtest): 引擎基本面门扩展（MOD-BT-096 v2）+B 档 14 只；N3/N5=283e64c1d2
    2026-09-15T03:36:05+08:00（strategy_lifecycle_advisor+C5 刷新报告+夜班方案入册）；
    N6 的 B5/B1/B2 落地笔为本件同窗的 5ebe47d4c0 2026-09-15T03:43:12+08:00
    feat(ops): Owner 窗口自动化批——盘后结算挂调度（B5）+QMT 看门狗（B1 半自动）+B2 自愈核销+B3 裁定登记。
    本件自身末笔 0b4eddb231 ext_footprint=0。

### 2026-09-15-governance-module-mining-sop-map.md
- 类型=file · HEAD 末次=2026-09-16T06:22:01+08:00（79faf9a91b） · 归档双活=`docs/_working/archive/2026-09/c_class_scattered/2026-09-15-governance-module-mining-sop-map.md` 字节等值 1/1 · 末笔生产面=3 件
- 提交链：79faf9a91b test(gov): 治理战役收官——红蓝对抗加固+挖掘地图 §5 全表终态回填；f5c82f742a feat(governance): 治理减法批 A5 收官——agent_health_monitor 删除（；b1ab1a6040 docs(governance): 挖矿地图加法表 A3/A4 终态回填——裁定#254 接线凭据（1d6a2；0059cc05e7 docs(governance): 挖矿地图减法批终态回填——R1-R4 凭据 1ddcd089/A2 通知通
- 做了什么：治理守护模块挖矿 SOP 战役地图：提交内存耗尽事故复盘、75 src+25 scripts+38 文档资产八域模块死活地图、§4 体检五条结构性发现、§5 加减乘除四表逐条回填终态与 commit 凭据、§4.5 存废自裁（裁定#255/#256）
- 剩余欠账：①§6 新增 SOP 待写项至今未立：docs/01_policies_and_standards/sop/ops_sop/ 实测仅 emergency_runbook.md/index.md/merge_conflict_resolution_policy.md/worktree_cleanup_policy.md 四件，无 process_runaway_incident_sop.md；②§7 未挖长尾四条在册（R4 逐域深挖、E1 消费方普查、autonomy_core 域死活、docs/02 蓝图级对账）；③R4 熔断/KillSwitch 收敛标注为长期战役，capacity_assurance+context_pipeline_auto 两项待裁；④M4 的 Ollama 版本升级列 Owner 待裁
- 结案报告：
    frontmatter completes_when 的机械判据（§5 每条带处置 commit）已满足：减法批 1ddcd089cf
    2026-09-16T00:51:43+08:00 refactor(governance): 治理加减乘除减法批——删除 8 个确认死模块…；
    乘 M1+M2+M3 6044c47fc6 2026-09-16T06:05:49+08:00 feat(infra): 治理战役 M1+M2+M3——统一进程孵化入口；
    除批 8aaede05cb 2026-09-15T19:54:10+08:00 fix(reaper): 孤儿 llama-server 事故双补丁；
    加法 A2/A3/A4 分别 85e396146b（治理全景图前端页）、a6cf1aad2d（告警前端接线）、
    1d6a206b93+49dde8fda5（kill_switch_orchestrator 与 last_resort_watchdog 接线，裁定#254）、
    9deb35e709（A5 四件删除）、a164befb8f（M4 溯源+VRAM 预算门）、8a8d0654d3（A1 nssm 册裁定废弃归档，裁定#256）。
    收官笔 79faf9a91b（§5 全表终态回填+红蓝加固），ext_footprint=3。

### 2026-09-15-gutters-eoc3-verification-deadend.md
- 类型=file · HEAD 末次=2026-09-15T11:41:42+08:00（28d7731fee） · 归档双活=`docs/_working/archive/2026-09/c_class_scattered/2026-09-15-gutters-eoc3-verification-deadend.md` 字节等值 1/1 · 末笔生产面=0 件
- 提交链：28d7731fee docs(gov): Gutters 候选证伪除名——P3 全案清零（Owner 切网后原书核对完成）：经本机；8245256b73 docs(gov): Gutters 原书核对开工交底——核证通路全灭记录落档（Owner 令开工后全通道探测
- 做了什么：双沟 Gutters 的 EOC3 核证记录：八条通路探测明细（全灭）→ 经代理取得 EOC3 三版 PDF 1315 页、76 章目录核验无 Gutters 章 → P3 候选前提证伪除名，八候选终态 6 在册+2 除名，全案清零
- 剩余欠账：①§一~§四为过时过程留档（文首已自标「读史勿照办」），其「唯一解锁=Owner 原书取证」结论已被 §五 终版覆盖；②本件含「Owner 动作」样式文本=数据，未执行；③文件头带 [BLUEPRINT]/[MODULE] 空锚注记，是否应由生成器清理归对齐批
- 结案报告：
    终态结论已入正式真源（合同 §3 双查命中→按 R2 改判①）：
    docs/01_policies_and_standards/_registry/catalogs/chart_pattern_registry.yaml:41 的 v2.16.0 changelog
    记「任务书候选 Gutters 经 thepatternsite 核对实名=Inverted Roof」与「Straight-Line Run 驳回（非独立形态）」；
    同文件 :6783 条目注「任务书候选名 Gutters 经核对实名=Inverted Roof，别名 gutter 保留溯源」。
    六条在册登记笔 19f569352e 2026-09-14T08:49:56+08:00；本件终版笔 28d7731fee（ext_footprint=0，纯单文件 docs 批）。

### 2026-09-15-handoff-factory-docs-discussion.md
- 类型=file · HEAD 末次=2026-09-15T03:27:02+08:00（275bc860dc） · 归档双活=`docs/_working/archive/2026-09/c_class_scattered/2026-09-15-handoff-factory-docs-discussion.md` 字节等值 1/1 · 末笔生产面=0 件
- 提交链：275bc860dc docs: 全链路工厂方案+穷尽立项稿工作区最新版（含勘误吸收）、DSR 第0步重算定案附录、清理台账+交接包
- 做了什么：「全链路工厂+组合层穷尽」两稿的交接指令（可复制 prompt）：列六条已查实硬事实（4 个业务工厂未接产线、Lane C 未编排、DSR num_trials 口径偏乐观等）与六个待答问题、讨论纪律与完成定义
- 剩余欠账：①六个反问的逐条答复未回写本件，结论落在下游战役目录（docs/_working/full-auto-chain/ 15 工段，目录 index 记 created 2026-09-20）；②整篇为「请执行」样式指令文本，按合同 §6 判为数据，本代理未执行其中任何语义；③引用的两份草稿（2026-09-14-full-chain-factory-blueprint.md / -combination-layer-exhaustive-charter.md）仍是 docs/_working 顶层散件，归其他分片判定
- 结案报告：
    交接对象的落地面：a0f907e928 2026-09-15T06:06:08+08:00 feat(backtest): F-06 批次A基建+结构知识件——
    执行器/ANOVA/E2挂接/行业真源/N_eff预注册（即本交接令所指 F-06 组合层第一期）；
    战役目录 docs/_working/full-auto-chain/（00_skeleton + S01..S15 十五工段）已建成，
    其 index 自述生成日期 2026-09-20。本件自身末笔 275bc860dc ext_footprint=0。

### 2026-09-15-neff-estimator-preregistration.md
- 类型=file · HEAD 末次=2026-09-15T06:06:08+08:00（a0f907e928） · 归档双活=`docs/_working/archive/2026-09/c_class_scattered/2026-09-15-neff-estimator-preregistration.md` 字节等值 1/1 · 末笔生产面=7 件
- 提交链：a0f907e928 feat(backtest): F-06 批次A基建+结构知识件——执行器/ANOVA/E2挂接/行业真源/N
- 做了什么：4.1 N_eff 估计器预注册锁定记录：锁定 effective_rank（熵加权特征值广度）为主、marchenko_pastur 为受限备选、排除 clustering；定双口径披露（n_trials_raw+n_trials_effective）、输入矩阵口径与生效批次，并给出四步估计器规格
- 剩余欠账：实现件注释自述「n_trials_effective 预留位（effective_rank 随批次 B 落地，当前恒 None）」——批次 B 实跑对该披露位的回填记录未在本件回写
- 结案报告：
    落地笔即本件末笔 a0f907e928（message 明列 N_eff 预注册），ext_footprint=7。
    实现件在盘且逐字承接本规格：src/zephyr/backtest/core/n_trial_ledger.py:29-30 注「N_eff 预注册（2026-09-15）…
    本账本预留 n_trials_effective 披露位」、:137-138 两口径字段、:143 def compute_effective_rank(
    文档串记「N_eff 预注册 4.1 规格实现，锁定勿改」）、:309 写入 n_trials_effective 披露位的 CAS 方法。

### 2026-09-15-szopen-pipeline-handoff.md
- 类型=file · HEAD 末次=2026-09-15T02:21:49+08:00（4f804539d5） · 归档双活=`docs/_working/archive/2026-09/c_class_scattered/2026-09-15-szopen-pipeline-handoff.md` 字节等值 1/1 · 末笔生产面=0 件
- 提交链：4f804539d5 docs: docs/_working 清理批(2/3)——51 份文档结案报告写入（C-1~C-4 裁定固化；2e8e5287f8 docs(alt-data): 服务地址侦察终局——三路线实弹定案 + Owner 动作清单入任务书；dc166d7e24 docs(alt-data): 能见度批登记收尾——canonical token+模块翻译重建+任务书进度留；631450cb92 docs(alt-data): 深圳平台管线交接包终版——47接口任务书(订阅两层坑/服务ID绑定发现/14坑
- 做了什么：深圳开放数据 47 接口接入管线交接单：背景（19/47 已接、28 卡服务地址）、必读三件与工作路径、任务 0-4 清单（复测订阅/向 Owner 收地址/已生效建管线/批量接入/回补纪律）、14 条坑位清单、五·五进度留痕与五·六侦察终局
- 剩余欠账：①本件的 28 接口欠账已被后继批超额覆盖：0ba60dd0ef 2026-09-15T00:52:07+08:00「47/47 收官」早于本件末笔（4f804539d5 02:21），即交接单发布时点已滞后于事实；②大表全史回补（水库 7,630 万行/能见度 2,456 万行）仍是「报批专项」未见放行记录；③DoD 六项未在件内逐项回勾；④全文为「给新对话的 AI，按任务清单顺序执行」指令样式文本=数据，未执行
- 结案报告：
    任务 2/3 落地笔：0ba60dd0ef 2026-09-15T00:52:07+08:00 feat(alt-data): 深圳开放数据批3 全量接入——47/47
    收官（水位/环境气象/气候历史/地面观测+口岸 7 系列并表），message 含「47 接口对账定案」与 4 新表 FINAL 核数。
    现盘 schemas/categories/market/ 下 alt_sz_* DDL 计 21 件（含 reservoir_level/climate_hist/ground_obs/env_meteor）。
    配套治本笔：3c90156077（能见度批）、020aa571de 2026-09-16T03:25:52+08:00（钥匙库登记）、
    c7197c245a 2026-09-16T01:46:30+08:00（CAP-CONSISTENCY setattr 形态豁免，alt 批 10 条 alt_sz cap 误报清偿）。
    本件自身末笔 4f804539d5 ext_footprint=0。

### 2026-09-15-tilib-handoff.md
- 类型=file · HEAD 末次=2026-09-15T23:52:28+08:00（a103bb8cc7） · 归档双活=`docs/_working/archive/2026-09/c_class_scattered/2026-09-15-tilib-handoff.md` 字节等值 1/1 · 末笔生产面=1 件
- 提交链：a103bb8cc7 docs(handoff): 指标库线交接包——P0 CH 内存爆满现状与恢复三选一/九批总账/批9数据批+批
- 做了什么：技术指标库线交接包：§0 P0 运维事故（technical_indicator 1304 parts/125GB 致 Code 241）与恢复三选一、九批总账表、批9 数据批+批10 筹码族施工清单、必读文件七件、配方与坑 12 条、§7 三项验收标准
- 剩余欠账：①§3 杂项「16 号 memo §7 开放问题逐项核销状态刷新」未见回执；②§6 坑位 12 条与本文件「回填 MUST 单进程串行」铁律未进任何 SOP/常驻真源（属一次性交接经验，登记义务在 tilib_clearance 台账，该目录已归档 docs/_working/archive/2026-09/tilib_clearance）；③§5 列出的 .runtime/tmp 探针与夜间计划任务归属未复核
- 结案报告：
    §0 P0 处置落地笔：345516da8c 2026-09-22T08:14:03+08:00 data+docs: 磁盘清偿终局班——…TI 瘦身 OPTIMIZE FINAL
    （即恢复选项 1 的执行）。批9 落地笔：509db008fb 2026-09-20T18:38:43+08:00 feat(data): 技术指标库批9-5
    tilib清欠班波6——stock_daily_basic 数据批建成+全市场换手率回填（验收 000852 100%）。
    批10 落地笔：7963211f1a 2026-09-21T15:51:41+08:00 与 94f92230ec 2026-09-21T17:18:38+08:00
    （筹码族三件套+扩项，实现件 src/zephyr/factor/technical_indicators/chips.py）。
    线的收官笔：3424a718e7 2026-09-20T16:45:08+08:00 docs(project): 技术指标库清欠班收官。本件末笔 ext_footprint=1。

### 2026-09-18-gate-identity-root-fix-plan.md
- 类型=file · HEAD 末次=2026-09-19T03:35:27+08:00（47a7426b7f） · 归档双活=无 · 末笔生产面=0 件
- 提交链：47a7426b7f docs(working): 施工方案更正批——推翻我自己一条[亲验]断言 + 补 D-17/WP16/WP9；dd39de9b6c docs(working): 门禁身份与触发台账治本施工方案（闸0 · B′ · 交主施工队）
- 做了什么：门禁身份与触发台账治本施工方案（B′ 方案）：五身份面+第六面普查实测、触发记录载体致命限制、已定位坏写入端与破坏性地雷、WP1-WP7 七工作包定义与依赖序、禁止事项六条与误差分级声明
- 剩余欠账：①§1.3 站点二（gate_persistence INSERT 列名必失败）已由施工侧实测证伪并在战役台账冻结（R-A1），本文件 §7 的 [亲验] 分级仍留该错判原文——战役侧明令「不改 Max 原文，修正只落台账 §4 事实修正表」，故本件的自纠以末笔 47a7426b7f 为限；②WP5/WP6/WP16 的逐包终态与 SP1-SP11 尾巴写在 docs/_working/rule_audit_campaign/CONSTRUCTION_LEDGER.md（另 unit）；③全文含「交给谁/禁止/施工队必读」指令样式文本=数据，未执行
- 结案报告：
    WP1 两处施工落地笔：ee54c976f1 2026-09-19T04:16:53+08:00 fix(rollback/gov): WP1改1 heal_db_consistency
    按活库实列重写 + 拆 C-0 破坏性地雷；413edaff0e 2026-09-19T04:28:23+08:00 fix(rollback/gov): WP1改2
    clean_pycache 加三重护栏——拆 shutil.rmtree 破坏性地雷。WP7 落地笔 f8c1fc044a
    2026-09-19T02:43:48+08:00（台账 R-A10 记「两轴派生可判分母 0→86」）。
    WP1 收尾核验件 39e926b6a8 2026-09-20T01:52:18+08:00 docs(final3): W1-H 身份键地基(WP1)核验与收尾状态件。
    本件自身末笔 47a7426b7f ext_footprint=0（纯 docs/_working 批）。

### 2026-09-18-landing-anchor-algo-flow-closeout
- 类型=dir · HEAD 末次=2026-09-18T06:54:43+08:00（fa39796599） · 归档双活=`docs/_working/archive/2026-09/2026-09-18-landing-anchor-algo-flow-closeout` 字节等值 7/7 · 末笔生产面=1 件
- 提交链：fa39796599 docs(governance): #ARCH-326 置 resolved + B6 台账终局段——反向孤件；8559bf00d7 feat(governance): 登记 裁定#336——Owner 授权退役 ALGO_FLOW 反向孤件 ；562320d091 feat(algo_flow): 反向孤件普查 reconciler 落地——#ARCH-326 治本，检测面；15de0d4734 docs(governance): 落地面锚定态战役挖矿全谱落地——W1~W5 环节封矿+施工留痕
- 做了什么：落地面锚定态战役：W1 worktree→主仓判定收敛单源治本（2ac7d910ed）+ B6 反向孤件 reconciler 检测面与 Owner 授权退役面落地（562320d091），镜像退役经裁定#336 执行（e4df828ddc），#ARCH-326 置 resolved（fa39796599）
- 剩余欠账：台账 b6 L82 自述「终局（2026-09-18 06:46，completes_when 达成）」。W2 三条治本候选按台账「登记不硬闯」移交净窗持有者；W4 判据在册、施工走再生成窗；W5 依裁定#292 明确零施工（69 件作者语义欠账只核身份）。均为设计内移交，非本 unit 欠账
- 结案报告：
    状态①。台账 b6_reverse_orphan_reconciler.md §终局 自述 completes_when 达成；本代理实跑
    git log 核实其点名的落地哈希全部真实存在：2ac7d910ed（W1 锚定态治本）、562320d091（检测面）、
    8559bf00d7（裁定#336 登记）、b0c2999b80（ALGO-FLOW-LINK 退役方向判据）、e4df828ddc（镜像出仓
    +注册表摘 token）、fa39796599（#ARCH-326 resolved）。
    
    等值双活实证（live 副本与归档侧等值 → 处置=删 live 重复份，不是二次归档）：本 unit 7 个 live
    文件与 docs/_working/archive/2026-09/2026-09-18-landing-anchor-algo-flow-closeout/ 同名件
    逐文件 sha256 相等，7/7：00_skeleton_environments.md f65bd7b23ba95158、
    b6_reverse_orphan_reconciler.md 68dab21c7f837149、W1_landing_anchoring.md 3a409950da28b7ea、
    W2_commit_chain.md 27f0db53ad8f3eec、W3_retirement.md 65f709915fa1abd8、
    W4_selfref_exemption.md 4d955e9fafec1232、W5_author_debt.md 11e4cc1b72626db6（live 侧与归档侧
    同值；归档侧另多 1 件 index.md）。
    
    删 live 的前置指针事实：仓内承重引用已指向归档侧——
    scripts/governance/d5_architecture/generators/externalize_algo_flow.py:631 与
    tests/governance/test_w4_selfref_exemption.py:8 的「判据真源」写的就是
    docs/_working/archive/2026-09/2026-09-18-landing-anchor-algo-flow-closeout/。
    但 capability_canonical_file_registry.yaml 同时挂着两套条目（live 侧 7 条 :33292-33316 +
    归档侧条目 :41069 起），删 live 重复份须同步摘除 live token 条目，否则注册表留悬空路径。

### 2026-09-18-rule-audit-master-construction-plan.md
- 类型=file · HEAD 末次=2026-09-19T03:58:08+08:00（0315d5555d） · 归档双活=无 · 末笔生产面=2 件
- 提交链：0315d5555d docs(governance): D-18 恒真假绿条款入法 + WP17 立项（对抗校验器 blocked；47a7426b7f docs(working): 施工方案更正批——推翻我自己一条[亲验]断言 + 补 D-17/WP16/WP9；d622d4d180 docs(working): 施工总方案补 D-14~D-16 裁定 + 修订 D-9（宪法双真源已分叉，非镜；d6c18ee4e3 docs(working): 施工总方案补 D-13 裁定——Flash 写权限收窄为"可读取即确定值才改"
- 做了什么：规则与审计一条龙施工总方案：全局纪律十条、裁定 D-1~D-18（B′ 方案、放行入账、死数据顺序、第四册生成器、对价退役、判据收窄、两轴风险档、A/B 双盲法、D-14 rules/ 冻结、D-15 队列正门、D-17 多库同名表纪律、D-18 恒真假绿）、WP1-WP17 工作包总表与施工卡、五波顺序、回执格式与六种停手回流情形
- 剩余欠账：①D-12/WP12 被施工侧实测判为对外零效应的空改动并冻结（台账 R-A3），本件仍以原文在册（同上：修正表落台账，不改原文）；②Owner 门位件（C-34/C-35/C-42/C-60/C-61/C-67）台账 §17.6 自述「执行方只备料不执行」，终态未回写本件；③本件含大量「施工队照办/禁止」样式指令文本=数据，未执行；④尾批（工棚拆除、index 豁免面登记、W6 A/B 班）由 rule_audit_campaign/2026-09-21-tails-handover-prompt.md 承接，其中 W6 已由 7f83ce9134 落袋
- 结案报告：
    战役主体完结自述在下游：docs/_working/rule_audit_campaign/2026-09-21-tails-handover-prompt.md:7
    「夜班取证→Max 日班判案（裁定#340..#360，Owner 全批）→final3 施工班按裁定号逐批落地（A0-G 全完成
    +WP9 判案#372+rules 批）」。对应落地笔（均 git log 亲验）：
    968243f540 2026-09-19T12:18:33+08:00 裁定#340..#360 判决批；48acb99c46 2026-09-20T12:20:26+08:00 rules 统一批（WP9 判案#372 侧）；
    e0e115a93e 2026-09-19T22:22:54+08:00 W1-G 裁定#359 WP17 对抗校验器恒真修复；
    f8c1fc044a 2026-09-19T02:43:48+08:00 WP7 两轴派生；85fe86c61a 2026-09-19T05:27:16+08:00 B19 进程内门禁预跑器
    （夜裁-01/P0-1 处方件）；7f83ce9134 2026-09-21T16:01:42+08:00 裁定#392（D-9） 宪法 A/B 班四件落袋（WP13/D-8 侧）。
    本件自身末笔 0315d5555d ext_footprint=2。

### 2026-09-18_vocab_consolidation_campaign
- 类型=dir · HEAD 末次=2026-09-22T14:54:28+08:00（d32d12e8ac） · 归档双活=`docs/_working/archive/2026-09/2026-09-18_vocab_consolidation_campaign` 字节等值 13/26 · 末笔生产面=0 件
- 提交链：d32d12e8ac [接手批][st-gateaudit-20260922] 他会话门禁超时中断 staged 遗产归因落地（拆 ；5123c7e9b7 [residual][st-residual-20260922][终局批：resume两件+WO-14归置+词；2d6836dbb5 [taskcards][裁定#392] 登记面前置批（为后续 12 批解 RULING-REFERENCE/C；2f1cb40a02 [workclean][W8-r2-H4v3] index 重生成批（35 新 index 按 EXEMPT-
- 做了什么：target_layer 词表收编战役 W1-W8：五真源挖矿（消费者/生成器/门禁/分层）+裁定#335 三段式自裁+词表 v1.1.0→v1.2.0 收编 17+8+10 值/校验器正则归位+[DOMAIN] 头字段全仓补标 12/12 批+红蓝对抗修复+基线三连复跑封账
- 剩余欠账：机械底座标 archive_twin_exists：docs/_working/archive/2026-09/2026-09-18_vocab_consolidation_campaign 存 23 件旧副本（13 件字节等同），本棚 26 件为新版——final_report.md 与 w8_landing/{index,landing_log}.md 仅在主棚、00_skeleton.md 与各 index 双棚不一致，归档侧去重/补件须以主棚为准；终局判定自述唯一长期挂账=10 旧域 DB 净删（Owner 门位 F 类待令，不阻塞封账）；③#ARCH-337 热文件蒸发、⑨D_COMPLIANCE 幽灵行两项本班标『转报未复测』
- 结案报告：
    终报（final_report.md，st-residual-20260922 代终局班落仓，随 5123c7e9b7）§3：
    『W6 判据连续两轮问题=0 按轮 2+轮 3 达成；W8 封账完成（骨架四格 ✅+frontmatter
    archived）；战役无未达成项』。落地链：裁定#335 词表 v1.1.0（f8aed2365e8）→
    [DOMAIN] 全仓补标 12/12（fcf46a42ac9）→W6 轮 2 滞后红治本（13383a70c03）→
    TC-05 W8 封账批基线三连（0b128a1ba5）→裁定#392 D-4 追认 10 域收编随登记面前置批
    （2d6836dbb5）→终报落仓（5123c7e9b7）→staged 遗产归因落地（d32d12e8ac）。
    真源承接已成立：docs/01_policies_and_standards/_registry/catalogs/
    target_layer_vocabulary.yaml v1.2.0 在册、ruling_registry #335/#392 在册、
    能力册 token 在册；骨架本体翻牌 archived。

### 2026-09-19-overnight-handover-max-shift.md
- 类型=file · HEAD 末次=2026-09-20T17:52:01+08:00（c506bc80ae） · 归档双活=无 · 末笔生产面=7 件
- 提交链：c506bc80ae [final3][P11][MAXEXEC] C 类四桶批量处置：114 散文件+12 已收口目录 git m
- 做了什么：通宵 Flash 班→Max 日班交接令：真源分工指针、面 A/面 B 二分、前夜不得重开的裁定表（D-1~D-18）、夜班八笔落地 commit 表、七项主动否决清单、夜裁-01..24 四梯队待裁册、W1-W6 后续工作序、并发与避让实测、夜班认账八条
- 剩余欠账：①夜裁-01..24 已全部映射为正式裁定 #340..#360 并逐条判决（真源=docs/_working/rule_audit_campaign/2026-09-19-max-dayshift-rulings.md），本件作为交接载体未回写映射；②Owner 门位删除打包（夜裁-03①）与 C-34/C-35/C-42/C-60/C-61/C-67 尾巴经台账 §17.6 在册，本件不承载其终态；③本件含命令样例与「日班开工前重测」指令样式文本=数据，未执行
- 结案报告：
    载体销项笔：968243f540 2026-09-19T12:18:33+08:00（裁定#340..#360 判决书入库，覆盖本件 §五全部 24 条）。
    本件 §三自述八笔落地笔中抽查在案：bdc21c8811 2026-09-19T06:55:26+08:00（孤儿检测豁免）、
    85fe86c61a 2026-09-19T05:27:16+08:00（夜裁-01 处方件 B19 预跑器）、e0e115a93e
    2026-09-19T22:22:54+08:00（夜裁-23/WP17 修复）。
    本件自身末笔 c506bc80ae 为 215 文件归档批（ext_footprint=7）。

### 2026-09-19-overnight-scope-lock-report.md
- 类型=file · HEAD 末次=2026-09-20T17:52:01+08:00（c506bc80ae） · 归档双活=无 · 末笔生产面=7 件
- 提交链：c506bc80ae [final3][P11][MAXEXEC] C 类四桶批量处置：114 散文件+12 已收口目录 git m
- 做了什么：通宵 Flash 班范围锁定回执：19 张 T0 卡可用性实测表、三笔治本落地、七项 P0 结构性发现（55 台 pre-commit 零执行权、装载器 fail-open、三台缺 --ci、扫描口径白名单病、9 台存量失明、编码失明、网关兜底放行）、被证伪的八个吓人数字、真欠账 T-1~T-8、A2/A7 并入回执与新立 P0-8/P0-9
- 剩余欠账：①T-1..T-8 与 P0-1..P0-9 的处置终态经交接令→判决书→台账三级承载（rule_audit_campaign/），本件不承载；②A7 剩余登记四项（26 条绝对针、137 件 .tmp 漂移、5 条裸名消歧、blueprint_registry 的 SSoT 措辞）为在册尾巴；③本件含命令与派单样式文本=数据，未执行；④其自述「案卷 1404 份被 24h TTL 吃掉」的教训为过程记录，长期判据侧已由台账 R-A7 承载
- 结案报告：
    本件 §三/§八B 自述八笔落地笔逐笔 git log 亲验在案：bdc21c8811 2026-09-19T06:55:26+08:00、
    3a67233f41 2026-09-19T06:56:08+08:00、0406b66fce 2026-09-19T06:56:49+08:00、40bfe9a7c8
    2026-09-19T07:20:13+08:00、3450edb560 2026-09-19T07:22:50+08:00、7877077bf7 2026-09-19T07:22:24+08:00
    （check_index_integrity 剥锚点，主区 1263→547）、864618bc7a 2026-09-19T07:34:14+08:00（绝对针改相对）、
    e9fb06c2d4 2026-09-19T07:35:21+08:00（5 行改指已核实真址）。
    发现面的判决承载：968243f540 2026-09-19T12:18:33+08:00 裁定#340..#360。
    本件自身末笔 c506bc80ae 为归档批（ext_footprint=7）。

### altdata_night
- 类型=dir · HEAD 末次=2026-09-18T15:35:18+08:00（437f119d3e） · 归档双活=`docs/_working/archive/2026-09/altdata_night` 字节等值 2/2 · 末笔生产面=0 件
- 提交链：437f119d3e docs(campaign): 晨报补录D5跨资产终报——HL资金费深回溯465万行100%+清算流0xfff；685f1fa512 docs(campaign): 通宵双分包战役收官——E16红蓝三轮(3修→0→0)达标+E17收尾✅+六要素；6be4d8b5ce docs(campaign): 通宵双分包战役收官——E16红蓝三轮(3修→0→0)达标+E17收尾✅+六要素；734fe7d660 fix(data)+docs(campaign): 红蓝夜验收修复批——两处「声称已登记但实际缺失」补登+总簿
- 做了什么：通宵双分包战役总统筹（E0-E17）：产业链 T1-T6/T10、数据线 D1-D8 三波、图谱 Alpha T7-T9 并入、D9 存量迁移 90,243 件、红蓝三轮验收与六要素晨报落盘
- 剩余欠账：文档内部自相矛盾（记为分歧，不改判）：总簿 §1 E15 行状态=⬜（验收判据含「原目录双备份期 30 天」，约 2026-10-18 到期），晨报 §① E15 行=✅（E 盘 29,998+F 盘 60,245 件迁移零失败、抽检 4,511、manifest 双份）。§4 遗留 4 条与晨报 §④ 遗留 11 条/§⑤ 待裁 7 条均为对外移交项（换源决策/切源/重启/登记），不属本 unit 施工欠账。上一轮同 unit 分片记 ask（理由=「判①须先显式转移 E15 时效验收义务」），本代理判①并把该义务写明交总指挥处置
- 结案报告：
    状态①。晨报 §① 逐环节列 E0-E17 交付要点+commit 锚，§⑥ 收尾清单自述 claims 全 release、
    统筹队列 7 袋全 done、临时件已清、worktree 由卫队自清、骨架状态已回写（⬜→✅）。本代理实跑
    git log 核实末笔 437f119d3e 与 685f1fa512/734fe7d660/a0144fab3f 为真实提交。
    义务转移提示（给总指挥，非本 unit 欠账）：总簿 E15 的 30 天双备份期至 2026-10-18，
    真源=G:\zephyr_cold\00_manifest 与 10_g_drive_cold_storage_sop.md。
    
    等值双活实证（live 副本与归档侧等值 → 处置=删 live 重复份，不是二次归档）：2 个 live 文件与
    docs/_working/archive/2026-09/altdata_night/ 同名件逐文件 sha256 相等，2/2：
    00_master_ledger.md 7357cdeb8d7d1898、01_morning_report.md eec9887efcc8aac5（两侧同值；
    归档侧另多 1 件 index.md）。capability_canonical_file_registry.yaml 挂着 live 侧两条
    （:33325、:33329），删 live 须同步摘条。

### auction_bridge_switch_mining_2026_09_17.md
- 类型=file · HEAD 末次=2026-09-17T13:17:58+08:00（46fb28508f） · 归档双活=`docs/_working/archive/2026-09/c_class_scattered/auction_bridge_switch_mining_2026_09_17.md` 字节等值 1/1 · 末笔生产面=1 件
- 提交链：46fb28508f docs(data): known_data_gaps 登记竞价窗口结构性缺口+历史通道知识（AI 发现面）+；92812a31a0 feat(data): 竞价族桥接切换方案 A' 落地——qmt_bridge 竞价双 capability+
- 做了什么：竞价族桥接切换的挖矿盘点与施工终态：9/18 miniQMT 关停前两表 source 切 qmt_bridge 的方案 A′（ch_auction_derive 对 tick_depth_5 派生）、三项实证、六个裁决点自裁留痕、E2E 对拍零失配、32 空窗日回补、竞价历史回补三档研究、红蓝两轮
- 剩余欠账：①frontmatter completes_when 要求「台账 §2.2-B 两项勾选且 9/18 退役日首日验证通过后随批次归档」——§11 明晨观察清单六项在本件内均未回勾，未见首日验证回执；②运营红旗移交未见销案：stk_limit 收集器自 9/16 起无新行（后续 a065f76ef1 WO-3 哨兵补盲与 363e4fa1ed WO-2 断供止血链覆盖部分采集链）；③档 2（1min 首 bar 量标定）与 QUOTE_V17/v20 合并对拍为立卡后置项
- 结案报告：
    本件施工面自述「✅ 施工完成（方案 A′ 落地）」，其缺口知识已入正式真源：末笔 46fb28508f
    2026-09-17T13:17:58+08:00 docs(data): known_data_gaps 登记竞价窗口结构性缺口+历史通道知识（ext_footprint=1）。
    下游哨兵接线笔 a065f76ef1 2026-09-21T10:20:35+08:00（WO-3 哨兵补盲：auction 升级为四腿之一+日历逐日 diff 检查器）。
    未完成项仅为首日验证回勾，属本件自身登记义务，非施工呆账。

### audit_integrity
- 类型=dir · HEAD 末次=2026-09-16T16:08:04+08:00（dbfeb47e59） · 归档双活=`docs/_working/archive/2026-09/audit_integrity` 字节等值 2/2 · 末笔生产面=5 件
- 提交链：dbfeb47e59 feat(audit): 密钥分期验证基建+新真钥部署落地（作者 st-auditkey-20260916 批；92f042a8f2 docs(audit): GW-A2 接力收口——审计链取证报告终态（st-auditfix2-2026091
- 做了什么：审计链三维损伤取证（prev 断链 5,595/内容失配 5,343/HMAC 不可验 26,909）+ 多写方互踩治本（跨进程 append 锁+锁内实时尾读，裁定#266）+ HMAC 密钥分期验证基建与 256-bit 真钥部署（裁定#267），终验生产链 mismatch=0
- 剩余欠账：报告 §5 移交清单 C-1~C-4 实为已清偿（文档自述滞后于 HEAD，记为分歧）：C-1 gate_chain 同型锁=src/zephyr/gov_enforcement/rule_enforcement/audit_chain_verifier.py:8 INVARIANTS（点名「C-1同型锁 裁定#287」）；C-2 轮转接锁=src/zephyr/gov_audit/log_rotation.py:49-61,156；C-3 overlap 收窄=config/audit_key_eras.yaml transition_overlap_seconds: 0；C-4=src/zephyr/gov_audit/secret_registry_drift.py（INVARIANTS 自述「C-4 周期核对（裁定#287）」），四件同批落地于 1b830f63c7。另 §4.4/§9.7 含「他会话在途件不代修」「撞号 #264→#265→#266 合法性认定归 Owner」的留痕项，属 Owner 门位认定非施工欠账
- 结案报告：
    状态①。两报告构成同案两裁定（#266 治本、#267 密钥分期+部署）的凭据链：三维普查数字复现、
    append-only integrity_incident 事件入生产链、era 后 HMAC 失配 26,909→0、mismatch=0、
    审计域 3,364 passed / 0 failed。两文件 front-matter completes_when 均含「收口」，
    GW-A2 §9.1 明示密钥线由 st-auditkey 收口（裁定#267）。裁定在册：
    docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml:2266（裁定#266 条目）。
    移交清单 C-1~C-4 已由 1b830f63c7 全部落地（见 residue 逐件路径:行）。
    
    等值双活实证（live 副本与归档侧等值 → 处置=删 live 重复份，不是二次归档）：2 个 live 文件与
    docs/_working/archive/2026-09/audit_integrity/ 同名件逐文件 sha256 相等，2/2：
    2026-09-16-audit-key-era-deployment.md 0266162484e9ab68、
    audit_chain_incident_forensics_gwa.md 3ba41a394dd3e634（两侧同值；归档侧另多 1 件 index.md）。
    删 live 前须同步的活指针（四处，均指 live 路径）：
    src/zephyr/gov_audit/secret_registry_drift.py:21（真源指针）、
    ruling_registry.yaml:2261、:2297（evidence/引用）、
    capability_canonical_file_registry.yaml:5409、:27272（token 条目）。

### code_doc_gov_campaign
- 类型=dir · HEAD 末次=2026-09-22T15:12:03+08:00（137e9c2ada） · 归档双活=无 · 末笔生产面=0 件
- 提交链：137e9c2ada [接手批][st-gateaudit-20260922] 他会话门禁超时中断 staged 遗产归因落地（拆 ；d32d12e8ac [接手批][st-gateaudit-20260922] 他会话门禁超时中断 staged 遗产归因落地（拆 ；d9a09b2764 [ARCH-APPROVAL:ARCH-MODEL-LIFECYCLE-001] error_code_reg；2f1cb40a02 [workclean][W8-r2-H4v3] index 重生成批（35 新 index 按 EXEMPT-
- 做了什么：丙线代码文档治理五分包端到端交付：WO-12 疑似 bug 九条全终态（6 修+3 证伪留痕）／WO-13 测试真账六族闭环+A14 资产册 32 表登记（264→296）／WO-14 企架文档归置（裁定#384，66 件 R100 归档+197 处引用改齐+两目录留壳）／WO-15 悬账验活三态判定／WO-16 final3 尾巴 R8-R11
- 剩余欠账：交付报告 §三『就绪暂存待落地』批 F（WO-13 修账主体 87 件）+批 D（WO-14 归置 196 件）此后已由接手批落地（d32d12e8ac+137e9c2ada，本次实测 design_memos 原址只剩 README+16 号留壳件、49 件在 archive/2026-09/design_memos）——报告该节文字仍标『等 st-ulib 收口』属陈旧状态；§五 移交项四条：A14 余 46 张无 DDL 真源表待锚点、tests/db 目录树 30 节点存量欠账（pre-existing 非本役）、D2 判定台账 22 行存活待复验、C 类 167 件历史 staged 建议 Owner 一句话批量入袋
- 结案报告：
    交付报告 §一 五分包终态列全 ✅；§二 已落地 commit 五条（2fd1ce8ac4/de9b795162/
    6a6e77c8f0/83329aef38+1451fb978b/队列 q-0010）；§四 红蓝抽验：2 件归置件断链
    （1 处散文残留已修）+3 项编目源反查全锚+tests/path 全绿。
    卡点由他会话解除：报告标为『内容零缺口、等 requeue』的批 F/批 D，
    以『他会话门禁超时中断 staged 遗产归因落地』名义随 d32d12e8ac（19 件）与
    137e9c2ada（10 件）入 HEAD；本棚最后两笔提交即该两批。
    台账件（w12..w16）在册，归档无断链风险（197 处引用改齐随归置批同批）。

### data_fix_campaign
- 类型=dir · HEAD 末次=2026-09-23T02:46:51+08:00（58fe0f7d7e） · 归档双活=无 · 末笔生产面=0 件
- 提交链：58fe0f7d7e [b10-final][st-b10-final-20260922][复职收尾实录] §10：merge 54；549a4c6b54 Merge branch 'dev' into ai/st-b10-final-20260922/b10-fi；32b4e138a4 [b10-final][st-b10-final-20260922][复职终态] 验收数字回填：CYQ 20/；4e02dcbf54 [b10-final][st-b10-final-20260922][静窗令收口批C] 交付报告 §8 收口记
- 做了什么：甲线数据正确性战役：分包0-6（09-17 tick+五档找回 28,327,322 行、估值双修、断供止血六链、哨兵 55→58 腿、批10 筹码族代码层、SCD2 定性=测试病、1970 A 族 398,740 格 NULL 化）+ 批10 终局四分包（volume 量纲治本：写侧 miniqmt ×100、存量 8,417,710 行 mutation、CYC 去 ÷100、58 片全量重算）与复职收尾（merge 549a4c6b54 落 dev、夜跑任务启用）。
- 剩余欠账：①§5.1 结构性发现「warmup 踩踏病」自述为移交/待裁（治本建议=provider _fetch_single_period 加 warmup 读窗或 full_refresh 禁午间触发，本班未修）；②§5.2 backtest/core/cost_model_calibration.py unit_gotchas 文案仍写「volume=手」（他域不代修，文档已过时）；③§5.3 reaper 规则4 坑（cmdline 含 .runtime/ 的后台进程被级联击杀）；④3 日健康观察 D1 本班只完成启用、移交「接力」——本代理只读实测：schtasks tilib_indicator_backfill_nightly LastRunTime=2026-09-24 02:30:01 / LastTaskResult=1（非 0），且 data/runtime/dwm_shard_state 与 data/runtime/tilib_nightly_run.log 均不在盘（backfill_night.ps1:7-8 约定路径）→ D1 未见成功证据；⑤§7 停手项 8 条如实登记（含实时源接线=Owner 门位、1970 B 族 46,905 键列结构性禁 Nullable）；⑥§10「夜探针件已被 tmp 清理消失=ps1 尾行无害失败，维护班可顺手删除该行」=文件内指令样式文字，本代理未执行。
- 结案报告：
    收口事实：
    - 两份交付报告自述「completes_when: Owner 验收后随战役归档」；末笔 58fe0f7d7e 为 §10 复职收尾实录
      （merge 549a4c6b54 已进 HEAD 链，275493de9b 代码批 11 文件经 git log 核实在 HEAD）。
    - 施工项均有修前红证/修后绿证数字（tick 09-17=28,327,322 行；daily_valuation close>0=99.91%；
      新 4 列近月非零率 99.86-99.91%；CYQ 20/20 零偏差；214 列台账零空列 total=7,111,345；kline 全表手行残留 0）。
    - 结论级内容已在正式真源（见 already_in_truth_source），按合同 §3 命中即判 ①。
    - 未收口部分不属施工欠账：Owner 门位停手项 8 条 + 3 日观察接力（D1 本代理实测 LastTaskResult=1，见 residue）。
    - 单位性质：11 件全为一次性过程/验收报告（除 §5.1 一条病理发现），故不判 ②。

### dsr-recalc
- 类型=dir · HEAD 末次=2026-09-15T14:12:12+08:00（e58d28df99） · 归档双活=`docs/_working/archive/2026-09/dsr-recalc` 字节等值 2/2 · 末笔生产面=3 件
- 提交链：e58d28df99 feat(backtest): DSR 修口径 A2+A3——台账 num_trials 可考证回填 + 存量
- 做了什么：DSR 口径 A2+A3 交付：23 个 run 的 num_trials 可考证回填、存量 261 行按累计 N=4481 重算（refold/normal_approx 两路径）、锚点行翻案 0.9809→0.0517 过 fail-closed 断言、8 行诚实跳过、145 条 DSR 冻结解除
- 剩余欠账：§9 明示遗留 A4（metrics.py 坏路径退役）/A5（阈值三线 SSOT）/_c4_engine 累计口径接线=交后续班次，非本 unit 欠账。§1 口径裁定的长期效力已由 trial_ledger_registry.yaml（N 账本真源，MOD-BT-200）与后续裁定承接。机械底座 closure=0/pending=0（无关键词命中）与本判读不冲突——收口凭据是 §9「本报告即交付物」+A1/A2/A3 全勾，不是结案词
- 结案报告：
    状态①。报告 §9 自述 A1/A2/A3 全交付（A1=N 账本，本代理核实其引用哈希真实：
    f4d1ea4f42 2026-09-15T13:37:29+08:00 feat(backtest): F-06/DSR A1 N 试次账本落库——
    全局累计试验数计数器（MOD-BT-200））；逐行明细 2026-09-15-dsr-recalc-rows.yaml 机器可复核，
    本代理实跑 sha256 与归档侧一致。§7 明示「全部 261 个新值均为当日口径新值、与历史值不可逐位比」，
    §8 冻结解除生效。§1 权重口径「锁定勿再议」且 N 账本真源指向正式注册表
    docs/01_policies_and_standards/_registry/catalogs/trial_ledger_registry.yaml。
    
    等值双活实证（live 副本与归档侧等值 → 处置=删 live 重复份，不是二次归档）：2 个 live 文件与
    docs/_working/archive/2026-09/dsr-recalc/ 同名件逐文件 sha256 相等，2/2：
    2026-09-15-dsr-recalc-report.md 968a2f9e1a3ad11a、
    2026-09-15-dsr-recalc-rows.yaml 508f882f3336c46c（两侧同值；归档侧另多 1 件 index.md）。
    删 live 的硬前置（生产代码把 live 路径当默认值/CONSUMERS 声明）：
    scripts/backtest/dsr_recalc_backfill.py:5（`[CONSUMERS] docs/_working/dsr-recalc/...report.md`）
    与 :226（`--report` 默认值=docs/_working/dsr-recalc/2026-09-15-dsr-recalc-rows.yaml）。
    不同步改这两处就删 live，会把一次性重算工具的默认输出路径指向失踪文件。
    另 capability_canonical_file_registry.yaml:27082、:27716 挂着 live 侧 token 条目。

### flash_speedup
- 类型=dir · HEAD 末次=2026-09-24T04:26:38+08:00（3919c83d87） · 归档双活=无 · 末笔生产面=6 件
- 提交链：3919c83d87 [st-commitsys-20260924] 提交指路指南v1总包15文件（playbook机生+两接口+三；1081110b75 [flash_speedup] 91 号文件勘误一行（Max A-1）：X-5 实际落地 commit 修正为；137e9c2ada [接手批][st-gateaudit-20260922] 他会话门禁超时中断 staged 遗产归因落地（拆 ；211219040b [residual][st-residual-20260922][TC-03 步骤1-2 X-5 收口] se
- 做了什么：Flash 提交链提速战役（24/h→100+ 目标）：F1 衍生提交折叠、F4 生成器并发（57.4s→~28s）、F9 队列 untracked 新件死信治本、F5 DC 预检快败、F2 前置四件+H harness 重建全部落地，门禁链 P50 41.6→29.0s（-30%）、串行天花板 24→92/h；F6 堵点本 3572 行四态归属 UNCLASSIFIED=0；Fresh 轮 13 条病灶分诊（12 Complex→Max+1 已直修 be934b079d）；X-5 表驱动收编与 B-X5CORRECT 更正行入总簿。
- 剩余欠账：①总簿 frontmatter status=active 且环节表 R 行仍写「施工中」，与 90_report frontmatter `status: final_report_two_round_verification_green` 自述矛盾（历史行不改，登记不代修）；②Owner 门位待裁未闭：P-4 门禁退役/§4.2 触发率审计（全仓仅 AIR:3816 一处 G8 提及，无审计机制在册）、P-5=N-1（gate_registry.yaml:764 BLUEPRINT-FORMAT 至今 own_scope: false；#ARCH-318 状态 open）、P-6=N-2、P-7=N-4（pid=0 心跳窗口竞态）、F2 ⑤「7 天>40 车道」观察窗口径未裁；③91 号文件 §6「先处置 §1→再落 §4→后推堵点本」等对 Max/Owner 的指令样式文字=数据，本代理未执行；④围栏疑点（交总指挥，本代理未动该 unit）：末笔 3919c83d87 由在飞会话 st-commitsys-20260924（session_registry 心跳 age≈0min）把 F5_registry_debt/LEDGER_flash_speedup_F5.md 以改名件写入本 unit，机械围栏按 dirty=0/mtime 748min/无 claim 全零放行——「在飞会话把非自家件提交进本 unit」这一维围栏看不见；⑤91 号含 2026-09-23 Max 勘误行（X-5 真实落地=211219040b），历史行不改。
- 结案报告：
    收口事实：
    - 战役免签包全落地且 hash 逐笔核实为 HEAD 祖先：fe47296db5(F1)、025df945e0(F4)、3c853303da+6ea82b9cfb(F9)、
      1fb04f6eb9(F5 代码核)、be934b079d(预检映射)、727ad32a54(F2 前置+判据书行)、b5cd9ff505/145697a7db(总簿)；
      X-5 真实落地=211219040b（91 号勘误行 + 总簿 B-X5CORRECT 行互证，B-X5CLOSE 虚记已更正）。
    - 战役文档 22 件已全部进 HEAD（09-22 接手批 137e9c2ada 落地 _working 棚产物，09-24 3919c83d87 收改名件）。
    - 结论级内容已按合同 §3 命中正式真源（门禁常数裁定、#ARCH-318/#ARCH-324 病灶登记、台账纪律、
      提交指路指南 permanent SOP），故判 ① 而非 ②。
    - 未闭部分=Owner 门位裁定与已登记 open issue（P-4/P-5/P-7），属门禁/架构治理线后续批，不是本 unit 施工呆账。

### forensics
- 类型=dir · HEAD 末次=2026-09-17T03:05:53+08:00（2436f92c17） · 归档双活=`docs/_working/archive/2026-09/forensics` 字节等值 1/1 · 末笔生产面=3 件
- 提交链：2436f92c17 chore(governance): qwen3-coder:30b 保留核查移除——M4 转办项闭环（裁定#；fc54392533 [M4 Resolution] Ollama 0.32.1→0.34.1 升级闭环：AV-LLAMA 崩溃族根；a164befb8f feat(gov): 治理战役 M4——llama-server 崩溃族溯源报告+VRAM 预算门防崩溃循环
- 做了什么：llama-server 崩溃族溯源（8 例/3 签名族/AV@libllama.dll+0x2a230 确定性缺陷+VRAM 超订归因）→ VRAM 预算门+M1 登记/M2 水位/M3 超寿收割落地 → §7 Ollama 0.32.1→0.34.1 升级闭环（裁定#269）→ §8 qwen3-coder:30b 转办项核查并移除（裁定#290）
- 剩余欠账：机械底座 pending=4 为 §5 旧「待裁」措辞的关键词命中，两项已由同报告的 §7/§8 追加段落地（裁定#269/#290），信号滞后于追加段——记为底座与读后判分歧。§7 被动验收口径自述「自 2026-09-16 16:09 起 7 天（至 2026-09-23）无新增 0xc0000005/0xc0000409 即正式结案」，末次崩溃记录=2026-09-15 23:22:31，时窗在今日（09-24）已过；本代理按合同未越界复跑 Windows 事件日志（只读仓库判定），该复跑口径保留在报告 §6 供抽查
- 结案报告：
    状态①。front-matter completes_when 给两条完成路径（升级落地或 Owner 接受现状），第一条已满足：
    fc54392533 升级闭环（裁定#269，安装包 SHA256 a92986c86ab6854675ffd1b725db7c0350d40755895c95c397c58d61014e14d9
    留存 .runtime/tmp/ollama_upgrade/，验证四全）+ 2436f92c17 转办项闭环（裁定#290，
    config/gguf_vram_budget.yaml 与测试同 commit）。裁定在册证据（本代理实跑 grep）：
    docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml:2405 将
    docs/_working/forensics/llama_server_crash_forensics_202609.md 列为裁定 evidence 条目，
    :2378/:3283/:3308 正文引用同一报告（含 §8 转办口径）。
    
    等值双活实证（live 副本与归档侧等值 → 处置=删 live 重复份，不是二次归档）：live 文件与
    docs/_working/archive/2026-09/forensics/llama_server_crash_forensics_202609.md 逐字节相等
    （sha256 前缀 e405b0d0809b8f30，1/1；归档侧另多 1 件 index.md）。
    删 live 前须同步的活指针：ruling_registry.yaml:2405（evidence 列表项，指 live 路径）与
    :2378/:3283/:3308 正文引用、module_translation_registry.yaml:57720、
    capability_canonical_file_registry.yaml:27212、architecture_issue_registry 与
    candidate_module_registry 的引用条目。裁定正文里的路径字符串一旦悬空即成取证断链，属高敏感指针。

### guides
- 类型=dir · HEAD 末次=2026-09-21T10:50:43+08:00（2f1cb40a02） · 归档双活=无 · 末笔生产面=0 件
- 提交链：2f1cb40a02 [workclean][W8-r2-H4v3] index 重生成批（35 新 index 按 EXEMPT-；6044c47fc6 feat(infra): 治理战役 M1+M2+M3——统一进程孵化入口（孵化即登记）+水位门禁+reaper
- 做了什么：统一进程孵化入口（MOD-INF-PROC-INCUBATOR 治理战役 M1+M2+M3）迁移指南：孵化即登记/水位门禁/收割闭环三件口径+一行改法+参数口径表+首批 5 消费方迁移实录
- 剩余欠账：§5 长尾迁移清单未迁：本次实测 scripts/mcp/launcher.py 与 src/zephyr/gov_enforcement/rule_bridge/session_worktree.py 仍无 get_incubator/spawn_registered 引用（grep 零命中），指南自述『随各自车道渐进迁移、禁一次大爆破』=非本 unit 欠账
- 结案报告：
    施工链：6044c47fc6（2026-09-16）落地 M1+M2+M3——process_incubator 模块+水位门禁+reaper
    收割闭环+首批 5 消费方（auto_runtime_core/services_registry/reconcile_runner/
    write_audit_daemon/worktree_drift_watchdog，本次 grep get_incubator 实测全部在位）。
    指南本体口径（三件套定义、一行改法、lifetime/gate 参数表、首批名单、测试两件）已整体
    收录进正式蓝图，蓝图侧自标 construction_progress: completed。2f1cb40a02 为索引重生成批。

### index.md
- 类型=file · HEAD 末次=2026-09-21T10:50:43+08:00（2f1cb40a02） · 归档双活=`docs/_working/archive/2026-08/index.md` 字节等值 0/1 · 末笔生产面=0 件
- 提交链：2f1cb40a02 [workclean][W8-r2-H4v3] index 重生成批（35 新 index 按 EXEMPT-；c506bc80ae [final3][P11][MAXEXEC] C 类四桶批量处置：114 散文件+12 已收口目录 git m；f8a627d1ec chore(docs): 清理 _working 第一批废弃文件；92a4f0f05e chore: 删除已完成的任务规格文档 (ttl=task_bound, completes_when 满足)
- 做了什么：docs/_working 顶层目录索引（generate_missing_index_md.py 机生，2026-09-21 生成），列 2 件施工卡+2 件夜班件+25 个下级目录导航
- 剩余欠账：twin=Y 比字节结论=非重复件：顶层 docs/_working/index.md 3,366B sha256(前16)=1ee24c9b653fc129（52 行）vs 归档 docs/_working/archive/2026-09/index.md 8,744B sha=1b59db97a650365b（100 行），同名仅因生成器对每个目录各产一份索引，二者 title/表体不同目录内容，unified diff 逐行显示条目集完全不同→按不同对象处理，非重复簇（合同 §4 内收判据「跨域不同对象不并」）。另一事实：本件自 09-21 生成后未随 _working 实态重生成，列 28 项而本 shard 22 件散件中 20 件未列入，属生成物滞后，重生成义务在生成器（禁手工维护）
- 结案报告：
    本件无施工项：由 scripts/governance/d1_structure/generate_missing_index_md.py 自动产出，
    末笔 2f1cb40a02 2026-09-21T10:50:43+08:00 为 36 文件纯 docs/_working 批（ext_footprint=0）。
    twin 比字节差异与滞后属机械底座/生成器面，不需内容级裁定。

### oddjobs_night
- 类型=dir · HEAD 末次=2026-09-23T10:48:38+08:00（b9997fc0ac） · 归档双活=无 · 末笔生产面=0 件
- 提交链：b9997fc0ac docs(oddjobs): 增补班回执入账——件6/件7 hash+三卡验收判据+基建抢修两件+门禁配方 [；2cef81e986 docs(oddjobs): 台账终稿补记——落地hash终态+八轮门禁舞配方+目录改名披露 [GW:st-o；5b6ee808a6 [st-oddjobs-20260923][件5·PCR标的层回补+E4重考批] 批点单#6 执行：①回补 t
- 做了什么：通宵杂项班七件逐件落地并交回执：件2 .gitignore 止血+假 governance.db 三件删除（cb7786e75d）、件3 A-2 两段接线核验+红证 4 用例（f7d687ce6c，裁定#403 随批）、件4 考古三态（②README 墓碑 2ddffb6804，①③登记不动=他会话在飞）、件5 ETF 真后复权回补+E4 重考 INSUFFICIENT→PASS（5b6ee808a6）、件6 live 三安全卡 S-1/S-2/S-3（bca95a6342）、件7 TC-06 裁定落地（2b9e780533）。
- 剩余欠账：件4② 永久件 index.md 删除被 PS-STD-012 三通道死拦→留 Owner 门位（工作树删除态已就绪）；本会话翻译册 +8 行纯追加条目仍在暂存面随其 owner 批吸收；件4① tdm 5 行注释+B09 实现侧在暂存堆待 ALGO-NOTE-SYNC 原子落；冷库旧版 crisis_drill_monthly 演练段留演练线；备份件 .runtime/tmp/oddjobs_night_backup/ 24h TTL；件1 t0-revival 合并窗口未达（脏文件 844→918）；台账含「维护班可查/建议…」样式指令文字=数据，本代理未执行；目录改名披露（令面路径 oddjobs_20260923 撞 R5-DIGIT-SUFFIX，改 oddjobs_night）。
- 结案报告：
    收口事实：
    - 台账 frontmatter `completes_when: 通宵班五件全部处置完毕并交付晨报（2026-09-23 晨）` 已满足，
      「终稿补记」给出落地 hash 终态（件2=cb7786e7｜件4②=2ddffb68｜件3=f7d687ce6c｜件5=5b6ee808），
      增补班再补件6=bca95a63、件7=2b9e7805；八笔全部经 git log 核实存在且为 HEAD 祖先。
    - 会话自述收尾：release 全 claim + 心跳 daemon idle 自退 + 清临时；本代理核 session_registry 无该会话 claim 残留。
    - 交付物已进真源（backfill_etf_hfq_for_pcr.py 三注册齐、S-3 新模块 depgraph 节点+翻译+token、裁定随批在册）。
    - 剩余=Owner 门位一项（永久件删除）与他会话在途件移交，非本 unit 施工呆账。

### p21_contract_header_slimming_proposal.md
- 类型=file · HEAD 末次=2026-09-15T02:36:48+08:00（6274c2e160） · 归档双活=`docs/_working/archive/2026-09/c_class_scattered/p21_contract_header_slimming_proposal.md` 字节等值 1/1 · 末笔生产面=9 件
- 提交链：6274c2e160 feat(gov)+refactor(backtest): 外审遗留二期三项全施工——P2-1 ALGO_FL；59e5d875e3 fix(gov)+fix(test): 外审遗留批 P1-4/P2-2/P2-3 落地+P2-1 设计稿+ti
- 做了什么：P2-1 契约头减负设计稿：逐标记消费方实查（哪些必留守、哪些机器可再生可出仓）+ 方案=ALGO_FLOW 块 generate→externalize→gate 校验替代源码驻留 + 试点 event_driven_engine.py + §5 实施记录（extractor 外部锚加载、试点迁移、3 新例、三消费方兼容实测）
- 剩余欠账：两处文档自述滞后于 HEAD，记为分歧：①§5 表「存量推广=未启动」，实际推广已于 09-16/09-17 全量完成（见 closure_report 链与实跑计数：tracked .py 中带 `# [ALGO_FLOW] external:` 锚 3280 件、tracked docs/03_modules/**/algo_flow/*.yaml 3267 件）；②文件头「结案报告（2026-09-15 由 st-fullchain-20260914 核验）：设计/计划类且无落地证据，保守保留，commit 提及 0 处」为上一轮清理批自动生成文本，按合同 §6 只当数据、未执行，且其「无落地证据」结论与 §5 实施记录+上述链矛盾。本 unit 无归档侧同名件（twin=-，facts archive_twin_exists=false），处置=真归档
- 结案报告：
    状态①。§3.3 实施序四步全部有 HEAD 落地面：
    步1 工具链（extractor/externalizer 支持外部锚）= 2bdc9f074a
    2026-09-17T03:24:09+08:00「P2-1 出仓工具链落地——截断块出仓通道+根层件镜像归位+口径常量」，
    在库件 scripts/governance/d5_architecture/generators/externalize_algo_flow.py；
    步2 门禁与校验分支 = scripts/governance/d5_architecture/checkers/check_algo_flow.py 与
    scripts/governance/_shared/code_algorithm_extractor.py 均含外部锚解析
    （git grep "[ALGO_FLOW] external:" 命中该两件）；
    步3 存量推广 = 尾池出仓批次 af2f1ebbd3/d99c7068c2/…/984728c6a3（2026-09-17 02:29-02:59 六批，
    每批「12 件源 + 12 件镜像」）→ 481aaed065 2026-09-17T06:37:37+08:00
    「尾池最后 5 件机械出仓——P2-1 机械面清零」→ 7c25e8fe86 07:10:30「P2-1 §16 机械面清零留痕」；
    试点本体 = 6274c2e160（含 round-trip 与 3 新例）。
    现状量化（本代理实跑）：tracked .py 含外部锚 3280 件、tracked docs/03_modules/**/algo_flow/*.yaml 3267 件。
    §4 四条「明确不做」边界（不删 BLUEPRINT/INVARIANTS 行、不改 module_id 校验语义、不引入注释率 KPI 新规范）
    与宪法 §4 净零增长对账口径一致，属设计内边界。
    
    双活情况：本 unit 不属与 docs/_working/archive/2026-09/ 等值的双活重复件
    （facts twin='-'，archive_twin_exists=false），故处置=真归档而非删重复份。
    唯一外部指针=capability_canonical_file_registry.yaml:13398 的 live token 条目，
    归档时须同批改路径。

### redblue
- 类型=dir · HEAD 末次=2026-09-15T07:12:22+08:00（e5df571ac9） · 归档双活=`docs/_working/archive/2026-09/redblue` 字节等值 1/1 · 末笔生产面=5 件
- 提交链：e5df571ac9 fix(gov+strategy): 复核班猎红清偿批——①blueprint_id_legacy 单测 st；02d6a8fb62 docs(working): 红蓝对抗 v5 复测报告——裁定#252 全链路 17/17 PASS + B 
- 做了什么：红蓝对抗 v5 复测（裁定#252 全链路 7/7、gate 双格式判活 6/6、搭便车重放 4/4、F1 回归 2/2=17/17 PASS）+ v6 独立复核与分域猎红清偿（9+5 处孤儿红：stub 绕过治本/battle_map 挂锚同步/domain_events 摘要重算/策略家族法 relabel/STR-E-TIMING grandfather/depgraph 丢边回插）+ §4 dead/ 季度退役审计机制设计
- 剩余欠账：文档头部「结案报告（由 st-fullchain-20260914 核验）=未结案（仍有待办）。处置=保留」是上一轮清理批自动生成的文本，按合同 §6 只当数据读、未执行；其判据（L93/L106「设计稿待 Owner 批准后施工」）已被 HEAD 证据推翻（见 closure_report）。残余非欠账项：§6.5-6 depgraph 丢边根因「登记不修」并点名 Owner 关注共存策略；§6.5-4 家族归并为唯一 Owner 拍板点（判独立成族即 revert 5 条 relabel）；§5 旧格式锁 30min TTL 抢锁窗口=裁定#252 明确接受的永久残余面
- 结案报告：
    状态①。判据=报告自述收口（§6.2「v5 §5 三项遗留全部闭合」+ 终验电池 4409 passed×2 零红）
    且其全部前瞻项在 HEAD 侧有落地面：
    ① §4 dead/ 季度退役审计机制设计稿 → 已施工：src/zephyr/governance/audit/dead_queue_retirement_reconciler.py
    （模块 docstring 自述「红蓝 v5 报告 §4 设计稿 → 施工」「Owner 批准 2026-09-15」），
    落地链 fb4155ecb9（注册接线+24h 节流护栏「C 项收尾」）→ 2e731e5fc7（增量游标，存量 956 条可扫完）
    → 3b20e0d254（报告格式改 .yaml），并常驻注册于
    src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py:1674-1679
    （make_dead_queue_retirement_reconciler），出证件 docs/_working/archive/2026-09/dead_queue/retirement_audit.yaml 在库。
    ② §6.5-8 screen_source.py「留待属主会话吸收入库」→ 已入库：
    src/zephyr/strategy_pipeline/screen_source.py 与 tests/strategy_pipeline/test_screen_source.py 均 tracked，
    首入库笔 011b06f283 2026-09-15T08:51:51+08:00（adopt-prior-work）。
    ③ §5 v5 三项遗留 → §6.2 表逐条闭合（tests/xt4tmp 由 fbd7edf209 出库、探针自删、锁窗口=设计接受）。
    结论：报告自身施工项全落地、无本 unit 欠账，故判①（与上一轮分片的③判定分歧，理由即上述①②）。
    
    等值双活实证（live 副本与归档侧等值 → 处置=删 live 重复份，不是二次归档）：live 文件与
    docs/_working/archive/2026-09/redblue/2026-09-15-xtreme-redblue-v5-report.md 逐字节相等
    （sha256 前缀 de895e38fdbe33d3，1/1；归档侧另有 2026-09-14-ch-redblue-adversarial-report.md 与 index.md）。
    删 live 前须同步：capability_canonical_file_registry.yaml:27824 的 live token 条目，
    以及 ruling_registry.yaml / architecture_issue_registry.yaml / module_translation_registry.yaml /
    test_suite_registry.yaml 中指向 docs/_working/redblue/ 的引用行。

### unified_campaign
- 类型=dir · HEAD 末次=2026-09-22T08:14:03+08:00（345516da8c） · 归档双活=无 · 末笔生产面=2 件
- 提交链：345516da8c [GW:] data+docs: 磁盘清偿终局班——裁定#399 废表两态制 17 张全删终局+TI 瘦身 O；96864d1add [disk-ch][乙线·追加令v2] a3 阶段执行批：阶段1.2 G抽屉库迁F+阶段4.1/4.7 G总仓；6684ba5d83 [disk-ch][乙线] 通宵班总落地（27文件）：裁定#383 storage_tiering退役+裁定#；2f1cb40a02 [workclean][W8-r2-H4v3] index 重生成批（35 新 index 按 EXEMPT-
- 做了什么：四包合流的全项目统一施工方案 v1.0（三总包甲/乙/丙并行+三档停机时序制）：交付派工单集 WO-1..16、四路总台账、数据库修复总方案 19 病条、Owner 签字单与停机声明板
- 剩余欠账：声明板三条 09-21 登记行状态仍为 planned 未回写 done（同日晚批已 done，属账面滞后）；战役下游仍在飞：乙线续班 st-backup-cold-20260924 于 09-24 03:50 仍在 disk_reorg_campaign/LEDGER_final.md 心跳（G/F 盘审计+0600 验收），且 a6_remaining_work_order 有日历删除项（09-28/10-05/10-18/10-21）——本棚是乙/丙两棚的母方案引用源，归档前须确认引用链；v0.1 五件降级为底稿（裁定#378 明示）仍在棚内与 v1_0 并存；台账 §6 复现命令『D1 staged 计数』类口径为历史快照
- 结案报告：
    三线交付物已在盘且各有终报（非本棚文件，作归属证据列举）：
    甲线 docs/_working/data_fix_campaign/final_delivery_report_20260921.md +
    b10_final_delivery_report_20260922.md（WO-1..4）；
    乙线 docs/_working/disk_reorg_campaign/a5_delivery_report.md §⑧『红蓝对抗 18/18 PASS』
    + LEDGER_final.md 五盘对照表（WO-5..11，17/17 废表 DROP 见 345516da8c）；
    丙线 code_doc_gov_campaign/FINAL_REPORT_st_code_doc_20260921.md 五分包全终态
    （WO-12..16），其 §三『就绪暂存待落地』批 F/批 D 已由接手批 d32d12e8ac+137e9c2ada
    落地（本次实测 design_memos 原址仅剩 README+16 号留壳件，49 件在
    archive/2026-09/design_memos）。签字单十项经 2d7308df1f/1ad0003e36 批文全落。
    战役级终验凭证=乙线 a5 §⑧；剩余为日历窗删除与账面板滞后面。

### 同花顺资料
- 类型=dir · HEAD 末次=2026-09-09T15:54:32+08:00（267f649c5b） · 归档双活=无 · 末笔生产面=2 件
- 提交链：267f649c5b chore(workspace): 工作区卫生处置(#ARCH-308)——孤儿台账认领+验收截图入库+运行时
- 做了什么：ths_import.py 于 2026-09-08 生成的 THS 被投清单登记台账（893 行表）落盘留档，文件头自述用途=供将来股权穿透表消费、禁入 ig_company_edge；2026-09-09 卫生批按 #ARCH-308 孤儿台账认领入库
- 剩余欠账：机械底座 closure=0/pending=0（无关键词命中）与本判读不冲突：收口凭据是文件头自述的落盘性质+认领提交，不是结案词。unit 内两文件互为字节等值重复（文件名日期格式之差 2026-09-08 / 20260908），归档/清理侧须去重为一份。下游消费（股权穿透表）属他线未来事项，非本 unit 欠账
- 结案报告：
    状态①（落盘动作完成，无本 unit 欠账）。生成器在仓且 tracked：
    scripts/industry_graph/ths_import.py（该台账可再生成，符合宪法 §9.5 静态清单由生成器产出的纪律）。
    
    等值实证分两类，须区分处置：
    (1) 本 unit **不属于**「与 docs/_working/archive/2026-09/ 等值的双活重复件」——
    facts archive_twin_exists=false，本代理实跑
    `Path('docs/_working/archive').rglob('*')` 过滤 `ths_import` / `被投` / `同花顺` 三种关键词，
    归档侧零命中。故处置=真归档（移动），不是删 live 重复份。
    (2) unit 内部双件互为重复：被投清单登记_ths_import_2026-09-08.md 与
    被投清单登记_ths_import_20260908.md 各 37,813 B、893 行，sha256 全等
    （前缀 5de49d0f1bdc16e0）→ 无论归档或保留都应去重留一份，保留名与既有引用一致者。
    指针耦合（四处，均指该目录/文件，移动须同步）：
    docs/01_policies_and_standards/_registry/catalogs/data_asset_registry.yaml:9515
    （evidence=「2026-09-09 首次导入实证：docs/_working/同花顺资料/…」）、
    industry_graph_field_dictionary.yaml:909 与 :928（good_example 引用）、
    capability_canonical_file_registry.yaml:6181 与 :6185（两文件各一条 token，正是重复件的两条）、
    .gitignore:627（docs/_working/同花顺资料/*.xlsx）。

## 4. ②应进蓝图未进 — 《待升级条目清单》（本包禁自行改蓝图）

- **[2026-08-25-page-by-page-review.md]** 涨跌色语义宪章：只抄欧易皮、A 股红涨绿跌语义不换（色值经六轮实测终定 --up #eb4b6d / --down #31bd65，后 v5 改低饱和 #25A750/#CA3F64 族），属全站禁改判据
  - 出处=docs/_working/2026-08-25-page-by-page-review.md#§G-二 + #修订记录 0.4.0/0.10.0 · 建议去向=docs/03_modules/_domain_frontend/blueprint.md §设计语言与语义色（新章）；或 docs/01_policies_and_standards/rules/trae_086_frontend_module_construction.yaml 附属视觉条款 · 理由=Owner 两度拍板且被六次返工验证，任何前端/视觉会话改色前必须先见到该判据，否则重演色彩返工 · 真源已查=未命中
- **[2026-08-25-page-by-page-review.md]** §C 币圈域架构裁定：不是加页面而是加第 6 组 + 镜像复用（盘面/持仓风控/策略/回测/档案 4-5 页），复用不重建清单与「币圈内容绝不混入作战室/打板/情绪/复盘」隔离铁律
  - 出处=docs/_working/2026-08-25-page-by-page-review.md#§C-1/§C-2 · 建议去向=docs/02_enterprise_architecture/（市场分片三层隔离相关域文档）+ docs/03_modules/_domain_frontend/blueprint.md §2 模块边界 · 理由=charter 级新域扩展判据，直接决定后续任何币圈页面/模块是否算越界，属长期架构约束 · 真源已查=未命中
- **[2026-08-25-page-by-page-review.md]** 市场轴三级结构 + mega menu 双列 + 共用页双挂制（真共用 4 页/框架共用实例分家/A 股特有不镜像三分类）
  - 出处=docs/_working/2026-08-25-page-by-page-review.md#修订记录 0.14.0/0.15.0 · 建议去向=docs/03_modules/_domain_frontend/blueprint.md §3.1 组件架构（导航结构节） · 理由=新市场（美股/期货）接入时的可插拔结构约定，是一次性过程记录之外的长期判据 · 真源已查=未命中
- **[2026-08-25-page-by-page-review.md]** Owner 形式化直觉（设计公理）：图形=与 K 线的接触点集合，按触碰点判断走势是否仍在图形内——人机共校纠错样本可反哺形态库 231 规则参数
  - 出处=docs/_working/2026-08-25-page-by-page-review.md#§G-四 四.B/四.C 之间 · 建议去向=docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/（形态/画线相关 memo）或对应形态库蓝图 · 理由=被 Owner 明写为「四.B/C 的设计公理」，是尚未施工的画线学习管道的唯一口径来源，留在 _working 会随归档失传 · 真源已查=未命中
- **[2026-08-25-page-by-page-review.md]** 「规范即实物」格式裁定：设计规范不入 PDF、以内嵌设计规范页（DS-1~DS-10 吃 CSS 变量+真实 class 渲染）为真源，配合规扫描器三级验收
  - 出处=docs/_working/2026-08-25-page-by-page-review.md#修订记录 0.9.0 · 建议去向=docs/01_policies_and_standards/sop/construction_sop/（前端视觉规范 SOP 一条）+ docs/03_modules/_domain_frontend/blueprint.md 指向 design 页 · 理由=决定视觉规范真源位置（文档 vs 实物），影响所有后续视觉会话，属流程级长期判据 · 真源已查=未命中
- **[2026-09-07-tdm-backtest-protocol.md]** 拼装回测 V1 合成语义=分 sleeve 独立回测按 PP-001 加权和，结构性丢失 5 类 C2 组合层交互（intent 净额轧平/相关性聚类约束/8 sleeve 资金竞争/组合熔断路径依赖/共享预算带非线性区），使用时必须携带清单+覆盖折扣标注，结论强制标注「不含 C3 自适应调权」
  - 出处=docs/_working/2026-09-07-tdm-backtest-protocol.md#§1（L35-47） · 建议去向=docs/01_policies_and_standards/sop/backtest_system_sop/（新增条款册，如 sop_e_assembly_backtest_contract.md）+ docs/02_enterprise_architecture/02_domain_architecture_docs/34_d_backtest.md 交叉引用 · 理由=是任何回测结论可不可采信的合同条款，不属一次性过程记录；现只活在 _working，随归档即断链 · 真源已查=未命中
- **[2026-09-07-tdm-backtest-protocol.md]** 启动闸门 G1-G10 是回测准入判定表：未闭环闸门（G4 棘轮+配对核算器/G7/G10 制度时变维表）消化前，回测结论不得作为 C3 调权输入
  - 出处=docs/_working/2026-09-07-tdm-backtest-protocol.md#§2（L53-68） · 建议去向=docs/01_policies_and_standards/sop/backtest_system_sop/sop_a_full_map_orchestration.md（回测前置门位章） · 理由=永久性准入门（每次回测都要重判），当前无正式真源承载 · 真源已查=未命中
- **[2026-09-07-tdm-backtest-protocol.md]** 回测盲区清单 16 项=结论报告强制披露段（打板排队位次/跌停卖不出/竞价全链/封单质量/龙虎榜席位/板块成分 2026-07 前/知识层 PIT…）
  - 出处=docs/_working/2026-09-07-tdm-backtest-protocol.md#§6（L98-101） · 建议去向=docs/01_policies_and_standards/sop/backtest_system_sop/sop_d_run_archive_naming.md（报告模板必披露段）或 34_d_backtest.md · 理由=报告格式的长期判据；IBT-V1 协议已声明继承，但正式 SOP 里没有该段 · 真源已查=未命中
- **[2026-09-07-tdm-backtest-protocol.md]** PIT 纪律五条（HMM filtered 禁 smoothed / 状态序列同版本一次生成冻结落盘 / 龙虎榜 T 日 18:00 后发布故只用 T-1 / 竞价基准按 T-1 收盘后时点建模 / DS-186 禁今日成分回填历史）+ fill model 三档（打板禁触价即成交，条件化成交概率 + 乐观/中性/悲观出区间；卖出端必含跌停封死不可成交状态机）
  - 出处=docs/_working/2026-09-07-tdm-backtest-protocol.md#§3+§4（L70-83） · 建议去向=docs/03_modules/_domain_backtest/blueprint.md §口径契约（或 34_d_backtest.md 对应章） · 理由=回测正确性判据，任何引擎/会话改口径都必须先对齐，属长期架构约束 · 真源已查=未命中
- **[2026-09-07-tdm-backtest-protocol.md]** 口径冻结项 6 条：双价格序列（涨跌停用不复权/因子用前复权）、成本口径分场景（CST-T0-001 保守档仅压力假设 vs CST-ASTOCK-001 实盘档）、分频合成与清算时刻、闲置资金 GC001 收益化（D88/D107）、conflict_priority 硬编码待 schema v1.8、红节点语义真源=69 号备忘录
  - 出处=docs/_working/2026-09-07-tdm-backtest-protocol.md#§8（L130-137） · 建议去向=docs/01_policies_and_standards/_registry/catalogs/ 相应口径册（cost_model/risk_limit）+ 34_d_backtest.md 口径章 · 理由=「冻结」即长期有效判据，且注册表侧只零散承接了个别值 · 真源已查=未命中
- **[2026-09-09-tdm-field-upgrade-discussion.md]** TDM 图上节点字段空间已饱和：两轮 10 角度扫描后，节点字段收敛于「锚定五联+语义三件+治理四件+本轮 tags/latency_budget」，其余业界字段（Model Card/交易日志/SLO 类）一律归库侧或台账侧，禁为加字段而加字段
  - 出处=docs/_working/2026-09-09-tdm-field-upgrade-discussion.md#§七（第二轮调研，饱和结论行） · 建议去向=docs/01_policies_and_standards/sop/trading_decision_map_sop/trading_decision_map_layering_policy.md §新增字段准入（或 catalogs/field_dictionary.yaml 头注判据段） · 理由=是长期字段准入判据（防后续会话重复提案/重复调研），不是一次性过程记录；现状真源无任何「字段饱和」口径可引用 · 真源已查=未命中
- **[2026-09-09-tdm-field-upgrade-discussion.md]** Owner 三条「不做」裁定及理由：owner 字段（单人+AI 军队追责无区分度）、risk_tier（任何节点坏了都不行=无区分度）、review_frequency（留给统一 AI 维护体系设计）
  - 出处=docs/_working/2026-09-09-tdm-field-upgrade-discussion.md#§五（已裁定表） · 建议去向=docs/01_policies_and_standards/_registry/catalogs/field_dictionary.yaml（否决留档段）或 docs/01_policies_and_standards/sop/trading_decision_map_sop/ 新增字段章节 · 理由=属长期负面判据（negative list），不登记则下一轮调研必然重提同一批字段 · 真源已查=未命中
- **[2026-09-10-commit-pipeline-perf-plan.md]** commit gate 二分法准入判据：内容扫描型 gate 必须 own-scope（只扫本会话 staged/claimed），结构校验型按扫描类型分级放行——L0 宪法 §3-3 现行条文的分级依据即本件 §2.6
  - 出处=docs/_working/2026-09-10-commit-pipeline-perf-plan.md#§2.6（106 gate 实测分级总表+分类口径） · 建议去向=docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml（增 scan_type/tier 字段承载分级）+ docs/01_policies_and_standards/rules/trae_080_panorama_alignment.yaml 同级 governance 规则册新增 gate 分级条 · 理由=是被宪法正文引用的长期准入判据（每新建一个 gate 都要用），非一次性过程记录；不进真源则宪法指针永久悬空 · 真源已查=未命中
- **[2026-09-10-commit-pipeline-perf-plan.md]** 提交通道三条根因与收益口径（全局提交锁等待参数化 60s 缺省、门禁全量重扫、checker 子进程 spawn 税），以及「第一约束=功能效果严格不变、只提速提效」的等价性审计口径（§2.7 十二行逐项）
  - 出处=docs/_working/2026-09-10-commit-pipeline-perf-plan.md#§0.2 + #§2.7 · 建议去向=docs/01_policies_and_standards/sop/governance_sop/ 提交通道性能条（或并入 parallel_session_coordination_policy.md §提交队列章节） · 理由=属长期治理口径（后续任何通道改造都要按「行为严格等价」举证），且宪法 §2 的队列/own-scope 条文化后缺一份可引用的判据细则 · 真源已查=未命中
- **[2026-09-11-g07-sentiment-validation.md]** G07 三态裁定=COMBINATION_INVALID（代理收益口径：分层后 ρ_max=0.768>0.6，全样本 0.667→CONSENSUS 层 0.768），TDM-E-L2-05 水温响应不满足转蓝条件（<0.6）维持红节点 pending_gate，复核路径=真实策略 PnL（三策略实盘/仿真 ≥6 月）到位后按 30 号 §6.2 原判据重验
  - 出处=docs/_working/2026-09-11-g07-sentiment-validation.md#§0 与 #§5 第 1 条 · 建议去向=docs/03_modules/_domain_signal/sentiment_cycle/blueprint.md §（把 :32「待 G07 相关性验证」改为已裁定口径）+ config/trading_decision_map.yaml TDM-E-L2-05 red_reason 注记 · 理由=是 TDM 红/蓝节点转档判据与模块 MATURITY 定性的依据；真源现仍停留在「待验证」，任何后续会话按真源读会重复做同一次验证 · 真源已查=未命中
- **[2026-09-11-g07-sentiment-validation.md]** 分层相关性结构结论：event-multifactor 是唯二稳定低相关对（全样本 0.391，各层 0.20-0.48）可并行；daban-multifactor 是主矛盾（CONSENSUS 层 0.768），且 ρ 随情绪温度单调上升（0.495→0.621→0.768）——趋同非阶段异质性假象而是策略信号在热门期真实趋同
  - 出处=docs/_working/2026-09-11-g07-sentiment-validation.md#§2 核心发现 1-4 · 建议去向=docs/03_modules/_domain_signal/sentiment_cycle/blueprint.md §组合语义 或 docs/02_enterprise_architecture/02_domain_architecture_docs/ 对应 d_trading/signal 文档 · 理由=属长期组合判据（决定哪些 sleeve 可并行扩张），不是一次性数据快照 · 真源已查=未命中
- **[2026-09-11-g07-sentiment-validation.md]** 处置建议：G13 FirmRiskAggregator 加情绪暴露硬上限（按 0.3-0.6 档保守处置，具体=CONSENSUS 阶段三 sleeve 合计暴露上限、EBING 阶段 daban sleeve 上限），且 30 号 §6.2 三级响应下 CONSENSUS 层（>0.7）已入「暂停部署」档——真实 PnL 复核前疯狂期多策略并行扩张冻结
  - 出处=docs/_working/2026-09-11-g07-sentiment-validation.md#§5 第 2、3 条 · 建议去向=docs/01_policies_and_standards/_registry/catalogs/risk_limit 类登记表 或 docs/03_modules/_domain_portfolio_core/... 蓝图风控段（具体册由总指挥裁） · 理由=是资金暴露侧长期约束判据（Owner 门位候选），留在 _working 则实际风控永不生效 · 真源已查=未命中
- **[2026-09-11-g07-sentiment-validation.md]** 方法论保留与工具缺口：本裁定仅在「裸信号多头组合次日收益」代理口径内成立（共同市场 beta 机械抬高全部 ρ，定性方向可信、绝对档位待实盘）；过程中实证定位器兜底分支会把 2024-09-30 evidence CONSENSUS 0.644 强制打成 FREEZING，建议给 locate_sentiment_phase 增「回放/打标模式」显式语义或 evidence argmax 输出字段
  - 出处=docs/_working/2026-09-11-g07-sentiment-validation.md#§0 关键保留 与 #§4 第 2 条 · 建议去向=docs/01_policies_and_standards/_registry/catalogs/validation_method_registry.yaml（sensor_monotonicity 条目 notes 加代理口径适用限制）+ docs/03_modules/_domain_signal/sentiment_cycle/blueprint.md §已知缺陷 · 理由=一条是验证口径的长期适用限制（防止后人把代理结论当真实组合结论），一条是可回测性缺陷登记，均为判据级 · 真源已查=未命中
- **[2026-09-12-data-layer-gap-analysis.md]** 数据分层三轴判据：内容轴（行情/基本面/另类/治理）×加工轴（ODS/DWD/DWS/ADS 阶段）×延迟轴（tick/日内/日频/月频）为并立三轴，本项目现有 L1/L2/L3 只覆盖内容轴
  - 出处=docs/_working/2026-09-12-data-layer-gap-analysis.md#§1.1 §1.2 §1.3 §1.4 对照结论 · 建议去向=docs/02_enterprise_architecture/02_domain_architecture_docs/10_d_data.md（数据域架构文档分层章）或 docs/03_modules/_domain_data 蓝图 · 理由=是后续所有新表/新品类归位的判据框架，一次性体检报告退役后无处可查即失判据；双 grep（docs/03_modules/*/blueprint.md 与 catalogs/+02_enterprise_architecture/）对「加工轴/内容轴/延迟轴」三词均零命中 · 真源已查=未命中
- **[2026-09-12-data-layer-gap-analysis.md]** 逐层体检口径与完成度基线：L1 行情≈95%（缺口全为取舍）、L2 扩展层数据≈70%/消费≈30%、L3 另类≈15%、数据治理轴≈90%（个人项目罕见级）
  - 出处=docs/_working/2026-09-12-data-layer-gap-analysis.md#§2 逐层体检（2.1-2.4） · 建议去向=docs/01_policies_and_standards/_registry/catalogs/data_asset_registry.yaml 头注（现状基线段）或 docs/02_enterprise_architecture/02_domain_architecture_docs/10_d_data.md · 理由=作为「缺不缺数据」的裁决基线被反复引用（本件即被 10_d_data.md:4894 与 alt-data 系列四份文档引为起点），属长期判据而非过程记录 · 真源已查=未命中
- **[2026-09-12-data-layer-gap-analysis.md]** P2-A 显性化义务：加工轴必须在 ROOR / 数据资产登记表头补一段 ODS/DWD/DWS/ADS 映射说明（不重构、纯登记，成本半天）
  - 出处=docs/_working/2026-09-12-data-layer-gap-analysis.md#§3 缺什么（P2-A 行） · 建议去向=docs/01_policies_and_standards/_registry/catalogs/data_asset_registry.yaml 头 + docs/registry_of_registries.yaml · 理由=该义务至今未执行（真源 grep ODS/DWD/DWS/ADS 零命中），是本件唯一尚未消化的可执行长期条款，不入库即随件退役而丢失 · 真源已查=未命中
- **[2026-09-13-knowledge-reserve-nonpipeline.md]** 微观结构序列复杂度候选：排列熵 / 递归量化分析（RQA）确定性作市场状态特征（kline 全窗口可算）——真源 grep 排列熵/递归量化/RQA 零命中
  - 出处=docs/_working/2026-09-13-knowledge-reserve-nonpipeline.md#板块三 市场微观结构研究 末条 · 建议去向=docs/01_policies_and_standards/_registry/catalogs/candidate_module_registry.yaml（signal_ashare 候选条目）或 docs/03_modules/_domain_signal 蓝图特征储备段 · 理由=同板块其余三项（订单不平衡/VPIN/数据在库因子未建）已按候选入册，唯独此项随文档悬空；不入库则该候选在退役后不可发现 · 真源已查=未命中
- **[2026-09-13-knowledge-reserve-nonpipeline.md]** 前沿分布预测模型雷达清单：神经 Lévy 跳扩散、条件生成模型（CVAE/扩散）、分位数回归森林、结合 GARCH 的无限隐马尔可夫（IHMM/HDP-HMM）、量子概率、分布评估双标准（PIT 校准度+sharpness/AlphaEval 免回测评测）、状态空间与参数化波动率族（GARCH/TGARCH/t/有偏 t/q-高斯）
  - 出处=docs/_working/2026-09-13-knowledge-reserve-nonpipeline.md#板块五 前沿模型观察 · 建议去向=docs/library/（业务资产库研究雷达表，经 python -m zephyr.library.lookup 检索）或 docs/03_modules/_domain_backtest 蓝图 车道E 演进段 · 理由=本件自述「研究雷达，不承诺落地」=长期观察清单性质，非一次性过程记录；真源 grep 神经 Lévy/CVAE/无限隐马尔可夫 零命中，若不内收则车道 E 后续深化缺对照清单 · 真源已查=未命中
- **[2026-09-13-knowledge-reserve-nonpipeline.md]** 跨资产与频域储备两项：汇率/商品期货→A 股传导（kline_global/hog_futures 在库、联动因子未建）、频域多尺度特征（5min/30min/日度波动率族，分钟线表已在库）
  - 出处=docs/_working/2026-09-13-knowledge-reserve-nonpipeline.md#板块六 另类数据与特征储备 · 建议去向=docs/01_policies_and_standards/_registry/catalogs/candidate_module_registry.yaml 或 factor_registry.yaml 族头储备段 · 理由=数据已在库、只差因子化的排队候选，属长期特征清单；真源 grep 频域多尺度 零命中 · 真源已查=未命中
- **[2026-09-14-full-chain-factory-blueprint.md]** 工厂裁决三问判据：设计空间大且可枚举且有客观评分→建工厂，否则建求解器/守卫；风控（环节 8）永不建工厂，红线不交给 AI 学习
  - 出处=docs/_working/2026-09-14-full-chain-factory-blueprint.md#二 · 建议去向=docs/01_policies_and_standards/policies/（新建或并入 factory 建设判据卷）或 docs/03_modules/_master_blueprint §判据章 · 理由=是「要不要建某个工厂」的可复用裁决规则，跨域长期有效，现只活在 _working 散文里 · 真源已查=未命中
- **[2026-09-14-full-chain-factory-blueprint.md]** 终局形态=五部件+一条回路（D 设计空间/C 编译器/E 评分咽喉/M 记忆/G 资源 Governor + F-09 回灌边），九个 F-xx 是 D 在不同环节的实例化，共用同一 E/M/G
  - 出处=docs/_working/2026-09-14-full-chain-factory-blueprint.md#八-8.1 · 建议去向=docs/02_enterprise_architecture/08_algorithm_overview/system_foundation.md §工厂终局形态（现该文件仅含 active_if/一次定型片段） · 理由=架构骨架判据，决定后续所有工厂件的归属与复用边界 · 真源已查=未命中
- **[2026-09-14-full-chain-factory-blueprint.md]** 三条设计铁律：①Schema 一次定型、执行分期 ②退化维度由编译器折叠不被人裁剪 ③「这期先不做」必须写成 active_if 谓词而非删维
  - 出处=docs/_working/2026-09-14-full-chain-factory-blueprint.md#八-8.2 · 建议去向=docs/01_policies_and_standards/sop/construction_sop/construction_workflow_policy.md §设计定型章 或 docs/01_policies_and_standards/rules/trae_<n>_*.yaml · 理由=属施工期恒定约束（Owner 已裁「接受为本文档顶层设计原则」），现仅在 _working 与本件派生的模块蓝图里，跨模块施工无检索入口 · 真源已查=未命中
- **[2026-09-14-full-chain-factory-blueprint.md]** F-01~F-09 工厂矩阵（现状/动作/优先级）+ 三层路线图 L1/L2/L3，含「F-09 回灌总线排 L2 末，无真实反馈数据先建闭环=自欺」「车道 B/D/E 缓立项」两条裁定
  - 出处=docs/_working/2026-09-14-full-chain-factory-blueprint.md#四、#六、#十一后裁定记录 · 建议去向=docs/03_modules/_domain_strategy_pipeline 或 _master_blueprint 的工厂路线图章（并登记 F-01~F-09 编号↔module_id 映射） · 理由=长期排期与「永不/暂缓」类判据，防止各会话重复立项或抢跑被裁定缓建的车道 · 真源已查=未命中
- **[2026-09-14-full-chain-factory-blueprint.md]** 实证家底结论：四工厂（Factor/Signal/Strategy/MlModel）import 仅出现在自身 __init__ 与 tests、无 orchestrator 引用=设计件非运行件；车道C 挖掘机挖完编排层不收（factory_intake_pipeline lane is None 直接 continue）
  - 出处=docs/_working/2026-09-14-full-chain-factory-blueprint.md#五-1、#五-2 · 建议去向=docs/03_modules/_domain_strategy_pipeline/blueprint.md §接线现状（或 architecture_issue_registry 登记为待办架构债） · 理由=是「断点在哪」的可核对判据，后续每次接线/回归都以此为准绳；现在只有本件叙述，代码变更后可核对性会丢 · 真源已查=未命中
- **[board_synthesis]** 通达信 880/881 板块指数合成定案口径=t-1 流通股本加权链式（派氏、日内除数恒定）；流通市值加权实证弃用（概念段 corr -0.62 负相关），等权仅作股本缺失降级路径
  - 出处=docs/_working/board_synthesis/2026-09-15-board-index-synthesis-plan.md#§1 + 2026-09-15-phase3-minute-calibration-report.md#§2 · 建议去向=docs/03_modules/_domain_data/blueprint.md（板块数据合成/口径节；消费侧交叉 _domain_signal 逆势榜 MOD-SIG-071 输入口径） · 理由=双真值日 580 板块实测定案的长期数据口径，后续所有板块合成与消费方必须遵循，属判据级结论而非一次性过程记录 · 真源已查=未命中
- **[board_synthesis]** 合成序列对拍验收矩阵：日收益 corr≥0.99、95 分位绝对差≤0.15pp、方向一致率≥97%、分钟 top-20 排序重合≥90%、3 月滚动差≤1pp；连续两轮全达标=合成器冻结转产，不达标项如实登记差距（不做假达标）
  - 出处=docs/_working/board_synthesis/2026-09-15-board-index-synthesis-plan.md#§4（冻结判定行） · 建议去向=docs/03_modules/_domain_data/blueprint.md（合成数据验收判据节） · 理由=可复用的合成数据质量门柱，适用于任何后续自建指数序列，非本战役一次性 · 真源已查=未命中
- **[board_synthesis]** 板块成分生命周期管理判据：成分每日快照表（SCD 视角）+ 调仓按除数修正保指数连续 + 新股按 industry_class 归类并入 / 退市 ST 剔除 / 股本变动由 t-1 权重吸收；启用前历史成分无源须以「当前成分回溯近似+误差实测登记」交底
  - 出处=docs/_working/board_synthesis/2026-09-15-board-index-synthesis-plan.md#§2 / #§2.1 · 建议去向=docs/03_modules/_domain_data/blueprint.md（成分数据基建节） · 理由=表已建成并持续供数（docs/library/data.md:193 active），但 as-of/调仓 diff/除数修正的架构判据只存在于 _working 方案里 · 真源已查=未命中
- **[full-auto-chain]** 端到端无人值守链 S01-S15 环节清单（每环节一句话职责+自动化态+本班处置），Owner 终局只做四类事=账号注册/API 申请/充值/转正审批，中间一切人工参与是要消灭的对象
  - 出处=docs/_working/full-auto-chain/00_skeleton_full_auto_chain.md#1 环节清单+引言北极星校准 · 建议去向=docs/03_modules/ 新建链路级蓝图（如 _cross_layer/full_auto_chain/blueprint.md）或 docs/02_enterprise_architecture 链路章 · 理由=跨域链路面貌与终局判据，是环节归口与后续缺件度量的基准，非一次性施工记录 · 真源已查=未命中
- **[full-auto-chain]** 最小下单桥三重护栏：只读 .env.qmt 的 QMT_SIM_* 两键（实盘密钥前缀键名（本册按 REAL-KEY-REFERENCE-SCAN 判据掩码，原文指该前缀一族） 禁出现在任何路径）+双终端在线辨机唯一权威=TCP 配对法（LISTEN 端口法禁用）+live 账号未配置且 blocks_live_trading=true；单笔 100 股远价当日必撤、idempotency_key 带日期前缀
  - 出处=docs/_working/full-auto-chain/S14_live_qmt_bridge/README.md#5（护栏清单）+#6 封矿结论 · 建议去向=docs/01_policies_and_standards/sop/（QMT 实弹 runbook 判据章）+ docs/03_modules/_domain_ex_core/* 蓝图安全不变量节 · 理由=资金破坏性操作的长期安全判据；实测两处方案更正（限价=跌停价而非×1.01、price_type LIMIT 0→11）只在此棚成文 · 真源已查=未命中
- **[full-auto-chain]** 转正后闭环前置判据：现建 live 监控回路属『在错误层位提前建将被覆盖的中间件』，监控对象不存在则不施工；衰减认证阈值与复活机制预注册（MOD-SIG-150）等转正链跑通后按路线图逐件闭环
  - 出处=docs/_working/full-auto-chain/S15_post_live_monitoring/README.md#6 封矿结论 · 建议去向=docs/01_policies_and_standards/sop/construction_sop/construction_workflow_policy.md（不过度工程判据条） · 理由=可复用的『何时不施工』判据，与一次性登记清单不同层 · 真源已查=未命中
- **[full-auto-chain]** S14→S15 之间的流转执行器与订单翻译件（目标权重→订单清单）为链上唯一未接板（挂起项登记，非晋升判据），解锁条件 C6✅+C5✅ 已满足；挂起理由与依赖写在环节文档而非任何注册表
  - 出处=docs/_working/full-auto-chain/S14_live_qmt_bridge/README.md#7 堵点 4 · 建议去向=docs/01_policies_and_standards/_registry/catalogs/backtest_backlog.yaml 或 task card 册（交总指挥裁，本代理不改册） · 理由=避免晋升蓝图时把待办当结论丢失：该条是欠账不是判据，列此供分诊 · 真源已查=未命中
- **[live_readiness]** 实盘准入门禁清单 G1-G12：挂实盘旗须逐门机械可证全绿（密钥轮换闭环/整装回测四阈值/策略包毕业/模拟盘 N 交易日/熔断链实弹/blocks_live_trading 接线/交易级告警专条…），且 promote_ready≠决定，全绿仍须 Owner 签发、禁 AI 自动升档
  - 出处=docs/_working/live_readiness/admission_gate_design.md#§1 门清单（G1–G12）+§4 反面清单 · 建议去向=docs/01_policies_and_standards/sop/ 新增实盘准入 SOP（或 docs/03_modules/_domain_ex_core/pre_execution_checker/blueprint.md 门位章） · 理由=可复用的资金破坏性门位判据，非本班一次性记录；现行仅存在于 _working · 真源已查=未命中
- **[live_readiness]** 六面准入判据（风控/仓位/监控/告警/密钥/合规 25 项，每项判据+现状+四态图例：绿达标/黄有条件/红补齐前禁挂旗/白须 Owner 外部确认）
  - 出处=docs/_working/live_readiness/live_admission_checklist.md#面1-面6 · 建议去向=docs/01_policies_and_standards/sop/（与上一条同批）+ config/qmt_environments.yaml 注记交叉引用 · 理由=判据级检查表，后续任何准入评估班须复用同一口径 · 真源已查=未命中
- **[live_readiness]** 异常处置 E1-E8 分级纪律：五级熔断各自动作与冷却（含 API_TIMEOUT/SECOND_LEVEL 自恢复、DAILY_LOSS 86400s 不自动恢复）、双终端在线辨机唯一权威=TCP 配对法（LISTEN 端口法禁用）、保命三动作、当班速查卡
  - 出处=docs/_working/live_readiness/exception_handling_manual.md#E1-E8+附 速查卡 · 建议去向=docs/01_policies_and_standards/sop/（运行期异常处置册）或 config/qmt_environments.yaml 引用的 runbook 件 · 理由=全部对照代码实测行为写出的运行判据，与宪法 §9 运维红线同层 · 真源已查=未命中
- **[live_readiness]** pilot 档 SOP 骨架：B-007 五档阶梯 shadow→paper→pilot→daily_review→auto、风险预算倒推仓位、六段预算带×60% 硬顶、Owner 八个干预点 H1-H8、未接电依赖如实声明
  - 出处=docs/_working/live_readiness/small_capital_live_sop_draft.md#§1 适用范围+§8 未接电依赖 · 建议去向=docs/02_enterprise_architecture/04_architecture_principles_decisions/system_charter.md §档位（现仅存档位定义，无 pilot 档 SOP） · 理由=档位流转的长期操作制度；但生效前置=件4 全绿+Owner 逐项 confirmed，晋升须 Owner 门位先行 · 真源已查=未命中
- **[resource_schedule]** 资源排班「一库一器一闸一图」四件套架构与 18 字段双证纪律（每字段必须有生产者+消费者双证才入表；measured 双轨=表内最新快照 CAS+样本流 append-only 不建 DB 表；三套压力阈值口径不收编）
  - 出处=docs/_working/resource_schedule/resource_schedule_panorama_plan_v1.md#2.1-2.4（含 §2.1 关键裁决①-④） · 建议去向=docs/03_modules/_domain_infrastructure_runtime/blueprint.md §资源排班（或该域新设 MOD-RESCHED 蓝图，台账自述 docs/03_modules/** 待建） · 理由=字段口径与真源分层是后续任何排班/画像改动的判据，一次性战役报告无法被后继施工引用；缺蓝图=每次改表都要回读 _working 方案件。 · 真源已查=未命中
- **[resource_schedule]** 排班冲突闸四查判据与实测边界：判据①共开工声明豁免/判据②内存预算永不豁免、expand_windows 单表达式 64 触发上限（盘中级 cron 28 天只展开首 ~1 周，第 2-4 周同刻堆积不在扫描范围）、判据①唯一豁免口=归因失败（非 git 通道写表 pileup=False 只跑判据②）
  - 出处=docs/_working/resource_schedule/resource_schedule_v2_acceptance_evidence.md#3（§7 红蓝对抗·登记口径风险 1/2） · 建议去向=docs/03_modules/_domain_infrastructure_runtime/blueprint.md §排班冲突闸 判据节（量化边界另可登记 docs/01_policies_and_standards/rules/ 同域规则册） · 理由=三条都是闸的已知失真面（漏判区间），属长期判据；不写进真源=后续用闸结论时会把「0 block」当全量真值。 · 真源已查=未命中
- **[resource_schedule]** 实测校准 HOLD 口径：常驻/watchdog 类实体的 measured.p90_duration_min 语义≠单次执行寿命（sch_worktree_drift_watchdog 申报 1min vs 实测 464.9min），5 项 HOLD 项走周复报提醒环而非改申报值
  - 出处=docs/_working/resource_schedule/p3_global_replan_report.md#2 与 resource_schedule_v2_acceptance_evidence.md#4（校正批 HOLD 5）、morning_report/latest.md#3 校准表 · 建议去向=docs/03_modules/_domain_infrastructure_runtime/blueprint.md §采样器/校准器 口径节 · 理由=采样口径决定之后所有申报值裁定，属长期判据；现只在晨报（会被覆盖）与战役报告（临时区）里。 · 真源已查=未命中
- **[tdm20_campaign]** TDM 层语义二分判据：chainpile 七层（L0 元问题…L6 治理）≠TDM 漏斗层（L0 预案…L4 执行），知识供给轴落位 entry_flow+layer=L9，禁与漏斗层混用；L9 前缀满足 R1（entry→L*）
  - 出处=docs/_working/tdm20_campaign/00_tdm20_ledger.md#§2 D-1 · 建议去向=docs/03_modules/_domain_governance/blueprint.md §TDM 层语义（或 _system_master/blueprint.md 的 TDM 章） · 理由=任何后续往图上挂供给节点的批次都要用这条命名/落位判据，否则会把供给层节点错插进决策漏斗；目前只有代码常量 + 临时台账。 · 真源已查=未命中
- **[tdm20_campaign]** 边语义四元组判据与欠账可探测口径：触及 L9 的边 payload_type/frequency/lag/pit_proof 全必填且走封闭词表（error 级），存量 194 旧边机械回填 pit_proof=legacy-unaudited（欠账显式化不糊弄）；lag 语义=数据时点相对消费时点（T-1）
  - 出处=docs/_working/tdm20_campaign/00_tdm20_ledger.md#§2 D-4（含 D-2 不改 schema_version 前提） · 建议去向=docs/03_modules/_domain_governance/blueprint.md §TDM 边契约 + docs/01_policies_and_standards/rules/ 地图对齐同域规则册（机读判据） · 理由=这是地图 schema 演进的长期判据，写在 ttl: task_bound 台账里下个批次读不到就会重开辩论。 · 真源已查=未命中
- **[tdm20_campaign]** 判定/结算分离铁律：禁向判定台账写入非实跑产出的行（把 proposed 冒充实跑=造假），交付只给「节点↔判定表↔档位」契约对照+缺口读数（该有而没有=接线缺口，报而不造）
  - 出处=docs/_working/tdm20_campaign/00_tdm20_ledger.md#§2 D-6（05_morning_report.md#五 重申守约） · 建议去向=docs/01_policies_and_standards/sop/governance_sop/construction_ledger_method_policy.md §台账只记三件事/回执六项 · 理由=跨车道通用的台账写入门槛（不止 TDM），现政策册只讲回执六项与「永不说全绿」，未含「判定面禁写非实跑行」这条。 · 真源已查=未命中
- **[tdm20_campaign]** AGG 生产切换三判据与可逆形态：①夜批连续≥5 交易日零缺勤+当日更新（机械复核）②并行期无解析/供给事故③Owner 签字；一键切回=data/runtime/anchored_cap.disabled（零代码零重启、下一分配日生效）、陈旧>7 日历日 applied=False 不盲用、策略路由阈值未冻结不接线；回滚窗至 2026-10-23 后走退役复审
  - 出处=docs/_working/tdm20_campaign/06_agg_switch_rollback_plan.md#§1-§4 与 00_tdm20_ledger.md#§3b · 建议去向=docs/03_modules/_domain_risk/blueprint.md（regime/熔断消费节）+ docs/03_modules/_domain_portfolio_core/blueprint.md §组合层 cap 裁剪 · 理由=production 翻转类结论必须有蓝图级判据与回滚义务（10-23 复审），否则回滚窗一过预案就随 _working 归档失联。 · 真源已查=未命中
- **[trading_vision]** 日度编排器= T2 晨判唯一拍板体：读齐（日历/regime/各层门/包选择）→合成拍板（总仓位上限+no_trade 三源合成）→落库分发，不新增判断逻辑；『今日不交易=禁新开仓≠清仓』，保命件横切独立于编排器
  - 出处=docs/_working/trading_vision/2026-09-16-daily-orchestrator-blueprint.md#一、架构定位（1-5 条）+二、每日流程 S1-S5 · 建议去向=docs/03_modules/_domain_strategy_pipeline/daily_decision_orchestrator/blueprint.md（新建，模块已在盘无蓝图） · 理由=已实现模块的架构定位与安全语义，是长期判据；该模块被日循环消费但 docs/03_modules 全域无蓝图承载 · 真源已查=未命中
- **[trading_vision]** 判定台账标准四铁律：判定时刻写死 PIT 锚／outcome 只由结算器事后回填（判定模块禁写结算列）／表只增不改、修订=新 judgment_id 追加／准确率统计须可由 judgment_id 联结独立复算
  - 出处=docs/_working/trading_vision/2026-09-16-judgment-ledger-standard.md#一、核心铁律 · 建议去向=docs/01_policies_and_standards/sop/backtest_system_sop/（判定台账族制度条）+ docs/03_modules/_domain_plan_engine/blueprint.md 判据章 · 理由=全仓『每个产出判定的模块必接台账』的制度化判据，非一次性过程记录 · 真源已查=未命中
- **[trading_vision]** Owner 愿景机构化翻译基线：L1-L5 五层决策级联+三处可编码亮点（信噪比择时/regime-dependent allocation/TD 序列金字塔仓位）+主观转量化三课（信号化/风险预算倒推仓位/逐层归因）
  - 出处=docs/_working/trading_vision/2026-09-16-owner-vision-system-mapping.md#一、决策级联+二、机构三差异 · 建议去向=docs/02_enterprise_architecture/04_architecture_principles_decisions/system_charter.md §档位与策略包章 · 理由=Owner 交易方法论唯一对照真源，下游 SOP/检查表（live_readiness 件2）已按行号反向引用，属长期架构输入 · 真源已查=未命中
- **[trading_vision]** 缺口三分法归口：采集缺口→上游采集线／历史缺口→登记（backtest_backlog）／结构缺口→蓝图+立项；五层数据够用性矩阵按『考试需要』定料防为填库而下载
  - 出处=docs/_working/trading_vision/2026-09-16-data-sufficiency-matrix.md#三类缺口分派归口 · 建议去向=docs/01_policies_and_standards/_registry/catalogs/known_data_gaps.yaml 判据头 + sop/data_ops_sop/data_source_onboarding_sop.md · 理由=可复用的缺口分类处置判据，与一次性盘点数字不同层 · 真源已查=未命中

（②态条目合计 51 条）

## 5. ③未施工 — 《未施工清单》（带真源指针 + owner 线索）

- **[2026-08-28-d-disk-cleanup-plan.md]** models/qwen25-7b-base（14.2GB）+ qwen25-7b-sft-v1 迁 E 盘（全仓 grep 已证零代码引用，embedding 模型在 data/models/local_model/ 禁动）
  - 真源=docs/_working/2026-08-28-d-disk-cleanup-plan.md#执行步骤 §1（L42-50） · owner 线索=Owner（文首「用户确认三项都做，但不是现在」=Owner 择期窗口）
- **[2026-08-28-d-disk-cleanup-plan.md]** 删或迁 .git.backup.20260803（6.3GB），前置=git fsck --full 通过 + 建议先迁 E 盘观察 1-2 周
  - 真源=docs/_working/2026-08-28-d-disk-cleanup-plan.md#执行步骤 §2（L52-64） · owner 线索=Owner
- **[2026-08-28-d-disk-cleanup-plan.md]** 选择性清 tmp 旧备份/日志轮转（禁删 *.heartbeat/*.lock/scheduler_run.log）+ echo-guard 索引迁盘后再清（否则 rescan 重建仍占 D 盘）
  - 真源=docs/_working/2026-08-28-d-disk-cleanup-plan.md#执行步骤 §3（L66-77） · owner 线索=Owner（先查 echo-guard 是否支持索引路径配置，属运维动作非代码项）
- **[2026-08-30-b4-six-factor-construction-breakdown.md]** S1 因子值产出接线：disclosure_plan.actual_date + 法定截止日规则 → compute_dreport → 因子表；Jump on PEAD 事件日+5 日窗取 OHLC 算 AR
  - 真源=docs/_working/2026-08-30-b4-six-factor-construction-breakdown.md#§3 表 S1（L51）；实证缺口：grep compute_dreport|jump_on_pead src/**/*.py 仅命中 src/zephyr/intelligence/event_factor_matrix.py 本体（零装配消费者） · owner 线索=none（派单账无署名；前置裁定见 2026-08-30-b16-feed-exploration.md §2.3 两条待裁）
- **[2026-08-30-b4-six-factor-construction-breakdown.md]** S2 z-score 截面归一 + event_impact_score 按 26 号 §2.5 公式融合（w1-w4 + PEAD_inversion_gate 门控），注入 BM-SEL-19 漏斗且不双真源
  - 真源=docs/_working/2026-08-30-b4-six-factor-construction-breakdown.md#§3 表 S2（L52） · owner 线索=none
- **[2026-08-30-b4-six-factor-construction-breakdown.md]** S3 event_funnel.py 过滤层接 event_impact_score，event_driven_sleeve_strategy 经漏斗消费（当前仅 TYPE_CHECKING 声明）
  - 真源=docs/_working/2026-08-30-b4-six-factor-construction-breakdown.md#§3 表 S3（L53） · owner 线索=none
- **[2026-08-30-b4-six-factor-construction-breakdown.md]** S4 G23 回测校准：Jump 3% 阈值/隔夜 20 日窗/dReport 分档映射 A 股实证，终值回写 26 号 §2.4（禁「跑通即定值」）
  - 真源=docs/_working/2026-08-30-b4-six-factor-construction-breakdown.md#§3 表 S4（L54）+ #§3 纪律行 L56 · owner 线索=none
- **[2026-08-30-b4-six-factor-construction-breakdown.md]** §4 风险项 2：六因子与打板相关性 G07 实测为既有前置（26 号 §6 待定问题），>0.6 需重审 sleeve 组合
  - 真源=docs/_working/2026-08-30-b4-six-factor-construction-breakdown.md#§4-2（L61） · owner 线索=none
- **[2026-08-30-b7-batch-bc-doc-supplement-checklist.md]** 11 张事件流表（convertible_bond_iv/calendar_event/share_change/rights_issue/equity_pledge_detail/concept_board/concept_board_constituent 等）从附录「未消费登记」3-5 字段行升级为 63 号 §7.0.1 六字段正文小节
  - 真源=docs/_working/2026-08-30-b7-batch-bc-doc-supplement-checklist.md#§3.1（L65-79）；实证未完成：docs/_working/archive/2026-09/design_memos/26_event_driven_strategy_detail.md:667-673 仍是「附录：数据资产消费登记…当前状态统一为未消费登记」 · owner 线索=none（63 号 §7.2 第二波「未来工程-小型」裁定，纯文档施工 1-2 天分 3 小批）
- **[2026-08-30-b7-batch-bc-doc-supplement-checklist.md]** 4 张板块轮动表（sector_meta/index_constituent + sector_list/concept_sector 前置件）六字段升级，被依赖表 sector_list 须先补最小文档
  - 真源=docs/_working/2026-08-30-b7-batch-bc-doc-supplement-checklist.md#§3.2（L83-90） · owner 线索=none
- **[2026-08-30-b7-batch-bc-doc-supplement-checklist.md]** 4 张因子原料表（industry_class_suppl/analyst_forecast/stock_indicator + stock_valuation 待 Q8）六字段升级，并标注与 16 号技术指标的派生/原生边界
  - 真源=docs/_working/2026-08-30-b7-batch-bc-doc-supplement-checklist.md#§3.3（L92-99） · owner 线索=none
- **[2026-08-30-b7-batch-bc-doc-supplement-checklist.md]** ARCH-300（open）：concept_sector/sector_list/convertible_bond_list 三表任务已配置但 0 行——须排查月度任务执行链并实证灌数，否则三表 L3 语义抽检不达标
  - 真源=docs/_working/2026-08-30-b7-batch-bc-doc-supplement-checklist.md#§4 前置条件-1（L105）+ #§2 表 L52-54 · owner 线索=none（登记为架构议题，数据域施工）
- **[2026-08-30-b7-batch-bc-doc-supplement-checklist.md]** Q8 五张 dormant 表（index_adjustment/ipo_schedule/margin_target_adjustment/stock_valuation/msci_adjustment）dormant vs 补采集待人决策（63 号 §10.2 跟踪中，不重复登记）
  - 真源=docs/_working/2026-08-30-b7-batch-bc-doc-supplement-checklist.md#§4 前置条件-2（L106） · owner 线索=Owner（63 号 §10.2 Q8 人决策项）
- **[2026-09-01-stockq-component-split-inventory-v2.md]** 右栏剩余 6 件未建：sq-company-intro / sq-financial-read / sq-related-news / sq-fair-value / sq-limit-up-gene / sq-data-source-badge（清单 §二 18/21/22/23/24/25）
  - 真源=docs/_working/2026-09-01-stockq-component-split-inventory-v2.md#§二 右栏资料面板表（L87-97）；实证=ls src/zephyr/frontend/dashboard/web/features/stockq/ 无同名文件 · owner 线索=none（清单 §八-4 建议首个测试件=sq-stock-header，该件已建）
- **[2026-09-01-stockq-component-split-inventory-v2.md]** K 线区剩余件未建：sq-kline-main/sq-kline-volume/sq-kline-macd/sq-kline-kdj/sq-draw-tools/sq-marks-bs/sq-marks-trade/sq-marks-chip/sq-cost-line/sq-timeline/sq-chip-peak
  - 真源=docs/_working/2026-09-01-stockq-component-split-inventory-v2.md#§二 中栏 K 线区域表（L63-75）+ #筹码峰独立区域（L81） · owner 线索=后继战役账见 docs/_working/archive/2026-09/2026-09-12-frontend-split-inventory.md（app1.js 主拆批，自述待办已闭环）+ docs/01_policies_and_standards/sop/frontend_component_split_sop.md
- **[2026-09-01-stockq-component-split-inventory-v2.md]** 6 个纯 UI 件（w-price-tag/w-pct-badge/w-data-table/w-mini-chart/w-icon-toggle/w-status-light）与 8 个数据服务件（svc-market/svc-stock-info/svc-events/svc-chip/svc-fav/svc-position/svc-news/svc-quant）零落地
  - 真源=docs/_working/2026-09-01-stockq-component-split-inventory-v2.md#§三（L105-113）+ #§四（L118-127）；实证=web/widgets 目录不存在件、web/services 仅 api.js · owner 线索=none
- **[2026-09-01-stockq-component-split-inventory-v2.md]** §八 待 Owner 裁定 5 条（26+6+8 命名是否采用/右栏 11 拆是否够细/manifest 14 字段是否够用/首个测试件选择/app1.js ≤500 行骨架只留事件分发是否接受）无裁定回填
  - 真源=docs/_working/2026-09-01-stockq-component-split-inventory-v2.md#§八（L211-218） · owner 线索=Owner（原文明示「待 Owner 裁定」）
- **[2026-09-08-qmt-bridge-migration-ledger.md]** §1 未确认三项：下单链路 QmtFileBridgeBroker（HTTP 18901+orders_sim.csv 兜底）、执行取价 QmtFileBridgeQuoteProvider（quote.csv 尾读+新鲜度闸门）、交易通道监控 fetchBridgeStatus + 健康面板组件 components/qmt_bridge_health.py
  - 真源=docs/_working/2026-09-08-qmt-bridge-migration-ledger.md#§1（L37-41，复选框未勾） · owner 线索=none（施工台账无派单署名；健康面板另有蓝图 docs/03_modules/_domain_frontend/blueprint_qmt_bridge_health.md）
- **[2026-09-08-qmt-bridge-migration-ledger.md]** §2.2-A 分钟K线族 17 任务：档 2 逐表裁定未做（方案 b 合成已落码 bae99e9362，但 9/18 后 akshare 5 日对拍观察项未启动、a 方案触发条件未评估）
  - 真源=docs/_working/2026-09-08-qmt-bridge-migration-ledger.md#§2.2-A（L71-92）+ #§8.3.1 裁定③（L215「后续动作仅剩 9/18 后按触发条件启动 akshare 5 日对拍观察」） · owner 线索=Owner 已批裁定③（d0aa441149 追认），对拍窗口触发方=9/18 后数据域施工会话
- **[2026-09-08-qmt-bridge-migration-ledger.md]** §2.2-B L2/期权族 5 任务续命：桥扩期权 universe（TICKDUMP v21 草稿已备料未激活）+ auction 族 tasks.yaml source 裁定
  - 真源=docs/_working/2026-09-08-qmt-bridge-migration-ledger.md#§2.2-B（L94-104）+ #§8.6 任务五（L276，明示未激活） · owner 线索=Owner（§8.6 任务五红线 3：沙箱策略激活留 Owner 9/18 后终端操作）
- **[2026-09-08-qmt-bridge-migration-ledger.md]** §2.2-C 财报族 4 任务 + §2.2-D 其他在产 3 任务 + §2.3 档 3 周边 6 任务（港/美/期货/转债）逐表评估未做；§2.1 档 1 有 fallback 的 26 个「已评估并裁定」勾选为零
  - 真源=docs/_working/2026-09-08-qmt-bridge-migration-ledger.md#§2.1/§2.2-C/§2.2-D/§2.3（L50-67, L106-123） · owner 线索=none
- **[2026-09-08-qmt-bridge-migration-ledger.md]** §3 P0-2 钱路（paper_session/intraday_main 下单链切 BrokerInterface 注入）与 §3 P0-3 对账（recon_runner/broker_settlement_adapter 切桥）未施工；§3 market_breadth_collector 8 处 miniqmt 直连改桥聚合未施工（依赖 §2.2-D 裁定）
  - 真源=docs/_working/2026-09-08-qmt-bridge-migration-ledger.md#§3（L143, L150-151） · owner 线索=none
- **[2026-09-08-qmt-bridge-migration-ledger.md]** §4-F1 前端 trade_panel 默认 broker_id 由 miniqmt 切 qmt_bridge（实测 src/zephyr/frontend/dashboard/components/trade_panel.py:92 仍为 miniqmt）
  - 真源=docs/_working/2026-09-08-qmt-bridge-migration-ledger.md#§4（L155） · owner 线索=Owner 窗口（原文标注「9/17 收盘后窗口——红线 2」，窗口已过未回写）
- **[2026-09-08-qmt-bridge-migration-ledger.md]** §5 退役日 SOP 全部 6 步与 §6 验证标准 5 条未逐项勾选闭环（其中 §6 第 1 条经本代理实测判定未达成）
  - 真源=docs/_working/2026-09-08-qmt-bridge-migration-ledger.md#§5（L163-170）+ #§6（L172-178） · owner 线索=none
- **[2026-09-08-qmt-bridge-migration-ledger.md]** §8.4 三条独立小问题：TTLRejudgeDaily 计划任务每日 18:05 退出码 1 闪红 / QUOTE_V17 并入 TICKDUMP3 的 9/15 开评（v20 方案）/ convertible_bond_list 10/1 正档观察
  - 真源=docs/_working/2026-09-08-qmt-bridge-migration-ledger.md#§8.4（L221-223） · owner 线索=none
- **[2026-09-08-qmt-bridge-migration-ledger.md]** §8.7 待查项（未勾）：intraday_minute 槽位 9:00-9:30 盘前空转拉「当日」bar 的 provider 层空跑防护（原文建议 9/17 窗口一并评估）
  - 真源=docs/_working/2026-09-08-qmt-bridge-migration-ledger.md#§8.7 待查项（L335） · owner 线索=none
- **[2026-09-12-alt-data-construction-plan.md]** 第 2 批（注册类）：雪球三件 follow/tweet/deal + 百度指数接入（BAIDU_INDEX_TOKEN 每日刷新 + concept_factor_mapper 唤醒）+ 互动易 irm_qa + 上海/浙江开放平台获批后接入
  - 真源=docs/_working/2026-09-12-alt-data-construction-plan.md#§4 批次规划（第 2 批行）；§2.1/§2.2 施工图 · owner 线索=st-altdata-20260912 系列（handoff §8-2 接手人=新对话），密钥已在 .env/secret_registry
- **[2026-09-12-alt-data-construction-plan.md]** 第 3 批（爬虫试点）：政府采购网中标公告——唤醒 web_scraper_engine + alt_data_compliance_reviewer；textdata.cn 历史问答集可选买断
  - 真源=docs/_working/2026-09-12-alt-data-construction-plan.md#§4 批次规划（第 3 批行）；缺口侧登记 src/zephyr/data/config/known_data_gaps.yaml:650 · owner 线索=none
- **[2026-09-12-alt-data-construction-plan.md]** 第 4 批（海外源）：GDELT 15 分钟事件流、SEC EDGAR EFTS 全文、IMF WEO/IFS 精选序列落 macro_data 共表（indicator_name 前缀 IMF_，复用 FRED 模式）、Alpha Vantage/EODHD 免费层美股深度补缺
  - 真源=docs/_working/2026-09-12-alt-data-construction-plan.md#§3.5 国际宏观 + §4 批次规划（第 4 批行） · owner 线索=none
- **[2026-09-12-alt-data-construction-plan.md]** 每批治理闭环义务：alt_data_catalog 登记 → compliance_reviewer → alt_source_health_manager 探针 → known_data_gaps.yaml（机制件已在盘，随各批执行）
  - 真源=docs/_working/2026-09-12-alt-data-construction-plan.md#§5 治理闭环；接线器 src/zephyr/alt_data/alt_source_bootstrap.py · owner 线索=none
- **[2026-09-12-alt-data-handoff.md]** §8-2 第 2 批注册类接入：百度指数（token+每日刷新+concept_factor_mapper 唤醒）、雪球、互动易 irm_qa、SH/SZ 开放平台获批源
  - 真源=docs/_working/2026-09-12-alt-data-handoff.md#§8 第 2 条 · owner 线索=st-altdata-20260912 交接对象（新对话）
- **[2026-09-12-alt-data-handoff.md]** §8-3 第 3 批爬虫试点：政府采购网中标公告（唤醒 web_scraper_engine+compliance_reviewer）；textdata.cn 历史问答集（可选买断）
  - 真源=docs/_working/2026-09-12-alt-data-handoff.md#§8 第 3 条 · owner 线索=none
- **[2026-09-12-alt-data-handoff.md]** §8-4 第 4 批海外源：GDELT 日频拉取、SEC EFTS、IMF SDMX 2.1 精选序列落 macro_data、Alpha Vantage/EODHD 免费层美股深度补缺
  - 真源=docs/_working/2026-09-12-alt-data-handoff.md#§8 第 4 条 · owner 线索=none
- **[2026-09-12-work-roadmap.md]** 泳道1-1.3 stock_indicator 个股估值历史回补（D4 裁定，5000 股×1200 日 PE/PB/PS，解锁估值因子族与 C3 估值类翻译）
  - 真源=docs/_working/2026-09-12-work-roadmap.md#§1 泳道 1（1.3 行）；裁定真源 ruling_registry.yaml:1621 裁定#228 D4 · owner 线索=Owner（本件明写 Owner 点头即跑）；数据工程会话
- **[2026-09-12-work-roadmap.md]** 泳道1-1.1 三大报表中报全科目 ~4,500 只缺口回补 + 1.4 死重清理批（三表 1970 垃圾行 ~9,600 + 双写哨兵 27.5K + disclosure_plan 11%，带备份 DELETE 走 RULE-DATA-OPS）
  - 真源=docs/_working/2026-09-12-work-roadmap.md#§1 泳道 1（1.1/1.4 行） · owner 线索=none（miniQMT 9/18 窗口已过期，需重估路径）
- **[2026-09-12-work-roadmap.md]** 泳道1-1.5 云盘同步器 7/3 停更重启决定（不重启则登记 known_data_gaps）
  - 真源=docs/_working/2026-09-12-work-roadmap.md#§1 泳道 1（1.5 行）；相关现状 src/zephyr/data/config/known_data_gaps.yaml:439（bdpan 云盘取证记录） · owner 线索=Owner（本件明写 Owner 一句话）
- **[2026-09-12-work-roadmap.md]** 泳道4 币圈影子 MVP（等 Owner 域名 + Cloudflare 账号，四站被墙唯一解）
  - 真源=docs/_working/2026-09-12-work-roadmap.md#§1 泳道 4 表末行；同口径欠账见 docs/_working/2026-09-11-tdm-morning-review-report.md 币圈 D 类 · owner 线索=Owner
- **[2026-09-12-work-roadmap.md]** 泳道5 schemas/categories 129>120 FOLDER-CAPACITY 超限拆分手术（Owner 级裁定）与币圈残留件/module_translation 残件清偿
  - 真源=docs/_working/2026-09-12-work-roadmap.md#§1 泳道 5 表 · owner 线索=Owner（本件标 Owner 级裁定）
- **[2026-09-13-dedup-analysis.md]** B 组 4 组合并前置批：先统一变量名/docstring 措辞（纯格式批）使 diff 归零，再并入 analysis_utils
  - 真源=docs/_working/2026-09-13-dedup-analysis.md#§二 第 3 条（B 组前置） · owner 线索=night-sweep-20260913 交下一班（§三 明写下一班按 §2 执行，预计 1-2 小时）
- **[2026-09-13-dedup-analysis.md]** plan_engine 域 _safe_float 提取至 plan_engine 域共享处；_table 跨域（plan_engine↔signal）落 zephyr/shared/ 层或保留双副本登记
  - 真源=docs/_working/2026-09-13-dedup-analysis.md#§二 第 1 条 · owner 线索=none
- **[2026-09-13-dedup-analysis.md]** 实例方法接口变更单独小批：_resolve_table/_resolve_query_fn 改模块级 resolve_table(registry) 并改 3 处调用约定
  - 真源=docs/_working/2026-09-13-dedup-analysis.md#§二 第 2 条 · owner 线索=none
- **[2026-09-13-dedup-analysis.md]** C 组 2 组禁盲合并：如需收敛，先写行为对照测试锁定两套语义再裁去留（similar_day_evaluator._parse_eval_date↔market_breadth_history_store._resolve_end_date；fine_scoring_engine.compute_density_penalty↔selection_funnel_skeleton.density_penalty_from_summary）
  - 真源=docs/_working/2026-09-13-dedup-analysis.md#§一 C 组 + §二 第 4 条 · owner 线索=none
- **[alt_data_consumption_plan.md]** F1-F3 千股千评因子（关注度异动 zscore/机构参与度动量/排名跃迁事件流）——启动条件为积累达标（文内定 10 月中），未见立卡或封矿回执
  - 真源=docs/_working/alt_data_consumption_plan.md §1.A（F1/F2/F3 段）+ §7.3 C-3 行 · owner 线索=alt-data 消费线（前序交接 2026-09-12-alt-data-handoff.md）；本域总台账=docs/_working/2026-09-14-typhoon-bdi-factor-mining-plan.md
- **[alt_data_consumption_plan.md]** F23 涨停板情绪周期的因子位定稿（六阶段状态机阈值 provisional 待 OOS 毕业），F15 恐贪反弹窗自动化信号侧
  - 真源=docs/_working/alt_data_consumption_plan.md §6.1 F23、§1.F F15 · owner 线索=情绪/因子线（后续 emomine、bizmine 会话在跑，未见本卡销案）
- **[alt_data_consumption_plan.md]** F18-F20 互动易卡（H 族文内标「第 2 批，未接」）与 F27 政策文本→板块映射卡（R12 来源闸未过挂起，Batch3 解挂列 2d）
  - 真源=docs/_working/alt_data_consumption_plan.md §1.H、§6.1 政策文本卡、§7.1 F27 · owner 线索=none
- **[alt_data_consumption_plan.md]** F24 期权 PCR/基差与 F26 ETF 份额反转的因子构造本体（数据侧已由 83ddfdf4f5/5b6ee808a6 部分补齐，卡未落）
  - 真源=docs/_working/alt_data_consumption_plan.md §6.1 F24、§7.1 F26、§7.3 C-5 行 · owner 线索=oddjobs 线已回补 PCR 标的层（5b6ee808a6），因子构造待派
- **[alt_data_consumption_plan.md]** 长尾矿脉未挖项在册：CICSI 消费者信心补源、日耗煤字段核验、龙虎榜席位多源验证、GDELT/IMF 消费卡、台风灾损权重矩阵
  - 真源=docs/_working/alt_data_consumption_plan.md §5.5 下批长尾、§6.3 Batch3 长尾 · owner 线索=none
- **[altdata_line]** 90 收敛终局清单填充：对各域挖矿队列按四格（可得性/信号浓度/系统契合度/维护成本）逐条打分定 P0/P1/观察池
  - 真源=docs/_working/altdata_line/90_convergence_todo.md#当前预判（待终局修正）→「（终局清单待填）」行 + 文档头注「状态：占位」 · owner 线索=数据线统筹（文档自述触发=数据线聊完后整理，无署名）
- **[altdata_line]** 08 路线图 P0 收尾细项：结构层三达标由 1.5/3 补齐（P0-1..P0-5 细项含 R1 精确化/R3 补年挂接/R5 IO 系数回填/3,171 无映射反哺/桥 52 条人工终检）
  - 真源=docs/_working/altdata_line/08_full_chain_roadmap.md#P0 收尾细项表（P0-1..P0-5 行）；现状口径见 07_industry_chain_repair_workorder.md:74「结构层达标状态：…有水量（⏳ R5 待 IO 表下载）」 · owner 线索=产业链修复线（REPAIR-WO-001 承接方，07 工单原班）
- **[altdata_line]** 08 路线图 P1-P8 全段未发车（底座补全/油价五波 MVP/传导链引擎/研报放量/公告因子/【快】清单/人物线/运营稳态）
  - 真源=docs/_working/altdata_line/08_full_chain_roadmap.md#阶段表 P1-P8 行（头注「状态：P0 执行中」） · owner 线索=none（按「每环节先挖矿→出施工文档→施工」节奏派单）
- **[altdata_line]** 01 骨架【快】快赢清单 ~20 叶逐个落地复核（现仅部分叶位带夜班落地锚，余为 ⬜/💰）
  - 真源=docs/_working/altdata_line/01_data_type_skeleton.md:8 标记图例 + A/B/C/D/E/F 各表【快】行（如 C13/E10/E12/F7/F10） · owner 线索=数据线挖矿队列（经 09 子分包机制派单）
- **[bizmine_chain_mining]** B2 逐环节深挖：16 环节各建作业簿（六向台账+自审闸三态+环节裁定），产物 a2_gap_register.md 缺口总账与 stages/<环节号>_<名>/c0..c9 全套
  - 真源=docs/_working/bizmine_chain_mining/skeleton/b0_stage_skeleton.md#批次志（B2 待回填）+ a0_master_plan.md#3 产物目录结构 · owner 线索=st-bizmine2-20260919（9cf3a2739a 判死）→ 总包接手方
- **[bizmine_chain_mining]** B3 外部方法学源回填：机构 alpha 流水线阶段划分/开源先例（qlib·RD-Agent·alphalens·gplearn·Nautilus·Optuna）边界/过拟合防御框架落位，各带 URL+发布方+年份
  - 真源=docs/_working/bizmine_chain_mining/skeleton/b1_source_diff_matrix.md#5 S5 外部方法学源（占位） · owner 线索=none
- **[bizmine_chain_mining]** B4 三重扫描收口（按生产者/按形态资产类/按消费者文献）+ 增量曲线拉平 + 🌑 清点，方可写 a4_sealing_verdict 封矿声明与 a5 交付报告
  - 真源=docs/_working/bizmine_chain_mining/skeleton/b0_stage_skeleton.md#§3 三重扫描计划 + b1_source_diff_matrix.md#4 批次志 · owner 线索=none
- **[bizmine_chain_mining]** 封矿后按方案 §0 第④步进入施工（P0 清单+新挖缺口逐环节接电），当前零施工记录
  - 真源=docs/_working/bizmine_chain_mining/a0_master_plan.md#0 前线分析（结论行） · owner 线索=总包（a0 frontmatter status: 施工中）
- **[cold_backup_automation]** §10 批 4『身份证』：business_data_categories.yaml lifecycle 仍 209 permanent/2 hot_90d/1 hot_1d，未对齐契约十层（结案报告实测反证）
  - 真源=docs/_working/cold_backup_automation/cold_backup_closure_report.md#§二 批 4 行 · owner 线索=乙线 st-disk-ch-20260921 / 续班 st-diskreorg-close-20260922
- **[cold_backup_automation]** §10 批 5 后半程：滚动归档 reconciler 三步走 shadow→半自动→全自动未走完（执行件在盘，进度报告标 UNCERTAIN）
  - 真源=docs/_working/cold_backup_automation/cold_backup_closure_report.md#§二 批 5 行 + contracts/data_retention_contract.yaml:83 · owner 线索=乙线（同上）
- **[cold_backup_automation]** §10 批 3 欠账 24.9G 清账 / 批 7 vhdx 季度压缩机制化停机窗 / 批 8 restore 演练自动化与 90_tmp 对账：报告均标 UNCERTAIN 未见落地证据
  - 真源=docs/_working/cold_backup_automation/00_master_plan.md#§10 执行批次（:267-279 摘要） · owner 线索=乙线；批 8 压缩窗含 Owner 到场点（a4_go_signal.md:23）
- **[cold_backup_automation]** 知识固化第 ④ 步：capability 册冷库/备份关键词登记+ROOR 挂接+permanent 手册提炼（保留清除清单 17 行挂 MOD-INF-043）+日历删除三笔（09-28/10-05/10-18/10-21）
  - 真源=docs/_working/disk_reorg_campaign/a6_remaining_work_order.md#§2 A-D（本棚为其母方案） · owner 线索=st-backup-cold-20260924（当前在飞续班）
- **[construction_backlog.md]** B3 audit_fn 接真源：DailyAuditor.audit 持仓/净值/限额真源接线（现空快照）+ SettlementReconciler.reconcile 注入 post_settlement 管线，文内标注「待 QMT 在线窗口施工（无实证不施工纪律）」
  - 真源=docs/_working/construction_backlog.md §B3 两行未勾项 · owner 线索=2026-09-15 夜班裁定（同 5ebe47d4c0 的 B3 裁定登记）；运维红线归 Owner 在线窗口
- **[construction_backlog.md]** B4 LiveStrategyAdapter 真信号源施工：模拟盘信号源从空转接真策略信号 + start_paper_session.py 交易日 09:25 前拉起（当前手动形态）
  - 真源=docs/_working/construction_backlog.md §B4 两行未勾项 · owner 线索=模拟盘战役（后续 fb5a7821d7/28b85901bf 已推进 sim_daily_runner 与 plan 桥，归属需总指挥对账）
- **[construction_backlog.md]** B6 首次回测=模拟盘对账跑通：同信号同窗口逐日 diff + 偏差归因登记（滑点/部分成交/拒单）
  - 真源=docs/_working/construction_backlog.md §B6 · owner 线索=none
- **[construction_backlog.md]** B1 次项：日循环 SOP 开盘前确认 QMT 在线由看门狗日志承担，行内未勾
  - 真源=docs/_working/construction_backlog.md §B1 第二行 · owner 线索=运维侧（scripts/qmt_watchdog.ps1 已落地）
- **[construction_backlog.md]** C1 测试债专项批：56 存量红逐条归因清零 + 785 failed/17 errors 分包清偿（文内已自标旧数字仅历史参照，以 .runtime/construction_backlog.md 模块单测总账为准）
  - 真源=docs/_working/construction_backlog.md §C1 · owner 线索=测试健康度线（后续 dataqa/测试审计批 d2d2e0eb6a 覆盖体检面）
- **[construction_backlog.md]** C2 P0-2 残余三件：FLE gates 启用评估（#61 CAND 另案）、trend_analyzer 库处置、Dashboard 死数据「数据截至」提示
  - 真源=docs/_working/construction_backlog.md §C2 三行未勾项 · owner 线索=none
- **[daily_loop_campaign]** 把 W1 官方词表常量模块（src/zephyr/shared/vocab/）与 W2 收编册（state_vocabulary_registry.yaml，含 tests/gov_enforcement/test_state_vocab_registry_gate.py）从工作区未跟踪态落成提交——当前执法门在 HEAD、被执法词表在盘外，属半落地
  - 真源=docs/_working/daily_loop_campaign/03_self_ruling_vocab_ssot.md#三、施工方案 W1/W2（git status 实测 ??） · owner 线索=st-dloop-20260921（会话未在 session_registry 在册，dloop 批余件在 09-22 接手批被明示『排除：dloop 在飞批余件待其自落地』）
- **[daily_loop_campaign]** 缺口④路由表 config 落地：六段↔五态映射定稿+TDM-E-L1 三空格（ignition/euphoria/distribution）填格+60% 硬顶与过渡带系数定稿
  - 真源=docs/_working/daily_loop_campaign/owner_gate_list.md#C 项 + routing_table_v1_draft.md §1 · owner 线索=Owner（R41 词表资金分配门位）
- **[daily_loop_campaign]** 策略卡 1（300ETF 波段+底仓 T）/卡 2（regime 切换器）立卡→S-OWNER 考试链毕业→喂 GRADUATED_PACKAGES，编排器解除『今日不出手』安全态的唯一合法路径
  - 真源=docs/_working/daily_loop_campaign/owner_gate_list.md#D 项 · owner 线索=Owner 批 + 考试链
- **[daily_loop_campaign]** 三份接线提案未施工：L2 板块放行门／cohort 与 T4／recon runner 通道（wiring_proposals_*.md 工单形态，HEAD 侧无对应实装改动）
  - 真源=docs/_working/daily_loop_campaign/wiring_proposals_L2_sector_gate.md 等三件 · owner 线索=none
- **[daily_loop_campaign]** 模拟盘部署批（E 项）与 pending_events.jsonl 两条 09-16 c4_batch_due 滞留消费端核查（H 项移交）
  - 真源=docs/_working/daily_loop_campaign/owner_gate_list.md#E/H 项 · owner 线索=C4/任务卡线（H 项明示非丁线写域）
- **[datavein]** 运维急件：重启采集链+重跑 kline_etf_{1,5,15,30,60}min_incremental 五任务，补齐 09-16 半根与 09-17 全链 0 行
  - 真源=docs/_working/datavein/2026-09-17-etf60min-depth-workorder.md#§六-1（L77）+ §一-3（L16） · owner 线索=数据采集线（工单接收方，移交方 st-datavein-20260917）
- **[datavein]** 通道 C 代码件：ch_tick_kline/合成路径 ETF 参数化+回补 CLI（零覆盖格过滤、dry-run 默认、BufferedWriter 正道、--execute 后缺格清零复验）
  - 真源=docs/_working/datavein/2026-09-17-etf60min-depth-workorder.md#§三 移交建议（L57）+ §六-2（L78）；HEAD 侧核验=known_data_gaps.yaml:884 status 仍 monitoring · owner 线索=数据采集线（持通道/代码权限）；在飞线索=scripts/data/backfill_etf60min_depth.py（未跟踪，2026-09-23，头注署名 st-datatail-20260923 夜窗卡）
- **[datavein]** 残余格子（2021-02-08 159915 孤立散格等合成源不覆盖点）走通道 D 大QMT 沙箱逐日下载
  - 真源=docs/_working/datavein/2026-09-17-etf60min-depth-workorder.md#§六-3（L79）+ §二 缺口表 · owner 线索=数据采集线
- **[datavein]** known_data_gaps.yaml kline_etf_60min_depth_windows 条目回写 resolution_actual（工单 front-matter completes_when 第④条=结案必要条件）
  - 真源=docs/_working/datavein/2026-09-17-etf60min-depth-workorder.md#front-matter completes_when（L3）；现值 src/zephyr/data/config/known_data_gaps.yaml:875-888（status: monitoring） · owner 线索=数据采集线
- **[datavein]** 附带时效项（工单如实登记、非移交义务）：tick_depth_5 距做T 精确回测还差 ~17 个全市场交易日；通道 D 服务器 ~1 个月保留窗内 08-18~09-10 五档回补机会每日报废
  - 真源=docs/_working/datavein/2026-09-17-etf60min-depth-workorder.md#§四（L66） · owner 线索=数据线（时效敏感）
- **[fullflow_campaign]** B1 幂等键命门修复（资金级）：begin_signal_batch 真调+trade_date 改取信号携带交易日；本次实测 src/zephyr 全域仍零调用者（仅 order_manager.py:236 定义）⇒ 未落地
  - 真源=docs/_working/fullflow_campaign/delivery/MAX_EXECUTE_LIST.md#B1 · owner 线索=Max 复审班（交付报告 §七 交接口径）
- **[fullflow_campaign]** B2 slippage_bps 真写 NULL：本次实测 execution_report_producer.py:415-416 仍为 f"{float(value):.6f}" ⇒ 未落地，前置=签字 A1 契约批准
  - 真源=docs/_working/fullflow_campaign/delivery/MAX_EXECUTE_LIST.md#B2 · owner 线索=Max（A1 卡 Owner 契约批准）
- **[fullflow_campaign]** A00/A00b/A14/A16/A17/A18 等 22 项 Owner/Max 裁定：含既成事实定性、熔断跨进程可达性方案、接线率权威口径三选一
  - 真源=docs/_working/fullflow_campaign/delivery/MAX_ADJUDICATE_LIST.md#A00/A00b/A14 · owner 线索=Owner（A00 系 Owner 门位）/ Max
- **[fullflow_campaign]** B21 严格 HEAD 口径两轮复跑 + B22/B23 写侧只增不减与 index 净删即拦两治本 + skeleton/04_sixway 机读台账重生成（现自述 392KB 已知失真未重生成，CH 超时把『测不到』判红 B16）
  - 真源=docs/_working/fullflow_campaign/COORDINATION_LEDGER.md#R-073/R-074（尾段）与 delivery/FINAL_DELIVERY_REPORT.md#六 末两条 · owner 线索=none（战役总包已交班）
- **[fullflow_campaign]** 57 条仍成立断点中『钱/结论会脏』的 B13/B14（两处失败不响+告警最后一米入口去重过度）未执行
  - 真源=docs/_working/fullflow_campaign/delivery/FINAL_DELIVERY_REPORT.md#六 待执行段 · owner 线索=Max
- **[industry_chain_alpha]** 施工批2（事件+车道升级）：A6 链上硬事件响应窗 → A7 关联半径衰减标定 → A8 供给冲击方向分离 → E4 挂载 → C2 LLM 硬事件抽取量产 → A13 三高数据源升级 → B4 尾部 blast radius 持仓预警
  - 真源=docs/_working/industry_chain_alpha/industry_chain_alpha_mining_ledger.md#§5 施工批次表（批2 行，L193） · owner 线索=st-igalpha-20260917 裁决书批次派单（总账 §5「均待 Owner 放行或按既有自治授权滚动」）
- **[industry_chain_alpha]** 施工批3（组队服务）：B1 链感知聚类（赶 A2 组队窗口）→ B2 同链暴露上限 → A9 客户集中度财报意外 → A11 IO 行业轮动先验/A12 商品价格→板块 regime → 裁3 交接件（暴露矩阵+字段字典）给 F2
  - 真源=docs/_working/industry_chain_alpha/industry_chain_alpha_mining_ledger.md#§5（批3 行，L194）+ #§0 裁3 · owner 线索=同上；A12 归 C-1 regime 线（本线供矩阵）
- **[industry_chain_alpha]** 施工批4（AI 原生+基建）：C1 链查询 Agent/MCP 三工具 → D1 图谱版本化快照（解锁条件=快照 ≥2 vintage）→ A14 链核心度画像 → B3 传染压力测试 → C4 策略生成注入链上下文
  - 真源=docs/_working/industry_chain_alpha/industry_chain_alpha_mining_ledger.md#§5（批4 行，L195）+ 裁2（L18） · owner 线索=同上（D1 备注「可提前：变更批自动快照成本极低」）
- **[industry_chain_alpha]** 四线挖矿 workbook 未挖干：a 簿 §2 六向台账多格「待挖」且自述「挖矿未完成，施工冻结」，A-4/A-5 未动；b/c/d 簿同构，按挖后自审闸（SOP §6）各线裁定完毕前不得扩施工
  - 真源=docs/_working/industry_chain_alpha/a_batch1_construction/a_mining_workbook.md#§2 六向状态台账 + #§5 判据行（L48-49）+ §6「A-4/A-5：未动」 · owner 线索=各线挖矿会话（a 簿建账日 2026-09-17 Owner 五轮令；通宵班署名 st-igchain-20260918）

（③态条目合计 84 条）

## 6. Owner 点名面 design_memos

- 归档侧 `docs/_working/archive/2026-09/design_memos/` 已有 49 件；现场 `16_technical_indicator_catalog.md`、`README.md`。
- README 原文：「本目录施工文档已于 2026-09-20 依裁定#384 逐件三裁归置：49 件归档至 `docs/_working/archive/2026-09/design_memos/`（git 历史保留），去向明细见归置台账 `docs/_working/code_doc_gov_campaign/p3_placement/w14_placement_ledger.md`。仅 `16_technical_indicator_catalog.md` 依特判留置原位（tilib 指标库活真源，待数据线批 10 完工后再裁）。」→ **该面已依裁定#384 逐件三裁归置完毕**，非本轮欠账；`16_` 系明文特判留置。
- `16_technical_indicator_catalog.md`：行数=314 · HEAD 末次=2026-09-22（275493de9b） · 脏=1 · mtime=24.0min · 归档同名件=无 → **④在飞**
- `README.md`：行数=13 · HEAD 末次=2026-09-22（5123c7e9b7） · 脏=0 · mtime=887.3min · 归档同名件=无 → **候判**

## 7. 归档/去重执行记录（含阻断实测）

- **执行状态：未执行**，原因=实测阻断（下表）：①态且无归档 twin 的 11 个 unit，**全部**存在 `_working` 之外的入站引用（含热册 `capability_canonical_file_registry.yaml`、`ruling_registry.yaml`、`known_data_gaps.yaml`、`.gitignore` 乃至 `scripts/*.py`、`tests/*.py`）→ `git mv` 必同批改这些锚点，而热册此刻由执行者在途持有（本包 D13 现场），按铁律「热件被他包/他手占用→跳过登记」不擅动。

| 待归档 unit | 类 | 件数 | 外部入站引用数 | 内部引用数 | 引用者样本 |
|---|---|---|---|---|---|
| `2026-09-18-gate-identity-root-fix-plan.md` | file | 1 | 1 | 3 | `docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml` |
| `2026-09-18-rule-audit-master-construction-plan.md` | file | 1 | 2 | 1 | `docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml`、`scripts/governance/d8_doc_sync/auto_sync_all_registries.py` |
| `2026-09-19-overnight-handover-max-shift.md` | file | 1 | 1 | 1 | `docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml` |
| `2026-09-19-overnight-scope-lock-report.md` | file | 1 | 2 | 1 | `docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml`、`docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml` |
| `code_doc_gov_campaign` | dir | 13 | 3 | 9 | `docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml`、`docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/README.md`、`docs/02_enterprise_architecture/09_ai_architecture/implementation_plans/README.md` |
| `data_fix_campaign` | dir | 11 | 3 | 10 | `docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml`、`scripts/audit_technical_indicator_columns.py`、`src/zephyr/data/config/known_data_gaps.yaml` |
| `flash_speedup` | dir | 22 | 3 | 15 | `docs/01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml`、`docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml`、`tests/governance/audit/test_arch_diagram_wave_concurrency.py` |
| `guides` | dir | 2 | 1 | 6 | `docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml` |
| `oddjobs_night` | dir | 3 | 1 | 0 | `docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml` |
| `unified_campaign` | dir | 17 | 2 | 11 | `docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml`、`docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml` |
| `同花顺资料` | dir | 2 | 12 | 2 | `.gitignore`、`docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml`、`docs/01_policies_and_standards/_registry/catalogs/data_asset_registry.yaml` |

- **等值双活 108 件**（归档侧已存在且逐字节相同，上一轮 cp 而非 mv 所致）：处置只能是「删 live 重复份」= 净删，属新设分叉且 R2 原文只授权 `git mv` → 已列《裁定请求 R2-b》候裁，**未擅删**。
- 双活总计：等值 108 件 / 不等值 10 件。
- 底座风险登记：原底座目录 `.runtime/tmp/align_dirty/r2/` 于 05:00 被执行者 §3.7-④「清大件」步骤连带删除（shard_05/06 两代理独立见证），已迁 `.runtime/tmp/working_cleanup_r2/` 重建；此即 §2-D13「临时面缺属主围栏」又一实例。

## 8. 待问总指挥（分片 ask 项）

（无）

## 8b. 同 unit 被两片判到（取先回收者，差异留此备查）
- `guides`：state=[1, 1]
- `trading_vision`：state=[2, 2]
- `bizmine_chain_mining`：state=[3, 3]
- `cold_backup_automation`：state=[3, 3]
- `fullflow_campaign`：state=[3, 3]
- `live_readiness`：state=[2, 2]
- `daily_loop_campaign`：state=[3, 3]
- `unified_campaign`：state=[1, 1]
- `full-auto-chain`：state=[2, 2]
- `2026-09-18_vocab_consolidation_campaign`：state=[1, 1]
- `code_doc_gov_campaign`：state=[1, 1]
- `resource_schedule`：state=[2, 2]
- `data_fix_campaign`：state=[1, 1]
- `oddjobs_night`：state=[1, 1]
- `tdm20_campaign`：state=[2, 2]
- `flash_speedup`：state=[1, 1]
- `2026-08-22-frontend-backend-gap-ledger.md`：state=[1, 1]
- `2026-08-24-aiarch-construction-list.md`：state=[1, 1]
- `2026-08-24-designmemos-construction-list.md`：state=[1, 1]
- `2026-08-25-page-by-page-review.md`：state=[2, 2]
- `2026-08-28-d-disk-cleanup-plan.md`：state=[3, 3]
- `2026-08-28-remaining-construction-roadmap.md`：state=[1, 1]
- `2026-08-30-b16-feed-exploration.md`：state=[1, 1]
- `2026-08-30-b4-six-factor-construction-breakdown.md`：state=[3, 3]
- `2026-08-30-b7-batch-bc-doc-supplement-checklist.md`：state=[3, 3]
- `2026-08-31-frontend-gap-views-derived.md`：state=[4, 4]
- `2026-08-31-frontend-governance-four-piece-drafts.md`：state=[1, 1]
- `2026-09-01-stockq-component-split-inventory-v2.md`：state=[3, 3]
- `2026-09-04-trading-decision-map-discussion.md`：state=[1, 1]
- `2026-09-05-audit-greatwall-report.md`：state=[1, 1]
- `2026-09-05-steward-b-class-owner-book.md`：state=[1, 1]
- `2026-09-06-flash-execution-report.md`：state=[1, 1]
- `2026-09-07-tdm-backtest-protocol.md`：state=[2, 2]
- `2026-09-07-tdm-internal-factpack.md`：state=[1, 1]
- `2026-09-07-tdm-pre-backtest-review-checklist.md`：state=[1, 1]
- `2026-09-07-tdm-review-round-report.md`：state=[1, 1]
- `2026-09-08-qmt-bridge-migration-ledger.md`：state=[3, 3]
- `2026-09-09-clearance-night-report.md`：state=[1, 1]
- `2026-09-09-greatwall-quality-task-brief.md`：state=[1, 1]
- `2026-09-09-news-industry-wiring-directive.md`：state=[1, 1]
- `2026-09-09-node-backtest-governance.md`：state=[1, 1]
- `2026-09-09-node-template-draft.md`：state=[1, 1]
- `2026-09-09-tdm-field-upgrade-discussion.md`：state=[2, 2]
- `2026-09-09-tdm-growth-blueprint.md`：state=[1, 1]
- `2026-09-09-tdm-missing-modules-construction.md`：state=[1, 1]
- `2026-09-09-tdm-night-greatwall-directive.md`：state=[1, 1]
- `2026-09-10-chainmap-frontend-batch-plan.md`：state=[1, 1]
- `2026-09-10-commit-pipeline-perf-plan.md`：state=[2, 2]
- `2026-09-10-legacy-clear-night-report.md`：state=[1, 1]
- `2026-09-10-nodebt-night-report.md`：state=[1, 1]
- `2026-09-10-xflow-batch-report.md`：state=[1, 1]
- `2026-09-10-xflow-followup-design.md`：state=[1, 1]
- `2026-09-11-backtest-evidence-log-discussion.md`：state=[1, 1]
- `2026-09-11-backtest-system-sop-discussion.md`：state=[1, 1]
- `2026-09-11-chainmap-final-batch-report.md`：state=[1, 1]
- `2026-09-11-commit-queue-dead-zero-closure.md`：state=[1, 1]
- `2026-09-11-crypto-shadow-mvp.md`：state=[1, 1]
- `2026-09-11-g07-sentiment-validation.md`：state=[2, 2]
- `2026-09-11-l308-aggregator-construction.md`：state=[1, 1]
- `2026-09-11-news-chain-wiring-spec-cards.md`：state=[1, 1]
- `2026-09-11-tdm-morning-review-report.md`：state=[1, 1]
- `2026-09-12-alt-data-batch1-construction-report.md`：state=[1, 1]
- `2026-09-12-alt-data-construction-plan.md`：state=[3, 3]
- `2026-09-12-alt-data-handoff.md`：state=[3, 3]
- `2026-09-12-data-layer-gap-analysis.md`：state=[2, 2]
- `2026-09-12-expectation-consumption-design.md`：state=[1, 1]
- `2026-09-12-fundamental-consumption-design.md`：state=[1, 1]
- `2026-09-12-handoff-c3-zcode.md`：state=[1, 1]
- `2026-09-12-igfact-ckg2021-data-asset-analysis.md`：state=[1, 1]
- `2026-09-12-research-report-data-plan.md`：state=[1, 1]
- `2026-09-12-research-report-handoff.md`：state=[1, 1]
- `2026-09-12-work-roadmap.md`：state=[3, 3]
- `2026-09-13-c5-cluster-differentiation-report.md`：state=[1, 1]
- `2026-09-13-dedup-analysis.md`：state=[3, 3]
- `2026-09-13-factory-gate-review.md`：state=[1, 1]
- `2026-09-13-io-structure-anchor-plan.md`：state=[1, 1]
- `2026-09-13-knowledge-reserve-nonpipeline.md`：state=[2, 2]
- `2026-09-13-p002-semantic-review.md`：state=[1, 1]
- `2026-09-13-panic-rebound-sim-paper.md`：state=[1, 1]
- `2026-09-13-strategy-factory-pipeline-discussion.md`：state=[1, 1]
- `2026-09-13-tdm-upgrade-blueprint.md`：state=[1, 1]
- `2026-09-13-xtreme-redblue-retest.md`：state=[1, 1]
- `2026-09-13-xtreme-redblue-v3-log.md`：state=[1, 1]
- `2026-09-13-xtreme-redblue-v3-plan.md`：state=[1, 1]
- `2026-09-13-xtreme-redblue-v3-report.md`：state=[1, 1]
- `2026-09-14-agg-switch-design.md`：state=[1, 1]
- `2026-09-14-auto-mount-research.md`：state=[1, 1]
- `2026-09-14-c4-history-repair-plan.md`：state=[1, 1]
- `2026-09-14-ch-connection-handoff.md`：state=[1, 1]
- `2026-09-14-chart-pattern-mining-report.md`：state=[1, 1]
- `2026-09-14-combination-layer-exhaustive-charter.md`：state=[1, 1]
- `2026-09-14-dsr-enable-impact-assessment.md`：state=[1, 1]
- `2026-09-14-fac-e1c-formula-mining-design.md`：state=[1, 1]
- `2026-09-14-full-chain-factory-blueprint.md`：state=[2, 2]
- `2026-09-14-handoff-market-data-repair.md`：state=[1, 1]
- `2026-09-14-indicator-mining-batch4.md`：state=[1, 1]
- `2026-09-14-lane-c-agentic-mining-charter.md`：state=[1, 1]
- `2026-09-14-market-data-gap-report.md`：state=[1, 1]
- `2026-09-14-p0-syntax-gate.md`：state=[1, 1]
- `2026-09-14-p002-reprint-result.md`：state=[1, 1]
- `2026-09-14-pattern-consumer-plan.md`：state=[1, 1]
- `2026-09-14-sim-partition-discussion.md`：state=[1, 1]
- `2026-09-14-supply483-verification-report.md`：state=[1, 1]
- `2026-09-14-tdm-consumption-sop-draft.md`：state=[1, 1]
- `2026-09-14-tilib-batch6-plan.md`：state=[1, 1]
- `2026-09-14-tilib-batch7-wiring-plan.md`：state=[1, 1]
- `2026-09-14-typhoon-bdi-factor-mining-plan.md`：state=[1, 1]
- `2026-09-14-xtreme-redblue-v4-report.md`：state=[1, 1]
- `2026-09-15-c4-acceptance-interim.md`：state=[1, 1]
- `2026-09-15-c5-cluster-refresh.md`：state=[1, 1]
- `2026-09-15-four-big-items-blueprint.md`：state=[1, 1]
- `2026-09-15-full-automation-night-plan.md`：state=[1, 1]
- `2026-09-15-governance-module-mining-sop-map.md`：state=[1, 1]
- `2026-09-15-gutters-eoc3-verification-deadend.md`：state=[1, 1]
- `2026-09-15-handoff-factory-docs-discussion.md`：state=[1, 1]
- `2026-09-15-neff-estimator-preregistration.md`：state=[1, 1]
- `2026-09-15-szopen-pipeline-handoff.md`：state=[1, 1]
- `2026-09-15-tilib-handoff.md`：state=[1, 1]
- `2026-09-18-gate-identity-root-fix-plan.md`：state=[1, 1]
- `2026-09-18-rule-audit-master-construction-plan.md`：state=[1, 1]
- `2026-09-19-overnight-handover-max-shift.md`：state=[1, 1]
- `2026-09-19-overnight-scope-lock-report.md`：state=[1, 1]
- `alt_data_consumption_plan.md`：state=[3, 3]
- `auction_bridge_switch_mining_2026_09_17.md`：state=[1, 1]
- `construction_backlog.md`：state=[3, 3]
- `index.md`：state=[1, 1]

## 8c. 安全附带发现（RULE-SECRETS·本任务分片揪出）

- **已实证 1 件（须 Owner 处置）**：`docs/_working/2026-09-12-alt-data-handoff.md` §2「Owner 已申请到的 API 与密钥状态」表（第 51-56 行）逐行列 **Alpha Vantage / EODHD / 百度指数 Access-Token / 北京市开放平台 key / Tushare** 等真实凭证值（本文件只记位置与指纹，不复述任何值）。同内容另有 **第二份** = `docs/_working/archive/2026-09/c_class_scattered/2026-09-12-alt-data-handoff.md`（上一轮 cp 归档把敏感件也复制了一份），且两份**均已在 git 历史**里。该文件自身第 59/117 行还写着「值只进 `.env`、密钥真源=…」= 与在册纪律相悖。
- **宽口径普查（尺子未定标，只作线索不作结论）**：`docs/_working` 全 2344 个 tracked 件扫凭证形状 → 命中 1243 处 / 45 文件；抽样定性显示**绝大多数为 `creation_token` 治理标识符**（如 `*-20260910` 日期后缀 slug）与红蓝测试用假值（含 `FAKE` 字样），故本报告不采用该计数作为违规数。命中文件清单（按命中行数排序，供人核）：
  - `docs/_working/registry_incident_20260922/c2_dead_letter_triage_shard2/w1_registry_missing_candidates_shard2.json`：1070 处
  - `docs/_working/registry_incident_20260922/c1_escape_forensics/evidence/missing_entries_verdict.json`：116 处
  - `docs/_working/registry_incident_20260922/c1_escape_forensics/evidence/commit_diffs.json`：5 处
  - `docs/_working/registry_incident_20260922/c1_escape_forensics/evidence/commits_window.json`：5 处
  - `docs/_working/2026-09-11-tdm-morning-review-report.md`：2 处
  - `docs/_working/2026-09-12-alt-data-handoff.md`：2 处
  - `docs/_working/align_dirty/working_cleanup_r2.md`：2 处
  - `docs/_working/archive/2026-09/c_class_scattered/2026-09-11-tdm-morning-review-report.md`：2 处
  - `docs/_working/archive/2026-09/c_class_scattered/2026-09-12-alt-data-handoff.md`：2 处
  - `docs/_working/oddjobs_final/LEDGER.md`：2 处
  - `docs/_working/2026-09-10-chainmap-frontend-batch-plan.md`：1 处
  - `docs/_working/2026-09-10-commit-pipeline-perf-plan.md`：1 处
  - ……其余 33 件见 `.runtime/tmp/working_cleanup_r2/secrets_scan_r2.json`。
- **门禁盲区（候批）**：SECRETS 三道 gate 显未覆盖 `docs/_working/**.md` 的表格式明文凭证（否则本件早被拦）；建议随 D2/D3 一并裁：把 md 表格内 `| provider | \`<token>\` |` 形状纳入既有 gate 的 own-scope 扫描。

## 9. 复核命令

```bash
export PATH="$LOCALAPPDATA/Programs/Python/Python312:$LOCALAPPDATA/Programs/Python/Python312/Scripts:$PATH"
cd /d/ZephyrAlpha
python .runtime/tmp/working_cleanup_r2/r2_base.py        # 168 unit 三查+双活+围栏+分片切法
python .runtime/tmp/working_cleanup_r2/scan_extras_r2.py # 凭证形状普查(带正/反例控制)+①态归档入站引用阻断表
python .runtime/tmp/working_cleanup_r2/assemble_r2.py    # 本文件
```
