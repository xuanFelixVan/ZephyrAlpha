# 清风量化系统蓝图 (BLUEPRINT)

> **版本**: v1.0
> **创建日期**: 2026-03-30
> **合并来源**:
> - ULTIMATE_BLUEPRINT.md
> - DEPLOYMENT_BLUEPRINT.md
> - SECURITY_BLUEPRINT.md
> - API_INTEGRATION_BLUEPRINT.md
> - AI_RESEARCH_FRAMEWORK.md
> - DEVELOPMENT_ROADMAP.md
> - System_Manifest.md
>
> **归档位置**: `06_ARCHIVE/main/BLUEPRINTS/`
>
> **本文档定位**: 蓝图总览，完整内容见归档

---

## 📌 文档结构

本文档是7个原始蓝图文档的**合并版本**，完整内容已移至归档。

| 章节 | 来源文档 | 归档位置 |
|------|----------|----------|
| 第一章：终极愿景 | ULTIMATE_BLUEPRINT.md | [查看完整](./06_ARCHIVE/main/BLUEPRINTS/01_ULTIMATE_BLUEPRINT.md) |
| 第二章：技术栈 | ULTIMATE_BLUEPRINT.md | [查看完整](./06_ARCHIVE/main/BLUEPRINTS/01_ULTIMATE_BLUEPRINT.md) |
| 第三章：部署蓝图 | DEPLOYMENT_BLUEPRINT.md | [查看完整](./06_ARCHIVE/main/BLUEPRINTS/02_DEPLOYMENT_BLUEPRINT.md) |
| 第四章：安全蓝图 | SECURITY_BLUEPRINT.md | [查看完整](./06_ARCHIVE/main/BLUEPRINTS/03_SECURITY_BLUEPRINT.md) |
| 第五章：API蓝图 | API_INTEGRATION_BLUEPRINT.md | [查看完整](./06_ARCHIVE/main/BLUEPRINTS/04_API_INTEGRATION_BLUEPRINT.md) |
| 第六章：AI研究框架 | AI_RESEARCH_FRAMEWORK.md | [查看完整](./06_ARCHIVE/main/BLUEPRINTS/05_AI_RESEARCH_FRAMEWORK.md) |
| 第七章：开发路线图 | DEVELOPMENT_ROADMAP.md | [查看完整](./06_ARCHIVE/main/BLUEPRINTS/06_DEVELOPMENT_ROADMAP.md) |
| 第八章：系统架构 | System_Manifest.md | [查看完整](./06_ARCHIVE/main/BLUEPRINTS/07_SYSTEM_MANIFEST.md) |

---

## 第一章：终极愿景

### 1.1 人机协作模式

**最终愿景**: 人(决策) → AI(执行) → AI(优化) → 人(监督) → AI(报告)

```
人的职责（仅4项）:
1. 策略方向决策（什么时候用什么策略）
2. 风控规则设计（你能承受多大风险）
3. 资金管理（仓位分配/风险管理）
4. 最终交易授权（确认AI的建议）

AI的职责（全部自动化）:
1. 数据采集清洗
2. 因子计算
3. 信号生成
4. 组合优化
5. 交易执行
6. 绩效归因
7. 策略优化
8. 报告生成
```

### 1.2 完整模块分层架构

```
Layer 8: 人机交互层 (Human-AI Interface)
Layer 7: AI报告层 (AI Reporting)
Layer 6: 组合优化层 (Portfolio Optimization)
Layer 5: 策略执行层 (Strategy Execution)
Layer 4: 机器学习层 (Machine Learning) ← 新增核心模块
Layer 3: 舆情分析层 (Sentiment & Alternative Data) ← 核心差异化模块
Layer 2: Alpha因子层 (Alpha Factors)
Layer 1: 数据预处理层 (Data Preprocessing)
Layer 0: 数据源层 (Data Sources)
```

---

## 第二章：技术栈

### 2.1 数据源选择

| 数据源 | 定位 | 理由 |
|--------|------|------|
| **iFind终端** | 主数据源 | 5700+因子，机构级质量 |
| **同花顺SuperCommand** | 补充数据源 | 实时行情/选股 |
| **Baostock** | 免费财务验证 | 历史财务数据免费 |
| **AkShare** | 另类数据补充 | 宏观/非结构化数据 |

### 2.2 回测/实盘平台

| 平台 | 选择 | 理由 |
|------|------|------|
| **QMT (迅投)** | ✅ 主平台 | 国金证券QMT，深度API支持 |
| **Backtrader** | 备选/研究 | 轻量回测，快速验证 |
| **自研引擎** | 最终目标 | 完全可控的完整回测 |

### 2.3 AI/ML技术栈

| 用途 | 技术选择 | 说明 |
|------|---------|------|
| **LLM调用** | LangChain | AI研究Agent |
| **情感分析** | DeepSeek API / Qwen3 | 新闻/舆情分析 |
| **机器学习** | scikit-learn / PyTorch | 因子挖掘/预测 |
| **强化学习** | Stable-Baselines3 | 策略自我优化 |
| **参数优化** | Optuna | 超参数搜索 |
| **因子库** | **Qlib Alpha158** | 升级目标，AI量化框架 |

---

## 第三章：部署蓝图

### 3.1 部署环境

| 环境 | 目标 | 配置 |
|------|------|------|
| **开发环境** | 本地开发和测试 | Python 3.9+, venv, SQLite |
| **测试环境** | 功能测试和集成测试 | Docker, PostgreSQL, Redis |
| **模拟环境** | 模拟交易验证 | Kafka, 5年历史数据, Grafana |
| **生产环境** | 实盘交易 | Kubernetes, 8个FactorCalculator容器 |

### 3.2 部署流程

1. 代码检查 (pylint, flake8)
2. 单元测试 (pytest, coverage > 80%)
3. 构建Docker镜像
4. 推送到镜像仓库
5. 初始化数据库和缓存
6. 健康检查

---

## 第四章：安全蓝图

### 4.1 权限级别

| 级别 | 角色 | 权限 |
|------|------|------|
| 1 | 超级管理员 | 所有权限 |
| 2 | 系统管理员 | 配置、监控、告警 |
| 3 | 策略开发者 | 策略开发、回测、部署 |
| 4 | 交易员 | 交易执行、风险监控 |
| 5 | 分析师 | 数据查询、报告生成 |
| 6 | 审计员 | 日志查询、审计报告 |

### 4.2 密钥管理

- API密钥: 环境变量或Vault
- 数据库密钥: bcrypt加密
- 加密密钥: AES-256对称, RSA-2048非对称
- 密钥轮换: 每90天

### 4.3 数据安全

- 传输层: TLS 1.3
- 存储层: Fernet加密
- 备份: 每天全量 + 每小时增量

---

## 第五章：API蓝图

### 5.1 API架构

```
API Gateway
├── 认证中间件 (JWT验证, 限流, CORS)
└── API Routes
    ├── /api/v1/data - 数据接口
    ├── /api/v1/factors - 因子接口
    ├── /api/v1/backtest - 回测接口
    ├── /api/v1/trading - 交易接口
    ├── /api/v1/risk - 风控接口
    └── /api/v1/research - 研究接口
```

### 5.2 技术选型

| 组件 | 选择 |
|------|------|
| **框架** | FastAPI |
| **验证** | Pydantic |
| **认证** | JWT Token |
| **风格** | RESTful |

---

## 第六章：AI研究框架

### 6.1 设计原则

```
❌ 4.0过度设计: LangChain + LangGraph + AutoGen + CrewAI + 多Agent协作
✅ 5.0务实设计: LangChain调用LLM + 简单工具封装
```

### 6.2 工具列表

| 工具名称 | 功能 | 返回格式 |
|----------|------|----------|
| `get_stock_data` | 获取股票数据 | DataFrame |
| `calculate_factor` | 计算因子值 | Dict |
| `run_backtest` | 执行回测 | 回测报告 |
| `search_research_docs` | 搜索研究文档 | 文档列表 |
| `get_factor_performance` | 获取因子绩效 | IC/IR报告 |
| `generate_report` | 生成分析报告 | Markdown |

---

## 第七章：开发路线图

### 7.1 阶段划分

| 阶段 | 名称 | 时间 | 核心目标 |
|------|------|------|----------|
| Phase 0 | 准备阶段 | 2-4周 | 环境搭建 + QMT入门 |
| Phase 1 | 基础架构 | 1-2月 | 数据-回测-风控基础 |
| Phase 2 | 回测完善 | 2-3月 | 专业级回测能力 |
| Phase 3 | ML集成 | 3-4月 | AI量化能力 |
| Phase 4 | 舆情系统 | 2-3月 | 新闻→信号流程 |
| Phase 5 | AI自主量化 | 3-4月 | 人授权+AI执行 |
| Phase 6 | 实盘优化 | 2-3月 | 稳定实盘运行 |

**总时间**: 12-18个月

---

## 第八章：系统架构

### 8.1 完整目录结构

```
ZephyrAlpha/
├── config/                              # 配置文件
│   ├── system.yaml
│   ├── qmt.yaml
│   ├── ifind.yaml
│   └── risk/rules.yaml
├── src/                                # 源代码
│   ├── core/                          # 核心基类
│   ├── data/                          # 数据层
│   ├── factors/                       # 因子层
│   ├── ml/                            # 机器学习层
│   ├── sentiment/                     # 舆情分析层
│   ├── backtest/                      # 回测引擎
│   ├── portfolio/                     # 组合优化
│   ├── execution/                     # 执行层
│   ├── risk/                          # 风控层
│   ├── ai/                            # AI自主量化
│   ├── visualization/                  # 可视化
│   └── utils/                         # 工具
├── scripts/                            # 脚本
├── notebooks/                          # Jupyter
├── tests/                             # 测试
├── data/                              # 数据
├── logs/                              # 日志
└── docs/                              # 文档
```

### 8.2 关键技术决策

| 选择 | 理由 |
|------|------|
| **QMT为主** | 国金证券对接，Python API完善，回测实盘一致 |
| **iFind数据** | 5700+因子，机构级质量，数据直接可用 |
| **Qlib Alpha158** | 业界验证的AI因子库，减少自己造轮子 |
| **Streamlit** | 快速开发，AI辅助生成代码 |
| **DeepSeek/Qwen3** | 情感分析双引擎，降级策略完备 |

---

## 索引

| 原文档 | 归档位置 |
|--------|----------|
| ULTIMATE_BLUEPRINT.md | [06_ARCHIVE/main/BLUEPRINTS/01_ULTIMATE_BLUEPRINT.md](./06_ARCHIVE/main/BLUEPRINTS/01_ULTIMATE_BLUEPRINT.md) |
| DEPLOYMENT_BLUEPRINT.md | [06_ARCHIVE/main/BLUEPRINTS/02_DEPLOYMENT_BLUEPRINT.md](./06_ARCHIVE/main/BLUEPRINTS/02_DEPLOYMENT_BLUEPRINT.md) |
| SECURITY_BLUEPRINT.md | [06_ARCHIVE/main/BLUEPRINTS/03_SECURITY_BLUEPRINT.md](./06_ARCHIVE/main/BLUEPRINTS/03_SECURITY_BLUEPRINT.md) |
| API_INTEGRATION_BLUEPRINT.md | [06_ARCHIVE/main/BLUEPRINTS/04_API_INTEGRATION_BLUEPRINT.md](./06_ARCHIVE/main/BLUEPRINTS/04_API_INTEGRATION_BLUEPRINT.md) |
| AI_RESEARCH_FRAMEWORK.md | [06_ARCHIVE/main/BLUEPRINTS/05_AI_RESEARCH_FRAMEWORK.md](./06_ARCHIVE/main/BLUEPRINTS/06_AI_RESEARCH_FRAMEWORK.md) |
| DEVELOPMENT_ROADMAP.md | [06_ARCHIVE/main/BLUEPRINTS/06_DEVELOPMENT_ROADMAP.md](./06_ARCHIVE/main/BLUEPRINTS/06_DEVELOPMENT_ROADMAP.md) |
| System_Manifest.md | [06_ARCHIVE/main/BLUEPRINTS/07_SYSTEM_MANIFEST.md](./06_ARCHIVE/main/BLUEPRINTS/07_SYSTEM_MANIFEST.md) |

---

**版本**: v1.0 | **创建**: 2026-03-30 | **状态**: ✅ 活跃
