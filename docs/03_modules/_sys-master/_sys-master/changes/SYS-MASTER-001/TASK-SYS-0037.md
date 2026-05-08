---
task_id: "TASK-SYS-0037"
source_blueprint: "SYS-MASTER-001"
source_section: "§96 数据生命周期管理与记忆存证 + §97 时间同步与时钟一致性 + §98 实时流式与异步处理 + §100 蓝图的增量式审查与可持续维护"

title: "数据生命周期五阶段(Create采集→Store存储→Use使用→Archive归档→Purge清除)+AutoHousekeep+数据遗忘权GDPR + 时间同步三级(硬件NTP→系统Time Sync→应用BusinessTs)+偏差监控(bias>50ms→拒绝信号) + 实时流式Batch/Stream双轨(行情订阅WebSock/订单+连接池 min10/断流处理)+FIFO+背压 + 蓝图增量审查(Chunk级标记/时间预算/一致性+指显+完整性6维评分) 四合一数据与运维管线"
description: |
  将 §96 数据生命周期 + §97 时间同步 + §98 实时流式 + §100 增量审查四合一落地为数据管线的完整性与运维保障。
  §96 定义：
  （1）五阶段——Create（行情API→采集→validate§29→打 timestamp+source_tag）· Store（热：行情日线~5yrs≤90day→ Redis·冷：≥5年→SQLite/Cloud）· Use（量化→因子/信号 不 破损源→可控 P oss deduc cons）· Archive（数据>7年→压缩归档 + 每月1次完整性校验 AutoHousekeep）· Purge（Owner清除 / >15年数据无用途→ Mark hor + cleaner→报告Owner）。
  （2）数据遗忘权（GDPR）——PII清洗：user/payment/email data 必须永久删除（provide cert）+ 存储加密· Audit trail（印记immutable history，power purge除外）→清除前Owner 5天公示+强制保留  Opp。
  §97 定义：
  （1）三级时间源——硬件NTP（pool.ntp.org + 每1min同步，<10ms jitter）· System Time Sync（Windows/Linux 使用 `w32tm` / `timedatectl`→Adherence <50ms drift）· Business 应用 Timestamp（所有生成逻辑ts = business逻辑⇨一致性（UTC+8,1ms）·business序列强一致性第γ⇒）。
  （2）偏差监控——H-NTP vs System >50ms → alarm=拒绝生成任何信号+拒绝生成新高频交易。
  （3）时间戳规范——所有日志/订单/行情 ts ISO8601（2026-05-03T09:30:00.123Z ）· 回测时钟 模拟 start=同步 start 到UTC真值 < 1ms pos。
  §98 定义：
  （1）双轨——Batch（日终抓数据→因子计算→adapt  no race） + Stream（实时行情WebSocket订阅→结构→洗→连续流入→引擎→信号0后缓存）。
  （2）基础设施——连接池（≥10保持连接 断自动重连· WS断流→FIFO暂存posters→背压阈值知报警>FIFO depth 1k paddl• 断流<2m→ notification Operator • 恢复← auto）。
  §100 定义：
  （1）增量式审查 Chunk——标记蓝图层（自L0<设计>~最新）· 时间预算（审查 ≤ 30 min/Chunk,跑量审查旧→心理标记慢 自动）。
  （2）审查质量六维——consistency(+semantic割裂检测)/accuracy(数字引用验证§0.2/路径)/completeness(with context manifest 字段) / traceability(正反向链路)/token_efficiency(审查Token/成果)/no_regression(high无下降→对比上次）。
  本卡搭建 data_lifecycle.py + time_sync.py + realtime_streaming.py + incremental_review.py。
priority: "P1"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_sys-master\\blueprint.md"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\data_lifecycle.py"
    description: "§96 5阶段(Create/Store/Use/Archive/Purge)+AutoHousekeep+遗忘权GDPR(Audit trail+5天公示)"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\time_sync.py"
    description: "§97 3级时间源(硬件NTP/System/BusinessTs)+偏差监控>50ms拒绝+ISO8601时间戳"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\realtime_streaming.py"
    description: "§98 Batch/Stream双轨+连接池≥10+FIFO暂存+背压1kpaddl+断流恢复"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\incremental_review.py"
    description: "§100 Chunk标记(L0-最新)+时间预算≤30min/Chunk+审查6维评分(一致性/准确性/完整性/追溯性/Token效率/无退化)"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\data_lifecycle.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\time_sync.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\realtime_streaming.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\incremental_review.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\l*\\**\\*.py"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_sys-master\\blueprint.md"
    reason: "§96 5阶段+GDPR遗忘 + §97 3级时间+偏差+ISO8601 + §98 双轨+连接池+背压 + §100 Chunk审查+6维评分"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 26000
timeout_minutes: 70

acceptance_criteria:
  - "data_lifecycle.py 实现 DataStage 枚举（CREATE/STORE/USE/ARCHIVE/PURGE）——CREATE(capture→validate§29→ts+source_tag)· STORE(hot <5yrs≤90d Redis/cold≥5yrs SQLite/Cloud)· USE(factor/signal no break+attr deduc cons)· ARCHIVE(>7yrs zip compress+monthly integrity check AutoHousekeep)· PURGE(Owner delete/>15yrs unused→mark+cleaner→report Owner)· GDPR(PII cleanse user/payment/email permanent delete+encrypt· Audit trail immutable except power purge→5day Owner announce+forced retain)"
  - "time_sync.py 实现 TimeSource（HARDWARE_NTP/SYSTEM_TIME/BUSINESS_TS）——NTP(pool.ntp.org per1min,<10ms jitter)· System(w32tm/timedatectl drift<50ms)· Business(所有逻辑ts=strong一致性 UTC+8 1ms· 偏差监控: NTP vs System>50ms→alarm reject signal+HFT)· TimestampSpec(ISO8601 2026-05-03T09:30:00.123Z· backtest clock simulate sync UTC true<1ms)"
  - "realtime_streaming.py 实现 StreamMode 枚举（BATCH/STREAM）——BATCH(eod grab→factor compute→no race)· STREAM(WebSocket sub→realtime行情→wash→continuous→engine→signal cache)· ConnectionPool(≥10 keep-alive auto reconnect· WS disconnect→FIFO temp store→backpressure>1k depth alert· disconn<2min notify Operator· restore auto)"
  - "incremental_review.py 实现 ChunkMarker——tag sections(L0 design→latest)· TimeBudget(≤30min per chunk, auto mental throttle slow)· Review6Dim——Consistency(+semantic fragmentation detection)· Accuracy(number+reference verify §0.2/path)· Completeness(context manifest fields)· Traceability(forward+reverse links)· TokenEfficiency(review tokens/output)· NoRegression(high→no decline vs last)——→ weighted composite score"
  - "script_manifest.yaml 注册全部 4 个 .py"

rollback_instructions: |
  1. 删除 data_lifecycle.py / time_sync.py / realtime_streaming.py / incremental_review.py
  2. 从 script_manifest.yaml 移除注册

depends_on:
  - "TASK-SYS-0034"
blocked_by: []
status: "done"
tags_fn:
  - "data"
tags_ly: "cross_layer"
tags_md: "deepseek"
tags_st: "active"
tags_mo:
  - "SYS-MASTER-001"
completed_gates: []
blocked_gates: {}
artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "supervised"
autonomy_checklist: []
---
