---
ttl: task_bound
doc_type: report
title: 深度审查报告——I09 ch_reader 只读查询
object: I09 ch_reader
target: src/zephyr/data/ch_reader.py:95（inject_final/query/count/query_table，全文 177 行）
reviewer: GLM-5.3-Flash / st-deeprev-20260918
baseline: 2fa92002c3（HEAD=73d1d045；按工作区现状审）
date: 2026-09-18
status: 已审
---

# 深度审查报告：I09 ch_reader（GLM-5.3-Flash / 基线 2fa92002c3）

## 1 对象快照
- 范围：统一读层全文（FINAL 自动注入纯函数+三查询入口）。委托 ch_writer.query 执行。
- 消费方：backfill_checker、integrity_checker、catchup_guard、consensus_crosscheck、回测 data_handler 等（头注+grep 概览）。
- 测试：头注 [TESTS] 空——**全仓无专测，确认缺口**（本批 grep tests/ 无 ch_reader 文件）。
- 变更热力：8 commits（稳定但正确性关键）。

## 2 六轴审查日志表
| 轴 | 发现 | 锚点 | 级 | 验证法 |
|---|---|---|---|---|
| A | **P2 FINAL 注入静默失效三通道**：①引擎缓存投毒（CH 故障后空串永久缓存，主锚 I08-P1）→ 注入永久关闭；②`_FROM_PATTERN` 只匹配 FROM 子句，**JOIN 表不注入**（`JOIN db.t2 ON...` 不经 FROM 匹配），Replacing 被联结表重复行进结果；③`re.search(r"\bFINAL\b")` 已有即跳过——SQL 含列名/别名为 `final` 的子句（如 `WHERE final=1`）误判已注入。三通道均静默（设计声明"引擎查询失败不注入=降级"，但降级=重复行，读方无感知） | ch_reader.py:51,77-92,86-89 | P2 | JOIN 两 Replacing 表查询 explain/查重复；构造含 final 列名 SQL |
| A | count() 失败返回 0——与"空表 0"不可区分：缺口探测/空表兜底（catchup_guard._table_is_empty 依赖）在 CH 故障时把"查不到"当"没数据"，反向放大误补跑/误判 | ch_reader.py:112-140 + catchup_guard.py:263-272 | P2 | 断 CH 跑 run_weekend_backfill 观察全表判缺（另见 I11） |
| A | query_table 字符串拼接 where/order_by——内部调用方可信，但无参数化通道，未来外部输入接入即注入面 | ch_reader.py:143-177 | P3 | 读码（登记性） |
| B | 降级链依赖 ch_writer.is_replacing_engine 的缓存——与 I08 投毒发现联动；query 失败返空串语义与写侧一致 | ch_reader.py:108-109 | P2（主锚 I08） | 见 rpt_i08 |
| C | FINAL 注入对 system.* 表跳过正确；对别名/子查询形态（FROM (SELECT...)）正则不匹配=不注入，行为安全 | ch_reader.py:51,80-90 | 已查无 | 正则单测 |
| D | 头注 INVARIANTS"保证查询返回去重后的数据"与 ②③ 通道现实不符——文档承诺强于实现 | ch_reader.py:8,20-29 | P3 | 对读 |

## 3 SOTA 对照
- FINAL 读取去重策略与官方权衡一致（去重保证 vs 查询开销），官方同时指出 FINAL 是"便利性换性能"，大表建议 argMax/OPTIMIZE 路线——本项目统一 FINAL+自动注入属安全优先，正确性缺口在三通道静默失效而非选型。**对等已有（选型）+立卡候选（失效通道收口）**。来源：ClickHouse 官方 ReplacingMergeTree 文档 https://clickhouse.com/docs/concepts/features/operations/update/replacing-merge-tree（ClickHouse Inc.，2024-2026）；Tinybird 同题 https://www.tinybird.co/blog/clickhouse-replacingmergetree-example（Tinybird，2024）。

## 4 缺陷清单
1. P2 FINAL 注入三通道静默失效（引擎缓存投毒主因在 I08，本模块需补：JOIN 表注入+final 词法误判收敛+失效时显式告警而非静默）。
2. P2 count() 0 值语义合并——建议失败返 None 或抛（调用方显式降级）。
3. P3 where 拼接注入面登记；头注承诺与实现对齐。

## 5 挂起疑问
- 回测 data_handler 等读方是否已在 SQL 手写 FINAL（若有则 ② 的实际暴露面缩小）——grep FINAL 消费 SQL 属收口方复核项。

## 6 完备性自评
六轴全查。长尾：无测试文件=无法审测试本身（缺口本身即发现）；消费方 SQL 形态全量普查未做（抽查为准）。
