# CHANGELOG - 项目变更记录

> 清风量化交易系统版本变更历史
>
> **版本**：v1.0
> **更新日期**：2026-03-28
> **维护者**：清风量化

---

## 变更记录规范

### 格式说明

```
## [版本号] - YYYY-MM-DD

### 新增
- 新增内容

### 优化
- 优化内容

### 修复
- 修复内容

### 废弃
- 废弃内容
```

### 类型标签

| 标签 | 说明 |
|------|------|
| `### 新增` | 新功能、新文档 |
| `### 优化` | 改进、重构、结构优化 |
| `### 修复` | Bug修复、错误修正 |
| `### 废弃` | 废弃功能、废弃文档 |

---

## 版本历史

### [v4.0] - 2026-03-28

> 本次更新完成了文档结构的重大重构，建立了清晰的模块化架构。

#### 新增

- 新增 `SPEC.md` - 统一入口规格文档
- 新增 `CODE_STATUS.md` - 代码状态标记规范
- 新增 `archive/main/README.md` - main模块归档索引
- 新增 `archive/factor-library/README.md` - 因子库归档索引
- 新增 `docs/technical-specs/architecture/` - 系统架构模块
  - `json-schemas.md` - JSON接口定义
  - `distributed-system.md` - 分布式计算
  - `barra-optimizer.md` - Barra优化器
  - `low-latency.md` - 低延迟架构
  - `disaster-recovery.md` - 容灾备份
- 新增 `docs/technical-specs/modules/` - 核心模块
  - `cost-model.md` - 全成本模型
  - `backtest-engine.md` - 回测引擎
  - `risk-management.md` - 风险管理
  - `order-routing.md` - 订单路由
  - `trading-monitor.md` - 交易监控
  - `trading-api.md` - 交易API
  - `trading-auditor.md` - 日志审计
- 新增 `docs/technical-specs/trading-rules/` - 交易规则
  - `a-share-rules.md` - A股规则
- 新增 `docs/technical-specs/ai-optimization/` - AI优化
  - `self-optimization.md` - AI自我优化
  - `monitoring.md` - 市场监控
  - `stock-strength.md` - 股票强度
- 新增 `docs/trading-tactics/strategy-pool/` - 策略池
  - `index.md` - 策略池概述
  - `classification.md` - 策略分类
  - `interface-standard.md` - 策略接口
  - `manager.md` - 策略管理器
  - `retail-strategies-a.md` - 游资策略（上）
  - `retail-strategies-b.md` - 游资策略（下）
- 新增 `docs/trading-tactics/tactics/` - 战术库
  - `technical-indicators.md` - 技术指标
  - `pattern-recognition.md` - 形态识别
  - `limit-up-analysis.md` - 涨停板分析
  - `market-cycles.md` - 市场周期
  - `ai-integration.md` - AI策略整合
  - `wave-trading.md` - 波段战法
- 新增 `docs/factor-library/01_METHODOLOGY/` - 研究方法论
  - `factor_definition.md` - 因子定义标准
  - `ic_analysis.md` - IC分析体系
  - `factor_preprocessing.md` - 因子预处理
  - `factor_synthesis.md` - 因子合成
  - `backtest_standards.md` - 回测标准
- 新增 `docs/factor-library/05_BACKTEST/` - 回测报告目录
  - 价值类/PE_TTM_IC_20260328.md
  - 价值类/PE_TTM_BACKTEST_20260328.md
  - 相关性矩阵_20260328.md

#### 优化

- 优化目录结构：从4个大型文档拆分为34个模块化文件
- 优化归档策略：统一归档到 `docs/archive/`
- 优化代码状态：明确示例代码/框架代码/可执行代码三级分离
- 优化文档引用：建立完整的交叉引用体系
- 优化因子库结构：扁平化目录层级

#### 废弃

- 废弃 `main/01_FRAMEWORK/` - 框架已迁移
- 废弃 `main/03_ARCHIVE/` - 归档已迁移
- 废弃 `factor-library/05_RAW_DATA/` - 目录重复，已合并
- 废弃 `factor-library/06_ARCHIVE/` - 归档已迁移

---

### [v3.1] - 2026-03-28

> 本次更新完成了main模块的机构级升级。

#### 新增

- 新增 `main/01_FRAMEWORK/量化策略框架_v3.1.md` - v3.1框架
- 新增 `main/CHANGELOG.md` - 版本变更记录

#### 优化

- 优化性能目标：年化收益目标从15%提升到18%
- 优化风险控制：最大回撤从15%降到12%
- 优化架构设计：8层Layer 0-7架构

---

### [v3.0] - 2026-03-26

> 初始重构版本，建立专业机构标准框架。

#### 新增

- 新增7层量化策略框架
- 新增因子库5723+指标
- 新增战术库CD.1-CD.89

---

## 项目阶段

| 阶段 | 状态 | 说明 |
|------|------|------|
| 研究/策略设计 | ✅ 当前 | 验证策略想法，建立方法论 |
| 回测验证 | 🔜 下一阶段 | 用历史数据验证策略 |
| 模拟交易 | ⏳ 未来 | 真实环境验证 |
| 实盘交易 | ⏳ 未来 | 实际资金验证 |

---

## 相关文档

| 文档 | 说明 |
|------|------|
| [SPEC.md](./SPEC.md) | 主规格文档 |
| [CODE_STATUS.md](./CODE_STATUS.md) | 代码状态规范 |
| [README.md](./README.md) | 项目README |

---

## 更新记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0 | 2026-03-28 | 初始版本，建立变更记录规范 |
