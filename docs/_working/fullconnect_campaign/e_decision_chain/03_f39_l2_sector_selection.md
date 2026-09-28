---
ttl: task_bound
title: F39 L2 板块选择——全流通挖干案卷（矿道 L05）
session: zc-l05-20260927
creation_token: fc-f39-l2-sector-20260927
---

# F39 L2 板块选择——挖干案卷

> 一句话：板块层总枢纽——10 子环节产出当日板块候选池（3-5 个主攻板块）排序喂 L3（只传"板块强度调节分+龙头定位"两字段）。节点组=TDM-E-L2+01..10 组；**今日 yaml:545-1393 机数=29 节点**。总册 built｜P1｜T4；上游 F38，下游 F40/F41+P1-04。

## 一、六向台账（实证锚点）

| 向 | 内容（锚点） |
|---|---|
| ①上游输入 | L1 六段/水温/市场级调节；DS-059/170/082/181/186/107/224/225；emotion_index（偏好第二轴，L02 SKEL A 块） |
| ②数据原料 | kline_sector_880 70 日面板+limit_up_pool×sector_constituent+money_flow（册引 f39 册 §四）；c1_market.kline_sector_880 437,204 行/469 码当日到（12 号文，L03 SKEL §1 册引） |
| ③状态输出 | c1_market.sector_state（rrg_quadrant/strength/net_inflow_pct/capital_score/watch_score）+c1_market.sector_preference（preference_label/tilt/banned_quadrant）；板块总分 clamp[0,100] 前 15% 进候选池 |
| ④下游消费 | L3（两字段层级隔离）；daily_gate_snapshot.load_l2_admission（**写好但全仓零消费方**，L03 SKEL §2 实证）；P1-04 板块退潮否决；boundary_revision_engine 电风扇降档（:92/139/338，L03 SKEL §4 唯一实证生产接线） |
| ⑤自动化触发 | sector_close_final 15:10（schedule.yaml:258 今日实锚）+sector_pre_open 09:15（:263）；旁路 ZephyrAlpha_SectorSnapshot 16:40+IntradayFundFlow 五时点（册引） |
| ⑥缺口债 | L2-05 module_ref=null（pending_gate，今日 sed 实锚 :988-1013 含 red_reason: pending_gate）；L2-08 四段生命周期码面无枚举；L2-03 量能缩量维缺；29 件验证全 untested |

## 二、子模块三级枚举（2026-09-27 实扫）

- 域 `src/zephyr/signal_ashare/`：155 件 .py；sector/ 子目录 18 件+core/ 11 件（今日 ls 实扫）。
- sector/ 18 件（册引+实扫交集）：sector_rrg.py（四象限 :70-78）、sector_rotation_state.py（五分类 :40-59）、sector_adjustment.py、sector_ecology_judge.py（三态 :8,38-42）、sector_gate.py（水温响应+三级放行，重复挂 L2-05-2/05-1）、sector_leader.py（龙头四定位）、sector_pullback.py（A/B/C 取最弱 :60-63,148-149）、sector_conduction.py（封闭乘数，MOD-SIG-136）、sector_momentum.py、sector_momentum_persistence.py、sector_divergence.py（1141 行）、sector_analyzer.py、sector_siphon.py、sector_breadth.py、sector_state_aggregator.py（AGGREGATOR_VERSION=0.1.0 纯函数）等。
- 编排件：src/zephyr/data/sector_state_pipeline.py（纯编排层，算法全委托 aggregator）。
- 31 个 module_ref 全在盘零缺件（册引 f39 册 §四）；共享挂载：sector_gate×2、sector_conduction×2、sector_analyzer×2、sector_pullback×2。

## 三、接线四态独立复核（2026-09-27）

| 件 | 四态判定 | 独立证据 |
|---|---|---|
| sector_state 供料端 | **生产接线** | 双调度槽在 HEAD+总闸未挂=启用态（L03 SKEL §2 实测）+回放 985 日 425,787 行 |
| load_l2_admission 消费端 | **纯库挂机** | L03 SKEL §2④ grep 实证全仓零消费方；**daily_gate_snapshot HEAD :156-162 仍 v1 absent stub**（今日 grep 实锚 :44/:50/:100 absent 契约注释+"admission_gate 放行判定不激活（三原料判定归 G05 选股引擎）"） |
| 轮动序列 B4 族 | **半接线** | 唯一生产消费=boundary_revision_engine 电风扇降档；sector_rotation_score_mapping sector_overlay_active=False 不参与打分 |
| L2-05 水温总开关 | **缺件** | module_ref=null+red_reason=pending_gate（今日实锚）；响应面在 05-2 sector_gate 有 |
| 传导 L2-06 | **纯库挂机** | sector_conduction 仅 __init__ 导出面无生产调用方（L04 SKEL W0④ coverage-audit 同判） |

**骨架勘误（登记待 D 线）**：
1. **节点计数漂移**：f39 册头称"共 32 节点"、§四称"30 节点+1 共享"，今日机数=29（yaml:545-1393 含 gate）。差异或因共享挂载/组口径，亲核后以机数为准修正册面（文档矛盾=事故，宪法 §4.3）。
2. **L2 门"恒 not_evaluated"表述过时**：L03 SKEL §12 已改判"HEAD=v1 absent stub（not_evaluated 版从未进 git）"，f39 册 §五沿用旧口径"如实三态不伪造"——结论一致但态名应统一为 absent stub。
3. **L04 板块→个股传导缺口（wiring_gap_inventory §1.2"跨 F39/F40 无线"，登记本卷+F40 卷）**：L2-06 传导乘数（10→+15%/6→+5%/<6→−10%）+三级放行门槛+龙头定位两字段，TDM 声明喂 L3-07-1 打板链，但码面 sector_conduction 无生产调用方、两字段无落库载体（L04 SKEL W0③⑥+W7）、L2 门三原料判定归 G05 而 G05 未激活——传导线在设计上跨 F39/F40 而接线为三处纯库/悬空叠加。处置=L04 SKEL L04-C01/C02（池持久化+通电）+L04-C08（传导两字段接线核验），本卷只登记不重立。

## 四、缺口清单（处置+优先级）

| # | 缺口 | 处置 | 级 |
|---|---|---|---|
| G39-1 | L2 门消费端 v1 absent stub | L03-C02 两步：水位桥方案甲（Owner 已批）+batch2 五行补丁；前置核水位桥 WIP 容器（secbuild 分支）防双落 | **P0** |
| G39-2 | L2-05 module_ref=null pending_gate | 最小施工=sector_gate 增放行比例查表行（半天）或降格语义并入 05-2 改图注（D 裁定先行） | P1 |
| G39-3 | L2-08 四段生命周期判据-码面差异 | a) 码面补四段分级函数或 b) 改判据走 S4 场景（D 裁定+台账留痕） | P1 |
| G39-4 | 29 件验证全 untested plan=None | sensor_monotonicity 批量冻结阈值（1-2 天） | P1 |
| G39-5 | L2-03 量能缩量维缺 | 补量能维（0.5 天纯函数） | P2 |
| G39-6 | 节点计数 32/30/29 漂移（勘误 1） | D 线亲核后统一口径 | P2 |
| G39-7 | S10 NO_EDGE 动量主判失效（L03 SKEL LK-03） | L03-C06 v2 考试卡实跑（卡已冻结） | P1 |

## 五、自审闸三态

**挖干可施工**（供料端全绿实证+实件零缺；四处判据-码面/接线差异已列修法；传导线缺口按 L04 SKEL 账本引用不重立）。

### 待裁
- L2-05 处置路径 a/b、L2-08 处置路径 a/b——均 D 裁定场景，本卷不代裁。
- 水位桥 WIP 容器定位（secbuild 分支 f44c1bfd742）——施工前置核实项。

## 六、复跑命令

```bash
sed -n '40,78p' src/zephyr/signal_ashare/sector/sector_rrg.py            # 四象限
sed -n '988,1013p' config/trading_decision_map.yaml                      # L2-05 null+pending_gate
grep -c "node_id: TDM-E-L2" config/trading_decision_map.yaml             # =29（勘误基准）
grep -n "admission_gate 放行判定不激活" src/zephyr/strategy_pipeline/daily_gate_snapshot.py
grep -n "sector_close_final\|sector_pre_open" src/zephyr/data/config/schedule.yaml  # :258/:263
grep -rln "sector_conduction" src/zephyr --include="*.py" | grep -v __pycache__     # 传导消费方清点
```
