---
doc_type: audit_report
title: 候选模块清单 — D_SECURITY
version: "1.0"
status: active
date: auto-generated
owner: auto-generator
ttl: permanent
---

# D_SECURITY 候选模块清单

> [← 返回索引](index.md)

> 本域候选 **394** 条（原有 0 + harvest 394）。
> harvest 去重四态: likely_new=66 / likely_implemented=320 / uncertain=8

## 完整清单

| ID | 名称 / Name | 大白话（干什么用） | 域 | 状态 | 四问卡点 | 优先级 | 触发信号摘要 | 下次复查 |
|------|------|------|------|------|------|:---:|------|------|
| CAND-HARVEST-0302 | Identity & Access Manager 身份与访问管理器 | / D-SECURITY-02 / Identity & Access Manager / ✅ 能建 / 📋 项目内有蓝图编号MOD-INF-018已建设 / OAuth2+JWT+MFA / | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0303 | Secret Manager 密钥管理器 | / D-SECURITY-03 / Secret Manager / ❌ 不能建 / / 门禁: 需Vault/HSM硬件 / 密钥管理+轮换 / | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0304 | Access Controller 访问控制器 | / D-SECURITY-08 / Access Controller / ✅ 能建 / 📋 项目内有蓝图编号MOD-INF-018已建设 / RBAC+ABAC+最小权限 / | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0305 | LLM Security Gateway LLM安全网关 | / D-SECURITY-12 / LLM Security Gateway / ✅ 能建 / 📋 项目内有蓝图编号MOD-INF-014已建设 / 九层防御L0-L8 / | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0306 | M3-S01 | M3 S01 供应链漏洞扫描器 ❌ 不能建 门禁: 需SBOM基础设施+CVE数据库+供应链扫描工具 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0307 | M3-S02 | M3 S02 恶意包检测器 ❌ 不能建 门禁: 需SBOM基础设施+CVE数据库+供应链扫描工具 恶 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0308 | M3-S03 | M3 S03 代码混淆防护器 ❌ 不能建 门禁: 需SBOM基础设施+CVE数据库+供应链扫描工具 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0309 | M3-S04 | M3 S04 完整性校验器 ❌ 不能建 门禁: 需SBOM基础设施+CVE数据库+供应链扫描工具 完 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0310 | M3-S05 | M3 S05 VEX文档管理器 ❌ 不能建 门禁: 需SBOM基础设施+CVE数据库+供应链扫描工具 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0311 | M3-S06 | M3 S06 供应链评分引擎 ❌ 不能建 门禁: 需SBOM基础设施+CVE数据库+供应链扫描工具 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0312 | M3-S07 | M3 S07 许可证合规扫描器 ❌ 不能建 门禁: 需SBOM基础设施+CVE数据库+供应链扫描工具 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0313 | M3-S08 | M3 S08 依赖锁定管理器 ❌ 不能建 门禁: 需SBOM基础设施+CVE数据库+供应链扫描工具 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0314 | M3-NEW-01 | / M3-NEW-01 / Slopsquatting检测器 / ❌ 不能建 / / 门禁: 需SBOM基础设施+CVE数据库+供应链扫描工具+GNN/FAIR模型/攻击图 / AI幻觉包名检测 / | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0315 | M3-NEW-02 | / M3-NEW-01 / Slopsquatting检测器 / ❌ 不能建 / / 门禁: 需SBOM基础设施+CVE数据库+供应链扫描工具+GNN/FAIR模型/攻击图 / AI幻觉包名检测 / | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0316 | M3-NEW-03 | / M3-NEW-01 / Slopsquatting检测器 / ❌ 不能建 / / 门禁: 需SBOM基础设施+CVE数据库+供应链扫描工具+GNN/FAIR模型/攻击图 / AI幻觉包名检测 / | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0317 | M3-NEW-04 | / M3-NEW-01 / Slopsquatting检测器 / ❌ 不能建 / / 门禁: 需SBOM基础设施+CVE数据库+供应链扫描工具+GNN/FAIR模型/攻击图 / AI幻觉包名检测 / | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0318 | M3-NEW-05 | / M3-NEW-01 / Slopsquatting检测器 / ❌ 不能建 / / 门禁: 需SBOM基础设施+CVE数据库+供应链扫描工具+GNN/FAIR模型/攻击图 / AI幻觉包名检测 / | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0319 | M3-NEW-06 | / M3-NEW-01 / Slopsquatting检测器 / ❌ 不能建 / / 门禁: 需SBOM基础设施+CVE数据库+供应链扫描工具+GNN/FAIR模型/攻击图 / AI幻觉包名检测 / | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0320 | M3-NEW-07 | / M3-NEW-01 / Slopsquatting检测器 / ❌ 不能建 / / 门禁: 需SBOM基础设施+CVE数据库+供应链扫描工具+GNN/FAIR模型/攻击图 / AI幻觉包名检测 / | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0321 | M3-NEW-08 | / M3-NEW-01 / Slopsquatting检测器 / ❌ 不能建 / / 门禁: 需SBOM基础设施+CVE数据库+供应链扫描工具+GNN/FAIR模型/攻击图 / AI幻觉包名检测 / | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0322 | M3-NEW-09 | / M3-NEW-01 / Slopsquatting检测器 / ❌ 不能建 / / 门禁: 需SBOM基础设施+CVE数据库+供应链扫描工具+GNN/FAIR模型/攻击图 / AI幻觉包名检测 / | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0323 | M3-NEW-10 | / M3-NEW-01 / Slopsquatting检测器 / ❌ 不能建 / / 门禁: 需SBOM基础设施+CVE数据库+供应链扫描工具+GNN/FAIR模型/攻击图 / AI幻觉包名检测 / | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0324 | M1-NEW-07 | / M3-NEW-05 / GNN恶意依赖检测器 / ❌ 不能建 / / 门禁: 需SBOM基础设施+CVE数据库+供应链扫描工具+GNN/FAIR模型/攻击图 / GNN检测 / | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0474 | 数据安全与合规 Data Security & Compliance | ║  │ 🆕Data Observability五维度映射(Freshness/Volume/Schema/Distribution/     │  ║ | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0572 | 四级数据分类 Four-tier Data Classification | L1公开/L2内部/L3机密/L4绝密 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0573 | RBAC访问控制 RBAC Access Control | Trader/RiskMgr/Researcher/Admin/AI Agent/Compliance角色 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0574 | 加密体系 Encryption System | TLS 1.3+AES-256-GCM+字段加密+备份加密 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0575 | AI脱敏管道 AI Desensitization Pipeline | 原始数据→分类识别→脱敏处理→审计记录 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0576 | 审计日志 Audit Log | 交易≥7年/决策≥3年/数据访问≥1年/AI调用≥1年/系统变更≥1年 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0612 | Audit Trail 不可变审计轨迹 | 密码学完整性保证+防篡改审计链 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0866 | Agent Security Module Agent安全模块 | Agent安全模块对抗韧性+串谋检测(9种)+涌现检测+幻觉防护+红队对抗(6维度) | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0867 | Insider Trading Prevention 内幕交易防护 | 内幕交易防护数据分级+信息隔离墙Ethical Wall+交易行为监控 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0868 | API Security Gateway API安全网关 | API安全网关四层架构(路由/认证/限流/审计)+API密钥轮换+速率限制 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0904 | LLM Security LLM安全网关 | LLM安全网关(九层防御+输入/输出过滤+Prompt注入防护) | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1001 | Audit Log Protector 审计日志保护器 | 审计日志不可篡改+完整性 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1002 | MCP Sandbox Execution Isolator MCP沙箱执行隔离器 | MCP执行隔离+沙箱+审计 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1003 | L0 Supply Chain SHA256 Verifier L0供应链SHA256验证器 | pip hash+requirements.txt锁定+完整性验证 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1004 | Code Security Auto Scanner 代码安全自动扫描器 | SAST工具Bandit/Semgrep+CI/CD集成 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1005 | Dependency Vulnerability Auto Detector 依赖漏洞自动检测器 | CVE数据库比对Safety/pip-audit | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1006 | Vendor Risk Scorer 供应商风险评分器 | 供应商安全评分卡 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1007 | Vendor Security Assessor 供应商安全评估器 | 供应商系列5项之一安全评估器 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1008 | Vendor Compliance Checker 供应商合规检查器 | 供应商系列5项之二合规检查器 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1009 | Vendor Incident Tracker 供应商事件追踪器 | 供应商系列5项之三事件追踪器 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1010 | Vendor Risk Assessor 供应商风险评估器 | 供应商系列5项之四风险评估器 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1011 | Vendor Report Generator 供应商报告生成器 | 供应商系列5项之五报告生成器 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1012 | Dependency Penetration Mapper 依赖穿透映射器 | 供应商扩展3项之一依赖穿透映射 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1013 | SLA Compliance Monitor SLA合规监控器 | 供应商扩展3项之二SLA合规监控 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1014 | Security Certification Verifier 安全认证验证器 | 供应商扩展3项之三安全认证验证 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1015 | Vendor Risk Quantifier 供应商风险量化器 | 量化供应商风险影响 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1016 | Security Scan Compliance Checker 安全扫描合规检查器 | 检查安全扫描覆盖率 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1017 | Fail-Closed Policy Manager 失败关闭策略管理器 | 安全检查失败时默认拒绝 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1018 | Financial Security Compliance Checker 金融安全合规检查器 | 金融行业安全合规检查 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1019 | OPA/Rego Engine OPA/Rego引擎 | OPA/Rego系列6项之一引擎 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1020 | Policy Definer 策略定义器 | OPA/Rego系列6项之二定义器 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1021 | Policy Executor 策略执行器 | OPA/Rego系列6项之三执行器 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1022 | Policy Auditor 策略审计器 | OPA/Rego系列6项之四审计器 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1023 | Policy Version Manager 策略版本管理器 | OPA/Rego系列6项之五版本管理器 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1024 | Policy Conflict Detector 策略冲突检测器 | OPA/Rego系列6项之六冲突检测器 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1025 | AI Agent Dependency Sandbox AI Agent依赖沙箱 | Agent运行时隔离 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1026 | L4 Agent Security Permission Isolator L4 Agent安全权限隔离器 | Agent权限边界执行 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1027 | AI Writable Permission Controller AI可写权限控制器 | Agent可修改路径白名单 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1028 | AI Code Modification Auditor AI代码修改审计器 | Agent代码修改审计追踪 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1029 | AI Read-Only Permission Executor AI只读权限执行器 | Agent只读操作权限控制 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1030 | Data Source API Key Security Storage 数据源API密钥安全存储器 | API密钥加密存储+访问控制 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1031 | Agent Communication Encryptor Agent间通信加密器 | Agent间通信加密 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1032 | Agent Behavior Baseline Learner Agent行为基线学习器 | Agent正常行为基线自动学习 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1033 | Agent Permission Dynamic Shrinker Agent权限动态收缩器 | 基于行为模式动态收缩Agent权限 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1034 | Agent Output Content Filter Agent输出内容过滤器 | Agent输出敏感信息过滤 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1035 | Vulnerability Scanner 漏洞扫描器 | 漏洞扫描+CVE比对+修复建议 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1036 | Security Incident Responder 安全事件响应器 | 安全事件响应+处置+恢复 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1037 | Red-Blue Team Verifier 红蓝对抗验证器 | 红蓝对抗+安全验证+报告 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1038 | Simplified Unified Authentication System 简化统一认证系统 | 统一认证+单点登录+MFA | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1039 | Attack Behavior Auto Blocker 攻击行为自动阻断器 | 攻击行为自动阻断+隔离+告警 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1040 | End-to-End Data Encryption and Access Controller 数据端到端加密与访问控制器 | 端到端加密+访问控制+密钥管理 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1041 | Data Encryption and Masking Processor 数据加密与脱敏处理器 | 数据加密+脱敏+差分隐私 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1042 | Casbin RBAC Permission Controller Casbin RBAC权限控制器 | Casbin RBAC+策略+执行 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1043 | Operation Audit Log System 操作审计日志系统 | 操作审计+日志+不可篡改 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1044 | Data Access Controller 数据访问控制器 | 数据访问控制+RBAC+审计 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1045 | Security Incident Responder Execution Layer 安全事件响应器执行层 | 安全事件响应执行层+自动化处置 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1046 | Role Permission Inheritance 角色权限继承 | 角色继承+权限传递+冲突检测 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1047 | Dynamic Permission Allocation 动态权限分配 | 动态权限+ABAC+条件分配 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1048 | Permission Change Audit 权限变更审计 | 权限变更审计+记录+告警 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1049 | Log Integrity Verification 日志完整性验证 | 日志完整性验证 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1183 | Security Awareness Trainer 安全意识培训器 | 安全意识培训门禁未满足 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1184 | Zero Trust Architect 零信任架构师 | 零信任架构设计源文件未详述 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1185 | Content Fingerprint Generator Verifier 内容指纹生成验证器 | SHA-256内容指纹+完整性验证 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1186 | MCP Document Compliance Checker MCP文档合规检查器 | MCP协议文档合规性检查 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1187 | Authentication Failure Handler 认证失败处理器 | 防暴力破解+账户锁定策略 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1188 | Model File Path Security Checker 模型文件路径安全性检查器 | 路径穿越防护+模型文件完整性 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1189 | Log Injection Protection 日志注入防护 | 日志内容过滤+注入模式检测 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1190 | IP Whitelist Manager IP白名单管理 | 出站IP白名单管理HB-SEC-01执行层 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1191 | Network Isolation Policy 网络隔离策略 | 网络隔离策略D-INFRA域 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1192 | Knowledge Access Control 知识访问控制 | 知识库按数据分级访问控制 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1193 | Security Audit Event Aggregator 安全审计事件聚合器 | 安全事件聚合+关联分析 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1194 | Security Domain Config Hot-Update Adapter 安全域配置热更新适配器 | 安全策略热更新+审计记录 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1195 | Security Domain Monitoring Metric Collection Adapter 安全域监控指标采集适配器 | Prometheus安全指标采集 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1196 | Security Audit Log Archive and Retention Manager 安全审计日志归档与保留管理器 | 日志分级归档+7年保留策略 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1197 | eBPF Security Manager eBPF安全管理器 | eBPF网络安全策略执行门禁未满足 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1769 | Data Masking & Privacy 数据脱敏与隐私 | v1→v2映射至SEC-002 InputOutputGuard；项目内有蓝图MOD-INF-014已建设 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1770 | Input Detection/Auth/Scan 输入检测/认证/扫描等 | v1 D-SECURITY-29~46共18项，v2按职责归入SEC-002/007/008/009 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1865 | InputOutputGuard 输入输出防护 | 输入输出防护：输入清洗/输出过滤/路径守卫/Native API守卫;九层防御L1+L3层 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1866 | PromptProtection 提示词防护 | 提示词注入防护：DAN/角色扮演/ignore注入模式检测;九层防御L2提示词保护层 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1867 | AgentSandbox Agent沙箱隔离 | Agent沙箱隔离：进程沙箱/代码执行隔离/资源限制/执行超时;九层防御L2a层 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1868 | MultiAgentSecurity 多Agent安全 | 多Agent安全：Agent间共谋检测/权限隔离/冲突解决;九层防御L4+L8层 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1869 | SupplyChainSecurity 供应链安全 | 供应链安全：依赖漏洞扫描/CVE比对/SBOM管理/SHA256校验;九层防御L0供应链层 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1870 | KeySecretManager 密钥管理 | 密钥层级管理：密钥存储/轮换/访问控制/泄露检测/密钥审计;SSOT单一真相源守卫 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1871 | SelfProtection 自保护 | 自保护：对抗性变异检测/代码完整性校验/自我验证/隔离保护;九层防御L5-L7层 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1872 | ACLGuard 访问控制 | 访问控制：RBAC/ABAC/权限守卫/Kill Switch;身份管理/意图绑定;治理桥接 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1900 | AI Construction Governor AI代码质量门控 | AI生成因子公式Hash校验+回归截断+值域偏差预警 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1901 | Non-AI Module Boundary Guard AI/non-AI模块边界守卫 | AI模块与non-AI模块边界明确划分AI权重≤30% | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1903 | Look-Ahead Bias Detector 前视偏差检测器 | 时序数据前视偏差自动检测与PIT门控联动 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1943 | 安全与治理 Security & Governance | 知识来源追溯+模块变更审计+自动操作日志+人工审批节点 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2045 | Kill Switch 紧急停机开关 | 独立于学习系统的硬开关可立即暂停所有学习系统操作 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2046 | Agent漂移检测 Agent Drift Detection | 监控LLM Agent的决策模式与设计意图的偏差KL散度检测 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2047 | NIST AI 100-5参考框架 NIST AI 100-5 Reference Framework | 三层安全架构:行为约束(预防)/行为监控(检测)/行为恢复(响应) | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2048 | Agent能力评估协议 Agent Capability Assessment Protocol | 定期评估Agent的能力边界评估结果纳入漂移检测基线 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2049 | 群集行为风险防护 Cluster Behavior Risk Protection | 监控本系统模块与行业主流模型的相关性>0.7自动增加差异化 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2073 | TEE可信执行环境 TEE Trusted Execution Environment | / R-35 / TEE可信执行环境 / ❌ / 硬边界约束二（单机Windows，无TEE硬件） / SGX/TDX硬件+Linux就绪 / | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2077 | Formal Verification形式化验证 Formal Verification | / R-39 / Formal Verification形式化验证 / ❌ / 硬边界约束二（SMT求解器需专业工具链） / Z3/PySMT集成+形式化验证专家就绪 / | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2143 | Communication Security 通信安全 | 通信安全身份认证消息完整性审计追踪 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2188 | Agent Mesh Cryptographic Identity Agent Mesh密码学身份 | / Agent Mesh (密码学身份) / Agent Card DID标识 / Agent ID + 启动时注册哈希（MVP简化版），未来升级Ed25519 / | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2194 | Behavior Pattern Testing 行为模式测试 | 行为模式测试个体多样性团队多样性串谋检测涌现检测漂移检测 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2210 | Crypto-Shredding 加密粉碎 | Crypto-Shredding数据保密性不等于数据完整性加密个人数据独立密钥哈希链基于密文销毁密钥即GDPR合规 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2233 | Dependency Graph ZK Proof 依赖图ZK证明 | / 依赖图ZK证明(证明合规但不暴露证据内容) / ❌受限 / GATE-004/006 / | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2235 | Log Independent Encryption Infrastructure 日志独立加密基础设施 | 日志独立加密基础设施AES-256-GCM建设状态可建 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2236 | Key Destruction 密钥销毁 | / 密钥销毁+销毁证书+被遗忘权响应 / ❌受限 / GATE-004/GATE-006激活 / | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2269 | PromptGuard 2 PromptGuard 2越狱检测 | > **LlamaFirewall (Meta, 2025)对标**：三护栏架构——PromptGuard 2(越狱检测BERT模型)、Agent Alignment Checks(链式思维审计，检测提示注入+目标错位)、CodeShiel | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2270 | Agent Alignment Checks Agent对齐检查 | > **LlamaFirewall (Meta, 2025)对标**：三护栏架构——PromptGuard 2(越狱检测BERT模型)、Agent Alignment Checks(链式思维审计，检测提示注入+目标错位)、CodeShiel | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2271 | CodeShield CodeShield代码盾 | > **LlamaFirewall (Meta, 2025)对标**：三护栏架构——PromptGuard 2(越狱检测BERT模型)、Agent Alignment Checks(链式思维审计，检测提示注入+目标错位)、CodeShiel | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2286 | OAuth 2.0 OAuth 2.0认证 | > **设计哲学**：参考Google A2A Protocol（2025.1版本支持WebSocket/SSE流式传输+OAuth 2.0认证+状态回滚） (2025年4月)，适配本系统单机部署场景。A2A协议定义Agent间的能力发现、 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2291 | DID Decentralized Identifier DID去中心化标识符 | DID Decentralized Identifier去中心化标识符Agent密码学身份LP-010 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2292 | Zero-Knowledge Proof 零知识证明 | 零知识证明L3外部可验证性Merkle根锚定外部时间戳权威+选择性披露 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2293 | Crypto-Shredding 密码粉碎 | Crypto-Shredding数据保密性加密个人数据独立密钥销毁密钥即GDPR合规 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2294 | AES-256-GCM AES-256-GCM加密 | AES-256-GCM加密日志独立加密基础设施可建 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2339 | Memory Security Constraints 记忆安全约束 | 记忆安全约束5项敏感数据不入记忆到记忆不可篡改到记忆访问控制到记忆一致性到记忆恢复 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2364 | Security Constraints 安全约束 | 安全约束5项审批记录纳入审计报告须保持完整性到治理日志须含策略变更历史到治理策略存储不可变到监管报送审批记录须含human_approval字段到B-016禁止AI自动清理未归档交易日志和审计记录 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2397 | Crypto-Shredding Key Destruction Restricted Crypto-Shredding密钥销毁受限 | / ❌受限 / D-REPORTING-02(多因子归因+策略退化检测)→D-FACTOR; D-REPORTING-03(LLM摘要)→LLM服务; D-REPORTING-03(Crypto-Shredding)→GATE-004/00 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2409 | Observability Security Constraints 可观测性安全约束 | 可观测性安全约束5项敏感数据不入Trace+Trace不可篡改哈希链+Trace访问控制角色限制+Trace存储合规≥7年+可观测性开销限制<5% | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2447 | Insider Trading Protection 内幕交易防护 | 数据分级+信息隔离墙Ethical Wall+交易行为监控 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2578 | Ethical Wall 信息隔离墙 | 数据访问控制+通信隔离+行为监控防止内幕信息流向交易决策方 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2579 | Watch List 观察名单 | 包含存在内幕信息风险的证券列表加强监控但不限制交易 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2580 | Restricted List 限制名单 | 包含已确认内幕信息的证券列表禁止交易硬阻断 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2581 | Trading Behavior Monitoring 交易行为监控 | 异常交易模式检测+内幕交易信号指标+自动告警 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2582 | AI Driven Insider Trading Monitoring AI驱动内幕交易监控 | LLM语义分析替代纯规则匹配 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2583 | Compliance Framework Comprehensive Benchmark 合规框架综合对标 | 跨架构合规对标覆盖§2-§7多层 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2584 | Compliance Security Module Completion 合规安全模块补全 | 源自A5安全架构§15.9合规安全模块补全 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2608 | IAM Access Control IAM与访问控制 | RBAC+ABAC+一人开发场景+Agent身份与权限 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2609 | Key Layer Management 密钥层级管理 | / 密钥层级管理（三层MK/DK/SK+Shamir 2-of-3+PQC后量子迁移路线） / 风险度量（→A4） / | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2610 | Audit Chain 审计链 | SHA-256哈希链+Merkle树+不可篡改操作日志 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2611 | Agent Security Agent安全 | 对抗韧性+串谋检测9种+涌现检测+幻觉防护 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2658 | Security Domain Division 安全域划分 | 交易域/数据域/治理域/运维域+跨域交互规则 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2659 | Defense in Depth 6 Layer 纵深防御6层 | / 纵深防御6层（含L3 LLM 4层guardrails+MCP Triple Gate+合规框架综合对标） / 治理审批流（→A2） / | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2698 | L2 L3 Data Access Audit L2/L3数据访问审计 | 数据访问审计所有L2/L3数据访问操作记录写入审计链 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2699 | Access Record 审计记录 | 数据访问审计包含访问者身份/时间/数据类型/访问目的 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2700 | Abnormal Access Pattern Detection 异常访问模式检测 | 数据访问审计非交易时段访问/异常频率/异常范围 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2701 | Daily Data Access Report 每日数据访问报告 | 数据访问审计每日生成Trader审查 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2702 | Cross Wall Request 跨墙请求 | 跨墙审批程序需要使用内幕信息的人员/Agent提交 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2703 | Restricted List Check 限制名单检查 | 跨墙审批程序在限制名单上的证券直接阻断 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2704 | Data Classification Determination 数据分级判定 | 跨墙审批程序L2及以下vs L3绝密分级 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2705 | L2 Auto Approval L2自动审批 | 跨墙审批程序L2及以下自动审批+事后审计 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2706 | L3 Manual Approval L3人工审批 | 跨墙审批程序L3绝密合规审查+Trader人工审批 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2707 | Temporary Cross Wall Authorization 临时跨墙授权 | 跨墙审批程序审批通过后授予临时访问权限 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2708 | Wall Personnel Management 墙上人员管理 | 跨墙审批程序跨墙期间行为受到额外监控 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2709 | Cross Wall End 跨墙结束 | 跨墙审批程序授权到期或任务完成后自动撤销 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2710 | Wall Personnel Extra Monitoring 墙上人员额外监控 | 墙上人员管理跨墙期间所有操作受到额外监控 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2711 | Wall Personnel Discussion Ban 墙上人员禁止讨论 | 墙上人员管理禁止与交易决策方讨论跨墙信息 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2712 | Wall Personnel Communication Audit 墙上人员通信审计 | 墙上人员管理通信记录额外审计 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2713 | Cross Wall Audit Chain 跨墙操作审计链 | 墙上人员管理跨墙操作记录写入审计链保留7年 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2714 | Pre Announcement Trading 重大公告前交易检测 | 异常交易模式检测交易时间vs公告时间比对 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2715 | Abnormal Profit 异常盈利检测 | 异常交易模式检测交易盈利率vs市场平均 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2716 | Related Trading 关联交易检测 | 异常交易模式检测交易标的与信息获取关联 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2717 | Timing Anomaly 时序异常检测 | 异常交易模式检测交易时序与信息时序比对 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2718 | Volume Price Anomaly 量价异常检测 | 异常交易模式检测交易量/价格vs历史分布 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2719 | Pre Announcement Position Rate 公告前建仓率 | 内幕交易信号指标公告前5日建仓次数/总建仓次数 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2720 | Abnormal Profit Rate 异常盈利率 | 内幕交易信号指标超额收益率超过市场3σ的比例 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2721 | Info Trading Time Lag 信息-交易时滞 | 内幕交易信号指标信息获取到交易的平均时间 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2722 | Restricted List Trigger Rate 限制名单触发率 | 内幕交易信号指标触发限制名单的次数/总交易次数 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2723 | Auto Alert and Manual Review 自动告警与人工审查 | 内幕交易防护检测到异常交易模式时立即向Trader告警 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2735 | Monitoring Response 监控与响应 | / 监控与响应 / 5 / 5/5 / 无（行为异常检测+串谋检测+审计链+事件响应6阶段+KILLSWITCH） / | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2865 | Vendor Risk 供应商风险 | A5功能域安全模块补全供应商风险 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2872 | 模型运行层 Model Runtime Layer | 工具调用验证+参数校验+上下文隔离+温度控制 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2873 | 输出审查层 Output Review Layer | 输出分类+敏感信息检测+指令提取验证+幻觉检测 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2874 | 权限与审计层 Permission and Audit Layer | 最小权限+操作审计+实时阻断+工具调用监控 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2875 | 交易指令数据密钥 Trading Data Key | 保护交易指令订单数据L3月度轮换 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2876 | 策略参数数据密钥 Strategy Data Key | 保护策略参数因子公式L3月度轮换 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2877 | 持仓数据密钥 Position Data Key | 保护持仓数据盈亏数据L2季度轮换 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2878 | 因子数据密钥 Factor Data Key | 保护因子值信号数据L2季度轮换 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2879 | 审计日志数据密钥 Audit Data Key | 保护审计日志L2季度轮换 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2880 | 系统配置数据密钥 Config Data Key | 保护系统配置L2季度轮换 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2881 | 行情数据密钥 Market Data Key | 保护行情数据L1半年轮换 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2882 | 主密钥 Master Key | / 主密钥(MK) / 1 / RSA-4096（PQC迁移见§4.4；双重用途演进见DEC-SEC-06） / 加密DK+签名审计日志（双重用途，见§5.1/DEC-SEC-06） / Shamir 2-of-3分割存储 / 年度轮换 / | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2883 | 数据密钥 Data Key | AES-256-GCM加密业务数据MK加密保护 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2884 | 会话密钥 Session Key | AES-256-GCM/ECDH加密临时通信DK派生 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2885 | Network and Physical Layer 网络 | 网络分段+出站白名单+进程级微隔离+TLS 1.3强制加密 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2886 | Host and OS Layer 主机与操作系统层 | Windows安全基线+端口最小化+补丁管理+凭证保护 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2887 | Application and API Layer 应用与API层 | 输入验证+API安全+LLM调用安全+供应链安全 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2888 | Data Layer 数据层 | 加密策略+数据分级与脱敏+DLP+PIT数据保护 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2889 | Identity and Access Layer 身份与访问层 | Zero Trust核心原则+RBAC+ABAC+Agent身份管理+最小权限 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2890 | Monitoring and Response Layer 监控响应 | 安全事件检测+SIEM+事件响应6阶段+红队演练 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2891 | IAM与访问控制 IAM and Access Control | RBAC 4角色+ABAC策略引擎+Agent身份注册认证权限边界 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2892 | 密钥层级管理 Key Hierarchy Management | MK→DK→SK三层+Shamir 2-of-3分割+PQC三阶段迁移 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2893 | 审计链 Audit Chain | SHA-256哈希链+Merkle树每1000条+6W日志规范+7年交易日志保留 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2894 | Agent安全 Agent Security | 4层guardrails+串谋9种探测+涌现+目标偏移检测+幻觉防护+记忆投毒6层防御 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2895 | 内幕交易防护 Insider Trading Protection | 4级数据分类+信息隔离墙+观察名单/限制名单+跨墙审批+交易行为监控 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2896 | Trader 交易员 | 人类交易决策者审批策略确认异常交易管理数据源 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2897 | AI_Agent | 执行交易策略数据处理信号生成最小权限严格沙箱 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2898 | System 系统 | 日志写入健康检查密钥轮换服务级权限无业务操作 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2899 | ABAC策略引擎 ABAC Policy Engine | 属性定义+动态访问决策+交易时段特殊策略+KILLSWITCH.md对标 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2900 | Peak Suspicion 峰值怀疑 | 分析Agent内部状态识别可疑度峰值 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2901 | Deception Split 欺骗分割 | 比较Agent内部推理和外部输出检测不一致 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2902 | Correlation 相关性 | 分析多个Agent输出之间的统计相关性检测异常协调 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2903 | Ensemble 集成 | 综合3种探测技术结果使用加权投票或ML模型集成判断 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2904 | Graph 图谱 | 构建Agent交互图分析图结构特征检测异常通信模式 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2905 | Gap Ratio 缺口比率 | 计算最高欺骗分数与次高欺骗分数的比值 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2906 | Collective Score 核心 | 将所有Agent的欺骗分数求和/求均值 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2907 | Pairwise Correlation 成对相关性 | 计算每对Agent激活值的相关系数 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2908 | Behavior Trajectory Similarity 行为轨迹相似度 | 比较Agent间的行为序列使用编辑距离衡量相似度 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2909 | Steganography Communication Detection 图谱 | 通信内容统计特征分析+通信容量分析+通道容量限制 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2910 | Identity Rotation and Anonymization 身份轮换与匿名化 | 定期轮换Agent的协作伙伴防止稳定串谋伙伴关系 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2911 | Whistleblower Agent 举报代理 | 部署专门的监控Agent监控其他Agent的可疑行为 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2912 | Goal Drift Detection 目标漂移检测 | 步数检查点+目标偏移评分+长链执行限制+偏移恢复 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2913 | Fact Checking 事实核查 | 交易相关输出与行情数据交叉验证+数值输出与历史统计分布比对 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2914 | Consistency Check 一致性检查 | 时间一致性+上下文一致性+跨Agent一致性 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2915 | Confidence Scoring Mechanism 置信度评分机制 | 每个LLM输出附带置信度评分0.0-1.0 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2916 | Red Team Adversarial Framework 红队对抗框架 | 提示词注入+串谋+涌现+幻觉+越权+记忆投毒6维度测试 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2917 | Input Provenance Tagging 标签 | 所有记忆条目必须附带来源标记不可被Agent修改 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2918 | Write-time Validation 写入时验证 | 记忆写入时进行内容过滤拦截指令性模式 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2919 | Session-scoped Memory 内存 | 默认记忆为会话级会话结束后自动清除 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2920 | Trust-aware Retrieval 信任感知检索 | 记忆检索时计算复合信任评分 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2921 | Memory Audit 内存审计 | 每日自动审计所有持久化记忆条目 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2922 | Memory Integrity Check 内存 | 持久化记忆条目附带SHA-256哈希签名 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2923 | Cross-wall Approval Procedure 跨墙审批流程 | 分级审批L2及以下自动L3人工+临时跨墙授权+墙上人员管理 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2924 | Abnormal Trading Pattern Detection 异常交易模式检测 | 重大公告前交易+异常盈利+关联交易+时序异常+量价异常 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2925 | AI-driven Insider Trading Monitoring 监控 | LLM语义分析替代纯规则匹配 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2926 | WASM Sandbox Runtime WASM沙箱运行时 | Windows单机WASM运行时支持有限不能建 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2927 | Dependency Behavior eBPF Monitor 依赖行为eBPF监控器 | Windows不支持eBPF不能建 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2928 | Micro VM Isolator 微VM隔离器 | Firecracker需Linux KVM不能建 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2929 | mTLS Auto Generator mTLS自动生成器 | 单机部署无需mTLS不能建 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2944 | SIEM Security Information and Event Management 安全事件 | 日志集中收集+关联分析+告警规则+告警分级 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2945 | Six-stage Incident Response Process 响应标签 | 检测+分类+遏制+根除+恢复+复盘 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2946 | DLP Data Loss Prevention 事件 | 出站内容检查+敏感模式检测+剪贴板监控+文件操作监控 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2947 | PIT Data Protection PIT数据保护 | PIT数据标记+PIT隔离+PIT完整性+PIT审计 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2948 | Shamir Secret Sharing Shamir秘密共享 | 主密钥使用Shamir秘密共享算法分割为3个份额 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2949 | PQC Post-Quantum Cryptography Migration 图谱 | 三阶段迁移路线经典密码→混合模式→纯PQC | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2950 | Merkle Tree Structure Merkle树结构 | 每1000条日志构建一棵Merkle树SHA-256哈希作为叶子节点 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2951 | SHA-256 Hash Chain SHA-256哈希链 | 每条日志包含前一条日志的SHA-256哈希形成链式结构 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2952 | 6W Log Specification 6W日志规范 | WHO+WHAT+WHEN+WHERE+WHY+RESULT | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2953 | Merkle Inclusion Proof Merkle包含证明 | 验证单条日志是否属于某棵Merkle树 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2954 | Blockchain Anchored Timestamp 区块链锚定时间戳 | 每棵Merkle树的根哈希锚定到公有链不能建 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2955 | TEE Trusted Execution Environment 环境执行 | 单台PC无TEE硬件支持不能建 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2956 | FHE Fully Homomorphic Encryption 全量 | 计算开销1000-10000x单机性能不足不能建 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2957 | FL Federated Learning FL联邦学习 | 需多方参与单人开发无协作方不能建 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2958 | MPC Secure Multi-party Computation MPC安全多方计算 | 通信轮次多延迟高单机无多方需求不能建 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2959 | BLACKICE Red Team Toolkit BLACKICE红队工具包 | 容器化红队工具包14个精选开源工具Docker一键启动 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2960 | LLM Pentesting 5-layer Methodology LLM渗透测试5层方法论 | 输入输出层/检索层/工具调用层/模型层/运行时层 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2961 | AI-driven Automated Red Team AI驱动自动化红队 | AI赋能传统渗透全流程自动化 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2962 | Docker Container Docker容器 | 进程级隔离namespace+cgroup低风险开发测试 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2963 | gVisor Container gVisor容器 | 系统调用拦截中风险任务 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2964 | Firecracker microVM Firecracker微虚拟机 | 硬件级隔离独立内核高风险交易执行 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2965 | ISOLATEGPT hub-spoke ISOLATEGPT中心辐射 | 语义+技术双重隔离多Agent协作 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2979 | 安全域规则目录 Security Domain Rule Catalog | 访问控制审计加密漏洞 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3063 | 审计日志完整性 Audit Log Integrity | 日志记录完整率 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3075 | NVIDIA AI Red Team 2026 NVIDIA AI红队2026 | 沙箱化Agent工作流安全指南 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3076 | NIST CAISI 2025 | 红队竞赛13个前沿模型250K+攻击 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3077 | AAAI 2026 FinJailbreak AAAI 2026金融越狱 | 金融AI Agent红队测试FCFT | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3078 | SOC 2 Type II for AI AI SOC 2 Type II认证 | AICPA信任服务标准扩展到AI | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3403 | FCFT金融宪法微调 FCFT Financial Constitution Fine-Tuning | / 金融治理越狱(FinJailbreak) / 领域特定对抗提示→绕过安全对齐 / SOTA模型显著脆弱 / FCFT(金融宪法微调)嵌入金融法规→漏洞降低>55% / | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3431 | llm_security/gateway.py LLM安全网关入口 | SEC-001已有代码映射AISG网关核心入口 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3432 | llm_security/protocol.py LLM安全协议定义 | SEC-001已有代码映射AISG协议层 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3433 | l0_supply_chain.py L0供应链安全 | SEC-001已有代码映射九层防御L0供应链层 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3434 | l8_multi_agent.py L8多Agent安全 | SEC-001已有代码映射九层防御L8多Agent层 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3435 | security_gateway_base.py 安全网关基类 | SEC-001已有代码映射L10合规网关基类 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3436 | default_security_gateway.py 默认安全网关 | SEC-001已有代码映射L10合规网关默认实现 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3437 | input_sanitizer.py 输入清洗器 | SEC-002已有代码映射输入清洗 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3438 | l1_input.py L1输入防御 | SEC-002已有代码映射L1输入防御层 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3439 | l3_output.py L3输出过滤 | SEC-002已有代码映射L3输出过滤层 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3440 | input_guard.py 输入守卫 | SEC-002已有代码映射agent_rbac输入守卫 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3441 | output_guard.py 输出守卫 | SEC-002已有代码映射agent_rbac输出守卫 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3442 | path_guard.py 路径守卫 | SEC-002已有代码映射agent_rbac路径守卫 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3443 | native_api_guard.py Native API守卫 | SEC-002已有代码映射Native API守卫 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3444 | false_completion_detector.py 虚假完成检测器 | SEC-002已有代码映射虚假完成检测 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3445 | shell_dialect_detector.py Shell方言检测器 | SEC-002缺口标记Shell方言检测属输入防护 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3446 | l2_prompt_protection.py L2提示词保护 | SEC-003已有代码映射L2提示词保护层 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3447 | injection_patterns.py 注入模式库 | SEC-003已有代码映射注入模式库 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3448 | vibe_coding_guard.py Vibe Coding防护 | SEC-003已有代码映射Vibe Coding防护 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3449 | cybersec_2026_guard.py 2026新型攻击防护 | SEC-003已有代码映射2026新型攻击防护 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3450 | novel_attack_guard.py 新型攻击防护 | SEC-003已有代码映射新型攻击防护 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3451 | rule_injection_guard.py 规则注入防护 | SEC-003已有代码映射规则注入防护 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3452 | context_drift_detector.py 上下文漂移检测器 | SEC-003缺口标记与提示词保护交叉偏向自保护 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3453 | process_sandbox.py 进程沙箱 | SEC-004已有代码映射进程沙箱 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3454 | l2a_process_sandbox.py L2a进程沙箱 | SEC-004已有代码映射L2a进程沙箱层 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3455 | rollback_sandbox.py 回滚沙箱 | SEC-004已有代码映射回滚沙箱 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3456 | cold_start_lock.py 冷启动锁 | SEC-004已有代码映射冷启动锁 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3457 | cascading_failure_isolator.py 级联故障隔离器 | SEC-004已有代码映射级联故障隔离 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3458 | dry_run.py 干运行 | SEC-004已有代码映射干运行 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3459 | engine_degradation.py 引擎降级 | SEC-004缺口标记降级是沙箱资源限制延伸 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3460 | l4_agent.py L4 Agent安全 | SEC-005已有代码映射L4 Agent安全层 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3461 | multi_agent_collusion_detector.py 多Agent共谋检测器 | SEC-005已有代码映射共谋检测 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3462 | replay_attack_guard.py 重放攻击防护 | SEC-005已有代码映射重放攻击防护 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3463 | toctou_guard.py TOCTOU防护 | SEC-005已有代码映射TOCTOU防护 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3464 | sequence_guard.py 序列守卫 | SEC-005已有代码映射序列守卫 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3465 | cross_session_detector.py 跨会话检测器 | SEC-005已有代码映射跨会话检测 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3466 | wireheading_prevention.py Wireheading防护 | SEC-005已有代码映射Wireheading防护 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3467 | audit_trail/supply_chain_security.py 供应链安全审计 | SEC-006已有代码映射供应链安全审计 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3468 | dep_cve_correlator.py CVE关联器 | SEC-006已有代码映射CVE关联分析 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3469 | remote_attestation.py 远程证明 | SEC-006已有代码映射远程证明 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3470 | security_config_scanner.py 安全配置扫描器 | SEC-006已有代码映射安全配置扫描 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3471 | key_hierarchy.py 密钥层级 | SEC-007已有代码映射密钥层级 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3472 | secrets_lifecycle.py 秘密生命周期 | SEC-007已有代码映射秘密生命周期 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3473 | shared/security/secrets.py 共享密钥 | SEC-007已有代码映射共享密钥 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3474 | ssot_guard.py SSOT守卫 | SEC-007已有代码映射SSOT单一真相源守卫 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3475 | secrets.py 秘密模式检测 | SEC-007已有代码映射秘密模式检测 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3476 | secret_rotation.py 密钥轮换 | SEC-007已有代码映射密钥轮换 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3477 | adversarial_mutator.py 对抗变异器 | SEC-008已有代码映射对抗变异 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3478 | code_integrity.py 代码完整性 | SEC-008已有代码映射代码完整性 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3479 | l7_validation.py L7验证 | SEC-008已有代码映射L7验证层 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3480 | isolation.py 隔离保护 | SEC-008已有代码映射隔离保护 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3481 | red_team_scanner.py 红队扫描器 | SEC-008已有代码映射红队扫描 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3482 | l5_resource_protection.py L5资源保护 | SEC-008已有代码映射L5资源保护层 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3483 | l6_observability.py L6可观测性 | SEC-008已有代码映射L6可观测层 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3484 | immutable_core.py 不可变核心 | SEC-008已有代码映射不可变核心 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3485 | integrity_self_check.py 完整性自检 | SEC-008已有代码映射完整性自检 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3486 | micro_verifier.py 微验证器 | SEC-008已有代码映射微验证器 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3487 | post_action_verifier.py 事后验证器 | SEC-008已有代码映射事后验证 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3488 | continuous_verifier.py 持续验证器 | SEC-008已有代码映射持续验证 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3489 | behavior_audit_logger.py 行为审计日志器 | SEC-008已有代码映射行为审计日志 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3490 | blind_spot_tracker.py 盲点追踪器 | - ⚠️ agent_rbac/blind_spot_tracker.py（盲点追踪）属于自保护范畴但偏向治理，应与D-GOVERNANCE协调 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3491 | kill_switch.py Kill Switch kill_switch.py紧急制动 | SEC-009已有代码映射Kill Switch紧急熔断 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3492 | permission_guard.py 权限守卫 | SEC-009已有代码映射权限守卫 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3493 | abac_guard.py ABAC守卫 | SEC-009已有代码映射ABAC守卫 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3494 | rbac_guard.py RBAC守卫 | SEC-009已有代码映射RBAC守卫 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3495 | derive_rbac_roles.py RBAC角色推导 | SEC-009已有代码映射RBAC角色推导 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3496 | permission_mode_manager.py 权限模式管理器 | SEC-009已有代码映射权限模式管理 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3497 | permission_hooks.py 权限钩子 | SEC-009已有代码映射权限钩子 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3498 | emergency_override.py 紧急覆盖 | SEC-009已有代码映射紧急覆盖 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3499 | escalation_handler.py 升级处理器 | SEC-009已有代码映射升级处理 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3500 | identity.py 身份管理 | SEC-009已有代码映射身份管理 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3501 | intent_binder.py 意图绑定 | SEC-009已有代码映射意图绑定 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3502 | defense_depth.py 防御纵深 | SEC-009已有代码映射防御纵深 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3503 | guard_layers.py 守卫层编排 | SEC-009已有代码映射守卫层编排 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3504 | approver_check.py 审批检查 | SEC-009已有代码映射治理桥接审批检查 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3505 | a2a_check.py A2A检查 | SEC-009已有代码映射治理桥接A2A检查 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3506 | capability_check.py 能力检查 | SEC-009已有代码映射治理桥接能力检查 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3507 | bootstrap_superadmin.py 超级管理员引导 | SEC-009已有代码映射治理桥接超级管理员引导 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3508 | capability.py 能力定义 | SEC-009已有代码映射共享能力定义 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3509 | audit_log_guard.py 审计日志守卫 | - ⚠️ agent_rbac/audit_log_guard.py（审计日志守卫）横跨ACL与审计，应与D-GOVERNANCE协调归属 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3510 | session_lifecycle.py 会话生命周期 | SEC-009缺口标记会话管理与D-AUT-CORE交叉 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3511 | session_concurrency.py 会话并发 | SEC-009缺口标记会话管理与D-AUT-CORE交叉 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3512 | non_repudiation.py 抗抵赖 | SEC-009缺口标记纳入ACLGuard抗抵赖 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3513 | memory_guard.py 内存守卫 | SEC-009缺口标记纳入ACLGuard内存保护 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3514 | memory_provenance_guard.py 内存来源守卫 | SEC-009缺口标记纳入ACLGuard内存保护 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3515 | canary_rollout_manager.py 金丝雀发布管理器 | SEC-004缺口标记金丝雀归SEC-004沙箱 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3516 | blueprint_fidelity.py 蓝图保真 | SEC-008缺口标记蓝图保真归SEC-008 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3517 | phase_executor.py 阶段执行器 | SEC-004缺口标记纳入AgentSandbox阶段执行 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3518 | observability.py 可观测性 | SEC-008缺口标记纳入SelfProtection | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3519 | risk_mitigation.py 风险缓解 | SEC-008缺口标记纳入SelfProtection | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3520 | 进程沙箱层 Process Sandbox Layer | 九层防御L2a代码执行隔离/资源限制/超时 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3521 | 可观测性层 Observability Layer | 九层防御L6行为审计/指标采集/告警 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3522 | 验证层 Validation Layer | 九层防御L7完整性自检/微验证器/红队扫描 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3523 | 多Agent安全层 Multi-Agent Security Layer | 九层防御L8共谋检测/跨会话防护 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3524 | shared/contracts/security模块包 shared contracts security | 场内已有模块1个SEC-009 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3525 | llm_security/dashboard 安全仪表盘 | SEC-001缺口标记安全仪表盘未在AISGGate子模块体现 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4241 | Microstructure Defense 微结构防御 | / microstructure_defense.py / governance/ / 微结构防御 / ❌ 属于D-SECURITY——微结构防御是安全域 / | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4835 | 4层guardrails 4-layer Guardrails | 安全架构-提示词注入防御4层guardrails详见A5§2.3 L3层定义 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4839 | BLACKICE 红队工具包 | / BLACKICE / Databricks (2026) / 容器化红队工具包，14个精选开源工具（Garak/Promptfoo/PyRIT/ART/Giskard等），统一CLI，Docker一键启动 / **能建**：Docker | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4840 | OWASP Gen AI Red Teaming Guide OWASP生成式AI红队指南 | / OWASP Gen AI Red Teaming Guide / OWASP (2025) / 全栈红队方法论：模型权重→训练数据→API端点→用户界面 / 已采纳为本系统红队框架基础 / | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4841 | LLM Pentesting 5层方法论 LLM Pentesting 5-layer Methodology | / LLM Pentesting 5层方法论 / Repello AI (2026) / 输入输出层/检索层/工具调用层/模型层/运行时层，30项检查清单 / **能建**：5层攻击面与本系统6层纵深防御天然对应 / | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4842 | AI驱动自动化红队 AI-driven Automated Red Team | 红队工具-行业趋势(2026)AI赋能传统渗透全流程自动化 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4844 | OWASP ASI 10类行为监控 OWASP ASI 10 Behavior Monitoring | / 行为风险(Behavioral) / Agent以非预期方式追求目标 / §15.4 OWASP ASI 10类行为监控+意图匹配 / | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4849 | 记忆投毒检测指标 Memory Poisoning Detection Metrics | 记忆投毒防御-记忆注入拦截率/可疑记忆比例/记忆-行为偏离度/持久化记忆增长率 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4850 | 注册流程 Registration Flow | Agent身份注册-Agent启动时向IAM服务注册获取唯一agent_id+Ed25519密钥对 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4851 | 认证流程 Authentication Flow | Agent身份认证-Agent每次操作前向IAM服务请求访问令牌+签名验证+ABAC策略 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4852 | 令牌管理 Token Management | Agent身份认证-访问令牌短期有效5分钟自动刷新 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4863 | Vulnerability Fix Window Assessor 漏洞修复窗口评估器 | 漏洞修复窗口评估 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4864 | AI Hallucination Package Name Guard AI幻觉包名防护 | AI幻觉包名防护 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4865 | SBOM Reachability Analyzer SBOM可达性分析器 | SBOM可达性分析 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4866 | Attack Surface Simulator 攻击面模拟器 | 攻击树杀伤链依赖混淆恶意包注入仿真 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4867 | AI Agent Dependency Security Sandbox AI Agent依赖安全沙箱 | Agent隔离权限边界资源限制WASM沙箱 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4869 | Financial Constitution Fine-Tuning 金融宪法微调 | 嵌入金融法规到模型权重降低FinJailbreak漏洞 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4875 | Zero-Knowledge Compliance Audit Layer 零知识合规审计层 | 可证明合规但不暴露策略细节的审计机制 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4876 | ZKP Proof Generator ZKP证明生成器 | 交易episode转换为ZK证明 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4877 | Shield Module Shield模块 | 不安全动作可行域投影保证零违规 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4889 | CollusionDetection 串谋检测 | 行为相似度+时间窗口关联+统计显著性检验 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-5022 | Defense in Depth 6 Layers 纵深防御6层 | / — / 纵深防御6层 / 含L3 LLM 4层guardrails+MCP Triple Gate / ✅ / | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-5023 | Key Hierarchy Management 密钥层级管理 | / — / 密钥层级管理 / 三层MK/DK/SK+Shamir 2-of-3+PQC后量子迁移路线 / ✅ / | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-5024 | Vendor Risk Management 供应商风险管理 | 风险评估/合规检查/事件追踪/SLA监控10子模块 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-5025 | Data Access Audit 数据访问审计 | 数据访问日志+异常访问检测+权限变更追踪 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-5026 | Data Desensitization Engine 数据脱敏引擎 | 外部API传输脱敏+策略/持仓/因子数据过滤 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-5027 | Security Policy as Code 安全策略即代码 | OPA/Rego安全策略引擎+6子模块 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-5028 | Content Security 内容安全 | / — / 内容安全 / 内容指纹/MCP文档合规检查/模型文件路径安全性/知识访问控制 / ✅ / | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-5029 | Blockchain Anchoring 区块链锚定 | 审计链上链 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-5030 | TEE Trusted Execution Environment TEE可信执行环境 | 硬件不支持 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-5031 | eBPF Kernel Monitoring eBPF内核监控 | Windows不支持+驱动风险 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-5032 | WASM Sandbox WASM沙箱 | 单机架构不需要 | D_SECURITY | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |

## 按四问卡点分组（为什么没开发）

> 四问过滤：q1已实现 / q2需求驱动 / q3域活着 / q4 AI替代。任一问「否」即不进 depgraph 设计态，登记在候选库。

### 待评估（394 条）

| ID | 名称 | 大白话（干什么用） | 域 | 卡点理由 | 替代方案 |
|------|------|------|------|------|------|
| CAND-HARVEST-0302 | Identity & Access Manager 身份与访问管理器 | / D-SECURITY-02 / Identity & Access Manager / ✅ 能建 / 📋 项目内有蓝图编号MOD-INF-018已建设 / OAuth2+JWT+MFA / | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0303 | Secret Manager 密钥管理器 | / D-SECURITY-03 / Secret Manager / ❌ 不能建 / / 门禁: 需Vault/HSM硬件 / 密钥管理+轮换 / | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0304 | Access Controller 访问控制器 | / D-SECURITY-08 / Access Controller / ✅ 能建 / 📋 项目内有蓝图编号MOD-INF-018已建设 / RBAC+ABAC+最小权限 / | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0305 | LLM Security Gateway LLM安全网关 | / D-SECURITY-12 / LLM Security Gateway / ✅ 能建 / 📋 项目内有蓝图编号MOD-INF-014已建设 / 九层防御L0-L8 / | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0306 | M3-S01 | M3 S01 供应链漏洞扫描器 ❌ 不能建 门禁: 需SBOM基础设施+CVE数据库+供应链扫描工具 | D_SECURITY | harvest待评估（uncertain） |  |
| CAND-HARVEST-0307 | M3-S02 | M3 S02 恶意包检测器 ❌ 不能建 门禁: 需SBOM基础设施+CVE数据库+供应链扫描工具 恶 | D_SECURITY | harvest待评估（uncertain） |  |
| CAND-HARVEST-0308 | M3-S03 | M3 S03 代码混淆防护器 ❌ 不能建 门禁: 需SBOM基础设施+CVE数据库+供应链扫描工具 | D_SECURITY | harvest待评估（uncertain） |  |
| CAND-HARVEST-0309 | M3-S04 | M3 S04 完整性校验器 ❌ 不能建 门禁: 需SBOM基础设施+CVE数据库+供应链扫描工具 完 | D_SECURITY | harvest待评估（uncertain） |  |
| CAND-HARVEST-0310 | M3-S05 | M3 S05 VEX文档管理器 ❌ 不能建 门禁: 需SBOM基础设施+CVE数据库+供应链扫描工具 | D_SECURITY | harvest待评估（uncertain） |  |
| CAND-HARVEST-0311 | M3-S06 | M3 S06 供应链评分引擎 ❌ 不能建 门禁: 需SBOM基础设施+CVE数据库+供应链扫描工具 | D_SECURITY | harvest待评估（uncertain） |  |
| CAND-HARVEST-0312 | M3-S07 | M3 S07 许可证合规扫描器 ❌ 不能建 门禁: 需SBOM基础设施+CVE数据库+供应链扫描工具 | D_SECURITY | harvest待评估（uncertain） |  |
| CAND-HARVEST-0313 | M3-S08 | M3 S08 依赖锁定管理器 ❌ 不能建 门禁: 需SBOM基础设施+CVE数据库+供应链扫描工具 | D_SECURITY | harvest待评估（uncertain） |  |
| CAND-HARVEST-0314 | M3-NEW-01 | / M3-NEW-01 / Slopsquatting检测器 / ❌ 不能建 / / 门禁: 需SBOM基础设施+CVE数据库+供应链扫描工具+GNN/FAIR模型/攻击图 / AI幻觉包名检测 / | D_SECURITY | harvest待评估（likely_new） |  |
| CAND-HARVEST-0315 | M3-NEW-02 | / M3-NEW-01 / Slopsquatting检测器 / ❌ 不能建 / / 门禁: 需SBOM基础设施+CVE数据库+供应链扫描工具+GNN/FAIR模型/攻击图 / AI幻觉包名检测 / | D_SECURITY | harvest待评估（likely_new） |  |
| CAND-HARVEST-0316 | M3-NEW-03 | / M3-NEW-01 / Slopsquatting检测器 / ❌ 不能建 / / 门禁: 需SBOM基础设施+CVE数据库+供应链扫描工具+GNN/FAIR模型/攻击图 / AI幻觉包名检测 / | D_SECURITY | harvest待评估（likely_new） |  |
| CAND-HARVEST-0317 | M3-NEW-04 | / M3-NEW-01 / Slopsquatting检测器 / ❌ 不能建 / / 门禁: 需SBOM基础设施+CVE数据库+供应链扫描工具+GNN/FAIR模型/攻击图 / AI幻觉包名检测 / | D_SECURITY | harvest待评估（likely_new） |  |
| CAND-HARVEST-0318 | M3-NEW-05 | / M3-NEW-01 / Slopsquatting检测器 / ❌ 不能建 / / 门禁: 需SBOM基础设施+CVE数据库+供应链扫描工具+GNN/FAIR模型/攻击图 / AI幻觉包名检测 / | D_SECURITY | harvest待评估（likely_new） |  |
| CAND-HARVEST-0319 | M3-NEW-06 | / M3-NEW-01 / Slopsquatting检测器 / ❌ 不能建 / / 门禁: 需SBOM基础设施+CVE数据库+供应链扫描工具+GNN/FAIR模型/攻击图 / AI幻觉包名检测 / | D_SECURITY | harvest待评估（likely_new） |  |
| CAND-HARVEST-0320 | M3-NEW-07 | / M3-NEW-01 / Slopsquatting检测器 / ❌ 不能建 / / 门禁: 需SBOM基础设施+CVE数据库+供应链扫描工具+GNN/FAIR模型/攻击图 / AI幻觉包名检测 / | D_SECURITY | harvest待评估（likely_new） |  |
| CAND-HARVEST-0321 | M3-NEW-08 | / M3-NEW-01 / Slopsquatting检测器 / ❌ 不能建 / / 门禁: 需SBOM基础设施+CVE数据库+供应链扫描工具+GNN/FAIR模型/攻击图 / AI幻觉包名检测 / | D_SECURITY | harvest待评估（likely_new） |  |
| CAND-HARVEST-0322 | M3-NEW-09 | / M3-NEW-01 / Slopsquatting检测器 / ❌ 不能建 / / 门禁: 需SBOM基础设施+CVE数据库+供应链扫描工具+GNN/FAIR模型/攻击图 / AI幻觉包名检测 / | D_SECURITY | harvest待评估（likely_new） |  |
| CAND-HARVEST-0323 | M3-NEW-10 | / M3-NEW-01 / Slopsquatting检测器 / ❌ 不能建 / / 门禁: 需SBOM基础设施+CVE数据库+供应链扫描工具+GNN/FAIR模型/攻击图 / AI幻觉包名检测 / | D_SECURITY | harvest待评估（likely_new） |  |
| CAND-HARVEST-0324 | M1-NEW-07 | / M3-NEW-05 / GNN恶意依赖检测器 / ❌ 不能建 / / 门禁: 需SBOM基础设施+CVE数据库+供应链扫描工具+GNN/FAIR模型/攻击图 / GNN检测 / | D_SECURITY | harvest待评估（likely_new） |  |
| CAND-HARVEST-0474 | 数据安全与合规 Data Security & Compliance | ║  │ 🆕Data Observability五维度映射(Freshness/Volume/Schema/Distribution/     │  ║ | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0572 | 四级数据分类 Four-tier Data Classification | L1公开/L2内部/L3机密/L4绝密 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0573 | RBAC访问控制 RBAC Access Control | Trader/RiskMgr/Researcher/Admin/AI Agent/Compliance角色 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0574 | 加密体系 Encryption System | TLS 1.3+AES-256-GCM+字段加密+备份加密 | D_SECURITY | harvest待评估（likely_new） |  |
| CAND-HARVEST-0575 | AI脱敏管道 AI Desensitization Pipeline | 原始数据→分类识别→脱敏处理→审计记录 | D_SECURITY | harvest待评估（likely_new） |  |
| CAND-HARVEST-0576 | 审计日志 Audit Log | 交易≥7年/决策≥3年/数据访问≥1年/AI调用≥1年/系统变更≥1年 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0612 | Audit Trail 不可变审计轨迹 | 密码学完整性保证+防篡改审计链 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0866 | Agent Security Module Agent安全模块 | Agent安全模块对抗韧性+串谋检测(9种)+涌现检测+幻觉防护+红队对抗(6维度) | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0867 | Insider Trading Prevention 内幕交易防护 | 内幕交易防护数据分级+信息隔离墙Ethical Wall+交易行为监控 | D_SECURITY | harvest待评估（likely_new） |  |
| CAND-HARVEST-0868 | API Security Gateway API安全网关 | API安全网关四层架构(路由/认证/限流/审计)+API密钥轮换+速率限制 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0904 | LLM Security LLM安全网关 | LLM安全网关(九层防御+输入/输出过滤+Prompt注入防护) | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1001 | Audit Log Protector 审计日志保护器 | 审计日志不可篡改+完整性 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1002 | MCP Sandbox Execution Isolator MCP沙箱执行隔离器 | MCP执行隔离+沙箱+审计 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1003 | L0 Supply Chain SHA256 Verifier L0供应链SHA256验证器 | pip hash+requirements.txt锁定+完整性验证 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1004 | Code Security Auto Scanner 代码安全自动扫描器 | SAST工具Bandit/Semgrep+CI/CD集成 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1005 | Dependency Vulnerability Auto Detector 依赖漏洞自动检测器 | CVE数据库比对Safety/pip-audit | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1006 | Vendor Risk Scorer 供应商风险评分器 | 供应商安全评分卡 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1007 | Vendor Security Assessor 供应商安全评估器 | 供应商系列5项之一安全评估器 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1008 | Vendor Compliance Checker 供应商合规检查器 | 供应商系列5项之二合规检查器 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1009 | Vendor Incident Tracker 供应商事件追踪器 | 供应商系列5项之三事件追踪器 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1010 | Vendor Risk Assessor 供应商风险评估器 | 供应商系列5项之四风险评估器 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1011 | Vendor Report Generator 供应商报告生成器 | 供应商系列5项之五报告生成器 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1012 | Dependency Penetration Mapper 依赖穿透映射器 | 供应商扩展3项之一依赖穿透映射 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1013 | SLA Compliance Monitor SLA合规监控器 | 供应商扩展3项之二SLA合规监控 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1014 | Security Certification Verifier 安全认证验证器 | 供应商扩展3项之三安全认证验证 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1015 | Vendor Risk Quantifier 供应商风险量化器 | 量化供应商风险影响 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1016 | Security Scan Compliance Checker 安全扫描合规检查器 | 检查安全扫描覆盖率 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1017 | Fail-Closed Policy Manager 失败关闭策略管理器 | 安全检查失败时默认拒绝 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1018 | Financial Security Compliance Checker 金融安全合规检查器 | 金融行业安全合规检查 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1019 | OPA/Rego Engine OPA/Rego引擎 | OPA/Rego系列6项之一引擎 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1020 | Policy Definer 策略定义器 | OPA/Rego系列6项之二定义器 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1021 | Policy Executor 策略执行器 | OPA/Rego系列6项之三执行器 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1022 | Policy Auditor 策略审计器 | OPA/Rego系列6项之四审计器 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1023 | Policy Version Manager 策略版本管理器 | OPA/Rego系列6项之五版本管理器 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1024 | Policy Conflict Detector 策略冲突检测器 | OPA/Rego系列6项之六冲突检测器 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1025 | AI Agent Dependency Sandbox AI Agent依赖沙箱 | Agent运行时隔离 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1026 | L4 Agent Security Permission Isolator L4 Agent安全权限隔离器 | Agent权限边界执行 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1027 | AI Writable Permission Controller AI可写权限控制器 | Agent可修改路径白名单 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1028 | AI Code Modification Auditor AI代码修改审计器 | Agent代码修改审计追踪 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1029 | AI Read-Only Permission Executor AI只读权限执行器 | Agent只读操作权限控制 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1030 | Data Source API Key Security Storage 数据源API密钥安全存储器 | API密钥加密存储+访问控制 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1031 | Agent Communication Encryptor Agent间通信加密器 | Agent间通信加密 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1032 | Agent Behavior Baseline Learner Agent行为基线学习器 | Agent正常行为基线自动学习 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1033 | Agent Permission Dynamic Shrinker Agent权限动态收缩器 | 基于行为模式动态收缩Agent权限 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1034 | Agent Output Content Filter Agent输出内容过滤器 | Agent输出敏感信息过滤 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1035 | Vulnerability Scanner 漏洞扫描器 | 漏洞扫描+CVE比对+修复建议 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1036 | Security Incident Responder 安全事件响应器 | 安全事件响应+处置+恢复 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1037 | Red-Blue Team Verifier 红蓝对抗验证器 | 红蓝对抗+安全验证+报告 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1038 | Simplified Unified Authentication System 简化统一认证系统 | 统一认证+单点登录+MFA | D_SECURITY | harvest待评估（likely_new） |  |
| CAND-HARVEST-1039 | Attack Behavior Auto Blocker 攻击行为自动阻断器 | 攻击行为自动阻断+隔离+告警 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1040 | End-to-End Data Encryption and Access Controller 数据端到端加密与访问控制器 | 端到端加密+访问控制+密钥管理 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1041 | Data Encryption and Masking Processor 数据加密与脱敏处理器 | 数据加密+脱敏+差分隐私 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1042 | Casbin RBAC Permission Controller Casbin RBAC权限控制器 | Casbin RBAC+策略+执行 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1043 | Operation Audit Log System 操作审计日志系统 | 操作审计+日志+不可篡改 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1044 | Data Access Controller 数据访问控制器 | 数据访问控制+RBAC+审计 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1045 | Security Incident Responder Execution Layer 安全事件响应器执行层 | 安全事件响应执行层+自动化处置 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1046 | Role Permission Inheritance 角色权限继承 | 角色继承+权限传递+冲突检测 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1047 | Dynamic Permission Allocation 动态权限分配 | 动态权限+ABAC+条件分配 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1048 | Permission Change Audit 权限变更审计 | 权限变更审计+记录+告警 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1049 | Log Integrity Verification 日志完整性验证 | 日志完整性验证 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1183 | Security Awareness Trainer 安全意识培训器 | 安全意识培训门禁未满足 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1184 | Zero Trust Architect 零信任架构师 | 零信任架构设计源文件未详述 | D_SECURITY | harvest待评估（likely_new） |  |
| CAND-HARVEST-1185 | Content Fingerprint Generator Verifier 内容指纹生成验证器 | SHA-256内容指纹+完整性验证 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1186 | MCP Document Compliance Checker MCP文档合规检查器 | MCP协议文档合规性检查 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1187 | Authentication Failure Handler 认证失败处理器 | 防暴力破解+账户锁定策略 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1188 | Model File Path Security Checker 模型文件路径安全性检查器 | 路径穿越防护+模型文件完整性 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1189 | Log Injection Protection 日志注入防护 | 日志内容过滤+注入模式检测 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1190 | IP Whitelist Manager IP白名单管理 | 出站IP白名单管理HB-SEC-01执行层 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1191 | Network Isolation Policy 网络隔离策略 | 网络隔离策略D-INFRA域 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1192 | Knowledge Access Control 知识访问控制 | 知识库按数据分级访问控制 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1193 | Security Audit Event Aggregator 安全审计事件聚合器 | 安全事件聚合+关联分析 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1194 | Security Domain Config Hot-Update Adapter 安全域配置热更新适配器 | 安全策略热更新+审计记录 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1195 | Security Domain Monitoring Metric Collection Adapter 安全域监控指标采集适配器 | Prometheus安全指标采集 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1196 | Security Audit Log Archive and Retention Manager 安全审计日志归档与保留管理器 | 日志分级归档+7年保留策略 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1197 | eBPF Security Manager eBPF安全管理器 | eBPF网络安全策略执行门禁未满足 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1769 | Data Masking & Privacy 数据脱敏与隐私 | v1→v2映射至SEC-002 InputOutputGuard；项目内有蓝图MOD-INF-014已建设 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1770 | Input Detection/Auth/Scan 输入检测/认证/扫描等 | v1 D-SECURITY-29~46共18项，v2按职责归入SEC-002/007/008/009 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1865 | InputOutputGuard 输入输出防护 | 输入输出防护：输入清洗/输出过滤/路径守卫/Native API守卫;九层防御L1+L3层 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1866 | PromptProtection 提示词防护 | 提示词注入防护：DAN/角色扮演/ignore注入模式检测;九层防御L2提示词保护层 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1867 | AgentSandbox Agent沙箱隔离 | Agent沙箱隔离：进程沙箱/代码执行隔离/资源限制/执行超时;九层防御L2a层 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1868 | MultiAgentSecurity 多Agent安全 | 多Agent安全：Agent间共谋检测/权限隔离/冲突解决;九层防御L4+L8层 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1869 | SupplyChainSecurity 供应链安全 | 供应链安全：依赖漏洞扫描/CVE比对/SBOM管理/SHA256校验;九层防御L0供应链层 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1870 | KeySecretManager 密钥管理 | 密钥层级管理：密钥存储/轮换/访问控制/泄露检测/密钥审计;SSOT单一真相源守卫 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1871 | SelfProtection 自保护 | 自保护：对抗性变异检测/代码完整性校验/自我验证/隔离保护;九层防御L5-L7层 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1872 | ACLGuard 访问控制 | 访问控制：RBAC/ABAC/权限守卫/Kill Switch;身份管理/意图绑定;治理桥接 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1900 | AI Construction Governor AI代码质量门控 | AI生成因子公式Hash校验+回归截断+值域偏差预警 | D_SECURITY | harvest待评估（likely_new） |  |
| CAND-HARVEST-1901 | Non-AI Module Boundary Guard AI/non-AI模块边界守卫 | AI模块与non-AI模块边界明确划分AI权重≤30% | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1903 | Look-Ahead Bias Detector 前视偏差检测器 | 时序数据前视偏差自动检测与PIT门控联动 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1943 | 安全与治理 Security & Governance | 知识来源追溯+模块变更审计+自动操作日志+人工审批节点 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2045 | Kill Switch 紧急停机开关 | 独立于学习系统的硬开关可立即暂停所有学习系统操作 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2046 | Agent漂移检测 Agent Drift Detection | 监控LLM Agent的决策模式与设计意图的偏差KL散度检测 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2047 | NIST AI 100-5参考框架 NIST AI 100-5 Reference Framework | 三层安全架构:行为约束(预防)/行为监控(检测)/行为恢复(响应) | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2048 | Agent能力评估协议 Agent Capability Assessment Protocol | 定期评估Agent的能力边界评估结果纳入漂移检测基线 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2049 | 群集行为风险防护 Cluster Behavior Risk Protection | 监控本系统模块与行业主流模型的相关性>0.7自动增加差异化 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2073 | TEE可信执行环境 TEE Trusted Execution Environment | / R-35 / TEE可信执行环境 / ❌ / 硬边界约束二（单机Windows，无TEE硬件） / SGX/TDX硬件+Linux就绪 / | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2077 | Formal Verification形式化验证 Formal Verification | / R-39 / Formal Verification形式化验证 / ❌ / 硬边界约束二（SMT求解器需专业工具链） / Z3/PySMT集成+形式化验证专家就绪 / | D_SECURITY | harvest待评估（likely_new） |  |
| CAND-HARVEST-2143 | Communication Security 通信安全 | 通信安全身份认证消息完整性审计追踪 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2188 | Agent Mesh Cryptographic Identity Agent Mesh密码学身份 | / Agent Mesh (密码学身份) / Agent Card DID标识 / Agent ID + 启动时注册哈希（MVP简化版），未来升级Ed25519 / | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2194 | Behavior Pattern Testing 行为模式测试 | 行为模式测试个体多样性团队多样性串谋检测涌现检测漂移检测 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2210 | Crypto-Shredding 加密粉碎 | Crypto-Shredding数据保密性不等于数据完整性加密个人数据独立密钥哈希链基于密文销毁密钥即GDPR合规 | D_SECURITY | harvest待评估（likely_new） |  |
| CAND-HARVEST-2233 | Dependency Graph ZK Proof 依赖图ZK证明 | / 依赖图ZK证明(证明合规但不暴露证据内容) / ❌受限 / GATE-004/006 / | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2235 | Log Independent Encryption Infrastructure 日志独立加密基础设施 | 日志独立加密基础设施AES-256-GCM建设状态可建 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2236 | Key Destruction 密钥销毁 | / 密钥销毁+销毁证书+被遗忘权响应 / ❌受限 / GATE-004/GATE-006激活 / | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2269 | PromptGuard 2 PromptGuard 2越狱检测 | > **LlamaFirewall (Meta, 2025)对标**：三护栏架构——PromptGuard 2(越狱检测BERT模型)、Agent Alignment Checks(链式思维审计，检测提示注入+目标错位)、CodeShiel | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2270 | Agent Alignment Checks Agent对齐检查 | > **LlamaFirewall (Meta, 2025)对标**：三护栏架构——PromptGuard 2(越狱检测BERT模型)、Agent Alignment Checks(链式思维审计，检测提示注入+目标错位)、CodeShiel | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2271 | CodeShield CodeShield代码盾 | > **LlamaFirewall (Meta, 2025)对标**：三护栏架构——PromptGuard 2(越狱检测BERT模型)、Agent Alignment Checks(链式思维审计，检测提示注入+目标错位)、CodeShiel | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2286 | OAuth 2.0 OAuth 2.0认证 | > **设计哲学**：参考Google A2A Protocol（2025.1版本支持WebSocket/SSE流式传输+OAuth 2.0认证+状态回滚） (2025年4月)，适配本系统单机部署场景。A2A协议定义Agent间的能力发现、 | D_SECURITY | harvest待评估（likely_new） |  |
| CAND-HARVEST-2291 | DID Decentralized Identifier DID去中心化标识符 | DID Decentralized Identifier去中心化标识符Agent密码学身份LP-010 | D_SECURITY | harvest待评估（likely_new） |  |
| CAND-HARVEST-2292 | Zero-Knowledge Proof 零知识证明 | 零知识证明L3外部可验证性Merkle根锚定外部时间戳权威+选择性披露 | D_SECURITY | harvest待评估（likely_new） |  |
| CAND-HARVEST-2293 | Crypto-Shredding 密码粉碎 | Crypto-Shredding数据保密性加密个人数据独立密钥销毁密钥即GDPR合规 | D_SECURITY | harvest待评估（likely_new） |  |
| CAND-HARVEST-2294 | AES-256-GCM AES-256-GCM加密 | AES-256-GCM加密日志独立加密基础设施可建 | D_SECURITY | harvest待评估（likely_new） |  |
| CAND-HARVEST-2339 | Memory Security Constraints 记忆安全约束 | 记忆安全约束5项敏感数据不入记忆到记忆不可篡改到记忆访问控制到记忆一致性到记忆恢复 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2364 | Security Constraints 安全约束 | 安全约束5项审批记录纳入审计报告须保持完整性到治理日志须含策略变更历史到治理策略存储不可变到监管报送审批记录须含human_approval字段到B-016禁止AI自动清理未归档交易日志和审计记录 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2397 | Crypto-Shredding Key Destruction Restricted Crypto-Shredding密钥销毁受限 | / ❌受限 / D-REPORTING-02(多因子归因+策略退化检测)→D-FACTOR; D-REPORTING-03(LLM摘要)→LLM服务; D-REPORTING-03(Crypto-Shredding)→GATE-004/00 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2409 | Observability Security Constraints 可观测性安全约束 | 可观测性安全约束5项敏感数据不入Trace+Trace不可篡改哈希链+Trace访问控制角色限制+Trace存储合规≥7年+可观测性开销限制<5% | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2447 | Insider Trading Protection 内幕交易防护 | 数据分级+信息隔离墙Ethical Wall+交易行为监控 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2578 | Ethical Wall 信息隔离墙 | 数据访问控制+通信隔离+行为监控防止内幕信息流向交易决策方 | D_SECURITY | harvest待评估（likely_new） |  |
| CAND-HARVEST-2579 | Watch List 观察名单 | 包含存在内幕信息风险的证券列表加强监控但不限制交易 | D_SECURITY | harvest待评估（likely_new） |  |
| CAND-HARVEST-2580 | Restricted List 限制名单 | 包含已确认内幕信息的证券列表禁止交易硬阻断 | D_SECURITY | harvest待评估（likely_new） |  |
| CAND-HARVEST-2581 | Trading Behavior Monitoring 交易行为监控 | 异常交易模式检测+内幕交易信号指标+自动告警 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2582 | AI Driven Insider Trading Monitoring AI驱动内幕交易监控 | LLM语义分析替代纯规则匹配 | D_SECURITY | harvest待评估（likely_new） |  |
| CAND-HARVEST-2583 | Compliance Framework Comprehensive Benchmark 合规框架综合对标 | 跨架构合规对标覆盖§2-§7多层 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2584 | Compliance Security Module Completion 合规安全模块补全 | 源自A5安全架构§15.9合规安全模块补全 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2608 | IAM Access Control IAM与访问控制 | RBAC+ABAC+一人开发场景+Agent身份与权限 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2609 | Key Layer Management 密钥层级管理 | / 密钥层级管理（三层MK/DK/SK+Shamir 2-of-3+PQC后量子迁移路线） / 风险度量（→A4） / | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2610 | Audit Chain 审计链 | SHA-256哈希链+Merkle树+不可篡改操作日志 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2611 | Agent Security Agent安全 | 对抗韧性+串谋检测9种+涌现检测+幻觉防护 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2658 | Security Domain Division 安全域划分 | 交易域/数据域/治理域/运维域+跨域交互规则 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2659 | Defense in Depth 6 Layer 纵深防御6层 | / 纵深防御6层（含L3 LLM 4层guardrails+MCP Triple Gate+合规框架综合对标） / 治理审批流（→A2） / | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2698 | L2 L3 Data Access Audit L2/L3数据访问审计 | 数据访问审计所有L2/L3数据访问操作记录写入审计链 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2699 | Access Record 审计记录 | 数据访问审计包含访问者身份/时间/数据类型/访问目的 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2700 | Abnormal Access Pattern Detection 异常访问模式检测 | 数据访问审计非交易时段访问/异常频率/异常范围 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2701 | Daily Data Access Report 每日数据访问报告 | 数据访问审计每日生成Trader审查 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2702 | Cross Wall Request 跨墙请求 | 跨墙审批程序需要使用内幕信息的人员/Agent提交 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2703 | Restricted List Check 限制名单检查 | 跨墙审批程序在限制名单上的证券直接阻断 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2704 | Data Classification Determination 数据分级判定 | 跨墙审批程序L2及以下vs L3绝密分级 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2705 | L2 Auto Approval L2自动审批 | 跨墙审批程序L2及以下自动审批+事后审计 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2706 | L3 Manual Approval L3人工审批 | 跨墙审批程序L3绝密合规审查+Trader人工审批 | D_SECURITY | harvest待评估（likely_new） |  |
| CAND-HARVEST-2707 | Temporary Cross Wall Authorization 临时跨墙授权 | 跨墙审批程序审批通过后授予临时访问权限 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2708 | Wall Personnel Management 墙上人员管理 | 跨墙审批程序跨墙期间行为受到额外监控 | D_SECURITY | harvest待评估（likely_new） |  |
| CAND-HARVEST-2709 | Cross Wall End 跨墙结束 | 跨墙审批程序授权到期或任务完成后自动撤销 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2710 | Wall Personnel Extra Monitoring 墙上人员额外监控 | 墙上人员管理跨墙期间所有操作受到额外监控 | D_SECURITY | harvest待评估（likely_new） |  |
| CAND-HARVEST-2711 | Wall Personnel Discussion Ban 墙上人员禁止讨论 | 墙上人员管理禁止与交易决策方讨论跨墙信息 | D_SECURITY | harvest待评估（likely_new） |  |
| CAND-HARVEST-2712 | Wall Personnel Communication Audit 墙上人员通信审计 | 墙上人员管理通信记录额外审计 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2713 | Cross Wall Audit Chain 跨墙操作审计链 | 墙上人员管理跨墙操作记录写入审计链保留7年 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2714 | Pre Announcement Trading 重大公告前交易检测 | 异常交易模式检测交易时间vs公告时间比对 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2715 | Abnormal Profit 异常盈利检测 | 异常交易模式检测交易盈利率vs市场平均 | D_SECURITY | harvest待评估（likely_new） |  |
| CAND-HARVEST-2716 | Related Trading 关联交易检测 | 异常交易模式检测交易标的与信息获取关联 | D_SECURITY | harvest待评估（likely_new） |  |
| CAND-HARVEST-2717 | Timing Anomaly 时序异常检测 | 异常交易模式检测交易时序与信息时序比对 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2718 | Volume Price Anomaly 量价异常检测 | 异常交易模式检测交易量/价格vs历史分布 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2719 | Pre Announcement Position Rate 公告前建仓率 | 内幕交易信号指标公告前5日建仓次数/总建仓次数 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2720 | Abnormal Profit Rate 异常盈利率 | 内幕交易信号指标超额收益率超过市场3σ的比例 | D_SECURITY | harvest待评估（likely_new） |  |
| CAND-HARVEST-2721 | Info Trading Time Lag 信息-交易时滞 | 内幕交易信号指标信息获取到交易的平均时间 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2722 | Restricted List Trigger Rate 限制名单触发率 | 内幕交易信号指标触发限制名单的次数/总交易次数 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2723 | Auto Alert and Manual Review 自动告警与人工审查 | 内幕交易防护检测到异常交易模式时立即向Trader告警 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2735 | Monitoring Response 监控与响应 | / 监控与响应 / 5 / 5/5 / 无（行为异常检测+串谋检测+审计链+事件响应6阶段+KILLSWITCH） / | D_SECURITY | harvest待评估（likely_new） |  |
| CAND-HARVEST-2865 | Vendor Risk 供应商风险 | A5功能域安全模块补全供应商风险 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2872 | 模型运行层 Model Runtime Layer | 工具调用验证+参数校验+上下文隔离+温度控制 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2873 | 输出审查层 Output Review Layer | 输出分类+敏感信息检测+指令提取验证+幻觉检测 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2874 | 权限与审计层 Permission and Audit Layer | 最小权限+操作审计+实时阻断+工具调用监控 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2875 | 交易指令数据密钥 Trading Data Key | 保护交易指令订单数据L3月度轮换 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2876 | 策略参数数据密钥 Strategy Data Key | 保护策略参数因子公式L3月度轮换 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2877 | 持仓数据密钥 Position Data Key | 保护持仓数据盈亏数据L2季度轮换 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2878 | 因子数据密钥 Factor Data Key | 保护因子值信号数据L2季度轮换 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2879 | 审计日志数据密钥 Audit Data Key | 保护审计日志L2季度轮换 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2880 | 系统配置数据密钥 Config Data Key | 保护系统配置L2季度轮换 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2881 | 行情数据密钥 Market Data Key | 保护行情数据L1半年轮换 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2882 | 主密钥 Master Key | / 主密钥(MK) / 1 / RSA-4096（PQC迁移见§4.4；双重用途演进见DEC-SEC-06） / 加密DK+签名审计日志（双重用途，见§5.1/DEC-SEC-06） / Shamir 2-of-3分割存储 / 年度轮换 / | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2883 | 数据密钥 Data Key | AES-256-GCM加密业务数据MK加密保护 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2884 | 会话密钥 Session Key | AES-256-GCM/ECDH加密临时通信DK派生 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2885 | Network and Physical Layer 网络 | 网络分段+出站白名单+进程级微隔离+TLS 1.3强制加密 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2886 | Host and OS Layer 主机与操作系统层 | Windows安全基线+端口最小化+补丁管理+凭证保护 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2887 | Application and API Layer 应用与API层 | 输入验证+API安全+LLM调用安全+供应链安全 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2888 | Data Layer 数据层 | 加密策略+数据分级与脱敏+DLP+PIT数据保护 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2889 | Identity and Access Layer 身份与访问层 | Zero Trust核心原则+RBAC+ABAC+Agent身份管理+最小权限 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2890 | Monitoring and Response Layer 监控响应 | 安全事件检测+SIEM+事件响应6阶段+红队演练 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2891 | IAM与访问控制 IAM and Access Control | RBAC 4角色+ABAC策略引擎+Agent身份注册认证权限边界 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2892 | 密钥层级管理 Key Hierarchy Management | MK→DK→SK三层+Shamir 2-of-3分割+PQC三阶段迁移 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2893 | 审计链 Audit Chain | SHA-256哈希链+Merkle树每1000条+6W日志规范+7年交易日志保留 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2894 | Agent安全 Agent Security | 4层guardrails+串谋9种探测+涌现+目标偏移检测+幻觉防护+记忆投毒6层防御 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2895 | 内幕交易防护 Insider Trading Protection | 4级数据分类+信息隔离墙+观察名单/限制名单+跨墙审批+交易行为监控 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2896 | Trader 交易员 | 人类交易决策者审批策略确认异常交易管理数据源 | D_SECURITY | harvest待评估（likely_new） |  |
| CAND-HARVEST-2897 | AI_Agent | 执行交易策略数据处理信号生成最小权限严格沙箱 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2898 | System 系统 | 日志写入健康检查密钥轮换服务级权限无业务操作 | D_SECURITY | harvest待评估（likely_new） |  |
| CAND-HARVEST-2899 | ABAC策略引擎 ABAC Policy Engine | 属性定义+动态访问决策+交易时段特殊策略+KILLSWITCH.md对标 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2900 | Peak Suspicion 峰值怀疑 | 分析Agent内部状态识别可疑度峰值 | D_SECURITY | harvest待评估（likely_new） |  |
| CAND-HARVEST-2901 | Deception Split 欺骗分割 | 比较Agent内部推理和外部输出检测不一致 | D_SECURITY | harvest待评估（likely_new） |  |
| CAND-HARVEST-2902 | Correlation 相关性 | 分析多个Agent输出之间的统计相关性检测异常协调 | D_SECURITY | harvest待评估（likely_new） |  |
| CAND-HARVEST-2903 | Ensemble 集成 | 综合3种探测技术结果使用加权投票或ML模型集成判断 | D_SECURITY | harvest待评估（likely_new） |  |
| CAND-HARVEST-2904 | Graph 图谱 | 构建Agent交互图分析图结构特征检测异常通信模式 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2905 | Gap Ratio 缺口比率 | 计算最高欺骗分数与次高欺骗分数的比值 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2906 | Collective Score 核心 | 将所有Agent的欺骗分数求和/求均值 | D_SECURITY | harvest待评估（likely_new） |  |
| CAND-HARVEST-2907 | Pairwise Correlation 成对相关性 | 计算每对Agent激活值的相关系数 | D_SECURITY | harvest待评估（likely_new） |  |
| CAND-HARVEST-2908 | Behavior Trajectory Similarity 行为轨迹相似度 | 比较Agent间的行为序列使用编辑距离衡量相似度 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2909 | Steganography Communication Detection 图谱 | 通信内容统计特征分析+通信容量分析+通道容量限制 | D_SECURITY | harvest待评估（likely_new） |  |
| CAND-HARVEST-2910 | Identity Rotation and Anonymization 身份轮换与匿名化 | 定期轮换Agent的协作伙伴防止稳定串谋伙伴关系 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2911 | Whistleblower Agent 举报代理 | 部署专门的监控Agent监控其他Agent的可疑行为 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2912 | Goal Drift Detection 目标漂移检测 | 步数检查点+目标偏移评分+长链执行限制+偏移恢复 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2913 | Fact Checking 事实核查 | 交易相关输出与行情数据交叉验证+数值输出与历史统计分布比对 | D_SECURITY | harvest待评估（likely_new） |  |
| CAND-HARVEST-2914 | Consistency Check 一致性检查 | 时间一致性+上下文一致性+跨Agent一致性 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2915 | Confidence Scoring Mechanism 置信度评分机制 | 每个LLM输出附带置信度评分0.0-1.0 | D_SECURITY | harvest待评估（likely_new） |  |
| CAND-HARVEST-2916 | Red Team Adversarial Framework 红队对抗框架 | 提示词注入+串谋+涌现+幻觉+越权+记忆投毒6维度测试 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2917 | Input Provenance Tagging 标签 | 所有记忆条目必须附带来源标记不可被Agent修改 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2918 | Write-time Validation 写入时验证 | 记忆写入时进行内容过滤拦截指令性模式 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2919 | Session-scoped Memory 内存 | 默认记忆为会话级会话结束后自动清除 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2920 | Trust-aware Retrieval 信任感知检索 | 记忆检索时计算复合信任评分 | D_SECURITY | harvest待评估（likely_new） |  |
| CAND-HARVEST-2921 | Memory Audit 内存审计 | 每日自动审计所有持久化记忆条目 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2922 | Memory Integrity Check 内存 | 持久化记忆条目附带SHA-256哈希签名 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2923 | Cross-wall Approval Procedure 跨墙审批流程 | 分级审批L2及以下自动L3人工+临时跨墙授权+墙上人员管理 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2924 | Abnormal Trading Pattern Detection 异常交易模式检测 | 重大公告前交易+异常盈利+关联交易+时序异常+量价异常 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2925 | AI-driven Insider Trading Monitoring 监控 | LLM语义分析替代纯规则匹配 | D_SECURITY | harvest待评估（likely_new） |  |
| CAND-HARVEST-2926 | WASM Sandbox Runtime WASM沙箱运行时 | Windows单机WASM运行时支持有限不能建 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2927 | Dependency Behavior eBPF Monitor 依赖行为eBPF监控器 | Windows不支持eBPF不能建 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2928 | Micro VM Isolator 微VM隔离器 | Firecracker需Linux KVM不能建 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2929 | mTLS Auto Generator mTLS自动生成器 | 单机部署无需mTLS不能建 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2944 | SIEM Security Information and Event Management 安全事件 | 日志集中收集+关联分析+告警规则+告警分级 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2945 | Six-stage Incident Response Process 响应标签 | 检测+分类+遏制+根除+恢复+复盘 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2946 | DLP Data Loss Prevention 事件 | 出站内容检查+敏感模式检测+剪贴板监控+文件操作监控 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2947 | PIT Data Protection PIT数据保护 | PIT数据标记+PIT隔离+PIT完整性+PIT审计 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2948 | Shamir Secret Sharing Shamir秘密共享 | 主密钥使用Shamir秘密共享算法分割为3个份额 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2949 | PQC Post-Quantum Cryptography Migration 图谱 | 三阶段迁移路线经典密码→混合模式→纯PQC | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2950 | Merkle Tree Structure Merkle树结构 | 每1000条日志构建一棵Merkle树SHA-256哈希作为叶子节点 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2951 | SHA-256 Hash Chain SHA-256哈希链 | 每条日志包含前一条日志的SHA-256哈希形成链式结构 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2952 | 6W Log Specification 6W日志规范 | WHO+WHAT+WHEN+WHERE+WHY+RESULT | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2953 | Merkle Inclusion Proof Merkle包含证明 | 验证单条日志是否属于某棵Merkle树 | D_SECURITY | harvest待评估（likely_new） |  |
| CAND-HARVEST-2954 | Blockchain Anchored Timestamp 区块链锚定时间戳 | 每棵Merkle树的根哈希锚定到公有链不能建 | D_SECURITY | harvest待评估（likely_new） |  |
| CAND-HARVEST-2955 | TEE Trusted Execution Environment 环境执行 | 单台PC无TEE硬件支持不能建 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2956 | FHE Fully Homomorphic Encryption 全量 | 计算开销1000-10000x单机性能不足不能建 | D_SECURITY | harvest待评估（likely_new） |  |
| CAND-HARVEST-2957 | FL Federated Learning FL联邦学习 | 需多方参与单人开发无协作方不能建 | D_SECURITY | harvest待评估（likely_new） |  |
| CAND-HARVEST-2958 | MPC Secure Multi-party Computation MPC安全多方计算 | 通信轮次多延迟高单机无多方需求不能建 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2959 | BLACKICE Red Team Toolkit BLACKICE红队工具包 | 容器化红队工具包14个精选开源工具Docker一键启动 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2960 | LLM Pentesting 5-layer Methodology LLM渗透测试5层方法论 | 输入输出层/检索层/工具调用层/模型层/运行时层 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2961 | AI-driven Automated Red Team AI驱动自动化红队 | AI赋能传统渗透全流程自动化 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2962 | Docker Container Docker容器 | 进程级隔离namespace+cgroup低风险开发测试 | D_SECURITY | harvest待评估（likely_new） |  |
| CAND-HARVEST-2963 | gVisor Container gVisor容器 | 系统调用拦截中风险任务 | D_SECURITY | harvest待评估（likely_new） |  |
| CAND-HARVEST-2964 | Firecracker microVM Firecracker微虚拟机 | 硬件级隔离独立内核高风险交易执行 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2965 | ISOLATEGPT hub-spoke ISOLATEGPT中心辐射 | 语义+技术双重隔离多Agent协作 | D_SECURITY | harvest待评估（likely_new） |  |
| CAND-HARVEST-2979 | 安全域规则目录 Security Domain Rule Catalog | 访问控制审计加密漏洞 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3063 | 审计日志完整性 Audit Log Integrity | 日志记录完整率 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3075 | NVIDIA AI Red Team 2026 NVIDIA AI红队2026 | 沙箱化Agent工作流安全指南 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3076 | NIST CAISI 2025 | 红队竞赛13个前沿模型250K+攻击 | D_SECURITY | harvest待评估（likely_new） |  |
| CAND-HARVEST-3077 | AAAI 2026 FinJailbreak AAAI 2026金融越狱 | 金融AI Agent红队测试FCFT | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3078 | SOC 2 Type II for AI AI SOC 2 Type II认证 | AICPA信任服务标准扩展到AI | D_SECURITY | harvest待评估（likely_new） |  |
| CAND-HARVEST-3403 | FCFT金融宪法微调 FCFT Financial Constitution Fine-Tuning | / 金融治理越狱(FinJailbreak) / 领域特定对抗提示→绕过安全对齐 / SOTA模型显著脆弱 / FCFT(金融宪法微调)嵌入金融法规→漏洞降低>55% / | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3431 | llm_security/gateway.py LLM安全网关入口 | SEC-001已有代码映射AISG网关核心入口 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3432 | llm_security/protocol.py LLM安全协议定义 | SEC-001已有代码映射AISG协议层 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3433 | l0_supply_chain.py L0供应链安全 | SEC-001已有代码映射九层防御L0供应链层 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3434 | l8_multi_agent.py L8多Agent安全 | SEC-001已有代码映射九层防御L8多Agent层 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3435 | security_gateway_base.py 安全网关基类 | SEC-001已有代码映射L10合规网关基类 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3436 | default_security_gateway.py 默认安全网关 | SEC-001已有代码映射L10合规网关默认实现 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3437 | input_sanitizer.py 输入清洗器 | SEC-002已有代码映射输入清洗 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3438 | l1_input.py L1输入防御 | SEC-002已有代码映射L1输入防御层 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3439 | l3_output.py L3输出过滤 | SEC-002已有代码映射L3输出过滤层 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3440 | input_guard.py 输入守卫 | SEC-002已有代码映射agent_rbac输入守卫 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3441 | output_guard.py 输出守卫 | SEC-002已有代码映射agent_rbac输出守卫 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3442 | path_guard.py 路径守卫 | SEC-002已有代码映射agent_rbac路径守卫 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3443 | native_api_guard.py Native API守卫 | SEC-002已有代码映射Native API守卫 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3444 | false_completion_detector.py 虚假完成检测器 | SEC-002已有代码映射虚假完成检测 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3445 | shell_dialect_detector.py Shell方言检测器 | SEC-002缺口标记Shell方言检测属输入防护 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3446 | l2_prompt_protection.py L2提示词保护 | SEC-003已有代码映射L2提示词保护层 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3447 | injection_patterns.py 注入模式库 | SEC-003已有代码映射注入模式库 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3448 | vibe_coding_guard.py Vibe Coding防护 | SEC-003已有代码映射Vibe Coding防护 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3449 | cybersec_2026_guard.py 2026新型攻击防护 | SEC-003已有代码映射2026新型攻击防护 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3450 | novel_attack_guard.py 新型攻击防护 | SEC-003已有代码映射新型攻击防护 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3451 | rule_injection_guard.py 规则注入防护 | SEC-003已有代码映射规则注入防护 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3452 | context_drift_detector.py 上下文漂移检测器 | SEC-003缺口标记与提示词保护交叉偏向自保护 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3453 | process_sandbox.py 进程沙箱 | SEC-004已有代码映射进程沙箱 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3454 | l2a_process_sandbox.py L2a进程沙箱 | SEC-004已有代码映射L2a进程沙箱层 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3455 | rollback_sandbox.py 回滚沙箱 | SEC-004已有代码映射回滚沙箱 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3456 | cold_start_lock.py 冷启动锁 | SEC-004已有代码映射冷启动锁 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3457 | cascading_failure_isolator.py 级联故障隔离器 | SEC-004已有代码映射级联故障隔离 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3458 | dry_run.py 干运行 | SEC-004已有代码映射干运行 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3459 | engine_degradation.py 引擎降级 | SEC-004缺口标记降级是沙箱资源限制延伸 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3460 | l4_agent.py L4 Agent安全 | SEC-005已有代码映射L4 Agent安全层 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3461 | multi_agent_collusion_detector.py 多Agent共谋检测器 | SEC-005已有代码映射共谋检测 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3462 | replay_attack_guard.py 重放攻击防护 | SEC-005已有代码映射重放攻击防护 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3463 | toctou_guard.py TOCTOU防护 | SEC-005已有代码映射TOCTOU防护 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3464 | sequence_guard.py 序列守卫 | SEC-005已有代码映射序列守卫 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3465 | cross_session_detector.py 跨会话检测器 | SEC-005已有代码映射跨会话检测 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3466 | wireheading_prevention.py Wireheading防护 | SEC-005已有代码映射Wireheading防护 | D_SECURITY | harvest待评估（likely_new） |  |
| CAND-HARVEST-3467 | audit_trail/supply_chain_security.py 供应链安全审计 | SEC-006已有代码映射供应链安全审计 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3468 | dep_cve_correlator.py CVE关联器 | SEC-006已有代码映射CVE关联分析 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3469 | remote_attestation.py 远程证明 | SEC-006已有代码映射远程证明 | D_SECURITY | harvest待评估（likely_new） |  |
| CAND-HARVEST-3470 | security_config_scanner.py 安全配置扫描器 | SEC-006已有代码映射安全配置扫描 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3471 | key_hierarchy.py 密钥层级 | SEC-007已有代码映射密钥层级 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3472 | secrets_lifecycle.py 秘密生命周期 | SEC-007已有代码映射秘密生命周期 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3473 | shared/security/secrets.py 共享密钥 | SEC-007已有代码映射共享密钥 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3474 | ssot_guard.py SSOT守卫 | SEC-007已有代码映射SSOT单一真相源守卫 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3475 | secrets.py 秘密模式检测 | SEC-007已有代码映射秘密模式检测 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3476 | secret_rotation.py 密钥轮换 | SEC-007已有代码映射密钥轮换 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3477 | adversarial_mutator.py 对抗变异器 | SEC-008已有代码映射对抗变异 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3478 | code_integrity.py 代码完整性 | SEC-008已有代码映射代码完整性 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3479 | l7_validation.py L7验证 | SEC-008已有代码映射L7验证层 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3480 | isolation.py 隔离保护 | SEC-008已有代码映射隔离保护 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3481 | red_team_scanner.py 红队扫描器 | SEC-008已有代码映射红队扫描 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3482 | l5_resource_protection.py L5资源保护 | SEC-008已有代码映射L5资源保护层 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3483 | l6_observability.py L6可观测性 | SEC-008已有代码映射L6可观测层 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3484 | immutable_core.py 不可变核心 | SEC-008已有代码映射不可变核心 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3485 | integrity_self_check.py 完整性自检 | SEC-008已有代码映射完整性自检 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3486 | micro_verifier.py 微验证器 | SEC-008已有代码映射微验证器 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3487 | post_action_verifier.py 事后验证器 | SEC-008已有代码映射事后验证 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3488 | continuous_verifier.py 持续验证器 | SEC-008已有代码映射持续验证 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3489 | behavior_audit_logger.py 行为审计日志器 | SEC-008已有代码映射行为审计日志 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3490 | blind_spot_tracker.py 盲点追踪器 | - ⚠️ agent_rbac/blind_spot_tracker.py（盲点追踪）属于自保护范畴但偏向治理，应与D-GOVERNANCE协调 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3491 | kill_switch.py Kill Switch kill_switch.py紧急制动 | SEC-009已有代码映射Kill Switch紧急熔断 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3492 | permission_guard.py 权限守卫 | SEC-009已有代码映射权限守卫 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3493 | abac_guard.py ABAC守卫 | SEC-009已有代码映射ABAC守卫 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3494 | rbac_guard.py RBAC守卫 | SEC-009已有代码映射RBAC守卫 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3495 | derive_rbac_roles.py RBAC角色推导 | SEC-009已有代码映射RBAC角色推导 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3496 | permission_mode_manager.py 权限模式管理器 | SEC-009已有代码映射权限模式管理 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3497 | permission_hooks.py 权限钩子 | SEC-009已有代码映射权限钩子 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3498 | emergency_override.py 紧急覆盖 | SEC-009已有代码映射紧急覆盖 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3499 | escalation_handler.py 升级处理器 | SEC-009已有代码映射升级处理 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3500 | identity.py 身份管理 | SEC-009已有代码映射身份管理 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3501 | intent_binder.py 意图绑定 | SEC-009已有代码映射意图绑定 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3502 | defense_depth.py 防御纵深 | SEC-009已有代码映射防御纵深 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3503 | guard_layers.py 守卫层编排 | SEC-009已有代码映射守卫层编排 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3504 | approver_check.py 审批检查 | SEC-009已有代码映射治理桥接审批检查 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3505 | a2a_check.py A2A检查 | SEC-009已有代码映射治理桥接A2A检查 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3506 | capability_check.py 能力检查 | SEC-009已有代码映射治理桥接能力检查 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3507 | bootstrap_superadmin.py 超级管理员引导 | SEC-009已有代码映射治理桥接超级管理员引导 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3508 | capability.py 能力定义 | SEC-009已有代码映射共享能力定义 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3509 | audit_log_guard.py 审计日志守卫 | - ⚠️ agent_rbac/audit_log_guard.py（审计日志守卫）横跨ACL与审计，应与D-GOVERNANCE协调归属 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3510 | session_lifecycle.py 会话生命周期 | SEC-009缺口标记会话管理与D-AUT-CORE交叉 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3511 | session_concurrency.py 会话并发 | SEC-009缺口标记会话管理与D-AUT-CORE交叉 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3512 | non_repudiation.py 抗抵赖 | SEC-009缺口标记纳入ACLGuard抗抵赖 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3513 | memory_guard.py 内存守卫 | SEC-009缺口标记纳入ACLGuard内存保护 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3514 | memory_provenance_guard.py 内存来源守卫 | SEC-009缺口标记纳入ACLGuard内存保护 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3515 | canary_rollout_manager.py 金丝雀发布管理器 | SEC-004缺口标记金丝雀归SEC-004沙箱 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3516 | blueprint_fidelity.py 蓝图保真 | SEC-008缺口标记蓝图保真归SEC-008 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3517 | phase_executor.py 阶段执行器 | SEC-004缺口标记纳入AgentSandbox阶段执行 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3518 | observability.py 可观测性 | SEC-008缺口标记纳入SelfProtection | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3519 | risk_mitigation.py 风险缓解 | SEC-008缺口标记纳入SelfProtection | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3520 | 进程沙箱层 Process Sandbox Layer | 九层防御L2a代码执行隔离/资源限制/超时 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3521 | 可观测性层 Observability Layer | 九层防御L6行为审计/指标采集/告警 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3522 | 验证层 Validation Layer | 九层防御L7完整性自检/微验证器/红队扫描 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3523 | 多Agent安全层 Multi-Agent Security Layer | 九层防御L8共谋检测/跨会话防护 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3524 | shared/contracts/security模块包 shared contracts security | 场内已有模块1个SEC-009 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3525 | llm_security/dashboard 安全仪表盘 | SEC-001缺口标记安全仪表盘未在AISGGate子模块体现 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4241 | Microstructure Defense 微结构防御 | / microstructure_defense.py / governance/ / 微结构防御 / ❌ 属于D-SECURITY——微结构防御是安全域 / | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4835 | 4层guardrails 4-layer Guardrails | 安全架构-提示词注入防御4层guardrails详见A5§2.3 L3层定义 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4839 | BLACKICE 红队工具包 | / BLACKICE / Databricks (2026) / 容器化红队工具包，14个精选开源工具（Garak/Promptfoo/PyRIT/ART/Giskard等），统一CLI，Docker一键启动 / **能建**：Docker | D_SECURITY | harvest待评估（likely_new） |  |
| CAND-HARVEST-4840 | OWASP Gen AI Red Teaming Guide OWASP生成式AI红队指南 | / OWASP Gen AI Red Teaming Guide / OWASP (2025) / 全栈红队方法论：模型权重→训练数据→API端点→用户界面 / 已采纳为本系统红队框架基础 / | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4841 | LLM Pentesting 5层方法论 LLM Pentesting 5-layer Methodology | / LLM Pentesting 5层方法论 / Repello AI (2026) / 输入输出层/检索层/工具调用层/模型层/运行时层，30项检查清单 / **能建**：5层攻击面与本系统6层纵深防御天然对应 / | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4842 | AI驱动自动化红队 AI-driven Automated Red Team | 红队工具-行业趋势(2026)AI赋能传统渗透全流程自动化 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4844 | OWASP ASI 10类行为监控 OWASP ASI 10 Behavior Monitoring | / 行为风险(Behavioral) / Agent以非预期方式追求目标 / §15.4 OWASP ASI 10类行为监控+意图匹配 / | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4849 | 记忆投毒检测指标 Memory Poisoning Detection Metrics | 记忆投毒防御-记忆注入拦截率/可疑记忆比例/记忆-行为偏离度/持久化记忆增长率 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4850 | 注册流程 Registration Flow | Agent身份注册-Agent启动时向IAM服务注册获取唯一agent_id+Ed25519密钥对 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4851 | 认证流程 Authentication Flow | Agent身份认证-Agent每次操作前向IAM服务请求访问令牌+签名验证+ABAC策略 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4852 | 令牌管理 Token Management | Agent身份认证-访问令牌短期有效5分钟自动刷新 | D_SECURITY | harvest待评估（likely_new） |  |
| CAND-HARVEST-4863 | Vulnerability Fix Window Assessor 漏洞修复窗口评估器 | 漏洞修复窗口评估 | D_SECURITY | harvest待评估（likely_new） |  |
| CAND-HARVEST-4864 | AI Hallucination Package Name Guard AI幻觉包名防护 | AI幻觉包名防护 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4865 | SBOM Reachability Analyzer SBOM可达性分析器 | SBOM可达性分析 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4866 | Attack Surface Simulator 攻击面模拟器 | 攻击树杀伤链依赖混淆恶意包注入仿真 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4867 | AI Agent Dependency Security Sandbox AI Agent依赖安全沙箱 | Agent隔离权限边界资源限制WASM沙箱 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4869 | Financial Constitution Fine-Tuning 金融宪法微调 | 嵌入金融法规到模型权重降低FinJailbreak漏洞 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4875 | Zero-Knowledge Compliance Audit Layer 零知识合规审计层 | 可证明合规但不暴露策略细节的审计机制 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4876 | ZKP Proof Generator ZKP证明生成器 | 交易episode转换为ZK证明 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4877 | Shield Module Shield模块 | 不安全动作可行域投影保证零违规 | D_SECURITY | harvest待评估（likely_new） |  |
| CAND-HARVEST-4889 | CollusionDetection 串谋检测 | 行为相似度+时间窗口关联+统计显著性检验 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-5022 | Defense in Depth 6 Layers 纵深防御6层 | / — / 纵深防御6层 / 含L3 LLM 4层guardrails+MCP Triple Gate / ✅ / | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-5023 | Key Hierarchy Management 密钥层级管理 | / — / 密钥层级管理 / 三层MK/DK/SK+Shamir 2-of-3+PQC后量子迁移路线 / ✅ / | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-5024 | Vendor Risk Management 供应商风险管理 | 风险评估/合规检查/事件追踪/SLA监控10子模块 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-5025 | Data Access Audit 数据访问审计 | 数据访问日志+异常访问检测+权限变更追踪 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-5026 | Data Desensitization Engine 数据脱敏引擎 | 外部API传输脱敏+策略/持仓/因子数据过滤 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-5027 | Security Policy as Code 安全策略即代码 | OPA/Rego安全策略引擎+6子模块 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-5028 | Content Security 内容安全 | / — / 内容安全 / 内容指纹/MCP文档合规检查/模型文件路径安全性/知识访问控制 / ✅ / | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-5029 | Blockchain Anchoring 区块链锚定 | 审计链上链 | D_SECURITY | harvest待评估（likely_new） |  |
| CAND-HARVEST-5030 | TEE Trusted Execution Environment TEE可信执行环境 | 硬件不支持 | D_SECURITY | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-5031 | eBPF Kernel Monitoring eBPF内核监控 | Windows不支持+驱动风险 | D_SECURITY | harvest待评估（likely_new） |  |
| CAND-HARVEST-5032 | WASM Sandbox WASM沙箱 | 单机架构不需要 | D_SECURITY | harvest待评估（likely_implemented） |  |

## 复查时间表

> 按 next_review_date 升序。复查时重新过四问，触发信号命中则晋升到 depgraph 设计态。

| 下次复查 | 复查频率 | ID | 名称 | 域 | 状态 | 上次复查结论 |
|------|------|------|------|------|------|------|
| 2026-11-30 | quarterly | CAND-HARVEST-0302 | Identity & Access Manager 身份与访问管理器 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0303 | Secret Manager 密钥管理器 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0304 | Access Controller 访问控制器 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0305 | LLM Security Gateway LLM安全网关 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0306 | M3-S01 | D_SECURITY | 候选待评（candidate） | harvest待评估（uncertain） |
| 2026-11-30 | quarterly | CAND-HARVEST-0307 | M3-S02 | D_SECURITY | 候选待评（candidate） | harvest待评估（uncertain） |
| 2026-11-30 | quarterly | CAND-HARVEST-0308 | M3-S03 | D_SECURITY | 候选待评（candidate） | harvest待评估（uncertain） |
| 2026-11-30 | quarterly | CAND-HARVEST-0309 | M3-S04 | D_SECURITY | 候选待评（candidate） | harvest待评估（uncertain） |
| 2026-11-30 | quarterly | CAND-HARVEST-0310 | M3-S05 | D_SECURITY | 候选待评（candidate） | harvest待评估（uncertain） |
| 2026-11-30 | quarterly | CAND-HARVEST-0311 | M3-S06 | D_SECURITY | 候选待评（candidate） | harvest待评估（uncertain） |
| 2026-11-30 | quarterly | CAND-HARVEST-0312 | M3-S07 | D_SECURITY | 候选待评（candidate） | harvest待评估（uncertain） |
| 2026-11-30 | quarterly | CAND-HARVEST-0313 | M3-S08 | D_SECURITY | 候选待评（candidate） | harvest待评估（uncertain） |
| 2026-11-30 | quarterly | CAND-HARVEST-0314 | M3-NEW-01 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0315 | M3-NEW-02 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0316 | M3-NEW-03 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0317 | M3-NEW-04 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0318 | M3-NEW-05 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0319 | M3-NEW-06 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0320 | M3-NEW-07 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0321 | M3-NEW-08 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0322 | M3-NEW-09 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0323 | M3-NEW-10 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0324 | M1-NEW-07 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0474 | 数据安全与合规 Data Security & Compliance | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0572 | 四级数据分类 Four-tier Data Classification | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0573 | RBAC访问控制 RBAC Access Control | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0574 | 加密体系 Encryption System | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0575 | AI脱敏管道 AI Desensitization Pipeline | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0576 | 审计日志 Audit Log | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0612 | Audit Trail 不可变审计轨迹 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0866 | Agent Security Module Agent安全模块 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0867 | Insider Trading Prevention 内幕交易防护 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0868 | API Security Gateway API安全网关 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0904 | LLM Security LLM安全网关 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1001 | Audit Log Protector 审计日志保护器 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1002 | MCP Sandbox Execution Isolator MCP沙箱执行隔离器 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1003 | L0 Supply Chain SHA256 Verifier L0供应链SHA256验证器 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1004 | Code Security Auto Scanner 代码安全自动扫描器 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1005 | Dependency Vulnerability Auto Detector 依赖漏洞自动检测器 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1006 | Vendor Risk Scorer 供应商风险评分器 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1007 | Vendor Security Assessor 供应商安全评估器 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1008 | Vendor Compliance Checker 供应商合规检查器 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1009 | Vendor Incident Tracker 供应商事件追踪器 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1010 | Vendor Risk Assessor 供应商风险评估器 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1011 | Vendor Report Generator 供应商报告生成器 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1012 | Dependency Penetration Mapper 依赖穿透映射器 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1013 | SLA Compliance Monitor SLA合规监控器 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1014 | Security Certification Verifier 安全认证验证器 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1015 | Vendor Risk Quantifier 供应商风险量化器 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1016 | Security Scan Compliance Checker 安全扫描合规检查器 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1017 | Fail-Closed Policy Manager 失败关闭策略管理器 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1018 | Financial Security Compliance Checker 金融安全合规检查器 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1019 | OPA/Rego Engine OPA/Rego引擎 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1020 | Policy Definer 策略定义器 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1021 | Policy Executor 策略执行器 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1022 | Policy Auditor 策略审计器 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1023 | Policy Version Manager 策略版本管理器 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1024 | Policy Conflict Detector 策略冲突检测器 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1025 | AI Agent Dependency Sandbox AI Agent依赖沙箱 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1026 | L4 Agent Security Permission Isolator L4 Agent安全权限隔离器 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1027 | AI Writable Permission Controller AI可写权限控制器 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1028 | AI Code Modification Auditor AI代码修改审计器 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1029 | AI Read-Only Permission Executor AI只读权限执行器 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1030 | Data Source API Key Security Storage 数据源API密钥安全存储器 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1031 | Agent Communication Encryptor Agent间通信加密器 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1032 | Agent Behavior Baseline Learner Agent行为基线学习器 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1033 | Agent Permission Dynamic Shrinker Agent权限动态收缩器 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1034 | Agent Output Content Filter Agent输出内容过滤器 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1035 | Vulnerability Scanner 漏洞扫描器 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1036 | Security Incident Responder 安全事件响应器 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1037 | Red-Blue Team Verifier 红蓝对抗验证器 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1038 | Simplified Unified Authentication System 简化统一认证系统 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1039 | Attack Behavior Auto Blocker 攻击行为自动阻断器 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1040 | End-to-End Data Encryption and Access Controller 数据端到端加密与访问控制器 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1041 | Data Encryption and Masking Processor 数据加密与脱敏处理器 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1042 | Casbin RBAC Permission Controller Casbin RBAC权限控制器 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1043 | Operation Audit Log System 操作审计日志系统 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1044 | Data Access Controller 数据访问控制器 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1045 | Security Incident Responder Execution Layer 安全事件响应器执行层 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1046 | Role Permission Inheritance 角色权限继承 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1047 | Dynamic Permission Allocation 动态权限分配 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1048 | Permission Change Audit 权限变更审计 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1049 | Log Integrity Verification 日志完整性验证 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1183 | Security Awareness Trainer 安全意识培训器 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1184 | Zero Trust Architect 零信任架构师 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1185 | Content Fingerprint Generator Verifier 内容指纹生成验证器 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1186 | MCP Document Compliance Checker MCP文档合规检查器 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1187 | Authentication Failure Handler 认证失败处理器 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1188 | Model File Path Security Checker 模型文件路径安全性检查器 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1189 | Log Injection Protection 日志注入防护 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1190 | IP Whitelist Manager IP白名单管理 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1191 | Network Isolation Policy 网络隔离策略 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1192 | Knowledge Access Control 知识访问控制 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1193 | Security Audit Event Aggregator 安全审计事件聚合器 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1194 | Security Domain Config Hot-Update Adapter 安全域配置热更新适配器 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1195 | Security Domain Monitoring Metric Collection Adapter 安全域监控指标采集适配器 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1196 | Security Audit Log Archive and Retention Manager 安全审计日志归档与保留管理器 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1197 | eBPF Security Manager eBPF安全管理器 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1769 | Data Masking & Privacy 数据脱敏与隐私 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1770 | Input Detection/Auth/Scan 输入检测/认证/扫描等 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1865 | InputOutputGuard 输入输出防护 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1866 | PromptProtection 提示词防护 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1867 | AgentSandbox Agent沙箱隔离 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1868 | MultiAgentSecurity 多Agent安全 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1869 | SupplyChainSecurity 供应链安全 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1870 | KeySecretManager 密钥管理 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1871 | SelfProtection 自保护 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1872 | ACLGuard 访问控制 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1900 | AI Construction Governor AI代码质量门控 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1901 | Non-AI Module Boundary Guard AI/non-AI模块边界守卫 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1903 | Look-Ahead Bias Detector 前视偏差检测器 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1943 | 安全与治理 Security & Governance | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2045 | Kill Switch 紧急停机开关 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2046 | Agent漂移检测 Agent Drift Detection | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2047 | NIST AI 100-5参考框架 NIST AI 100-5 Reference Framework | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2048 | Agent能力评估协议 Agent Capability Assessment Protocol | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2049 | 群集行为风险防护 Cluster Behavior Risk Protection | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2073 | TEE可信执行环境 TEE Trusted Execution Environment | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2077 | Formal Verification形式化验证 Formal Verification | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2143 | Communication Security 通信安全 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2188 | Agent Mesh Cryptographic Identity Agent Mesh密码学身份 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2194 | Behavior Pattern Testing 行为模式测试 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2210 | Crypto-Shredding 加密粉碎 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2233 | Dependency Graph ZK Proof 依赖图ZK证明 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2235 | Log Independent Encryption Infrastructure 日志独立加密基础设施 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2236 | Key Destruction 密钥销毁 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2269 | PromptGuard 2 PromptGuard 2越狱检测 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2270 | Agent Alignment Checks Agent对齐检查 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2271 | CodeShield CodeShield代码盾 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2286 | OAuth 2.0 OAuth 2.0认证 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2291 | DID Decentralized Identifier DID去中心化标识符 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2292 | Zero-Knowledge Proof 零知识证明 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2293 | Crypto-Shredding 密码粉碎 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2294 | AES-256-GCM AES-256-GCM加密 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2339 | Memory Security Constraints 记忆安全约束 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2364 | Security Constraints 安全约束 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2397 | Crypto-Shredding Key Destruction Restricted Crypto-Shredding密钥销毁受限 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2409 | Observability Security Constraints 可观测性安全约束 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2447 | Insider Trading Protection 内幕交易防护 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2578 | Ethical Wall 信息隔离墙 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2579 | Watch List 观察名单 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2580 | Restricted List 限制名单 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2581 | Trading Behavior Monitoring 交易行为监控 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2582 | AI Driven Insider Trading Monitoring AI驱动内幕交易监控 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2583 | Compliance Framework Comprehensive Benchmark 合规框架综合对标 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2584 | Compliance Security Module Completion 合规安全模块补全 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2608 | IAM Access Control IAM与访问控制 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2609 | Key Layer Management 密钥层级管理 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2610 | Audit Chain 审计链 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2611 | Agent Security Agent安全 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2658 | Security Domain Division 安全域划分 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2659 | Defense in Depth 6 Layer 纵深防御6层 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2698 | L2 L3 Data Access Audit L2/L3数据访问审计 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2699 | Access Record 审计记录 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2700 | Abnormal Access Pattern Detection 异常访问模式检测 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2701 | Daily Data Access Report 每日数据访问报告 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2702 | Cross Wall Request 跨墙请求 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2703 | Restricted List Check 限制名单检查 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2704 | Data Classification Determination 数据分级判定 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2705 | L2 Auto Approval L2自动审批 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2706 | L3 Manual Approval L3人工审批 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2707 | Temporary Cross Wall Authorization 临时跨墙授权 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2708 | Wall Personnel Management 墙上人员管理 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2709 | Cross Wall End 跨墙结束 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2710 | Wall Personnel Extra Monitoring 墙上人员额外监控 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2711 | Wall Personnel Discussion Ban 墙上人员禁止讨论 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2712 | Wall Personnel Communication Audit 墙上人员通信审计 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2713 | Cross Wall Audit Chain 跨墙操作审计链 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2714 | Pre Announcement Trading 重大公告前交易检测 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2715 | Abnormal Profit 异常盈利检测 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2716 | Related Trading 关联交易检测 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2717 | Timing Anomaly 时序异常检测 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2718 | Volume Price Anomaly 量价异常检测 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2719 | Pre Announcement Position Rate 公告前建仓率 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2720 | Abnormal Profit Rate 异常盈利率 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2721 | Info Trading Time Lag 信息-交易时滞 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2722 | Restricted List Trigger Rate 限制名单触发率 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2723 | Auto Alert and Manual Review 自动告警与人工审查 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2735 | Monitoring Response 监控与响应 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2865 | Vendor Risk 供应商风险 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2872 | 模型运行层 Model Runtime Layer | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2873 | 输出审查层 Output Review Layer | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2874 | 权限与审计层 Permission and Audit Layer | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2875 | 交易指令数据密钥 Trading Data Key | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2876 | 策略参数数据密钥 Strategy Data Key | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2877 | 持仓数据密钥 Position Data Key | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2878 | 因子数据密钥 Factor Data Key | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2879 | 审计日志数据密钥 Audit Data Key | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2880 | 系统配置数据密钥 Config Data Key | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2881 | 行情数据密钥 Market Data Key | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2882 | 主密钥 Master Key | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2883 | 数据密钥 Data Key | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2884 | 会话密钥 Session Key | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2885 | Network and Physical Layer 网络 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2886 | Host and OS Layer 主机与操作系统层 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2887 | Application and API Layer 应用与API层 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2888 | Data Layer 数据层 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2889 | Identity and Access Layer 身份与访问层 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2890 | Monitoring and Response Layer 监控响应 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2891 | IAM与访问控制 IAM and Access Control | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2892 | 密钥层级管理 Key Hierarchy Management | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2893 | 审计链 Audit Chain | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2894 | Agent安全 Agent Security | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2895 | 内幕交易防护 Insider Trading Protection | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2896 | Trader 交易员 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2897 | AI_Agent | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2898 | System 系统 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2899 | ABAC策略引擎 ABAC Policy Engine | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2900 | Peak Suspicion 峰值怀疑 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2901 | Deception Split 欺骗分割 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2902 | Correlation 相关性 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2903 | Ensemble 集成 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2904 | Graph 图谱 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2905 | Gap Ratio 缺口比率 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2906 | Collective Score 核心 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2907 | Pairwise Correlation 成对相关性 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2908 | Behavior Trajectory Similarity 行为轨迹相似度 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2909 | Steganography Communication Detection 图谱 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2910 | Identity Rotation and Anonymization 身份轮换与匿名化 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2911 | Whistleblower Agent 举报代理 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2912 | Goal Drift Detection 目标漂移检测 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2913 | Fact Checking 事实核查 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2914 | Consistency Check 一致性检查 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2915 | Confidence Scoring Mechanism 置信度评分机制 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2916 | Red Team Adversarial Framework 红队对抗框架 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2917 | Input Provenance Tagging 标签 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2918 | Write-time Validation 写入时验证 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2919 | Session-scoped Memory 内存 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2920 | Trust-aware Retrieval 信任感知检索 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2921 | Memory Audit 内存审计 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2922 | Memory Integrity Check 内存 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2923 | Cross-wall Approval Procedure 跨墙审批流程 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2924 | Abnormal Trading Pattern Detection 异常交易模式检测 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2925 | AI-driven Insider Trading Monitoring 监控 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2926 | WASM Sandbox Runtime WASM沙箱运行时 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2927 | Dependency Behavior eBPF Monitor 依赖行为eBPF监控器 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2928 | Micro VM Isolator 微VM隔离器 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2929 | mTLS Auto Generator mTLS自动生成器 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2944 | SIEM Security Information and Event Management 安全事件 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2945 | Six-stage Incident Response Process 响应标签 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2946 | DLP Data Loss Prevention 事件 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2947 | PIT Data Protection PIT数据保护 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2948 | Shamir Secret Sharing Shamir秘密共享 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2949 | PQC Post-Quantum Cryptography Migration 图谱 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2950 | Merkle Tree Structure Merkle树结构 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2951 | SHA-256 Hash Chain SHA-256哈希链 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2952 | 6W Log Specification 6W日志规范 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2953 | Merkle Inclusion Proof Merkle包含证明 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2954 | Blockchain Anchored Timestamp 区块链锚定时间戳 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2955 | TEE Trusted Execution Environment 环境执行 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2956 | FHE Fully Homomorphic Encryption 全量 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2957 | FL Federated Learning FL联邦学习 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2958 | MPC Secure Multi-party Computation MPC安全多方计算 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2959 | BLACKICE Red Team Toolkit BLACKICE红队工具包 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2960 | LLM Pentesting 5-layer Methodology LLM渗透测试5层方法论 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2961 | AI-driven Automated Red Team AI驱动自动化红队 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2962 | Docker Container Docker容器 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2963 | gVisor Container gVisor容器 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2964 | Firecracker microVM Firecracker微虚拟机 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2965 | ISOLATEGPT hub-spoke ISOLATEGPT中心辐射 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2979 | 安全域规则目录 Security Domain Rule Catalog | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3063 | 审计日志完整性 Audit Log Integrity | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3075 | NVIDIA AI Red Team 2026 NVIDIA AI红队2026 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3076 | NIST CAISI 2025 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3077 | AAAI 2026 FinJailbreak AAAI 2026金融越狱 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3078 | SOC 2 Type II for AI AI SOC 2 Type II认证 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3403 | FCFT金融宪法微调 FCFT Financial Constitution Fine-Tuning | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3431 | llm_security/gateway.py LLM安全网关入口 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3432 | llm_security/protocol.py LLM安全协议定义 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3433 | l0_supply_chain.py L0供应链安全 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3434 | l8_multi_agent.py L8多Agent安全 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3435 | security_gateway_base.py 安全网关基类 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3436 | default_security_gateway.py 默认安全网关 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3437 | input_sanitizer.py 输入清洗器 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3438 | l1_input.py L1输入防御 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3439 | l3_output.py L3输出过滤 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3440 | input_guard.py 输入守卫 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3441 | output_guard.py 输出守卫 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3442 | path_guard.py 路径守卫 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3443 | native_api_guard.py Native API守卫 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3444 | false_completion_detector.py 虚假完成检测器 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3445 | shell_dialect_detector.py Shell方言检测器 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3446 | l2_prompt_protection.py L2提示词保护 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3447 | injection_patterns.py 注入模式库 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3448 | vibe_coding_guard.py Vibe Coding防护 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3449 | cybersec_2026_guard.py 2026新型攻击防护 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3450 | novel_attack_guard.py 新型攻击防护 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3451 | rule_injection_guard.py 规则注入防护 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3452 | context_drift_detector.py 上下文漂移检测器 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3453 | process_sandbox.py 进程沙箱 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3454 | l2a_process_sandbox.py L2a进程沙箱 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3455 | rollback_sandbox.py 回滚沙箱 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3456 | cold_start_lock.py 冷启动锁 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3457 | cascading_failure_isolator.py 级联故障隔离器 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3458 | dry_run.py 干运行 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3459 | engine_degradation.py 引擎降级 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3460 | l4_agent.py L4 Agent安全 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3461 | multi_agent_collusion_detector.py 多Agent共谋检测器 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3462 | replay_attack_guard.py 重放攻击防护 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3463 | toctou_guard.py TOCTOU防护 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3464 | sequence_guard.py 序列守卫 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3465 | cross_session_detector.py 跨会话检测器 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3466 | wireheading_prevention.py Wireheading防护 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3467 | audit_trail/supply_chain_security.py 供应链安全审计 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3468 | dep_cve_correlator.py CVE关联器 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3469 | remote_attestation.py 远程证明 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3470 | security_config_scanner.py 安全配置扫描器 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3471 | key_hierarchy.py 密钥层级 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3472 | secrets_lifecycle.py 秘密生命周期 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3473 | shared/security/secrets.py 共享密钥 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3474 | ssot_guard.py SSOT守卫 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3475 | secrets.py 秘密模式检测 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3476 | secret_rotation.py 密钥轮换 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3477 | adversarial_mutator.py 对抗变异器 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3478 | code_integrity.py 代码完整性 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3479 | l7_validation.py L7验证 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3480 | isolation.py 隔离保护 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3481 | red_team_scanner.py 红队扫描器 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3482 | l5_resource_protection.py L5资源保护 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3483 | l6_observability.py L6可观测性 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3484 | immutable_core.py 不可变核心 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3485 | integrity_self_check.py 完整性自检 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3486 | micro_verifier.py 微验证器 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3487 | post_action_verifier.py 事后验证器 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3488 | continuous_verifier.py 持续验证器 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3489 | behavior_audit_logger.py 行为审计日志器 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3490 | blind_spot_tracker.py 盲点追踪器 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3491 | kill_switch.py Kill Switch kill_switch.py紧急制动 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3492 | permission_guard.py 权限守卫 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3493 | abac_guard.py ABAC守卫 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3494 | rbac_guard.py RBAC守卫 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3495 | derive_rbac_roles.py RBAC角色推导 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3496 | permission_mode_manager.py 权限模式管理器 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3497 | permission_hooks.py 权限钩子 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3498 | emergency_override.py 紧急覆盖 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3499 | escalation_handler.py 升级处理器 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3500 | identity.py 身份管理 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3501 | intent_binder.py 意图绑定 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3502 | defense_depth.py 防御纵深 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3503 | guard_layers.py 守卫层编排 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3504 | approver_check.py 审批检查 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3505 | a2a_check.py A2A检查 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3506 | capability_check.py 能力检查 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3507 | bootstrap_superadmin.py 超级管理员引导 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3508 | capability.py 能力定义 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3509 | audit_log_guard.py 审计日志守卫 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3510 | session_lifecycle.py 会话生命周期 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3511 | session_concurrency.py 会话并发 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3512 | non_repudiation.py 抗抵赖 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3513 | memory_guard.py 内存守卫 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3514 | memory_provenance_guard.py 内存来源守卫 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3515 | canary_rollout_manager.py 金丝雀发布管理器 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3516 | blueprint_fidelity.py 蓝图保真 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3517 | phase_executor.py 阶段执行器 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3518 | observability.py 可观测性 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3519 | risk_mitigation.py 风险缓解 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3520 | 进程沙箱层 Process Sandbox Layer | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3521 | 可观测性层 Observability Layer | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3522 | 验证层 Validation Layer | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3523 | 多Agent安全层 Multi-Agent Security Layer | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3524 | shared/contracts/security模块包 shared contracts security | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3525 | llm_security/dashboard 安全仪表盘 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4241 | Microstructure Defense 微结构防御 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4835 | 4层guardrails 4-layer Guardrails | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4839 | BLACKICE 红队工具包 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4840 | OWASP Gen AI Red Teaming Guide OWASP生成式AI红队指南 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4841 | LLM Pentesting 5层方法论 LLM Pentesting 5-layer Methodology | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4842 | AI驱动自动化红队 AI-driven Automated Red Team | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4844 | OWASP ASI 10类行为监控 OWASP ASI 10 Behavior Monitoring | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4849 | 记忆投毒检测指标 Memory Poisoning Detection Metrics | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4850 | 注册流程 Registration Flow | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4851 | 认证流程 Authentication Flow | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4852 | 令牌管理 Token Management | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4863 | Vulnerability Fix Window Assessor 漏洞修复窗口评估器 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4864 | AI Hallucination Package Name Guard AI幻觉包名防护 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4865 | SBOM Reachability Analyzer SBOM可达性分析器 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4866 | Attack Surface Simulator 攻击面模拟器 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4867 | AI Agent Dependency Security Sandbox AI Agent依赖安全沙箱 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4869 | Financial Constitution Fine-Tuning 金融宪法微调 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4875 | Zero-Knowledge Compliance Audit Layer 零知识合规审计层 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4876 | ZKP Proof Generator ZKP证明生成器 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4877 | Shield Module Shield模块 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4889 | CollusionDetection 串谋检测 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-5022 | Defense in Depth 6 Layers 纵深防御6层 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-5023 | Key Hierarchy Management 密钥层级管理 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-5024 | Vendor Risk Management 供应商风险管理 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-5025 | Data Access Audit 数据访问审计 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-5026 | Data Desensitization Engine 数据脱敏引擎 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-5027 | Security Policy as Code 安全策略即代码 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-5028 | Content Security 内容安全 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-5029 | Blockchain Anchoring 区块链锚定 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-5030 | TEE Trusted Execution Environment TEE可信执行环境 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-5031 | eBPF Kernel Monitoring eBPF内核监控 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-5032 | WASM Sandbox WASM沙箱 | D_SECURITY | 候选待评（candidate） | harvest待评估（likely_implemented） |
