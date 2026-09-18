---
ttl: task_bound
doc_type: report
title: 深度审查作业簿——数据源策略注册
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：数据源策略注册（I17）

- 状态: **已审**
- 级别: P2｜类型: 管线
- 基线 commit: 2fa92002c3（工作区 HEAD=b80084c0df）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/data/policy_registry.py:188`（PolicyRegistry 类）
- 生产调用方: zephyr.data.scheduler（:505/:1839 熔断检查）、zephyr.data.cli（pause/resume/speed-test）、zephyr.data.backfill_checker（:740）
- 测试文件: tests/zephyr/data/test_policy_registry.py
- 备注: —

## 1 对象快照

- 审查范围：`policy_registry.py` 全文 290 行：SourcePolicy 数据类、DEFAULT_POLICIES 常量（8 源）、PolicyRegistry（load_yaml/maybe_reload/get_policy/register）、模块级单例 get_registry()。
- 排除项：scheduler 侧熔断器（circuit_breakers，64号 Q17）属另一对象；cli.py 只审 pause/resume 与本对象的交互面。
- 测试覆盖概况：单测存在；重点审 pause 生命周期与热更新交互（测试未覆盖跨进程/重载冲掉场景）。
- 材料包缺项：无运行时证据包（未见 pause 相关事故记录）；config/policies.yaml 已实测读取比对。
- 变更热力：`git log --follow` = 16 次，中热区（#ARCH-RSS-INVESTING-403-001 等治本批多次触达 retry_on）。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| E 对抗 | **CLI pause/resume 是死控**：`_cmd_pause` 只改本进程内存 registry（register+print"已熔断"），常驻调度进程（`start` 子命令自进程 while 循环）完全不共享该状态，无文件落盘、无 IPC、无信号——紧急熔断对在跑的 daemon 零效果，重启后同样丢失 | policy_registry.py:258-261 + cli.py:218-236（register 即返回）+ cli.py:365（start 常驻进程）+ scheduler.py:1841（daemon 进程内读 enabled） | P1 | 起两个终端：A 跑 `python -m zephyr.data start`，B 跑 `python -m zephyr.data pause akshare`；观察 A 日志 akshare 任务照常抓取 |
| E 对抗 | 即使同进程，pause 状态也会被热更新冲掉：daemon 主循环每 60s maybe_reload()（mtime 变即重载），config_changed 事件 force=True 重载——load_yaml 按 yaml 键整只重建 SourcePolicy，yaml 无 enabled 字段→dataclass 默认 True，pause 被静默撤销 | cli.py:307 + scheduler.py:678-680, 1122-1124 + policy_registry.py:227-229（整只替换）+ :84（enabled 默认 True） | P1 | 同进程内：pause 后 `touch` policies.yaml，等下一轮 maybe_reload，get_policy('akshare').enabled 回 True |
| A 深度 | load_yaml 是**整只替换不是合并**：yaml 中某源只写部分字段时，其余字段回落到 dataclass 默认而非 DEFAULT_POLICIES 值——两套兜底语义不同（如 akshare 在 DEFAULT 有 disconnect_vpn=True，yaml 若删该键则静默变 False） | policy_registry.py:88-91, 227-229 vs :97-182 | P2 | yaml 临时只留 `akshare: {rpm: 60}`，对比 load 前后 get_policy('akshare').disconnect_vpn |
| B 上游 | yaml 解析无防御：`yaml.safe_load` 异常直接上抛（load_yaml 无 try），daemon 60s 循环里 maybe_reload 抛出会打断主循环的 Event().wait 流程（cli.py:307 无 try）；坏 yaml=调度循环中断 | policy_registry.py:224-225 + cli.py:304-308 | P2 | 向 policies.yaml 写入 `: : :` 后观察 daemon 循环 |
| B 上游 | from_dict 只过滤未知键不做类型校验：`rpm: "60"`（字符串）可入库，下游 `60/rpm` 类运算时才 TypeError，故障点远离配置点 | policy_registry.py:87-91 | P3 | 构造 `SourcePolicy.from_dict({'rpm': '60'})` 再参与限流计算 |
| D 旁系 | 双真源承载：DEFAULT_POLICIES（代码）与 config/policies.yaml 各一份 8+ 源策略，无一致性校验（模式 #4）；实测 yaml 键集=16 源（多出 akshare_alt/io_table/cls/fred/eia/qweather 等 8 个新源只在 yaml），qmt_bridge 只在 DEFAULT——两册已事实分叉，靠 load_yaml 覆盖掩盖 | policy_registry.py:97-182 vs src/zephyr/data/config/policies.yaml（16 键，无 qmt_bridge） | P2 | `python -c` 对比 DEFAULT_POLICIES 键集与 yaml 键集 |
| C 下游 | get_policy 未注册源返回 `SourcePolicy()`（rpm=0 不限流、respect_robots_txt=True、max_retries=3）却 log 声称"保守默认"——rpm=0=不限速对爬取源并不保守，反爬封 IP 风险 | policy_registry.py:250-256, :70-72 | P3 | `get_registry().get_policy('nonexistent')` 查 rpm |
| E 对抗 | 竞态窗口小但存在：load_yaml 在锁外读文件+解析，锁内应用——两线程并发 reload 时后写者胜，无版本号防回退（旧数据覆盖新数据可能性低，因读同一文件） | policy_registry.py:223-232 | P3 | code review 即证 |
| A 深度(测试) | 测试未覆盖：pause→reload 冲掉、yaml 部分字段回落语义、类型错误注入——恰是本对象三个最痛分支 | tests/zephyr/data/test_policy_registry.py | P3 | grep 测试文件无 reload+pause 组合用例 |

## 3 SOTA 对照

| 对照项 | 结论 | 来源 |
|---|---|---|
| 客户端限流/重试策略集中注册表（per-source rate limit + retry policy as config） | **对等已有**：业界通用做法（requests-ratelimiter/tenior 配置化重试；API 网关 per-route policy）。本对象 yaml 热更新设计不落后 | Tenacity retry 文档, tenacity.readthedocs.io（2025 活跃）；requests-ratelimiter, GitHub v框架文档 2025 |
| 运行时熔断开关持久化（feature-flag/circuit-breaker state 需持久层或控制面） | **立卡候选**：业界控制面（如 LaunchDarkly flag、Envoy admin endpoint）状态变更即时到达运行进程且有持久化；本对象 pause 走进程内存=偏离业界惯例，建议立卡改 flag 文件（与 `data/runtime/*.disabled` 项目惯例对齐）或落 yaml | Envoy admin / circuit breaker 文档, envoyproxy.io, 2025；LaunchDarkly feature flag persistence 概念文档, launchdarkly.com |

## 4 缺陷清单

1. **D-1（P1）紧急熔断跨进程失效且不持久**
   - 现状→证据→影响：见轴 E 第一行。CLI pause 打印"已熔断"=假完成状态（模式 #12 近亲）：操作员以为断了，daemon 继续打源，反爬封 IP/数据污染窗口敞开。
   - 建议修法：pause/resume 改写 `data/runtime/source_pause/<source>.flag`（对齐 consensus_crosscheck.disabled 惯例），daemon 在 `_should_run` 检查；或落 policies.yaml enabled 字段经既有热更新生效。
   - 验证法：双终端实验（轴 E 行）；修后 B 终端 pause，A 终端 60s 内任务跳过。
2. **D-2（P1）热更新撤销 in-memory 熔断**
   - 同轴 E 第二行。修 D-1 即顺带治本；若暂不改，至少 load_yaml 合并时保留既有 enabled 状态（`dataclasses.replace(old, **new_fields)`）。
   - 验证法：pause 后 touch yaml 观察是否复活。
3. **D-3（P2）整只替换语义使两套兜底漂移无感**（模式 #4）
   - 建议修法：load_yaml 改为「以 DEFAULT_POLICIES 为底、yaml 字段级覆盖」；或加一致性自检（load 后对共同键断言与 DEFAULT 不冲突的字段数并 log）。
   - 验证法：删 yaml akshare.disconnect_vpn 键，断言加载后仍为 True。
4. **D-4（P2）坏 yaml 打断 daemon 主循环**
   - 建议修法：maybe_reload/load_yaml 捕 yaml.YAMLError→log.error+保持旧策略（fail-safe 保留现场），并告警一次防刷屏。
   - 验证法：写坏 yaml 后 daemon 日志出现 error 且调度继续。
5. **D-5（P3）未注册源"保守默认"名不副实**：rpm=0 建议改为显式 `rpm=30` 等保守上限，或未注册源直接拒绝抓取（fail-closed）。
6. **D-6（P3）DEFAULT_POLICIES 与 yaml 键集分叉无巡检**：qmt_bridge 只在代码、8 个新源只在 yaml；建议任务侧加启动断言 log 差集。

## 5 挂起疑问

- pause 是否存在我未发现的远程通道（如 dashboard api_server 转发）？已 grep scheduler/cli 未见，若 dashboard 有独立 pause 端点则 D-1 降级为"CLI 路径失效"。
- scheduler.py:642-645 的 policy_registry setter（Stage 4 公共化）允许外部整体替换 registry——谁在用 setter 未查到调用方，可能是测试专用，建议收窄。

## 6 完备性自评

- 六轴全查：A/B/C/D/E/F 均有结论；数学四问对本对象=策略参数语义，已按限流/退避参数逐项过（backoff 三模式由 provider 消费，未在本对象展开）。
- 长尾：provider 侧（provider_base）如何消费 rpm/backoff 未逐行审（属 P2 数据管线另一对象）；DEFAULT_POLICIES 各源参数值本身的合理性（如 tushare rpm=200 与积分档位匹配）依赖运营手册，未实证。
