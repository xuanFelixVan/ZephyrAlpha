---
ttl: task_bound
title: S07 入库升格挖矿文档
session: st-fullauto-20260915
date: 2026-09-15
---
# S07 入库升格（策略工厂 E6/C6 intake 段）

## 1 现状盘点（自动化状态+file:line 证据）

**结论先行：C6 自动入库是四段中治理设计最完整的——事件驱动+CAS 只增+FSM 预授权+Owner 门，机制层面已"全自动 only-add"；但一次生产性自动入库都没发生过（断点在上游 OOS 缺口），注册表 157 条里 147 条 candidate 积压待复检。**

### 1.1 编排本体（MOD-BT-189）
- `src/zephyr/strategy_pipeline/intake.py`：`run_intake` L256-357 六步=①bothwin 及格→②BH-FDR（q=0.10，L57，门的是 sim 流转非候选登记）→③ρ>0.6 聚类簇首（L58，`cluster_heads` L84-122 并查集+strength 定簇首）→④注册表追加（deterministic STR-<家族>-<序号> L301-303，三轴差异化论证 `differentiation_ok` L126-151）→⑤auto_mount 挂图→⑥FSM 预授权流转→⑦报告落盘+回执。
- 自动模式 `run_intake_auto` L429-435：及格集/p 值/ρ 矩阵全从台账自取（screen_source）。
- 数据源 `screen_source.py`（MOD-BT-191）：`fetch_bothwin` L118-144 与 strategy_screen_query.cmd_bothwin 口径一字不差（IS 冻结批 translated_c4 ∧ 全部 oos_tested 段>0 ∧ decay<0.5）；**无 OOS 段直接跳过**（L132-134）；p 值=SR·sqrt(年数) 渐近正态双侧 L154-159；ρ 矩阵=及格集两两日净收益 Pearson（重叠<60 日不判 L208-210）。
- 写路径 fail-closed 双钥匙：KillSwitch 探针 L67-74（探针失败也停）+验收⑥证据文件 L328-329（`docs/_working/pipeline-research/acceptance6-replay.md` **实测存在**）；注册表追加经 registry_writer CAS L335；幂等键=code_path（回退 strategy_id）L284-288。
- 挂图 `_auto_mount_sids` L387-426：复用 auto_mount 五步管线（登记→regime 分段 Sharpe 判激活→ops→文本手术→only_add 断言→safe_write_text CAS 写 MAP_YAML→38 规则校验→报告）；**失败不回滚注册表，告警+下批重放自愈** L418-421。

### 1.2 FSM 与 Owner 门（MOD-BT-188）
- `src/zephyr/strategy_pipeline/lifecycle_fsm.py`：五态七转换 L83-106；candidate→sim 机器自动（`SimPromotionGuard` L64-73=双窗∧BH-FDR∧无未决衰减三条件，规则文本即本文件）；**sim→production 强制 owner_token**（`OwnerTokenGuard` L76-81）——机器流程不带 token 天然停门，即 Owner 拍板位的后端本体（S13 前端直接对接）。

### 1.3 事件接线（MOD-BT-190，注意与 hypothesis_translator 撞号）
- `pipeline_events.py`：c4_batch_completed→`run_intake_auto(trigger=batch, dry_run=False)` L140-145；`emit_c4_batch_completed` L303-311（c4_batch_screen 落账钩子，记录+立即轻 drain，失败留 journal）；`wire_data_scheduler` L315-330（调度器唤醒钩子：轻 kind drain+翻译件积压扫描+月度档评估，永不反噬调度器）；DataScheduler `__init__` 自动挂钩（src/zephyr/data/scheduler.py:628-633，懒加载防环）。
- journal 实证：`.runtime/strategy_pipeline/pending_events.jsonl`+`last_receipt.json`（pending_left=1，均为 c4_batch_due 重事件，见 S06 文档）。

### 1.4 注册表与挂图现状（实测）
- `docs/01_policies_and_standards/_registry/catalogs/strategy_registry.yaml`：**157 条 = 147 candidate + 2 sim + 8 backtest**。sim 两条：lane_e_quantile_baseline（L148，MOD-BT-084）与 c4_e3da6fa71af1_panic_rebound（L12216，MOD-BT-068）。
- `auto_mount.py`：MAP_YAML=config/trading_decision_map.yaml（L56，sleeve 区 L1324-1325 已有 daban/multifactor proposed 槽位）；CLASS_NODE_MAP L62-66 仅 7 类；NEW_SLEEVE_WEIGHT=0.05（L60，新 sleeve 等权 5%）；激活判定=IS 窗 regime 分段 Sharpe（`_cached_judge` L91-101，dominant 序列来自 c1_backtest.regime_snapshot_history）。
- 报告：docs/_working/pipeline-research/reports/ 4 批 intake-*.md/json（2026-09-15 验证性回执，trigger=C1 假说件 STR-AUTO-001 **未污染生产注册表**——registry grep 无此 id）。

## 2 六向挖矿日志表

| 轮 | 方向 | 矿脉 | 判定 | 关键产出 |
|----|------|------|------|---------|
| 1 | ①上游 | bothwin 数据源完备性 | signal | screen_source 与 cmd_bothwin 一字不差（台账只读纪律 L9）；前置=oos_tested 行存在——上游 S06 无自动 OOS 批（见 S06 文档断点①），本环节首条自动入库被卡 |
| 2 | ②下游 | sim 之后的流向 | signal | sim 条目→S08 开钱包（账本硬编码单策略=骨架施工 C1）、→S11 TDM sleeve（挂图有、参与整装回测无接线=骨架 C3）；转正建议只 print（S12 断）——本环节下游两头皆断，入库即"入库孤岛" |
| 3 | ②下游 | 注册表现状核对 | signal | 147 candidate 积压：BH 族=当批及格全集（防选择偏差，passing_with_p L163-166），未及格者"留观后续批次重检"（intake.py L196）但**无周期性复检事件**；candidate→shelved 转换（FSM L96）无自动触发方 |
| 4 | ③机制 | FDR 与入库治理（全网） | signal | Harvey-Liu-Zhu t≥3.0（蓝图 E2 已引，SSRN 经典）；BH-FDR 本体在库（zephyr.strategy_pipeline.bh_fdr，tests/strategy_pipeline/test_bh_fdr.py）；业界治理对照：SR 11-7 模型风险管理三件套（独立验证/outcomes analysis/关停权限，ryanoconnellfinance.com/model-risk-management/，美联储框架解读）——Owner 门=sim→production 与 SR 11-7"关停权限归人"同构，治理层位正确；QuantConnect 全自动 pipeline（quantconnect.com）=idea→backtest→paper→live 单链，其 paper→live 即本项目 sim→production |
| 5 | ④后端 | 写路径钥匙与毒丸 | signal | EVIDENCE 存在✅；KillSwitch fail-closed（含探针失败）；事件 3 次失败→毒丸停摆（pipeline_events.py:196-199）——全自动链在 S07 的两个人工介入单点 |
| 6 | ⑤前端 | 注册表 diff/入库播报 | noise | 仅 intake-*.md 报告落盘，无面板无推送（归 S12/S13）；登记不施工 |
| 7 | ⑥数据字段 | 三轴初值与挂图映射 | signal | 三轴=启发式词表初值（screen_source.py:45-53/241-248），条目自认"语义字段待复核"（intake.py:207）=自动入库留下的人工尾巴；derive_class 全未命中→multifactor，而 CLASS_NODE_MAP 无 multifactor 键（auto_mount.py:62-66）→挂图 _plan_inserts 对该类 skipped/error（only-add 自愈兜住但永不挂上） |

**计数：signal 6 / noise 1 / 受阻 0**（全网搜索 1 次命中，无 429）。

## 3 业界与开源对照

- **多重检验治理**：本环节 BH-FDR q=0.10 门 sim 流转、族=当批及格全集（含已入库者防选择偏差）——与 Harvey-Liu-Zhu（t≥3.0）/Bailey-López de Prado（DSR）的多重检验观一致；特色是"族随批动态"而非固定阈值，量越大及格线越紧（蓝图铁律 2）有业界依据。
- **治理层位**：SR 11-7（美联储模型风险框架）要求独立验证+持续监控+**人保留关停权**——本仓 candidate→sim 全自动、sim→production/production→retired 强制 owner_token，正是"自动升格+人守出口"的机构共识形态；对比 QuantConnect（平台级 paper→live 需人工 deploy）层位一致。
- **机器可核验的预授权**：三条件（双窗/FDR/无衰减）全部字段级机器可验（lifecycle_fsm.py:55-73），优于业界常见的"委员会审批"黑箱——Owner 圈定 A 方案规则文本即治理真源，属领先设计。
- A 股适配闸：rho 聚类宁漏勿误（重叠<60 日不判）、家族吸收留痕（family_redundancy），适配日频 A 股多因子同涨同跌特性，成立。

## 4 堵点与欠账清单

| # | 堵点 | 证据 | 断链等级 |
|---|------|------|---------|
| 1 | **上游 OOS 缺口→首条自动入库未发生**（主动断点在 S06） | screen_source.py:132-134；全仓无自动 OOS 批 | 高（结构性，S06-G1 解） |
| 2 | **147 candidate 积压无复检机制**：未过 FDR/未及格者留观但无月度复检事件；FSM shelved 转换无自动触发方 | strategy_registry.yaml 157 条；pipeline_events 月度档仅 mount_audit/sim_memo | 中（注册表只进不出） |
| 3 | **毒丸停摆单点**：intake 失败 3 次=事件毒丸等人（KillSwitch/CH 故障场景） | pipeline_events.py:196-199 | 中（低频高影响） |
| 4 | 三轴启发式初值"语义字段待复核"=每条自动入库埋一个人工复核尾巴 | intake.py:207 | 低（可积累成债） |
| 5 | multifactor 类挂图无节点映射，自动入库条目可能永不挂图（自愈循环空转） | auto_mount.py:62-66 vs screen_source.py:238 | 中（S11 前必须解） |
| 6 | IS 批标签 `C4-translated-20260912` 硬编码两处（screen_source.py:38、c4_batch_screen.py:49）：将来换 IS 窗口需同步改，无单一真源 | 两文件对照 | 低（技术债） |
| 7 | sim→production 的 Owner 证据包（S12 建议书）只有 sim_memo_monthly 生成器，无推送——Owner 拍板位后端好、前端零 | pipeline_events.py:251-256 | 边界登记（S12/S13 施工域） |

## 5 施工项建议（具体到文件/函数/验收标准）

| 项 | 内容 | 验收标准 |
|----|------|---------|
| S07-G1 | 端到端首跑验证（依赖 S06-G1 OOS 自动化）：手动补跑一次 OOS 批后触发 `pipeline_events drain`，观察 intake 全六步 | 新 STR-xxx 条目出现在 strategy_registry.yaml（lifecycle=candidate 或 sim）；MAP_YAML 挂图 ops≥1；intake-*.md 报告落盘且 created_sids 非空 |
| S07-G2 | multifactor 挂图映射补全：CLASS_NODE_MAP 增加 `"multifactor": "TDM-E-<合适节点>"`（或 intake 对无映射类显式拒收/降级 candidate-only） | multifactor 条目要么挂图成功要么 skipped 有明确 reason，不再无限自愈空转 |
| S07-G3 | candidate 积压复检月度档：pipeline_events 增 `candidate_recheck_monthly`（复用 maybe_emit_monthly 模式）——对 candidate 条目重跑 bothwin/FDR 判定，可升 sim 或转 shelved | 月度报告含复检结论数；首次运行给出 147 条的分流建议清单 |
| S07-G4 | IS 批标签单一真源：提常量到共享模块（如 zephyr.strategy_pipeline.constants），screen_source/c4_batch_screen 同源引用 | grep 两文件无重复字面量；38 规则/测试全绿 |
| S07-G5 | 毒丸自愈缓冲：MAX_ATTEMPTS 3 次中，KillSwitch 类失败不计 attempts（状态恢复后自然重放），仅业务失败计数 | 单测：kill_switch 阻塞 5 次后事件 attempts 仍为 0 |
| S07-G6 | （挂起排期）三轴语义复核自动化：等 S12 建议书落地时把"待复核"字段一并呈给 Owner 拍板页 | —— |

## 6 封矿结论

- **矿脉封矿**：7 轮 6 signal 后剩余方向（FSM shelved 自动降档规则、ρ 矩阵分块计算）属 S09-S11 施工域边界，按"越界不挖"登记后封批。
- **方案封矿**：无。C6 自动入库+FSM 预授权+Owner 门正是终局全貌第④类 Owner 事项（转正审批）的机器侧对偶，核心有位。
- **终局视角**：本环节机制层已是"终局形态"（事件驱动/only-add/预授权/人守出口），是全链中离无人值守最近的段；其激活条件完全系于上游 OOS 自动化（S06-G1）。G1-G4 打完+"首条自动入库"实证后，S04→S07 四段可宣告端到端无人值守（至 sim 为止；sim→实盘的 Owner 拍板位由 S12/S13 接管）。
