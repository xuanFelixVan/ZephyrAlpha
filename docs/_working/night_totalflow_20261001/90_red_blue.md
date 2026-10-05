---
ttl: task_bound
---

# 90 红蓝对抗剧本与执行记录（night_totalflow_20261001）

## 执行记录（10-01 凌晨）

- **R1 PASS**（L-D）：Memory 引擎等价注入 NULL list_date → valid_from=2000-01-01；生产四表 system.columns 新 DEFAULT 复读生效。
- **R2 PASS**（L-A 真值保护）：--date 20260909（含 295,983 行 tdx 真值）→ 干净 ABORT 拒写。
- **R6 PASS**（tick 防重灌）：0929 驱动重跑 todo=0/8119 全跳过/rows=0/计数 28,423,987 不变。
- **R7 PASS**（auction 幂等）：0929 derive 重跑 → FINAL 读数 5,572 精确复原（物理 11,144=合并前瞬态）。
- **R8 PASS**（品类真源）：TableRegistry 读 market_sector_kline_intraday 正确；未知 key fail-closed。
- **R5 改判 HOLD**（TI 幂等）：两轮校准 FAIL=计算核 09-19 后语义漂移实证（B_mine §七）——盲重跑风险>收益，回填 HOLD+结构性修复卡归 Owner 门位批；校准污染已清（FINAL 40 键复原）。
- **R3/R4 顺延**：cffex 死信归零（10-02 18:06 后验）与队列杀袋（G2 修落地后验）=时点依赖终验，移交晨检。

## 判收

R1/R2/R6/R7/R8 全 PASS + R5 HOLD 有据 + R3/R4 时点终验移交 → 本节闭环。
