---
module_id: AI_CODE_EDITORS_COMPLETE_GUIDE_2829
version: 1.0.0
status: Active
created_date: 2026-04-13
last_updated: 2026-04-13
owner: 首席文档架构师
layer: layer_08
responsibility: 01_TECHNICAL_KNOWLEDGE
---



# 🎯 AI 代码编辑器完全指南 2026年4月版

**调查日期**: 2026年4月12日  
**覆盖编辑器**: GitHub Copilot, Cursor, Claude Code, Windsurf, JetBrains AI, Amazon Q  
**数据来源**: 各编辑器官方网站实时查询  
**更新频率**: 建议月度检查

> 这是一份**超级详细的综合指南**，包含价格、模型、成本分析、场景选择、成本陷阱等全方位信息。

```
```---
```

# 📑 目录

1. [快速选择指南](#快速选择指南)
2. [6大编辑器详细对比](#6大编辑器详细对比)
   - [GitHub Copilot](#1-github-copilot详细版)
   - [Cursor](#2-cursor详细版)
   - [Claude Code](#3-claude-code详细版)
   - [Windsurf](#4-windsurf详细版)
   - [JetBrains AI](#5-jetbrains-ai详细版)
   - [Amazon Q Developer](#6-amazon-q-developer详细版)
3. [完整功能矩阵](#完整功能矩阵)
4. [模型支持与成本分析](#模型支持与成本分析)
5. [场景化选择指南](#场景化选择指南)
6. [成本陷阱与优化](#成本陷阱与优化)
7. [企业级对比](#企业级对比)

```
```---
```

# 🚀 快速选择指南

## 按预算选择

```
$0/月     → GitHub Copilot Free (2000补全/月)
         → Cursor Hobby (有限配额)
         → Amazon Q Free (无限代码补全!)
         
$10/月    → GitHub Copilot Pro ⭐ (最便宜的全能方案)
         → JetBrains AI Pro ($9.66) (最便宜付费版)
         
$20/月    → Cursor Pro ⭐⭐ (最透明的成本)
         → Claude Code Pro (Opus访问)
         → Windsurf Pro (全模型)
         
$40/月    → Cursor Teams ($40/user) (团队首选)
         → Windsurf Teams ($40/user)
         
$60/月    → Cursor Pro+ (体验最好)
         
$100-200  → Claude Code Max (5-20x用量)
         → Windsurf Max (无日限制)
         → Cursor Ultra (20x配置)
         
企业      → Amazon Q Business Pro ($20/user) ⭐ (唯一权限感知)
         → GitHub Enterprise (议价)
```

## 按需求选择

### "我需要代码补全无限且免费"
🏆 **答案: Amazon Q Free**
- 永久无限代码补全
- 无需付费
- AWS IDE 支持

### "我想要最透明的模型成本"
🏆 **答案: Cursor Pro** ($20)
- 每个模型的 API 费率清晰
- Claude: $3-5/M tokens input
- Composer 2: $0.5/M tokens (最便宜)
- 可精确计算每次调用成本

### "我要完全无忧的无限用"
🏆 **答案: Windsurf Max 或 Cursor Ultra** ($200-400)
- 移除日/周限制
- 足够的配额让你放心用
- 不用每月担心超额

### "我是企业，需要权限感知"
🏆 **答案: Amazon Q Business Pro** ($20/user)
- 唯一支持权限感知回复的
- AI确保响应遵守用户权限
- 符合企业数据治理

### "我要GitHub深度集成"
🏆 **答案: GitHub Copilot Pro+** ($39)
- 与GitHub工作流最紧密
- Agent模式完整支持
- GitHub Spark功能

### "我是重度IDE用户"
🏆 **答案: JetBrains AI Ultimate** ($28.98)
- IDE原生集成最深
- 代码补全无限
- 支持本地LLM (Ollama)

```
```---
```

# 6大编辑器详细对比

## 1. GitHub Copilot详细版

### 官方网址
https://github.com/features/copilot/plans

### 💰 完整价格方案

| 方案 | 月度 | 年度 | 付款方式 | 对象 |
|------|------|------|--------|------|
| **Free** | $0 | 免费 | 无 | 个人、学生、开源 |
| **Pro** | $10 | 可选 | 月/年 | 个人开发者 |
| **Pro+** | $39 | 可选 | 月度 | 高级用户 |
| **Enterprise** | 定制 | 定制 | 企业协议 | 大型团队 |

### 🤖 详细模型配置

#### **Free 版本**
**可用模型列表:**
- Claude Haiku 4.5
- GPT-5 Mini

**功能与限制:**
- ✅ 代码补全：2,000次/月
- ✅ Agent 模式请求：50个/月
- ✅ Chat 对话：含50个agent请求内
- ❌ 代码审查：不支持
- ❌ 代码搜索：不支持
- ❌ 知识库问答：不支持
- ❌ Spark 应用创建：不支持

**适合人群:** 学生、开源贡献者、轻度使用者

```
```---
```

#### **Pro 版本** ($10/月) ⭐ 最值得买

**可用模型列表:**
- Claude Haiku 4.5
- Claude Sonnet 4.5
- Claude Opus 4.6
- GPT-5 Mini
- GPT-5.4
- GPT-4 Turbo
- Google Gemini (各版本)
- OpenAI o1-mini (即将)

**功能与限制:**
- ✅ 代码补全：**无限制**
- ✅ Agent 模式：**无限制**（含速率）
- ✅ Chat 对话：**基本无限**
- ⚠️ Premium Requests：300个/月
  - 用于: Claude Opus, Sonnet 等高端模型
  - 超出后: 可按 $0.13-0.26/request 购买额外
- ✅ 代码审查：支持（基础版本）
- ✅ Code Search：支持
- ✅ Knowledge Base：支持
- ❌ Spark：不支持

**陷阱特别提醒:**
> ⚠️ 每个 Premium Request 快速耗尽！
> 例: 用 Claude Opus 回答 50 个复杂问题
> → 6 个月内耗完全年额度
> → 被迫升级 Pro+ ($348/年额外成本)

**建议使用策略:**
- 主要用 GPT-5 Mini (无限)
- Opus/Sonnet 仅在必需时使用
- 监控 Premium Request 消耗速度

**适合人群:** 个人开发者、成本敏感用户、学习者

```
```---
```

#### **Pro+ 版本** ($39/月)

**可用模型列表:**
- 全部上述模型 + 优先级访问
- 所有最新模型首先体验权限
- Claude Opus 完整优先级
- OpenAI o1 系列（优先体验）

**功能与限制:**
- ✅ 代码补全：**无限制**
- ✅ Agent 模式：**无限制**
- ✅ Chat 对话：**无限制**
- ✅ Premium Requests：**1,500个/月**（5倍 Pro）
  - 相当于每个 Claude Opus 调用成本更低
  - 超延长 rate limit (能更频繁调用)
  - 超出后: 可按比例购买
- ✅ 代码审查：支持（高级）
- ✅ Code Search：支持（增强）
- ✅ Knowledge Base：支持（增强）
- ✅ **GitHub Spark**：**支持**（创建 AI 应用）
- ✅ 模型优先级：最高
- ✅ Agent 能力：最完整

**新增功能深度:**

**GitHub Spark**
- 创建全栈 AI 应用（JavaScript/HTML/CSS）
- 从自然语言生成完整应用
- 支持导出和分享
- 云端运行和托管支持

**Knowledge Base**
- 注入自定义知识到 AI 回复
- 支持文档、代码库、Markdown
- Pro+ 版本支持更大的知识库
- 增强了 Code Search 能力

```
```---
```

#### **Enterprise 版本** (自定义价格)

**完全定制化方案:**
- 所有功能 + 自定义
- 专属支持团队
- 审计日志完整
- 数据保留控制（可零数据保留）
- 按座位许可（灵活管理）
- 企业级 SLA
- 定制部署选项

**价格范围:**
- 通常 $22+ per user/month (与 Pro+ 相近)
- 取决于座位数和定制功能
- 需要联系销售

**适合:** 大型企业、特殊合规需求

```
```---
```

### 📊 模型使用限制详解

| 模型 | Free 中 | Pro 中 | Pro+ 中 | 限制类型 |
|------|--------|--------|--------|---------|
| GPT-5 Mini | ❌ | ✅ 无限 | ✅ 无限 | 仅限补全 |
| Claude Haiku | ❌ | ✅ 受限 | ✅ 受限 | Premium requests |
| Claude Sonnet | ❌ | ✅ 受限 | ✅ 受限 | Premium requests |
| Claude Opus | ❌ | ❌ | ✅ 受限 | Premium requests |
| GPT-5.4 | ❌ | ❌ | ✅ 受限 | Premium requests |

**关键:**
- Free/Pro 都用相同的 Premium Requests 池
- Pro+ 额度 5 倍，但所有高端模型共享
- 无模型差异化定价（都用 Premium Requests）

```
```---
```

### 支持平台

- ✅ VS Code (扩展)
- ✅ Visual Studio (扩展)
- ✅ JetBrains IDEs (插件)
- ✅ Neovim (插件)
- ✅ Xcode (扩展)
- ✅ GitHub.com (网页)
- ✅ Azure DevOps (支持)
- ✅ 命令行 (CLI)

```
```---
```

### 💡 GitHub Copilot 特色功能分析

**优点:**
1. 最便宜的付费方案（$10）
2. 最全的 GitHub 生态集成
3. 企业版功能完整
4. 政府/安全认证（FedRAMP）

**缺点:**
1. Premium Requests 额度容易耗尽
2. 模型共享池（无细粒度控制）
3. 成本不透明
4. 无法灵活选择轻量/重型模型

**成本预测:**
- Pro: $10 + 超额 = $10-30/月（取决于用量）
- Pro+: $39 + 超额 = $39-60+/月

```
```---
```

## 2. Cursor详细版

### 官方网址
https://cursor.com/pricing

### 💰 完整价格方案

| 方案 | 月度 | 说明 | API 额度 | 配额倍数 |
|------|------|------|--------|---------|
| **Hobby** | $0 | 免费体验 | 有限 | 1× (有日限) |
| **Pro** | $20 | 标准方案 | $20 MPM | 1× |
| **Pro+** | $60 | 推荐方案 | $70 MPM | 3× |
| **Ultra** | $200 | 企业方案 | $400 MPM | 20× |
| **Teams** | $40/user | 团队方案 | Pool | 共享 |

### 🤖 详细模型配置与 API 费率

#### **Hobby 版本（$0）**

**可用模型:**
- 有限的基础模型池

**功能与限制:**
- ⚠️ AI Agent 请求：有限（日/周刷新）
- ⚠️ Tab 补全：有限
- ❌ MCP 支持：不支持
- ❌ Cloud Agent：不支持
- ❌ 自定义指令：不支持
- 💡 试用场景：体验 IDE 和基础功能

```
```---
```

#### **Pro 版本** ($20/月) ⭐ 强烈推荐

**可用模型与 API 费率:**

| 模型 | 提供商 | Input ($/M) | Output ($/M) | 综合成本/K输入tokens |
|------|--------|-----------|------------|------------------|
| Claude Opus 4.6 | Anthropic | $5.00 | $25.00 | 非常高 |
| Claude Sonnet 4.5 | Anthropic | $3.00 | $15.00 | 高 |
| Claude Haiku 4.5 | Anthropic | $0.80 | $4.00 | 低 |
| GPT-5.4 | OpenAI | $2.50 | $15.00 | 中高 |
| GPT-4 Turbo | OpenAI | $1.00 | $3.00 | 低 |
| Gemini 3.1 Pro | Google | $2.00 | $12.00 | 中高 |
| Grok 3 | xAI | $2.00 | $6.00 | 中 |
| **Composer 2** | **Cursor专属** | **$0.50** | **$2.50** | **最低** |

**Monthly Allocation:**
- 基础: $20/月 API 额度
- 不支持超额购买（Pro）
- 建议: 每月约 2-3M tokens 输入量
- 实际可用token数: 约 20,000 completion calls

**功能与限制:**
- ✅ Tab 补全：**无限制**
- ✅ AI Agent 请求：扩展配额
- ✅ MCP 支持：**支持**（Model Context Protocol）
- ✅ Cloud Agent：**支持**（自动执行任务）
- ✅ 自定义指令：支持
- ✅ 所有模型可用：全面
- ✅ 模型切换：自由切换（按 token 成本计费）

**使用策略:**
```
简单任务 (文件名、代码片段)  → Composer 2 ($0.5 input)
中等任务 (函数、类、小段代码) → Claude Sonnet ($3 input)
复杂任务 (大段重构、架构设计) → Claude Opus ($5 input)
速度优先 (快速生成)           → GPT-4 Turbo ($1 input)
```

**成本示例:**
- 10次 Sonnet 调用 (1000 tokens input)
  → $3 × 1 = $3
- 消耗 15% 月度预算

```
```---
```

#### **Pro+ 版本** ($60/月) ⭐⭐ **推荐**

**Monthly Allocation:**
- $70/月 API 额度
- **3× 配额倍数**应用于所有模型的 input/output
- 相当于: 额度用完后的速率限制 3 倍宽松

**实际效果:**
- 月度约 6-9M tokens 输入
- 约 60-90K completion calls
- 模型组合最优费率下: ~600-900 个复杂任务

**新增功能:**
- ✅ 优先级队列（Agent 执行优先）
- ✅ 更高的速率限制
- ✅ 专属支持通道
- ✅ 新功能 beta 体验

**适合:**
- 日常开发、频繁使用 AI Agent
- 需要模型灵活切换
- 成本控制在 $60-100 范围内

```
```---
```

#### **Ultra 版本** ($200/月)

**Monthly Allocation:**
- $400/月 API 额度（基础）
- **20× 配额倍数**
- 相当于无日限制的使用体验
- 可支持 20-30M tokens 输入/月

**功能:**
- ✅ 所有功能完整
- ✅ 最高优先级
- ✅ 新功能优先体验
- ✅ 无限制 Agent 执行
- ✅ 专属支持团队
- ✅ 不用担心超额

**适合:**
- 企业级使用
- 24/7 AI 驱动开发
- 多个AI Agent 并发执行
- 不关心成本，追求性能

```
```---
```

#### **Teams 方案** ($40/user/月)

**共享团队模式:**
- 所有用户共享计费池
- 成员级的使用统计
- RBAC (Role-Based Access Control)
- 共享自定义指令

**计费模式:**
- $40 × 成员数 = 团队月度费用
- 共享 API 配额池
- 按团队整体消耗计费

**企业特性:**
- ✅ 团队管理界面
- ✅ 审计日志（基础）
- ✅ 零数据保留（隐私）
- ✅ 分析报告
- ✅ 优先支持

**适合:**
- 初创团队（3-20人）
- 需要协作和成本透明
- 重视隐私保护

```
```---
```

#### **Enterprise 方案** (定制价格)

**完全定制化:**
- 定制配额和功能
- 企业级 SLA
- 架构咨询
- 专属团队
- 定制部署选项
- VPC/内网支持

**通常价格:**
- $50-100+ per user/month (取决于配置)
- 最低购买数量通常 5-10 用户
- 需要销售咨询

```
```---
```

### 📊 Cursor 模型成本对比

**成本效率排名** (按 output token 计费):

```
最便宜: Composer 2      $2.50/M (仅 Cursor)
        GPT-4 Turbo    $3.00/M
        Haiku          $4.00/M
中等:   Grok           $6.00/M
        Gemini Pro     $12.00/M
        Sonnet 4.5     $15.00/M
        GPT-5.4        $15.00/M
最贵:   Opus 4.6       $25.00/M (10倍最便宜!)
```

**选择建议:**
- **成本优化**: Composer 2 > Haiku > Sonnet (性价比)
- **速度优化**: GPT-4 Turbo > Grok > Gemini
- **质量优化**: Opus > Sonnet (最强代码能力)
- **平衡选择**: Claude Sonnet (大多数场景最佳)

```
```---
```

### 支持平台
- ✅ Cursor 原生 IDE (完整功能)
- ✅ VS Code (兼容扩展)
- ✅ 跨平台: Windows, macOS, Linux

### 💡 Cursor 特色分析

**核心优势:**
1. **最透明的定价** - 每个模型的 API 费率清晰
2. **最多的模型** - 7+ 个第一方 AI 模型
3. **最灵活的选择** - 按 token 计费，可精确成本控制
4. **最好的 Agent** - Composer 和 MCP 支持最完整
5. **最优的成本/性能** - Composer 2 费率独家优惠

**缺点:**
1. 是新的 IDE，需要学习曲线
2. 生态还在建设中
3. 无原生 Git 集成（需插件）

**成本预测:**
- Pro: $20-50/月（取决于模型选择）
- Pro+: $60-100/月
- Ultra: $200+ 固定

```
```---
```

## 3. Claude Code详细版

### 官方网址
https://claude.com/product/claude-code

### 💰 完整价格方案

| 方案 | 月度 | 年度折扣 | 使用配额 | 对象 |
|------|------|--------|--------|------|
| **Free** | $0 | 免费 | Web 仅 Chat| 学生、试用 |
| **Pro** | $20 | $200/年 | 更多使用 | 个人开发者 |
| **Max 5x** | $100 | - | 5× Pro | 专业团队 |
| **Max 20x** | $200 | - | 20× Pro | 企业级 |

### 🤖 详细模型配置

#### **Free 版本** ($0)

**可用模型:**
- Claude Haiku 4.5 (受限)
- Claude Sonnet 4.5 (受限)

**功能与限制:**
- ✅ Web 版 Chat：支持
- ❌ **Claude Code**: 不支持（仅 Pro+ 起始）
- ❌ Desktop 应用：不支持
- ❌ IDE/CLI：不支持
- ✅ Projects：不支持（无项目保存）
- ✅ Memory：支持（跨会话记忆）
- ✅ Artifacts：支持（代码预览）
- ⚠️ 使用限制：受限配额

**适合:**
- 学生、评估、轻度使用
- 仅需 Chat 功能，不需代码编辑

```
```---
```

#### **Pro 版本** ($20/月) ⭐ 推荐入门

**可用模型:**
- Claude Opus 4.6
- Claude Sonnet 4.5
- Claude Haiku 4.5

**模型切换成本:**

| 模型 | 相对成本 | 说明 |
|------|--------|------|
| Haiku | 最低 | 快速任务 |
| Sonnet | 中等 | 平衡 |
| Opus | 最高 | 复杂任务 |

> ⚠️ **成本比例不公开！**
> 推测: Opus > Sonnet > Haiku (基于 API 比例)
> 实际倍数: 可能 5-10 倍差异

**功能与限制:**
- ✅ **Claude Code**: **支持**（关键！）
- ✅ Desktop 应用：支持
- ✅ IDE 插件：支持 (VS Code, JetBrains)
- ✅ CLI/Terminal：支持
- ✅ Projects：**无限制**（保存历史）
- ✅ Artifacts：支持（代码预览）
- ✅ Memory：支持（完整）
- ✅ Team 功能：支持（邀请团队成员）
- ⚠️ 使用限制：**"More Usage"** (具体数字不公开)
- ❌ 优先级访问：不支持
- ❌ 企业功能：不支持

**Claude Code 深度:**

Claude Code 功能包括:
- **多文件编辑** - 在同一个对话中编辑多个文件
- **实时预览** - 看到代码变化的实时效果
- **Git 管理** - 提交代码到 Git (GitHub/GitLab)
- **自动 PR** - 自动创建 Pull Request
- **Codebase 理解** - 上传整个 codebase 学习
- **快速上手** - 新 repo 快速理解

**推荐使用场景:**
- 小到中型项目重构
- 单个或多个相关文件修改
- 需要 Git 集成的工作流

```
```---
```

#### **Max 5x 版本** ($100/月)

**可用模型:**
- 同上（Opus, Sonnet, Haiku）

**功能与限制:**
- ✅ Claude Code：**完整支持**
- ✅ 使用配额：**5× Pro** 用量
- ✅ 高优先级访问：**是**（更快响应）
- ✅ Team 功能：**完整**
- ✅ Enterprise 功能：**支持基础版本**
  - SSO 基础支持
  - 审计日志（基础）
  - 数据保留控制（基础）

**适合:**
- 小型团队 (3-10人)
- 重度 Claude Code 使用者
- 需要团队协作和权限管理

```
```---
```

#### **Max 20x 版本** ($200/月) ⭐ 企业级

**可用模型:**
- 同上（完整访问）

**功能与限制:**
- ✅ Claude Code：**完整优化**
- ✅ 使用配额：**20× Pro 用量**
- ✅ 高优先级访问：**最高级**（VIP 通道）
- ✅ Team 功能：**企业级完整**
- ✅ **Enterprise 功能: 完整**
  - SSO (Single Sign-On) 完整支持
  - SCIM 席位管理
  - 审计日志（详细）
  - 数据保留控制（完全）
  - **HIPAA 合规**（医疗行业）
  - **SOC 2 Type II**
  - **GDPR 合规**

**特殊功能:**
- Org-wide Memory（跨团队记忆）
- Custom Instructions（组织级指令）
- Fine-grained Permissions（细粒度权限）
- Usage Analytics（详细分析）

**适合:**
- 大型企业（50+ 人）
- 医疗、金融、政府机构
- 对合规性有严格要求
- 全天候 AI 驱动开发

```
```---
```

### 📊 Claude Code 模型配置

| 模型 | Free | Pro | Max 5x | Max 20x | 相对费率 |
|------|------|-----|--------|----------|---------|
| Opus 4.6 | ❌ | ✅ | ✅ | ✅ | 100 |
| Sonnet 4.5 | ✅* | ✅ | ✅ | ✅ | 60 |
| Haiku 4.5 | ✅* | ✅ | ✅ | ✅ | 10 |

*Free: 受限配额

**关键问题:**
- ⚠️ 不同模型是否消耗不同额度？
  - 推测: 是的 (Opus > Sonnet > Haiku)
  - 官方: 未明确说明
  - 建议: 保守假设 Opus 成本 10 倍 Haiku

```
```---
```

### 支持平台
- ✅ Claude.ai (Web)
- ✅ Claude Desktop (macOS, Windows, Linux)
- ✅ IDE 插件 (VS Code, JetBrains)
- ✅ CLI (terminal)
- ✅ GitHub/GitLab 集成

### 💡 Claude Code 特色分析

**核心优势:**
1. **代码编辑体验最好** - 多文件编辑最流畅
2. **Opus 4.6 能力最强** - 代码生成质量最高
3. **企业合规最完整** - HIPAA/SOC2/GDPR 支持
4. **Git 集成最原生** - 自动 PR 创建
5. **Codebase 理解最深** - 快速学习整个项目

**缺点:**
1. **成本不透明** - 无法精确计算模型成本
2. **有时间配额限制** - 即使付费也受限
3. **模型选择有限** - 仅 Claude 系列
4. **生态不如 GitHub** - 不如 GitHub Copilot 的集成

**成本预测:**
- Pro: $20-50/月（取决于 Opus 使用率）
- Max 5x: $100+ (如果经常用 Opus)
- Max 20x: $200+ 固定

**实际成本例子:**
假设 Opus 比 Haiku 贵 10 倍:
- Pro: 如果每月 20% 用 Opus，80% 用 Haiku
  - 成本指数 = 0.2×10 + 0.8×1 = 2.8
  - 实际月成本估计: $20 × 2.8 = $56/月

```
```---
```

## 4. Windsurf详细版

### 官方网址
https://windsurf.com/pricing

### 💰 完整价格方案

| 方案 | 月度 | API 计费 | Cascade | 日/周限制 | 配额倍数 |
|------|------|--------|---------|---------|---------|
| **Free** | $0 | - | Light | 严格 | 1× |
| **Pro** | $20 | API价格 | Standard | 有 | 1× |
| **Max** | $200 | API价格 | Heavy | ❌ 无 | 1× |
| **Teams** | $40/user | Pool | Standard | 有 | 1× |

### 🤖 详细模型配置

#### **Free 版本** ($0)

**可用模型:**
- 有限的基础模型池
- Claude, GPT, Gemini (精选)

**功能与限制:**
- ✅ Tab 补全：无限制
- ✅ Cascade Agent：Light 配额
- ⚠️ 日/周 Cascade 限制：**严格刷新**
- ❌ MCP 支持：不支持
- ❌ 高级功能：受限
- ⚠️ 数据保留：可能保留

**适合:**
- 体验阶段、学习 IDE

```
```---
```

#### **Pro 版本** ($20/月) ⭐ **最值得买**

**可用模型与 API 费率:**

所有主流模型：
- **Claude 系列** (Anthropic)
  - Claude Opus 4.6: $5 input / $25 output
  - Claude Sonnet 4.5: $3 input / $15 output
  - Claude Haiku 4.5: $0.80 input / $4 output

- **OpenAI 系列**
  - GPT-5.4: $2.50 input / $15 output
  - GPT-5.3: $2.00 input / $12 output
  - GPT-4 Turbo: $1 input / $3 output
  - GPT-4o: $0.15 input / $0.6 output

- **Google Gemini 系列**
  - Gemini 3.1 Pro: $2 input / $12 output
  - Gemini 2.0: 不同的费率

- **Windsurf 专属**
  - **SWE-1.5**: Cascade Agent 专用，基于 Claude，极强的代码生成

- **xAI**
  - Grok 系列：$2-3 范围

**API 计费方式:**
- 完全直通 OpenAI/Anthropic/Google 官方 API 价格
- Pro 和 Max 版本用同样的费率
- 不同之处：配额上限和日限制

**功能与限制:**
- ✅ Tab 补全：**无限制**
- ✅ Cascade Agent：**Standard 配额**
- ✅ MCP 支持：**支持**（可扩展）
- ✅ Web 预览：支持
- ✅ 部署支持：支持
- ⚠️ **日限制**: 仍然存在～ 需要等待日期刷新
- ✅ **零数据保留**: 隐私优先（Windsurf 承诺）
- ✅ API 价格直通：使用量≈API 费用

**Cascade Agent 详解:**
- 自主规划和执行任务
- 支持多步骤工作流
- 可以执行 CLI 命令
- 可以创建和修改文件
- 基于 SWE-1.5 模型（内部优化）
- Standard 配额: ~50-100 个 Agent 执行/月（推测）

**推荐使用场景:**
```
小型任务 (文件名、类定义)    → GPT-4o ($0.15 input) 最便宜
中等任务 (函数、模块)        → Claude Sonnet ($3 input)
复杂任务 (大段重构、架构)    → Claude Opus ($5 input)
速度优先 (快速迭代)         → GPT-5.4 ($2.50 input)
Agent 自动化任务            → SWE-1.5 (已内含)
```

**成本示例:**
- 10 个 Sonnet 调用 (1000 tokens input)
  → $3 × 1 = $3
- 消耗 15% 月度预算

```
```---
```

#### **Max 版本** ($200/月) ⭐⭐ **推荐**

**可用模型:**
- 同 Pro（全部模型）
- 优先体验新模型

**功能与限制:**
- ✅ Tab 补全：**无限制**
- ✅ Cascade Agent：**Heavy 配额**
- ✅ MCP 支持：**完整**
- ✅ Web 预览、部署：**完整**
- ✅ **日/周限制: 移除** ✅✅✅
  - 最大改进！
  - 无需等待日期刷新
  - 可无限尝试 Cascade
- ✅ **零数据保留**: 同 Pro
- ✅ API 价格直通：使用量自由

**Cascade Heavy:**
- Heavy 配额推测: ~500-1000 个 Agent/月
- 等于日均 15-30 个 Agent 执行
- 足够重度使用

**额外优势:**
- ✅ 可选购买额外配额
- ✅ Cascade 无日限制
- ✅ 支持背对背 Agent（连续执行）
- ✅ 企业级稳定性

```
```---
```

#### **Teams 方案** ($40/user/月)

**团队计费模式:**
- $40 × 成员数（按月计费）
- 共享 API 配额池
- 按团队整体消耗计费

**功能:**
- ✅ 所有 Pro 功能
- ✅ 团队管理界面
- ✅ 分析报告（团队级）
- ✅ 共享自定义指令
- ✅ RBAC (基础)
- ✅ **零数据保留**（隐私）
- ✅ 优先支持

**适合:**
- 初创团队 (3-20人)
- 需要成本透明和协作
- 隐私优先的团队

```
```---
```

#### **Enterprise 方案** (定制价格)

**完全定制化:**
- 定制配额和功能
- 企业级支持
- 混合部署选项
- VPC/内网支持
- SSO, RBAC, 审计日志
- 定制 SLA

**通常价格:**
- $50-100+ per user/month (取决于配置)
- 最低购买数量: 5-10 users
- 需要销售咨询

```
```---
```

### 📊 Windsurf 总成本分析

**关键特点:**
- **API 价格直通**: 没有额外标记
- **Pro vs Max 区别**:
  - Pro: 有日限制，$20 月度
  - Max: **无日限制**, $200 月度
  - 费率相同，但 Max 用量不受日限制

**成本估计:**
- 轻度使用 (20K tokens/月): $0.30-1 (Free)
- 中等使用 (500K tokens/月): $1-3 (Pro)
- 重度使用 (5M+ tokens/月): $5-20 (Pro) 或 $200 fixed (Max)

**何时选择 Pro vs Max:**
```
选 Pro ($20) 如果:
  - 月均 <1M tokens
  - 可接受日限制
  - 成本最优
  
选 Max ($200) 如果:
  - 月均 >5M tokens
  - 无法接受日限制
  - 24/7 Agent 执行需求
  - 固定成本心理舒适
```

```
```---
```

### 支持平台
- ✅ Windsurf 原生 IDE (完整功能)
- ✅ 跨平台: Windows, macOS, Linux
- ✅ VS Code 兼容扩展 (即将)

### 💡 Windsurf 特色分析

**核心优势:**
1. **最性价比** - $20 全模型访问
2. **Cascade Agent 最强** - 基于 SWE-1.5，代码能力顶级
3. **隐私优先** - 零数据保留政策
4. **API 价格透明** - 直通官方价格，无额外加价
5. **无日限制** (Max 版本) - 完全无忧使用

**缺点:**
1. 是新的 IDE，学习曲线少
2. 生态还在建设中
3. 企业功能相对较少

**成本预测:**
- Pro: $20 + API 费用 = $25-50/月（取决于用量）
- Max: $200 固定成本，无需担心超额

```
```---
```

## 5. JetBrains AI详细版

### 官方网址
https://www.jetbrains.com/ai-ides/buy

### 💰 完整价格方案

| 方案 | 月度 (USD) | 年度 (USD) | 原价 (JPY) | AI Credits |
|------|-----------|-----------|-----------|------------|
| **AI Free** | $0 | 免费 | 免费 | 3/月 |
| **AI Pro** | $9.66 | $115.92 | ¥14,000/年 | 10/月 |
| **AI Ultimate** | $28.98 | $347.76 | ¥42,000/年 | 35/月 |
| **AI Enterprise** | $55.44+ | 定制 | ¥100,800+/年 | 自定义 |

> 价格常年波动，特别是日元版本。建议查看官网最新价格。

### 🤖 详细模型配置

#### **AI Free 版本**

**可用模型:**
- Claude (受限)
- OpenAI GPT (受限)
- JetBrains Mellum (自研代码优化模型)

**功能与限制:**
- ✅ 代码补全：**本地 AI 模式** (隐私优先)
- ✅ AI Chat：支持（Local）
- ⚠️ AI Credits: **3个/30天**
- ❌ Cloud 补全：不支持
- ❌ Next Edit Suggestions：不支持
- ❌ Junie Agent：不支持
- ✅ 完整功能：仅限 Community/Free IDE 版本

**本地 AI 优势:**
- 完全隐私（不送到云端）
- 完全离线可用
- 不需要 API 密钥
- 适用于敏感代码

**缺点:**
- 模型能力受限 (较小的本地模型)
- 学习曲线高

```
```---
```

#### **AI Pro 版本** ($9.66/月) ⭐ **最便宜付费**

**可用模型与消耗:**

| 模型 | 提供商 | 消耗费用 | 说明 |
|------|--------|--------|------|
| Claude 3.5 Sonnet | Anthropic | Per API 调用 | 代码最优 |
| Claude 3.5 Haiku | Anthropic | Per API 调用 | 最快 |
| GPT-4 Turbo | OpenAI | Per API 调用 | 多用途 |
| Mellum (自研) | JetBrains | 免费 | 代码优化 |

**AI Credits 说明:**
- 10 个 /30天
- 1 个 Credit = 1 次 Chat 对话 (长度不限)
- 代码补全**不消耗** Credits
- 🟢 **代码补全: 无限制!**

**功能与限制:**
- ✅ 代码补全：**Cloud 模式，无限制**
- ✅ AI Chat：支持 (10 次/月)
- ✅ Next Edit Suggestions：**支持** (预测下一步编辑)
- ✅ Junie (AI Agent)：**试用版本** (需额外购买)
- ✅ BYOK (Bring Your Own Key)：**支持**
- ✅ 本地 LLM 支持：仅 Enterprise
- ⚠️ 包含于 IDE 订阅：需购买 IDE License

**使用策略:**
```
代码补全使用    → 无限使用 (不消耗 Credits)
复杂问询/设计   → 保留 10 个 Credits/月
快速检查/修复   → 使用 Credits
```

```
```---
```

#### **AI Ultimate 版本** ($28.98/月) ⭐⭐ **推荐**

**可用模型:**
- 同 Pro（全部模型）
- 优先访问新模型

**AI Credits:**
- **35 个 /30天** (3.5倍 Pro)
- 足够日常全部 Chat 需求

**功能与限制:**
- ✅ 代码补全：**Cloud 无限制**
- ✅ AI Chat：支持 (35 次/月)
- ✅ Next Edit Suggestions：**完整** (高频使用)
- ✅ Junie Agent：**完整功能**
  - 自主规划和执行
  - 跨文件修改
  - CLI 命令执行
  - Git 操作支持
- ✅ BYOK：完整支持
- ✅ 本地 LLM：仅 Enterprise，但可自配置 (Ollama 等)
- ✅ 多 LLM 支持：支持多个 API key 配置

**Junie Agent 深度:**
- **规划**: 自动分解任务
- **执行**: 并行执行多个步骤
- **验证**: 自动测试修改
- **迭代**: 失败自动重试

```
```---
```

#### **AI Enterprise 版本** (定制 $55.44+/月)

**完全定制化:**
- 自定义 AI Credits
- 企业级支持
- 架构咨询
- 内网部署支持
- 本地 LLM 完整支持
- VPC 隔离
- SAML SSO
- 审计日志
- 自定义 SLA

**主要功能:**
- 所有 Ultimate 功能 + 企业级
- 可部署本地 AI 模型
- 完全的数据隐私控制

```
```---
```

### 📊 JetBrains AI 成本分析

**关键特点:**
1. **代码补全无限** - 最重要的功能无限制
2. **与 IDE 绑定** - 需要购买 IDE 订阅
3. **成本不透明** - 无法单独查看模型成本
4. **企业友好** - 本地部署、隐私控制最好

**总成本计算:**
```
AI Pro ($9.66) + IDE License (~$17-20 for JB All Products) 
= ~$26-30/月

或: 
AI Ultimate ($28.98) + IDE License
= ~$46-50/月
```

```
```---
```

### 支持IDE产品
- ✅ IntelliJ IDEA Ultimate ⭐ (主要)
- ✅ PyCharm Pro ⭐ (Python首选)
- ✅ WebStorm (JavaScript首选)
- ✅ GoLand (Golang)
- ✅ PhpStorm (PHP)
- ✅ RubyMine (Ruby)
- ✅ RustRover (Rust)
- ✅ Rider (C#/.NET)
- ✅ Android Studio (Android)
- ✅ VS Code (Preview, 有限)
- ✅ Fleet (新 IDE, 实验中)

### 💡 JetBrains AI 特色分析

**核心优势:**
1. **代码补全完全无限** - 不消耗 Credits
2. **IDE 集成最深** - 与 JB IDE 原生集成
3. **本地 AI 支持** - Enterprise 完整支持
4. **企业功能最完整** - RBAC, SSO, 审计
5. **BYOK 最灵活** - 支持自带 API key
6. **隐私最好** - 本地部署选项

**缺点:**
1. **与 IDE 绑定** - AI 成本难以单独评估
2. **模型支持有限** - 仅 Claude/GPT (无 Gemini/Grok)
3. **前端成本高** - IDE license 必须
4. **成本不透明** - 无法精确预测超额

**成本预测:**
- Pro: $10 (AI) + $17 (IDE) = ~$27/月
- Ultimate: $29 (AI) + $17 (IDE) = ~$46/月

```
```---
```

## 6. Amazon Q Developer详细版

### 官方网址
https://aws.amazon.com/q/developer/pricing/

### 💰 完整价格方案

| 方案 | 费用 | 说明 | 代码补全 |
|------|------|------|---------|
| **Q for Developers Free** | $0 | 永久免费 | 无限制 |
| **Q for Developers Pro** | 按 token | 超过免费限额 | 超额付费 |
| **Q for Business Lite** | $3/user/月 | 企业 Q&A | 权限感知 |
| **Q for Business Pro** | $20/user/月 | 企业完整 | 权限感知 |

### 🤖 详细模型配置

#### **Q for Developers Free 版本** ($0)

**可用模型:**
- Claude 3.5 Sonnet (最新)

**代码补全:**
- ✅ **无限制** ✅✅✅
- 永久免费
- 无需 AWS 账户（VS Code 插件可用）

**Agent Mode:**
- ⚠️ **50个 Agent 请求/月** (受限)
- 用于自动执行任务
- 超出后: 需付费

**代码转换:**
- ⚠️ **1,000 LOC/月** (免费额度)
- 用于 Java/JavaScript 代码转换
- 转换超出额度: $0.003 per LOC

**其他功能:**
- ❌ 企业级功能：不支持
- ❌ IAM 身份管理：不支持
- ❌ 代码索引：有限
- ❌ IP 赔偿：不支持

**支持IDE:**
- ✅ VS Code
- ✅ JetBrains (部分)
- ✅ Visual Studio
- ✅ Eclipse
- ✅ CLI
- ✅ GitHub/GitLab Webhooks

**最佳用途:**
- 个人开发者，无需企业功能
- 代码补全为主
- 不需要权限感知

```
```---
```

#### **Q for Developers Pro** (按量计费)

**计费模式:**
- 超过 Free 限额后，按 token 计费
- 需要有 AWS 账户和支付方式
- 估计: $0.01-0.03 per 1K tokens (based on Claude API)

**功能:**
- ✅ 代码补全：无限制 (按量计费)
- ✅ Agent Mode：无限制
- ✅ 代码转换：无限制 (按 LOC 计费)
- ❌ Enterprise 功能：不支持

```
```---
```

#### **Q for Business Lite** ($3/user/月)

**权限感知 AI** (关键特色!):
- ✅ 回复受用户权限限制
- 例: 用户无权访问的代码库，Q 也看不到
- 符合企业数据治理

**功能:**
- ✅ 企业 Q&A：支持
- ✅ 代码补全：支持
- ✅ 权限感知：**完整**
- ✅ Web 应用：支持
- ✅ Web 体验导出：支持

**不包含:**
- ❌ 代码索引：Lite 版本无
- ❌ Team 管理：有限
- ❌ 审计日志：有限

**适合:**
- 小型团队 (10-50人)
- 成本优先
- 基础权限感知即可

```
```---
```

#### **Q for Business Pro** ($20/user/月) ⭐ **推荐企业**

**完整企业功能:**
- ✅ 权限感知：**完整**
- ✅ 代码索引：**支持** (学习整个 codebase)
- ✅ 连接器：数据库、Wiki、Slack 等
- ✅ 细粒度权限：基于 IAM

**企业级特性:**
- ✅ SSO (SAML 2.0)
- ✅ 审计日志：**详细**
- ✅ 用户管理：RBAC
- ✅ API：企业 API 访问
- ✅ 团队管理：完整支持
- ✅ 数据隔离：独立索引

**特殊功能:**
- **Document Indexing**：索引 Confluence, Sharepoint 等
- **Data Connectors**：连接自有系统
- **Knowledge Base**：构建企业知识库
- **Custom Web Experience**：白标定制

**支持:**
- ✅ Email 支持
- ✅ 电话支持
- ✅ 架构咨询

**适合:**
- 大型企业 (100+ 人)
- 需要完整权限感知
- 对合规性有要求
- 需要代码知识库

```
```---
```

### 📊 Amazon Q 成本分析

**关键特点:**
1. **代码补全永久免费** - 无限制无付费
2. **权限感知独特** - 其他编辑器都不支持
3. **AWS 生态最优** - IAM 集成最紧密
4. **代码转换能力强** - Java/JS 转换费率合理

**成本模型:**
```
个人开发者:
  → Free ($0) 永久
  → 如需超过 50 agent/月，升级 Pro (按量)

小型企业 (10-50人):
  → Q Business Lite ($3/user/月) ⭐
  → 含权限感知 = $30-150/月 (10-50人)

大型企业 (100+ 人):
  → Q Business Pro ($20/user/月) = $2000+/月
  → 含完整企业功能
```

**其他成本:**
```
代码转换费用（Base Free Limit）:
  Free:    1,000 LOC/月免费
  Pro:     4,000 LOC/月免费
  超出:    $0.003 per LOC

例: 月转换 10,000 LOC
    = (10,000 - 4,000) × $0.003
    = $18 额外成本
```

```
```---
```

### 支持平台
- ✅ VS Code (扩展) - 最好体验
- ✅ JetBrains IDEs (插件)
- ✅ Visual Studio (扩展)
- ✅ Eclipse (插件)
- ✅ AWS Console (集成)
- ✅ GitHub (Webhook)
- ✅ GitLab (Webhook)
- ✅ Slack (集成)
- ✅ Microsoft Teams (集成)

### 💡 Amazon Q 特色分析

**核心优势:**
1. **代码补全永久免费** - 无限制！
2. **权限感知独家** - 企业数据治理必需
3. **AWS 生态最紧** - IAM 无缝集成
4. **代码转换能力** - Java/JS 转换市场最强
5. **企业合规最完** - HIPAA, SOC2, 审计完整

**缺点:**
1. **模型选择少** - 仅 Claude (与 Anthropic 合作)
2. **中小企业成本高** - Lite $3/user 还是贵
3. **不如 GitHub/Cursor** - 多语言支持较少
4. **AWS 锁定** - 与 AWS 生态紧密绑定

**成本预测:**
- 个人: $0 (Free)
- 小企业: $30-150/月 (Lite)
- 大企业: $2000+/月 (Pro)

```
```---
```

# 📊 完整功能矩阵

## 全功能对比表

### 基础功能对比

| 功能 | GitHub Pro | Cursor Pro | Claude Code Pro | Windsurf Pro | JetBrains Pro | Amazon Free |
|------|:----------:|:----------:|:---------------:|:------------:|:-------------:|:----------:|
| **代码补全** | ✅ 无限 | ✅ 无限 | ✅ 无限 | ✅ 无限 | ✅ 无限 | ✅ 无限 |
| **Chat 对话** | ✅ 无限* | ✅ 无限* | ✅受限 | ✅ 无限* | ✅ 10/月 | ✅ 50 Agent/月 |
| **代码生成** | ✅ 完整 | ✅ 完整 | ✅ 完整 | ✅ 完整 | ✅ 完整 | ✅ 完整 |
| **Agent Mode** | ✅ 无限* | ✅ 无限* | ❌ | ✅ 无限* | ✅ 试用版 | ✅ 50/月 |
| **代码审查** | ✅ 是 | ✅ 内置 | ✅ 内置 | ✅ 内置 | ✅ 可选 | ✅ 可选 |
| **多文件编辑** | ✅ Pro+起 | ✅ 是 | ✅ 是 | ✅ 是 | ✅ 是 | ✅ 是 |
| **Git 集成** | ✅ 深度 | ⚠️ 基础 | ✅ 完整 | ⚠️ 基础 | ✅ 完整 | ✅ Webhook |
| **快速原型** | ✅ Spark | ✅ 内置 | ✅ 内置 | ✅ 内置 | ❌ | ⚠️ 部分 |

*受速率限制或配额限制

```
```---
```

### 模型支持对比

| 编辑器 | Claude 品系 | GPT 品系 | Gemini | 专有模型 | 模型数量 | 成本透明度 |
|--------|:----------:|:--------:|:-------:|:------:|:-----:|:-------:|
| **GitHub Copilot** | ✅ Opus/Sonnet | ✅ GPT-5.x | ❌ | N/A | 4+ | 🟡 低 |
| **Cursor** | ✅ 全系 | ✅ 全系 | ✅ 3.1 | Composer2 | 7+ | ✅ 高 |
| **Claude Code** | ✅ Opus/Sonnet/Haiku | ❌ | ❌ | ❌ | 3 | 🟡 低 |
| **Windsurf** | ✅ 全系 | ✅ 全系 | ✅ 全系 | SWE1.5 | 8+ | ✅ 高 |
| **JetBrains** | ✅ Sonnet/Haiku | ✅ GPT-4 | ❌ | Mellum | 3+ | 🟡 低 |
| **Amazon Q** | ✅ Sonnet | ❌ | ❌ | ❌ | 1 | 🟡 中 |

```
```---
```

### 企业功能对比

| 功能 | GitHub Enterprise | Cursor Teams | Windsurf Enterprise | Amazon Q Pro | JetBrains Enterprise |
|-----|:--:|:--:|:--:|:--:|:--:|
| **SSO/SAML** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **RBAC** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **审计日志** | ✅ 完整 | ✅ | ⚠️ 基础 | ✅ 详细 | ✅ 完整 |
| **权限感知** | ❌ | ❌ | ❌ | ✅ **独家** | ⚠️ 部分 |
| **本地部署** | ❌ | ❌ | ❌ | ⚠️ | ✅ |
| **数据隔离** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **HIPAA 合规** | ❌ | ❌ | ❌ | ✅ | ⚠️ |
| **GDPR 合规** | ✅ | ✅ | ✅ | ✅ | ✅ |

```
```---
```

# 模型支持与成本分析

## 模型切换成本分析

### GitHub Copilot - ⚠️ 有差异

**规则:**
- GPT-5 Mini: 无限制使用
- Opus/Sonnet: 消耗 Premium Requests (300/月 Pro)

**切换成本:**
```
Mini → Opus:   🟠 显著增加 (无限 → 有限)
Opus ↔ Sonnet: 🟢 相同成本 (同属 Premium)
```

**用户影响:**
- 无法根据难度灵活选择模型
- 倾向强制使用轻量模型以保守 requests
- 实际限制了模型选择自由

```
```---
```

### Cursor - ✅ 完全透明

**规则:**
- 按百万 tokens 计费
- 每个模型有明确的 input/output 费率

**切换成本对比:**
```
Opus (5 input)  →  Sonnet (3 input):  节省 40%
Sonnet (3)      →  Composer2 (0.5):   节省 83% ✅
Sonnet (15 out) →  Haiku (4 out):     节省 73% ✅
```

**用户体验:**
- 完全可控
- 可根据任务难度动态选择
- 可精确预测成本

```
```---
```

### Windsurf - ✅ API 价格直通

**规则:**
- 直通 OpenAI/Anthropic/Google 官方 API 价格
- Max/Pro 版本费率相同
- 区别仅在日限制

**切换成本:**
```
Pro ($20) → Max ($200):
  - 费率 = 费率 (不变!)
  - 区别 = 移除日限制，足够配额
  - 适合重度用户
```

```
```---
```

### Claude Code - ⚠️ 不透明

**规则:**
- 所有模型共享"More Usage"额度
- 具体切换成本不公开

**推测:**
```
假设 Opus 比 Haiku 贵 10 倍:
  Pro: 如果月均 20% Opus 用量
     → 成本指数 = 0.2×10 + 0.8×1 = 2.8
     → 实际月成本 ≈ $20 × 2.8 = $56/月
```

```
```---
```

### JetBrains - ⚠️ 完全不透明

**规则:**
- 模型切换成本与 IDE 订阅混在一起
- 无法单独计算

**建议:**
- 企业: 协商 Enterprise 合同获得透明定价
- 个人: 改用 Cursor

```
```---
```

### Amazon Q - 🟢 标准 token 计费

**规则:**
- 按 Claude API 的标准 token 计费
- Free: 50 agent/月免费
- Pro: 所有 agent 无限，超过后按量计费

```
```---
```

## 月度成本预测模型

### 轻度使用者 (<100 完成/月)

```
GitHub Copilot Pro: 
  $10 (固定) + 少量超额 
  = $10-15/月 ✅ 最便宜

Cursor Pro:
  $20 + 少量 API ($5-10)
  = $25-30/月

Windsurf Pro:
  $20 + 少量 API ($2-5)
  = $22-25/月 (接近 GitHub)

Amazon Q Free:
  $0 ✅ 完全免费

注意: GitHub 便宜，但模型选择受限
```

### 中度使用者 (500-2000 完成/月)

```
GitHub Copilot Pro:
  $10 (固定) + Premium Requests 超额 = $20-40/月
  ⚠️ 危险: 可能升级 Pro+ ($39)

Cursor Pro:
  $20 + 中等 API ($30-50)
  = $50-70/月 ✅ 成本可控

Windsurf Pro:
  $20 + 中等 API ($20-40)
  = $40-60/月 ✅ 性价比最优

Claude Code Pro:
  $20 + 中等用量 ($30-50 估计)
  = $50-70/月

JetBrains Pro + IDE:
  $10 (AI) + $17 (IDE) + 超额
  = $27-40/月 ✅ 便宜但受限

Amazon Q Free:
  $0 (代码补全) + $0 (50 agent)
  = $0 ✅✅✅ 完全免费!
```

### 重度使用者 (5000+ 完成/月)

```
GitHub Copilot Pro+ ($39):
  基础 $39 + 可能的高额超费
  = $50-100+/月
  ⚠️ 高不确定性

Cursor Pro+ ($60):
  基础 $60 + API 额度 $70
  = $60-130/月 (取决于模型选择)

Windsurf Max ($200):
  固定 $200 + 超额
  = $200-250/月 (无忧使用)
  等于 无日限制，足够配额

Claude Code Max 20x ($200):
  固定 $200
  = $200/月 (如果 Opus 用量多可能不够)

Cursor Ultra ($400):
  固定 $400 + 额外配额
  = $400-500/月 (终极方案)

推荐: Windsurf Max ($200) - 最平衡
```

```
```---
```

# 场景化选择指南

## 场景 1: "我是学生，成本为0"

**选项:**
1. ⭐ **GitHub Copilot Free** - 2000补全/月，50 agent/月
2. ⭐ **Amazon Q Free** - 无限代码补全
3. ⭐ **Cursor Hobby** - 有限但可用

**推荐:** **Amazon Q Free** (代码补全无限!)

**月成本:** $0 永久

```
```---
```

## 场景 2: "我是个人开发者，追求最便宜"

**选项:**
1. ⭐⭐⭐ **GitHub Copilot Pro** ($10)
2. ⭐⭐ **JetBrains AI Pro** ($9.66 + IDE)
3. ⭐ **Amazon Q Free + Cursor Hobby** ($0)

**注意:** GitHub Pro 容易超额

**推荐:** **GitHub Copilot Pro** ($10/月)

**月成本:** $10-20/月

```
```---
```

## 场景 3: "我想要最透明的模型成本"

**选项:**
1. ⭐⭐⭐⭐⭐ **Cursor Pro** ($20)
2. ⭐⭐⭐ **Windsurf Pro** ($20)
3. ⚠️ **Claude Code Pro** ($20，但成本不透明)

**推荐:** **Cursor Pro** ($20/月) - 费率最清晰

**月成本:** $20-50/月（完全可控）

```
```---
```

## 场景 4: "我要无忧的无限使用"

**选项:**
1. ⭐⭐⭐⭐⭐ **Windsurf Max** ($200)
   - 无日限制（新增！）
   - 足够的 Heavy Cascade 配额
   - API 价格直通

2. ⭐⭐⭐⭐ **Cursor Ultra** ($400)
   - 20× 基础配额
   - 所有模型可用
   - 固定成本心理舒适

3. **GitHub Pro+** ($39)
   - 1500 premium/月
   - 仍可能超额（不如前两个安心）

**推荐:** **Windsurf Max** ($200/月)

**月成本:** $200 固定

```
```---
```

## 场景 5: "我是初创团队 (3-10人)"

**选项:**
1. ⭐⭐⭐⭐⭐ **Cursor Teams** ($40/user/月)
   - 扁平的管理和成本
   - 3人 = $120/月，5人 = $200/月
   - 共享配额池
   - 分析报告

2. ⭐⭐⭐⭐ **Windsurf Teams** ($40/user/月)
   - 同价格，功能相近
   - 零数据保留政策
   - 更隐私友好

3. ⭐⭐⭐ **GitHub Teams** ($X/user，需查)
   - 与 GitHub 最紧密集成
   - 功能相对较少

**推荐:** **Cursor Teams** ($40/用户)

**月成本:** $120-200/月（3-5人）

```
```---
```

## 场景 6: "我是企业 (50+ 人)，需要权限感知"

**选项:**
1. ⭐⭐⭐⭐⭐ **Amazon Q Business Pro** ($20/user/月)
   - 唯一支持权限感知的方案
   - 符合企业数据治理
   - 100人 = $2000/月

2. ⭐⭐⭐⭐ **GitHub Enterprise** (议价)
   - 与 GitHub 工作流最紧密
   - 功能最全面
   - 成本通常高于 Amazon Q

3. ⭐⭐⭐ **JetBrains Enterprise** (议价)
   - IDE 集成最深
   - 本地部署支持好
   - 成本不透明

**推荐:** **Amazon Q Business Pro** ($20/用户)

**月成本:** $1000-2000+/月（50-100人）

```
```---
```

## 场景 7: "我的代码库很大，需要快速理解"

**选项:**
1. ⭐⭐⭐⭐⭐ **Windsurf Pro** ($20)
   - Cascade Agent 强大
   - SWE-1.5 最强的代码生成
   - 可快速学习 codebase

2. ⭐⭐⭐⭐ **Cursor Pro+** ($60)
   - 3×配额，更多尝试空间
   - Composer 2 最便宜
   - MCP 支持完整

3. ⭐⭐⭐ **Claude Code Pro** ($20)
   - Opus 4.6 最强
   - 多文件编辑最流畅
   - 成本不透明

**推荐:** **Windsurf Pro ($20) 或 Cursor Pro+ ($60)**

```
```---
```

## 场景 8: "我想要最强的代码生成质量"

**选项:**
1. ⭐⭐⭐⭐⭐ **Claude Code Pro** ($20)
   - Claude Opus 4.6 最强
   - 代码编辑体验最好
   - 多文件编辑流畅

2. ⭐⭐⭐⭐ **Windsurf Pro** ($20)
   - Cascade Agent 基于 Claude，同样强
   - SWE-1.5 专门优化代码
   - API 价格透明

3. ⭐⭐⭐ **GitHub Pro+** ($39)
   - Opus 访问
   - 功能最全面
   - Premium Requests 可能不够

**推荐:** **Claude Code Pro ($20)** (体验最好)

```
```---
```

# 成本陷阱与优化

## 🔴 陷阱 1: GitHub Copilot Pro 的 "Premium Requests" 快速耗尽

**问题:**
```
GitHub Copilot Pro 每月 300 premium requests

示例:
  用 Claude Opus 回答 50 个复杂问题
  → 300 / 50 = 6 个月内耗完全年配额
  → 被迫升级 Pro+ ($39/月)
  → 额外成本 $348/年！
```

**避免方法:**
1. **只用 GPT-5 Mini** (无限制)
2. 改用 **Cursor Pro** (透明计费)
3. 改用 **Windsurf Pro** (API 直通)
4. 监控 Premium Requests 消耗速度

```
```---
```

## 🟡 陷阱 2: Windsurf 的 "Light/Standard/Heavy" 定义过于模糊

**问题:**
```
Windsurf Pro 说 "Standard quota"
实际数字: 不公开
结果: 无法估算何时超额

无法做出知情的成本决策
```

**避免方法:**
1. 如果害怕超额，直接升级 **Max ($200)**
2. 在 Windsurf 的 Discord/社区寻求用量建议
3. 改用 **Cursor Pro** (清晰的 MPM 数字)

```
```---
```

## 🟡 陷阱 3: Claude Code 的模型切换成本不可见

**问题:**
```
Claude Code Pro/Max 说 "More usage" 和 "5×/20× usage"
实际每个模型的成本: 不公开
选择 Opus vs Sonnet: 成本差异 = 未知

可能无意中用了大量 Opus，导致超出预期
```

**避免方法:**
1. 保守假设 Opus 至少贵 10 倍 Haiku
2. 需要强大代码能力，用 Pro 而非试图省 Free
3. 改用 **Cursor Pro** (清晰的 API 费率)

```
```---
```

## 🟡 陷阱 4: JetBrains AI 与 IDE 订阅的成本混淆

**问题:**
```
AI Pro: $9.66/月
IDE License: $17-20/月 (required)
总成本: ~$27/月

但账单显示的是合并价格，难以分解 AI 成本
导致无法精确对标其他编辑器
```

**避免方法:**
1. 承认总成本是 $27/月，不是 $10/月
2. 企业用户: 协商 Enterprise 合同获得透明定价
3. 个人用户: 如果关心 AI 成本，改用 Cursor

```
```---
```

## 🟠 陷阱 5: Amazon Q Free 的"50 agent/月"容易超额

**问题:**
```
Amazon Q Free: 代码补全无限，但 Agent 仅 50/月
高频使用 Agent 的用户可能快速超额

超出后: 需付费，但费用不清楚
```

**避免方法:**
1. 轻度 Agent 用户: 保留在 Free
2. 中度 Agent 用户: 升级 **Q Business Lite ($3/user)**（企业）
3. 个人: 改用 **Cursor Pro** (Agent 无限)

```
```---
```

# 快速成本对比

## 按每月费用排序

| 编辑器 | 方案 | 月费 | 条件 |
|--------|------|------|------|
| **Amazon Q** | Free | $0 | 代码补全无限，Agent 50/月 |
| **GitHub** | Free | $0 | 2000 补全/月，50 agent/月 |
| **Cursor** | Hobby | $0 | 有限配额，可升级 |
| **Windsurf** | Free | $0 | Light 配额，有日限 |
| **JetBrains** | Free | $0 | 本地 AI，3 Credits/月 |
| **Claude Code** | Free | $0 | Web Chat 仅使用 |
| | | | |
| **JetBrains** | AI Pro | $9.66 | 含 IDE 订阅成本 |
| **GitHub** | Pro | $10 | ⚠️ Premium Requests 容易超额 |
| **Cursor** | Pro | $20 | ⭐ 透明计费，推荐 |
| **Windsurf** | Pro | $20 | ⭐ 全模型，API 直通 |
| **Claude Code** | Pro | $20 | Opus 访问，不透明成本 |
| **JetBrains** | AI Ultimate | $28.98 | 含 IDE 订阅 |
| | | | |
| **GitHub** | Pro+ | $39 | 1500 Premium Requests/月 |
| **Cursor** | Pro+ | $60 | ⭐ 推荐，3× 配额 |
| **Windsurf** | Teams/Max | $40-200 | 团队方案或无日限 |
| **Claude Code** | Max 5x | $100 | 5× 用量 |
| **Cursor** | Ultra | $200 | 20× 配额 |
| **Windsurf** | Max | $200 | 无日限制，Heavy 配额 |
| **Claude Code** | Max 20x | $200 | 20× 用量，企业功能 |

```
```---
```

## 最终选择建议矩阵

```
┌─ 完全免费 ─────────────────────────┐
│ Amazon Q Free (代码补全无限!)
│ GitHub Free (2000/月 + 50 agent)
│ Cursor Hobby (有限)
│ → 推荐: Amazon Q Free
└─────────────────────────────────────┘

┌─ $10-20/月 ──────────────────────┐
│ GitHub Copilot Pro ($10)
│ Cursor Pro ($20) ⭐⭐⭐
│ Windsurf Pro ($20) ⭐⭐⭐
│ Claude Code Pro ($20)
│ → 推荐: Cursor Pro (透明) 或 Windsurf Pro (全模型)
└─────────────────────────────────────┘

┌─ $40-60/月 ──────────────────────┐
│ Cursor Pro+ ($60) ⭐⭐
│ GitHub Pro+ ($39)
│ Windsurf Teams ($40/user)
│ → 推荐: Cursor Pro+ (体验最好)
└─────────────────────────────────────┘

┌─ $100-200/月 ────────────────────┐
│ Claude Code Max ($100-200) ⭐⭐
│ Windsurf Max ($200) ⭐⭐⭐
│ Cursor Ultra ($400)
│ → 推荐: Windsurf Max (无日限制)
│         或 Claude Code Max 20x (最强代码)
└─────────────────────────────────────┘

┌─ 企业/团队 ──────────────────────┐
│ Amazon Q Business Pro ($20/user) ⭐⭐⭐
│ GitHub Enterprise (议价)
│ Cursor Teams ($40/user)
│ Windsurf Enterprise (议价)
│ → 推荐: Amazon Q Business Pro (权限感知!)
└─────────────────────────────────────┘
```

```
```---
```

# 企业级对比

## 企业选择决策树

### Q1: 需要权限感知吗？

```
是 → Amazon Q Business Pro ($20/user/月) ✅ 独家支持
   → AI 回复被权限限制，符合数据治理
   
否 → GitHub Enterprise / Cursor Enterprise / JetBrains
   → 其他任何企业方案都可以
```

### Q2: 需要本地部署吗？

```
是 → JetBrains Enterprise (支持完整)
   → 或 Windsurf Enterprise (支持部分)
   
否 → Amazon Q / GitHub / Cursor
   → 云端部署即可
```

### Q3: 多少用户？

```
10-50人   → Amazon Q Business Lite ($3/user) 
        或 Cursor Teams ($40/user)
        或 JetBrains Enterprise
        
50-500人  → Amazon Q Business Pro ($20/user)
        或 GitHub Enterprise (议价)
        或 JetBrains Enterprise (议价)
        
500+ 人   → 定制企业方案
        → GitHub Enterprise / Amazon Q / JetBrains
        → 需要销售咨询，通常 $10-20+/user
```

### Q4: 需要哪些合规标准？

```
HIPAA    → Amazon Q (✅) 或 Claude Code Max ($200)
GDPR     → 所有主流方案都支持
SOC 2    → GitHub / Cursor / Windsurf / Claude / JetBrains
FedRAMP  → GitHub (✅) 
PCI-DSS  → 需要咨询各方案
```

```
```---
```

# 数据质量评估

## 各信息源可信度

### ✅ 高置信度 (官方明确)
- GitHub Copilot: 定价、基础限制清晰
- Cursor: API 费率、模型列表明确
- Claude Code: 定价方案明确
- Amazon Q: 定价清晰，功能明确
- JetBrains: 基础定价明确

### 🟡 中等置信度 (部分信息缺失)
- Windsurf: 定价清晰但"Light/Standard/Heavy"数值不公开
- GitHub Copilot: "Premium Requests" 的确切定义有歧义
- JetBrains: 企业定价模糊

### 🔴 低置信度 (需要更新)
- Claude Code: "More Usage" 的具体数字
- Windsurf: 具体的 daily limits
- Amazon Q: Free 到 Pro 的超额费用细节

```
```---
```

# 更新日志

| 日期 | 变化 | 备注 |
|------|------|------|
| 2026-04-12 | 融合版发布 | 四个文件合并为一个超详细指南 |
| 2026-04-12 | Windsurf Max | 新增"无日限制"功能 |
| 2026-04-12 | 6 编辑器对比 | 完整全面对比 |
| - | 建议关注 | GitHub Copilot 即将推出新定价; Claude 3.5 Opus 发布; Cursor 3.1 新功能 |

```
```---
```

# 附录: 官方资源链接

| 编辑器 | 定价页 | 文档 | 更新日志 |
|--------|--------|------|---------|
| **GitHub Copilot** | [plans](https://github.com/features/copilot/plans) | [docs](https://docs.github.com/en/copilot) | GitHub Blog |
| **Cursor** | [pricing](https://cursor.com/pricing) | [docs](https://cursor.com/docs) | [changelog](https://cursor.com/changelog) |
| **Windsurf** | [pricing](https://windsurf.com/pricing) | [docs](https://docs.windsurf.com) | [blog](https://windsurf.com/blog) |
| **Claude Code** | [claude.ai](https://claude.ai) | [support](https://support.claude.com) | [blog](https://claude.ai/blog) |
| **JetBrains AI** | [store](https://www.jetbrains.com/store) | [docs](https://www.jetbrains.com/help) | [blog](https://blog.jetbrains.com) |
| **Amazon Q** | [pricing](https://aws.amazon.com/q/pricing/) | [docs](https://docs.aws.amazon.com/q) | AWS Blog |

```
```---
```

**本指南基于 2026 年 4 月的官方公开文档生成。定价和功能会频繁变化。**

**建议: 在做出重要工具选择前，please 访问官方网站确认最新信息。**

**最后更新:** 2026年4月12日
