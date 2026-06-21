---
module_id: KE-955
status: active
title: 5.3 跳级规则（明令禁止）
category: governance
---

# 5.3 跳级规则（明令禁止）

5.3 跳级规则（明令禁止）

- **禁止** 直接调用 `GateEngine.evaluate(task, "G3")` 而跳过 G1/G2：task 的 `gate_status` 字段必须按 `passed_g1 → passed_g2 → passed_g3 → …` 顺序推进
- **例外**：scaffold 补录（历史知识回填）允许 Owner 签发 `gate-exempt: G1 | reason: legacy-backfill | valid_until: <date>` 在 commit trailer 中豁免；见§九

---
