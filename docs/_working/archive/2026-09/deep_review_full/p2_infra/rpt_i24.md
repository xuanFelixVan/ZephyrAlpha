---
ttl: task_bound
title: 深度审查作业簿——DatabaseService
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：DatabaseService（I24）

- 状态: **已审**
- 级别: P2｜类型: 基础设施
- 基线 commit: 2fa92002c3（工作区 HEAD=b80084c0df）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/infrastructure/database_service.py:86`（DatabaseService 类；get_clickhouse_conn :161，单例 :365）
- 生产调用方: ch_writer（:191 writer/default）、api_server（:82 admin/dashboard 槽）、quality_sentinel（:456 reader/quality_sentinel 槽）、backtest/core/data_handler（:371 reader/default）、backtest/core/n_trial_ledger（:397 reader/default）、ex_core/daban_load_producer（:474 reader/default）+ governance/infrastructure 系
- 测试文件: tests/db/test_db_auto_ops.py
- 备注: 2026-09-14 连接统一治本（Code: 181）对象；slot 槽位机制是治本产物

## 1 对象快照

- 审查范围：`database_service.py` 全文 399 行：governance SQLite 双连接（读写/只读 PRAGMA query_only）、depgraph PG per-thread 连接（threading.local + _live_pg_conns 注册表）、ClickHouse (role,slot) 进程级缓存连接（reader/writer/admin 三角色 + invalidate 自愈）、Redis 单例、health_check、atexit close_all、get_db_service 单例。
- 排除项：database_crud_mixin（9 个 CRUD 下沉件）、ch_config/redis_config（配置加载）、api_server/ch_writer 各自的执行层锁（在 I26/ch_writer 域，但本报告审「跨模块串行化契约」）。
- 测试覆盖概况：test_db_auto_ops 覆盖 init/健康检查；多线程并发执行场景未见。
- 材料包缺项：无近 N 天 Code:181/Simultaneous queries 报错频次统计（运行时证据包缺）。
- 变更热力：中高热区（2026-09-14 连接治本、5.64.2/5.64.5 三轮修复，均为并发事故驱动）。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| E 对抗 | **(reader,default) 槽执行无串行化**：ch_writer 有 _ch_lock 串行化 writer 槽（ch_writer.py:110, 443）、api_server 有 _ch_lock 串行化 dashboard 槽（api_server.py:79, 109-126）——但 data_handler/n_trial_ledger/daban_load_producer 领 (reader,default) 连接后**裸 execute 无锁**；clickhouse-driver Client 明示非线程安全（官方 FAQ：每线程须独立连接）；api_server 自己 2026-09-01 就实证过同型错误"Simultaneous queries on single connection" | database_service.py:161-214（无锁契约声明）vs data_handler.py:371-373, n_trial_ledger.py:397, daban_load_producer.py:474 + api_server.py:109-111 实证注释 + clickhouse-driver 官方文档（轴 F） | P2 | 两线程各持 get_clickhouse_conn(role="reader") 并发 execute 100 次，复现 Simultaneous queries/块交错 |
| E 对抗 | 契约缺口文档化缺失：get_clickhouse_conn docstring 只说"进程级缓存"，未声明「调用方必须自行串行化同槽 execute」——治本把连接收敛到单条，却把线程安全责任静默转嫁给各消费方，履行者（ch_writer/api_server）与未履行者（backtest 系）无审计差异 | database_service.py:162-175 | P2 | 读 docstring 确认无该契约声明 |
| B 上游 | dashboard 用 admin（base）账号（api_server.py:82-89，role="admin"）=前端查询链持有全权账号：RBAC 收紧（#ARCH-CH-027 reader/writer 分权）后 dashboard 是残留例外——端点 SQL 若有内插面（I26 审）则升级为注入+DDL 双风险 | database_service.py:168-170（admin=base 账号注释）+ api_server.py:82-89 | P2 | `SHOW GRANTS FOR base`；api_server 端点 SQL 内插扫描（归 I26） |
| A 深度 | governance SQLite 双连接：check_same_thread=False+WAL+busy_timeout 30s+autocommit（sqlite_factory.py:67-88）——跨线程安全依赖「单 Writer 假设」（注释自认）无机械强制；两连接对象跨线程裸共享无锁 | sqlite_factory.py:68-88 + database_service.py:110-134 | P3 | 双线程并发写同一读写连接压测 |
| A 深度 | _live_pg_conns 只增不减（除 close_all）：每线程 2 连接注册，连接 closed 后引用仍留列表（get_depgraph_conn 重建时不摘除旧引用）——长命进程+线程churn 下列表缓增（内存微量） | database_service.py:157-158, 104 | P3 | 模拟 100 线程创建销毁后 len(_live_pg_conns) |
| C 下游 | health_check 全部吞异常返回 bool：CH 断连时 get_clickhouse_conn 返回的是**半开旧连接**→health=False 但连接仍被缓存——health 检查不触发 invalidate（invalidate 义务在各消费方 except 里），健康检查失败后系统自愈依赖下一个消费方碰壁 | database_service.py:289-294 vs :216-228 | P3 | 手工断网跑 health_check 再恢复，观察连接是否复用坏态 |
| D 旁系 | 三套 SQL 入口并存：DatabaseService（本件）、ch_reader/ch_writer（data 域）、api_server _ch_exec（dashboard 槽）——宪法 §9.1 说 DatabaseService 唯一真源，data 域实际走 ch_writer 连接体系（经 get_db_service 领 writer 槽，兼容但叙事上双轨） | 本件定位 vs ch_writer.py:185-191 | P3 | code review |
| E 对抗 | admin 角色无 extra_kwargs settings 合并时的 settings 键：reader 有 readonly=1、writer/admin 无任何 settings 默认——admin 槽若被误用于业务查询无护栏 | database_service.py:186-195 | P3 | code review |

## 3 SOTA 对照

| 对照项 | 结论 | 来源 |
|---|---|---|
| clickhouse-driver Client 线程安全模型 | **对等已有（风险确证）**：官方文档明示"each cursor should use its own connection"（Client 非并发安全）；GitHub issue #18 多线程混用实证——本对象单连接跨线程共享必须配套调用方串行化，凡未配者即踩官方明示红线 | clickhouse-driver 官方文档 Features 页, clickhouse-driver.readthedocs.io, 2025：https://clickhouse-driver.readthedocs.io/en/latest/features.html ；Multithreaded client issue #18, github.com/mymarilyn/clickhouse-driver, 存档：https://github.com/mymarilyn/clickhouse-driver/issues/18 |
| 连接池模式（pool per role/slot） | **立卡候选**：业界标准=Queue 池（clickhouse_pool/clickhouse-client-pool）或 per-thread Client；本项目 (role,slot) 单连接+槽级自锁混合模式在两处已自锁，剩余裸用槽立卡改「DatabaseService 内置 per-slot execute 锁」一次性根治（代价=全查询串行，reader 槽可扩池） | clickhouse-pool, openapps.pro/packages/clickhouse-pool, 2025；clickhouse-client-pool, github.com/lroolle/clickhouse-client-pool, 2025（同批次检索） |
| 连接自愈（validate-on-borrow） | 对等已有偏弱：业界池（DBUtils/SQLAlchemy pool_pre_ping）在借出时自动探活；本对象 invalidate 靠消费方 except 自觉——health_check 不触发重建，弱于业界 | SQLAlchemy pool_pre_ping 文档, docs.sqlalchemy.org, 2025（同批次检索域） |

## 4 缺陷清单

1. **D-1（P2）(reader,default) 槽三消费方裸 execute 无串行化**
   - 现状→证据：见轴 E 第一行。爆炸半径=backtest 系并发跑时间歇性 Simultaneous queries/半开连接，正是 2026-09-14 治本想根治的 Code:181 家族病的变体（治了连接构造，没治执行并发）。
   - 建议修法：①最小改：DatabaseService 增加 per-(role,slot) execute 包装（`execute_serialized(role, slot, sql, params)` 内置锁），三消费方迁移；②文档改：docstring 加粗声明「同槽并发须调用方自锁」，并 grep 全消费方审计留痕；③backtest 系单线程跑则登记豁免理由。
   - 验证法：轴 E 并发复现脚本；修后压测 0 错。
2. **D-2（P2）dashboard 持 admin（base）全权账号**
   - 建议：给 dashboard 建只读账号或 reader 角色专用槽（readonly=1 服务端强制）；若历史依赖 DDL（DESCRIBE 之外的操作需核 I26），收敛权限面。
   - 验证法：切 reader 槽回归 api_server 全端点。
3. **D-3（P3）health_check 不触发自愈**：检查失败顺手 invalidate 对应槽，让下一消费方拿到新连接。
4. **D-4（P3）_live_pg_conns 泄漏式增长 + governance 连接「单 Writer 假设」无强制**：登记性修复（重建时摘旧引用；写锁或至少 docstring 升级为硬契约）。
5. **D-5（P3）admin 槽无默认 settings 护栏**。

## 5 挂起疑问

- backtest data_handler/n_trial_ledger 是否存在同进程多线程并发消费 reader/default 的实际场景（若永远单线程串行，D-1 降级为潜在面）。
- api_server 是否有端点执行非 SELECT（决定 D-2 权限收敛可行性）——归 I26 深查。
- Redis 单例连接的 decode_responses 与业务消费方实况未审（Redis H1 热缓存使用面小）。

## 6 完备性自评

- 六轴全查：A（双连接模型/线程安全逐条）、B（ch_config fail-closed 上游）、C（消费方清单 7+ 全列）、D（SQL 三轨叙事）、E（并发五问：静默=无、假阳性=health bool、重放无关、时序=D-1 核心）、F（官方文档双源确证线程安全红线）。
- 长尾：database_crud_mixin 9 CRUD 未逐行审；Redis 连接池参数未审；PG per-thread 连接在 APScheduler 线程池回收后的 socket 复用行为未实测。
