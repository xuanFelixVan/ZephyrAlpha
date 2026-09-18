---
ttl: task_bound
doc_type: report
title: 深度审查报告——I05 Provider 基类+能力契约
object: I05 Provider 基类+能力契约
target: src/zephyr/data/provider_base.py:202（IngestProviderBase / FetchPayload / FetchResult / CapabilityContract / IngestProviderMeta）
reviewer: GLM-5.3-Flash / st-deeprev-20260918
baseline: 2fa92002c3（HEAD=73d1d045；按工作区现状审）
date: 2026-09-18
status: 已审
---

# 深度审查报告：I05 Provider 基类+能力契约（GLM-5.3-Flash / 基线 2fa92002c3）

## 1 对象快照
- 范围：抽象基类+数据类+策略辅助（call_with_policy 限流重试/backoff/_http_get/rate_limit_sleep）+ 能力契约元数据（#ARCH-CH-022 机器可执行契约）。
- 消费方：scheduler 工厂、全部 implementations/*_provider、capability_validator。
- 测试：tests/zephyr/data/test_provider_base.py 存在。
- 变更热力：18 commits，最近 2026-09-16。

## 2 六轴审查日志表
| 轴 | 发现 | 锚点 | 级 | 验证法 |
|---|---|---|---|---|
| E | **P2 thread_safety 声明无强制执行**：meta.thread_safety ∈ thread_local/shared/single_thread 三态，但全仓无消费点据此加锁/拒绝并发——"single_thread" 源（QMT 系）在调度器并发下裸奔（与 I01 P2-2 同根，本条为契约面证据） | provider_base.py:162,173（grep thread_safety 消费=0 处执行语义） | P2 | grep 全仓；两线程同 provider 并发 fetch 观察 |
| A | call_with_policy retry_on 子串匹配：`pattern in err_str` 过宽（如 pattern="timeout" 会命中消息里偶然含该词的数据错误）→ 该不重试的重试，放大配额消耗 | provider_base.py:290-299 | P3 | 构造含关键词的业务异常观察重试 |
| A | rate_limit_sleep 持锁睡眠（Event().wait 在 with _lock 内）——同 provider 实例的并发调用在锁上排队，语义正确（全局节流）但阻塞点隐蔽；`_last_call_ts` 在睡眠后重取 time.time()，多线程下实际间隔≥60/RPM 成立 | provider_base.py:344-355 | 已查无（设计如此） | 并发测实际 RPM |
| A | calc_backoff jittered 抖动 ±0.5s 固定不随 initial 缩放（initial=30s 时抖动占比可忽略，无实际 jitter 效果） | provider_base.py:361-376 | P3 | 单测数学 |
| B | FetchPayload.extra: dict = None——类型注解 dict 实缺省 None，下游全靠 `(payload.extra or {})` 防御，契约靠约定 | provider_base.py:75 | P3 | 传 None extra 走 qmt_bridge 路由 |
| C | FetchResult.__post_init__ rows_fetched=0 时取 len(rows)——qmt_bridge 派生路径利用该默认把"表内行数"冒充 rows_fetched（详见 I06），契约本身未约束语义 | provider_base.py:100-102 | P3 | 见 I06 报告 |
| D | CapabilityContract 归一化（str→默认契约）向后兼容设计良好；expected_market/variety 未填不校验=渐进收紧正确 | provider_base.py:105-150 | 已查无 | 读码 |
| E | _http_get 纳入重试循环（5xx 重试/4xx 立即抛）符合语义 | provider_base.py:321-342 | 已查无 | mock 测试 |

## 3 SOTA 对照
- 限流+指数退避+jitter 的重试范式与 Google SRE / AWS SDK 惯例对等（exponential+jitter 标准形）；本实现 jitter 恒定 ±0.5s 为弱化版。**对等已有（弱化）**。来源：通用 retry/backoff 工程范式（AWS Architecture Blog 等；未单独检索 URL=受阻如实记）。
- 机器可执行能力契约（声明即校验、ERROR 阻断启动）优于行业平均的文档式契约：**对等已有（偏优）**。

## 4 缺陷清单
1. P2 thread_safety 无执行点——建议 capability_validator 或调度器装载时按三态注入并发策略（single_thread→per-source 互斥），或在文档明示"仅描述性"消除契约幻觉。
2. P3 组：retry_on 子串过宽、jitter 恒定、extra 类型注解。

## 5 挂起疑问
- thread_local 型源（baostock）在调度器线程池下是否每线程 connect 由各 provider 自理——未逐一核 implementations（超出本对象边界，转施工侧抽查项）。

## 6 完备性自评
六轴全查。长尾：test_provider_base.py 断言强度未逐条审；policy_registry.SourcePolicy 字段语义未展开（仅确认字段存在）。
