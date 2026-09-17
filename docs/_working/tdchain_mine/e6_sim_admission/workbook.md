---
ttl: task_bound
title: E6 模拟盘准入判据作业簿——E6 双尺重考取证+STD-SIM-ACCESS-002 转正
session: st-tdchain-20260917
date: 2026-09-18
parent: docs/_working/tdchain_mine/a0_master_ledger.md
---

# E6 模拟盘准入判据作业簿

## 六向台账

- **目标**：交接令任务 5（组合门替代单一 Sharpe 2 硬门的判据草案）。侦察结论：**判据本体已存在**——config/standards.yaml STD-SIM-ACCESS-002（draft，S5 定尺：OOS Sharpe≥1.5+回撤≤15%+DSR>0.5（N=预注册族 N_eff）+三腿 ρ̄≤0.7/容量证明/换手上限 12x）；v1 尺 STD-SIM-ACCESS-001 已标 suspect（#306：DSR>0 在累计 N=4562 口径下需年化 SR≥2.68，与 1.5 数学互斥=不可过）。剩余缺口=转正前置证据链核实（E6 双尺重考）+flip frozen+登记裁定。
- **证据**：
  - 转正前置（standards.yaml change_rule）：draft→frozen 须附全量在架组合新旧尺重考报告+翻转清单复核。
  - experiments_ledger.md:44："E6 双尺零不可解释翻转 采纳 f6549823"——重考疑似已完成，取证代理在飞（产物落点/exp_evidence/adjudications/backtest_artifacts）。
  - 组合门打分器：scripts/backtest/promotion_combo_gate.py（40ca90eb88+import 修复 383c0af8e1+翻译 dc285476f4）——v2 尺的机器执行件已在产。
  - STD-SWITCH-001（切换判据）#305 定稿+P4 回验 WIN 具备转正资格——顺带核实其重考证据，一并处置。
- **块**：B1 取证（代理）；B2 若证据链完整→standards.yaml 两 STD flip frozen（CAS 写）+裁定登记（原子同 commit）；B3 若缺口→列清单不硬翻，草案终稿文档落档（Owner 裁）；B4 本簿回写。
- **依赖**：取证代理；无代码施工。
- **三态**：执行中。
- **下一步**：取证回报后按 B2/B3 分叉执行。

## 处置记录（回写区）

（待取证回报）

## 长尾登记

- flip 属"修标"：standards.yaml 头注释流程=AI 提案→治理立案→Owner 修宪；但 #306（Owner 终局授权批）已裁定 v2 提案路径，重考达标后 flip=执行既定裁定，非新修标——留裁定留痕双保险。
