---
module_id: KE-2974
status: active
title: 核心职能
category: module_blueprint
---

# 核心职能

核心职能

**VMS 是全系统的统一向量记忆体**——所有系统（Orc、KB、CE、FLE）产出的需要语义检索的内容，最终都写入 VMS。设计哲学从"多分几个 Collection"升级为 **"让 AI agent 可审计、可自愈、可持续"**：

1. **可审计**：每条写入强制 provenance（继承 unified_memory_api 的 WriteTrace），包含 origin / audit_chain / arbitration
2. **可自愈**：IndexHealthMonitor 自动检测 + 修复索引损坏，Collection 漂移自检
3. **可持续**：双嵌入维度按需分配、TTL 自动过期、compaction 自动触发、检索质量闭环反哺 FLE

---
