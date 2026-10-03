---
ttl: task_bound
session: st-f4-casebooks-20261003
date: 2026-10-03
title: F4 病历挂载方案（五本永久病历本 × 图11 D11-* 挂载面）
completes_when: 总筹复核采纳并随上户口批把 casebooks 字段回写骨架+渲染后，本件转施工输入归档
---

# F4 病历挂载方案（casebooks）

> 战役=commitmap-cure-20261003 · F4 车道（sid=st-f4-casebooks-20261003）。
> 法源=00_design_basis.md §3 病历挂载四机规 + 挂图SOP vertical_map_mounting_policy.md §3/§4（casebooks=L1 菜单四标准字段之一）。
> 红线执行：五源纯读零改写；本件只引用（条目ID/册#章码+一句话）不复制病历内容。
> **路径勘误**：任务书两处路径已过时——①战役目录真身=`docs/_working/commitmap_cure/`（R5 语义名处方，无日期后缀）；②死因案例册真身=`docs/01_policies_and_standards/sop/governance_sop/commit_guide_sources/death_cases_registry.yaml`（非 _registry/catalogs/）。本方案按真身路径引用。

## §0 总表：五本登记身份 → 挂载 → 计数（验收②完备性自检在此）

| # | 病历本 | 登记身份 | 建议挂载环节 | 章级拆分 | 条目计数 |
|---|--------|----------|--------------|----------|----------|
| 1 | 死因案例册 death_cases_registry | **module_id=CFG-COMMIT-DEATH-CASES-001**（owner=MOD-INF-005，ttl: permanent，提交指路指南生成器第三真源） | 主挂 C02/C05/C07/D01-D06；兼挂 S03/S06/C01/C06/C08/C10/C11 | 21 cases 按 6 死因族（§2.1） | 21 |
| 2 | 堵点本 all_problems_ledger | 路径身份 docs/_working/branch_zero_takeover/all_problems_ledger.md（ttl: task_bound，session=st-ffchief-20261002） | 五域各挂：域一→S01-S03/S08；域二→C01/C03/C05-C07/C10；域三→C08/C09/C13/D01；域四→S08/D06；域五→S05/C07/C08 | 五域=五章（§2.2） | 盘面 33（册面口径 35，偏差 −2 见 §3） |
| 3 | 抢救台账 dead_letter_salvage_ledger_20261003 | 路径身份 docs/_working/branch_zero_takeover/dead_letter_salvage_ledger_20261003.md（ttl: task_bound，session=st-deadletter-cure-20261003） | 主挂 D01/D02/D04/D06；兼挂 C08/C13/D05 | 9 章（§2.3） | 底数 1235 袋/12798 文件条目/360 唯一路径；章内结构化条目 70 |
| 4 | 审查发现 review_findings（卷一）+ review_findings_round2（卷二） | 路径身份 docs/_working/branch_zero_takeover/review_findings{,_round2}.md（ttl: task_bound） | 主挂 C11/C13（对账观测环节）；兼挂 S01-S04/S08、C05/C07/C10、D06 | 卷一 3 章+卷二 4 章（§2.4） | 卷一 17 单元 + 卷二 12 编号单元 = 29 |
| 5 | 记忆教训索引 MEMORY.md | 仓外路径 C:/Users/fanzi/.zcode/cli/memories/projects/zephyralpha-88c39a4848e315f8/memory/MEMORY.md（ZCode 记忆库索引，总 376 条） | 30 节点 facts/病历层按 10 主题簇（§2.5）；**禁写 machine_facts 机生面**（防腐三律 1，重扫即清） | 交链相关 10 簇（§2.5） | 交链相关 98/376（口径见 §2.5） |

五本全部 ≥1 环节挂载 ✅；gap 节点 G01/G02 不挂（骨架外缺口件无运行代码可挂，其病历由 C07/C13 同章覆盖）。

## §1 挂载矩阵：环节 → casebooks 字段建议值

字段值粒度=`册码#章码`（册码定义见 §0，章码定义见 §2；图本体只存此字符串列表=INV-1 指针，禁抄条目正文）。

| 环节 | casebooks 建议值 |
|------|------------------|
| D11-S01 会话冷启动 | AP#域一；MEM#1；RV2#缺口(R2-F6) |
| D11-S02 worktree 分配 | AP#域一；MEM#1；RV2#缺口(B-1) |
| D11-S03 心跳与活性 | AP#域一；MEM#1；RV2#缺口(R2-F1/R2-F2)；DCS#队列(DEATH-017) |
| D11-S04 改前 claim | AP#域一；MEM#2；RV1#缺口(F3 归一锚面) |
| D11-S05 暂存晋升 | AP#域五；MEM#2 |
| D11-S06 worktree 内提交 | AP#域二；MEM#2；DCS#队列(DEATH-017) |
| D11-S07 merge 回主区 | AP#域二；MEM#2 |
| D11-S08 放弃与死会话回收 | AP#域一+域四；MEM#1；RV1#缺口(F2/F3/F5)；RV2#缺口(R2-F1/R2-F5)+RV2#裁定(#477/#478) |
| D11-S09 handoff 交接 | MEM#2 |
| D11-C01 提交正门 | AP#域二；MEM#5；DCS#队列(DEATH-017) |
| D11-C02 失败指引递送 | DCS#全册（本册=C02 递送锚 commit_navigation_playbook 的第三真源原料）；MEM#9 |
| D11-C03 claim 结算重试 | AP#域二；MEM#2 |
| D11-C04 全局锁与改道 | MEM#6 |
| D11-C05 in-process 门禁链 | AP#域二；DCS#真源+结构+手续；MEM#3；RV1#缺口(F6) |
| D11-C06 暂存提交本体 | DCS#结构(DEATH-002)；MEM#5 |
| D11-C07 precommit 通道 | AP#域二；DCS#手续+通道+真源+审批；MEM#3；RV1#缺口(F6) |
| D11-C08 入队快照 | AP#域三；SV#底数+SV#治未病；DCS#队列(DEATH-016)；MEM#4 |
| D11-C09 排空调度 | AP#域三；MEM#4 |
| D11-C10 真落盘 | AP#域二；DCS#队列(DEATH-016/018)；RV1#缺口(F3/F4)；MEM#5 |
| D11-C11 post-commit 对账 | RV1#全卷+RV2#全卷（**主挂**）；MEM#10；DCS#队列(DEATH-016 兼) |
| D11-C12 机器车道紧急 | MEM#4 |
| D11-C13 队列台账观测 | AP#域三；SV#治未病(三次重试报警)；RV1#观察+RV2#观察；MEM#10 |
| D11-D01 死信产生 | SV#底数+SV#死因；DCS#队列；AP#域三；MEM#8 |
| D11-D02 死因三分类 | SV#死因+SV#方案(分诊)；DCS#全册（死因→处方蒸馏正典）；MEM#8 |
| D11-D03 死信台账告警 | AP#域三；SV#治未病；MEM#10 |
| D11-D04 requeue 复活 | SV#裁定(B doctor 三铁闸)+SV#抢救目标+SV#口径；DCS#队列(DEATH-009/016)；MEM#7 |
| D11-D05 级联失效 | SV#底数(cascade_stale)；DCS#队列(DEATH-018)；MEM#8 |
| D11-D06 死信归档清零 | SV#裁定(A 不变量 SV)+SV#三问+SV#施工序；AP#域四；RV1#缺口(F4)；MEM#8 |

## §2 各本章级拆分依据（章码定义，逐源）

### §2.1 死因案例册 → 6 死因族（21 cases 全覆盖）

| 章码 | 收录 cases | 一句话（族语义） | 挂载 |
|------|-----------|------------------|------|
| DCS#手续 | DEATH-001/003/005/012/014/019 | 缺 token/目录命名/缺翻译/查重白名单/热册净删/目录容量=补表就能过 | C05/C07/D02 |
| DCS#通道 | DEATH-004/006/010/011/013 | frontmatter/目录契约/ruff/Final/蓝图头=通道内可修 | C07 |
| DCS#真源 | DEATH-020/021 | 词表先行批与热册蒸发=真源一致性病 | C05/C07 |
| DCS#结构 | DEATH-002/007/008/009 | basename 碰撞/搬运孤儿/悬空 import/陈旧快照=结构联动病 | C05/C06/D04 |
| DCS#队列 | DEATH-016/017/018 | 吸收型死信/worktree 假回执/基底冲突=队列机制病 | C01/C06/C08/C10/C11/D01/D04/D05 + S03/S06 |
| DCS#审批 | DEATH-015 | PROTECTED-PATHS 审批通道 | C07 |

### §2.2 堵点本 → 五域五章（33 条全在册）

| 章码 | 条目 | 一句话 | 挂载 |
|------|------|--------|------|
| AP#域一 会话生命周期 | #1-#6 | 鸡生蛋注册/后台树回收/pid 判活/接管三件套/孤儿侦测/V5 护栏 | S01/S02/S03/S08 |
| AP#域二 提交链 | #7-#18 | 落地门超时/belt 空转/守护堆积/连坐/CREATE-GUARD~noqa 门禁族 | C01/C03/C05/C06/C07/C10 |
| AP#域三 belt 与队列 | #19-#23 | 快照丢册/scratch 残渣/目录容量/sweep-absorbed/判弃销账 | C08/C09/C13/D01/D06 |
| AP#域四 档案安全 | #24-#30 | worktree 退役零删除/TTL 区抢救/对拍/tag 归档/判弃裁定/混沌演训 | S08/D06 |
| AP#域五 文档与档案 | #31-#33 | 晚期成品忘入带/TTL frontmatter 族/字面量误扫 | S05/C07/C08 |

### §2.3 抢救台账 → 9 章（§0-§6+裁定章+治未病+施工顺序）

| 章码 | 收录 | 一句话 | 挂载 |
|------|------|--------|------|
| SV#底数(§1) | 归因 7 类+袋桶 4 | 1235 袋/12798 条目三分归因；袋桶 232+435+465+103=1235 对账平 | D01/D05/C08 |
| SV#抢救目标(§2) | 子集 2+线索 2+TOP 样例 10+版本分布 1 | 360 唯一路径=正确手工口径（51+309；108+252） | D04/D06 |
| SV#死因(§3) | 死因表 8 行 | 死因前五全是机械手续（CREATE-GUARD 372/TRANSLATION 191/R5 130/VOCAB 83/DEPGRAPH 74） | D01/D02 |
| SV#方案(§4) | 4 层（L2 判据 4+L3 分支 4+L4 防再生 3） | 急诊分诊台四层：迁移感知/base_head 归因/治愈通道/防再生 | D02/D04 |
| SV#口径(§5) | 口径 3 行 | 逐唯一目标路径而非逐袋 | D04 |
| SV#三问(§6) | 3 问 | Owner 三问（已由裁定章闭合，留档注记） | D06 |
| SV#裁定 | A/B/C（内嵌不变量 SV+铁闸 3+附 1+档位 3） | pristine_lost/never_landed 一律不自动销账+doctor 三铁闸+残差三档 | D04/D06 |
| SV#治未病 | 1 条 | 同一(session,path)被同一门挡 3 次当场报警，不许攒到第 11 版 | C08/C13/D03 |
| SV#施工序 | 4 行 | Layer1→2→4→3 顺序与司法标准（Layer3 走 worktree+裁定登记） | D06 |

### §2.4 审查发现（两卷）→ 7 章

| 章码 | 收录 | 一句话 | 挂载 |
|------|------|--------|------|
| RV1#向量 | A-G 7 判定 | 三夜战役四主张独立复测 10/10 过 | C11 |
| RV1#缺口 | F1-F6 | scan CLI 崩/TAKEOVER-PENDING 静默失效(P0)/CRLF 吸收/孤儿脏面/册陈旧快照 | S04/S08/C05/C07/C10/D06 |
| RV1#观察 | 4 条 | gate_execution_stats 断流/死亡钩子文案/21 条超宽 trigger/ffchief-0020 | C13 |
| RV2#缺口 | R2-F1/F2/F3/F5/F6+B-1 | 判死口径错位/心跳守护假活/sweep 截断/命中面零咬合/注册无埋点/prune 孤儿 | S01/S02/S03/S08/C13/D06 |
| RV2#观察 | I-1/I-2 | pid=0 判死口径（=R2-F1 同物异号）/超宽告警噪音 | S03/C13 |
| RV2#待裁定 | D-1/D-2/D-3 | 三项已全闭环（裁定#477 退回自修/#478 否决纳面降格盘点/D-3 同批治本），留档作门位先例 | S08 |
| RV2#裁定 | #477/#478 | "门给得出处方不构成裁定件"+纳面=仓库级冻结判据不成立 | S08/D06 |

### §2.5 记忆教训索引 → 10 交链主题簇（98/376 条）

口径：钩子涉及 提交链/队列/门禁/死信/belt/serializer/claim/心跳/热册/正门/提交速度 者入选；一题一簇主归属（重复索引行去重计 1）；战役任务书类（commitmap-cure-campaign-plan）不入。挂载=册#簇码指针进 casebooks 人工语义层，**禁写 machine_facts**（机生面重扫即清，防腐三律 1）。

| 簇码 | 条数 | 主题（代表条目，全名单见记忆库） | 挂载 |
|------|------|----------------------------------|------|
| MEM#1 活性与接管 | 13 | 自判死自接管配方/看门两段判活/孤儿侦测/SESSION-REQUIRED 根治/主区蒸发三源抢救（vmount-sop-batch-three-defects、st-construct-20261002、takeover-archreview、chief7-night-war、session-heartbeat-recipes、deepclean、redblue-review、lanech、fullchief、wm1-cutover、fullscore-takeover、drift-watchdog、main-area-evaporation） | S01/S02/S03/S08 |
| MEM#2 claim/暂存/merge/交接 | 11 | 失败连 claim 放锁须重 acquire/claim TTL 300s/验收即提交/merge 连坐走 --merge-finalize/交接令三段分诊（backup-cold-20260924、datasop、safe-write-cas、shared-todo、worktree-optional、t0revival、concurrent-write-rm、owner-merged-handoff、worktree-premerge、morning-closeout、fullflow-mine） | S04/S05/S06/S07/S09/C03 |
| MEM#3 门禁与热册 | 28 | 五连门死因全集/117→99 瘦身/own_scope/注册表先行半落地态/CREATE-GUARD temp-index 读 HEAD/词表线在飞阻断/册陈旧快照（gslim、gate-audit、gaudit2、recfix、ailayer-closeout、wm1-wave0、staticwindow、xhs、regfix-laneA、registry-loss、c1-escape、owner-rule-essence、storageswap2、f2-labels、night-cleanup、zcloseout、commit-pipeline-v2、gate-chain-perf、encfix、tdm-gate-lessons、altdata-dual、automation-night、residual、metaq-283、stfinalbuild、ddup-phantom、commitchain-20260922、night-multi-session） | C05/C06/C07 |
| MEM#4 队列与 belt | 10 | 死信螺旋 76% 失败率/判官与证据不同源/入队同源预检/daemon 吃启动代码/53min 锁饥饿/belt 换血（death-spiral、rootcure-preflight、qcure、belt-daemon、cleaninv、chief9、four-chain、fms-chief、chief4-build、nightsweep-overnight） | C08/C09/C12 |
| MEM#5 落地与正门 | 11 | serializer 执行 HEAD 代码/直投教义 60 秒/判落地必直读 git show/假 SUCCESS/入库铁律/Popen(timeout) 熔断（serializer-headcode、fullscore-night、qoder-legacy、chief6、matrix-final、nightsweep2、workspace-forensics、commitchain-cure-20261001、fullflow-closeout-20260923、nightbuild、commit-pipeline-v21） | C01/C06/C10 |
| MEM#6 锁与提交性能 | 5 | 逐月变慢 P50 40s/门禁 30→128/300s 锁等待 vs 311-393s 门禁链/4 会话硬冲 35min（commit-speed、gate-survival、queue-starvation、concurrent-commit-lock、govreform-p0） | C04 |
| MEM#7 requeue 复活 | 8 | --from-bag 铁律/requeue 翻案从车道 cwd 跑/死袋验 HEAD 后直提/六死袋复活/级联死先 grep HEAD（datatail、w1-restore、metaq-gc、zchief8、chief7-qoder、cleanup-final、f1-guide、debtpay） | D04/D05 |
| MEM#8 死信清零与销账 | 9 | 三分法 purge184+REVIEW5/2733 封矿/--sweep-absorbed 首跑 696/判弃裁定/blob 快照救回/破坏性操作机械可证（dead-zero、finaldel、legacy-audit、c2-shard1、c2-shard2、altdata-night-campaign、owner-mechanical、commitchain-d2、blob-snapshot-recovery） | D01/D02/D05/D06 |
| MEM#9 指南递送 | 1 | 拦截成本前移为指引成本+G1G2 热册还原治本（commitsys-guide-v1-blackhand） | C02 |
| MEM#10 观测与告警 | 2 | 堵点本专人专事法则 N=20/24h 告警+堵点本三记账 kind+THD-ALERT-007（conveyor-principle、regfix-laneB） | C11/C13/D03 |

## §3 验收①：逐源条目计数对账

| 源 | 册面声明 | 盘面实数 | 对账结论 |
|----|----------|----------|----------|
| all_problems_ledger | frontmatter+结语="三十五类全治本" | 编号 #1-#33 连续无跳号=**33 条** | ⚠️ **偏差 −2**（6+12+5+7+3=33）。红线不代修，呈总筹复核：疑域四 7 条中 #24/#26/#30 三条演训/审计事项并计口径差异 |
| death_cases_registry | unique_key=case_id | DEATH-001..021 连续无跳号=**21 条** | ✅ 一致。附注：记忆线索提过 DEATH-022（同构包装器工厂化），盘面册止于 021——疑在指南册或未入册，一并呈复核 |
| salvage_ledger | §0 称 1235 只死袋/12798 条 | 袋桶 232+435+465+103=**1235** ✅；归因 3113+2965+2547+2523+1481+161+8=**12798** ✅；路径 51+309=**360** ✅（108+252=360 ✅） | ✅ 三处加总全对账平；§2 TOP 为 10 行代表样例，全量 360 在 .runtime/tmp/salvage_ledger.json |
| review_findings | 无计数声明 | A-G 7+F1-F6 6+观察 4=**17** | ✅ 内部一致 |
| review_findings_round2 | 无计数声明 | R2-F1/F2/F3/F5/F6+B-1+I-2+D-1/2/3+#477/#478=**12 编号单元** | ⚠️ **R2-F4 跳号**（F3 直跳 F5，无处置说明），呈复核；I-1 与 R2-F1 同物异号已并计 |
| MEMORY.md | 无 | 索引 376 条；交链 curated **98 条**（口径 §2.5，6 组重复索引行去重） | ✅ 口径内自洽；curated 名单可由总筹按 §2.5 复算 |

## §4 验收②③：完备性与只挂本自检

**②完备性**：五本挂载环节数 = 死因案例册 13 环节、堵点本 14 环节、抢救台账 9 环节、审查发现两卷 14 环节、记忆索引 30 节点全覆盖——全部 ≥1 ✅。28 个 stage 节点全部 ≥1 本病历（无零病历环节）✅；G01/G02 显式不挂并注记理由（骨架外缺口件，病历经 C07/C13 同章可达）。

**③只挂本不挂病例**：本方案进图本体的全部内容=册码/章码字符串+路径指针（INV-1）；任何单条 case/袋/条目不进挂载面。§2 表内出现的条目号（DEATH-017、R2-F1 等）仅为**本方案文档内**的人类可读章界注记，不进图字段；章码语义真源=各病历本册页本身，图与方案都不复制其正文。

**SOP 挂载四判据对照**（vertical_map_mounting_policy §2）：为流程而生全挂 ✅（五本全是提交链伴生病历）；路径部位只挂手 ✅（DCS 全册只挂 C02=递送锚原料位，其余按族挂）；影响速质效设施挂 ✅（全部影响提交速度/质量/效率的病史知识）；一岗多流程=引用非复制 ✅（全 INV-1，DEATH-017 三处挂载即三处引用）。

## §5 呈批与落地衔接（移交总筹）

1. **字段粒度呈批**：casebooks 值=`册码#章码` 字符串列表（推荐，保"各环节挂各章"粒度）；或纯册级（更简，丢章粒度）。章码语义真源建议随上户口批在各本册头补一行章码注记（本会话红线不代写）。
2. **身份缺口呈批**：堵点本/抢救台账/审查两卷/MEM 现为路径身份（任务口径合法）；若按机规 1 升级为册号，建议上户口批统一授 CASEBOOK-* 册号或入 ROOR 登记。死因案例册已有 module_id 合格。
3. **账面偏差三笔**（§3）：AP 35vs33（−2）、R2-F4 跳号、DEATH-022 线索——均只登记不代修。
4. **MEM 仓外指针呈批**：图引用仓外绝对路径是否合规需总筹定口径；若图限仓内指针，MEM 降级为骨架 §1 人工语义层注记（机生面禁写不变）。
5. **落地序**：本方案采纳后=骨架回写（00_skeleton.md §1 增 casebooks 字段）→ generate_dev_delivery_map.py 渲染 → 与 W-M1 B3 热册时序禁同窗（design basis §5.4）。
6. **本件合规态**：已 claim（st-f4-casebooks-20261003）+ git add 暂存。**CREATE-GUARD token 未落册，须随 chief 落地批同批原子登记**（capability=commitmap_casebooks，dry-run 已预演 1 条零越界）——本班实跑遭写前守恒闸正确拒写：capability 册正处总筹**改名迁移在途**（盘面三条 token 已换挂新路径 `commitmap_cure/`、HEAD 仍持旧路径 `commitmap_cure_20261003/`，闸判"盘缺 HEAD 3 条"实为合法改名窗口非陈旧蒸发）；按"他会话在途不代修"未动热册，补回旧路径三条=复活 R5 已处方的死目录名，禁走。chief 落地批 temp-index 读 HEAD 配方 + 同批 batch_creation_tokens 即覆盖（届时 HEAD 已含改名修正，守恒闸自通）。
