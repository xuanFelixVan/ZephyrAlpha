---
ttl: task_bound
completes_when: 八项全部获裁定号后转 archived
---

# D 类裁定打包清单（8 项+补充材料）——st-taskcards-exec-20260921 收集，2026-09-21 夜

> 用途：一次性交 Max/Owner 裁完，替代零散催裁。每项只呈证据与选项，**禁自裁已遵守**
> （本会话未对任何一项自行拍板）。材料时点=2026-09-21 03:00-05:00 实测。
> 交由：Max 初裁（出裁定号），涉净删/Owner 门位项按宪法升级 Owner。

## D-1｜TC-02 步骤0：5 件 staged 处置权对表（总包 or 本卡）

- **这是什么**：docs/_working/rule_audit_campaign/ 下 5 件 staged 未提交（index.md、
  a2_handoff/index.md、a2_handoff/A2_M5_prescriptions.md、a2_handoff/rules_m1_repoint.patch、
  a2_handoff/rules_repoint_rows.json，本班 porcelain 复测仍 A 状态）。WO-15/w15 判语
  （code_doc_gov_campaign/p4_ledgers/w15_hanging_accounts_verdict.md 文件第 198-202 行）
  逐条判「C 类真未落地，留暂存待提交，交总包统一处置」；引用面已 19 处。
- **为何要裁**：w15 把处置动作推给「总包统一处置」，tc_02 卡要执行前必须对表认领，否则双处置。
- **不点会怎样**：5 件继续滞留暂存区（已 48h+），注册表 6 条 token 对 0 条入库文件的账实分裂持续。
- **机判证据**：git cat-file -e HEAD:各路径全 fatal（HEAD 无）；54 把锁零指向（tc_02 卡实测）。
- **硬墙预告**：.patch/.json 过不了 DIRECTORY-CONTRACT（docs/_working 仅允 .md/.csv/.yaml/.html），
  甲路线须转载体（tc_02 卡步骤 2 方案 a：转 .md 附录后删原文件）。
- **选项**：①并入总包批（w15 既判路线）②授权 tc_02 卡执行（甲向落地+token 收编）③让渡回总包另排。

## D-2｜TC-03 步骤1：X-5 CloneGuard merge 治本方案复核（【M】）

- **这是什么**：裁定 #369 已判 CloneGuard 拦截源 merge 治本（先例 30dc814645），施工未做；
  final3 W3 要求方案标【M】=Max 复核后在施工。
- **为何要裁**：merge 治本的具体落法需 Max 复核签字；复核通过即可施工原文 2.1 节。
- **不点会怎样**：在盘 +8/+26 编辑继续裸奔（本夜已建 .md 补丁备份防灭失=q-0002 批），
  WORKTREE-BASE-CONFLICT 伪门禁归因继续 UNKNOWN。
- **机判证据**：盘上 grep WORKTREE-BASE-CONFLICT 码2/测3，HEAD 版两文件均 0；备份件
  docs/_working/flash_speedup/t1_worktree_base_conflict_patch_backup.md（本夜落地）。
- **选项**：①复核通过授权施工 ②改 ack 白名单（**违 #369 与禁私开红线，不建议**）③再挂一周观察。

## D-3｜TC-04 步骤2：W2 提交链三项治本去留（随母题 close 后的孤儿施工）

- **这是什么**：三项治本候选（①落地面 blob 回灌主树 index ②qid done 短路 ③claim 路径空间统一）
  代码客观未做，但母题 #ARCH-324 已被 #377-G03 按 A 案裁 close。
- **为何要裁**：母题关闭后三项施工变成「对已关闭 issue 的孤儿施工」，去留需定性。
- **不点会怎样**：MM 假象/重复入队/claim 错配三类摩擦按现状带病运行（有临时防线）。
- **机判证据**：本夜补登 docs/_working/flash_speedup/F5_registry_debt/LEDGER.md
  （三项逐条未落地+复核命令，可机判）；「三项移交全部登记」旧声明正式证伪在案。
- **选项**：①随母题销项（三项登记为 known-limitation）②另立 backlog 卡 ③授权施工（需净窗）。

## D-4｜TC-05 步骤2：10 个词表滞后域定性——**材料更新：死结已解除，改追认**

- **这是什么**：原裁定需求=10 域 stable_fail（dataqa R3 实锤 test_check_vocab_domain_convergence
  两轮红）定「known-transitional 豁免 vs DB 旧域净删」。
- **本夜实测新事实**：10 域**已被某班收编进词表**（conv 校验器 known 79→89、合法值 62→72，
  2026-09-21 04:5x 实测 RC=0）；本班定向复跑该单测=**6 passed（4.54s）**——结构性死结不存在了。
- **为何要裁（新）**：①追认收编动作的授权来源（哪条线干的、是否过净删门位）；
  ②原 #335 过渡态口径是否随之关闭；③若收编含未批净删/改册，需补程序追认。
- **不点会怎样**：词表战役 W8 已按实测判据封账（w8_landing/landing_log.md），但收编者悬空
  =又一例「施工了不回写登记面」。
- **机判证据**：w8_landing/landing_log.md 基线三连表+单测复跑数字；dataqa R3 flaky 日志为旧态对照。
- **选项**：①追认收编+关闭过渡态口径 ②追认+保留 transitional 豁免标记一个观察期 ③回滚收编（不推荐，死结复活）。

## D-5｜TC-08 步骤1：A5 死会话接线遗产代落 + O-1/O1/O2/凭据四项补裁定号

- **这是什么**：residG 死会话的 pipeline_events 两段接线成品只在 G 盘冷库
  （G:/zephyr_cold/30_corpus/fullflow_harvest/20260918-194729/worktree/），主仓 grep=0
  （三次落地三次被回滚）；且 BT-P1-031（9098c65245）已重写该文件，旧成品须按新版重排。
  另 O-1（老蔡日期映射）/O1（对冲合约）/O2（warning 阈值）/凭据四项至今无裁定号
  （ruling_registry grep 零命中），O2 仅有 config/paper_hedge.yaml 注释级预裁
  （index_code: IM、beta×0.5、real_channel_locked: true）。
- **为何要裁**：代落死会话遗产=处置权问题（Max 裁）；四项预裁转正=裁定体系完整性（RULE-RULING）。
- **不点会怎样**：pf_alloc 日线管线的 L1 危机短路持续缺位（成品躺冷库）；四项预裁无号可引。
- **机判证据**：tc_08 卡 A 级取证表（冷库实测+grep 双向）；接线判据两段
  （crisis_block_check 短路 fail-closed / SIM_DAILY_KINDS FIFO 末位）。
- **选项**：①批代落（按 BT-P1-031 后新版重排两段接线）②判遗产失效另立施工单 ③只补四项裁定号、接线另议。

## D-6｜TC-09 步骤2：index.md vs README.md 双惯例口径

- **这是什么**：两套目录索引惯例并存——生成器产 index.md（#355/#356 口径）vs 丙线
  README.md(doc_type:index)（#384 WO-14 口径）；check_index_integrity /
  generate_missing_index_md 只认 index.md，README 替代面会被永久计缺（存量 findings 2100 条判定面）。
- **为何要裁**：口径不收敛则每轮扫描出假红，且两惯例继续分叉。
- **不点会怎样**：WO-14 归置落地后，integrity 检查器与归置现实永久脱节。
- **机判证据**：tc_09 卡实读检查器 203 行+dry-run；WO-14 staged 49 件 R+README A 在途（冻结至其落地）。
- **选项**：①统一 README 替代惯例（检查器改双认）②统一 index.md 惯例（WO-14 返工，代价大）③双认并存+去重规则。

## D-7｜TC-07 步骤2：standards_governance/__init__.py 两解（Owner 门位）

- **这是什么**：该路径未跟踪、从未入 ref、无豁免或 PEP420 裁定；但 HEAD 注册表 33015 行
  已预登记（账实脱节）；现靠 PEP420 隐式命名空间可导入。
- **为何要裁**：Owner 门位（tc_07 卡路由）；两解=补实体 __init__.py 过 CREATE-GUARD vs
  裁定 PEP420 豁免+注册表对齐。
- **不点会怎样**：账实脱节持续，后续施工在该包上的 CREATE-GUARD/导入行为不可预期。
- **机判证据**：git status+git log --all 零踪迹；注册表 33015 行预登记在案（tc_07 卡实测）。
- **选项**：①补实体 __init__.py（登记 token 随批）②裁定 PEP420 豁免+注册表条目改注 ③维持现状登记为 known-issue。

## D-8｜TC-09 步骤1：5 个工棚磁盘残骸拆除（Owner 门位）

- **这是什么**：.worktrees/ 下 5 棚全部无 git 注册（git 层已被 final3 W9-6 收口：
  分支删除+四证 ALLOWED 存档 09-18 20:51），纯磁盘残骸——st-auditdoc-v4-20260918
  15,533 文件+AI-GOVA-001/AI-TD2-GOV-001/AI-TD2-SEC-001/AI-VCFIX-001 四棚。
  OPS-GUARD 禁会话内删 .worktrees/**。
- **为何要裁**：删除面=Owner 门位（宪法人机门位+OPS-GUARD）。
- **不点会怎样**：「git 干净、磁盘 5 万文件」成常态，占盘且误导考古。
- **机判证据**：git worktree list 零条目+无 .git 指针（tc_09 卡实测）；worktree_abort.jsonl
  三连 ALLOWED 存证可引用。
- **选项**：①批拆 5 棚（外部通道/Owner 手删）②只拆 st-auditdoc-v4（证据最全）③留置。

## 补充材料｜ARCH-331 定义不可考（D-3 关联，补定义后才能补登记）

- R2 核查清单「ARCH-331（09-18 实测未登记；未登记号不具合法井号引用形态，故不加 # 书写）」全源零定义（桌面原文/归档/注册表全文/
  docs 全文检索均无）；可查的 #331 全部是裁定号（做T 砍，#304 撞号改号）。
- 无定义禁凭空造册：须原交接令作者或 Max 补一句「ARCH-331 是什么」后，登记批才能执行。
- 归置：本条已写入 docs/_working/flash_speedup/F5_registry_debt/LEDGER.md 附节。

## 移交登记项（非裁定，附带回执）

- known_data_gaps etf_minute_tz_split_pre_202607 status→resolved：**不代改**（甲线写域），
  已由 tc06_r1_closeout.md 路由至甲线 WO-3 的 A15 批（台账 A15 本含「etf 时区已执行改 completed」）。
