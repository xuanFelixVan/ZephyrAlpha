---
ttl: task_bound
volume: 05_cost_gates
session: st-commitspeed-tbl-20260924
---

# 05 · 成本门（考尺三道门/哑门病史/成本两真相）

## 一、环节定义与边界
成本焊进考尺的判定域：五档滑点扫描（0/5/10/20/40bp）+三道门判定（档位单调性/全成本档存活/E7 换手上限）+预注册参数面。上游=_c4_engine.daily_net_returns（slippage_bp kwarg 档覆盖，引擎口径唯一）；下游=f06_e4_wfa_exam（E4 正考）/exam_cost_reexam（存活池重过）/批F 三路搜索轨（GPU）。

## 二、六向台账

| 向 | 内容（证据） |
|---|---|
| 上游输入 | config/exam_scale_cost_gate.yaml（tiers_bp=[0,5,10,20,40]/survival_floor=0.0/monotonic_tol=1e-9/min_days=60/turnover cap 8x·244 日）；净值档位序列由调用方注入（纯函数零 IO 零重跑） |
| 下游消费 | scripts/backtest/f06_e4_wfa_exam.py+exam_cost_reexam.py（exam_cost_gate.py 头 CONSUMERS 实锚）+factory_grid_executor（04 册 4.2）；成本合格名单→E4 存活池 |
| 自动化触发 | imported 库件（无自有触发）；随考试批次/搜索轨调用 |
| 真源与注册表 | MOD-BT-IBT-COSTGATE；冻结纪律="调整=裁定通道（§5 人机门位）"（yaml 头注）；DEFAULT_* 常量与 yaml 双头但"禁双头改"注记钉真源=yaml |
| 门禁与质量尺 | tests/backtest/test_exam_cost_gate.py+test_cost_gate_tier_wiring.py+test_factory_grid_stage_cost_tiers.py；fail-closed 全程：证据缺失（档位<3/天数<min_days）判不通过非跳过；裁定#325 口径=逐条如实 PASS/FAIL 禁"全绿"表述 |
| 当前运行状态 | **绿**（哑门病史已闭，见堵点1）；但"成本两真相分裂"未闭（堵点2，待裁） |

## 三、子模块清单（7 子环节）

| # | 子环节 | 入口 file:line | 状态 |
|---|---|---|---|
| 5.1 | 判定核心三道门：①五档单调非增（tol 1e-9）②最高档 sharpe>=survival_floor（照妖镜：4440 超短频繁交易必须被拦）③年化单边换手<=8x（推导：38.6pct/4.75 年÷39x，8x→拖累≈1.7pct/年） | src/zephyr/backtest/regime_validation/exam_cost_gate.py:38-52（常量），:17-32（INVARIANTS） | 绿 |
| 5.2 | 判定/扫描分离（2026-09-24 方案①）：run_cost_tier_scan tiers_bp 子集覆盖仅供 T1 轻档粗筛（validate_scan_tiers 两档合法），三门判定仍恒全档证据（<3 档 fail-closed 不通过） | exam_cost_gate.py INVARIANTS 尾段+__all__:54-60 | 绿（粗筛不放水语义在） |
| 5.3 | 预注册参数面 yaml（Owner 通宵令批C，冻结后禁改） | config/exam_scale_cost_gate.yaml 全文（本车道实读） | 绿 |
| 5.4 | E7 换手门实测战绩：T0 200 格上 8x 线 0/200 触发；惩罚强度跨 20 倍带排秩稳定（Spearman 0.9998~1.0000，top50 50/50） | e2e_integration/LEDGER.md:136 | 绿 |
| 5.5 | 轻档/全档对拍红蓝载体 | scripts/backtest/calibrate_cost_tier_redblue.py（03_gpu_campaign §三4 指名消费） | 绿（载体在；下窗方案①跑批时用） |
| 5.6 | 存活池重考（批D 新鲜窗）：exam_cost_reexam 消费门在 | scripts/backtest/exam_cost_reexam.py（exam_cost_gate CONSUMERS 第二项） | **黄**：批D 产物仓内未见（IBT-F01），重考未完成——GPU 搜索的池基悬空 |
| 5.7 | 成本口径标准族：CST-ASTOCK-001（回测实盘档）/CST-T0-001（做T 31.2bp 往返；转债/跨境 ETF 无印花 1-8bp）；冻结土规=佣金 2.5bp 双边+印花 10bp 卖+滑点 5bp | T0_SCHEME_MATRIX.md 判定口径节；prereg objective.cost_caliber | 绿 |

## 四、堵点与病灶
1. **哑门病史（已闭，防复发登记）**：prereg pass_criteria 曾"全仓 0 消费"（w3_w5_precheck §2.2 缺口原文）——判据写了没人读=哑门；09-24 哑门三修批 A 落地→00:43 被 k4 池化终批以陈旧快照吞并（exam_cost_gate.py -194/exam_cost_reexam.py -208/exam_scale_cost_gate.yaml -29）→复活批 q-0006 再落地。**闭环验证**：现 CONSUMERS 面+executor 档位扫描接线（factory_grid_executor.py:799-812）+三测试件全在码。教训：修真批落地必须 git log --name-only 对账（提交链战役同类课题）。
2. **成本两真相分裂（IBT-D01，待裁）**：同一策略考尺口径 5bp 平面 vs ADV 分层标定两套数字并存——GPU 搜出来的"成本后 Sharpe"与整装回测引擎成本口径不同源，毕业生到 IBT 复考时会换尺。已入 pending_rulings（建议：毕业生复考强制双口径出证）。
3. **E4 存活 17 vs 修后成本合格 3（IBT-B04）**：修后合格名单未落主区——搜索轨起步池用哪份无裁定。同上入 pending_rulings（与 IBT-F01 批D 重考同案：池基悬空三症状一体）。
4. yaml DEFAULT 双头（真源注记=yaml）——机械判定禁凭记忆的 SSOT 铁律下，常量层与 yaml 层漂移无对账测试。修法：加 config↔常量一致性断言测试。XS。

## 五、提速与合并机会
- 5.5 对拍红蓝+5.6 存活池重考+f06 考试三件可编排为"考后一链"（GPU 完赛事件触发：T2 晋级→考试→成本门→DSR 记账一次跑完，IBT-E07 缺口同解）。
- exam_scale_cost_gate.yaml 与 search_space_prereg.yaml 的 cost_gate 节重复（后者注"真源=前者禁双头改"）——已用注记收敛，进一步可让 prereg 加载时直接内联校验 yaml sha256（防双头漂移）。

## 六、自审闸三态
**挖干可施工**（7 子环节全实证；哑门闭环有今昔对比证据）。堵点 2/3 待裁，4 可施工。

## 七、复核命令
```bash
sed -n '1,60p' src/zephyr/backtest/regime_validation/exam_cost_gate.py
cat config/exam_scale_cost_gate.yaml
sed -n '797,812p' scripts/backtest/factory_grid_executor.py
grep -n "哑门三修\|复活批" docs/_working/e2e_integration/LEDGER.md | head -5
ls tests/backtest/test_exam_cost_gate.py tests/backtest/test_cost_gate_tier_wiring.py
```
