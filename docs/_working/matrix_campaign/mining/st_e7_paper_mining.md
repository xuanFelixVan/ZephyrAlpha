---
campaign: matrix-20261006
lane: S-skeleton
status: draft
ttl: task_bound
---

# st_e7_paper —— E7 模拟盘前哨（SPM 23 节点）

- 真源: `config/strategy_production_map.yaml`；行号=SPM:L*。
- 职责: 策略上岗前最后一道 paper 考试：前哨考核/联赛/mSPRT/灰度，产出转正建议。
- 计数: 23 = 1 stage(built) + 22 mech（built 19 / pending 3）。

## 1. 族内节点全清单

| node_id | 名称 | 状态 | module_ref | 行 |
|---|---|---|---|---|
| FAC-E7 | 模拟盘前哨（stage） | built | MOD-BT-225 | SPM:L368 |
| FAC-E7-M-001 | 模拟盘前哨考核器（Paper Outpost） | built | MOD-BT-225 | SPM:L4051 |
| FAC-E7-M-002 | sim 表部署脚本 | built | MOD-BT-083 | SPM:L4067 |
| FAC-E7-M-003 | 模拟盘治理建议生成器 | built | MOD-BT-094 | SPM:L4082 |
| FAC-E7-M-004 | 转正建议包 | built | MOD-BT-199 | SPM:L4098 |
| FAC-E7-M-005 | E7 前哨对账器（名实冲突见报告：battle 表作 Closed Book Gate） | built | MOD-BT-201 | SPM:L4122 |
| FAC-E7-M-006 | 模拟盘日链接电执行体（sim_daily_runner 桥执行腿） | **pending** | MOD-BT-222 | SPM:L4137 |
| FAC-E7-M-007 | 模拟盘判定台账表结构（病历册） | **pending** | MOD-BT-223 | SPM:L4151 |
| FAC-E7-M-008 | 转正建议晨报摘要渲染器（Morning Digest） | **pending** | MOD-BT-232 | SPM:L4163 |
| FAC-E7-M-009 | 策略灰度发布（Shadow Canary——E7→E8 上新安全阀） | built | dir:_domain_infrastructure_operations/strategy_canary_release | SPM:L4174 |
| FAC-E7-M-010 | 策略仿真器（沙箱+信号模拟） | built | MOD-SIM-002 | SPM:L4186 |
| FAC-E7-M-011 | 日终处理器（E7 对账 NAV/PnL 确认手） | built | MOD-TRADING-012 | SPM:L4198 |
| FAC-E7-M-012 | mSPRT 冠军挑战者序贯晋升 | built | MOD-PF-008 | SPM:L4211 |
| FAC-E7-M-013 | Almgren-Chriss 冲击模型（E7 滑点/容量实测参考） | built | dir:_domain_execution_sim/almgren_chriss_impact_model | SPM:L4222 |
| FAC-E7-M-014 | A/B联赛成对晋升判据执行器 | built | code:scripts/backtest/league_judge.py | SPM:L4234 |
| FAC-E7-M-015 | 联赛注册表（赛马计分板） | built | code:scripts/backtest/league_registry.py | SPM:L4245 |
| FAC-E7-M-016 | 联赛档案打包器（病历册） | built | code:scripts/backtest/league_archive.py | SPM:L4257 |
| FAC-E7-M-017 | 联赛月度快照 | built | code:scripts/backtest/league_monthly_snapshot.py | SPM:L4269 |
| FAC-E7-M-018 | 联赛复原器 | built | code:scripts/backtest/league_restore.py | SPM:L4281 |
| FAC-E7-M-019 | 模拟盘钱包账本 | built | code:scripts/backtest/sim_paper_ledger.py | SPM:L4293 |
| FAC-E7-M-020 | 模拟盘平台日刊生成器（病历） | built | code:scripts/backtest/sim_platform_journal.py | SPM:L4304 |
| FAC-E7-M-021 | sim 转正建议书生成器 | built | code:scripts/backtest/sim_promotion_memo.py | SPM:L4316 |
| FAC-E7-M-022 | 月度危机演练件 | built | code:scripts/backtest/crisis_drill_monthly.py | SPM:L4327 |

## 2. 接线现状与缺口判定

- 已接线：前哨考核+联赛五件（judge/registry/archive/snapshot/restore）+ mSPRT 晋升 + 灰度安全阀 + 钱包账本/日刊/建议书全 built。
- 缺口 3 枚全部集中在**桥执行与交付呈现**：
  - M-006 桥执行腿 pending（MOD-BT-222）——与 chief 02 §1 GAP-1（sim_daily_runner bridge-execute `_BRIDGE_ENV="sim"`→real 翻转，死线 2026-10-08）互为印证：工厂侧标 pending、总包侧标他队施工中，两账一致、归属 st-datasop。
  - M-007 判定台账表结构 pending——病历册缺表。
  - M-008 晨报渲染器 pending——转正建议的人工消费面缺呈现。
- 可考性：E7 是 H9 §4"回测只能近似环节"的承接面（做T/订单九态转模拟盘 sim 平面考，H9 §3.1 T3c）；sim_daily_runner 三闸（plan-bridge/bridge-execute）即本层运行时化身。

## 3. 修复建议（一句话）

M-006 随 GAP-1 归属队列落地（勿双头施工）；M-007/M-008 是 E7 病历闭环的最后一页，建议列入 T3c 前置件。

## 4. 交叉验证

- chief 02 §1：GAP-1/GAP-2（三卡 T 日信号生成件 E-TIMING-001/TSMALL-001/DABAN-023 回测重放接口）——三卡的 sim 考试归宿即本层。
- H9 §1.6/§1.7：模拟盘平面已接回撤六态机 defensive_only 与 KILL 清算（sim_daily_runner.py:1318,1356-1394,1465）——TDM X 族 B 类接口的 live 半边在本层运行。
- census 图13 盘前段 paper session 09:25（census §3 图13）与本层时序衔接。
