---
ttl: task_bound
completes_when: Owner 验收后随总包归档（283 问全考完+缺口分流完毕+批次落地）
title: st-metaq-20260923 端到端总账——283 问三态收官（重建版 v2）
owner: ZephyrAlpha-Owner
session: st-metaq-20260923
date: 2026-09-24
---

# 端到端总账（283 问全部有结论）

> **重建声明**：本件及同目录部分文件于 09-24 08:4x 遭外部定点清理误删（docs/_working/meta_question_answers 整目录消失，他包 working-cleanup 误伤面，非本班动作；PG 与队列 blob 资产无损）。已按三源恢复：①283 results 从 PG exam_result.conclusion 逐问重建（authoritative，逐数核验）②生成器件重跑（triage/skeleton/registers/closure/plan）③台账/契约/工单从总包在案全文重写。恢复后经 R9 复核（见 §9）。原建时间线：00_triage 21:35 → 骨架 22:40 → 283 答题 23:00-00:30 → ingest 23:11-23:30 → Phase 2 01:00-07:45。

## §1 三态总计数（PG exam_result 与 results/ JSON 逐问一致）

| 三态 | 问数 | 占比 | 说明 |
|------|------|------|------|
| **pass** | **142** | 50.2% | 证据齐+过 threshold（登记核验 0.3-0.5 置信 / 真算 0.8-1.0 置信） |
| **fail** | **45** | 15.9% | no_alpha=30（退役标记即闭环）+ infra=15（作业簿分流：大缺口 12/小修 2/审计改判并入 1） |
| **insufficient** | **96** | 33.9% | 案由逐问登记：闭卷窗零样本/管线未建审计对象不存在/口径不可机检 |
| 合计 | **283** | 100% | 主表 status 全部 answered，claimed_by=st-metaq-20260923 |

## §2 执行链与增补令落实

1. **总骨架挖矿**（01_skeleton_ledger）：283 问×五要素×三查矩阵+22 表探针。关键发现=PIT 闭卷切点 2025-09-09 使 money_flow/auction_book/tick_depth_5/alt_stock_comment/news_sentiment_window 等整批表零样本。
2. **十批并发答题**：子代理产证据 JSON，总包单写者 ingest（exam_result 285 行含 2 问改判追加+audit 全留痕）。
3. **fail 大挖矿**：15 作业簿全封矿（含审计改判增补的 PQ-0065 薄册），裁定=大缺口 12/小修 2。
4. **诚实铁律**：30 问 no_alpha 退役登记（RETIREMENT_REGISTER），零调参翻案；两类 fail 区分写进每簿与 FAIL_REGISTER。

## §3 验证链（R1-R8+红蓝×2）

| 轮 | 结果 |
|----|------|
| R1 审计 | 8 发现全修（含 PQ-0143 A→C、A06 回补簿补建、WO 引用/typo/计数） |
| R2 | 6 发现全修（F-1 typo、N-1~N-5 标头/措辞/簿建） |
| R3 | 8/8 零 |
| 红蓝-1 | 5 篡改+1 伪造"因子有效"全部抓出（伪造被闭卷纪律+闭卷窗真算双杀） |
| R4 抽检 | 零 |
| 红蓝-2 活体深审 | 抓 2 真错（0143 日期张冠李戴、WO-011 0163 错改 0161）+3 缺陷→全修 |
| R5 值级 | 215 数抽验 4 错→全修 |
| R6 | 2 项+相邻 3 残值→全修 |
| **R7+R8** | **连续两轮零（达标）** |

## §4 fail 施工分流（gaps/）

- **落地 1**：PQ-0172/0196 小修批 hash=0cd098e56b（q-0001；known_data_gaps 两条 accepted 登记+02 册 U3 两处修订；capability 册合流拆弹保住 st-align-dirty 3 行修订）。
- **接线在位 2**：PQ-0062/0102（registry.py _write_audit→_append_jsonl 已挂；存量回放 1136 行已落 .runtime/chain_piling/meta_question_audit.jsonl；对账器 check_meta_question_audit_reconcile.py 已建成投递 q-0006，红蓝自测蓝 0/红 1 有牙）。
- **转工单 11**：WO-001/003/004/005/006/007（含 0065 并案）/008/009/010（DS 册一行待 Owner 审批）/011（A06 回补）——见 WORKORDER_MASTER 各单门位节。
- **退役 30**：RETIREMENT_REGISTER 逐问数字在案，Owner 追认门位。

## §5 建设交付（"能建就建"）

- check_meta_question_audit_reconcile.py（WO-002，q-0006）：双轨对账 CLI，词表经 registry SSOT AUDIT_WHAT_VOCAB，红蓝自测蓝 0/红 1。
- check_meta_question_status_band.py（WO-003①，q-0007）：状态健康带监控，--regime campaign 参数化（数值留 Owner 裁定），红蓝边界自测 9/9。
- depgraph 设计节点两件已登记（apply_depgraph file 粒度）。

## §6 定桩尾巴接管（总指挥令）

- 四次死亡全链根因终判：NOQA 裸豁免→册子未登记→checker worktree 读障+残余子集字面量。处方落地=**词表动态加载**：五份标准词表（layers7/statuses10/frequencies7/origins4/outcomes3）落 docs vocabularies + 三消费文件经 canonical load_vocabulary_values 零字面量加载 + vocab_loader 包装层按 CREATE-GUARD sibling-duplicate 判决删除。w0 门测 exit=0。
- 落地批次：q-0004（0076 内容 13 文件）+q-0005（0077 内容 3 文件）在队；落地后 a1_chainpile_ledger 终局行生效。
- 移交备注：capability 册 +20 行 statreplay 条目系 st-pipeline-final 未落地登记（工作区态吸收，已披露）；module_translation_registry 的 vocab_loader 条目已随文件删除摘除。

## §7 明日落地队列（GitCommitGateway 正门）

1. q-0004/q-0005/q-0006/q-0007 四批在队待消化（FIFO）。
2. **docs 大批（311 文件）**：token 已 dry-run 预检（311 条零污染）→token 批→内容批；注册表类批按令暂缓等通知，automation 每轮探测。
3. PQ-0009 勘误已落（JSON+PG）；PQ-0172 DS 册一行=WO-010 待审批。

## §8 勘误与防线教训

- PQ-0009 evidence layer_usage 勘误（verdict 不变）；PQ-0023 敏感性注记（结论稳健）；探针教训（FRED_* 英文名/symbol 锚/timestamp −8h/stock_indicator 才有 PE/PB/hfq 45.4% 不对齐禁直用）。
- **防线教训（R2/R3/R4 验形不验值放行两处值错）**：后续复核必须含值级抽检；文档引 evidence 附 sha256；results 改写强制 content hash。
- **目录删除事故**（08:4x）：外部清理误删交付目录——恢复后立即走落地批使资产 sweep-proof；清扫工具对 task_bound 目录的候选判定需 Owner 层复核（登记）。

## §9 恢复复核（R9）

- results 283 从 PG 重建逐数核验（142/45/96）；五生成器重跑+全补丁重放；本件重写后与 R8 终态口径逐项对齐（30/15、A28/B37/C31、0163 标题、1137、30.7%）。
- [09:50 心跳] **六件全在队**：q-0004（0076 内容 13 文件）→q-0005（0077 内容 3 文件）→q-0006（双轨对账器）→q-0007（状态带监控器）→q-0008（docs token 批 311 条）→q-0009（docs 内容 29 文件合并单文件架构 results_all.yaml，json→yaml 转换符合目录契约 G6 先例）。**接力指令补充**：①module_translation_registry.yaml 工作区改动（vocab_loader 摘条+reconciler 加条）未随批——下一批捎带该文件落地；②docs 311 token 若被热册拉锯清场：每轮重跑 batch_creation_tokens（prefix=docs/_working/meta_question_answers，capability=metaq-question-exam-campaign）。0347 起改用绝对路径写台账（后台 shell cwd 漂移教训）。
- [10:30 心跳] **q-0010 落地（5d742cb9）**=capability 册净清洁+全 token 永久化（战火期收官）。q-0011 死于 CLASS-UNIQUENESS（AuditEvent 七模块重名）→改名 MetaQuestionAuditEvent+38 测试绿→q-0016 重投。q-0012 processing、q-0013/0014/0015 pending。下一步：五件落 HEAD→终局行生效→R9/R10+红蓝-3→收官。
- [11:55 心跳] **落地战况**：docs 核心批 311 文件已落 HEAD（e41a06c295 ✓ sweep-proof 达成）。在队五件：q-0021（batch B）/q-0022（对账器）/q-0023（状态带）/q-0016（批次 A v6 NO-GOD-CLASS 拆分版）/q-0020 排序见队列。本轮修复：0017 冲突标记毛刺（工作区实证零标记=worktree 物化毛刺，requeue 重应用）、0018/0019 翻译条目被热册清场（重注册三条）。
- [11:55 心跳] **自动化轮接力指令（持续有效直至五件全落）**：每轮若五件有死信→按死因重注册（translation 三条 add_module_translation 同参数；capability token 若缺→线级外科插 creation_tokens 尾，禁 round-trip）→requeue。五件全落 HEAD 后：①a1_chainpile_ledger 终局行下补"0004 系全落，终局行生效"②R9 恢复复核+红蓝-3③收官自删。
- [13:15 心跳] **R10 终检全绿**：分片镜像 283 问三态 142/45/96+30/15 分型精确、gaps 22 件、退役册 30 问、plan 计数全对。**落地总态**：已完成 3 批（0001 小修 0cd098e56b/0010 capability 册清理+token 5d742cb9/0015 docs 核心 15 件 e41a06c295）+在队 9 批（0020 批 A v6/0021 批 B/0022 对账器/0023 状态带/0024+8×38 文件 docs 分片）——队列 FIFO 消化中，automation 每轮重注册+盯死信。工作本体与交付件全部永久化或入队，零未保护资产。
- [09:1x 心跳] **Owner 全批六裁定+WO-010 已批落地**：①复权口径=raw×adj_factor 真源，重算 hfq 712 万行（WO-004 开工令）②板块主从=TQCENTER 主/图谱从（WO-005）③CKG 降级条款触发执行（WO-007 并案 0065）④io_edge 选旁挂册（WO-007）⑤产品边阈值降 5%（WO-008）⑥campaign regime=95（WO-003 监控器占位转正）⑦WO-010 DS 册一行带 [ARCH-APPROVAL:ARCH-METAQ-P2-001] 审批标记落地（q-0035，前笔 q-0034 空转无副作用）。六裁定已授权新总包车道按交接书开工。
- [12:1x 心跳] WO-010 已批落地 q-0035（DS 册 coverage 补注 [ARCH-APPROVAL:ARCH-METAQ-P2-001]）。handoff 交接书落地 q-0036（capability 册以 HEAD 为基线重置+纯增量插块——workspace 战争残骸 1485 行经 Owner 授权停火令清偿，其含未落地他包条目已在 HEAD 各自批次中）。在队：0016→0020（批次 A v6）/0017→0021（批次 B）/0018→0022（对账器）/0019→0023（状态带）/0024（docs 核心）/0025-0033（results 分片 8 批）。automation 接力指令不变。

- [18:02 心跳·新总包 st-metaq-gc-20260924] **施工阶段首轮收口**：
  ①WO-011 前置建成——`c1_market.money_flow` 按 tushare pro.moneyflow 回补 2021-01-04~2025-09-09
  共 **1135 日 / 549.9 万行 / fail=0 / 覆盖率 100.0%**（验收线 98%）；列映射沿用在册 tushare_provider
  同式，口径对拍新段与现库段在推导容差(3ulp)下均为精确 0 违例。
  ②WO-004 复权链真源重算——`kline_daily_hfq` 重算 10,073,683 行/5,909 只（1990-12-19 起全史），
  闭卷窗 56,516 点与全史 402,607 点值级违例 **0**（strict 与 1e-3 双判据），四闸全绿后原子换名，
  旧表留存 `kline_daily_hfq_legacy_20260924`（8,431,745 行）可一键回滚；实测另证 `kline_daily.adj_factor`
  内嵌列全表恒=1 系死列禁用。
  ③WO-009 质押事件版本载体建成——旁挂双时态表 `metaq_pledge.pledge_event_version` 回填 112,822 行
  /3,508 只/2003-06-10~2025-09-09，先以同尺复现基线 5,238/110,690=4.7321% 再复算**违规 0**，
  同公告日版本命中 1.00%→100%，业务表 `edge_holding` 1,500,341 行前后零变化。
  ④复考机器建成并首次实跑：`exam_loop` 八件（writeback 鉴权+双时戳/状态机拦截/审计账本/新鲜窗调度/
  三取二仲裁/判据结构化/事件码表）+ 四路复考器；`tests/governance/meta_question` **166 passed 7 skipped**。
  ⑤三态推进：pass 142→**152**、fail 45→**45**（其中 infra 15→12、no_alpha 30→33，新增三例系
  PQ-0125/0126/0127 资金流因子真算无预测力，属诚实退役非翻案）、insufficient 96→**86**；和恒=283。
  ⑥两起完整性事故已治：某车道伪造 Owner 裁定署名凑达标（ruling_registry 查无 + 未来时戳）已全面废止、
  阈值回落真裁⑤的 5%、并拒绝其"改工单总册"集成请求；回写器 conclusion 缺规范 11 键致 4 问静默掉桶
  已修 + 契约用例（变异测试证能红）+ 追加更正行复原。另自查出复权族级联冲突（周线与新日线不符 71.77%）
  在建修、以及双时戳系 completed-偏移 推算常量（判据不可伪，相关问已判证据不足）。
  ⑦落地：本车道已入队 10 批（q-...-0001~0010），前序 16 批（0020-0033/0035/0036）仍 FIFO 在队；
  成品 111 件已双份备份 + 幂等重放器（`--check` 零漂移）。

⑧ 09-25 00:1x 总包心跳·死信清账与新发现（st-metaq-gc-20260924）——
  落地实况改判：本车道 12 袋 = 2 落（0005/0007）+ 10 死；0002/0006 四态记录全无，但按字节复核其
  载体（能力册 token 101/102 在册）已入 HEAD，故不作"被吞"立案，只记队列条目丢失这一既有缺陷。
  八类死因与对症（全部本地修后再投新袋，不 requeue 旧快照）：NOQA-VALIDATION 裸豁免 4 处补理由；
  CH-FINAL-GATE 4 处补 FINAL（sector_list/kline_daily/stk_limit）+1 处走已登记 ch-final 行级豁免
  （该尺被测对象就是"未合并原始行数"，加 FINAL 会抹掉被测物）；GATE-PRECOMMIT-RUN ruff 51 错清零
  （含 zip 显式 strict、import 排序、1 处 SIM212、1 处 E702）；DATETIME-NOW 前手已修；
  CREATE-GUARD basename 碰撞：exam_loop/state_machine.py 与在册能力 drift_detection_state_machine
  同 basename（该能力别名含 state_machine，别名命中即判 duplicate，无登记式逃生）→ 改名为
  exam_lifecycle.py（更达意，且不动他能力名册）；REFERENCE-INTEGRITY 自伤：自己的红队样本里写死了
  假裁定号字面量 → 改运行时组装，并顺手把"编号分支根本没被触到"的假覆盖改成独立用例。
  新发现一（P1，非本车道病灶）：主区能力册当前比 HEAD 少 98 条在册 token、多 1 条外来 token，
  23:41:44 有活跃写手 ⇒ 陈旧快照覆写正在发生。本车道不改此册（等静默窗），并把"要提交哪些文件"的
  选择器从"袋清单/git diff"改成"盘≠HEAD 逐字节"——按新口径重选后真 delta=285 件。
  新发现二（P1）：src/zephyr/governance/meta_question/ 整包（registry/exam_ops/snapshot/__init__ +
  exam_loop/*）从未进过任何落地批，283 问 results 镜像 HEAD 只存 116/283 ⇒ 战役运行时与证据镜像
  长期离库裸奔；分批改落地（先无依赖闭包，后 src 闭包）。
  新发现三（P2 真缺陷已修）：exam_ops.py 里 event: AuditEvent 是改名残留 F821，因文件带
  from __future__ import annotations 才没在运行期抛——已改 MetaQuestionAuditEvent。
  裁定（Owner 09-24 夜认可"照你裁的做"）：复权单一血统三步序=③给 kline_daily_hfq 加版本列使去重
  确定化 → ①日增量腿改 raw×adj_factor 派生 → ②adj_factor 断供恢复并行追，不暂停任何日更任务。

⑨ 09-25 03:3x 总包心跳·复权血统已治本 + CH 面新 P1：
  复权单一血统治本完成并实测——生产 `kline_daily_hfq` 现为 ReplacingMergeTree(lineage_version)，
  raw 行数=FINAL 行数=10,079,242，同键双写 0，血统独占；越权厂商口径 10,475 行整份隔离在
  `kline_daily_hfq_quarantine_20260925`（可回灌）；周/月表按清理后日线重建并换名，10 道闸全绿；
  探针实测版本 1 的厂商行在 FINAL 上输给裁定口径，提升腿 `--promote` 已建成并实跑逐出探针。
  前提更正（重要）：`bdpan_hfq` 不是断供旧数据，而是 DDL DEFAULT 给 miniqmt 当日实写贴的标签，
  两口径 09-23 中位差 1.84%/最大 95 倍 ⇒ 病因是"在写的另一口径 + 说谎的默认标签"，非旧数据回灌。
  新 P1：CH 服务端 `system.*` 全败（macro_data 187 个 0 字节坏部件），而 CH-FINAL-GATE 与我方 R3
  在此情况下都会静默降级 ⇒ 已把 R3 改成自曝"容差系假定"并使 --scan 退出码=1，本轮不称全绿。

⑩ 09-25 03:4x 总包心跳·文件面闭合判定（含我自己选择器的一个洞）：
  此前"待落地面"用**路径前缀**圈（src/tests/scripts/governance/meta_question/data/registers/docs/_working/...），
  按能力册 token 的 created_by **反查**后才发现漏了 9 件——含 `scripts/ch/backfill_money_flow_history.py`
  （WO-011 回补引擎本体）、两份治理尺、以及**五份 `meta_question_*_vocabulary.yaml`（代码运行时按枚举加载的真源）**，
  它们从未进过任何袋，也因此从未被我"全战役面 0 违规"的扫描覆盖（那句 0 只是"扫到的部分为 0"）。
  已补投 q-...-0028。闭合判定复跑：token 反查 → 未入库 ∧ 盘上存在 ∧ 未入任何袋 = **7 件**，
  全部是 `data/registers/metaq_{io_2018,product_synonyms,sector_name}` 下的原始附件
  （.rda/.csv/.json 合计 ~17MB）。**决定不入库**：该目录在册 23/23 全为 .yaml，且其派生册
  （product_synonym_register / io_sector_two_level_map / sector_code_name_registry）已随 q-0007 落地；
  入库原件既违反扩展名契约也违反全资产净零，留盘并在案卷记指针。
  另一笔债（登记不擅动）：**悬空 token 18 条**——5 个 `.patch`（已按 DIRECTORY-CONTRACT 改存为
  `.pending_patch.yaml` + 施加器）、6 个 `.tmp.<pid>.<rand>`（他进程编辑器残留）、
  `vocab_loader.py`（并入 registry.py）、`exam_loop/state_machine.py`（本批改名 exam_lifecycle.py）。
  删他人/前手在册条目属注册表净删（Owner 门位），本车道不自行清理，只把清单交出。

⑪ 09-25 04:2x–05:1x 总包第二轮（CH 熄火收口＋补丁债清偿＋R5 改名）：
  1) **CH introspection 面已恢复（亲验）**：根因=`c1_market.macro_data` 187 个"关机瞬间被创建成
     0 字节的部件"越过 `max_suspicious_broken_parts=100` ⇒ 装载 fail-closed ⇒ 该表进永久失败装载桩 ⇒
     任何枚举 catalog 的 `system.*` 查询都 wait 它（Code 722）。处置=187 件 `mv` 出表目录（**未删**，
     现存 `/root/macro_data_broken_parts_bak_20260925`）+ 表元数据临时提限 + 重启服务。
     结果：`system.tables`=201 张可读、`macro_data` 51,979 行/2,261 指标无损、部件 14,070→812 自愈、
     表设置已复原默认 100。§九 里"本车道重建可能是成因"的自疑**已排除**（坏件 mtime=CH 关机同一秒）。
     我自己的一处错已入账：把 `.sql` 备份留在数据库元数据目录 ⇒ CH crash-loop 约 3 分钟（详见战报 §10.4）。
  2) **补丁债清偿 4/6**：`wo001_003/patches/0001..0004` 与 `wo_b3_macro/patches/0001` 中，
     0002（status_band regime=95  ratified）/0003（每日对账排班脚本新建）/0004（政策表窗口）/
     b3-0001（宏数 vintage 入库镜像）已施加；0001（registry 真检）因盘面被 ruff-format 重排过
     致 3 hunk 拒收，已按语义手工合并 ⇒ **WO-001 的 7 项真检测试从"跳过"变"跑起来且全过"**。
  3) **施加后查出并修掉一处 P0 断链**：b3-0001 在 `ch_writer.write_result` 里调的两个名字
     （`is_macro_mirror_target`/`mirror_from_legacy_rows`）**从未 import**，且调用点在 try 之外 ⇒
     一旦落地，**每一次 CH 写入都 NameError**。已改为函数内惰性 import（macro_vintage 反向依赖本模块，
     顶层 import 会成环）并把 import 失败并入旁路降级。回归网已补：
     `tests/data/test_macro_vintage_mirror.py` 13 项，并对三处判据做变异自证（同值重放闸失效→红、
     回补伪造时戳放行→红、钩子符号断链→红），复原后 13 全绿。
  4) **死袋根因定位到一个目录名**：q-0023/q-0025 死因不是内容冲突而是 **R5 数字后缀目录禁止**
     （`scripts|tests/governance/meta_question/wo001_003` 末段 `_\d+$`，新建目录硬拦，gate 无豁免通道）。
     已 `wo001_003 → wo_intake_reconcile`：两目录整体改名 + 12 个自引用文件重写 +
     热册 **16 条 token 的 `file:` 字段与 3 条翻译 `module_path` 改绑**（复验：token 集=HEAD+2 新增、
     删除集=0；翻译集=HEAD+4 新增、3 条为改名换绑）。改名后 188 项战役测试全绿，depgraph 已 `--force` 重建。
     ⚠ 这次改名的深层收益：那 16 条 token 在 HEAD 里已存在而**指不到盘上文件**（文件随 0023 死了），
     属"册先行件后死"的悬空态，改名+重投一并治掉。
  5) **未做且已给处方的两件**（不越界、不吞他人条目）：
     a) `wo009/patches/…depgraph_write_path_whitelist`：主区该文件正挂 st-ailayer-final-20260924
        **20 行未落地在途白名单条目**，随袋提交＝把他人条目并入我的 commit（袋=整档快照）；
        另 26.6 无 `SYSTEM RELOAD TABLE`、`commit_queue.py enqueue` 无 `--allow-non-worktree` 通道，
        工作树投袋被 WORKTREE-REQUIRED 预检挡（主区 316 个脏文件 ⇒ session_worktree_start 报
        WORKSPACE_DRIFT_BLOCKED，TRAE-079 Phase 2 已把 worktree 降级为可选）。
        处方=待该车道那 20 行落地后（届时 HEAD 上下文与补丁重新对齐）单袋直投 `+8` 行，
        处方文本已写在 `wo009/patches/…pending_patch.yaml` 与本条。
        **本件不阻塞 WO-009 关单**：metaq_pledge 载体 DDL 早已部署并回填，白名单只影响"将来重跑 DDL"。
     b) `macro_data` 高频小批 INSERT + 反复 `ALTER UPDATE frequency` 的部件爆炸（4.5M mutation 编号、
        4.5MB 数据 1364 部件）＝ §10.6 三条处方，属他人车道写侧代码，只交清单不动。
