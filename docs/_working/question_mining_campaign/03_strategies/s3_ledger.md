---
ttl: task_bound
title: S3 策略面挖矿台账（st-pqmine-20260927）
session: st-pqmine-20260927
date: 2026-09-27
status: 挖干待汇总
candidate_file: s3_candidates.yaml
candidate_count: 13
---

# S3 策略面挖矿台账

## 一、矿区与真源（六向之一：真源）

| 真源 | 用途 | 实测关键数 |
|------|------|-----------|
| docs/01_policies_and_standards/_registry/catalogs/strategy_registry.yaml（REG-STR-001，13021 行） | 策略唯一真源 | 161 策略（151 candidate / 8 backtest / 2 sim）；risk_rules 0/161；exit_logic 15/161；position_sizing 4/161；capacity_aum_limit 0/161；last_decay_scan_at 0/161；regime_valid 43/161；combination_strategy 全空 |
| docs/01_policies_and_standards/_registry/catalogs/cost_model_registry.yaml | 成本真源 | 6 模型；CST-ASTOCK-001=佣金万0.854+印花5bp+滑点1bp（L80/92），used_by 3 sleeve 策略 |
| scripts/backtest/f06_e4_wfa_exam.py:640 | E4 执行器 | 冻结土规成本 2.5bp+10bp+5bp（与 CST-ASTOCK-001 两口径并存） |
| docs/01_policies_and_standards/sop/backtest_system_sop/exam_policy.md | 考试判据真源（裁定#365） | §1 prereg frozen、§2 禁硬编码+DSR 喂全量+regime 必报、§3 双口径声明、§4 adj_factor 恒1→暂定档标签、§5 负结果台账 |
| config/strategy_production_map.yaml（策略工厂 v0.2） | 工厂环节图 | FAC-E0..E9 build_status：E4/E5/E6 built、E0/E1/E2/E3/E8/E9 partial、E7 pending(module_ref=null) |
| docs/_working/2026-09-14-combination-layer-exhaustive-charter.md | 组合层案卷 | DSR N 未落账事故：145 条台账冻结；重放 Sharpe 0.983→1.15 数据漂移；批次 B 三前置（L173/218/224） |
| docs/01_policies_and_standards/_registry/catalogs/backtest_backlog.yaml（REG-BTB-001） | 预注册册 | 142 对象（总册记 137=漂移）；plan 非空 5；threshold_status=frozen 5/120 testable |
| data/backtest_artifacts/runs/（154 目录） | run 台账 | SCR-C4-* 系列 on disk |
| docs/01_policies_and_standards/_registry/catalogs/risk_limit_registry.yaml + grep | 风控真源消费面 | registry 仅被 dashboard/治理门禁/decision_map 引用；src/zephyr/backtest+scripts/backtest 零引用 |

## 二、出题分布（13 题）

| 角度 | 题 | 一句话 |
|------|----|--------|
| ①可复现性 | S3-001/002 | run 台账落盘率；sim 策略重放净值一致（数据漂移前科复检） |
| ②成本敏感性 | S3-003/004 | ±1bp 符号翻转带宽；E4 冻结成本 vs 登记成本对账（三口径矛盾） |
| ③regime 适应性 | S3-005 | regime_valid 标注证据支撑率（无分桶=降级档纪律） |
| ④风控闸接线 | S3-006/007 | REG-RLM-001→回测路径接线断链；已考策略四件套齐备率 |
| ⑤策略间相关性 | S3-008/009 | 恐慌反弹双胞胎语义重复检测；可重放策略两两 ρ 矩阵（E8 ρ<0.7 闸前置） |
| 监控/容量/纪律 | S3-010/011/012/013 | E6 衰减扫描空转；容量三件套登记债；暂定档标签纪律执行率；DSR N 账本三前置完成度 |

## 三、去重记录

- 基线：results_all.yaml 283 题（全文索引化到 .runtime/tmp/s3s4_mining/pq_index.txt）+ 退役 30 题全文。
- 逐题 dedup_check 写入候选文件（vs_results/vs_retired 双栏）。
- 关键避让：PQ-0044（screen 通过率）、PQ-0053（焊成本校准）、PQ-0091（择时回测）、PQ-0104~0109（E1C 空间/考尺/合并闸）、PQ-0043/0089/0090/0094（组合分配层）、PQ-0012/0131（复权数据链路）、PQ-0002（meta_question 标题去重）、PQ-0145（轮动扣费重放）。
- 关键词机扫：净值/成本敏感/冻结成本/容量/衰减扫描/相关性闸/重复条目/暂定/标签纪律/N 账本/风控限额/regime_valid 在 283 题中 0~5 次命中（命中项逐一核对为 E1C/组合分配近邻题，已在 dedup_check 说明差异）；退役册主题词 0 命中。
- 禁翻案自查：S3-002/003 重放类题全部用原参数原窗、判据=复现偏差/敏感性带宽，非预测力主张，不触退役册"禁改参数重跑"铁律。

## 四、三态自审（挖干/未干/受阻）

- **S3-001 run 落盘率**：挖干（154 目录实测+evidence 解析口径已定）。
- **S3-002 重放一致**：挖干出题（考试执行需重放算力，判据已机解化）。
- **S3-003 成本敏感性**：挖干出题（6 档矩阵判据已定）。
- **S3-004 成本口径对账**：挖干（两口径数值+行号双锚实锤）。
- **S3-005 regime 证据支撑**：挖干（43 条清单可机生）。
- **S3-006/007 风控接线/四件套**：挖干（双零实测：grep 0 命中+字段 0/161）。
- **S3-008 双胞胎**：挖干（参数元组行号双锚）。
- **S3-009 ρ 矩阵**：挖干出题（依赖 S3-002 重放件，标 monthly 周期复考）。
- **S3-010 衰减空转**：挖干（0/161 实测）。
- **S3-011 容量债**：挖干（0/161+占位值判别法）。
- **S3-012 暂定标签**：挖干（exam_policy §4 + registry grep 实证）。
- **S3-013 DSR N 账本**：挖干出题（三前置判据逐条机解化；现状预期 insufficient 属合法出口）。
- **受阻项**：strategy_screen/exam 判定书正文在 PG（c1_backtest.*），本代理 reader 纪律未连库抽列，S3-009/S3-013 考试执行时须经 DatabaseService 取数——不影响出题成立。

## 五、未挖尽面（移交后续波次）

1. 151 条 candidate 策略的 entry_logic 可量化率分层（打板 23 条 vs 机构式）——量大，建议与 S2 因子波合流。
2. meta_labeling_config/combination_strategy 全空与 FAC-E8 regime 元分配的衔接考题（待 E8 施工后再考更有肉）。
3. aliases 46 条的跨册（factor_registry）同义漂移——归 S2/治理面更宜。

## 六、净零声明

本波零新册新 gate 新脚本：13 题全部挂靠既有真源（REG-STR-001/REG-BTB-001/exam_policy/工厂图/组合层宪章），候选文件+台账为本战役宪章既定产出位，无替代删除对象。
