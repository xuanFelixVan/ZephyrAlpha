---
ttl: task_bound
title: S08 模拟盘开户挖矿文档
session: st-fullauto-20260915
date: 2026-09-15
---

# S08 模拟盘开户（新 sim 策略自动开钱包）

> 骨架定位：S07 intake 升格出 lifecycle:"sim" 条目后，**自动为每个 sim 策略开虚拟钱包**。
> 当前状态=❌ 断：开户动作不存在，账本单策略硬编码。本环节=施工 C1 的地基。

## 1 现状盘点（自动化状态+file:line 证据）

### 1.1 上游已自动化（S07 侧，本环节的输入）

- C6 intake 编排全自动：`src/zephyr/strategy_pipeline/intake.py:311-312`——`promote_to_sim()` 过
  FSM 预授权三条件（§8 双窗 ∧ BH-FDR q≤0.10 ∧ 无未决衰减预警）后 `lifecycle = "sim"`，
  条目写入注册表时 `lifecycle_status: lifecycle`（`intake.py:212`，经 registry_writer CAS）。
- 触发链已通：DataScheduler task_completed → `pipeline_events.wire_data_scheduler`
  （`src/zephyr/strategy_pipeline/pipeline_events.py:315-330`）→ `c4_batch_completed` 事件 →
  `run_intake_auto(dry_run=False)`（`pipeline_events.py:142-145`）。
- FSM 真源：`src/zephyr/strategy_pipeline/lifecycle_fsm.py:95`——candidate→sim 边
  guard=`SimPromotionGuard`（L64-73，三条件全机器可验证，零人工）；sim→production 才是
  OwnerTokenGuard（L76-80）。

### 1.2 注册表 sim 条目现状（开户应服务的对象）

- `docs/01_policies_and_standards/_registry/catalogs/strategy_registry.yaml` 共 158 条带
  lifecycle_status 的条目，其中 **`lifecycle_status: "sim"` 恰 2 条**（grep 实证）：
  - `STR-E-TIMING-001`（L129 起，code_path=`scripts/backtest/lane_e_quantile_baseline.py`，L147-148）
  - `STR-VREV-025`（code_path=`scripts/backtest/translated/c4_e3da6fa71af1_panic_rebound.py`，L12215-12216）
- 注册表 schema 枚举注释：candidate/backtest/sim/paper/live/monitoring/decayed/retired
  （strategy_registry.yaml:58）——注意此枚举与 FSM 五态词表分裂（详见 S10 文档 §4）。

### 1.3 断点本体：账本单策略硬编码，无开户动作

- 钱包账本 `scripts/backtest/sim_paper_ledger.py`：
  - **L40 `STRATEGY_ID = "STR-VREV-025"` 模块级硬编码**；L42-44 连策略参数（阈值/-0.015/-0.014/
    持仓 20 日/标的 000852/成本）全部内联在账本里——即账本把"恐慌反弹"这一策略逻辑**复制内嵌**，
    并非消费翻译件 `build()` 契约。
  - L182 `rebuild(STRATEGY_ID, ...)` 重建也只重建该单钱包。
  - `[STARTUP] manual`（L6）；`[CONSUMERS]` 注明"每日自动化（接线另批）"（L5）。
- **无任何"开户"代码路径**：grep 全仓 `sim_paper_ledger` 的引用方，只有 script-manifest.yaml 登记；
  intake/pipeline_events/registry_writer 均不 import 它。intake 写完注册表 sim 条目后链路到此为止。
- 数据面：`c1_backtest.sim_pocket_daily` / `c1_backtest.sim_trade_log` 的**唯一写入方=
  sim_paper_ledger**（grep 实证，另两文件为 DDL 部署件 `scripts/ch/apply_sim_*_ddl.py`）；
  读方=`sim_platform_journal`（S09）与 `sim_deviation_report`（S10）。
- 结论：**"注册表 sim 条目 → 钱包存在"之间零接线**。STR-E-TIMING-001 已 sim 但无钱包，
  平台日刊与月度偏离报告实际只看得到 STR-VREV-025 一条腿。

## 2 六向挖矿日志表

| 轮 | 矿脉（方向） | 动作与证据 | 判定 |
|----|-------------|-----------|------|
| R1 | ①上游：intake→sim 流转链 | intake.py L303-312 三条件判定+L312 lifecycle 写入；lifecycle_fsm.py L95/L100 sim 双边；pipeline_events L142-145 事件消费链 | **signal** |
| R2 | ②下游：sim 条目→运行引擎/钱包 | grep `sim_paper_ledger` 全仓仅 manifest 登记；intake 无开户调用；注册表 2 sim 条目实查（L147-148/L12215-12216） | **signal**（断点定性） |
| R3 | ④后端：账本模块解剖 | sim_paper_ledger L40/L42-44/L182；策略逻辑内联非消费 build() 契约；[STARTUP] manual | **signal** |
| R4 | ⑥数据字段：sim_pocket_daily/sim_trade_log 读写反查 | 唯一写方=ledger；读方=journal/deviation_report；DDL 部署件 2 个；schema 注释枚举 L58 | **signal** |
| R5 | ③机制（外部）：paper trading 平台开户惯例 | QuantConnect research→backtest→paper→live 流水线（https://www.quantconnect.com/docs/v2/cloud-platform/research-pipeline ，QuantConnect，访问 2026-09）；Quantpedia "paper trade 验证回测不过拟合"（https://quantpedia.com/how-to-paper-trade-quantpedia-backtests/ ，访问 2026-09） | **signal** |
| R6 | 旁证查无：scripts/*.ps1 与计划任务有无 sim 四件 | grep 零命中（仅 check_specific_versions.ps1 提到 53 号文文件名）；schtasks 30 个 Zephyr 任务无 paper/sim | **查无**（断点旁证，非 noise） |

轮次判定：5 signal / 0 noise / 1 查无。未连续两轮 noise，矿脉未枯；但 C1 施工方案已成形（§5），
按"候选>0 即转施工"纪律封批。

## 3 业界与开源对照

- **流水线分期惯例**：QuantConnect 把 research→backtest→paper→live 做成看板式晋升管线，paper
  是独立阶段且账户/引擎与回测同构（URL 见 R5）——本项目"翻译件 build() 同口径重放"与该惯例
  同构，方向正确，缺的是**每策略自动开户**这一步。
- **paper 账户隔离惯例**：业界 paper 账户=独立资金额度+独立成交流水（本项目已做到：
  一策略一钱包行+sim_trade_log 事件流，sim_paper_ledger.py:46-47 两表契约）；缺口在"开户"
  是手工/代码硬编码而非流水线自动派生。
- **验证期长度**：QuantifiedStrategies 建议 paper 至少 3-6 个月再上真钱（https://www.quantifiedstrategies.com/algorithmic-trading-strategies/ ，访问 2026-09）——与 SOP-C §8"连续 2 月月度判定"量级吻合，可作 S10 阈值的外部锚。

## 4 堵点与欠账清单

| # | 堵点 | 证据 | 后果 |
|---|------|------|------|
| 1 | 无"开户"动作：intake 升格 sim 后不创建钱包 | intake.py 全文无 ledger 调用；grep 查无 | sim 条目=纸面状态，平台日刊心跳检会报"钱包行缺失" |
| 2 | 账本单策略硬编码+策略逻辑内联 | sim_paper_ledger.py:40-44 | 每新增 sim 策略需改代码，违反"静态清单禁手工维护"精神 |
| 3 | 账本逻辑与翻译件双真源漂移风险 | 账本 L42-44 内联阈值 vs translated/c4_e3da6fa71af1 build() | 阈值改动只改一边→偏离报告误判 |
| 4 | STR-E-TIMING-001 无钱包 | 注册表 L147-148 sim；账本只认 STR-VREV-025 | 偏离报告 `registry_sim_entries()` 会跳过它（缺 build 契约则 warn 跳过，sim_deviation_report.py:110-121），治理覆盖不全 |
| 5 | 事件链无 sim 开户钩子 | pipeline_events LIGHT/HEAVY_KINDS 无开户 kind | 无人值守链路在此断 |

## 5 施工项建议（C1 模拟盘自动开户方案雏形）

**C1 多策略钱包引擎 + intake 开户钩子**（两件，同批施工）：

1. **钱包引擎通用化**——`scripts/backtest/sim_paper_ledger.py` 改造为 `--strategy STR-XXX` 参数化：
   - 账本**不再内联策略逻辑**，改为消费注册表 `code_path` 翻译件 `build(start, end) → (weights, closes)`
     契约（与 sim_deviation_report.py:157-171 同一重放口径，消灭双真源）；
   - 钱包初始资金=Owner 已批额度分档（现行 100 万/钱包，QUOTA 预警线复用
     sim_platform_journal.py:34 的 110 万线）；日账=昨日权重面板×今收价×冻结土规成本；
   - 幂等=同策略+日替换写（现行语义保留）；`sim_trade_log` 事件流照旧；
   - 兼容期：STR-VREV-025 保留内联路径或一次性迁移到翻译件口径，用偏离报告对账验证等位。
   - 验收标准：`python scripts/backtest/sim_paper_ledger.py --mode sim_daily --strategy STR-E-TIMING-001`
     产出该策略钱包行；同日重跑零 diff；STR-VREV-025 迁移后与旧口径月收益偏差=0。
2. **intake 开户钩子**——`src/zephyr/strategy_pipeline/intake.py::run_intake` 在 `sim_promoted`
   非空时（dry_run=False 分支，约 L342 后）emit 新事件 kind `sim_wallet_due`（payload=新 sim sids），
   `pipeline_events._default_handler` 增加 handler：调钱包引擎为每个新 sim sid 建首日钱包行
   （轻 kind，幂等：已有钱包行则跳过）。fail-closed 与现有事件语义一致（失败留 journal 重放）。
   - 验收标准：单测模拟 run_intake 升格 2 策略 → journal 出现 sim_wallet_due → drain 后
     sim_pocket_daily 出现两策略首日行；KillSwitch 激活时不写。
3. **登记欠账**：STR-E-TIMING-001 补开钱包（C1 落地后首跑即覆盖，无需单独施工）。

## 6 封矿结论

- 矿脉层面：核心矿已挖干（流转链/账本/数据面/外部惯例四向闭环），双噪音未现但施工方案已
  成形，按纪律封批转 C1 施工。
- 方案层面：C1 是终局全貌的必经件（无人值守链路中"开户"必须无人参与），**施工**裁定，
  无过度工程嫌疑；钱包引擎消费翻译件契约是唯一能同时消灭"双真源漂移"与"每策略改代码"
  两个人工位的形态。

## 7 施工班状态回填（2026-09-15）

- C1 两件均落地：①intake `run_intake` sim 流转后 emit `sim_wallet_due`，pipeline_events handler 复用账本 ensure_wallet（幂等，轻 kind）；②`sim_paper_ledger.py` 参数化（`--strategy-id`，用法见 :29）。
- 诚实边界（对齐骨架挂起项"账本消费 build() 契约重构"）：非内置引擎策略（如 STR-E-TIMING-001）钱包行待翻译件 build() 重放接线后才产真实信号口径——禁伪造，接线仍挂起。
- §5 验收标准对应状态：钩子与参数化已随管线套件测试；"STR-E-TIMING-001 产出真实信号钱包行"待 build() 接线后达成。
