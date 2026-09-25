---
ttl: task_bound
completes_when: 2026-10-08 GLM 免费期收官总报落账后归档
title: 双编译器自动化总计划（Qoder 千问白班 × ZCode GLM 夜班 × GPU 专道）
owner: Owner
session: st-autoplan-20260924
date: 2026-09-24
---

# 双引擎自动化总计划（文件桥 · 调度唯一真源）

> 本册是 Qoder（千问 3.8 Flash）与 ZCode（GLM-5.3 Flash）全部自动化班底的调度真源。
> 任何 lane 开工前必读本册+宪法 AGENTS.md；**只做本册登记的活，禁无事生非**；发现新活先登记本册再排班。
> 追加记录必用 safe_write_text CAS（src/zephyr/shared/io/file_utils.py）+ 先 `lock_files.py acquire`；提交唯一正门 `scripts/git_commit.py --enqueue`。
> 提交死因处方真源=commit_navigation_playbook.md（机生 102/102，禁手改，源册在 commit_guide_sources/）。

## 0. 引擎与时间窗（硬边界）

| 引擎 | 模型/定位 | 免费窗 | 截止 | 并发 |
|---|---|---|---|---|
| Qoder | 千问 3.8 Flash，弱→纯执行 | 24h 全天 | 2026-09-30 | 15-20 子代理 |
| ZCode 夜班 | GLM-5.3 Flash，较聪明→方案/仲裁/落地 | 每晚 23:00-09:00 | 2026-10-08 | ~10 异步对话 |
| 本机 GPU 3090 | L3 专道唯一持有 | 09-25 12:00 点火，59h → 09-27 23:00 | — | 1 对话 |
| 总指挥付费窗 | ZCode 白天轻巡检 | 全天，**避开 14:00-18:00**（不打折） | — | 1-2 |

里程碑：09-25 12:00 GPU 点火｜09-27 23:00 GPU 收窗 + W-M1 72h 对账｜09-30 Qoder 免费收官报告｜10-07 夜=GLM 最后免费夜｜10-08 晨收官总报+全部自动化自删。

在册既有自动化（勿重复建设）：第二链每日核验 07:15｜battle_map 周一 09:00｜模拟盘钱包交易日 19:30｜candle_pattern DROP 评估 12-15 一次性。

## 1. 分工与写域互斥

| Lane | 引擎 | 职责 | 写域（禁跨写） |
|---|---|---|---|
| L0 总指挥 | ZCode | 本册维护/队列健康/死信分诊仲裁/跨 lane 冲突/晨报夜审 | docs/_working/cmd_ledger/ |
| L1 提交优化 | 白 Qoder 执行+夜 GLM 设计 | 提交系统提速/README/堵点销号/心跳线程化 | 提交系统面+指南源册 |
| L2 审计对齐（边审边修） | 同上 | 假绿核销/dedupe/fail_open_register/audit_all 缺口 | cleanup_final+audit_all 面 |
| L3 GPU 专道 | ZCode 单对话 | GPU 排查/运行/记账；窗内他 lane 禁重算力 | e2e_integration LEDGER+GPU 输出 |
| L4 原问题 283 消费 | 白采集+夜裁 | 工单 11 张/insuff 96/fail 45 | meta_question_answers/ |
| L5 数据源/因子/策略挖矿 | 夜 GLM 设计 | SL-B 10 线 mining memo/E1C 批次设计 | chain_piling 面（prereg 册只读！） |
| L6 AI层/模拟盘/压测收尾 | 白 Qoder | cleanup-final ⑦⑧⑨ 路由件 | pipeline_final 面 |

sid 规范：Qoder=`st-qoder-<lane>-<MMDD>-<NN>`；ZCode 夜班=`st-night-<MMDD>-<NN>`。便于 claim 释放与死信归主。

## 2. 今晚关键路径（09-24 夜 → 09-25 12:00 点火前，倒计时活）

1. **GPU 三案裁定备忘**（L3 出稿、L0 复核、明晨呈 Owner，12:00 前必须裁）：实测 35.33s/格=预算 5.2 倍→59h×0.8≈4640 格。三案：①两档粗筛（T1 0/40bp，容量~9600，需 Owner 修冻结）②朴素重排 4640（T0 已完 200+T1≈2900+T2≈1500）③压 T1 面板至流动性 top-3000。出处=docs/_working/e2e_integration/LEDGER.md L126-151。
2. **prereg v2 冻结催办**：config/search_space_prereg.yaml `frozen_at: null`+`owner_signoff: pending`→fail-closed 不放行。与 config/factor_mining_whitelist.yaml（FAC-E1C 算子白名单 v1 草稿）同批呈 Owner 签字。
3. **W-M1 Phase1 双轨观测**（当前=双轨第 1 天，七册 22495 条已导入，批 1-7 在队）：对账门判据脚本化（.runtime/registry_ledger/reconcile 快照比对）+09-27 72h 对账预案+Phase2 切主扳机建议（真源=docs/_working/registry_migration/09_wm1_master_plan.md）。
4. **队列积压分诊**：pending=56/dead=317/processing=1。L0 先分诊 09-22 后新死信（dead_reason 字段对照 playbook 处方，能机械修正的修正后 requeue）；cleanup_final 任务①翻译册 6 组 dedupe（7712→7706）死信 requeue、任务③ fail_open_register 14 悬空清零直连。
5. **AI 层"队列畅通"广播判定**：待 E2E 主体完成+队列 drain 后，向 docs/_working/ai_layer_vision/LEDGER_final.md 追加广播行解锁触发件（245 件数先与 Owner 原令核对）。

## 3. 真活清单（全部带锚点；本册未登记的活不开工）

### 3.1 夜班 GLM 桶（聪明活）
- L4：WO-001~011 逐张出施工方案（docs/_working/meta_question_answers/gaps/WORKORDER_MASTER.md，覆盖 15 份 PQ workbook）；insuff 96 三分诊（A28/B37/C31，01_phase2_plan.md）逐条裁定建议（B 类转 L5 供数设计）；fail 45 分型（gaps/FAIL_REGISTER.md：15 infra+30 no_alpha）infra 15 件修复方案。
- L2：六处审查器假绿 a-f 逐项核销推进（④ab/④c 两批已落 af88a8e416/95c8e062e0，余项对 docs/_working/cleanup_final/ledger.md ④ 清单销号）；audit_all 缺口总账（docs/_working/audit_all/）消化。
- L1：提交提速六台包+落地三发现+D27 归包重审落地；belt daemon 心跳线程化设计（长 drain 心跳分支不可达病根）。
- L5：SL-B01~B10 逐线 mining memo（获取方式/成本/PIT 对冲/退役判据；真源=docs/_working/chain_piling_campaign/02_source_line_registry.md，29 线 A16/B10/C3）——直接消化对应 insuff 问。
- L0：每日夜审白班 Qoder 产出（抽验+红蓝）。

### 3.2 白班 Qoder 桶（执行活，按 §5 卡片派）
- L2 机械修复执行（卡A）；L4 证据采集 sweep（卡B）；L1 README+堵点销号（卡C）；L5/GPU 静态排查只读（卡D）。
- L6：模拟盘 17 件终批跟投（5 件复活件在队 q-20260924-st-sim-launch-20260923-0003，登记=docs/_working/pipeline_final/final_report.md）；压测 PhaseB 30 件在 .runtime/commit_queue/hold_stress_phaseB_20260923/——**禁擅自 requeue**（判明全空转死信，归 st-stress 车道决策）。
- 机械再生成：generate_commit_guide.py、generate_project_depgraph.py --force、翻译 loader 等生成器件重跑对账。

### 3.3 GPU 专道（L3 唯一）
今晚三案备忘→明日 12:00 Owner 人工点火→59h 每 4h 心跳记账→09-27 收窗初报。窗内其他 lane 禁重算力（大 pytest/回放/回补错峰让路）。

### 3.4 Owner-only（自动化禁入，只备料呈批）
凭据外泄 R4 轮换裁决｜GPU 三案终裁｜prereg v2 签字+算子白名单审定｜生产流转/注册表净删/flag 出厂翻转｜AI 层广播放行确认。

## 4. 日历（逐日分派）

| 日期 | 白天（Qoder） | 夜里（GLM 23:00-09:00） | 硬点 |
|---|---|---|---|
| 09-24 四 | 本册落地+自动化排班（本会话） | 夜班#1=§2 五件倒计时活 | — |
| 09-25 五 | 卡A/B/C/D 首轮 | GPU 记账+L4 工单方案 | 12:00 GPU 点火 |
| 09-26 六 | 轻活（让路 GPU） | GPU 记账+L5 SL-B memo 开工 | — |
| 09-27 日 | 轻活 | GPU 收窗初报+W-M1 72h 对账+Phase2 建议 | 23:00 GPU 收窗 |
| 09-28 一~09-30 三 | 免费尾窗冲刺：白班桶大头清库 | L4/L2/L1 深水区 | 09-30 Qoder 收官报告 |
| 10-01 四~10-07 三 | 按需付费轻跑或停 | 夜班持续 | 10-07 夜=最后免费夜 |
| 10-08 四 | — | 收官总报→本册归档→自动化自删提醒 | GLM 免费期止 |

## 5. Qoder 白班任务卡（可直接粘进 Qoder）

**通用头（每卡都带）**：开工先读 D:\ZephyrAlpha\AGENTS.md 冷启动三步（PATH 修 Python312→lock_files cleanup→process_reaper --status，reaper 不在=禁写）。sid=st-qoder-<lane>-<MMDD>-<NN>。改前 claim、毕后 release；提交唯一正门 `python scripts/git_commit.py --session <sid> --files <清单> --enqueue`（失败带 --adopt-prior-work 重试；禁裸 git commit）。禁碰他 lane 写域与暂存区外来内容。每卡每批 ≤10 文件，批批提交。

**卡A · L2 审计对齐机械修复**
- 目标：docs/_working/cleanup_final/ledger.md 任务①③收口——翻译册 6 组 dedupe 死信按册修正后 requeue；fail_open_register 14 处悬空按对齐清单补真源后清零。
- 允许：上述两册对应 yaml/脚本修复+配套测试。禁令：不动 ④ 已核销项、不新建规则/gate、不动 audit_all 之外的他册。
- 判据：dedupe 后计数 7706 且零死信复发；fail_open_register 悬空探针=0。ledger.md 状态翻转用 safe_write CAS。
- 参考：假绿根因（probe_dangling_refs 正则缺陷）见 docs/_working/align_dirty/align_dirty_ledger.md L421。

**卡B · L4 PQ 证据采集 sweep**
- 目标：insuff 96 三分诊 B 类 37 条（docs/_working/meta_question_answers/01_phase2_plan.md）逐条跑证据采集，填对应 gaps/PQ-XXXX_workbook.md「证据」栏（数据有无/覆盖窗/缺口行数/来源 SQL）。
- 禁令：只读 DB+只填证据栏；不改 criterion/threshold/结论（结论归夜班 GLM 裁）；不接新数据源（归 L5）。
- 判据：37 条 workbook 证据栏 100% 非空且 SQL 留痕。每批 ≤10 条，批批提交。

**卡C · L1 README+堵点销号**
- 目标：①README.md（根，115 行）全量校点——失效路径/过时计数/过时入口清单化修复（计数必须改用字段不写死）；②堵点本 .runtime/audit/bottleneck_ledger.jsonl 高频死因 top10 逐条对照 commit_navigation_playbook.md 死因处方，能机械修的修，不能修的登记桥册转夜班。
- 允许：README.md、纯文档/文案修复、指南源册 commit_guide_sources/*.yaml 数据条目（改后必重跑 scripts/governance/generators/generate_commit_guide.py——机生件本体禁手改）。
- 禁令：禁改门禁/gate 行为逻辑。判据：README 零失效引用；堵点 top10 每条有处置记录。

**卡D · GPU-viability 静态排查（只读）**
- 目标：扫描 config/strategy_production_map.yaml 等策略/组合注册表，逐策略标注「可否 GPU 化/数据量级/预估加速比」，产出候选清单交 L3 复核。
- 禁令：全程只读！GPU 窗内（09-25 12:00 起）禁跑任何重计算；不写 e2e_integration/ 以外新文件（产出=docs/_working/e2e_integration/gpu_viability_candidates.md，新建须随批登记 creation_token）。
- 判据：注册表全量策略覆盖无遗漏。

## 6. 铁律（并发战争教训浓缩，违者夜班仲裁回滚）

1. 冷启动三步缺一不可；reaper 计划任务不存在=禁任何写操作。
2. 改前 claim、毕后 release；提交唯一正门 git_commit.py --enqueue；禁裸 git commit、禁 plumbing 绕门；commit 后必 `git log -1 --name-only` 核实归属。
3. 新建 .py/.yaml/.md 必登记 creation_token（scripts/governance/d3_metadata/batch_creation_tokens.py，token 登记册与新文件同袋提交——gate 读暂存态）；热文件必 safe_write_text；.ps1 纯 ASCII。
4. 写域互斥按 §1 表；跨界先在本册登记改派；外来 staged 违规 warn+记册不代修。
5. 长批先登记 data/runtime/process_reaper_keep.txt；.runtime 根禁直写（暂存走 .runtime/sessions/<sid>/staging/，tmp 走 .runtime/tmp/）；测试禁写生产路径。
6. 净零铁律：新册/新规则必须声明替代合并项；静态清单禁手工维护，一律生成器产出。
7. 实盘四禁常效：开实盘终端≠授权，只 env=sim 8886156677。
8. 桥册追加格式：`## <Lane> · <MM-DD HH:MM> · <主题>`+要点若干；禁止删改他人轮次记录。

## 7. 呈 Owner 裁定项（随夜班备料滚动更新）

| # | 事项 | 截止 | 出处 |
|---|---|---|---|
| 1 | GPU 三案终裁（推荐②朴素重排 4640 保底，①需修冻结收益最大） | 09-25 12:00 前 | e2e_integration/LEDGER.md L126-151 |
| 2 | prereg v2 签字（frozen_at=null）+FAC-E1C 算子白名单审定 | GPU 窗内挖矿前 | config/search_space_prereg.yaml |
| 3 | 凭据外泄 R4：五家 API key 轮换与否 | 本周 | 呈报在案 |
| 4 | 压测 PhaseB 30 件 hold 区处置权（归 st-stress 车道） | 09-30 前 | hold_stress_phaseB_20260923/ |
| 5 | AI 层"队列畅通"广播放行 + 245 件数确认 | E2E 主体后 | ai_layer_vision/LEDGER_final.md |

---

## 轮次记录

（以下由各 lane 按格式追加，禁删改他人记录）
