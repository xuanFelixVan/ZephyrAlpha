---
title: 历史回测结果向 experiment_tracking 回灌评估
date: 2026-08-28
ttl: permanent
---

> **归档注记（2026-08-30）**：已闭环——结论"按需回灌（当前不回灌）"经复核成立，唯一候选源（c1_repro 1 批）知识已由 md 报告承载、无批量历史待回灌，roadmap A20 项勾销。commit 2a16988d。

> **文档元信息**（_working 临时区豁免规范，EXEMPT-ZONE-FM）：doc_type=report · owner=ZephyrAlpha-Owner · language=zh · status=active · version=1.0.0 · date=2026-08-28 · topic=backfill_evaluation · scope=07_trading_decision_architecture · completes_when=回灌决策执行完毕或 Owner 裁定归档（归档不删除，保留审计链）。

# 历史回测结果向 experiment_tracking 回灌评估

> **出处**：[50_backtest_observability_workplan.md](../02_enterprise_architecture/07_trading_decision_architecture/design_memos/50_backtest_observability_workplan.md) §3⑤「历史结果回灌（待评估）」+ 结案报告回填（2026-08-28 代码实证复核）登记的小型遗留；[剩余施工路线图](../_working/2026-08-28-remaining-construction-roadmap.md) A20 项。
> **性质**：纯评估文档（裁定建议），不改代码。评估人：session AI-WAVE0-001。

## 一、历史回测结果现存何处（2026-08-28 实证）

| 位置 | 内容实证 | 格式 | 回灌必要性 |
|---|---|---|---|
| `logs/c1_repro/`（11 文件） | 51 号 C1 复现批产出：`c1_metrics.json`（Shrinkage 开/关对比 4 指标：Sharpe 0.3678→0.3474 / MaxDD 0.2221→0.1485 / Calmar / Turnover + backtest_config）、`c1_repro_report.md`、`a2_a3_validation_report.md`、`basket_data_spec.json`、`deadzone_analysis_report.md`、`overlay_audit_daily.csv`、`regime_features.csv`、`shrinkage_schedule.csv(.gated)`、`repro_handoff.md` | **报告型产物**（md 报告+csv 数据+单个汇总 json），非 experiment_tracking 的 run_meta.json 跟踪型格式 | 唯一候选回灌源（仅 1 批） |
| `logs/experiment_tracking_fallback/` | 5 个 run 已在位：c1-validation×4（`1786116372_54076857`/`23e1fa7ca61f`/`48b0f874bc84`/`run-w414-demo`）+ test×1 | **原生 run_meta.json**（FallbackBackend 格式） | 无需回灌（已是目标格式） |
| `data/backtest_artifacts/`（result_repository，CTR-P1-017） | **零存量 JSON**（回测流水线尚未跑批产出 BacktestRunArtifact） | BacktestRunArtifact JSON | 无存量可回灌 |
| MLflow M1 的 2 个 smoke run | 合成数据 | — | **已裁定丢弃重跑**（51 号 §二.3），明确排除 |

## 二、回灌价值 vs 成本

**价值面**：
- `logs/c1_repro/` 是 regime 体系 C1/A2/A3 验证的历史基线证据，回灌后 Panel「实验历史」Tab（`_tab_experiment_history`）可查询到该基线 run。
- 长期看实验历史完整性（审计链连续）。

**成本面**：
- 格式归一化成本：`c1_metrics.json` 是报告型汇总（baseline/experiment 双列 4 指标），需映射为 run_meta.json（params/metrics/tags/status），双列结构压平有信息取舍。
- 有效存量仅 **1 批**（非时间序列）——实验跟踪的核心价值是"可查询的指标序列对比"，单批历史无序列价值；其知识价值已由 `c1_repro_report.md` / `a2_a3_validation_report.md` 报告型存档承载。
- 回灌 run 混入真实实验流需打 `backfill` tag 区分（50 号 §3 表格已预留该设计），否则污染实验统计口径。
- 项目先例口径：51 号对低价值历史 run（M1 smoke）裁定**丢弃重跑**而非保留——宁缺毋滥。

## 三、结论建议：**按需回灌（当前不回灌）**

理由：
1. 当前唯一候选源（c1_repro 1 批）的知识已由 md 报告承载，回灌仅增加 Panel 一行记录，边际价值低；
2. experiment_tracking 既有 5 个 run 已是原生格式，无历史积压；
3. 回测跑批（路线图 B 类触发链）尚未启动，`data/backtest_artifacts/` 零存量——**无批量历史等待回灌**；
4. 与 51 号"低价值 run 丢弃"裁定口径一致，避免为回灌而回灌。

## 四、触发条件与实现要点（若未来回灌）

**触发条件**（任一命中即启动回灌施工）：
- 回测跑批启动后产生 ≥10 个非原生格式历史 run 存量；
- Owner 要求实验历史完整性审计（审计链需覆盖跑批前历史）。

**实现要点**：
- 一次性脚本（如 `scripts/backfill_experiment_tracking.py`，非新建常驻系统）：扫描源目录 → 归一化映射（`passed`→`metrics.passed`、四指标→`metrics`、`backtest_config`→`params`、批次打 `tags: {backfill: "true", source: "c1_repro"}`）→ 写 `logs/experiment_tracking_fallback/{component}/{run_id}/run_meta.json`；
- 幂等（目标 run_id 已存在则跳过）；默认 dry-run，`--apply` 才落盘；
- 回灌后跑 `tests/experiment_tracking/` 全量 + Panel「实验历史」Tab 目检。
