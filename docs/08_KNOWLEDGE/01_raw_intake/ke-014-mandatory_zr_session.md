---
module_id: KE-014---mandatory-zr---session-005
status: active
title: 5.3.5 🔴 MANDATORY-ZR — Session 终了强制自净（IRN-011 · ZR-008）
category: agent_instruction
ttl: permanent
doc_type: knowledge_entry
---

# 5.3.5 🔴 MANDATORY-ZR — Session 终了强制自净（IRN-011 · ZR-008）

5.3.5 🔴 MANDATORY-ZR — Session 终了强制自净（IRN-011 · ZR-008）

> **这不是"建议"——是GateEngine可硬阻断的强制条款，对标IRN-011零残留原则。**

**触发时机**：每次 AI session **结束前**（在保存 session continuity handoff 包之后、最终确认完成之前）。

**必须执行的操作**（以 `MANDATORY` 标记）：

1. **MANDATORY**：运行临时文件扫描 → 发现 `_temp*` / `_check*` / `_phase_*` 前缀文件 → **立即 `DeleteFile`（物理删除）**——不允许"留给下一个session"。对标 ZR-001。
2. **MANDATORY**：`python scripts/lock_files.py release-all <session_id>` → 释放本 session 持有的所有文件锁 → `python scripts/lock_files.py status` 确认 CLEAN。对标 §4 规则 7。
3. **MANDATORY**：确认本次 session 产生的所有 `.py` 文件已在合法三目录（`scripts/governance/` / `src/zephyr/` / `tests/`）中——不存在根目录孤儿。对标 ZR-003 + ZR-007。
4. **MANDATORY**：如果 session 中删除过任何文件或目录 → 检查是否有**废墟引用残留**（其他文件仍引用已删除的路径）。对标 ZR-005。
5. **非阻断但建议**：用 `detect_residual_files.py` 做一次内容残留检测——确认没有被替代但未删除的旧文件。对标 ZR-006。

**为什么这是铁律**：
- AI session 的上下文记忆极短（§5.1）——你今天留下的临时文件，**永远不会被下一个 AI session 自动发现和清理**
- 临时文件 = 磁盘噪音 = 下一个 AI session 的认知负担 = 冷启动时的"这个文件是干嘛的？"浪费 token 和时间
- 对标：Boy Scout Rule（"Always leave it cleaner than you found it"）、vi2"文件即债务"、Google Dead Code Elimination Policy
- **pre-commit GATE-ZR 为硬阻断执行层**——任何残留物尝试通过 git commit 入库，将直接被拒绝
