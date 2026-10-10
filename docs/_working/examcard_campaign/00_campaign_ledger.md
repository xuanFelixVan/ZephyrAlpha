---
ttl: task_bound
title: 考试卡+断言治本双战役作战台账（st-examchief-20261009）
created: "2026-10-09"
sid: st-examchief-20261009
family_id: EXAMCARD-CAMPAIGN
---

# 作战台账（随进展追加）

## 车道状态板（2026-10-09 21:00 快照）

| 车道 | 状态 | 凭据锚点 |
|---|---|---|
| W1 F06 治本 | ✅根因钉死+修复+蓝探针绿；彩排批A 计算中（py-spy 实证 active，非挂起）；正式验收=10-11 周六窗 | 01_w1_f06_root_cause.md + w1_evidence/ |
| W3 骨架生成器 | ✅核心闭环：186/186 覆盖、重跑零 diff、only-add+手工卡保护（10/10 测试）；户口五合一已办 | MOD-BT-241；tests/backtest/test_generate_exam_card_skeleton.py |
| W4 20 卡预注册 | ✅20 张预注册卡落盘（看数前冻结，零数据窥视）；**分数面阻塞**：前置② dexp TI 读侧确定性修复未落 HEAD（argMax 第三路 git log 零命中）——如实登记阻塞非跳过 | exam_cards/entry_flow/L1/*__calibration__0[2-8]*.yaml |
| W5 confidence 闭环 | ✅裁定#501 冻结 v1 判据+回写器落地（13/13 测试）；实弹演示随 W4 首分 | MOD-BT-242；裁定#501 |
| W6 Qoder 云模型 | ✅实弹达成：LLMGateway 增 qwen provider（G1-1 内收零新模块），经 LSG 全链真云调用一次（qwen-flash 1250ms"链路正常"） | src/zephyr/infrastructure/pipeline/llm_gateway.py |
| W7-① fexam 搬家 | ⏸避让延迟：横跨 4 本热册（3 本可能总队在持）——总队队列落地后执行 | 本表 |
| W7-②③ | 候补（dataset_registry 立项/lockfile 钉扎） | 方案 §7.5 净零候补位 |
| F1 lookup state | 🔨子代理施工中 | agent 报告待回 |
| F2 边界登记 | ✅offzone_retrieval_boundary_sop.md 落盘（裁决 b 案） | library_sop/ |
| F3 触发面 | ✅trae_065 v1.1.0+裁定#499 | rules/trae_065 |
| F4 挖矿 SOP | ✅mining_sop_policy v1.7.0 §7.5 | mining_sop/ |
| F5 复盘入册 | ✅CASEBOOK-010 开册+case 0 首录（裁定#500）+prereg 三元组结构落地 | casebook_registry+asset_assertion_cases.yaml |
| W2 GPU 摊销 | ⏳等批A 完成取真全引擎 s/格（热点复测①）；L1 实测已大幅跑赢 L2 设计预期（0.061-0.606s/格纯 pass vs 推演 11.7s），若全引擎 ≤3.5 则按架构册 §六停手条款登记判定，不为饱和而饱和 | p1_wiring_benchmark.md |

## 排队与提交账

- q-20261009-st-examchief-20261009-0001（W1 件 7 文件，含 token 册补 3 条 quant_methodology 修复）已入袋，传送带消化中。
- 待投批次：W3 生成器+186 卡册+2 测试件；W4 20 卡；W5 回写器+裁定#501；W6 llm_gateway；F 文档批（F2/F3/F4/F5+裁定#499/#500）。
- token 工具 HEAD 基底自检在 W1 件落地前会拦（补回 3 条在 W1 批里）——投递序=先等 W1 落地。

## 阻塞与升旗

1. W4 分数面/前置②：dexp argMax(ingest_ts) 第三路未落 HEAD——20 卡分数建立在任意版本指标上的风险未排除，禁开考分数面。
2. W7-① 热册避让：等总队（st-chiefc）队列消化。
3. 批A 时长：全引擎旧路径 ~35s/格推算，census-extend 剩余格数决定收窗时点；不干预（他会在途 CH 负载为 main 因素，reaper keep 在册）。

## 追记（2026-10-10 早）：主袋清障动作账

- st-fig16-20261005（10-05 老会话，零活进程实证）的暂存件 panorama_alignment_gate.py（+25/-13，63 行 `__all__` 缺 Final 触发 MUTABLE-CONST-WITHOUT-FINAL 全局门）封死全仓直落通道。
- 处置=git restore --staged 单文件退栈（**三态验证零丢失**：worktree==index，内容全留工作树，其回来 re-add 即可恢复）；未代改其代码（§3.4）；本条即登记。


## 追记（2026-10-10）：W4 首分开考+W5 判据实弹

- **前置②解除**：dexp 0060 落 HEAD（indicator_reader argMax ×4，总统筹验真同数）。
- **首卡开考**：TDM-E-L1-S1/02_指数趋势位置（kline_index 000300 全窗 1880 行，与冻结窗 2019-2023 IS+2024-2025.09 OOS 完全匹配；信号=MA20/MA60 复合三态档位，序数桶型 runner 回退已补）。**verdict=fail**（ic_mean=-0.0013<0.02、OOS 反号 IS-0.0013/OOS+0.0445；桶序单调 1.0=三态平凡序）。**负结果如实入 exam_scores_v1.yaml**（预注册纪律：门柱冻在先跑分在后，fail 行不迁移 confidence=W5 判据机判实弹正确拒绝）。
- **数据面断供新发现**：c1_market.limit_up_down 仅覆盖 2026-07-20 起（5397 行）——广度面 6+1 卡冻结窗（2019-2025）无数据，需源回补（接 HANDOVER 断供修复工单族）；波动面 IV/宏观事件表待接。20 卡可立即开考面=指数族；广度面候源回补后按各自冻结窗开考。
- **N 账本 CAS 告警**：TrialLedger 记账撞注册表族保护 ×10（热册竞态），ledger_warning 已如实入分数行（不吞考试结果）——转维护班面。
- **runner 顺手修**：序数分桶回退/窗口边界 Timestamp 化/行情段日期正则解析（含中文段注容许），测试 7 passed。

## 追记（2026-10-10 晨）：追加令执行账

- **R3-B5 停呈**：X-R1-03 查证命中保留面①（护盘资产定向加仓白名单：熔断期窄门+总资金 5-10% 预算+position/core 实盘面）→立即停，呈 Owner。
- **R3-B2 口径查证收口**：E 道（2025-10..2026-09 深回撤年/无止损 MaxDD -57.56%/止损必触发）vs T3b（2020-02/03 CRISIS/覆盖 0.35%/27 对）=情景区+覆盖率混杂，双测量各自内部有效；三坑过检。裁定#505 入 PG 账本（#503 撞号让位、#504 他班占用、#505 取号登记 v16）。
- **R3-B1 冻卡**：双窗锚定卡两张（X-S1-03 止盈族/X_tp 维、X-S1-02 止损重考/X_stop 维新考卷——旧 T3b FAIL 存续 G4-5）门柱看数前冻结；X_sector 命名缺口（草案无此维疑 X_ladder）挂 Owner 确认；B3/B4 跑数三件套齐才动（fire_grid fail-closed 在守）。
- **R8**：famex v2 维持暂缓；标定判据预注册=下一步（3 条非 state 先例派生，判据立不起=停呈）。
- **T5 三态现测**：见下。
- **T5 判定=继续避让并登记**：活进程零占用+fs 目标位空闲，但四本引用目录（trial_ledger/factor/technical_indicator/capability）现归 regsolo 单口写面活跃管理（capability/ruling/translation 三册本会话全程目击其单口写）——引用改写应提交该通道而非直改；搬家本体（git mv 31 件）候通道窗口。

## 追记（2026-10-10 晨二）：X_sector 命名取证定谳+R10 治本+门柱三件

- **X_sector 定谳（批复退回件，证据定谳非上报）**：index.md:85 原文"schema 增维（X_stop/X_tp/X_sector 等）须裁定"=三维并列各有实义；X_sector=**板块传导维**（sector_propagation_wiring_v1.md:40,67：sector_surface.py 新件+`X_sector=['off','strength_top15','conduction']`，沿 X_stop/X_breaker T3b 先例），与 X_ladder（X-S2-05 分批止盈 Exit Ladder）**异物非同名**。追加令三维授权指向成立；X_sector 开维施工（新件+schema 增维）=独立批次，不在本次两张冻卡范围（已冻 X_tp/X_stop 正确）。
- **R10 治本+补记**：根因=TrialLedger CAS 的 yaml.safe_dump 往返丢他会话新增注释块（13 行非条目）触发注册表族 mass-edit 保护误拒。治本=条目级无损断言（_entry_fingerprints：旧 batch_records/screen_runs 键集 ⊆ 新集）+断言过则 allow_mass_edit 放行（保护意图=防条目蒸发，注释损失由断言兜底）。补记入账 ✓（examcard:TDM-E-L1-S1/02_指数趋势位置:2026-10-10），测试 15 passed。
- **G1/G2 实施**：净费参数入 exam_scale_cost_gate.yaml 唯一参数面（net_fee 节，禁硬编码）；校准器出分附净费桶读数（net_bucket_medians）+换手计量（signal_turnover_daily，只计量不判罚）。
- **G3**：缓行登记（触发器=总资金≥300 万或外部资金接入；缓行期禁预立阶梯门柱）。

## 追记（2026-10-10 午）：二号收口令执行账（st-examclose-20261010）

- **归属协调+W1 claim（先到登记）**：原二号 st-examchief-20260909 无会话目录=不在岗；备袋会话 st-examchief-20261009 心跳末条 2026-10-10T02:31:35Z exited（idle 超时）。无活口，本会话接手二号余件并 claim 今晚 23:00 W1 F06 窗验收。
- **T1 清窗实测=翻动未止（停投分支）**：观测窗 11:16:05→11:33:28；capability 册 worktree 11:32:21 被旧形态渲染覆写（无 GENERATED 头/键序旧形，对 HEAD +832/-790 reflow 残留），11:32:52 index 被写回 HEAD 正典态（index mtime 08:46→11:32:52）；gate_audit（allow_overlap_usage/obj_s_env_denial/registry_mass_deletion_foreign_staged 35MB）11:25 仍在写。与 11:26:18 队列落地（q-20261010-st-fwin-exec-20261009-0004，GW overlap+multi-domain+tracked-drift 留痕）同窗同现；stash_notice 所记 09-30 侧 stash 含 capability/translation/architecture 三册旧形（本仓无 stash reflog，该通知=陈旧文档）；与 disk_reorg 台账「蒸发战争：stale-index 并发提交回退他人内容今晨三起」同源。写入 PID 未能逐个钉死（无 stash reflog、无 hook 写审计命中）——系统级根因=共享暂存区落地周期复活 stale 形，归维护班根治面。按令登记上报，不硬投。
- **R3 袋实况=半数载荷已过时（第二停投理由）**：袋 231 件仅 11 件对 HEAD 有差，其中——①双窗卡 token 两条已在 HEAD 正典投影在册（merge_evaluation=「R3 离场族双窗冻卡（裁定#505）归 exam_card 族」×2），capability 册携带=纯渲染 reflow 零内容增量；②7 张 L1 卡 staged 形=examined→preregistered 回退+run_id/score_row 置 null，与 exam_scores_v1（17 行 fail 实录，nightmine 05:07-08:56 实跑在案）相抵，落地=数据倒退；③真剩余增量=calibration_exam.py（+30 未暂存，chief 末笔）+本台账段+2 件 ruff 修复（writeback SIM300/skeleton I001，修后 46 测试全绿）。建议：袋作废重 derive（剔三册与 7 卡，仅余真增量件），候翻动根治后走正门。
- **T4 巡检收账**：W4 分数册 17 行全 fail（如实入册，预注册纪律）；W5 零 PASS（回写器候面不动）；W2 批A 16h+ 仍在算（19:17 到限先杀，全引擎 s/格 标定取数大概率落空=如实不动）。
- **W1 验收安排**：19:17 彩排批（PID 32284 wrapper+50252 python，10-09 19:16:58 起）到限先杀不占窗位（F06Grid state=Running 在位会顶掉 23:00 自然触发）；23:00 自然窗按冻结门柱（manifest.csv 有产出且 rc=0）验收；红=五层证伪链取证上报，禁现场改判据。
