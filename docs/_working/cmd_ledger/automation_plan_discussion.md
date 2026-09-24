---
ttl: task_bound
completes_when: 方案定稿转正式桥册后本册转讨论存档
title: 双引擎自动化编制讨论记录（夜班9席+白天岗位制+切碎指令机制）
owner: Owner
session: st-autoplan-20260924
date: 2026-09-24
---

# 自动化编制讨论记录（随讨论滚动更新，一任务一对话）

> 性质：讨论期临时记录册。定稿后内容转正式调度桥册（automation_master_plan.md 重写），本册转存档。
> 引擎：Qoder=千问3.8 Flash 24h 免费（**2026-09-30 截止**）；ZCode=GLM-5.3 Flash 每晚 23:00-09:00（**2026-10-08 截止**）。
> 总原则（Owner 原话口径）：全干苦力——工作量大、不需要人盯、明确肯定要干的活；不做无事生非；GLM 夜班裁定+干活双职、按饱和排量。

## 一、Owner 决策流水（已拍板）

| # | 决策 |
|---|---|
| D1 | GLM 夜班不只裁定，必须干活，工作量饱和 |
| D2 | ZCode 开 9 席自动 + 1 席留 Owner 手机插单（原 8 席扩为 9 席，2026-09-24 深审讨论后） |
| D3 | 挖矿（策略/因子/数据源）交白天千问挖（量大苦力），夜班 GLM 审查裁定 |
| D4 | GPU 从编制移除：Owner 自己单独开对话负责施工 |
| D5 | 付费白天总指挥删除；总指挥（如设）只在夜里 GLM 免费窗 |
| D6 | AI 层 245 件"队列畅通"广播权=夜班总指挥核验后自放（队列清空+件数核对两条件） |
| D7 | Qoder 白天写席 ≤5，其余全只读（依据：队列 pending56/dead318+现场热册拉锯目击） |
| D8 | 白天增设专职深审岗 5-8 个：各自负责一小板块（根目录/文档文字/代码等），每天逐步做不贪大，每批 100-300 文件 |
| D9 | 任务切碎+重复指令：自动化只能发重复指令，故每岗指令恒定+游标 checkpoint 自寻址续批 |
| D10 | 千问改数不改逻辑：配置/数据/文档直接改，代码逻辑只出补丁单，夜班 GLM 落 |
| D11 | 自动施工队分两班：**治理班**（项目本体对齐/清理/深审/全景图/图书馆/根目录/表头字段全套）+ **业务班**（挖矿：数据/因子/策略） |
| D12 | 新增**全网战法收集岗**（业务班）：外网全网挖战法（Google/GitHub/论文站等），挖到挖不干净为止；入库走既有 sop_c 外部策略漏斗 |
| D13 | SOP 先行：先盘点现有 SOP→对齐升级→任务清单建进 SOP 体系（长期工作，不另造散册） |
| D14 | SOP 粒度定案：不按环节新造——挖矿按对象各族已有；考试→整装回测同属 backtest_system_sop 一族；缺环仅"问题金字塔考试运营"候补升 exam_policy；全链索引=automation_crew_policy 附录B |
| D15 | automation_sop 族落地（automation_crew_policy+index 两件）+三处升级（README 两族登记+两班导航／sop_c §9 外网渠道／audit_prompts 分工矩阵挂深审岗） |

## 二、ZCode 夜班编制（9 席，23:00-09:00，10-08 自删）

| 席 | 一席一事 | 代表真活（锚点） |
|---|---|---|
| ① 总指挥 | 开班分派/逐席点名催饱和/增量死信仲裁/AI层广播/08:45 晨报 | cmd_ledger 桥册；commit_queue status |
| ② 283问消费席 | 原问题消费 | 工单11张(WORKORDER_MASTER.md)+insuff96(01_phase2_plan.md A28/B37/C31)+fail45(FAIL_REGISTER.md)+pass142复考排程 |
| ③ 审计对齐席 | 边审边修 | cleanup_final/ledger.md ①③④+audit_all 缺口总账 |
| ④ 提交优化席 | 提交链治本 | 提速六台包+落地三发现+D27+心跳线程化+README 校点 |
| ⑤ 死信清账席 | 存量死信清账 | .runtime/commit_queue/dead 318 封按死因分诊→修复→requeue |
| ⑥ 挖矿审查席 | 审白天三矿产出 | 合格品裁定入册/返工单/B37 供数销项；产出写回桥册 |
| ⑦ AI层/模拟盘收尾席 | 收尾清账 | ai_layer_vision 245件(广播后)+模拟盘17件跟投+压测 hold 区看护(禁擅自 requeue) |
| ⑧ 数据作业席 | 数据回补 | 板块分钟K缺日+known_data_gaps 销号+断供对账 |
| ⑨ 注册表健康观测席 | 注册表完整性日巡 | **新增第9席**：每日 reconcile 探针防蒸发（09-22 事故+当日拉锯教训）；W-M1 双轨对账至 09-27+Phase2 扳机准备 |
| ⑩ Owner 席 | 手机插单 | 桥册"Owner 插单"节写一行，当夜总指挥优先调度 |

sid 规范：ZCode 夜班=st-night-<MMDD>-<席号>；Qoder 白天=st-qoder-<岗>-<MMDD>-<NN>。

## 三、Qoder 白天编制（15-20 子代理；写席≤5+读席不限；4 小时岗轮转）

### 3.1 深审岗（D8：每岗一小板块，每天逐步做，每批 100-300 文件）

| 岗 | 板块 | 审什么 |
|---|---|---|
| A1 根目录岗 | 仓库根（README/顶层配置/根级散件） | 失效路径、过时计数写死、过时入口、许可证/声明缺失 |
| A2 文档文字岗 | docs/01_policies_and_standards 散文 | 失效引用、计数矛盾、前后矛盾、过期日期、术语漂移 |
| A3 代码岗·交易域 | src/zephyr/trading | 死代码、裸调违规（duckdb/getenv/datetime.now）、克隆对、TODO/FIXME |
| A4 代码岗·治理域 | src/zephyr/governance+gov_enforcement | 同上+gate 注册一致性 |
| A5 代码岗·数据域 | src/zephyr/data | 同上+SQL 散落、时区违规 |
| A6 代码岗·安全前端域 | src/zephyr/security+frontend+shared | 同上+密钥硬编码、i18n 硬编码 |
| A7 配置测试岗 | config/+schemas/+tests/ | YAML 死键、schema 漂移、测试写生产路径违规 |
| A8 scripts 岗 | scripts/ | 死脚本、路径漂移、裸 git/裸 SQL |

- 深审产出=findings 台账（追加式）+补丁单（代码逻辑类）；**审计员不改代码逻辑**（D10）。
- 修复闭环：改数不改逻辑项→E2 岗白天销；代码逻辑项→补丁单→夜班 GLM 席③④落。

### 3.2 非深审岗

| 岗 | 事 |
|---|---|
| M1 挖数据源 | SL-B 10 线逐线 mining memo 初稿（真源=chain_piling_campaign/02_source_line_registry.md） |
| M2 挖因子 | prereg v2 空间内批次备料（**Owner 签字前只备料不实跑**；config/search_space_prereg.yaml frozen_at=null） |
| M3 挖策略 | 组合候选+历史考试复盘素材（重算力留给 GPU/夜班，千问只做 CPU 轻预筛） |
| E1 数据回补实跑 | 既定 runner 实跑（板块分钟K 等），失败即停写堵点册 |
| E2 机械修复执行 | 销夜班返工单+深审台账中"改数不改逻辑"项 |
| R 读席组 | B37/C31 证据采集、GPU-viability 静态扫描（给 Owner 的 GPU 对话）、堵点/README 盘点 |

### 3.3 写席预算（≤5，D7）

M1、M2、M3、E1、E2 五个写岗=5 个写席；A1-A8 深审岗只写自己的 findings 台账（追加型，冲突面小）——如并发紧张，深审台账写入排队等写席空窗，findings 可先落 .runtime/sessions/<sid>/staging/。

## 四、切碎+重复指令机制（D9，每岗四件套）

每岗四件套（放 docs/_working/automation_campaign/ 下，岗名建子目录）：
1. `scope.md` 板块清单（生成器产出或目录清单，静态）
2. `checkpoint.md` 游标（上批审到哪；每批推进）
3. `ledger.md` findings 台账（追加式，safe_write CAS+claim）
4. `instruction.md` **恒定重复指令**（每次自动化原样重发，内容如下模板）

重复指令模板（A 岗示例，各岗只换板块名与清单源）：

```
【深审岗·<板块>】（本指令恒定，每次执行相同内容）
1. 冷启动三步：PATH 修 Python312 → lock_files cleanup → process_reaper --status（reaper 不在=禁写只报）
2. 读 docs/_working/automation_campaign/<岗>/checkpoint.md 取游标；若已标 DONE 则本轮无事，短报退出
3. 从 scope.md 清单取下一批 ≤100 文件（游标起）
4. 逐文件按审计清单审；findings 追加 ledger.md（safe_write CAS+先 claim）；代码逻辑问题只记补丁单不直接改
5. 推进 checkpoint.md；若清单见底，标 DONE 并汇报总条数
6. 提交走 scripts/git_commit.py --enqueue（sid=st-qoder-<岗>-<MMDD>-<NN>）；失败写堵点册即停，勿硬啃
铁律：只审本板块；发现热册被并发改写立即停手上报；禁跨板块；禁新建规则/gate/注册表
```

## 五、昼夜闭环

白天千问：挖（M1-M3）+采（R）+跑（E1）+修（E2）+深审（A1-A8）→ 夜里 GLM：审矿（⑥）+销返工（③④）+清死信（⑤）+裁定（②）+观测（⑨）+落地 → 白天按判词继续。晨报=Owner 手机看板。

## 六、Owner 桌上待办（自动化不碰）

prereg v2 签字+factors 白名单审定（M2 席签约后才能实跑）｜凭据 R4 轮换裁决｜压测 PhaseB hold 区处置｜GPU 三案（Owner 自己的 GPU 对话内完成，09-25 12:00 点火）。

## 七、开工三步（等 Owner 一声"开工"）

1. 重写正式桥册 automation_master_plan.md 为本编制（token 已在册，可直接落地）
2. 排 ZCode 夜班 9 席自动化（23:00 开班/夜间点名/08:45 收口，全带 10-08 自删条款）
3. 产出 Qoder 全套岗位卡+四件套骨架（scope/checkpoint/ledger/instruction）给 Owner 粘进 Qoder

## 八、SOP 盘点结论（2026-09-24 实勘，docs/01_policies_and_standards/sop/）

现状：**10 族 46 件** + README（SOP-INDEX-001 九族导航）+ index.md + 根级 `audit_prompts_20_ai.md`（全仓打扫+自主审计治本闭环 v4：AI-00 总控 + AI-01~22 域差异表）。
族清单：governance_sop(10)｜construction_sop(5)｜mining_sop(6)｜backtest_system_sop(7)｜data_ops_sop(3)｜trading_decision_map_sop(3)｜ops_sop(4)｜data_audit_sop(2)｜review_sop(4)｜**library_sop(2，未入 README 索引=孤儿族)**。
机生件仅 1 处：commit_navigation_playbook.md（禁手改，源册=commit_guide_sources/）。

六个直答：
a. 自动化班底 SOP：**无**（最接近=data_audit_sop 夜班自主执行版+根 audit_prompts v4 无人值守编排）
b. 全网收集：**有地基**——mining_sop_policy 全网调研六向寻路＋backtest_system_sop/sop_c 外部策略入库漏斗＋data_source_onboarding；GitHub 专项无
c. 审计方法论：**分散三处**（data_audit_sop 族＋review_sop/deep_review 六轴法＋governance_sop/deep_adjudication）＋根 audit_prompts_20_ai
d. 数据库 SOP：仅 data_ops_sop 一族（足够，不另设）
e. 清理归档：按对象分散三处（worktree_cleanup／sop_d 档案命名／audit_prompts）
f. mining_sop 覆盖：因子八段+TASC 指标+域骨架+TDM 寻路+通用全网调研；数据源归 data_ops、战法归 sop_c

**结论（到底要多少套）：10 族不动 + 新建 1 套 + 升级 3 处——**
1. 【新建】《自动化班底值守 SOP》一套：冷启动/claim/队列正门/写域互斥/**切碎四件套+重复指令模板**/晨报协议/插单协议/10-08 自删条款/两班任务清单（附录）。落点建议=sop/ 下新族 automation_sop/（净零声明：收拢本讨论册口头机制，替代散落各包 LEDGER 的操作口径）
2. 【升级】audit_prompts_20_ai.md：深审岗 A1-A8 直接挂 AI-01~22 域差异表（不发明新审计法），补切碎/checkpoint 执行节
3. 【升级】sop_c+mining_sop：补外网渠道清单（Google/GitHub/论文站/quant 站）、GitHub 专项（搜法/许可证/去重）、战法格式化标准 → 支撑 D12 全网战法收集岗
4. 【升级】sop/README+index：登记孤儿族 library_sop + 两班导航节（治理班/业务班各自从哪族进）

## 九、两班工作清单（v1 草案，待升级 SOP 后定稿）

### 治理班（项目本体干净/对齐/新鲜——"远期不用的归档清理+表头字段全套审计"）
全景图对齐（GOMAP 孤儿等）｜图书馆治理（library_sop 血肉编目+08词典残差）｜文件/目录/临时文件清理归档｜深审 A1-A8（根目录/文档文字/代码四域/配置测试/scripts，含 registry 表头字段）｜死信+堵点+队列卫生｜注册表健康观测（⑨席）｜提交链优化+README｜audit_all 缺口收口｜W-M1 双轨观测至 Phase2｜AI层/模拟盘收尾清账

### 业务班（挖 alpha——"全网挖到挖不干净为止"）
283问消费（工单/insuff/复考）｜挖数据源（SL-B 10线）｜挖因子（prereg 管道）｜挖策略（组合候选）｜**全网战法收集岗**（外网渠道全挖→sop_c 漏斗→去重→夜班审查→prereg；注意许可证/合规）｜数据作业回补｜挖矿审查（夜班⑥席）｜模拟盘跟投

席位映射：夜班 9 席中①③④⑤⑨偏治理，②⑥⑦⑧偏业务；白天深审 A1-A8+E1-E2 归治理，M1-M3+全网收集+R 席归业务。两班各设一名夜班班头（总指挥兼）还是各设总指挥=**待 Owner 定**。

### 全网战法收集岗补充（D12 细化）
渠道起步清单：GitHub（quant/回测/因子库，按 star+许可证筛）｜论文站（SSRN/arXiv quant）｜中外 quant 社区/博客｜TASC 等指标专栏（已有 indicator_sop 对接）。
产出物：战法卡（原文链接/许可证/逻辑描述/伪代码/所需数据源映射）→ sop_c 漏斗入库 → 夜班⑥席审查 → 合格入 prereg/图书馆。
能力前置：需确认 Qoder 子代理有无联网搜索能力；ZCode 侧有 WebSearch/WebFetch 可兜底。

## 修改记录

- 2026-09-24 v1 初稿（L0-L6 七席+GPU 席+付费指挥）→ Owner 否付费指挥、GPU 移出
- 2026-09-24 v2 九对话版（挖矿迁白天千问、AI广播权自放、写席≤5）
- 2026-09-24 v3 夜班扩 9 席（+⑨注册表健康观测席）、白天增深审岗 A1-A8+切碎重复指令机制（本册）
- 2026-09-24 v4 两班制（治理班/业务班）+全网战法收集岗+SOP 盘点结论（10 族不动+新建1+升级3）
- 2026-09-24 v5 SOP 落地：automation_sop 族两件新建+README/sop_c/audit_prompts 三处升级完成（D14/D15）；候补=exam_policy 升级承接 283 问考试运营
