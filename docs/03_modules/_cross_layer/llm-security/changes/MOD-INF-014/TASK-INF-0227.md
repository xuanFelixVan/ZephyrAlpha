---
task_id: "TASK-INF-0227"
source_blueprint: "MOD-INF-014"
source_section: "§10 L7 — Red Team 自动扫描 + 威胁情报更新 + 防御效果度量（§10.2/§10.4 子模块）"
title: "L7 Red Team 自动攻击模拟+威胁情报更新+防御效果度量——200+载荷库+garak/promptfoo集成+月度Scorecard"
description: |
  实现 L7 的 Red Team 自动扫描引擎 + 攻击载荷库管理 + 威胁情报更新 + 防御效果度量系统。
  包含：RedTeamScanner（garak CLI + promptfoo 集成）、AttackPayloadLibrary（按 OWASP LLM01-LLM10 分类的 200+ 载荷）、
  ThreatIntelUpdater（OWASP/MITRE/NIST/CVE 自动跟踪+差异分析+规则草案生成）、
  DefenseMetricsEngine（漏拦率/误拦率/响应时间/覆盖率/自动化率五大 KPI + 月度 Scorecard）。
priority: "P2"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\llm-security\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\self_protection\\l7_validation.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\payloads\\red_team_payloads.yaml"
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\self_protection\\red_team_scanner.py"
    description: "RedTeamScanner——garak+promptfoo 集成+自定义扫描器"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\self_protection\\threat_intel.py"
    description: "ThreatIntelUpdater——OWASP/MITRE/NIST/CVE 自动跟踪+差异分析+规则草案"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\self_protection\\defense_metrics.py"
    description: "DefenseMetricsEngine——五 KPI 度量+月度 Scorecard+趋势对比+优化推荐"
  - path: "D:\\ZephyrAlpha\\tests\\llm_security\\test_l7_red_team.py"
    description: "L7 Red Team + Threat Intel + Defense Metrics 验证测试——15条用例"
allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\self_protection\\red_team_scanner.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\self_protection\\threat_intel.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\self_protection\\defense_metrics.py"
  - "D:\\ZephyrAlpha\\tests\\llm_security\\test_l7_red_team.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\self_protection\\l7_validation.py"
applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "Pydantic V2——禁止 dataclass"
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\llm-security\\blueprint.md"
    reason: "§10.2 核心能力(Red Team/回归/威胁情报/度量) + §10.3/§10.4 接口定义+载荷库结构"
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules: ["M1","M3"]
estimated_tokens: 15000
timeout_minutes: 90
acceptance_criteria:
  > L7 Red Team + Threat Intel + Defense Metrics 全部 12 条关键要求：
  - "RedTeamScanner 类含 run_red_team_scan(scope=quick|daily|full) / generate_novel_payloads(count=20) / load_payload_library(db_path) 3个方法"
  - "run_red_team_scan() 集成 garak CLI（NVIDIA 开源 LLM 漏洞扫描器）+ promptfoo（prompt 测试框架）"
  - "scope=quick: 核心 100 条载荷（每次部署前）/ daily: quick + AI 生成 20 条新变体 / full: 全量 200+ 条（每周）"
  - "RedTeamReport Pydantic V2 model: bypass_rate / false_positive_rate / per_payload_details / overall_score / timestamp"
  - "AttackPayloadLibrary 按 OWASP LLM01-LLM10 分类：LLM01 200+ 直接/间接注入变体 + LLM02 100+ 信息泄露尝试 + LLM06 50+ 权限提升 + LLM07 80+ Prompt提取 + LLM10 30+ 资源耗尽"
  - "generate_novel_payloads() 基于已知攻击模式变异：同义词替换/编码转换/语法重组/多语言翻译后攻击——生成 20 条新变体"
  - "ThreatIntelUpdater: check_owasp_updates() / check_mitre_atlas_updates() / check_nist_updates() / check_cve_releases() / check_vendor_advisories() 5 个数据源"
  - "自动生成更新摘要（AI 分析 + 对比当前防御覆盖）+ 生成对应的检测规则草案（待 Owner 确认）"
  - "DefenseMetricsEngine: measure_bypass_rate() / measure_false_positive_rate() / measure_response_time() / measure_coverage() / measure_automation_rate() 5 个度量方法"
  - "核心 KPI 定义：绕过率 → Phase0 <5%, Phase2 <1% / 误拦率 → Phase0 <2%, Phase2 <0.5% / OWASP 覆盖 → Phase0 100%"
  - "MonthlySecurityScorecard Pydantic V2 model: maturity_score / trend_vs_last_month / top_weak_layer / recommended_hardening_items / roi_analysis——对标 NIST AI RMF"
  - "防御层薄弱点识别（漏拦率最高的层标记为最薄弱层）+ 优化优先级排序 + ROI 分析（加固成本 vs 风险降低）"
  - "R6 隔离策略：Red Team 测试使用独立沙箱环境 + 测试数据与生产数据严格隔离 + 禁止使用生产 API 做 Red Team"
  - "15条单元测试全部通过（按 scope=quick/daily/full 三级各 5 条）"
rollback_instructions: |
  1. 删除 red_team_scanner.py / threat_intel.py / defense_metrics.py / test_l7_red_team.py
  2. 确认 l7_validation.py（TASK-INF-0210）未受影响
depends_on: ["TASK-INF-0201","TASK-INF-0210","TASK-INF-0214"]
blocked_by: []
status: "created"
tags_fn: ["security","red-team","threat-intel"]
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "active"
tags_mo: ["MOD-INF-014"]
completed_gates: []
blocked_gates: {}
artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "supervised"
autonomy_checklist: []
---

# 目标

实现 L7 层中 TASK-INF-0210 未覆盖的三个子模块：
1. **Red Team 自动扫描**——集成 garak + promptfoo，管理 200+ 条攻击载荷，支持三级扫描粒度
2. **威胁情报自动更新**——跟踪 OWASP/MITRE/NIST/CVE/厂商公告，自动生成差异分析+规则草案
3. **防御效果度量**——五维 KPI 计算，月度 Security Scorecard，薄弱点识别+优化推荐

以上是蓝图 §10.2 和 §10.4 在 TASK-INF-0210（验证门禁+代码自检+DeepSeek风险）之外的完整补充。

## 触发条件
- TASK-INF-0210 (L7 内部验证层) 已通过
- TASK-INF-0214 (payloads/ 目录 + red_team_payloads.yaml 已创建) 已通过
- LSG 已集成 garak CLI + promptfoo CLI

## 执行步骤

### 读
- `D:\ZephyrAlpha\docs\03_modules\_cross_layer\llm-security\blueprint.md` §10.2—§10.5
- `D:\ZephyrAlpha\src\zephyr\llm_security\payloads\red_team_payloads.yaml`

### 做
1. 实现 RedTeamScanner——garak CLI 子进程调用 + promptfoo 集成 + 3 级 scope + 载荷变异生成
2. 实现 ThreatIntelUpdater——5 个数据源 check + 差异分析 + 规则草案自动生成
3. 实现 DefenseMetricsEngine——5 KPI 度量 + 月度 Scorecard + ROI 分析
4. 编写 15 条单元测试（按 quick/daily/full 三级各 5 条）
