# ZephyrAlpha 项目交接文档

> **生成日期**: 2026-03-29
> **交接版本**: v5.0
> **项目名称**: ZephyrAlpha (清风量化交易系统 v5.0)

---

## 一、项目概述

### 1.1 项目定位

**ZephyrAlpha** 是一个面向个人投资者的量化交易系统，支持：
- 全A股市场量化策略开发
- AI增强的舆情分析和市场预测
- 本地化部署，保护数据隐私

### 1.2 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| **数据源** | iFind (同花顺) | 主力数据源，5700+因子 |
| **数据补充** | AkShare, Tushare, 爬虫 | 免费数据补充 |
| **存储** | ClickHouse + Redis | 分层存储，支持100GB+ |
| **回测** | Backtrader + VectorBT | 双平台分工 |
| **实盘** | QMT/miniQMT | 国金证券QMT API |
| **AI** | GLM-4-Flash, Qwen2.5, ChatGLM3 | 本地LLM |

### 1.3 硬件配置

| 组件 | 规格 |
|------|------|
| GPU | RTX 3090 24GB |
| RAM | 64GB |
| CPU | i7-12700KF |
| 存储 | 1.2TB SSD |

---

## 二、目录结构

```
D:\ZephyrAlpha\                    # 项目根目录
├── docs/                          # 文档中心
│   ├── INDEX.md                   # 文档导航入口
│   ├── UNIFIED_ARCHITECTURE.md    # 统一架构文档
│   ├── System_Manifest.md         # 系统清单
│   ├── SITEMAP.md                 # 站点地图
│   ├── 00_OVERVIEW/              # 系统总览
│   ├── 01_FRAMEWORK/             # 框架定义
│   ├── 02_FACTOR_LIBRARY/         # 因子库
│   ├── 03_TRADING_TACTICS/       # 交易策略
│   ├── 04_EXECUTION/             # 执行层
│   ├── 05_IMPLEMENTATION/        # 实施指南
│   ├── 06_ARCHIVE/               # 归档
│   └── 08_USER_EXPERIENCE/      # 用户体验
│
├── ZephyrAlpha/                    # 代码项目 (原quant_system_v5)
│   ├── src/                       # 源代码
│   ├── tests/                     # 测试
│   ├── config/                   # 配置
│   └── notebooks/                 # Jupyter
│
├── 旧文件/                        # 历史版本
```

---

## 三、已确认的技术方案

### 3.1 舆情分析系统

| 组件 | 技术 | 说明 | 状态 |
|------|------|------|------|
| 数据获取 | AkShare + iFind | 新闻来源 | ✅ |
| 情感分析 | GLM-4.7-Flash (模力方舟API) | 免费，200K上下文 | ✅ 已测试 |
| 事件分类 | Qwen3-4B (模力方舟API) | 免费，32K上下文 | ✅ 已测试 |
| 推理分析 | DeepSeek-R1-Distill-Qwen-14B | 免费，推理能力 | ✅ 已测试 |
| 数学证明 | DeepSeek-Prover-V2-7B | 免费 | ✅ 已测试 |
| 验证方案 | IC验证法 + 标注数据集 | 因子有效性验证 | 规划中 |

**模力方舟API Key**: `XA8UNQKJTRBEXHXJICM7KBOJHP6NRVN6UINHIZF8`

### 3.2 数据存储

| 层级 | 技术 | 用途 |
|------|------|------|
| 热数据 | Redis | 最近1年分钟K线 |
| 温数据 | ClickHouse | 1-5年日K线 |
| 冷数据 | ClickHouse压缩 | 5-10年历史数据 |

### 3.3 回测平台

| 平台 | 用途 | 特点 |
|------|------|------|
| Backtrader | 开发调试 | 逐K线运行，断点调试 |
| VectorBT | 批量优化 | 向量化，速度快 |

### 3.4 因子计算

| 类型 | 时机 | 示例 |
|------|------|------|
| 预计算 | 盘后 | MA/EMA, 财务因子, 舆情日均 |
| 实时计算 | 盘中 | 价格动量, 资金流, 突发舆情 |

### 3.5 QMT接入

```python
# miniQMT 连接配置
from xtquant import xttrader

trader = xttrader.xttrader()
trader.connect()
```

QMT安装路径: `D:\国金证券QMT交易端`

---

## 四、待完成任务

### 4.1 高优先级

| 任务 | 说明 | 状态 |
|------|------|------|
| 安装依赖 | `pip install -r requirements.txt` | 待完成 |
| QMT连接测试 | xtquant库连接测试 | 待完成 |
| ClickHouse部署 | 安装配置ClickHouse | 待完成 |
| 数据下载 | iFind历史数据下载 | 待完成 |

### 4.2 中优先级

| 任务 | 说明 | 状态 |
|------|------|------|
| 舆情系统搭建 | iFind + 爬虫 + LLM | 规划中 |
| 回测框架对接 | Backtrader/VectorBT + ClickHouse | 规划中 |
| 因子计算模块 | 预计算 + 实时计算 | 规划中 |

### 4.3 低优先级

| 任务 | 说明 | 状态 |
|------|------|------|
| AI模型调优 | 根据IC验证优化 | 规划中 |
| 实盘对接 | QMT信号传递 | 规划中 |
| 风控模块 | 仓位管理、止损 | 规划中 |

---

## 五、文档位置

### 5.1 核心文档

| 文档 | 路径 | 说明 |
|------|------|------|
| 统一架构 | `docs/UNIFIED_ARCHITECTURE.md` | Layer 0-8架构 |
| 系统清单 | `docs/System_Manifest.md` | 模块清单 |
| 舆情方案 | `docs/02_FACTOR_LIBRARY/04_DATA_SOURCE/ALTERNATIVE_DATA.md` | 新闻+LLM方案 |
| 数据存储 | `docs/02_FACTOR_LIBRARY/04_DATA_SOURCE/ALTERNATIVE_DATA.md` | ClickHouse方案 |
| 快速参考 | `docs/QUICK_REFERENCE.md` | 命令速查 |

### 5.2 索引文档

| 文档 | 路径 |
|------|------|
| 文档入口 | `docs/INDEX.md` |
| 站点地图 | `docs/SITEMAP.md` |
| 版本历史 | `docs/00_OVERVIEW/VERSION_HISTORY.md` |

---

## 六、命名规范

### 6.1 文件命名

| 类型 | 规范 | 示例 |
|------|------|------|
| Python | 小写_下划线 | `datahub.py` |
| 策略 | s+编号+名称 | `s001_trend_follow.py` |
| 因子 | alpha+编号+名称 | `alpha_001_momentum.py` |
| 配置 | 小写.yaml | `system.yaml` |
| 测试 | test_+模块名 | `test_datahub.py` |

### 6.2 目录命名

```
docs/           # 文档目录
src/           # 源代码
tests/         # 测试代码
config/        # 配置文件
scripts/       # 脚本工具
data/          # 数据目录
```

---

## 七、开发规范

### 7.1 工作流程

```bash
# 1. 创建分支
git checkout -b feature/xxx

# 2. 编写代码 + 测试
pytest tests/ -v

# 3. 提交
git commit -m "feat: 描述"

# 4. 推送
git push origin feature/xxx
```

### 7.2 提交类型

| 类型 | 说明 |
|------|------|
| feat | 新功能 |
| fix | 修复bug |
| docs | 文档更新 |
| test | 测试 |
| refactor | 重构 |

### 7.3 代码标准

- 使用类型提示
- 添加文档字符串
- 遵循PEP 8
- 单元测试覆盖率 > 80%

---

## 八、常见问题

### 8.1 QMT连接问题

**Q**: QMT连接失败怎么办？
**A**:
1. 确保QMT客户端已登录并运行
2. 确认xtquant库已安装
3. 检查路径配置: `D:\国金证券QMT交易端`

### 8.2 安装依赖超时

**Q**: pip安装超时？
**A**: 使用国内镜像
```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 8.3 数据存储选择

**Q**: 选择什么数据库？
**A**:
- 100GB以内: PostgreSQL + TimescaleDB
- 100GB以上: ClickHouse

---

## 九、下一步建议

### Phase 1: 环境搭建
1. 安装Python依赖
2. 部署ClickHouse
3. 测试QMT连接

### Phase 2: 数据管道
1. iFind数据下载
2. 数据入库ClickHouse
3. 舆情系统搭建

### Phase 3: 回测开发
1. Backtrader框架对接
2. 策略开发
3. IC验证

### Phase 4: 实盘对接
1. QMT信号对接
2. 风控模块
3. 自动化运行

---

## 十、关键链接

| 资源 | 链接 |
|------|------|
| Backtrader文档 | https://www.backtrader.com/ |
| VectorBT文档 | https://vectorbt.dev/ |
| ClickHouse | https://clickhouse.com/ |
| xtquant | 国金证券提供的miniQMT库 |
| GLM-4-Flash | https://open.bigmodel.cn/ |

---

## 十一、交接检查清单

### 已完成

- [x] 项目目录重命名 (quant_system_v5 → ZephyrAlpha)
- [x] 文档路径引用更新
- [x] 版本号更新为v5.0
- [x] 舆情系统技术方案确定
- [x] 存储方案确定 (ClickHouse)
- [x] 回测平台确定 (Backtrader + VectorBT)
- [x] QMT接入方案确定
- [x] Python依赖已安装 (大部分)
- [x] xtquant已安装 (版本250516.1.1)
- [x] QMT目录存在 (D:\国金证券QMT交易端)

### 待完成

- [ ] 部署ClickHouse (当前未安装)
- [ ] 测试QMT连接 (需要QMT客户端运行)
- [ ] 安装缺失依赖: optuna, stable-baselines3, deepseek, clickhouse-connect
- [ ] 修复17个测试失败 (因子计算/风控/告警模块)
- [ ] 下载历史数据

### 环境状态 (2026-03-29 检查)

| 组件 | 状态 | 说明 |
|------|------|------|
| Python | ✅ 3.13.12 | 已安装 |
| 核心依赖 | ✅ 已安装 | pandas, numpy, scipy等 |
| xtquant | ✅ 250516.1.1 | 已安装 |
| TA-Lib | ✅ 0.6.8 | 已安装 |
| ClickHouse | ❌ 未安装 | 需要部署 |
| optuna | ❌ 缺失 | 需安装 |
| stable-baselines3 | ❌ 缺失 | 需安装 |
| deepseek | ❌ 缺失 | 需安装 |
| clickhouse-connect | ❌ 缺失 | 需安装 |

### 测试状态

- **通过**: 132个测试
- **失败**: 17个测试

主要失败原因:
1. `test_ichimoku` - `_calculate_ichimoku`返回字典缺少`cloud_span_a`键(返回`senkou_span_a`)
2. `test_placeholder_warning` - 警告类型不匹配
3. `test_order_for_existing_position` - 字符串匹配问题
4. `test_max_positions_reached` - `KeyError: 'max_position_pct'`配置缺失
5. `create_account()` - 不支持`daily_pnl`和`max_drawdown`参数
6. `test_send_*` - 告警通道未配置SMTP

---

> **注意**: 归档目录(`06_ARCHIVE/`)、`旧文件/` 目录保持不变，是历史版本记录。
