---
standard_type: 技术文档
applicable_scope: 全系统
compliance_level: 初始标准
parent_document: docs/INDEX.md
implementation_status: 设计阶段
owner: 文档维护者
version: 1.0.1
module_id: DOC_README
created_date: 2026-03-28
last_updated: 2026-04-08
---
# 清风量化交易系统 v5.1

> 清风量化系统 v5.1 - 专业级量化交易系统（个人开发者适配版）

---

## 快速开始（3步）

### 1. 环境配置
```bash
cd ZephyrAlpha
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

### 2. 配置文件
```bash
copy .env.example .env
# 编辑 .env 填入API密钥
```

### 3. 运行系统
```bash
python -m src.main
```

---

## 核心文档

> 全库文档的**统一入口**为 **[文档索引 `docs/INDEX.md`](docs/INDEX.md)**；下表为常用直达链接（接口与策略规格仍位于 `03_TRADING_TACTICS`，与仓库目录结构一致）。

| 文档 | 说明 |
|------|------|
| [文档索引](docs/INDEX.md) | 全库导航与分类（推荐首访） |
| [统一架构](docs/01_FRAMEWORK/ARCHITECTURE.md) | Layer 0–11 权威分层 |
| [系统站点图](docs/05_IMPLEMENTATION/SITEMAP.md) | 实施层站点图与导航 |
| [接口规范](docs/03_TRADING_TACTICS/API_Contract.md) | API 契约 |
| [策略定义](docs/03_TRADING_TACTICS/Strategy_Spec_S001.md) | 示例策略规格 |
| [常见问题](docs/02_FACTOR_LIBRARY/10_MANUAL/FAQ.md) | FAQ |

---

## 系统架构

```
Layer 0: 数据层 → Layer 1: 前置层 → Layer 2: Alpha层 → Layer 3: 风险层
  ↓
Layer 4: 组合层 → Layer 5: 执行层 → Layer 6: 监控层 → Layer 7: 归因层
```

详见: [docs/01_FRAMEWORK/ARCHITECTURE.md](docs/01_FRAMEWORK/ARCHITECTURE.md)

---

## 项目结构

```
ZephyrAlpha/
├── config/          # 配置文件
├── src/            # 源代码
├── data/           # 数据存储
├── logs/           # 日志文件
├── tests/          # 测试代码
├── docs/           # 完整文档
├── scripts/        # 脚本工具
├── notebooks/      # Jupyter笔记本
├── requirements.txt
└── .env.example
```

---

## 技术栈

- **语言**: Python 3.10+
- **数据**: pandas, numpy, scipy
- **数据库**: SQLite, DuckDB
- **调度**: APScheduler
- **日志**: loguru

---

## 相关资源

- **文档导航入口**: [docs/INDEX.md](docs/INDEX.md)
- **因子库**: [docs/02_FACTOR_LIBRARY/](docs/02_FACTOR_LIBRARY/)
- **策略与执行（战术层目录）**: [docs/03_TRADING_TACTICS/](docs/03_TRADING_TACTICS/)
- **变更日志**: [docs/06_ARCHIVE/CHANGELOG.md](docs/06_ARCHIVE/CHANGELOG.md)

---

**版本**: v5.1 | **更新**: 2026-04-08
