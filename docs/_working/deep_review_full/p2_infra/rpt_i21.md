---
ttl: task_bound
doc_type: report
title: 深度审查作业簿——CH parts监控
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：CH parts监控（I21）

- 状态: **已审**
- 级别: P3｜类型: 管线
- 基线 commit: 2fa92002c3（工作区 HEAD=b80084c0df）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/data/ch_parts_monitor.py:119`（check_and_alert）
- 生产调用方: scheduler.py:445（时段写库收尾，B5 接线）+ CLI main()（巡检脚本）
- 测试文件: tests/zephyr/data/test_ch_parts_monitor.py
- 备注: MATURITY=testing 头注与"生产接线"现状不符（见 D-5）

## 1 对象快照

- 审查范围：`ch_parts_monitor.py` 全文 178 行：阈值 fail-closed 统读（THD-HEALTH-005，实测注册表值 30/单分区口径）、system.parts 按分区聚合探测、TSV 容错解析、Alerter CRITICAL 告警、CLI 巡检入口。
- 排除项：BufferedWriter 攒批（parts 产生根因侧，另一对象）；threshold_loader 内部（下游依赖，契约=缺文件 raise）。
- 测试覆盖概况：单测在（口径修正 2026-09-03 后应已同步，未逐用例核）。
- 材料包缺项：无近 N 天 parts 告警触发记录（运行时证据包缺）；未实测当前各表单分区 parts 基线。
- 变更热力：9 次提交，低中热区（2026-09-03 口径修正 100→30 + 分区级判定是最近实质变更）。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| D 旁系 | 文档三处漂移：①模块 docstring ">100 告警"（:21）②check_and_alert 参数注"默认 100，64号 Q8 裁定"（:137）——注册表实值 30（2026-09-03 Owner 拍板，registry:197-198）；③"触达飞书 webhook + SMTP 邮件"（:131）——外推通道 2026-09-15 已裁撤（alerter.py:28）。与"注册表唯一真源"自述矛盾（文档承载旧值） | ch_parts_monitor.py:21, 131, 137 vs alert_threshold_registry.yaml:195-199 + alerter.py:28 | P3 | 读三处对比即证 |
| E 对抗 | CH 查询失败→返回 []（"宁漏报不误报阻断"，:105-109）：parts 爆炸最严重的形态恰是 CH merge 满载响应超时——监控在目标事故场景下最盲；查询连续失败无独立告警计数器 | ch_parts_monitor.py:104-109 | P2 | 注入 query_fn 抛异常，确认无 notify 且返回 []；连续失败亦然 |
| A 深度 | 阈值 import 期冻结（DEFAULT_PARTS_THRESHOLD 模块级常量，:54）：注册表改值需重启调度进程才生效——与"统读热生效"预期有隙；fail-closed（缺文件 import 即炸）是有意取舍 | ch_parts_monitor.py:53-54 | P3 | 改 registry 值后不重启调用 check_parts_threshold()，仍旧值 |
| A 深度 | `_SQL_ACTIVE_PARTS` 全库聚合无 WHERE db 过滤：system 表/元数据表也进 TSV，库大时解析量增大（当前规模可忽略）；GROUP BY 无 HAVING，传输全部分区行 | ch_parts_monitor.py:60-63 | P3 | 实跑看行量（收口方） |
| B 上游 | ch_reader 失败返回空串（契约）→ parse 空列表→ [] 与"健康"同构——同 I16 D-3 的盲区结构，本对象因失败路径有 log.warning（:108）而稍好 | ch_parts_monitor.py:66-70 + ch_reader.py:99 | P3 | code review |
| C 下游 | CLI main() 文案仍按"表"口径打印（"无表 active parts 超阈值"），且 violations 打印不含 partition 字段（:171-173 丢 partition 信息）——巡检输出与分区判定口径不同步 | ch_parts_monitor.py:165-174 | P3 | 造违规数据跑 main() 看输出 |
| A 深度(测试) | 未见"查询异常→[]"与"CLI 口径"用例（如测试文件已覆盖则本条收回） | tests/zephyr/data/test_ch_parts_monitor.py | P3 | grep 测试断言 |

## 3 SOTA 对照

| 对照项 | 结论 | 来源 |
|---|---|---|
| ClickHouse 内生 parts 背压（parts_to_delay_insert 默认 1000 / parts_to_throw_insert 默认 3000，超限 INSERT 变慢直至拒绝） | **对等已有+立卡候选**：CH 官方 MergeTree 设置已内置同型防护（延迟/拒写两级），本项目监控阈值 30/分区比内生阈值严格一个数量级=早期预警价值成立；**立卡**：DDLSide 建表显式收紧 parts_to_delay_insert/throw（如 150/300）可把"告警后人肉介入"升级为"自动背压"，与本监控互补 | ClickHouse 官方文档 MergeTree settings（parts_to_delay_insert/parts_to_throw_insert）, clickhouse.com, 2025：https://clickhouse.com/docs/reference/settings/merge-tree-settings ；知识库 Too many parts 调优, clickhouse.com, 2025 |
| system.parts active parts 巡检 SQL 模式 | **对等已有**：与官方社区监控 SQL（GROUP BY database,table,partition + count active）一致，且本对象"按单分区判定"的 2026-09-03 口径修正与官方建议口径相同 | 同上 clickhouse.com 文档域 + 官方 system.parts 表文档, 2025 |
| 批量写入防 parts 爆炸（batched/async insert） | 对等已有：BufferedWriter 攒批（裁定 #ARCH-CH-003）即官方 best practice（大批量/async_insert），项目已落地 | 同上官方文档 insert 性能页, 2025 |

## 4 缺陷清单

1. **D-1（P2）目标事故场景下的监控盲区无二级防线**
   - 现状→证据→影响：CH 超时/不可用（parts 爆炸的典型伴生症状）→ [] 静默（:105-109）；scheduler :446-448 外层再吞异常。爆炸半径=2026-07-09 型事故重演时监控恰在最需要时失明。
   - 建议修法：check_and_alert 维护"连续查询失败计数"（模块级或挂 scheduler 状态），≥3 次经 alerter 发 CH 探测失败 CRITICAL（与 parts 告警同通道，不需新通道）。
   - 验证法：query_fn 桩连抛 3 次断言 notify 被调。
2. **D-2（P3）三处文档漂移**（轴 D 行）：修 docstring 两处旧值+一处已裁撤通道描述；MATURITY=testing 改 production（已在调度主链上跑）。
3. **D-3（P3）阈值 import 冻结**：注册表改值需重启；若需热生效改函数内读取+短 TTL 缓存（当前低频改动可接受，登记即可）。
4. **D-4（P3）CLI 输出口径滞后**：文案与打印字段补 partition。

## 5 挂起疑问

- alert_rules.yaml ALERT-CH-001 的 Grafana 消费链是否真实存在（:22 自述"由遥测链路消费"，Grafana 未在本仓见部署证据）——若 Grafana 不存在则该行是幽灵引用。
- 当前各表单分区 parts 基线离 30 多远（需生产 CH 只读查询，审查环境未执行）。

## 6 完备性自评

- 六轴全查：A（阈值冻结/SQL 口径）、B（ch_reader 吞错契约）、C（scheduler 接线+CLI）、D（三处漂移）、E（失败盲区+双层吞异常）、F（ClickHouse 官方文档对照，已获真实 URL）。
- 长尾：threshold_loader 的 cast/畸形分支未逐行审（独立模块）；OPTIMIZE FINAL 清碎屑运维预案（registry:198 提及）未验证是否成文。
