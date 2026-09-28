---
ttl: task_bound
title: "F69 T0/成本门/IBT——T0 成本模型+考试成本双口径门+复权降级"
session: zc-l07-20260927
create_guard: creation_token 由落地车道随批补办（M2 车道先例）
---

# F69 · T0/成本门/IBT（总册状态 built/P2；本卷复核=门本体 built wired（GPU 判卷实战消费中），双口径分裂/池基悬空两待裁承压）

## 一、六向台账（实证锚点）

| 向 | 实证（本日实勘） |
|---|---|
| 上游输入 | 净值档位序列由调用方注入（纯函数零 IO 零重跑，M2-05 实锚）；config/exam_scale_cost_gate.yaml（tiers_bp=[0,5,10,20,40]/survival_floor=0.0/monotonic_tol=1e-9/min_days=60/turnover cap 8x·244 日——M2-05 §二实锚+本卷引用）；CST-T0-001 做T 31.2bp 往返口径（T0_SCHEME_MATRIX） |
| 下游消费 | exam_cost_gate.py 头 CONSUMERS 三路=f06_e4_wfa_exam（E4 正考）/exam_cost_reexam（存活池重过）/factory_grid_executor（T1 轻档粗筛 :797-812）；**实战新证：grid_20260926-024947 handover_verdict cost_gate_spot 五档全真跑 50 格抽样（ok=22/bad=28）=门在判卷位实战运行** |
| 自动化触发 | imported 库件（无自有触发）；随考试批次/GPU 扫描调用 |
| 真源与注册表 | 门本体=src/zephyr/backtest/regime_validation/exam_cost_gate.py（232 行实测，MOD-BT-IBT-COSTGATE）；T0 成本模型=src/zephyr/ex_sor/services/t0_cost_model.py（144 行实测，testing）；复权降级真源=sop/backtest_system_sop/exam_policy.md（**标题自含"成本双口径·复权降级·负结果台账"**，本日 sed 实测）；冻结纪律="调整=裁定通道"（yaml 头注）；DEFAULT_* 常量与 yaml 双头但注记钉真源=yaml |
| 门禁与质量尺 | 三道门=①五档单调非增（tol 1e-9）②最高档 sharpe≥survival_floor（0）③年化换手≤8x；判定/扫描分离（run_cost_tier_scan 粗筛不放水，<3 档 fail-closed）；裁定#325 口径=逐条如实 PASS/FAIL 禁"全绿"；测试=test_exam_cost_gate/test_cost_gate_tier_wiring/test_factory_grid_stage_cost_tiers 三件（M2-05 实锚） |
| 当前运行状态 | **绿（哑门病史已闭）**：09-24 哑门三修批 A→k4 池化陈旧快照吞并→复活批 q-0006 再落地（M2-05 §四1 闭环）；E7 换手门 T0 实测战绩 0/200 触发+惩罚强度排秩稳定（Spearman 0.9998）；IBT 四窗战役级完成（HOLDOUT -12.2%/-1.389 单次烧毁，M2-06） |

## 二、子模块三级枚举（成本考尺三级：门→模型→口径册；本日实扫）

- **判定门**：exam_cost_gate.py（三门+run_cost_tier_scan 扫描分离，232 行）；exam_scale_cost_gate.yaml（冻结参数面）；tests 三件
- **T0 模型面**：t0_cost_model.py（ex_sor/services，testing，零装配）；做T 矩阵判卷=T0_SCHEME_MATRIX/FINAL_REPORT（34 法三态：✅7/⏳13/⛔8/🔧6，M2-04 4.7）
- **复权降级面**：exam_policy.md（无条件证据档降级收录 :37/试验次数留痕缺原料=结论降级 :56——两级"降级"语义实测）；ch_tick_replay.py 1 档降级（2-5 档填 0 如实登记，撮合只用 bid1/ask1，:8/:54/:116）；IBT 协议复权事件在案（600016 缺+老股深史 0.2-0.4% 偏差，M2-06 堵点 6）
- **IBT 面**（协议治理整装回测，M2-06 8 子环节）：IBT-PROTOCOL-V1（frozen 2026-09-22）+ibt/四件（runner/redblue/attrib/mining_matrix）+五册真源 docs/_working/integrated_backtest/+红蓝 4 轮连续两轮 0

## 三、接线四态独立复核

| 面 | 四态判定 | 复核证据 |
|---|---|---|
| 成本门三道门 | built wired（三消费方+判卷实战） | CONSUMERS 头+本日 handover spot 抽样 50 格实测 |
| T0 成本模型 | **码在零装配（testing）** | 144 行零生产消费者（M7-05 同判）；CST-T0-001 口径靠文档面 |
| 双口径门 | built 机制/**两真相未裁** | 5bp 平面（考尺）vs ADV 分层（IBT）并存=IBT-D01/R-M2-2 Owner 待裁 |
| 复权/档位降级 | built（如实登记语义在） | exam_policy 两级降级+ch_tick_replay 1 档降级实测 |

### 骨架勘误
- 无锚点级勘误（exam_cost_gate.py 路径 regime_validation/ 实证相符）。补充：t0_cost_model 总册未列（现锚点仅 exam_cost_gate.py），建议补列并标 testing 态。

## 四、缺口清单

| # | 缺口 | 处置 | 优先 |
|---|---|---|---|
| 1 | 成本两真相分裂（IBT-D01） | Owner 裁 R-M2-2：建议毕业生复考强制双口径出证（零重跑过渡） | P1（Owner） |
| 2 | E4 存活 17 vs 修后成本合格 3+批 D 重考未完成（IBT-F01）=搜索池基悬空三症状一体 | T1 已完赛→立批 D 重考再放 T2（R-M2-3 建议①）；artifacts_v2 现仅 1 pkl（M2-06 实测） | P0 |
| 3 | cost_gate_spot 判卷口径 28/50 bad（F68 缺口 1 同源） | 复核 spot 抽样口径 vs 门本体三门语义是否同构，防判卷器自我加严 | P0 |
| 4 | yaml DEFAULT 双头漂移无对账测试 | config↔常量一致性断言测试（XS，M2-05 堵点 4） | P2 |
| 5 | T0 模型 testing 态零装配 | 标 research 域集中登记（M7-05 §五方案）；做T 真跑前勿提前激活 | P2 |

## 五、自审闸三态
**挖干可施工**（门/模型/口径/降级/IBT 五面 file:line 实证；缺口 1/2 Owner 待裁在 R-M2-2/R-M2-3 不代裁；本卷新增：handover cost_gate_spot 实战证据+F68 判卷口径交叉缺口 3）。

## 六、复跑命令
```bash
wc -l src/zephyr/backtest/regime_validation/exam_cost_gate.py src/zephyr/ex_sor/services/t0_cost_model.py   # 232/144
grep -n "CONSUMERS" src/zephyr/backtest/regime_validation/exam_cost_gate.py | head -2
head -3 docs/01_policies_and_standards/sop/backtest_system_sop/exam_policy.md   # 标题含双口径/复权降级
grep -E "cost_gate_spot" -A8 data/strategy_intake/grid_20260926-024947/handover_verdict.yaml | head -12   # 实战判卷
sed -n '38,52p' src/zephyr/backtest/regime_validation/exam_cost_gate.py   # 三门常量
ls tests/backtest/test_exam_cost_gate.py tests/backtest/test_cost_gate_tier_wiring.py
```
