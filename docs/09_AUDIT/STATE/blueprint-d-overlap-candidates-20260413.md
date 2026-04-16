---
module_id: AUDIT_BLUEPRINT_D_OVERLAP_CANDIDATES_20260413
standard_type: audit_state
applicable_scope: D 类蓝图主题重叠候选（启发式）
generated_date: '20260413'
generated_by: scripts/governance/scan_blueprint_d_overlap_candidates.py
---

# 蓝图 D 类重叠候选（机器建议 · 非最终裁决）

> **机器真源**：[`BLUEPRINT_D_OVERLAP_CANDIDATES_20260413.json`](./BLUEPRINT_D_OVERLAP_CANDIDATES_20260413.json)
> **扫描蓝图数**：765 ｜ **候选对（写入本文件）**：400（截断前 11375 对，仅保留 score 最高的 400 对）

## 说明

- **截断**：满足阈值的候选共 **11375** 对，仅保留 score 最高的 **400** 对（`--max-output-pairs`）；调参见 Playbook §4。

- **不是**语义 embedding / LLM；基于 **标题、responsibility、正文抽样、H2 标题** 的 token 与标题集合相似度。
- **建议 canonical** 与 **合并大纲** 为 **规则化启发式**，须经 [D 类蓝图重叠 Playbook](../../05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/d-class-blueprint-overlap-playbook.md) 评审后再改稿。
- 与 **C1（字节相同）** 互补：本脚本跳过 **partial_hash** 全同对（应交给 `scan_duplicate_file_content.py`）。

## 候选对（按 score 降序，截断展示）

### 1. score=0.996

- **A**: `docs/06_ARCHIVE/blueprints/human-ai-interface-layer-technical-blueprint.md`
- **B**: `docs/06_ARCHIVE/blueprints/overlap-human-ai-interface-layer-technical-blueprint-20260407-190203.md`
- **指标**: token_jaccard=0.9927, heading_jaccard=1.0, |∩token|=272
- **共有 H2（归一化后）**: 1. 文档治理, 一、架构设计, 七、总结, 三、技术实现路线, 二、核心组件详细设计, 五、对标分析
- **标题**: A「Layer 8: 人机交互层蓝图…」 / B「Layer 8: 人机交互层蓝图…」
- **建议 canonical**: `docs/06_ARCHIVE/blueprints/overlap-human-ai-interface-layer-technical-blueprint-20260407-190203.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/06_ARCHIVE/blueprints/human-ai-interface-layer-technical-blueprint.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 📋 执行摘要
  - 一、架构设计
  - 二、核心组件详细设计
  - 三、技术实现路线
  - 四、质量保证
  - 五、对标分析
  - 六、实施计划
  - 七、总结
  - 1. 文档治理

### 2. score=0.9941

- **A**: `docs/01_FRAMEWORK/model-registry-blueprint.md`
- **B**: `docs/06_ARCHIVE/blueprints/overlap-model-registry-blueprint-20260407-190203.md`
- **指标**: token_jaccard=0.9894, heading_jaccard=1.0, |∩token|=186
- **共有 H2（归一化后）**: 1. 文档治理, 一、架构设计, 七、相关文档, 三、数据模型设计, 二、核心组件详细设计, 五、质量保证
- **标题**: A「模型注册中心蓝图…」 / B「模型注册中心蓝图…」
- **建议 canonical**: `docs/01_FRAMEWORK/model-registry-blueprint.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/06_ARCHIVE/blueprints/overlap-model-registry-blueprint-20260407-190203.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 📋 执行摘要
  - 一、架构设计
  - 二、核心组件详细设计
  - 三、数据模型设计
  - 四、实施路线
  - 五、质量保证
  - 六、成功指标
  - 七、相关文档
  - 1. 文档治理

### 3. score=0.9896

- **A**: `docs/06_ARCHIVE/reports/overlap-incomplete-blueprint-archive-report-20260404-20260407-190203.md`
- **B**: `docs/09_AUDIT/REPORTS/incomplete-blueprint-archive-report-20260404.md`
- **指标**: token_jaccard=0.9811, heading_jaccard=1.0, |∩token|=208
- **共有 H2（归一化后）**: 1. 归档执行摘要, 2. 归档文档详情, 3. 归档执行过程, 4. 归档效果评估, 5. 后续建议, 6. 归档总结
- **标题**: A「内容不完整蓝图文档归档报?…」 / B「内容不完整蓝图文档归档报告…」
- **建议 canonical**: `docs/09_AUDIT/REPORTS/incomplete-blueprint-archive-report-20260404.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/06_ARCHIVE/reports/overlap-incomplete-blueprint-archive-report-20260404-20260407-190203.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 归档执行摘要
  - 2. 归档文档详情
  - 3. 归档执行过程
  - 4. 归档效果评估
  - 5. 后续建议
  - 6. 归档总结
  - 7. 相关文档

### 4. score=0.9885

- **A**: `docs/06_ARCHIVE/blueprints/overlap-complete-blueprint-20260407-190203.md`
- **B**: `docs/09_RESEARCH_INNOVATION/_archive/complete-blueprint.md`
- **指标**: token_jaccard=0.9791, heading_jaccard=1.0, |∩token|=421
- **共有 H2（归一化后）**: 一、开源方案完整清单, 七、研究监控平台补充模块, 三、特征工程平台补充模块, 九、研究基础设施补充模块, 二、研究数据平台补充模块, 五、实验管理平台补充模块
- **标题**: A「Layer 9: 研究与创新层完整蓝图 v3.0…」 / B「Layer 9: 研究与创新层完整蓝图 v3.0…」
- **建议 canonical**: `docs/09_RESEARCH_INNOVATION/_archive/complete-blueprint.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/06_ARCHIVE/blueprints/overlap-complete-blueprint-20260407-190203.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 核心定位
  - 📋 执行摘要
  - 一、开源方案完整清单
  - 二、研究数据平台补充模块
  - 三、特征工程平台补充模块
  - 四、模型开发平台补充模块
  - 五、实验管理平台补充模块
  - 六、研究协作平台补充模块
  - 七、研究监控平台补充模块
  - 八、研究安全平台补充模块
  - 九、研究基础设施补充模块
  - 十、完整实施路线图
  - 十一、预期效果
  - 十二、总结

### 5. score=0.986

- **A**: `docs/06_ARCHIVE/audit_reports/research-workflow-management-blueprint-legacy-p1-cleanup-archive.md`
- **B**: `docs/10_AI_WORKFLOW/research-workflow-management-blueprint.md`
- **指标**: token_jaccard=0.9746, heading_jaccard=1.0, |∩token|=230
- **共有 H2（归一化后）**: 一、模块概述, 七、质量保证, 三、技术实现, 九、开源项目集成, 二、架构设计, 五、实施路径
- **标题**: A「研究工作流管理蓝图 (RESEARCH_WORKFLOW_MANAGEMENT)…」 / B「研究工作流管理蓝图 (RESEARCH_WORKFLOW_MANAGEMENT)…」
- **建议 canonical**: `docs/10_AI_WORKFLOW/research-workflow-management-blueprint.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/06_ARCHIVE/audit_reports/research-workflow-management-blueprint-legacy-p1-cleanup-archive.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 文档职责说明
  - 一、模块概述
  - 二、架构设计
  - 三、技术实现
  - 四、数据模型
  - 五、实施路径
  - 六、接口定义
  - 七、质量保证
  - 八、风险评估
  - 九、开源项目集成
  - 十、总结

### 6. score=0.9692

- **A**: `docs/06_ARCHIVE/blueprints/model-performance-version-management-blueprint-legacy-p1-cleanup-archive.md`
- **B**: `docs/10_AI_WORKFLOW/model-performance-version-management-blueprint.md`
- **指标**: token_jaccard=0.944, heading_jaccard=1.0, |∩token|=236
- **共有 H2（归一化后）**: 1. 文档治理, 一、模块概述, 七、风险管, 三、接口定, 九、相关文档, 二、详细架构设
- **标题**: A「设置MLflow跟踪URI…」 / B「设置MLflow跟踪URI…」
- **建议 canonical**: `docs/10_AI_WORKFLOW/model-performance-version-management-blueprint.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/06_ARCHIVE/blueprints/model-performance-version-management-blueprint-legacy-p1-cleanup-archive.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 一、模块概述
  - 二、详细架构设
  - 三、接口定
  - 四、数据模
  - 五、实施计
  - 六、测试策
  - 七、风险管
  - 八、验收标
  - 九、相关文档
  - 1. 文档治理

### 7. score=0.9315

- **A**: `docs/09_AUDIT/STATE/blueprint-d-overlap-candidates-20260411.md`
- **B**: `docs/09_AUDIT/STATE/blueprint-d-overlap-candidates-20260412.md`
- **指标**: token_jaccard=0.8755, heading_jaccard=1.0, |∩token|=204
- **共有 H2（归一化后）**: 候选对（按 score 降序，截断展示）, 说明
- **标题**: A「蓝图 D 类重叠候选（机器建议 · 非最终裁决）…」 / B「蓝图 D 类重叠候选（机器建议 · 非最终裁决）…」
- **建议 canonical**: `docs/09_AUDIT/STATE/blueprint-d-overlap-candidates-20260412.md`
- **理由（机器）**: 建议正文体量更大（可能更完整）
- **另一路径**: `docs/09_AUDIT/STATE/blueprint-d-overlap-candidates-20260411.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 说明
  - 候选对（按 score 降序，截断展示）

### 8. score=0.9203

- **A**: `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/data-version-control-blueprint.md`
- **B**: `docs/06_ARCHIVE/blueprints/data-version-control-blueprint-legacy-p1-cleanup-archive.md`
- **指标**: token_jaccard=0.9459, heading_jaccard=0.8571, |∩token|=210
- **共有 H2（归一化后）**: 1. 文档治理, 一、设计背景与目标, 实现方案, 核心功能, 核心定位, 设计目标
- **标题**: A「数据版本控制蓝图…」 / B「数据版本控制蓝图…」
- **建议 canonical**: `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/data-version-control-blueprint.md`
- **理由（机器）**: 建议路径含图纸柜 `01_BLUEPRINTS`
- **另一路径**: `docs/06_ARCHIVE/blueprints/data-version-control-blueprint-legacy-p1-cleanup-archive.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 核心定位
  - 设计目标
  - 核心功能
  - 实现方案
  - 一、设计背景与目标
  - 1. 文档治理
  - 变更历史

### 9. score=0.9186

- **A**: `docs/06_ARCHIVE/duplicates/complete-blueprint-overview-merged.md`
- **B**: `docs/11_STRATEGIC_DECISION/complete-blueprint-overview.md`
- **指标**: token_jaccard=0.8519, heading_jaccard=1.0, |∩token|=328
- **共有 H2（归一化后）**: 一、完整模块清单, 一、架构设计, 七、成功指标, 七、风险与应对, 三、实施计划详情, 三、数据模型
- **标题**: A「[模块名称]蓝图…」 / B「Layer 11 战略决策层完整系统蓝图总览…」
- **建议 canonical**: `docs/11_STRATEGIC_DECISION/complete-blueprint-overview.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/06_ARCHIVE/duplicates/complete-blueprint-overview-merged.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 📋 文档职责说明
  - 📋 执行摘要
  - 一、完整模块清单
  - 二、实施策略
  - 三、实施计划详情
  - 二、剩余P1级蓝图清单
  - 三、蓝图模板
  - 一、架构设计
  - 二、功能设计
  - 三、数据模型
  - 四、开源集成方案
  - 五、实施路径
  - 六、质量保证
  - 七、成功指标

### 10. score=0.8996

- **A**: `docs/06_ARCHIVE/blueprints/overlap-investment-committee-support-blueprint-20260407-190203.md`
- **B**: `docs/11_STRATEGIC_DECISION/investment-committee-support-blueprint.md`
- **指标**: token_jaccard=0.8175, heading_jaccard=1.0, |∩token|=224
- **共有 H2（归一化后）**: 一、系统架构设计, 七、风险与应对, 三、开源集成方案, 二、核心功能设计, 五、实施路径, 八、相关文档
- **标题**: A「投资委员会决策支持系统蓝图…」 / B「投资委员会决策支持系统蓝图…」
- **建议 canonical**: `docs/11_STRATEGIC_DECISION/investment-committee-support-blueprint.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/06_ARCHIVE/blueprints/overlap-investment-committee-support-blueprint-20260407-190203.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 📋 执行摘要
  - 一、系统架构设计
  - 二、核心功能设计
  - 三、开源集成方案
  - 四、数据库设计
  - 五、实施路径
  - 六、成功指标
  - 七、风险与应对
  - 八、相关文档

### 11. score=0.8609

- **A**: `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/data-governance-platform-blueprint.md`
- **B**: `docs/06_ARCHIVE/blueprints/overlap-data-governance-platform-blueprint-20260407-190203.md`
- **指标**: token_jaccard=0.9381, heading_jaccard=0.7, |∩token|=212
- **共有 H2（归一化后）**: 1. 文档治理, 一、设计背景与目标, 变更历史, 实现方案, 核心功能, 核心定位
- **标题**: A「DATA GOVERNANCE PLATFORM BLUEPRINT…」 / B「DATA GOVERNANCE PLATFORM BLUEPRINT…」
- **建议 canonical**: `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/data-governance-platform-blueprint.md`
- **理由（机器）**: 建议路径含图纸柜 `01_BLUEPRINTS`
- **另一路径**: `docs/06_ARCHIVE/blueprints/overlap-data-governance-platform-blueprint-20260407-190203.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 核心定位
  - 设计目标
  - 核心功能
  - 实现方案
  - 一、设计背景与目标
  - 1. 文档治理
  - 接口与契约（蓝图终稿）
  - 验收标准（可检查）
  - 已知限制
  - 变更历史

### 12. score=0.8536

- **A**: `docs/01_FRAMEWORK/algorithm-deployment-control-blueprint.md`
- **B**: `docs/06_ARCHIVE/audit_reports/overlap-algorithm-deployment-control-blueprint-20260407-190202.md`
- **指标**: token_jaccard=0.8702, heading_jaccard=0.7857, |∩token|=228
- **共有 H2（归一化后）**: 一、系统架构设计, 七、质量保证, 三、部署监控, 九、成功指标, 二、技术实现方案, 五、个人开发优化方案
- **标题**: A「算法部署控制系统蓝图…」 / B「算法部署控制系统蓝图…」
- **建议 canonical**: `docs/01_FRAMEWORK/algorithm-deployment-control-blueprint.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/06_ARCHIVE/audit_reports/overlap-algorithm-deployment-control-blueprint-20260407-190202.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 接口与契约（蓝图终稿）
  - 验收标准（可检查）
  - 已知限制
  - 📋 执行摘要
  - 一、系统架构设计
  - 二、技术实现方案
  - 三、部署监控
  - 四、数据模型设计
  - 五、个人开发优化方案
  - 六、实施路线图
  - 七、质量保证
  - 八、风险评估
  - 九、成功指标
  - 十、相关文档

### 13. score=0.815

- **A**: `docs/11_STRATEGIC_DECISION/archive/blueprint-creation-progress-report-20260407.md`
- **B**: `docs/11_STRATEGIC_DECISION/archive/p1-blueprint-creation-progress-report-20260407.md`
- **指标**: token_jaccard=0.6636, heading_jaccard=1.0, |∩token|=142
- **共有 H2（归一化后）**: 一、已完成蓝图文档清单, 七、总结, 三、蓝图文档质量评估, 二、剩余蓝图文档清单, 五、下一步行动, 六、成功标准
- **标题**: A「…」 / B「…」
- **建议 canonical**: `docs/11_STRATEGIC_DECISION/archive/blueprint-creation-progress-report-20260407.md`
- **理由（机器）**: 建议正文体量更大（可能更完整）
- **另一路径**: `docs/11_STRATEGIC_DECISION/archive/p1-blueprint-creation-progress-report-20260407.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 📋 执行摘要
  - 一、已完成蓝图文档清单
  - 二、剩余蓝图文档清单
  - 三、蓝图文档质量评估
  - 四、实施建议
  - 五、下一步行动
  - 六、成功标准
  - 七、总结

### 14. score=0.7809

- **A**: `docs/01_FRAMEWORK/mlops-platform-blueprint.md`
- **B**: `docs/06_ARCHIVE/blueprints/overlap-mlops-platform-blueprint-20260407-190203.md`
- **指标**: token_jaccard=0.8953, heading_jaccard=0.5385, |∩token|=231
- **共有 H2（归一化后）**: 1. 文档治理, ?八、验收标?, ⚠️ 七、风险评?, 📅 五、实施路线图, 📚 九、相关文档索?, 🔌 四、核心接口定?
- **标题**: A「MLOps平台蓝图：端到端机器学习运维平台…」 / B「MLOps平台蓝图：端到端机器学习运维平台…」
- **建议 canonical**: `docs/01_FRAMEWORK/mlops-platform-blueprint.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/06_ARCHIVE/blueprints/overlap-mlops-platform-blueprint-20260407-190203.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 📊 一、概述
  - 🎯 二、专业机构对接
  - 🏗?三、技术架构设计
  - 🔌 四、核心接口定?
  - 📅 五、实施路线图
  - 🔧 六、技术选型
  - ⚠️ 七、风险评?
  - ?八、验收标?
  - 📚 九、相关文档索?
  - 1. 文档治理
  - 📊 一、概?（自另一稿合并时需核对是否重复）
  - 🎯 二、专业机构对?（自另一稿合并时需核对是否重复）
  - 🏗?三、技术架构设?（自另一稿合并时需核对是否重复）

### 15. score=0.7662

- **A**: `docs/01_FRAMEWORK/strategic-decision-layer-blueprint.md`
- **B**: `docs/11_STRATEGIC_DECISION/archive/blueprint-v2.0.1-backup.md`
- **指标**: token_jaccard=0.8295, heading_jaccard=0.6, |∩token|=253
- **共有 H2（归一化后）**: 一、架构设计, 三、数据模型设?, 二、核心组件详细设?, 五、成功指?, 四、实施路?, 📋 执行摘要
- **标题**: A「Layer 11: 战略决策层蓝图…」 / B「Layer 11: 战略决策层蓝图…」
- **建议 canonical**: `docs/01_FRAMEWORK/strategic-decision-layer-blueprint.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/11_STRATEGIC_DECISION/archive/blueprint-v2.0.1-backup.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 📋 执行摘要
  - 一、架构设计
  - 二、核心组件详细设?
  - 三、数据模型设?
  - 四、实施路?
  - 五、成功指?
  - 六、相关文?
  - 1. 文档治理
  - 六、相关文档（自另一稿合并时需核对是否重复）
  - 七、开源替代方案（自另一稿合并时需核对是否重复）

### 16. score=0.7459

- **A**: `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/blueprint-final-audit-20260412-211533.md`
- **B**: `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/blueprint-final-audit-20260412-211735.md`
- **指标**: token_jaccard=0.538, heading_jaccard=1.0, |∩token|=85
- **共有 H2（归一化后）**: 修复建议, 施工准入判断, 核心指标, 详细问题清单, 问题汇总, 验收标准评估
- **标题**: A「蓝图终稿综合审计报告…」 / B「蓝图终稿综合审计报告…」
- **建议 canonical**: `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/blueprint-final-audit-20260412-211533.md`
- **理由（机器）**: 建议正文体量更大（可能更完整）
- **另一路径**: `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/blueprint-final-audit-20260412-211735.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 核心指标
  - 问题汇总
  - 验收标准评估
  - 详细问题清单
  - 修复建议
  - 施工准入判断

### 17. score=0.7425

- **A**: `docs/01_FRAMEWORK/mamba-ssm-blueprint.md`
- **B**: `docs/01_FRAMEWORK/mixture-of-experts-blueprint.md`
- **指标**: token_jaccard=0.5317, heading_jaccard=1.0, |∩token|=67
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「requirements_mamba.txt…」 / B「混合专家模型(MoE)蓝图…」
- **建议 canonical**: `docs/01_FRAMEWORK/mixture-of-experts-blueprint.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/01_FRAMEWORK/mamba-ssm-blueprint.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 18. score=0.7352

- **A**: `docs/08_HUMAN_AI_INTERFACE/65_RISK_REPORTING_SYSTEM/risk-reporting-system-blueprint.md`
- **B**: `docs/08_HUMAN_AI_INTERFACE/72_COMPLIANCE_REPORTING_SYSTEM/compliance-reporting-system-blueprint.md`
- **指标**: token_jaccard=0.5185, heading_jaccard=1.0, |∩token|=70
- **共有 H2（归一化后）**: 🎯 核心功能, 📋 模块概览, 🚀 实施计划
- **标题**: A「模块65: 风险报告系统 (RISK_REPORTING_SYSTEM)…」 / B「模块72: 合规报告系统 (COMPLIANCE_REPORTING_SYSTEM)…」
- **建议 canonical**: `docs/08_HUMAN_AI_INTERFACE/72_COMPLIANCE_REPORTING_SYSTEM/compliance-reporting-system-blueprint.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/08_HUMAN_AI_INTERFACE/65_RISK_REPORTING_SYSTEM/risk-reporting-system-blueprint.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 📋 模块概览
  - 🎯 核心功能
  - 🚀 实施计划

### 19. score=0.725

- **A**: `docs/01_FRAMEWORK/mixture-of-experts-blueprint.md`
- **B**: `docs/01_FRAMEWORK/multimodal-fusion-blueprint.md`
- **指标**: token_jaccard=0.5, heading_jaccard=1.0, |∩token|=65
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「混合专家模型(MoE)蓝图…」 / B「requirements_multimodal.txt…」
- **建议 canonical**: `docs/01_FRAMEWORK/multimodal-fusion-blueprint.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/01_FRAMEWORK/mixture-of-experts-blueprint.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 20. score=0.7145

- **A**: `docs/01_FRAMEWORK/mamba-ssm-blueprint.md`
- **B**: `docs/01_FRAMEWORK/multimodal-fusion-blueprint.md`
- **指标**: token_jaccard=0.4809, heading_jaccard=1.0, |∩token|=63
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「requirements_mamba.txt…」 / B「requirements_multimodal.txt…」
- **建议 canonical**: `docs/01_FRAMEWORK/multimodal-fusion-blueprint.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/01_FRAMEWORK/mamba-ssm-blueprint.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 21. score=0.7135

- **A**: `docs/01_FRAMEWORK/model-pruning-blueprint.md`
- **B**: `docs/01_FRAMEWORK/model-quantization-blueprint.md`
- **指标**: token_jaccard=0.4792, heading_jaccard=1.0, |∩token|=69
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「模型剪枝蓝图…」 / B「模型量化蓝图…」
- **建议 canonical**: `docs/01_FRAMEWORK/model-quantization-blueprint.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/01_FRAMEWORK/model-pruning-blueprint.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 22. score=0.7129

- **A**: `docs/01_FRAMEWORK/mia-defense-blueprint.md`
- **B**: `docs/01_FRAMEWORK/model-watermark-blueprint.md`
- **指标**: token_jaccard=0.4779, heading_jaccard=1.0, |∩token|=65
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「MIA防御蓝图…」 / B「模型水印蓝图…」
- **建议 canonical**: `docs/01_FRAMEWORK/model-watermark-blueprint.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/01_FRAMEWORK/mia-defense-blueprint.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 23. score=0.7054

- **A**: `docs/01_FRAMEWORK/model-pruning-blueprint.md`
- **B**: `docs/01_FRAMEWORK/model-watermark-blueprint.md`
- **指标**: token_jaccard=0.4643, heading_jaccard=1.0, |∩token|=65
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「模型剪枝蓝图…」 / B「模型水印蓝图…」
- **建议 canonical**: `docs/01_FRAMEWORK/model-watermark-blueprint.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/01_FRAMEWORK/model-pruning-blueprint.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 24. score=0.7051

- **A**: `docs/01_FRAMEWORK/mia-defense-blueprint.md`
- **B**: `docs/01_FRAMEWORK/model-pruning-blueprint.md`
- **指标**: token_jaccard=0.4638, heading_jaccard=1.0, |∩token|=64
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「MIA防御蓝图…」 / B「模型剪枝蓝图…」
- **建议 canonical**: `docs/01_FRAMEWORK/model-pruning-blueprint.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/01_FRAMEWORK/mia-defense-blueprint.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 25. score=0.6989

- **A**: `docs/01_FRAMEWORK/mixture-of-experts-blueprint.md`
- **B**: `docs/01_FRAMEWORK/model-watermark-blueprint.md`
- **指标**: token_jaccard=0.4526, heading_jaccard=1.0, |∩token|=62
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「混合专家模型(MoE)蓝图…」 / B「模型水印蓝图…」
- **建议 canonical**: `docs/01_FRAMEWORK/model-watermark-blueprint.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/01_FRAMEWORK/mixture-of-experts-blueprint.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 26. score=0.6986

- **A**: `docs/01_FRAMEWORK/knowledge-distillation-blueprint.md`
- **B**: `docs/01_FRAMEWORK/model-pruning-blueprint.md`
- **指标**: token_jaccard=0.4521, heading_jaccard=1.0, |∩token|=66
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「知识蒸馏蓝图…」 / B「模型剪枝蓝图…」
- **建议 canonical**: `docs/01_FRAMEWORK/knowledge-distillation-blueprint.md`
- **理由（机器）**: 建议正文体量更大（可能更完整）
- **另一路径**: `docs/01_FRAMEWORK/model-pruning-blueprint.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 27. score=0.6971

- **A**: `docs/01_FRAMEWORK/model-watermark-blueprint.md`
- **B**: `docs/01_FRAMEWORK/multimodal-fusion-blueprint.md`
- **指标**: token_jaccard=0.4493, heading_jaccard=1.0, |∩token|=62
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「模型水印蓝图…」 / B「requirements_multimodal.txt…」
- **建议 canonical**: `docs/01_FRAMEWORK/model-watermark-blueprint.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/01_FRAMEWORK/multimodal-fusion-blueprint.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 28. score=0.6967

- **A**: `docs/01_FRAMEWORK/mia-defense-blueprint.md`
- **B**: `docs/01_FRAMEWORK/multimodal-fusion-blueprint.md`
- **指标**: token_jaccard=0.4485, heading_jaccard=1.0, |∩token|=61
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「MIA防御蓝图…」 / B「requirements_multimodal.txt…」
- **建议 canonical**: `docs/01_FRAMEWORK/mia-defense-blueprint.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/01_FRAMEWORK/multimodal-fusion-blueprint.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 29. score=0.6953

- **A**: `docs/01_FRAMEWORK/model-pruning-blueprint.md`
- **B**: `docs/01_FRAMEWORK/multimodal-fusion-blueprint.md`
- **指标**: token_jaccard=0.446, heading_jaccard=1.0, |∩token|=62
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「模型剪枝蓝图…」 / B「requirements_multimodal.txt…」
- **建议 canonical**: `docs/01_FRAMEWORK/model-pruning-blueprint.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/01_FRAMEWORK/multimodal-fusion-blueprint.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 30. score=0.6944

- **A**: `docs/01_FRAMEWORK/mamba-ssm-blueprint.md`
- **B**: `docs/01_FRAMEWORK/mia-defense-blueprint.md`
- **指标**: token_jaccard=0.4444, heading_jaccard=1.0, |∩token|=60
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「requirements_mamba.txt…」 / B「MIA防御蓝图…」
- **建议 canonical**: `docs/01_FRAMEWORK/mia-defense-blueprint.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/01_FRAMEWORK/mamba-ssm-blueprint.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 31. score=0.6932

- **A**: `docs/01_FRAMEWORK/model-quantization-blueprint.md`
- **B**: `docs/01_FRAMEWORK/model-watermark-blueprint.md`
- **指标**: token_jaccard=0.4422, heading_jaccard=1.0, |∩token|=65
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「模型量化蓝图…」 / B「模型水印蓝图…」
- **建议 canonical**: `docs/01_FRAMEWORK/model-quantization-blueprint.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/01_FRAMEWORK/model-watermark-blueprint.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 32. score=0.6928

- **A**: `docs/01_FRAMEWORK/mia-defense-blueprint.md`
- **B**: `docs/01_FRAMEWORK/model-quantization-blueprint.md`
- **指标**: token_jaccard=0.4414, heading_jaccard=1.0, |∩token|=64
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「MIA防御蓝图…」 / B「模型量化蓝图…」
- **建议 canonical**: `docs/01_FRAMEWORK/model-quantization-blueprint.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/01_FRAMEWORK/mia-defense-blueprint.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 33. score=0.6926

- **A**: `docs/01_FRAMEWORK/mia-defense-blueprint.md`
- **B**: `docs/01_FRAMEWORK/mixture-of-experts-blueprint.md`
- **指标**: token_jaccard=0.4412, heading_jaccard=1.0, |∩token|=60
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「MIA防御蓝图…」 / B「混合专家模型(MoE)蓝图…」
- **建议 canonical**: `docs/01_FRAMEWORK/mia-defense-blueprint.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/01_FRAMEWORK/mixture-of-experts-blueprint.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 34. score=0.692

- **A**: `docs/01_FRAMEWORK/fund-management-interface-blueprint.md`
- **B**: `docs/01_FRAMEWORK/position-management-interface-blueprint.md`
- **指标**: token_jaccard=0.4643, heading_jaccard=1.0, |∩token|=52
- **共有 H2（归一化后）**: 📋 一、概述, 🔧 三、开源项目集成, 🚀 二、实施路径
- **标题**: A「资金管理界面蓝图…」 / B「持仓管理界面蓝图…」
- **建议 canonical**: `docs/01_FRAMEWORK/fund-management-interface-blueprint.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/01_FRAMEWORK/position-management-interface-blueprint.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 📋 一、概述
  - 🚀 二、实施路径
  - 🔧 三、开源项目集成

### 35. score=0.6899

- **A**: `docs/01_FRAMEWORK/market-microstructure-model-blueprint.md`
- **B**: `docs/01_FRAMEWORK/model-watermark-blueprint.md`
- **指标**: token_jaccard=0.4362, heading_jaccard=1.0, |∩token|=65
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「市场微观结构模型蓝图…」 / B「模型水印蓝图…」
- **建议 canonical**: `docs/01_FRAMEWORK/market-microstructure-model-blueprint.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/01_FRAMEWORK/model-watermark-blueprint.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 36. score=0.6891

- **A**: `docs/01_FRAMEWORK/mamba-ssm-blueprint.md`
- **B**: `docs/01_FRAMEWORK/model-watermark-blueprint.md`
- **指标**: token_jaccard=0.4348, heading_jaccard=1.0, |∩token|=60
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「requirements_mamba.txt…」 / B「模型水印蓝图…」
- **建议 canonical**: `docs/01_FRAMEWORK/model-watermark-blueprint.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/01_FRAMEWORK/mamba-ssm-blueprint.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 37. score=0.6879

- **A**: `docs/01_FRAMEWORK/mia-defense-blueprint.md`
- **B**: `docs/01_FRAMEWORK/model-performance-benchmark-blueprint.md`
- **指标**: token_jaccard=0.4326, heading_jaccard=1.0, |∩token|=61
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「MIA防御蓝图…」 / B「模型性能基准蓝图…」
- **建议 canonical**: `docs/01_FRAMEWORK/model-performance-benchmark-blueprint.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/01_FRAMEWORK/mia-defense-blueprint.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 38. score=0.6879

- **A**: `docs/08_HUMAN_AI_INTERFACE/69_CAPACITY_PLANNING_TOOL/capacity-planning-tool-blueprint.md`
- **B**: `docs/08_HUMAN_AI_INTERFACE/70_COST_MANAGEMENT_TOOL/cost-management-tool-blueprint.md`
- **指标**: token_jaccard=0.4326, heading_jaccard=1.0, |∩token|=61
- **共有 H2（归一化后）**: 🎯 核心功能, 📋 模块概览, 🚀 实施计划
- **标题**: A「模块69: 容量规划工具 (CAPACITY_PLANNING_TOOL)…」 / B「模块70: 成本管理工具 (COST_MANAGEMENT_TOOL)…」
- **建议 canonical**: `docs/08_HUMAN_AI_INTERFACE/69_CAPACITY_PLANNING_TOOL/capacity-planning-tool-blueprint.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/08_HUMAN_AI_INTERFACE/70_COST_MANAGEMENT_TOOL/cost-management-tool-blueprint.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 📋 模块概览
  - 🎯 核心功能
  - 🚀 实施计划

### 39. score=0.6874

- **A**: `docs/01_FRAMEWORK/mamba-ssm-blueprint.md`
- **B**: `docs/01_FRAMEWORK/model-pruning-blueprint.md`
- **指标**: token_jaccard=0.4317, heading_jaccard=1.0, |∩token|=60
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「requirements_mamba.txt…」 / B「模型剪枝蓝图…」
- **建议 canonical**: `docs/01_FRAMEWORK/model-pruning-blueprint.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/01_FRAMEWORK/mamba-ssm-blueprint.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 40. score=0.687

- **A**: `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/risk-contribution-analysis-blueprint.md`
- **B**: `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/strategy-portfolio-optimization-blueprint.md`
- **指标**: token_jaccard=0.4309, heading_jaccard=1.0, |∩token|=187
- **共有 H2（归一化后）**: 1. 概述, 2. 技术实现, 3. 接口定义, 4. 实施路径, 5. 文档治理, 变更历史
- **标题**: A「风险贡献分析蓝图…」 / B「策略组合优化蓝图…」
- **建议 canonical**: `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/risk-contribution-analysis-blueprint.md`
- **理由（机器）**: 建议路径含图纸柜 `01_BLUEPRINTS`
- **另一路径**: `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/strategy-portfolio-optimization-blueprint.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 核心定位
  - 设计目标
  - 核心功能
  - 实现方案
  - 1. 概述
  - 📚 相关文档
  - 2. 技术实现
  - 3. 接口定义
  - 4. 实施路径
  - 变更历史
  - 接口与契约（蓝图终稿）
  - 验收标准（可检查）
  - 已知限制
  - 5. 文档治理

### 41. score=0.6865

- **A**: `docs/01_FRAMEWORK/self-supervised-learning-blueprint.md`
- **B**: `docs/01_FRAMEWORK/synthetic-data-generation-blueprint.md`
- **指标**: token_jaccard=0.4361, heading_jaccard=1.0, |∩token|=58
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「requirements_ssl.txt…」 / B「requirements_synthetic.txt…」
- **建议 canonical**: `docs/01_FRAMEWORK/self-supervised-learning-blueprint.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/01_FRAMEWORK/synthetic-data-generation-blueprint.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 42. score=0.6857

- **A**: `docs/01_FRAMEWORK/mixture-of-experts-blueprint.md`
- **B**: `docs/01_FRAMEWORK/model-pruning-blueprint.md`
- **指标**: token_jaccard=0.4286, heading_jaccard=1.0, |∩token|=60
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「混合专家模型(MoE)蓝图…」 / B「模型剪枝蓝图…」
- **建议 canonical**: `docs/01_FRAMEWORK/model-pruning-blueprint.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/01_FRAMEWORK/mixture-of-experts-blueprint.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 43. score=0.6852

- **A**: `docs/01_FRAMEWORK/knowledge-distillation-blueprint.md`
- **B**: `docs/01_FRAMEWORK/multimodal-fusion-blueprint.md`
- **指标**: token_jaccard=0.4276, heading_jaccard=1.0, |∩token|=62
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「知识蒸馏蓝图…」 / B「requirements_multimodal.txt…」
- **建议 canonical**: `docs/01_FRAMEWORK/knowledge-distillation-blueprint.md`
- **理由（机器）**: 建议正文体量更大（可能更完整）
- **另一路径**: `docs/01_FRAMEWORK/multimodal-fusion-blueprint.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 44. score=0.6836

- **A**: `docs/01_FRAMEWORK/knowledge-distillation-blueprint.md`
- **B**: `docs/01_FRAMEWORK/mia-defense-blueprint.md`
- **指标**: token_jaccard=0.4247, heading_jaccard=1.0, |∩token|=62
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「知识蒸馏蓝图…」 / B「MIA防御蓝图…」
- **建议 canonical**: `docs/01_FRAMEWORK/knowledge-distillation-blueprint.md`
- **理由（机器）**: 建议正文体量更大（可能更完整）
- **另一路径**: `docs/01_FRAMEWORK/mia-defense-blueprint.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 45. score=0.6836

- **A**: `docs/01_FRAMEWORK/model-quantization-blueprint.md`
- **B**: `docs/01_FRAMEWORK/multimodal-fusion-blueprint.md`
- **指标**: token_jaccard=0.4247, heading_jaccard=1.0, |∩token|=62
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「模型量化蓝图…」 / B「requirements_multimodal.txt…」
- **建议 canonical**: `docs/01_FRAMEWORK/model-quantization-blueprint.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/01_FRAMEWORK/multimodal-fusion-blueprint.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 46. score=0.6832

- **A**: `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/portfolio-attribution-blueprint.md`
- **B**: `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/portfolio-constraint-management-blueprint.md`
- **指标**: token_jaccard=0.424, heading_jaccard=1.0, |∩token|=173
- **共有 H2（归一化后）**: 1. 概述, 3. 接口定义, 4. 实施路径, 5. 文档治理, 变更历史, 实现方案
- **标题**: A「组合归因分析模块蓝图…」 / B「组合约束管理模块蓝图…」
- **建议 canonical**: `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/portfolio-attribution-blueprint.md`
- **理由（机器）**: 建议路径含图纸柜 `01_BLUEPRINTS`
- **另一路径**: `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/portfolio-constraint-management-blueprint.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 核心定位
  - 设计目标
  - 核心功能
  - 实现方案
  - 1. 概述
  - 3. 接口定义
  - 4. 实施路径
  - 接口与契约（蓝图终稿）
  - 验收标准（可检查）
  - 已知限制
  - 变更历史
  - 5. 文档治理

### 47. score=0.683

- **A**: `docs/01_FRAMEWORK/model-performance-benchmark-blueprint.md`
- **B**: `docs/01_FRAMEWORK/model-watermark-blueprint.md`
- **指标**: token_jaccard=0.4236, heading_jaccard=1.0, |∩token|=61
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「模型性能基准蓝图…」 / B「模型水印蓝图…」
- **建议 canonical**: `docs/01_FRAMEWORK/model-performance-benchmark-blueprint.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/01_FRAMEWORK/model-watermark-blueprint.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 48. score=0.6826

- **A**: `docs/01_FRAMEWORK/model-versioning-blueprint.md`
- **B**: `docs/01_FRAMEWORK/model-watermark-blueprint.md`
- **指标**: token_jaccard=0.4228, heading_jaccard=1.0, |∩token|=63
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「模型版本控制蓝图…」 / B「模型水印蓝图…」
- **建议 canonical**: `docs/01_FRAMEWORK/model-versioning-blueprint.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/01_FRAMEWORK/model-watermark-blueprint.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 49. score=0.6818

- **A**: `docs/01_FRAMEWORK/model-rollback-blueprint.md`
- **B**: `docs/01_FRAMEWORK/model-versioning-blueprint.md`
- **指标**: token_jaccard=0.4214, heading_jaccard=1.0, |∩token|=67
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「模型回滚机制蓝图…」 / B「模型版本控制蓝图…」
- **建议 canonical**: `docs/01_FRAMEWORK/model-rollback-blueprint.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/01_FRAMEWORK/model-versioning-blueprint.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 50. score=0.6814

- **A**: `docs/01_FRAMEWORK/model-performance-benchmark-blueprint.md`
- **B**: `docs/01_FRAMEWORK/model-pruning-blueprint.md`
- **指标**: token_jaccard=0.4207, heading_jaccard=1.0, |∩token|=61
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「模型性能基准蓝图…」 / B「模型剪枝蓝图…」
- **建议 canonical**: `docs/01_FRAMEWORK/model-performance-benchmark-blueprint.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/01_FRAMEWORK/model-pruning-blueprint.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 51. score=0.6808

- **A**: `docs/01_FRAMEWORK/model-lineage-blueprint.md`
- **B**: `docs/01_FRAMEWORK/model-watermark-blueprint.md`
- **指标**: token_jaccard=0.4196, heading_jaccard=1.0, |∩token|=60
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「requirements_lineage.txt…」 / B「模型水印蓝图…」
- **建议 canonical**: `docs/01_FRAMEWORK/model-lineage-blueprint.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/01_FRAMEWORK/model-watermark-blueprint.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 52. score=0.6789

- **A**: `docs/08_HUMAN_AI_INTERFACE/55_PERFORMANCE_ANALYSIS_TOOLS/performance-analysis-tools-blueprint.md`
- **B**: `docs/08_HUMAN_AI_INTERFACE/59_PERF_BENCHMARK_VALIDATION/performance-benchmark-testing-blueprint.md`
- **指标**: token_jaccard=0.4464, heading_jaccard=1.0, |∩token|=50
- **共有 H2（归一化后）**: 🎯 核心功能, 🏗️ 推荐方案, 📋 模块概览
- **标题**: A「模块55: 性能分析工具 (PERFORMANCE_ANALYSIS_TOOLS)…」 / B「模块59: 性能基准测试 (PERFORMANCE_BENCHMARK_TESTING)…」
- **建议 canonical**: `docs/08_HUMAN_AI_INTERFACE/55_PERFORMANCE_ANALYSIS_TOOLS/performance-analysis-tools-blueprint.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/08_HUMAN_AI_INTERFACE/59_PERF_BENCHMARK_VALIDATION/performance-benchmark-testing-blueprint.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 📋 模块概览
  - 🎯 核心功能
  - 🏗️ 推荐方案

### 53. score=0.6786

- **A**: `docs/01_FRAMEWORK/model-rollback-blueprint.md`
- **B**: `docs/01_FRAMEWORK/model-watermark-blueprint.md`
- **指标**: token_jaccard=0.4156, heading_jaccard=1.0, |∩token|=64
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「模型回滚机制蓝图…」 / B「模型水印蓝图…」
- **建议 canonical**: `docs/01_FRAMEWORK/model-rollback-blueprint.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/01_FRAMEWORK/model-watermark-blueprint.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 54. score=0.678

- **A**: `docs/01_FRAMEWORK/market-microstructure-model-blueprint.md`
- **B**: `docs/01_FRAMEWORK/model-performance-benchmark-blueprint.md`
- **指标**: token_jaccard=0.4145, heading_jaccard=1.0, |∩token|=63
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「市场微观结构模型蓝图…」 / B「模型性能基准蓝图…」
- **建议 canonical**: `docs/01_FRAMEWORK/market-microstructure-model-blueprint.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/01_FRAMEWORK/model-performance-benchmark-blueprint.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 55. score=0.6776

- **A**: `docs/01_FRAMEWORK/knowledge-distillation-blueprint.md`
- **B**: `docs/01_FRAMEWORK/mamba-ssm-blueprint.md`
- **指标**: token_jaccard=0.4138, heading_jaccard=1.0, |∩token|=60
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「知识蒸馏蓝图…」 / B「requirements_mamba.txt…」
- **建议 canonical**: `docs/01_FRAMEWORK/knowledge-distillation-blueprint.md`
- **理由（机器）**: 建议正文体量更大（可能更完整）
- **另一路径**: `docs/01_FRAMEWORK/mamba-ssm-blueprint.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 56. score=0.6773

- **A**: `docs/01_FRAMEWORK/rag-system-blueprint.md`
- **B**: `docs/01_FRAMEWORK/text-encoder-blueprint.md`
- **指标**: token_jaccard=0.4344, heading_jaccard=1.0, |∩token|=53
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「requirements_rag.txt…」 / B「requirements_text.txt…」
- **建议 canonical**: `docs/01_FRAMEWORK/rag-system-blueprint.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/01_FRAMEWORK/text-encoder-blueprint.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 57. score=0.6771

- **A**: `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/liquidity-constrained-optimization-blueprint.md`
- **B**: `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/portfolio-diversification-metric-blueprint.md`
- **指标**: token_jaccard=0.4129, heading_jaccard=1.0, |∩token|=109
- **共有 H2（归一化后）**: 2. 功能设计, 3., 4. 变更历史, 5. 文档治理, 变更历史, 实现方案
- **标题**: A「执行计划…」 / B「有效资产数量…」
- **建议 canonical**: `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/liquidity-constrained-optimization-blueprint.md`
- **理由（机器）**: 建议路径含图纸柜 `01_BLUEPRINTS`
- **另一路径**: `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/portfolio-diversification-metric-blueprint.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 核心定位
  - 接口与契约（蓝图终稿）
  - 验收标准（可检查）
  - 已知限制
  - 设计目标
  - 核心功能
  - 实现方案
  - 2. 功能设计
  - 3.
  - 4. 变更历史
  - 5. 文档治理
  - 变更历史

### 58. score=0.6769

- **A**: `docs/01_FRAMEWORK/model-performance-benchmark-blueprint.md`
- **B**: `docs/01_FRAMEWORK/multimodal-fusion-blueprint.md`
- **指标**: token_jaccard=0.4155, heading_jaccard=1.0, |∩token|=59
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「模型性能基准蓝图…」 / B「requirements_multimodal.txt…」
- **建议 canonical**: `docs/01_FRAMEWORK/model-performance-benchmark-blueprint.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/01_FRAMEWORK/multimodal-fusion-blueprint.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 59. score=0.6761

- **A**: `docs/08_HUMAN_AI_INTERFACE/45_CONFIG_MANAGEMENT/config-management-blueprint.md`
- **B**: `docs/08_HUMAN_AI_INTERFACE/48_VERSION_MANAGEMENT/version-management-blueprint.md`
- **指标**: token_jaccard=0.411, heading_jaccard=1.0, |∩token|=67
- **共有 H2（归一化后）**: 🎯 功能需求, 🏗️ 技术架构, 📋 模块概览, 🚀 实施计划
- **标题**: A「模块45: 配置管理 (CONFIG_MANAGEMENT)…」 / B「模块48: 版本管理 (VERSION_MANAGEMENT)…」
- **建议 canonical**: `docs/08_HUMAN_AI_INTERFACE/45_CONFIG_MANAGEMENT/config-management-blueprint.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/08_HUMAN_AI_INTERFACE/48_VERSION_MANAGEMENT/version-management-blueprint.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 📋 模块概览
  - 🎯 功能需求
  - 🏗️ 技术架构
  - 🚀 实施计划

### 60. score=0.676

- **A**: `docs/01_FRAMEWORK/knowledge-distillation-blueprint.md`
- **B**: `docs/01_FRAMEWORK/mixture-of-experts-blueprint.md`
- **指标**: token_jaccard=0.411, heading_jaccard=1.0, |∩token|=60
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「知识蒸馏蓝图…」 / B「混合专家模型(MoE)蓝图…」
- **建议 canonical**: `docs/01_FRAMEWORK/knowledge-distillation-blueprint.md`
- **理由（机器）**: 建议正文体量更大（可能更完整）
- **另一路径**: `docs/01_FRAMEWORK/mixture-of-experts-blueprint.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 61. score=0.676

- **A**: `docs/01_FRAMEWORK/mamba-ssm-blueprint.md`
- **B**: `docs/01_FRAMEWORK/model-quantization-blueprint.md`
- **指标**: token_jaccard=0.411, heading_jaccard=1.0, |∩token|=60
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「requirements_mamba.txt…」 / B「模型量化蓝图…」
- **建议 canonical**: `docs/01_FRAMEWORK/model-quantization-blueprint.md`
- **理由（机器）**: 建议正文体量更大（可能更完整）
- **另一路径**: `docs/01_FRAMEWORK/mamba-ssm-blueprint.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 62. score=0.6758

- **A**: `docs/01_FRAMEWORK/model-performance-benchmark-blueprint.md`
- **B**: `docs/01_FRAMEWORK/model-quantization-blueprint.md`
- **指标**: token_jaccard=0.4106, heading_jaccard=1.0, |∩token|=62
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「模型性能基准蓝图…」 / B「模型量化蓝图…」
- **建议 canonical**: `docs/01_FRAMEWORK/model-quantization-blueprint.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/01_FRAMEWORK/model-performance-benchmark-blueprint.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 63. score=0.6745

- **A**: `docs/01_FRAMEWORK/mixture-of-experts-blueprint.md`
- **B**: `docs/01_FRAMEWORK/model-quantization-blueprint.md`
- **指标**: token_jaccard=0.4082, heading_jaccard=1.0, |∩token|=60
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「混合专家模型(MoE)蓝图…」 / B「模型量化蓝图…」
- **建议 canonical**: `docs/01_FRAMEWORK/model-quantization-blueprint.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/01_FRAMEWORK/mixture-of-experts-blueprint.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 64. score=0.6744

- **A**: `docs/01_FRAMEWORK/self-supervised-learning-blueprint.md`
- **B**: `docs/01_FRAMEWORK/text-encoder-blueprint.md`
- **指标**: token_jaccard=0.4231, heading_jaccard=1.0, |∩token|=55
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「requirements_ssl.txt…」 / B「requirements_text.txt…」
- **建议 canonical**: `docs/01_FRAMEWORK/self-supervised-learning-blueprint.md`
- **理由（机器）**: 建议正文体量更大（可能更完整）
- **另一路径**: `docs/01_FRAMEWORK/text-encoder-blueprint.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 65. score=0.6739

- **A**: `docs/01_FRAMEWORK/prompt-engineering-blueprint.md`
- **B**: `docs/01_FRAMEWORK/rag-system-blueprint.md`
- **指标**: token_jaccard=0.4252, heading_jaccard=1.0, |∩token|=54
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「requirements_prompt.txt…」 / B「requirements_rag.txt…」
- **建议 canonical**: `docs/01_FRAMEWORK/rag-system-blueprint.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/01_FRAMEWORK/prompt-engineering-blueprint.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 66. score=0.6737

- **A**: `docs/01_FRAMEWORK/market-microstructure-model-blueprint.md`
- **B**: `docs/01_FRAMEWORK/mia-defense-blueprint.md`
- **指标**: token_jaccard=0.4067, heading_jaccard=1.0, |∩token|=61
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「市场微观结构模型蓝图…」 / B「MIA防御蓝图…」
- **建议 canonical**: `docs/01_FRAMEWORK/market-microstructure-model-blueprint.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/01_FRAMEWORK/mia-defense-blueprint.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 67. score=0.6729

- **A**: `docs/01_FRAMEWORK/model-lineage-blueprint.md`
- **B**: `docs/01_FRAMEWORK/multimodal-fusion-blueprint.md`
- **指标**: token_jaccard=0.4113, heading_jaccard=1.0, |∩token|=58
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「requirements_lineage.txt…」 / B「requirements_multimodal.txt…」
- **建议 canonical**: `docs/01_FRAMEWORK/model-lineage-blueprint.md`
- **理由（机器）**: 建议正文体量更大（可能更完整）
- **另一路径**: `docs/01_FRAMEWORK/multimodal-fusion-blueprint.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 68. score=0.6728

- **A**: `docs/01_FRAMEWORK/model-ab-testing-blueprint.md`
- **B**: `docs/01_FRAMEWORK/model-watermark-blueprint.md`
- **指标**: token_jaccard=0.4051, heading_jaccard=1.0, |∩token|=64
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「模型A/B测试蓝图…」 / B「模型水印蓝图…」
- **建议 canonical**: `docs/01_FRAMEWORK/model-ab-testing-blueprint.md`
- **理由（机器）**: 建议正文体量更大（可能更完整）
- **另一路径**: `docs/01_FRAMEWORK/model-watermark-blueprint.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 69. score=0.6727

- **A**: `docs/01_FRAMEWORK/llm-fine-tuning-blueprint.md`
- **B**: `docs/01_FRAMEWORK/mia-defense-blueprint.md`
- **指标**: token_jaccard=0.4049, heading_jaccard=1.0, |∩token|=66
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「基础模型微调蓝图…」 / B「MIA防御蓝图…」
- **建议 canonical**: `docs/01_FRAMEWORK/llm-fine-tuning-blueprint.md`
- **理由（机器）**: 建议正文体量更大（可能更完整）
- **另一路径**: `docs/01_FRAMEWORK/mia-defense-blueprint.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 70. score=0.6721

- **A**: `docs/01_FRAMEWORK/model-lineage-blueprint.md`
- **B**: `docs/01_FRAMEWORK/model-pruning-blueprint.md`
- **指标**: token_jaccard=0.4069, heading_jaccard=1.0, |∩token|=59
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「requirements_lineage.txt…」 / B「模型剪枝蓝图…」
- **建议 canonical**: `docs/01_FRAMEWORK/model-lineage-blueprint.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/01_FRAMEWORK/model-pruning-blueprint.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 71. score=0.672

- **A**: `docs/01_FRAMEWORK/automl-pipeline-blueprint.md`
- **B**: `docs/01_FRAMEWORK/text-encoder-blueprint.md`
- **指标**: token_jaccard=0.4219, heading_jaccard=1.0, |∩token|=54
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「requirements_automl.txt…」 / B「requirements_text.txt…」
- **建议 canonical**: `docs/01_FRAMEWORK/automl-pipeline-blueprint.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/01_FRAMEWORK/text-encoder-blueprint.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 72. score=0.672

- **A**: `docs/01_FRAMEWORK/synthetic-data-generation-blueprint.md`
- **B**: `docs/01_FRAMEWORK/text-encoder-blueprint.md`
- **指标**: token_jaccard=0.4219, heading_jaccard=1.0, |∩token|=54
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「requirements_synthetic.txt…」 / B「requirements_text.txt…」
- **建议 canonical**: `docs/01_FRAMEWORK/synthetic-data-generation-blueprint.md`
- **理由（机器）**: 建议正文体量更大（可能更完整）
- **另一路径**: `docs/01_FRAMEWORK/text-encoder-blueprint.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 73. score=0.6715

- **A**: `docs/01_FRAMEWORK/mia-defense-blueprint.md`
- **B**: `docs/01_FRAMEWORK/model-versioning-blueprint.md`
- **指标**: token_jaccard=0.4027, heading_jaccard=1.0, |∩token|=60
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「MIA防御蓝图…」 / B「模型版本控制蓝图…」
- **建议 canonical**: `docs/01_FRAMEWORK/model-versioning-blueprint.md`
- **理由（机器）**: 建议正文体量更大（可能更完整）
- **另一路径**: `docs/01_FRAMEWORK/mia-defense-blueprint.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 74. score=0.6713

- **A**: `docs/01_FRAMEWORK/mia-defense-blueprint.md`
- **B**: `docs/01_FRAMEWORK/model-lineage-blueprint.md`
- **指标**: token_jaccard=0.4085, heading_jaccard=1.0, |∩token|=58
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「MIA防御蓝图…」 / B「requirements_lineage.txt…」
- **建议 canonical**: `docs/01_FRAMEWORK/model-lineage-blueprint.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/01_FRAMEWORK/mia-defense-blueprint.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 75. score=0.6713

- **A**: `docs/01_FRAMEWORK/mixture-of-experts-blueprint.md`
- **B**: `docs/01_FRAMEWORK/model-performance-benchmark-blueprint.md`
- **指标**: token_jaccard=0.4085, heading_jaccard=1.0, |∩token|=58
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「混合专家模型(MoE)蓝图…」 / B「模型性能基准蓝图…」
- **建议 canonical**: `docs/01_FRAMEWORK/model-performance-benchmark-blueprint.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/01_FRAMEWORK/mixture-of-experts-blueprint.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 76. score=0.6707

- **A**: `docs/01_FRAMEWORK/model-performance-benchmark-blueprint.md`
- **B**: `docs/01_FRAMEWORK/model-versioning-blueprint.md`
- **指标**: token_jaccard=0.4013, heading_jaccard=1.0, |∩token|=61
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「模型性能基准蓝图…」 / B「模型版本控制蓝图…」
- **建议 canonical**: `docs/01_FRAMEWORK/model-versioning-blueprint.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/01_FRAMEWORK/model-performance-benchmark-blueprint.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 77. score=0.6707

- **A**: `docs/01_FRAMEWORK/model-pruning-blueprint.md`
- **B**: `docs/01_FRAMEWORK/model-versioning-blueprint.md`
- **指标**: token_jaccard=0.4013, heading_jaccard=1.0, |∩token|=61
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「模型剪枝蓝图…」 / B「模型版本控制蓝图…」
- **建议 canonical**: `docs/01_FRAMEWORK/model-versioning-blueprint.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/01_FRAMEWORK/model-pruning-blueprint.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 78. score=0.6707

- **A**: `docs/01_FRAMEWORK/model-quantization-blueprint.md`
- **B**: `docs/01_FRAMEWORK/model-versioning-blueprint.md`
- **指标**: token_jaccard=0.4013, heading_jaccard=1.0, |∩token|=63
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「模型量化蓝图…」 / B「模型版本控制蓝图…」
- **建议 canonical**: `docs/01_FRAMEWORK/model-versioning-blueprint.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/01_FRAMEWORK/model-quantization-blueprint.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 79. score=0.6705

- **A**: `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/multi-objective-optimization-blueprint.md`
- **B**: `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/portfolio-constraint-management-blueprint.md`
- **指标**: token_jaccard=0.4009, heading_jaccard=1.0, |∩token|=170
- **共有 H2（归一化后）**: 1. 概述, 3. 接口定义, 4. 实施路径, 5. 文档治理, 变更历史, 实现方案
- **标题**: A「…」 / B「组合约束管理模块蓝图…」
- **建议 canonical**: `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/multi-objective-optimization-blueprint.md`
- **理由（机器）**: 建议路径含图纸柜 `01_BLUEPRINTS`
- **另一路径**: `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/portfolio-constraint-management-blueprint.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 核心定位
  - 设计目标
  - 核心功能
  - 实现方案
  - 1. 概述
  - 3. 接口定义
  - 4. 实施路径
  - 接口与契约（蓝图终稿）
  - 验收标准（可检查）
  - 已知限制
  - 变更历史
  - 5. 文档治理

### 80. score=0.67

- **A**: `docs/01_FRAMEWORK/market-microstructure-model-blueprint.md`
- **B**: `docs/01_FRAMEWORK/multimodal-fusion-blueprint.md`
- **指标**: token_jaccard=0.4, heading_jaccard=1.0, |∩token|=60
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「市场微观结构模型蓝图…」 / B「requirements_multimodal.txt…」
- **建议 canonical**: `docs/01_FRAMEWORK/market-microstructure-model-blueprint.md`
- **理由（机器）**: 建议正文体量更大（可能更完整）
- **另一路径**: `docs/01_FRAMEWORK/multimodal-fusion-blueprint.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 81. score=0.67

- **A**: `docs/01_FRAMEWORK/model-lineage-blueprint.md`
- **B**: `docs/01_FRAMEWORK/model-rollback-blueprint.md`
- **指标**: token_jaccard=0.4, heading_jaccard=1.0, |∩token|=62
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「requirements_lineage.txt…」 / B「模型回滚机制蓝图…」
- **建议 canonical**: `docs/01_FRAMEWORK/model-rollback-blueprint.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/01_FRAMEWORK/model-lineage-blueprint.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 82. score=0.6685

- **A**: `docs/01_FRAMEWORK/knowledge-distillation-blueprint.md`
- **B**: `docs/01_FRAMEWORK/model-watermark-blueprint.md`
- **指标**: token_jaccard=0.3974, heading_jaccard=1.0, |∩token|=60
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「知识蒸馏蓝图…」 / B「模型水印蓝图…」
- **建议 canonical**: `docs/01_FRAMEWORK/knowledge-distillation-blueprint.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/01_FRAMEWORK/model-watermark-blueprint.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 83. score=0.6685

- **A**: `docs/01_FRAMEWORK/model-lineage-blueprint.md`
- **B**: `docs/01_FRAMEWORK/model-quantization-blueprint.md`
- **指标**: token_jaccard=0.3974, heading_jaccard=1.0, |∩token|=60
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「requirements_lineage.txt…」 / B「模型量化蓝图…」
- **建议 canonical**: `docs/01_FRAMEWORK/model-lineage-blueprint.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/01_FRAMEWORK/model-quantization-blueprint.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 84. score=0.6685

- **A**: `docs/01_FRAMEWORK/model-lineage-blueprint.md`
- **B**: `docs/01_FRAMEWORK/model-versioning-blueprint.md`
- **指标**: token_jaccard=0.3974, heading_jaccard=1.0, |∩token|=60
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「requirements_lineage.txt…」 / B「模型版本控制蓝图…」
- **建议 canonical**: `docs/01_FRAMEWORK/model-versioning-blueprint.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/01_FRAMEWORK/model-lineage-blueprint.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 85. score=0.6683

- **A**: `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/data-governance-platform-blueprint.md`
- **B**: `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/data-mesh-blueprint.md`
- **指标**: token_jaccard=0.397, heading_jaccard=1.0, |∩token|=131
- **共有 H2（归一化后）**: 1. 文档治理, 一、设计背景与目标, 变更历史, 实现方案, 已知限制, 接口与契约（蓝图终稿）
- **标题**: A「DATA GOVERNANCE PLATFORM BLUEPRINT…」 / B「DATA MESH BLUEPRINT…」
- **建议 canonical**: `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/data-governance-platform-blueprint.md`
- **理由（机器）**: 建议路径含图纸柜 `01_BLUEPRINTS`；建议正文体量更大（可能更完整）
- **另一路径**: `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/data-mesh-blueprint.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 核心定位
  - 设计目标
  - 核心功能
  - 实现方案
  - 一、设计背景与目标
  - 1. 文档治理
  - 接口与契约（蓝图终稿）
  - 验收标准（可检查）
  - 已知限制
  - 变更历史

### 86. score=0.6679

- **A**: `docs/01_FRAMEWORK/neural-architecture-search-blueprint.md`
- **B**: `docs/01_FRAMEWORK/text-encoder-blueprint.md`
- **指标**: token_jaccard=0.4173, heading_jaccard=1.0, |∩token|=53
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「requirements_nas.txt…」 / B「requirements_text.txt…」
- **建议 canonical**: `docs/01_FRAMEWORK/neural-architecture-search-blueprint.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/01_FRAMEWORK/text-encoder-blueprint.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 87. score=0.6678

- **A**: `docs/08_HUMAN_AI_INTERFACE/56_SECURITY_AUDIT/security-audit-blueprint.md`
- **B**: `docs/08_HUMAN_AI_INTERFACE/59_PERF_BENCHMARK_VALIDATION/performance-benchmark-testing-blueprint.md`
- **指标**: token_jaccard=0.4324, heading_jaccard=1.0, |∩token|=48
- **共有 H2（归一化后）**: 🎯 核心功能, 🏗️ 推荐方案, 📋 模块概览
- **标题**: A「模块56: 安全审计 (SECURITY_AUDIT)…」 / B「模块59: 性能基准测试 (PERFORMANCE_BENCHMARK_TESTING)…」
- **建议 canonical**: `docs/08_HUMAN_AI_INTERFACE/59_PERF_BENCHMARK_VALIDATION/performance-benchmark-testing-blueprint.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/08_HUMAN_AI_INTERFACE/56_SECURITY_AUDIT/security-audit-blueprint.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 📋 模块概览
  - 🎯 核心功能
  - 🏗️ 推荐方案

### 88. score=0.6674

- **A**: `docs/01_FRAMEWORK/llm-fine-tuning-blueprint.md`
- **B**: `docs/01_FRAMEWORK/model-pruning-blueprint.md`
- **指标**: token_jaccard=0.3952, heading_jaccard=1.0, |∩token|=66
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「基础模型微调蓝图…」 / B「模型剪枝蓝图…」
- **建议 canonical**: `docs/01_FRAMEWORK/llm-fine-tuning-blueprint.md`
- **理由（机器）**: 建议正文体量更大（可能更完整）
- **另一路径**: `docs/01_FRAMEWORK/model-pruning-blueprint.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 89. score=0.6673

- **A**: `docs/01_FRAMEWORK/mixture-of-experts-blueprint.md`
- **B**: `docs/01_FRAMEWORK/model-lineage-blueprint.md`
- **指标**: token_jaccard=0.4043, heading_jaccard=1.0, |∩token|=57
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「混合专家模型(MoE)蓝图…」 / B「requirements_lineage.txt…」
- **建议 canonical**: `docs/01_FRAMEWORK/model-lineage-blueprint.md`
- **理由（机器）**: 建议正文体量更大（可能更完整）
- **另一路径**: `docs/01_FRAMEWORK/mixture-of-experts-blueprint.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 90. score=0.6672

- **A**: `docs/01_FRAMEWORK/knowledge-distillation-blueprint.md`
- **B**: `docs/01_FRAMEWORK/model-quantization-blueprint.md`
- **指标**: token_jaccard=0.3949, heading_jaccard=1.0, |∩token|=62
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「知识蒸馏蓝图…」 / B「模型量化蓝图…」
- **建议 canonical**: `docs/01_FRAMEWORK/knowledge-distillation-blueprint.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/01_FRAMEWORK/model-quantization-blueprint.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 91. score=0.6661

- **A**: `docs/01_FRAMEWORK/model-versioning-blueprint.md`
- **B**: `docs/01_FRAMEWORK/multimodal-fusion-blueprint.md`
- **指标**: token_jaccard=0.396, heading_jaccard=1.0, |∩token|=59
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「模型版本控制蓝图…」 / B「requirements_multimodal.txt…」
- **建议 canonical**: `docs/01_FRAMEWORK/model-versioning-blueprint.md`
- **理由（机器）**: 建议正文体量更大（可能更完整）
- **另一路径**: `docs/01_FRAMEWORK/multimodal-fusion-blueprint.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 92. score=0.666

- **A**: `docs/01_FRAMEWORK/model-card-blueprint.md`
- **B**: `docs/01_FRAMEWORK/model-watermark-blueprint.md`
- **指标**: token_jaccard=0.3926, heading_jaccard=1.0, |∩token|=64
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「模型卡片蓝图…」 / B「模型水印蓝图…」
- **建议 canonical**: `docs/01_FRAMEWORK/model-card-blueprint.md`
- **理由（机器）**: 建议正文体量更大（可能更完整）
- **另一路径**: `docs/01_FRAMEWORK/model-watermark-blueprint.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 93. score=0.6658

- **A**: `docs/01_FRAMEWORK/mamba-ssm-blueprint.md`
- **B**: `docs/01_FRAMEWORK/model-performance-benchmark-blueprint.md`
- **指标**: token_jaccard=0.4014, heading_jaccard=1.0, |∩token|=57
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「requirements_mamba.txt…」 / B「模型性能基准蓝图…」
- **建议 canonical**: `docs/01_FRAMEWORK/model-performance-benchmark-blueprint.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/01_FRAMEWORK/mamba-ssm-blueprint.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 94. score=0.6652

- **A**: `docs/01_FRAMEWORK/model-lineage-blueprint.md`
- **B**: `docs/01_FRAMEWORK/model-performance-benchmark-blueprint.md`
- **指标**: token_jaccard=0.3973, heading_jaccard=1.0, |∩token|=58
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「requirements_lineage.txt…」 / B「模型性能基准蓝图…」
- **建议 canonical**: `docs/01_FRAMEWORK/model-lineage-blueprint.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/01_FRAMEWORK/model-performance-benchmark-blueprint.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 95. score=0.665

- **A**: `docs/01_FRAMEWORK/multimodal-fusion-blueprint.md`
- **B**: `docs/01_FRAMEWORK/text-encoder-blueprint.md`
- **指标**: token_jaccard=0.4091, heading_jaccard=1.0, |∩token|=54
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「requirements_multimodal.txt…」 / B「requirements_text.txt…」
- **建议 canonical**: `docs/01_FRAMEWORK/multimodal-fusion-blueprint.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/01_FRAMEWORK/text-encoder-blueprint.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 96. score=0.6649

- **A**: `docs/01_FRAMEWORK/model-pruning-blueprint.md`
- **B**: `docs/01_FRAMEWORK/neural-architecture-search-blueprint.md`
- **指标**: token_jaccard=0.4029, heading_jaccard=1.0, |∩token|=56
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「模型剪枝蓝图…」 / B「requirements_nas.txt…」
- **建议 canonical**: `docs/01_FRAMEWORK/model-pruning-blueprint.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/01_FRAMEWORK/neural-architecture-search-blueprint.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 97. score=0.6647

- **A**: `docs/01_FRAMEWORK/market-microstructure-model-blueprint.md`
- **B**: `docs/01_FRAMEWORK/mixture-of-experts-blueprint.md`
- **指标**: token_jaccard=0.3933, heading_jaccard=1.0, |∩token|=59
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「市场微观结构模型蓝图…」 / B「混合专家模型(MoE)蓝图…」
- **建议 canonical**: `docs/01_FRAMEWORK/market-microstructure-model-blueprint.md`
- **理由（机器）**: 建议正文体量更大（可能更完整）
- **另一路径**: `docs/01_FRAMEWORK/mixture-of-experts-blueprint.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 98. score=0.6646

- **A**: `docs/01_FRAMEWORK/llm-fine-tuning-blueprint.md`
- **B**: `docs/01_FRAMEWORK/multimodal-fusion-blueprint.md`
- **指标**: token_jaccard=0.3902, heading_jaccard=1.0, |∩token|=64
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「基础模型微调蓝图…」 / B「requirements_multimodal.txt…」
- **建议 canonical**: `docs/01_FRAMEWORK/llm-fine-tuning-blueprint.md`
- **理由（机器）**: 建议正文体量更大（可能更完整）
- **另一路径**: `docs/01_FRAMEWORK/multimodal-fusion-blueprint.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 99. score=0.6643

- **A**: `docs/01_FRAMEWORK/model-rollback-blueprint.md`
- **B**: `docs/01_FRAMEWORK/multimodal-fusion-blueprint.md`
- **指标**: token_jaccard=0.3896, heading_jaccard=1.0, |∩token|=60
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「模型回滚机制蓝图…」 / B「requirements_multimodal.txt…」
- **建议 canonical**: `docs/01_FRAMEWORK/model-rollback-blueprint.md`
- **理由（机器）**: 建议正文体量更大（可能更完整）
- **另一路径**: `docs/01_FRAMEWORK/multimodal-fusion-blueprint.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 100. score=0.6635

- **A**: `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/multi-period-dynamic-optimization-blueprint.md`
- **B**: `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/portfolio-optimization-diagnostics-blueprint.md`
- **指标**: token_jaccard=0.3881, heading_jaccard=1.0, |∩token|=85
- **共有 H2（归一化后）**: 2. 功能设计, 3. 实施路径, 4. 文档治理, 变更历史, 实现方案, 已知限制
- **标题**: A「…」 / B「组合优化诊断蓝图…」
- **建议 canonical**: `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/multi-period-dynamic-optimization-blueprint.md`
- **理由（机器）**: 建议路径含图纸柜 `01_BLUEPRINTS`；建议正文体量更大（可能更完整）
- **另一路径**: `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/portfolio-optimization-diagnostics-blueprint.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 核心定位
  - 设计目标
  - 核心功能
  - 实现方案
  - 接口与契约（蓝图终稿）
  - 验收标准（可检查）
  - 已知限制
  - 2. 功能设计
  - 3. 实施路径
  - 4. 文档治理
  - 变更历史

### 101. score=0.6629

- **A**: `docs/01_FRAMEWORK/market-microstructure-model-blueprint.md`
- **B**: `docs/01_FRAMEWORK/model-pruning-blueprint.md`
- **指标**: token_jaccard=0.3871, heading_jaccard=1.0, |∩token|=60
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「市场微观结构模型蓝图…」 / B「模型剪枝蓝图…」
- **建议 canonical**: `docs/01_FRAMEWORK/market-microstructure-model-blueprint.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/01_FRAMEWORK/model-pruning-blueprint.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 102. score=0.6618

- **A**: `docs/01_FRAMEWORK/mamba-ssm-blueprint.md`
- **B**: `docs/01_FRAMEWORK/model-lineage-blueprint.md`
- **指标**: token_jaccard=0.3972, heading_jaccard=1.0, |∩token|=56
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「requirements_mamba.txt…」 / B「requirements_lineage.txt…」
- **建议 canonical**: `docs/01_FRAMEWORK/model-lineage-blueprint.md`
- **理由（机器）**: 建议正文体量更大（可能更完整）
- **另一路径**: `docs/01_FRAMEWORK/mamba-ssm-blueprint.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 103. score=0.6608

- **A**: `docs/01_FRAMEWORK/mixture-of-experts-blueprint.md`
- **B**: `docs/01_FRAMEWORK/model-versioning-blueprint.md`
- **指标**: token_jaccard=0.3893, heading_jaccard=1.0, |∩token|=58
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「混合专家模型(MoE)蓝图…」 / B「模型版本控制蓝图…」
- **建议 canonical**: `docs/01_FRAMEWORK/model-versioning-blueprint.md`
- **理由（机器）**: 建议正文体量更大（可能更完整）
- **另一路径**: `docs/01_FRAMEWORK/mixture-of-experts-blueprint.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 104. score=0.6598

- **A**: `docs/01_FRAMEWORK/knowledge-distillation-blueprint.md`
- **B**: `docs/01_FRAMEWORK/llm-fine-tuning-blueprint.md`
- **指标**: token_jaccard=0.3815, heading_jaccard=1.0, |∩token|=66
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「知识蒸馏蓝图…」 / B「基础模型微调蓝图…」
- **建议 canonical**: `docs/01_FRAMEWORK/llm-fine-tuning-blueprint.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/01_FRAMEWORK/knowledge-distillation-blueprint.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 105. score=0.6591

- **A**: `docs/01_FRAMEWORK/model-ab-testing-blueprint.md`
- **B**: `docs/01_FRAMEWORK/model-rollback-blueprint.md`
- **指标**: token_jaccard=0.3801, heading_jaccard=1.0, |∩token|=65
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「模型A/B测试蓝图…」 / B「模型回滚机制蓝图…」
- **建议 canonical**: `docs/01_FRAMEWORK/model-ab-testing-blueprint.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/01_FRAMEWORK/model-rollback-blueprint.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 106. score=0.6588

- **A**: `docs/08_HUMAN_AI_INTERFACE/58_API_DOCUMENTATION_GENERATION/api-documentation-generation-blueprint.md`
- **B**: `docs/08_HUMAN_AI_INTERFACE/60_COLLABORATION_TOOLS/collaboration-tools-blueprint.md`
- **指标**: token_jaccard=0.422, heading_jaccard=1.0, |∩token|=46
- **共有 H2（归一化后）**: 🎯 核心功能, 🏗️ 推荐方案, 📋 模块概览
- **标题**: A「模块58: API文档生成 (API_DOCUMENTATION_GENERATION)…」 / B「模块60: 协作工具 (COLLABORATION_TOOLS)…」
- **建议 canonical**: `docs/08_HUMAN_AI_INTERFACE/60_COLLABORATION_TOOLS/collaboration-tools-blueprint.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/08_HUMAN_AI_INTERFACE/58_API_DOCUMENTATION_GENERATION/api-documentation-generation-blueprint.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 📋 模块概览
  - 🎯 核心功能
  - 🏗️ 推荐方案

### 107. score=0.6584

- **A**: `docs/01_FRAMEWORK/multimodal-fusion-blueprint.md`
- **B**: `docs/01_FRAMEWORK/neural-architecture-search-blueprint.md`
- **指标**: token_jaccard=0.3971, heading_jaccard=1.0, |∩token|=54
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「requirements_multimodal.txt…」 / B「requirements_nas.txt…」
- **建议 canonical**: `docs/01_FRAMEWORK/multimodal-fusion-blueprint.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/01_FRAMEWORK/neural-architecture-search-blueprint.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 108. score=0.6584

- **A**: `docs/01_FRAMEWORK/rag-system-blueprint.md`
- **B**: `docs/01_FRAMEWORK/synthetic-data-generation-blueprint.md`
- **指标**: token_jaccard=0.4031, heading_jaccard=1.0, |∩token|=52
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「requirements_rag.txt…」 / B「requirements_synthetic.txt…」
- **建议 canonical**: `docs/01_FRAMEWORK/synthetic-data-generation-blueprint.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/01_FRAMEWORK/rag-system-blueprint.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 109. score=0.6575

- **A**: `docs/01_FRAMEWORK/model-pruning-blueprint.md`
- **B**: `docs/01_FRAMEWORK/model-rollback-blueprint.md`
- **指标**: token_jaccard=0.3774, heading_jaccard=1.0, |∩token|=60
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「模型剪枝蓝图…」 / B「模型回滚机制蓝图…」
- **建议 canonical**: `docs/01_FRAMEWORK/model-rollback-blueprint.md`
- **理由（机器）**: 建议正文体量更大（可能更完整）
- **另一路径**: `docs/01_FRAMEWORK/model-pruning-blueprint.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 110. score=0.6575

- **A**: `docs/01_FRAMEWORK/neural-architecture-search-blueprint.md`
- **B**: `docs/01_FRAMEWORK/synthetic-data-generation-blueprint.md`
- **指标**: token_jaccard=0.3985, heading_jaccard=1.0, |∩token|=53
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「requirements_nas.txt…」 / B「requirements_synthetic.txt…」
- **建议 canonical**: `docs/01_FRAMEWORK/synthetic-data-generation-blueprint.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/01_FRAMEWORK/neural-architecture-search-blueprint.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 111. score=0.6571

- **A**: `docs/01_FRAMEWORK/model-ab-testing-blueprint.md`
- **B**: `docs/01_FRAMEWORK/model-pruning-blueprint.md`
- **指标**: token_jaccard=0.3765, heading_jaccard=1.0, |∩token|=61
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「模型A/B测试蓝图…」 / B「模型剪枝蓝图…」
- **建议 canonical**: `docs/01_FRAMEWORK/model-ab-testing-blueprint.md`
- **理由（机器）**: 建议正文体量更大（可能更完整）
- **另一路径**: `docs/01_FRAMEWORK/model-pruning-blueprint.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 112. score=0.6567

- **A**: `docs/01_FRAMEWORK/prompt-engineering-blueprint.md`
- **B**: `docs/01_FRAMEWORK/text-encoder-blueprint.md`
- **指标**: token_jaccard=0.4, heading_jaccard=1.0, |∩token|=52
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「requirements_prompt.txt…」 / B「requirements_text.txt…」
- **建议 canonical**: `docs/01_FRAMEWORK/prompt-engineering-blueprint.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/01_FRAMEWORK/text-encoder-blueprint.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 113. score=0.6558

- **A**: `docs/01_FRAMEWORK/mia-defense-blueprint.md`
- **B**: `docs/01_FRAMEWORK/model-card-blueprint.md`
- **指标**: token_jaccard=0.3742, heading_jaccard=1.0, |∩token|=61
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「MIA防御蓝图…」 / B「模型卡片蓝图…」
- **建议 canonical**: `docs/01_FRAMEWORK/model-card-blueprint.md`
- **理由（机器）**: 建议正文体量更大（可能更完整）
- **另一路径**: `docs/01_FRAMEWORK/mia-defense-blueprint.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 114. score=0.6558

- **A**: `docs/01_FRAMEWORK/model-card-blueprint.md`
- **B**: `docs/01_FRAMEWORK/model-versioning-blueprint.md`
- **指标**: token_jaccard=0.3743, heading_jaccard=1.0, |∩token|=64
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「模型卡片蓝图…」 / B「模型版本控制蓝图…」
- **建议 canonical**: `docs/01_FRAMEWORK/model-card-blueprint.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/01_FRAMEWORK/model-versioning-blueprint.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 115. score=0.6554

- **A**: `docs/01_FRAMEWORK/mamba-ssm-blueprint.md`
- **B**: `docs/01_FRAMEWORK/model-versioning-blueprint.md`
- **指标**: token_jaccard=0.3826, heading_jaccard=1.0, |∩token|=57
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「requirements_mamba.txt…」 / B「模型版本控制蓝图…」
- **建议 canonical**: `docs/01_FRAMEWORK/model-versioning-blueprint.md`
- **理由（机器）**: 建议正文体量更大（可能更完整）
- **另一路径**: `docs/01_FRAMEWORK/mamba-ssm-blueprint.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 116. score=0.6554

- **A**: `docs/01_FRAMEWORK/market-microstructure-model-blueprint.md`
- **B**: `docs/01_FRAMEWORK/synthetic-data-generation-blueprint.md`
- **指标**: token_jaccard=0.3826, heading_jaccard=1.0, |∩token|=57
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「市场微观结构模型蓝图…」 / B「requirements_synthetic.txt…」
- **建议 canonical**: `docs/01_FRAMEWORK/market-microstructure-model-blueprint.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/01_FRAMEWORK/synthetic-data-generation-blueprint.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 117. score=0.655

- **A**: `docs/01_FRAMEWORK/llm-fine-tuning-blueprint.md`
- **B**: `docs/01_FRAMEWORK/model-watermark-blueprint.md`
- **指标**: token_jaccard=0.3728, heading_jaccard=1.0, |∩token|=63
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「基础模型微调蓝图…」 / B「模型水印蓝图…」
- **建议 canonical**: `docs/01_FRAMEWORK/llm-fine-tuning-blueprint.md`
- **理由（机器）**: 建议正文体量更大（可能更完整）
- **另一路径**: `docs/01_FRAMEWORK/model-watermark-blueprint.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 118. score=0.6543

- **A**: `docs/01_FRAMEWORK/automl-pipeline-blueprint.md`
- **B**: `docs/01_FRAMEWORK/synthetic-data-generation-blueprint.md`
- **指标**: token_jaccard=0.3926, heading_jaccard=1.0, |∩token|=53
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「requirements_automl.txt…」 / B「requirements_synthetic.txt…」
- **建议 canonical**: `docs/01_FRAMEWORK/synthetic-data-generation-blueprint.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/01_FRAMEWORK/automl-pipeline-blueprint.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 119. score=0.6541

- **A**: `docs/01_FRAMEWORK/neural-architecture-search-blueprint.md`
- **B**: `docs/01_FRAMEWORK/rag-system-blueprint.md`
- **指标**: token_jaccard=0.3984, heading_jaccard=1.0, |∩token|=51
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「requirements_nas.txt…」 / B「requirements_rag.txt…」
- **建议 canonical**: `docs/01_FRAMEWORK/neural-architecture-search-blueprint.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/01_FRAMEWORK/rag-system-blueprint.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 120. score=0.6538

- **A**: `docs/01_FRAMEWORK/knowledge-distillation-blueprint.md`
- **B**: `docs/01_FRAMEWORK/model-performance-benchmark-blueprint.md`
- **指标**: token_jaccard=0.3766, heading_jaccard=1.0, |∩token|=58
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「知识蒸馏蓝图…」 / B「模型性能基准蓝图…」
- **建议 canonical**: `docs/01_FRAMEWORK/knowledge-distillation-blueprint.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/01_FRAMEWORK/model-performance-benchmark-blueprint.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

> 共 400 对，上文仅展示前 120 对；详见 JSON。
