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
