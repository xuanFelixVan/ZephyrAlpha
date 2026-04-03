---
module_id: DOC_DOC_001
version: 5.0.0
status: Active
created_date: 2026-04-01
last_updated: 2026-04-01
owner: 首席文档架构?
standard_type: 专业量化机构文档
applicable_scope: 全系?
compliance_level: 专业标准
parent_document: INDEX.md
implementation_status: 进行?
---

# ZephyrAlpha 项目交接文档

> **生成日期**: 2026-03-29
> **最后更?*: 2026-03-30
> **交接版本**: v5.0
> **项目名称**: ZephyrAlpha (清风量化交易系统 v5.0)

---

## 一、项目概?

### 1.1 项目定位

**ZephyrAlpha** 是一个面向个人投资者的量化交易系统，支持：
- 全A股市场量化策略开?
- AI增强的舆情分析和市场预测
- 本地化部署，保护数据隐私
- Layer 0-11 完整架构

### 1.2 技术栈

| 层级 | 技?| 说明 |
|------|------|------|
| **数据?* | iFind (同花? | 主力数据源，5900+因子 |
| **数据补充** | AkShare, Tushare | 免费数据补充 |
| **另类数据** | 东方财富(资金?、心知天气、AQI、百度指?| 免费API |
| **存储** | ClickHouse + Redis | 分层存储 |
| **回测** | Backtrader + VectorBT | 双平台分?|
| **实盘** | QMT/miniQMT | 国金证券QMT API |
| **AI** | 模力方舟API (GLM-4.7-Flash? | 免费模型 |

### 1.3 硬件配置

| 组件 | 规格 |
|------|------|
| GPU | RTX 3090 24GB |
| RAM | 64GB |
| CPU | i7-12700KF |
| 存储 | 1.2TB SSD |

---

## 二、目录结?

```
D:\ZephyrAlpha\                    # 项目根目?
├── docs/                          # 文档中心
?  ├── INDEX.md                   # 文档导航入口
?  ├── UNIFIED_ARCHITECTURE.md    # 统一架构文档
?  ├── System_Manifest.md         # 系统清单
?  ├── SITEMAP.md                 # 站点地图
?  ├── 00_OVERVIEW/              # 系统总览
?  ├── 01_FRAMEWORK/             # 框架定义
?  ├── 02_FACTOR_LIBRARY/         # 因子?
?  ├── 03_TRADING_TACTICS/       # 交易策略
?  ├── 04_EXECUTION/             # 执行?
?  ├── 05_IMPLEMENTATION/        # 实施指南
?  ├── 06_ARCHIVE/               # 归档
?  └── 08_USER_EXPERIENCE/      # 用户体验
?
├── src/                           # 源代?
├── tests/                         # 测试
├── config/                         # 配置
├── scripts/                        # 脚本
├── data/                          # 数据
├── notebooks/                      # Jupyter
└── docs/                          # 文档
```

---

## 三、已确认的技术方?

### 3.1 数据?(Layer 1)

#### 3.1.1 存储分层方案

| 层级 | 技?| 数据 | 保留时间 | 用?|
|------|------|------|----------|------|
| **热数?* | Redis | 1分钟K?| 60交易?| 实盘交易 |
| **温数?* | ClickHouse | 5分钟K?| 1?| 中期回测 |
| **冷数?* | ClickHouse | 日K?| 10? | 长期回测 |

#### 3.1.2 数据源分?

| 数据类型 | 主数据源 | 备用/补充 |
|----------|----------|-----------|
| 行情数据?900因子?| iFinD | AkShare |
| 新闻/舆情 | AkShare + 其他 | iFinD不能提供 |
| 另类因子 | 多种免费API | - |

#### 3.1.3 免费另类因子

| 类别 | 因子 | 获取方式 |
|------|------|----------|
| 资金?| 北向/融资融券/龙虎?| 东方财富API |
| 天气 | 温度/AQI | 心知天气/PM25.in |
| 搜索 | 百度指数 | AkShare |
| 宏观 | GDP/CPI/利率 | 国家统计局 |

#### 3.1.4 因子更新频率

| 频率 | 因子类型 | 更新时机 |
|------|----------|----------|
| tick/分钟 | 行情因子 | 实时 |
| 日更 | 资金?技术指?| 盘后18:00 |
| 季更 | 基本面因?| 财报发布?|
| 实时 | 新闻情感/公告事件 | 随时 |

### 3.2 舆情分析系统

| 组件 | 技?| 说明 | 状?|
|------|------|------|------|
| 数据获取 | AkShare + iFind | 新闻来源 | ?|
| 情感分析 | GLM-4.7-Flash (模力方舟API) | 免费?00K上下?| ?已测?|
| 事件分类 | Qwen3-4B (模力方舟API) | 免费?2K上下?| ?已测?|
| 推理分析 | DeepSeek-R1-Distill-Qwen-14B | 免费，推理能?| ?已测?|
| 数学证明 | DeepSeek-Prover-V2-7B | 免费 | ?已测?|
| 舆情数据结构 | sentiment_score, valence, arousal, dominance | 多维度情?| ?已设?|

**模力方舟API Key**: `XA8UNQKJTRBEXHXJICM7KBOJHP6NRVN6UINHIZF8`

### 3.3 因子计算框架 (Layer 2)

| 组件 | 功能 | 状?|
|------|------|------|
| 因子注册?(Registry) | 元数据管?| ?已规?|
| 依赖?(DAG) | 拓扑排序 | ?已规?|
| 调度?(Scheduler) | 任务调度 | ?已规?|
| 计算引擎 (Engine) | 批量计算 | ?已规?|
| 验证?(Validator) | IC/IR检?| ?已规?|

### 3.4 未来因子工具 (规划)

| 工具 | 定位 | 触发条件 |
|------|------|----------|
| TA-Lib | 200+技术指标库 | 需要更多技术指标时 |
| Alphalens | 专业因子分析 | 进入策略优化阶段 |
| 因子组合优化 | PCA降维/权重优化 | 因子数量超过50?|

### 3.5 回测平台

| 平台 | 用?| 特点 |
|------|------|------|
| Backtrader | 开发调?| 逐K线运行，断点调试 |
| VectorBT | 批量优化 | 向量化，速度?|

### 3.6 QMT接入

```python
# miniQMT 连接配置
from xtquant import xttrader

trader = xttrader.xttrader()
trader.connect()
```

QMT安装路径: `D:\国金证券QMT交易端`

---

## 四、已讨论完的Layer

### 4.1 ?Layer 1 - 数据?

| 主题 | 状?| 文档 |
|------|------|------|
| 存储分层方案 | ?完成 | ALTERNATIVE_DATA.md |
| 舆情数据结构 | ?完成 | sentiment_score, valence?|
| 新闻获取方案 | ?完成 | AkShare+iFind+Marketaux |
| 另类因子体系 | ?完成 | 资金?天气/搜索指数 |
| 因子更新频率 | ?完成 | 分钟/??季分?|
| 实时vs历史处理 | ?完成 | 统一接口架构 |
| 5900因子策略 | ?完成 | iFinD预计?本地按需 |
| 数据备份规划 | ?规划 | STORAGE_TIER.md |

### 4.2 ?Layer 2 - 因子计算框架

| 主题 | 状?| 文档 |
|------|------|------|
| 因子注册?| ?完成 | FACTOR_CALCULATION_FRAMEWORK.md |
| 因子依赖管理 | ?完成 | DAG分层/Layer 0-3 |
| 因子调度?| ?完成 | 日频/分钟调度 |
| 因子计算引擎 | ?完成 | 批量计算/并行 |
| 因子验证 | ?完成 | IC/IR/完整?|
| 未来工具规划 | ?完成 | TA-Lib/Alphalens/PCA |

### 4.3 ?待讨?

| Layer | 主题 | 说明 |
|-------|------|------|
| Layer 3 | 策略逻辑 | 策略路由?优先?|
| Layer 4 | 风控规则 | 仓位/止损/回撤 |
| Layer 5 | 交易执行 | QMT对接 |
| Layer 6 | 监控告警 | 监控指标 |
| Layer 7 | 报告生成 | 报告内容 |
| Layer 8 | AI决策 | 6个AI模块 |

---

## 五、文档位?

### 5.1 核心文档

| 文档 | 路径 | 说明 |
|------|------|------|
| 统一架构 | `docs/UNIFIED_ARCHITECTURE.md` | Layer 0-11架构 |
| 系统清单 | `System_Manifest.md` | 系统模块清单 |
| 舆情方案 | `docs/02_FACTOR_LIBRARY/04_DATA_SOURCE/ALTERNATIVE_DATA.md` | 新闻+LLM方案 |
| 数据存储 | `docs/02_FACTOR_LIBRARY/04_DATA_SOURCE/ALTERNATIVE_DATA.md` | ClickHouse方案 |
| 快速参?| `docs/QUICK_REFERENCE.md` | 命令速查 |

### 5.2 索引文档

| 文档 | 路径 |
|------|------|
| 文档入口 | `docs/INDEX.md` |
| 站点地图 | `docs/SITEMAP.md` |
| 版本历史 | `docs/00_OVERVIEW/VERSION_HISTORY.md` |

---

## 六、命名规?

### 6.1 文件命名

| 类型 | 规范 | 示例 |
|------|------|------|
| Python | 小写_下划?| `datahub.py` |
| 策略 | s+编号+名称 | `s001_trend_follow.py` |
| 因子 | alpha+编号+名称 | `alpha_001_momentum.py` |
| 配置 | 小写.yaml | `system.yaml` |
| 测试 | test_+模块?| `test_datahub.py` |

### 6.2 目录命名

```
docs/           # 文档目录
src/           # 源代?
tests/         # 测试代码
config/        # 配置文件
scripts/       # 脚本工具
data/          # 数据目录
```

---

## 七、开发规?

### 7.1 工作流程

```bash
# 1. 创建分支
git checkout -b feature/xxx

# 2. 编写代码 + 测试
pytest tests/ -v

# 3. 提交
git commit -m "feat: 描述"

# 4. 推?
git push origin feature/xxx
```

### 7.2 提交类型

| 类型 | 说明 |
|------|------|
| feat | 新功?|
| fix | 修复bug |
| docs | 文档更新 |
| test | 测试 |
| refactor | 重构 |

### 7.3 代码标准

- 使用类型提示
- 添加文档字符?
- 遵循PEP 8
- 单元测试覆盖?> 80%

---

## 八、常见问?

### 8.1 QMT连接问题

**Q**: QMT连接失败怎么办？
**A**:
1. 确保QMT客户端已登录并运?
2. 确认xtquant库已安装
3. 检查路径配? `D:\国金证券QMT交易端`

### 8.2 安装依赖超时

**Q**: pip安装超时?
**A**: 使用国内镜像
```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 8.3 数据存储选择

**Q**: 选择什么数据库?
**A**:
- 100GB以内: PostgreSQL + TimescaleDB
- 100GB以上: ClickHouse

---

## 九、下一步建?

### Phase 1: 环境搭建
1. 安装Python依赖
2. 部署ClickHouse
3. 测试QMT连接

### Phase 2: 数据管道
1. iFind数据下载
2. 数据入库ClickHouse
3. 舆情系统搭建

### Phase 3: 回测开?
1. Backtrader框架对接
2. 策略开?
3. IC验证

### Phase 4: 实盘对接
1. QMT信号对接
2. 风控模块
3. 自动化运?

---

## 十、关键链?

| 资源 | 链接 |
|------|------|
| Backtrader文档 | https://www.backtrader.com/ |
| VectorBT文档 | https://vectorbt.dev/ |
| ClickHouse | https://clickhouse.com/ |
| xtquant | 国金证券提供的miniQMT?|
| GLM-4-Flash | https://open.bigmodel.cn/ |

---

## 十一、交接检查清?

### 已完?

- [x] 项目目录重命?(quant_system_v5 ?ZephyrAlpha)
- [x] 文档路径引用更新
- [x] 版本号更新为v5.0
- [x] 舆情系统技术方案确?
- [x] 存储方案确定 (ClickHouse)
- [x] 回测平台确定 (Backtrader + VectorBT)
- [x] QMT接入方案确定
- [x] Python依赖已安?(大部?
- [x] xtquant已安?(版本250516.1.1)
- [x] QMT目录存在 (D:\国金证券QMT交易?

### 待完?

- [ ] 部署ClickHouse (当前未安?
- [ ] 测试QMT连接 (需要QMT客户端运?
- [ ] 安装缺失依赖: optuna, stable-baselines3, deepseek, clickhouse-connect
- [ ] 修复17个测试失?(因子计算/风控/告警模块)
- [ ] 下载历史数据

### 环境状?(2026-03-29 检?

| 组件 | 状?| 说明 |
|------|------|------|
| Python | ?3.13.12 | 已安?|
| 核心依赖 | ?已安?| pandas, numpy, scipy?|
| xtquant | ?250516.1.1 | 已安?|
| TA-Lib | ?0.6.8 | 已安?|
| ClickHouse | ?未安?| 需要部?|
| optuna | ?缺失 | 需安装 |
| stable-baselines3 | ?缺失 | 需安装 |
| deepseek | ?缺失 | 需安装 |
| clickhouse-connect | ?缺失 | 需安装 |

### 测试状?

- **通过**: 132个测?
- **失败**: 17个测?

主要失败原因:
1. `test_ichimoku` - `_calculate_ichimoku`返回字典缺少`cloud_span_a`?返回`senkou_span_a`)
2. `test_placeholder_warning` - 警告类型不匹?
3. `test_order_for_existing_position` - 字符串匹配问?
4. `test_max_positions_reached` - `KeyError: 'max_position_pct'`配置缺失
5. `create_account()` - 不支持`daily_pnl`和`max_drawdown`参数
6. `test_send_*` - 告警通道未配置SMTP

---

> **注意**: 归档目录(`06_ARCHIVE/`)、`旧文?` 目录保持不变，是历史版本记录?
