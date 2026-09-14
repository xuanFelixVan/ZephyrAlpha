---
blueprint_id: MOD-SIG-149
module_name: pattern_lifecycle
domain: D_ASHARE_SIGNAL
doc_type: blueprint
ttl: permanent
design_maturity: design
stability: evolving
safety_level: L
ai_autonomy: ai_modifiable
version: "0.1.0"
created: 2026-09-15
last_updated: 2026-09-15
owner: ZephyrAlpha-Owner
---

# MOD-SIG-149 pattern_lifecycle 蓝图

> 设计真源：复活观察机制方案 v1.0（docs/_working/pattern_line/
> resurrection-watch-plan.md）。148 三态之上的生命周期覆盖层。

## 0. 文件清单

| 文件 | 说明 |
|------|------|
| src/zephyr/signal_ashare/strategy_signal/pattern_lifecycle.py | 退役计数/死亡快照/复活闸/尝试预算 |
| tests/signal_ashare/strategy_signal/test_pattern_lifecycle.py | 合成 45 窗全循环单测 |

## 1. 状态机与阈值（预注册）

failed 连续 **RETIRED_AFTER=20** 物化窗 → retired（死亡快照：
retired_at/n/hit_rate/baseline/reason=statistical|structural）；
retired → 死后增量（新事件≥50）单侧二项检验 **p<0.01**（第二次尝试 0.005）
→ resurrected；再失败满 **2** 次 → frozen（Owner 门位解冻）。
谱系：O'Brien-Fleming 1979/Lan-DeMets 1993 序贯 α 消耗。

## 2. 不变式

1. retired/resurrected/frozen 为覆盖态：每日三态不穿过（单写手，分支互斥必 continue）；
2. structural 死因冻结自动复活（Owner 门位专属）；
3. 复活判据用死后增量（死亡快照对照原点），不用全历史；
4. 台账 JSON safe_write CAS，tmp_path 注入测试。

## 3. 边界

不删目录条目；不跑独立任务（随 148 certify 同进程）；structural 复活不做自动化。
