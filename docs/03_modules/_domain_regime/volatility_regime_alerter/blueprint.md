---
module_id: MOD-REGIME-011
title: "波动率体制转换与关键时点预警蓝图 — GARCH(1,1) 波动预测+RV 压缩标记+突变告警"
doc_type: blueprint
status: Active
version: "0.1.2"
ttl: permanent
layer: L2_domain
layer_name: regime
functional_domain: regime
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-08-25"
last_updated: "2026-08-25"
priority: P0
blueprint_level: module
design_maturity: production
build_status: production
responsibility_domain: 
---

# MOD-REGIME-011 波动率体制转换与关键时点预警 蓝图

> **module_id**: MOD-REGIME-011 | **域**: D_REGIME | **层**: L2 业务域
> **优先级**: P0 | **来源**: CAND-CYCLE-003（B10-01358，AUD-DRAFT-001 裁定=做）
> **SSoT**: depgraph MOD-REGIME-011
> **号段说明**: MOD-REGIME-009/010 已被 2026-08-24 design_memos 施工清单（P1-E9）预留，本模块顺延 011。

## 1. 定位

A1 交易决策架构 §3 模块2。场内现状（TSV 对账）：HMM 体制识别已有
（MOD-REGIME-001 production），**GARCH(1,1) 波动预测 + RV 压缩检测 + 突变预警
为 regime 命门缺口**。本模块补该缺口并产出 overlay 消费契约。

排雷裁定（W3）：TSV 依赖栏写"arch 库"，但项目既有裁定=**自研 L-BFGS-B 高斯
QMLE，不引 arch 库**（AI-FHS-001 #1，MOD-RK-26 fhs_engine 先例）。本模块直接
复用 `FHSEngine` 的 GARCH(1,1) 拟合（`garch_params.sigma_forecast`），零新依赖。

## 2. 输入 / 输出

- 输入：日频收益序列（np.ndarray，建议 ≥60 样本激活 GARCH；≥30 兜底 RV 维度）。
- 输出 `VolRegimeSignal`：
  - `rv_ratio`（RV_5d/RV_20d 年化波动比）+ `compression_flag`（<0.8 压缩早标记；
    <0.5 强压缩归模块51 B10-01387 联动）；
  - `sigma_forecast_annualized`（GARCH 次日条件波动预测，年化）；
  - `shift_ratio`（sigma_forecast/RV_20d）+ 突变告警（≥1.5）；
  - `overlay_dims()`：**接 overlay_signals_builder 的消费契约**——
    `{"vol_compression": flag, "vol_shift_alert": flag, "vol_forecast_score": [0,100]}`，
    对齐 overlay 不变式（score∈[0,100]/flag∈{0,1}/无信号=0 平时不干预）。

## 3. 核心规则

1. GARCH 自研复用：FHSEngine(L-BFGS-B QMLE，fallback_to_historical=True) →
   回读 `garch_converged`/`garch_params`；不收敛 → vol_forecast 维度降级 0 +
   `garch_available=False`（对齐 FHS 回退哲学，不抛错）。
2. RV 压缩标记独立于 GARCH（只要 ≥rv_long_window 样本即可用）。
3. 突变告警线 shift_ratio≥1.5；`vol_forecast_score` 按 1.0→0 分/阈值→100 分
   线性映射截断。
4. 降级哲学（对齐 MOD-REGIME-002）：样本不足/非有限值/GARCH 不收敛 →
   维度=0 不抛错；仅配置非法 Fail-Closed（VolatilityAlerterConfigError）。
5. 错误码未登记（申请中，W3 fragment 补登草稿）。

## 4. 依赖

- `zephyr.risk.core.fhs_engine`（MOD-RK-26，GARCH(1,1) 自研实现复用）；
- numpy；
- 设计态契约：MOD-REGIME-002 overlay_signals_builder（overlay_dims 消费，
  运行时装配批接线，本批不改 production 代码）。

## 5. 测试

- `tests/regime/test_volatility_regime_alerter.py`（10 测：不引 arch 库断言/
  压缩标记/突变告警/overlay 契约/降级不抛错/配置 Fail-Closed）。

## 6. 依据

- construction_backlog_dig.tsv B10-01358（A1 §3 模块2，裁定=做 P0）；
- CAND-CYCLE-003（candidate_module_registry.yaml）；
- AI-FHS-001 #1（GARCH 自研裁定）；MOD-RK-26 fhs_engine。

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-REGIME-011`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-REGIME-011` 的 2 个 file 节点 | production | `extract_depgraph.py --modules MOD-REGIME-011` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | active | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-REGIME-011 | MOD-REGIME-011 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | production | production | ✅ |
| file_count | 2 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## 7. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 7.1 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/regime/test_volatility_regime_alerter.py` | ✅ 已实现 | |

### 7.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §7（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于 `D:\ZephyrAlpha\\`
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下


