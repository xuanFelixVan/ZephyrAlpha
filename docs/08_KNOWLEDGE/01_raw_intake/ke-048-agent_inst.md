---
module_id: KE-048
status: active
title: 8.1 已经自动加载（热记忆）——但需自检
category: agent_instruction
ttl: permanent
---

# 8.1 已经自动加载（热记忆）——但需自检

8.1 已经自动加载（热记忆）——但需自检

本文件 AGENTS.md 已被工具自动注入上下文，但注入副本可能是**旧版快照**（IDE 缓存滞后）。

**MUST**：每个新 session 启动后你必须立即执行 **准入校验（Admission Check）**：
1. 从磁盘重新读取 `D:\ZephyrAlpha\AGENTS.md`
2. 对比磁盘版 vs 注入版的 `版本：vX.Y.Z`（位于本文件第 3 行）
3. 若版本号不一致 → 以磁盘版为准，输出 `⚠️ AGENTS.md 版本漂移：注入版=vX.Y.Z, 磁盘版=vA.B.C，已切换至磁盘版`
4. 若磁盘读取失败 → 继续用注入副本，但提示 Owner 路径不可达

> **对标**：Kubernetes Admission Controller —— 任何进入集群的资源必须通过准入校验，AGENTS.md 注入也不例外。
