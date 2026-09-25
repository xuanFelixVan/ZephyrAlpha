---
ttl: task_bound
volume: 06_ibt_backtest
session: st-commitspeed-tbl-20260924
---

# 06 · IBT 整装回测（四窗/协议/红蓝/HOLDOUT 保密考卷）

## 一、环节定义与边界
协议治理下的整装（assembled）回测：四层级联（L1 regime 节流×L3 个股 15 员×L4 线性合成×向量化引擎 T+1/全成本/PIT）在四窗（W_IS/W_OOS/W_HOLDOUT/W_POSTD）出证+红蓝对抗。上游=数据矩阵+策略资产池；下游=模拟盘准入判定+Max 整改方案（批 A-H）。真源五册=docs/_working/integrated_backtest/（PROTOCOL-V1/DATA-MATRIX/RUN-REPORT/REDBLUE-REPORT/FINAL-DELIVERY）+审计=decision_map_campaign 11 号文。**HOLDOUT 单次烧毁纪律：跑前禁跑、跑后禁重。**

## 二、六向台账

| 向 | 内容（证据） |
|---|---|
| 上游输入 | 引擎=zephyr.backtest.implementations.vectorized_engine（DefaultBacktestEngine：execution_lag_days=1 硬断言+开盘优先成交+PIT 池过滤+护栏内建）；数据=kline_daily_hfq 四窗全绿（W_IS 484.7 万行/4996 标的）+regime_snapshot_history（PIT 读法 trade_date<t 最近行）；成员=15 员（IBT-A 等权 1/15；IBT-B 加 L1 shrinkage 节流） |
| 下游消费 | artifacts/（run_summary/nav/trades/sensitivity/redblue 机读 yaml）；模拟盘准入判定（差项=成本容量/池时效/regime 方向失真三座大山）；max_remediation_plan.md 批 A-H 整改线 |
| 自动化触发 | manual CLI（ibt_runner.py 头 TTL=task_bound 自注"一次性战役工具件"）；无计划任务 |
| 真源与注册表 | IBT-PROTOCOL-V1.md（frozen 2026-09-22T01:05，协议窗口/成本/判据/红蓝设计冻结）；BLUEPRINT=MOD-BT-IBT-RUNNER；复现件=scripts/backtest/ibt/（runner/redblue/attrib/mining_matrix 四件实测 ls） |
| 门禁与质量尺 | 红蓝四向 4 轮：8/8→6/7+1RED（覆盖缺件补跑）→8/8→8/8 连续两轮 0 闭环；引擎护栏=lag0 raise/ImplausibleBacktestError/CH 空串→RuntimeError；holdout 铁律=最近 12 月保密考卷、定稿锚 D=2026-09-09 |
| 当前运行状态 | **绿（战役级完成）**：四窗终版数字落 FINAL-DELIVERY §2（下表）；但 11 号文审计出 3 处跨车道未闭项（堵点 3-5） |

首跑终版数字（FINAL-DELIVERY.md §2 实录，本车道转录）：W_IS -12.1%/Sharpe -0.12/DD 35.3%；W_OOS +11.9%/+0.34/16.0%（基准 +31.9%）；**W_HOLDOUT -12.2%/-1.389（C 门不过，单次烧毁）**；W_POSTD -2.1%（<60 样）。红蓝红证要点：49,147 fills 逐笔 T+1 审计 0 违例；2,721 个 regime 键全 PIT；成本五档两窗严格单调+零成本全场最优。

## 三、子模块清单（8 子环节）

| # | 子环节 | 入口 file:line | 状态 |
|---|---|---|---|
| 6.1 | 协议冻结件（窗口/成本/判据/红蓝设计，禁跑中改动） | docs/_working/integrated_backtest/IBT-PROTOCOL-V1.md；ibt_runner.py:36-40（WINDOWS 常量） | 绿 |
| 6.2 | 四窗 runner（IBT-A 静态/IBT-B 节流/成员单跑/000300 基准/成本敏感性 --sensitivity 仅 IS/OOS；面板缓存 .runtime/tmp/ibt_panels） | scripts/backtest/ibt/ibt_runner.py:26-48 | 绿 |
| 6.3 | 红蓝对抗件（同目录导入复用 run_engine/regime/数据装载；四向探针=前视注入/T+1 审计/PIT 键/退市剔除/成本单调） | scripts/backtest/ibt/ibt_redblue.py（runner 头 CONSUMERS 实锚） | 绿（4 轮连续两轮 0 案底） |
| 6.4 | 归因件（三座大山定量：成本拖累 38.6pct+换手 33-39x；regime r4/r10 方向失真互证；池时效 IS 全负→OOS 转正→HOLDOUT 全灭） | scripts/backtest/ibt/ibt_attrib.py；ibt_attribution.yaml | 绿 |
| 6.5 | 挖矿矩阵件（数据完备性 wall 279s 实测：表级 SQL+17 策略×4 窗 build 冒烟） | scripts/backtest/ibt/ibt_mining_matrix.py→IBT-DATA-MATRIX.md+ibt_data_matrix.yaml | 绿 |
| 6.6 | PIT/前视防线族（引擎内建+探测器：look_ahead_bias_detector/overfitting_protection_gate/pit_manager/purged_kfold/cpcv/deflated_sharpe_calculator/n_trial_ledger） | src/zephyr/simulation/（ls 实测 7 件）+src/zephyr/backtest/core/（ls 实测 6 件） | 绿 |
| 6.7 | 整装审计（八环节"宇宙不完整"举一反三，469 vs 800+ 同款问法） | docs/_working/decision_map_campaign_20260924/11_integrated_backtest_audit.md §0 总览表 | 绿（审计交付） |
| 6.8 | 整改线（Max 施工方案批 A-H+14 项问题清单 HANDOFF） | docs/_working/integrated_backtest/max_remediation_plan.md+IBT-HANDOFF-TO-MAX.md | **黄**：批A 成本考尺修真批落地（经 q-0006 复活），余批随 GPU 窗排程 |

## 四、堵点与病灶（含已闭环历史案，防复发登记）
1. **已修·FACT 符号后缀死权重**：面板 000002.SZ vs 引擎裸码→FACT 六 sleeve 全程不可成交（首版 W_IS 数字作废重跑）——修=runner split('.')[0] 符号归一+清面板缓存（IBT 台账 01:16 杀批记录）。教训：跨件 ID 归一要进数据装载层，非消费端补丁。
2. **已修·跨批 sharpe 漂移（新鲜窗类）**：OOS 敏感性 02:30 夜跑带推进 hfq 表致跨批重算漂移——修=同批六档全量重算定稿（03:03 案底）。配方已沉淀：**敏感档全量同批跑**。
3. **未闭·组合构建占位（IBT-C01）**：等权 1/15 是占位件，7 态×15 员权重矩阵=105 格全空，装配层本体未建——与 07 册 pf_alloc 装配体衔接（pf_alloc 已供件，缺"IBT 复考挂 pf_alloc 权重"一步）。跨车道移交。
4. **未闭·成绩单断桥+蒸发（IBT-B03）**：22 件 nav/trades/run_summary 尾件主区盘面不见（09-24 蒸发连环案受害者，10_evaporation_forensics.md）——修复依赖 artifacts 重建（runner 幂等可重放）。移交施工班。
5. **未闭·批 D 新鲜窗重考（IBT-F01）**：artifacts_v2 仅 1 pkl，重考未完成→GPU 搜索池基悬空（与 05 册堵点 3 同案）。
6. **在案·600016 复权事件缺+老股深史 0.2-0.4% 偏差**（PROTOCOL §4，甲线尾款）——登记级，不阻断。
7. **在案·探针列名误报（状态轴列名坑支线）**：financial_derived trade_date 列名不符=探测 SQL 问题非数据缺失，IBT-DATA-MATRIX §1 已澄清+11 号文 §1.2 复核留痕（诚实披露闭环）。

## 五、提速与合并机会
- ibt_runner 与 vectorized_engine 与 factory_grid（_c4_engine）**两套引擎成本口径**（IBT-D01）若裁定统一，IBT 复考可直接消费 GPU manifest 省一轮全量重跑（前提=5 册堵点 2 裁定）。
- PANEL_CACHE（.runtime/tmp/ibt_panels）与 GPU 侧宽表加载重复读盘——T1 完赛后若跑 IBT 复考，先共享宽表缓存层。M。

## 六、自审闸三态
**挖干可施工**（8 子环节 file:line+五册真源+审计班双源交叉；未闭项全部有案底编号 IBT-XXX）。堵点 3/4/5 跨车道移交，1/2 已闭防复发。

## 七、复核命令
```bash
sed -n '1,48p' scripts/backtest/ibt/ibt_runner.py
grep -n "W_HOLDOUT\|-1.389\|38.6pct" docs/_working/integrated_backtest/IBT-FINAL-DELIVERY.md | head
sed -n '12,40p' docs/_working/decision_map_campaign_20260924/11_integrated_backtest_audit.md
ls scripts/backtest/ibt/ docs/_working/integrated_backtest/
```
