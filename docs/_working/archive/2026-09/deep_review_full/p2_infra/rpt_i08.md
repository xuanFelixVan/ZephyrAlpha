---
ttl: task_bound
title: 深度审查报告——I08 ch_writer 统一写入
object: I08 ch_writer统一写入
target: src/zephyr/data/ch_writer.py:757（write_tsv_outcome L757-829；get_client L153-213；全文 1066 行）
reviewer: GLM-5.3-Flash / st-deeprev-20260918
baseline: 2fa92002c3（HEAD=73d1d045；按工作区现状审）
date: 2026-09-18
status: 已审
---

# 深度审查报告：I08 ch_writer 统一写入（GLM-5.3-Flash / 基线 2fa92002c3）

## 1 对象快照
- 范围：唯一写入口——HTTP INSERT 主路径+本地落盘兜底（WriteOutcome 三态）、TCP query/delete、表列/引擎缓存、RBAC writer 凭据、质量门禁挂点、health_check。
- 消费方：scheduler/buffered_writer/wal_writer/local_replay/backfill_checker/ch_reader/tick 链——爆炸半径=全仓数据写入。
- 测试：tests/zephyr/data/test_ch_writer.py 存在。
- 变更热力：44 commits（返工密集：列缓存死信/连接自愈/RBAC 等事故修复史在注释中可考）。

## 2 六轴审查日志表
| 轴 | 发现 | 锚点 | 级 | 验证法 |
|---|---|---|---|---|
| A | **P1 引擎缓存投毒→FINAL 永久失效**：get_table_engine 在 query 失败/表不存在时把空串写入 table_engine_cache 且无失效路径（invalidate_table_schema_cache 只清两个列缓存不清引擎缓存）；CH 短暂不可达后，is_replacing_engine 恒 False → ch_reader FINAL 注入全表关闭 → Replacing 表重复行静默返回给全部读方，直至进程重启 | ch_writer.py:741-744,647-656（对照列缓存 L624-627 提前 return 不缓存=行为不一致） | P1 | CH 停 30s→恢复→查 is_replacing_engine("c1_market.kline_daily") 返回 False；invalidate 后仍 False |
| A | **P1 主写入路径绕过质量门禁**：apply_quality_gate 仅 write_result 调用（L907-925）；调度器主力=BufferedWriter→write_tsv_outcome 直达，未经四门禁——quality_flag 保持默认 1（未校验行与通过行同标记，质量旗语义失真，checklist #4 双承载漂移同族） | ch_writer.py:907-925 + buffered_writer.py:167-206（无 gate 调用）+ gov quality_gate.py:145 注释自证 | P1 | grep apply_quality_gate 调用面；对 buffered 写入行查 quality_flag 分布 |
| E | delete_where 失败仅返回 False，调度主路径忽略（双写——主锚 I01）；DDL 经 query() 成败同返空串，调用方无从判定（依赖事后验证，如 _isolate_part 的 find_part 复核） | ch_writer.py:954-982,427-484 | P2 | delete 失败 mock；query("ALTER...") 返回值 |
| A | HTTP 主路径 INSERT 失败后 invalidate_table_schema_cache（列缓存自愈，2026-09-14 死信事故治本）正确；但 4xx 与 5xx 都会失效缓存+落本地——数据错（列不匹配）也进 local_fallback，回灌再失败=死信循环（有 create_fallback=False 防复制，风险有界） | ch_writer.py:788-815 | P3 | 构造列错批观察 fallback/回灌行为 |
| B | RBAC writer 凭据经 get_secret_or_default（RULE-SECRETS 合规）；密码走 header 不进 URL | ch_writer.py:75-83,330-339 | 已查无 | 读码 |
| A | tsv_escape：\x00 删除+控制字符→空格+反斜杠转义完备；float inf 输出 "inf" CH 侧可能 parse 失败（fail-fast 可接受） | ch_writer.py:519-539 | P3 | inf 单测 |
| E | health_check 全局态篡改窗口（清 ch_client/_tcp_fail_ts 探测后恢复）：并发写入线程在窗口内可能拿到被恢复覆盖的新连接/旧连接——竞态窗口小且有冷却自愈 | ch_writer.py:1024-1064 | P3 | 并发 health_check+write 压测 |
| C | 本地兜底语义=LOCAL_DURABLE 三态区分（禁把本地持久化伪装 CH 已提交）设计正确；回灌 create_fallback=False 防复制闭环 | ch_writer.py:118-143,757-829 | 已查无 | 读码+rpt_i01 关联 |
| D | SQL_INSERT_TSV 显式 async_insert=0+BufferedWriter 攒批=可控微批（见 §3）；HTTP query GET 传长 SQL 受 URL 长度限制（长 IN 列表场景） | ch_writer.py:91-93,465-471 | P3 | 万级 IN 单测 |

## 3 SOTA 对照
- 微批 INSERT（async_insert=0 + 应用层攒批）vs 官方 async_insert：ClickHouse 官方当前推荐大数据量批量插入、async_insert 用于高并发小批；本项目应用层攒批（BufferedWriter）达到同等效果且投递结果可判（三态），**对等已有（应用层实现）**。来源：ClickHouse 官方文档《Deduplication》《ReplacingMergeTree》https://clickhouse.com/docs/concepts/features/operations/insert/deduplication 、https://clickhouse.com/docs/concepts/features/operations/update/replacing-merge-tree（ClickHouse Inc.，2024-2026）；Altinity《ReplacingMergeTree: the good, the bad and the ugly》https://altinity.com/blog/clickhouse-replacingmergetree-explained-the-good-the-bad-and-the-ugly（Altinity，2023-2024）。
- FINAL 读取去重 vs argMax/OPTIMIZE FINAL 替代：官方明示 FINAL 有查询时开销且随表增长——本项目全量 FINAL 注入在表大后需评估 argMax 模式：**立卡候选**（读侧性能改造点，非正确性问题）。

## 4 缺陷清单
1. **P1 引擎缓存投毒**：修法=get_table_engine 失败（空串）不缓存（对齐列缓存行为）+invalidate_table_schema_cache 一并清引擎缓存。爆炸半径=所有 Replacing 表读方（回测 data_handler/巡检计数/交叉验证）。
2. **P1 质量门禁旁路**：修法=把 apply_quality_gate 下沉到 write_tsv_outcome 或 BufferedWriter._init_columns 后逐批调用（eff_cols 可得）；爆炸半径=调度器主链全部行。
3. P2 DDL/delete 语义弱返回——修法=DDL 专用返回 bool 或异常。
4. P3 组见 §2。

## 5 挂起疑问
- quality_gate 对 rows 的 flag 置 0 改写与 BufferedWriter 列过滤索引的交互（若下沉需复验 keep_indices 对 quality_flag 列的过滤）——施工侧注意点，非审查结论。

## 6 完备性自评
六轴全查。长尾：test_ch_writer.py 未逐断言；local_replay 死信存量规模未查（需 CH 权限）；fetch_perf_recorder/quality_gate 内部算法未审（边界外）。
