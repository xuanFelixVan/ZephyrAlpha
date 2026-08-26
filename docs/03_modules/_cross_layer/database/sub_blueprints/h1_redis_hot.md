---
module_id: MOD-H1_REDIS_HOT
submodule_path: src/zephyr/infrastructure/h1_redis_hot
title: "H1 redis_hot 实盘热缓存施工蓝图 — Redis <5ms 因子截面在线存储"
doc_type: blueprint
status: Active
version: "1.2.0"
layer: L2_domain
layer_name: hot_cache
functional_domain: data
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: AI-session-20260801-h1
valid_from: "2026-08-01"
date: "2026-08-01"
ttl: permanent
construction_progress: completed
actual_disk_path: "src/zephyr/infrastructure/h1_redis_hot/"
belongs_to: "MOD-ARCH_BIZDB"
parent_module: "MOD-ARCH_BIZDB"
codification_level: L1
last_updated: "2026-08-02"
generation: 1
rule_form: structural
scope: module
stability: evolving
verifiability: design_review
references:
  - path: "D:\\临时工作区\\架构图\\数据架构.md"
    section: "§7.1 三层存储 / §11.1 双存储架构(DD-11-01) / §12.4.2 CQRS读端 / §7.4 备份策略"
    why: "H1 设计要素真源——Key设计/容量/持久化/SLA 均来自此文档"
  - path: "d:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\database\\business_data_architecture.md"
    section: "§8.1 能造现在就造 / §11.1 现在建 / §14 子蓝图索引"
    why: "业务数据库母蓝图——H1 的上游设计定位"
  - path: "d:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\database\\blueprint.md"
    section: "三层冷热架构定位"
    why: "数据库集成蓝图——三层冷热架构 Hot 层触发条件裁定(2026-07-13)"
depends_on:
  - target: MOD-ARCH_BIZDB
    at: "§8.1/§11.1"
    why: "母蓝图定义 H1 为实盘热缓存，能造现在就造"
  - target: MOD-INF-002
    at: "database_service.py:176"
    why: "DatabaseService.get_redis_conn() 已实现（2026-08-02，D2 决策归属 MOD-INF-002）；redis_config.py 配置加载器同模块（真源 config/.env.redis）"
tags: [redis, hot-cache, online-store, feature-store, cqrs, realtime, factor-cross-section, h1, sub-blueprint, dd-11-01]
priority: P1
runtime_plane: hot
responsibility_domain: 
build_status: production
design_maturity: design
---

# H1 redis_hot 实盘热缓存施工蓝图

## 概述

H1 redis_hot 是业务数据库三层冷热架构的 **Hot 平面**——盘中实盘/模拟盘的实时热缓存，承载决策引擎 <5ms 因子截面读取（DD-11-01 在线存储）。它是实盘交易命脉：盘中 tick 下载后 D-FACTOR Engine 每 3 秒计算因子截面写入 Redis，决策引擎（D-SIGNAL/D-RISK）<5ms 读取做信号触发与风控。

本蓝图是母蓝图 [MOD-ARCH_BIZDB](file:///d:/ZephyrAlpha/docs/03_modules/_cross_layer/database/business_data_architecture.md) 的子蓝图之一（§11.1 现在建第 7 项），承接 [数据架构.md](file:///D:/临时工作区/架构图/数据架构.md) §7.1/§11.1/§12.4.2 的设计要素，细化到 Redis Key 字段级 + 接口级。

**触发条件已命中**：[blueprint.md](file:///d:/ZephyrAlpha/docs/03_modules/_cross_layer/database/blueprint.md) §三层冷热架构定位（2026-07-13 裁定）"Hot 层(Redis) 施工时机=实盘交易启动前开发"。用户即将进入"盘中模拟盘交易 + 盘后回测"双线并行阶段，模拟盘=国金 QMT 模拟端（账号 8886156677，模拟资金 1000 万，真实盘中交易流程，仅资金非真），是实盘完整彩排，盘中推理闭环与真实实盘同节奏。

> **施工进度**：`construction_progress: completed`（步骤1-7全链路完成：Redis 7.0.15 部署 172.24.30.100:6379 → get_redis_conn 实现 → schema/writer/reader/projectors 代码 → h1_integration.py D-FACTOR/SIGNAL/RISK 集成适配器 → E2E 联调通过 读取延迟 avg=0.20ms/max=0.38ms 远低于 <5ms SLA → depgraph build_status=stable/design_maturity=production。待真实 QMT 盘中联调——需交易日，代码级 E2E 已通过）。

---

## §0 代码对齐验证

### §0.1 代码文件清单

<!-- AUTOGEN: source=depgraph.nodes, generator=extract_depgraph.py, reconciler=blueprint_frontmatter_reconciler.py -->
> **⚠️ 自动化提示**：文件清单真源在 PostgreSQL depgraph.nodes 表，本节手写内容可能过时。
> 查询最新文件清单：`python scripts/governance/extract_depgraph.py --modules MOD-H1_REDIS_HOT`
> 以下手写内容保留职责描述（depgraph 无此信息），文件列表以 depgraph 为准。

| # | 文件名 | 对应蓝图章节 | 职责 | 存在性 |
|---|--------|------------|------|:---:|
| 1 | h1_redis_schema.py | §3 | Redis Key/数据结构定义（DDL-as-Code） | ✅ 已建 |
| 2 | h1_redis_writer.py | §4.1 | 因子截面/持仓/信号批量写入 Redis | ✅ 已建 |
| 3 | h1_redis_reader.py | §4.2 | <5ms 在线特征查询接口 | ✅ 已建 |
| 4 | h1_cqrs_projectors.py | §4.3 | 事件→Redis 物化视图投影器 | ✅ 已建 |
| 5 | database_service.py（get_redis_conn） | §4.4 | Redis 连接统一入口 | ✅ 已实现 |
| 6 | h1_integration.py | §9 | D-FACTOR/SIGNAL/RISK 集成适配器 | ✅ 已建 |

> **复用现有接口**：[database_service.py](file:///d:/ZephyrAlpha/src/zephyr/infrastructure/database_service.py) `get_redis_conn()` 已实现（2026-08-02），返回 `redis.Redis` 实例，连接参数从 `config/.env.redis` 经 `redis_config.load_redis_config()` 加载。

### §0.2 对齐验证矩阵

| 验证项 | 验证方法 | 结果 |
|--------|---------|:---:|
| construction_progress = completed → §0.1 步骤1-7全建（部署+schema+writer+reader+projectors+集成+production） | 逐文件核对 | ☑ |
| Redis Key 设计 = 数据架构.md §11.1/§12.4.2 | 路径比对 | ☑ |
| actual_disk_path = §11 产出物路径 | 路径比对 | ☑ |
| get_redis_conn() 已实现 | `grep "get_redis_conn" src/zephyr/infrastructure/database_service.py` | ☑ |
| E2E 读取延迟 <5ms | test_h1_writer_reader_projectors.py（avg=0.20ms/max=0.38ms） | ☑ |
| depgraph build_status=stable | `extract_depgraph.py --modules MOD-H1_REDIS_HOT` | ☑ |

### §0.3 版本-代码映射

| 蓝图版本 | 代码覆盖范围 | 缺失组件 | 缺失原因 |
|---------|------------|---------|---------|
| v1.2.0 (本版) | 全部业务代码已建（schema/writer/reader/projectors/integration/get_redis_conn）+ E2E 联调通过 + depgraph=stable | 真实 QMT 盘中联调（需交易日） | 休市日无法进行实盘联调 |

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-H1_REDIS_HOT`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-H1_REDIS_HOT` 的 22 个 file 节点 | design | `extract_depgraph.py --modules MOD-H1_REDIS_HOT` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | planned | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-H1_REDIS_HOT | MOD-H1_REDIS_HOT | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | production | production | ✅ |
| file_count | 22 文件 | 6 文件（§0.1） | ❌ |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## §1 设计依据

| # | 来源 | 章节 | 提供的设计要素 |
|---|------|------|-------------|
| 1 | 数据架构.md | §7.1 三层存储架构 | Hot 平面定位：延迟<10ms、可用性 99.99%、容量~19GB、内存估算~200MB |
| 2 | 数据架构.md | §11.1 双存储架构(DD-11-01) | 在线存储 Redis Hash、Key=feature:{symbol}、<5ms、每3秒截面写入 |
| 3 | 数据架构.md | §12.4.2 读端 CQRS | 5 个物化视图 Key 设计（position/signal/trade/risk/account） |
| 4 | 数据架构.md | §7.4 备份策略 | Redis 持久化：AOF appendfsync everysec + RDB 每日快照 |
| 5 | 数据架构.md | §7.2 容量规划 | ~200MB→1年~500MB→3年~1GB，扩展触发 maxmemory>70% |
| 6 | 数据架构.md | §7.3 生命周期 | 盘中无 TTL/盘后切 3600s；盘后清 Redis→3 个月迁 E 盘 |
| 7 | 母蓝图 MOD-ARCH_BIZDB | §8.1/§11.1 | H1=Redis，64G 内存够，实盘热缓存，能造现在就造 |
| 8 | blueprint.md | 三层冷热架构定位 | Hot 层触发条件=实盘交易启动前开发（2026-07-13 裁定） |
| 9 | 能力定位书 | 约束三/B-017 | miniQMT Tick=3秒、下单10笔/秒；策略日频不做HFT，3秒Tick用于信号触发/风控 |
| 10 | qmt_environments.yaml | sim 终端 | 模拟盘=国金QMT模拟端(8886156677)，真实盘中流程，实盘彩排 |

---

## §2 <5ms 场景定义（DD-11-01）

> **设计决策 DD-11-01**（数据架构.md 行1974）：采用离线+在线双存储。训练需 PIT 历史查询（Parquet，~100ms 可接受），推理需 <5ms 实时查询（Redis，延迟不可接受）。单一存储无法同时满足。

### §2.1 <5ms 刚需场景

| 场景 | 触发频率 | 读通路 | 延迟要求 | 说明 |
|------|---------|--------|:-------:|------|
| 盘中信号触发 | 每 3 秒/tick | Redis GET 因子截面 | <5ms | D-SIGNAL 读最新因子截面，3 秒 tick 间隔内完成决策 |
| 盘中风控查询 | 实时 | Redis GET 持仓/风控状态 | <5ms | D-RISK 实时风控，订单前校验 |
| 组合优化 | 信号触发时 | Redis GET 持仓+账户 | <5ms | D-POSITION 仓位裁决输入 |
| 当前持仓查询 | 下单前 | Redis GET position:{symbol} | <5ms | 防重复下单、仓位校验 |

### §2.2 与 B-017 日频策略的兼容性

能力定位书 B-017"不做 HFT，策略根频率=日频"与 <5ms 推理**不矛盾**：
- 策略决策是日频（每日开盘/盘中决策几次），但**盘中需实时监控 5000 只股票的信号触发/风控**
- 3 秒 tick 间隔内要完成全市场因子截面读取+信号扫描，<5ms 是单次读取延迟，不是高频交易
- 历史 PIT 查询走 Parquet（~100ms，回测/训练用），不进 Redis

### §2.3 CP-02 SLA

| SLA 编号 | 指标 | 阈值 | 降级策略 |
|---------|------|------|---------|
| CP-02 | Redis 因子值→信号端到端 | ≤5 秒（Tick→因子→Redis→信号） | <5ms 读取失败→P1 告警 + 使用上一批次因子值 + 标记过期 |

---

## §3 Redis Schema（Key 设计）

> 真源：数据架构.md §11.1（在线存储）+ §12.4.2（CQRS 读端物化视图）。

### §3.1 因子截面（在线存储，DD-11-01）

| Key 模式 | 数据结构 | Field | Value | TTL | 容量 |
|---------|---------|-------|-------|:---:|------|
| `feature:{symbol}` | Hash | `{factor_name}:{ver}` | `{factor_value}` (float) | 盘中无 / 盘后 3600s | ~50MB |

- **写入**：D-FACTOR Engine 每 3 秒截面批量写入，PIPELINE 模式，5000 只 × 200 因子 ≈ 1M 条/3 秒
- **读取**：`get_online_features(symbol, feature_names) → dict[str, float]`，<5ms
- **窄表理念**（DD-P3-01）：Field 含因子名+版本，新增因子不改 Key 结构

### §3.2 CQRS 读端物化视图（事件投影）

| 物化视图 | Key 模式 | 数据结构 | 更新频率 | 查询延迟 | 容量 |
|---------|---------|---------|:-------:|:-------:|------|
| 当前持仓 | `position:{symbol}` | Hash | 实时（OrderFilled 事件） | <5ms | ~5MB |
| 活跃信号 | `signal:active` | Set+Hash | 实时（SignalEvent） | <5ms | — |
| 当日交易 | `trade:today:{symbol}` | List | 实时（ExecutionEvent） | <5ms | — |
| 风控状态 | `risk:status` | Hash | 实时（RiskEvent） | <5ms | — |
| 账户状态 | `account:summary` | Hash | 实时 | <5ms | — |

### §3.3 Tick 缓存

| Key 模式 | 数据结构 | 用途 | TTL | 容量 |
|---------|---------|------|:---:|------|
| `tick:{symbol}:latest` | Hash | 盘中最新 tick（price/volume/bid1-5/ask1-5） | 盘中无 / 盘后即清 | ~100MB |

### §3.4 Key 命名规范

- 全小写 + 冒号分隔：`feature:000001.SZ`、`position:600000.SH`
- symbol 格式遵循 miniQMT 约定（6 位代码 + 交易所后缀）
- 盘后清理脚本按 `scan` 前缀批量删除当日临时 Key（保留 feature 的 3600s TTL 兜底）

---

## §4 接口设计

### §4.1 H1RedisWriter（因子截面写入）

```python
class H1RedisWriter:
    """D-FACTOR Engine 每 3 秒截面写入 Redis（PIPELINE 模式）"""
    def __init__(self, redis_conn):
        self.conn = redis_conn  # 来自 DatabaseService.get_redis_conn()

    def write_factor_cross_section(self, cross_section: dict[str, dict[str, float]]):
        """批量写入因子截面
        Args:
            cross_section: {symbol: {factor_name: factor_value}}, 5000只×200因子
        批量写入: PIPELINE 模式，~1M条/3秒
        """
```

### §4.2 H1RedisReader（<5ms 在线查询）

```python
class H1RedisReader:
    """决策引擎 <5ms 在线特征查询"""
    def __init__(self, redis_conn):
        self.conn = redis_conn

    def get_online_features(self, symbol: str, feature_names: list[str]) -> dict[str, float]:
        """读取单标的因子截面，<5ms
        Returns: {factor_name: factor_value}
        失败降级: 抛 H1RedisUnavailable → 调用方使用上一批次因子值+标记过期(CP-02)
        """

    def get_position(self, symbol: str) -> dict:
        """读取当前持仓，<5ms"""

    def get_risk_status(self) -> dict:
        """读取风控状态，<5ms"""
```

### §4.3 H1CqrsProjectors（事件→物化视图）

```python
class PositionProjector:
    """OrderFilled 事件 → position:{symbol} Hash 物化视图"""
    def handle(self, event: Event):
        if event.event_type == "OrderFilled":
            key = f"position:{event.payload['symbol']}"
            if event.payload["direction"] == "BUY":
                # HINCRBY quantity, HSET avg_price, HSET updated_at
                ...
```

> 投影逻辑真源：数据架构.md §12.4.2 行3020。

### §4.4 复用 DatabaseService.get_redis_conn()

```python
# src/zephyr/infrastructure/database_service.py（已实现 2026-08-02）
def get_redis_conn(self):
    """获取 Redis 连接（业务数据库 H1 热缓存）
    返回 redis.Redis 实例，连接参数来自 config/.env.redis
    经 redis_config.load_redis_config() 加载（fail-closed）
    """
    # 已实现：双重检查锁 + 惰性初始化 + 健康检查
    return redis.Redis(host=..., port=..., db=..., password=..., decode_responses=True)
```

---

## §5 约束条件

### §5.1 技术约束

| # | 约束 | 值 | 依据 |
|---|------|-----|------|
| 1 | 因子截面读取延迟 | <5ms | DD-11-01 |
| 2 | 因子截面写入频率 | 每 3 秒/批 | miniQMT Tick=3秒 |
| 3 | 批量写入模式 | PIPELINE | 5000只×200因子≈1M条/3秒 |
| 4 | 持久化 | AOF appendfsync everysec + RDB 每日 | 数据架构.md §7.4 行1104 |
| 5 | maxmemory 上限 | 64GB×30%=~19GB | 能力定位书约束二 |
| 6 | 扩展触发 | maxmemory 使用率>70% | 数据架构.md §7.2 |
| 7 | 盘中无 TTL / 盘后 3600s | feature Key | 数据架构.md §7.1/§11.1 |
| 8 | 窄表 Field（factor_name:ver） | 新增因子不改 Key 结构 | DD-P3-01 |

### §5.2 容量估算

> 真源：数据架构.md §7.2 行1076 + 行2137。

| 维度 | 当前 | 1年 | 3年 | 硬件上限 | 扩展触发 |
|------|:---:|:---:|:---:|:-------:|---------|
| Hot (Redis) | ~200MB | ~500MB | ~1GB | ~19GB | maxmemory>70% |

内存明细（~200MB）：因子截面~50MB（5000只×200因子×50字节）+ Tick缓存~100MB + 持仓/信号/风控~5MB + Redis内部开销~45MB。

### §5.3 迁移/废弃方案

| # | 迁移项 | 来源 | 目标 | 状态 |
|---|--------|------|------|:----:|
| 1 | get_redis_conn() 预留→实现 | NotImplementedError | 真实 redis.Redis 连接 | ✅ 已完成 |
| 2 | 无历史数据迁移 | — | Redis 为纯热缓存，盘后清空，无历史迁移 | — |

---

## §6 错误处理

### §6.1 异常场景

| # | 异常场景 | 检测方式 | 恢复策略 | 影响范围 |
|---|---------|---------|---------|---------|
| 1 | Redis 连接失败 | 连接超时 | 重试 + 告警 | 因子截面读取不可用 |
| 2 | 因子截面读取超 5ms | 计时 | P1 告警 + 使用上一批次因子值 + 标记过期(CP-02) | 信号延迟 |
| 3 | 批量写入失败 | RedisException | 记录失败批次 + 重试 | 因子截面延迟 |
| 4 | maxmemory 满 | maxmemory-policy 触发 | 告警 + 检查 TTL 策略 | Key 被淘汰 |

### §6.2 可观测性规格

| 指标名 | 类型 | 采集方式 | 告警阈值 | 告警级别 |
|--------|------|---------|---------|---------|
| h1_read_latency_seconds | Histogram | 计时 | P95>5ms | P1 |
| h1_write_cross_section_seconds | Histogram | 计时 | P95>3s | P1 |
| h1_redis_unavailable_total | Counter | 自动埋点 | >0 | P1 |
| h1_maxmemory_usage_ratio | Gauge | INFO memory | >70% | P2 |
| h1_factor_freshness_seconds | Gauge | 时间戳差 | >5s | P1（CP-02） |

### §6.3 退化矩阵

| 组件 | 失败后可用功能 | 不可用功能 | 降级策略 | 恢复条件 |
|------|-------------|-----------|---------|---------|
| Redis | 无（H1 是热缓存命脉） | 盘中<5ms推理 | 降级为进程内 L1 内存缓存 + 标记数据可能过期 + 限制下单 | Redis 恢复 |
| H1RedisReader | 上一批次因子值 | 实时因子截面 | CP-02：使用上一批次 + 标记 expired | Redis 恢复 |
| H1RedisWriter | 历史因子截面查询 | 实时因子更新 | 因子截面停滞，Reader 继续读旧值 | Writer 恢复 |

---

## §7 安全考量

| # | 安全项 | 措施 | 依据 |
|---|--------|------|------|
| 1 | Redis 凭证 | 环境变量存储（.env: REDIS_PASSWORD），禁止硬编码 | 防幻觉十八条 |
| 2 | 网络访问 | Redis 仅监听内网/本地，禁止公网暴露 | 基础设施安全 |
| 3 | 持仓/账户数据敏感 | 盘后清理 trade:today/account:summary | 最小留存 |
| 4 | 命令禁用 | 禁用 FLUSHALL/FLUSHDB（用 DEL 按 Key） | 防误删 |
| 5 | 模拟盘 vs 实盘隔离 | 不同 Redis DB（sim=db0, live=db1）或不同实例 | qmt_environments 隔离原则 |

---

## §8 部署方案

### §8.1 Redis 实例

| 项 | 值 |
|---|---|
| infra_id | INFRA-DB-007（已登记，status=connected） |
| 引擎 | Redis 7.0.15（AOF+RDB 双开） |
| 部署位置 | Hyper-V Ubuntu VM（zephyr-ch, 172.24.30.100，与 ClickHouse 同 VM，D1 决策 2026-08-02） |
| 端口 | 6379（默认） |
| maxmemory | 512mb（VM 实际 1.8GB RAM，留余量给 ClickHouse；远超~200MB 实际用量） |
| maxmemory-policy | allkeys-lru（兜底淘汰，正常不应触发） |
| 持久化 | appendonly yes + appendfsync everysec + save 900 1（RDB） |
| 统一入口 | `DatabaseService.get_redis_conn()` |

### §8.2 与 INFRA-CACHE-001 的关系

| 维度 | INFRA-CACHE-001（治理缓存） | H1 redis_hot（业务热缓存） |
|------|---------------------------|-------------------------|
| 用途 | Session Context / SSoT 校验 / Embedding Cache | 盘中因子截面/持仓/信号/风控 |
| runtime_plane | warm | hot |
| 依赖模块 | MOD-INF-001/MOD-TASK_SYSTEM | D-FACTOR/D-SIGNAL/D-RISK/D-POSITION |
| 故障影响 | 治理流程降级 | 实盘推理命脉 |

> **D3 决策（2026-08-02 用户确认）**：当前阶段采用**单实例 + DB 号隔离**——Redis 7.x 实例（172.24.30.100:6379）承载 H1 业务缓存，DB 号分配：db0=模拟盘（sim）、db1=实盘（live）、db2=治理缓存（INFRA-CACHE-001 预留）。INFRA-CACHE-001 立项前不拆独立实例（避免过度工程，违反设计准入一问标准）。未来升级触发条件见 §8.3。

### §8.3 演进路径与升级触发条件（D3 决策记录）

> **时态属性**：永久保留——未来 AI 查"INFRA-CACHE-001 何时立项 / Redis 是否需要拆分"时，查本节 T1–T4，任一命中即启动升级评估。

**当前架构**：单实例 + DB 号隔离——Redis 7.x 实例（172.24.30.100:6379）承载 H1 业务缓存，DB 号分配：db0=模拟盘（sim）、db1=实盘（live）、db2=治理缓存（INFRA-CACHE-001 预留）。

**演进目标**：当触发条件命中时，升级为"业务缓存 / 治理缓存独立实例"（隔离故障域）。

**升级触发条件（任一命中即启动拆分评估）：**

| # | 触发条件 | 判定方式 | 当前状态 |
|---|---------|---------|:-------:|
| T1 | INFRA-CACHE-001 正式立项 | `candidate_module_registry` 中 INFRA-CACHE-001 → approved，或 depgraph 治理缓存模块 `build_status: planned → active` | ❌ 未立项 |
| T2 | 淘汰策略冲突 | 业务需 `allkeys-lru`、治理需 `volatile-ttl`，DB 号隔离无法满足（maxmemory-policy 为实例级） | ❌ 未冲突 |
| T3 | 治理缓存容量压力 | 治理缓存预估内存 > 200MB | ❌ 未达（<50MB） |
| T4 | 故障隔离刚需 | 实盘要求"业务 Redis 故障不影响治理流程"（或反之） | ❌ 未达 |

**升级路径（预评估，调整代价低）：**

| 步骤 | 变更 | 影响文件 |
|------|------|---------|
| 1 | `.env.redis` 新增 `REDIS_GOVERNANCE_HOST/PORT/PASSWORD` | [config/.env.redis](file:///d:/ZephyrAlpha/config/.env.redis) |
| 2 | `get_redis_conn(purpose)` 参数化 | [database_service.py](file:///d:/ZephyrAlpha/src/zephyr/infrastructure/database_service.py)、[redis_config.py](file:///d:/ZephyrAlpha/src/zephyr/infrastructure/redis_config.py) |
| 3 | 无数据迁移（DB 号隔离下数据本就分离，只切换连接指向） | — |

- **预估工时**：< 0.5 天
- **升级后状态**：H1 独占 172.24.30.100:6379，INFRA-CACHE-001 起独立实例（端口 6380 或新 VM）

> **检索约定**：未来 AI 查"INFRA-CACHE-001 何时立项 / Redis 是否需要拆分"时，查本节 T1–T4，任一命中即启动升级评估。真源在本节，注册表 `INFRA-DB-007.note` 仅放指针。

---

## §9 与推理引擎集成点

| 集成点 | 方向 | 数据 | 接口 |
|--------|:----:|------|------|
| D-FACTOR Engine | → H1 | 每 3 秒因子截面 | H1RedisWriter.write_factor_cross_section |
| D-SIGNAL | H1 → | 因子截面（信号触发） | H1RedisReader.get_online_features |
| D-RISK | H1 → | 持仓/风控状态 | H1RedisReader.get_position/get_risk_status |
| D-POSITION | H1 → | 持仓/账户 | H1RedisReader.get_position |
| D-TRADING | → H1 | OrderFilled/ExecutionEvent | H1CqrsProjectors（持仓投影） |
| D-DATA (miniQMT) | → H1 | 盘中 tick | tick:{symbol}:latest 缓存 |

---

## §10 风险

| # | 风险 | 概率 | 影响 | 缓解 |
|---|------|:---:|:---:|------|
| R01 | ~~Redis 实例未部署阻塞实盘~~ | ~~高~~ | ~~P1~~ | ✅ 已解决——Redis 7.0.15 已部署 172.24.30.100:6379（2026-08-02） |
| R02 | 模拟盘延迟~1分钟影响测试 | 中 | P2 | 模拟盘延迟是下单回报延迟，不影响 Redis<5ms 读取测试 |
| R03 | maxmemory 估算偏差 | 低 | P2 | ~200MB 实际 vs 512mb 配置，余量充足 |
| R04 | 治理缓存与业务缓存争用 | 中 | P2 | 分离实例（§8.2） |

---

## §11 施工步骤（✅ 全部完成）

> 步骤1-7全链路完成（2026-08-02）。代码级 E2E 联调通过，depgraph build_status=stable/design_maturity=production。待真实 QMT 盘中联调（需交易日）。

1. ✅ 部署 Redis 实例（INFRA-DB-007）+ 配置 AOF/RDB — Redis 7.0.15 @ 172.24.30.100:6379
2. ✅ 实现 `DatabaseService.get_redis_conn()` — 已实现，redis_config.load_redis_config() 加载
3. ✅ 编写 h1_redis_schema.py（Key 定义） — DDL-as-Code
4. ✅ 编写 H1RedisWriter / H1RedisReader / H1CqrsProjectors — 全链路联调通过
5. ✅ 集成 D-FACTOR（写）/ D-SIGNAL/D-RISK（读） — h1_integration.py 适配器 + 4条 depgraph 数据依赖边
6. ✅ E2E 联调（代码级验证 <5ms 读取） — avg=0.20ms/max=0.38ms（远低于 5ms SLA）
7. ✅ build_status: planned → stable / design_maturity: design → production — depgraph 已转换

---

## 验收标准

| # | 验收项 | 验证方法 | 结果 |
|---|--------|---------|:---:|
| 1 | 蓝图 frontmatter 合法 | PS-STD-001 字段校验 | ☑ |
| 2 | depgraph H1 节点已登记（build_status=stable） | `extract_depgraph.py --modules MOD-H1_REDIS_HOT` | ☑ |
| 3 | 五图对齐干净 | `align_panoramas.py` domain_mismatches=0 | ☑ |
| 4 | Redis Key 设计与数据架构.md 一致 | 路径比对 §3 | ☑ |
| 5 | get_redis_conn() 已实现 | grep database_service.py | ☑ |
| 6 | E2E 读取延迟 <5ms | test_h1_writer_reader_projectors.py（avg=0.20ms） | ☑ |
| 7 | INFRA-DB-007 status=connected | infrastructure_registry.yaml | ☑ |

---

## 必备链接

| # | 文件 | module_id | 完整绝对路径 | 编写时用途 |
|---|------|-----------|------------|----------|
| 1 | 母蓝图 | MOD-ARCH_BIZDB | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\database\business_data_architecture.md` | H1 上游设计定位 |
| 2 | 数据库集成蓝图 | SH-DB-001 | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\database\blueprint.md` | 三层冷热架构定位 |
| 3 | 数据架构图 | — | `D:\临时工作区\架构图\数据架构.md` | Redis Key/容量/持久化真源 |
| 4 | C1 子蓝图（模板） | MOD-C1-MARKETCH | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\database\sub_blueprints\c1_market_clickhouse.md` | 子蓝图结构参照 |
| 5 | 能力定位书 | — | `D:\临时工作区\能力定位书.md` | 硬约束（miniQMT/B-017） |
| 6 | QMT 环境真源 | CFG-qmt-environments | `D:\ZephyrAlpha\config\qmt_environments.yaml` | 模拟盘定义 |
| 7 | 基础设施注册表 | — | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\infrastructure_registry.yaml` | INFRA-DB-007 登记 |

---

## 涉及的文件范围

| # | 文件/目录 | 完整绝对路径 | 关系 | 变更类型 |
|---|---------|------------|------|---------|
| 1 | `src/zephyr/infrastructure/h1_redis_hot/` | `D:\ZephyrAlpha\src\zephyr\infrastructure\h1_redis_hot\` | H1 业务代码 | ✅ 已建（schema/writer/reader/projectors/integration） |
| 2 | `database_service.py` | `D:\ZephyrAlpha\src\zephyr\infrastructure\database_service.py` | get_redis_conn() 实现 | ✅ 已修改（2026-08-02） |
| 3 | `h1_redis_hot.md` | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\database\sub_blueprints\h1_redis_hot.md` | 本蓝图 | ✅ 已建+已更新至 v1.2.0 |

---

## ⚠️ Vibe Coding 蓝图编写铁律

> **时态属性**：施工声明——AI 进入蓝图修改/施工时必读。永久保留。

| # | 铁律 | 违反后果 |
|---|------|---------|
| 1 | 所有路径必须是绝对路径（含盘符 `D:\`） | 文件创建到错误位置 |
| 2 | 必备链接不可省略 | AI 跳过不读，施工时缺少关键信息 |
| 3 | 蓝图必须是最终设计结果——不记录决策过程 | 蓝图过厚，关键信息被噪音淹没 |
| 4 | 产出物路径必须与 GOV-DOC-002 一致 | 路径幻觉 |
| 5 | 涉及文件范围必须明确列出 | 范围漂移 |
| 6 | 容量估算必须写 | 容量瓶颈 |
| 7 | 迁移/废弃方案必须写 | 断链 |
| 8 | "待定"/"建议"/"按需"等模糊词禁止使用 | 执行漂移 |
| 9 | 蓝图必须自包含 | 信息缺失 |
| 10 | construction_progress 必须与代码实际状态一致 | 重复造轮子 |
| 11 | actual_disk_path 必须与 §11 产出物路径一致 | 搜索失败 |
| 12 | 已实现代码不在蓝图中重复 | 蓝图过厚 |

---

## ⚠️ 安全删除协议

> **时态属性**：施工声明——AI 施工涉及删除时必读。永久保留。

| # | 铁律 |
|---|------|
| 1 | 禁止蓝图阶段物理删除任何文件 |
| 2 | 迁移型删除必须逐条迁移、逐条验证 |
| 3 | 物理删除只能在 stable 搬入阶段执行 |
| 4 | 物理删除必须人类确认 |
| 5 | "宁可慢，不可漏" |
