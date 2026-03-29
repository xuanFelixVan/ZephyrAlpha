# 开发路线图 v5.0

> 清风量化系统 - 从零到赚钱的务实路线图

---

## 核心理念

> **"先生成利润，先生成利润，先生成利润"**
>
> 不追求完美架构，只追求：
> 1. 能跑起来
> 2. 能赚钱
> 3. 能维护

---

## 路线图总览

```
┌─────────────────────────────────────────────────────────────────────┐
│                        开发路线图 v5.0                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Phase 0        Phase 1        Phase 2        Phase 3        Phase 4  │
│  环境搭建  ──▶  回测框架  ──▶  因子选股  ──▶  模拟交易  ──▶  实盘准备  │
│  (1-2天)       (3-5天)       (5-10天)      (3-5天)       (1周)     │
│                                                                     │
│  ✅ 完成        ✅ 文档        📖 进行中       📋 计划        📋 计划    │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Phase 0: 环境搭建 (1-2天)

### 目标
- 安装Anaconda
- 创建量化环境
- 安装依赖库
- 跑通第一个Hello World

### 检查清单
- [ ] Anaconda安装成功
- [ ] 量化环境quant创建成功
- [ ] 依赖库安装成功
- [ ] 了解目录结构

### 交付物
- 可用的Python环境
- 已配置的ZephyrAlpha项目

### 文档
- [LEARNING_PATH.md](./LEARNING_PATH.md) - 环境搭建章节
- [dev-setup.md](./dev-setup.md) - 开发环境配置

---

## Phase 1: Backtrader回测框架 (3-5天) ✅ 文档已完成

### 目标
- 编写并运行第一个量化策略
- 理解回测报告
- 学会修改策略参数

### 检查清单
- [ ] 运行均线交叉策略回测
- [ ] 理解回测报告指标
- [ ] 修改参数观察效果
- [ ] 添加止损止盈

### 交付物
- `src/main.py` - 回测主入口
- `src/modules/strategies/s001_ma_cross.py` - 均线策略
- `src/modules/dataloader.py` - 数据加载器
- `src/modules/analyzers/performance.py` - 绩效分析
- `src/modules/risk/rules.py` - 风控规则

### 核心代码
```python
# 运行回测
python src/main.py --code 000001.SZ --start 2024-01-01 --end 2024-12-31
```

### 文档
- [PHASE1_DESIGN.md](./PHASE1_DESIGN.md) - **详细设计文档**
- [first-backtest.md](./first-backtest.md) - 快速开始

### 里程碑
- 第一个策略跑通 ✅
- 能看懂回测报告 ✅
- 学会调参 ✅

---

## Phase 2: 因子选股 (5-10天) 📖 文档已完成

### 目标
- 理解什么是因子
- 计算简单因子
- 完成单因子选股回测
- 理解IC分析

### 检查清单
- [ ] 计算过至少3个因子
- [ ] 完成单因子选股回测
- [ ] 理解IC分析
- [ ] 尝试因子组合

### 交付物
- `src/modules/factors/` - 因子计算模块
  - `factor_base.py` - 因子基类
  - `value_factors.py` - 估值因子
  - `momentum_factors.py` - 动量因子
  - `quality_factors.py` - 质量因子
  - `factor_portfolio.py` - 因子组合器

### 核心代码
```python
# 因子选股
portfolio = FactorPortfolio()
portfolio.add_factor('ret20', ReturnN(20).calculate(data))
portfolio.add_factor('roe', ROE().calculate(data))
selected = portfolio.select_stocks(n=50)
```

### 文档
- [factor_design.md](./factor_design.md) - **详细设计文档**

### 里程碑
- 理解因子原理 ✅
- 能计算多个因子 ✅
- 完成因子组合 ✅

---

## Phase 3: 模拟交易 (3-5天) 📋 待开发

### 目标
- 搭建模拟交易框架
- 实现每日自动调仓
- 生成净值曲线
- 对接模拟账户

### 检查清单
- [ ] 模拟交易框架搭建完成
- [ ] 运行完整月度的模拟
- [ ] 生成净值曲线
- [ ] 理解仓位管理

### 交付物
- `src/modules/trading/simulation.py` - 模拟交易框架
- `src/modules/trading/rebalancer.py` - 调仓模块

### 核心代码
```python
# 模拟交易
trader = SimulationTrading(initial_cash=100000)
for date in trading_dates:
    selected = run_factor_selection(date)
    trader.daily_rebalance(date, selected, prices)
```

### 文档
- 模拟交易详细设计 (待创建)

### 里程碑
- 模拟框架可用 ⏳
- 完整回测通过 ⏳
- 净值曲线生成 ⏳

---

## Phase 4: 实盘准备 (1周) 📋 待开发

### 目标
- 选择券商API
- 对接实盘账户
- 小资金实盘测试
- 建立风控机制

### 检查清单
- [ ] 券商API对接完成
- [ ] 小资金实盘测试
- [ ] 风控机制建立
- [ ] 监控告警配置

### 交付物
- `src/modules/brokers/` - 券商对接模块
- `config/broker.yaml` - 券商配置

### 里程碑
- 实盘对接 ⏳
- 小资金测试 ⏳
- 正式运行 ⏳

---

## 技术债务清单

### 可以欠的债（暂时忽略）
| 债 | 理由 | 未来时机 |
|---|------|----------|
| NozyIO可视化编辑器 | UI不是核心 | 有团队后 |
| 36环节决策框架 | 太复杂 | 策略稳定后 |
| MLflow实验追踪 | 个人不需要 | 自动化需求高时 |
| K8s容器化 | 过度工程 | 有运维团队后 |

### 不能欠的债（必须做）
| 债 | 理由 | 优先级 |
|---|------|--------|
| **风控规则** | 保住利润 | 🔴 P0 |
| **回测验证** | 确保策略有效 | 🔴 P0 |
| **数据验证** | 避免垃圾进垃圾出 | 🔴 P0 |
| **参数记录** | 可复现 | 🟡 P1 |

---

## 学习资源

### 书籍
| 书名 | 难度 | 推荐度 |
|------|------|--------|
| 《Python量化交易》 | ⭐ | ⭐⭐⭐⭐⭐ |
| 《量化投资》 | ⭐⭐ | ⭐⭐⭐⭐ |
| 《中山大学量化公开课》 | ⭐ | ⭐⭐⭐⭐ |

### 在线资源
| 资源 | 说明 | 链接 |
|------|------|------|
| Backtrader文档 | 回测框架 | backtrader.com |
| akshare文档 | 数据获取 | akshare.pro |
| tushare文档 | 数据获取 | tushare.pro |

---

## 下一步行动

### 立即开始（今天）

1. **安装Anaconda**
   ```bash
   # 下载并安装
   # https://www.anaconda.com/download
   ```

2. **创建环境**
   ```bash
   conda create -n quant python=3.10
   conda activate quant
   pip install backtrader pandas numpy matplotlib akshare
   ```

3. **运行第一个回测**
   ```bash
   cd d:\ZephyrAlpha
   python src/main.py --code 000001.SZ
   ```

### 本周目标

| 天数 | 任务 | 交付物 |
|------|------|--------|
| Day 1-2 | 环境搭建 | 跑通回测 |
| Day 3-5 | 学习策略 | 修改策略参数 |
| Day 6-7 | 学习因子 | 计算第一个因子 |

---

## 常见问题

### Q: 我是零基础，能学会吗？
A: 能。这个路线图专为新手设计，每一步都有详细文档。

### Q: 需要多少时间？
A: 每天1-2小时，约2-3周可以完成Phase 1-2。

### Q: 学完能找到工作吗？
A: 这个系统主要是个人投资工具，不是求职准备。

### Q: 遇到问题怎么办？
A: 1. 查看文档 2. 搜索引擎 3. AI助手 4. 社区提问

---

**最后更新**: 2026-03-29
**版本**: v5.0
**适用对象**: 零基础新手
**下一步**: 查看 [LEARNING_PATH.md](./LEARNING_PATH.md) 开始学习
