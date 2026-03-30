# 清风量化交易系统 v5.0

> 专业级量化交易系统 - 个人开发者适配版

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

| 文档 | 说明 |
|------|------|
| [docs/BLUEPRINT.md](docs/BLUEPRINT.md) | 系统蓝图 |
| [docs/INDEX.md](docs/INDEX.md) | 文档索引 |
| [docs/API_Contract.md](docs/API_Contract.md) | 接口规范 |
| [docs/Strategy_Spec_S001.md](docs/03_TRADING_TACTICS/Strategy_Spec_S001.md) | 策略定义 |
| [docs/FAQ.md](docs/FAQ.md) | 常见问题 |

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

- **文档中心**: [docs/](docs/)
- **因子库**: [docs/02_FACTOR_LIBRARY/](docs/02_FACTOR_LIBRARY/)
- **策略池**: [docs/03_TRADING_TACTICS/](docs/03_TRADING_TACTICS/)
- **变更日志**: [docs/CHANGELOG.md](docs/CHANGELOG.md)

---

**版本**: v5.0 | **更新**: 2026-03-31
