---
ttl: task_bound
completes_when: F5 收尾报告落 HEAD 且裁定登记（拟裁定#484+，施工时实查最大号）后本件转归档
status: executed
executed_as: 裁定#487（#486 被 fig16 占用顺延）；落地 commit e546b6d7a3（F3 写入+F4 防线+F5 收尾同袋原子，8 文件纯净+capability token 由 gomap 先行袋 9dd96e8920 承载入 HEAD）；F2 终审=03_f2_verdict.md
title: 轴归一手术·作战工单（裁定#483 后置项，Owner 2026-10-05 开工令，已执行完毕）
owner_dispatcher: st-bm-reclass-20261004（GLM-5.3 总筹）
executor: st-axisunify-flash-20261005（Flash 执行）
---

# 轴归一手术工单：BM 格子 ↔ TDM/工厂节点 词汇收敛

> 总筹：GLM-5.3（st-bm-reclass-20261004）。执行：Flash（st-axisunify-flash-20261005）。
> 法源：裁定#483（battle_map=横向·覆盖切片；流程叙事真源=TDM/策略工厂）；裁定#482 先例（图13↔排班=互挂引用不迁移，本手术同款手术形）。
> **本手术是词汇收敛，不是搬家**：锚点不迁、BM 表不退役、运行时字段语义不动。

## 0. 目标一句话

同一生命周期环节只留一个叙事真源：battle_map 格子降为"挂载格子+互挂引用"，
映射关系入住 TDM/工厂 YAML 的既有字段模式（五联锚加一联），配一致性防线防漂。

## 1. 红线（违反=停笔上报，无例外）

1. **零 PG 写入**：battle_map_* 三表冻结（裁定#483 配套条款）。不新增/删除/修改环节，不动 anchors。
2. **不动运行时三消费**：strategy_registry `battle_map_ref`、前端 bt-battle-stage.js、api_server `/battle_map_flow` 字段语义原样。
3. **零新建注册册**：映射不建新 YAML 册，入住 `config/trading_decision_map.yaml` 节点的 `battle_map_refs:` 字段（五联锚模式加一联）+ `config/strategy_production_map.yaml` 同款；validator 复用/扩展 `check_decision_map.py`（先读 `docs/_working/map_build/20_join_checker_design.md` 设计稿定复用形）。
4. **C 级争议不自行并合**：产出 03 呈批件后停笔，等 GLM 裁定门（F2）。
5. 宪法冷启动全序列（RULE-ENV/GUARDIAN/WORKTREE/LOOKUP/DEPGRAPH）+ 提交唯一正门 git_commit.py。

## 2. 分阶段任务

### F0 盘点（只读）
- BM 341 环节：step_id/name_zh/flow_stage/parent（PG battle_map_steps，用既有加载器或 DatabaseService 只读，禁散写 SQL）。
- TDM 184 节点：node_id/name_zh/layer/decision_question（config/trading_decision_map.yaml）。
- 工厂 27 节点：E0-E9（config/strategy_production_map.yaml）。
- **在途冲突盘点**：trading_decision_map.yaml 正被 tdm_mount 车道挂血肉（docs/_working/tdm_mount/ 四件+挂图 SOP 血肉 F 批）——查 .ailocks/session_registry 活跃 claim，同窗错峰或申报合流，禁双写。
- 产出：`01_census.yaml`（三轴清单+计数核对行）。

### F1 映射提案（只读+提案）
逐 BM 环节提案对端（TDM 节点 or 工厂 E 段 or 自有），关系四型+置信三级：
- 段归属预判：研究孵化/模型训练/回测验证/模拟验证→工厂 E0-E9；选股/买入/卖出/仓位/风控/执行/对账→TDM；横切 BM-12/数据质量 BM-RES-01-E 等→自有（不并）。
- **A 级**=命名直配（如风控审批对风控节点）；**B 级**=语义判读（读 module_translation_registry §battle_map_steps 叙事 vs TDM decision_question/judgment_basis）；**C 级**=粒度错位（BM 格子粗聚合 vs TDM 细节点，多对多）或判读存疑。
- 证据留行：双方原文各摘一句。产出：`02_mapping_proposal.yaml`（每条=BM step ↔ 对端列表+关系型+级别+证据）+ B/C 级计数汇总。

### F2 裁定门（GLM，执行方停笔点）
- 03 呈批件：C 级逐条+ B 级全量清单（GLM 全过目，A 级免审）。w5_1 四判据逐条：同真源可派生→必并｜零触发零消费→退役｜同域重复簇→收敛唯一｜跨域不同对象→不并。
- 放行=F2 终审签字（对话或呈批件批复均可）。

### F3 写入批（F2 放行后）
- TDM YAML 逐节点加 `battle_map_refs: [BM-XXX...]`（+工厂侧同款）；字段头/注释标注法源（裁定#483+本裁定）。
- 写入用 CAS（safe_write_text）或既有编辑正门；与 tdm_mount 车道协调后同窗提交。
- **与裁定登记同 commit 原子**（RULE-RULING）。产出：`04_write_batch.md`（diff 摘要+计数）。

### F4 一致性防线
- validator：TDM/工厂侧 battle_map_refs 必须实存于 PG battle_map_steps（死引用=error）；交易段 BM 环节无 TDM 回链=warn（君子协定起步，触发率实证后再议 gate 化，按 perf 方案 own-scope 分级）。
- 复测三件：DECISION-MAP gate、align_all、align_battle_map——全部不得劣化。
- 挂接 alignment_checklist §3 注记。产出：`05_validator_report.md`。

### F5 收尾
- `06_closeout.md`：覆盖报告（A/B/C 分布、C 级裁定结果、缺口清单）+ 净零申报（复用件清单）+ memory 更新。
- 归档本工单，release 全部 claim，git log 归属核验。

## 3. 后勤配方（昨夜学费，直接用）

- 新文件 CREATE-GUARD token：batch_creation_tokens 正门（capability 册拉锯时用真空窗口战术：守望 holder=None 即重插+claim+提交）。
- 队列袋若死于 ghost_session：.runtime/sessions/<sid>/heartbeat.jsonl append `{"status":"alive"}` 行+`--resolve`；死于三向合并"身份判不了"=capability 册类，改直连。
- FOREIGN_CHANGE 处方：release→`--claim-only --adopt-prior-work`→commit 同旗。
- 撞号：裁定号施工时 grep 实查最大号。

## 4. 验收（总筹签字线）

①映射覆盖率报告 C 级清零（裁完）；②validator 死引用=0；③三项复测不劣化；④净零合规（零新册/validator 有复用申报）；⑤裁定登记与写入批同 commit；⑥git log 归属纯净。
