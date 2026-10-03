---
ttl: task_bound
completes_when: 六项裁定随骨架回写批消化+12号标签 Owner 表态+C3 销案确认后转归档
title: 提交链治本战役 01_F2六项复核裁定+B3收尾路线（5.3总筹 2026-10-03）
---

# §1 F2 六项复核裁定（总筹 2026-10-03，逐项实读代码）

| # | F2 提请 | 裁定 | 依据 |
|---|---------|------|------|
| 1 | 降级窗30m 归属歧义（idle 自退 1800 vs V5 重注册 1860，F2 取前者） | **改判 = V5 重注册降级窗 1860s**（session_concurrency.py 头部 wave4-D V5：`_REREGISTER_MIN_INTERVAL_SECONDS` = idle 上限+2×30s，窗内重注册=**降级执行**——"降级"一词的真身）；idle 自退 1800s（`:174 _ACTIVITY_IDLE_TIMEOUT_SECONDS`）为**另一独立活性机制**，已拆独立行 ④b"守护自退窗" | CSV L188-189 已随批改写；活性簇实为 8 套，7合1 更名"活性合流" |
| 2 | 标签⑨双职责（安全红线兜进"底线体面"） | **呈批 Owner：建议增设第 12 标签「别把钥匙留在门口」**——密钥不裸奔/SQL 不散落/LLM 必经安检。安全红线与风格洁癖是不同法律地位（RULE-SECRETS 是宪法 12 硬规则之一），内收分析也需分开判。Owner 不批则 ⑨ 兜底成立 | 密钥/裸SQL/LLM裸调等 ≈10+ 台可机械圈出改挂 |
| 3 | ghost 拾取闸挂点 S08 vs S03（F2 取 S08） | **维持 S08**——拾取动作发生在收割/接管时点（process_reaper 幽灵判据 ghost_suspects 连续 3 轮确认）；其活性参与面按一岗多流程双挂 S03 | 00_design_basis §4 |
| 4 | CAPABILITY-LOOKUP-REQUIRED 贴①勉强 | **暂维持①**（查能力+留审计=进场登记仪式）；手术批 reuse_scan 落地后改挂"先查再建"簇——CSV 记"预计改挂" | 00_design_basis §2.2 |
| 5 | 手续④⑤挂 S02 vs C05 执法位 | **维持 S02 + C05 双挂**——办手续的动作在 S02（施工时），执法兜底在 C05（DOC-HEADER-SUITE）；一岗多流程=引用非复制 | 00_design_basis §4 |
| 6 | DERIVED-FILE-DELETION-PROTECTION ⑦ 中置信 | **⑦ 确认，置信升高**——实读 `commit_gates/derived_file_deletion_gate.py`：模块头确认其为 GitCommitGateway 注册的派生文件删除保护门=档案安全族 | 实读 |

# §2 W-M1 C3 裁定建议

**建议销案**：基线"33→1"四种机械口径全不命中（W-M1 实勘 catalogs30/195/0/39 均不对）；全仓唯一"33"命中=72h 评估卷 CAPCAN pg_only=33，已被 B1/B2 批消化；noqa 豁免册死文件豁免=0 即合理终态。Owner 若记得 33 出处另给真源则重开。

# §3 B3 收尾路线（总筹拍板）

- **PD-1 采方案①**（state v2 map 化）：七册全武装不欠账；方案②留六册私改检测缺口违背本战役"一次治到位"定调。state.py 小改+向后兼容读旧单册形态，净零申报=替代单槽形态。
- **PD-2 采补登**：REG-MODULE-TRANSLATION-001 / REG-CAND-001 / REG-RULING-001 三册随 B3 批补登 ROOR（entry 形态施工单已定稿，entry_count 用 reconcile 实值 8748/623/294）。
- **C4 YAML 侧并入 B3**：F1 已完工释放 claim，B3 全量 render 七册时快照机制顺带吸收翻译册旧名行除名（三重保险在库）。
- **时序**（施工单三前置）：队列排空 → PD-1/PD-2 落地 → 广播让道窗 → B3 原子批。ROOR 触碰窗 = W-M1 B3（含 PD-2）→ 图11 上户口批，**禁同窗**。
- B3 执行人 = 5.3 总筹（本会话），施工单四节齐全可直接走。

# §4 盘面收敛记录（随批披露）

F1 两产物主区 index 残影（旧快照陷阱，今日已咬过 st-vmount-sop 首投一次）已收敛：`git restore --staged --worktree` 两文件回 HEAD 终态，盘面横幅清零复核（diff 方向预先核验=纯 F1 落地反向，无他会话内容）。

# §5 呈批 Owner（两件，一句话可裁）

1. **12 号安全标签**（§1#2）：批增设「别把钥匙留在门口」/ 或确认 ⑨ 兜底。
2. **C3 销案**（§2）：确认/给 33 真源重开。
