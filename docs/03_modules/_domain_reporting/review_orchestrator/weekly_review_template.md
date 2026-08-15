---
doc_type: blueprint
ttl: permanent
title: 周复盘四段式模板（人工维护资产，MOD-RPT-009）
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "1.0.0"
date: 2026-08-15
---

# 周复盘 <period>

> 模板性质：人工维护资产（55 号 §3.6 决策五 + §6 暂缓项——先人工维护，跑 12 期稳定后再固化模板引擎）。
> doc_type 取 blueprint 系 03_modules 目录契约（allowed_doc_types）合规 + 词表「cookbook template 取目标文档类型」口径；本文档是 MOD-RPT-009 的模板资产。
> 结构固定四段（决策内容不可增删）；内容由 MOD-RPT-009 ReviewOrchestrator.run_weekly 自动装配，人只读 + 补第 ④ 段裁定。
> 风险概览：日均评分 <avg_risk_score> / 最大回撤 <max_drawdown> / 告警 <alert_total> 条 / 趋势 <trend_direction>

## 1. 本周盈亏与归因

<54 号对账归因链路供给：本周盈亏 + 因子/策略归因分解。人读确认归因是否可解释（54 号裁定：归因清晰度是生存项）。>

## 2. 偏离与告警事件

<MOD-RK-23 偏离快照表：| 策略 | 偏离度 | 日收益相关 | 动作 |；>30% 告警 / >50% 退役评估；相关破下限标注。>
<本周告警事件清单：RED/ORANGE 逐条 + 认领情况。>

## 3. 阈值与参数变更

<本周阈值/参数变更清单——阈值唯一真源 alert_threshold_registry.yaml（55 号 §3.3：阈值不集中即不可审计，本节=个人系统唯一的风控评审点）。>

## 4. 下周 action items

<本周复盘产出的行动项，逐条 checkbox；经 action_item_sink 进 IncidentManager/候选库跟踪闭环。>
