---
module_id: KE-944
status: active
title: 5.1.2 子目录准入与防幻觉路径映射
category: governance
---

# 5.1.2 子目录准入与防幻觉路径映射

5.1.2 子目录准入与防幻觉路径映射

> **设计目的**：AI 每次新会话都是零记忆，不知道上一次把文件放在哪了。
> 本节的设计目标是：**AI 只需要看这一张表，就能无歧义地判断任何文件该放哪，不需要推断任何路径。**
>
> **防幻觉机制**：
> 1. **完整路径**——每个目录都从项目根开始写完整路径，AI 不需要拼接
> 2. **真实锚点**——每个目录都列出当前已存在的真实文件，AI 可以用它来验证路径是否正确
> 3. **反向映射**——不仅写"这个目录能放什么"，还写"这类文件只能放这个目录"
> 4. **module_id 交叉引用**——每个锚点文件都标注 module_id，AI 可以通过搜索 module_id 验证文件位置

**完整路径映射表**：

| # | 目录完整路径 | 定位 | 当前真实文件（锚点） | ✅ 能放 | ❌ 不能放（→ 正确位置） |
|---|------------|------|-------------------|--------|---------------------|
| 1 | `docs/01_policies_and_standards/meta/` | 元标准层 | PS-STD-000 ~ PS-STD-007, PS-REG-001 | 元标准（关于规则体系本身的规则） | 领域治理规则（→ #2）、操作步骤（→ #10）、层域规则（→ #14~#17） |
| 2 | `docs/01_policies_and_standards/rules/` | 文档治理 | GOV-DOC-001~010 | 文档命名/路径/编码/生命周期/安全规则 | AI 治理（→ #3）、任务治理（→ #4） |
| 3 | `docs/01_policies_and_standards/governance/ai/` | AI 治理 | GOV-AI-001~007 | AI 自治/入职/幻觉/模型契约/操作预算 | 任务卡（→ #4）、VC 操作步骤（→ #10） |
| 4 | `docs/01_policies_and_standards/governance/task/` | 任务治理 | GOV-TASK-001~003 | 任务卡/交接/裁定/生命周期 | AI 操作预算（→ #3）、VC 操作（→ #10） |
| 5 | `docs/01_policies_and_standards/governance/security/` | 安全治理 | （experimental 新建）GOV-SEC-001~003 | 密钥管理/访问控制/安全事件策略 | 安全操作手册（→ #11 或 #10） |
| 6 | `docs/01_policies_and_standards/governance/compliance/` | 合规治理 | （experimental 新建）GOV-CMP-001~002 | 监管分类法/审计追踪策略 | 合规操作手册（→ #11）、L10 特定规则（→ #14 L10） |
| 7 | `docs/01_policies_and_standards/governance/architecture/` | 架构治理 | （experimental 新建）GOV-ARCH-001~003 | ADR 协议/架构评审/架构版本化 | 架构视图（→ 02_enterprise_architecture/）、模块文档（→ 03_modules/） |
| 8 | `docs/01_policies_and_standards/governance/data/` | 数据治理 | （experimental 新建）GOV-DATA-001~003 | 数据质量/血缘/保留策略 | 数据操作手册（→ #11）、L00 特定规则（→ #14 L00） |
| 9 | `docs/01_policies_and_standards/governance/module/` | 模块治理 | （experimental 新建）GOV-MOD-001~005 | 模块准入/生命周期/接口契约/注入规则 | 模块文档（→ 03_modules/）、模块代码（→ src/zephyr/） |
| 10 | `docs/01_policies_and_standards/operational/vibe_coding/` | VC 操作 | OPS-VC-001~003 | VC 上下文规则/session 状态机/可验证性操作 | VC 声明式约束（→ governance/ 对应子域） |
| 11 | `docs/01_policies_and_standards/operational/devops/` | DevOps 操作 | OPS-DEV-001 | pre-commit/CI/部署流程 | DevOps 策略（→ governance/ 对应子域） |
| 12 | `docs/01_policies_and_standards/operational/migration/` | 迁移操作 | OPS-MIG-001 | 迁移审计/迁移步骤 | 迁移策略（→ governance/ 对应子域） |
| 13 | `docs/01_policies_and_standards/domains/L00_data_source/` | L00 层域 | （beta 新建）DOM-L00-001~002 | L00 层的 governance/ + operational/ | 全局规则（→ governance/） |
| 14 | `docs/01_policies_and_standards/domains/L02_alpha_factor/` | L02 层域 | （beta 新建）DOM-L02-001~002 | L02 层的 governance/ + operational/ | 全局规则（→ governance/） |
| 15 | `docs/01_policies_and_standards/domains/L04_risk_management/` | L04 层域 | （beta 新建）DOM-L04-001~002 | L04 层的 governance/ + operational/ | 全局规则（→ governance/） |
| 16 | `docs/01_policies_and_standards/domains/L07_post_trade_analytics/` | L07 层域 | （beta 新建）DOM-L07-001~002 | L07 层的 governance/ + operational/ | 全局规则（→ governance/） |
| 17 | `docs/01_policies_and_standards/_registry/contracts/` | 验证契约 | （stable 新
