---
module_id: KE-2978
status: active
title: 正面后果
category: module_blueprint
ttl: permanent
---

# 正面后果

正面后果

1. **单蓝图自包含**：AI 读一份文件理解全链路——零跳转。
2. **TaskCard 继承 Task**：基座对齐 metadata_registry.yaml §7 真源——不留两套并行模型，旧 v0.2.0 TaskCard 废弃。
3. **防漂移六维**：上游/下游/范围白名单/范围黑名单/规则引用/上下文装配/回滚全部结构化——AI 凭任务卡单文件施工。
4. **task_id 自文档**：`KBG-001` 一眼知道是架构决策——对标 Jira PROJ-123。
5. **SQLite + .md 双轨**：机器可查(SQL) + 人可读(md)——互补不可替代。
6. **三层防御幻觉**：DeepSeek 生产 → GLM 审查 → Claude 兜底——模型分工有 REG-LLM-001 数据支撑。
7. **路径合规创建**：MTH-013——AI 永不自行决定目录层级。
