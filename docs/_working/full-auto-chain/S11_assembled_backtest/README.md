---
ttl: task_bound
title: S11 整装回测接线挖矿文档
session: st-fullauto-20260915
date: 2026-09-15
---

# S11 整装回测接线（sim 毕业→TDM sleeve→参与整装组合回测→出证据）

> 骨架定位：Owner 口述修正——**策略模拟盘跑通后不是单策略直进实盘，而是作为 sleeve 填入
> 整装回测（交易决策全景图 TDM）参与组合整装回测，整装回测完毕才算成功**。本环节=施工 C3
> 的地基，核心问题：**整装回测的执行入口在哪？从"策略已挂图"到"参与一次完整整装组合回测
> 并落成绩"中间缺哪些自动步骤？**

## 1 现状盘点（自动化状态+file:line 证据）

### 1.1 整装回测 runner 入口结论（本挖矿核心答案）

**整装回测后端已存在且成熟：`run_framework_backtest()`，位于
`src/zephyr/pf_core/strategy_engine/framework_composer.py:1162`（MOD-FWCOMP-001，
"整装组合回测器（二期整装回测后端）"L17）。**

全链路（`run_framework_backtest` L1162-1246）：

```
get_framework_plan(plan_id)                      ← config/framework_plans.yaml 方案权重 α_i
→ _select_vectorizable_members (L1003)           ← tick-only 成员跳过并披露
→ _build_member_panels (L1023)                   ← 逐成员 StrategyRunner.build_weight_panel
→ compose_weight_panels (L381)                   ← W(t,s)=Σα_i(t)·w_i(t,s) 线性合成+Σ=1 归一
    （regime_by_date 非空=三期动态：逐日查 regime_overrides，L579-673）
→ verify_weight_panel_identity (L686)            ← 独立复算逐位硬验收（容差 1e-9，#275 定案）
→ DefaultBacktestEngine.run(data, signals)       ← 复用向量化引擎，禁重写撮合（L8 不变量）
→ _persist_framework_artifact (L1069)            ← sink→产物 bt-fw-<8hex>.json 落
                                                   data/backtest_artifacts/
```

**唯一触发方式=仪表盘 API（人工）**：`src/zephyr/frontend/dashboard/api_server.py:1045`
`POST /api/framework-backtest-run`（body: plan_id/symbols/start/end/dynamic/regime_series...）
→ 串行线程池 `_FW_RUN_POOL`（L956，max_workers=1 防 CH 连接竞争）→ 轮询
`GET /api/framework-backtest-run`（L1124）。**无 CLI wrapper、无计划任务、无事件接线**
（grep run_framework_backtest 全仓：api_server+composer+前端 manifest 三处，无脚本/调度）。

### 1.2 输入契约

- **方案权重真源=`config/framework_plans.yaml`**（三套预设 fw-defensive/fw-balanced/
  fw-aggressive，Σ=1 容差 1e-6；三期 regime_overrides 覆盖表键=REGIME_STATES 七态）。
- **成员 ID 词表=pf_core 代码注册表 kebab-case 策略**：default-equity（default_equity_strategy.py:112）、
  topn-momentum（topn_momentum_strategy.py:103）、multifactor-sleeve（multifactor_sleeve_strategy.py:112）、
  daban-sleeve（daban_sleeve_strategy.py:154）、eventdriven-sleeve（event_driven_sleeve_strategy.py:110）
  +tick-only 三件（intraday-surge-fall/orderbook-imbalance/vwap-reversion）。
  经 `@StrategyRegistry.register` 注册，autodiscover("zephyr.pf_core") 发现
  （framework_composer.py:897-923 `_resolve_member_modes`）。
- **成员面板机制**：`strategy_runner.build_weight_panel`（strategy_runner.py:381-405）=
  load_history(CH 日频) → 因子面板（factor_ids 默认 momentum_20d）→ 截面合成 synthesize →
  PIT shift(1) → 各调仓日（默认 W-FRI）调**该成员策略自己的** `generate_target_weights`
  产权重→ffill。即成员面板=sleeve 策略产权重×通用因子信号，非翻译件 build() 口径。
- **regime 日序**：显式注入 `{date: state}`（api_server 校验七态词表 L1088-1103）；
  真源=regime_detector.REGIME_STATES=["r1","r2","r3","r4","r10","r11","r12"]
  （regime_detector.py:249）；离线批量生产件已落=`zephyr/backtest/regime_validation/
  shrinkage_provider.py:130 build_schedule_from_detector`；另一数据源=`c1_backtest.
  regime_snapshot_history.dominant`（auto_mount.py:105-115 消费先例；写方=print_regime_history.py，
  **manual CLI，无排班**）。

### 1.3 关键断桥：TDM PP-001 ≠ framework_plans.yaml（两套权重真源不通）

- auto_mount（S07/S11 挂图器，`scripts/backtest/auto_mount.py:21-27`）把新策略挂上的是
  **TDM（config/trading_decision_map.yaml）**：节点 strategy_mounts+state_matrix 格子+
  `portfolio_plan.sleeves`（新 sleeve 0.05 等权起步、老 sleeve 等比缩水，`sleeve_plan` L152-157，
  only_add_assert L246-271 语义门+38 规则校验）。
- 挂图现状（auto-mount-report-20260915-0228.md）：已挂 6 策略——STR-VREV-025/026、
  STR-MOMTREND-033（TDM-E-L1）、STR-TSMALL-001、STR-VAL-001（TDM-E-L3-07-3）、
  STR-DABAN-023（TDM-P-P2）；权重方案=8 个 kebab sleeve 老成员等比缩水+6 个 STR-* 各 0.05。
- **但整装回测 runner 读的是 framework_plans.yaml，不是 TDM**：
  `grep "STR-" config/framework_plans.yaml` = **0 命中**——6 个已挂图 STR-* 策略**不在任何
  整装方案的成员表里**。
- TDM `portfolio_plan.sleeves` 的消费方反查：只有 `src/zephyr/trading/decision_map.py:415-445/
  946-982` 的 load/validate（R12 整装方案校验）——**无任何回测 runner 消费 TDM 权重**。
- 翻译件口径（c4_*.py build()）与 StrategyRegistry 口径（generate_target_weights）是两套
  不兼容接口，framework_composer 无 STR-* 适配器——**这就是"挂图有、参与整装回测无接线"的
  断点本体**。

### 1.4 输出落档与实跑证据

- 产物=`data/backtest_artifacts/bt-fw-<8hex>.json`（BacktestRunArtifact CTR-P1-017 十五字段
  契约冻结；plan_id/成员/跳过/rescale/regime_day_counts/panel_reconciliation 落 metrics 扩展，
  framework_composer.py:1069-1118）。目录现存 45 件产物，其中 bt-fw-* 8+ 件
  （2026-09-09~09-10，含动态 regime 跑 bt-fw-c7ca8ad7 dyn=True）——**整装回测被人工跑通过**。
- 耗时量级（产物时间戳推断）：同晚 23:30→23:44→23:46→23:52 连续 4 跑，单跑分钟级；
  窗口 equity_points 69-126（约 3-6 个月窗口）。**精确耗时未实测，C3 验收时补测。**
- 面板对账：verify_weight_panel_identity（L686-746）独立复算（不调 compose，防同源盲区），
  超容差落 warn——每次运行自带回归绊线，C3 自动化可直接消费该字段做验收。

### 1.5 相邻库存（已落码未接线的资产盘点）

- `src/zephyr/backtest/core/walk_forward.py`（MOD-BT-001）：WF 三模式+White's Reality Check+
  CPCV 切分——通用离线验证层，**未接入整装链**（TDM-F-C3-04 节点把 WFE>60% 列为参数校准
  门槛，属远期）。
- `src/zephyr/backtest/core/strategy_cpcv_matrix.py`（MOD-BT-028）：策略级 CPCV 稳健分筛选
  （性能矩阵注入式，不跑回测）——同上，离线层未接线。
- `src/zephyr/pf_alloc/core/`（MOD-PA-003 多策略资金分配器等 14 件）与
  `src/zephyr/pf_core/core/performance_attribution_engine.py`（MOD-PF-007 Brinson 归因+降级/
  拥挤检测）：**实盘运行时侧（D-PF-CORE/PC-01）的生产库，非整装回测链组件**，本班只登记
  边界不接线。
- TDM 自我注记：TDM-F-C1 节点 algo_note"PP-001 演进：等权→…→拼装回测归因（拼装回测引擎
  planned）"（trading_decision_map.yaml:3877）——TDM 侧也承认整装回测接线是 planned。

## 2 六向挖矿日志表

| 轮 | 矿脉（方向） | 动作与证据 | 判定 |
|----|-------------|-----------|------|
| R1 | ④后端：runner 定位 | grep walk_forward/weight_panel/verify_weight_panel_identity → framework_composer.py L17"整装组合回测器"+L1162 run_framework_backtest | **signal**（入口结论） |
| R2 | ②下游：触发链反查 | api_server.py:1016/1045/1124 三端点；_FW_RUN_POOL 串行；前端 manifest.yaml:169 消费；无 CLI/调度/事件 | **signal** |
| R3 | ①上游：输入契约+断桥定性 | framework_plans.yaml 全读；grep STR- 零命中；TDM sleeves 消费反查仅 decision_map validate；auto-mount-report 6 策略实证 | **signal**（C3 核心断点） |
| R4 | ③机制：成员面板+regime 动态链 | strategy_runner.py:381-505；shrinkage_provider.py:130；regime_detector.py:249；regime_snapshot_history 写方 manual | **signal** |
| R5 | ⑥数据字段：产物与耗时 | data/backtest_artifacts 45 件、bt-fw-* 8+ 件、动态跑实证；耗时分钟级（时间戳推断，待实测） | **signal** |
| R6 | ④后端：库存盘点（walk_forward/CPCV/pf_alloc/pf_core） | MOD-BT-001/MOD-BT-028/MOD-PA-003/MOD-PF-007 头注+消费反查：离线层与实盘库未接整装链 | **signal** |
| R7 | ③机制（外部）：组合回测实践 | Man Group 多策略组合构建（man.com，访问 2026-09）；Hedge Fund Journal 动态 sleeve 权重带（thehedgefundjournal.com，访问 2026-09）；MathWorks Financial Toolbox 回测引擎 rebalance schedule（mathworks.com，访问 2026-09）；QuantInsti WFO（blog.quantinsti.com，访问 2026-09） | **signal** |
| R8 | 旁证：PP-001 误命中与无关库 | exam_test_cases.py EX-PP-001 用例无关；amibroker 论坛 RFC 无关 | **noise**（单轮内子项，被 R1-R7 signal 打断不构成封矿） |

轮次判定：7 signal / 1 noise。核心矿（runner 入口+断桥）已挖透，封批转 C3。

## 3 业界与开源对照

- **多策略 sleeve 组合惯例**：Man Group/Hedge Fund Journal（URL 见 R7）：多策略组合=底层
  策略池→sleeve 权重（带状约束）→组合层再平衡；组合回测必须能"新 sleeve 进池后一键重出
  组合净值+归因"。本项目 compose_weight_panels+verify_weight_panel_identity 已达该形态，
  缺的只是自动触发与 STR-* 成员适配。
- **引擎对照**：MathWorks Financial Toolbox backtest 引擎（rebalance schedule+strategy 类注入）
  与 QuantStart Python 框架（URL 见 R7）均为"权重面板进引擎"模式——与本项目
  DefaultBacktestEngine(signals=weight_panel) 同构，架构选型无需改。
- **walk-forward 组合校准**：QuantInsti/HackerNoon WFO 模式（URL 见 R7）：组合权重参数须
  walk-forward 出样本外验证——对应本项目 TDM-F-C3-04 的 WFE 门槛（planned），C3 不做，
  登记远期矿脉。

## 4 堵点与欠账清单

| # | 堵点 | 证据 | 后果 |
|---|------|------|------|
| 1 | **断桥①**：TDM PP-001 权重不进 runner | framework_plans.yaml 零 STR-；TDM sleeves 无回测消费方 | 挂图=纸面动作，整装回测永远跑"旧 8 员" |
| 2 | **断桥②**：STR-* 翻译件无成员适配器 | build() 接口 vs StrategyRegistry.generate_target_weights 两套契约 | 即使把 STR-* 写进方案表，runner 也造不出其面板 |
| 3 | **断桥③**：整装回测无自动触发 | 仅 API 人工触发；无 CLI/事件/计划任务 | "整装回测完毕才算成功"无人值守不可达 |
| 4 | regime 日序无持久化生产 | regime_snapshot_history 写方 print_regime_history manual；动态模式要求显式注入 | 自动跑动态整装缺日序供给件 |
| 5 | 标的池无自动口径 | API body 必填 symbols，人工给 | 无人值守无法定参（UNI 注册表有 universe 资产，未接） |
| 6 | 耗时/资源未实测 | 仅产物时间戳推断分钟级 | C3 排班与超时参数缺依据 |
| 7 | walk-forward/CPCV/归因层未接线 | R6 库存盘点 | 整装证据包缺 OOS 稳健性与归因章（远期欠账，不阻 C3 最小路径） |

## 5 施工项建议（C3 整装回测接线方案雏形）

**目标最小路径：`新策略挂图成功 → 自动重跑一次整装组合回测 → 证据包落档+告警`，
四件施工：**

1. **STR-* 成员适配器（断桥②，核心件）**：
   `src/zephyr/pf_core/strategy_engine/` 新增 translated 面板适配：输入=注册表 code_path
   翻译件 `build(start,end)→(weights,closes)`（与 sim_deviation_report.py:157-171 同一重放
   口径），输出=与其余成员同构的 date×symbol 权重面板（weights 已是该口径；closes 仅供
   引擎 data 对齐）。挂进 `_build_member_panels`：成员 ID 以 `STR-` 前缀路由到适配器
   （kebab 老成员走原路）。
   - 验收标准：STR-VREV-025 面板与 sim_deviation_report 同月重放逐位一致；非调仓日语义
     与引擎 ffill 契约对齐；面板空/缺契约=跳过并落 skipped 披露（不拖垮整装跑）。
2. **方案表生成器（断桥①）**：新脚本 `scripts/backtest/generate_framework_plan_from_tdm.py`：
   读 TDM `portfolio_plan.sleeves`（真源，auto_mount 只-add 已保 Σ=1）→ 生成/更新
   framework_plans.yaml 的新 plan（建议 plan_id=`fw-tdm-current`，保留三套人工预设不动；
   写入走 safe_write_text CAS+38 规则校验复用）。生成器产管，禁手工维护（运维红线 5）。
   - 验收标准：TDM 挂 6 策略后生成的方案表含 14 员、Σ=1e-6；重放零 diff；YAML 校验过。
3. **自动触发接线（断桥③）**：pipeline_events 新增 kind `fw_backtest_due`（重 kind，
   仿 run_c4_batch_due 子进程+超时模式）：
   - 触发源 A（事件式）：intake `_auto_mount_sids`（intake.py:387-426）applied=True 后
     emit（挂图成功=自然唤醒，事件触发合规）；
   - handler 四步：生成器刷新方案表（步骤 2）→ 组装参数（symbols=UNI-RULE-001 或
     中证1000 成份注册表，start/end=近 12 个月滚动窗；regime_by_date=regime_snapshot_history
     dominant 自动产出日序，步骤 4 供给）→ 子进程跑 `run_framework_backtest` → 验收
     （panel_reconciliation.within_tolerance=True+equity_points>0）→ 证据包落
     `docs/_working/pipeline-research/fw-backtests/`（md+json：成员/权重/对账/关键指标/
     产物 run_id）+ Alerter 通报。产物 bt-fw-*.json 落档不变。
   - 验收标准：人为挂一个测试 STR → 全链无人参与产出证据包；对账超容差或空净值=告警+
     非零 rc。
4. **regime 日序供给件**：把 print_regime_history 的落库逻辑提为可调函数或注册
   `regime_snapshot_daily` 事件 kind（挂 daily_kline 完成唤醒），保证 regime_snapshot_history
   日更；C3 handler 读表产 regime_by_date。动态模式首跑可先静态（regime_by_date=None）
   降级验收，日序件跟上后切动态。
5. **耗时实测与排班参数**：C3 首跑记录单跑耗时/CH 峰值内存，回填本档 §1.4，
   定超时（建议首值 3600s）与串行约束（复用 _FW_RUN_POOL 同款单线程语义，子进程天然串行）。
6. **登记远期（不在 C3）**：整装 walk-forward OOS 章（MOD-BT-001/028 接线）、Brinson 归因章
   （MOD-PF-007 接线）、月度整装例跑（C3 稳定后挂月度 marker）。

## 6 封矿结论

- 矿脉层面：7 signal/1 noise，runner 入口、输入输出契约、断桥本体、库存边界全部挖透，封批。
- 方案层面：整装回测接线是 Owner 口述流程修正（"整装完毕才算成功"）的承载环节，消灭
  "人工点页面发起回测+人工读产物"人工位，终局必经，**施工**（C3，四件套方案见 §5）；
  walk-forward 组合校准与归因章**挂起排期**（解锁条件=C3 最小路径稳定运行一个月）。
- 一句话结论：**整装回测 runner=framework_composer.run_framework_backtest，已被人工跑通；
  缺的是 TDM PP-001→方案表的生成桥、STR-* 翻译件面板适配器、事件式自动触发三件，
  三件齐则"挂图→整装回测→证据包"全自动可达。**
