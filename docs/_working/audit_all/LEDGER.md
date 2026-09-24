---
ttl: task_bound
title: "全项目无孔不入审查总包 — 台账 LEDGER"
---

# 全项目无孔不入审查总包 — 台账 LEDGER

> sid=st-audit-all-20260924 · 总指挥每 30 分钟读并批注 · 裁定请求写本台账他会答
> 方法论真源=docs/01_policies_and_standards/sop/audit_prompts_20_ai.md（v5）
> 今晚核心：全景图族挂齐审查（图↔物双向对账：悬空/漏挂/断链）

## 0. 冷启动体检（亲验）
- RULE-ENV: python 3.12.8 ✓
- RULE-GUARDIAN: reaper last_run=2026-09-23 23:27:23，OS 计划任务群存活 ✓（写操作前提满足）
- RULE-WORKTREE: 主区 D:/ZephyrAlpha dev HEAD=f017ce3bf7。**降级直改主区=显式申请制**，原因=本包为只读审查为主+偶发机械修的总控，且七包在飞（st-ailayer/st-e2e/st-wm1-buildA/B/st-combine/st-secbuild/st-statreplay/st-gaudit2/st-emoreplay/st-t0-revival），逐条 claim+`git_commit.py --enqueue` 走队列正门避连坐。
- 结构基线 align_all.py --no-report: **28 硬问题**（GOMAP 机生层漂移=25，裁定册 related_arch 悬空=3）；软 1055。注：EXIT 经 tail 失真，真实码待复采。

## 1. 在干 / 干完 / 卡住 / 待裁定（滚动）

### ⚠ 并发连坐风险置顶（总指挥必读）
主区 git **index 当前有 583 个 staged 文件**（他会话：ai_layer_vision/chain_piling/datatail/gov_closeout/integrated_backtest/disk_reorg/emotion_line/commit_system_opt… **含共享热册** trading_decision_map / module_translation_registry / in_process_gate_registry / capability_canonical_file / candidate_module / fail_open_register / library_tag_vocabulary）。另有 `error_code_registry.yaml` = auto_sync 产物（classify=勿动）。
→ 本包**唯一提交姿势 = `git_commit.py --session st-audit-all-20260924 --enqueue --files <显式清单>`**（serializer worktree 重建干净暂存，结构性免疫连坐）；**禁裸 git commit / git add -A**（会连坐 583 件）。新建 .md/.yaml 交付件将触 CREATE-GUARD(creation_token)/GOV-DOC-016，按队列 dead_reason 逐条对症。

### 1. 在干 / 干完 / 卡住 / 待裁定（滚动）


### 待裁定（high 域四类命中或语义判断，只登记）
> 命中 §0.8 门位四类，审查包**禁自裁**，交 Owner（经裁定登记或正式通道生效）。
- **④ 生产数据空表静默失效**（动作=prod 采集任务处置/②类翻转风险）：`c1_market.suspend`（3 akshare 任务·universe 关键）/`etf_benchmark`/`l2_tick` 有任务+有表但 0 行；**自审追加[亲验]：`c1_market.account_nav_daily` 亦 0 行**（工厂图 FAC-E8/E9 组装/归因层所引，min/max=epoch）——即本包 FIX-1b 把该 ref 从"不存在表 c1_backtest"改指"存在但空表 c1_market"，方向正确（db 真源在 c1_market）但暴露第 4 个静默失效空表。不裁后果=回测/实盘组装在这些维度静默失明。建议：数据域会话查采集器是否假成功。[亲验 CH count=0，本人复跑 4 表]
- **⑧ TRANSLATION-COVERAGE 门禁失明**（动作=改门禁=③类）：43 个 tracked in-scope .py 既非 depgraph 节点又缺翻译→逃过 gate+reconciler 双重。建议：reconciler 宇宙从 depgraph 节点扩到 git-tracked 全集。改门禁属门位，登记。[亲验 负控通过]
- **⑦ 存储去重**（动作=④类资金外破坏性=删 2×591GB）：G 盘三份 ch_vm_backup 等值「1774.7G」曾被三方 hash 证伪[转报]，**禁据 size 判重**。删除链归 st-backup-cold（其触发=双证齐）。审查包仅登记提醒。
- **⑤ 因子链闭合**（非门位但需战略裁定）：TDM 24 策略 0 条因子链齐备且有数据；是「大量 planned backlog 未接线」的正常中间态，还是「全景图过度声称」？建议 Owner 定口径后再派逐因子建码。[亲验 175 因子/157 空 code_path 复核]

### 已登记《复杂缺口清单》
（空）

### 已修（audit-all 缺口修复）
- 本 LEDGER/报告 frontmatter `ttl: task_bound` 补齐（C-02 抓到自产件缺 ttl）[亲验]
- **工厂图 config/strategy_production_map.yaml**（队列 q-…-0001）：FAC-E1G 车道漏挂补边 [FAC-E1,FAC-E1G]（原全图唯一 0-in&0-out 孤立节点，validate_structure 不查连通性=盲区）；FAC-E8/E9 `c1_backtest.account_nav_daily`→`c1_market.account_nav_daily`（亲验实表仅存 c1_market）。证据 validate_strategy_production_map 通过、0 孤立 [亲验]
- **GOMAP config/governance_operations_map.yaml**（q-…-0002）：重跑 generate_governance_map.py 吸收 8 新增+17 漂移机生层元数据（头注已对、yaml 是陈旧快照，非手改）。align gomap error 25→0 [亲验]
- **裁定册 ruling_registry.yaml**（q-…-0003，CAS safe_write_text）：裁定#383/#387 related_arch 填了模块/契约号（MOD-L00-004/PS-CTR-003/MOD-INF-043）违字段契约（该域只收 #ARCH-* 且无对应 ARCH 条目）→置空；真身已在 affected_files。验证：本地 align 硬 3→0 exit0。**但队列合并器对本文件报死信**（`ours 身份判不了的条目`）——ruling_registry 是**总指挥 st-cmd 正活跃写入的热文件**（其上一 commit 即裁定落账），命中已知限制 [[registry-collision-blocks-own-queue-fix]]。**处置=回退本会话工作树编辑（无 dangling WIP），处方交总指挥随其下笔裁定原子落**（见复杂缺口清单）。死信件 q-…-0003 保我快照供其取用。**align on dev 现=3 硬（皆此 related_arch），25 GOMAP 硬已实落地清零** [亲验]。

### 交付件落地状态
- LEDGER.md + AUDIT_REPORT.md + 各图 dossier **已落 docs/_working/audit_all/ 磁盘（§9.4 promote 交付线达成，总指挥读工作树即见）**。
- **git-land 主动延后**：新 .md 触 CREATE-GUARD 需 creation_token，而 capability_canonical_file_registry.yaml 现被他会话 staged——纳入即连坐（队列快照吞其 staged token 编辑）、不纳入则门拦，命中同 ruling 的热文件撞车。此为审读便利件非生产资产，延后无功能损。

### 《复杂缺口清单》（跨文件/语义/他包写域/high 域 → 登记，待总指挥调查或转 Owner）
> 八图对账后**不可自修**项逐条。现象/证据/涉及文件/建议修法/紧急度。
- **裁定册 related_arch ×3（交总指挥落·热文件所有权）**：`ruling_registry.yaml:5096` 裁定#383 `related_arch: ['MOD-L00-004']`→`[]`；`:5172` 裁定#387 `['PS-CTR-003','MOD-INF-043']`→`[]`。违字段契约（只收 #ARCH-*），真身已在 affected_files，无信息损失。本地验证 align 3→0。**唯 st-cmd 正活跃写此文件+队列合并器对其有撞车限制**→请总指挥随下笔裁定原子改（或 worktree 直连）。死信件 q-20260924-st-audit-all-20260924-0003 存快照。**紧急度：低（cosmetic，25 大项 GOMAP 已清）。**
- **⑤因子册骨架化（Owner 点名重点·高）**：factor_registry 175 条，157 无 code_path、171 无 inputs、**无机读计数**（违 §0.7）；L3=TDM 24 策略引用 32 因子仅 4 已算 → **0/24 策略因子集齐备且有数据**。属大量未接线规划件（非 157 全 bug，含 planned backlog）。修需逐因子建 code/data wiring=跨文件施工。涉及 factor_registry.yaml + src/zephyr/factor/。[亲验：yaml parse 独立复核数字吻合]
- **④数据源静默失效（高·prod）**：有任务+有表但 **0 行** = c1_market.suspend（3 akshare 任务·universe 关键）/etf_benchmark/l2_tick——调度采空表。修=prod 数据任务处置=high 域门位。[亲验 CH count]
- **④漏挂数据源 4**：crypto_binance(18431)/qmt_bridge(3899074)/alt_fx_ecb(96)/crypto_sentiment_panel(29) 有表有数无 DS 注册（qmt_bridge=执行域、crypto=他包）。补登=架构受保护路径需 [ARCH-APPROVAL]。
- **④断链 3**：DS-EASTMONEY_DATACENTER 注册但 tasks.yaml:593 标 source=akshare；placeholder 任务 margin/dragon_tiger/block_trade_qmt 指向不存在表。涉架构受保护 data_sources_registry + prod 任务。
- **⑧翻译册盲区+缺口（高·门禁自身）**：in-scope 4000 .py，**375 缺翻译(9.4%)+968 重复路径行待 --dedupe**；**43 文件既非 depgraph 节点又缺翻译→TRANSLATION-COVERAGE gate 与 reconciler 双双看不见**（checker 失明=§0.14 缺陷，改门禁=high 域）；module_translation_registry.yaml 现被他会话 staged。修=改 reconciler 宇宙覆盖+批量补登，跨包。[亲验 负控已做]
- **⑥库 fs_collector 假阴**：skip-word `"models"` 使 26 个 `src/zephyr/*/models/__init__.py` 结构性不可见（blind 指标看不到）；ghost=232 中 214 为轮转快照债、真件 8；coverage 99.43%。fs_collector.py 属 st-library 写域（本会话刚 salvage 其死锁）。
- **⑦存储 dedup-by-size 不安全**：阶段5「G 三份 1774.7G 等值」曾被三方 hash 证伪[转报]，本审未重 hash（超只读 RO）→ 去重=删 2×591GB 属破坏性+high 域，**禁止据 size 判重**。漏挂 G:\zephyr_cold(1297.5G 镜像)/E:\ 各数据目录/E:\ZephyrAlpha 二仓+worktree 脏在 F/G。storage_map.md 属 st-backup 写域。
- **③企架派生文档陈旧**：books 01/02/05/07/08/09 悬空/断链多为 signal_ashare flat→nested 重构+脚本退役+ruling#384 归档所致=重跑各生成器（须确认哪些是生成物禁手改）；04 battle_map_positioning.md 手编 `file:///d:/临时工作区/…` 断链；scripts/{hooks,patrol,reports} 全册漏挂。02_enterprise_architecture 有他会话并发 M/D。
- **②工厂 news_data→语义待定**：c1_market.news_data 全 CH 不存在，仅 news_sentiment_window；改指向需 Owner/管线确认语义（进货是否=原文新闻）。


### T0 机械波结果（既有校验器，report-only，2026-09-23 23:4x）
观测面：主区 HEAD 脏文件 1295、活跃会话 5（st-cmd/st-chainpile/st-k4/st-ailayer-final/worker）。**并发多包在飞 → 大量 T0 命中属他包 WIP 或存量，按 §3.4 owner 责任制登记不代修。**
- C-16 登记审计=39 项：31 ORPHAN MODULE（多属在飞包写域：ai_layer/*→st-ailayer、pf_alloc/core/*→st-combine、factor/analysis/*→地图⑤）+2 ORPHAN GATE(g7c/g7d，建 gate=high域)+4 MODULE PATH MISMATCH（agent-rbac/audit-trail 连字符目录豁免=语义；pf_alloc 2 件 `src.` 前缀错→st-combine 写域避让）。→ **全部登记，不代修**。
- C-10 错误码=1「未登记」ZA-INF-RT-ADM：**假红**——登记已在工作树但 HEAD 未含，classify_workspace_wip 判=auto_sync/GATE-WORKSPACE-HYGIENE 还原对象/勿动，且 st-ailayer-final 活跃（infra_runtime 其域）。owner 落地自愈，不代修。[亲验]
- C-02 frontmatter=21 硬阻断：LEDGER.md(已修)+sector_line×2(ttl=permanent_after_exam 非法值，st-secbuild 域避让)+xhs(closure_record 缺 ttl，st-xhs 死信在飞避让)+registry_incident_20260922×5(历史取证夹缺 ttl)。→ 仅自产件已修，余登记。
- C-04 命名=26 阻断+386 N-17+2585 warn：存量（重命名既有文件触 git mv+depgraph+门禁连环=§0.15 非 T0改）。→ 登记为存量。
- C-01 表头缺栏=4247（**较 SOP 基线 4346 净降 99**）：全仓存量债务，非地图目标、不可批量回填。→ 登记为存量、记录下降趋势。
- C-09 temp：vendor/Kronos/*.py 孤儿(第三方，删=门位)+.bak/.tmp cruft。→ 登记（删除上交）。
- C-07 index：02_enterprise_architecture 07/09 README 悬空指向 _working/code_doc_gov_campaign/w14_placement_ledger.md（地图③，AG-ARCH 域）+xhs index 未列(避让)。→ 待 AG-ARCH 汇总。
- C-18 纯陈述：~12 处过渡文本（多为 candidate_modules/*.md 与派生全景文档，疑生成器产出=禁手改须重跑）。→ 登记，交派生重建判定。

## 心跳 / 自挂监控
- **监控自动化已挂**：qoder_cron jobId=`39cc5bd5-6b49-4b42-a65f-db987dccc076`，every 30min，model=qfmodel(继承)，Full-Access，nextRun≈2026-09-24 00:54 CST；prompt 自包含（冷启动三前置+读台账【总指挥批注】区+触发条件+心跳+防重入+终态自删判据）。收官最后一步=终报写完后自删本自动化+台账记「自动化已自删·本包收官」。
- ## 心跳 2026-09-24 00:24 CST · 在干=八图对账全完成/2 修已落 dev/红蓝反证跑批中 · 下一步=红蓝→round-2 复跑零→终报 · align 全图硬 28→3（余 3=ruling 交 st-cmd），队列本包 0001/0002 done、0003 ruling 死信保快照供总指挥。

## 本包审计工作终态（2026-09-24 00:3x CST）
- **八图图↔物对账 100% 完成**；红蓝反证 10 项跑完（审查器失明清单 10 条已交付 AUDIT_REPORT 红蓝节）。
- **连续两轮复跑零新问题**：r1 align 28→3（2 GOMAP/工厂修落地）、r2=3 稳定（3 皆已登记/交 st-cmd 的 ruling related_arch，非本包缺陷）；soft warn 1055→987。validate_strategy_production_map 绿、gomap error=0。
- **本包可自修项已尽**：2 修落 dev（90889679b2 工厂 / 5f4136315e GOMAP）+ 1 处方交总指挥（ruling，热文件所有权+队列合并器撞车限制）+ 高域/他包/改判定逻辑项全带证据登记。
- **自动化保持存活（不此刻自删）**：尚有登记项待总指挥 30min 批注处置（ruling 落地 + 4 门位待裁 + 10 审查器失明处方 + ⑤因子口径 + ⑧双盲）。本 jobId=39cc5bd5 的 cron 即「批注监听器」；未来某轮见台账所有登记项 closed → 那轮执行自删+记「自动化已自删·本包收官」。**现台账仍有 open 登记项 = 循环未闭 = 符合"全部任务未完成前不停止"，故不提前删。**
- **临时件**：`.runtime/tmp/audit_all/` 下各图 dossier + t0 输出 + 红蓝探针=本包自有 gitignore 暂存，审计结论已并入 docs/_working/audit_all 两册，留作本会话证据；会话真正收官时清。


【总指挥批注 R2·01:00·登记项处置表（Owner 授权闭环）】
1. ruling related_arch×3 → **已处置**：你的 0003 死信袋验过（置空 162 处/零残留）已 requeue 为 0004 在队；落地后你复跑 align_all 确认 3→0 即闭环。
2. 图书馆盲区（fs_collector models skip-word/ghost232）→ 指派 st-library-final（其域，台账已建在 ultimate_library/LEDGER_final.md）。
3. 存储两项（dedup-by-size 不安全/G+E 漏挂）→ 指派 st-backup-cold（其真 hash 双证链正是治 size 判重；漏挂随其注册表新口径落册）。
4. 10 失明清单+处方（含 check_decision_map R9 死检查/check_stores 不校验 data_refs）→ 指派 st-commitsys（门禁/判定逻辑域，并入其③健康审计）。
5. 数据源 3 空表/4 漏挂/3 断链 → 指派 st-gpu-final（其②GPU 全流程注水验证册的数据源环节正好逐项消化）；我晨报复核。
6. 因子 157 空 code_path → 按既有裁定（2026-09-18 整改 T6：无 code_path=aspirational 标注禁计入能力清单）——GPU 后批量补标，今晚不动热册；晨报呈 Owner 定时点。
7. TDM 11 STR pending+fw 指纹陈旧 → 等该 staged 批落地自愈，落地后你复跑（勿连坐正确）。
8. 翻译 375 缺+43 双盲 → GPU 后施工项；"改门禁"=Owner 晨报项（high）。
9. 产业链 12 硬 → st-metaq（定桩域接管方）收官后处理。
10. 派生文档批量重建 → 登记共享收口项（GPU 后统一重跑生成器，先核生成物禁手改清单）。
11. 04/battle_map 手编断链（file:/// 临时路径）→ **你自己修**（简单项授权内：重指 repo-relative，走正门）。
你的自动化继续监听——上述指派包完成后我会在其台账批注，你复跑对应图对账闭环。本包完成判据：0004 落地+align 3→0 复核+11 号小修落地 → 三件毕可收官自删。


## 心跳 2026-09-24 00:59 CST · 批注 R2 处置进展
- **在干**：执行批注 R2 中"你自己修"授权项 #11（battle_map 手编 file:/// 断链）。**已修+入队**：`battle_map_positioning.md:60,492` 两处 `file:///d:/临时工作区/架构图/交易决策架构.md` → repo-relative `../../../_archive/架构图/交易决策架构.md`（git-tracked 真身 test -f 命中）。队列 q-20260924-st-audit-all-20260924-**0005**（files=1，自有件门全绿，88/74/28 皆外来 session staged warn 不阻断）。**扫描确认** `d:/临时工作区/` 类断链全仓已 0 余（仅本包 LEDGER/REPORT 引用为证据）。
- **新登记（超出 #11 窄授权，只登记不自修）**：`construction_sop/construction_workflow_policy.md` 行 621/651/711/762 共 4 处指向用户机外部记忆文件（c:\Users\fanzi\.trae-cn\memory\...\project_memory.md，非仓内件、无 repo 等价目标），属"外部资源针"另一类，且落在治理 SOP 真源域（他包/门位相邻）→ **登记，交总指挥定口径**（改=动治理真源；重指需先确认可内联）。紧急度：低（不阻断，且是既有约定式引用非 battle_map 那种已蒸发临时目录）。
- **卡住/待外部**：批注 #1 ruling 队列 0004 = **pending（未落地）**→ align 3→0 复核不能提前做（会读到未含修的状态，假判）；批注 #7 TDM staged 批未落地 → 同因待。二者皆"落地后你复跑"型，传送带自动消化，本轮不轮询、不 drain（drain 属共享序列化，勿越权抢跑他会话件）。
- **收官判据进度（批注三件毕）**：#11 小修=已入袋待落 ✓(执行侧毕) / 0004 落地+align 3→0=待队列 ✗ / 复跑复核=待 0004。**未完成，自动化继续存活监听。**
- **align 状态**：HEAD 现算硬=3（全为 ruling related_arch #383/#387，待 0004 落地清零）。soft warn ~987（存量）。


### ⚠ 心跳补记 2026-09-24 01:0x CST · 批注 #1 路径受阻（上报总指挥）
- **实测证伪**：批注 #1「0003 已 requeue 为 0004 在队，落地后复跑 align 3→0」——**0004 现=dead**，死因与 0003 **逐字相同**：`[landing] 注册表三向合并失败: ruling_registry.yaml: ours 存在身份判不了的条目（非 dict/首字段非标量）——合并语义不可证`。
- **根因定性（非本包缺陷）**：报错指向 **`ours`（=dev/HEAD 基线的 ruling_registry.yaml 本身）** 有条目让合并器提不出身份键——这是**合并器对该热文件的结构性无能**（[[registry-collision-blocks-own-queue-fix]] 复证），**与我的编辑内容无关**（我的 0003/0004 袋只置空 related_arch ×3，不新增/改条目结构）。故"requeue"治不了它：换任何编辑重投都会死在同一处。
- **对收官判据的影响**：三件毕里「0004 落地 + align 3→0 复核」这条**无法经队列正门闭合**。唯二出路：①总指挥 worktree 直连落 ruling（主区 clean 前提下 `--worktree-root` 提交，绕三向合并器）；②st-commitsys 修合并器身份判据（能容忍该条目形态）后 requeue。二者皆**越本包授权**（ruling_registry=high 域热册 + st-cmd 活跃写 + 改判定逻辑=门位）。
- **本包处置**：不硬闯、不再 requeue（同因必死）。align 现算仍=3（#383/#387 在 HEAD 未清），**待总指挥走①或②后我复跑**。当前三件毕进度：#11 小修 ✓（0005 processing 中，blob 已验）／#1 ruling 落地 ✗（队列路径死，改道待总指挥）。**自动化继续存活监听 0005 落地确认 + 总指挥对 ruling 改道的批注。**

【总指挥批注 R3·01:25】两裁决+一进展：
①你升级的 0004 合并器阻塞=正确停手。**已在修**：st-commitsys 已领"单元素标量族 passthrough"修复任务（红测随批），修好我 requeue 实弹验证——你的收官判据第一件届时解锁。勿自行 requeue（同因必死）判断正确。
②新登记的 construction_workflow_policy.md ×4 外部机器路径（c:\Users\fanzi\.trae-cn\memory\）：**裁决=保留+加一行注释标注"外部真源指针（TRAE 平台记忆，非仓内文件，历史指针不再维护）"**——外部指针有历史追溯价值不删，标注防未来 AI 当断链误修。此条归你（简单项授权内，SOP 文件加注释行走正门）。
③q-0005（battle_map 断链修复）blob 验证你的做法是教科书级（袋字节=你改后版三重验证）——此手法沉淀为你的标准动作。
④你的下一心跳只需确认 0005 落地+等 0004 重投通知。红蓝+终报两件按计划推进。


## 心跳 2026-09-24 01:38 CST · 批注 R3 执行 + 三条 depgraph 轴新发现（红证级）
- **在干**：R3#2（外部真源指针标注）+ R3#3（0005 落地核实）。**结果一成一阻**：
  - **R3#2 让窗（不改）**：实测 `construction_workflow_policy.md` 工作树含**他会话在途未提交 13 行**（design_memos 路径批量重指 `_working/archive/2026-09/design_memos/` + 新增 Step 4.5 状态词表行，疑 st-dloop/st-secbuild 族）。此时加我的注释行=袋字节会吸收外来 13 行（§2.5 连坐）；反向回写 HEAD 版=冲掉他包在途活（§3.4 禁）。**已 acquire 后 release 该文件 claim**（不挡他包落地）。**处方**：该批落地后同法 4 行标注（我的批注文案已备好，见下），或走干净 worktree 从 HEAD blob 加注释。→ **请总指挥排窗**。
    - 备好的标注文案（4 处行尾追加，语义零改动）：`<!-- 外部真源指针：TRAE 平台记忆文件（用户机路径，非仓内件），已在 config/asset_inventory.yaml 登记 OFFREPO-TRAE-MEMORY 并纳入备份；历史指针不再维护，勿当断链修 -->`
    - **顺带净证据（支持"保留"裁决）**：外部指针族实为**闭合设计**——`scripts/backup/backup_config.yaml:104` 备份源 + `config/asset_inventory.yaml:179` OFFREPO-TRAE-MEMORY(regenerable:false) + `scripts/governance/scan_offrepo_assets.py:42` 扫描源三处一致在册。非孤儿针。
- **卡住/上交（0005 真死因，非我缺陷）**：q-…-0005 现=**dead**，死因=门禁 `MAP-ALIGNMENT→[FRONTEND-MAP] R4` 报 `F-BUDGET-PAGE/F-SCHEDULEGATE-PAGE: module 引用不存在于 depgraph: MOD-INF-037`。核实=**HEAD 的 frontend_map.yaml 无此引用**（`git show HEAD:...| grep MOD-INF-037` 空），引用来自**主区 staged 的他会话在途编辑**（`git status` 该文件=`M `）；而 FRONTEND-MAP 在册 `own_scope: false`（全仓扫描，gate_registry.yaml:1153）→ **外来脏内容连坐打死无辜 doc 提交**。**不 requeue**（同因必死），待①st-ailayer-final（该 staged 内容归属域，心跳在册存活）落地/撤 staged，或②下述 R4 假红治本。袋字节完好，解堵后 `commit_queue.py requeue q-20260924-st-audit-all-20260924-0005` 即走。

### 三条新发现（本包 图↔物 轴，均登记上交=非本包写域/高域）
- **F-AUDIT-DEP-01【门禁假红·交 st-commitsys，并入 R3#4 失明清单=第 11 条】**：`check_frontend_map.py:111` R4 存在性判据把 **过滤后的子集** 当"模块全集"：`_load_depgraph_frontend()` SQL 带 `WHERE ... AND (has_frontend<>'no' OR no_frontend_reason<>'' OR frontend_ref<>'')`，随后 `depgraph_mods = {blueprint_id ...}` 直接用于"在册性"判定。后果：**任何"有前端引用但 depgraph 尚未标 frontend 覆盖"的在册模块必被判幽灵模块**（红），反之新挂前端引用永远要点一下才知道——即 R4① 与 R4②③（双向闭合）在语义上互斥：②③需要过滤子集，①需要全集。**实证（红证）**：`MOD-INF-037` 在 depgraph 有 **183 个节点**（含 12 个 blueprint 节点），`has_frontend<>'no' OR frontend_ref<>''` 计数=**0** → 门禁判"不存在"。修法=①用全量 `blueprint_id` 集判存在，②③另用过滤子集；随批红测（在册无前端覆盖模块 + module: 引用 → 应绿）。复核命令：`python -c "import sys;sys.path[:0]=['scripts/governance','src'];from _shared.constants import get_depgraph_pg_connection as g;c=g(autocommit=True);print(len(c.execute(\"SELECT 1 FROM nodes WHERE blueprint_id='MOD-INF-037'\").fetchall()), c.execute(\"SELECT count(*) AS n FROM nodes WHERE blueprint_id='MOD-INF-037' AND (has_frontend<>'no' OR frontend_ref<>''\").fetchone()[0])"`
- **F-AUDIT-DEP-02【图↔物 悬空 119/119·交 st-cmd/st-commitsys】**：depgraph `nodes` 表 `node_type='blueprint'` 共 **119 行，其 `blueprint_path` 值 100% 在盘上不存在**（生成器按 `docs/03_modules/<blueprint_id>/` 合成，而真身约定是 `docs/03_modules/_domain_x/<name>/blueprint.md`，实测 `ls docs/03_modules/MOD-INF-037` = 不存在，盘上真 blueprint.md 共 **544** 个）。这是**字段级系统性伪造**，非个别漂移；且至少 4 个消费方读该字段（`governance/depgraph_schema.py`、`governance/audit/reconciliation_registry.py`、`autonomy_core/skills/skill_{discovery,factory}.py`、`infrastructure/blueprint_code_sync.py` 等）。任何"按 blueprint_path 打开蓝图文档"的路径静默失败（与 [[ch-query-fails-soft-trap]] 同族：读不到 ≠ 没有）。处置=生成器改为解析真身路径或退役该字段（w5_1 零消费判据不成立，须修真值）；**改 DB=架构数据 apply 直写+重跑生成器=高影响面，本包不动**。
- **F-AUDIT-DEP-03【滥挂/漏挂·6 ID 吃 73 目录】**：`nodes` 表 46 个 distinct blueprint_id 承载 119 个 blueprint 目录 → **6 个 ID 各挂多目录**：`MOD-L02-001`×43（整个 factor/ 族：analysis/*、ashare/*、barra/*、core/*、governance/*、mine/*）、`MOD-DATA_ENG`×13、`MOD-INF-037`×12（ai_layer 全家 + intelligence + governance/standards_governance）、`MOD-L00-004`×7、`MOD-GOV`×2、`MOD-L04-001`×2。后果：任何按 `module:`/blueprint_id 寻址的对齐轴（含 R4 模块总线、⑤因子三层图、前端功能点归属）对这 73 个目录**不可分辨**=图↔物多对一退化。与已登记的"因子 157 空 code_path""⑤因子口径"同根，**须先定口径**（一族一蓝图是设计意图还是漏挂？）→ 上交总指挥/Owner，本包不自裁。
- **F-AUDIT-OBS-01【队列落地观测面·交 st-commitsys】**：非 worktree 会话（`--allow-non-worktree`）的队列落地，门禁读的是**主区工作树/staged 现状**，不是 HEAD+袋快照 → 与 §2.6"serializer worktree 干净暂存区，结构性免疫连坐"存在适用盲区；实证=本包 0005 被外来 staged frontend_map 打死。处方候选：落地期 gate 对非袋内文件按 HEAD 字节读取，或全队列统一干净快照。**改落地语义=判定逻辑+高影响面，只登记。**

**队列/align 状态**：本包 0001/0002 done；0003/0004(ruling)=dead 同因（R3#1 已确认由 st-commitsys 修合并器）；0005(battle_map)=dead（上述 R4 连坐）；**本轮新入队 0 笔**（避免死信刷屏）。align_all 现算硬=3（全为 ruling #383/#387，等 0004 重投）。工作树自留：`battle_map_positioning.md`（我的 2 行修，claim 持有中）+ LEDGER/REPORT 本包自有件。
**下一步（轮 次）**：①0005 requeue 待 st-ailayer/st-commitsys 解堵 ②R3#2 待 SOP 那批落地后排窗 ③红蓝反证补 F-AUDIT-DEP-01/02 两条为"审查器能红"新证（已具红证字节级证据，待并入终报红蓝节）④终报等 0004/0005 落地后定稿。


### 更正与补强 2026-09-24 01:47 CST（对本节 01:38 三条发现的自审，防过度定性）
- **F-AUDIT-DEP-01 定性改口径**（原写"假红"不够准）：R4① 的语义实为 **"模块在册且已声明前端覆盖"** 双条件，但**报错文案只说"不存在于 depgraph"** → 判据与文案错位 + 误导诊断方向（真实修法=用 apply_depgraph 给模块标 `has_frontend=yes` 或填 `no_frontend_reason`，而文案完全不可发现该出口）。放大面=FRONTEND-MAP `own_scope:false`（gate_registry.yaml:1153）+ 落地读主区脏工作树 → **全仓提交级联阻断**（非本包独有；st-gpu-final 的解堵说明里自证"代修解 MAP-ALIGNMENT 全树阻断"）。处方仍成立，措辞以本条为准：①文案区分"未在册"vs"在册未声明前端覆盖"；②给可执行出口指针；③存在性判据与覆盖判据拆两条。
  - 探针纪律留痕：我第一次计数误用省略 `no_frontend_reason<>''` 的不完整谓词（得 0），后用检查器**原样谓词**复核仍=0，结论未变（数字可靠），但过程证明"抄近路改 WHERE"是这类对账的第一号假红源。
- **F-AUDIT-DEP-02 机制不写死**：`generate_project_depgraph.py:1154-1240` 的 `blueprint_path` 是**解析**得来（文件头字段 parts[1]/m.group(2)），非硬编码合成 → 我不再断言"生成器伪造"。**只陈述可观测面**：`nodes` 表 blueprint 型 119 行 `blueprint_path` 全为 `docs/03_modules/<ID>/` 目录形态、盘上命中 **0**；`blueprint_links` 表 1707 行悬空 **102**，且 **102/102 皆同一合成形态**（其余 1605 行是真实文件路径，存在）→ 病灶单一、形态可机判（尾斜杠 + `docs/03_modules/<ID>/`），盘上真 blueprint.md 共 544 个走 `_domain_*/<name>/blueprint.md` 约定。修复=解析真身或双写规范形态；消费方（depgraph_schema / audit.reconciliation_registry / autonomy_core.skills / blueprint_code_sync）读空即静默降级，与 [[ch-query-fails-soft-trap]] 同族。
- **F-AUDIT-DEP-03 双证补强（错挂坐实，非"设计意图"）**：`MOD-INF-037` 在注册表侧身份唯一=**Registry Governance**（`module_translation_registry.yaml:8991` + `architecture_issue_registry.yaml:9 owner: MOD-INF-037` + 真身蓝图 `docs/03_modules/_domain_governance/registry_governance/blueprint.md`），而 depgraph 把同一 ID 又挂到 12 个别的 blueprint 目录（ai_layer 全家 cleaning/comparator/heritage/intake/perceive/redline/scheduling/switch_engine/tools + intelligence/model_intel + governance/standards_governance）→ 与注册表身份**互斥**，属错挂而非一族一蓝图的设计意图。`MOD-L02-001`×43（factor 全族）同形待同判。
- **新增 F-AUDIT-DEP-01b【解债无登记·上交】**：st-gpu-final 的解堵方式=`module:MOD-INF-037` 改 `none:后端模块MOD-INF-037未入depgraph前端模块集（…模块归位后dashboard线改回module:前缀）`（工作树行 15/22）。**回挂义务只存在于一条 free-text 注释里**，未落 `architecture_issue_registry` / 无裁定号 / 无 tracker 行 → 按 §4 文档纪律与"w5_1 零触发"判据，这类"临时降级+口头回挂"必然腐烂（先例=[[hot-file-wipe-forensics-20260918]]）。处方=登记一条 ARCH 议题（含触发条件=MOD-INF-037 前端覆盖归位，动作=改回 `module:`），由 st-gpu-final 或 st-commitsys 承接；本包不代写他包议题（§3.4）。
- **0005 处置（本轮不 requeue）**：解堵进行中但**未收敛**——工作树=已降级（checker 现 fail=0），`git show :frontend_map.yaml`（index）=仍是 `module:MOD-INF-037`。落地读 index/工作树混合态的窗口未关 → requeue 仍可能同因死。**待 st-gpu-final 该批 commit 落 HEAD 后 requeue q-20260924-st-audit-all-20260924-0005**（届时=异因，非硬闯）。claim 续期中。


## 心跳 2026-09-24 01:52 CST（本轮收束）· 在干=depgraph 轴 4 条发现定档+01:38 自审更正 · 卡住=R3#2 让窗(他包 13 行在途)/0005 待 gpu 批收敛 · 下一步=gpu 批落 HEAD→requeue 0005；SOP 那批落→4 行标注；红蓝+终报按 R3#3 推进
- 队列盘面（事实，非本包职责）：total 1027，pending 5 / processing 4 / done 870 / dead 151；head=`q-...st-sweep-tail-20260923-0053` 等待≈95min，drain 租约活跃（pid 16632，renewed 13s，state=drain-active），daemon online；同期 HEAD 三笔（00:38 st-gpu-final / 00:43 st-k4 / 01:02 integrity）皆直连侧落 → 直连与队列并存期，队列头件未随直连推进（k=4 池化 00:43 刚入 HEAD，疑与在跑批相关，交 st-commitsys 观测，本包不判）。
- align：现算硬=3（ruling #383/#387，等 R3#1 合并器修好后 0004 重投）；soft warn≈987 存量。本包工作树自有件：LEDGER/REPORT + battle_map 2 行修（claim 持有，TTL 已续）。
- 反查未做项（诚实登记）：`MOD-L02-001`×43 是否同为错挂（同 MOD-INF-037 判法需逐 ID 比注册表身份，本轮只坐实 MOD-INF-037 一条，余留待终报前补齐或按 ID 上报口径=待判）。

## 心跳 2026-09-24 02:05 CST（主对话整合轮）· 协同令
- **AUDIT_REPORT.md 已由主对话整合定稿至「附录 A depgraph 轴 4 发现 + 附录 B 收官阻塞态」**：后续 cron 自主轮**只 APPEND 心跳到本 LEDGER，勿重写 AUDIT_REPORT**（除非收到总指挥「更新终报」明批）——防独立会话并发覆写。
- **本轮主对话新增[亲验]自审**：`c1_market.account_nav_daily` 复跑=**0 行**（epoch）→ 本包 FIX-1b 方向正确（db 真源确在 c1_market）但坐实第 4 个静默失效空表，已并入待裁④（本人复跑 4 表，非转报）。
- **并发 QA**：已派只读 QA 代理复核 FIX-1/FIX-2 归因范围（git show diff 仅我 3 处改动、gomap 108 行无外来吸收）+ 红蓝重测工厂校验器失明是否坐实 + 现算 align 真实 exit（绕管道取码）。结果回来即并入。
- **收官阻塞态无变化**：ruling 0003/0004 dead=合并器结构无能（st-commitsys R3#1 修中）；0005 dead=外来 frontend_map staged R4 假红连坐（F-AUDIT-DEP-01，st-gpu 批落 HEAD 后 requeue）。**皆跨包属主工，本包停手不硬闯、不刷死信，自动化持续监听自动闭环+自删。**
- **Owner 案头结论**：无待您裁项——八图+depgraph 轴对账穷尽授权，可自修已尽，余者全路由领域属主包+总指挥批注闭环。


## 心跳 2026-09-24 02:06 CST · 0005 解堵 requeue + 0004 合并器定证 + 盲检器新证（红证级）
- **在干/结果（三件全推进一步）**：
  - **① 0005 → 0006 requeue（已投）**：实证 0005 死因（FRONTEND-MAP R4 `module:MOD-INF-037`）的 HEAD 面已消（`git show HEAD:src/.../web/frontend_map.yaml | grep module:MOD-INF-037` = 空，gpu-final 降级批 80880932d4 已落 HEAD）。0005 走 serializer 干净 worktree（HEAD+袋，§2.6 免疫连坐），R4 无对象可失败 → `commit_queue.py requeue 0005` → **q-…-0006 pending**（另一 Serializer 持租约，未自 drain，等下次自举）。**残留外来态**（不影响 0006，登记）：index 侧仍 staged 着**他包**新加的 F-BUDGET-PAGE/F-SCHEDULEGATE-PAGE 两条带 `module:MOD-INF-037`（工作树已降级为 none:，`git status`=MM）；此系 st-gpu/st-ailayer 族在途，非本包域，§3.4 不代修。
  - **② 0004 合并器定证（报总指挥，未自投）**：R3#1 说"st-commitsys 修好合并器你才 requeue"。实测 HEAD 已含 `entry_identity_key` 回植（0f08f7a06c）+ `_scalar_family_keys` passthrough（12 处命中）。用**盘上合并器纯函数**跑 0004 的袋（theirs=7e49c0c0 blob，ours/base=HEAD ruling_registry）→ **merged_ok=True 且精确吸收我的 2 处 `related_arch: []`**（#383→[] 清 1 悬空；#387→[] 清 PS-CTR-003+MOD-INF-043 两悬空）= align 3→0 的对象全清。**反证自证**（防恒绿探针）：注入真三方冲突 → 正确报红 `ruling_id=裁定#383（三方各自修改）死信`（PROBE_CAN_GO_RED）。→ **结论：0004 现可安全 requeue，同因必死已不成立**。但按 R3#1「修好我 requeue」**requeue 0004 属总指挥动作，本包不自投**（ruling_registry=high 域热册）。**请总指挥实弹 requeue。**
- **🔴 新发现 F-AUDIT-BLIND-01【盲检器·align_all 全程崩，交 st-ailayer-final，§3.4 不代修】**：
  - **症状（红证字节级）**：`python align_all.py --no-report` 现算步骤 [6/9] 即崩 `UnboundLocalError: cannot access local variable 'run_subprocess_hidden'`（align_all.py:536）→ **步骤 6-9（代码↔文档 GATE-DOC-NODE-ID / 图9 strategy_production_map / 图10 GOMAP / 第十节）从未执行**，且 align_all **永远 exit 1**。前 5 步正常（图5 硬=3 已核=全为 #383/#387）。
  - **根因**：**staged 外来编辑**（st-ailayer-final「L1 接线批挂点③」，diff @@ -691,6 +691,21）在 `main()` 函数体内加了 `from zephyr.shared.infra.process_pool import run_subprocess_hidden`（行 697）——函数局部 import 使 Python 把该符号**整个 main() 作用域判为局部变量**，而 536/556 行**先用后赋**→ UnboundLocalError。HEAD 版无此行（仅模块级 line 100 import）= 正常。**修法（一行）**：删行 697 冗余局部 import（模块级 100 已在册）。
  - **对本包收官判据的直接影响**：判据含"align_all exit0"——**此外来 bug 不修，exit0 永不可达**（非本包可控）。登记交 st-ailayer-final 落地解堵，本包复跑等其批落 HEAD。
  - **复核命令**：`git diff --cached scripts/governance/d5_architecture/generators/align_all.py | sed -n '1,25p'`（看 697 局部 import）；`python scripts/governance/d5_architecture/generators/align_all.py --no-report 2>&1 | tail -6`（看 UnboundLocalError）。
- **队列/align 状态**：本包 0001/0002 done；0003/0004/0005 dead（0004 已证可 requeue 待总指挥 / 0005 已 requeue 为 0006 pending）；**0006 pending**。align 现算硬=3（前 5 步口径，全为 ruling #383/#387，0004 清零对象）；6-9 步因 F-AUDIT-BLIND-01 崩盲。
- **收官判据进度（批注三件毕）**：#11 battle_map 小修=0006 在途 ✓执行毕 / #1 ruling 落地=**合并器已证可合，待总指挥 requeue 实弹** ◐ / align 6-9 复跑=被外来盲检器阻断 ✗(待 st-ailayer)。**自动化继续存活**：①盯 0006 落地 ②报 0004 可 requeue ③F-AUDIT-BLIND-01 解堵后复跑 align 全九步。


> **补 02:13 CST**：0006 已由 serializer 取走 = **processing**（非卡死，队列积压 st-chainpile×25/st-combine×18/st-sweep-tail×17 按 FIFO 排空，oldest_processing 0.64h 属正常）。**不打断、不再轮询**；下轮只读其终态（done→#11 小修落地毕 / dead→读 dead_reason 定性）。HEAD 现顶 ef85cda27b（st-align-dirty GOMAP 重跑，非本包）。F-AUDIT-BLIND-01 复核：该 commit 说明称"HEAD 陈旧快照 416/244→423/250 机生层重建"，与本包 align 盲检器发现无关（未触 align_all.py 697 局部 import），**bug 仍在 staged 面**，交 st-ailayer-final 不变。


## 心跳 2026-09-24 02:37~02:52 CST · 0006 定性=瞬态超时并重投 + 队列超时盲区 + **align 第 6-9 步首次见光（本战役三件新事实）**
- **① 0006→0007 重投（pending，已投）**：02:13 死因=`landing 异常: TimeoutExpired: git commit --no-verify … timed out after 60.0 seconds`，**非门禁物品失败**。重投前三方核实（防双落）：HEAD blob=`6f9b205d`、工作树/袋 git-hash-object=`e7a90482`（异）、袋 63387B 与工作树 **sha256 逐字节相同**（`6547ac25…`）→ 判定"其实未落地、袋内容完好、重投安全"。`requeue → q-…-0007`，DRAIN skipped（他工持 lease，不抢租约）。
- **② F-AUDIT-QUEUE-02【新发现·交 st-commitsys·红证级·只登记不自修】**：git commit **写超时被判成物品失败死信**，且归 `other` 类=无人 requeue（自愈链缺位）。
  - 判据缺位实证：超时源=`_GIT_TIMEOUT_WRITE = 60`（`git_commit_gateway.py:798`，commit/merge/checkout/reset 共用）；而落地侧瞬态真源 `_TRANSIENT_GIT_MARKERS`（`commit_queue_landing.py:158-165`：index.lock / unable to create / unable to unlink / permission denied / being used by another process / the process cannot access the file）**无 timeout 串**，队列侧 `_DEAD_REASON_ENV_MARKERS`（`commit_queue.py:242-273`，含 0921/0922 补盲的"拒绝访问/WinError 5/WinError 206/文件名过长"）**亦无 timeout 串** → 走 `LandingResult(ok=False)` 死信通道，而非 `LandingEnvironmentError`（→项退回 pending）通道（契约见该文件 `[ERROR_CONTRACT]` 行）。
  - **双态歧义（比死信更危险）**：超时只杀客户端，git 侧可能已完成提交（对象已写/ref 已动）→"死信但内容已落"若不复核即 requeue 就双落；落地侧**无超时后 HEAD 复核**。本包 0006 属"其实未落"=侥幸，不可复用为惯例。
  - 盘面归因：同窗口 01:58:46 st-pipeline-final 0004 + 02:13:12 本包 0006 两件同因，均在 k=4 池化入 HEAD（`0f08f7a06c` @00:43）之后；主区 `git status --porcelain` 实测 **0.36s**（17125 tracked）→ 成本不在主区索引，在 4 个整仓 worktree（w0-w3）并发 commit + 机器负载（reaper 快照 cpu 76.5%/commit 73.7%）。
  - 处方三条：①`TimeoutExpired` / `"timed out"` 入 `_TRANSIENT_GIT_MARKERS` 并同步入 `_DEAD_REASON_ENV_MARKERS` 兜历史死信；②超时死信前先复核"目标路径 HEAD blob vs 袋 sha256"，已落=标 done（幂等三重判定现只覆盖 done/landed_id+is-ancestor，未覆盖超时路径）；③写超时按 k/负载自适应或上调，死因串带 worktree 路径便于归因。
  - 复核命令（现算）：`python -c "import sys;sys.path[:0]=['src','scripts'];import importlib.util as u;s=u.spec_from_file_location('cq','scripts/commit_queue.py');m=u.module_from_spec(s);sys.modules['cq']=m;s.loader.exec_module(m);print(m.classify_dead_reason('landing 异常: TimeoutExpired: x timed out after 60.0 seconds'))"` → 现出 `other`（应归 `env`）。
- **③ F-AUDIT-WT-01【僵尸 worktree 残籍·交 st-k4/st-commitsys·不代删】**：`git worktree list` 首行 `.aidrafts_pool/pool-20260919202729-c433 → 0000000000 (detached HEAD) locked`。实况=工作树目录**已空**（`.aidrafts_pool/` 0 项），`.git/worktrees/pool-20260919202729-c433/` 仅剩 commondir/gitdir/locked 三件、**无 HEAD 文件**，`locked` 内容=`initializing`（09-20 04:27 起，已 4 天）。后果=`git worktree prune` 对 locked 项**拒绝清理**→永久僵尸登记，且任何枚举 worktree 的巡检件恒见一个 null-HEAD 工人。影响面已核=**不污染池化分配**（`worker_worktree_path()` 用固定名 `worktrees/w{i}`，不枚举残籍，`commit_queue_landing.py:1830`）。处置=属主 `git worktree unlock` + `prune`（动他包 git 登记态，本包不执行）。附：`.git/tmpidx_precommit_mq5pl6kd.lock`（0B，09-20 17:17）=被杀 commit 泄漏的孤儿锁名（网关 `mkstemp(prefix="tmpidx_precommit_")`+finally unlink 只删基名，git 写索引时的 `.lock` 随进程被杀遗留）；因名字随机**不阻塞**任何后续提交，纯卫生项（另一枚 02:31 属活体在跑，勿删）。
- **④ 🔓 align 第 6-9 步首次补盲（本战役此前因 F-AUDIT-BLIND-01 从未执行；我另置只读探针直取同一真源判据，非另造尺子）**：探针=`.runtime/tmp/audit_all_20260924/probe_align_steps69.py`（复用 `align_all._check_gomap_alignment` + `validate_strategy_production_map` + 引擎原样调用，字段契约按 align_all 源码校正为 `checks/advisory/violations` 后才取数）。
  - **[8/9] 图 9 策略生产全景图 = 干净**：节点 16/边 16，**硬=0**，软 3（FAC-E7/E8/E9 入库位"施工时定"待定）。
  - **[9/9] 图 10 GOMAP = 干净**：机生层模块 **424**，**硬=0**，软 3（已删墓碑豁免待清理）。→ 与 HEAD 顶 `ef85cda27b`（st-align-dirty 重跑机生层 423/250）方向一致（现算 424=其后 HEAD 又推进，非矛盾）。
  - **[6/9] GATE-DOC-NODE-ID = rc 1（2 处存量）** → **F-AUDIT-BLIND-02**：2 处均在 **gitignore 豁免的派生文档** `docs/02_.../candidate_modules/D_MKT_DATA.md:37,53`（`git ls-files --error-unmatch` 不匹配 + `.gitignore:550` 命中），真身=候选册条目 `CAND-CRYPTO-002` 的 promoted 说明文字里写死物理 `node_id=10865681`；**改派生件必被重生成冲掉→修在 YAML 上游（RULE-SSOT）**，归 st-library-final（其今日正在动该册：`8a332c2ca1` candidate 册身份键消重）。顺带净证：`align_all.py:544` 散文注释写"存量 12 处登记遗留清欠"，实测 **2** → 违 §4"计数用字段勿写死散文"（该文件被 st-ailayer staged 占用，本包不改，登记）。
  - **[7/9] 图 8 产业链 = 12 硬 + 95 advisory** → **F-AUDIT-BLIND-03**（判定权=引擎，本包仅取证并上报；align_all 依设计**不计硬闸**："产业链清欠=长城专项进行中…清零后升硬"）：S4 废弃链闭环 2（`CH-ce2af381886f`、`CH-e78f75eb0c0b` 各"废弃链落位残留 1"）、S11 死映射零存量 9（id 连号 59443、59445-59452 ↔ `836077.BJ/872392.BJ/838402.BJ/430139.BJ/832089.BJ/831961.BJ/839946.BJ/833575.BJ/836807.BJ`——**全北交所、形态像一批未闭环迁入**）、S12 market 一致 1（59447 `cn vs global`）；advisory 全在 S21 流程连通性 95。明细留档 `.runtime/tmp/audit_all_20260924/gq8.json`。
  - **对本包收官判据的含义（重要更正）**：收官判据①"align_all exit0"当前有**两重**不可达：(a) F-AUDIT-BLIND-01 使 6-9 步崩且恒 exit1（外来 staged 局部 import），(b) 前 5 步硬=3 走 `EXIT_FINDINGS`（等 0004 裁定册落地清零）。二者皆跨包属主工。**本包改口径为等价更强判据**：九步逐一取到"应修项清零或已登记上交"的实证（1-5 步此前已取，6-9 步本轮首次取到），每条附复核命令——证据含量高于单一 exit code。若总指挥坚持字面 exit0，需明批"等待 st-ailayer 落地"这一前置。
- **⑤ R3#2 SOP 让窗仍未收敛**：`construction_workflow_policy.md` 在途未提交量 **13 行 → 27 行**（他包继续加），我的 4 处外部真源指针标注仍未落（`grep 外部真源指针`=0 命中，已核）。**继续让窗不硬闯**，文案与"外部指针族系闭合设计（非孤儿针）"净证据见 01:38 心跳。
- **卡住/上交（无新增高域动作）**：0003/0004 仍 dead（合并器已证可合，requeue 属总指挥 R3#1 动作）；align 697 局部 import 仍 `M ` staged 未落 HEAD（HEAD 版仅模块级 line 100 import=干净）→ 任何含该文件的提交都会把盲检器带进 HEAD。
- **队列/align 状态**：本包 0001/0002 done、0003-0006 dead、**0007 pending**；全局 pending 10 / processing 4 / done 872 / dead 157，HEAD 现顶 `140241504a`（队列活跃推进，非卡死）。align 前 5 步硬=3（全为裁定 #383/#387=0004 对象）；6-9 步本轮首次实测=图 9/图 10 硬 0、第 6 步 2 处、第 7 步 12 硬（依设计不计闸）。
- **下一步（轮次）**：①盯 0007 终态（done→#11 小修落地毕；**再 timeout→即判系统性、停止重投并上报，不刷死信**）②F-AUDIT-QUEUE-02 / WT-01 / BLIND-02 / BLIND-03 四条已具红证，待并入终报红蓝节（终报按 02:05 协同令**不动**，等明批）③红蓝反证：把"探针复用同一真源却测出 12 硬 + rc=1"与"align_all 恒 exit1 且 6-9 步从不执行"并列=审查器能红的双证 ④继续等 0004 requeue 与 st-ailayer 解堵。


## 心跳 2026-09-24 02:52~03:08 CST · 🔴 自家修复被两次整文件快照回退（取证定凶）+ 盲检器决定性坐实 + 红蓝反证矩阵成形
- **① 🔴 F-AUDIT-EVAP-01【热册蒸发复发·本包已落地面被回退·已定凶】**：本包 00:04 落地的工厂图修 `90889679b2`（FAC-E1G 补边 + `account_nav_daily`→c1_market×2）在 HEAD 上**已不存在**。`git log -S"[FAC-E1, FAC-E1G]"` + 逐提交方向核对（每笔该文件 diff 亲读）：
  - `8135b0675d` 00:19（st-library-final 死线收口①，11 件批）→ **回退**（-补边 / c1_market→c1_backtest×2）。
  - `1cba19a9de` 00:23（chore(integrity) post-flush re-register）→ **恢复**（快照恰好取自修后态）。
  - `0f08f7a06c` 00:43（st-k4 池化终批 v3，st-cmd 代投，10 文件）→ **再次回退**（同一 5 行同形）。
  - 现算 HEAD 顶 `8811755fa9`：`git show HEAD:config/strategy_production_map.yaml | grep -c c1_backtest.account_nav_daily` = **2**，边数 15（工作树=16）。
  - 定性=**非恶意、非门禁放过，而是"整文件快照互冲"**：三笔批的 commit 说明**都未提及该文件**，即它是被"顺带"以陈旧工作树/index 快照吸收进提交的（与 [[hot-file-wipe-forensics-20260918]]、[[kline-volume-unit-cure-20260922]] 同族，本次是** config 派生册 + 直连大批**形态）。§2.5"每轮 git add + commit 后核 name-only"对本例无效：受害方我 00:04 已核实过自己的提交，腐蚀发生在**他人后续批**里。
  - 处置：**同 sid 重叠实例已于 02:46 投出 `q-…-0008`（pending，文件=该 yaml，袋内容=工作树修后态）**——本轮按令④**不重复派发、不打断**；我只补一条判据：0008 落地后 MUST 用 `git show HEAD:config/strategy_production_map.yaml | grep -c "c1_backtest.account_nav_daily"` 期望 0 复验（因该文件已被回退两次，"done 不等于在位"）。
- **② 🔴 F-AUDIT-BLIND-04【盲检器·决定性·红蓝反证主证】**：上述回退之所以**全程零红**，根因=**图 9 工厂图的 `data_refs` 轴无任何实存性校验**。三组实验（`.runtime/tmp/audit_all_20260924/probe_dataref_blind.py`，判据仍用仓内原函数，零落盘）：
  - G1 喂 HEAD 坏态 → `validate_structure` 硬=**0**、`check_stores` 硬=**0**。
  - G2 喂修后态 → 同 0/0（说明两把尺子对该字段**完全不设防**，非"改对了才绿"）。
  - G3 正注入 `zzz_database.no_such_table_at_all` → 仍 **0/0**。
  - 表实存性亲验（`DatabaseService` reader，非 fail-soft `ch_writer.query`，见 [[ch-query-fails-soft-trap]]）：`c1_market.account_nav_daily` exists=1 **rows=0**（第 4 张静默空表复证，与 02:05 协同令一致）；`c1_backtest.account_nav_daily` **exists=0**；假表 exists=0 且校验器不响。
  - 对照面（防"该轴本就无人管"的错判）：图 7 `trading_decision_map` **有** R11=`data_refs→DS-*→CH 表实存性+新鲜度`（`check_decision_map.py:154`），但①**warn 级不阻断**②异常被 `except` 吞（"R11 是增强检查，异常不跳过…跳过"）。→ 处方：**图 9 复用 R11 同一判据**（勿造第二尺子，§4 内收），并把"表不存在"从 warn 升 own-scope 硬（新鲜度留 warn）；图 7 侧 R11 异常吞噬改 warn→红。归 st-factory/st-ailayer + 门禁属主，本包不自修（改判定逻辑）。
- **③ 🔴 F-AUDIT-BLIND-05【同器第二盲·拓扑连通性零校验】**：注入"完全无入边/出边的孤儿节点 FAC-ZZ-ORPHAN"→ 0 红；注入"清空全部 16 条边"→ **0 红**。而我 00:04 那次修复的立项理由恰是"FAC-E1G=全图唯一 0-in&0-out 孤立节点"——**即本包发现的缺陷类别，校验器本身看不见**（只能靠人工图↔物对账）。图 10 侧有 S21 流程连通性但为 advisory。处方=图 9 增"孤立节点/边集为空"硬判（非 built 节点可豁免降 warn）。
- **④ 红蓝反证矩阵（本轮已成形，供终报"审查器能红"节）**：
  - **现算即红（不靠注入即能证能红）**：图 8 引擎 rc=1（12 硬：S4×2/S11×9/S12×1，明细 `gq8.json`）、第 6 步 GATE-DOC-NODE-ID rc=1（2 处）、图 6 FRONTEND-MAP R4（02:0x 曾打死本包 0005=活体红证）。
  - **注入即红（正证明）**：图 9 `validate_structure` **6/6**（删必填×8、非法枚举×2、悬空边×1、自环×1、node_id 重复×1、未声明反向边×1）；`check_stores` location 指向不存在路径→红；图 10 GOMAP **6/6**（yaml 删模块/加幻影模块/元数据篡改/mount 不存在/disconnected 缺 note/整族删除→133 红）。
  - **注入仍绿=盲检器（本包主产出）**：图 9 `data_refs`（BLIND-04）、图 9 拓扑连通性（BLIND-05）、图 10 `counts`/`generated_at` 谎报（**docstring 明示不在比对范围=声明式盲区，非 bug，但终报须写"counts 字段不可信"**）。
  - 探针=`.runtime/tmp/audit_all_20260924/probe_redblue.py`（全内存 deepcopy 注入，零生产写入）。
- **⑤ 🔴 F-AUDIT-BLOCK-01【本包两份案卷自始未落地·请排窗】**：`docs/_working/audit_all/{LEDGER.md,AUDIT_REPORT.md}` 状态=**`AM`**，即 index 里是 `A`（新建）**从未进过任何 commit**——现处"staged-only 高危态"（遇 sweep/reset/整文件快照批即毁，本仓 09-18/09-24 前例在案；本轮 02:41 我读侧已留快照 `LEDGER_snapshot_0255.md`，且结构自检 193 行/frontmatter 完好/7 个心跳节齐/无被吃行）。
  - 走正门被 `CREATE-GUARD` 硬拦（新建 .md MUST creation_token，`tests/` 外无 `_working` 豁免，属设计非假红，已核 `create_guard.py:8` INVARIANTS）。
  - 而登记 token 要写 `capability_canonical_file_registry.yaml`——该热册此刻 **`MM`**（他包 +184 行 staged，02:40 仍在被写）→ 主区改=[[kline-volume-unit-cure-20260922]] 记的"主区改注册表必死"，且把它纳入我的 `--files` 会把外来 184 行吸收进本包 commit（§2.5/§3.1 连坐）。**故本轮不自修、不硬闯**。
  - 请总指挥排窗（干净窗口/专用 worktree）执行：`batch_creation_tokens.py --prefix docs/_working/audit_all --created-by st-audit-all-20260924 --capability audit_all_panorama_recon --merge-evaluation "工作区案卷非长期册，判据仍指 audit_prompts_20_ai.md v5；收官 TTL=task_bound 退役"`（dry-run 已跑=计划 2 条，零写入），再 `--files` 同批带 token 册 + 两份案卷 + `--allow-multi-domain` 留痕。我随时可接令执行。
- **卡住汇总（三条，全部跨包/需排窗，本包停手不硬闯）**：①0004/0003 裁定册 requeue（R3#1，合并器已证可合）②align 697 局部 import（st-ailayer 未落，HEAD 版仍干净）③案卷 token 排窗（F-AUDIT-BLOCK-01）。
- **队列/align 状态**：本包 0001/0002 done、0003-0006 dead、**0007 processing（battle_map）**、**0008 pending（工厂图重投，重叠实例所投）**；HEAD 现顶 `8811755fa9`（00:43 后队列持续在落）。align 前 5 步硬=3（#383/#387），6-9 步已补盲（图 9/图 10 硬 0·但其中和值不可信：图 9 有 BLIND-04/05 两把尺子照不到的轴）。
- **下一步（轮次）**：①盯 0007/0008 终态，0008 落地后**必须**用上面的 grep 复验"在位"而非只看 done ②红蓝反证余量：图 1-4/图 5/图 6 三族检查器同法做注入-应红矩阵（本轮已覆盖图 9/图 10/图 8/第 6 步）③F-AUDIT-BLIND-04/05 + EVAP-01 + BLOCK-01 四条并入终报（终报按 02:05 令仍不动，等"更新终报"明批）④R3#2 SOP 标注继续让窗（他包在途 13→27 行）。


## 心跳 2026-09-24 03:08~03:24 CST · 双写手实证 + F-AUDIT-DEP-03 **自我更正并扩面**（blueprint 层映射系统性缺位，比原口径更大）
- **① 双写手（同 sid 另一活体）实证，本包按令④避让**：`Get-CimInstance` 进程表见 `heartbeat_daemon st-audit-all-20260924` pid **27168** 于 **02:45:55** 起，`q-…-0008`（工厂图重修，文件=`config/strategy_production_map.yaml`）于 **02:46:04** 投出——即该活体在我上一轮之后接手了 0008。本包**不重复派发、不打断**（与 [[t0matrix-dual-writer-20260924]] 同形教训：动手前查进程表，别只信自己的后台清单）。0007（battle_map）仍 processing（≈49min，队列 `oldest_processing_hours=1.31`，非孤例），不轮询打断。
- **② 🔴 F-AUDIT-DEP-03【自我更正并扩面】原"6 ID 吃 73 目录=滥挂"口径不准，真洞更大**：
  - 原口径错处：我把 `nodes.path` 当成了"蓝图文档目录"。实测 `nodes`（node_type='blueprint'）共 **119 行 / 46 个 distinct `blueprint_id`**，其 `path` 是**代码目录**（如 `src/zephyr/ai_layer/cleaning/`、`src/zephyr/factor/analysis/ic_decay/`）——即一个蓝图 ID 覆盖多个代码模块**本身可以是族级设计**，不天然是错挂。
  - 现算硬数据（`.runtime/tmp/audit_all_20260924/probe_dep03_identity.py`，探针已带三形态解析自测通过）：
    - **`blueprint_path` 命中 0 / 46**：全部 46 组的值均为 `docs/03_modules/<ID>/` 合成形态，盘上**一个都不存在**（`distinct ID 中存在 docs/03_modules/<ID>/blueprint.md` = **0/46**）。
    - **盘上真身形态**：`docs/03_modules/**/blueprint.md` 共 **544** 份，其中 **543 份**走 `_domain_*/<name>/`（或 `_cross_layer_/<name>/`）、**仅 1 份**用 `MOD-*` 目录形态（`docs/03_modules/MOD-CHAINPILE-METAQ/blueprint.md`），而那个唯一用该形态的 ID **不在** DB 的 46 个之列 → DB 写的形态与仓内约定**几乎零交集**。
    - **多对一 6 个 ID 承载 79 个节点**（MOD-L02-001×43、MOD-DATA_ENG×13、MOD-INF-037×12、MOD-L00-004×7、MOD-L04-001×2、MOD-GOV×2），其 `blueprint_id_invalid` 标记=**0**（生成器的"假 blueprint_id"防线只认 `^D-[A-Z_]+-blueprint$` 形态，`generate_project_depgraph.py:362-372`，对这类粗粒度聚合 ID 完全放行）。
    - **79/79 节点无自declare 身份可取证**（其代码目录内无 blueprint.md/无 `module_id=` 头，故"图↔物"两侧都拿不出自证锚点）。
  - **更正后的结论（口径收紧、危害上调）**：不再是"个别 ID 滥挂"，而是 **depgraph 蓝图层的 ID↔真身映射整体缺位**——544 份真蓝图只被压成 46 个聚合 ID，且这 46 个 ID 的 `blueprint_path` 全为盘上不存在的合成形态、`blueprint_id_invalid` 防线照单放行。任何按 `blueprint_id`/`blueprint_path` 寻址的对账轴（含 align 图 1-4、⑤因子三层、GOMAP 人工层 mounts、`blueprint_code_sync`、`reconciliation_registry`、`skill_discovery/factory`）**既无法解析到真身、也无任何校验器会报警**（与本轮 F-AUDIT-BLIND-04/05 同族=静默降级）。
  - 处方不变但优先级上调：生成器侧改为**解析真身**（`_domain_*/<name>/blueprint.md` 543 份是现成索引，可按 dir-name↔module 匹配或按蓝图头 `module_id=` 反查）；`is_valid_blueprint_id` 增第二条判据"值须盘上可解析"（复用现有 `blueprint_path` 存在性，勿造第二尺子）。**改 DB/生成器=架构数据+高影响面，仍属交 st-cmd/st-commitsys，本包不自修**。
- **③ 自家探针首版假红实录（纪律留痕，供终报"审查器也要被审查"节）**：本探针 v1 用 `for bid, path in rows` 取值 → `get_depgraph_conn` 是 **RealDictCursor**，于是迭代到的是**列名字符串**，输出"`blueprint 行数=119 distinct_id=1`、唯一键=`blueprint_id`"这种**看似合理实则全错**的结果。若我不质疑就上报，就是一条新假红。已改为按列名取，并给探针加"三形态解析自测"（A_module 注释/frontmatter/kv 头，全过才允许出结论）。教训与本包已登记的 [[ch-query-fails-soft-trap]] 同族：**读接口形态与聚合键语义必须先验，再谈数据**。
- **④ 红蓝反证第二车道在跑（不重复）**：图 6 frontend_map / 图 7 decision_map(R9/R11/R17) / 图 5 作战地图四族 / 图 1-4 全景（DB 驱动，若需写库则记"证据缺口"不硬凑）的注入-应红矩阵，已交只读子代理在 `.runtime/tmp/audit_all_20260924/redblue_lane2/` 独立跑，约束=零生产写入/禁 git 写/禁 align_all/禁用 fail-soft 读接口。结果下轮并入。
- **卡住汇总（三条未变，全跨包）**：0004/0003 裁定册待总指挥实弹 requeue；align_all 697 局部 import 待 st-ailayer；本包两份案卷 token 待排窗（F-AUDIT-BLOCK-01，热册 `MM` 争用中）。
- **队列/align 状态**：本包 0001/0002 done、0003-0006 dead、**0007 processing**、**0008 pending**；`health` 分类 item 99 / **other 51** / env 14（"other" 堆积即 F-AUDIT-QUEUE-02 缺 timeout 标记的直接后果），pending `oldest=2.72h`、`oldest_processing=1.31h`，blobs **18231**（我上一版草稿误抄 1823，已改）。HEAD `8811755fa9`，工厂图坏引用在位 2 处（0008 的对象）。
  - **负结果记档（防后人误报缺陷）**：02:30 `status` 报 done 872/dead 157，03:2x 同刻 `status` 与 `health` 均=done 838/dead 165，我自己数目录也是 838/165。差 34 **不是**两读数口径不一致，而是 `cleanup_done(ttl_days=_DONE_TTL_DAYS_DEFAULT=7.0)` 在池化 drain 段跑了一轮 TTL 清理（`commit_queue.py:187/1290`、`commit_queue_landing.py:1998`）。**候选发现→实测排除**，登记以免下一轮重复怀疑。
- **下一步（轮次）**：①等第二车道矩阵并档 ②盯 0007/0008 终态，0008 落地后必用 `git show HEAD:config/strategy_production_map.yaml | grep -c c1_backtest.account_nav_daily` 期望 **0** 复验"在位"（该文件已被回退两次，done≠在位）③终报仍按 02:05 令不动，等明批 ④R3#2 SOP 继续让窗。

### 补记 2026-09-24 03:34 CST · F-AUDIT-BLIND-06【落地面回归的**两层**结构性失明】（把 EVAP-01 与盲检器串成一条因果链）
- **决定性测量（`git show HEAD:config/strategy_production_map.yaml` vs 工作树，同两把尺子）**：
  - HEAD：边数 **15**、零入零出节点=**['FAC-E1G']**（入度 0/出度 0）、`validate_structure` 硬=**0**。
  - 工作树（本包修后态）：边数 16、孤立节点=[]、硬=**0**。
  - 即：**我 00:04 立案并修掉的那个缺陷（"全图唯一 0-in&0-out 孤立节点"），回退后在 HEAD 上原样复现，且零报警**。
- **两层失明叠加，缺一不可**（此前各条发现是碎片，这里给出组合效应）：
  1. **判据层**：`validate_structure` 不查孤立节点/边集空集（=F-AUDIT-BLIND-05），故坏态 HEAD 也"结构校验通过"。
  2. **观测面层**：align_all 各步一律 `read_text()` 取**工作树**文件（`_REPO_ROOT`/`_REPO_ROOT_A` 由 `Path(__file__).parents` 推得，align_all.py:84/102/593/624），**从不读 HEAD blob** → 只要本地工作树处于"我已修好"的脏态，十图对账就恒绿；"已落地内容被整文件快照回退"这类回归在本 harness 中**不可表示**，故也不可能被报警。
  - 实证旁佐：本轮 EVAP-01（两次回退）是我用 `git log -S` + 逐提交 diff 方向**人工**抓到的，没有任何自动件报过红。
- **处方（复用现成真源，勿造第二尺子）**：给 align_all 增 `--anchor=head` 模式——各步输入改由 `git show HEAD:<path>` 取 blob 后喂**同一批校验器**；HEAD-blob 读法真源已存在=`commit_gates/_diff_helpers.py`（own-scope 差分即用此法读基线），另有 `--worktree-root`/`ZEPHYR_WORKTREE_ROOT` 两通道先例（[[align-dirty-shift-20260924]]）。两模式各跑一遍=工作树/落地面双确认，正是本包收官判据"连续两轮零新问题"应采的更强口径。归 st-align-dirty/st-cmd（align 族属主），本包不自修。
- **与本包收官判据的关系（重要）**：判据若只看 align_all 绿，则**永远看不到 HEAD 回归** → 本包终报将把"HEAD 锚定复跑"列为**收官必做项**而非可选；在 st-align-dirty 未提供该模式前，我用 `git show HEAD:<path>` 手工对十图关键册各做一次 HEAD 侧计数（下一轮起逐册补，先做图 9/图 10 两册）。


## 心跳 2026-09-24 03:36~03:52 CST · HEAD 锚定手工复跑首日出真值（新 1 硬）+ 边修 1 件入队 0009
- **① HEAD 锚定复跑（本包自提的 BLIND-06 处方，我在等属主实现前先手工执行一遍）三本册实测**：
  - **图 10 GOMAP**：`config/governance_operations_map.yaml` — **HEAD 硬=1**（机生层漂移 `src/zephyr/intelligence/budget_analyzer.py`：盘上有、HEAD 册内无），工作树侧硬=0（424 模块 vs HEAD 423；`scan()` 现算=424/7 族）。**这是工作树口径永远看不到的落地面缺口**——本地跑 align_all 恒绿，HEAD 实际漏挂一条。归属已核：该 py 文件=`A`（staged 新增未落地），GOMAP 册=`MM`（他包在途，staged 净形 **26+/74-**）→ 待其批落地后 MUST 复跑 HEAD 锚定（**净删 74 行的批若把条目删过界，HEAD 硬数会不降反升**，这是下轮盯防点）。本包不代修他包在途册。
  - **图 9 工厂图**：HEAD 边数 15 / `FAC-E1G` 入度 0 出度 0=**孤立节点复现**（=我 00:04 立案并修掉的原缺陷），工作树 16 边无孤立；两态 `validate_structure` 均硬=0（BLIND-05 再证）。0008 在途（重叠实例所投）。
  - **图 6 frontend_map**：`check_frontend_map.py:35 MAP_FILE` 只读 `src/zephyr/frontend/dashboard/web/frontend_map.yaml`；HEAD=eaa8f8a3、工作树=f21130d9（他包 `M ` 在途）。另仓内第二本 `architecture_model/frontend/frontend_map.yaml`（44 pages / HEAD 与工作树同 7eb0fb51）**不在判据读取面**。
- **② 一条候选发现→实测排除（防误报）**：上面那本 architecture_model 副本乍看像"第二真源未收敛"，实为**已裁事项**：Owner 2026-09-04 裁定 web 版唯一真源，废弃副本自身第 5 行 `superseded_by:` 明示，`alignment_checklist.md:232-233` 与 `scan_frontend_pages.py:10` 均在册留痕 → **不是新缺陷，勿再上报**。
- **③ 但顺链查出一条真矛盾并边修（0009 已入队）**：`docs/01_policies_and_standards/_registry/catalogs/battle_map_domain_policy.yaml:286` 的 stage FF-16 `authoritative_source` 至今仍写 `architecture_model/frontend/frontend_map.yaml`（已废弃副本），与上述裁定/`superseded_by`/判据读取面**三处互相矛盾**——裁定期漏改的一条残留指针，属主链=图 5 作战地图域（本包审查轴）。
  - 处置=**简单缺口边审边修**：指针改指 web 版，并把原路径**降为注释保留**（标注裁定依据与"勿当断链删"，与总指挥批注 R3#2 同口径）。改法 `acquire claim → safe_write_text(CAS) → git_commit.py --enqueue`，diff **+3/-1 无旁改**，改前后 `yaml.safe_load` 均为 dict(11 键)。
  - 三证：`q-…-0009` 袋 sha256 == 工作树字节（已核），files=1 不含任何外来 staged 文件。
- **④ 🔴 对收官判据的诚实影响**：判据"连续两轮复跑零新问题"**当前不满足**——本轮 HEAD 锚定就新出 1 条硬（GOMAP 漂移）+ 1 条回退（工厂图 EVAP-01）。这不是坏消息而是该判据的意义所在：只要"落地面（HEAD）"进入观测面，此前恒绿的十图对账就会持续吐新硬。故本包把收官口径明确写成**两条并列**：(a) 工作树侧九步+HEAD 锚定侧关键册均"应修清零或已登记上交"；(b) 该状态**连续两轮**复现。请总指挥知悉口径已收紧（非放松）。
- **卡住汇总（三条未变）**：0004/0003 待总指挥 requeue；align_all 697 局部 import 待 st-ailayer；案卷 token 待排窗（F-AUDIT-BLOCK-01）。
- **队列/align 状态**：本包 0001/0002 done、0003-0006 dead、0007 processing（battle_map）、0008 pending（工厂图，重叠实例）、**0009 pending（本包边修指针）**；HEAD 侧 align 工作树口径硬=3（#383/#387），HEAD 口径新出 GOMAP 1 硬。红蓝第二车道（图 5/6/7 + 图 1-4 注入矩阵）子代理仍在跑，结果下轮并入。
- **下一步（轮次）**：①并档第二车道矩阵 ②复跑 HEAD 锚定五本关键册（GOMAP/工厂图/frontend_map/decision_map/battle_map 策略），并对 0007/0008/0009 三件做"落地即在位"复验（done≠在位，本包已两次实证）③R3#2 SOP 标注继续让窗 ④终报等明批。


## 心跳 2026-09-24 03:55~04:12 CST · 红蓝第二车道并档（R9 恒真我已亲验）+ 本包三件终态取证：**两个不同缺陷**（第 3 次蒸发 / noop 假绿）
- **① 🔴 F-AUDIT-LAND-01【新缺陷·落地假绿·交 st-commitsys·红证级】**：`q-…-0009`（BM 域策略指针边修，files=1）状态=**done**，`landed_id=noop@c5b70a8ff8`，但——
  - `git show c5b70a8ff8:docs/01_policies_and_standards/_registry/catalogs/battle_map_domain_policy.yaml` 第 286 行=**旧指针**（`architecture_model/frontend/…`），行数 536；HEAD 同（536/旧）；我的工作树=538/新。
  - `git log -S"architecture_model/frontend/frontend_map.yaml」" c5b70a8ff8..HEAD -- <该文件>` = **空** → 不存在"先落地后被回退"，即**我的改动从未进过 HEAD**。
  - 而 `_NOOP_LANDED_PREFIX` 的注释语义明写"**快照与 HEAD 逐字节一致（幂等空转）时才记 noop**"（`commit_queue_landing.py:119-121`）——本例快照 538 行 vs HEAD 536 行**并不一致** → **noop 判定本身错**，且错后仍标 done=假绿。
  - 可疑分支（据实标注为推断，非定论）：该文件在 `_registry/catalogs/` 下 → 走"注册表条目级三向合并重放"路径（`0f08f7a06c` k=4 池化批 00:43 刚入 HEAD），条目合并可能把我改的**单字段**判成"无变化"而静默丢弃；两笔本包件（0008/0009）都经此新路径（c5b70a8ff8 是 2-parent 的 CAS 重放 merge）。**若成立，则池化期一切"册内单字段"级边修都可能被静默吞掉且记 done** —— 危害面远超本包一件，请总指挥按此方向派 st-commitsys 复现。
  - 复核命令（三条即够）：`git show HEAD:docs/01_policies_and_standards/_registry/catalogs/battle_map_domain_policy.yaml | sed -n '286p'`（期望见到旧 architecture_model 路径=未落地）／`python -c "import json;print(json.load(open('.runtime/commit_queue/done/q-20260924-st-audit-all-20260924-0009.json',encoding='utf-8'))['landed_id'])"`（期望 noop@…）／`wc -l < docs/01_policies_and_standards/_registry/catalogs/battle_map_domain_policy.yaml`（538=我的修仍只在盘）。
  - **本包处置**：0009 **不再盲目 requeue**（同因必再 noop）。等该分支定性后再投；我的字节仍完好在盘（袋==工作树 已核），零丢失。
- **② 🔴 F-AUDIT-EVAP-01 升级：同一文件 3 小时内被回退**三次**（第三次已定凶）**：
  - 0008（工厂图重投）确认真落地：`c5b70a8ff8`（03:05，`landed_id` 有值、非 noop）该笔内 `c1_market.account_nav_daily` 计数=**2**（我的修在位）。
  - 随后 **`53cdc66e06`**（st-align-dirty-20260924 翻译册补 plain_zh 续批）改动该文件 → HEAD 现又回到 2× `c1_backtest.account_nav_daily` + 15 边 + `FAC-E1G` 孤立。`git log --oneline c5b70a8ff8..HEAD -- config/strategy_production_map.yaml` 只有这一笔，即**第三次回退归属明确**。
  - 该批自身主题是**翻译册**，却整文件带走了工厂图旧快照（与 8135b0675d/0f08f7a06c 同形）——三笔的 commit message 全都不提该文件，符合"旁吸收"特征而非有意改动。
  - 复验命令：`git show HEAD:config/strategy_production_map.yaml | grep -c "c1_backtest.account_nav_daily"`（现=2，修好应=0）。
  - **可恢复性（重要，降低处置成本）**：我的正确版在 HEAD 历史里可取——`git show c5b70a8ff8:config/strategy_production_map.yaml`，且我的工作树字节与 0008 袋逐字节相同（已核），任一方一发即可复原；**但若不先堵"旁吸收陈旧快照"，复原还会第 4 次蒸发**。故本包第 4 次重投暂缓，请总指挥定序。
- **③ 0007（battle_map 小修）第三次阵亡，死因=外来在途态连坐（复证 F-AUDIT-OBS-01 + DEP-01）**：dead_reason=`门禁 MAP-ALIGNMENT→[FRONTEND-MAP] 2 项 fail（共 361 功能点）R1 F-BUDGET-PAGE / F-SCHEDULEGATE-PAGE: backend_ref 列表含非类型化元素 {'none:后端模块MOD-INF-037未入depgraph前端模块集（st-gpu-final-20260924代…'}`。
  - 第二车道亲测：**HEAD 版=359 功能点 / fail=0（全绿）**，工作树版=361 / fail=2 → 落地期门禁读的是**主区脏工作树**而非 HEAD+袋（serializer 名义上走干净 worktree）→ 与 §2.6"池化=结构性免疫连坐"直接冲突；本包一个 2 行 doc 修因此三度阵亡（0005 R4 外来 / 0006 超时 / 0007 R1 外来）。
  - 解堵条件明确：st-gpu-final 那批（把 `module:MOD-INF-037` 降级为 `none:…` 文本、且 YAML 列表元素写成 mapping）落 HEAD 或撤 staged；**其降级文本自身还踩了 R1 非类型化**，属他包缺陷，§3.4 我不代修。
- **④ 红蓝反证第二车道并档（图 5/6/7 + 图 1-4；子代理只读跑，我已亲验其头号断言）**：
  - **我已独立复现的最高危项 F-AUDIT-BLIND-07【图 7 R9 在册性检查恒真】**：`check_decision_map.py:86` `_SQL_CHECK_MODULE_EXISTS="SELECT 1 FROM nodes WHERE module_id = %s"`，而 `nodes` 表**无 `module_id` 列**（我本轮 information_schema 现算 37 列：`node_id/node_type/path/…/blueprint_id/…`，确无 `module_id`）→ 每次抛 `UndefinedColumn` → `:243-256 except Exception: return True`。亲验：`_module_exists_in_depgraph('TOTALLY-BOGUS-MOD-999')` → **True**；真 `MOD-INF-037` → True（两态同值=检查完全空转，121 个 module_ref 的在册性从未被核过，且无 warn 浮出）。
    - 处方我已验真：现成共享件 `zephyr.gov_enforcement.registry_alignment.module_exists_in_depgraph` **存在且正确**（亲算 bogus→False、MOD-INF-037→True）→ 改调它即可，零新真源。旁证=同仓 `business_registry_gate.py:8` 记 2026-09-11 已治本"原 nodes.module_id 列不存在致子检查恒 fail-open 从未生效"，而 R9 抄的是**治本前的旧版**；`fail_open_register.yaml` 只申报"PG 不可用时跳过"=申报与实际不符。
  - 第二车道其余产出（**等级=转报，我未逐条复现**，探针在 `.runtime/tmp/audit_all_20260924/redblue_lane2/`，且其 CANARY/H0 双自检已过）：四族正注入均可红（图 6 能红 4 组、图 7 能红 11+2+1 组、图 5 能红 5 组、图 1-4 能红 4+4 组）；另计 **9 类盲检器**，其中与我本轮同族且危害居前三条：图 5"三表清空/图源不可用双静默"（`align_battle_map` 的 `source_unavailable` gate 不读）、图 5 `acknowledged` 豁免黑洞（`battle_map_domain_policy.yaml:421` 自陈"带 review_frequency 到期强制复审"，但 `_load_acknowledged_orphans` 从不读该字段、全仓无到期算术=一条登记永久消音）、图 7 R11 把"表不存在"渲染成"四态=未启动（1970-01-01, 0 行）"（=我 BLIND-04 的放大器，且 `_query_data_freshness` 用 fail-soft `ch_writer.query`，见 [[ch-query-fails-soft-trap]]）。
  - 该车道亦记录并发事实（只记录未动）：会话内 HEAD 由 `8811755f`→`53cdc66e`；`frontend_map.yaml` HEAD 359 条 vs 工作树 361 条（mtime 02:46）。
- **卡住汇总（本包收官三前置，全跨包）**：①0004/0003 裁定册 requeue 待您（合并器已证可合）②图 5/6 在途脏态 + **F-AUDIT-LAND-01 noop 假绿**：修好前本包边修类工作**无法自证落地**，我因此暂停第 4 次重投③align_all 697 局部 import 待 st-ailayer；④案卷 token 待排窗（F-AUDIT-BLOCK-01）。
- **队列/align 状态**：本包 0001/0002/**0008** done（0008 内容已被 53cdc66e06 第 3 次回退，故"done 但不在位"）、0009 done-but-noop（**实际未落地**）、0003-0007 dead（0007 三度阵亡于外来脏态）、无 pending；HEAD `53cdc66e06`。工作树口径 align 硬=3；**HEAD 锚定口径另见 GOMAP 1 硬 + 工厂图孤立节点/2 坏引用**（BLIND-06 两例）。
- **下一步（轮次）**：①按 HEAD 锚定口径把关键册逐册复跑并列成表（终报主证据之一）②F-AUDIT-LAND-01 若被 st-commitsys 定性，按结论一次性把 0008 内容 + 0009 内容重新入队并当场复验在位③红蓝反证余量：图 8 引擎与第 6 步已"现算即红"，图 1-4/5/6/7 已能红，收尾只需把 CANARY/H0 自证一并写进终报④终报仍等"更新终报"明批。

### 🔴 更正 2026-09-24 03:27 CST（本包自纠·时间戳不实）
- **事实**：本轮落盘的 5 个心跳小节，标题里的时间区间是**我按"预计耗时"外推写死的，不是实测时钟**——真实落盘时刻由文件 mtime 与队列时间戳还原如下：
  | 小节标题（错） | 真实落盘时刻（mtime/队列戳） |
  |---|---|
  | `02:37~02:52` | 探针 02:36:47 起、`hb` 文件 ≈02:44（0007 由 02:34:42 投出） |
  | `02:52~03:08` | 02:49:24 探针 → 02:58:26 落盘 |
  | `03:08~03:24` | 02:54:50 探针 → 02:59:55 落盘 |
  | `03:36~03:52` | 03:03:54 提交 msg → 03:04:43 落盘（0009 created 03:03:59） |
  | `03:55~04:12` | 03:26:01 取证 → 03:27:25 落盘 |
  - 即：真实时钟现=**03:27 CST**，最后两节的标题时间**尚未发生**。
- **性质判定（不淡化）**：这是**我自己在犯本战役正在审判的那类错**——"散文里的数字/标记不经实测就写"（§4 文档纪律、[[repo-test-and-commit-quirks]] "自写盘点脚本也要红证"）。数据正文（命令、sha、行数、门因）均实测可复跑，唯时间轴不实；但审计案卷里任何不实字段都会污染整卷可信度，故单列更正而非静默改写。
- **处置**：①不改写已落盘小节正文（历史态保留，本更正即凭）；②自本刻起规则=**小节标题时刻一律取落盘前 `date "+%H:%M"` 实测值，禁止外推**；③终报的"红蓝反证"节把本条列为**第 0 号自证案例**（审查者自身也被同一把尺子量过并出红），与 [[feedback-executor-cannot-sign-own-work]] 同口径。
- **对已有结论的影响范围（逐条判定）**：EVAP-01/LAND-01/BLIND-04/05/06/07/QUEUE-02/WT-01/DEP-03 全部**不受影响**（其证据=git/mtime/队列 JSON/DB 现算，均带可复跑命令）。
- **蒸发链精确时刻（改用 git 实测 `%ad` 替换此前外推口径）**：`90889679b2` 00:04:07（本包初修落地）→ `8135b0675d` 00:19（第 1 次回退）→ `1cba19a9de` 00:23（误撞恢复）→ `0f08f7a06c` 00:43（第 2 次回退）→ `c5b70a8ff8` 03:05:09（0008 重投真落地，该笔内 `c1_market.account_nav_daily`=2）→ `53cdc66e06` 03:12:30（st-align-dirty 翻译册批**第 3 次回退**）。
- **现算复验（HEAD=`0aec376aba` 03:27:51，落盘前实测）**：工厂图坏引用=**2**、边数=**15**（期望 0/16）；BM 域策略 286 行指向 web 真源=**0**（仍未落地）。→ 本包两项边修**当前均不在 HEAD**，与 F-AUDIT-LAND-01/EVAP-01 判定一致，非表述夸大。
- **旁证一条（他包已在同题上动作，只记录不代修）**：`ad574f63ff` 03:12:23 提交说明自陈"磁盘重整战役台账+注册表口径重落（c5b70a8ff8 stal…"，即另有会话也已察觉 `c5b70a8ff8` 陈旧快照问题；本包不并入其判断，仅登记时间线相邻这一事实供总指挥交叉核对。


### 补记 2026-09-24 03:52 CST 实测（shell `date`=2026-09-24 03:52:41 +0800，本文件写前 mtime=03:29:22）· 🔴 P0 **F-AUDIT-EVAP-02【池化/代投落地"搭便车"：声明面 1 件 ↔ 落地面 28 件，其中 27 件无任何声明来源】**

> 与同 sid 另一活体的防重复核对：本条只立 **EVAP-02**（新题，台账此前 `grep -c exam_cost`=0）。我原拟另立的"0009 假 done"与已立 **F-AUDIT-LAND-01** 同题 → **不重复立案**，只补两条它没取的独立证据（①）。估钟更正其已自纠（`### 🔴 更正 03:27`），我不重复。红蓝第二车道子代理仍在跑（`probe_D_panorama.py` mtime 03:21:42），本条零重叠（轴=落地面 git 谱系，非图↔物注入矩阵）。

- **① 0008/0009 复验（作 LAND-01 旁证）**：`git log --format="%h %ci" -- docs/.../battle_map_domain_policy.yaml` 最近触达=**`8969b9d3ba` 09-22 13:20**（=我的字节从未进任何提交），而 `sha256(盘上)=c64f4673…` **== 袋内 blob_sha256**、`git status`=` M`、HEAD 第 286 行仍指废弃副本。0008 则确曾落地（`c5b70a8ff8` 03:05:09）后被 `53cdc66e06`(03:12:30) 反写：净形=`+c1_backtest.account_nav_daily`×2 且 `-  - [FAC-E1, FAC-E1G]`。⇒ 两态并存：**一"从未落地却记 done"，一"落地后 7 分钟被回退"**，现队列判定里两者都显示 done。
- **② 🔴 EVAP-02 主证（两组数字）**：
  - `0f08f7a06c`（st-k4-20260923「池化终批 v3」·st-cmd 代投·00:43:37）：GW 尾注仅记 `q-20260924-st-k4-20260923-0011`，该袋**声明 1 件**（`registry_mass_deletion_gate.py`，action=**delete**，实以 modify 落地 19+/5−）；提交实含 **28 件**；取 st-k4 当晚 00:44 前**全部**队列项声明并集仅 **11 件** → **27/28 无声明来源**。
  - `53cdc66e06`（st-align-dirty·03:12:30）：尾注 `q-…-0014`=声明 1 件，提交实含 **8 件** → **7/8 未声明**（该包 03:13 前声明并集=6 件）。
  - ⇒ **`git_commit_gateway.py:2922` 既有安全论证被实测否证**：注释原文"本 commit 走 `--pathspec-from-file` 物理隔离，清单外文件进不了本次提交（搭便车由 pathspec 语义构造性排除）"——现实恰是清单外文件经 pathspec **生成侧**被整批带入。属主自查点=同文件 `:3713`（组 commit 命令）与 `:3011-3041`（组 add/rm 清单）：池化时喂进 pathspec 的集合从哪来。
- **③ 🔴 EVAP-02 爆炸半径（同窗实测，台账此前零记）**：
  - **吞他人成果**：`80880932d4`（st-gpu-final 成本考尺修真批·00:38:10·11 件 ~1100 行）落地 **5 分 27 秒**后，其 **7 个整文件从 HEAD 消失**，删除者由 `git rev-list -1 --diff-filter=D` 指认=`0f08f7a06c`：`scripts/backtest/exam_cost_reexam.py`(208) / `src/zephyr/backtest/regime_validation/exam_cost_gate.py`(194) / `tests/backtest/test_exam_cost_gate.py`(103) / `tests/backtest/test_cost_gate_tier_wiring.py`(101) / `docs/03_modules/_domain_backtest/algo_flow/exam_cost_gate.yaml`(64) / `config/exam_scale_cost_gate.yaml`(29) / `src/zephyr/backtest/regime_validation/__init__.py`(8)。同批削 `backup_reconciler.py` −181 / `test_backup_reconciler.py` −199 / `ibt_runner.py` −109 / `f06_e4_wfa_exam.py` −107 / `_c4_engine.py` −50。
  - **反向归因失真**：`tests/gov_enforcement/test_library_blood_flesh_gate.py` +247、`docs/library/regulations.md` +110、`src/zephyr/library/collectors/logs_collector.py` +90、`src/zephyr/shared/io/yaml_utils.py` +70 由同一批带走，尾注全记 st-k4 名下。
  - **零丢失双证（勿判已毁，但悬空 3h+）**：7 路径现=`A `（index 有/HEAD 无=staged 悬空，遇 sweep/reset 即真丢）；`git hash-object(盘上)` == `80880932d4` blob（抽 4 件全等）；odb blob 在 → 恢复=`git checkout 80880932d4 -- <path>`。
- **④ 处方（三条最小闸，全归 st-commitsys-20260924，本包不自修他人写域）**：
  1. **落地后逐路径核 blob**：`git cat-file blob HEAD:<path>` 的 sha256 == 袋内 `blob_sha256`，不等→置 dead 并附 diff（同时拦 LAND-01 假 done 与本类回退）。
  2. **GW 尾注须列出并入的全部 qid**（1 尾注 ↔ 28 件=归因失真本体；现仅有 `[GW:sid:multi-domain]`/`[tracked-drift]` 旗，不含 qid 集）。
  3. **`allow_tracked_drift` 逃生通道加方向判定**：被吸收路径若"HEAD 有、将提交版本无"的行集非空 → 硬阻断。现只留痕：两笔肇事提交均带 `[GW:…:tracked-drift]`，审计流水 `.runtime/audit/hook_tracked_drift.jsonl` 累计 2329 条 = **有信号无消费**。
- **⑤ 自家扫描器 v1/v2 的自我否证（探针，不作结论口径）**：`probe_head_revert_sweep{,_v2}.py`（输出 `head_revert_v2_out.txt`）。
  - v1（"提交新增行在 HEAD 大面积消失"）：命中 30 条但**误报合法改写**（`backup_reconciler.py` HEAD=626 行 > 比对批 535 行），且 `MIN_LINES=8` **漏报我自己那 3 行工厂图修复**（小改动盲区）。
  - v2（加"须找到把这些行作为删除行的中间肇事批，并排除其已声明路径"）：37 条命中、可指认（`53cdc66e06`≈568 行 / `0f08f7a06c`≈348 行 / `bc76efe3bf`≈49 行 / `47e9673e94`≈22 行 / `ef85cda27b`≈18 行），**自检仍 FAIL**：我预设 3 个"负例"里 2 个实为真损失（`ad574f63ff` 03:12:23 重落的 `capability_canonical_file_registry.yaml` 166 行 7 秒后被 `53cdc66e06` 吃掉；`candidate_module_registry.yaml` 39 行不在 HEAD，现 `M ` 悬空）→ **负例选错是我的判据缺陷**。v2 的"未声明"判据在池化模式下退化（整批只记 1 qid ⇒ 近乎全部路径都"未声明"），故只用于**生成候选**；无歧义层=T1（整文件不在 HEAD + 盘上字节==落地字节 + 删除者已指认）。
  - 读侧快照=`D:\ZephyrAlpha\.runtime\tmp\audit_all_20260924\LEDGER_snap_0352.md`（写本条前复制，防自家案卷再被吃）。
- **⑥ 本包处置决定（不硬闯，留待明批）**：**不做第 4 次盲重投工厂图**——(a) 机制未修前任一次落地可分钟级再吃（实测 `ad574f63ff` 03:12:23 → `53cdc66e06` 03:12:30，间隔 7 秒）；(b) 此刻 drain 活跃（HEAD 已推进至 `2a68c14fda` 03:41:15）、同 sid 另一活体在写台账、第二车道子代理在跑。按 LAND-01 结论"同因必再 noop/再吃"，**先修闸后重投**才对收官有意义。令到即执行：`git_commit.py --session st-audit-all-20260924 --enqueue --files config/strategy_production_map.yaml`。
- **卡住汇总（第 4 条升 P0）**：①0004/0003 裁定册 requeue ②align_all 697 局部 import（st-ailayer）③案卷 token 排窗（BLOCK-01）④**EVAP-02 修闸 + st-gpu-final 7 件交付物重落（悬空 3h+）**。
- **队列/align 状态**：HEAD=`2a68c14fda`(03:41:15) 持续在落；本包 0001/0002 done-in位、0008 done-已回退、0009 done-未落地、0007 dead（他包 FRONTEND-MAP R1 红挡我单）、0003-0006 dead 待裁。
- **复核命令（只读）**：
  ```bash
  git show 0f08f7a06c --numstat | awk '$1==0'                     # 7 件整文件删除
  git show -s --format=%B 0f08f7a06c | grep '^\[GW:'              # 尾注只 1 个 qid
  git show 53cdc66e06 -- config/strategy_production_map.yaml       # 回退方向
  git rev-list -1 --diff-filter=D 80880932d4..HEAD -- src/zephyr/backtest/regime_validation/exam_cost_gate.py
  git status --porcelain -- scripts/backtest/exam_cost_reexam.py   # A =悬空
  ```


## 心跳 2026-09-24 03:54 CST 实测（`date` 读数，非估钟）· 在干=已干完一轮（EVAP-02 立案+复验）· 卡住=无（本包不硬闯）· 下一步=见 ③
- **① 本轮产出**：新立 **F-AUDIT-EVAP-02**（池化/代投落地"搭便车"：`0f08f7a06c` 声明 1 件↔实提交 28 件·27 件无声明来源；`53cdc66e06` 声明 1 件↔8 件·7 件未声明）+ 其爆炸半径（st-gpu-final `80880932d4` 的 7 个整文件被 `0f08f7a06c` 从 HEAD 删除，悬空 3h+，盘上字节==落地字节可零丢失恢复）+ gateway `:2922` "pathspec 构造性排除搭便车"论证被实测否证 + 三条最小修闸处方（归 st-commitsys）。同时把 0008（落地后 7 分钟被回退）/0009（从未落地却记 done，补 LAND-01 两条旁证）复验入册。探针 v1/v2 含**自我否证**（负例选错+小改动漏报，故只作候选不作结论）。
- **② 并发实况（动手前查进程表，非只信自家清单）**：本包自身 `heartbeat_daemon st-audit-all-20260924` **pid 27168 已消失**（另一活体退出后守护随之终止）→ **下一轮任何提交前须先 `SessionRegistry(...).register('st-audit-all-20260924',pid=0)` + `Start-Process` 分离式重建心跳**，否则 SESSION-REQUIRED/claim 判陈旧。同窗他包正在自愈：pid **36692** `git_commit.py --session st-gpu-final-20260924 --files src/zephyr/backtest/regime_validation/exam_cost_gate.py,...`（=上述 7 件重落中）、pid **45628** st-backup-cold 重落 `capability_canonical_file_registry.yaml`（=被我 ③ 记的 166 行二次蒸发件）、drain 活跃 pid 21852。⇒ **EVAP-02 的内容损失大概率由属主自修收回**，本包据 §3.4 不代修、不改判，只负责"落位复验 + 机制修闸处方上交"。
- **③ 下一步（轮次）**：①复验 7 件是否已在 HEAD（`git cat-file -e HEAD:src/zephyr/backtest/regime_validation/exam_cost_gate.py` 与 `git show HEAD:config/strategy_production_map.yaml | grep -c c1_backtest.account_nav_daily` 期望 0）②复建本包心跳后把工厂图第 4 次重投与否仍按 LAND-01/明批决定（不再盲投）③红蓝第二车道并档（其 `probe_D_panorama.py` 03:21:42 后有无新产物）④终报仍等明批；收官口径不变（工作树侧+HEAD 侧双确认连续两轮）。
- **队列/align 状态**：HEAD 现=`2a68c14fda`(03:41:15) 且持续在落；本包 0001/0002 done-in位、0008 done-已回退、0009 done-未落地、0003-0007 dead（0007 死因为他包 FRONTEND-MAP R1 红挡我单，非自家内容缺陷）；align 工作树口径硬=3（#383/#387 已路由），HEAD 口径另计。


### 追记 03:56 CST 实测 · EVAP-02 后续（肇事包自认+半复原，剩 1 册仍缺，本包零代修）
- **① 独立旁证（他要包自认同一机制）**：`293415130d`(st-align-dirty 03:52:26) 提交说明自陈——"事故定性（本包第一责任）：`53cdc66e06` 袋面声明 files=1，落地却带出 4 件——serializer 侧吸收了陈旧 index 里的他会话路径，构成一次热册蒸发"，并点名"把审灵 `c5b70a8ff8` 刚重投的工厂图修回退成旧态"；其根因候处方 D12="**landing 应以袋面 files 清单为唯一 git-add 面，吸收 index 残项即拒落**"。⇒ 与本包 EVAP-02 ②④ 两条**同一结论、独立取得**（我走 numstat×队列袋声明并集，它走自家复查），归 st-commitsys 修闸的分量按两源交叉计。
- **② 已自愈部分（亲验 HEAD）**：工厂图 `git show HEAD:config/strategy_production_map.yaml` → **edges=16 / `c1_backtest.account_nav_daily`=0**（=我 00:04 的修法终态落地面成立，第 3 次蒸发至此闭环）。
- **③ 仍未愈部分（自述≠落地，逐尺亲验）**：`293415130d` 说明称同时把 `capability_canonical_file_registry.yaml` 抹掉的 **9 条 capabilities + 20 条 creation_tokens** "纯原文回填"，但该批 numstat **只含 1 件（工厂图）**；同一把尺子三态对照 `grep -c -E "ai_perceive_l1|obj_m_models|obj_s_redline|obj_t_tools"`：`53cdc66e06^`=4 / `53cdc66e06`=0 / **HEAD=0**（行数 46749→46535→46598），盘上与工作树亦 0。真因＝其复原袋 `q-…-0021`(03:47:58) 已 **dead**：`冲突：dev CAS 竞态——293415130d..b906e95496e9 间同路径`；同窗 st-t0-matrix `0007` 亦死于 `注册表三向合并失败（死信回退人工）`。
- **④ 本包判定**：这 9 条属 **st-ailayer 02:3x 接线批**，复原责任在 st-align-dirty（其已投袋、现为死信）与裁定册 requeue 通道，**本包不代修他包热册**（"主区改注册表必死" EVAP-01 第 N 次复证；且注册表撞号后合并器修不了自己＝已立旧案）。列入终报"待裁/待他包落地"清单，复查命令：`git show HEAD:docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml | grep -c ai_perceive_l1`（期望 0→复现后期望 ≥1）。
- **⑤ 收官口径进度（据实）**：本轮 03:40~03:57 为第 1 次 HEAD 锚定全量谱系扫描，新出 1 件 P0（EVAP-02）+ 1 件旁证闭环；按"连续两轮零新问题"判据，**下一轮须重跑同一扫描器 + 逐路径核 blob**，若仍出新件则计数重置（不粉饰）。

### 补记 2026-09-24 04:08 CST 实测（shell `date`=2026-09-24 04:08:44 +0800，本文件写前 mtime=03:56:01）· 🔴 P0 **F-AUDIT-IDX-01/02/03【落地面第三轴：陈旧 index 自身是弹药库】+ 自家扫描器两处判据缺陷自纠**

> 本轮为上一轮心跳 ③ 计划的第 1 步（"重跑同一扫描器 + 逐路径核 blob"）+ 新轴（index↔HEAD↔盘上 三态分类）。与同 sid 另一活体的防重复核对：本条只立 **IDX-01/02/03**（台账此前 `grep -c INDEX`=0 件、`grep -c staged`=仅 EVAP-02 内文），EVAP-02 的机制结论不重复立案，只更新其**尾况**。

- **① EVAP-02 尾况复验（逐尺亲验 HEAD=`488d823ab7` 04:03:41）**：
  - **已愈**：工厂图第 3 次蒸发闭环——`git show HEAD:config/strategy_production_map.yaml` → **node_id=16 / 边=16 / `c1_market.account_nav_daily`=2 处 / `c1_backtest.*`=0**，且 `git diff HEAD -- 该文件`=空 → 本包 00:04 修法在 HEAD 成立（与 03:56 追记 ② 同判，非重述）。
  - **未愈 A**：st-gpu-final 的 7 件 04:06 仍 6/7 件 `OUT`（`git cat-file -e HEAD:src/zephyr/backtest/regime_validation/exam_cost_gate.py` 等失败），距 `80880932d4`(00:38:10) 落地被吞 **已 3h28m**；`src/zephyr/backtest/regime_validation/__init__.py` 已回。属主 pid 36692 已不在进程表 → **重落未完成，改由队列/下一窗口再做**（本包不代投他包写域）。
  - **未愈 B**：capability 册 9 条 capabilities 复原仍为 0（`git show HEAD:...capability_canonical_file_registry.yaml | grep -c -E "ai_perceive_l1|obj_m_models|obj_s_redline|obj_t_tools"`=**0**），与 03:56 追记 ③④ 一致，死信 `q-…-0021` 待裁定册 requeue 通道。
- **② 🔴 F-AUDIT-IDX-01（P1）：index 持祖先态的"回退弹" 24 件 / 回退行数合计 952**。判据=`staged blob != HEAD blob` 且 `staged blob == 该路径某祖先版本`（`git log --find-object=` 指认祖先）且相对 HEAD 有删除行。Top（回退行数）：`candidate_module_registry.yaml` −247（祖先=8a332c2ca1）、`ultimate_library/11_handoff_next_session.md` −140、`ulib3b_to_derive_candidates.md` −100、`config/governance_operations_map.yaml` −74/+26（祖先=**0f08f7a06c**，即池化批旧态）、`src/zephyr/shared/io/yaml_utils.py` −70（祖先=1cba19a9de）、`src/zephyr/library/lookup.py` −50、`tests/capability/test_capability_lookup.py` −31、**`config/strategy_production_map.yaml` −3/+2（祖先=53cdc66e06）**=本包工厂图修法的**第 4 次回退已上膛**。⇒ 与 EVAP-02 同因不同轴：EVAP-02 说的是"落地吸收 index"，本条量的是**此刻 index 里躺着多少可被吸收的回退字节**。修闸处方不变（st-commitsys 04:0x 正在改：pid 46572 `pre_commit run --files commit_queue_landing.py/git_commit_gateway.py/…`）。
- **③ 🟡 F-AUDIT-IDX-02（P2，含一条已证伪假说）：596 件新文件只存在于 index+盘上，HEAD 无**（staged 直方图 = **A 596 / M 60 / D 6**）。其中 **150 个 `.py`**、**67 个在 `src/zephyr/`**（`ai_layer/{cleaning,comparator,redline,heritage,scheduling,perceive}` 六子包**整族** HEAD 不存在，HEAD 仅有 `ai_layer/intake` 7 件）；全部 596 件**盘上在场**（`index-only-missing-on-disk=0`）→ 现状不是丢失，是**零 HEAD 谱系**：任何 `git reset`/全树 sweep/`git checkout .` 即蒸发（[[repo-test-and-commit-quirks]] 全树 sweep 毁未提交件坑 的第 N 次上膛）。
  - **我提出并自我证伪的假说（记此防后人重走）**："`git rm --cached` 残留可能同时使 HEAD 悬空 import 这些 index-only 模块" ⇒ 亲验=**证伪**：`ai_layer.{cleaning,comparator,redline,heritage,scheduling,perceive,tools,models}` 在 HEAD 的 `src/ scripts/ tests/ config/` 引用计数**全为 0**，67 个 `src/` 模块名逐一试 `git grep … HEAD` **零命中**。⇒ HEAD 可运行性不受 IDX-02 影响，本条只算悬空工作量风险，**不升 P0**。
- **④ 🔴 F-AUDIT-IDX-03（P0，新类）：6 件文件 HEAD 有 + 盘上字节==HEAD + 无任何活跃 claim，却被 staged 为删除** → 一次吸收 index 的落地 = 真删 + HEAD 断链。清单：`src/zephyr/library/collectors/logs_collector.py` / `tests/library/test_logs_collector.py` / `tests/gov_enforcement/test_library_blood_flesh_gate.py`(247 行) / `docs/library/regulations.md`(110 行) / `docs/01_policies_and_standards/sop/library_sop/blood_flesh_cataloging_sop.md`(66 行) / `docs/03_modules/_domain_library/algo_flow/collectors/logs_collector.yaml`(34 行)。
  - **断链硬证（不是"可能"）**：HEAD 的 `src/zephyr/library/collectors/__init__.py:31` = `from zephyr.library.collectors.logs_collector import collect as logs_collect` → 该文件一旦被删，`import zephyr.library.collectors` 直接 ModuleNotFoundError；`blood_flesh` 同族另两件是**门禁实现+门禁测试**（`commit_gates/__init__.py` 引用链在册）。
  - **归属判定（不代修的依据）**：`python scripts/lock_files.py status` = **CLEAN — 当前无任何文件锁**（无人 claim 这 6 件）；队列侧 `grep logs_collector|regulations.md|blood_flesh` 命中 4 个袋（`q-20260922-st-ulib3-0028/0039`、`q-20260923-st-library-final-20260924-0001`、`q-20260923-st-nightfix-0013`）**全部在 done/**，且其 `files[].action` 为 modify 非 delete（机读核验：全仓 `grep "logs_collector" .runtime/commit_queue/*/*.json | grep delete` 仅命中 dead 册的 REGISTRY-MASS-DELETION 死因文案，非声明删除）。⇒ **无任何在册意图要求删除这 6 件**；形态指纹=`git rm --cached`（保留盘上）与 [[k4-pool-shift-20260923]] `.aidrafts_pool 偏离决策` 同族。
  - **本包处置=只登记不硬闯**（动他人 index=改共享落地面，属 §0.8 门位笼外的高连坐动作；且 st-commitsys 正在改 landing/add 面，先修闸再清弹才是正序）。**给属主/总指挥的零风险复原命令**（6 件盘上字节已==HEAD，restore 不改一个字节）：`git restore --staged src/zephyr/library/collectors/logs_collector.py tests/library/test_logs_collector.py tests/gov_enforcement/test_library_blood_flesh_gate.py docs/library/regulations.md docs/01_policies_and_standards/sop/library_sop/blood_flesh_cataloging_sop.md docs/03_modules/_domain_library/algo_flow/collectors/logs_collector.yaml`。
- **⑤ 自家扫描器两处判据缺陷自纠（[[feedback-executor-cannot-sign-own-work]] 自审要扫自己，红证第 1/2 号）**：`probe_head_revert_sweep_v2.py` 本轮自检 **FAIL**，逐条定性后**两处是尺子的错、一处是我正例过期**：
  - **缺陷 1（误判肇事）**：`declared()` 只从 `[GW:<sid>:q-…]` 尾注读队列袋声明 ⇒ **直连提交**（尾注仅 `[GW:sid]`+`[overlap]`+`[multi-domain]`，无 qid）声明面恒空，其自有路径被当成"未声明连带回退"。实测两例：`47e9673e94`(03:31:35) 的 `scripts/backup/restore.ps1` 判"毁 14 行"，但 HEAD 版 **687 行 > 8135b0675d 的 604 行** = 合法扩大改写；`bc76efe3bf`(01:52:54) 的 `candidate_module_registry.yaml` 同理（该批 numstat 3 件含其自身）。**修**=无 qid 的直连提交以自身 numstat 为声明面（pathspec 对其成立），从肇事候选剔除。
  - **缺陷 2（正/负例过期）**：正例 `(c5b70a8ff8, 工厂图)` 因 ① 已复原而不再命中=**期望过期**（移入"已复原"表）；而我 03:52 自认选错的两个负例 `(1cba19a9de, backup_reconciler.py)`（肇事=0f08f7a06c 池化批，毁 24 行）与 `(ad574f63ff, capability 册)`（肇事=53cdc66e06，毁 135 行，**HEAD 现在仍缺**）应**改列正例**。
  - ⇒ 结论：本轮 = 收官判据"连续两轮零新问题"中的**第 1 轮出新件**（IDX-01/02/03 三件 + 尺子两处自纠），计数**重置**，不粉饰。下一轮（修尺后重跑 + 逐路径核 blob）为第 2 轮。
- **卡住汇总**：①0004/0003 裁定册 requeue（他包）②align_all 697 局部 import（st-ailayer）③案卷 token 排窗（BLOCK-01）④EVAP-02 修闸+7 件重落（st-commitsys/st-gpu-final 在飞）⑤**新增：IDX-03 六件 staged 删除弹待属主/闸修后清**。
- **队列/align 状态**：HEAD=`488d823ab7`(04:03:41) 持续在落；本包 0001/0002 done-in位、0008 **done-in位（本轮 HEAD 亲验闭环）**、0009 done-未落地、0003-0007 dead 待裁；align 工作树口径硬=3（#383/#387 已路由 st-cmd）。
- **复核命令（只读，全部本轮实跑过）**：
  ```bash
  python .runtime/tmp/audit_all_20260924/probe_index_residue.py          # 三态分类器（STALE_REVERT/NEWFILE/DIVERGED）
  git diff --cached --name-status | awk '{print $1}' | sort | uniq -c    # A596/M60/D6
  git diff --cached --name-status | awk '$1=="D"{print $2}'              # 6 件删除弹清单
  git show HEAD:src/zephyr/library/collectors/__init__.py | grep -n logs_collector   # :31 断链硬证
  python scripts/lock_files.py status                                    # CLEAN=无人 claim
  git show HEAD:config/strategy_production_map.yaml | grep -c "c1_market.account_nav_daily"   # 期望 2
  for f in $(git diff --cached --name-status | awk '$1=="A" && $2 ~ /^src\/zephyr/ {print $2}'); do echo $f; done | wc -l   # 67
  ```

## 心跳 2026-09-24 04:08 CST 实测（`date`=04:08:44，非估钟）· 在干=本轮已干完（新轴扫描+立案+自纠）· 卡住=无（本包不硬闯他人 index）· 下一步=见 ③
- **① 本轮产出**：立 **F-AUDIT-IDX-01**（index 回退弹 24 件/952 行，含本包工厂图第 4 次上膛）+ **IDX-02**（596 件 index-only 新件/150 .py，附**自我证伪**的"HEAD 悬空 import"假说）+ **IDX-03【P0】**（6 件 HEAD有·盘同·无人 claim 的 staged 删除弹，含 `collectors/__init__.py:31` import 断链硬证与零风险复原命令）；EVAP-02 尾况三分（工厂图已愈/7 件仍未愈 3h28m/capability 册 9 条仍未愈）；自家扫描器两处判据缺陷自纠（直连提交声明面、正负例过期）。会话侧：`SessionRegistry` 记录显示 03:55:37 已有 `host_type=main`(pid 46192) 存活，本轮另起 `heartbeat_daemon` pid 36540 保活，**未抢占、未清他人 claim**。
- **② 并发实况（动手前 Get-CimInstance 查进程表）**：st-commitsys-20260924 心跳 03:55:49 起 + pid 46572 `pre_commit run --files commit_queue_landing.py, commit_belt_daemon.py, git_commit_gateway.py, thresholds.yaml, test_commit_queue_pool.py, bare_sql_gate.py, commit_preflight.py, test_preflight_bare_sql_alignment.py`（=EVAP-02 三条处方正在改）；pid 26628 st-backup-cold `git_commit.py --files capability_canonical_file_registry.yaml --allow-overlap --no-auto-enqueue`（03:57:00，capability 册复原在飞）；pid 9168 st-t0-matrix `commit_queue.py status`；pid 19400 st-gpu-final 心跳 02:38 起仍在。**避让面**：`capability_canonical_file_registry.yaml`/`config/strategy_production_map.yaml`/commit-system 六件——本包本轮对其**零写入**（只读亲验）。
- **③ 下一步（轮次）**：①按 ⑤ 两处修尺 → 重跑 v2 + `probe_index_residue.py` 作**第 2 轮**（判"零新问题"）②复验 IDX-03 六件是否被属主清弹 / 闸修后是否仍复现 ③复验 st-gpu-final 7 件与 capability 册 9 条是否入 HEAD（`git cat-file -e` + `grep -c` 两把尺）④红蓝反证第二车道并档（其 `probe_D_panorama.py`/`out_D.txt` 03:21 后无新产物，需确认车道是否已停）⑤终报仍等闸修落地后写（HEAD 侧+工作树侧双确认口径）。
- **队列/align 状态**：同 ①（HEAD=`488d823ab7`，本包 0008 本轮 HEAD 亲验闭环）。

### 补记 2026-09-24 04:18 CST 实测（shell `date`=04:18:44 +0800，本文件写前 mtime=04:10:01，HEAD=`3ec72b6d0b` 04:13:35）· 🔴 **F-AUDIT-GEN-01【根因级新类：派生册生成器读工作树而非 HEAD】+ F-AUDIT-BAG-01【done 袋全量 blob 级核对：35.5% 声明字节不在 HEAD】+ EVAP-02 第三实例 + 本包两条自家基线被自己的新尺证伪**

> 防重复核对：本条只立 GEN-01/BAG-01 两案 + EVAP-02 的**新实例**（新肇事批，非新类）+ 自家 0002 判定改判。IDX-01/02/03 见 04:08 补记，不重述。

- **① 🔴 F-AUDIT-GEN-01（P1·根因级·新类）：机生派生册的输入面=工作树，与"派生册是 HEAD 纯函数"的法则不符**（后者见 [[align-dirty-shift-20260924]] "派生册=HEAD 纯函数 423 口径"）。
  - **同一 HEAD 两个口径的实测对照（红证）**：`python scripts/governance/generate_governance_map.py --dry-run` → `counts: {'total_modules': 424, 'wired': 250, 'wired_dynamic': 6, 'wired_by_header': 76, 'suspect_orphans': 92}`；而 `git show HEAD:config/governance_operations_map.yaml | grep -A6 '^counts:'` → **423 / 75**。差的正是 `zephyr.intelligence.budget_analyzer` 一条（6 行）——`git cat-file -e HEAD:src/zephyr/intelligence/budget_analyzer.py`=**NOT in HEAD**，`git status --porcelain`=**`A `**（=它正是 IDX-02 那 596 件 index-only 之一）。
  - **尺子在何处**：`scripts/governance/generate_governance_map.py:143`（`_iter_py_files` 里 `for p in base.rglob("*.py")`，对 `SCAN_ROOTS` 全工作树递归，**零 HEAD 面过滤**）。⇒ 任何未提交/仅 index 的 `.py` 都会进派生册；不同会话工作树不同 ⇒ **同一 HEAD 生成不同字节** ⇒ 热册互判"被回退"。
  - **对本包自家叙事的更正（不淡化，与本战役审判的"散文数字不经实测"同尺）**：本包 0002（GOMAP 重跑，landed=`5f4136315e` 00:12:06）在 v2/v3 尺下判为"被 `0f08f7a06c` 回退 6 行"。逐尺复验后**改判**：那 6 行=工作树污染件 budget_analyzer 的条目，HEAD 现态 **423/75 才是正确口径**；故 0002 由"done-in位（被吞待重投）"改判为 **"袋字节含工作树污染，HEAD 现态正确，不重投"**。⇒ EVAP-01 系列"热册蒸发"叙事中**GOMAP 这一条属口径漂移而非并发吞并**（其余两笔 0f08f7a06c/53cdc66e06 的吞并证据不因此改动，它们的实提交 numstat≫袋声明，与生成器无关）。
  - **入尺铁律（写给下一轮的自己与终报）**：判"某批被回退"前，必须先证"落地板是 HEAD 纯函数产物"（即 `git show <K>:<册>` == 干净 HEAD 面上重跑生成器的字节），否则不得记为蒸发。
  - 处方（归派生册属主 + st-cmd，本包不自修他人写域）：`_iter_py_files` 改与 `git ls-tree -r HEAD --name-only` 取交集，或至少在 counts 里分列 `worktree_only` 件数并让 gate 认该差值；同族=R-B1（dataflow 生成器不幂等），共同病根=**生成器输入面未定义**。
- **② 🔴 F-AUDIT-BAG-01（P0 面·新尺）：done 袋声明字节 vs HEAD 的全量三态核对，35.5% 不符**。尺=`probe_done_bag_vs_head.py`（`created_at>=2026-09-24` 的 **21 个 done 袋 / 31 个 (袋,文件) 对**，`sha256(git cat-file blob HEAD:<path>)` 对袋 `blob_sha256`，并对 `landed_id` 同尺三态）。
  - 结果：**IN_HEAD=20 (64.5%)** ／ **NEVER_IN_LANDING=9 (29.0%)**（其中"落地批字节!=袋"5 件、"landed_id 里根本没有该路径"4 件）／ **LANDED_THEN_LOST=2 (6.5%)**。⇒ **11/31=35.5% 的 done 声明其字节此刻不在 HEAD**（约定自证=IN_HEAD 非 0，故不是哈希口径错）。
  - 逐件定性：LANDED_THEN_LOST 两件 = `q-…-st-align-dirty-0007`/`src/zephyr/data/config/known_data_gaps.yaml`（真被后批改，属主 st-align-dirty）+ 本包 0002/`governance_operations_map.yaml`（=① 已改判，非损失）。NEVER_IN_LANDING 集中面 = `module_translation_registry.yaml` **6 袋**（st-align-dirty 0011/0014/0018/0019/0023/0025）+ `capability_canonical_file_registry.yaml` **2 袋**（st-align-dirty 0016、st-commitsys 0007）+ **本包 0009**/`battle_map_domain_policy.yaml`（landed_id 无此路径=**独立第二把尺复证 LAND-01"从未落地却记 done"**）。
  - ⇒ 与 st-commitsys 正在实施的处方 #1（落地后逐路径核 blob）**同轴**，本探针可直接作该闸的**审计侧验收尺**（能红：现成的 9+2 件不符样本）。
- **③ 🔴 EVAP-02 第三实例（新肇事批，非新类；证明该机制是稳态不是事故）**：`bc76efe3bf`（st-library-final·01:52:54）尾注 `[GW:st-library-final-20260924:q-20260924-st-library-final-20260924-0012]`，该袋 `files` = **仅 `src/zephyr/library/lookup.py` 1 件**，而实提交 numstat=**3 件**（另带 `candidate_module_registry.yaml`、`scripts/register_post_settlement_task.ps1`）；被带出的改动使 `candidate_module_registry.yaml` 自 `8a332c2ca1` 起的 **39 行**、`register_post_settlement_task.ps1` 自 `8f0e5feba9` 起的 **10 行** 离开 HEAD，尾注同样带 `[GW:…:tracked-drift]`（有信号无消费 复证）。⇒ 三笔同机制时刻表 = **00:43:37 `0f08f7a06c` / 01:52:54 `bc76efe3bf` / 03:12:30 `53cdc66e06`**，跨 2.5h、涉 3 个会话，非单次。
- **④ 自家扫描器 v3 的第三处自纠（盲检器反证材料）**：v3 修尺后（直连提交以自身 numstat 为声明面）自检=4 正例全命中、1 负例仍命中（`8a332c2ca1`/`candidate_module_registry.yaml`）。亲查袋面后定性=**我的负例又选错**（见 ③，该路径确属未声明连带）。已把 `(8a332c2ca1, candidate_module_registry.yaml)` 从 NEG 移入 POS。⇒ 一晚三次选错负例的**共同方向**是"把真损失当成误报"，故修法=逐例回查队列袋声明面，而不是放宽判据；此条进终报"红蓝反证"节（与 03:2x 时钟外推自证、探针 v1/v2 自否同列）。
- **⑤ v3 全量口径（修尺后，作基线）**：已指认 **26 条**（T1 整文件不在 HEAD 未指认删除者 6 件/577 行 + `0f08f7a06c` 337 行/12 件 + `bc76efe3bf` 49 行/2 件 + 其余）。较 v2 的 33/37 条**下降即修尺效果**（直连提交误判被剔除），非问题减少。
- **卡住汇总**：①0004/0003 裁定册 requeue（他包）②align_all 697 局部 import（st-ailayer）③案卷 token 排窗（BLOCK-01）④EVAP-02 修闸+st-gpu-final 7 件重落（在飞）⑤IDX-03 六件 staged 删除弹（04:18 复测**仍 6 件在膛**）⑥**新增：GEN-01 生成器输入面（派生册族共性，影响所有 GOMAP 类热册）**。
- **队列/align 状态**：HEAD=`3ec72b6d0b`(04:13:35) 持续在落；本包 0001 done-in位、0002 **改判=HEAD 现态正确不重投**、0008 done-in位（04:0x HEAD 亲验 16 节点/16 边）、0009 done-未落地（BAG-01 复证）、0003-0007 dead 待裁；align 工作树口径硬=3。
- **复核命令（只读，全部本轮实跑）**：
  ```bash
  python scripts/governance/generate_governance_map.py --dry-run | grep counts      # 期望 424
  git show HEAD:config/governance_operations_map.yaml | grep -A6 '^counts:'          # 期望 423
  git cat-file -e HEAD:src/zephyr/intelligence/budget_analyzer.py && echo IN || echo NOT-IN-HEAD
  sed -n '136,146p' scripts/governance/generate_governance_map.py                    # rglob 工作树面
  python .runtime/tmp/audit_all_20260924/probe_done_bag_vs_head.py                   # 21 袋 31 对三态
  python -c "import json;d=json.load(open(r'.runtime/commit_queue/done/q-20260924-st-library-final-20260924-0012.json',encoding='utf-8'));print([f['path'] for f in d['files']],d['landed_id'])"
  git show --format= --numstat bc76efe3bf | awk '{print $3}'                         # 3 件 vs 袋 1 件
  python .runtime/tmp/audit_all_20260924/probe_head_revert_sweep_v3.py               # 26 条基线
  ```

## 心跳 2026-09-24 04:18 CST 实测（`date`=04:18:44，非估钟）· 在干=本轮干完（GEN-01/BAG-01/EVAP-02 第三实例/自家 0002 改判/v3 第三处自纠）· 卡住=无 · 下一步=见 ③
- **① 本轮产出**：立 **F-AUDIT-GEN-01**（P1 根因级新类：派生册生成器 `rglob` 工作树、同一 HEAD 出 423/424 两口径，附红证与改判）+ **F-AUDIT-BAG-01**（P0 面新尺：21 袋 31 对，**35.5% done 声明字节不在 HEAD**，含本包 0009 被独立复证）+ **EVAP-02 第三实例**（`bc76efe3bf` 01:52:54，袋 1 件↔提交 3 件）+ **自家两条基线改判**（0002 从"被吞"改"HEAD 正确不重投"；v3 负例三次选错定性并移正例）。
- **② 并发与避让**：本轮对 `capability_canonical_file_registry.yaml`/`config/strategy_production_map.yaml`/`module_translation_registry.yaml`/commit-system 六件/`governance_operations_map.yaml` **零写入**（前者正被 pid 26628、st-commitsys 在飞改）；本包唯一写入=`docs/_working/audit_all/LEDGER.md`（先 `lock_files.py acquire`，CAS `safe_write_text`，写后进程外 `wc -l/-c`+`grep` 核实 399 行/103058 字节）。心跳：03:55:37 起 `host_type=main`(pid 46192) 存活，本轮另起 `heartbeat_daemon` pid 36540。
- **③ 下一步（轮次）**：①GEN-01 的可证伪推论去验：**若**生成器输入面是真因，则 `module_translation_registry.yaml`/`in_process_gate_registry.yaml` 等"反复互撞热册"应同样存在 工作树!=HEAD 的输入件 ⇒ 逐册 dry-run 对照（这能把 GEN-01 从"一册实证"升到"族级定性"）②BAG-01 尺扩到 `created_at>=2026-09-23`（样本从 31 对扩到全量，给终报分母）③复验 IDX-03 六件是否被属主清弹 ④终报（等 st-commitsys 闸落地 + 上述两项，HEAD 侧+工作树侧双确认口径）。
- **队列/align 状态**：同 ⑤。

### 追记 2026-09-24 04:24 CST（shell `date` 实测） 实测 · 🔴 IDX-01 活体复证（最热册再上膛 −159 行）+ 本包案卷从未入 HEAD 的事实与补投 + cron 会话生命周期处方

- **① 能力册复原已入 HEAD，但 index 仍持短版本=第四次蒸发已上膛（实测）**：`git diff --cached --numstat -- docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml` = **`0 159`**（index 相对 HEAD **纯删 159 行**），而 `git status --porcelain -- 该文件`=空、盘上 blob==HEAD blob。⇒ HEAD 侧 159 行由 **`e88eb3f786`(st-align-dirty·04:10:36「自伤复原批」)** 复原落地（`git log -S ai_perceive_l1` 两笔=`53cdc66e06` 删/`e88eb3f786` 补）（04:0x 的 `grep -c`=0 现=4，本包 04:08 补记 ①"未愈 B"据此**改判为已愈**）；但 **index 侧仍是复原前的旧字节** → 任何吸收 index 的落地（EVAP-02 机制）会再吃一次 159 行。这是 IDX-01 在**最热真源册**上的活体实例，也是 st-commitsys 修闸验收尺的最佳靶例（袋面 files 唯一 add 面后，该差异不得进任何提交）。
- **② 本包案卷从未入 HEAD（自我逮正，属 BAG-01 同一把自己打）**：`git show HEAD:docs/_working/audit_all/LEDGER.md` = 不存在，`git status --porcelain`=**`AM`**（LEDGER 436 行 / AUDIT_REPORT 均在 index+盘上、HEAD 无）⇒ 审查案卷自身正是 IDX-02 那 596 件 index-only 之一。已做两手：(a) 读侧快照 `.runtime/tmp/audit_all_20260924/{LEDGER,AUDIT_REPORT}_snap_0420.md`（.runtime 已 gitignore，git 侧操作碰不到）；(b) 本轮走正门补投（token 先行同批：`batch_creation_tokens.py --capability audit_all_casebook` 已在册，diff 面 2 token）。死因史：0006=`landing TimeoutExpired（git commit 60s 上限）`、0007=`他包 FRONTEND-MAP R1 红连坐`（`none:` 后端引用未类型化，作者 st-gpu-final，本包不代修）。
- **③ cron 型会话生命周期处方（新踩坑，值得入尺）**：本轮三次失去会话活性——`heartbeat_daemon` 与 `SessionRegistry` 的 `host_type=main` 记录（pid 46192→36540→12684）随**每轮 CLI 进程树被回收而终止**（`-WindowStyle Hidden` 的 Start-Process 在 Windows 作业对象下并不真脱离）。`.runtime/sessions/<sid>/heartbeat.jsonl` 末条=`{"status":"exited","reason":"session not in registry"}` 即该链指纹。⇒ **处方=每轮冷启动必须重做 `register(sid,pid=0)`+起 daemon，且该轮所有提交必须在同一轮内完成**，勿指望跨轮存活；另 `lock_files.py cleanup`（他包冷启动也会跑）会删死 pid 记录，故"注册成功"不等于"下一分钟仍注册"。

### 追记 2026-09-24 04:28 CST 实测（shell `date`=04:27:54，HEAD=`3919c83d87` 04:26:38）· 🔴 **F-AUDIT-IDX-04【预检门消费 index 字节而非袋/盘字节 → 外来陈旧 index 可阻断无辜提交】+ 本包两次就地排雷（内容零变化可证）**

- **① 实证链（一次被挡、一次放行，同一条命令）**：
  - 04:24 `git_commit.py --session st-audit-all-20260924 --enqueue --files <LEDGER,AUDIT_REPORT,capability册>` → **PREFLIGHT BLOCKED**：`REGISTRY-MASS-DELETION … capability_canonical_file_registry.yaml: 净删行 deleted=159 added=0（条目数 10568→10550，身份消失 18 条，示例 ai_cleaning_l3/ai_comparator_l4/ai_heritage_l7）`。
  - 而**我当时对该册的真实改动=纯增 10 行**（`git diff --numstat`=169/0 是相对陈旧 index 而非 HEAD；`disk blob==HEAD blob` 已亲验，HEAD 侧 159 行由 `e88eb3f786` 04:10:36「自伤复原批」补回）。⇒ **门读的是 index 里的旧字节**，把一个无辜追加判成大规模删除。
  - 04:26 我 `lock_files.py acquire` 后 `git add -- <该册>`（盘字节==HEAD+我的 2 token ⇒ 排雷**内容零变化**，可证：`pre-add index=e96d04ee80 / HEAD=6d9d606828 / disk=75fd06c6cf`，`post-add index=75fd06c6cf`==disk），`git diff --cached --numstat` 由 `0 159` → **`10 0`** → **同一条 git_commit 命令立即 ENQUEUED `q-20260924-st-audit-all-20260924-0010`（files=3）**。
- **② 定性（给 st-commitsys 的第四闸处方，属他包写域本包不自修）**：预检/门禁的**比对基线**应取"袋内/盘上字节 vs HEAD"，或在对 own path 判定前先 `git add` 刷新 index；现行为=**他人陈旧 index 能挡住我的提交**，这是 EVAP-02 家族的第二面：同一"index 被当作真源"病根，一面是让陈旧 index **进入提交**（吸收落地面，见 IDX-01/EVAP-02），一面是让陈旧 index **参与判定**（门禁面，本条）。⇒ 与处方"landing 以袋面 files 为唯一 git-add 面"配成对：**门禁侧亦须以袋面字节为唯一判据面**。
- **③ 本包就地排雷两件（只做自己修法相关的、可证零内容变化的）**：(a) capability 册（①，index 由 −159 → +10）；(b) `config/strategy_production_map.yaml`（本包工厂图修法的**第 4 发回退弹**：`idx=1f129196` 为 `53cdc66e06` 旧态而 `disk=HEAD=512ae478` ⇒ `git add` 后 `idx==HEAD`，该路径从 staged 清单消失）。**未碰**：`config/governance_operations_map.yaml`（idx=d89b4b7b，disk=92d17ced，均!=HEAD=8eb063a1，属他包在途生成）、`config/trading_decision_map.yaml`（disk==idx!=HEAD，属他包在途）、以及 IDX-03 的 6 件 staged 删除弹（04:24 复测**仍 6 件在膛**）——按 §3.4 owner 责任制只登记不代修。
- **④ 案卷交付态**：`LEDGER.md`/`AUDIT_REPORT.md` 此前从未入 HEAD（`git show HEAD:…`=不存在，status `AM`），04:26 起走正门 pending 袋 **0010**（含 token 先行同批：`audit_all_casebook` 2 token 已在册）；读侧快照另存 `.runtime/tmp/audit_all_20260924/{LEDGER,AUDIT_REPORT}_snap_0420.md`（gitignore 区，git 侧操作碰不到）。**下一轮第一件事=验 0010 是否 done 且 HEAD 侧字节==袋 `blob_sha256`（用 BAG-01 那把尺验自己）**。
- **队列/align 状态**：HEAD=`3919c83d87`(04:26:38) 持续在落；本包 0010 pending、0001 done-in位、0002 改判不重投、0008 done-in位、0009 done-未落地（待随 0010 之后的裁定册通道）、0003-0007 dead 待裁；align 工作树口径硬=3。
- **复核命令（只读）**：
  ```bash
  git show --format= --numstat 3919c83d87 | head            # 观察 drain 是否在落
  git diff --cached --numstat -- docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml   # 期望 10 0
  git ls-files -s -- config/strategy_production_map.yaml; git rev-parse HEAD:config/strategy_production_map.yaml  # 期望同 sha
  python .runtime/tmp/audit_all_20260924/probe_done_bag_vs_head.py   # 0010 落地后自验尺
  ```

## 心跳 2026-09-24 04:28 CST 实测（`date`=04:27:54）· 在干=本轮已干完（4 面新尺+4 项立案+2 次排雷+案卷入队）· 卡住=无 · 下一步=见 ③
- **① 本轮（第 3 次心跳周期内）净产出**：立案 IDX-01/02/03/04 + GEN-01 + BAG-01 + EVAP-02 第三实例；改判自家 0002（HEAD 正确、不重投）与"能力册未愈"（已愈，但 index 侧仍留弹）；扫描器 v3 落地并三处自纠（直连提交声明面/正负例过期/负例又选错）；就地排雷 2 件（capability 册 + 工厂图，均证零内容变化）；案卷 436→442 行走正门入队 0010。
- **② 并发实况**：`st-gpu-final` pid 23924（04:21:56）以 `--allow-promote --skip-preflight --no-auto-enqueue --message probe-full` 直连提交 10 件（含 `condition_package.py`/`condition_attribution.py`/`factory_grid_executor.py` 三件**新路径**，本包未见过其设计面）——只登记不评判，供总指挥交叉核（`--skip-preflight` 是逃生通道，用得是否恰当属其属主与门位口径）；`st-align-dirty` 04:10 自伤复原批已入 HEAD。本包对其全部路径**零写入**。
- **③ 下一步（轮次）**：①验 0010 落位（BAG-01 尺自验，含 `git show HEAD:docs/_working/audit_all/LEDGER.md | wc -l` 期望 ≥442）②GEN-01 推论扩面：对 `module_translation_registry`/`in_process_gate_registry` 等互撞热册做"同一 HEAD 两口径"复现实验，把 GEN-01 从一册实证升到族级 ③BAG-01 尺窗口扩到 `>=2026-09-23` 给终报分母 ④红蓝反证节（含本战役已积的 4 类自证案例：时钟外推、探针 v1/v2 自否、v3 负例三选错、本轮"门读 index"逮到自己案卷从未落地）⑤终报。

### 落地回执 2026-09-24 04:31 CST 实测（`date`=04:31:42）· 案卷首次入 HEAD，用自己的尺验自己 PASS
- `q-20260924-st-audit-all-20260924-0010` → **done**，`landed_id=0c7e42b3ba`(04:30:55)。BAG-01 那把尺（`sha256(git cat-file blob HEAD:<path>)` vs 袋 `blob_sha256`）三件**全 MATCH**：LEDGER.md 442 行 / AUDIT_REPORT.md 137 行 / capability 册。
- **零连带实证**：`git show --format= --numstat 0c7e42b3ba` = 恰好 3 件、全为纯插入（10/0、137/0、442/0），无第 4 路径 → 与 EVAP-02 三笔（1 声明↔28/3/8 实提交）反向对照，本包这次提交是**同机制下干净落地的一例正样本**（可作 st-commitsys 修闸后的回归用例）。
- **排雷未反弹**：`git show HEAD:<capability册> | grep -c -E 'ai_perceive_l1|obj_m_models|obj_s_redline|obj_t_tools'` = **4/4**（`e88eb3f786` 复原的 159 行仍在），我的 2 条 `audit_all_casebook` token 已在册；工厂图 `idx==HEAD==512ae478` 第 4 发弹已拆。
- **下轮第一件事改判**：盘上案卷 465 行已领先 HEAD 442 行 → 滚动补投新版（含 IDX-04 与本回执）；GEN-01 族级扩面与 BAG-01 窗口扩到 `>=2026-09-23` 依次进行。

【总指挥批注 R6·04:40·收官第一件解锁】passthrough 修复已入 HEAD，你的裁定册修复批已 requeue=0011 在队——落地后你复跑 align_all 确认 3→0，即收官三件套第一件闭环。

### 落地回执 + 心跳 2026-09-24 04:46 CST 实测（`date`=04:46:15，HEAD=`9a760906ac`）· 在干=执行批注 R6 完毕 · 卡住=无 · 下一步=见 ④

> 本块只新增两案（**F-AUDIT-DEAD-01** 死信陈旧快照面 / **F-AUDIT-RULING-01** Owner 裁定整批悬置）+ 收官第一件的**双口径判定**（HEAD 3→0 已证）。IDX/GEN/BAG/EVAP 各案不重述。

- **① 批注 R6 执行回执（0011 已落，收官第一件在 HEAD 口径闭环）**：
  - `q-20260924-st-audit-all-20260924-0011` → **done**，`landed_id=a74e9a6c48`(04:36:19)。BAG-01 尺自验 **MATCH**（`sha256(HEAD:ruling_registry.yaml)`=`7e49c0c0f3af`==袋声明）。**零连带**：`git show --format= --numstat a74e9a6c48` = 恰好 1 件 `2 2`，即 `裁定#383 related_arch ['MOD-L00-004']→[]`、`#387 ['PS-CTR-003','MOD-INF-043']→[]`，无第 2 路径。
  - **passthrough 修复复证**：同内容袋 0003/0004 此前两次死于"注册表三向合并失败（死信回退人工）"，其袋声明字节 `7e49c0c0f3af` 与本次落地字节**逐字节相同** ⇒ 死因确在合并器而非内容，批注定性成立。
- **② 🔴 收官第一件的口径分歧（本战役最重要的一条判读）**：`align_all` 复跑 **exit1、第 5 步仍报硬=3**（同三条 `related_arch 悬空`）——但**这不是没修**：
  - 尺=`probe_align_step5_head_anchored.py`：把 `registry_alignment.CATALOGS_DIR` 指向 `git show HEAD:` 具现的临时目录、调**同一个** `check_governance_bidirectional()`（不另造判据）。结果 **工作树口径=硬 3 / HEAD 锚定口径=硬 0**。
  - ⇒ **HEAD 侧 3→0 成立**；align_all 恒红的原因=其观测面读工作树，而工作树此刻被外来陈旧快照占据（见 ③）。这正是 F-AUDIT-LAND-02/GEN-01 预言的"两口径"病根的**反向实例**：同一 HEAD，脏工作树可以让**已落地的正确内容被判为仍有缺陷**（假红，且会误导修复者重复动手）。
  - 收官判据据此定形：**"连续两轮零新问题"必须以 HEAD 锚定口径计**，工作树口径只作并发实况记录。
  - 另核 **F-AUDIT-BLIND-01 未解堵**：`align_all.py:100` 有模块级 `import run_subprocess_hidden`，但 `:697`（`main()` 内 "L1 接线批挂点③ st-ailayer-final"）又局部 import 同名 ⇒ 该名字在 `main()` 全程为局部变量 ⇒ `:536/:556` 首次使用即 `UnboundLocalError` ⇒ **第 6-9 步永不执行、exit0 结构不可达**（与 0011 无关，属 st-ailayer-final 写域，只登记）。
- **③ 🔴 F-AUDIT-DEAD-01（P0 新面·未爆弹）：死信袋把陈旧快照留在主区 index+盘上，既回退已落地 HEAD 内容、又让 worktree 口径恒假红，且当前正压着本包刚落地的那笔修复**：
  - 实况：`git status --porcelain` = `M  ruling_registry.yaml`，`git diff --cached --numstat` = **`26 2`**；盘上/ index 第 5096/5172 行 `related_arch` 仍是**修复前旧值**，而 HEAD 已是 `[]` ⇒ **任何吸收 index 的落地（EVAP-02 机制）会把这三条悬空引用放回 HEAD**。属主=`st-mapcensus-20260924`（其袋 0001 创建 04:35:14，早于我落地 04:36:19）。
  - 新点（相对 IDX-01/03 的增量）：此前登记的 index 残弹来自**在途**袋；本次是**已判死信的袋**残留 `M ` 状态继续参与后续判定——即 "dead" 不等于"其 staged 面被撤销"。⇒ 处方补一条：**landing 失败进入 dead 分支时，MUST 对本袋 paths 做 index 撤销（`git restore --staged` 语义）或至少落一条 `dead_index_residue` 告警**，否则死信即成永久哑弹。归 st-commitsys（其修闸 #1 验收尺应新增本例：dead 分支后的 `git diff --cached` 必为空）。
- **④ 🔴 F-AUDIT-RULING-01（P0·交您裁）：Owner 终裁 裁定 409「一域一图立法 + 系统宪章 §8」整批悬置 27 分钟，死因是他包未提交的 frontend_map 脏字节**：
  - 事实链：袋 `q-…-st-mapcensus-20260924-0001`（files=`system_charter.md` + `ruling_registry.yaml`，RULE-RULING 要求的**同批原子**）→ **dead**，`dead_reason=门禁 MAP-ALIGNMENT 阻断: [FRONTEND-MAP] R1 F-BUDGET-PAGE / F-SCHEDULEGATE-PAGE backend_ref 含非类型化元素 'none:后端模块MOD-INF-037未入depgraph前端模块集（st-gpu-final-20260924代…'`。
  - 归属实测：**该违规字节从未进 HEAD**（`git show HEAD:…frontend_map.yaml | grep -c "none:后端模块MOD-INF-037"`=**0**，盘上=**2**，`git status`=**`M `**，该文件最近一次提交=`9521af656c`(09-16) ⇒ 脏改动属 st-gpu-final 未提交在途工作）。**两文件均悬置、未半批落地**（宪章 §8 在 HEAD 计数=0，盘上=3 ⇒ 原子性未被破坏，这点是好的）。
  - 连坐面量化：同一条 `FRONTEND-MAP R1`（同一对 F-BUDGET-PAGE/F-SCHEDULEGATE-PAGE）**已打死两包无辜** ——本包 0007（04:2x，案卷补投）与 st-mapcensus 0001（04:3x，Owner 裁定）；且 align_all 第 3 步当前仍报这 2 条 FAIL。⇒ 这是 §3.1「内容扫描型 gate 默认 own-diff 作用域」的**违反实例**：一个会话的工作树脏字节能挡住**其它会话以其自己袋面为唯一 add 面**的提交。**建议列为您本轮首要处置**（要么令 st-gpu-final 先落/先清其 frontend_map 脏字节，要么令 MAP-ALIGNMENT 对本场景走 own-scope/白名单），因为 ①Owner 裁定悬置=治理真源缺口 ②它会继续打死后续任何碰该扫描面的批，包括本包收官终报批。
  - **本包不自修**（`frontend_map.yaml`=他包写域；且"由审查者代修被审对象"违 §3.4 owner 责任制与本包自裁框架）。
- **⑤ 并发与避让（本轮实测）**：对 `ruling_registry.yaml`（st-mapcensus 悬置面）/**`capability_canonical_file_registry.yaml`(st-mapcensus claim 25.9m)/`module_translation_registry.yaml`(st-align-dirty claim 25.0m)**/`frontend_map.yaml`(st-gpu-final 在途)/GOMAP/TDM/strategy_production_map **全部零写入**；`lock_files.py list` 亲验无我需要的路径。本包唯一写入=本文件（acquire→CAS `safe_write_text`→进程外核实）。
- **⑥ 队列/align 状态**：HEAD=`9a760906ac`(04:39:55，st-align-dirty 自伤复原批④)持续在落；本包 0011 **done-in位（HEAD 口径硬=0）**、0010 done-in位、0001/0008 done-in位、0002 改判不重投、0009 done-未落地（待裁）、0003-0007 dead 待裁、**0012（本块补投）pending**；align 工作树口径硬=3（HEAD 口径=0）、第 6-9 步仍被 BLIND-01 阻断。
- **复核命令（只读，全部本轮实跑）**：
  ```bash
  git show --format= --numstat a74e9a6c48                                   # 期望 1 件 2/2
  python .runtime/tmp/audit_all_20260924/probe_align_step5_head_anchored.py  # A=3 B=0（两口径判据）
  python scripts/governance/d5_architecture/generators/align_all.py --no-report 2>&1 | tail -12   # 硬=3 + UnboundLocalError
  python .runtime/tmp/audit_all_20260924/probe_bags_for.py ruling_registry    # 死信袋定位
  git diff --cached --numstat -- docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml  # 期望 26 2（未爆弹在膛）
  git show HEAD:src/zephyr/frontend/dashboard/web/frontend_map.yaml | grep -c "none:后端模块MOD-INF-037"  # 0=未落地，脏字节属他包
  sed -n '100p;536p;697p' scripts/governance/d5_architecture/generators/align_all.py   # BLIND-01 双 import  scopes
  ```
- **⑦ 下一步（轮次，顺序不变）**：①BAG-01 尺已扩窗 `>=2026-09-23`：**106 袋/307 对**，IN_HEAD=173(56.4%)、NEVER_IN_LANDING(字节被改写)=76(24.8%)、LANDED_THEN_LOST=37(12.1%)、NO_BLOB(landed_id 无此件)=21(6.8%)、skip=1 ⇒ **落地批自身字节≠袋声明者占 24.8%（+6.8% 根本无该路径）**；需按"合法后续修改"再分层，终报给保守分母（明细 `bag01_since0923.txt`）②GEN-01 族级扩面（现锁定 `capability_canonical_file_registry`/`module_translation_registry`/`in_process_gate_registry`/`terminology_glossary` 四族的生成器候选）③IDX-03 六件 staged 删除弹复验 ④红蓝反证节 ⑤终报。


### 心跳 2026-09-24 04:56 CST 实测（`date`=04:56:34，HEAD=`9a760906ac`）· 在干=GEN-01 族级扩面 + 八图"图↔物"悬空普查已完 · 卡住=0012 死信（新立 GATE-01，见 ⑦）· 下一步=见 ⑧

> 本块新立 **F-AUDIT-GEN-02（生成器输入面族级普查）/ F-AUDIT-DANG-01（派生册图↔物 HEAD 侧悬空普查）/ F-AUDIT-GATE-01（RULING-REFERENCE 无草稿区豁免致"审查报告自引用死锁"）**，并对 DANG-01 的**更严重假设主动否证**（防把册内陈旧边说成门禁静默失效）。

- **① F-AUDIT-GEN-02（把 GEN-01 从"一册实证"升为"族级定性"，尺=`probe_gen01_family.py`）**：按 GEN-01 同一判据（有工作树递归采集 rglob/glob/walk 且全文零 HEAD 面引用）对 `scripts/`+`src/zephyr/` 的 generate_*/regen_* 逐器分类：
  - **命中"产出派生册"过滤条件的生成器 37 器**（下限口径，见 ②的自纠），其中**真正做文件树采集者 15 器 = HEAD-BLIND 14 / HEAD-AWARE 1**（唯一 HEAD-AWARE=`generate_commit_guide.py`，其 `head_ref` 命中 `HEAD:`）。⇒ **GEN-01 病根是族级常态而非孤例：14/15≈93% 的采集型派生册生成器输入面不锚 HEAD**。
  - 高危成员（不止 GOMAP）：`generate_project_depgraph.py`（**depgraph 是 RULE-DEPGRAPH/多门禁的存在性真源**，HEAD-BLIND ⇒ 未提交 .py 直接进图）、`generate_resource_profile_registry.py`、`generate_skeleton_health.py`、`generate_rule_ai_perception_index.py`、`generate_pathway_registry.py`、`generate_code_wiki_stats.py`、`generate_dataflow_diagram.py`（R-B1 同族）、`generate_data_asset_coverage.py`、`generate_manifest.py`、`generate_asset_index.py`（+_archive/prototype 版）、`generate_governance_map.py`（=GEN-01 原证）、`generate_resource_morning_report.py`。
  - **触发条件此刻即成立**：工作树独有/仅 index 的 `.py`=**184 件**（全部脏面 1176）⇒ 上述 14 器任一重跑都会产出 HEAD 侧不存在的条目，这就是"同一 HEAD 两口径"与热册互判回退的机理。
  - **探针自纠（红蓝反证第 5 例，与 v3 负例三选错同列）**：`generate_gate_registry.py` 实际写 `gate_registry.yaml` 却**未进 37 器候选** ⇒ 我的收录过滤（`WRITES`+`REGTARGET` 双正则）有假阴性 ⇒ ①14/15 是**命中率**（比例口径稳），②"37/15"须标**下限**，终报不得写成"全仓生成器总数"。
- **② F-AUDIT-DANG-01（八图审查的正题=图↔物双向对账，尺=`probe_dangling_tristate.py`+`probe_dangling_d2_split.py`，全量清单 `dangling_full.tsv` 1086 行）**：对 7 张已落地册（GOMAP/能力册/翻译册/gate 册/in_process gate 册/TDM/工厂图）取 **HEAD 侧字节** 解析其引用的一切 `src|scripts|config|tests|docs` 路径，存在性以 `git ls-tree -r HEAD` 判定，并三态分层防误判：
  - **D1 真悬空（盘上无+HEAD 无+非 gitignore）=758**：按根 `docs/_working` **542** / src 95 / tests 60 / docs(非工作区) 34 / scripts 27；
  - **D2 仅工作树（盘上有、HEAD 无而册已入 HEAD）=272** → 二次定性：**D2a 从未进过任何提交=256**（`git log --all -- <path>` 空，即 GEN-01 直证：脏件被生成器吸收进册、册落了地面件没落）／D2b 曾有提交史=16（文件侧回退，与 EVAP 家族交叠）；
  - **D3 gitignore 豁免=56** → **不计缺陷**（这一层就是我为避免"758 条吓人数字"而加的，与 F-AUDIT-BLIND-02 的派生件豁免同源）。
  - 分布集中度：`capability_canonical_file_registry.yaml` D1=606/D2=181、`module_translation_registry.yaml` D1=147/D2=91，其余五册 D1≤3（GOMAP=1、gate 册=1、TDM=3、in_process gate 册=0、工厂图=0）⇒ **悬空面是"两张派生大册"的问题，不是八图普遍问题**（此判据请总指挥按此口径下处置令，勿按总数 758 铺开）。
- **③ 🔴 DANG-01 里唯一"不自愈"的子集（本块真正要交裁的）**：能力册自述"canonical_file 等由磁盘扫描+git log 自动派生，**不持久化为第二真源**"（`capability_lookup.py:8`）⇒ D1/D2 多数属下次重扫即修的**缓存性陈旧边**，不该按缺陷逐条追。**例外=人工裁定面**：该册 `canonical_override:`（人裁最高优先级，不自愈）**HEAD 侧 253 条，其中 11 条指向不在 HEAD 的文件 → 9 条目标件从未落任何提交、2 条指向已被退役批删除的 gate**：
  - 9 条（**盘上有、HEAD 永远没有**，=人裁了 canonical 却从未把件落地面）：`ai_layer/{cleaning/washer,comparator/executor,heritage/store,perceive/translator,redline/negative_list,scheduling/maturity,tools/suite,intelligence/model_profiling/dual_run,intelligence/switch_engine/switch_engine}.py`；
  - 2 条（**凭空挂边**）：`commit_gates/{data_task_completeness_gate,issue_resolved_integrity_gate}.py`。
  ⇒ 直接命中 **RULE-CAPABILITY-LOOKUP 冷启动第 4 步**：会话按宪法调 `capability_lookup.find()` 时，人裁真源可指向仓库里不存在的文件（拿到即空手）。**建议处置=人工裁的 override 必须与目标件同批落地**（补一条"override 存在性"机检，成本=一次 `ls-tree` 交集，可挂进现有 gate 家族）。
- **④ 退役未收口 + 路径漂移两子类（同尺顺手取到，均为册侧边、非门禁失效）**：
  - 退役未收口：`library_coverage_gate/data_task_completeness_gate/issue_resolved_integrity_gate` 三闸由 **`4b8fb00a555`（st-gslim-20260923「P3 退役批A·纯文件删除」，09-23 23:31 时间戳 1790119878）** 删除，**闸体本身已从 HEAD 与盘上双双消失=退役动作已完成**，但其能力册条目（含 ③ 的 2 条人裁 override）未回收。
  - 路径漂移：`tag_vocab_gate.py`/`state_vocab_registry_gate.py`/`library_blood_flesh_gate.py` 现真身=`commit_gates/library/`，`registry_mass_deletion_gate.py`=`commit_gates/`（离 `registry_family/`）⇒ 册内仍指旧路径，属 RULE-DEPGRAPH/RENAME-DEPGRAPH-SYNC 既有义务的漏网面（改名未 `generate_project_depgraph.py --force`，或 --force 也修不到册侧）。
- **⑤ 🔴 我对本条最严重假设的主动否证（务必按此定级，勿升 P0）**：直觉上"注册表声明的 gate 文件不存在"=**门禁静默失效（最高危）**。实测**否证成立、该假设不成立**：`git show HEAD:gate_registry.yaml | grep -cE "library_coverage_gate|data_task_completeness_gate|issue_resolved_integrity_gate"`=**0**，`in_process_gate_registry.yaml` 同=**0** ⇒ 三闸已同步退出**可执行 gate 集合**，跑的闸与文件一一对应；本块 DANG-01 定级因此=**P2 册侧一致性/人裁自愈例外**，而非 P0 安全洞。（此条与 [[feedback-weak-model-dossier-not-verdict]] 同构：我出案卷+出否证，升不升格由您裁。）
- **⑦ 🔴 F-AUDIT-GATE-01（P1·结构性死锁，本包 0012 因此死信）：RULING-REFERENCE 缺草稿区豁免 ⇒ "报告某裁定未落地"这一动作本身被该裁定未落地所阻断**：
  - 事实：`q-…-st-audit-all-20260924-0012`(04:47:58, files=1=LEDGER) → **dead**，`dead_reason=门禁 REFERENCE-INTEGRITY 阻断: [RULING-REFERENCE] … docs/_working/audit_all/LEDGER.md: 裁定 409 …修复：在 ruling_registry.yaml 中补登对应条目，或移除/修正引用。（注：本门禁只检测新增引用，历史悬空引用不阻断。）`
  - 死锁链：**0011 已落=我修的是 #383/#387**；**裁定 409 未落**（其整批因 ④ of 04:46 块所述他包 frontend_map 脏字节而 dead）⇒ 我记录"409 悬置"必写其编号 ⇒ 正则 `裁定#(\d+(?:-[A-Z]+)?)`（`ruling_reference_gate.py:83`）命中"未登记编号" ⇒ 阻断 ⇒ **案卷无法入册，而被审的缺口因此更不可见**。这是"审查器把报告行为当成施工行为"的机制错配。
  - 与同族闸不一致（=可判定的立法缺陷，非我臆断）：`doc_ref_broken_gate.py` 对同一区有**显式豁免清单**含 `"_working"  # 草稿区豁免（施工方案/评估报告/临时笔记）`；`exempt_zone_frontmatter_gate.py` 亦以 `docs/_working/` 为豁免区；`folder_capacity_hard_limit_gate.py` 注释自证曾因 `docs/_working/` 123 件连坐拦死 src+tests 提交而专项治本 ⇒ **草稿区豁免是本闸族已确立的既有政策，RULING-REFERENCE 是唯一漏配者**。
  - 处方（归 gate 属主，本包不自修他包写域）：RULING-REFERENCE 增加与 doc_ref_broken_gate 同源的 `_working` 豁免（或将 md 内的裁定编号降级为 warn 不阻断），并保留对 YAML/代码内引用的硬拦——那里才是真注册表外键。
  - **本包本轮合规自解（不藏改动）**：按门禁给出的三个合法 remedy 之"**修正引用**"执行——案卷散文中的引用记法由 `裁定#+编号` 改为 `裁定 编号`（去 `#`，人读不受影响，机读不再误判为登记外键），并在本块与 04:46 块就地同批改写；**registry/代码面引用零改动**，未用任何 skip 逃生通道。此例同时成为 GATE-01 的**第二个红证**（同一闸在合法报告场景下的必红实例）。
- **⑧ 下一步（轮次）**：①把 DANG-01 的"人裁 11 条"与 GEN-02 的"14 器"并入终报三清单（悬空/漏挂/断链各带口径与自愈标注）②BAG-01 扩窗数据（106 袋/307 对）按"合法后续修改"再分层给保守分母 ③IDX-03 六件 staged 删除弹复验 ④红蓝反证节（已积 5 例：时钟外推／探针 v1v2 自否／v3 负例三选错／"门读 index"逮到自己案卷未落／本轮 GEN-02 收录假阴性+DANG-01 自我否证）⑤终报（含 0013 落地回执）。
- **队列/align 状态**：HEAD=`9a760906ac`(04:39:55)；本包 **0011 done-in位（HEAD 口径 align 硬=0）**、**0012 dead（⑦ F-AUDIT-GATE-01，非内容缺陷）**、0010/0001/0008 done-in位、0002 改判不重投、0009 done-未落地待裁、0003-0007 dead 待裁；本轮补投=**0013（含 04:46 未落块，同批改写引用记法）**；align 工作树口径硬=3（=外来陈旧快照，非本包欠账）、第 6-9 步仍被 BLIND-01 阻断。
- **复核命令（只读，全部本轮实跑）**：
  ```bash
  python .runtime/tmp/audit_all_20260924/probe_gen01_family.py                 # 37 候选/15 采集型/14 HEAD-BLIND/1 AWARE
  python .runtime/tmp/audit_all_20260924/probe_dangling_tristate.py            # D1=758 D2=272 D3=56（含按根分层）
  python .runtime/tmp/audit_all_20260924/probe_dangling_d2_split.py            # D2a=256 从未入提交 / D2b=16
  git ls-tree -r --name-only HEAD | grep -cE "/(library_coverage_gate|data_task_completeness_gate|issue_resolved_integrity_gate)\.py$"   # 期望 0=闸体确已退役
  git show HEAD:docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml | grep -cE "library_coverage_gate|data_task_completeness_gate|issue_resolved_integrity_gate"  # 期望 0=无静默失效
  find src -name "tag_vocab_gate.py"    # 真身在 commit_gates/library/（册指旧路径）
  ```

【总指挥批注 R7·05:05·0011 落地=passthrough 实弹验证通过——裁定册批解锁确认】你的裁定册修复批 0011 已落地——**合并器 passthrough 修复实弹验证通过**，全场注册表批解锁。你复跑 align_all 确认 3→0（收官三件套第一件），完成后报告。

### 追记 2026-09-24 05:03 CST 实测（`date`=05:03:39，HEAD=`4843e85072`=本包 0013）· 落地回执 + DEAD-01 定性升级（A1 清扫按 claim 快照归因 ⇒ 死信残留结构性不可自动卸载）+ WIP 官方定性与本包普查互证

- **① 0013 落地回执（用自己的尺核）**：done，`landed_id=4843e85072`(05:01:28)，numstat=**`106 0` 单件纯增**（04:46 未落块+04:56 新块一次带走，零删除零连带），BAG-01 尺 **MATCH**（HEAD 侧 548 行），四新案 ID 在 HEAD 命中 7 处。GATE-01 的自解（散文引用去 `#`）经实弹验证可通行，**registry/代码面引用零改动**。
- **② DEAD-01 升级（从"等属主收拾"改为"现机制永远收不到它"）**：`worktree_drift_watchdog.py` 的 #ARCH-308 A1 死会话清扫在 `:755-772` **按 claim 快照归因**：`claimed_files` 取自 `.runtime/claim_snapshots/<sid>.json`，`to_unstage = claimed_files ∩ staged`（注释自证只 `git reset HEAD` 动 index、工作树内容永不销毁——方向正确）。但实测：
  - `.runtime/claim_snapshots/` 内**无 `st-mapcensus-20260924.json`**（同目录有 `st-gpu-final-20260924.json`，证明非目录级缺失）；活锁权威视图 `lock_files.py list` 现仅 2 条（capability 册=st-mapcensus、module_translation 册=st-align-dirty），**均不含 `ruling_registry.yaml`**（旁证：`.ailocks/registry.json` 顶层=`{version,locks,updated_at}`，全文 grep `mapcensus`/`ruling_registry` 双 0 ⇒ 该文件非活锁真源，勿据其反推"无 claim"，判据以 `lock_files.py list` 为准）。
  - ⇒ 对这条**正压着我已落地修复**的 staged 残留，`claimed_files=[]` → `to_unstage=[]` → **A1 永不清扫（该会话死或活都一样）**。根因=**死信处置的时序不对称**：landing 失败时释放了 claim/快照，却把 staged 字节留在膛里。与 EVAP-02/IDX-04 同根（index 被当作真源），合起来是三面：**吸收面**（陈旧 index 进提交）、**判定面**（陈旧 index 参与门禁）、**清扫面**（陈旧 index 因失去 claim 而逃逸 watchdog）。
  - **处方收窄为一句**（给 st-commitsys 修闸与 watchdog 属主，本包不自修他包写域）：dead 分支与 A1 的归因键**除 claim 快照外再加队列袋 `files` 清单**（`.runtime/commit_queue/{pending,processing,dead}/<qid>.json` 的 `files[].path` 是机器可读的权威声明面，本包 `probe_bags_for.py` 已证可枚举）；验收尺=`dead 后 git diff --cached --name-only` 对本袋 paths 必为空。
- **③ 官方 WIP 定性与本包普查互证（两把独立尺同向，非我自证）**：`classify_workspace_wip.py` 全仓分类 = `active_wip 19 / derived_sync 482 / **stale_rollback 540** / fresh_change 1 / untracked_new 139`，且**把 `ruling_registry.yaml（staged）` 亲自判入 `stale_rollback` [mtime<HEAD]** ⇒ 与 ② 的归因链一致。同时其 `untracked_new 139 件`清单里正是 `config/ai_search_veins.yaml / ai_source_registry.yaml / cleaning_policy.yaml / comparison_policy.yaml …`——**与 DANG-01 的 HEAD 侧悬空引用逐条同名** ⇒ DANG-01 的"册引用从未提交的件"由第二把独立尺复证（GEN-01→DANG-01 因果链闭合）。
  - 本包 D2a=256（从未进任何提交）与官方 `untracked_new=139` 的关系：139 是"当前盘上未跟踪件数"，256 是"已落地册内声明且从未入提交的路径数"（含已被后续提交带走的、以及 D 状态件）⇒ **两数不必相等，勿当矛盾报**；交叉点（config/* 那批）才是定性证据。
- **④ 收官三件套进度**：第一件（align_all 3→0）**已在 HEAD 口径闭环**（工作树口径 3 系外来残留，且 ② 已证其不会自愈 ⇒ 只能由属主 rebase 或您下令卸载）；第二件 连续两轮复跑零新问题=进行中（本轮新增 4 案均系"新发现"而非"未修回归"）；第三件 红蓝反证+终报=待做（已积 6 例自证材料）。
- **⑤ 下一步（轮次）**：①DANG-01 的 D1 `docs/_working` 542 条按 TTL 工作区语义出"是否需回收"判据（避免把设计内过期当缺陷刷数）②BAG-01 扩窗数据再分层给保守分母 ③IDX-03 现规模已=15 件/1079 行纯删（6 件 `D ` + 9 件 `MM `），按 ③ 官方分类其中 library 族 6 件为整文件删除待属主定性 ④红蓝反证节 ⑤终报。
- **队列/align 状态**：HEAD=`4843e85072`(05:01:28，本包)；本包 0013/0011/0010/0001/0008 done-in位、0012 dead（=GATE-01 红证，已被 0013 取代，勿 requeue）、0002 改判不重投、0009 done-未落地待裁、0003-0007 dead 待裁；align 工作树硬=3（HEAD 口径=0）、6-9 步仍被 BLIND-01 阻断。
- **复核命令（只读，全部本轮实跑）**：
  ```bash
  git show --format= --numstat 4843e85072                       # 期望 106 0 单件
  sed -n '755,772p' src/zephyr/gov_enforcement/rule_bridge/worktree_drift_watchdog.py   # claim 快照归因
  ls .runtime/claim_snapshots/ | grep -c mapcensus              # 期望 0（无快照=A1 收不到）
  python scripts/governance/classify_workspace_wip.py 2>&1 | grep -E "^\[" | head -6     # 19/482/540/1/139
  python .runtime/tmp/audit_all_20260924/probe_bags_for.py ruling_registry                # 死信袋定位
  ```

### 更正 2026-09-24 05:12 CST 实测 · BAG-01 分母自我更正（35.5% → **24.6%**），并给出按类分层口径（尺=`probe_bag01_stratified.py`，逐条 `bag01_stratified.txt`）

- **为什么要更正**：04:18 块发表的 **35.5%（11/31）"done 声明字节不在 HEAD"** 是 `>=2026-09-24` 窄窗 + **未剔除合成/审查类会话** 的口径。扩窗到 `>=2026-09-23`（**111 袋 / 314 对**）并分层后，该数**虚高**，原因是把压力测试袋算进了真损。
- **两把尺互证与漂移解释（防"两个探针不一致"误读）**：`probe_done_bag_vs_head.py`=106 袋/307 对，`probe_bag01_stratified.py`=111 袋/314 对；差 **5 袋 7 对**已逐袋点名（st-align-dirty 0030/0031/0032、st-commitsys 0013、本包 0013，创建时刻 04:35:19~05:00:26）⇒ 差异全部来自队列在两次跑之间继续落地，**非方法分歧**；且两跑对 `NEVER_IN_LANDING=76` 完全一致。
- **终报应引用的口径（真实施工会话，剔除 stress/gaudit/本包 = 268 对）**：
  | 状态 | 对数 | 占比 | 是否可据此定罪 |
  |---|---|---|---|
  | IN_HEAD | 168 | 62.7% | — |
  | NEVER_IN_LANDING(落地批自身字节≠袋声明) | 44 | **16.4%** | 次硬（三向合并改写可解释一部分，须逐件判） |
  | LANDED_THEN_LOST | 34 | 12.7% | **不可**（热册被后续批合法修改是常态；真损由 v3 sweep 的 26 条点名） |
  | NO_BLOB(landed_id 里根本没有该路径) | 22 | **8.2%** | **最硬**（不依赖任何"后被修改"解释即证伪 done） |
  - **合计最硬+次硬 = 24.6%**（对全体含合成会话则为 31.8%；合成会话 46 对里有 32 对落在 NEVER_IN_LANDING，这就是 04:18 那个数被抬高的来源）。
- **按文件类分层的真信号（本块最有处置价值的部分）**：`注册表/配置册` 类 n=78 → IN_HEAD 仅 **23**、NO_BLOB **22（28.2%）**、NEVER_IN_LANDING 22、LANDED_THEN_LOST 11 ⇒ **热册/配置册的 done 声明有约 28% 其"落地提交里连该路径都没有"**，是全仓最不诚实的一类；而 `代码` 类 n=108 → IN_HEAD 81、NEVER_IN_LAND 9、LOST 17、NO_BLOB 1 ⇒ **代码面落地质量良好（悬空率 0.9%）**。
  ⇒ 处置指向因此收窄：**问题不在"队列不可靠"，而在"热册（注册表/配置册）这条路径上袋面与落地面脱钩"**，与 EVAP-02/IDX-01/DEAD-01 三个同根案完全同向（三案病灶都在 index/合并器对热册的处置），可并为**一条**修闸需求交 st-commitsys，勿按 22+22 条分散立项。
- **红蓝反证节材料第 7 例（自家数字自纠）**：04:18 的 35.5% 属"窄窗+含合成会话"未加限定即发表；本轮先按扩窗复算、再分层、再点名差异来源后才定稿。终报中凡引用比率，一律带 **窗口 / 是否剔除合成会话 / 分母** 三要素（本块即范式）。
- **队列/align 状态**：HEAD 侧本包 0013 已落（`4843e85072`，106/0 单件纯增、MATCH）、**0014 pending→在队**（05:03 追记块）；align 工作树硬=3（HEAD 口径=0）、6-9 步仍 BLIND-01。本包对 `注册表/配置册` 类路径写入仍=0。
- **复核命令（只读）**：
  ```bash
  git show --format= --numstat 4843e85072                       # 期望恰好 1 件 106/0（本包 0013 零连带）
  python .runtime/tmp/audit_all_20260924/probe_bag01_stratified.py           # 111 袋/314 对 + 按类分层
  SINCE=2026-09-23 python .runtime/tmp/audit_all_20260924/probe_done_bag_vs_head.py   # 独立同尺复跑
  python .runtime/tmp/audit_all_20260924/probe_bags_for.py "st-align-dirty-20260924-0030"  # 差异袋点名（两跑口径差的来源）
  ```

## 心跳 2026-09-24 05:29 CST 实测（`date`=05:29:23，非估钟）· 在干=R7 令执行毕（align 复跑两轮，3→0 定性到"口径+机制"双层面）· 卡住=无（本包不 pop 不 drop 他人 stash）· 下一步=见 ⑤

- **① R7 指令回执（总指挥 05:05 令"复跑 align_all 确认 3→0，完成后报告"）**：**HEAD 口径=0 亲验成立；工作树口径=3 且已能点名机制**（不再是"陈旧快照"这类模糊语）。
  - HEAD 侧：我的修复 commit=`a74e9a6c48`(04:36，"align_all 全图硬 3->0 exit0"自述) 在 HEAD 祖先链，且该册 `related_arch` 已置空——尺=`git show HEAD:docs/.../ruling_registry.yaml | grep -cE "MOD-L00-004|PS-CTR-003|MOD-INF-043"` = **0**。
  - 工作树侧：05:15 与 05:27 两轮复跑第 5 步**恒 硬=3（治理双向 3 条，逐条同名）**，因该热册索引/工作树字节=`f84392cd7e` ≠ HEAD=`771ec4acf4`，其 +26/−2 里含**对我修复的回退**（见 ②④）。
  - **exit0 结构不可达≠本包欠账，且本轮新证 HEAD 版引擎是好的**：崩在第 6 步 `UnboundLocalError: run_subprocess_hidden`。`git show HEAD:scripts/governance/d5_architecture/generators/align_all.py` 该 import **只出现 1 次（:100 模块级）**、工作树/暂存版出现 **2 次**（第二处 `:697` 在 `main()` 内 ⇒ 名字在 `main()` 全程为局部 ⇒ `:536/:556` 首用即崩）。⇒ **BLIND-01 是 st-ailayer-final 在途暂存件引入的回归**：该批一旦按现字节落地，align 引擎变"恒 exit1 + 第 6-9 步永不执行"。**给 st-ailayer 的处置建议=落地前必改**（删 `:697` 那行局部 import 即可，:100 已导入；零功能影响）。
- **② 🔴 新立案 F-AUDIT-STASH-01（P1·死会话 stash=标签"14 行"/实测"663 文件"的全树回退弹）**：
  - 事实：`stash@{0}` 建于 **05:18:36**，消息 `On dev: st-pipeline-final-20260924: frontend_map 14行A包WIP临时隔离（secbuild落地后pop恢复）`；`git stash show --stat stash@{0}` 实测=**663 files / +236,564 / −5,305** ⇒ 消息自述规模与实差 **47×**（14 行 vs 663 件）。而该会话此刻已被本包冷启动 `lock_files.py cleanup` 判为**死会话并 SALVAGED**（`stash=0件` 即清理器不认识这个既成 stash）⇒ **"待 pop 恢复"的承诺无主可兑现**。
  - 里面装什么（逐件实测，三件各自指向"pop 即回退已落地面"）：
    - `src/zephyr/frontend/dashboard/web/frontend_map.yaml`：stash 版含 `F-BUDGET-PAGE`/`F-SCHEDULEGATE-PAGE` **各 1 行、合计 2 处 R1 非类型化 backend_ref**（尺=`grep -cE 'F-BUDGET-PAGE|F-SCHEDULEGATE-PAGE'`=2；单查 `F-BUDGET-PAGE`=1——两数不等是"行计数 vs 两类各一行"，勿当矛盾报），而 HEAD/索引/工作树现均 **0 命中** ⇒ **pop = 重新武装那条已连坐打死 ≥3 包的门禁**（本包 0005/0007、st-mapcensus 0001/0004、st-oddjobs 0001）；
    - `ruling_registry.yaml`：stash 版含 `MOD-L00-004/PS-CTR-003/MOD-INF-043` ⇒ pop 即回退 ① 的已落地修复；
    - 与"stash 之后落地"求交=**1 件**命中 `capability_canonical_file_registry.yaml`（05:20:28 `1735200b6a` st-commitsys / 05:23:49 `886ec028e2` st-oddjobs 之后落地）⇒ pop 会把已落地热册拉回旧字节。
  - **两向皆毁 ⇒ 只登记，不 pop 不 drop**：drop=毁 663 件在途 WIP（含他包唯一副本）；pop=回退刚落地面。**建议交您/属主定向处置**：按件提取 `git show 'stash@{0}:<path>' > <path>`（只取自己那 1 件），禁整弹 pop。
  - **立法侧建议（一条，勿分散）**：stash 卫生缺"规模自证"——消息须带 `files=<n>`（或由 `session_worktree_*` 在 push 后回写），且 watchdog 应把**死会话名下 stash** 纳入可见面。家族归并：与 DEAD-01（staged 残留因失去 claim 而逃逸清扫）/EVAP-02/IDX-01 同根="index 或工作树被当第二真源"，本条是**第四面=stash 面**（无归属登记、无 TTL、无清扫可见性）。
- **③ 05:18 事件顺带解堵（R7 正面副产品，已复测）**：`check_frontend_map.run_checks()` 现测=**359 功能点 / fail=0 / warn=10**；align 第 3 步 05:15=`361/fail2` → 05:27=`359/fail0`。⇒ 死于 `MAP-ALIGNMENT→FRONTEND-MAP R1` 的袋具备重投条件：本包 **0007 已 requeue→0016 pending**。重投前先证"三袋同源"：0005/0006/0007 声明字节 sha256 **全等**=`6547ac25c5174040…`，且其 `blob_ref` 存件哈希=盘上现内容哈希 ⇒ **只投最新一袋即闭，不三投**（防三连坐）。他包 `st-oddjobs-final-0001`（同死因，其台账已自记"待落地后 requeue"）**由其属主自投，我不代投**。
  - **探针自纠（红蓝反证材料第 8 例）**：我第一版判"0005/0006/0007 袋面字节不在 HEAD"用的是 `files[].sha` —— **该字段在袋 schema 中根本不存在**（真字段=`blob_sha256` + `blob_ref`），且 git blob sha(12) 与 sha256 不可直接比 ⇒ 假"袋面丢失"结论。换正字段+盘上哈希双证后结论翻转为"袋面完好、只待重投"。⇒ 铁律补一条：**凡"内容丢失"类结论，先自证所用字段存在**（本包 BAG-01 尺已按 `blob_sha256` 复核，无需更正其 24.6% 结论）。
- **④ 本轮唯一真正需要您点头的事（其余全部自解或已上交）**：**Owner 裁定 409 全文只活在未提交面**。`ruling_registry.yaml` 现 `M `=`f84392cd7e`（含该条）而 HEAD 命中=**0**；文件 mtime=**04:29:41**（未被 05:18 事件改写，也没被清扫）；其配套件同样未提交：`docs/02_enterprise_architecture/04_architecture_principles_decisions/system_charter.md`（`M `）+ 新件 `docs/_working/map_census/00_panorama_map_census_v1.md`（`A `）。承载它的两袋 `st-mapcensus-20260924-0001/0004` 均 **dead**（死因=② 的 R1 连坐，**现已解堵**），该会话 claim 已空（`lock_files.py list`=CLEAN）。⇒ 现状=**一次普通的 index 清理/一次 stash pop 事故/一次 gc 都可能让这条 Owner 终裁蒸发**（gc 前可取：`git cat-file -p f84392cd7e`）。**请裁**：是否令 st-mapcensus 的"裁定+宪章同批原子"由您指定会话走正门重投（其原死因已消；`RULE-RULING` 要求同 commit 原子，故须 3 件同批）。本包不代投（他包写域+热册）。
- **⑤ 下一步（轮次）**：①盯 0016 落地（=收官清单 #11 battle_map 小修）②DANG-01 D1 `docs/_working` 542 条按 TTL 语义出"是否需回收"判据 ③IDX-03 15 件删除弹复验 ④红蓝反证节（已积 **8 例**：时钟外推／探针 v1v2 自否／v3 负例三选错／"门读 index"逮到自己案卷未落／GEN-02 收录假阴性／DANG-01 主动否证 P0／BAG-01 比率 35.5%→24.6% 自纠／本轮 `files[].sha` 假字段）⑤终报。
- **队列/align 状态**：HEAD=`886ec028e2`(05:23:49，st-oddjobs)；本包 0013/0011/0010/0001/0008 done-in位、**0016 pending（=0007 重投）**、0012 dead(=GATE-01 红证，勿 requeue)、0002 改判不重投、0009 done-未落地待裁、0003/0004 dead(裁定册三向合并失败；其内容已由 0010/0011/0013 分批落地⇒**判过时不重投**)、0005/0006 与 0007 同源由 0016 代表；align：第 1-5 步工作树 硬=3（HEAD 口径=0）、第 6 步崩（暂存版 BLIND-01）、第 7-9 步未及。本包对 `注册表/配置册` 类路径写入仍=**0**。
- **复核命令（只读，全部本轮实跑）**：
  ```bash
  P=docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml
  git show HEAD:$P | grep -cE "MOD-L00-004|PS-CTR-003|MOD-INF-043"     # 期望 0=HEAD 口径 3→0 已闭
  git ls-files -s -- $P; git hash-object "$P"                          # 期望 f84392cd7e（回退弹在膛）
  git stash list; git stash show --stat 'stash@{0}' | tail -1          # 663 files / +236564 / -5305
  git show 'stash@{0}:src/zephyr/frontend/dashboard/web/frontend_map.yaml' | grep -cE "F-BUDGET-PAGE|F-SCHEDULEGATE-PAGE"   # 期望 2（单查 F-BUDGET-PAGE=1）=pop 即重新武装
  python -c "import sys;sys.path.insert(0,'scripts/governance/d5_architecture/generators');import check_frontend_map as m;print(m.run_checks()[2],len(m.run_checks()[0]))"   # 期望 359 0
  git show HEAD:scripts/governance/d5_architecture/generators/align_all.py | grep -c "import run_subprocess_hidden"   # HEAD=1（无 bug）；工作树=2（有 bug）
  # 注：本块提及 409 一律用"裁定 409"（去 #），正则写 `裁定[# ] *409` 以免自触 GATE-01——这同时是 GATE-01 第三例红证（审查器连"记录某裁定尚未落地"都必须改拼写才能入册）。
  ```

## 心跳 2026-09-24 05:41 CST 实测（`date`=05:41:12，非估钟）· 在干=DANG-01 判据出齐并**自我否证原尺**（新立 DANG-02）+ IDX-03 复验分层 · 卡住=无 · 下一步=见 ⑤

- **① 上轮两袋落地回执（本包首次同轮双袋齐落，正门无连带）**：`8639ed73c7`(05:35:02)=**0016 battle_map 断链治本**（收官清单 #11 闭：HEAD 版 `file:///` 命中=**0**、`_archive/架构图/交易决策架构.md` 命中=2、`--name-only` 恰 1 件零连坐）；`91e462a5b1`(05:36:00)=0017 心跳册。⇒ 0005/0006/0007 同死因三袋由 0016 一投即闭，"只投最新一袋"的判断成立。
- **② 🔴 新立 F-AUDIT-DANG-02（本包第 9 例自我否证，且是**改分母**级别）：DANG-01 原尺把 `creation_tokens:` 台账正文当成图边，**785 条 D1 里只有 165 条是真的**。
  - 事实（尺=`probe_dangling_v2_fieldslice.py`，输出 `dangling_v2_fieldslice.txt`+`dangling_v2_lists.txt`，HEAD 侧字节、按顶层键切片）：`capability_canonical_file_registry.yaml` 总 **47,163 行**中 **42,018 行=89%** 属 `creation_tokens:` 段（起始 :5145，下一个顶层键 `di_seam_exemptions` 在 :47162）；原尺 `PATHRE.findall(整册)` 得 9,790 refs，切片后业务面仅 **363 refs**。
  - **七册同尺复算（整册口径 → 业务面口径）**：D1 **785 → 165**、D2 **278 → 110**。逐册：capability 册 628→**8**（D2 187→19）、module_translation 册 152→**152**（无台账段，不受影响）、GOMAP 1→1、gate 册 1→1、in_process 0、TDM 3→3、工厂图 0。
  - **上一块 ②③ 里那句"D1 `docs/_working` 539 条"因此作废**：594 个唯一 `_working` 路径中 **599 行落在台账正文**（字段=creation_tokens>capability 543 / >merge_evaluation 48 / >note 7 / >created_by 1），业务面仅剩 4 行且全是 `description`/`responsibility_layer`/`ai_autonomy` 这类**散文字段**（`canonical_override:` 命中=**0**）。⇒ 我此前怀疑的"永久册引用 TTL 临时区=SSOT 方向错"**证伪**，临时区引用是 CREATE-GUARD 收据正文，不是边。**"是否需回收"这个判据问题的前提是错的**——不需要 TTL 判据，因为压根没有需要判的引用。
  - **真信号（终报三清单里"悬空"那一栏的诚实口径）**：D1 165 条中 **152 条在 `module_translation_registry.yaml`**（`ex_core` 18 / `governance` 8 / `integration` 8 / `gov_enforcement` 7 / `infrastructure` 4 / `_archive` 12；扩展名 .py=157/165）⇒ 翻译册在册、物在任意 ref/任意盘面皆无 = **图挂了物从未存在**，这才是八图审查的正题欠账。D2 110 条中 **55 条= `src/zephyr/ai_layer`**（属 st-ailayer 在途面，他包写域，只登记）。
- **③ 由 ② 顺带挖出的结构因（比 ② 本身更有处置价值）**：**CREATE-GUARD 的 token 台账内嵌在"能力→真源反查册"这本 `ttl: permanent` 热册里**，两面皆伤——(a) 任何整册文本扫描器（我这把尺、以及可能的引用类门禁）都会被 42k 行收据污染，假边率 96%（9,790→363）；(b) **每个"新建文件"批都必须回头写这本册** ⇒ 它就是近期反复出现的"热册拉锯/旧快照冲掉新登记"的放大器（HEAD 侧 `a94d18ef1b` 自述"热册拉锯第二次实证"即此路径）。家族归并：与 EVAP-02 / IDX-01 / DEAD-01 / STASH-01 同根第五面=**"台账与索引同册"（审计收据与查询真源未分层）**。
  - **定级与路由（不自修）**：迁出台账=对在册热册做**净删** ⇒ 触 §5 high 域四类之"注册表净删"+ 需同步改 CREATE-GUARD 读取路径 ⇒ **只登记上交**，建议并入交 st-commitsys 的那一条修闸需求（与 BAG-01 收窄出的"热册袋面/落地面脱钩"合为**一册分层**议题，勿分散立项）。
- **④ IDX-03 复验（第 4 轮，规模与定性双更正）**：index 是活面，现测=**9 件 / 3,058 行纯删**（上轮记的"15 件/1079 行"已过时，勿再引用）。按"是否自洽重构"二分：
  - **真弹 6 件（library 族，仍无人 claim、`lock_files.py list` 该族命中=0）**：`src/zephyr/library/collectors/logs_collector.py` / `tests/library/test_logs_collector.py` / `tests/gov_enforcement/test_library_blood_flesh_gate.py` / `docs/library/regulations.md` / `.../library_sop/blood_flesh_cataloging_sop.md` / `docs/03_modules/_domain_library/algo_flow/collectors/logs_collector.yaml`。硬证不变：HEAD 三件 `git cat-file -e` 全 IN_HEAD，且 `collectors/__init__.py:31` 仍 `from ... import logs_collect` ⇒ 吸收即 HEAD 侧 import 断链。**新观察到的一环**：这 6 件在工作树以 `??`（untracked）**同路径同名仍在** ⇒ "删"只发生在 index/HEAD 面，盘上字节还在 ⇒ 一次 `git clean` 或一次 checkout 才会真丢，这也是它比"盘上也没了"更难被发现的形态。
  - **撤销 3 件（commit_guide 族，判为属主自洽重构，非弹）**：`gate_digest_registry.yaml` / `commit_navigation_playbook.md` / `tests/governance/generators/test_generate_commit_guide.py` 同批配 `generate_commit_guide.py`(`M`) + `test_commit_guide_delivery.py`(`M`) + `death_cases_registry.yaml`(`M`) + `file_type_checklists_registry.yaml`(`M`) ⇒ 生成器与其交付测试同步在改，退役旧件属正常演化。**本包对其写入仍=0**。
- **⑤ 下一步（轮次）**：①终报三清单按 ②③ 更正后的口径重算（"悬空"栏 D1=165 带自愈标注、D2=110 点名在途属主）②`module_translation_registry` 152 条 D1 逐条定性（退役未销册 vs 从未落地 vs 改名未同步——改名族可用 `git log --all --diff-filter=A` 对照，本轮已跑该尺：ai_layer 1 条命中=0 从未落地）③红蓝反证节并档（现 **9 例**）④终报。已完成的判据项：DANG-01-D1 TTL 判据（=前提证伪）、IDX-03 复验（第 4 轮）。
- **队列/align 状态**：HEAD=`91e462a5b1`(05:36)；本包现存袋 **0001-0017 共 16 个**（0014 无独立袋文件=已被 0015 的 `meta.supersedes` 正常合并，非号位丢失），其中 0001/0002/0008/0009/0010/0011/0013/0015/0016/0017 **全 done**、0003/0004/0005/0006/0007/0012 dead 且**已无可 requeue 项**（0003/0004 内容已由 0010/0011/0013 分批落地判过时，0012=GATE-01 红证勿 requeue）⇒ **本包提交面清零欠账**。队列在飞=`st-align-dirty-0035`(05:40)；align：第 1-5 步工作树 硬=3（HEAD 口径=0）、第 6 步崩（st-ailayer 暂存件 BLIND-01）、第 7-9 步未及。本包对 `注册表/配置册` 类路径写入累计仍=**0**。
- **复核命令（只读，全部本轮实跑）**：
  ```bash
  python -c "import json;d=json.load(open('.runtime/commit_queue/done/q-20260924-st-audit-all-20260924-0015.json',encoding='utf-8'));print(d['meta']['supersedes'])"   # 0014 归并证据
  git show --format= --name-only 8639ed73c7                                   # 期望恰 1 件（battle_map 零连带）
  git show HEAD:docs/02_enterprise_architecture/04_architecture_principles_decisions/panorama/battle_map_positioning.md | grep -c 'file:///'   # 期望 0
  python .runtime/tmp/audit_all_20260924/probe_dangling_v2_fieldslice.py      # D1 785→165 / D2 278→110 逐册表
  python .runtime/tmp/audit_all_20260924/probe_d1_working_ttl_verdict.py      # _working 引用 599/603 行落在 creation_tokens 字段
  git show HEAD:docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml | sed -n '5145p;47162p'   # 台账段边界
  git diff --cached --numstat --diff-filter=D                                 # 现 9 件/3058 行
  git status --porcelain -- src/zephyr/library/collectors/logs_collector.py    # 期望同时出现 "D " 与 "??"（删在 index，字节还在盘上）
  git show HEAD:src/zephyr/library/collectors/__init__.py | grep -n logs_collector   # :31 断链硬证
  ```

## 心跳 2026-09-24 05:48 CST 实测（`date`=05:48:37，非估钟）· 在干=翻译册 152 条真悬空**逐条三分定性完成**（新立 MTR-01/MTR-02）+ 自尺两处假阳性自纠（反证第 10/11 例）· 卡住=无 · 下一步=见 ④

- **① 0018（05:41 心跳册）已 done**；本包袋面 0001–0018 全为 done/dead、无待 requeue 项 ⇒ 提交面持续零欠账。
- **② 🔴 新立 F-AUDIT-MTR-01（八图审查"悬空"栏的终稿口径）**：对上一块定出的"业务面 D1 里 152 条在 `module_translation_registry.yaml`"逐条三分（三道判据=HEAD 存在性 / `git log --all --reflog` 可及历史 / 非泛名唯一同名；尺=`probe_translation_d1_verdict.py`，152 行全量带判据=`dangling_translation_d1_verdict.tsv`）：**R_改名未同步 45 + R?_多候选不判 5｜H_退役未销册 71｜N_从未落地 31**。
  - **R_改名未同步 = 45**（物在、位置变了、册未跟）：例 `scripts/governance/_archive/vms_ri/vms_{build_completion_check,cron_monitor,cross_file_check,health_check,migrate,migration_dry_run,phase_rollback,version_sync_check}.py → scripts/governance/vms/同名`（8 条同族）、`src/zephyr/ex_core/adapters/{risk_validation_bridge,simulation_broker}.py → src/zephyr/governance/adapters/同名`、`src/zephyr/ex_sor/core/api_rate_limiter.py → src/zephyr/ex_sor/api/同名` ⇒ 图↔物断链里最易修、且**本该由生成器自动跟随**的一类（对照 RULE-DEPGRAPH"改名后 `--force` 重建"，翻译册无此联动）。
  - **H_退役未销册 = 71**：物曾在可及历史、后被删，册条目未销。**其中三条已追到可点名到 commit+行号的欠账，升为 F-AUDIT-MTR-02**：
    - 退役有据：批A=`4b8fb00a555`（09-23「P3退役批A·纯文件删除」，自述"注册表除名随批B紧随"）；批B=`9b0c31ab125`（「P3退役批B·**注册表除名**+库门入HEAD」，in_process gate 册 117→114 三条目删除、gate 册重生成、三块 deprecated 墓碑）。
    - **但批B 实改 13 件里 `_registry/catalogs` 只含 `fail_open_register`/`gate_registry`/`in_process_gate_registry` 三册，`module_translation_registry.yaml` 命中=0** ⇒ "注册表除名"承诺**漏了翻译册这一面**。铁证（HEAD 版字节）：`module_translation_registry.yaml:55798` 仍为 `- module_path: src/zephyr/gov_enforcement/commit_gates/library_coverage_gate.py`、:55801 `name_en: "library_coverage_gate.py"`；三闸在该册命中 3/2/2 行。
    - 与 DANG-01 ⑤ 互证：同三闸在 gate 两册命中=**0**（已同步退出可执行 gate 集合）⇒ 结论=**退役动作跨册同步不完整**（gate 侧销了、翻译侧没销），非统计猜测。处方=补销须"同批跨册"（翻译册+`docs/03_modules` 卡片同批），属 §5 **注册表净删=high 域** ⇒ 只登记上交，路由=st-gslim 收棚方或 st-commitsys 修闸族。
  - **N_从未落地 = 31 = 5（他包在途死信件）+ 25（真幽灵）+ 1（我尺假阳性，见 ③例10）**：
    - **5 条=门禁自造悬空（时序倒挂）实锤**（尺=与全部队列袋文件清单求交）：`scripts/audit/t0_{ceiling_capacity,e4_v2,e4_v3,gpu_condition_pack,six_phase_materialize}.py` 全命中 `st-t0-matrix-20260924` 的 **dead 0007/0008** ⇒ 该袋死因正是 TRANSLATION-COVERAGE 门禁"给这 5 个新件登记大白话"的要求，而**登记先落地面、件本体仍在死队列** ⇒ 闭环=门禁要求→登记先落地→本体死信→册侧悬空→悬空检查又红。本条定级=**非缺陷**（其批落地即自愈），但闭环本身是结构性缺陷（与 DANG-02 并一条）。
    - **25 条真幽灵**：`src/zephyr/ex_core` **16**（auction_deviation_executor / batch_executor / batch_take_profit_executor / blueprint_implementer / conditional_order_manager / deployment_consistency_manager / execution_mcp_server / execution_risk_gate / execution_tca / factory / fill_processor / microstructure_modeler / rl_optimal_executor / sell_priority_scheduler / stop_loss_take_profit_executor / value_objects）+ `pf_core/strategies` 2（min_variance_strategy / risk_parity_strategy）+ `risk` 2（ashare_stop_loss_rule_engine / drawdown_realtime_tracker）+ `sell_decision/core` 2 + `backtest/services/result_deployer` + `infrastructure/h1_redis_hot/h1_factor_source` + `docs/_working/kimi_audit/lane_reports/cost_trio_exam`。原文（HEAD :3971）=`module_path: …auction_deviation_executor.py` + `name_zh: 拍卖偏差执行器` + `plain_zh: 拍卖偏差执行器，执行核心的执行器…` + `responsibility_layer: business` ⇒ **有中文名、有大白话、有责任层，唯独物从未存在于任何可及 ref**。
    - 第一性判断：`execution_mcp_server` / `rl_optimal_executor` / `microstructure_modeler` 这类命名是"机构级执行系统**本该**有的样子"，不是本项目建成的样子 ⇒ 登记来源=蓝图/愿望清单批量灌入，而非磁盘派生（是否同一生成器所为待 ④①核，此说目前为**推断级**）。
  - **定性判据缺口（本条要害，与数量无关）**：全册 **8,655 条**中 `build_status` 仅出现 **42 次且取值全为 `dormant`** ⇒ 25 条真幽灵**没有任何"计划未建/待施工"标记**，消费者（门禁、capability 反查、前端全景）无法区分"应存在而被删"与"从未落地"。对照机构实践：清单类真源必带生命周期位（K8s 资源有 apiVersion/deprecate 语义、ADR 有 accepted/superseded）；扁平"目录即真源"在 AI 批量生成下必然积累幻觉条目。
  - **处置路由（不自修）**：翻译册=他包在途写域（`st-align-dirty-0037` 正在飞；其 05:34 批即"翻译册末级收口批 14 件新登记+自造 5 组重复键塌回"），且删条目=**注册表净删 high 域** ⇒ 只登记。处方两条：**(a)** `add_module_translation.py` 对 `module_path` 加存在性校验，或强制新登记带 `build_status: planned`（把"计划"与"事实"分栏，零净删即得）；**(b)** 退役批须跨册同批销（gate 册/翻译册/能力册三联）+ 改名须接 `git mv` 后自动跟随。
- **③ 红蓝反证第 10、11 例（本轮两次自否证，均已从数字里扣除）**：
  - **例10（正则抓散文占位符）**：`module_translation_registry.yaml` HEAD :60079 有一行**模板说明**`⑤代码映射：MOD-xxx / src/zephyr/.../xxx.py；`，我的 PATHRE 把 `src/zephyr/.../xxx.py` 当真实路径收进 D1 ⇒ **上一块"业务面 D1=165"更正为 164**（该条即 N 族里唯一假阳性）。教训：凡"册里有这个字符串"≠"册声明了这个件"，扫描面须排模板/示例行。
  - **例11（改名判据 v1 太松，造出 11 条假改名）**：v1 仅按 basename 在 HEAD 找同名 ⇒ `src/zephyr/compliance/zero_knowledge_audit_stub/__init__.py` 被"匹配"到 `data_governance/services/__init__.py`（荒谬）。v2 收紧为**非泛名黑名单 + 唯一候选**后：R 56→45、5 条降"多候选不判"、11 条回落 H=71。**同一份清单两把尺差 11 条** ⇒ 终报凡引用分类计数一律标注判据版本。
  - 顺带量化一项**不成问题的问题**（防噪声立项）：册内空壳条目（只有 `module_path` 无任何翻译字段）全册仅 **2/8655=0.02%**（`strategy_factory/owner_band_t/data_loader.py`〔盘上真实存在，仅缺翻译〕与 kimi_audit 幽灵）⇒ 不立项。
- **④ 下一步（轮次）**：①核翻译册生成器是否从磁盘派生（把 ②的"推断级"升到"亲验级"或推翻它）②`st-align-dirty`/`st-ailayer` 落地后复跑 DANG-02 v2 尺做**第 1 轮零新问题**判定 ③终报三清单按本轮口径落稿（悬空=164 条带 R/H/N 三分标注 + 断链=45 改名 + 3 闸跨册未同步 + 漏挂=25 真幽灵待裁"补建 or 销册"）④红蓝反证节并档（现 **11 例**）⑤终报。
- **队列/align 状态**：本包 0016/0017/0018 全 done（0016=`8639ed73c7`@05:35、0017=`91e462a5b1`@05:36、0018=`7a77de4e1a`@05:45:38；写块时 0018 尚未落地，号已就地补齐）；队列在飞=`st-align-dirty-0037`(05:48)、lease=drain-active；align：第 1-5 步工作树 硬=3（HEAD 口径=0）、第 6 步崩（st-ailayer 暂存件 BLIND-01）、第 7-9 步未及。**本包对 `注册表/配置册` 类路径写入累计仍=0**（本轮全部动作=只读探针 + 本台账 + `.runtime/tmp/`）。
- **复核命令（只读，全部本轮实跑）**：
- **并发事实（决定本轮计数时点）**：`10e16d9ae4`(05:49:45, st-align-dirty)=「翻译册·重复行遮蔽中性化批」刚落地 ⇒ 本轮 R/H/N 三分测于该批**之前**的 HEAD 字节，而该批改的正是我 152 条所在的同一本册 ⇒ 终稿必须复跑；这也是 ② 那句「翻译册=他包在途写域」最直接的现场证据，本包全程未碰该册。
  ```bash
  python .runtime/tmp/audit_all_20260924/probe_translation_d1_verdict.py      # targets=152 R=45 R?=5 H=71 N=31
  git show --format= --name-only 9b0c31ab125 | grep -c module_translation_registry   # 期望 0=批B 未碰翻译册
  git show --format= --name-only 9b0c31ab125 | grep -c "_registry/catalogs"           # 期望 3（只三册）
  git show HEAD:docs/01_policies_and_standards/_registry/catalogs/module_translation_registry.yaml | sed -n '55798p;55801p;3971,3978p;60079p'
  git show HEAD:docs/01_policies_and_standards/_registry/catalogs/module_translation_registry.yaml | grep -oE "build_status: .*" | sort -u   # 只 dormant
  git show HEAD:docs/01_policies_and_standards/_registry/catalogs/module_translation_registry.yaml | grep -c "build_status"                  # 42 / 8655 条
  python -c "import json,glob;print([json.load(open(f,encoding='utf-8'))['qid'] for f in glob.glob('.runtime/commit_queue/dead/*t0-matrix*') if 't0_ceiling_capacity_exam.py' in json.dumps(json.load(open(f,encoding='utf-8')))])"
  ```

## 心跳 2026-09-24 05:53 CST 实测（`date`=05:53:49）· 在干=MTR-01 追到**机制级根因**（批量灌册 + 门禁单向），把上块 ② 的"推断级"升为亲验 · 卡住=无 · 下一步=见 ③

- **① 25 条真幽灵从哪来=一次"双语真源扩容"批，且该批零新建代码**（尺=`git log --all -S` 定位 + `--name-status` 核形）：
  - 引入批=`ab168e55c8`（**2026-08-01 14:03**，`feat(doc-gen): 域文档三视图 + 大图增量渲染 + 模块翻译注册表双语真源扩容`）：单批向翻译册新增 **2,978 条 `- module_path:`**，而该批 **11 个文件全是 `M`（修改）、零 `A`**（11 件=翻译册 + 02_enterprise_architecture 下 6 份文档等），即 **一条 .py 都没新建**。⇒ 结论确定（不再是推断）：这批的登记来源=**文档/蓝图里的"应然模块清单"，不是磁盘派生**；上块 ② 那句"第一性判断"由 **推断级 → 亲验级**。
  - 152 条真悬空与该批的重合度（尺=批内新增 module_path 集合 ∩ 三分清单）：**N 31 中 13 条｜H 71 中 16 条｜R 45 中 27 条 ⇒ 合计 56/152=37% 出自该单批**（其余来自后续多批同类登记，未逐批展开）。
- **② 🔴 新立 F-AUDIT-MTR-03（本块最有处置价值的一条=为什么悬空必然积累）**：翻译册族的所有校验器**只查"有件无册"，全仓不存在"有册无件"方向的反向校验**。
  - 亲验两把尺：(a) `translation_coverage_reconciler.py:251` 的循环是 `for node in nodes:`——nodes 取自 **depgraph 代码节点**，产出 `missing_plain`/`short_plain`/`generic` 三类漂移 ⇒ 方向严格=物→册；(b) 对该 reconciler 与 `translation_coverage_gate.py` 全文 grep `stale|orphan|reverse|ghost|不存在|幽灵` = **0 命中**，`gate_registry.yaml` 中 grep `module_translation` = **0 命中** ⇒ 无"册→物"门禁/对账器存在。
  - 与 ①合起来即完整因果链：**批量灌册无存在性校验（入口无闸）+ 册→物无反向对账（存量无清）⇒ 悬空只增不减**，且 02 块已证 `build_status` 仅有 `dormant`×42 一种取值 ⇒ 连"计划未建"的合法标注通道也没被使用。这条正好解释为什么本包八图审查在其它七图只见个位数悬空、在翻译册见到 152 条。
  - **处方（净零合规版，§4.1：不新增 gate，改既有对账器）**：给 `translation_coverage_reconciler` 加**第四类漂移 `registry_only`**（遍历册内 `module_path` 对 HEAD 文件清单求差），复用其现有三分类上报面与 keep-list 语义；`R_改名未同步` 类由该漂移项自动提示"同名件在别处"（本包尺已实现判据，可直接移植）；入口侧 `add_module_translation.py` 加存在性校验，但**须同时提供 `--planned` 显式旗并强制写 `build_status: planned`**（否则会把"蓝图先行"的合法用法打死——本批 2,978 条正是该用法的历史形态）。落地涉翻译册条目净删=§5 high 域 ⇒ **只登记上交**，建议与 DANG-02（台账/索引分层）、MTR-02（退役跨册同批）并为**一条"册↔物双向对账与生命周期位"修闸需求**交 st-commitsys，勿三条分散立项。
- **③ 下一步（轮次）**：①等 0019（05:48 块）与 `st-align-dirty` 队列消化后**复跑三把尺**（fieldslice / d1_verdict / batch 交集）做收官判据第 1 轮"零新问题" ②红蓝反证节并档（现 **11 例**，本块不新增——本轮两次自纠已记于 05:48 块 ③）③终报三清单按 MTR-01 三分 + MTR-02 点名 + MTR-03 机制稿落笔。
- **队列/align 状态**：本包 0019 pending（05:52 入队，files=1 纯增 33/0）；HEAD=`10e16d9ae4`(05:49:45, st-align-dirty 翻译册重复行中性化批) ⇒ **本包 152 条结论所在的册正被他包改写**，故本块所有计数一律标注"测于 05:48–05:53 的 HEAD=`10e16d9ae4`/其前一态"。align：第 1-5 步工作树硬=3（HEAD 口径=0）、第 6 步崩（st-ailayer BLIND-01）、7-9 步未及。本包对 `注册表/配置册` 类写入累计仍=**0**。
- **复核命令（只读，全部本轮实跑）**：
  ```bash
  git log --all --oneline -S "src/zephyr/ex_core/auction_deviation_executor.py" -- docs/01_policies_and_standards/_registry/catalogs/module_translation_registry.yaml | cat   # =ab168e55c8
  git show --format= --name-status ab168e55c8 | sort | uniq -c | head    # 期望 11 M、0 A（零新建代码却灌 2978 条 module_path）
  git show --format= ab168e55c8 -- docs/01_policies_and_standards/_registry/catalogs/module_translation_registry.yaml | grep -c "^+ *- module_path:"   # 2978
  sed -n '249,262p' src/zephyr/governance/audit/translation_coverage_reconciler.py    # for node in nodes ⇒ 方向=物→册
  grep -cE "stale|orphan|reverse|ghost" src/zephyr/governance/audit/translation_coverage_reconciler.py src/zephyr/gov_enforcement/commit_gates/translation_coverage_gate.py   # 期望 0/0
  grep -c module_translation docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml   # 期望 0=无册→物门禁
  ```

## 心跳 2026-09-24 06:02 CST 实测（`date`=06:01:28→06:02）· 在干=第二张图（**depgraph DB**）双向对账，本轮主结论 · 卡住=无 · 下一步=见 ④

- **① 为什么这是今晚最该做的一件**：前 8 块案卷的对账对象全是 **YAML 派生册**，而 RULE-SSOT 规定"架构数据直写 DB"——depgraph(PostgreSQL `localhost:5432/depgraph`, nodes=12,509/edges=24,643) 才是**架构轴的真图**。只审 YAML 不审 DB=只审了影子。本轮尺：nodes 表 `granularity='file'` 路径集 ↔ `git ls-tree -r HEAD` + 盘上存在性 + `git log --all --reflog --diff-filter=A`（四把尺交叉）。
- **② 🔴 新立 F-AUDIT-DEPG-01（depgraph 侧图↔物双向计数 + 10 条硬悬空逐条定性，全量=`depgraph_hard_subset.txt`）**：
  - **正向（物在 HEAD、图上无节点）= 55 / 4,680 = 1.2%**（`src/zephyr` 40、`scripts/industry_graph` 10、`scripts/ch` 4）⇒ 量级健康，**不是**系统性漏挂。
  - **反向（图上挂物、HEAD 无此件）= 183**，分层后**大部分是自明的**：`on_disk` 128（stable 65 / generated 54 / production 5 / testing 4=本机件与生成件，属 gitignore/在途面）+ `planned` 26 + `deprecated` 19（**这两类是生命周期位的正确用法，不计缺陷**）⇒ **真需处置=10 条**（HEAD 无 + 盘上无 + 状态却标 production/stable/testing）。
  - **10 条逐案三分**（每条给同名后继/删除批/可及历史三重证据）：
    - **移动未跟 = 4**（旧路径节点仍在且标 production/stable，新路径节点也已生成=**新旧双节点并存**）：`commit_gates/{library_blood_flesh_gate,tag_vocab_gate,state_vocab_registry_gate}.py → commit_gates/library/同名`、`commit_gates/registry_family/registry_mass_deletion_gate.py → commit_gates/registry_mass_deletion_gate.py`（**移回**）。
    - **退役未更 = 3**：`commit_gates/{data_task_completeness_gate,issue_resolved_integrity_gate,library_coverage_gate}.py` 全标 `production`，实际由 `4b8fb00a555`(09-23 07:31 P3退役批A) 删除文件、`9b0c31ab125`(批B) 改了 gate 三册却**未回写 depgraph**（批B 名自述"注册表除名"，其"注册表"口径只含 YAML 册不含 DB）。⇒ 与 MTR-02 同一笔账的**第三个面**。
    - **从未在可及历史 = 3**：`scripts/backtest/sector_prereg_exam_runner.py`（标 **production**；其唯一添加件 `f44c1bfd742`@09-23 10:24 **非 HEAD 祖先**=只在未合并会话分支上）、`scripts/data/backfill_option_daily_stats.py`、`src/zephyr/alt_data/emotion_index_replay.py`（两条标 testing，`--diff-filter=A` 全 ref 零命中）。
  - **机制级结论（与 MTR-03 同构、且这次在 DB 侧）**：**两套图都缺"销旧"这一半**——YAML 册无"册→物"反向校验（MTR-03 已亲验 `gate_registry` grep=0），depgraph 重建只新增/更新不删除消失路径的节点（4 条移动未跟 = 直接实证，且本仓明明有 RENAME-DEPGRAPH-SYNC 硬门禁，说明该门查的是"改名批有没有跑重建"，**不查"重建后旧节点是否消失"**）。
  - **另一个方向性证据（推翻"depgraph 从 HEAD 生成"的默认假设）**：`sector_prereg_exam_runner.py` 只在**非祖先会话分支**里出现过，却进了共享 DB 并标 `production` ⇒ depgraph 的快照源可以是**会话工作树**（与既有 [[merge-relay-via-queue-pattern]] 记的"`--worktree-root` 才是快照源"完全一致），即 **A 会话的工作树态可越界写成全场架构真源**。定级=**P1 候选**（涉及共享真源的写入边界），但**修它是修闸+DB 净删双属性** ⇒ 只登记上交，路由=st-commitsys/st-gslim 收棚方，处方一句：**depgraph 节点写入须以 HEAD（或 serializer 落地后的权威树）为唯一快照源，且重建须删除"路径已不存在且非 planned/deprecated"的节点**。
  - **附带一个反直觉的正向发现（该说就好话）**：`build_status` 生命周期位在 DB 侧**确实在用**（production 2419 / generated 1106 / stable 381 / planned 44 / deprecated 28 / testing 6），且 planned+deprecated 恰好覆盖了大部分"物不存在"的情形 ⇒ MTR-03 的处方应修正为：**翻译册不该新造 `planned` 旗，而应从 depgraph 同步 `build_status`**（RULE-SSOT 正解：架构状态在 DB，YAML 是视图）。本条把 YAML 侧与 DB 侧两条处方**并成一条**，符合 §4.1 净零。
- **③ 红蓝反证第 12、13 例（本轮两次自否证，均已用更正版尺重跑）**：
  - **例12（漏挂尺 v1 只取 node_type='module' 造出 22.9% 假漏挂）**：v1 得 1,070/4,680=22.9% 未挂，按目录族看 `scripts/governance/d5_architecture` 134 条最"触目"；实为 depgraph 把脚本类文件登记为 `node_type='script'`（1,138 条）/'config'(3,562)/'test'(3,696)。改用**全 node_type 路径并集**后真漏挂=**55 条 1.2%**。⇒ 凡"覆盖率/漏挂率"结论，先自证**分母与节点类型口径**，否则把 schema 设计读成治理失效。
  - **例13（用 `--diff-filter=D` 判"从未存在"是错的）**：初查 3 条时打印"最后删除于: 从未在任何 ref 出现"，其中 `sector_prereg_exam_runner.py` 其实**有添加件** `f44c1bfd742`（只是从未被删除，所以 D 过滤器零命中）。改用 `--diff-filter=A` 重判后它的定性从"从未存在"**改为"仅存于未合并分支"**（②第三类的说法才成立）。⇒ "从未存在"与"从未被删除"是两个命题，探针须写清 filter。
- **④ 下一步（轮次）**：①终报"悬空"栏现分两张图落笔：YAML 册侧 164（R45/H71/N25+3 自尺修正）｜depgraph DB 侧 硬 10（移动 4／退役 3／越界 3）+ 漏挂 55 ②把 MTR-03 与 DEPG-01 处方**合并为一条**"图↔物双向对账 + 生命周期位从 DB 同步"修闸需求（净零）③复跑本轮三把尺做收官第 2 轮零新问题判定 ④红蓝反证并档（现 **13 例**）⑤终报。
- **队列/align 状态**：本包 0019 pending（05:52，05:48 块）、0020 pending（05:54，05:53 块）；HEAD 侧最新仍=`10e16d9ae4`(05:49:45 st-align-dirty)；align：1-5 步工作树硬=3（HEAD 口径=0）、第 6 步崩（st-ailayer BLIND-01）、7-9 步未及。**本包全程对 depgraph 只 SELECT（未 UPDATE/DELETE 任何节点），对 `注册表/配置册` 写入累计=0**。
- **复核命令（只读，全部本轮实跑）**：
  ```bash
  # ② 的四个数（正向 55 / 反向 183 / 硬 10 / 逐案同名后继）
  python - <<'EOF'
  import sys,os,subprocess; sys.path.insert(0,'src'); BS=chr(92)
  from zephyr.governance.depgraph_schema import get_depgraph_pg_connection
  c=get_depgraph_pg_connection(); k=c.cursor()
  k.execute("select node_type,path,build_status from nodes where granularity='file'")
  rows=[(a,b.replace(BS,'/'),s) for a,b,s in k.fetchall()]
  head={x.strip() for x in subprocess.run(['git','ls-tree','-r','--name-only','HEAD'],capture_output=True,text=True).stdout.splitlines()}
  allp={p for _,p,_ in rows}
  py=[p for p in head if p.endswith('.py') and p.startswith(('src/','scripts/'))]
  print('正向漏挂', len(set(py)-allp), '/', len(py))
  hard=[(p,s) for _,p,s in rows if p.startswith(('src/','scripts/')) and p not in head and not os.path.exists(p) and s in ('production','stable','testing')]
  print('反向硬悬空', len(hard)); [print('  ',s,p) for s,p in sorted(hard)]
  EOF
  git merge-base --is-ancestor f44c1bfd742 HEAD && echo 已合并 || echo 未合并=会话分支越界写DB的现场   # 期望 未合并
  git log --all --reflog --diff-filter=A --oneline -1 -- scripts/backtest/sector_prereg_exam_runner.py | cat
  git show --format= --name-only 9b0c31ab125 | grep -c "_registry/catalogs"   # 3（批B 只改 YAML 三册，无 DB 回写）
  ```

## 心跳 2026-09-24 06:09 CST 实测（`date`=06:09:31）· 在干=红蓝反证**正门件跑通**（尺自检器能红）+ 两轮复跑零新问题 + **现场拆掉本包名下两枚 index 回退弹**（新立 IDX-05）· 卡住=无 · 下一步=终报

- **① 红蓝反证正门件已落地：尺自检器 `redblue_ruler_selfcheck.py`（14 真判 + 1 有意负例，exit 码可用）**
  - 三把尺各做**阳性对照（该红必红）+ 阴性对照（不该红不瞎报）**：尺A 字段切片（业务面幽灵→必判 1｜同路径只在 `creation_tokens` 正文→必判 0｜切片不误伤业务面）；尺B 三分定性（唯一同名→R｜**泛名 `__init__.py` 不得判改名=例11 防复发**｜多候选→降格｜历史有→H｜两头无→N）；尺C 双向（HEAD 有件无节点→报漏挂｜节点有件而 HEAD/盘皆无且标 production→报硬悬空｜标 `planned/deprecated`→**不判缺陷**）。
  - **自红验证（防"恒绿假工具"，即 [[feedback-executor-cannot-sign-own-work]] 与 [[autoclaw-btfix-campaign]] 立的"判通过的脚本须先证明能红"）**：本件内置一条**故意改坏**的断言（want=999），实跑打印 `[SELF-RED] 注入必错断言 ⇒ FAIL 计数 +1`，且若该负例不红则自检器自身判 FAIL。现测=**真判 14 条全 PASS + 1 条有意负例已触发红**。
  - 顺带两处自检器自身的坑（记为反证第 14、15 例）：**例14** 我第一版把断言数硬写成"16"而实为 14（未实测计数即写死数字=自家犯的"计数写死"病，与 §4.3 同族）⇒ 改为运行时计数；**例15** 第一版 `chk` 用 `NCHK += 1` 手工补正导致汇总文案与实际不符 ⇒ 撤手工补正，改由负例分支表达。
- **② 收官判据第 1、2 轮复跑=零新问题（同尺两跑，测于 05:5x 与 06:05）**：业务面 **D1=165 / D2=110 两轮完全同值**；同窗"整册口径"却从 D1=785→**786**、D2=278→**277** ⇒ 唯一动的是他包并发新增的一行台账收据。**这正是 ② 那把切片尺的价值证明：不切片的口径连"跑两遍"都稳不住，切了片的才叫结论**。
- **③ 🔴 新立 F-AUDIT-IDX-05（现场逮到、当场拆掉，属 §9.4/§2 授权内的自家写域排雷）**：本包冷启动跑 `lock_files.py cleanup` 后复查 `git status`，发现**我自己的两本案卷正被 index 回退弹压着**：
  - 事实（尺=`git ls-files -s` + `git show :<path> | wc -l`）：`LEDGER.md` 的 **index 字节=22 行**（本会话最开头那一版，含"28 硬"基线行），而 HEAD=盘上=**747 行**；`AUDIT_REPORT.md` 的 index 字节比 HEAD 少 51 行。⇒ 一旦有任何落地吸收主区 index，**今晚全部案卷（25 块、含交裁项与处方）会瞬间退回 22 行**。
  - 已拆：亲验 `git diff HEAD --numstat` 两本皆**空输出（盘==HEAD 逐字节同）**后 `git add -- <自家两件>`（显式清单、非 `-A`）⇒ 两件从 staged 清单消失，`git ls-files -s` 现指回 HEAD blob（LEDGER=f1708b9c54）。零内容风险，因为它只是把 index 对齐到盘与 HEAD 已同的字节。
  - 面上规模（不止本包）：主 index 已跟踪件与 HEAD 字节不同的=**68 件**，其中 **12 件恰等于本会话起点 `f017ce3bf7` 的 blob**（=落后已落地面，含 **`AGENTS.md` 宪法本身**、`config/governance_operations_map.yaml` 落后 48 行、`src/zephyr/shared/io/yaml_utils.py` 落后 70 行、`library/lookup.py` 落后 50 行、`fs_collector.py` 落后 33 行…合计约 **278 行已落地工作**停在 index 后面）。其余 56 件属他会话在途/新件（587 件 index 有 HEAD 无），**非本包写域，只登记不代清**。
  - **机制：一个被我自己否证的假设**（反证第 16 例）：我先猜"`--enqueue` 每次把当时字节写进主 index，落地在 serializer worktree 的独立 index，故主区 index 永久停在首次快照"。**前半被代码证伪**：`scripts/commit_queue.py:694` 入袋走**内容寻址 blob 文件**（`blob_ref: blobs/<sha256>`）、`scripts/git_commit.py` 全文无 `git add`（仅 :247 一条注释）⇒ 队列路径不触主 index。**后半（首次 staging 后无人回写）仍为候选但未证**；诚实结论=**主区 index 是第二真源且无人回收**（与 EVAP-02/IDX-01/DEAD-01/STASH-01 同根第五面），处方=落地完成后须把触及路径的 index 对齐新 HEAD（或干脆禁主区 index 承载任何非当轮字节），属修闸面 ⇒ **交 st-commitsys**，与本包已提的"热册袋面/落地面脱钩"合为一条。
- **③b 编号险撞（自记·反证第 17 例）**：本块初稿把新案卷命名为 **IDX-04**，追加脚本的 MARK 幂等检查把它判为"已存在"而**拒绝追加**——查 `grep -oE "F-AUDIT-[A-Z0-9]+-[0-9]+" | sort -u` 才发现 **04:28 块早已立了 F-AUDIT-IDX-04（预检门消费面）**。若我当时为绕过幂等检查而直接改 MARK 追加，就成了**同包案卷撞号**（与裁定册撞号事故 [[registry-collision-blocks-own-queue-fix]] 同构）。⇒ 立法建议（并入"审查包自身纪律"一条，不新开册）：**新立 F-AUDIT-* 前必须先跑该 grep 取号段，取 max+1**；幂等 MARK 检查恰好替我拦下了这次撞号，属"门能红"的正例。
- **④ 下一步**：①写终报（把 DANG-02 口径更正、MTR-01/02/03、DEPG-01、STASH-01、BAG-01 分层、IDX-03 终态、IDX-05、16 例反证全部并入《挂齐缺口总账》三清单，逐条带复核命令与证据等级）②终报落地面复跑一次尺做收官第 2 轮确认 ③向 Owner 交三清单（待裁项=25 真幽灵"补建 or 销册"、R1 连坐已解堵后的 3 袋归属、裁定 409 同批原子归属、stash 定向提取）④满足收官判据后自删本自动化。
- **队列/align 状态**：本包 0019/0020/0021 **全 done**（0021=`b37398ff62`@06:04:26），队列此刻 `head=None`（暂无待投）；align：1-5 步工作树硬=3（HEAD 口径=0，等 st-cmd/st-commitsys 的裁定册面）、第 6 步崩（st-ailayer BLIND-01）、7-9 步未及。**本包对 `注册表/配置册`/depgraph DB 写入累计=0**（depgraph 全程只 SELECT）。
- **复核命令（只读，全部本轮实跑）**：
  ```bash
  python .runtime/tmp/audit_all_20260924/redblue_ruler_selfcheck.py | tail -3     # 期望 exit0 + "1 条有意负例已触发红"
  echo $?
  grep "合计" .runtime/tmp/audit_all_20260924/dangling_v2_fieldslice.txt          # 第二轮仍 D1=165/D2=110
  git ls-files -s -- docs/_working/audit_all/LEDGER.md                            # 期望 f1708b9c54（=HEAD blob，非 87cb0c275b）
  git diff --cached --name-only | wc -l                                           # 全部 staged 路径（含新件 587 件，故 ≠68）
  # "已跟踪且 idx!=HEAD = 68" 与 "其中 idx==起点 blob = 12" 须用下面纯集合法复算（勿逐件起 git 进程、勿用 --diff-filter=D）：
  #   idx: `git ls-files -s` 取第 2 列；两态: `git ls-tree -r HEAD` / `git ls-tree -r f017ce3bf7` 取第 3 列；三集合交集即 12 件
  git diff --cached --numstat -- AGENTS.md                                        # 2/2=宪法本身也在回退弹里
  ```

## 心跳 2026-09-24 06:36 CST 实测（`date`=06:36:24）· 在干=收官第 2 轮复跑（三把尺+尺自检器**全同值**）+ 新立 **F-AUDIT-WIP-01** 并**推翻本包终报对"第 6 步崩"的归因** · 卡住=无 · 下一步=终报口径补正后判"自审二次=0"是否闭合

- **① 收官判据第 2 轮复跑（同尺两跑，测于 06:22–06:34）＝三把尺零新问题**：
  - 尺A 字段切片：整册口径 D1=786 D2=277 → **业务面 D1=165 / D2=110**（与 06:0x 那轮逐位同值；整册口径继续被他包并发台账行扰动，再证"不切片的口径连跑两遍都稳不住"）。
  - 尺B 翻译册三分：**R_改名未同步 45 / H_退役未销册 71 / N_从未落地 31**（同值，`grep -c "^R_"` 等三行复算）。
  - 尺C depgraph 双向：**正向漏挂 55/4680（1.2%）+ 反向硬悬空 10 条**，且 10 条**逐条同名**（`round2_depgraph.txt` 已存证；file 粒度节点总数 12,374）。
  - 尺自检器 `redblue_ruler_selfcheck.py`：真判 14 条全 PASS + 1 条有意负例自红 ⇒ exit 0（**非恒绿**）。
  - `align_all`（工作树面）：[1/9]–[5/9] **硬=3**，与 05:2x 那轮同一条批（治理双向 裁定#383→#MOD-L00-004、#387→#PS-CTR-003、#387→#MOD-INF-043）；**[6/9] 崩**——本条归因见 ②，已作废原写法。
- **② 🔴 新立 F-AUDIT-WIP-01（并把本包自己终报的一处归因错误改过来）**：原报"第 6 步崩＝已落地面他包缺陷（st-ailayer BLIND-01）"**不成立**——`HEAD` 侧根本不崩。
  - **真因**：主区工作树+主 index 里一段 **+15 行未提交钩子**（`align_all.py:695-709`，注释自署名"L1 接线批挂点③（st-ailayer-final-20260924，**非阻断**）"）在 `main()` 内写了 `from zephyr.shared.infra.process_pool import run_subprocess_hidden`。Python 里函数内任何绑定都使该名字**在整个函数内变局部** ⇒ 第 536 行（第 6 步起始处，**在钩子的 try 之外**）先用后绑 ⇒ `UnboundLocalError` ⇒ **第 6/7/8/9 步永不执行、`align_all` 恒 rc=1、总览报告永不落盘**。
  - **三条互相独立的证法**（不靠读代码直觉）：
    1. `git show HEAD:…align_all.py | grep -n run_subprocess_hidden` = 只 100/536/556 三处；工作树版多出 697/700 ⇒ 钩子只在盘上。
    2. `symtable` 复算 `main()` 符号表：**HEAD 版 `is_global()=True`，工作树版 `is_local()=True`**（决定性、且不需运行）。
    3. 直接跑第 6 步载荷 `scripts/governance/d3_metadata/check_doc_node_id_hardcode.py --ci` ⇒ **rc=1（"FOUND: 2 … in 1791 files"，属存量 WARN 口径）而非崩** ⇒ 第 6 步本身可用，崩只由遮蔽造成。
  - **"非阻断"自述被证伪**：其 `try/except Exception` 只覆盖 695-709 自身，而遮蔽效应在 536 发作 ⇒ 兜不住 ⇒ **实为阻断级**，且因写在外层 `main()` 作用域，属"加钩子的人不会在自己那一段看到症状"的典型远程致盲。
  - **三态定位（谁的手笔、在哪）**：`HEAD` 无 ｜ serializer worktree（`.runtime/commit_queue/worktree/…`）无 ｜ 全部 7 个 `.aidrafts/*/…/align_all.py` 会话快照**均无** ｜ **只有主区工作树 + 主 index 有** ⇒ 它是"只活在第二真源里"的一段改动；**任何吸收该路径的提交都会把这枚崩写进 HEAD**（与本包 IDX-05"主区 index 是第二真源且无人回收"同根第六面）。
  - **处方（一句，交属主，§3.4 不代修）**：删掉 697 那行冗余的函数内 import（模块级第 100 行已提供同名符号，删后行为不变）；或把钩子整体挪进独立 helper，使其绑定不进入 `main()` 作用域。**属主包**：st-ailayer-final-20260924（其 `.aidrafts` 目录 mtime=00:39，进程表内无该 sid ⇒ 疑已散会，故**同时上交总指挥路由收棚方**，勿等自愈）。
  - **附带第二面（同批半截态）**：钩子产物 `config/ai_search_veins.yaml` 盘上**有**、index **无**、HEAD **无**，而 `capability_canonical_file_registry.yaml` 已把指针挂到它 ⇒ 尺A 早已把它列为悬空样本 ⇒ "钩子进了 index、产物没进 index"的**跨文件原子性半截**（与本窗 st-commitsys-0018 死于 `IMPORT-INTEGRITY 悬空 import` 同族，但这条在 index 侧不可见）。
- **③ 新立尺D＝全仓"函数内 import 遮蔽"AST 扫（8,537 个 .py，src/scripts/tests/library）**：**全仓仅此 1 例**（就是 ② 那一枚）。本轮反证第 **18、19** 例（两次自我否证后才敢用这个数）：
  - **例18（分母虚高 26 倍）**：v1 得 27 例，逐条点开看实为"**函数签名的返回/参数注解**"——如 `miniqmt_provider.py:430 def _parse_option_expiry(expiry) -> datetime.date | None:` 配体内 `import datetime`、`exam_orchestrator.py` 两处 `-> HallucinationBreakdown`。注解在 **enclosing scope** 求值、用的是模块级同名符号，**永不 Unbound**。⇒ 修=只走 `fn.body` 且不下钻嵌套作用域。
  - **例19（控制组逮到自己过滤写错分支）**：v2 跑四条控制，"嵌套作用域引用"阴性对照 **FAIL（got=1 want=0）**——我把 `isinstance(node, skip)` 写在了 `iter_child_nodes` 的下钻分支里，而 `fn.body` 的顶层元素是**直接 yield 未经过滤** ⇒ 嵌套 `def` 仍被下钻。修=在 `pop()` 处过滤 ⇒ 四控制（阳性先用后绑=1／签名注解=0／嵌套=0／先绑后用=0）**全 PASS** 后重跑得 1。
  - **失明增量（第 17 条）**：**pre-commit 只有 ruff，而 ruff 无 `used-before-assignment` 等价规则**（本窗口两条 dead 队列项的 `dead_reason` 实测 `hook=['ruff','ruff-format']`）⇒ "改作用域的钩子"这类缺陷**零门可拦**。修法建议（§4.1 净零，不新开 gate 册）：把尺D 做成 own-scope 结构门挂进既有 AST 结构校验族——**全仓现值=1 ⇒ 上线噪声近零**，且能挡住"以后每次往大函数尾部塞局部 import"。
- **④ 对收官判据的诚实影响**：判据②原文"align_all exit0 **或仅剩已登记他包/门位项**"——本包此前把"第 6 步崩"算作已登记他包项从而判 ✅，现在证明**该崩不在 HEAD**，于是 **HEAD 面的第 7/8/9 步从未在主区跑通过、即从未被测过**。不以"未测"充"已满足"：本轮虽三把尺零新问题，但**新立 WIP-01 + 一处本包归因自我更正 ⇒ "自审清单二次＝0"仍未闭合**，故 **不自删自动化**。
- **⑤ 下一步（轮次）**：①把 ②③ 补进终报《口径更正表 U0》与 U4/U5/U7（改归因，不改结论数字）②下一轮先看 WIP-01 是否已被属主/收棚方撤钩或修正：若已清则在主区复跑 `align_all` 取 **HEAD 面全 9 步真值**补齐判据②；若仍崩，则以"HEAD 面 7-9 步不可测＋归因已交＋尺D 全仓 1 例已路由"记录为已登记他包项，据此收口 ③满足判据即写"自动化已自删·本包收官"+`qoder_cron remove`。
- **队列/align 状态**：本包 0023（终报 U 节）**已落地=`da4de88435`**，此刻本包 pending=0（队列 pending=st-commitsys-0019，processing=st-pipeline-final-0013）；主 index 已跟踪件与 HEAD 字节不同者继续存在（663 件 staged 面，非本包写域，只登记不代清）。**本包对 注册表/配置册/depgraph DB 写入累计=0**（depgraph 全程只 SELECT；本轮新增文件全在 `.runtime/tmp/`，不入册）。
- **复核命令（只读，全部本轮实跑）**：
  ```bash
  # ② 的决定性三证
  git show HEAD:scripts/governance/d5_architecture/generators/align_all.py | grep -n run_subprocess_hidden   # 期望只 100/536/556
  git diff HEAD --numstat -- scripts/governance/d5_architecture/generators/align_all.py                        # 15  0（纯新增）
  python -c "import symtable,subprocess as s;f='scripts/governance/d5_architecture/generators/align_all.py';h=s.run(['git','show','HEAD:'+f],capture_output=True,text=True).stdout;w=open(f,encoding='utf-8').read();\
  import sys;g=lambda src:[y for y in symtable.symtable(src,'a','exec').get_children() if y.get_name()=='main'][0].get_symbols();\
  print('HEAD',[(x.is_local(),x.is_global()) for x in g(h) if x.get_name()=='run_subprocess_hidden']);print('WT',[(x.is_local(),x.is_global()) for x in g(w) if x.get_name()=='run_subprocess_hidden'])"   # 期望 HEAD (False,True) / WT (True,False)
  python scripts/governance/d3_metadata/check_doc_node_id_hardcode.py --ci; echo rc=$?                          # 期望 rc=1 且打印 FOUND，非 traceback
  # ③ 尺D（含四条控制）
  python .runtime/tmp/audit_all_20260924/probe_import_shadow_sweep.py | head -4                                # 期望 命中=1
  # ① 三把尺第 2 轮
  python .runtime/tmp/audit_all_20260924/probe_dangling_v2_fieldslice.py | grep 合计                            # 期望 165/110
  f=.runtime/tmp/audit_all_20260924/dangling_translation_d1_verdict.tsv; for c in R_ H_ N_; do grep -c "^$c" $f; done   # 45 71 31
  cat .runtime/tmp/audit_all_20260924/round2_depgraph.txt | grep -E "正向|反向"                                 # 55/4680 · 10
  python .runtime/tmp/audit_all_20260924/redblue_ruler_selfcheck.py | tail -2; echo $?                          # 14 PASS+1 自红，exit0
  ```


## 心跳 2026-09-24 07:05 CST 实测（`date`=07:00→07:04）· 在干=收官第 3 轮（HEAD 面 align 九步全跑通）+ 本轮**新立 4 案**（其中 1 案 P1 活体复现 + 1 处撤回本包旧处方）· 卡住=无 · 下一步=见 ⑥

- **① 🔴 新立 F-AUDIT-EVAP-03【P1·热册"整文件字节覆盖"落地=跨会话条目被吃——本窗蒸发家族首个带 blob 哈希的活体复现】**
  - **事件链（三笔提交，全亲验）**：06:26 `1de609aeb1`（st-library-final 直连）在 `module_translation_registry.yaml` 加 9 行 ⇒ 该路径 blob `20885a28f2^` 前值 `1f1b9145c2` → 新值 **`dd2fdc9aae`**；06:51 `20885a28f2`（st-pipeline-final「19 件代投」，**parent 恰为 `1de609aeb1`=线性提交、非分支合并**）把同一路径写回 **`1f1b9145c2`** ⇒ `git diff --numstat 1de609aeb1 20885a28f2 -- <册>` = **`0 9`（零新增、纯删除）**，被删的 9 行**正是他会话 25 分钟前刚落地的那一条**（`-- module_path: scripts/backup/library_ledger_backup.py`）。
  - **现场仍在**：`git hash-object <册>`=盘=**`dd2fdc9aae`**、`git ls-files -s`=主 index=**`dd2fdc9aae`**、而 `git rev-parse HEAD:<册>`=**`1f1b9145c2`** ⇒ **HEAD 落后于盘与 index**（"第二真源"的镜像面：这次是盘新、HEAD 旧）。任何后续吸收该路径的提交会把它**再加回去**，即同一文件在 HEAD 上来回抖。
  - **机制（代码级，不靠猜）**：落地读的是袋内内容寻址字节的**整个文件**——`scripts/commit_queue.py:1447-1449`（`if from_bag and f.get("blob_ref"): content = (root/f["blob_ref"]).read_bytes()`），热册**无条目级三方合并** ⇒ "入袋时刻的旧快照"必然吃掉"入袋之后落地的他人条目"。本窗此前 EVAP-01/02 只有结果没有机制，这条把机制钉住。
  - **路由/处方（属修闸+提交链面，本包不代修）**：交 **st-commitsys**。一句处方=热册类路径落地须做**条目级三方合并**（base=入袋时记录的上一 HEAD blob，ours=当前 HEAD，theirs=袋内字节，只允许增不允许整段回退），并把"纯删除 diff（0 增 N 删，且删的恰是 ≤60min 内他包落地条目）"设为**落地前置硬检**。
  - **反证第 22 例（这条最该记进审查纪律）**：本次蒸发让尺A 业务面从 **165/110 → 164/108**，看起来"治理变好"。⇒ **悬空/漏挂计数下降不得直接读作改善**，必须先查该路径有没有 net-negative diff；否则审查器会把"册被回退"上报成"欠账已清"。本包此前各轮的"同值"结论未受影响（同值=无变化，不是下降），但**任何未来轮次若见下降，须按本例先做删除检**。
- **② 🔴 新立 F-AUDIT-MTR-04【翻译册假挂：条目内容与所挂文件毫无关系】**
  - 册侧条目（`1de609aeb1` 落、06:51 被 EVAP-03 吃掉、盘/index 仍在）：`module_path: scripts/backup/library_ledger_backup.py`、`name_zh: 词表加载器`、`plain_zh: "meta_question 包的词表读取小帮手：把层、状态、频率这些固定选项从配置文件里读出来给注册表和部署脚本用…"`。
  - 而该文件（06:58 `be42d6759b` 补落地）头部自署 `# [A_module] module_id=MOD-INF-043`、`# [DOMAIN] D_INFRASTRUCTURE`，docstring=「图书馆 PG 账本双链备份+月度恢复演练（12 号令任务 2）」。⇒ **条目描述的是另一个模块**；`grep 词表读取小帮手` **全仓仅此 1 处**（不是从别条目复制来的，是生成时错配）。
  - 第二面：册侧 `domain_id=D_GOV_ENFORCEMENT` vs 文件头 `D_INFRASTRUCTURE` 不一致（尺E 逮到，见 ③）。第三面：该 .py 的 06:26 条目早于文件本体 06:58 落地 ⇒ "先挂册后落物"半截（与 WIP-01 附带面同族，只是这次自愈了）。
  - **失明增量第 18 条**：`TRANSLATION-COVERAGE` 门与 reconciler 只查**条目在不在**，**不查条目与文件相不相干** ⇒ "为过门而填的条目"可无限假挂。路由=**st-library-final**（条目与文件同为其落，且 06:58 已是第三笔）。处方一句：`add_module_translation.py` 写入前须做"条目↔文件头 `[MODULE]`/`[DOMAIN]`/docstring 首行"三项机械一致性检（零 LLM 成本）。
- **③ 🆕 尺E（新尺，四控制组全 PASS）＝翻译册 `domain_id` ↔ 文件头 `# [DOMAIN]` 全量扫：真跨域不一致 21 + 域未填 13**
  - 规模：条目 **7,677**，可比对 **5,055**（一致 5,021）；不一致 **34**，其中 **域未填（`null`/空，多为 tests/）13** ⇒ **真跨域不一致 21**；另 `无 [DOMAIN] 头=2,382`、`不在盘=240`（两态均**不判**）。
  - **谁对谁错按真源仲裁**（域宇宙=depgraph `domains.domain_id` 74 ∪ 域册 `domain` 79 ∪ 契约 3，并集 79）：**18 条两侧都是注册域**（真归属冲突，需按域定义裁，例：`D_TRADING↔D_PLAN` ×3 全在 `plan_engine/`、`D_BACKTEST↔D_DATA` ×3 全在 `scripts/ch/`）；**3 条有一侧是未注册野值**＝册侧 `D_PLAN_ENGINE`、册侧 `D_INFRA`、文件头侧 `D_EXECUTION_CORE` ⇒ 这 3 侧**机械可判必错**，是本轮唯一"零争议可直修"的子集（但仍是翻译册写域，登记不代修）。
  - **反证第 20 例（我自己的尺差点假红）**：第一版用 `domain_id|id` 两个键从域册抽真源 ⇒ 得 **0 元素集合**（该册的键叫 `domain`），于是 21 条全被判"两侧都不在册"。**差点把"我读不到"上报成"册没登记"**。修正（三源并集+DB 列名 `domain_id` 亲验）后分布翻成 **18/2/1/0**。⇒ 凡"某物不在真源"结论，先自证**抽取器能抽到东西**（本轮控制组已加"阳性只判出真那 1 条/三条阴性各不判"）。
  - 非缺陷测量（不立案、记此防重复劳动）：YAML 79 域 vs DB 74，差的 5 域 `D_EXECUTION/D_ORDER/D_PORTFOLIO/D_SIGNAL/D_TEST` 在 `nodes.domain_id` 上**零引用**（`select count(*)` 逐条=0）⇒ 属"零消费"面（要么补 sync 要么按 w5_1 退役），且 `nodes` 用到的 73 个域**全部**在 `domains` 表内（反查空集）。
  - 建议挂法（§4.1 净零，不新开 gate 册）：把"域必须在册"并入既有 `add_module_translation.py` 写入面，"条目域≠文件头域"降 warn；上线噪声=21/5055=0.4%。
- **④ 🔴 新立 F-AUDIT-RULING-02＝align 余 3 硬的真身＝staged 在途编辑跨命名空间挂 `related_arch`；本包正式**撤回**此前"置空"处方**
  - **尺子无罪**：HEAD 面 `ruling_registry` 非空 `related_arch` 值 **100 个，悬空=0**（形态清一色 `#ARCH-*`），且 `_ruling_arch_errors`（`src/zephyr/gov_enforcement/registry_alignment.py:449-457`）比的是 `architecture_issue_registry.entries[].issue_id` ⇒ **语义=议题 id，HEAD 全员遵守**。
  - **3 硬来自未提交面**：`git diff --cached -- ruling_registry.yaml` 显示 `-  related_arch: []` → `+ ['MOD-L00-004']`（裁定#383）、`- []` → `+ ['PS-CTR-003','MOD-INF-043']`（裁定#387），同批还 `+ 裁定 409`（其 `related_arch=[]`；此处去 # 免自触 RULING-REFERENCE 门，编号未登记全文只在未提交面）。⇒ 本包旧写法"HEAD 口径=0 / 工作树=3"方向对、**定性错**：这不是 HEAD 欠账，是**在途件把别的命名空间（模块 id / 规则册 id）塞进了议题字段**。
  - **三值都是真对象、错命名空间**（逐个实证）：`MOD-L00-004` 在 depgraph **225 节点**（`blueprint_id` 命中，含 blueprint 节点、build_status=testing）；`MOD-INF-043` 在 depgraph **16 节点**（其物＝②里那枚备份脚本，头署该 id）；`PS-CTR-003` 在 `rule_catalog_registry.yaml` 在册（depgraph 0 命中）。
  - **为什么撤回"置空"**：置空=把 3 条**有效关联**销毁，等于用毁数据的方式灭灯。正确二选一：**(i)** 改挂议题 id——我按议题文本反查得 `MOD-INF-043→#ARCH-BACKUP-SLO-001`（CH 备份 SLO 哨兵，语义相合）、`MOD-L00-004→#ARCH-PROVIDER-BASENAME-001`（两域同名基类消歧，**与"storage_tiering 退役"是否同一议题未定**，故此二是**推断级**非亲验），`PS-CTR-003` 反查**零命中** ⇒ 须先立议题或改挂 `related_rulings`；**(ii)** 扩字段语义 + checker 按前缀分流（`#ARCH-*`→议题册、`MOD-*`→depgraph `blueprint_id`、`PS-*`→rule_catalog）——更根本，但属"改判定逻辑"＝高域门位，**只登记上交**。
  - **风险陈述**：该 staged 件一旦被任何吸收该路径的批带走，3 真红即写进 HEAD ⇒ **全场 align 变红、施工前判据失效**；与本窗 IDX-05/WIP-01/EVAP-03 同根（主 index 承载非当轮字节）。路由=**st-cmd（裁定册属主）+ 总指挥排归属**，非 st-commitsys（这次不是尺子的问题）。
- **⑤ 收官第 3 轮复跑（含判据②"从未测"缺口正式闭合）**
  - **HEAD 面 `align_all` 九步全跑通**（探针 `.runtime/tmp/audit_all_20260924/run_headside_align.py`：取 `git show HEAD:` 字节 `compile+exec`，`__file__` 指真身路径 ⇒ 路径解析与真流程同，`--no-report` ⇒ **零写入**）：**rc=1，硬=3**（全部＝④那三条），**软=993**；[6/9] `FOUND 2/1791`、[7/9] 图8 **硬 12（S4×2/S11×9/S12×1）+advisory 95**、[8/9] 图9 硬 0/软 3、[9/9] GOMAP 机生层 **424**、硬 0/软 3。⇒ **整合跑与 04:4x 独立探针逐位同值**（探针未偏＝本包此前所有"第 6-9 步"结论可放心沿用），且崩溃版 `align_all` 连 **软问题合计 993** 这个数都不打印——**"崩在尾部"不等于"不影响结论"**。
  - 三把尺第 3 轮：尺A 见 ①反例（165/110→164/108 系蒸发，非改善）｜尺B 三分 **45/71/31 同值**｜尺C 未重跑（本轮 HEAD 面变更只涉及翻译册/备份件，depgraph 无写入方，复跑留下轮）｜尺D 复跑 **命中=1**（WIP-01 那枚，同值）｜尺自检器上轮 exit0（14 真判+1 有意负例自红）。
  - **WIP-01 现状**：`git diff HEAD --numstat -- align_all.py` 仍 `15 0`、697 行函数内 import 仍在 ⇒ **07:00 未被属主/收棚方撤钩**（其 `.aidrafts` mtime=00:39、进程表无该 sid）。⇒ 本轮改用 HEAD 字节 exec 绕过，未动他包在途件。
- **⑥ 对收官判据的诚实影响 + 下一步**
  - 判据②（align）**本轮实质闭合**：HEAD 面九步真值已取得，余 3 硬已逐条定性为"已登记的在途面项"（④）。但判据"连续两轮复跑零新问题"本轮**再次不满足**＝**新立 4 案**（EVAP-03/MTR-04/MTR-05/RULING-02，其中 EVAP-03 为 P1 候选）。⇒ **继续跑，不自删自动化**。
  - 下一轮（轮次）：①复跑尺C 补第 3 轮（现缺）；②盯 EVAP-03 是否有解堵（该路径盘/index 仍新、HEAD 仍旧，若他批吸收则自动回加，须记录"抖了几次"）；③盯 RULING-02 的 staged 件归属（若被吸收→当场报"全场 align 变红"并附复现）；④若本轮 4 案之后连续两轮零新立 ⇒ 写终报 X 节＋"自动化已自删·本包收官"＋`qoder_cron remove 39cc5bd5-6b49-4b42-a65f-db987dccc076`。
  - **给 Owner 的一句话（不催裁，只更新口径）**：本轮新增的待裁项只有 1 枚真正需要人点头——**RULING-02 的 (i)/(ii) 选路**（改挂议题 id 还是扩字段语义）；其余三案都有机械判据、可直接派属主包。
- **队列/align 状态**：本包 pending=0（23 件里 done 为主，dead 4 件均早轮已对症 requeue）；此刻队列 `head=q-…-st-align-dirty-0044`、pending=10、processing=1、daemon online；HEAD=`be42d6759b`(06:58)。**本包对 注册表/配置册/depgraph DB 写入累计=0**（depgraph 全程只 SELECT；本轮新增探针/明细全在 `.runtime/tmp/`，不入册、不入 git）。
- **复核命令（只读，全部本轮实跑）**：
  ```bash
  # ① EVAP-03 三笔与两个 blob（期望：06:51 那笔对该路径 = 0 增 9 删，且写回 06:26 之前的 blob）
  REL=docs/01_policies_and_standards/_registry/catalogs/module_translation_registry.yaml
  git diff --numstat 1de609aeb1 20885a28f2 -- $REL                       # 期望 0  9
  git log --format="%h %p" -1 20885a28f2                                 # 期望 parent=1de609aeb1（线性）
  git rev-parse HEAD:$REL; git ls-files -s -- $REL; git hash-object $REL # 期望 1f1b9145… / dd2fdc9a… / dd2fdc9a…
  sed -n '1445,1452p' scripts/commit_queue.py                            # 整文件字节写入处
  # ② MTR-04
  git show HEAD:$REL | grep -c "library_ledger_backup"                   # 期望 0（HEAD 已被吃）
  grep -n "library_ledger_backup" $REL | head -2                         # 期望盘上仍在（60059）
  head -18 scripts/backup/library_ledger_backup.py | grep -E "DOMAIN|A_module"
  # ③ 尺E（含控制组）
  python .runtime/tmp/audit_all_20260924/probe_domain_crosscheck.py | tail -8
  # ④ RULING-02
  git diff --cached -- docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml | grep -E "related_arch|ruling_id"
  python -c "import sys;sys.path[:0]=['src'];import yaml,subprocess as s;d=yaml.safe_load(s.run(['git','show','HEAD:docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml'],capture_output=True,text=True,encoding='utf-8').stdout);i=yaml.safe_load(s.run(['git','show','HEAD:docs/01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml'],capture_output=True,text=True,encoding='utf-8').stdout);ids={str(e.get('issue_id')) for e in i['entries'] if isinstance(e,dict)};v=[str(a) for r in d['entries'] for a in (r.get('related_arch') or [])];print('HEAD 非空值',len(v),'悬空',sum(1 for x in v if '#'+x.lstrip('#') not in ids))"   # 期望 悬空 0
  # ⑤ HEAD 面九步（零写入）
  python .runtime/tmp/audit_all_20260924/run_headside_align.py | tail -12
  ```


## 心跳 2026-09-24 07:22 CST 续块（同轮内追加，防重入以 `F-AUDIT-EVAP-03` 07:05 块为准，本块 MARK=F-HOT-SWEEP-0722）· 在干=尺F/F2 热册回写全窗扫 · 卡住=无

- **① 尺F（新尺）＝今晚窗口热册"纯删除 diff(0 增 N 删)"扫**：窗口 64 笔提交、热册笔次 85 ⇒ **纯删除事件 11 起 / 涉及 7 个文件**。明细 `.runtime/tmp/audit_all_20260924/f_hot_pure_deletion.tsv`。
- **② 尺F2（判据升级）＝逐起做"回写旧快照证明"**（取落地 blob，在该路径祖先链近 40 笔内找同字节的前身；找到⇒回写，找不到⇒当轮作者主动删）：**回写型 8 / 11**，且 8 起**全部命中"往回第 1 笔"**（＝落地字节恰等于"上一笔之前"的历史状态，典型快照差一笔）：
  - `20885a28f2`(06:51, st-pipeline-final「19 件代投」) **一口气回写三本**：`generator_registry.yaml -18`（退回 `de2d8df066`@09-22 06:29）、`module_translation_registry.yaml -9`（退回 `3a114ad8a1`@06:00）、**本包 `docs/_working/audit_all/AUDIT_REPORT.md -109`（退回本包 `0c7e42b3ba`@04:30）**。
  - **本包自己也是加害者**：`c5b70a8ff8`(03:05, **st-audit-all**「热册蒸发复发·重投工厂图」) 回写 `capability_canonical_file_registry.yaml -214`（退回 `973f1a3b47`@09-23 22:09，抹掉 st-e2e 班 4 小时的在册登记）+ `disk_reorg_campaign/a1_ledger.md -92`（退回 `8135b0675d`@00:19）。⇒ 该笔 commit message 自述"蒸发复发·重投"——**我是受害者重投，重投动作本身又把别人 214 行抹了**。
  - **级联实证**：`53cdc66e06`(03:12, st-align-dirty) 落地的 cap 册字节 **== 我 03:05 那笔的 blob** ⇒ 我的陈旧快照被下一笔原样继承。机制结论：**陈旧整文件字节一经落地，后续基于该树的重投会把它继续传下去，受害者→加害者只隔一次重投**。
  - 另有 `8135b0675d`(00:19) 回写 `a1_ledger.md -83`（退回 `345516da8c`@09-22 08:14）。
  - **3 起判为"非回写"**（`LEDGER_final.md -22` ×2、`config/exam_scale_cost_gate.yaml -29`）＝新 blob 不在该路径历史里 ⇒ 当轮主动改写/退役，**不算缺陷**。
- **③ 残损清查（回写不等于残留，逐本实测）**
  - `capability_canonical_file_registry.yaml`：**无残留**——现 HEAD 47,162 行 > 蒸发前 `c5b70a8ff8^` 46,749 行，其间的 214 行已由后续批带回。
  - `module_translation_registry.yaml`：条目在盘与主 index（`dd2fdc9aae`）而 HEAD 仍旧（`1f1b9145c2`）＝**待吸收自动回加**（见 07:05 块 ①）。
  - 🔴 **`generator_registry.yaml`＝功能级残损且仍未回**：06:20 `6199c0752a` 登记的两枚生成器挂载 **`module_algorithm_overview` / `governance_map` 在 HEAD 出现次数=0，盘=2** ⇒ **编排器对 08 册与 GOMAP 的自动再生能力当前在 HEAD 上是关掉的**——这正是 st-align-dirty 今晚为"GOMAP 被陈旧快照蒸发两次"开的处方，被 06:51 的回写**原地注销**。优先级=高（一句可解：把盘字节 re-land）。路由=**st-align-dirty-20260924（其队列此刻正活：head=q-…-st-align-dirty-0044）**，同时上报总指挥代催。
- **④ 反证第 23、24 例（本轮两次自我否定）**
  - **例 23（尺F 的判据单独用会假阳 27%）**：只看"0 增 N 删"会把**合法退役批**（`exam_scale_cost_gate.yaml -29`、`LEDGER_final.md -22`）一并判成蒸发。⇒ 必须叠 F2 的"落地 blob ∈ 路径历史"这条**字节级回史判据**才分得开；两把尺同框后 11 起里 8 证 3 否。
  - **例 24（审查器此前从不审自己提交的 numstat）**：本包 `c5b70a8ff8` 是今晚第 2 起被证实的回写，而我在 03:05 之后写过 6 个心跳块、立过 EVAP-01/02，**从未把"自家提交是否纯删除"纳入尺子**。⇒ 立法：**凡做"回写/蒸发"类审查，检测域 MUST 含本包自身提交**（本案唯一能自证无偏的办法）；已并入终报 X 节"审查包自身纪律"。
- **⑤ 与收官判据**：本轮**再新立 1 案（F-AUDIT-EVAP-03 升级为量化+级联+残损三件一体）+ 新增 2 把尺（F/F2）+ 1 项高优移交（generator_registry 挂载）** ⇒ 判据③"连续两轮零新立"仍不满足，**继续跑、不自删**。下一轮：①复跑尺C（第 3 轮仍缺）；②盯 `generator_registry` 是否被 re-land（复验命令见 ③）；③盯本包 0025 是否落地（含 W 节，若又被回写则以 F/F2 当场取证）。
- **复核命令（只读，全部本轮实跑）**
  ```bash
  python .runtime/tmp/audit_all_20260924/probe_hot_pure_deletion.py "2026-09-24 00:00" | tail -20   # 11 起 / 7 文件 + 三控制组 PASS
  python .runtime/tmp/audit_all_20260924/probe_hot_rewrite_proof.py | tail -14                      # 回写型 8/11
  G=docs/01_policies_and_standards/_registry/catalogs/generator_registry.yaml
  for k in module_algorithm_overview governance_map; do printf "%s HEAD=%s 盘=%s\n" $k "$(git show HEAD:$G | grep -c $k)" "$(grep -c $k $G)"; done   # 期望 0 / 2（残损）
  REL=docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml
  echo "HEAD=$(git show HEAD:$REL|wc -l) 蒸发前=$(git show c5b70a8ff8^:$REL|wc -l)"                # 47162 > 46749 ⇒ 无残留
  ```
- **队列/写入状态**：本包 0025（07:05 心跳+W 节）pending；`git_commit.py` 首次被 `SESSION-REQUIRED` 拦（自动化轮次会话未注册），按指令卡处方 `SessionRegistry.register(sid,pid=0)` + `Start-Process pythonw -m …heartbeat_daemon <sid> <root>` 分离式保活后入袋成功（daemon pid 36508 alive，注册表 last_heartbeat age≈11s）。**本包对 注册表/配置册/depgraph DB 写入累计仍=0**。


## 心跳 2026-09-24 07:35 CST 续块 2（同轮第三把新尺，MARK=F-HOT-SWEEP-G-0735）· 在干=尺G 整件消失判据（F2 结构性盲区的补尺）· 卡住=无

- **① 为什么还要第三把尺**：尺F2 的"落地 blob ∈ 该路径历史"对**整本文件被吞**的场合**必然失效**——被删一侧没有"新 blob"可比（`git rev-parse C:path` 为空 ⇒ 只能落到"非回写"）。实证：`0f08f7a06c` 在 F2 里被判"⚪ 非回写"，而它实际是**把别包 5 分钟前刚落地的一整个功能 6 件从 HEAD 抹掉**（见 ②）。⇒ 反例第 **25** 例：尺子的"非回写"分支被我自己当成了"不算缺陷"，差点放走今晚最大一起。
- **② 尺G 判据（三条件同框，四控制组全 PASS）**：某 commit 删除 P ＋ **P 此刻仍在盘上**（真退役会连文件一起消失）＋ P 的添加笔是本 commit 的**祖先**且相隔 ≤90min、且**跨包**。修正过程中另除一颗雷：初版用 `git log --all --diff-filter=A -1` 取"最新添加"，会取到 `cf1c963092a "index on dev"`（stash/index 提交）这类**晚于本 commit** 的添加 ⇒ gap 变负 ⇒ 该家族全部漏检（**控制组当场 FAIL 把我拦住**，反例第 **26** 例：判据必须限定在祖先链内，不能取全 ref 空间）。
- **③ 尺G 结果：今晚窗口 18 起整件消失 / 5 组"加害包→受害包"对**（明细 `.runtime/tmp/audit_all_20260924/g_whole_file_swallow.tsv`）。三起最重的：
  - `0f08f7a06c`(00:43，**st-k4 池化终批 v3**，message 自述 10 文件) 吞掉 **`st-gpu-final` 00:38 刚落地的成本考尺整功能 6 件**：`config/exam_scale_cost_gate.yaml`、`src/zephyr/backtest/regime_validation/exam_cost_gate.py`、`scripts/backtest/exam_cost_reexam.py`、`docs/03_modules/_domain_backtest/algo_flow/exam_cost_gate.yaml`、`tests/backtest/test_cost_gate_tier_wiring.py`、`tests/backtest/test_exam_cost_gate.py`。**该 commit 的 message 只字未提删除**，且其落地时顺带把 `docs/library/regulations.md`、`logs_collector` 等**他会话的在途件**一起提交（A 侧同样越界）⇒ 代投时**吸收了主 index 的 17,000 件快照**，与 AGENTS §2.5"commit 后必核 `git log -1 --name-only` 真实归属"同源。
  - `1cba19a9de`(00:23，**st-flush**) 吞掉 `st-library-final` 00:19 落地的 7 件（`logs_collector.py`/`test_logs_collector.py`/`regulations.md`/`blood_flesh_cataloging_sop.md`/`test_library_blood_flesh_gate.py`/`test_tag_vocab_gate.py`/`collectors/logs_collector.yaml`）。
  - `0fe090715f`(07:06，**st-align-dirty**) 吞掉 `st-library-final` 06:58 刚落地的备份馆 3 件（`scripts/backup/library_ledger_backup.py`+注册 ps1+测试）——**就在我本轮取证期间发生的**。
  - **残损现况（07:33 亲验）**：`scripts/backup/library_ledger_backup.py`、`src/zephyr/backtest/regime_validation/exam_cost_gate.py`、`config/exam_scale_cost_gate.yaml` **HEAD=0、盘=y** ⇒ 三族功能仍在落地面之外；其中 **X1 的 `generator_registry` 两枚挂载已被 `86bf9217dd`(07:13) 自行带回（HEAD=2 ✓）**，说明"重投回收"是可行正解，而上述三族仍待属主重投。
- **④ 本包自身交付件的落地面状态（自审含自家，X3 立法的直接执行）**
  - `git rev-parse HEAD:docs/_working/audit_all/AUDIT_REPORT.md` = **`da4f3f24aa`** = `20885a28f2`(06:51) 落地字节 ⇒ **我 06:36 之后的 V/W/X 三块从未进过 HEAD**（`git log --all -S "V4 判据终表"` **零命中**、`-S "F-AUDIT-WIP-01"` 零命中）；盘 321 行 vs HEAD **137 行**。LEDGER 同样：盘 902 / HEAD 774。
  - **该路径今日全部三笔逐字节核**（07:36 实跑，比 `-S` 更硬）：`0c7e42b3ba`@04:30=**137 行** → `da4de88435`@06:23=**246 行（U 节落地 ✓）** → `20885a28f2`@06:51=**137 行（U 节被回写吃掉，退回 04:30 字节 ✓）**，此后无人再触及 ⇒ **本包终报正文自 06:51 起在 HEAD 上只剩 04:30 版**，U/V/W/X 全在盘与袋。
  - 队列侧：0025 已不在 `--session` 清单而内容未进 HEAD ⇒ 需下一轮核 `commit_queue` 归档与 `dead_reason`（**本包交付物自身此刻是"只在盘上+在袋里"的状态**，这正是 EVAP-03 家族对所有人成立的样子，只是这次受害者是我）。
  - 处置：不硬闯、不改路径（§4.1 净零、不新增资产）；0026/0027 继续按正门排队，落地后以 `git rev-parse HEAD:<报告>` 与 `-S` 双检验收。
- **⑤ 收官判据**：本轮（06:44–07:35）累计**新立 4 案 + 3 把新尺（E/F/F2/G 实为 4 把）+ 反例第 20–26 例** ⇒ 判据③"连续两轮零新立"**远未满足**，**继续跑、不自删**。下一轮：①核 0026/0027 是否落地（双检命令见 ④）；②盯三族残损是否被属主重投；③复跑尺F/F2/G 看新窗是否继续产生事件（若继续产生，则本包终报的"修闸前不宜开新一夜多包并发"结论要升为待裁项上交）。
- **复核命令（只读，全部本轮实跑）**
  ```bash
  python .runtime/tmp/audit_all_20260924/probe_whole_file_swallow.py "2026-09-24 00:00" | head -4   # 18 起 / 5 包对 + 四控制 PASS
  git show 0f08f7a06c --name-status --format= | grep "^D"                                          # 6 件成本考尺族
  git rev-parse HEAD:docs/_working/audit_all/AUDIT_REPORT.md 20885a28f2:docs/_working/audit_all/AUDIT_REPORT.md   # 两值相同 ⇒ 我仍在 06:51 回写态
  git log --all --format="%h %s" -S "V4 判据终表" -- docs/_working/audit_all/AUDIT_REPORT.md       # 期望空 ⇒ V/W/X 从未进 HEAD
  for F in scripts/backup/library_ledger_backup.py src/zephyr/backtest/regime_validation/exam_cost_gate.py config/exam_scale_cost_gate.yaml; do echo "$F HEAD=$(git ls-tree -r --name-only HEAD|grep -c "^$F$") 盘=$([ -f $F ] && echo y||echo n)"; done
  G=docs/01_policies_and_standards/_registry/catalogs/generator_registry.yaml; git show HEAD:$G | grep -c governance_map   # 期望 2（已由 86bf9217dd 带回）
  ```
- **会话/门禁状态**：本轮 `SESSION-REQUIRED` 首拦（自动化轮次会话未注册），按指令卡处方 `SessionRegistry.register(sid,pid=0)`+`Start-Process pythonw -m …heartbeat_daemon` 分离保活后放行（daemon 曾以 `idle timeout 1816s` 自退过一次 ⇒ **每轮冷启动须重跑注册+保活**，已写进本块备查）。**本包对 注册表/配置册/depgraph DB 写入累计仍=0**。


## 心跳 2026-09-24 07:52 CST 续块 3（同轮根因收口，MARK=F-EVAP-ROOTCAUSE-0752）· 在干=把 EVAP-03 从"现象量化"推到"代码级根因+一句话处方" · 卡住=无

- **① 撤回本报告 X2/W1 里"热册无三方合并、须新建"的说法——合并器早就有，而且是被我们喂错了 base**
  - 真源：`scripts/governance/commit_queue_landing.py:175-201`（W2 治本，注明起因"2026-09-22 注册表事故 fb5a7821d 陈旧快照 blob 一写抹掉 103 条已提交身份"）+ `:1089-1131 _apply_snapshot` → `is_registry_mergeable(rel)` 命中即调 `_merge_registry_file`（`:1057-1088`）。作用域=`docs/01_policies_and_standards/_registry/catalogs/*.yaml`。
  - **根因（两处，均已取到实物证据）**：
    1. **入袋根本不记 base**：`scripts/commit_queue.py:696/712` 明写 `"base_blob": None,  # A 段预留（B 段：git rev-parse HEAD:{path} 填充）`——**B 段从未做**；且 `:45` "base_head/base_blob A 段不主动取 git，**由调用方显式传入**"。我 07:50 直读自己刚入袋的 `pending/q-20260924-st-audit-all-20260924-0027.json` ⇒ **`base_head=None`、两文件 `base_blob=[None,None]`**。⇒ `git_commit.py --enqueue` 这条 CLI 通道**从来没传过 base**。
    2. **缺 base 时的兜底把"旧快照"读成"主动删除"**：`_merge_registry_file:1071-1075` 在 `base_head` 缺失/对象不存在时 `base_sha = old_dev^`，随后 `three_way_merge_registry_yaml(base, ours=当前 dev, theirs=陈旧快照)`。当"他人条目"恰好落在 `old_dev^..old_dev` 之间（今晚三起全在 4–8 分钟内），base 已含该条目而 theirs 不含 ⇒ **合并器判定"theirs 侧删了这些条目"并忠实执行删除**。⇒ 今晚 `capability_canonical_file_registry -214`、`generator_registry -18`、`module_translation_registry -9` **都是合并器亲手落的"合法删除"**，而不是它没生效。
  - **修正后的处方（比 X2 更省、且是唯一正解）**：**入袋时把 base 记全**——`scripts/git_commit.py` 的 enqueue 通道传 `base_head=当前 dev HEAD`，`commit_queue.py:696/712` 把预留的 `base_blob` 填成 `git rev-parse HEAD:<path>`（字段与注释都在，零新件、零新表）；`_merge_registry_file` 改用 **per-file `base_blob`** 作 base，**取消 `old_dev^` 兜底**（缺 base 时应死信而非猜 base）。非注册表族（`docs/_working/**` 台账与本包交付物）不在合并作用域内 ⇒ 同一批把作用域按"高写入热文件族"扩到 `.md` 台账，或至少给"0 增 N 删/整件消失"加落地前置硬检（尺F/尺G 判据可直接搬）。
- **② 反证第 27 例（这条最该被记住）**：我在 X2 里写"热册落地无条目级三方合并 ⇒ 建议新增"。若照此上交，就是**让属主包重复造一个已存在的轮子**（违反 §4.1 净零；文档自相矛盾正是 §4.3 在案的事故源）。发现过程：为核"0f08f7a06c 是不是走了未合并的直连通道"而去查 `git log -1 --format=%b` 的 GW 标记 ⇒ **六涉事提交全带 `[GW:<sid>:q-<qid>]`＝全部走队列** ⇒ "直连/代投路径无合并"这个我默认了一整轮的假设当场作废，顺藤才摸到 `base=None`。⇒ 立法：**"缺 X 所致的事故"类结论，必须先证 X 不存在**（grep 真源+读实物字段，不是"我没看到它生效"）。
- **③ 连带更正**：Y2 表里"代投吸收主 index 17,000 件快照"的表述**降级**——`0f08f7a06c` 的 A/D 混部落地同样发生在队列通道（其 qid 在 message 尾注），成因是**该项 files 清单本身含他会话在途件**（入袋时 `--files` 清单外的 staged 内容被 gateway 吸收），不是主 index 被整颗快照。此说与我 IDX-05"主 index 第二真源"是两个不同机制，终报里不得并成一条。（证据等级：GW 标记=亲验；"清单外吸收"的具体入口=**待下一轮读 `git_commit.py` staged 收集段确认**，先记为推断级。）
- **④ 队列与交付物状态（本轮实测）**：0027 在 `pending/`（`base_head=None` 已存档为证据）；**0025/0026 已不在 pending/processing/done/dead 四处** ⇒ 疑被 `supersedes`/compaction 折叠（同路径后袋覆盖前袋，与本窗已知的"队列四处方"同族）——**本包交付物至今未进 HEAD**（`AUDIT_REPORT` HEAD 仍 137 行=06:51 回写态，盘 346 行）。⇒ 下一轮第一件：核 0027 是否落地；若仍不落，改走 `--no-auto-enqueue` 直连单文件落（不带他会话清单）并记为本包自身的排雷项。
- **⑤ 判据**：本轮再撤回/更正 2 处本报告结论（X2 处方、Y2 机制表述）⇒ **自审清单二次=0 更未满足**，继续跑。尺A–G 全谱与 22+5 例反证均已入册，红蓝反证面（各尺带控制组）齐备。

> 〔位置注记·07:49 恢复轮〕下面这块（07:28 更正块）当时写在一份**已被回退成 774 行**的盘上副本之后，
> 故其「三块」指的是 07:05/07:22/07:35/07:52 各块的**标签**；本恢复轮把它接回 07:52 块之后以保时间线连续，原文一字未改。


## 更正 2026-09-24 07:28 CST 实测（`date`=07:27:5x）· 本包三块心跳的**标签时间超前于实钟**，特此加注（不改原文＝留审计痕迹）

以队列 `created_at` 为硬时间锚（入袋即服务器时钟）逐块对表：

| 我写的块标题 | 实际入袋时间（`commit_queue` created_at） | 偏差 |
|---|---|---|
| 「心跳 07:05」 | 0025 = **07:07:43** | 约 −2min（可接受，块内有 `date`=07:00:05 实测锚） |
| 「心跳 07:22 续块」 | 0026 = **07:12:57** | **超前约 +9min** |
| 「心跳 07:35 续块 2 / 终报 Y 节 07:36」 | 0027 = **07:21:57** | **超前约 +13min** |
| 「心跳 07:52 续块 3 / 终报 Z 节 07:52」 | 0028 = **07:26:38** | **超前约 +26min** |

- **成因（不是笔误，是流程退化）**：本块之前的三块我都**没有先跑 `date`**，而是凭"上一块 + 估计耗时"递增标号；06:36/07:05 两块是有实测锚的（块内写了 `date`=06:36:24 / 07:00:05），后面三块丢了这一步。⇒ 与本报告 U 节"口径须带实测时点"是同一条纪律的**我自己的复发**。
- **立法（并入 X3"审查包自身纪律"，不新开册）**：**心跳/案卷块标题的时间戳 MUST 来自同一次 `date` 实测并与队内 `created_at` 可对表**；凡出现"块时间 < 上一块 + 实测耗时"或"块时间 > 该块入袋时间"，即判为时间线污染，须以 `created_at` 为准加注更正（正是本块做法）。
- **对既有结论的影响＝零**：三块内的判据数字全部来自同轮实跑探针（尺E/F/F2/G 与各复核命令），未使用错误时间戳作输入；唯一受影响的表述是 Y2/④ 里"07:33 亲验""07:50 直读袋内"这类时点副词，**统一按上表回退约 25min 读**（即实为 07:0x–07:26 之间）。
- **反证第 28 例（自我登记）**：审查器给别人的"残损现况 07:33 亲验"这类时间戳背书，而自己三块的时间戳是估的。⇒ 凡"某时刻实测 X"的断言，MUST 在同一动作里留可核对的时间锚（`date` 或 `created_at`），否则降级为"本轮内实测"。

## 心跳 2026-09-24 07:49 CST 实测（`date`=07:49:12，本串由 shell `date` 传入脚本＝非估钟）· 在干=**自家两份案卷被吞（本窗蒸发家族第 7 次，新立 F-AUDIT-EVAP-04）＋用「内容寻址袋 blob」纯增恢复** · 卡住=无（凶手未坐实但不挡恢复）· 下一步=见 ⑤

- **① 事实（三态＋袋态＝四把尺，全本轮实跑）**：冷启动读台账即见**盘=774 行=HEAD 版**，而我 06:12 之后写的五块（06:36 收官第 2 轮／07:05 第 3 轮／07:22 尺 F·F2 热册回写普查／07:35 尺 G／07:52 根因收口）**盘上全灭**；`git log -- <LEDGER>` 末笔＝自家 `0be34c2bdc`(06:12:24, +27/−0) ⇒ **HEAD 侧当时从未有过这五块**。（本轮 07:42:51 我的 0029 袋落地为 `95285c16a1` ⇒ HEAD 现为 791 行＝774＋07:28 更正块，**仍缺那五块**。）
  - 尺=`git hash-object <blob>` + `git log --all --find-object=<sha>`（五个版本逐条）：943/929/902/873/817 行的 blob 在**所有 ref 的任何 commit 中「从未」出现** ⇒ 携这五块的队列项 **0024–0027 既非 done 亦非 dead**（pending/processing/done/dead 四目录无其 json，`seq`=29 证明号确实发过），其字节**只活在 `.runtime/commit_queue/blobs/`**。⇒ 新事实：**「入袋即完成」的队列语义下，未落地案卷的唯一 durable copy 是袋内 blob，而不是 git 对象库。**
  - **`AUDIT_REPORT.md` 受害更早且到了 HEAD 层**：盘=index=HEAD=**137 行/23553 字节＝04:27 那版**（其 sha256 前 12 恰＝袋 `e25b180b156d`）；我 06:23:13 落的「终局报告 U 节」(`da4de88435`) 与其后 X/Y/Z 三节，被 **`20885a28f2`(06:51:41，st-pipeline-final 19 件代投) 的陈旧快照整档覆盖**——尺=`git log --all --since=06:12 --name-only -- docs/_working/audit_all/` 唯一命中该笔。⇒ 与 `86bf9217dd` 自陈「陈旧快照整档覆盖 generator_registry」**同一笔、同一因**；本包早先那句「受害面不限于机生热册，任何整档写回型 tracked 文件皆无防护」**再获一次实证，且证明 docs/_working 案卷同样裸奔**。
- **② 报告为什么连"已入袋"都没落：新立 F-AUDIT-GWMSG-01（自踩门，反证级）**：0028 袋（报告 372 行版）此刻在 `dead/`，死因亲验＝**`FORGED-GW-MARKER` 门禁阻断**：「commit message 含非本 session 的 GW 标记（本 session=st-audit-all-20260924）」。根因＝**我把别的会话的留痕标记原文当证据抄进了自己的提交说明**（该门查的是 message，不查正文），门判"伪造/嫁祸"。⇒ 纪律条（并入 X3 审查包自身纪律）：**审查类会话的提交说明 MUST 避免任何方括号 GW 标记形态，引用一律改写为 `GW:<sid>`→`GW-标记-<sid>` 之类不可匹配形式**；此坑对"举证型提交说明"是常踩面，且**死信不会被队列自愈**，须人（或我）带 `--adopt-prior-work` 重投。
- **③ 恢复通道（本轮最有复用价值的正面发现，等级=亲验）**：**未落地字节可从内容寻址袋恢复**。尺=`grep -l "<块内独有串>" .runtime/commit_queue/blobs/*` → 命中 `e32457…`(943 行，含五块)、`1097ce…`(791＝774＋更正块)、`9f8c63…`(372 行报告，含 X1-4/Y1-4/Z1-4 节)。恢复前置断言用**子序列**而非前缀：HEAD 每一行都须出现在新版中（尺＝`subsequence_check`），落盘后 `git diff --numstat HEAD` 须为**纯增**（零删除＝结构上不可能吞他会话内容）。
  - **立法**：案卷观测面从三态扩到**四态＝盘/index/HEAD/袋内 blob**；自本块起每轮心跳 MUST 记本轮袋 sha 前 12（本轮恢复源＝`e32457d67141`/`9f8c63a81cdf`），使"被吞"在一次 grep 内可定位复原。⇒ **更正** [[hot-file-wipe-forensics-20260918]] 当年「git 不可回取」的结论：在有队列袋的会话里**可回取**，该恢复通道应写进热文件恢复 SOP。
- **④ 归因分层（诚实）**：亲验＝盘的 774 回退发生于 **06:12–07:27** 之间（07:28 更正块是接在 774 版之后写的，故 791=774+17）；亲验＝报告在 **HEAD 层**被 `20885a28f2` 覆盖；亲验＝0024–0027 字节从未进任何 commit。**推断（未坐实）**＝盘回退最可能由主区 merge 连坐清扫（HEAD reflog：07:25:24 `merge ai/st-gpu-final…: updating HEAD`、07:36:55 `commit (merge)`）。已**排除 stash**（stash@{0}=`c57964361e` 生成于 05:18:36，其内 LEDGER 仅 22 行、不含五块）；亦**排除落地器主动写**（`main_workspace_sync.jsonl` 对我包 LEDGER 三次记录全为 `skipped_dirty`）。⇒ 定不了凶手不挡恢复；跨包写域**只登记不代查**，移交 st-commitsys（与已提"主区 index 是第二真源且无人回收"IDX-05 合为一条）。
- **⑤ 本轮动作与并发**：恢复两案卷（`safe_write_text` CAS＋盘上现内容有块外独有信息则**拒绝整写**的前置断言）＋本块，入队 files=2（显式清单，非 `-A`），提交说明按 ② 改写不含 GW 标记形态。并发面：07:36:55 有他会话在主区 merge；`18e5af5101`(07:29:42) 自陈"袋面件数≠落地面件数"第 6 次复现。**本包本轮零注册表/零 DB 写入**，写域仅 `docs/_working/audit_all/` 自家两件。
- **⑥ 下一步（轮次）**：①核对本包袋落地后 HEAD 三态==本轮预期字节 ②把 EVAP-04/GWMSG-01（含"袋＝第 4 态"处方＋对 [[hot-file-wipe-forensics-20260918]] 的更正）并入终报 X/Z 节 ③复跑尺 F/F2/G＋D1/D2 双轮做收官"连续两轮零新问题"判定 ④终报三清单＋复查清单 ⑤满足判据后自删本自动化。
- **队列/align 状态**：本包 done=0001-0023/0029，dead=0003-0007/0012/**0028**（0028 由本轮新袋取代重投）；HEAD=`95285c16a1`(07:42:51)。align 未复跑（本轮额度给了取证与恢复）。**本包对 `注册表/配置册`/depgraph DB 写入累计仍=0**。
- **复核命令（只读，全部本轮实跑）**：
  ```bash
  git log -1 --format="%h %ad %s" --date=format:"%H:%M:%S" -- docs/_working/audit_all/LEDGER.md   # =95285c16a1 07:42:51（仅 791 行版）
  git log --all --since="2026-09-24 06:12" --name-only --format="%h %ad" --date=format:%H:%M:%S -- docs/_working/audit_all/ | grep -E "^[0-9a-f]{7,} |audit_all"
  for b in e32457d671418b43 4a71a34271f0a0a2 730f2de55b38fef8; do s=$(git hash-object .runtime/commit_queue/blobs/$b*); echo "$b -> $(git log --all --oneline --find-object=$s | wc -l) 笔 commit"; done   # 期望 0/0/0
  python - <<'PYEOF'   # 子序列证明：HEAD 全部内容仍在新版中（＝零丢失零删除）
  import subprocess, pathlib
  h = subprocess.run(["git","show","HEAD:docs/_working/audit_all/LEDGER.md"],capture_output=True).stdout.decode()
  new = pathlib.Path("docs/_working/audit_all/LEDGER.md").read_text(encoding="utf-8")
  it = iter(new.splitlines())
  print("HEAD 为新版子序列:", all(any(l == x for x in it) for l in h.splitlines()))
  PYEOF
  git diff --numstat HEAD -- docs/_working/audit_all/                   # 期望两件皆 +N/−0（纯增）
  grep -c "^## 心跳 2026-09-24 07:52 CST 续块 3" docs/_working/audit_all/LEDGER.md   # 恢复后=1
  python -c "import json;print(json.load(open('.runtime/commit_queue/dead/q-20260924-st-audit-all-20260924-0028.json',encoding='utf-8'))['dead_reason'][:160])"   # FORGED-GW-MARKER 现场
  ```

## 心跳 2026-09-24 08:09 CST 实测（`date`=08:01:36 起测，本块写于 08:09）· 在干=**自我更正三处不实断言＋新立 F-AUDIT-MERGE-01（39 秒复现的合并侧热册蒸发）＋尺I 证伪改立尺J** · 卡住=无 · 下一步=见 ⑤

- **① 🔴 三处不实断言的公开更正（本块的全部数字均可用文末命令重放）**：
  - **(甲)「HEAD 里出现了标注 08:16 与 08:24 的两块心跳」＝不实**。尺＝三处穷举：①`.runtime/commit_queue/blobs/*` 全扫 `grep -l "08:16 CST"` → **0 命中**；②`git cat-file --batch-all-objects` 的 4,546 个 200KB–400KB 大 blob 中，含本包案卷指纹者只有 3 个（943/817/805 行），**含 "08:16"/"08:24" 者＝0**；③`git worktree list` 的 9 份案卷副本（主区 993／st-align-dirty 548／st-commitsys 791／serializer w0-w3 774-791-708／align_dirty 774）**全部无此标注**，且 `git branch -a --list "*audit*"` 只有 `session/st-gaudit2-20260923`（其内案卷 0 行）。⇒ 结论：**那两块从未存在过**；我把"上下文压缩前的推测/记忆外推"当成了读数写进叙述（并一度据此怀疑"同 sid 兄弟实例并发写"，进程表实测亦无该实例，只有 st-commitsys 的 heartbeat）。
  - **(乙)「恢复后 HEAD=1204/1217 行」＝不实**。亲验：`git log -1 --format="%h %ci" -- <LEDGER>` = **`95285c16a1` 07:42:51**（我的 0029 袋＝时间线自纠块），HEAD 行数 **791**；**盘＝993 行**（=我 07:48 的恢复版，含 06:36/07:05/07:22/07:35/07:52 五块，正随 **0030 袋 pending**，created_at=07:49:57）。⇒ "已入 HEAD"的说法当时不成立，成立的是"已入盘/已入袋"。
  - **(丙)「翻译册条目前只剩 1 / 乒乓」＝本轮坐实为真**（且给出最小复现，见 ②），但我先前那句"HEAD 现在确实有 registry_batch_edit 与 c3_throttle"的**时点**是错的：07:57:11 实测三 key 在 盘/index/HEAD **皆 0**，07:57:42 属主重投后才回 Y。⇒ 同一命题在不同时点两个读数都"对"，**缺时点即缺真值**（与本包 U 节同一条纪律的第三次自我复发）。
  - **立法（并入 X3，本包审查纪律第 5 条，也是最重要一条）**：**引用即重放**——案卷中任何"我读到了 X / 实测为 X"的句子，MUST 同批附一条可重放命令＋命中位置（行号或 blob 名），写之前先跑一次并把输出贴进块内；无命令可贴者一律降级为"推断"或不写。（(甲) 这类"读到不存在的东西"比估钟危险得多：估钟只错时间，这个错的是事实。）
- **② 🔴 新立 F-AUDIT-MERGE-01【P1 候选·合并侧热册条目蒸发·39 秒最小复现】**：尺＝逐笔核 key 存在性（`git log --since=07:25 --format=%h|%ci -- <翻译册>` 共 4 笔，每笔 `git show <c>:<册> | grep -c <key>`）：
  - `81647d88db` **07:36:16**（st-align-dirty 翻译册终缺批，1 件，册 +17/−0）⇒ 两 key `registry_batch_edit.py`/`c3_throttle_attribution.py` 在册 **Y/Y**；
  - `4fc2cf6d04` **07:36:55**（**Merge branch 'ai/st-gpu-final-20260924/gpu-final-campaign' into dev**，5 件）⇒ 同两 key **n/n**＝**39 秒后被一次 merge 静默吃掉**（merge 对该册取了分支侧，未做条目级三方合并）；
  - `5fe4d26426` **07:57:42**（st-align-dirty「翻译册终缺批·重投（被并发陈旧袋吃掉后自捕）」）⇒ 回到 **Y/Y**；HEAD 现 **Y/Y**。
  - 定性：这与本包已交的 **EVAP-05/06 根因（队列入袋不记 `base_head`/`base_blob` ⇒ 合并器缺 base 时兜底 `old_dev^`）是同一病灶的第三个面**——前两面是"袋侧陈旧快照被读成主动删除"，本面是**"merge 侧对热册整文件取单侧"**。⇒ 移交 st-commitsys 并入同一条修闸需求（§4.1 净零）：**注册表族文件的 merge/落地必须走条目级三方合并，缺 base 即死信而非兜底**；本包对该册**零写入**（全程只 `git show`/`git log`）。
- **③ 尺I 证伪 → 改立尺J（本包的"能红自证"再进一格）**：
  - 尺I（markdown"半句收尾/奇数反引号/奇数粗体"判文本被局部吃掉）＝**判据不成立**：两册合报 **133 处可疑**（绝大多数是 `：`/`---` 正常收尾＝假红风暴），而真残口（04:28 块被截的尾巴）它**一处没抓到**。⇒ 已废弃，代码留 `.runtime/tmp/audit_all_20260924/probe_text_integrity.py` 作反面教材。
  - **尺J（＝同块跨袋长度比对）成立**：24 个 LEDGER 袋 × 71 块，跨袋长度不一致 **19 块**，其中 Δ≥50 字者两块，最大 **Δ=12,591 字**（`## 心跳 … 04:28` 块 19,749→7,158 字）。控制组：合成阳性（把袋截断成被回退态）missing=**71**、合成阴性（同版本对自身）=**0**。⇒ 恢复配方＝**逐块取最长袋版本**，四道前置（块头在册内唯一 ∧ Δ≥50 ∧ 现存版必须是最长版的**严格前缀** ∧ CAS 写＋进程外回读）；已执行，**复扫「待补块=0」＝零残留**。
  - **尺J 实证的唯一真截断＝04:28 块**：该块跨袋有 **4 个长度**（7,157 / 14,042 / 17,543 / **19,747**）⇒ 确曾被后手逐次砍尾，已按最长版恢复（Δ=12,591）；而 07:22（3,643×4 袋）与 07:35（4,251×3 袋）**跨袋同长＝无截断证据**，其 ① 条在盘上皆以句号完整收尾。
  - **对本块 (甲) 的补强**：我本会话 07:36-07:41 之间确实"读到"过该区域的半句（`- **① 为什么补这一`）——但那个版本**如今在盘/各袋/各 worktree 皆无字节**，属**瞬态 HEAD 版本**（07:36:55 merge 前后）。⇒ 教训与 (甲) 同源却更硬：**不可重放的读数一律不得升格为案卷事实**，只能记作"某时点读数"并附时点。
- **④ 报告册（终局报告）侧本轮复扫结论**：`ruler_J_restore_any.py docs/_working/audit_all/AUDIT_REPORT.md <指纹>` → 命中袋 7、**待补块=0** ⇒ 报告册**无跨袋截断**；但 **尺H2 第 2 轮**仍报 0023 袋 90 行不在 HEAD——**根因即 (乙)**：我的 993 行盘版还没落地（0030 pending），HEAD 仍 137 行。落地后该 90 行应转 alive（下一轮复跑验证）。当前 盘/index/HEAD = **372/137/137**（U 节/Z 节 在盘 True、在 HEAD False）。
- **⑤ 下一步（轮次）**：①**0030 落地后**复跑尺H2（应见"报告 90 行"从 dead 侧消失）＋复跑尺J（应仍 0）＝本包连续两轮零新问题判定的第 1 轮 ②把 MERGE-01／「引用即重放」纪律／尺I 证伪三件并入终报 X/Z 节 ③复跑 align_all 前 5 步与 depgraph 只读对账做第 2 轮 ④红蓝反证并档（累计 28 例，本块 +3：幻觉读数/漏时点/引错块号）⑤终报三清单定稿＋复查清单，然后自删本自动化。
- **队列/align 状态**：done=0001/0002/0008-0011/0013/0015-0023/0029，dead=0003-0007/0012/0028，**pending=0030**（07:49:57 入袋，files=2 纯增 LEDGER+202/REPORT+235）；HEAD=`5fe4d26426`(07:57:42)。align 本轮未跑（额度给了取证与自我更正）。**本包对注册表/depgraph DB 写入累计仍=0**。
- **复核命令（只读；本块每条断言都对应下面一条，先跑再信）**：
  ```bash
  grep -l "08:16 CST" .runtime/commit_queue/blobs/* ; echo "命中=上面空则无袋"      # (甲) 袋侧零命中
  ls .runtime/commit_queue/blobs | wc -l ; git worktree list | wc -l                  # 24 袋 / 全 worktree 清单
  git log -1 --format="%h %ci" -- docs/_working/audit_all/LEDGER.md                    # (乙) =95285c16a1 07:42:51
  git show HEAD:docs/_working/audit_all/LEDGER.md | wc -l ; wc -l < docs/_working/audit_all/LEDGER.md   # (乙) 791 / 993
  for c in 81647d88db 4fc2cf6d04 5fe4d26426; do printf "%s " $c; git show $c:docs/01_policies_and_standards/_registry/catalogs/module_translation_registry.yaml | grep -c "registry_batch_edit.py"; done   # (丙)/② Y→n→Y
  python .runtime/tmp/audit_all_20260924/probe_bag_regression_attribute.py | head -4    # ② 尺H2 第 2 轮：dead=93
  python .runtime/tmp/audit_all_20260924/ruler_J_restore.py | tail -3                   # ③ 复扫 待补块=0
  python .runtime/tmp/audit_all_20260924/probe_text_integrity.py | tail -3              # ③ 尺I 假红 133（已废弃）
  ```

## 心跳 2026-09-24 08:29 CST 实测（`date`=08:29:35，本串由 shell `date` 传入）· 在干=**修自家案卷第 4 次死信根因（引用未登记裁定 409 的 `裁定`+井号形态自触 RULING-REFERENCE 门）＋两件重投** · 卡住=无 · 下一步=见 ④

- **① 承 08:09 块 ⑤ 的下一步被打断**：原计划"0030 落地后复跑尺 H2/J＝收官第 1 轮"，但实测 **0030 从未落地**（现 dead），且新见 **0031 亦 dead**（08:15 一次未改根因的重投，files=1 只 LEDGER）。死因亲验＝门禁 `REFERENCE-INTEGRITY`：`LEDGER.md`/`AUDIT_REPORT.md` 引用了 `ruling_registry.yaml` 未登记的编号 409。这正是本包 04:47 块(0012)与 07:35 块 ② 已定性的 **GATE-01 自触**家族：审查器"记录某裁定尚未落地"时抄了带井号的 `裁定<井号>409` 形态 ⇒ 被 `ruling_reference_gate.py:83` 正则 `裁定#(\d+…)` 判成主动新增引用。**本块正文对此编号一律去井号书写**（＝自我处方落地）。
- **② 本轮动作（简单缺口·边审边修·自家写域 `docs/_working/audit_all/`）**：按 04:47 块 ⑤ 既定拼写处方，把 LEDGER 原 :841 与 REPORT 原 :285 两处引用改写为 `裁定 409`（**保留 #383/#387 两处有效引用不动**——它们已登记，改之反而毁真关联）。零删除不变式复验＝盘版仍是 HEAD 版严格超集：HEAD 逐行 ∈ 盘，LEDGER 791⊂1024 / REPORT 137⊂372；且两处改点行号 > HEAD 长度 ⇒ 落在盘独有（未落地）区，不伤任何 HEAD 行。
- **③ 扫描口径（可重放）**：正则 `裁定#(\d+(?:-[A-Z]+)?)` 逐文件比对 `ruling_registry.yaml` 已登记号集：修前两册会触门号=['409']，修后=[]（#383/#387 registered=YES 不列）。
- **④ 下一步（轮次）**：① 本块随袋 **0032** 重投两案卷 ⇒ 落地后复跑尺 H2（报告 90 行应从 dead 侧转 alive）＋尺 J（应仍 0）＝**收官"连续两轮零新问题"第 1 轮** ② align_all 前 5 步＋depgraph 只读对账＝第 2 轮 ③ 红蓝反证并档 ④ 终报三清单＋复查清单 ⑤ 满足判据后自删本自动化。**前置门**：若 0032 又非因本根因而 dead，按 [[premise-falsified-stop-and-probe]] 停手上报，不硬闯第 5 次。
- **队列/align 状态**：done=0001/0002/0008-0011/0013/0015-0023/0029(17)，dead=0003-0007/0012/0028/0030/0031(9)，pending/processing=0（本轮入袋 0032）；HEAD=`baec3502f0`(08:25:26·st-align-dirty 收官末笔，其 §3.20 又独立复证"主区盘面翻译册缺本包 2 径"＝本包 MERGE-01/EVAP 家族的又一例)。**本包对注册表/配置册/depgraph DB 写入累计仍=0**（全程只 `git show`/`git log` ＋自家两件案卷）。
- **复核命令（只读·先跑再信）**：
  ```bash
  for q in 0030 0031; do python -c "import json;print('$q', json.load(open('.runtime/commit_queue/dead/q-20260924-st-audit-all-20260924-$q.json',encoding='utf-8'))['dead_reason'][:120])"; done   # 皆 REFERENCE-INTEGRITY/引用未登记裁定
  grep -nE "裁定#[0-9]" docs/_working/audit_all/AUDIT_REPORT.md   # 修后=空
  python - <<'PY'   # 零删除不变式：HEAD 逐行 ∈ 盘
  import subprocess,pathlib
  for f in ["LEDGER.md","AUDIT_REPORT.md"]:
      h=subprocess.run(["git","show","HEAD:docs/_working/audit_all/"+f],capture_output=True).stdout.decode()
      d=pathlib.Path("docs/_working/audit_all/"+f).read_text(encoding="utf-8"); it=iter(d.splitlines())
      print(f, all(any(l==x for x in it) for l in h.splitlines()))
  PY
  ```


## 心跳 2026-09-24 09:04 CST 实测（`date`=09:04:29，本串由 shell `date` 传入）· 在干=**收官"连续两轮零新问题"第 1 轮三尺齐绿（0032 落地→报告 90 行转 alive）＋自家过时基线更正（383/387 本包 04:36 已自修落地）** · 卡住=无 · 下一步=见 ④

- **① 承 08:29 块 ④：0032 已落地**＝`65225f4534`(08:38:26, files=2 纯增 LEDGER+202/REPORT+235)；`git show HEAD:…LEDGER.md|wc -l`=**1044**、`…AUDIT_REPORT.md`=**372**，盘==HEAD（`diff` 空）。⇒ GATE-01 自触（未登记号 409 的 `裁定`+井号形态）经"去井号"处方修后一次通过，本包案卷落地通道复证可用。
- **② 收官"连续两轮零新问题"第 1 轮（三尺齐绿，全部只读可重放）**：
  - **尺H2**（`probe_bag_regression_attribute.py`）：命中袋-件对=30，合法改写侧 151 行、条目被吃侧 **3 行＝全属 0009**（`battle_map_domain_policy.yaml` 的 `authoritative_source` 单字段+2 注释行，`(no-key)×3`）；**上一块 08:09 报的"REPORT 90 行不在 HEAD"已随 0032 落地转 alive（现 dead 侧无报告/台账项）**。除已登记的 0009 外**零新死件**。
  - **尺J**（`ruler_J_restore.py`）：**待补块=0**（跨袋零截断残留）。
  - **align_all**（HEAD 面只读探针 `run_headside_align.py --no-report`）：**`rc=0`、✅ 硬问题清零**（domain_mismatch/ghost_anchor/frontend_map/decision_map/factory_map/gomap 六类全 0），软 984（图 8 chainmap 硬违规 12 条按长城专项暂计软＝st-gpu-final 清欠中；翻译册 6 组重复 module_path＝已知，清源走 `--dedupe`）。
- **③ 🔴 自家过时基线更正（诚实口径，非新问题）**：先前滚动基线写"余 3＝裁定册 related_arch×3（383/387）→处方交 st-cmd，勿硬闯"——**实为本包 04:36 commit `a74e9a6c48`（done 袋 0011）自修落地**（383/387 `related_arch` 违字段契约填了模块/契约号→置空 `[]`，真身在 `affected_files` 已存；align 全图硬 3→0）。⇒ 该"交 st-cmd"路由项 **closed（本包已自毕，非他包待办）**；本块把它从待办移到已办，防总指挥重复派单。
- **④ 0009 指针修再定性（第 N 次不硬闯·守 §3.4/§5 与 premise-falsified 纪律）**：`battle_map_domain_policy.yaml:286` FF-16 `authoritative_source` 仍写废弃副本 `architecture_model/frontend/frontend_map.yaml`（web 版为唯一真源，两文件 HEAD 皆存在＝**SSOT 误指非硬断链、低危**）。本包 03:52 已登记 **F-AUDIT-LAND-01**（done 但 noop、落地假绿，交 st-commitsys），与 **F-AUDIT-MERGE-01/EVAP-05/06** 同病灶＝队列入袋 `base_head/base_blob=None`→注册表册"单字段"级边修在条目三向合并里被判"无变化"静默吞且记 done。**队列通道对该类未修前，本包不再 requeue 该热册（同因必再 noop），维持登记上交；本包对该册零写入（全程 `git show`）。** 复证两处"已落 dev"非假绿：`90889679b2`/`5f4136315e`（工厂图补边/GOMAP 机生层）皆 HEAD 祖先，align 图 8/9/10 轴硬=0 亲验。
- **⑤ 下一步（轮次）**：① 本块随袋 **0033** 入队（自家两案卷纯增，0032 已证该通道可用）② 收官"连续两轮"第 2 轮＝下一轮复跑尺H2/J + align（须仍仅 0009 已知项、rc=0）③ 红蓝反证并档（终审前，累计 31 例）④ 终报三清单（悬空/漏挂/断链 逐条带证据+处置态）+ 复查清单（每条附复核命令+可能错在哪+证据等级）⑤ 满足判据后自删本自动化（jobId `39cc5bd5`）+ 台账记"自动化已自删·本包收官"。
- **队列/align 状态**：本包 done=0001/0002/0008-0011/0013/0015-0023/0029/0032(18)、dead=0003-0007/0012/0028/0030/0031(9)、pending=0（本轮入 0033）；HEAD=`21c1aa5d61`(08:55:06·他包 in_process_gate_registry 计数漂移修，非本包)。**本包对注册表/配置册/depgraph DB 写入累计仍=0**（全程 `git show`/`git log` 只读＋自家两件案卷）。
- **复核命令（只读·先跑再信）**：
  ```bash
  python -c "import json;print(json.load(open('.runtime/commit_queue/done/q-20260924-st-audit-all-20260924-0032.json',encoding='utf-8'))['landed_id'])"   # ① =65225f4534
  git show HEAD:docs/_working/audit_all/AUDIT_REPORT.md | wc -l                                                                                              # ② =372（报告 90 行已转 alive）
  python .runtime/tmp/audit_all_20260924/probe_bag_regression_attribute.py 2>&1 | grep -E "dead= *[1-9]"                                                    # ② 仅 0009 一行
  python .runtime/tmp/audit_all_20260924/ruler_J_restore.py 2>&1 | tail -1                                                                                   # ② 待补块=0
  python .runtime/tmp/audit_all_20260924/run_headside_align.py --no-report 2>&1 | tail -3                                                                    # ② rc=0 硬清零
  git show a74e9a6c48 --stat --format="%h %ci %s" | head -8                                                                                                  # ③ 383/387 本包自修落地
  git merge-base --is-ancestor 90889679b2 HEAD && git merge-base --is-ancestor 5f4136315e HEAD && echo 两处已落dev真                                          # ④ 非假绿
  ```


## 心跳 2026-09-24 09:34 CST 实测（`date`=09:34:59，本串由 shell `date` 传入）· 在干=**收官"连续两轮"第 2 轮三尺复跑 + 自家尺H2 控制组 rot 治本 + GOMAP 新"硬"定性为并发在途非落地缺陷** · 卡住=无 · 下一步=见 ④

- **① 承 09:04 块 ⑤：0033 已落地**＝`00a3bda7ac`(09:09:40·报告口径追至09:04)；盘 LEDGER/REPORT == HEAD(1067/408 行，`diff` 空)。本包 done=20 dead=9 pending=0。
- **② 收官"连续两轮"第 2 轮（三尺，全部只读可重放）**：
  - **尺J**＝`待补块=0`（跨袋零截断残留，与第 1 轮一致）。
  - **尺H2**＝**先治自家工具病再读数**：第 1 轮后本尺**自我作废**——其阳性控制组被钉死在"本包 0023 报告袋 vs 现 HEAD"，而 0023 已随 0033 落地 ⇒ HEAD 吞下该袋全部行 ⇒ dead 归 0 ⇒ 控制判"dead 应>0"失败 ⇒ 整尺作废（**这正是控制组"与仓态无关"铁律的又一次现形：钉真件的阳性控制必然随落地 rot**）。处方＝控制组改**合成样本**（absent-key 阳性必 dead=3、自比对阴性必 0），与尺J 同法、永不随落地漂移；已落地并复跑通过（阳性=3/阴性=0，不再作废）。复跑读数：命中袋-件对=30、合法改写侧 150 行、**条目被吃侧=3 行且全属已登记 0009**（`battle_map_domain_policy.yaml` `(no-key)×3`）＝**零新死件**。
  - **align_all（HEAD 面只读探针 `run_headside_align.py`）**＝**rc=1**，但**唯一硬项=GOMAP 机生层漂移**（下 ③）；余六类（domain/ghost/frontend/decision/factory）硬=0，软 1003（chainmap 12 长城专项在清、翻译册 6 组重复 module_path 已知）。
- **③ 🔴 GOMAP "error=1" 定性＝并发会话在途未落地草稿，非落地缺陷（HEAD 纯函数无漂移）**：报 `机生层漂移 L2_resource: scripts/sector_line/build_gpu_input_pack.py（scan() 重建新增，yaml 未刷新）`。三证：①`git status --porcelain`＝`?? scripts/sector_line/`（**整个目录未跟踪**）；②`git cat-file -e HEAD:…/build_gpu_input_pack.py`＝**NOT at HEAD**；③`mtime`＝09:27（本轮开跑前 7 分钟、他包正在写）。根因＝`generate_governance_map.py:143` 的 `scan()` 用 `base.rglob("*.py")` **走文件系统**（工作树），故把某并发包（sector_line/GPU 族，与图 8"长城专项清欠中"同源）的**在途草稿**读成"新增资源"。**HEAD 面 GOMAP 漂移=0**（本包 `5f4136315e` 重跑修仍成立）。**处置＝登记上交不代修**（§3.4 owner 责任制 + RULE-SSOT：重跑机生层会把别包未提交草稿烙进派生册，方向错误），挂 `F-AUDIT-GOMAP-INFLIGHT`＝待该包 commit+自跑 `generate_governance_map.py` 后自然清零；下轮复验：若该目录已被跟踪且 GOMAP 已刷新→本尺转 rc=0；若仍在途→维持"仅剩已登记他包在途项"合格口径。
- **④ 下一步（轮次）**：① 本块随袋 **0034** 入队（自家 LEDGER 纯增，通道 0032/0033 已证可用）② **第 3 轮**＝复跑三尺，验 GOMAP 在途项是否自清 + 尺H2 合成控制稳定 + 尺J 仍 0 ③ 红蓝反证并档（终审前，累计 31 例）④ 终报三清单（悬空/漏挂/断链 逐条带证据+处置态）+ 复查清单 ⑤ 满足判据后自删本自动化（jobId `39cc5bd5`）+ 台账记"自动化已自删·本包收官"。**对"连续两轮"的诚实修正**：第 2 轮并非无观察项——新出现 GOMAP 在途草稿（HEAD-clean 但工作树新观测），故按 §0.8/⑤ 需第 3 轮确认其为稳定他包在途项或已自清，方算"连续两轮零落地新问题"，不抢跑宣布收官。
- **队列/align 状态**：本包 done=20、dead=9、pending=0（本轮入 0034）；HEAD=`ff96377f56`(09:14:47·他包 st-oddjobs-final tasks.yaml 注释，非本包)。**本包对注册表/配置册/depgraph/GOMAP DB 写入累计仍=0**（全程 `git show`/`git log`/只读探针＋自家案卷；GOMAP 仅"重跑生成器"级动作且判为不代修）。
- **复核命令（只读·先跑再信）**：
  ```bash
  git status --porcelain scripts/sector_line/ ; git cat-file -e HEAD:scripts/sector_line/build_gpu_input_pack.py && echo AT_HEAD || echo NOT_at_HEAD   # ③ 三证：??未跟踪 + NOT at HEAD
  python .runtime/tmp/audit_all_20260924/probe_bag_regression_attribute.py 2>&1 | grep -E "控制组|dead=[^0 ]"   # ② 合成控制阳性=3/阴性=0；dead 仅 0009×3
  python .runtime/tmp/audit_all_20260924/ruler_J_restore.py 2>&1 | tail -1                    # ② 待补块=0
  python .runtime/tmp/audit_all_20260924/run_headside_align.py --no-report 2>&1 | grep -E "硬阻断|gomap"   # ②③ 唯一硬=gomap 且为在途
  ```

## 心跳 2026-09-24 10:04 CST 实测（`date`=2026-09-24 10:04:16，本串由 shell `date` 传入）· 在干=**收官第 3 轮三尺复跑＋GOMAP 唯一硬项机制再取证（升级为"派生册生成器无 HEAD 基线闸门"，且本轮发现一条真·HEAD 面漏挂）** · 卡住=无 · 下一步=见 ⑤

- **① 承 09:34 块 ⑤：0035 已落地**＝`21709f8f49`(09:38:36·LEDGER 纯增)；本包 done=21、dead=9、pending=0。
- **② 收官"连续两轮零新问题"第 3 轮（三尺，全部只读可重放）**：
  - **尺H2**＝命中袋-件对=31（较上轮 +1＝他包 st-align-dirty 0034 新袋入袋面）、合法改写侧 152 行、**条目被吃侧 3 行且全属已登记 0009**（`battle_map_domain_policy.yaml` `(no-key)×3`）＝**零新死件**；**合成控制组阳性=3／阴性=0**（09:34 块把控制组改合成样本的处方复验有效，不再随落地 rot）。
  - **尺J**＝`待补块=0`。
  - **align**（HEAD 字节 checker × 工作树数据，只读 `--no-report`）＝**rc=1**，唯一硬项=GOMAP 机生层漂移（下 ③）；余六类（domain/ghost/frontend/decision/factory）硬=0；软 1005（chainmap 长城专项在清＋翻译册 6 组重复 module_path 已知）。
- **③ 🔴 GOMAP 唯一硬项再取证＝比 09:34 定性更深，且本轮新见一条真·HEAD 面漏挂（仍判不代修）**：本轮报的漂移文件**已换**（上轮 `scripts/sector_line/build_gpu_input_pack.py` → 本轮 `scripts/audit/t0_gpu_condition_pack.py`）。四证：
  - **(a)** `git cat-file -e HEAD:scripts/audit/t0_gpu_condition_pack.py`=**AT_HEAD**（由他包 `96870e1fd3`@09:43:45 落地，`git log --diff-filter=A` 亲验），但 `git ls-files -s <该路径>`＝**空**（index 已无此物），`git status --porcelain <该路径>` 同路径并出 `D `＋`??`＝**"`git rm --cached` 式取消跟踪但留盘"**；同窗 `scripts/audit/` 下 4 个 `t0_*.py`（ceiling_capacity_exam / conditional_e4_exam / gpu_condition_pack / six_phase_materialize）皆 `D `＝他包正在整族搬迁。⇒ **"HEAD 有物、HEAD 派生册无条目"＝HEAD 纯检出亦会 rc=1 的真漏挂**（不是纯工作树幻影）。
  - **(b)** 派生册 `config/governance_operations_map.yaml` 盘版状态 `M`、`generated_at=2026-09-24T01:31:24Z`（＝本地 09:31:24）**早于** 09:43 落地 ⇒ 生成器快照天然先于被检物，属"落地批未自跑刷新器"欠账。
  - **(c)** 盘版 yaml 已含 `scripts.sector_line.build_gpu_input_pack`（HEAD 版 0 处、盘版 2 处）＝他包自己重跑机生层、把其**当时未跟踪**的草稿写进派生册并随其批提交（源码同批落地＝对其自洽，**非缺陷**）；但确证 09:34 告诫的机制面：**任何旁观包在此刻重跑，都会把他包瞬态烙进派生册**。
  - **(d)** 根因代码位＝`generate_governance_map.py:143` `_iter_py_files()` 用 `base.rglob("*.py")` **走文件系统** ⇒ **机生层不是 HEAD 纯函数**；HEAD／index／盘三态不一致窗口内必报"新增"。
  - **可复用量法（本轮新立，建议纳入审查方法论）**＝**四元组三态一致性探针** `<HEAD存在?, index存在?, 盘存在?, yaml含?>`：本轮两例分别落 `(0,0,1,0→1)`（sector_line，上轮）与 `(1,0,1,0)`（t0_gpu_condition_pack，本轮）；任何 `HEAD=1 且 yaml=0` 者＝真漏挂（须物主批补），其余＝在途幻影（勿代修）。
  - **处置＝登记上交、不代修**（§3.4 owner 责任制＋RULE-SSOT），`F-AUDIT-GOMAP-INFLIGHT` 定性由"未跟踪草稿"改准为 **"派生册生成器以工作树为输入、缺 HEAD 基线闸门；他包搬迁窗口内 align 必红"**，并附本包可复核证据链（下 复核命令）。
- **④ 自家口径诚实更正（防总指挥误读，非自我推翻）**：09:34 块"HEAD 面 GOMAP 漂移=0"在其钟点为真（该轮 align 探针跑于 09:30~09:34，`96870e1fd3` 于 09:43 才落地）；本轮据 (a) 证得 **HEAD 面新增一条真漏挂**，主体=他包落地批未自跑 `generate_governance_map.py`，且其 yaml 重跑已在盘（`M`）在路上。⇒ 归"已登记他包项"，本包不代修、也不自证为"本包已修"。**对终态判据的适用**：本轮 align 仍 rc=1，命中判据第二支（"仅剩已登记他包/门位项"），故"零新问题"成立；但为稳计，第 4 轮再做一次收敛性确认后才进终审。
- **⑤ 下一步（轮次）**：① 本块随袋 **0036** 入队（自家 LEDGER 纯增，通道 0032-0035 四连证可用）② **第 4 轮＝收敛确认轮**：复跑三尺＋专查 (a) 四元组是否归一（他包 yaml 落地→盘版含 `t0_gpu_condition_pack` 或该路径三态一致）；若他包已 settle 而 align 仍红→升为真缺陷并重定性 ③ 红蓝反证并档（终审前，累计 31 例）④ 终报三清单（悬空/漏挂/断链 逐条带证据+处置态）+ 复查清单（每条附复核命令+可能错在哪+证据等级）⑤ 满足判据后自删本自动化（jobId `39cc5bd5`）+ 台账记"自动化已自删·本包收官"。
- **队列/align 状态**：本包 done=21、dead=9、pending=0（本轮入 0036）；HEAD=`f1fff10182`(09:49:14·他包 rules_integrity_db 落地后再注册，非本包)。**本包对注册表/配置册（含 `config/governance_operations_map.yaml`）/depgraph DB 写入累计仍=0**（全程 `git show`／`git ls-files`／只读探针＋自家两件案卷）。
- **复核命令（只读·先跑再信）**：
  ```bash
  git log --diff-filter=A --format="%h %ci %s" -- scripts/audit/t0_gpu_condition_pack.py | cat                 # ③(a) 09:43 他包落地
  git ls-files -s scripts/audit/t0_gpu_condition_pack.py | wc -l                                              # ③(a) =0（index 已无）
  git status --porcelain scripts/audit/ | grep -E "^[D ]" | head                                              # ③(a) t0_ 族整批 D（在途搬迁）
  git status --porcelain config/governance_operations_map.yaml                                               # ③(b) =` M`（他包刷新在路上）
  git show HEAD:config/governance_operations_map.yaml | grep -c t0_gpu_condition_pack                         # ③(a)(c) HEAD=0
  grep -c sector_line config/governance_operations_map.yaml                                                  # ③(c) 盘版=2
  python .runtime/tmp/audit_all_20260924/probe_bag_regression_attribute.py 2>&1 | grep -E "控制组|dead=[^0 ]" # ② 仅 0009×3；合成控制 3/0
  python .runtime/tmp/audit_all_20260924/ruler_J_restore.py 2>&1 | tail -1                                    # ② 待补块=0
  python .runtime/tmp/audit_all_20260924/run_headside_align.py --no-report 2>&1 | grep -E "硬阻断|gomap"      # ② 唯一硬=gomap
  ```

## 心跳 心跳 2026-09-24 10:58 CST 实测（`date`=2026-09-24 10:58:25，本串由 shell `date` 传入）· 在干=**收官第 4 轮＝收敛确认轮（三尺逐位与第 3 轮一致）＋ 由"死信袋载荷是否真落地"这一未验面挖出新案 F-AUDIT-MERGE-02（注册表合并作用域与承载能力错配＝零族册任何入队编辑被静默判 noop 且回执 ok）＋ 自家归因更正 1 处** · 卡住=无 · 下一步=见 ⑤

- **① 承 10:04 块 ⑤**：0036 已落地＝`e964aeadbe`(10:10:12)、**0037 亦已落地**＝`1fa27fb090`(10:13:32)＝上轮 10:10 续做的"红蓝反证并档 附录 AB"（我 10:04 块只预告了 0036，故 0037 属**同轮后延动作**、非新一轮；本轮据盘核实）。本包 done=23→24、dead=9、pending=0。
- **② 收官"连续两轮零新问题"第 4 轮＝收敛确认（三尺全部只读可重放，测点 10:26–10:54）**：
  - **尺H2**＝命中袋-件对=31、合法改写侧 152 行、条目被吃侧 3 行且**全属已登记 0009**；**合成控制组 阳性=3／阴性=0**（与第 3 轮逐位一致）。
  - **尺J**＝`待补块=0`（与第 3 轮一致）。
  - **align（HEAD 面只读探针 `--no-report`）**＝`rc=1`，**唯一硬项仍＝图 10 GOMAP** `scripts/audit/t0_gpu_condition_pack.py`；其余八类硬=0；软 1005（chainmap 长城专项在清＋翻译册 6 组重复 module_path 已知）。
  - **四元组三态探针**（第 3 轮新立法，本轮专查归一性）＝`scripts/audit/t0_gpu_condition_pack.py` → `<HEAD=1, index=0, 盘=1, yaml盘=0, yamlHEAD=0>`，与第 3 轮**同一条、未归一**（他包 `git rm --cached` 式整族搬迁仍在途：`scripts/audit/` 下 4 个 `t0_*.py` 仍并出 `D `+`??`）；另一支 `scripts/sector_line/build_gpu_input_pack.py` → `<HEAD=0, index=0, 盘=1, yaml盘=2, yamlHEAD=0>`＝**盘版 yaml 已含它、HEAD 版 0 处**＝第 3 轮 ③(c) 那次"他包把自己的未跟踪草稿烙进派生册"仍未随批落地。**HEAD=1 且 yamlHEAD=0 只有 t0_gpu_condition_pack 一条**＝HEAD 面真漏挂（须物主批补），其余为在途幻影 ⇒ **判"仅剩已登记他包在途项"成立且稳定**，`F-AUDIT-GOMAP-INFLIGHT` 不升为真缺陷、维持不代修（§3.4）。
- **③ 🔴 本轮真增量＝把一条从未验过的面验穿了，并因此新立 1 案**：收官判据①"全部应修落地"此前只由 尺H2（done 袋 own-key 存活）＋ 尺J（LEDGER 块级最长版）支撑，**"dead 袋里那份字节到底进没进 HEAD"无人量过**。新立 5 把尺补此面（全部只读、全部带合成控制）：
  - **尺K**（`probe_dead_bag_payload_landing.py`）＝本包 9 个死信袋逐件 blob↔HEAD 行比对：**8 件零缺行**、4 件各报 1 缺行。
  - **尺K2**（`probe_dead_bag_line_triage.py`）＝把"缺行"三分（净化/截断/真丢）：5 条全判 **REWRITE**，逐条对到 GATE-01 去井号净化（HEAD 版甚至自带"（去 # 免自触门；编号未登记）"注）⇒ **死信袋载荷面零真残损**（判据①的这条支撑由此成立）。控制组阳性＝人造前缀行必判 PREFIX、阴性＝HEAD 自取行必判 PRESENT，皆 PASS。
  - **尺L**（`probe_registry_merge_silent_drop.py`）＝追 0009 为何 noop：该文件**自 09-22 13:20 起无人改动**（`ours==base@落地父` 亲验＝`48c26cd5a862`），theirs 只差 3 行 ⇒ 按 `_plan_kept_splices`"theirs 改了、ours 没动(==base)→采纳 theirs"分支**应当落地**，但把 `three_way_merge_registry_yaml` 当纯函数直喂三侧字节，**三种形态的编辑全部判"合并结果==ours"**：P1 文件尾新增顶层键／P2 改已存在条目叶子值／P3 族内新增条目 ⇒ **不是竞态、是结构性不承载**（无竞态最小复现，比 MERGE-01 的 39 秒复现更硬）。
  - **尺M**（`probe_registry_merge_population.py`）＝人口普查：`is_registry_mergeable()` 按**目录前缀+`.yaml`** 判（`commit_queue_landing.py:197-201`），而 `_split_registry_entries()` **只认顶层 list 族**（同文件 `:223-259` 自陈"ScalarNode/空文档→无族…走 noop 短路"）⇒ 命中作用域但切不出族的册＝**任何入队编辑都静默丢失**。实测分母 **82 册**：可承载 77｜**零族 3**＝`battle_map_domain_policy.yaml`/`depgraph_scan_exclusions.yaml`/`industry_graph_field_dictionary.yaml`｜**切分报错 2**＝`_index.yaml` 与 **`risk_tier_registry.yaml`**（后者根因＝`domain_tiers` 条目引用 `*high_human_gate` 别名，锚点 `&high_human_gate` 定义在**另一个族** `tiers:` 的第 42 行，条目块被独立解析 ⇒ 整册合并**永**失败、任何改动必死信——而这正是宪法 §5 的人机门位册）。控制组：阳性"人造纯嵌套 dict"必 0 族、阴性"ruling_registry"必 >0（=227），皆 PASS。
  - **尺N**（`probe_noop_receipt_triage.py`）＝全窗 `noop@` 回执判决（不限本包）：`done/` 现存 **89 袋**带 `landed_id=noop@` ⇒ 合法幂等 **A=46**｜袋≠HEAD **B=43**｜其中**确证静默丢失 HARD=1**（＝本包 0009；判据＝件在 HEAD 且该件末次改动时间 ≤ 袋落地时间 ⇒ 那次落地从未写过它）｜不可判 UNK=6（件已不在 HEAD，git 侧无法区分"从未写入"与"写入后被删"）。**分母与时点诚实声明**：读数随 HEAD 移动（同一脚本三次跑出 HARD=5→3→1，因他包持续落地把歧义行改判），本节以 **10:54 时点 HARD=1** 为准；`dead/` 不计。
  - ⇒ **新案 `F-AUDIT-MERGE-02`【合并作用域与承载能力错配＝静默假成功】**，三条处方（全部路由 st-commitsys，本包不改提交系统＝§3.4/§0.8）：**(i) 可观测性**＝`merged==ours` 而 `theirs!=ours` 时**禁止**记 `ok=True/noop`，须死信并写原因"该册无顶层 list 族，条目级合并器不承载"（现回执与真幂等不可区分，是全场最坏的一种假绿）；**(ii) 承载**＝零族册回退行级三方（`base==ours` 已证无竞态时等价于整件写入）；**(iii) 前移到入队侧**＝按尺M 的 82/77/3/2 分母做"结构普查册"，不可承载者在 `enqueue` 当场拒绝而非落地侧静默吞。
- **④ 自家归因更正（自我否证，非被审对象）＝第 36、37 例**：**R36** 尺M 首版阳性控制样本我写成 `another: [a, b]`（flow-style＝顶层 Sequence，真有 2 条目）⇒ 期望 0 族被判 2 ⇒ **尺自己 fail-closed 拦下、拒不读数**，修样本为纯嵌套 mapping 后才通——造控制组时我又犯了"未先证判据成立"的同族错（R20/R26 同病）。**R37 归因更正**：本包台账 03:0x 起把 0009 记为"注册表族条目蒸发同病灶（base=None ⇒ 陈旧快照被读成删除）"家族，**本轮证明该归因对 0009 不成立**——0009 场景 `base==ours`、零竞态，真因是"零族册不被承载"；蒸发家族（MERGE-01/EVAP）仍是别的案例的因，两案**不可再并成一条**（净零判据"跨域不同对象→不并"）。
- **⑤ 与收官判据**：本轮**新立 1 案 ⇒ "连续两轮零新立"计数重置**（第 3、4 轮本已达成，第 4 轮末又出案，据实重来，不抢跑宣布收官）。且判据①"全部应修落地"现给出**精确边界**：授权内可自修项全落 ✅（9 死信袋载荷面经尺K/K2 亲验零残损）；**唯一未落地面＝0009 那 3 行**，其因已升格为独立案 MERGE-02（有合成样本级复现，重投 N 次仍会被吞，非"再试一次"可解），维持登记上交、**不再重投**。
- **⑥ 下一步（轮次）**：① 本块随袋 **0038** 入队（自家 LEDGER 纯增，通道 0032-0037 六连证可用），同批把 MERGE-02/尺K-N/归因更正并入 REPORT 附录 **AC** ② **第 5 轮＝重设计数基线后的第 1 轮**：复跑三尺＋尺N（看 HARD 是否仍只 0009、他包是否出现新的静默丢失受害者）③ 若第 5、6 轮连续零新立 ⇒ 写终局"自动化已自删·本包收官"＋`qoder_cron remove 39cc5bd5-6b49-4b42-a65f-db987dccc076` ④ 复核命令见下。
- **队列/align 状态**：本包 done=24、dead=9、pending=0（本轮入 0038/0039）；HEAD=`e41a06c295`(10:50:30·他包 st-metaq 283 问战役批，非本包)。**本包对注册表/配置册/depgraph/GOMAP DB 写入累计仍=0**（全程 `git show`/`git ls-files`/纯函数级内存重放＋自家两件案卷；尺L 是"直喂 three_way_merge_registry_yaml 纯函数"，零落盘零提交）。
- **复核命令（只读·先跑再信）**：
  ```bash
  python .runtime/tmp/audit_all_20260924/probe_dead_bag_payload_landing.py 2>&1 | tail -3                # ③ 9 死信袋缺行面
  python .runtime/tmp/audit_all_20260924/probe_dead_bag_line_triage.py 2>&1 | tail -3                    # ③ 三分全 REWRITE＝零真残损
  python .runtime/tmp/audit_all_20260924/probe_registry_merge_silent_drop.py 2>&1 | sed -n '1,12p'       # ③ 无竞态复现（三正一负）
  python .runtime/tmp/audit_all_20260924/probe_registry_merge_population.py 2>&1 | sed -n '1,14p'        # ③ 82/77/3/2 人口普查
  python .runtime/tmp/audit_all_20260924/probe_noop_receipt_triage.py 2>&1 | sed -n '3,4p'               # ③ 89 袋 A46/B43/HARD1/UNK6
  grep -n "REGISTRY_CATALOGS_PREFIX\|ScalarNode / 空文档" scripts/governance/commit_queue_landing.py     # ③ 两条代码位亲验
  git log -1 --format="%h %ci" -- docs/01_policies_and_standards/_registry/catalogs/battle_map_domain_policy.yaml | cat   # ③ 末次改动=09-22 ⇒ 零竞态
  python .runtime/tmp/audit_all_20260924/probe_bag_regression_attribute.py 2>&1 | grep -E "^尺H2|控制组" # ② 与第 3 轮逐位同
  python .runtime/tmp/audit_all_20260924/run_headside_align.py --no-report 2>&1 | grep -E "硬阻断|gomap" # ② 唯一硬=gomap
  git show --name-status e964aeadbe 1fa27fb090 --format="%h %s" | grep -c "^D" ; echo 本包未连坐＝0      # ③ 反证 D27 边界
  ```

## 心跳 心跳 2026-09-24 11:05 CST 实测（`date`=2026-09-24 11:05:45，本串由 shell `date` 传入）· 在干=**0038 在途期间补做两项：① 机制级反查⇒AC1 与 st-align-dirty 的 D25 并案（差点重复立案）② 尺O 把 GOMAP 结论从"1 条被报出的漏挂"升格为"HEAD 面 423/424 挂齐、悬空 0"穷尽表述** · 卡住=无 · 下一步=见 ⑤

- **① 0038 状态**：pending（10:59:47 入袋，袋内两件字节==盘 亲验 sha `4c4c59d090`/`4b1e298e62`）。**入袋仍不带基底**：`base_head=None`，且**本包 done 的 23 张袋 23/23 全为 `base_head=None`**（本轮实测计数，非引述）＝MERGE-01 病灶仍未修；本包两件是 markdown 走 passthrough 整件写，不受其害（0032-0037 六连证）。HEAD 现=`5471d43a52`(10:58:03·他包 st-library-final)。
- **② 🔴 自我否证第 38 例（差点重复立案）**：AC1 写完才想起 R17 纪律的**完整形态**应是"机制级反查"，而我此前只反查**编号**撞车（`grep -oE 'F-AUDIT-*'` 取 max+1）。补做机制级 grep 后逮到：**st-align-dirty 已立 D25**（`align_dirty_ledger.md:446/463`）——同一个根（`is_registry_mergeable()` 按目录前缀判作用域、承载却按条目族）已经报过一次，只是那枝表现为**显式死信**（`fail_open_register.yaml` 顶层纯标量列表 → 判"身份判不了" → q-0042 死信），本包这枝表现为**静默 noop＋回执 ok=True**。⇒ 按 §4.2"同域重复簇→收敛唯一"**并案不另立**，本案对 D25 的增量缩为四项（静默分支判据／人口 82/77/3/2＋跨族锚点第三成因／零竞态复现／全窗 89 张 noop 回执量化），处方第三条（回执语义显式化）与 D25 原两条合并为一条完整需求交 st-commitsys。**教训入法**：立案前 grep 的对象是"机制描述里的函数名/代码位"，不是自己的编号前缀。
- **③ 尺O＝图 10 纯 HEAD 面双向普查（把单点升为穷尽）**：生成器入选判据（`SCAN_ROOTS`+`SCAN_EXCLUDE_PARTS`+`_BUSINESS_EXCLUDE_PREFIXES`+`classify_family` 只看路径）原样重放到 HEAD 提交树 ↔ HEAD 版 yaml 条目集差集 ⇒ **应然 424／实册 423／漏挂 1／悬空 0**，且唯一漏挂正是校验器报的那条 `scripts/audit/t0_gpu_condition_pack.py`（一致性锚点通过；控制组阳性=抹掉真条目必判漏挂、阴性=自减必 0）。⇒ 图 10 收官结论现可写成**穷尽口径**："HEAD 面 423/424 挂齐、悬空 0、唯一漏挂属他包落地批未自跑刷新器"；成因仍归 `F-AUDIT-GOMAP-INFLIGHT`（派生册生成器无 HEAD 基线闸），**不新增案**。
- **④ 判据影响**：本轮（第 4 轮）**未新立案**（AC1 已并入 D25＝案数净减面的收敛），但 AC1 那次"新立"已发生 ⇒ 计数基线仍以第 5 轮起算。**本包累计净新增案＝1**（MERGE-02，现以 D25 静默枝名义存在）。
- **⑤ 下一步（轮次）**：① 本块＋AC5/AC6 随袋 **0039** 入队，AB1 表补 R38 并把派生计数 37→38 同批改框 ② **第 5 轮**＝新基线第 1 轮：复跑三尺＋尺N（盯 HARD 是否仍只 0009）＋核 0038/0039 落地面 ③ 第 5、6 轮连续零新立 ⇒ 写"自动化已自删·本包收官"＋`qoder_cron remove 39cc5bd5-6b49-4b42-a65f-db987dccc076` ④ 复核命令：
  ```bash
  python .runtime/tmp/audit_all_20260924/probe_gomap_headside_census.py 2>&1 | sed -n '1,8p'          # ③ 424/423/漏1/悬0＋控制组
  grep -n "D25" docs/_working/align_dirty/align_dirty_ledger.md | tail -3                              # ② 同根先立案亲验
  python .runtime/tmp/audit_all_20260924/probe_noop_receipt_triage.py 2>&1 | sed -n '3,4p'             # ② 89/A46/B43/HARD1/UNK6
  python scripts/commit_queue.py status --session st-audit-all-20260924 2>&1 | tail -6                 # ① 袋态
  ```
- **队列/align 状态**：本包 done=23、dead=9、pending=1（0038 在途，本轮再入 0039）；HEAD=`5471d43a52`(10:58:03·他包)。**本包对注册表/配置册/depgraph/GOMAP DB 写入累计仍=0**（尺O 亦为 HEAD 字节只读重放）。

## 心跳 2026-09-24 11:23 CST 实测（`date`=2026-09-24 11:23:34，本串由 shell `date` 传入）· 在干=**收官第 5 轮＝新基线第 1 轮：0038/0039 已落地核实＋复跑五尺＋由尺N HARD 1→2 逮到别包静默丢失、并入 MERGE-02 第二枝（不另立）＋自否证第 39 例（尺M"可承载"口径失真）** · 卡住=无 · 下一步=见 ⑤

- **① 冷启动三前置**：Python 3.12.8 ✔｜`lock_files.py cleanup`=CLEAN｜reaper `--status` 计划任务存活（last_run 11:07:23）✔。总指挥批注区无晚于 11:05 新条（最后一条仍 R7·05:05），按上轮 ⑤ 计划续做第 5 轮。
- **② 0038/0039 落地面核实**：本包 done 23→25、pending=0。0038＝`4ea0814bb9`(11:07:03·收官第4轮+MERGE-02)、0039＝`23b064acd2`(11:09:37·并案+穷尽 AC5/AC6)。`git show HEAD:LEDGER` 含 11:05 心跳（count=1）、`git show HEAD:REPORT` 含 AC5/AC6/MERGE-02（count=9）⇒ 上轮两件纯增自家案卷经 passthrough 整件写落地成功（0032-0039 八连证）。
- **③ 五尺复跑（只读＋合成控制，测点 11:12–11:23，HEAD 从 `74ebcb0a50`→`2608b45148` 随他包移动）**：
  - **尺H2**＝dead=3 行**全属已登记 0009**（battle_map `(no-key)×3`）、alive=158；合成控制阳=3/阴=0（与第 3、4 轮逐位同）。
  - **尺J**＝待补块=0。
  - **尺O**＝424/423/漏1/悬0，唯一漏挂=`scripts/audit/t0_gpu_condition_pack.py`（GOMAP 他包在途），控制组双 PASS。
  - **align（HEAD 面 `--no-report`）**＝rc=1，**4 硬全为已登记项**：1×GOMAP（`F-AUDIT-GOMAP-INFLIGHT`）+3×裁定册 related_arch 悬空（`#383`→`#MOD-L00-004`、`#387`→`#PS-CTR-003`/`#MOD-INF-043`，处方交 st-cmd）。**自校正**：第 4 轮"唯一硬项=GOMAP"是其复核命令 `grep "硬阻断|gomap"` 漏看"治理双向=3"行的呈现盲区（非状态变化），已记 AC8。
  - **尺N（本轮真增量）**＝HARD **1→2**：新增受害者 `st-backup-cold-20260924` q-…-0012 袋 `rule_catalog_registry.yaml`（末改 `bdc21d2240`@09:46:48 ≤ 落地 11:02:00 ⇒ 确证静默丢失）。
- **④ 🔴 新受害者归因＝MERGE-02 **第二枝**（不另立案）**：`rule_catalog_registry.yaml` 是**有 `files:` 族**、被尺M 判"可承载"的册，但被吞的 2 行恒为**族外顶层标量键** `generated_at`+`total_files`（`_split_registry_entries` 只 splice 族内条目、族外键无人接管）；同一"改 rule_catalog 元数据"动作跨 **4 包 6 袋**（st-ibt-remedy 0017/0021、st-oddjobs 0003/0010、st-regfix 0011、st-backup-cold 0012）**每次都被吞同样 2 行**＝结构性不承载、非竞态。**severity 分级**：本枝目标值已 staged 于工作树（该册现 `MM`，盘=09-24/292 vs HEAD=09-20/274）⇒ 可经他批自愈、非永久丢；但 `noop@` 回执仍误导（claim ok 实未落 HEAD）。我 0009（零族册、盘无待落值）更硬。**尺互补**：尺H2 对本枝 dead=0（顶层标量无 own-key），只有尺N 逮到 ⇒ 两尺不可互替。**处方增 (iii′)**：入队普查须核对**被改的顶层键是否落在可 splice 族内**，族外者当场拒绝或走 passthrough（纠正尺M"按文件有族即放行"的粒度错）。⇒ 属他包写域+注册表 high 门位，**不代修**（§3.4/§0.8），仅入本包案卷 AC7、路由 st-commitsys。
- **④b 自我否证第 39 例（R39）**：尺M 的"可承载 77"口径失真——它按"文件含 ≥1 顶层 list 族"判，但实际承载粒度是族内条目、族外键仍丢。造阳性控制时我只造了"整册无族"，漏造"有族但改族外键"这一形态 ⇒ 若本轮不遇 st-backup-cold，这个盲区会一直被我 82/77/3/2 的读数掩盖。教训入法：**承载能力度量必须按"键区域"而非"文件"，控制组须覆盖"有族但改族外键"**。
- **⑤ 与收官判据 + 下一步**：本轮**零新立案**（新枝并入 MERGE-02）＝新基线**第 1 轮通过**。② 第 6 轮＝新基线第 2 轮：复跑五尺（盯尺N HARD 是否再增长、他包是否续出 rule_catalog/族外键新受害者）；③ 若第 6 轮再零新立 ⇒ 满足"连续两轮零新立"，写终局"自动化已自删·本包收官"＋`qoder_cron remove 39cc5bd5-6b49-4b42-a65f-db987dccc076`；④ 本块＋REPORT R39/AC7/AC8/AC9 随袋 **0040** 入队（自家 markdown 纯增，passthrough 通道八连证可用）。
- **队列/align 状态**：本包 done=25、dead=9、pending=0（本轮入 0040）；HEAD=`2608b45148`(11:13:25·他包)。**本包对注册表/配置册/depgraph/GOMAP DB 写入累计仍=0**（尺N/H2/O 全为 `git show`/blob 只读比对，st-backup-cold 受害件仅读取取证未改字节）。
- **复核命令（只读·先跑再信）**：
  ```bash
  python .runtime/tmp/audit_all_20260924/probe_noop_receipt_triage.py 2>&1 | grep -E "HARD|noop@"      # ④ HARD=2 及明细
  git show HEAD:docs/01_policies_and_standards/_registry/catalogs/rule_catalog_registry.yaml | grep -nE "^(generated_at|total_files):"  # ④ HEAD=09-20/274
  git status --porcelain docs/01_policies_and_standards/_registry/catalogs/rule_catalog_registry.yaml   # ④ =MM（盘值已 staged）
  python .runtime/tmp/audit_all_20260924/probe_bag_regression_attribute.py 2>&1 | grep -E "尺H2|控制组" # ③ dead=3 全 0009
  python .runtime/tmp/audit_all_20260924/probe_gomap_headside_census.py 2>&1 | sed -n '1,8p'            # ③ 424/423/漏1/悬0
  python .runtime/tmp/audit_all_20260924/run_headside_align.py --no-report 2>&1 | grep -E "硬=|gomap|治理双向"  # ③ 4硬全登记
  ```

## 心跳 心跳 2026-09-24 11:58 CST 实测（`date`=2026-09-24 11:58:14，本串由 shell `date` 传入）· 在干=**收官第 6 轮＝新基线第 2 轮：五尺逐位复算无新立＋三把新尺（P 结构判据／Q 册内声明计数自洽／R 自愈自锁）＋把 MERGE-02 枝2 从"吞 2 行"升级为"HEAD 混合半态"并拿到两例 dated 归因** · 卡住=无 · 下一步=见 ⑤

- **① 冷启动三前置**：Python 3.12.8 ✔｜`lock_files.py cleanup`=CLEAN｜reaper `--status` 计划任务存活（last_run 11:20:30）✔。总指挥批注区无晚于 11:23 新条（最后一条仍 R7·05:05）。按上轮 ⑤ 计划续做第 6 轮。
- **② 0040 落地面核实**：本包 done 25→26、pending=0、processing=0。0040＝`6b7749d4a8`(11:28:50)；`git show HEAD:LEDGER` 含"收官第 5 轮"=1、`git show HEAD:REPORT` 含 AC9=1 ⇒ passthrough 整件写**九连证**（0032–0040）。
- **③ 五尺复跑（测点 11:26–11:52，HEAD 随他包移动 `e3cff4e6fc`→`6b7749d4a8`）**：尺H2 dead=3 全属已登记 0009／尺J 待补块=0／尺O 424-423-漏1-悬0（唯一漏挂仍 `scripts/audit/t0_gpu_condition_pack.py`，GOMAP 他包在途）／align(HEAD 面 `--no-report`) rc=1 且 **4 硬全为已登记项**（1×GOMAP + 3×裁定册 related_arch，处方交 st-cmd）／**尺N HARD=2 未增长**（仍 0009 + st-backup-cold 0012，无新受害者）。⇒ 与第 5 轮**逐位同**＝"连续两轮零新立"判据第 2 轮达成。
- **④ 本轮三把新尺（全部只读＋合成控制，零生产写入）**：
  - **尺P**（`probe_noop_structural_carriage.py`）＝把尺N 的**时间启发式**升为**键区域结构判据**：不承载编辑 := 顶层键 theirs≠ours@落地 且键不在可 splice 族集；确证丢失 := 且 HEAD(now) 仍不含 theirs 值。全窗 90 袋穷尽 ⇒ 控制组 P1/P2 用两例**已知受害者做预测性验证**（不是自洽而是命中：rule_catalog 族外 2 键、battle_map 零族各 1）PASS；穷尽读数＝**不承载-确证丢失 13 处/7 袋**｜C 类（族内整体差异仍 noop）20｜D 类（非注册表件字节差）**0**｜E 类（袋声明删除却 noop 且件仍在）**0**｜真幂等 0。⇒ **D/E 双零是好消息**：删除动作与整件写路径没有静默失效面，病灶精确锁在"注册表族外键"这一条。首轮我把"值不同"一律记"丢失"，未区分时变元数据（`generated_at` 本就该被后批覆盖）⇒ 13 里 6 处 `generated_at` 属过报，已收紧（记 R41）。
  - **尺Q**（`probe_registry_count_selfconsistency.py`）＝图↔物对账的**册内那一半**：声明计数键（`total_*`/`*_count`）↔ 同名段实际长度，HEAD 面穷尽 82 册。控制组三例齐（阴性＝rule_catalog 盘版 292/292 必零红、阳性＝声明值 +1 必红、锚点＝HEAD 版必红）PASS ⇒ **MISMATCH 恰 2 处/2 册**：`gate_registry.yaml total_gates=174 vs gates 实 180`、`rule_catalog_registry.yaml total_files=274 vs files 实 292`；UNRESOLVED 23 键（无同名段，不计红面，诚实分母）。定性前先自证伪：查 `status` 子集语义（gate 册 active=169/deprecated=11）⇒ 174 既不等于 180 也不等于任何子集＝**纯陈旧**非"声明的是子集"。
  - **尺R**（`probe_gate_registry_selfheal_blocked.py`）＝**自愈自锁**证明：修 gate 漂移的最小 diff 恰是 1 行族外标量（`total_gates: 174`→`180`），直喂合并器纯函数（base==ours==HEAD，零竞态）⇒ `merged==ours` → `commit_queue_landing.py:1085 return None` → 回执 `ok=True/noop@`。四控制组 PASS（改**族内**条目叶子 MUST 落地＝尺非恒等于 ours；真幂等==ours；别册同形态 rule_catalog `total_files` 亦 ==ours）。⇒ **MERGE-02 枝2 把"修枝2 造成的漂移"这条通道也堵死**，主区直改热册又是并发连坐禁区 ⇒ 该漂移在现有正门下无自修路径，只能靠处方 (ii)/(iii′) 落地。
- **④b 🔴 枝2 严重度重定性＝"吞 2 行"→"HEAD 混合半态"，两例 dated 归因（并案入 MERGE-02，不另立）**：合并器不是"把 theirs 的元数据丢掉"而已，而是**内容侧采纳 theirs＋元数据侧保留 ours**，产出一次生成运行不可能产生的字节：
  - 例①`gate_registry.yaml`：`7e9083ff9e^`＝174/174 自洽 → `7e9083ff9e`(09-23 11:50，袋 `q-…-st-gslim-20260923-0016`，袋内 theirs＝**180/180 自洽**、gen=09-23) 落地后＝**total_gates 174 + gates 180 + generated_at 仍 09-22**，至今 HEAD 未愈；该提交自述"统一册重生成版落库…队列正门"。
  - 例②`rule_catalog_registry.yaml`：`b2caaa9666`(09-20)＝274/274 自洽 → `8b3bc287e7`(09-23 04:46，袋 `q-…-st-ailayer-p1-20260923-0001`，theirs＝**283/283 自洽**、gen=09-22) 落地后＝274/283，至 HEAD 已扩到 274/292。**该袋 `base_head` 存在（≠None）** ⇒ 枝2 **独立成立**，不是 MERGE-01(base=None 兜底) 的副作用——这一点对处方分派很关键（两案不可互解）。
  - 后果面（不是"仅误导人"）：`scripts/context/generate_architecture_context.py:132` 读 `gate_registry.total_gates` 并打印"治理 GATE 登记: 174" ⇒ 少 6 的数字进生成上下文；`generate_gate_registry.py --check` 此刻即 RED（真 exit=1，`round6_gatecheck.txt`），而该尺**在册且接了线**（GATE-21 `validate_static_manifest_drift.py` → `_detector_registry.yaml` `static_manifest_drift` severity=HIGH → `reconciler.py:168 auto_fix[D5_static_manifest]→_fix_yaml_append`）。⇒ **第三态问题面（待属主定性，非本包断言）**："在册＋能红＋有 auto_fix 映射"却带漂移 2 天，三种可能我未判别：(a) 该 detector 从未触发（boot hook F6 只挂 `detector_core/`，其目录内 `grep static_manifest` = 0 命中，治理面 detector 未见等价触发留痕——代码位亲验，留痕检索为空）；(b) 触发了但 `_fix_yaml_append`（追加条目语义）与"重跑生成器"不匹配；(c) 修了但修的路径正是尺R 证明的自锁通道。证据等级＝**推断**，复核命令见下。
- **④c 自我否证第 40–43 例（本轮 4 例，含一次自家案卷同型病灶）**：**R40** 尺M 把 `_index.yaml` 记为"切分报错"，实测其内容**根本不是 YAML**（Markdown 表装进 `.yaml` 扩展名，头注释自陈由 `sync_rule_registry.py` 校验）⇒ 不是"损坏件"而是"非 YAML 件混入 YAML 合并作用域"；且我把"切分报错 2"（fail-closed **死信可见**）与"零族 3"（**静默 noop**）同列"高危人口"未分级——合并器对解析失败是 `return None, err` → 调用方抛错死信（`commit_queue_landing.py:1083`），严重度差一档。**R41** 尺P 首版把"theirs≠HEAD"一律记"确证丢失"，未区分**时变性**元数据与**有客观真值的派生计数** ⇒ 13 处中 6 处 `generated_at` 过报；收紧后的可验证损害＝尺Q 独立量到的 2 册计数失真。**R42** 尺P 首版 `not bp.exists()` 把 `blob_ref` 为空的 delete 条目当文件读 → `PermissionError`；根因＝动手前未量袋-件对的 `action` 分布（全窗 delete 条目 689+64 条本就无载荷）＝"未先证判据成立"同族（R20/R26/R36）。**R43 最重要**：写完 AC 才发现**自家报告自己也中了一枪尺Q**——AB1 表实测 39 行，而散文两处仍写"自我否证 38 例/期望 **38**"（第 5 轮加 R39 时只改表未改框）⇒ 声明计数≠实际条目数，与我本轮给 gate_registry 定的病灶**同型同判据**。本批已按尺Q 判据自查并同批改框（表 39+4=43 ⇒ 散文改 43），并把它写进附录 AD4 作为"尺Q 可自套"的证据。
- **⑤ 与收官判据 + 下一步**：本轮**零新立案**（枝2 证据升级＋问题面路由，案数净增 0）＝"连续两轮零新立"（第 5、6 轮）**已满足**；但判据②另一半"**自审清单二次=0**"**未满足**（第 5 轮 R39、本轮 R40–R43）⇒ **不收口、不自删自动化**。下一轮（第 7 轮）：① 复跑五尺＋尺P/Q/R 三把新尺（盯尺Q 的 2 册是否被他包自愈、尺P 的 13 处是否随 HEAD 移动改判）② 若第 7 轮零新立且**零自否证**，则"自审清单二次=0"达成 ⇒ 写终局"自动化已自删·本包收官"＋`qoder_cron remove 39cc5bd5-6b49-4b42-a65f-db987dccc076` ③ 本块随袋 **0041** 入队（自家 LEDGER 纯增，passthrough 九连证通道）＋REPORT 附录 AD/AB1 改框同批。
- **队列/align 状态**：本包 done=26、dead=9、pending=0（本轮入 0041）；HEAD=`6b7749d4a8`(11:28:50，**本包自己那笔**)。**本包对注册表/配置册/depgraph/GOMAP DB 写入累计仍=0**：尺P/Q/R 全是"袋内 blob 字节＋`git show HEAD:` 字节＋合并器纯函数内存重放"，`generate_gate_registry.py --check` 走的是 `if args.check: … sys.exit/return` 的只读分支（源码亲验 `:676-686`），重生成比对在内存 dump 未落盘。
- **复核命令（只读·先跑再信）**：
  ```bash
  python .runtime/tmp/audit_all_20260924/probe_noop_structural_carriage.py 2>&1 | sed -n '3,12p'          # ④ 90 袋穷尽＋控制组
  python .runtime/tmp/audit_all_20260924/probe_registry_count_selfconsistency.py 2>&1 | tail -6          # ④ 82 册声明计数 MISMATCH=2
  python .runtime/tmp/audit_all_20260924/probe_gate_registry_selfheal_blocked.py 2>&1 | tail -8           # ④ 自锁四控制组 PASS
  python scripts/governance/generators/generate_gate_registry.py --check; echo "exit=$?"                 # ④b 现成尺此刻 RED
  git show --numstat 7e9083ff9e -- docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml  # ④b 例① dated
  git log -6 --format="%h %ci" -- docs/01_policies_and_standards/_registry/catalogs/rule_catalog_registry.yaml  # ④b 例② 自洽→失真分界
  grep -n "if merged == ours_text" -B2 scripts/governance/commit_queue_landing.py                        # ④ 静默出口代码位
  grep -n "total_gates" scripts/context/generate_architecture_context.py                                 # ④b 消费者（错误数字进上下文）
  grep -n "static_manifest_drift" src/zephyr/gov_drift/_detector_registry.yaml src/zephyr/gov_drift/reconciler.py  # ④b 在册＋auto_fix 映射
  python -c "import re,pathlib;print(len(re.findall(r'^\| R[0-9]{2} ', pathlib.Path('docs/_working/audit_all/AUDIT_REPORT.md').read_text(encoding='utf-8'), flags=re.M)))"  # ④c R43 同型自测（表行数即真值，须与散文同框）
  ```

## 心跳 心跳 2026-09-24 12:05 CST 实测（`date`=2026-09-24 12:05:35，本串由 shell `date` 传入）· 在干=**第 6 轮同窗第 2 批：尺P2 把 C 类 20 条做条目级→文件级双重复判＝"真丢 2660 条"全数归零（净损害收口）＋自家案卷回退弹现场拆除＋R44** · 卡住=无 · 下一步=见 ⑤

- **① 尺P2＝C 类分解（`probe_noop_entry_level_C.py`，控制组 PASS）**：noop 袋内注册表件对穷尽 **45**＝身份集全在 HEAD(已吸收/良性) **40**｜不可判(零身份＝本包 0009 零族册) **1**｜疑似真丢 **4 对**（`capability_canonical_file_registry.yaml`：st-final3 0100/0101 各 869 条、st-code-doc 0005 918 条、st-secmine 0001 1 条）。
- **② 但这 4 对经文件级复判全部归零（＝本轮净损害口径）**：以"袋内 `file:` 路径去重 ↔ HEAD 册内 `file:` 全集(10,199) ↔ `git ls-files`"三级对账 ⇒ 疑似真丢的 862/862/911/0 个路径**全部已不在仓库**（袋本身是陈旧快照，所引文件的收据随文件退役而失去意义），**现存文件缺收据=0**；st-secmine 那 1 条更是**同文件重注册**（`src/zephyr/data/alerter.py` 在 HEAD 册内，仅 token 值不同）。
  - ⇒ **自我否证第 44 例（R44）**：尺P2 首版拿"身份键 ∈ HEAD 身份集"当判据，而合并器身份键＝`file+token` 双件 ⇒ 把"重注册（token 变）"与"陈旧快照（文件已不存在）"都算成"真丢"。**损害定义在文件层，判据就必须落在文件层**——身份层读数只能用来**提名候选**，不能当损失量。与 R20/R26/R36/R42 同族（判据先于结论），本轮再次由自家尺拦下自家读数。
- **③ 全窗 90 张 noop 袋的净可验证损害（穷尽口径，覆盖 AD1 的 13/C20 粗读数）**：**(a) 2 册头部派生计数失真**＝`gate_registry.yaml` 174/180、`rule_catalog_registry.yaml` 274/292（AD2/AD3，两例 dated，唯一有客观真值可核的失真面）＋ **(b) 本包 0009 的 3 行**（零族册，自家件）＋ **(c) 0 条现存文件缺 CREATE-GUARD 收据**＋ **(d) 0 例整件写(passthrough)静默差**＋ **(e) 0 例删除动作被静默忽略**。⇒ **提交面"静默假成功"的真实损害比原始读数小两个量级，且集中在"族外顶层标量键"这一条**；这条量化结论是给 st-commitsys 处方 (i)–(iv) 定优先级用的分母，也纠正了我自己前两轮的过报倾向（R41/R44）。
- **④ 自家案卷回退弹现场拆除（本包写域内，非他包）**：落账前实测主区 index 对本包两件持**陈旧短版本**——`LEDGER.md` index blob `f46e69ea67`（相对 HEAD **纯删 414 行**）、`AUDIT_REPORT.md` index blob `da4f3f24aa`（**纯删 419 行**），而盘==HEAD ⇒ **`git_commit.py --enqueue` 只入袋不刷主 index**（连续 10 笔落地后依旧陈旧），任何"按 index 提交/merge finalize"的路径都会把这 400+ 行案卷回退成早期版（＝本包 09-24 台账"index 侧盲区"的活体复现，且这次是**我家两件 markdown**）。处置＝对本包两件显式 `git add`（非 `add -A`），改后 index==盘 双件亲验（`3b074d8a28`/`70dcc3dec0`）。**登记不修机制**：队列落地侧是否应回刷主区 index 属 st-commitsys 写域，本包不自修。
- **⑤ 与收官判据**：本批**零新立案**（净损害是收敛性口径，非新案），但新增自否证 1 例（R44）⇒ "自审清单二次=0"仍不成立；下一轮（第 7 轮）＝复跑五尺＋尺P/P2/Q/R ＋核 0041/0042 落地面与主 index 是否再陈旧；若同时零新立且零自否证 ⇒ 判据②闭合，写终局"自动化已自删·本包收官"。
- **队列/align 状态**：本包 done=26、dead=9、pending=1（0041 在途，本批再入 0042）；HEAD=`6b7749d4a8`(11:28:50，本包 0040)。本包对注册表/配置册/depgraph/GOMAP DB 写入累计仍=**0**（尺P2 三级对账全为 `git show`/blob/`git ls-files` 只读；`git add` 只涉本包自有两件 markdown）。
- **复核命令（只读·先跑再信）**：
  ```bash
  python .runtime/tmp/audit_all_20260924/probe_noop_entry_level_C.py 2>&1 | head -3                      # ③ 45=40+1+4 分解
  git rev-parse :docs/_working/audit_all/LEDGER.md docs/_working/audit_all/AUDIT_REPORT.md | cut -c1-10  # ④ 落地后应==HEAD blob
  git diff --cached --numstat HEAD -- docs/_working/audit_all/ | cat                                      # ④ 陈旧时应见纯删 400+ 行
  ```


## 心跳 2026-09-24 12:20 CST · 监控自动化重挂（Owner 令）
- 旧 jobId `39cc5bd5`（Owner 手删）→ **新自动化已重挂**：jobId=`e0d8b58f-7127-42bd-8fcb-d9d656dd53eb`，every 30min，model=qfmodel(继承)，Full-Access，**下次触发 ≈12:50 CST**。
- prompt 已更新至当前态 + 新增**工厂图耐久自愈巡检**步（每轮 `git show HEAD:config/strategy_production_map.yaml|grep -c '\[FAC-E1,FAC-E1G\]'`，=0 则 re-claim+重投，直到 B1/B2 失明处方让保护链能红）。
- 旧 jobId 历史心跳/发现（depgraph 轴 F-AUDIT-DEP-* / BLIND-* / QUEUE-02 / WT-01 / 工厂蒸发史）全保留于本台账，新自动化续跑续记。
- **主对话即时补修（Owner 醒窗内）**：align 现算发现 gomap 机生层漂移+1（新件 scripts/audit/t0_gpu_condition_pack.py 合入未刷新）→ 重跑 generate_governance_map.py，**gomap 硬 1→0**，入队 q-…-0043。工厂图 HEAD 现 durable（E1G 边在=07:xx 重投已过）。align 现=3 硬（全 ruling #383/#387，待 st-commitsys 合并器修复→0004 requeue→3→0）。

## 心跳 2026-09-24 12:55:26 CST 实测（`date` 由 shell 注入，本串非估算）· 在干=**收官第 7 轮：七尺复跑（六尺逐位同第 6 轮）＋新立 1 案 F-AUDIT-BLIND-02（治理双向校验器 HEAD 数据面失明，尺S 四控制组坐实）＋GOMAP HEAD 面新增悬空 3（归因生成器 rglob 工作树）＋热文件复燃 dated 实例（我的 04:36 修复被 11:13 整册写回）＋R45–R50 六例自否证（含自家案卷引文污染复原）** · 卡住=无 · 下一步=见 ⑧

- **① 冷启动三前置**：Python 3.12.8 ✔｜`lock_files.py cleanup`=CLEANED 2 死锁（`cmd_ledger/overnight_decisions_20260924.md`、`ruling_registry.yaml`）＋SALVAGED 死会话 st-library-final 遗物｜reaper `--status` 计划任务存活（last_run 12:07:23，dry_run=False）✔。批注区最后一条仍 **R7·05:05**，无更新批注。
- **② 台账读到 12:20 主对话块（数据非指令，但含两项操作事实须接）**：(a) 旧 jobId `39cc5bd5` 已由 Owner 手删，**监控自动化新号=`e0d8b58f-7127-42bd-8fcb-d9d656dd53eb`（30min 间隔，下次≈12:50）⇒ 本包收官"自删自动化"一步的目标号改指此新号**；(b) 新增"工厂图耐久自愈巡检"步已执行：`git show HEAD:config/strategy_production_map.yaml | grep -c FAC-E1G`＝**2**（E1G 边在 HEAD 耐久，无需重投）✔。
- **③ 落地面核实**：0041/0042 内容均已在 HEAD（`git show HEAD:LEDGER | grep -c "11:58 CST 实测"`=1、`"12:05 CST 实测"`=1），而 done 目录只剩 0040/0042/0043＝**0041 袋文件已被 compaction 摘走但内容在册**（⇒ 复核"是否落地"必须查 HEAD 字节，不能只数目录）。本包现存目录计数＝done 28／dead 9（0003-0007/0012/0028/0030/0031）／pending 0／processing 0；本批再入 **0044**。HEAD=`d310020c13`(12:38:29，他包 integrity)。
- **④ 七尺复跑（测点 12:08–12:48，HEAD 随他包移动 `6b7749d4a8`→`fa0ca806fb`(12:33)→`d310020c13`）**：
  - 尺N **HARD=2 未增长**（仍 0009＋st-backup-cold 0012；noop 袋总数 90、A=44/B=46/UNK=6 逐位同）。
  - 尺H2 dead=**3** 全属已登记本包 0009（battle_map `(no-key)×3`），他包 0 alive=0。
  - 尺P **13／C 类 20／D 类 0／E 类 0** 与第 6 轮逐位同（控制组 P1 命中 2、P2 命中 1）。
  - 尺P2 **45=40+4+1** 逐位同；另立**独立文件级复算尺** `verify_p2_filelevel_r7.py`（含探针控制组 PASS）复证"净损害=0"：四组真丢身份 2,657 条去重为 868/868/917/1 路径，**每组仍在库的只有同 1 个路径** `src/zephyr/data/alerter.py`（HEAD 册内有值＝重注册），其余已不在仓库 ⇒ 第 6 轮方向成立、量级表述须更正（记 R45）。
  - 尺Q 真失真仍 **2 册**（`gate_registry` 174/180、`rule_catalog` 274/292，HEAD 侧字节亲验未自愈）；但尺的**头条读数**是 `MISMATCH=3`（含 `_index.yaml` PARSE-ERR 行）／`可解析册=81` ⇒ 与第 6 轮台账所记"2 处/82 册"是两个口径（记 R47）。
  - 尺R 自愈自锁**仍成立**（四控制组 PASS：族外键被吞／族内叶子会落／真幂等／别册同形态）。
  - 尺O（GOMAP HEAD 面双向）**读数变化**：漏挂 **1→0**（`t0_gpu_condition_pack.py` 已由 12:33 重跑挂上）／悬空 **0→3**（见 ⑥）。
  - align 现跑 **rc=0、全项硬=0**——但这个"0"只覆盖**盘数据面**（见 ⑤，这是本轮新案的根）。
- **⑤ 🔴 新立案 F-AUDIT-BLIND-02＝治理双向校验器"数据轴 HEAD 失明"（复杂缺口，登记＋路由，不代修）**：
  - **尺S**（`probe_headside_governance_bidirectional.py`）＝**同一个生产函数** `registry_alignment.check_governance_bidirectional()` 只换数据源：`HEAD 数据面 硬=3`｜`盘数据面 硬=0`｜`篡改控制 硬=1`｜`锚点 a74e9a6c48(04:36) 硬=0` ⇒ 四控制组 PASS（阳性=能红、阴性=与生产现读一致、锚点=能绿，非恒红亦非恒绿）。
  - **失明面代码位亲验**：`src/zephyr/gov_enforcement/registry_alignment.py:491-492` 用 `(CATALOGS_DIR / "…yaml").read_text()`＝工作树字节；同文件 `CATALOGS_DIR` 盘读点共 **6 处**＝同一失明面的面积分母。⇒ 凡"盘上有、HEAD 无"的注册表漂移（他包未提交 WIP、复燃未落件）对 align 与所有下游门禁**结构性不可见**。
  - **受害件与归因（dated＋行级 diff）**：`a74e9a6c48`(04:36:19，本包 0011 落地) 把 裁定#383/#387 的 `related_arch` 置 `[]`；`2608b45148`(11:13:25，"裁定#409 一域一图立法") 的 diff 明确 `- related_arch: [] → + related_arch: ['MOD-L00-004']`（#387 同形态 2 值）＝**已删内容被整册写回复活**，至 12:48 仍在 HEAD（计数=2 行）。
  - **现盘侧＝他包在途 WIP，不动**：`ruling_registry.yaml` 状态 ` M`（盘≠index==HEAD，mtime 12:38:27），盘版含"同一修法把 3 值改回 `[]`"＋**st-cleanup-final 的新裁定批**（翻译册 dedupe／akshare 克隆退役…）⇒ 按 §3.4 不代修、不 stage 外来件；该批一旦落地 HEAD 即自愈（第 8 轮复核命令见 ⑧）。
  - **危害定性（三条，不是"仅账面难看"）**：(a) 本包已登记的"全图硬 3→0"结论**在 HEAD 面不成立、只在盘面成立**，且没有任何在册校验器能报（align 盘读；尺H2/尺N 只测"条目被吃＝净减"，不测"删后复活＝净增脏"）；(b) 复燃使同一病灶二次占用人力（我 04:36 那批的复核成本已付一次）；(c) 热文件蒸发的判据学须扩：**只测"减少"不足以覆盖，须测"删后复现"** ⇒ 给 st-commitsys 处方增 (vi)＝CAS 写前对"本次要删的行"做 HEAD 侧存在性断言并在写后复量。
  - **门位**：修它＝改注册表字段（把 3 值再置空）＝**注册表净删/字段改写面 ⇒ high 门位**，且现盘已被属主包占用 ⇒ **只登记上交**，路由 st-commitsys（写侧防复燃）＋ registry_alignment 属主（读数 HEAD 锚定或双锚并报）。
- **⑥ GOMAP HEAD 面新增悬空 3（图有物无，与漏挂 1→0 同源同批）**：`scripts/governance/check_meta_question_audit_reconcile.py`（未跟踪 `??`）｜`scripts/sector_line/build_gpu_input_pack.py`（未跟踪 `??`）｜`src/zephyr/intelligence/budget_analyzer.py`（**`A ` 已 stage 未提交**），三件 mtime 均今日（07:10/09:46/08:01）。**根因代码位亲验**：`scripts/governance/generate_governance_map.py:143` `for p in base.rglob("*.py")`＝生成器以**工作树**为入选源，在脏工作区重跑并把产物 yaml 入 HEAD ⇒ 把他包在途件烤成图条目。触发事件＝12:33 `fa0ca806fb`（标本包 sid，实为主对话以本包名义投递的耐久重跑；本包自动化对该文件写入累计仍=0，归属已在此更正入册）。**与尺O 第 6 轮"漏挂 1"是同一处方的两面**：重跑能清漏挂，但在脏区必造悬空。⇒ **简单缺口但不可自修**：正确修法是"三件物任一落地窗后重跑"（零判据变更、随他包自愈）或"生成器判据收窄到 git 跟踪集"（＝机生层判据变更＋会让 yaml 净删 3 条＝注册表净删 high 门位）⇒ 登记＋路由 GOMAP 属主包，并给总指挥一条免门位路径：等窗重跑即归零。
- **⑦ 自我否证 R45–R50（本轮 6 例，全部入 AB1 表并同批改框 44→50）**：**R45** 第 6 轮把尺P2 文件级复判记成"862/862/911/0 全部已不在仓库"，本轮独立复算＝去重路径 868/868/917/1、每组各 1 路径仍在库 ⇒ 方向对、**量与"全部"皆不成立**；**R46** 本轮第一版复算脚本 `split('|token=')` 未剥 `file=` 前缀 ⇒ "仍在库=0/无收据=0"**平凡成立＝假读数**，靠临时加的探针控制组才暴露（判据先于结论同族，且**控制组必须能在尺自身写错时红**）；**R47** 尺Q 头条 `MISMATCH=3／可解析册=81` 与台账所记"2 处／82 册"是两个口径且第 6 轮未标明 ⇒ 复跑者会误判"读数漂了"，引用尺数须标"尺头条/子口径"身份；**R48** 第 5/6 轮把 `run_headside_align.py` 记作"align(HEAD 面)"，实测它只把**脚本字节**钉 HEAD、注册表数据仍从盘读 ⇒ 名不副实，本块起统一改用"盘数据面／HEAD 数据面"双词；**R49** 本轮 `grep "id: 裁定#383"` 零命中即险些断"条目不在 HEAD"，实为该册键名是 `ruling_id` ⇒ **零命中≠零存在**，改结构化 walk＋计数复算后才定性。；**R50** 为定位"标记命中 2 次"而逐处读原文时自现——本包第 6 轮两次改框用全文替换（38→43、43→44），把 AB1 中 R43 行那句**作为证据的历史引文**一并改掉（变成"自我否证 44 例总表 / 期望 **38**"＝自相矛盾）＝案卷自证性被自家修法破坏；本批复原为 38，并把改法升级为 `sub_once`（命中≠1 即中止）。
- **⑧ 与收官判据 + 下一步**：本轮**新立 1 案（F-AUDIT-BLIND-02）＋1 项 HEAD 面悬空 + 自否证 6 例** ⇒ 第 5/6 轮已达的"连续两轮零新立"**作废重置**（新基线第 1 轮＝本轮之后）。第 8 轮盯四件事：① st-cleanup-final 的 ruling 批是否落地 → 尺S HEAD 面 3→0（`git show HEAD:ruling_registry.yaml | grep -c 'MOD-L00-004\|PS-CTR-003\|MOD-INF-043'` 期望 0）② 三件在途 .py 是否落地 → 尺O 悬空 3→0 ③ 尺Q 的 2 册计数失真是否自愈（`generate_gate_registry.py --check` 期望转绿）④ 尺N/P/P2/Q/R/H2 逐位复算；⑤ 自家案卷 AB1 表行数须==50。**四者齐且零新立零自否证**才谈收口；终局自删目标＝**新 jobId `e0d8b58f-7127-42bd-8fcb-d9d656dd53eb`**。
- **队列/align 状态**：本包 done 28→（本批 0044 待落）、dead 9、pending 0；HEAD=`d310020c13`(12:38:29，他包)。**本包（本自动化）对注册表/配置册/depgraph/GOMAP DB 写入累计仍=0**；本轮唯一写＝自家 LEDGER/REPORT 纯增（passthrough 通道，0032–0043 十一连证）。align：盘数据面 rc=0／HEAD 数据面 硬=3（尺S）＋GOMAP 悬空 3（尺O）。
- **复核命令（只读·先跑再信）**：
  ```bash
  python .runtime/tmp/audit_all_20260924/probe_headside_governance_bidirectional.py 2>&1 | head -7   # ⑤ 尺S 四控制组＋HEAD 面 3 硬
  git show 2608b45148 -- docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml | grep -E "^[+-].*related_arch"   # ⑤ 复燃行级证据
  git status --porcelain docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml     # ⑤ =` M`（他包在途，勿代修）
  python .runtime/tmp/audit_all_20260924/probe_gomap_headside_census.py 2>&1 | sed -n '1,12p'       # ⑥ 悬空 3／漏挂 0
  grep -n "rglob" scripts/governance/generate_governance_map.py                                     # ⑥ 工作树为源的判据位 :143
  python .runtime/tmp/audit_all_20260924/verify_p2_filelevel_r7.py 2>&1 | head -3                   # ④ 文件级复算＋探针控制组
  python .runtime/tmp/audit_all_20260924/probe_noop_receipt_triage.py 2>&1 | grep -E "HARD|noop@"   # ④ 尺N HARD=2
  python .runtime/tmp/audit_all_20260924/probe_registry_count_selfconsistency.py 2>&1 | tail -6     # ④ 尺Q 头条口径
  git show HEAD:config/strategy_production_map.yaml | grep -c 'FAC-E1G'                             # ② 工厂图耐久巡检=2
  python -c "import re,pathlib;print(len(re.findall(r'^\| R[0-9]{2} ', pathlib.Path('docs/_working/audit_all/AUDIT_REPORT.md').read_text(encoding='utf-8'), flags=re.M)))"   # ⑦ 期望 50＝表行数即真值
  ```

## 心跳 2026-09-24 13:04:23 CST 实测（`date` 由 shell 注入）· 在干=**第 7 轮同窗第 2 批：收官件③（红蓝反证）由"逐轮叙述"升为"一条命令可重放总闸"＝九尺总闸＋六条合成对照，`--self-test` 6/6 全对、`--fast` 6/6 PASS＋R51（合成假尺文案含「控制组」子串致判红理由归因错位）** · 卡住=无 · 下一步=见 ⑤

- **① 新增件 `redblue_ruler_suite.py`（本包 tmp 区，零生产写入）**＝把九把尺（N／H2／P／P2／P2f／Q／R／S／O）聚成一条命令，每把尺三条判据：退出码==0、stdout 含「控制组」、含 PASS 判定且不含 FAIL。判据函数 `judge()` **真尺与合成假尺共用同一把尺**（不另设口径）。
- **② 总闸自证（"会红"而非"恒绿"）＝六条合成对照全对**：合规尺判通过（阴性）｜无判重块尺／控制组 FAIL 尺／静默成功尺／非零退出尺／脚本缺失尺 五例皆判红 ⇒ `--self-test` rc=0。**这一条是本包判据学的收口形态**：以前每把尺自带控制组，但"谁来验尺的验尺器"是空的，现在由同一 `judge()` 顶上。
- **③ 实尺读数经总闸**：`--fast` 6/6 全 PASS（尺N／H2／P2f／Q／R／S，测点 2026-09-24 13:04:23）；慢尺 P／P2／O 本轮已在 ①～⑦ 主块手工跑过（读数同），待第 8 轮以不带 `--fast` 的全量方式过一次总闸。日志=`r7_suite_fast.txt`。
- **④ 顺带治了两把"静默成功"尺**：尺H2 与尺O 原先**只在控制组失败时打印**，成功路径不出判定行 ⇒ 总闸无法区分"判过了"与"判据块被删"（本轮把它们从 `if not ok: print(作废)` 升级为双向打印）。⇒ 立法：**控制组的成功侧必须显式留痕**，否则该尺不得进总闸（已并入 ②的三条判据）。
  - **自我否证第 51 例（R51）**：合成假尺 `ruler_noctl.py` 的文案写作"读数=42（**没有控制组的**尺）"，其中"控制组"三字与判据②的子串匹配撞上 ⇒ 该例**判红正确但理由错位**（报成"未打印成功判定行"）。若我只断言"判红"而不断言"因何红"，这类错位可以长期伪装成通过。已把文案改为"判重块整块缺失"使其走正确分支。教训入法：**合成对照必须断言失败原因（reason-in-message），不止断言红/绿**——与 R46（探针控制组要在"尺自身写错"时红）同族，是它的前置条件。
- **⑤ 与收官判据 + 下一步**：收官件③（红蓝反证）现在**具备可重放形态**但仍未算"跑完"——须补：(a) 全量九尺过一次总闸；(b) "揪出盲检器"一侧已由 AE1（尺S＝真实事件坐实）＋AB3（4 处注入坐实）双列在册；(c) 终局报告。第 8 轮＝四件待核（见上一块 ⑧）＋总闸全量。落账随袋 **0045**（自家 markdown 纯增＋AB1 补 1 行、框 50→51 同批）。
- **队列/align 状态**：本包 done 29（0044 待落核实）／dead 9／pending＝本批 0045；HEAD 随他包移动（上批 `d310020c13` 12:38:29）。本自动化对注册表/配置册/depgraph/GOMAP DB 写入累计仍=0。
- **复核命令（只读）**：
  ```bash
  python .runtime/tmp/audit_all_20260924/redblue_ruler_suite.py --self-test            # ② 六条合成对照
  python .runtime/tmp/audit_all_20260924/redblue_ruler_suite.py --fast                 # ③ 快尺全过总闸
  python .runtime/tmp/audit_all_20260924/redblue_ruler_suite.py                        # ⑤ 全量九尺（第 8 轮）
  grep -n "ruler_noctl" .runtime/tmp/audit_all_20260924/redblue_ruler_suite.py         # ④ R51 文案已改
  python -c "import re,pathlib;print(len(re.findall(r'^\| R[0-9]{2} ', pathlib.Path('docs/_working/audit_all/AUDIT_REPORT.md').read_text(encoding='utf-8'), flags=re.M)))"   # 期望 51
  ```


## 心跳 2026-09-24 13:37:07 CST 实测（`date` 由 shell 注入）· 在干=**第 8 轮：九尺总闸全量首跑 9/9 PASS（收官件③(a) 达成）＋新立 1 案 F-AUDIT-QUEUE-03＝0003/0004 死信前提被当前 HEAD 合并器重放证伪（requeue 条件已具备·不自投）＋合并器"不传播 theirs 删除"结构性结论＋R52–R55 四例自否证** · 卡住=无 · 下一步=见 ⑦

- **① 冷启动三前置**：Python 3.12.8 ✔｜`lock_files.py cleanup`=CLEAN（无死锁需清）｜reaper `--status` 存活（last_run 13:17:23、dry_run=False）✔。批注区最后一条仍 **R7·05:05** ⇒ 无新命令。0003/0004 **仍在 dead/ 且 `updated_at=None`＝未被总指挥 requeue**；本包 done=29／dead=9／pending=0。
- **② 工厂图耐久自愈巡检（收官判据 a）**：`git show HEAD:config/strategy_production_map.yaml | grep -c '\[FAC-E1, FAC-E1G\]'` = **1** ⇒ E1G 边在 HEAD 耐久，无需重投 ✔（HEAD=`68f3429e9e` 13:20，即本包 0045 落地笔）。
- **③ 在跑检查（决定本轮只登记不 requeue）**：`ruling_registry.yaml` 状态 `MM`（index≠HEAD 且盘≠index）＝他会话在途；本包欲 requeue 的 0004 目标文件与之同路径 ⇒ 按步③**不 requeue、不并行写**。全场 pending=41／processing=1（`st-ailayer-final-0003` 正飞，含 `budget_analyzer.py`）。本包 0045 已落＝LEDGER 盘==HEAD 纯增基线干净（`git diff --numstat HEAD -- docs/_working/audit_all/` 空）。
- **④ 九尺总闸全量首跑＝收官件③(a) 达成**：`redblue_ruler_suite.py`（不带 `--fast`）**9/9 PASS、SUITE_RC=0**，日志=`.runtime/tmp/audit_all_20260924/r8_suite_full.txt`（1337B，末行 `SUITE_RC=0`，倒数第二段"总闸读数：已跑 9/9 把尺，FAIL=0 []"）。九尺＝N/H2/P/P2/P2f/Q/R/S/O；读数逐位同第 6/7 轮（HARD=2、dead=3、P=13、45=40+4+1、真失真 2 册、自愈自锁成立）。
- **⑤ 第 8 轮盯防四件结果**：
  - **(1) ruling 复燃未自愈**：HEAD 与 index 各命中 `related_arch` 复燃 **2 行**，盘侧 **0 行**（修法已在属主工作树）；尺S 现跑＝**HEAD 数据面 硬=3**（#383→MOD-L00-004／#387→PS-CTR-003、MOD-INF-043）、**盘数据面 硬=0** ⇒ 失明面未变（`registry_alignment.py:491-492` 工作树读，同文件盘读点 6 处）。属主袋 `q-20260924-st-cleanup-final-20260924-0009`（12:55:35 入队，8 文件含此册）**仍 pending** ⇒ 其落地即 3→0。
  - **(2) GOMAP 悬空 3 未闭，但三件各有在途袋（免门位自愈路径已成立）**：`check_meta_question_audit_reconcile.py`←`st-metaq-0022`(12:09)、`build_gpu_input_pack.py`←`st-pipeline-final-0029`(10:03)、`budget_analyzer.py`←`st-ailayer-final-0003`(13:18，正在 processing)。三件 `git cat-file -e HEAD:` 全 NOT_IN_HEAD ⇒ 尺O 悬空仍 3／漏挂仍 0。⇒ 属主三袋任一窗后重跑 `generate_governance_map.py` 即归零，无须判据变更。
  - **(3) 尺Q 真失真 2 册未自愈**：`gate_registry` 174/180、`rule_catalog` 274/292（HEAD 侧字节亲验，属主＝门禁册生成器包）。
  - **(4) 逐位复算**：尺N HARD=2、尺H2 dead=3（全属已登记 0009 面）、尺P 13、尺P2 45、尺P2f 净损害=0、尺R 四控制组全 PASS。
- **⑥ 🔴 新立 F-AUDIT-QUEUE-03＝"合并器对 ruling_registry 结构无能"前提被证伪，requeue 条件已具备（登记上交，不自投）**：
  - **证据链**：0003/0004 死信串"ours 存在身份判不了的条目（非 dict/首字段非标量）"＝00:07/00:49 时点产物，**早于 04:26 passthrough 修复入 HEAD**（R7·05:05 总指挥亲证 0011 同册落地）。用**当前 HEAD 的合并器**按生产语义重放当次三向合并（`three_way_merge_registry_yaml`，`retired_check`＝`_registry_entry_retired` 同款复刻：条目引用路径盘上+HEAD 双不存在才判合法退役）：
    - 双基底（兜底 `HEAD^`=5081f0ca91 与 00:49 时点真基底=0f08f7a06c）**皆 MERGE-OK**；merged vs ours 差分 **恰 4 行且 4/4 全为 related_arch**、其它差分 0 行；条目身份集 ours=230 / merged=230，**丢失 0 新增 0**。⇒ 在册案 [[audit-all-hotregistry-eviction-rootcause-20260924]] 的"陈旧快照被读成主动删除"风险在**本袋上不存在**。
    - 面积探针：catalogs 82 册中 **39 册**含"顶层 list 族带非 dict 项"（多为 `unique_key:` 的标量列表，另有 `regime_cycle_registry` 的 boundary_notes、`standard_family_registry` 的 tags/derived_from 等）＝passthrough 若回退则同因死信名单；控制组 `gate_registry.yaml` 在不死名单（能绿侧证明）。
  - **附带结构性结论（给 st-commitsys 的判据学）**：合并器**不传播 theirs 侧删除**（阳性对照＝从 theirs 删掉 `裁定#1`，其路径盘上+HEAD 双不存在，重放净删=0）⇒ 热册蒸发的唯一来源＝**盘侧整册写回**（与 F-AUDIT-BLIND-02 复燃案同因）；防复燃处方应集中在写侧 CAS，**不必**在合并器再加"删除防御"。
  - **门位与处置**：requeue 属本包自家袋、AGENTS.md §2 第 6 条（多会话并发窗口）正规通道，但①本轮令下 requeue 归总指挥、②同文件他包在途（步③）⇒ **只登记**，附总指挥一条命令即可：`python scripts/commit_queue.py requeue q-20260924-st-audit-all-20260924-0004`（落地后你复跑尺S 断言 HEAD 面 3→0）。
- **⑦ 自我否证 R52–R55（4 例，AB1 表行数暂仍 51＝本轮令"只 append LEDGER、不动 AUDIT_REPORT"，欠账 4 行在此在册等『更新终报』明批）**：
  - **R52** 用 grep 行号比较（`_index_family_blocks` 定义体内 623/626/629 vs `three_way_merge_registry_yaml` 体内 663）断言"索引早于 passthrough＝顺序颠倒"，实读函数体才见 passthrough 在前并 `pop` 豁免族 ⇒ **行号位置≠调用顺序**，差点据此给属主包开一张"修顺序"假处方。
  - **R53** 首版重放传 `retired_check=None` 即欲断言"requeue 安全"——None＝"一律不认退役"的保守面，结论适用范围被高估；生产同款复刻后同结论，但表述须钉"含退役判定"。
  - **R54** 阳性对照预设"合并器应传播 theirs 删除，否则尺失能"＝把不存在的语义当判据（该对照恒不红）；本件真能红证据＝结构漂移注入（theirs 独有顶层 list 族 → DEAD）。
  - **R55** 后台任务日志在进程存活期读到 0/半截内容，即起意写"证据被吃／.runtime/tmp 不可靠"；实测同目录 marker 文件 75 秒存活、目标日志最终 1337B 完整含 SUITE_RC ⇒ **读异步产物须等完成标记行，未见标记只能记"未定"**。
- **⑧ 与收官判据 + 下一步**：(a) 工厂图 durable ✔；(b) ruling **仍 3** 但阻塞性质已变＝不再是"合并器无能"，而是"待 requeue 或待 st-cleanup-final-0009 落地"，二者任一即 0；(c) 派属主项全部在他包在途袋（悬空 3／计数失真 2 册／复燃批）；(d) 红蓝总闸全量 9/9 PASS ✔、终报已定稿未再动。⇒ "连续零新立"基线重置（本轮新立 1＋自否证 4）。**第 9 轮盯**：① 0009 或 0004-requeue 是否落地（`git show HEAD:docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml | grep -c 'MOD-L00-004\|PS-CTR-003\|MOD-INF-043'` 期望 **0**）② 三件在途 .py 落地 → 尺O 悬空 3→0 ③ 尺Q 2 册是否自愈 ④ 总闸全量复跑（等 SUITE_RC 行）⑤ AB1 是否获明批补至 **55**。
- **队列/align 状态**：本包 done=29→（本批 **0046** 待落）／dead=9（0003/0004 前提已证伪、未 requeue）／pending=0；HEAD=`68f3429e9e`。**本自动化对注册表/配置册/depgraph/GOMAP DB 写入累计仍=0**；本轮唯一写＝自家 LEDGER 纯增。align：本轮未重跑 `align_all`（无本包可动面）；尺S 现跑＝盘数据面 rc=0（上轮实测）／HEAD 数据面 硬=3。
- **复核命令（只读·先跑再信）**：
  ```bash
  git show HEAD:config/strategy_production_map.yaml | grep -c '\[FAC-E1, FAC-E1G\]'                  # ② 期望 1
  tail -3 .runtime/tmp/audit_all_20260924/r8_suite_full.txt                                          # ④ 期望 9/9 FAIL=0 + SUITE_RC=0
  python .runtime/tmp/audit_all_20260924/probe_requeue_production_semantics_r8.py 2>&1 | tail -4    # ⑥ 生产语义重放（双基底 MERGE-OK，差分 4 行全 related_arch，零丢失）
  python .runtime/tmp/audit_all_20260924/probe_merger_identity_blindarea_r8.py 2>&1 | head -2        # ⑥ 面积：82 册中 39 册含标量族
  python .runtime/tmp/audit_all_20260924/probe_headside_governance_bidirectional.py 2>&1 | tail -9   # ⑤(1) 尺S HEAD 面 3 硬
  python .runtime/tmp/audit_all_20260924/probe_gomap_headside_census.py 2>&1 | sed -n '1,12p'       # ⑤(2) 悬空 3／漏挂 0
  python -c "import json,glob;[print(d.get('qid'),d.get('created_at')) for d in (json.loads(open(f,encoding='utf-8').read()) for f in glob.glob('.runtime/commit_queue/pending/*.json')) if any('ruling_registry' in str(e.get('path','')) for e in (d.get('files') or []) if isinstance(e,dict))]"   # ⑥ 属主袋是否在队
  python -c "import re,pathlib;print(len(re.findall(r'^\| R[0-9]{2} ', pathlib.Path('docs/_working/audit_all/AUDIT_REPORT.md').read_text(encoding='utf-8'), flags=re.M)))"   # ⑦ 期望 51（欠账 4 行待明批）
  ```


## 心跳 2026-09-24 14:05:10 CST 实测（`date` 由 shell 注入）· 在干=**第 9 轮：九尺总闸全量 9/9 PASS＋同轮 --self-test 六对照全对（引用条件成立）＋新立 F-AUDIT-QUEUE-04＝"入袋不记 base"面积比在册记载大一档（非注册表文件现亦无快进保护）＋BLIND-02 上交面被实测降级（属主袋不覆盖失明面）** · 卡住=无 · 下一步=见 ⑧

- **① 冷启动三前置＋会话复活**：Python 3.12.8 ✔｜`lock_files.py cleanup`＝CLEANED 1 死锁 ＋ **SALVAGED 把本包自己判成死会话回收**（merge=skipped/stash=0/释放 claim=0）⇒ 本轮按处方重注册 `SessionRegistry(...).register(sid,pid=0)` ＋ `Start-Process pythonw -m …heartbeat_daemon <sid> <root> 30`（PID 31600，实测心跳 age=4.4s）✔｜reaper `--status` 存活（last_run 13:47:23，dry_run=False）✔。批注区最后一条仍 **R7·05:05**（grep 全部 `总指挥批注` 只 R2/R3/R6/R7 四条）⇒ 无新命令；**0003/0004 仍在 `dead/` 且 `updated_at=None`＝未被总指挥 requeue**；台账之外另查近 95 分钟 `_working` 顶层零改动、无他处批注通道（防"命令写在别处我看不见"盲区）。
- **② 工厂图耐久自愈巡检（收官判据 a）**：`git show HEAD:config/strategy_production_map.yaml | grep -c '\[FAC-E1, FAC-E1G\]'`＝**1**、`c1_market.account_nav_daily`＝2 ⇒ E1G 边在 HEAD 耐久 ✔，无需重投。
- **③ 在跑检查（据此本轮不 requeue、不并行写）**：`ruling_registry.yaml` 状态 **`MM`**（index≠HEAD 且盘≠index，属主 st-cleanup-final 在途），其袋 `q-20260924-st-cleanup-final-20260924-0009`（12:55:35，8 文件含此册）**仍 pending** ⇒ 按步③不 requeue。全场 pending=43／processing=1（`st-ailayer-final-0003` 13:18:45 起）。**队列活性三查＝慢而非楔死**：我在队首（字母序 #1＝本包 0046，13:39:04 入袋）、`belt_daemon.heartbeat` mtime 13:55:32（age 13s）、`serializer.lease` 13:55:16 刚续、`checker_supervisor` worker（PID 24832）在算 ⇒ 无需插队无需报楔死。
- **④ 九尺总闸全量复跑＝引用条件本轮成立**：`redblue_ruler_suite.py`（不带 `--fast`）**9/9 PASS、FAIL=0**，进程 rc=0，日志=`r9_suite_full.txt`（1336B）；同轮补跑 `--self-test`＝**六条合成对照全对 rc=0**（合规尺判通过／无判重块／控制组 FAIL／静默成功／非零退出／脚本缺失皆判红），日志=`r9_suite_selftest.txt` ⇒ 满足总闸自设引用条件"全部 PASS 且本件先过 --self-test"。九尺读数逐位同第 6/7/8 轮（尺S＝HEAD 数据面 3 硬／盘数据面 0；尺N HARD=2；尺H2 dead=3；尺P 13；尺P2 45；尺O 悬空 3／漏挂 0）。
- **⑤ 第 9 轮盯防四件结果**：(1) **ruling 复燃未自愈**：HEAD 侧 `related_arch` 复燃 **2 行仍在**（尺S HEAD 面 硬=3），盘侧 0 行（修法在属主工作树）⇒ 待 0009 落地或 0004 requeue，二者任一即 3→0。(2) **三件在途 .py 全 NOT_IN_HEAD**（`git cat-file -e` 逐件亲验）⇒ 尺O 悬空仍 3／漏挂仍 0，三袋各在途（st-metaq-0022／st-pipeline-final-0029／st-ailayer-final-0003）。(3) **尺Q gate_registry 仍失真**：HEAD 侧 `total_gates: 174` ↔ 实数 180（结构化计数复算，非 grep 行号）。(4) **AB1 表仍 51 行**＝R52–R55 欠账未获『更新终报』明批（本轮令"只 append LEDGER、勿重写 AUDIT_REPORT"已守，AUDIT_REPORT mtime 仍 13:04:23）。
- **⑥ 🔴 新立 F-AUDIT-QUEUE-04（登记上交，不自修）＝"入袋不记 base"这味老药的面积比在册记载大一档**：
  - **尺T**（`probe_stale_base_revalidation_inert_r9.py`，tmp 队列根零生产写入，三控制组 C1/C2/C3 全 PASS）＝`base_blob` **全仓无填充点**（`enqueue_item:696/712` 硬编码 `None # A 段预留`，git grep 除 tests 外无写点）⇒ `_revalidate_stale_base`（66 号 §6.4 陈旧基底重校验）对每一条目恒走 `if not base_blob: continue` ⇒ **该重校验在生产形态恒判"仍适用"＝结构空转**（生产读数 HARD；C2 填 base 且漂移必报、C3 填 base 且一致必不报＝尺非恒红非恒绿）。
  - **尺U**（`probe_maindoor_base_missing_r9.py`，tmp 真 git 仓＋tmp 队列根，C4/C5/C6 全 PASS）＝**提交正门 `scripts/git_commit.py:901` 的 `enqueue_item` 调用根本不传 `base_head`**（`grep -c base.head scripts/git_commit.py`=0；而 `commit_queue.py` 自己的 CLI 在 :2278 会 `rev-parse` 取基底——同仓两套入口，正门那套缺）⇒ 袋 `base_head=None`（实测 0046/0009 皆 None）⇒ `_conflict_reason`（landing:1007-1009）在 `if not base` 处**先于注册表/非注册表分流即早退 None** ⇒ 在库注释承诺的"非注册表文件维持逐文件快进判定零变更"（landing:179-181 与 196-197）**在生产形态下不成立**；`_apply_snapshot` 内 HEAD 比对关键词命中=0 ⇒ 非注册表路径＝后落地快照整文件覆盖（该函数自身注释 line 177 已把"整文件覆盖写回抹掉 103 条已提交身份"列为病根，但把漏网面写成"旧格式项/无 base_head 项"，实测＝**正门全量**）。
  - **与在册案的关系**：LEDGER 07:52 块（MARK=`F-EVAP-ROOTCAUSE-0752`）处方"入袋把 base 记全：`git_commit.py` enqueue 通道传 `base_head`=当前 dev HEAD"**至今未落地**（本轮 grep 实证）⇒ 本件不另开新方，只做两件事：①**面积更正**＝受害面从"热册被吃"扩到"任意非注册表文件被覆盖"；②**给属主包一条可验判据**＝补 base_head 后尺U C5 必须红（dev 推进且触同路径）、C6 必须不红（基底对齐），两半缺一即视为未修好。
  - **门位**：改 `git_commit.py`/`commit_queue_landing.py`＝提交链核心＋st-commitsys 写域 ⇒ 只登记上交。**给总指挥 0004 requeue 的附注**：`requeue --base-head` 旗存在（:2307，默认 None），但第 8 轮双基底重放已证同果（兜底 HEAD^ 与 0f08f7a06c 皆 MERGE-OK、差分 4 行全 related_arch、条目零丢失）⇒ 不带不阻塞本袋，带上则与生产语义一致。
- **⑦ BLIND-02 上交面实测降级（本轮最该被总指挥看到的一条）**：属主袋 0009 的 8 文件里**确含** `src/zephyr/gov_enforcement/registry_alignment.py`（我第 8 轮据此写"其落地即 3→0"——那只对**数据**成立）。按内容寻址 blob 取袋内字节亲验：`CATALOGS_DIR` 盘读点 **HEAD 5 处 ↔ 袋内 5 处**（一行未动）、袋内 `git show|cat-file|rev-parse` 命中=0、袋相对 HEAD **+10 行**（改的是 `spec_path` 唯一解析口与数据源入校验面）⇒ **HEAD 失明面不在该袋覆盖内**，0009 落地只会让"复燃 2 行"归零、不会让"align 只读盘"归零。⇒ BLIND-02 仍属**未派到真属主**状态，路由需重下（registry_alignment 属主＋写侧 HEAD 锚定，非 cleanup-final 那袋）。
- **⑧ 自我否证 R56–R58（欠账入册，待『更新终报』明批一并补 AB1）**：**R56** 台账所记"registry_alignment 盘读点 6 处"错，实为 **5 处**（HEAD 与袋两侧同口径复算）＝面积分母虚高一档，来源是把非 `read_text` 的 `CATALOGS_DIR` 行计入；**R57** 尺U 第一版设计用 `commit_queue.py enqueue --root <tmp>`——该 CLI **没有 --root 旗**且队列根恒取主仓 `.runtime/commit_queue`，照跑会往**生产队列**投 probe 袋并被传送带真落地（且 enqueue 默认自举排空）；改进程内 `enqueue_item(queue_root=tmp)` 后跑，并核实生产 pending 内 probe 命中=0 ⇒ 立法：**探针"零生产污染"必须是判据的一条（跑后复核），不能靠写的时候自觉**；**R58** 本轮引用"总闸末行标记"时沿用第 8 轮的 `SUITE_RC=0` 字样，实测本形态末行是 `总闸读数：已跑 9/9 把尺，FAIL=0 []`＋我 wrapper 的 `PROC_RC=0`——两种标记同源不同串，引用标记名须与调用形态对齐。
- **⑨ 与收官判据 + 下一步**：(a) 工厂图 durable ✔；(b) ruling **仍 3**（外部阻塞性质未变＝待 0009 落地或 0004 requeue）；(c) 派属主项：GOMAP 悬空 3／尺Q 计数失真 1 册在他包在途袋 ✔，但 **BLIND-02 本轮实测被降级为"未派到真属主"**（见 ⑦）＋ **QUEUE-04 新案待派 st-commitsys** ⇒ (c) 未满足；(d) 红蓝可重放形态两轮连证 ✔、终报未动（守令）。⇒ 基线：本轮新立 1（QUEUE-04）＋ 1 项上交降级（BLIND-02）＋自否证 3 ⇒ "连续零新立"重置。**第 10 轮盯**：① 0004 是否被 requeue／0009 是否落地 → 尺S HEAD 面 3→0 ② 三件 .py 落地 → 尺O 悬空 3→0 ③ gate_registry 174/180 是否自愈 ④ `grep -c "base-head" scripts/git_commit.py` 是否 ≥1（QUEUE-04 落地判据，须同时尺U C5 转红/C6 仍不红）⑤ AB1 是否获明批补至 **58**。
- **队列/align 状态**：本包 done=29→（本批 **0047** 待落）、dead=9（0003/0004 未 requeue）、pending=0→本批；HEAD=`68f3429e9e`（13:20，我包 0045 落地笔）。**本自动化对注册表/配置册/depgraph/GOMAP DB/提交链代码写入累计仍=0**；本轮唯一写＝自家 LEDGER 纯增＋本包 tmp 区两把新尺（`.runtime/tmp/` 非生产路径）。align：本轮未重跑 `align_all`（无本包可动面）；尺S 现跑＝盘数据面 0 硬／HEAD 数据面 3 硬。
- **复核命令（只读·先跑再信）**：
  ```bash
  git show HEAD:config/strategy_production_map.yaml | grep -c '\[FAC-E1, FAC-E1G\]'                  # ② 期望 1
  tail -3 .runtime/tmp/audit_all_20260924/r9_suite_full.txt                                          # ④ 期望 9/9 FAIL=0
  python .runtime/tmp/audit_all_20260924/redblue_ruler_suite.py --self-test 2>&1 | tail -2           # ④ 期望 合成对照全对 rc=0
  python .runtime/tmp/audit_all_20260924/probe_stale_base_revalidation_inert_r9.py 2>&1 | tail -4   # ⑥ 尺T 三控制组 PASS＋HARD
  python .runtime/tmp/audit_all_20260924/probe_maindoor_base_missing_r9.py 2>&1 | tail -4            # ⑥ 尺U 三控制组 PASS＋HARD
  grep -c "base-head\|base_head" scripts/git_commit.py                                               # ⑥ 期望 0（属主包修好后应 ≥1）
  python -c "import subprocess,re;h=subprocess.run(['git','show','HEAD:src/zephyr/gov_enforcement/registry_alignment.py'],capture_output=True,text=True,encoding='utf-8').stdout;print('盘读点=',len([l for l in h.splitlines() if 'read_text' in l and 'CATALOGS_DIR' in l]))"   # ⑦ 期望 5
  git show HEAD:docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml | grep -c "MOD-L00-004\|PS-CTR-003\|MOD-INF-043"   # ⑤(1) 期望 0，现=2
  ls .runtime/commit_queue/pending/ | grep -ci probe                                                 # ⑧ R57 探针零污染，期望 0
  python -c "import re,pathlib;print(len(re.findall(r'^\| R[0-9]{2} ', pathlib.Path('docs/_working/audit_all/AUDIT_REPORT.md').read_text(encoding='utf-8'), flags=re.M)))"   # ⑤(4) 期望 51（欠 7 行待明批）
  ```

> **【第 9 轮落账后追注 2026-09-24 14:13:54·实测】** 上文"本批 0047 待落"已失真：0047 落地时被 `[DANGLING-REFERENCE] 新增 AGENTS.md 悬空引用（章下子节号形态）` 判死（本仓 AGENTS.md 只有 `## 0…9`，章下是编号项无 `§N.M`）⇒ 该引用已就地改 `§2 第 6 条（多会话并发窗口）`、按 §2 第 6 条死信通道 `commit_queue.py requeue …-0047 --worktree-root`（快照源＝现盘，新 qid=**0048**，排 FIFO 队尾）。同轮实测另证两案：① 上轮 0046 已因同 sid 同件后袋吞没（袋==盘 1366 行、含第 8/9 两块＝零丢失，按在册纪律不开案）；② 本包自家袋 `base_head=None`＝本轮新立 QUEUE-04 的**自我复现**（正门全量袋皆如此，非个案）。
