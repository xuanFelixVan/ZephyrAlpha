---
ttl: task_bound
completes_when: 全流通战役收官且最终交付报告落盘
---

# 静默失效模式扫查 · 处方集（不动手，交总包派工）

> 规则：真病例落在**他人独占文件**或**需要语义裁定**时不动手，只写
> `file:line + 病例描述 + 改法 + 能红测试设计`。本文件即交付物之一。
> 编号 `SILENT-Px-Rn`，派工时直接引用。

## P1 闩前置

### SILENT-P1-R1 · `src/zephyr/strategy_pipeline/pipeline_events.py`（residG 独占）
- 位置：`:193`（`log.debug('alerter 不可达', exc_info=True)`）、`:235`（receipt 落盘失败 DEBUG）、
  `:562`（audit marker 写入失败 DEBUG）。
- 病例：本文件是 `daily_decision_orchestrator._alert` 的默认下游。orchestrator 侧本车道已升 ERROR，
  **但 pipeline_events 自己把"告警器不可达/receipt 未落盘"记在 DEBUG** → 同一条链的一端可见、一端静默。
- 改法：三处 DEBUG→WARNING，并把 `alerter 不可达` 的 except 改为绑定异常名 + 打 `type(exc).__name__`；
  receipt/audit marker 落盘失败属"③出口有货"腿丢，应计数进 `summary`（与已收口的 F1 同构）。
- 能红测试设计：真 `pipeline_events` 对象 + `tmp_path` 作 receipt 根，把 receipt 父段做成普通文件
  → 断言 WARNING 记录存在且 receipt 计数 `!= 0`；旧实现在 WARNING 档位零记录 → 红。

### SILENT-P1-R2 · 计算型 `alerted` 字段的语义漂移（观察项，非缺陷判定）
- 位置：`data_eng/incremental_update_engine.py:156`、`pf_core/core/rebalance_cost_analyzer.py:227`、
  `gov_drift/agent_stability_index.py:242`。
- 描述：`alerted` 由阈值算出、在投递前赋值，语义是"**该告警**"。当前实现无误。
  风险：三处都把该字段随结果对象返回，若将来任何下游把 `alerted=True` 读成"已告警"，就会复刻 R-023。
- 建议（低成本消歧）：字段改名 `should_alert`，或在 dataclass 字段注释里钉死"非送达回执"。
- 能红测试设计：改名的话，加一条 grep 型测试钉 `assert "alerted: bool" not in src_of(...)`。

### SILENT-P1-R3 · `agent_stability_index.py:242` 的 `alerted = low == self._alert_consecutive`
- 病例：等号判据意味着**只在恰好第 N 个连续低窗出声一次**；此后 `low > N` 期间永不再报，且
  恢复（low 归零）没有任何消警/收敛事件。这是"去重闩 + 无恢复腿"的半闭环（§1 第⑥向缺腿）。
- 改法：加 `escalated` 状态位与恢复事件（与 F1 的"真落盘才置闩 + 恢复通知"同构）。
- 能红测试设计：真评估器连喂 5 个低窗 → 断言第 3 窗出声、第 4/5 窗进入"已升级"态而非"无事发生"；
  再喂一个正常窗 → 断言产出恢复事件。旧实现第二条必红。

## P2 恒真 / 硬编码返回

| 编号 | file:line | 恒真物 | 改法 | 能红测试设计 | 归属 |
|---|---|---|---|---|---|
| SILENT-P2-R1 | `src/zephyr/trading/boot_hooks.py:132` | `return "healthy"` 被 `register_system_health` 注册成**永不失效的活体探针** | 让 boot_hooks 自己维护一个 `hook_register_failures: list[str]`（各 `except` 分支 append），探针按该表返回 `healthy/degraded` | 真调用 boot 序列 + 把某个 hook 的依赖打成真故障 → 断言注册后的探针函数返回 `degraded`；旧实现恒 `healthy` → 红 | 需 Max 定"degraded 是否阻断 boot" |
| SILENT-P2-R2 | `src/zephyr/gov_enforcement/rule_enforcement/secrets_guard.py:28` | `check_env() -> True`（RULE-SECRETS 名义上的"三道 gate"之一） | 真实现（按 `REQUIRED_KEYS` 查 `secrets.py`）或**删/标 aspirational 并禁止计入能力清单** | 缺 key 的环境里断言 `check_env() is False`；旧实现 → 红 | 净删触注册表门位 |
| SILENT-P2-R3 | `src/zephyr/infrastructure/rollback/temporal_context_adapter.py:149`（+ `:56`、`:153` 明文密钥） | `_verify_hmac() -> True`，即**时间证明 HMAC 永不校验失败**；同文件两处明文密钥常量 | 实现真比较（`hmac.compare_digest`）+ 密钥走 `zephyr.secrets` | 用 A 密钥签、B 密钥验 → 断言 False；旧实现恒 True → 红 | 密钥类改动建议 Owner 知情 |
| SILENT-P2-R4 | `src/zephyr/orchestrator/lifecycle/system_transfer.py:29` | `verify_health_after_transfer() -> True`（BRK-003 整族零消费） | 与 L0_lifecycle 族接线一并裁 | 移交后：注入一个失败的子系统健康 → 断言 False | BRK-003 |
| SILENT-P2-R5 | `src/zephyr/gov_audit/corporate_actions.py:97` | `verify(sample_count=10) -> True`（**复权因子校验永不失败**） | 真抽样比对（源因子 vs 落库因子），失败返回 False + 差异明细 | 构造一只故意错乘数的因子表 → 断言 False；旧 → 红 | **钱路径，优先级最高** |
| SILENT-P2-R6 | `src/zephyr/feedback_loop/detectors/drift/concept_drift.py:34` | `check(...) -> 0.0`（漂移恒零） | 真统计量（PSI/KS）或标 `aspirational` | 喂两个明显不同的分布 → 断言 > 0 | BRK-011 |
| SILENT-P2-R7 | `src/zephyr/security/llm_defense/llm_security/layers/*.py`、`self_protection/l7_validation.py` | **30+ 个 `validate/check_*/verify_* -> True` 常量返回层桩**（LSG 七层防御的部分层默认实现是放行） | 逐层二选一：实现 或 `NOT_IMPLEMENTED` 显式抛 + 在 `FAIL_OPEN_LAYERS` 口径里登记"该层未实现" | 反向断言：未实现层必须让 `is_fail_closed()` 报 False，否则装配期 fail-closed 拒绝启动 | 安全架构级；与 BRK-048 判定同期裁 |

补充：`scripts/governance/meta/validate_emergency_bypass_log.py:127 _check_post_audit -> True`
（应急绕过审计的后校验恒真）与 `autonomy_core/skills/skill_executor.py:181 verify -> True`
一并纳入 P2-R7 的"恒真校验桩"同一批处置。

## P4 DEBUG 级放行

| 编号 | 位置 | 描述 | 改法 |
|---|---|---|---|
| SILENT-P4-R1 | `src/zephyr/data/implementations/akshare_provider.py`（约 25 处 `self._log.debug(f'…失败: {e}')`） | 逐 symbol 循环内降级 | **禁机械升级**（会造海量 WARNING）。正解=循环内计数、循环外聚合报一条 WARNING/告警，并保留 per-symbol DEBUG | instL 独占 |
| SILENT-P4-R2 | `pipeline_events.py:193/235/562/929` | 见 P1-R1 | 同上 | residG 独占 |
| SILENT-P4-R3 | `data/scheduler.py:563/1532`、`data/tick_subscriber.py:522/552/667` | 唤醒钩子注册失败、表存在性前置校验失败、Redis 缓存写失败均只 DEBUG | 表存在性校验失败应 WARNING（它决定后续是否走全量）；Redis 写失败应计数进 tick 健康指标 | z-failopen 独占面 |
| SILENT-P4-R4 | `src/zephyr/trading/boot_hooks.py:281/296/313/340/512/522/539/587` | **8 处治理/保命钩子**自身异常只留 DEBUG：`rbac_readiness_check`、`rbac_audit_sign`、`rbac_kill_switch_check`、`skill.freshness_critical`、`escalation_check`、`timeout_check`、`budget_delta`、`triple_align_event` | 与 SILENT-P2-R1 **同批改**：钩子异常 → 计入 boot 失败位 + WARNING（含真实类型名），健康探针据此报 degraded。单改日志等级会造"看得见失败但没人判"的半吊子 | 需 Max 定门位 |
| SILENT-P4-R5 | `src/zephyr/data/redundant_source/sqlite_fallback.py:199/209`、`trading/finalizer.py:93/103`、`trading/auto_task_generator.py:193/383`、`ex_core/live_strategy_adapter.py:385` | 兜底/清理/回执读取失败只 DEBUG | 逐条判：属"正常路径"的降级为 DEBUG 合理，属"回执未落"的须升 WARNING | 中低优先 |

## P5 兜底日志预设失败类别（10 条）

| 编号 | file:line | 现措辞预设 | 风险 |
|---|---|---|---|
| SILENT-P5-R1 | `src/zephyr/data/ch_writer.py:511` | "writer 无权限时需管理员预建" | 宽 `except Exception`；实为网络/编码错误时被读成权限问题（`apply_rbac.py` 会被误调） |
| SILENT-P5-R2 | `src/zephyr/data/implementations/eia_provider.py:203`、`fred_provider.py:251/274`、`qweather_provider.py:265` | "网络不可达，可能需 VPN" | 探活失败常见真因是**接口改版/返回 None**（BRK-033 三接口即此病），会被统一读成网络问题 |
| SILENT-P5-R3 | `src/zephyr/data/implementations/miniqmt_provider.py:622` | "账号可能无 L2 权限" | 与 BRK-032 权限缺口登记耦合，误归因会掩盖真故障 |
| SILENT-P5-R4 | `src/zephyr/gov_audit/delegation_bridge.py:83` | 函数名含 timeout，日志未带类型 | 归因面窄化 |
| SILENT-P5-R5 | `src/zephyr/governance/resilience_governance/f5_event_subscriber.py:304`、`f5_shutdown_manager.py:558` | `handle_deadlock failed` / `idle timeout callback error` | **停机/死锁处理路径**上的误导归因代价最高 |
| SILENT-P5-R6 | `src/zephyr/shared/infra/process_incubator.py:394/412` | "refused (concurrent writer)" | 把可能的路径/权限错误读成并发竞争；进程收割器归因错的先例在前 |
| SILENT-P5-R7 | `src/zephyr/risk/paper_hedge_leg.py:419` | "alerter 不可达" | z-land2 独占 |
| SILENT-P5-R8 | `scripts/commit_queue.py:1594` | "REG-ATH-001 不可达" | 队列健康面 |
| SILENT-P5-R9 | `scripts/backtest/promotion_combo_gate.py:94/116`、`scripts/ch/{backfill_research_report_2025,backfill_research_report_full,purge_news_data_rr_dup,rebuild_news_data,rebuild_news_data_tz2,tag_news_category}.py` | "不可达（降级）" | 批脚本，低优先 |
| 统一正解 | — | — | `logger.warning("…: %s: %s", type(exc).__name__, exc, exc_info=True)`，正文不写失败类别 |
