---
standard_type: audit_state
applicable_scope: D 类蓝图主题重叠候选（启发式）
generated_date: '20260411'
generated_by: scripts/governance/scan_blueprint_d_overlap_candidates.py
---

# 蓝图 D 类重叠候选（机器建议 · 非最终裁决）

> **机器真源**：[`BLUEPRINT_D_OVERLAP_CANDIDATES_20260411.json`](./BLUEPRINT_D_OVERLAP_CANDIDATES_20260411.json)
> **扫描蓝图数**：758 ｜ **候选对（写入本文件）**：400（截断前 12247 对，仅保留 score 最高的 400 对）

## 说明

- **截断**：满足阈值的候选共 **12247** 对，仅保留 score 最高的 **400** 对（`--max-output-pairs`）；调参见 Playbook §4。

- **不是**语义 embedding / LLM；基于 **标题、responsibility、正文抽样、H2 标题** 的 token 与标题集合相似度。
- **建议 canonical** 与 **合并大纲** 为 **规则化启发式**，须经 [D 类蓝图重叠 Playbook](../../05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/D_CLASS_BLUEPRINT_OVERLAP_PLAYBOOK.md) 评审后再改稿。
- 与 **C1（字节相同）** 互补：本脚本跳过 **partial_hash** 全同对（应交给 `scan_duplicate_file_content.py`）。

## 候选对（按 score 降序，截断展示）

### 1. score=0.9977

- **A**: `docs/06_ARCHIVE/overlap_COMPLETE_BLUEPRINT_20260407_190203.md`
- **B**: `docs/09_RESEARCH_INNOVATION/_archive/COMPLETE_BLUEPRINT.md`
- **指标**: token_jaccard=0.9958, heading_jaccard=1.0, |∩token|=473
- **共有 H2（归一化后）**: 一、开源方案完整清单, 七、研究监控平台补充模块, 三、特征工程平台补充模块, 九、研究基础设施补充模块, 二、研究数据平台补充模块, 五、实验管理平台补充模块
- **标题**: A「Layer 9: 研究与创新层完整蓝图 v3.0…」 / B「Layer 9: 研究与创新层完整蓝图 v3.0…」
- **建议 canonical**: `docs/09_RESEARCH_INNOVATION/_archive/COMPLETE_BLUEPRINT.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/06_ARCHIVE/overlap_COMPLETE_BLUEPRINT_20260407_190203.md`（可 stub / archive / 叙事归并）
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

### 2. score=0.996

- **A**: `docs/06_ARCHIVE/20260407_p1_cleanup_archive/HUMAN_AI_INTERFACE_LAYER_TECHNICAL_BLUEPRINT.md`
- **B**: `docs/06_ARCHIVE/overlap_HUMAN_AI_INTERFACE_LAYER_TECHNICAL_BLUEPRINT_20260407_190203.md`
- **指标**: token_jaccard=0.9928, heading_jaccard=1.0, |∩token|=275
- **共有 H2（归一化后）**: 1. 文档治理, 一、架构设计, 七、总结, 三、技术实现路线, 二、核心组件详细设计, 五、对标分析
- **标题**: A「Layer 8: 人机交互层蓝图…」 / B「Layer 8: 人机交互层蓝图…」
- **建议 canonical**: `docs/06_ARCHIVE/overlap_HUMAN_AI_INTERFACE_LAYER_TECHNICAL_BLUEPRINT_20260407_190203.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/06_ARCHIVE/20260407_p1_cleanup_archive/HUMAN_AI_INTERFACE_LAYER_TECHNICAL_BLUEPRINT.md`（可 stub / archive / 叙事归并）
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

### 3. score=0.9957

- **A**: `docs/06_ARCHIVE/overlap_INVESTMENT_COMMITTEE_SUPPORT_BLUEPRINT_20260407_190203.md`
- **B**: `docs/11_STRATEGIC_DECISION/INVESTMENT_COMMITTEE_SUPPORT_BLUEPRINT.md`
- **指标**: token_jaccard=0.9921, heading_jaccard=1.0, |∩token|=251
- **共有 H2（归一化后）**: 一、系统架构设计, 七、风险与应对, 三、开源集成方案, 二、核心功能设计, 五、实施路径, 八、相关文档
- **标题**: A「投资委员会决策支持系统蓝图…」 / B「投资委员会决策支持系统蓝图…」
- **建议 canonical**: `docs/11_STRATEGIC_DECISION/INVESTMENT_COMMITTEE_SUPPORT_BLUEPRINT.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/06_ARCHIVE/overlap_INVESTMENT_COMMITTEE_SUPPORT_BLUEPRINT_20260407_190203.md`（可 stub / archive / 叙事归并）
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

### 4. score=0.9956

- **A**: `docs/06_ARCHIVE/20260407_p1_cleanup_archive/STRATEGY_LIFECYCLE_MANAGEMENT_BLUEPRINT.md`
- **B**: `docs/10_AI_WORKFLOW/STRATEGY_LIFECYCLE_MANAGEMENT_BLUEPRINT.md`
- **指标**: token_jaccard=0.992, heading_jaccard=1.0, |∩token|=247
- **共有 H2（归一化后）**: 一、模块概述, 七、质量指标, 三、技术实现, 二、架构设计, 五、接口定义, 八、风险评估
- **标题**: A「策略生命周期管理蓝图 (STRATEGY_LIFECYCLE_MANAGEMENT)…」 / B「策略生命周期管理蓝图 (STRATEGY_LIFECYCLE_MANAGEMENT)…」
- **建议 canonical**: `docs/10_AI_WORKFLOW/STRATEGY_LIFECYCLE_MANAGEMENT_BLUEPRINT.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/06_ARCHIVE/20260407_p1_cleanup_archive/STRATEGY_LIFECYCLE_MANAGEMENT_BLUEPRINT.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 文档职责说明
  - 一、模块概述
  - 二、架构设计
  - 三、技术实现
  - 四、功能模块
  - 五、接口定义
  - 六、实施路径
  - 七、质量指标
  - 八、风险评估

### 5. score=0.9953

- **A**: `docs/06_ARCHIVE/20260407_p1_cleanup_archive/RESEARCH_WORKFLOW_MANAGEMENT_BLUEPRINT.md`
- **B**: `docs/10_AI_WORKFLOW/RESEARCH_WORKFLOW_MANAGEMENT_BLUEPRINT.md`
- **指标**: token_jaccard=0.9915, heading_jaccard=1.0, |∩token|=233
- **共有 H2（归一化后）**: 一、模块概述, 七、质量保证, 三、技术实现, 九、开源项目集成, 二、架构设计, 五、实施路径
- **标题**: A「研究工作流管理蓝图 (RESEARCH_WORKFLOW_MANAGEMENT)…」 / B「研究工作流管理蓝图 (RESEARCH_WORKFLOW_MANAGEMENT)…」
- **建议 canonical**: `docs/10_AI_WORKFLOW/RESEARCH_WORKFLOW_MANAGEMENT_BLUEPRINT.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/06_ARCHIVE/20260407_p1_cleanup_archive/RESEARCH_WORKFLOW_MANAGEMENT_BLUEPRINT.md`（可 stub / archive / 叙事归并）
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

### 6. score=0.9952

- **A**: `docs/06_ARCHIVE/overlap_BLUEPRINT_STANDARD_TEMPLATE_20260407_190203.md`
- **B**: `docs/09_AUDIT/TEMPLATES/BLUEPRINT_STANDARD_TEMPLATE.md`
- **指标**: token_jaccard=0.9913, heading_jaccard=1.0, |∩token|=227
- **共有 H2（归一化后）**: 1. 概述, n. 变更历史, 命名规范, 标准yaml头部, 标准变更历史, 标准文档结构
- **标题**: A「[模块名称]蓝图…」 / B「[模块名称]蓝图…」
- **建议 canonical**: `docs/09_AUDIT/TEMPLATES/BLUEPRINT_STANDARD_TEMPLATE.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/06_ARCHIVE/overlap_BLUEPRINT_STANDARD_TEMPLATE_20260407_190203.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 标准YAML头部
  - 标准文档结构
  - 1. 概述
  - 标准变更历史
  - N. 变更历史
  - 命名规范
  - 编码规范
  - 检查清单
  - 自动化工具
  - 示例文件
  - 版本历史

### 7. score=0.9943

- **A**: `docs/01_FRAMEWORK/MODEL_REGISTRY_BLUEPRINT.md`
- **B**: `docs/06_ARCHIVE/overlap_MODEL_REGISTRY_BLUEPRINT_20260407_190203.md`
- **指标**: token_jaccard=0.9896, heading_jaccard=1.0, |∩token|=190
- **共有 H2（归一化后）**: 1. 文档治理, 一、架构设计, 七、相关文档, 三、数据模型设计, 二、核心组件详细设计, 五、质量保证
- **标题**: A「模型注册中心蓝图…」 / B「模型注册中心蓝图…」
- **建议 canonical**: `docs/01_FRAMEWORK/MODEL_REGISTRY_BLUEPRINT.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/06_ARCHIVE/overlap_MODEL_REGISTRY_BLUEPRINT_20260407_190203.md`（可 stub / archive / 叙事归并）
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

### 8. score=0.9809

- **A**: `docs/06_ARCHIVE/overlap_INCOMPLETE_BLUEPRINT_ARCHIVE_REPORT_20260404_20260407_190203.md`
- **B**: `docs/09_AUDIT/REPORTS/INCOMPLETE_BLUEPRINT_ARCHIVE_REPORT_20260404.md`
- **指标**: token_jaccard=0.9652, heading_jaccard=1.0, |∩token|=222
- **共有 H2（归一化后）**: 1. 归档执行摘要, 2. 归档文档详情, 3. 归档执行过程, 4. 归档效果评估, 5. 后续建议, 6. 归档总结
- **标题**: A「内容不完整蓝图文档归档报?…」 / B「内容不完整蓝图文档归档报告…」
- **建议 canonical**: `docs/09_AUDIT/REPORTS/INCOMPLETE_BLUEPRINT_ARCHIVE_REPORT_20260404.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/06_ARCHIVE/overlap_INCOMPLETE_BLUEPRINT_ARCHIVE_REPORT_20260404_20260407_190203.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 归档执行摘要
  - 2. 归档文档详情
  - 3. 归档执行过程
  - 4. 归档效果评估
  - 5. 后续建议
  - 6. 归档总结
  - 7. 相关文档

### 9. score=0.9135

- **A**: `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/DATA_VERSION_CONTROL_BLUEPRINT.md`
- **B**: `docs/06_ARCHIVE/20260407_p1_cleanup_archive/DATA_VERSION_CONTROL_BLUEPRINT.md`
- **指标**: token_jaccard=0.9336, heading_jaccard=0.8571, |∩token|=211
- **共有 H2（归一化后）**: 1. 文档治理, 一、设计背景与目标, 实现方案, 核心功能, 核心定位, 设计目标
- **标题**: A「数据版本控制蓝图…」 / B「数据版本控制蓝图…」
- **建议 canonical**: `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/DATA_VERSION_CONTROL_BLUEPRINT.md`
- **理由（机器）**: 建议路径含图纸柜 `01_BLUEPRINTS`
- **另一路径**: `docs/06_ARCHIVE/20260407_p1_cleanup_archive/DATA_VERSION_CONTROL_BLUEPRINT.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 核心定位
  - 设计目标
  - 核心功能
  - 实现方案
  - 一、设计背景与目标
  - 1. 文档治理
  - 变更历史

### 10. score=0.9116

- **A**: `docs/06_ARCHIVE/20260407_p1_cleanup_archive/MODEL_PERFORMANCE_VERSION_MANAGEMENT_BLUEPRINT.md`
- **B**: `docs/10_AI_WORKFLOW/MODEL_PERFORMANCE_VERSION_MANAGEMENT_BLUEPRINT.md`
- **指标**: token_jaccard=0.8393, heading_jaccard=1.0, |∩token|=235
- **共有 H2（归一化后）**: 1. 文档治理, 一、模块概述, 七、风险管, 三、接口定, 九、相关文档, 二、详细架构设
- **标题**: A「设置MLflow跟踪URI…」 / B「设置MLflow跟踪URI…」
- **建议 canonical**: `docs/10_AI_WORKFLOW/MODEL_PERFORMANCE_VERSION_MANAGEMENT_BLUEPRINT.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/06_ARCHIVE/20260407_p1_cleanup_archive/MODEL_PERFORMANCE_VERSION_MANAGEMENT_BLUEPRINT.md`（可 stub / archive / 叙事归并）
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

### 11. score=0.8532

- **A**: `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/DATA_GOVERNANCE_PLATFORM_BLUEPRINT.md`
- **B**: `docs/06_ARCHIVE/overlap_DATA_GOVERNANCE_PLATFORM_BLUEPRINT_20260407_190203.md`
- **指标**: token_jaccard=0.9241, heading_jaccard=0.7, |∩token|=219
- **共有 H2（归一化后）**: 1. 文档治理, 一、设计背景与目标, 变更历史, 实现方案, 核心功能, 核心定位
- **标题**: A「DATA GOVERNANCE PLATFORM BLUEPRINT…」 / B「DATA GOVERNANCE PLATFORM BLUEPRINT…」
- **建议 canonical**: `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/DATA_GOVERNANCE_PLATFORM_BLUEPRINT.md`
- **理由（机器）**: 建议路径含图纸柜 `01_BLUEPRINTS`
- **另一路径**: `docs/06_ARCHIVE/overlap_DATA_GOVERNANCE_PLATFORM_BLUEPRINT_20260407_190203.md`（可 stub / archive / 叙事归并）
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

### 12. score=0.8506

- **A**: `docs/01_FRAMEWORK/ALGORITHM_DEPLOYMENT_CONTROL_BLUEPRINT.md`
- **B**: `docs/06_ARCHIVE/overlap_ALGORITHM_DEPLOYMENT_CONTROL_BLUEPRINT_20260407_190202.md`
- **指标**: token_jaccard=0.8647, heading_jaccard=0.7857, |∩token|=230
- **共有 H2（归一化后）**: 一、系统架构设计, 七、质量保证, 三、部署监控, 九、成功指标, 二、技术实现方案, 五、个人开发优化方案
- **标题**: A「算法部署控制系统蓝图…」 / B「算法部署控制系统蓝图…」
- **建议 canonical**: `docs/01_FRAMEWORK/ALGORITHM_DEPLOYMENT_CONTROL_BLUEPRINT.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/06_ARCHIVE/overlap_ALGORITHM_DEPLOYMENT_CONTROL_BLUEPRINT_20260407_190202.md`（可 stub / archive / 叙事归并）
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

### 13. score=0.8387

- **A**: `docs/02_FACTOR_LIBRARY/35_INDUSTRY_ROTATION/INDUSTRY_ROTATION_BLUEPRINT.md`
- **B**: `docs/02_FACTOR_LIBRARY/36_FACTOR_EXPOSURE_MGMT/FACTOR_EXPOSURE_MGMT_BLUEPRINT.md`
- **指标**: token_jaccard=0.746, heading_jaccard=1.0, |∩token|=47
- **共有 H2（归一化后）**: 1. 概述, 2. 技术实现, 3. 实施路径, 4. 文档治理, 5. 总结
- **标题**: A「行业轮动因子模块蓝图…」 / B「因子暴露管理模块蓝图…」
- **建议 canonical**: `docs/02_FACTOR_LIBRARY/36_FACTOR_EXPOSURE_MGMT/FACTOR_EXPOSURE_MGMT_BLUEPRINT.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/02_FACTOR_LIBRARY/35_INDUSTRY_ROTATION/INDUSTRY_ROTATION_BLUEPRINT.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 技术实现
  - 3. 实施路径
  - 4. 文档治理
  - 5. 总结

### 14. score=0.822

- **A**: `docs/02_FACTOR_LIBRARY/33_FACTOR_DECAY_MGMT/FACTOR_DECAY_MGMT_BLUEPRINT.md`
- **B**: `docs/02_FACTOR_LIBRARY/34_FACTOR_SIGNAL_GEN/FACTOR_SIGNAL_GEN_BLUEPRINT.md`
- **指标**: token_jaccard=0.7188, heading_jaccard=1.0, |∩token|=46
- **共有 H2（归一化后）**: 1. 概述, 2. 技术实现, 3. 实施路径, 4. 文档治理, 5. 总结
- **标题**: A「因子衰减管理模块蓝图…」 / B「因子信号生成模块蓝图…」
- **建议 canonical**: `docs/02_FACTOR_LIBRARY/34_FACTOR_SIGNAL_GEN/FACTOR_SIGNAL_GEN_BLUEPRINT.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/02_FACTOR_LIBRARY/33_FACTOR_DECAY_MGMT/FACTOR_DECAY_MGMT_BLUEPRINT.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 技术实现
  - 3. 实施路径
  - 4. 文档治理
  - 5. 总结

### 15. score=0.822

- **A**: `docs/02_FACTOR_LIBRARY/33_FACTOR_DECAY_MGMT/FACTOR_DECAY_MGMT_BLUEPRINT.md`
- **B**: `docs/02_FACTOR_LIBRARY/35_INDUSTRY_ROTATION/INDUSTRY_ROTATION_BLUEPRINT.md`
- **指标**: token_jaccard=0.7188, heading_jaccard=1.0, |∩token|=46
- **共有 H2（归一化后）**: 1. 概述, 2. 技术实现, 3. 实施路径, 4. 文档治理, 5. 总结
- **标题**: A「因子衰减管理模块蓝图…」 / B「行业轮动因子模块蓝图…」
- **建议 canonical**: `docs/02_FACTOR_LIBRARY/33_FACTOR_DECAY_MGMT/FACTOR_DECAY_MGMT_BLUEPRINT.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/02_FACTOR_LIBRARY/35_INDUSTRY_ROTATION/INDUSTRY_ROTATION_BLUEPRINT.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 技术实现
  - 3. 实施路径
  - 4. 文档治理
  - 5. 总结

### 16. score=0.822

- **A**: `docs/02_FACTOR_LIBRARY/33_FACTOR_DECAY_MGMT/FACTOR_DECAY_MGMT_BLUEPRINT.md`
- **B**: `docs/02_FACTOR_LIBRARY/36_FACTOR_EXPOSURE_MGMT/FACTOR_EXPOSURE_MGMT_BLUEPRINT.md`
- **指标**: token_jaccard=0.7188, heading_jaccard=1.0, |∩token|=46
- **共有 H2（归一化后）**: 1. 概述, 2. 技术实现, 3. 实施路径, 4. 文档治理, 5. 总结
- **标题**: A「因子衰减管理模块蓝图…」 / B「因子暴露管理模块蓝图…」
- **建议 canonical**: `docs/02_FACTOR_LIBRARY/33_FACTOR_DECAY_MGMT/FACTOR_DECAY_MGMT_BLUEPRINT.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/02_FACTOR_LIBRARY/36_FACTOR_EXPOSURE_MGMT/FACTOR_EXPOSURE_MGMT_BLUEPRINT.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 技术实现
  - 3. 实施路径
  - 4. 文档治理
  - 5. 总结

### 17. score=0.822

- **A**: `docs/02_FACTOR_LIBRARY/33_FACTOR_DECAY_MGMT/FACTOR_DECAY_MGMT_BLUEPRINT.md`
- **B**: `docs/02_FACTOR_LIBRARY/38_FACTOR_TURNOVER_OPT/FACTOR_TURNOVER_OPT_BLUEPRINT.md`
- **指标**: token_jaccard=0.7188, heading_jaccard=1.0, |∩token|=46
- **共有 H2（归一化后）**: 1. 概述, 2. 技术实现, 3. 实施路径, 4. 文档治理, 5. 总结
- **标题**: A「因子衰减管理模块蓝图…」 / B「因子换手率优化模块蓝图…」
- **建议 canonical**: `docs/02_FACTOR_LIBRARY/38_FACTOR_TURNOVER_OPT/FACTOR_TURNOVER_OPT_BLUEPRINT.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/02_FACTOR_LIBRARY/33_FACTOR_DECAY_MGMT/FACTOR_DECAY_MGMT_BLUEPRINT.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 技术实现
  - 3. 实施路径
  - 4. 文档治理
  - 5. 总结

### 18. score=0.822

- **A**: `docs/02_FACTOR_LIBRARY/34_FACTOR_SIGNAL_GEN/FACTOR_SIGNAL_GEN_BLUEPRINT.md`
- **B**: `docs/02_FACTOR_LIBRARY/35_INDUSTRY_ROTATION/INDUSTRY_ROTATION_BLUEPRINT.md`
- **指标**: token_jaccard=0.7188, heading_jaccard=1.0, |∩token|=46
- **共有 H2（归一化后）**: 1. 概述, 2. 技术实现, 3. 实施路径, 4. 文档治理, 5. 总结
- **标题**: A「因子信号生成模块蓝图…」 / B「行业轮动因子模块蓝图…」
- **建议 canonical**: `docs/02_FACTOR_LIBRARY/34_FACTOR_SIGNAL_GEN/FACTOR_SIGNAL_GEN_BLUEPRINT.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/02_FACTOR_LIBRARY/35_INDUSTRY_ROTATION/INDUSTRY_ROTATION_BLUEPRINT.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 技术实现
  - 3. 实施路径
  - 4. 文档治理
  - 5. 总结

### 19. score=0.822

- **A**: `docs/02_FACTOR_LIBRARY/34_FACTOR_SIGNAL_GEN/FACTOR_SIGNAL_GEN_BLUEPRINT.md`
- **B**: `docs/02_FACTOR_LIBRARY/36_FACTOR_EXPOSURE_MGMT/FACTOR_EXPOSURE_MGMT_BLUEPRINT.md`
- **指标**: token_jaccard=0.7188, heading_jaccard=1.0, |∩token|=46
- **共有 H2（归一化后）**: 1. 概述, 2. 技术实现, 3. 实施路径, 4. 文档治理, 5. 总结
- **标题**: A「因子信号生成模块蓝图…」 / B「因子暴露管理模块蓝图…」
- **建议 canonical**: `docs/02_FACTOR_LIBRARY/34_FACTOR_SIGNAL_GEN/FACTOR_SIGNAL_GEN_BLUEPRINT.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/02_FACTOR_LIBRARY/36_FACTOR_EXPOSURE_MGMT/FACTOR_EXPOSURE_MGMT_BLUEPRINT.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 技术实现
  - 3. 实施路径
  - 4. 文档治理
  - 5. 总结

### 20. score=0.822

- **A**: `docs/02_FACTOR_LIBRARY/34_FACTOR_SIGNAL_GEN/FACTOR_SIGNAL_GEN_BLUEPRINT.md`
- **B**: `docs/02_FACTOR_LIBRARY/38_FACTOR_TURNOVER_OPT/FACTOR_TURNOVER_OPT_BLUEPRINT.md`
- **指标**: token_jaccard=0.7188, heading_jaccard=1.0, |∩token|=46
- **共有 H2（归一化后）**: 1. 概述, 2. 技术实现, 3. 实施路径, 4. 文档治理, 5. 总结
- **标题**: A「因子信号生成模块蓝图…」 / B「因子换手率优化模块蓝图…」
- **建议 canonical**: `docs/02_FACTOR_LIBRARY/38_FACTOR_TURNOVER_OPT/FACTOR_TURNOVER_OPT_BLUEPRINT.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/02_FACTOR_LIBRARY/34_FACTOR_SIGNAL_GEN/FACTOR_SIGNAL_GEN_BLUEPRINT.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 技术实现
  - 3. 实施路径
  - 4. 文档治理
  - 5. 总结

### 21. score=0.822

- **A**: `docs/02_FACTOR_LIBRARY/35_INDUSTRY_ROTATION/INDUSTRY_ROTATION_BLUEPRINT.md`
- **B**: `docs/02_FACTOR_LIBRARY/38_FACTOR_TURNOVER_OPT/FACTOR_TURNOVER_OPT_BLUEPRINT.md`
- **指标**: token_jaccard=0.7188, heading_jaccard=1.0, |∩token|=46
- **共有 H2（归一化后）**: 1. 概述, 2. 技术实现, 3. 实施路径, 4. 文档治理, 5. 总结
- **标题**: A「行业轮动因子模块蓝图…」 / B「因子换手率优化模块蓝图…」
- **建议 canonical**: `docs/02_FACTOR_LIBRARY/38_FACTOR_TURNOVER_OPT/FACTOR_TURNOVER_OPT_BLUEPRINT.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/02_FACTOR_LIBRARY/35_INDUSTRY_ROTATION/INDUSTRY_ROTATION_BLUEPRINT.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 技术实现
  - 3. 实施路径
  - 4. 文档治理
  - 5. 总结

### 22. score=0.822

- **A**: `docs/02_FACTOR_LIBRARY/36_FACTOR_EXPOSURE_MGMT/FACTOR_EXPOSURE_MGMT_BLUEPRINT.md`
- **B**: `docs/02_FACTOR_LIBRARY/38_FACTOR_TURNOVER_OPT/FACTOR_TURNOVER_OPT_BLUEPRINT.md`
- **指标**: token_jaccard=0.7188, heading_jaccard=1.0, |∩token|=46
- **共有 H2（归一化后）**: 1. 概述, 2. 技术实现, 3. 实施路径, 4. 文档治理, 5. 总结
- **标题**: A「因子暴露管理模块蓝图…」 / B「因子换手率优化模块蓝图…」
- **建议 canonical**: `docs/02_FACTOR_LIBRARY/38_FACTOR_TURNOVER_OPT/FACTOR_TURNOVER_OPT_BLUEPRINT.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/02_FACTOR_LIBRARY/36_FACTOR_EXPOSURE_MGMT/FACTOR_EXPOSURE_MGMT_BLUEPRINT.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 技术实现
  - 3. 实施路径
  - 4. 文档治理
  - 5. 总结

### 23. score=0.822

- **A**: `docs/02_FACTOR_LIBRARY/39_EVENT_DRIVEN_FACTOR/EVENT_DRIVEN_FACTOR_BLUEPRINT.md`
- **B**: `docs/02_FACTOR_LIBRARY/40_FACTOR_CAPACITY_MGMT/FACTOR_CAPACITY_MGMT_BLUEPRINT.md`
- **指标**: token_jaccard=0.7188, heading_jaccard=1.0, |∩token|=46
- **共有 H2（归一化后）**: 1. 概述, 2. 技术实现, 3. 实施路径, 4. 文档治理, 5. 总结
- **标题**: A「事件驱动因子模块蓝图…」 / B「因子容量管理模块蓝图…」
- **建议 canonical**: `docs/02_FACTOR_LIBRARY/39_EVENT_DRIVEN_FACTOR/EVENT_DRIVEN_FACTOR_BLUEPRINT.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/02_FACTOR_LIBRARY/40_FACTOR_CAPACITY_MGMT/FACTOR_CAPACITY_MGMT_BLUEPRINT.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 技术实现
  - 3. 实施路径
  - 4. 文档治理
  - 5. 总结

### 24. score=0.8159

- **A**: `docs/02_FACTOR_LIBRARY/33_FACTOR_DECAY_MGMT/FACTOR_DECAY_MGMT_BLUEPRINT.md`
- **B**: `docs/02_FACTOR_LIBRARY/37_FACTOR_CORRELATION/FACTOR_CORRELATION_BLUEPRINT.md`
- **指标**: token_jaccard=0.7077, heading_jaccard=1.0, |∩token|=46
- **共有 H2（归一化后）**: 1. 概述, 2. 技术实现, 3. 实施路径, 4. 文档治理, 5. 总结
- **标题**: A「因子衰减管理模块蓝图…」 / B「因子相关性分析模块蓝图…」
- **建议 canonical**: `docs/02_FACTOR_LIBRARY/37_FACTOR_CORRELATION/FACTOR_CORRELATION_BLUEPRINT.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/02_FACTOR_LIBRARY/33_FACTOR_DECAY_MGMT/FACTOR_DECAY_MGMT_BLUEPRINT.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 技术实现
  - 3. 实施路径
  - 4. 文档治理
  - 5. 总结

### 25. score=0.8159

- **A**: `docs/02_FACTOR_LIBRARY/34_FACTOR_SIGNAL_GEN/FACTOR_SIGNAL_GEN_BLUEPRINT.md`
- **B**: `docs/02_FACTOR_LIBRARY/37_FACTOR_CORRELATION/FACTOR_CORRELATION_BLUEPRINT.md`
- **指标**: token_jaccard=0.7077, heading_jaccard=1.0, |∩token|=46
- **共有 H2（归一化后）**: 1. 概述, 2. 技术实现, 3. 实施路径, 4. 文档治理, 5. 总结
- **标题**: A「因子信号生成模块蓝图…」 / B「因子相关性分析模块蓝图…」
- **建议 canonical**: `docs/02_FACTOR_LIBRARY/37_FACTOR_CORRELATION/FACTOR_CORRELATION_BLUEPRINT.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/02_FACTOR_LIBRARY/34_FACTOR_SIGNAL_GEN/FACTOR_SIGNAL_GEN_BLUEPRINT.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 技术实现
  - 3. 实施路径
  - 4. 文档治理
  - 5. 总结

### 26. score=0.8159

- **A**: `docs/02_FACTOR_LIBRARY/35_INDUSTRY_ROTATION/INDUSTRY_ROTATION_BLUEPRINT.md`
- **B**: `docs/02_FACTOR_LIBRARY/37_FACTOR_CORRELATION/FACTOR_CORRELATION_BLUEPRINT.md`
- **指标**: token_jaccard=0.7077, heading_jaccard=1.0, |∩token|=46
- **共有 H2（归一化后）**: 1. 概述, 2. 技术实现, 3. 实施路径, 4. 文档治理, 5. 总结
- **标题**: A「行业轮动因子模块蓝图…」 / B「因子相关性分析模块蓝图…」
- **建议 canonical**: `docs/02_FACTOR_LIBRARY/37_FACTOR_CORRELATION/FACTOR_CORRELATION_BLUEPRINT.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/02_FACTOR_LIBRARY/35_INDUSTRY_ROTATION/INDUSTRY_ROTATION_BLUEPRINT.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 技术实现
  - 3. 实施路径
  - 4. 文档治理
  - 5. 总结

### 27. score=0.8159

- **A**: `docs/02_FACTOR_LIBRARY/36_FACTOR_EXPOSURE_MGMT/FACTOR_EXPOSURE_MGMT_BLUEPRINT.md`
- **B**: `docs/02_FACTOR_LIBRARY/37_FACTOR_CORRELATION/FACTOR_CORRELATION_BLUEPRINT.md`
- **指标**: token_jaccard=0.7077, heading_jaccard=1.0, |∩token|=46
- **共有 H2（归一化后）**: 1. 概述, 2. 技术实现, 3. 实施路径, 4. 文档治理, 5. 总结
- **标题**: A「因子暴露管理模块蓝图…」 / B「因子相关性分析模块蓝图…」
- **建议 canonical**: `docs/02_FACTOR_LIBRARY/37_FACTOR_CORRELATION/FACTOR_CORRELATION_BLUEPRINT.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/02_FACTOR_LIBRARY/36_FACTOR_EXPOSURE_MGMT/FACTOR_EXPOSURE_MGMT_BLUEPRINT.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 技术实现
  - 3. 实施路径
  - 4. 文档治理
  - 5. 总结

### 28. score=0.8159

- **A**: `docs/02_FACTOR_LIBRARY/37_FACTOR_CORRELATION/FACTOR_CORRELATION_BLUEPRINT.md`
- **B**: `docs/02_FACTOR_LIBRARY/38_FACTOR_TURNOVER_OPT/FACTOR_TURNOVER_OPT_BLUEPRINT.md`
- **指标**: token_jaccard=0.7077, heading_jaccard=1.0, |∩token|=46
- **共有 H2（归一化后）**: 1. 概述, 2. 技术实现, 3. 实施路径, 4. 文档治理, 5. 总结
- **标题**: A「因子相关性分析模块蓝图…」 / B「因子换手率优化模块蓝图…」
- **建议 canonical**: `docs/02_FACTOR_LIBRARY/37_FACTOR_CORRELATION/FACTOR_CORRELATION_BLUEPRINT.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/02_FACTOR_LIBRARY/38_FACTOR_TURNOVER_OPT/FACTOR_TURNOVER_OPT_BLUEPRINT.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 技术实现
  - 3. 实施路径
  - 4. 文档治理
  - 5. 总结

### 29. score=0.8132

- **A**: `docs/11_STRATEGIC_DECISION/archive/BLUEPRINT_CREATION_PROGRESS_REPORT_20260407.md`
- **B**: `docs/11_STRATEGIC_DECISION/archive/P1_BLUEPRINT_CREATION_PROGRESS_REPORT_20260407.md`
- **指标**: token_jaccard=0.6603, heading_jaccard=1.0, |∩token|=138
- **共有 H2（归一化后）**: 一、已完成蓝图文档清单, 七、总结, 三、蓝图文档质量评估, 二、剩余蓝图文档清单, 五、下一步行动, 六、成功标准
- **标题**: A「…」 / B「…」
- **建议 canonical**: `docs/11_STRATEGIC_DECISION/archive/BLUEPRINT_CREATION_PROGRESS_REPORT_20260407.md`
- **理由（机器）**: 建议正文体量更大（可能更完整）
- **另一路径**: `docs/11_STRATEGIC_DECISION/archive/P1_BLUEPRINT_CREATION_PROGRESS_REPORT_20260407.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 📋 执行摘要
  - 一、已完成蓝图文档清单
  - 二、剩余蓝图文档清单
  - 三、蓝图文档质量评估
  - 四、实施建议
  - 五、下一步行动
  - 六、成功标准
  - 七、总结

### 30. score=0.81

- **A**: `docs/01_FRAMEWORK/MLOPS_PLATFORM_BLUEPRINT.md`
- **B**: `docs/06_ARCHIVE/overlap_MLOPS_PLATFORM_BLUEPRINT_20260407_190203.md`
- **指标**: token_jaccard=0.9482, heading_jaccard=0.5385, |∩token|=238
- **共有 H2（归一化后）**: 1. 文档治理, ?八、验收标?, ⚠️ 七、风险评?, 📅 五、实施路线图, 📚 九、相关文档索?, 🔌 四、核心接口定?
- **标题**: A「MLOps平台蓝图：端到端机器学习运维平台…」 / B「MLOps平台蓝图：端到端机器学习运维平台…」
- **建议 canonical**: `docs/01_FRAMEWORK/MLOPS_PLATFORM_BLUEPRINT.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/06_ARCHIVE/overlap_MLOPS_PLATFORM_BLUEPRINT_20260407_190203.md`（可 stub / archive / 叙事归并）
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

### 31. score=0.81

- **A**: `docs/02_FACTOR_LIBRARY/32_FACTOR_DYNAMIC_WEIGHT/FACTOR_DYNAMIC_WEIGHT_BLUEPRINT.md`
- **B**: `docs/02_FACTOR_LIBRARY/33_FACTOR_DECAY_MGMT/FACTOR_DECAY_MGMT_BLUEPRINT.md`
- **指标**: token_jaccard=0.697, heading_jaccard=1.0, |∩token|=46
- **共有 H2（归一化后）**: 1. 概述, 2. 技术实现, 3. 实施路径, 4. 文档治理, 5. 总结
- **标题**: A「因子动态权重调整模块蓝图…」 / B「因子衰减管理模块蓝图…」
- **建议 canonical**: `docs/02_FACTOR_LIBRARY/32_FACTOR_DYNAMIC_WEIGHT/FACTOR_DYNAMIC_WEIGHT_BLUEPRINT.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/02_FACTOR_LIBRARY/33_FACTOR_DECAY_MGMT/FACTOR_DECAY_MGMT_BLUEPRINT.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 技术实现
  - 3. 实施路径
  - 4. 文档治理
  - 5. 总结

### 32. score=0.81

- **A**: `docs/02_FACTOR_LIBRARY/32_FACTOR_DYNAMIC_WEIGHT/FACTOR_DYNAMIC_WEIGHT_BLUEPRINT.md`
- **B**: `docs/02_FACTOR_LIBRARY/34_FACTOR_SIGNAL_GEN/FACTOR_SIGNAL_GEN_BLUEPRINT.md`
- **指标**: token_jaccard=0.697, heading_jaccard=1.0, |∩token|=46
- **共有 H2（归一化后）**: 1. 概述, 2. 技术实现, 3. 实施路径, 4. 文档治理, 5. 总结
- **标题**: A「因子动态权重调整模块蓝图…」 / B「因子信号生成模块蓝图…」
- **建议 canonical**: `docs/02_FACTOR_LIBRARY/32_FACTOR_DYNAMIC_WEIGHT/FACTOR_DYNAMIC_WEIGHT_BLUEPRINT.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/02_FACTOR_LIBRARY/34_FACTOR_SIGNAL_GEN/FACTOR_SIGNAL_GEN_BLUEPRINT.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 技术实现
  - 3. 实施路径
  - 4. 文档治理
  - 5. 总结

### 33. score=0.81

- **A**: `docs/02_FACTOR_LIBRARY/32_FACTOR_DYNAMIC_WEIGHT/FACTOR_DYNAMIC_WEIGHT_BLUEPRINT.md`
- **B**: `docs/02_FACTOR_LIBRARY/35_INDUSTRY_ROTATION/INDUSTRY_ROTATION_BLUEPRINT.md`
- **指标**: token_jaccard=0.697, heading_jaccard=1.0, |∩token|=46
- **共有 H2（归一化后）**: 1. 概述, 2. 技术实现, 3. 实施路径, 4. 文档治理, 5. 总结
- **标题**: A「因子动态权重调整模块蓝图…」 / B「行业轮动因子模块蓝图…」
- **建议 canonical**: `docs/02_FACTOR_LIBRARY/32_FACTOR_DYNAMIC_WEIGHT/FACTOR_DYNAMIC_WEIGHT_BLUEPRINT.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/02_FACTOR_LIBRARY/35_INDUSTRY_ROTATION/INDUSTRY_ROTATION_BLUEPRINT.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 技术实现
  - 3. 实施路径
  - 4. 文档治理
  - 5. 总结

### 34. score=0.81

- **A**: `docs/02_FACTOR_LIBRARY/32_FACTOR_DYNAMIC_WEIGHT/FACTOR_DYNAMIC_WEIGHT_BLUEPRINT.md`
- **B**: `docs/02_FACTOR_LIBRARY/36_FACTOR_EXPOSURE_MGMT/FACTOR_EXPOSURE_MGMT_BLUEPRINT.md`
- **指标**: token_jaccard=0.697, heading_jaccard=1.0, |∩token|=46
- **共有 H2（归一化后）**: 1. 概述, 2. 技术实现, 3. 实施路径, 4. 文档治理, 5. 总结
- **标题**: A「因子动态权重调整模块蓝图…」 / B「因子暴露管理模块蓝图…」
- **建议 canonical**: `docs/02_FACTOR_LIBRARY/32_FACTOR_DYNAMIC_WEIGHT/FACTOR_DYNAMIC_WEIGHT_BLUEPRINT.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/02_FACTOR_LIBRARY/36_FACTOR_EXPOSURE_MGMT/FACTOR_EXPOSURE_MGMT_BLUEPRINT.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 技术实现
  - 3. 实施路径
  - 4. 文档治理
  - 5. 总结

### 35. score=0.81

- **A**: `docs/02_FACTOR_LIBRARY/32_FACTOR_DYNAMIC_WEIGHT/FACTOR_DYNAMIC_WEIGHT_BLUEPRINT.md`
- **B**: `docs/02_FACTOR_LIBRARY/38_FACTOR_TURNOVER_OPT/FACTOR_TURNOVER_OPT_BLUEPRINT.md`
- **指标**: token_jaccard=0.697, heading_jaccard=1.0, |∩token|=46
- **共有 H2（归一化后）**: 1. 概述, 2. 技术实现, 3. 实施路径, 4. 文档治理, 5. 总结
- **标题**: A「因子动态权重调整模块蓝图…」 / B「因子换手率优化模块蓝图…」
- **建议 canonical**: `docs/02_FACTOR_LIBRARY/32_FACTOR_DYNAMIC_WEIGHT/FACTOR_DYNAMIC_WEIGHT_BLUEPRINT.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/02_FACTOR_LIBRARY/38_FACTOR_TURNOVER_OPT/FACTOR_TURNOVER_OPT_BLUEPRINT.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 技术实现
  - 3. 实施路径
  - 4. 文档治理
  - 5. 总结

### 36. score=0.8058

- **A**: `docs/02_FACTOR_LIBRARY/33_FACTOR_DECAY_MGMT/FACTOR_DECAY_MGMT_BLUEPRINT.md`
- **B**: `docs/02_FACTOR_LIBRARY/39_EVENT_DRIVEN_FACTOR/EVENT_DRIVEN_FACTOR_BLUEPRINT.md`
- **指标**: token_jaccard=0.6923, heading_jaccard=1.0, |∩token|=45
- **共有 H2（归一化后）**: 1. 概述, 2. 技术实现, 3. 实施路径, 4. 文档治理, 5. 总结
- **标题**: A「因子衰减管理模块蓝图…」 / B「事件驱动因子模块蓝图…」
- **建议 canonical**: `docs/02_FACTOR_LIBRARY/33_FACTOR_DECAY_MGMT/FACTOR_DECAY_MGMT_BLUEPRINT.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/02_FACTOR_LIBRARY/39_EVENT_DRIVEN_FACTOR/EVENT_DRIVEN_FACTOR_BLUEPRINT.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 技术实现
  - 3. 实施路径
  - 4. 文档治理
  - 5. 总结

### 37. score=0.8058

- **A**: `docs/02_FACTOR_LIBRARY/33_FACTOR_DECAY_MGMT/FACTOR_DECAY_MGMT_BLUEPRINT.md`
- **B**: `docs/02_FACTOR_LIBRARY/40_FACTOR_CAPACITY_MGMT/FACTOR_CAPACITY_MGMT_BLUEPRINT.md`
- **指标**: token_jaccard=0.6923, heading_jaccard=1.0, |∩token|=45
- **共有 H2（归一化后）**: 1. 概述, 2. 技术实现, 3. 实施路径, 4. 文档治理, 5. 总结
- **标题**: A「因子衰减管理模块蓝图…」 / B「因子容量管理模块蓝图…」
- **建议 canonical**: `docs/02_FACTOR_LIBRARY/33_FACTOR_DECAY_MGMT/FACTOR_DECAY_MGMT_BLUEPRINT.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/02_FACTOR_LIBRARY/40_FACTOR_CAPACITY_MGMT/FACTOR_CAPACITY_MGMT_BLUEPRINT.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 技术实现
  - 3. 实施路径
  - 4. 文档治理
  - 5. 总结

### 38. score=0.8058

- **A**: `docs/02_FACTOR_LIBRARY/34_FACTOR_SIGNAL_GEN/FACTOR_SIGNAL_GEN_BLUEPRINT.md`
- **B**: `docs/02_FACTOR_LIBRARY/39_EVENT_DRIVEN_FACTOR/EVENT_DRIVEN_FACTOR_BLUEPRINT.md`
- **指标**: token_jaccard=0.6923, heading_jaccard=1.0, |∩token|=45
- **共有 H2（归一化后）**: 1. 概述, 2. 技术实现, 3. 实施路径, 4. 文档治理, 5. 总结
- **标题**: A「因子信号生成模块蓝图…」 / B「事件驱动因子模块蓝图…」
- **建议 canonical**: `docs/02_FACTOR_LIBRARY/34_FACTOR_SIGNAL_GEN/FACTOR_SIGNAL_GEN_BLUEPRINT.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/02_FACTOR_LIBRARY/39_EVENT_DRIVEN_FACTOR/EVENT_DRIVEN_FACTOR_BLUEPRINT.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 技术实现
  - 3. 实施路径
  - 4. 文档治理
  - 5. 总结

### 39. score=0.8058

- **A**: `docs/02_FACTOR_LIBRARY/34_FACTOR_SIGNAL_GEN/FACTOR_SIGNAL_GEN_BLUEPRINT.md`
- **B**: `docs/02_FACTOR_LIBRARY/40_FACTOR_CAPACITY_MGMT/FACTOR_CAPACITY_MGMT_BLUEPRINT.md`
- **指标**: token_jaccard=0.6923, heading_jaccard=1.0, |∩token|=45
- **共有 H2（归一化后）**: 1. 概述, 2. 技术实现, 3. 实施路径, 4. 文档治理, 5. 总结
- **标题**: A「因子信号生成模块蓝图…」 / B「因子容量管理模块蓝图…」
- **建议 canonical**: `docs/02_FACTOR_LIBRARY/34_FACTOR_SIGNAL_GEN/FACTOR_SIGNAL_GEN_BLUEPRINT.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/02_FACTOR_LIBRARY/40_FACTOR_CAPACITY_MGMT/FACTOR_CAPACITY_MGMT_BLUEPRINT.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 技术实现
  - 3. 实施路径
  - 4. 文档治理
  - 5. 总结

### 40. score=0.8058

- **A**: `docs/02_FACTOR_LIBRARY/35_INDUSTRY_ROTATION/INDUSTRY_ROTATION_BLUEPRINT.md`
- **B**: `docs/02_FACTOR_LIBRARY/39_EVENT_DRIVEN_FACTOR/EVENT_DRIVEN_FACTOR_BLUEPRINT.md`
- **指标**: token_jaccard=0.6923, heading_jaccard=1.0, |∩token|=45
- **共有 H2（归一化后）**: 1. 概述, 2. 技术实现, 3. 实施路径, 4. 文档治理, 5. 总结
- **标题**: A「行业轮动因子模块蓝图…」 / B「事件驱动因子模块蓝图…」
- **建议 canonical**: `docs/02_FACTOR_LIBRARY/39_EVENT_DRIVEN_FACTOR/EVENT_DRIVEN_FACTOR_BLUEPRINT.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/02_FACTOR_LIBRARY/35_INDUSTRY_ROTATION/INDUSTRY_ROTATION_BLUEPRINT.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 技术实现
  - 3. 实施路径
  - 4. 文档治理
  - 5. 总结

### 41. score=0.8058

- **A**: `docs/02_FACTOR_LIBRARY/35_INDUSTRY_ROTATION/INDUSTRY_ROTATION_BLUEPRINT.md`
- **B**: `docs/02_FACTOR_LIBRARY/40_FACTOR_CAPACITY_MGMT/FACTOR_CAPACITY_MGMT_BLUEPRINT.md`
- **指标**: token_jaccard=0.6923, heading_jaccard=1.0, |∩token|=45
- **共有 H2（归一化后）**: 1. 概述, 2. 技术实现, 3. 实施路径, 4. 文档治理, 5. 总结
- **标题**: A「行业轮动因子模块蓝图…」 / B「因子容量管理模块蓝图…」
- **建议 canonical**: `docs/02_FACTOR_LIBRARY/40_FACTOR_CAPACITY_MGMT/FACTOR_CAPACITY_MGMT_BLUEPRINT.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/02_FACTOR_LIBRARY/35_INDUSTRY_ROTATION/INDUSTRY_ROTATION_BLUEPRINT.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 技术实现
  - 3. 实施路径
  - 4. 文档治理
  - 5. 总结

### 42. score=0.8058

- **A**: `docs/02_FACTOR_LIBRARY/36_FACTOR_EXPOSURE_MGMT/FACTOR_EXPOSURE_MGMT_BLUEPRINT.md`
- **B**: `docs/02_FACTOR_LIBRARY/39_EVENT_DRIVEN_FACTOR/EVENT_DRIVEN_FACTOR_BLUEPRINT.md`
- **指标**: token_jaccard=0.6923, heading_jaccard=1.0, |∩token|=45
- **共有 H2（归一化后）**: 1. 概述, 2. 技术实现, 3. 实施路径, 4. 文档治理, 5. 总结
- **标题**: A「因子暴露管理模块蓝图…」 / B「事件驱动因子模块蓝图…」
- **建议 canonical**: `docs/02_FACTOR_LIBRARY/36_FACTOR_EXPOSURE_MGMT/FACTOR_EXPOSURE_MGMT_BLUEPRINT.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/02_FACTOR_LIBRARY/39_EVENT_DRIVEN_FACTOR/EVENT_DRIVEN_FACTOR_BLUEPRINT.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 技术实现
  - 3. 实施路径
  - 4. 文档治理
  - 5. 总结

### 43. score=0.8058

- **A**: `docs/02_FACTOR_LIBRARY/36_FACTOR_EXPOSURE_MGMT/FACTOR_EXPOSURE_MGMT_BLUEPRINT.md`
- **B**: `docs/02_FACTOR_LIBRARY/40_FACTOR_CAPACITY_MGMT/FACTOR_CAPACITY_MGMT_BLUEPRINT.md`
- **指标**: token_jaccard=0.6923, heading_jaccard=1.0, |∩token|=45
- **共有 H2（归一化后）**: 1. 概述, 2. 技术实现, 3. 实施路径, 4. 文档治理, 5. 总结
- **标题**: A「因子暴露管理模块蓝图…」 / B「因子容量管理模块蓝图…」
- **建议 canonical**: `docs/02_FACTOR_LIBRARY/36_FACTOR_EXPOSURE_MGMT/FACTOR_EXPOSURE_MGMT_BLUEPRINT.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/02_FACTOR_LIBRARY/40_FACTOR_CAPACITY_MGMT/FACTOR_CAPACITY_MGMT_BLUEPRINT.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 技术实现
  - 3. 实施路径
  - 4. 文档治理
  - 5. 总结

### 44. score=0.8058

- **A**: `docs/02_FACTOR_LIBRARY/38_FACTOR_TURNOVER_OPT/FACTOR_TURNOVER_OPT_BLUEPRINT.md`
- **B**: `docs/02_FACTOR_LIBRARY/39_EVENT_DRIVEN_FACTOR/EVENT_DRIVEN_FACTOR_BLUEPRINT.md`
- **指标**: token_jaccard=0.6923, heading_jaccard=1.0, |∩token|=45
- **共有 H2（归一化后）**: 1. 概述, 2. 技术实现, 3. 实施路径, 4. 文档治理, 5. 总结
- **标题**: A「因子换手率优化模块蓝图…」 / B「事件驱动因子模块蓝图…」
- **建议 canonical**: `docs/02_FACTOR_LIBRARY/38_FACTOR_TURNOVER_OPT/FACTOR_TURNOVER_OPT_BLUEPRINT.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/02_FACTOR_LIBRARY/39_EVENT_DRIVEN_FACTOR/EVENT_DRIVEN_FACTOR_BLUEPRINT.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 技术实现
  - 3. 实施路径
  - 4. 文档治理
  - 5. 总结

### 45. score=0.8058

- **A**: `docs/02_FACTOR_LIBRARY/38_FACTOR_TURNOVER_OPT/FACTOR_TURNOVER_OPT_BLUEPRINT.md`
- **B**: `docs/02_FACTOR_LIBRARY/40_FACTOR_CAPACITY_MGMT/FACTOR_CAPACITY_MGMT_BLUEPRINT.md`
- **指标**: token_jaccard=0.6923, heading_jaccard=1.0, |∩token|=45
- **共有 H2（归一化后）**: 1. 概述, 2. 技术实现, 3. 实施路径, 4. 文档治理, 5. 总结
- **标题**: A「因子换手率优化模块蓝图…」 / B「因子容量管理模块蓝图…」
- **建议 canonical**: `docs/02_FACTOR_LIBRARY/38_FACTOR_TURNOVER_OPT/FACTOR_TURNOVER_OPT_BLUEPRINT.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/02_FACTOR_LIBRARY/40_FACTOR_CAPACITY_MGMT/FACTOR_CAPACITY_MGMT_BLUEPRINT.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 技术实现
  - 3. 实施路径
  - 4. 文档治理
  - 5. 总结

### 46. score=0.8043

- **A**: `docs/02_FACTOR_LIBRARY/32_FACTOR_DYNAMIC_WEIGHT/FACTOR_DYNAMIC_WEIGHT_BLUEPRINT.md`
- **B**: `docs/02_FACTOR_LIBRARY/37_FACTOR_CORRELATION/FACTOR_CORRELATION_BLUEPRINT.md`
- **指标**: token_jaccard=0.6866, heading_jaccard=1.0, |∩token|=46
- **共有 H2（归一化后）**: 1. 概述, 2. 技术实现, 3. 实施路径, 4. 文档治理, 5. 总结
- **标题**: A「因子动态权重调整模块蓝图…」 / B「因子相关性分析模块蓝图…」
- **建议 canonical**: `docs/02_FACTOR_LIBRARY/32_FACTOR_DYNAMIC_WEIGHT/FACTOR_DYNAMIC_WEIGHT_BLUEPRINT.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/02_FACTOR_LIBRARY/37_FACTOR_CORRELATION/FACTOR_CORRELATION_BLUEPRINT.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 技术实现
  - 3. 实施路径
  - 4. 文档治理
  - 5. 总结

### 47. score=0.8

- **A**: `docs/02_FACTOR_LIBRARY/37_FACTOR_CORRELATION/FACTOR_CORRELATION_BLUEPRINT.md`
- **B**: `docs/02_FACTOR_LIBRARY/39_EVENT_DRIVEN_FACTOR/EVENT_DRIVEN_FACTOR_BLUEPRINT.md`
- **指标**: token_jaccard=0.6818, heading_jaccard=1.0, |∩token|=45
- **共有 H2（归一化后）**: 1. 概述, 2. 技术实现, 3. 实施路径, 4. 文档治理, 5. 总结
- **标题**: A「因子相关性分析模块蓝图…」 / B「事件驱动因子模块蓝图…」
- **建议 canonical**: `docs/02_FACTOR_LIBRARY/37_FACTOR_CORRELATION/FACTOR_CORRELATION_BLUEPRINT.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/02_FACTOR_LIBRARY/39_EVENT_DRIVEN_FACTOR/EVENT_DRIVEN_FACTOR_BLUEPRINT.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 技术实现
  - 3. 实施路径
  - 4. 文档治理
  - 5. 总结

### 48. score=0.8

- **A**: `docs/02_FACTOR_LIBRARY/37_FACTOR_CORRELATION/FACTOR_CORRELATION_BLUEPRINT.md`
- **B**: `docs/02_FACTOR_LIBRARY/40_FACTOR_CAPACITY_MGMT/FACTOR_CAPACITY_MGMT_BLUEPRINT.md`
- **指标**: token_jaccard=0.6818, heading_jaccard=1.0, |∩token|=45
- **共有 H2（归一化后）**: 1. 概述, 2. 技术实现, 3. 实施路径, 4. 文档治理, 5. 总结
- **标题**: A「因子相关性分析模块蓝图…」 / B「因子容量管理模块蓝图…」
- **建议 canonical**: `docs/02_FACTOR_LIBRARY/37_FACTOR_CORRELATION/FACTOR_CORRELATION_BLUEPRINT.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/02_FACTOR_LIBRARY/40_FACTOR_CAPACITY_MGMT/FACTOR_CAPACITY_MGMT_BLUEPRINT.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 技术实现
  - 3. 实施路径
  - 4. 文档治理
  - 5. 总结

### 49. score=0.7975

- **A**: `docs/01_FRAMEWORK/STRATEGIC_DECISION_LAYER_BLUEPRINT.md`
- **B**: `docs/11_STRATEGIC_DECISION/archive/BLUEPRINT_v2.0.1_backup.md`
- **指标**: token_jaccard=0.8864, heading_jaccard=0.6, |∩token|=273
- **共有 H2（归一化后）**: 一、架构设计, 三、数据模型设?, 二、核心组件详细设?, 五、成功指?, 四、实施路?, 📋 执行摘要
- **标题**: A「Layer 11: 战略决策层蓝图…」 / B「Layer 11: 战略决策层蓝图…」
- **建议 canonical**: `docs/01_FRAMEWORK/STRATEGIC_DECISION_LAYER_BLUEPRINT.md`
- **理由（机器）**: 建议 front matter 日期更新
- **另一路径**: `docs/11_STRATEGIC_DECISION/archive/BLUEPRINT_v2.0.1_backup.md`（可 stub / archive / 叙事归并）
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

### 50. score=0.7944

- **A**: `docs/02_FACTOR_LIBRARY/32_FACTOR_DYNAMIC_WEIGHT/FACTOR_DYNAMIC_WEIGHT_BLUEPRINT.md`
- **B**: `docs/02_FACTOR_LIBRARY/39_EVENT_DRIVEN_FACTOR/EVENT_DRIVEN_FACTOR_BLUEPRINT.md`
- **指标**: token_jaccard=0.6716, heading_jaccard=1.0, |∩token|=45
- **共有 H2（归一化后）**: 1. 概述, 2. 技术实现, 3. 实施路径, 4. 文档治理, 5. 总结
- **标题**: A「因子动态权重调整模块蓝图…」 / B「事件驱动因子模块蓝图…」
- **建议 canonical**: `docs/02_FACTOR_LIBRARY/32_FACTOR_DYNAMIC_WEIGHT/FACTOR_DYNAMIC_WEIGHT_BLUEPRINT.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/02_FACTOR_LIBRARY/39_EVENT_DRIVEN_FACTOR/EVENT_DRIVEN_FACTOR_BLUEPRINT.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 技术实现
  - 3. 实施路径
  - 4. 文档治理
  - 5. 总结

### 51. score=0.7944

- **A**: `docs/02_FACTOR_LIBRARY/32_FACTOR_DYNAMIC_WEIGHT/FACTOR_DYNAMIC_WEIGHT_BLUEPRINT.md`
- **B**: `docs/02_FACTOR_LIBRARY/40_FACTOR_CAPACITY_MGMT/FACTOR_CAPACITY_MGMT_BLUEPRINT.md`
- **指标**: token_jaccard=0.6716, heading_jaccard=1.0, |∩token|=45
- **共有 H2（归一化后）**: 1. 概述, 2. 技术实现, 3. 实施路径, 4. 文档治理, 5. 总结
- **标题**: A「因子动态权重调整模块蓝图…」 / B「因子容量管理模块蓝图…」
- **建议 canonical**: `docs/02_FACTOR_LIBRARY/32_FACTOR_DYNAMIC_WEIGHT/FACTOR_DYNAMIC_WEIGHT_BLUEPRINT.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/02_FACTOR_LIBRARY/40_FACTOR_CAPACITY_MGMT/FACTOR_CAPACITY_MGMT_BLUEPRINT.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 技术实现
  - 3. 实施路径
  - 4. 文档治理
  - 5. 总结

### 52. score=0.7425

- **A**: `docs/01_FRAMEWORK/MAMBA_SSM_BLUEPRINT.md`
- **B**: `docs/01_FRAMEWORK/MIXTURE_OF_EXPERTS_BLUEPRINT.md`
- **指标**: token_jaccard=0.5317, heading_jaccard=1.0, |∩token|=67
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「requirements_mamba.txt…」 / B「混合专家模型(MoE)蓝图…」
- **建议 canonical**: `docs/01_FRAMEWORK/MIXTURE_OF_EXPERTS_BLUEPRINT.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/01_FRAMEWORK/MAMBA_SSM_BLUEPRINT.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 53. score=0.725

- **A**: `docs/01_FRAMEWORK/MIXTURE_OF_EXPERTS_BLUEPRINT.md`
- **B**: `docs/01_FRAMEWORK/MULTIMODAL_FUSION_BLUEPRINT.md`
- **指标**: token_jaccard=0.5, heading_jaccard=1.0, |∩token|=65
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「混合专家模型(MoE)蓝图…」 / B「requirements_multimodal.txt…」
- **建议 canonical**: `docs/01_FRAMEWORK/MULTIMODAL_FUSION_BLUEPRINT.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/01_FRAMEWORK/MIXTURE_OF_EXPERTS_BLUEPRINT.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 54. score=0.7145

- **A**: `docs/01_FRAMEWORK/MAMBA_SSM_BLUEPRINT.md`
- **B**: `docs/01_FRAMEWORK/MULTIMODAL_FUSION_BLUEPRINT.md`
- **指标**: token_jaccard=0.4809, heading_jaccard=1.0, |∩token|=63
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「requirements_mamba.txt…」 / B「requirements_multimodal.txt…」
- **建议 canonical**: `docs/01_FRAMEWORK/MULTIMODAL_FUSION_BLUEPRINT.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/01_FRAMEWORK/MAMBA_SSM_BLUEPRINT.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 55. score=0.7135

- **A**: `docs/01_FRAMEWORK/MODEL_PRUNING_BLUEPRINT.md`
- **B**: `docs/01_FRAMEWORK/MODEL_QUANTIZATION_BLUEPRINT.md`
- **指标**: token_jaccard=0.4792, heading_jaccard=1.0, |∩token|=69
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「模型剪枝蓝图…」 / B「模型量化蓝图…」
- **建议 canonical**: `docs/01_FRAMEWORK/MODEL_QUANTIZATION_BLUEPRINT.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/01_FRAMEWORK/MODEL_PRUNING_BLUEPRINT.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 56. score=0.7129

- **A**: `docs/01_FRAMEWORK/MIA_DEFENSE_BLUEPRINT.md`
- **B**: `docs/01_FRAMEWORK/MODEL_WATERMARK_BLUEPRINT.md`
- **指标**: token_jaccard=0.4779, heading_jaccard=1.0, |∩token|=65
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「MIA防御蓝图…」 / B「模型水印蓝图…」
- **建议 canonical**: `docs/01_FRAMEWORK/MODEL_WATERMARK_BLUEPRINT.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/01_FRAMEWORK/MIA_DEFENSE_BLUEPRINT.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 57. score=0.7054

- **A**: `docs/01_FRAMEWORK/MODEL_PRUNING_BLUEPRINT.md`
- **B**: `docs/01_FRAMEWORK/MODEL_WATERMARK_BLUEPRINT.md`
- **指标**: token_jaccard=0.4643, heading_jaccard=1.0, |∩token|=65
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「模型剪枝蓝图…」 / B「模型水印蓝图…」
- **建议 canonical**: `docs/01_FRAMEWORK/MODEL_WATERMARK_BLUEPRINT.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/01_FRAMEWORK/MODEL_PRUNING_BLUEPRINT.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 58. score=0.7051

- **A**: `docs/01_FRAMEWORK/MIA_DEFENSE_BLUEPRINT.md`
- **B**: `docs/01_FRAMEWORK/MODEL_PRUNING_BLUEPRINT.md`
- **指标**: token_jaccard=0.4638, heading_jaccard=1.0, |∩token|=64
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「MIA防御蓝图…」 / B「模型剪枝蓝图…」
- **建议 canonical**: `docs/01_FRAMEWORK/MODEL_PRUNING_BLUEPRINT.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/01_FRAMEWORK/MIA_DEFENSE_BLUEPRINT.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 59. score=0.6989

- **A**: `docs/01_FRAMEWORK/MIXTURE_OF_EXPERTS_BLUEPRINT.md`
- **B**: `docs/01_FRAMEWORK/MODEL_WATERMARK_BLUEPRINT.md`
- **指标**: token_jaccard=0.4526, heading_jaccard=1.0, |∩token|=62
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「混合专家模型(MoE)蓝图…」 / B「模型水印蓝图…」
- **建议 canonical**: `docs/01_FRAMEWORK/MODEL_WATERMARK_BLUEPRINT.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/01_FRAMEWORK/MIXTURE_OF_EXPERTS_BLUEPRINT.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 60. score=0.6986

- **A**: `docs/01_FRAMEWORK/KNOWLEDGE_DISTILLATION_BLUEPRINT.md`
- **B**: `docs/01_FRAMEWORK/MODEL_PRUNING_BLUEPRINT.md`
- **指标**: token_jaccard=0.4521, heading_jaccard=1.0, |∩token|=66
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「知识蒸馏蓝图…」 / B「模型剪枝蓝图…」
- **建议 canonical**: `docs/01_FRAMEWORK/KNOWLEDGE_DISTILLATION_BLUEPRINT.md`
- **理由（机器）**: 建议正文体量更大（可能更完整）
- **另一路径**: `docs/01_FRAMEWORK/MODEL_PRUNING_BLUEPRINT.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 61. score=0.6971

- **A**: `docs/01_FRAMEWORK/MODEL_WATERMARK_BLUEPRINT.md`
- **B**: `docs/01_FRAMEWORK/MULTIMODAL_FUSION_BLUEPRINT.md`
- **指标**: token_jaccard=0.4493, heading_jaccard=1.0, |∩token|=62
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「模型水印蓝图…」 / B「requirements_multimodal.txt…」
- **建议 canonical**: `docs/01_FRAMEWORK/MODEL_WATERMARK_BLUEPRINT.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/01_FRAMEWORK/MULTIMODAL_FUSION_BLUEPRINT.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 62. score=0.6967

- **A**: `docs/01_FRAMEWORK/MIA_DEFENSE_BLUEPRINT.md`
- **B**: `docs/01_FRAMEWORK/MULTIMODAL_FUSION_BLUEPRINT.md`
- **指标**: token_jaccard=0.4485, heading_jaccard=1.0, |∩token|=61
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「MIA防御蓝图…」 / B「requirements_multimodal.txt…」
- **建议 canonical**: `docs/01_FRAMEWORK/MIA_DEFENSE_BLUEPRINT.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/01_FRAMEWORK/MULTIMODAL_FUSION_BLUEPRINT.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 63. score=0.6953

- **A**: `docs/01_FRAMEWORK/MODEL_PRUNING_BLUEPRINT.md`
- **B**: `docs/01_FRAMEWORK/MULTIMODAL_FUSION_BLUEPRINT.md`
- **指标**: token_jaccard=0.446, heading_jaccard=1.0, |∩token|=62
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「模型剪枝蓝图…」 / B「requirements_multimodal.txt…」
- **建议 canonical**: `docs/01_FRAMEWORK/MODEL_PRUNING_BLUEPRINT.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/01_FRAMEWORK/MULTIMODAL_FUSION_BLUEPRINT.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 64. score=0.6944

- **A**: `docs/01_FRAMEWORK/MAMBA_SSM_BLUEPRINT.md`
- **B**: `docs/01_FRAMEWORK/MIA_DEFENSE_BLUEPRINT.md`
- **指标**: token_jaccard=0.4444, heading_jaccard=1.0, |∩token|=60
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「requirements_mamba.txt…」 / B「MIA防御蓝图…」
- **建议 canonical**: `docs/01_FRAMEWORK/MIA_DEFENSE_BLUEPRINT.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/01_FRAMEWORK/MAMBA_SSM_BLUEPRINT.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 65. score=0.6932

- **A**: `docs/01_FRAMEWORK/MODEL_QUANTIZATION_BLUEPRINT.md`
- **B**: `docs/01_FRAMEWORK/MODEL_WATERMARK_BLUEPRINT.md`
- **指标**: token_jaccard=0.4422, heading_jaccard=1.0, |∩token|=65
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「模型量化蓝图…」 / B「模型水印蓝图…」
- **建议 canonical**: `docs/01_FRAMEWORK/MODEL_QUANTIZATION_BLUEPRINT.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/01_FRAMEWORK/MODEL_WATERMARK_BLUEPRINT.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 66. score=0.6928

- **A**: `docs/01_FRAMEWORK/MIA_DEFENSE_BLUEPRINT.md`
- **B**: `docs/01_FRAMEWORK/MODEL_QUANTIZATION_BLUEPRINT.md`
- **指标**: token_jaccard=0.4414, heading_jaccard=1.0, |∩token|=64
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「MIA防御蓝图…」 / B「模型量化蓝图…」
- **建议 canonical**: `docs/01_FRAMEWORK/MODEL_QUANTIZATION_BLUEPRINT.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/01_FRAMEWORK/MIA_DEFENSE_BLUEPRINT.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 67. score=0.6926

- **A**: `docs/01_FRAMEWORK/MIA_DEFENSE_BLUEPRINT.md`
- **B**: `docs/01_FRAMEWORK/MIXTURE_OF_EXPERTS_BLUEPRINT.md`
- **指标**: token_jaccard=0.4412, heading_jaccard=1.0, |∩token|=60
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「MIA防御蓝图…」 / B「混合专家模型(MoE)蓝图…」
- **建议 canonical**: `docs/01_FRAMEWORK/MIA_DEFENSE_BLUEPRINT.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/01_FRAMEWORK/MIXTURE_OF_EXPERTS_BLUEPRINT.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 68. score=0.692

- **A**: `docs/01_FRAMEWORK/FUND_MANAGEMENT_INTERFACE_BLUEPRINT.md`
- **B**: `docs/01_FRAMEWORK/POSITION_MANAGEMENT_INTERFACE_BLUEPRINT.md`
- **指标**: token_jaccard=0.4643, heading_jaccard=1.0, |∩token|=52
- **共有 H2（归一化后）**: 📋 一、概述, 🔧 三、开源项目集成, 🚀 二、实施路径
- **标题**: A「资金管理界面蓝图…」 / B「持仓管理界面蓝图…」
- **建议 canonical**: `docs/01_FRAMEWORK/POSITION_MANAGEMENT_INTERFACE_BLUEPRINT.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/01_FRAMEWORK/FUND_MANAGEMENT_INTERFACE_BLUEPRINT.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 📋 一、概述
  - 🚀 二、实施路径
  - 🔧 三、开源项目集成

### 69. score=0.6899

- **A**: `docs/01_FRAMEWORK/MARKET_MICROSTRUCTURE_MODEL_BLUEPRINT.md`
- **B**: `docs/01_FRAMEWORK/MODEL_WATERMARK_BLUEPRINT.md`
- **指标**: token_jaccard=0.4362, heading_jaccard=1.0, |∩token|=65
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「市场微观结构模型蓝图…」 / B「模型水印蓝图…」
- **建议 canonical**: `docs/01_FRAMEWORK/MARKET_MICROSTRUCTURE_MODEL_BLUEPRINT.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/01_FRAMEWORK/MODEL_WATERMARK_BLUEPRINT.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 70. score=0.6891

- **A**: `docs/01_FRAMEWORK/MAMBA_SSM_BLUEPRINT.md`
- **B**: `docs/01_FRAMEWORK/MODEL_WATERMARK_BLUEPRINT.md`
- **指标**: token_jaccard=0.4348, heading_jaccard=1.0, |∩token|=60
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「requirements_mamba.txt…」 / B「模型水印蓝图…」
- **建议 canonical**: `docs/01_FRAMEWORK/MODEL_WATERMARK_BLUEPRINT.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/01_FRAMEWORK/MAMBA_SSM_BLUEPRINT.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 71. score=0.6879

- **A**: `docs/01_FRAMEWORK/MIA_DEFENSE_BLUEPRINT.md`
- **B**: `docs/01_FRAMEWORK/MODEL_PERFORMANCE_BENCHMARK_BLUEPRINT.md`
- **指标**: token_jaccard=0.4326, heading_jaccard=1.0, |∩token|=61
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「MIA防御蓝图…」 / B「模型性能基准蓝图…」
- **建议 canonical**: `docs/01_FRAMEWORK/MODEL_PERFORMANCE_BENCHMARK_BLUEPRINT.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/01_FRAMEWORK/MIA_DEFENSE_BLUEPRINT.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 72. score=0.6874

- **A**: `docs/01_FRAMEWORK/MAMBA_SSM_BLUEPRINT.md`
- **B**: `docs/01_FRAMEWORK/MODEL_PRUNING_BLUEPRINT.md`
- **指标**: token_jaccard=0.4317, heading_jaccard=1.0, |∩token|=60
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「requirements_mamba.txt…」 / B「模型剪枝蓝图…」
- **建议 canonical**: `docs/01_FRAMEWORK/MODEL_PRUNING_BLUEPRINT.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/01_FRAMEWORK/MAMBA_SSM_BLUEPRINT.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 73. score=0.6865

- **A**: `docs/01_FRAMEWORK/SELF_SUPERVISED_LEARNING_BLUEPRINT.md`
- **B**: `docs/01_FRAMEWORK/SYNTHETIC_DATA_GENERATION_BLUEPRINT.md`
- **指标**: token_jaccard=0.4361, heading_jaccard=1.0, |∩token|=58
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「requirements_ssl.txt…」 / B「requirements_synthetic.txt…」
- **建议 canonical**: `docs/01_FRAMEWORK/SYNTHETIC_DATA_GENERATION_BLUEPRINT.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/01_FRAMEWORK/SELF_SUPERVISED_LEARNING_BLUEPRINT.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 74. score=0.6857

- **A**: `docs/01_FRAMEWORK/MIXTURE_OF_EXPERTS_BLUEPRINT.md`
- **B**: `docs/01_FRAMEWORK/MODEL_PRUNING_BLUEPRINT.md`
- **指标**: token_jaccard=0.4286, heading_jaccard=1.0, |∩token|=60
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「混合专家模型(MoE)蓝图…」 / B「模型剪枝蓝图…」
- **建议 canonical**: `docs/01_FRAMEWORK/MODEL_PRUNING_BLUEPRINT.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/01_FRAMEWORK/MIXTURE_OF_EXPERTS_BLUEPRINT.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 75. score=0.6852

- **A**: `docs/01_FRAMEWORK/KNOWLEDGE_DISTILLATION_BLUEPRINT.md`
- **B**: `docs/01_FRAMEWORK/MULTIMODAL_FUSION_BLUEPRINT.md`
- **指标**: token_jaccard=0.4276, heading_jaccard=1.0, |∩token|=62
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「知识蒸馏蓝图…」 / B「requirements_multimodal.txt…」
- **建议 canonical**: `docs/01_FRAMEWORK/KNOWLEDGE_DISTILLATION_BLUEPRINT.md`
- **理由（机器）**: 建议正文体量更大（可能更完整）
- **另一路径**: `docs/01_FRAMEWORK/MULTIMODAL_FUSION_BLUEPRINT.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 76. score=0.6851

- **A**: `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/PORTFOLIO_ATTRIBUTION_BLUEPRINT.md`
- **B**: `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/PORTFOLIO_CONSTRAINT_MANAGEMENT_BLUEPRINT.md`
- **指标**: token_jaccard=0.4275, heading_jaccard=1.0, |∩token|=174
- **共有 H2（归一化后）**: 1. 概述, 3. 接口定义, 4. 实施路径, 5. 文档治理, 变更历史, 实现方案
- **标题**: A「组合归因分析模块蓝图…」 / B「组合约束管理模块蓝图…」
- **建议 canonical**: `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/PORTFOLIO_ATTRIBUTION_BLUEPRINT.md`
- **理由（机器）**: 建议路径含图纸柜 `01_BLUEPRINTS`
- **另一路径**: `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/PORTFOLIO_CONSTRAINT_MANAGEMENT_BLUEPRINT.md`（可 stub / archive / 叙事归并）
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

### 77. score=0.6836

- **A**: `docs/01_FRAMEWORK/KNOWLEDGE_DISTILLATION_BLUEPRINT.md`
- **B**: `docs/01_FRAMEWORK/MIA_DEFENSE_BLUEPRINT.md`
- **指标**: token_jaccard=0.4247, heading_jaccard=1.0, |∩token|=62
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「知识蒸馏蓝图…」 / B「MIA防御蓝图…」
- **建议 canonical**: `docs/01_FRAMEWORK/KNOWLEDGE_DISTILLATION_BLUEPRINT.md`
- **理由（机器）**: 建议正文体量更大（可能更完整）
- **另一路径**: `docs/01_FRAMEWORK/MIA_DEFENSE_BLUEPRINT.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 78. score=0.6836

- **A**: `docs/01_FRAMEWORK/MODEL_QUANTIZATION_BLUEPRINT.md`
- **B**: `docs/01_FRAMEWORK/MULTIMODAL_FUSION_BLUEPRINT.md`
- **指标**: token_jaccard=0.4247, heading_jaccard=1.0, |∩token|=62
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「模型量化蓝图…」 / B「requirements_multimodal.txt…」
- **建议 canonical**: `docs/01_FRAMEWORK/MODEL_QUANTIZATION_BLUEPRINT.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/01_FRAMEWORK/MULTIMODAL_FUSION_BLUEPRINT.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 79. score=0.683

- **A**: `docs/01_FRAMEWORK/MODEL_PERFORMANCE_BENCHMARK_BLUEPRINT.md`
- **B**: `docs/01_FRAMEWORK/MODEL_WATERMARK_BLUEPRINT.md`
- **指标**: token_jaccard=0.4236, heading_jaccard=1.0, |∩token|=61
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「模型性能基准蓝图…」 / B「模型水印蓝图…」
- **建议 canonical**: `docs/01_FRAMEWORK/MODEL_PERFORMANCE_BENCHMARK_BLUEPRINT.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/01_FRAMEWORK/MODEL_WATERMARK_BLUEPRINT.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

### 80. score=0.6826

- **A**: `docs/01_FRAMEWORK/MODEL_VERSIONING_BLUEPRINT.md`
- **B**: `docs/01_FRAMEWORK/MODEL_WATERMARK_BLUEPRINT.md`
- **指标**: token_jaccard=0.4228, heading_jaccard=1.0, |∩token|=63
- **共有 H2（归一化后）**: 1. 概述, 2. 架构设计, 3. 接口设计, 4. 技术栈, 5. 验收标准, 6. 文档治理
- **标题**: A「模型版本控制蓝图…」 / B「模型水印蓝图…」
- **建议 canonical**: `docs/01_FRAMEWORK/MODEL_VERSIONING_BLUEPRINT.md`
- **理由（机器）**: 按规则加权分略高（图纸柜/体量/日期）
- **另一路径**: `docs/01_FRAMEWORK/MODEL_WATERMARK_BLUEPRINT.md`（可 stub / archive / 叙事归并）
- **建议合并大纲（H2 草案）**:
  - 1. 概述
  - 2. 架构设计
  - 3. 接口设计
  - 4. 技术栈
  - 5. 验收标准
  - 6. 文档治理

> 共 400 对，上文仅展示前 80 对；详见 JSON。
