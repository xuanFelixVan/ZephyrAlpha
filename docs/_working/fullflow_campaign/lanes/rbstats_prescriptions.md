---
ttl: task_bound
completes_when: 本文件六条处方各自被 owner 车道或总包闭环
---

# 红队车道 rb-stats · 处方（撞他人独占面/需门位者，一律不代修）

> 车道 `st-ff-rb-stats-20260918`（攻面=过拟合 + regime 误报率）。
> 每条给：file:line + 改法 + 验收判据 + 复现命令。实测值均为本轮亲跑。

---

## P-1 【landA 独占面 `src/zephyr/pf_alloc/**`】Shrinkage 链存在两套互不相同的实现

**实测**（本轮探针，非推断）：同一个 `max(P)` 输入，两套档位表给出不同 ConfidenceSignal：

| 真源 | 表 | max(P)=0.25 | max(P)=0.80 |
|---|---|---|---|
| `src/zephyr/regime/core/regime_detector.py:192-197` `_CONFIDENCE_BANDS`（降序取下界）× `:199` `_RARITY_BANDS` | 0.50→1.0 / 0.30→0.9 / 0.15→0.8 / 0.0→0.7 | **0.80** | **1.00** |
| `src/zephyr/pf_alloc/core/regime_meta_allocator.py:94-99` `CONFIDENCE_THRESHOLDS`（升序取上界） | 0.60→0.30 / 0.80→0.60 / 0.95→0.85 / 1.01→1.00 | **0.30** | **0.85** |

（上表右侧四格为本轮亲跑数值：`RegimeDetector._compute_confidence_signal` vs
`RegimeMetaAllocator._compute_confidence_signal`，同一概率向量。）

- **谁在用哪套**：回测侧 `src/zephyr/backtest/regime_validation/shrinkage_provider.py:148`
  走 `detector.detect()`（检测器档）；实盘分配侧 `src/zephyr/pf_alloc/allocation_orchestrator.py:840`
  走 `meta_allocator.allocate(...)`（分配器档，ConfidenceSignal 自算，只复用检测器的 risk_signal 一个数）。
- 后果：**回测↔实盘的节流系数不同构**，max(P)=0.25（HMM 退化/均匀分布的常态档位）时
  **差 2.67 倍**，且方向是**实盘比回测收缩更狠** → 回测**高估**可得敞口。
- 分叉有明文出处：检测器表头注（`regime_detector.py:183-190`）记
  "C1 验证 2026-08-06 校准：原阈值 0.95/0.80/0.60 对 HMM 过高…致平时过度收缩"并给出
  ⚠️"当前阈值沿用 9 态校准值，步骤8 C1 验证后根据 4 态 max(P) 分布精调"；
  分配器表（`regime_meta_allocator.py:92-99`）用的正是被检测器侧判过高的那一族阈值，
  其理由改为外部印证（`regime_meta_allocator.py:460` "1uptick 2026-06 机构方案 max(P)<60% 减仓 30-50%"）。
  **两边各自有据、无人对账**，这才是本处方的核心，不是"谁写错了"。
- 附带：`regime_meta_allocator.py:470-485` 的 `_compute_risk_signal` 头注释自称"**本函数是占位接口**"
  （`:478`），但它就在钱路上（`allocation_orchestrator.py:842` 每调必过）。

**改法建议**：仿 `decision_gate.py` 的"单一判定源"先例（其 INVARIANTS 明文"禁两轨各算各的"），
把 ConfidenceSignal/RiskSignal 的档位表与聚合函数收敛到 `MOD-REGIME-001` 一处，
`pf_alloc` 侧只消费不重算；两套表若须并存（D1 ±20% 敏感性扰动要覆盖 `confidence_thresholds` 入参），
则必须加"默认档表 == 检测器档表"的字节级一致性测试。

**验收判据**：
1. `RegimeMetaAllocator.CONFIDENCE_THRESHOLDS` 与 `RegimeDetector._CONFIDENCE_BANDS` 存在机器可判的等价关系
   （同值，或有显式换算注记 + 换算测试）；
2. 交叉喂参必须**抛错**而非静默落 1.0（见 P-1b）。

**复现命令**：
```bash
PYTHONPATH=src python -c "
import datetime
from zephyr.regime.core.regime_detector import RegimeDetector, RegimeProbabilities
from zephyr.pf_alloc.core.regime_meta_allocator import RegimeMetaAllocator
d, a = RegimeDetector(), RegimeMetaAllocator()
for mp in (0.25, 0.80):
    pr = RegimeProbabilities(probabilities={}, hmm_probabilities={}, overlay_probabilities={},
        dominant_regime='r1', dominant_frequency=1.0, confidence=mp, timestamp=datetime.datetime(2026,1,1))
    vec = [mp, (1-mp)/3, (1-mp)/3, (1-mp)/3, 0, 0, 0]
    print('maxP', mp, 'detector=', round(d._compute_confidence_signal(pr),4),
                    'allocator=', round(a._compute_confidence_signal(vec),4))"
```
输出（本轮实测）：`maxP 0.25 detector= 0.8 allocator= 0.3` / `maxP 0.8 detector= 1.0 allocator= 0.85`

### P-1b 两套 `_compute_risk_signal` 入参 schema 互不兼容，且交叉喂参都落"最宽松值 1.0"

实测（本轮探针 `schema_crossfire`）：

| 喂法 | 结果 |
|---|---|
| 检测器原生形 `{"params":{1:0.35,...}}` → 分配器 | **1.0**（静默零节流） |
| 分配器原生形 `{"risk_base":0.35,...}` → 检测器 | **1.0**（`params` 取不到 → 降级分支） |
| 各自原生形 | 0.30 / 0.35（正确） |

即：**一次跨模块重构就能把危机节流悄悄调成 1.0，不报错、不写日志、不留痕。**
改法=两函数入口做 schema 断言（未知键/缺键即 `raise`），或按 P-1 合并为单一判定源。
验收判据=上述前两行必须抛错。

---

## P-2 【需总包/Owner 门位】regime 断供 fail-open 的**数值侧**未动（本车道只补了可观测性）

**实测**（S1 危机信号满格触发时，只断掉 RiskSignal 一条腿）：

| 场景 | r10 危机概率 | dominant | RiskSignal | Shrinkage |
|---|---|---|---|---|
| 危机 + 有供数 | 0.800 | r10 | 0.30 | **0.255** |
| 危机 + 断供 `{}` | **0.000** | **r1（低波震荡）** | 1.0 | **0.800** |
| 断供 `None` / `{"params":{}}` / 缺 #1 | 同上逐位相同 | r1 | 1.0 | 0.800 |

**危机中断供 = 节流松绑 3.14 倍**（`0.800/0.255`）。机制：`regime_detector.py:599-600` 的
`if _primary_risk_coef(risk_signal_inputs) >= 1.0: overlay_probs = 0`
——主腿没数被读成"主腿说没风险"，于是覆盖层危机概率被门清零。
与 R-K9（断供须 fail-closed 禁交易）方向相反。

**本车道已做**（零数值改动，故未越门位）：`missing_risk_legs()` +
`ShrinkageResult.degraded_legs` + WARNING 出声，使断供**可被机械检出**——
这是 R-K9 能被执行的**前提**，但本身不是执行。

**请总包裁/派**：把 `degraded_legs` 非空接成 `crisis_gate` / 分配链的一条独立失效腿
（禁在 `degraded_legs` 非空时放量）。**未做的理由**：改档位数值会动 C1/B 系列已验证的历史口径，
属"生产流转"（宪法 §5 high 域门位），红队车道不自签。
附注：`pf_alloc` 侧 `resolve_risk_signal`（`allocation_inputs.py:426-455`）**已是 fail-closed**
（无教材→risk=1.0 **且**概率平坦→conf 落最低档→总节流 0.30，并带 `risk_signal_source` 溯源标签），
是本役少见的正确降级设计，检测器侧应向它对齐。

---

## P-3 【regime 误报率无机械载体】B4 只算"命中"，不算"误报"

- `src/zephyr/regime/validation/phase2/b4_transition_accuracy.py` 判据
  "事件日 ±5 交易日内查找对应 transition 触发 → 命中；≥6/8 PASS" = **recall/敏感度**。
- **没有 precision 侧**：触发了但窗口内**无**对应事件的次数（=误报）不在统计里。
  故"regime 误报率很低"目前**无载体可算**，属散文。
- 雪上加霜：`src/zephyr/regime/validation/**` 在 `src/` 内**零消费者**（`git grep` 只见自身与
  `wyckoff_walkforward.py`），消费方全在 `scripts/tests/run_phase2_validation.py` —
  按 ORPHAN-MODULE 口径（只 `git grep src/**/*.py`）= 孤儿，且**无自动触发**（四要素缺三）。
- **改法**（择一，需先解决 owner 归属：regime 域未被 §2 独占地图划出）：
  1. B4 加 precision 侧：对每个 stage 触发计 `(触发日, 窗口内有事件=TP / 无事件=FP)`，
     输出 `false_alarm_rate = FP/(TP+FP)` 落 YAML 台账，并配哨兵阈值行；
  2. 分母必须**剔除 `degraded_legs` 非空的交易日**（否则 P-2 的断供日会被记成"没触发=对"，
     把误报率算小——这是本处方与 P-2 的硬耦合，勿拆开做）。
- 本轮一次性实测件（未永久化）：`.runtime/tmp/st-ff-rb-stats-20260918/regime_failopen_probe.py`
  （P-2 表格的数字来源）。

---

## P-4 【BRK-045 复测：未修，实测仍在】回测产物归因维度不可用

```bash
python -c "
from pathlib import Path; import json,collections
f=[p for p in Path('.').rglob('bt-*.json') if not ({'.aidrafts','.worktrees','.runtime'} & set(p.parts))]
v=collections.Counter(); a=0
for p in f:
  d=json.loads(p.read_text(encoding='utf-8'))
  stack=[d]
  while stack:
    o=stack.pop()
    if isinstance(o,dict):
      for k,x in o.items():
        if k=='order_type': v[str(x)]+=1
        stack.append(x)
    elif isinstance(o,list): stack+=o
  if 'algo_id' in json.dumps(d): a+=1
print(len(f),'files; order_type:',dict(v),'; files with algo_id:',a)"
```
- 本轮实测：**60** 件 `bt-*.json`；`order_type` 出现 **1666** 次，取值分布 `{'market': 1666}`（**无一非 market**）；
  含 `algo_id` 的文件 **0** 件。
- 结论：普查记载**成立且仍未闭合**——回测只演算市价单，且无算法单身份，
  故"回测↔实盘同构"**无从验证**（不是"验了没问题"，是"没有可验的字段"）。
- owner：回测/执行域（§2 独占地图未把 `data/backtest_artifacts/**` 与 `_c4_engine` 划给本车道）。

---

## P-5 【产端档案纪律】DSR 折减分母 N_eff 的原始档案缺失

- 消费端本车道已治（RB-STATS-01：E4 对账，非 `verified` 禁判通过，见 `scripts/backtest/f06_e4_wfa_exam.py`）。
- **产端仍漏**：`scripts/backtest/factory_grid_executor.py:755-766` 落 `net_returns.parquet`，但
  `data/strategy_intake/` 28 个批次里**只有 2 个**有该档案，且都是 8 列烟测批；
  真正产生门控分母的 `grid_20260916-123551`（n_sampled=**10080**，登记 `n_trials_effective: 9`）
  **无 net_returns** → 那个"9"当前无法复算。
- 估计器本身没问题：对两个有档案的批次原地复算 `compute_effective_rank` → **5 vs 登记 5，逐位吻合**。
  所以缺的是**档案纪律**，不是算法。
- 改法：`factory_grid_executor.run_batch` 把 `net_returns.*` 列为必产工件（与 manifest.csv 同级），
  写不出去就在 `summary.json` 打 `"n_eff_archived": false` 并让普查件拒收该批；
  同批把 `n_eff_meta` 从"批内格点数"扩记"实际入矩阵的列数"（10080 格点里 `degraded_recipes=5040`，
  半数是降级件——它们进不进 N_eff 的矩阵，直接决定分母是 9 还是别的）。
- 验收判据：任一被 E4 消费的 `birth_batch` 都能被 `verify_n_trials_provenance` 判 `verified`。

---

## P-6 【外来在途红，不代修】`tests/backtest/test_sim_paper_ledger.py::test_replay_pipeline_consistent`

- 本轮实测：`tests/backtest` 目录跑出 **1 failed / 1822 passed**（382s），失败件即此。
- **已按字节 A/B 证明与本车道无关**：把 `regime_detector.py` 换回 HEAD 字节后跑同一测试
  → 同样 `1 failed`（`res["events"] == []`），换回本车道修改版 → 同样 `1 failed`。
- 首个 traceback 指向 `alerter`/`crisis_gate`：`crisis_gate.py:402 crisis_gate_log 留痕失败
  （表可能未注册 DDL，由总统筹 apply）: 'str' object has no attribute 'year'`。
- 与共享任务板上"净损失：pf_alloc L1 危机闸接线只活在冷库，须落回"同域 → **归该 owner 车道**，
  本车道不碰（§3.4 他人独占面不代修）。

---

## P-7 【考试咽喉】IS 阶段门控是"自我打分"，且选参级泄漏**无机械防护**

**实测**（本轮，脚本 `.runtime/tmp/st-ff-rb-stats-20260918/noise_red_probe.py`，E1/E2 两行）：

| 实验 | 选参用的数据段 | IS sharpe | OOS sharpe | **OOS/IS 比率** | 0.70 比率门 | E4 判定 |
|---|---|---|---|---|---|---|
| E1 诚实切分 | 仅 IS 段 | 1.976 | −0.253 | 0.000 | 否决（有效） | 不通过 |
| E2 全样本泄漏切分 | **含 OOS 段** | 0.838 | 1.936 | **2.311** | **被反向击穿** | 不通过（仅因 DSR 尚存） |

两行的输入都是**纯噪声**（真值 Sharpe=0）。E2 说明：一旦参数搜索空间跨过样本外切分，
`oos_sharpe_ratio_threshold=0.70` 这条 P0-9 硬否决线**不但失效，而且反向**——
被挑出来的噪声"样本外比样本内还好"（2.311），任何只设下界不设上界的比率门都只会加分。
E2 唯一没被判通过，是因为 DSR 那条腿还站着；而 DSR 的分母正是 E3 已证可一列改字放水的那个数。

**现行防护的真实覆盖**：
- ✅ **折级**切分有机械不变量：`f06_e4_wfa_exam.py:build_folds` 以 `ValueError` 强证
  "每折训练窗全部早于测试窗 + 测试窗互不重叠"，且存量测试
  `test_no_overlap_leakage_train_all_before_test` 能红。
- ❌ **选参级**切分无任何机械防护：E4 的 IS 阶段入参 `is_sharpe` 直接取
  `f06_survivors.csv:is_window=2020-01-01..2023-12-31`，而该配方的 10080 格点普查
  （`grid_20260916-123551/summary.json: window=[2020-01-01, 2023-12-31]`）
  用的**正是同一段窗**——即"用同一段数据既选参数又给 IS 打分"，IS 门控=自我打分。
- 现状是**散文披露**：档案"诚实边界"自陈"折 1-4 测试段与已登记 IS 窗重叠，属'选择偏内'"。
  披露真实且诚实，但**无机检、无告警、无独立 IS 窗**。

**改法（择一，属回测域/工厂车道职权，本车道未动）**：
1. 给 IS 门控换一段**未被普查选参使用**的窗口（需把普查窗与考试窗在注册层面分离）；或
2. 加机械判据：`is_window == birth_batch 的 summary.window` 时，档案强制标注
   `is_stage_self_scored=true` 且 IS 阶段不计入 `overall_passed` 的独立证据（只加严不放行方向）；或
3. 给比率门加上界："OOS/IS 异常地好"本身即泄漏签名，应触发人工复核而非加分。

**验收判据**：构造一条"在全样本上选参"的合成泄漏路径（E2 即现成夹具），
考试件必须**报红或显式标注 self_scored**，不得静默把 2.311 的比率当优质证据计入。
