---
ttl: task_bound
session: st-infoaxis-20261013
date: 2026-10-13
title: 信息供给轴＋日内做T 总包战役台账
status: active
goal_block:
  goal_statement: >
    六域（传导链/股权穿透/研报/财报/千股千评·互动易/日内做T·Tick）产出物通过事件研究
    验证、结果正确、全绿；目标机制三件（TDM goal 块/目标就绪度生成器/开班令目标块硬前置）
    上线且机生读数在产——151 核心节点目标就绪度非红。
  output_contract: >
    P0 六本域作业簿（六向台账＋自审闸三态过闸＝封矿）｜P1 统一呈批包（裁决总表）｜
    P2 六域信号产出物（输出契约冻结→施工→打靶三裁）｜P3 目标机制三件（goal 块 151 节点/
    生成器出表/gate 在拦）｜P4 端到端事件研究验证全绿＋红蓝对抗通过。
  exam_ref: 事件研究协议（信号后 N 日超额＋方向命中＋多重比较校正＋PIT 滞后面逐源钉死，
    与 condaxis P2 冻结口径同批对齐）；做T 域=逐笔期望增益口径。
  campaign_ref: st-infoaxis-20261013（裁定#516；调研档=00_goal_structure_research_2026_10_13.md）
  acceptance_criteria:
    - 六域产出物事件研究验证通过（验证结果正确，非"写了文档"）
    - 目标机制三件上线且机生读数在产（goal 块落 TDM/生成器出表/gate 在拦）
    - 循环自检连续两轮问题=0；红蓝对抗测出即修
    - 临时文件清理＋GitCommitGateway 落地完整性确认；Owner 呈批项全部呈完
  stop_points: 判据数值冻结（看数前预冻结呈批）｜花钱项（只调研报价）｜退役判死业务资产
    （可先自解，真不可解才登记呈批；SQLite 小图退役=轨 B 保留面出方案不动手）｜宪法六类保留面
  completes_when: 完工判据六条全过；向 Owner 报"信息供给轴五域＋日内做T域全通＋目标机制上线，
    端到端事件研究验证全绿，151 核心节点目标就绪度非红"。
---

# st-infoaxis-20261013 战役台账

## §0 开班与授权

- 开班令 v2（2026-10-13 Owner 全授权）＋三条协调增补（PG/YAML 双尺同 commit 原子｜Q7 新门
  own-scope+净零+30 分钟预告窗｜今夜并行面：维护六班/根面清理班/死信放量班/GPU 六班）。
- 授权真源＝裁定#516（Owner 全批 Q1-Q8＋追批 Q9-Q10，PG registry_ledger 在册 snapshot v23）。
- 模型分层＝方案 B：GLM 5.3 守闸口（本档/契约设计/判据冻结/呈批/验收裁定），GLM 5.3 Flash
  跑车道（挖矿/施工/测试执行）。

## §1 首包三件套

| 件 | 状态 | 锚点 |
|---|---|---|
| ① 调研档入库 | 已入队 q-20261014-st-infoaxis-20261013-0001 | docs/_working/infoaxis/00_goal_structure_research_2026_10_13.md（FOLDER-CAPACITY 治本：根面平铺版迁子目录，CAPCAN token retire+register 同实体随迁） |
| ② ruling_registry 落账 Q1-Q10 | PG 已落（裁定#516 register→snapshot v23）；YAML 投影随①同袋 | 双尺：判"在册"用 PG ✓；判"物化"用 git（落地后 git log 核验） |
| ③ 新开班令带目标块 | 本档 goal_block 即样板，自我适用 | frontmatter goal_block 六字段 |

- 首包波折留痕：直接提交五连拦（FOLDER-CAPACITY→REGISTRY-MASS-DELETION 陈版吸收→
  CREATE-GUARD 撕裂读→TAKEOVER-PENDING 误判死→REGISTRY-YAML-PARSE 指纹竞态）——根因
  均为与提交队列排水竞态，终按宪法 §2.6 改道入队（结构性免疫连坐）。
- TAKEOVER 误判已自证 resolve＋worktree 心跳 daemon 常活（30s）。

## §2 六域地图（P0 挖矿对象）

| 域 | 核心病灶（输入真源§4 摘要） | 状态账互引 |
|---|---|---|
| 传导链 | G5 挂零（部门码↔ig_node 两套 id）；SQLite 小图零实例化；涨价/断供反号未建模；W1-W6 未结案；chain_impact_resolver=testing | F032/F030（C46 簇）；condaxis S4/S5 双锚 |
| 股权穿透 | 新真源 edge_holding 27.5 万条已切（#424）；零信号消费 | F032 G3 唯一全绿 |
| 研报 | collector production 但渠道预期源未接（花钱项）；ig_chunk 语料在库 | F031 B 档 |
| 财报 | PEAD 模块在产缺装配注入；selection_funnel 九阶段零挂接 | F030 数据绿 |
| 千股千评·互动易 | 两表在产，消费端纯管道零信号（Q8：出信号先行一季内无增量退役） | F030 A07/A14 双绿 |
| 日内做T·Tick | TDM-P-P2-01/02/03 全 proposed；miniQMT 模拟盘=实时源＋QMT 桥五档慢 3-5 秒（防前视）；tick 亿级历史断档 PIT 在案 | F043（C46 簇） |

## §3 目标机制三件（P3，与 P0 即刻并行）

- Q5 goal 块：四字段（goal_statement/output_contract/exam_ref/campaign_ref）；分母口径待钉死
  ——调研档写"31 源线身份节点"，tags 机械数出 30（A01-A17×17+B01-B10×10+C01-C03×3），
  差 1 须 P0 钉死（疑 AGG/V2/D1-D2/E1-E2/Z1-Z2 归属），钉死后 151 机械可导出。
- Q6 生成器：对标 l9_readiness_aggregator 全部纪律（aggregate()纯拼装/run_aggregate()60min
  节流写CH/maybe_emit()=task_completed 事件触发禁 cron/绿黄红=fail-open 禁静默绿/
  suspended 不计红/表名 TableRegistry 派生）。
- Q7 gate：新 commit gate CAMPAIGN-GOAL-BLOCK（开班令无 goal_block=拦；own-scope；
  触发面=本笔 git A 态 docs/**.md 且正文含令词；豁免=goal_block_exempt 留痕）；净零声明（§5）。
- **【预告时刻】CAMPAIGN-GOAL-BLOCK 上线预告（Owner 增补 b）：2026-10-14 00:5x 本条落账起
  30 分钟窗口——各班新开班令请带 frontmatter goal_block 三要（样例=本档；或
  goal_block_exempt:<理由≥10字> 留痕豁免）。门随本战役 Q6+Q7 袋合并 dev 后生效，对
  统筹派工令同自我适用。收班册/归档件用豁免标记零打扰。**

## §4 P0/P1/P2/P4 进度

| 相位 | 状态 | 锚点 |
|---|---|---|
| P0 六域挖矿 | **全封矿**（2026-10-14 00:5x） | 10 传导链/11 股权/12 研报/13 财报/14 千股千评·互动易/15 日内做T（六向台账＋自审闸三态过闸） |
| P1 统一呈批包 | **已组包** | 20_ruling_package.md（A 保留面 4 项停等；B 判据冻结 6 项待打靶前；C 技术口径 7 项默认先行；D 重大发现 4 条通报） |
| P3-Q5 goal 块 | **落地**（commit a1debd65@worktree 分支） | 186 节点/151 分母机械复现/19 族表 v0＋注入器探针 5 测试 |
| P3-Q6 生成器 | **落地**（q-0003 在队） | 表已建（11 列）＋首读数 187 行（绿10/黄76/红65/挂起35 诚实读数；CH HTTP 夜窗→local_replay 兜底待回灌）＋8 测试 |
| P3-Q7 gate | **落地**（enabled=false 自举两段） | CAMPAIGN-GOAL-BLOCK priority=142＋预告时刻 00:48＋7 测试；合并 dev 后收班袋翻 true |
| P2 施工 | 开工（2026-10-14 01:1x） | 首批三窄缺口车道：PEAD 装配批/研报预期修正面装配/IrmProvider 修复接线；传导链方向语义、股权三信号族、做T三模块接线随批上 |
| 首包①② | **已落 dev**（d006d7ea26） | 调研档 178 行＋裁定#516（PG v23+YAML 同 commit 原子双尺过） |
| P2 六域首刀 | **全落地入队**（2026-10-14 04-07 时段） | 传导链=方向语义件+resolver v2（q-0008）；股权=三信号族 702 行真数（q-0009）；研报=评级 47+修正三件套 4195 真数（q-0006）；财报=PEAD 2824 事件真数（q-0005）；千股千评=IrmProvider 修复（q-0005）＋微信号装配件（本批）；做T=OFI 特征件+考卡 v2 现势窗（q-0010） |
| P4 验证 | 管线级全通 | PEAD 事件研究端到端：SUE 五档×前瞻 5/20 日读数产出（1738 事件全价覆盖；本窗读数现正 SUE 反转形态——读数如实记录非判定，判据未冻结纪律）；评级变动×前瞻：downgrade fwd1=-1.05%/fwd5=-2.15%（方向经济合理）；五表 CH 全活：goal_readiness 187/pead 2824/rating 47/trio≥1400 键/equity 702 |
| 收口 | 队列清账中 | 死信分诊+销账+Q7 自举二段（门上 dev 后翻 true）由看护车道执行中 |

## §5 净零声明区（全资产净零增长，裁定#375）

| 新增资产 | 替代/合并对象 | 声明 |
|---|---|---|
| goal_readiness 生成器（Q6 新模块） | 复用 l9_readiness_aggregator 架构模式但不并（对象不同：节点目标 vs 源线数据）；读数面收敛进 l9_readiness 同族 CH 表设计 | 净增 1 模块＝目标机制读数面唯一真源，无同域重复簇 |
| Q7 gate | 无旧门可替代（新执法面） | 净增 1 gate；gate_registry 登记 own_scope |
| 六域作业簿（docs/_working/infoaxis/1x_*.md） | 一次性战役件（task_bound），收口按 TTL 处置 | 不替代既有册，互引 fullflow F 号状态账不重建 |

## §6 待裁项登记（P1 汇总呈批）

（P0 各域待裁项随封矿回填；跳过留裁清单随终报）

- P1 包 20_ruling_package.md 已组包（A 保留面 4 项停等 Owner：A1 研报数据采购/A2 股权数据源/A3 SQLite 小图退役/A4 ig_sector_bridge 权限；B 判据冻结 6 项打靶前逐批呈；C 技术口径 7 项默认先行）。

## §7 收班序列（宪法 §2.9）

任务完成＝merge 回 dev → release 全部 claim → staging promote/确认 TTL → handoff 交接包
→ 车道/工棚就地清（session_worktree archive --execute）→ 向 Owner 终报（附跳过留裁清单
＋P1 呈批包进度）。

## §10 夜班施工实录（2026-10-14 00:00-07:00）

- 子代理配额两次撞限（1310）后的施工策略切换：内联施工完成 PEAD/研报/IrmProvider/传导链/股权/做T 六域首刀。
- CH HTTP 夜窗断（00:00-04:00）：四装配 local_replay 兜底，04:00 后 CH 恢复全部幂等重写落库。
- 写通道三 bug 修复留痕：列串括号形（write_tsv 契约 "(a,b)"）／goal_readiness 表 UInt8→Int8 空表重建（RULE-DATA-OPS 三步验证过）／exprev 4195 行批在 ~1400 截断→分块写。
- 遗留基础设施 bug 登记（移交维护线）：write_tsv 分块误报 True（CH HTTP 间歇尾段）＝#ARCH-352 同族；exprev trio 表 1400/4195 键部分落地待日批收敛。
- 队列夜况：cascade_stale 级联（基底被他会话 landing 搅动）致多袋死信；q-0007 撞复发熔断 142 次（auto-retry 循环）弃重投改差量新袋 q-0016；主区脏面阻断 worktree merge（a1debd65 内容改走 q-0017 袋路径）。
- P0 更正追加：fund_earnings_forecast/fund_express_report 注册在册 CH/PG 零实存（"三时点"单时点可工作）。
