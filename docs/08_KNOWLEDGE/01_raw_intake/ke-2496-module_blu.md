---
module_id: KE-2401
title: 6.7 盲点总览（十一轮汇总）
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 6.7 盲点总览（十一轮汇总）

6.7 盲点总览（十一轮汇总）

| 轮次 | 盲点 | 数量 | P0 | P1 | P2 | 侧重领域 |
|:--:|------|:--:|:--:|:--:|:--:|------|
| 第一轮 | B1-B20 | 20 | 3 | 7 | 10 | 结构性冲突 / 架构完整性 / 运维能力 |
| 第四轮 | B21-B30 | 10 | 2 | 3 | 5 | 氛围编程社区对标 / 双轨边缘 / 非文件副作用 |
| 第五轮 | B31-B35 | 5 | 1 | 2 | 2 | 文件系统与 OS 级生产事故 / git gc 并发 / SQLite WAL |
| 第六轮 | B36-B40 | 5 | 1 | 2 | 2 | 跨学科注入 — DB WAL / 分布式共识 / 编译器 IR / 安全审计 / 排队论 |
| 第七轮 | B41-B55 | 15 | 3 | 6 | 6 | SRE DiRT 演练 / 金融 HFT Kill 粒度 / Durable Execution / DB 迁移工程 / Forward-Fix / Chaos Engineering / 依赖感知 / 对话上下文 / 数据完整性 / 回滚预算 |
| 第八轮 | B56-B75 | 20 | 4 | 7 | 9 | 自举回滚 / AI 幻觉溯源 / 变形攻击 / CVE 复引入 / Token 经济学 / 温备热切 / 语义化目标 / 分支拓扑回滚 / Git 基础设施污染 / GPG 签名链 / 密钥轮替 / Shell 跨平台 / venv 污染 / env 缓存 / 时间上下文断裂 / Owner 目标覆盖 / 网络分区 / S3 生命周期 / 外部证明 / Submodule 同步 |
| 第九轮 | B76-B95 | 20 | 4 | 7 | 9 | Prompt注入防护 / 策略即代码 / GDPR 遗忘权 / 连接池中毒 / Dev Container/WSL2 / MCP 工具回滚 / 确定性重放 / 告警疲劳抑制 / 渐进式回滚 / git bisect 保护 / File Watcher 暂停 / Shallow Clone 修复 / git notes 标记 / 软删除/硬删除 / filter-branch 引用断裂 / 决策疲劳防护 / 跨 Vendor 协调 / 回滚反馈闭环 / 回滚热力图 / 威胁情报 |
| 第十轮 | B96-B110 | 15 | 5 | 6 | 4 | **法证取证审计视角** — 自审计信任悖论 / git 二进制 PATH 中毒 / shell 元字符注入 / NTP 伪造时间线 / 静默 bit rot 腐蚀 / TOCTOU 竞态 / 信任根循环 / kill-9 截断审计 / in_flight 孤儿污染 / WAL 证据篡改 / Non-repudiation 问责空白 / reflog 一键抹除 / git notes 攻击面 / 持续完整性证明 / 观察者效应 |
| 第十一轮 | B111-B120 | 10 | 3 | 4 | 3 | **运维治理持续性视角** — 人力缺席/失能自治边界 / Feature Flag 发布分离范式 / LLM 模型版本静默行为漂移 / AI 置信度量化信号 / 回滚系统自复杂度 / Error Budget 自治门禁 / Git rebase/cherry-pick 进行中状态 / Commit Message 质量基础设施 / Fail-open/fail-closed 策略 / 多轮累积上下文污染 |
| 第十二轮 | B121-B130 | 10 | 4 | 5 | 1 | **对抗性AI安全视角** — Agent执行沙盒隔离 / AI主动破坏安全系统 (agentic misalignment) / 回滚后Runbook自动生成 / knowngoodstate已验证正确状态收据 / 回滚目标陈旧度风险 / 凭据自动轮替 / 回滚预写日志(WAL) / 多Agent文件冲突 / 操作意图存档 / 回滚系统被武器化滥用 |
| **合计** | **B1-B130** | **130** | **30** | **49** | **51** | "反应式"→"弹性"→"自愈自主"→"元认知"→"可取证信任"→"运维治理持续性"→"对抗性AI安全" |
