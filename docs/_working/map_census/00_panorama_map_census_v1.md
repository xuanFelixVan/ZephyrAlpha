---
ttl: task_bound
completes_when: 第一波三图立项裁定（或改判）落定后本件使命完成，转归档
title: 全景图流程域普查 Census v1（裁定#409 配套）
owner: ZephyrAlpha-Owner
---

# 全景图流程域普查 Census v1（裁定#409 配套）

> 2026-09-24 / 会话 st-mapcensus-20260924 / 四路只读挖矿（图覆盖面 / 运行时循环 / 数据供给链 / 开发交付与治理流）。
> 裁定依据：裁定#409 一域一图（翻案 final3 W4-5 第1条）；真源框架=alignment_checklist §3 + 宪章 §8。

## 0. 一句话结论

纵轴缺口 = 6 张候选图：**第一波 3 张真源已齐可直接机生建图**（交付流水线 / 数据供给链 / 交易日循环），**第二波 3 张需先立校验器或登记面**（AI 施工流 / 策略卡生命周期 / 治理立法流）；交易执行与基础设施守护**不建新图**（已有归属）。全景图总量收敛预期 ~16 张（现 10 + 第一波 3 + 第二波 3），不设硬上限，收敛靠一域一图+净零。

## 1. 现势：全景图 10 张的纵横分类（挖矿实证）

| 轴 | 图 | 对齐键 | 校验/gate |
|----|----|--------|-----------|
| 结构（横）5 张 | depgraph / dataflowgraph / blueprint / frontend_map / industry_chain_map | module_id / feature_id / chain_id | apply_depgraph / sync_panorama / FRONTEND-MAP gate137 / INDUSTRY-CHAIN-MAP gate141 |
| 流程（纵）5 张 | TDM / strategy_production_map / governance_operations_map / battle_map / decisiongraph（**半下岗**，季度退役观察 2026-Q4） | node_id / FAC-* / module_id / step_id / module_id | DECISION-MAP gate138 / FACTORY-MAP gate142 / align_all 第九节（机生）/ align_battle_map / 三图对齐 |

- GOMAP 机生实证：424 模块 wired 250 + suspect_orphans 92（孤儿判定已机械化的活体样板）。
- **GOMAP out_of_scope_refs（逐字）= 现成的待建纵轴清单**：提交门禁体系（"门禁是每模块配套,非运行时流水线节点"）/ 数据治理 / 代码质量治理 / 交易决策治理（→TDM 已覆盖）。

## 2. Owner 四问定案（2026-09-24 讨论已裁，写入裁定#409）

1. **交易执行流 → 不建新图**：TDM 已有 TDM-E-L4 买卖点与执行（13 子环节：订单九态 D31/执行容灾对账/滑点回写）+ TDM-X-S2 离场执行 6 子环节；缺的只是盘后结算段 → 归交易日循环图（图13）。
2. **提交门禁 → 不并 GOMAP，独立建图**：GOMAP 边界声明明确排除且域不同（开发时 vs 运行时，无连接点）→ 建"交付流水线图"，**并把会话生命周期+死信复活并图**（同域三车道，一域一图收敛示范）。
3. **数据管线 → 不进 TDM 也不进工厂**：数据链同时供给两端，放进任一张都成假父子 → 独立"数据供给链图"；与横向 dataflowgraph 同资产不同轴，不违一域一图。
4. **总数 → 不设上限**：需要多少建多少，每域收敛一张；域间无连接点才分图。

## 3. 第一波（真源已齐，按九图挂轴四件套直接施工）

### 图11 交付流水线图 dev_delivery_map
- 域：代码从会话诞生到落地主区的**开发时**全流程，三车道：①会话生命周期（startup→worktree 分配→claim→施工→merge→shutdown→handoff）②提交流（edit→claim 快照→enqueue 入袋→serializer 租约 FIFO→landing 工作树全门禁→post-commit 30+ reconciler→release→done）③死信复活（dead→classify[env/item]→分诊→requeue/--from-bag→再落地）。
- 触发/终点：commit 事件+会话启停 → HEAD 落地+claim 释放+handoff 交接包。
- 机生真源：`scripts/git_commit.py` / `scripts/commit_queue.py` / `git_commit_gateway.py`（ALGO_FLOW I1-O1）/ `.runtime` 队列 JSON 台账（pending/processing/done/dead）/ session_registry + handoffs。**全部机生可产，生成器零手画**。
- 吸收对象：GOMAP out_of_scope「提交门禁体系」+ parallel_session_coordination_policy（真源路径挂载，不复制内容）。

### 图12 数据供给链图 data_supply_chain_map
- 域：外部源→采集（tasks.yaml **272 任务/23 源**）→入库（ch_writer/WAL/DatabaseService 单通道）→衍生加工（consensus/financial/resample）→冷库备份（archiver 三段 export→verify→drop 至 F:/zephyr_cold + G: 双链 backup.ps1）→对账修复（integrity_check 23:00/daily_backfill 17:00/catchup_guard 05:30/eod 三方对账 15:40/OPTIMIZE FINAL）。
- 触发/终点：schedule.yaml **27 cron 槽**+4 执行器池+事件 → 对账 PASS+archive_manifest。
- 机生真源：schedule.yaml / tasks.yaml / data_asset_registry（REG-DATAFLOW-001，15 源 76 集 75 作业）/ `generate_data_acquisition_flow.py`（采集段已机生，**扩为全链即可**）。
- 吸收对象：GOMAP out_of_scope「数据治理」；data_acquisition_flow.md 并入为采集段。

### 图13 交易日循环图 trading_day_cycle_map
- 域：一个交易日的时间轴：盘前（L0.5 元数据 08:34→QMT 看门狗 08:45→paper session 09:25→竞价 9:15-9:25）→盘中（realtime 5 分钟/SimBridge 09:35/资金流 4 槽 10:05-15:05）→盘后（PostSettlement 15:30/eod 对账 15:40/daily_kline 16:30/**dloop 十环节 16:45**）→夜窗（L7-L11 财务/研报/完整性 23:00/周批）。
- 触发/终点：交易日历+槽位 → 日度拍板+结算对账 PASS。
- 机生真源：schedule.yaml 27 槽 / dloop master switch（MOD-PLAN-033 十环节链）/ post_settlement_pipeline / recon_runner。
- 注：与 TDM 分工=TDM 管"决策逻辑"（盘中判断），本图管"运营时序"（什么时点跑什么）；执行域已在 TDM L4，不重复。

## 4. 第二波（真源部分在位，先立校验器/登记面再建图）

| 候选 | 域/形态 | 缺口（四道门之④） |
|------|---------|-------------------|
| 图14 AI 施工升级流图 | construction_workflow 15 步闭环（Step0 冷启动→…→Step12 worktree 合并） | SOP verifiability: manual；每步 gate 命令已是脚本 → 先立"步骤锚校验器"再机生成图 |
| 图15 策略卡生命周期图 | **状态机形态**：预注册→开测→考卷 RED/GREEN→重判一次(#363)→封卡 SEALED→复活唯一口=预注册新卡(#399/#304) | 卡=md status 头+experiment_registry+N 台账三处分裂 → 先立卡状态登记面（或挂 experiment_registry 扩枚举）再建图 |
| 图16 治理立法流图 | 呈报→取号→登记（同 commit 原子，RULING-REFERENCE gate74）→执行→取代链 | 真源=ruling_registry+gate 已齐，但流程仅 7 步、建图收益中等 → 与 GOMAP 扩"治理排程层"合并评估，防碎图 |

## 5. 不建图清单（已有归属，防膨胀）

- 基础设施守护循环（belt daemon/reaper/watchdog/telemetry/MAPE-K guardian 等 10+ 常驻）→ GOMAP L0-L6 已覆盖，扩 mounts。
- 治理周/日批处理（C4Exam/ModelExam/GateFullTreeAudit 等 ~28 个 schtasks）→ GOMAP 扩"排程层"评估。
- 交易执行/结算 → TDM L4/X-S2 + 图13 盘后段。
- 图书馆业务流（登记→索书号→借阅→注销→盘点七流程）→ docs/library 机生视图+`zephyr.library.lookup` 即导航入口，暂不建图。
- 代码质量治理（GOMAP out_of_scope 第3项）→ 门禁链已由图11 承载，独立流程线暂不存在，观察。

## 6. 后续批次

1. alignment_checklist §11 补注记行"第1条流程类禁令被裁定#409 一域一图取代"（该节只增不改）。
2. 第一波三图逐图施工：结构校验器+对抗测试+gate+挂轴同批（FACTORY-MAP 图9 配方），每图一个生成器；建图批次走 token 先行+挂总线（module_id）+§3 登记。
3. alignment_checklist §3 图行加"纵/横"轴标注（随对齐批），完成宪章 §8.3 导航闭环。

## 附：真源路径速查

- 图面目录：`docs/01_policies_and_standards/sop/governance_sop/alignment_checklist.md` §3/§11
- 图11：scripts/git_commit.py · scripts/commit_queue.py · src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py · src/zephyr/security/access_control/session_concurrency.py · docs/01_policies_and_standards/policies/parallel_session_coordination_policy.md
- 图12：src/zephyr/data/config/schedule.yaml · src/zephyr/data/config/tasks.yaml · docs/01_policies_and_standards/_registry/catalogs/data_asset_registry.yaml · scripts/ch/archiver.py · scripts/backup/backup.ps1 · docs/01_policies_and_standards/sop/data_ops_sop/data_ops_policy.md
- 图13：src/zephyr/data/config/schedule.yaml · src/zephyr/plan_engine（dloop MOD-PLAN-033）· src/zephyr/trading/post_settlement_pipeline · src/zephyr/trading/recon_runner.py
- 宪章导航：docs/02_enterprise_architecture/04_architecture_principles_decisions/system_charter.md §8
