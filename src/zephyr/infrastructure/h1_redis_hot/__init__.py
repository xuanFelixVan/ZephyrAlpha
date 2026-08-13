# [BLUEPRINT] MOD-H1_REDIS_HOT | docs/03_modules/_cross_layer/database/sub_blueprints/h1_redis_hot.md
# [MODULE] zephyr.infrastructure.h1_redis_hot
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.database_service; zephyr.infrastructure.redis_config
# [CONSUMERS] zephyr.factor; zephyr.signal; zephyr.risk; zephyr.position; zephyr.trading
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 所有 Key 通过 h1_redis_schema 构造函数生成; Writer 用 PIPELINE 批量写; Reader <5ms; Projector 事件驱动
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] H1RedisUnavailable(Reader 降级信号); RedisConfigError(配置缺失); redis.RedisError(连接异常)
# [TESTS] tests/zephyr/infrastructure/h1_redis_hot/
# [A_module] module_id=MOD-H1_REDIS_HOT | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""

H1 Redis 热缓存模块——盘中实盘/模拟盘 <5ms 因子截面在线存储（DD-11-01）。

子模块：
    - h1_redis_schema: Key DDL（7类 Key 构造函数 + TTL/容量常量）
    - h1_redis_writer: D-FACTOR 批量因子截面写入（PIPELINE 模式）
    - h1_redis_reader: 决策引擎 <5ms 在线特征查询（降级 H1RedisUnavailable）
    - h1_cqrs_projectors: 事件→Redis 物化视图投影器（持仓/信号/风控）

部署：Redis 7.0.15 @ Hyper-V Ubuntu VM（172.24.30.100:6379，与 ClickHouse 同 VM，D1 决策）。
归属：MOD-INF-002（D2 决策：get_redis_conn 在 database_service.py）。
隔离：D3 决策——单实例 + DB 号隔离（db0=sim/db1=live/db2=gov），升级触发条件见蓝图 §8.3。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: D-FACTOR 因子截面批量数据
#   fields: 盘中因子截面（批量写入负载）
#   code: h1_redis_writer
# - id: I2
#   name: 决策引擎在线特征查询
#   fields: Key 查询请求（要求 <5ms 返回）
#   code: h1_redis_reader
# - id: I3
#   name: 领域事件流（持仓/信号/风控）
#   fields: CQRS 事件（事件驱动投影）
#   code: h1_cqrs_projectors
# - id: I4
#   name: Redis 连接配置
#   fields: 172.24.30.100:6379 + db 号隔离（db0=sim/db1=live/db2=gov）
#   code: zephyr.infrastructure.database_service / redis_config
# 层: 算法
# - id: A1
#   name_zh: ① Key DDL 构造
#   name_en: h1_redis_schema
#   intro: 7 类 Key 构造函数统一生成 Redis Key，附带 TTL 与容量常量
#   desc: 所有 Key 必须通过 schema 构造函数生成（模块 INVARIANTS），保证键空间一致可治理
#   inputs: I4
#   outputs: 规范 Key + TTL/容量常量
#   invariant: 所有 Key 通过 h1_redis_schema 构造函数生成
# - id: A2
#   name_zh: ② 因子截面批量写入
#   name_en: h1_redis_writer
#   intro: D-FACTOR 的因子截面用 PIPELINE 模式批量写进 Redis 热缓存
#   desc: PIPELINE 批量写（INVARIANTS：Writer 用 PIPELINE 批量写），盘中实盘/模拟盘在线存储（DD-11-01）
#   inputs: A1 I1
#   outputs: Redis 热缓存写入
# - id: A3
#   name_zh: ③ 在线特征查询
#   name_en: h1_redis_reader
#   intro: 决策引擎 <5ms 读因子截面，Redis 不可用抛 H1RedisUnavailable 降级
#   desc: Reader <5ms（INVARIANTS）；连接异常/不可用 → H1RedisUnavailable 降级信号（ERROR_CONTRACT）
#   inputs: A1 I2
#   outputs: 因子截面查询结果 / 降级信号
#   invariant: Reader <5ms
# - id: A4
#   name_zh: ④ 事件→物化视图投影
#   name_en: h1_cqrs_projectors
#   intro: 把持仓/信号/风控领域事件投影成 Redis 物化视图，事件驱动
#   desc: 事件驱动投影器（INVARIANTS：Projector 事件驱动），消费事件流维护 Redis 侧读模型
#   inputs: A1 I3
#   outputs: Redis 物化视图
# 层: 输出
# - id: O1
#   name_zh: H1 Redis 热缓存（因子截面/物化视图）
#   name_en: H1 Redis hot cache
#   intro: 盘中 <5ms 可读的因子截面与持仓/信号/风控物化视图，供五大域在线消费
#   invariant: 单实例 + DB 号隔离（db0=sim/db1=live/db2=gov）
#   downstream: zephyr.factor ; zephyr.signal ; zephyr.risk ; zephyr.position ; zephyr.trading
# - id: O2
#   name_zh: 降级信号 H1RedisUnavailable
#   name_en: H1RedisUnavailable
#   intro: Redis 不可用时 Reader 抛出的降级信号，调用方走降级路径
#   downstream: 决策引擎调用方降级处理（内部使用）
# [/ALGO_FLOW]
#
# 边:
# I4 --> A1
# A1 --> A2
# I1 --> A2
# A1 --> A3
# I2 --> A3
# A1 --> A4
# I3 --> A4
# A2 --> O1
# A4 --> O1
# A3 --> O1
# A3 --> O2
"""
