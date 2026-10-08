---
ttl: task_bound
title: "战役进度台账（实时更新）"
session: zc-chief-20260927
---

# 进度台账（91_progress）

| 时刻(本地) | 波 | 事件 |
|---|---|---|
| 01:5x | W0 | 体检绿：reaper 在岗/belt daemon 运行中/队列 3p+2proc/主区脏 557（他会话在飞，各线 claim 防撞） |
| 01:5x | W0 | 战役宪章+裁定台账+本台账+99 门位台账落盘 |
| 02:0x-02:5x | W1/W1' | 16 线并发发射：13 矿道+3 施工线 |
| 03:2x | W1 | **8 矿道交付 73 卷**：L00(骨架定版 Z=132=122+10 新增；29 候选实为 30 行→18 并入/10 新增/2 Owner)、L02(F13-F22,3 P0)、L05(F37-F45,7 P0；F42-F45 编排面实为 missing)、L07(F58-F69,5 P0；F68 T1 判卷 all_green=false 三阻断)、L09(F82-F93,1 P0=F88 LSG 运行时网不在岗；F92 系 ROOR 元数据漂移非空转)、L10(F94-F105,3 P0)、L11(F106-F115,F111 三方口径冲突实证：AGENTS L110 仍指 app_panel)、L12(F116-F122,无 P0) |
| 03:2x | W1 | **5 矿道限流折返**[1302]：L01(F01-F12)/L03(F23-F29)/L04(F30-F36)/L06(F46-F57)/L08(F70-F81)——控速复飞（≤3 并发） |
| 03:25 | W1' | **G 线落地 26d1dfb752**：撞号已被他会话 ef9e118ae7 先修（BLUEPRINT-FORMAT 77→130，后到者=DOC-HEADER-SUITE 保 77）；本线全表机判撞号对=0+补缺失的 registrar 级 fail-closed 回归测试（27+19 passed）；预检复活着证（本袋自身预检全链跑通） |
| 03:4x | W1' | **L 线落地 973b03c3a4+64c0a09865**：真凶双重=首轮 st-audit-fix-20260924 16:30:11 reconciler（clobber 窗内）+持续根因=HEAD COALESCE 修复自身缺陷（VALUES 求值期 NULL→'{}' 使守卫恒失效，影子表+生产双实证）；SQL 根修+shrink guard+68 条重放 0→68+34,236 register 实弹存活验证；42 passed/4 skipped；--feeds 复活（24_daban/游资温度 命中）。自伤披露：探针误伤 1 行已按死亡证明协议软删（event 1994629） |
| 04:0x | W1' | **P 线五项全落**：P1 str⧸date 共因 baee3850fd（norm_boundary_date 一处规整覆盖三实例，44+19 绿）；P2 l2_tick 系 09-09 已修+disabled 冻结非 bug，补真配置护栏 fb9011eee5（50 绿）；P3 etf_benchmark date_col 补声明 b9c2a69005（残余恒空 stub 登记 #19）；P4 restricted_shares 前瞻值上界 2d66c49156（24 绿含两件能红）；P5 realtime/suspend=东财/sina 反爬，换源须实弹→登记 #20；台账 cf9fa76e46；全量相关套件 118 绿 |
| - | W2 | 待：campaign 树 token 批登记（wide-prefix）+ 控速复飞 L01/L03 + Q 线解锁发射 |
| 09-27 08:35 | V 线 | V 线三件治理面红证/对账闭环 1c65406934：generate_gate_registry 三账 diff 段（21 测）+REFERENCE-INTEGRITY 活台配对红证（23 测）+tick 判重件红样 18 测；随批 capability 册 token 登记 |
| 09-27 16:29 | Q 线 | Q 袋真增量重贴 833284fe1e：关闭 enqueue/requeue 预检裸入口（lane-q 三文件，零回退重投） |
| 09-27 16:31 | 假绿战役 | autofix 三修 5d62909cb6：CI 治理入口+SSoT 路径漂移+ConfigCheck 读取腿（st-c7-autofix-20260927） |
| 09-27 16:59 | 治理工具 | 波5.2 裁定取号器+波1A.3 门禁三面对账表 bfdd84a440（散文周审计收敛为一张可复算表） |
| 09-28 02:59 | F62 | C-002 三门注入批重放 0cecaf771d：先报告后交易+日申报计数+盘中操纵监控进正门与 QMT 会话（前会话 st-f62-gates 三投全死后重放落地） |
| 09-28 03:59 | T 袋 | T 袋落地 1dd6c70c74：F40 候选池持久化+盘前通电／F41 L4-14 执行反馈环最后一米+九态映射桥（15 件） |
| 09-28 05:36 | 考试链 | t1_t2 交接件治理重构 fef8364c0e：MOD-BT-T1T2-HANDOVER 重构+测试收编（孤儿字节救援，ruff-format 死因修复重投） |
| 09-28 05:41-06:21 | 红蓝收尾 | wave7.3 红蓝三 commit：3065146281 reaper 孵化收割 PID 复用身份复核（缺陷②）／5103bbca85 GATE-DOMAIN-FK 补真域错挂归属判据（缺陷①）／ef96d76757 六向量红蓝用例落袋 |
| 09-28 07:48 | K 袋 | K 袋落地 461a86be17：F60 减仓编排进料+F61 KillSwitch 重启失忆窗闭合+PostSettlement 注册脚本形态探测器（复活死袋 q-20260927-st-chief7w-0004/0008） |
| 09-28 08:28 | E8/E9 | E8E9 袋复活 a349ddc1fe：F27 sleeve 装配+再平衡调度+TDM 对接／F28 影子组合对照+IS 决策时间戳链（21 件；死因 GATE-PRECOMMIT-RUN 四 hook，修复重投） |
| 09-28 08:41 | F56 判定 | F56 死袋判定=被 B7 超集取代：78982c4c81（st-zcloseout 接管袋B7）自含 phantom_grace_s/cancel_hold_s+18 测为更完整实现；kernel 件仓内零消费者 ORPHAN-MODULE 拦，三选一处方登记 99 #36 |
| 09-28 10:21 | 1A.5 | 死袋复活 6d0be14e4c：死指针改指活库+空壳源 fail-closed 预检+死指针尺（trae_034 与 99_skipped 两件剔除待裁，补登 99 #30-33/#35） |
| 09-28 12:32 | 跨队代修 | pf_alloc 史裁恢复 40003d97bb：allocation_inputs.py 本地常量 SQL_LATEST_ANCHORED_STATE 忠实恢复（probe-sql2 74a00a3605 误删致 import 断裂；09-25 史裁 schema 件 human_only，总包代修披露；13/13 绿） |

| 09-28 14:56 | 治理卫生 | ⚑-1② 判伪落档+99 台账合并 #21-#41+91 回填 a60cbe844e（含 376105ce64 误删五行恢复 #37-#41） |
| 09-28 15:11 | S4 工厂包 | F21/F22/F16 三修复收尾落袋 f28ce0d0f0（intake_ledger_recon 新件+台账 11 行补回；72/72 绿；CH rebuild 实弹留待） |
| 09-28 15:13 | W-156 | run_post_settlement_daily.ps1 假声明改锚 3dc18f13d6（手工/备份入口，非任务目标） |
| 09-28 15:41-16:12 | 挖矿救援 | 64 件 HEAD 外孤儿案卷 4 袋落库：068021b493 册先行(63 token)+06ec30c09c(32md)+603a8b404f(31md)+90d2e89f06(yaml)；64/64 token 零 CAS 冲突 |
| 09-28 17:0x | 终验处置 | 孤儿对抗测试退役 e36d0ff70f：test_dev_delivery_map/test_trading_day_cycle_map_adversarial 模块级 skip 随被测地图退役（验证器从未入 git，collect 炸弹拆除） |
| 09-28 17:0x-18:0x | 他会话交叉 | F62 清单闸写侧四连（5acdd1ef85/884e5639f8/03c1e41ab3/be37c89eb7）+F74 通知通道 d988f1e6d0+保留契约 v1.5.0 eda2898c52——总筹抽验通过 |
| - | 终验 | 两轮回归进行中（轮 1：library 195/gov_enf 104/ex_sor 616/signal_ashare 2850 全绿；governance 块A 3183P/5F 全分类；trading 2461P/2F 分类=CH 停机+负载敏感） |

## §终局四清单（总筹 st-zchief8-20260928 收官）

### ①已打通（全流通主链新增落地）
T 袋（F40 候选池+盘前通电/F41 反馈环+九态桥）｜K 袋（F60 减仓进料/F61 失忆窗+形态探测器）｜E8/E9 袋（F27 sleeve 装配+再平衡调度/F28 decision_timestamp+影子组合）｜S4 工厂包（F21 deferred 幂等/F22 llm_error 占坑/F16 台账对账器）｜t1_t2 交接件重构｜1A.5 死指针改活库｜F62 三门注入+清单闸写侧（他会话，总筹抽验）｜F56 判定=被 B7 超集取代（78982c4c81）｜pf_alloc 史裁恢复（40003d97bb）｜64 件挖矿案卷入库｜红蓝 wave7.3 八向量全闭合（V1-V8：6 拦+2 在案如实记录）+两缺陷修复（真域错挂门/PID 复用复核）。

### ②已修复（质量与基建）
落地链治本系列（2754cc9e6f TEST-SOURCE/94326c3bd9+a4211e4b16 head_reader/af7e492276 落地自证读回）｜红蓝两缺陷（5103bbca85/3065146281）｜孤儿对抗测试退役（e36d0ff70f）｜W-156 假声明改锚（3dc18f13d6）｜⚑-1② 判伪撤销（a60cbe844e）｜99 台账 #21-#41 合并+误删五行恢复｜91 台账断档回填。

### ③已排序待施工（二期，按优先序）
1. 合规门十闸余量接线（W-140：模拟盘执法先行，实盘面绑 TRD-A10 沙箱换版+30 交易日窗）｜2. F56 kernel 三选一（99 #36：a 委托 B7/b 例外面/等沙箱写侧进仓）（已做：edf0788dfb 选c墓碑+dd3b17f9fd 断腿重建，2026-09-29 回填）｜3. M1 封矿治理（F125/F127/F128/F130 装饰环接线或退役；裁-6 分母活边）（已做：794f16569b，2026-09-29 回填）｜4. trae_034 三死指针（PROTECTED-PATHS 待裁定通道，99 #35）（已做：1cf01067f5+7f9de37b2a，2026-09-29 回填）｜5. CH 复活后实弹批（etf_benchmark 重写#19/realtime 换源#20/intake_ledger_recon rebuild/apply_market_tables_ddl 执行）｜6. 二期序列：F53 Saga/F04 清洗四引擎/F74 铃铛余量/F73/F75/F92/F30/F05-F06｜7. 波9 回流 W-152..W-162。

### ④Owner 门位（99_skipped_for_owner.md #1-#41 全录）
高频提醒：#29 TRD-A10 沙箱换版+env=real（实盘前置）｜#34 裁-13 decision_timestamp 正式注册｜#35 trae_034 死指针｜#36 F56 kernel 三选一｜#8 见证层实盘域二次批｜#14 commit_queue_interactive 出厂翻转｜#21 F34 DDL --apply｜#25 F51 币圈退役｜#19/#20 换源实弹。其余见台账原文。

| 09-28 14:56 | 治理卫生 | ⚑-1② 判伪落档+99 台账合并 #21-#41+91 回填 a60cbe844e（含 376105ce64 误删五行恢复 #37-#41） |
| 09-28 15:11 | S4 工厂包 | F21/F22/F16 三修复收尾落袋 f28ce0d0f0（intake_ledger_recon 新件+台账 11 行补回；72/72 绿；CH rebuild 实弹留待） |
| 09-28 15:13 | W-156 | run_post_settlement_daily.ps1 假声明改锚 3dc18f13d6（手工/备份入口，非任务目标） |
| 09-28 15:41-16:12 | 挖矿救援 | 64 件 HEAD 外孤儿案卷 4 袋落库：068021b493 册先行(63 token)+06ec30c09c(32md)+603a8b404f(31md)+90d2e89f06(yaml)；64/64 token 零 CAS 冲突 |
| 09-28 17:0x | 终验处置 | 孤儿对抗测试退役 e36d0ff70f：test_dev_delivery_map/test_trading_day_cycle_map_adversarial 模块级 skip 随被测地图退役（验证器从未入 git，collect 炸弹拆除） |
| 09-28 17:0x-18:0x | 他会话交叉 | F62 清单闸写侧四连（5acdd1ef85/884e5639f8/03c1e41ab3/be37c89eb7）+F74 通知通道 d988f1e6d0+保留契约 v1.5.0 eda2898c52——总筹抽验通过 |
| - | 终验 | 两轮回归进行中（轮 1：library 195/gov_enf 104/ex_sor 616/signal_ashare 2850 全绿；governance 块A 3183P/5F 全分类；trading 2461P/2F 分类=CH 停机+负载敏感） |

## §终局四清单（总筹 st-zchief8-20260928 收官）

### ①已打通（全流通主链新增落地）
T 袋（F40 候选池+盘前通电/F41 反馈环+九态桥）｜K 袋（F60 减仓进料/F61 失忆窗+形态探测器）｜E8/E9 袋（F27 sleeve 装配+再平衡调度/F28 decision_timestamp+影子组合）｜S4 工厂包（F21 deferred 幂等/F22 llm_error 占坑/F16 台账对账器）｜t1_t2 交接件重构｜1A.5 死指针改活库｜F62 三门注入+清单闸写侧（他会话，总筹抽验）｜F56 判定=被 B7 超集取代（78982c4c81）｜pf_alloc 史裁恢复（40003d97bb）｜64 件挖矿案卷入库｜红蓝 wave7.3 八向量全闭合（V1-V8：6 拦+2 在案如实记录）+两缺陷修复（真域错挂门/PID 复用复核）。

### ②已修复（质量与基建）
落地链治本系列（2754cc9e6f TEST-SOURCE/94326c3bd9+a4211e4b16 head_reader/af7e492276 落地自证读回）｜红蓝两缺陷（5103bbca85/3065146281）｜孤儿对抗测试退役（e36d0ff70f）｜W-156 假声明改锚（3dc18f13d6）｜⚑-1② 判伪撤销（a60cbe844e）｜99 台账 #21-#41 合并+误删五行恢复｜91 台账断档回填。

### ③已排序待施工（二期，按优先序）
1. 合规门十闸余量接线（W-140：模拟盘执法先行，实盘面绑 TRD-A10 沙箱换版+30 交易日窗）｜2. F56 kernel 三选一（99 #36：a 委托 B7/b 例外面/等沙箱写侧进仓）（已做：edf0788dfb 选c墓碑+dd3b17f9fd 断腿重建，2026-09-29 回填）｜3. M1 封矿治理（F125/F127/F128/F130 装饰环接线或退役；裁-6 分母活边）（已做：794f16569b，2026-09-29 回填）｜4. trae_034 三死指针（PROTECTED-PATHS 待裁定通道，99 #35）（已做：1cf01067f5+7f9de37b2a，2026-09-29 回填）｜5. CH 复活后实弹批（etf_benchmark 重写#19/realtime 换源#20/intake_ledger_recon rebuild/apply_market_tables_ddl 执行）｜6. 二期序列：F53 Saga/F04 清洗四引擎/F74 铃铛余量/F73/F75/F92/F30/F05-F06｜7. 波9 回流 W-152..W-162。

### ④Owner 门位（99_skipped_for_owner.md #1-#41 全录）
高频提醒：#29 TRD-A10 沙箱换版+env=real（实盘前置）｜#34 裁-13 decision_timestamp 正式注册｜#35 trae_034 死指针｜#36 F56 kernel 三选一｜#8 见证层实盘域二次批｜#14 commit_queue_interactive 出厂翻转｜#21 F34 DDL --apply｜#25 F51 币圈退役｜#19/#20 换源实弹。其余见台账原文。
| 09-29 20:xx-09-30 04:xx | 总筹第二班 | 五遗留+四批文全施工：L09 根因修复 cf1018351b（StkLimit 每 run 68 次点查→缓存 0 次，717→126ms）；gov_audit 锁有界等待治本 cc730f6474+3ded37ff32；CH 实弹批（表核对 19/19、台账 rebuild 缺口=0、etf_benchmark 重写 3c01517bb2+f79a88a11e 实调 2370 行、realtime 换腾讯源 8479b8b7ce+b43af5cf7c 双源量纲互证）；批文②③④（trae_034 指针 1cf01067f5 两红转绿/裁-13=#420 落册 2963aaead9/F56 墓碑 edf0788dfb）；TRD-A10 准备件 337784b504（runbook+30 日台账+幽灵单日哨兵挂日终链）；六死袋复活五袋（belt 楔死换血+TEST-SOURCE 拆袋处方复用）
| 09-30 03:xx | 终验补账 | CR-007 计数尺七表补 ENTRY_SPECS+--update-entry-counts 回填（UNSPECIFIED 7→0、STALE 24→0，尺全绿）；错误码四码补登+TREEVIEW 前缀+ZA-MLS×4 随 F130 净删标 deprecated（袋在队）
| 09-30 04:xx | 终验定案 | 六目录两轮：chunkA 3157/3114 双零✓ chunkB r1 10381 零✓ r2 10387P+91F 已全归因（37=q0213 捞回批自曝 43F 基线/12=untracked 残渣已转存/42=状态漂移首曝其中错误码类已修、regen-clean 类=#431 战役在飞门翻中途态移交）｜trading 2458×2 双零✓（L09/FL09 双转绿）｜signal_ashare 2864×2✓ ex_sor 616×2✓ library 193×2✓ gov_enforcement 94×2✓ |

---

<!-- 以下整段由 st-chief7z-20261009 收口班追加（原拟单开 98 册，但新建 .md 的 creation_token 通道对 docs/_working 拒登记：工具回称"无待登记"而册内 0 命中，故内收进本册，不新增资产） -->

# 98 待裁总收敛与继任班台账（2026-10-09 00:xx）

> 本册是三本 Owner 册（`99_skipped_for_owner.md` 45 行 / `total_command_closeout/93_owner_menu.md` 42 项 / `night_sweep/99_owner_gate_menu.md` 61+9 行）的**去重收敛结果**，由四条并发核销车道对 HEAD 逐条实测产出，非任何册的自我声明。
> 证据文件（含每条命令与返回值）：`.runtime/tmp/st-c7v-owner-20261008/`、`.runtime/tmp/st-c7v-menu-20261008/`、`.runtime/tmp/st-c7v-night-20261008/`、`.runtime/tmp/st-c7v-dirty-20261008/`（临时区 24h TTL，重建配方见 §五）。

## 一、一句话结论

三册合计 **148 条申报**，逐条对 HEAD 实测后：**106 条已不需要你裁定**（已落地 36／已裁定 37／前提消失或已撤销 23／其余为重复申报），**真正仍需要你点头的只剩 18 项**（去重后；未去重 42 行）。同时查出 **2 处必须先纠正的账面不实**与 **1 个丢失的验收尺**。

## 二、诚信问题（先看这两条，它们决定其余条目能不能批量批）

1. **裁定#488 里 "C65 余菜单→按 99 册建议逐条批" 是一条覆盖本 148 条的总括授权**，而本仓自己的外部审查 `docs/_working/external_audit_mastertc/lane_g_open53_cards.md:83` 把它的授权链标为 **"待证（授权自述）"**，并点名 C65 是"最宽的越界项"；后续裁定#490 修了 C19/C18/C441，**唯独没管 C65**。
   ⇒ 后果：凡"唯一依据是 C65"的"已批"都不成立。核销车道查出的此类行：**B5 / B6 / B7 / B11 / C9 / E10 / B17 / F11**（B11 声称"Owner 2026-10-08 批退役"，但 C394 不在#488 正文里）。
   ⇒ 本册已把这些行**退回待裁**，不替你签。
2. **"批文②"（"其他全部按照你的建议批准施工"）没有任何裁定号**，而#431 在册范围只有 final_delivery 的 10 项。
   ⇒ 它被多本册当万能授权用，属在册查无。已按"未授权"处理。

另有 15 条菜单行与 HEAD 相反（例：称"册上查无"实为裁定#417 已登 10 天；称"已脱敏"实为账号 `8886156677` 明文在 `config/qmt_environments.yaml:38`；称"最大号 413"实为 492/309 条）。这些是**账面撒谎级**误差，不是笔误。

## 三、仍需你裁定的 18 项（去重后，按真实紧迫度排；每项=前因/后果/我的裁定建议/理由）

| # | 事项 | 前因（为什么摆到你面前） | 不点头会怎样 | 我的裁定建议 | 为什么这么裁 |
|---|---|---|---|---|---|
| 1 | **密钥轮转窗口（K1）** | 外审列为 P0 逾期，且**从未进过任何 Owner 菜单** | 过期密钥继续可用，SECRETS 三道 gate 的执法前提失效 | **立即批**，给一个 7 天窗口 | 唯一"每晚一天风险单调上升"且不需要新代码的项 |
| 2 | **实盘三兄弟 A1/A2/A3**（装配通道/拒单生效/准入） | 合规门已在 sim 面建成并实测（F62 门已注、ReportGate 实测 PASS）；实盘启用是宪法 §5 门位 | 实盘继续不接单（安全默认已 fail-closed，`env!=sim` 物理拒执） | **维持不接**，先补程序化交易报备回执的**在册登记**（HEAD 全库查无回执号） | 你之前给的"已报送"只覆盖 F62 券商报备六项，不等于批准实盘启用（#338⑤ 仍是门位）；无回执号即接=裸奔 |
| 3 | **后复权血缘列 DDL（hfq 表族）** | 无血缘列 ⇒ 旧口径行在 ReplacingMergeTree FINAL 视图里静默覆盖修正行（本仓 09-24 实证 bdpan 5210 胜/重算 349）；周线↔日线自报矛盾 71.77% | 后复权读数不可信继续污染回测与策略 | **批：加列 + 分表分批改（daily→weekly→monthly）+ 族内对拍后收口** | 这是"production 流转"门位，必须你签；但技术上有唯一正确解，不需要你选方案 |
| 4 | **真删批文（净删族）** | 隔离动作已做完，缺的是删除台账；C267 的七个库**已物理消失且无删除台账**（不可追责） | 隔离区继续占盘（D 盘 96%），且账面与盘面不符 | **批：只允许"已隔离+双镜像+先补台账"的三条件件删除**，顺序＝先立台账再删 | 没台账就批删=放弃追责能力；本仓已有 4 次热册静默蒸发前例 |
| 5 | **盘后退出码拆分 0=真绿/4=不可判定（补-2/C7）** | 现契约只有 0/非0 ⇒ "不可判定"被读成"绿"；外审实测"无 scale 参数 ⇒ 验收门恒过"仍为真 | 假绿继续吞真故障 | **批**，但同批必须附**受影响消费者清单**（至今未产出） | 语义正确、收益直接；唯一风险是消费方未同步（本仓死法=改契约不改消费者） |
| 6 | **价格笼子语义：拒单 vs 放行记红（补-1/C19 相关）** | 两册口径互斥（一册"预登记=拒单"，裁定#488"记红不拒单"），且**两种都没实装** | 边界行为不可预测 | **批：sim 拒单 / real 放行记红**（沿用 qmt_file_bridge 的 sim-only 先例） | 与既有门位裁定#338⑤ 一致；实盘侧行为变更必须等 #2 |
| 7 | **F 盘 1.02TB vhdx 摘除（E2/补-10）** | 原批窗口 10-05 已过；文件仍在盘且 10-08 仍在写；G/F 双等值声称曾被三方 hash 证伪 | F 红线（≥700G 空闲）继续被吃 | **批：先做一次读侧恢复演练，演练通过才摘** | 我记忆里 DR"可恢复性零实证"是本仓最大暗雷；不演练就删=赌 |
| 8 | **usercustomize 运行时网（#22）** | 宪法 §0.1 要求安装，99 册写"永久禁用"，而**机器上实际是装着的** | 文档与现网相反，下一班无法据册判断 | **批：以宪法为准=装**，并同批修正 99 册那一行 | 文档矛盾=事故（宪法自己定的规矩）；现网已在装的状态，改动=零风险对齐 |
| 9 | **PostSettlement 计划任务 State=Ready（B4/#45）** | 宪法 §9.3 要求对账器事件触发；时钟腿仍在，事件腿已落且幂等，零资金暴露 | §9.3 违宪标记长期挂红 | **批：改事件触发（禁用时钟触发），不删任务** | 已有幂等事件腿；改触发方式不减少任何保护 |
| 10 | **状态词表门 warn→block（④.2）** | `STATE_VOCAB_GATE_MODE="warn"` 硬编码无供方；#490 已收回"翻转已批"的说法 | 词表违规只留痕不拦 | **不急着翻：先出 2 周违规/误拦读数再定** | 历史上 VOCAB 门曾连坐死袋；无读数就翻=拿提交链赌博 |
| 11 | **C19 死密钥门 files_trigger** | 声明了但路径子串恒零命中 ⇒ 提交面空转 | 你以为有闸，其实没有 | **批：先修 files_trigger，再谈启用**（修=施工，不属门位，我已能自裁的会自裁） | 空转门是最危险的一类"假防护" |
| 12 | **12 张 shell 空表逐表定策（B15/#2）** | 12/13 已进 `known_data_gaps` ⇒ 不会假绿 | 保持现状无害 | **批：全部维持"登记不删"**，等 #3 血缘列一起处理 | 删除是门位且收益为零 |
| 13 | **F128 数据脱敏（#43/B2）** | 10 文件活、3 个在 `[DEPRECATED]` 下惰性；两册对同一批文读法相反；且**无任何"该脱敏是否真脱敏"的门** | 脱敏面不可证 | **批：接线优先，不净删**（同 #6 的 block 腿先例：只加执法不删资产） | 内收判据"零消费→退役"在这里不成立：消费方本来就该存在 |
| 14 | **四个 disabled 计划任务定性（#17）** | 名册声明但装载面禁用；本仓有过"watchdog 注册即禁用"误判 | 保护面可能形同虚设 | **批：先逐条定性（车道已给方法与判据），再单条启用** | 一次全启=不可归因；历史上批量启/停都出过事 |
| 15 | **D 盘 96%（E3）** | 工作树/镜像待释放，释放前须逐目录核对镜像文件数+字节 | 触发"停一切写批"熔断，落地链变慢 | **批：核对通过即释放；未核对者不动** | 唯一"核对后释放"路径可逆；盲删是本仓最贵教训 |
| 16 | **双真源三处（#3）+ F120/121/122（#28）+ ROOR 8 项（B7）** | 同名/同职责资产两处并存 | 读侧随机命中其一 | **批：按内收判据"同真源可派生→必并"逐对合并**（施工项，不需你选方案） | 我已在车道里验证这类是纯工程，不属门位；只是需要你的批文以免"代裁"嫌疑 |
| 17 | **CN-MACRO 供数（B6）与 indicators（B5）** | 上游断供/口径未定，两册都写了"按建议批" ⇒ 命根子是 C65 | 供数缺口继续 | **不批**（依 §二.1 退回） | 唯一依据是待证授权；且缺供数已登记不假绿 |
| 18 | **开销类 F4/F5/F6（含花钱项）+ F9/F10 + E5 flags 轮转 + E6/E7/E8 + C5 上岗规则 + E11/E13 + B10/B17/B18** | 多为"算力/开关/流程开销"取舍，其中数条的"已批"同样落在 C65 上 | 维持现状=维持安全默认 | **逐条：能自裁的我已在本册给出默认（不动）**；纯花钱与纯开关保留给你 | 花钱与出厂默认翻转是宪法明列门位，不代裁 |

**给你的一句话**：真正需要你现在表态的是 **#1、#3、#4、#7** 四项（安全逾期 + 数据可信 + 盘位）；#2 建议明确维持不接；其余 14 项我已给默认安全解，你不签也不会卡进度。

## 四、遗留施工清单（不是门位，AI 能自己干，但本班没做完）

| 序 | 项 | 现状证据 | 后果 |
|---|---|---|---|
| P0-1 | **红蓝验收尺重建**：`tests/governance/test_redblue_governance.py` 与 `test_redblue_robust.py` 在 tests 大迁移删除波 `7fa19b8249` 中**双双失踪，未在新家重建**（HEAD 内 `TestScenario3aIndexLock`/`global_commit_lock_contention`/`_CrashLedger` 零命中）；governance 版字节在 `wave1b/rescued/versions/test_redblue_governance_py.md` 有逐字副本，**robust 版只剩 blob `7fa19b8249^` + 一份 `.runtime/tmp` 的 883 行 TTL 风险副本** | 两册的登记行还指向已不存在的 `rescued/tests/governance/` | "全流通做过红蓝极限对抗"这句话现在**没有尺支撑**；这是本战役最贵的单点 |
| P0-2 | **35 个"册上有、盘上无"的半落地件**（`src/zephyr/data_security/wiring/*` 7.7 天、`scripts/governance/apply_meta_question_ddl.py` 12.7 天、`mount_obligation.py`+生成器+`tdm_mount_exemption_registry.yaml`、`translated/c4_*`×7）与 **5 个已落地却无 creation_token 的脚本**（`fexam/conditional_exam.py`、`paper_pool_gate.py`、`sector_surface.py`、`t0_material_line_fast/parity.py`） | 键集差实测 | 门禁执法面与真源册长期两面不一致（"配置只被一条路径消费"同族病） |
| P0-3 | **27 个只存在于 index 的字节**（含 `architecture_issue_registry.yaml` 1.67MB、`trading_decision_map.yaml`、`registry_of_registries.yaml`）——既不在 HEAD，也不在盘，也不在队列 blob；且 `worktree_drift_watchdog.py`(#ARCH-308 A1) 的 `_sweep_dead_sessions` 会对 94 个脏路径自动 `git reset HEAD --` | 车道逐路径核对 2249 只袋 | **一次 reset 即永久丢失**；这是当前最大的蒸发窗口 |
| P1-4 | `src/zephyr/governance/map_query.py` 在盘 3.9 天、四通道（HEAD/index/blob/worktree）均无 token | — | 无主孤儿代码 |
| P1-5 | 主区 16 个 `git rm --cached` 形态的暂存删除（HEAD 有文件、盘上字节仍在、无删除提交、注册表行未同批改） | — | 属 Owner 门位（并入 §三 #4），`git add -A` 会静默撤销它们 |
| P1-6 | S4 工厂包三件（F21/F22/F16）**本班未逐判据复验**；间接面证据：`SQL_ALREADY` 1 文件、`llm_error` 3 文件、`intake` 命名 5 文件在 HEAD | — | 需一条车道做"判据级"核销（存在≠内容） |
| P2-7 | 终验口径：本轮**未达成"落地面连续两轮零问题"**；HEAD 现存 77 件红蓝报告 + 93 件验收/回归报告，但都是历史班各报各的 | — | 需要一次冻结车道后的统一终验 |

## 五、复跑配方（证据可再生）

```bash
export PATH="$LOCALAPPDATA/Programs/Python/Python312:$LOCALAPPDATA/Programs/Python/Python312/Scripts:$PATH"; cd /d/ZephyrAlpha
# 1) 三册待裁定条目的逐条核销（HEAD 面）
git show HEAD:docs/_working/fullconnect_campaign/99_skipped_for_owner.md
git show HEAD:docs/_working/total_command_closeout/93_owner_menu.md
git show HEAD:docs/_working/night_sweep/99_owner_gate_menu.md
git grep -n "C65" HEAD -- docs/_working/external_audit_mastertc/lane_g_open53_cards.md
# 2) 红蓝尺失踪史
git log --all --diff-filter=A --name-only -- '*test_redblue_governance.py' '*test_redblue_robust.py'
git grep -c "TestScenario3aIndexLock" HEAD; git show 7fa19b8249^:tests/governance/test_redblue_robust.py | wc -l
# 3) 半落地/无 token 面
```

## 六、本班（st-chief7 系）交付清单（全部经 GitCommitGateway 或后继班落地，逐项对 HEAD 实测）

| 交付 | HEAD 证据（实测方式） |
|---|---|
| T 袋：候选池持久化 + 盘前通电 + 执行反馈环 + 九态桥 | `premarket_workflow.py` 含 tradability_preflight 3 处；`order_enums.py` 九态 15 处；`algo_execution_selector.py` QualityPriorProvider 4 处 |
| K 袋：熔断进料 + 重启重臂 + 生产装配 | `risk_layer_orchestrator.py` order_stats_provider 4 处；`trading_session.py` rebuild_from_disk；`start_paper_session.py` 2 处 |
| Q 袋：入队/重投预检旁路封口（484 行纯新增 0 删） | `commit_preflight.py` run_registration_inline_checks；`commit_queue.py` _run_registration_gate 4 处（落地哈希 `833284fe1e`） |
| E8/E9：再平衡执行器 + 调度槽 + 影子组合 + decision_timestamp | 四件均在 HEAD，`market_execution_report.py` decision_timestamp 5 处 |
| 治理工具：裁定取号器 + 门禁三面对账表 + 表产物 | 三件均在 HEAD（`#414` 已在裁定册，5 处命中） |
| 落地链治本：TEST-SOURCE-CONSISTENCY 源码面与测试面同源 | `test_source_consistency_gate.py` 用 `_repo_state_has_file` 4 处（哈希 `2754cc9e6f`） |
| 1A.5 死指针改活库 | `trae_034_task_card_standard.yaml` 3 处指 `databases/governance.db` |
| 战役案卷树 159 件入 HEAD（含 12 份补挖环节卷） | `git ls-tree HEAD -- docs/_working/fullconnect_campaign` = 159 |
| 孤儿件抢救：chart_condition_package（两血统择一，非缝合） | 在 HEAD |
| F56 桥指令核 | `src/zephyr/ex_core/bridge_instruction_kernel.py` 在 HEAD |
| 假绿三件（CI 入口/SSoT 路径/ConfigCheck 读腿） | 哈希 `5d62909cb6`；governance.yml 中 `run_all.py --ci` 调用点已消 |

