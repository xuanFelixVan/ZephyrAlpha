---
ttl: task_bound
doc_type: report
title: 深度审查报告——I02 调度监控+metrics
object: I02 调度监控+metrics
target: src/zephyr/data/scheduler.py:2429（_MonitorHandler L2327-2396、start_monitor L2403、get_health L2252-2317）+ src/zephyr/data/metrics.py + src/zephyr/data/alerter.py
reviewer: GLM-5.3-Flash / st-deeprev-20260918
baseline: 2fa92002c3（HEAD=73d1d045；按工作区现状审）
date: 2026-09-18
status: 已审
---

# 深度审查报告：I02 调度监控+metrics（GLM-5.3-Flash / 基线 2fa92002c3）

## 1 对象快照
- 范围：监控 HTTP 三端点、CH 探活缓存线程（scheduler.py:686-768）、get_health 降级判定、metrics.py 全文、alerter.py 全文（告警=监控的执行下游，断链检测核心）。
- 前科核实：daily_crypto 错挂 executor——schedule.yaml L79-81 注释实证（原 light 执行器不存在；APScheduler 注册不校验，触发时才 Executor lookup failed 并移除 job，该任务自上线从未自动跑成）；2026-09-16 已改挂 default。**同类错误的结构性防线仍未建**（P2-1）。
- 测试：tests/zephyr/data/test_metrics.py 存在（未逐断言=长尾）。

## 2 六轴审查日志表
| 轴 | 发现 | 锚点 | 级 | 验证法 |
|---|---|---|---|---|
| E | P2-1 executor 悬空前科无启动防线：add_job 不校验 executor ∈ init_scheduler 五键，错名照常注册、触发时静默移除 job——换一个时段名即可复发 daily_crypto 同型事故 | scheduler.py:2096-2153 + schedule.yaml L79-81 | P2 | add_job(executor="light") 复现 lookup failed |
| E | P2-2 告警外推通道已裁撤（2026-09-15 Owner 裁定，alerter.py:28）：CRITICAL（CH 死/卡死清理/破损 part 隔离）只剩 logging+data/failures/*.json；调度器进程死亡时无人来拉、文件靠前端页面轮询（api_server 确有消费）——"断了没人知道"结构性存在 | alerter.py:28,87-121 + scheduler.py:746-762,805-811,1018-1023 | P2 | 停进程确认零主动外发；grep data/failures 消费方=frontend/dashboard/api_server.py |
| E | P2-3 `check_consecutive_failures` 全仓零生产调用——"连续3天失败升级 CRITICAL"（蓝图 §6.5）是死代码，持续失败永不升级 | alerter.py:195-218 | P2 | grep -rn check_consecutive_failures src/ 仅定义 |
| A | P2-4 进程死亡后 metrics.prom 僵尸存活：textfile 模式只读文件不判新鲜度，counter 冻结看似存活；文件无 writer pid/时间戳陈旧标记 | metrics.py:205-232 | P2 | kill 进程后观察抓取端序列继续出数 |
| A | `check_daily_failure_rate` 名为"单日"实为每调度周期各自判（2 任务 1 失败=50%>5% 必告警）——噪声源 | scheduler.py:440-441 + alerter.py:173-193 | P3 | 数 failures/_daily_summary 频次 |
| A | get_health 缓存过期判定（>3 间隔→stale）设计正确；探活线程尾 sleep 30s 收敛可接受 | scheduler.py:700-768,2274-2277 | 已查无 | 读码 |
| B | get_health 直读 metrics 私有 `_lock/_task_total/_uptime`——跨类耦合，重构即断 | scheduler.py:2294-2297,2308 | P3 | 重命名私有字段看 /health |
| C | /metrics /health /status 绑 0.0.0.0:9100 无认证=内网信息暴露（任务清单/拓扑）；HTTP 访问日志静默 | scheduler.py:2395-2415 | P3 | 外部主机 curl 9100 |
| D | daily_crypto 修复后 executor 引用全量核对：14 default/5 heavy/3 realtime/1+1 各盘中 ⊆ 五键——当前零悬空 | schedule.yaml vs scheduler.py:2195-2201 | 已查无 | grep executor 值对集合 |
| E | start_monitor 端口占用→静默降级无 HTTP 监控仅 warning；若无 Prometheus up==0 告警即盲区 | scheduler.py:2410-2422 | P3 | 占 9100 起调度器观察 |

## 3 SOTA 对照
- textfile collector 陈旧性是社区公认 pitfall（node_exporter 不做 staleness，官方建议带时间戳 metric 或监 mtime）——本项目未做，与 P2-4 对应。来源：Prometheus 官方文档模式（prometheus.io，2019-2025；本条未单独检索 URL=受阻如实记，检索预算用于 I01/I08 两题）。
- 告警分级+per-task 300s 冷却去重与 alertmanager group/repeat_interval 模式对等：**对等已有**。

## 4 缺陷清单
1. P2-1：add_job 前断言 executor 键存在（一行防线，直接封死前科复发路径）。
2. P2-2：确认外部看门狗→手机链路真实存在并演练；否则为 CRITICAL 恢复一条带外通道。
3. P2-3：接线或显式退役 check_consecutive_failures（规范预算净零：二选一）。
4. P2-4：metrics.prom 增加 writer_pid+write_ts gauge 供抓取端陈旧判定。
5. P3 组见 §2。

## 5 挂起疑问
- external_watchdog 配置存在但未审（属 OPS 域）——若其已提供带外告警链路，P2-2 降 P3；请收口方核对后定级。

## 6 完备性自评
六轴全查。长尾：test_metrics.py 未逐断言；tick 侧 metrics_server 归 I07 邻接未审；Prometheus 抓取端配置不在本仓=无法验证 up 告警存在性（受阻如实记）。
