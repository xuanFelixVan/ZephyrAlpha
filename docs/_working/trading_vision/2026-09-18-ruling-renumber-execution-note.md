---
ttl: task_bound
completes_when: 裁定注册表三路撞号治理被确认落库（若工作区改号被清，按本说明重放；若已在库，归档本说明）。
---

# 裁定撞号治理执行说明（2026-09-18，st-overseer-20260916）

## 事件
dev 的 ruling_registry 出现三路 #304/#305 撞号：做T v2 战役砍（#304，dev 先占）、Regime 重校准（#304，regcal 分支被 tdchain 合并带入）、切换器判决（#304，s-owner002 分支，已被 Wave A cherry-pick 时改号消解）；#305 双写=STD-SWITCH-001（尺子车道）+ 日度编排器八点（P3 分支被合并带入）。

## 已裁定方案（代码绑定优先原则）
- **#304 保留=Regime 重校准**（regime_detector.py 不变式两处引用裁定号，改号须改代码）；做T v2 战役砍 → **改号 #331**。
- **#305 保留=日度编排器八点**（daily_decision_orchestrator.py 三处引用）；STD-SWITCH-001 → **改号 #332**。
- 两改号条目已附 renumber_note（tombstone 惯例）。

## 当前状态（2026-09-18 04:1x）
改号已落工作区并验证（YAML parse OK+条目级唯一性 150 条零撞号+代码引用零破坏）；**gateway 最终提交因注册表多车道提交战（12+ 活车道）暂未落地**——工作区 MM 态会被下个 registry 提交良性吸收，或被 reconciler 清回（清回则按下节重放）。

## 重放脚本（若工作区改号被清）
按 renumber_note 关键词检查：grep "renumber_note" ruling_registry.yaml——若有 2 条注记且 #331/#332 存在=已落库无需动作；若无=重放：对 registry 工作区执行（CAS 循环）：
1. `ruling_id: '裁定#304'` 且下一行含"做T v2" → 改 `裁定#331` + 插入 renumber_note（原文见本文件§已裁定方案）
2. `ruling_id: '裁定#305'` 且下一行含"STD-SWITCH-001" → 改 `裁定#332` + 插入 renumber_note
3. yaml.safe_load 验证 + 条目级唯一性验证（Counter 查重）→ 网关提交（--files 仅 registry，写提同命令原子化）
注意：全文 grep "裁定#304" 计数≠条目数（summary/注记引用合法存在），唯一性判定只看 ruling_id 字段。
