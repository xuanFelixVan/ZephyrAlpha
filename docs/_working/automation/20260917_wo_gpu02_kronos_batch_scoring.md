---
ttl: task_bound
completes_when: 全市场日线批量打分夜窗上线且预测落表，或本工单被否决归档
---

# 工单 GPU-02：Kronos 批量推理打分（常驻 GPU 工种）

> 状态：NEEDS-ADAPTER｜风险：中高（涉新表+信号消费门）｜前置：施工队收工（scripts/backtest）
> 使命来源：docs/_working/automation/20260917_automation_linkage_plan_v1.md §2-Q2 路 b

## 1. 就绪度证据（探查裁定）

- 适配器在位：`scripts/backtest/kronos_adapter.py`（MOD-BT-195，504 行）——`--symbols/--top-n` 多标的窗模式可跑全市场日线，**但属 walk-forward 评估型**：预测被立即对标签计分，输出仅 `print(json)`。
- 微调链在位且 E2E 已通：`kronos_finetune_prep.py`+`kronos_finetune_pkl_prep.py`（QlibDataset→日线适配层**已完成**，docs/_working/factory/kronos_finetune_e2e_evidence.md：16948/4365 窗全载、GPU 峰值 ~7G、torchrun 坏→单卡 launcher 兜底）。
- 缺件三件：①推理-only 前瞻模式（无标签 T+1 预测）②预测落表（table_registry 无 kronos 表、无写入方）③消费闸（`src/zephyr/signal_ashare/ml_forecast/kronos_tsfm_predictor.py` MOD-SIG-050 是显式占位 baseline，真消费属 B-007）。

## 2. 施工步骤

1. `kronos_adapter.py` 加 `--score-only` 模式：全 universe 日线→逐标的 T+1 前瞻预测（分布参数+点估计），**不碰评估代码路径**。
2. 新表 `kronos_prediction_daily`（DDL 走 apply_market_tables_ddl 真源；DateTime64(3)+显式时区；PIT 字段：预测时点/数据截止/barre 截面）；写入方走 DatabaseService（禁裸 duckdb）。
3. 夜窗任务 register_kronos_scoring_task.ps1（cron 00:30 周日~周四，gpu_default 组）；注册表再生挂互斥。
4. 消费侧**不接线**：预测表只落不用，`kronos_tsfm_predictor` 转正另走 B-007 申请（附本表 4 周样本质量报告）。

## 3. 验收标准

- [ ] score-only 模式全市场（~5000 标的）单夜跑完，GPU 峰值≤8G（gpu_default 预算内）
- [ ] 预测表 PIT 口径过 RULE-SCHEMA-TZ 检查；写入方过 LSG/DatabaseService 红线
- [ ] 注册表实体 sch_kronos_scoring 生成且冲突闸对 Ollama 大模型档互斥生效
- [ ] 4 周预测留存后出质量报告（IC/分位胜率），供 B-007 消费门评审

## 4. 红线

- 现货评估通道（walk_forward_eval/distribution_forecast_eval）行为零变更。
- 表净增=架构数据走 apply_*.py 直写 DB（RULE-SSOT）。
