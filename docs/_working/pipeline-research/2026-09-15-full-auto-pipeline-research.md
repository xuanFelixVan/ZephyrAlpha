---
ttl: task_bound
---

# C6 全自动入库管线（auto_pipeline）方案挖矿+立项草案——Owner 令"全自动化，不要人参与"

> 2026-09-15 凌晨班｜st-automount-20260915｜按 mining_sop 六向寻路（每向=内部反查+全网搜索双动作）
> 上游：auto_mount 已 production（43f84d01d5→5fb1b4c8dc）；本文档=方案真源，施工等 Owner 批准。

## 0. 一句话

把 C6 线的"人工驱动"部分（台账查询→及格判定→C5 聚类→差异化论证→入库→挂图）做成
**事件驱动全自动管线**：上游 C4 批测落地新行 → 管线自动完成 C5/C6 全部机械步骤 →
candidate 自动挂图 → sim 流转按 Owner 预授权的规则自动执行 → 全程报告落盘+告警通道可观测。

## 1. 挖矿增补（六向寻路日志）

| 向 | 内部反查（已查） | 全网搜索（已查） | 判定 |
|---|---|---|---|
| ①上游（触发源） | DataScheduler `subscribe("task_completed")` 事件机制现成（scheduler.py L712）；C4 批测 c4_batch_screen.py 已幂等四键落账 | wq-alpha-pipeline（brute-force overnight job 全 API 化）；worldquant-miner（24/7 全自动生成→测试→提交） | **事件订阅复用**，触发源零新建 |
| ②下游（消费方） | auto_mount `--apply` 已就绪；PP-001 聚合器消费地图 | BacktestBench（SIGKDD 2026）：LLM 回测能力 67% 准确率——全自动必须机器门禁兜底，不能 LLM 拍脑袋 | auto_mount 即下游，已建成 |
| ③算法/机制（多重检验） | DSR 批内折减已在 _c4_engine；§8 双窗土规已立规；bothwin 查询器已就绪 | Harvey & Liu Sharpe haircut / Benjamini-Hochberg FDR（多文献 2020-2026 一致：自动化管线必须 FDR 控制） | **BHFDR 增量**：及格判定加 BH-FDR q≤0.10（与 §8 并列门，不替代） |
| ④后端（状态机） | KillSwitch（reset requires owner）；factor 生命周期 StateMachine 泛型基类（research→…→retired 8 态 10 转换）现成；auto_runner 事件驱动 gate 执行器现成 | MLOps staged deployment 先例：shadow→canary→production 自动晋升+验证门 | **复用 StateMachine 模式**建 strategy lifecycle FSM |
| ⑤前端（可观测） | 面板 /api/tdm/validation 已渲染 decaying 徽章；Alerter 告警通道现成 | —（无新需求） | 复用面板+告警 |
| ⑥数据字段 | strategy_registry 全字段已支撑（lifecycle_status/baseline_sharpe/family_redundancy 已结构化） | factor zoo 警示（400+ 因子大多 OOS 死亡→自动化筛选必须严门禁） | 字段零新增，family_redundancy 模式推广 |

**噪音过滤**（四闸）：
- LLM 直接生成策略→自动入册（worldquant-miner 路线）：**noise**——BacktestBench 证明 LLM 回测判断
  准确率 67%，且我们 C3 翻译件有知识生效日哨兵（D120），LLM 裸生成无此防线。本项目管线只自动化
  "既有管线的机械环节"，LLM 生成仍走 C1 海选人工/半自动入口。
- 全自动实盘资金流转：**noise**——宪法 §5 production 流转=Owner 门（ Owner 令"不要人参与"的可执行
  解释=门位前置授权，见 §3 治理边界）。
- cron 全量重扫：**noise**——宪法 §9.3 禁 Timer/cron，必须事件驱动（数据落地事件才是真源信号）。
- GitHub Actions 定期跑批测：**noise**——self-hosted runner 24h 队列上限+本地 CH 依赖，本地守护订阅
  更贴已有架构（ch_health_probe 先例）。

**挖干判定**：第 1 轮六向全有产出/查无结论，第 2 轮补搜（staged deployment/kill switch/factor zoo）
均为风险面证实非新矿——**两轮 noise 收敛=挖干**。长尾矿脉：LLM 生成策略入口的自动化（排下一批，
依赖 BacktestBench 级评估能力，当前不施工）。

## 2. 管线设计（五段，全事件驱动）

```
[C4 批测落账] ─task_completed 事件→ [C5 自动聚类] ─及格∧簇首→ [C6 自动入库]
     → [auto_mount 挂图] → [sim 流转（预授权规则）] → [报告+面板+告警]
```

1. **触发**：DataScheduler 订阅扩展——C4 批测任务 task_completed ∧ success → 发布
   `strategy.pipeline.trigger` 事件（EventBus 现成枚举模式，新增事件类型）。
2. **C5 自动聚类**：机械复刻上一班人工流程——拉 bothwin 及格件 → 日净收益 ρ>0.6 贪心聚类 →
   簇首标记 → 写 `family_redundancy` 结构化块（STR-VREV-026 先例）。非簇首标 redundant 留档。
3. **C6 自动入库**：及格 ∧ 簇首 ∧ 三轴差异化论证（模板化生成+机器可验：信号源/持仓周期/状态适配
   与库内既有条目字段级对比）→ 注册表追加 candidate 条目（STR-* 号自动递增，creation_token 管线化）。
4. **自动挂图**：`auto_mount --apply --strategy <新 sid> --report`（已建成，直接调用）。
5. **sim 流转（预授权规则引擎）**：StateMachine 新建 strategy lifecycle FSM（复用因子版泛型基类），
   candidate→sim 转换条件=机器可验三件：§8 双窗全过 ∧ BH-FDR q≤0.10 ∧ 无未决衰减预警。
   **Owner 门位=事前预授权**（见 §3）。

## 3. 治理边界（宪法 §5 兼容性——关键裁定请求）

宪法 §5：production 流转/注册表净删=Owner 门。Owner 本令"不要人参与"的落地解释（三选一，
**请 Owner 圈定**）：
- **A（方案默认）**：Owner 预授权规则引擎——sim 流转按 §2.5 规则自动执行，规则文本本身一次性
  经 Owner 裁定登记（ruling_registry）；sim→production 仍 Owner 门（真金白银）。
- B：全自动到 sim 后**停**，production 永远人工。
- C：全自动含 production（**不建议**：单人系统资金风险无人类回路，业界 staged deployment 先例
  也保留 human-on-the-loop 名义门位）。
- 全线保留：KillSwitch（reset requires owner 先例）+ 月度 auto_mount 审计 + decay_watch 预警。
  自动≠无监督：面板徽章+Alerter 告警=人类回路，只是**不阻塞流程**。

## 4. 验收七条（立项死条款草案）

1. 新 CAND-* 落账后 ≤10 分钟，报告+candidate 条目+挂图 diff 自动产出（事件端到端）。
2. 幂等：同批事件重放零 diff（复用 auto_mount --replay 语义）。
3. FDR 门红蓝：伪造 p 值族（真 H0 集）必被 BH 拒。
4. FSM 非法转换必拒（candidate→production 直跳必抛 InvalidTransitionError）。
5. KillSwitch 触发时管线全链暂停且不丢事件（恢复后续跑）。
6. 三轴差异化论证机器判定与上一班人工裁定一致率 ≥5/6（回放历史批）。
7. Owner 视觉复核一轮。

## 5. 施工清单（一个夜班量级）

- `src/zephyr/strategy_pipeline/`（新包，MOD 号施工时领）：事件订阅器/聚类器/入库器/FSM/报告器
- `scripts/backtest/auto_mount.py` 零改动（下游接口已就绪）
- EventBus 新增 `STRATEGY_PIPELINE_TRIGGER` 事件类型；DataScheduler C4 任务完成回调注册
- 测试：FSM 转换表+BH-FDR 红蓝+幂等重放+KillSwitch 联动（估 25-30 用例）
- 义务：creation_token+add_module_translation+depgraph 登记+净零声明（替代 C5/C6 散文流程 SOP-C §5/§6）

## 6. 净零声明

替代 SOP-C §5（人工聚类差异化）+§6.2（手动挂图）流程散文与"挂哪了"口头裁定；不新增规范对象；
family_redundancy/bothwin/§8 土规/DSR 全部复用既有真源。
