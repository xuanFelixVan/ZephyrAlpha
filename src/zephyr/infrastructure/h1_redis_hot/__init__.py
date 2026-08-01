# [BLUEPRINT] MOD-H1-REDIS-HOT | docs/03_modules/_cross_layer/database/sub_blueprints/h1_redis_hot.md
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
# [A_module] module_id=MOD-H1-REDIS-HOT | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""H1 Redis 热缓存模块——盘中实盘/模拟盘 <5ms 因子截面在线存储（DD-11-01）。

子模块：
    - h1_redis_schema: Key DDL（7类 Key 构造函数 + TTL/容量常量）
    - h1_redis_writer: D-FACTOR 批量因子截面写入（PIPELINE 模式）
    - h1_redis_reader: 决策引擎 <5ms 在线特征查询（降级 H1RedisUnavailable）
    - h1_cqrs_projectors: 事件→Redis 物化视图投影器（持仓/信号/风控）

部署：Redis 7.0.15 @ Hyper-V Ubuntu VM（172.24.30.100:6379，与 ClickHouse 同 VM，D1 决策）。
归属：MOD-INF-002（D2 决策：get_redis_conn 在 database_service.py）。
隔离：D3 决策——单实例 + DB 号隔离（db0=sim/db1=live/db2=gov），升级触发条件见蓝图 §8.3。
"""
