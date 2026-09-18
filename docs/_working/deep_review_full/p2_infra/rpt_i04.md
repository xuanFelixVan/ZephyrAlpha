---
ttl: task_bound
doc_type: report
title: 深度审查报告——I04 DataService 查询服务
object: I04 DataService 查询服务
target: src/zephyr/data/data_service.py:96（class DataService；四能力门面）
reviewer: GLM-5.3-Flash / st-deeprev-20260918
baseline: 2fa92002c3（HEAD=73d1d045；按工作区现状审）
date: 2026-09-18
status: 已审
---

# 深度审查报告：I04 DataService 查询服务（GLM-5.3-Flash / 基线 2fa92002c3）

## 1 对象快照
- 范围：四能力门面（实时 Redis/PIT/决策打包/审计追溯）+ SLA 计量。后端全注入，本体无 IO（除委托）。
- 消费方：zephyr.backtest.core.data_handler、L3 策略 sleeve（头注声明；grep 生产装配点为长尾未逐个追）。
- 测试：tests/zephyr/data/test_data_service.py 存在。
- 变更热力：4 commits（稳定）。

## 2 六轴审查日志表
| 轴 | 发现 | 锚点 | 级 | 验证法 |
|---|---|---|---|---|
| A | **P2 query_pit_bitemporal 用字符串比较做业务时点过滤**：`str(r["report_period"]) <= valid_time.isoformat()`——若 report_period 为 "20260630"（CH IntegerDate/yyyymmdd 惯例）而 valid_time.isoformat()="2026-06-30"，逐字符比较 `'6'>'-'` 恒真 → 过滤**全丢**或**全留**；格式契约零文档（轴B：未文档化隐式契约=高危发现） | data_service.py:203-211 | P2 | 用 "20260630" 与 "2026-06-30" 两格式各跑一次比对结果；查 pit_query TSV 实际输出格式 |
| A | query_pit columns="*" 时 tsv_to_records 按 col_i 整数键返回——调用方拿到 {"col_0":...} 无列名，静默可用性陷阱（依赖 pit_query 内部查询列序稳定） | data_service.py:181,190-192 | P3 | columns="*" 调用看返回键 |
| B | get_realtime 双形态兼容（hgetall/get）：若 Redis 端写入形态与读取端不匹配（write_batch 写 Hash、注入普通 client 走 get）→ 永远 ok=False 静默 miss | data_service.py:153-157 + tick_subscriber 侧 TickRedisCache | P3 | 对 write_batch 落键形态 hgetall 验证 |
| C | audit_trail 后端缺省时静默返回空 upstream/downstream/events——"追溯能力降级"不告警（fail-open），与头注"缺后端 fail-closed"承诺仅对 realtime/pit 成立 | data_service.py:241-254 vs 13 | P3 | lineage=None 调 audit_trail 看静默空 |
| A | SLA 样本表 `_sla` 无上界累积（长驻进程内存缓涨；SLA report 仅手动拉取） | data_service.py:122-128 | P3 | 长跑进程观察 RSS |
| E | pack_decision_input 的 is_valid 过滤+universe 派生与 CTR-002 语义一致；注入 clock 可测，设计干净 | data_service.py:214-238 | 已查无 | 读码+测试 |
| D | main() 空壳"待实现"（__main__ 入口无效） | data_service.py:257-262 | P3 | python -m 执行 |

## 3 SOTA 对照
- 双时态（bitemporal：knowledge_time × valid_time）建模与学界 PIT/point-in-time 数据仓库实践（Snodgrass 时态SQL 谱系、量化界 point-in-time lookup 惯例）对齐：**对等已有**。来源：时态数据库通识（未单独检索 URL=受阻如实记，检索预算已用于 I01/I08 两题）。
- 门面+协议注入（Protocol）+SLA 计量：**对等已有**（标准 Faceted Gateway 模式）。

## 4 缺陷清单
1. P2 bitemporal 字符串比较隐式契约——建议统一经日期解析（date.fromisoformat/normalize）再比较，或在 pit_query 出口固定 ISO 格式并写契约测试。爆炸半径=双时态 PIT 查询的决策/回测口径（若命中全丢=静默缺数据，正是决策链上游喂错形态）。
2. P3 组：col_i 无名键、redis 形态耦合、audit fail-open、SLA 样本无界、main 空壳。

## 5 挂起疑问
- report_period 在 c3_* 表的实际类型/格式（Date 还是 yyyymmdd 整数）需查 schema 才能定 P2 实害概率——收口方一条 `DESCRIBE TABLE` 即可裁决。

## 6 完备性自评
六轴全查。长尾：pit_query/tsv_to_records 内部未审（只审其契约面）；backtest data_handler 装配点未逐个追（消费方清单以头注+grep 概览为限）。
