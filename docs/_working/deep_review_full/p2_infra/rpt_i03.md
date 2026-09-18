---
ttl: task_bound
doc_type: report
title: 深度审查报告——I03 数据CLI
object: I03 数据CLI
target: src/zephyr/data/cli.py:333（_build_parser 及 8 子命令；start 入口 L268-312）
reviewer: GLM-5.3-Flash / st-deeprev-20260918
baseline: 2fa92002c3（HEAD=73d1d045；按工作区现状审）
date: 2026-09-18
status: 已审
---

# 深度审查报告：I03 数据CLI（GLM-5.3-Flash / 基线 2fa92002c3）

## 1 对象快照
- 范围：integrator CLI 8 子命令（status/list/run/rerun-failed/pause/resume/start/speed-test）+ get_integrator 单例 + _load_dotenv。
- 测试：tests/zephyr/data/test_data_cli.py 存在（头注自述仅 1 个 AST 测试锚定，覆盖薄）。
- 变更热力：21 commits，最近 2026-09-16。

## 2 六轴审查日志表
| 轴 | 发现 | 锚点 | 级 | 验证法 |
|---|---|---|---|---|
| E | **P1 pause/resume 紧急熔断对常驻调度器无效**：CLI 在自己进程内 `registry.register(replace(policy, enabled=False))`——纯内存变更（policy_registry.register 无任何落盘，grep 证实无 yaml.dump/write）；生产调度器是另一常驻进程，`policy.enabled` 读的是它自己进程内的 registry，且 CLI 未写 policies.yaml 触发不了 maybe_reload。紧急熔断按钮实际熔的是空气 | cli.py:218-257 + policy_registry.py:258（无持久化）+ scheduler.py:1841-1844 | P1 | 起常驻调度器，另开终端 `integrator pause akshare`，观察该源任务照常执行 |
| A | rerun-failed 语义漂移：docstring"重跑今日失败任务"，实现 `list_failed_tasks()` 取 last_status=FAILED **不限日期**——数周前已废弃源的失败任务会被反复重跑 | cli.py:190-215 + progress_store.py:266-278 | P3 | 造一条上周 FAILED 记录跑 rerun-failed |
| B | pause 的正确生效路径其实存在但未被使用：scheduler 侧 maybe_reload 会重读 policies.yaml——CLI 若写回 YAML 即可跨进程生效；现实现绕开了它 | cli.py:233-235 vs scheduler.py:2499-2500 | P3 | （同 P1 验证） |
| C | `_cmd_start` 与 scheduler.main() 双入口重复（锁/信号/常驻循环三段复制）——改一处漏一处的经典温床 | cli.py:268-312 vs scheduler.py:2445-2503 | P3 | diff 两段逻辑 |
| A | status/list 只读，访问 `integrator._progress_store` 私有成员（Stage 4 公共化未覆盖此二处） | cli.py:123,196 | P3 | 读码 |
| D | 头注宣称"8 子命令"与 [INVARIANTS] 一致，handlers 表 8 键核对一致 | cli.py:8,408-417 | 已查无 | 对表 |
| E | run/rerun-failed 与常驻调度器并发跑同一任务：两边各自实例+各自 progress 锁（SQLite WAL+lock 串行化），任务级无互斥——手动 run 可与 cron 周期同任务并发（同源 Provider 双实例，反而规避了 I01 的共享实例并发，但产生双写竞争） | cli.py:174-187 + scheduler.py:1444 | P3 | cron 窗口内手动 run 同任务，查表行数 |

## 3 SOTA 对照
- CLI 管理命令应作用于运行中守护进程：业界标准=信号/控制文件/socket/AdminAPI（如 systemctl/celery remote control 模式）。本对象 in-memory-only 变更属反模式。结论：**立卡候选**（pause/resume 改写 policies.yaml 或经 /status 端点加 POST 控制口）。来源：celery remote control / systemd 惯例（通用工程知识；未单独检索 URL=受阻如实记，检索预算已用于 I01/I08）。

## 4 缺陷清单
1. **P1 熔断失效**：pause/resume 仅本进程内存生效。建议：写回 policies.yaml（借道 maybe_reload 生效）或走监控端口控制面；短期至少在 CLI 输出里显式警告"仅影响本进程，常驻调度器不受影响"。验证=双进程演练。
2. P3：rerun-failed 无日期过滤；_cmd_start 重复实现；私有成员访问。

## 5 挂起疑问
- 若 Owner 实际运维惯例是"暂停=改 policies.yaml+等热更新"，则 pause 子命令属误导性死功能而非资损路径——P1 定级请收口方按实际运维剧本复核（发现本身=行为与宣称不符，证据确凿）。

## 6 完备性自评
六轴全查。长尾：speed_tester 模块内部未审（本对象只验证转发）；test_data_cli.py 断言强度未审。
