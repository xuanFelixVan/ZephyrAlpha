---
module_id: KE-1636
title: 2. 盲点清单与关闭映射
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 2. 盲点清单与关闭映射

2. 盲点清单与关闭映射

| 盲点 | 内容 | 严重度 | 关闭方式 |
|------|------|:---:|---------|
| #39 | AI代码生成的非确定性→容量行为不可复现 | 高 | CapacityFingerprint (M-36) |
| #40 | Prompt与容量指令的语义冲突 | 高 | BudgetAwarePromptMerger (M-37) |
| #41 | 氛围编程"快速实验"的隐性容量税 | 高 | VibeExperimentTracker (M-38) |
| #42 | 长期离线(7天+)的容量自治 | 高 | Vacation Mode (owner_offline_protocol.yaml) |
| #43 | AI模型切换的容量行为突变 | 高 | ModelCapacityProfile + ModelSwitchRecalibrator |
| #44 | 容量运维知识的单点蒸发(Bus Factor=1) | 致命 | CapacityRunbookGenerator |
| #45 | 容量告警的精度退化 | 高 | AlertPrecisionTracker |
| #46 | 系统的"黄昏退化"——多周运行的结构性容量流失 | 高 | LongevityMonitor (M-39) |
| #47 | Git仓库膨胀的隐性容量成本 | 中 | git gc 自动调度 + git_repo_health CAP-015 |
| #48 | pip依赖更新的"容量炸弹" | 高 | DependencyCapacityGuard |
| #49 | 容量"数字孪生"——AI动手前先模拟 | 高 | CapacityDigitalTwin (M-40) |
| #50 | 容量系统自身生命周期——谁维护维护者 | 高 | Meta-SLO (META-001~005) + self_upgrade_protocol |
| #51 | "卡珊德拉困境"——系统预测准确但Owner不信 | 致命 | AlertEscalation (4级升格) |
| #52 | AI自我修改容量治理代码的"元风险" | 致命 | CoreIntegrityGuard (M-41) |
| #53 | 氛围编程的"过度抽象"容量陷阱 | 中 | CodeEconomyAnalyzer |
| #54 | AI生成的"影子模块"容量泄漏 | 高 | ModuleBirthRegistry |
