---
ttl: task_bound
title: T1-β 节点挖矿：数据进料全链路（供应商→校验→入库→特征可用）
session: st-qoder-mining-20260917
date: 2026-09-17
parent: S11_assembled_backtest
lane: I
---

# 节点挖矿：数据进料全链路（父环节 S11_assembled_backtest）

> 范围：一条行情/基本面数据从**供应商**到**特征可用**的全链路真实接线状态——CLI 面、
> provider→校验→ch_writer 入库、断更检测、缺桶/延迟可观测性、Fail-Closed 方向，
> 并用 ≤90 交易日真抽样判定"字段在 ≠ 数据可得"。
> regime 标签消费侧（F1-F4）已由 `regime_supply_chain_mining.md` / `risk_overlay_mining.md` 覆盖，
> 本文只在"进料口断供会被下游怎么吞掉"的交界处点名。
> 全部结论 AST/实测锚定：`file:line` 或现网数字。探测件（只读）在 `.runtime/tmp/mining_{ingest,gates}_20260918/`。

## 1 现状盘点（宣称 → 验真/验伪）

### 1.1 CLI 面：constitution 宣称 7 子命令，实测 8

| 宣称 | 验真结果 |
|---|---|
| `AGENTS.md` §7 + `src/zephyr/data/cli.py:21` docstring："7 个子命令…+ speed-test" | **验伪**。`src/zephyr/data/cli.py:375-387 get_subcommands()` argparse 实测 8 个：status / list / run / rerun-failed / pause / resume / start / speed-test。同文件 `:8` INVARIANTS 头反已改口"8子命令"→ **头注释与 docstring 在同文件内互相矛盾**（docstring 是 stale 侧） |
| 实测 `python -m zephyr.data --help` | 8 子命令全在，rc=0，无异常 |
| 实测 `python -m zephyr.data status` | 正常产出：`providers: (无已连接)`、`task_count: 230`、`已加载调度计划: 21 档时段`；并 WARN `[TableRegistry] task 'pattern_evidence_certify' table 'c1_market.market_pattern_certification' 未在 business_data_categories.yaml 注册（双真源漂移风险）` |
| 调度器是否在跑 | **在跑**：`ZephyrAlpha_DataScheduler` State=Running（`Get-ScheduledTask` 实测），`ZephyrAlpha_CHHealthProbe` Running，`ZephyrAlpha_DeadmanSwitch` Ready |

### 1.2 进料口"校验层"：三层宣称，两层零生产消费方

| 件 | 宣称 | 实测接线（AST 反向 import 索引，`.runtime/tmp/mining_gates_20260918/chain_wiring.json`） |
|---|---|---|
| `data/quality_gate.py` → `gov_enforcement/rule_enforcement/quality_gate.py` | 写前四门禁 | **真接线**：唯一生产调用点 `src/zephyr/data/ch_writer.py:910-912` |
| `data/cross_source_validator.py` | 跨源交叉校验 | **零生产消费方**：全仓仅 `tests/zephyr/data/test_cross_source_validator.py` import 它 |
| `data/cleaning_rule_engine.py` | 清洗规则引擎 | **零真实消费方**：仅 `src/zephyr/data/__init__.py:33,74` re-export + 自身测试，无任何调用点 |
| `data/source_sla_tracker.py` | 源 SLA 追踪 | **零生产消费方**：仅 `tests/data/test_source_sla_tracker.py` |
| `data/auto_backfiller.py` | 自动补数 | 仅 `src/zephyr/data/__init__.py` re-export + 测试 → **调度器不吃它**；实际补数走 `backfill_checker.run_daily_backfill`（`scheduler.py:214-218`） |
| `data/heartbeat_monitor.py` / `redundant_source/` | 主备源切换 | **真接线**：`src/zephyr/runtime/intraday_main.py`、`redundant_source/{recovery,source_switcher,tick_subscriber}` 共 8/12 处生产 import |

### 1.3 "冻结/退役"在 tasks.yaml 里是**注释**，不是字段——调度器照跑

`src/zephyr/data/config/tasks.yaml`（3139 行 / 230 任务）字段频率实测：
`task_id/table/source/schedule/incremental/dependencies/symbols/extra` 各 230，`capability` 229，
**`enabled` 出现 0 次、`status`/`state` 出现 0 次**。机器可读的停用只有一条路：`schedule: disabled`，全仓**仅 1 个**（`dividend_incremental`）。

注释自称"退役冻结 2026-09-18 / 表从未产出"的 4 个任务，`schedule` 字段仍指活档期：

| 任务 | 注释宣称 | 实测 `schedule` | 实测目标表 |
|---|---|---|---|
| `sector_list_refresh`（L1703） | "退役冻结…现阶段保持冻结 disabled 不动" | `intraday_realtime` | `c1_market.sector_list` = **5217 行**（表存在） |
| `repurchase_refresh`（L1832） | "miniQMT 独有源，表从未产出" | `daily_event` | `c3_fundamental.repurchase` = **6010 行** → **注释为伪** |
| `margin_trading_qmt_placeholder`（L1846） | "表从未产出" | `daily_capital` | `c1_market.margin_trading_qmt` → CH 报 `Code 60 Unknown table`（**表不存在**） |
| `dragon_tiger_qmt_placeholder`（L1860） | "表从未产出" | `daily_capital` | `c1_market.dragon_tiger_qmt` → 同上，**表不存在** |

即：注释级"冻结"对 `IntegratorScheduler` 无约束力；两个任务每天向**不存在的表**写入。

### 1.4 断更检测：399106 供应商侧治本"已落地"= 代码在、档期无

上一批的 P0（399106 广度断更）供应商侧根修件已入库，但其**回归面**为 0：

| 件 | 状态 |
|---|---|
| `src/zephyr/data/implementations/internal_compute_provider.py:808 _fetch_kline_index_breadth` / `:827-841 _fetch_breadth_freshness_sentinel` | 代码在（capability 注册 `:118-119`，路由 `:475-483`） |
| `src/zephyr/data/implementations/breadth_freshness_alerts.py`（311 行，专为"让断更可见"而写） | 代码在，阈值 `_ALERT_TRAILING_DAYS=2 / _CRITICAL_TRAILING_DAYS=5 / _SCAN_LOOKBACK_DAYS=60` |
| 档期 | **不存在**：`tasks.yaml` 内 `kline_index_breadth` / `breadth_freshness_sentinel` / `kline_index_breadth_refresh` 三个 task_id 全查无；`schedule.yaml` 21 档期亦无对应挂载 |
| `breadth_freshness_alerts.py:236,288` 自报 `feed_task: "kline_index_breadth_refresh"` | 指向**不存在的 task_id** → 告警件的"进料任务"归属自指空 |
| 真抽样（`.runtime/tmp/mining_ingest_20260918/probe_breadth.py`） | `399106` 零值段 2026-07-03→2026-09-15 共 **53 行**；10 只成分指数 universe 整体自 ~07-20 起停更；`899050` 07-02 后**整行缺失**；`EQW_ALLA`（内部重算旁路）在跑 → **真源坏、旁路掩** |
| 若哨兵今天被调度 | 实测 `scan()` 干跑将产 **10 条 critical** —— 全被"无档期"吞掉 |

### 1.5 Fail-Closed 方向：进料口每一层都把"无数据"改写成"健康"

| 层 | 落点 | 方向（实测） |
|---|---|---|
| 读 | `src/zephyr/data/ch_writer.py:427-460` | 空结果与传输失败**同返回值 `""`** → "无数据" ≡ "CH 不可达"，93 个 `ch_reader` 生产 import 方全部继承该歧义 |
| 读 | `src/zephyr/data/ch_reader.py:112-140 count()` | 失败 → `return 0`（`:13` ERROR_CONTRACT 自认） |
| 校验 | `src/zephyr/gov_enforcement/rule_enforcement/quality_gate.py:23` | 宣称"不合格数据**拒绝下发**"→ **验伪**：`:281-282,341-343` 只把异常行 `quality_flag=0` 后**原样返回**，无一行被拒 |
| 校验 | 同上 `:297,301,305` 门禁 2/3/4 | 无基准即 `return True`（"保守放行"）→ 缺 prev_close / 缺 open / 缺 adj_factor 的行**判康** |
| 校验 | 同上 `:341-343` | `if qf_idx is not None` → 表**无 quality_flag 列**时判定结果直接丢弃；实测 `index_kline_daily`、`market_breadth_daily` `system.columns` 查无此列（`has_qflag_col: false`）→ 指数/广度这两张 regime 主粮表**校验结果无处落地**，只剩 `:345` 一条 INFO 日志 |
| 写 | `src/zephyr/data/ch_writer.py:924-925` | `except Exception → log.warning("quality_gate 跳过")`，注释原文"质量门禁失败不得阻断写入" |
| 调度 | `src/zephyr/data/scheduler.py:1671-1692` | 0 行 → `#ARCH-SILENT-SUCCESS`：`log.warning` + `alerter.notify(level=LEVEL_WARN)`；`:1682-1684` 的理由注释"日志无人盯，告警才可见"为**伪**（见下行） |
| 告警 | `src/zephyr/data/alerter.py:117-119` | `notify()` 仅 `ERROR/CRITICAL` 落 failure 文件；`WARN/INFO` **不写任何产物却 `return True`** → WARN 级"0 行成功"零留痕 |
| 告警 | `alerter.py:195 check_consecutive_failures` / `:222 list_failure_files` / `:238 read_failure_file` | AST 实测生产调用方 **0** → 连续失败升级逻辑是死代码 |
| 熔断 | `scheduler.py:1779` | "源 {source} 已熔断，任务跳过" → 跳过的任务记 SUCCESS 还是 FAIL 取决于该源恢复时机，非硬阻断 |
| provider 路由 | `scheduler.py:1044,1076-1142` | route-meta 缺失仅 WARN，注释自认"Phase 4 … 将升级为 block"（未升级） |
| 下游 | `src/zephyr/regime/regime_feature_builder.py:573-574 .fillna(0)` / `:370,:506 np.nan_to_num` | 缺数据→0（"无涨跌"），与 `:577-604 _load_breadth` 的 `dead=(adv<=0)&(dec<=0)` 补洞只打 INFO、`:606-635 _load_breadth_fallback` 失败"维持 0 填充旧行为"叠加 → 断更在特征层被翻译成"市场平静" |
| 下游 | `regime_feature_builder.py:812-817 _safe_query` | 头注释称失败抛错，实测不可能抛（同 `""` 歧义链） |

## 2 六向挖矿日志表

| 向 | 挖到的事实 | 证据 |
|---|---|---|
| ①上游（供应商） | miniQMT 通道 2026-09-18 退役，但 4 个 `source=miniqmt` 任务仍挂活档期；2 张目标表在 CH 不存在 | §1.3 表 |
| ①上游 | `daily_crypto` 曾因 executor 写成不存在的 `light` 而"自上线从未自动跑成过（水位全靠手动）"，2026-09-16 才修 | `src/zephyr/data/config/schedule.yaml:70-73` |
| ②下游（特征可用） | 90 交易日抽样：`kline_daily` 88/90 天，缺 `2026-09-16`、`2026-09-17`（tail_missing）；`kline_index`、`kline_index_calc` 同缺同两天 | `.runtime/tmp/mining_ingest_20260918/gap_probe.json` |
| ②下游 | 特征层把缺失当平静 | §1.5 末两行 |
| ③机制（校验） | 四门禁全"保守放行"，且无 flag 列的表判定丢弃 | §1.5 校验三行 |
| ③机制（可观测） | 09-16 EOD 批：`data/failures/` 实测 62/155 成功，CH 侧 09-16 全天缺 → 失败可见但**只在 dashboard 拉 `data/failures/*.json` 时才可见**（`api_server.py:1312`），且 `_FAILURE_COOLDOWN_SEC=300`（`alerter.py:56`）把同任务重复失败压成一条 | 实测 + 代码 |
| ④后端（观测件） | `integrity_checker` 每日巡检确有档期（`schedule.yaml integrity_check: "00 23 * * 0-4"`，`scheduler.py:220-224` 特殊时段派入 `run_daily_check`），但 `_check_table_today` 阈值 ≤0 时返回 `healthy: True, skipped: True`（`integrity_checker.py:153-201`），`run_tick_duplication_check` 脚本缺失/不可达 → `degraded`"巡检降级不阻断"（`:204-250`），`_should_run_today`（`:73-85`）无时分模型 | 代码 |
| ④后端 | 补跑是**静默**的：`catchup_guard`（`schedule: 30 5 * * *`）`scheduler.py:226-230` → `catchup_guard.py:247-257` 只有"补跑失败"才 ERROR 落文件，单纯"超期"是 WARN=零留痕 | 代码 |
| ⑤前端 | `services_registry.py:132` 对 `deadman` 的自述："核心服务心跳停超 10 分钟，自动给你**飞书**发警报" → **验伪**：`scripts/deadman_switch.ps1` 全文无 webhook/feishu，告警面只有 `tmp/deadman_switch_alerts.log`（实测 3,603,096 字节，末次 09-16 22:24）+ Windows 事件日志（`:202-211`），且 `:178` 无 stale 即 `exit 0` 静默。飞书/SMTP 已于 2026-09-15 裁撤（`alerter.py:8,28`、`api_server.py:4355`） | 实测 |
| ⑤前端 | 运维告警面板 `OpsAlertFeed` 唯一非调度生产方 `scripts/governance/generators/generate_resource_week_view.py:252` 的 `--publish-alerts` 是 `action="store_true"` **默认关**（`:275-281`）→ 实测 `.runtime/ops_notifications/notifications.jsonl` **不存在**，面板从未收到一条记录 | 实测 |
| ⑥数据字段 | `quality_flag` 消费覆盖：AST 提取 `FROM *kline_daily` 静态 SQL 字面量 **41 条，仅 10 条带 `quality_flag=1` 谓词（24%）**；未过滤含 `frontend/dashboard/api_server.py:226,292`、`data/implementations/akshare_provider.py:222`、`index_eqw_compute.py:72`、`industry_graph/*` 回测件 | `.runtime/tmp/mining_ingest_20260918/kline_daily_sql.json` |
| ⑥数据字段 | CH 真抽样（窗口 2026-05-14→2026-09-17，90 交易日）：`kline_daily` `quality_flag=1` 486,903 行 / `=0` **10 行**（0.002%）→ 门禁实际拦截面近乎为零 | `qflag_ch.json` |

## 3 业界与开源对照（四闸）

| 候选做法 | 来源可溯 | 交叉验证 | A股适配 | 可回测+数据可得 | 裁定 |
|---|---|---|---|---|---|
| 入湖即校验 + 不合格行**拒写**并计数（Great Expectations / Soda "fail the pipeline"） | ✅ | ✅ 本仓 §1.5 证伪现方案 | ✅ | ✅ 纯代码 | **采纳**：进料口至少一条硬拒路径 |
| Data-contract：provider 未产 schema/未达最小行数即 job 红（"no data is a failure, not a success"） | ✅ | ✅ | ✅ | ✅ | **采纳**：0 行 SUCCESS 必须红 |
| 新鲜度 SLO + 双水位（arrival vs completeness，Airflow `execution_date`+`data_interval` / Monte Carlo 五维） | ✅ | ✅ | ✅ | ✅ | **采纳**：`catchup_guard` 现只有一条 WARN |
| 列级数据质量标记 + 消费侧强制过滤 | ✅ | ⚠️ 本仓 flag 覆盖 24% | ✅ | ✅ | **部分采纳**：先补"无 flag 列"的表 |
| 供应商多源实时互校（cross-source median） | ✅ | ✅ | ⚠️ A股免费源同时刻同源，伪冗余 | ✅ 但需 tick 历史 | **挂起**：`cross_source_validator` 先接线再谈扩展 |

## 4 堵点与欠账清单

| ID | 级别 | 病灶类 | 堵点 | 可施工验收标准 |
|---|---|---|---|---|
| ING-1 | P0 | 自欺骗-调度 | miniQMT 退役 4 任务只改注释不改 `schedule`，2 个每日写不存在的表（§1.3） | `tasks.yaml` 内注释含"退役/冻结/停用"的任务 `schedule` 必为 `disabled`；新增门禁断言"`source` 在 `policies.yaml` 已注册源集"且"`table` 在 CH `system.tables` 存在"；`dividend_incremental` 之外 `schedule: disabled` 计数 1→≥5 |
| ING-2 | P0 | 断更回归面 | 广度真源仍停更（53 零值行 + 899050 缺行），`kline_index_breadth_refresh` / `breadth_freshness_sentinel` 无档期，`feed_task` 指向不存在 task_id（§1.4） | `tasks.yaml` 新增两任务且 `schedule` 指活档期；`python -m zephyr.data list` 可见；连续 3 交易日 `breadth_freshness_sentinel` 有行；干跑 alert 的 critical 数从 10 收敛到 0（或 10 条critical 有据可查地转为已裁定豁免） |
| ING-3 | P0 | 自欺骗-告警 | `alerter.notify` WARN 不写产物却返回 True；`check_consecutive_failures` 零调用；`--publish-alerts` 默认关致面板从未发布（§1.5/⑤前端） | `notify(WARN)` 有可查产物（面板或 failure 文件）；`.runtime/ops_notifications/notifications.jsonl` 存在且周内有增量；`check_consecutive_failures` 生产调用方 ≥1；`services_registry.py:132` 文案与实际通道一致 |
| ING-4 | P1 | Fail-Open | 质量门禁"保守放行"三处 + 无 flag 列丢弃 + `ch_writer` 异常跳过（§1.5） | `index_kline_daily`/`market_breadth_daily` 补 `quality_flag` 列或等价旁表；`apply_quality_gate` 对"无基准"行返回 `unknown` 而非 `True` 并被计数；`ch_writer:924` 异常改为按表级白名单硬阻断；抽样窗口内 flagged 数不再为 0.002% 量级 |
| ING-5 | P1 | 观测 | `quality_flag` 读侧覆盖 24%，dashboard/回测件吃脏行 | 关键消费清单（api_server 行情块、`index_eqw_compute`、`industry_graph/backtest_*`）SQL 带 `quality_flag=1` 或显式登记豁免理由；AST 复测覆盖率 ≥80% |
| ING-6 | P1 | 契约歧义 | `""`/`0` 同义于失败（`ch_writer.py:427-460`、`ch_reader.py:112-140`） | 读接口返回 `(ok, value)` 或抛错；`count()` 失败不得为 0；回归测试覆盖"CH 不可达"与"表空"两分支 |
| ING-7 | P1 | 巡检 | `integrity_checker` 阈值≤0 → `healthy:True,skipped:True`；tick 查重脚本缺失 → `degraded` 不阻断；`_should_run_today` 无时分模型（④后端） | `skipped` 计入不健康；`degraded` 连续 2 日升级为 ERROR 落文件；巡检"当日应到未到"判定用 trading calendar + 档期 cron 双锚 |
| ING-8 | P2 | 死件 | `cross_source_validator` / `cleaning_rule_engine` / `source_sla_tracker` / `auto_backfiller` 零生产消费方（§1.2） | 逐个裁定：接线（补 1 个生产调用点 + 测试）或删件（走 REGISTRY 流程）；不允许长期挂 `MATURITY production` |
| ING-9 | P2 | 卫生 | `deadman_switch.ps1` 落 `tmp/deadman_switch_alerts.log`（仓库根，3.6MB），违反 .runtime 收口 | 改 `.runtime/tmp/` 并配 TTL；`retire_tmp_artifacts.py` 覆盖该路径 |

## 5 子节点清单（本节点内还可挖的）

1. `akshare_provider` 内部：`:204-252` 的水位查询无 `quality_flag` 过滤，且 `SELECT count()` 失败 → 0 → 与"供应商返 0 行"不可分。
2. `consensus_crosscheck` 档期（`30 23 * * 0-4`）绑 0 个 tasks.yaml 任务 → 走 `scheduler.py` 特殊时段？实测 21 档期中 5 个（`consensus_crosscheck`/`daily_backfill`/`integrity_check`/`catchup_guard`/`nightly_sentiment`）在 tasks.yaml 侧无任务，仅 4 个在 `scheduler.py:203-250` 有硬编码分支 → **`consensus_crosscheck` 无分支 = 空转档期**（待复核）。
3. `nightly_sentiment` 总闸：`data/runtime/nightly_sentiment.disabled` **实测存在** → 该服务当前静默停用（`scheduler.py:237-239` 直接 return False），且无任何面暴露此开关状态；`sentiment_panel` 90 天内仅 16 天有数据 = 与之一致。
4. `data/failures/` 的冷却语义（300s）与 `retire_tmp_artifacts.py` 90 天 TTL 的交互：长期失败会被压成一条 + 被清。
5. `ch_parts_monitor` 仅在 `scheduler.py` 一处 import —— 其输出是否有第二消费方待查。

## 6 封矿判定

**不封矿**（本节点判"进料链路可观测性"这条脉仍在，但有 3 条脉明确已枯）：

- 枯脉 A：`python -m zephyr.data` CLI 面——8 子命令逐个读通 + 实跑，无可再挖。
- 枯脉 B：ch_reader/ch_writer 契约——`""`/`0` 歧义、93/120/127 import 面已穷举，只剩"改还是不改"的裁定。
- 枯脉 C：399106 广度根因——真源/旁路/哨兵三态已量化到行，续挖只是重复采样。
- 活脉：ING-1/2/3 修复后的**回归面**（修一次会牵出新的"注释级开关"族），以及 §5.2/5.3 两个待复核的空转档期与总闸文件。

退出路径裁定建议：**转施工 ING-1 + ING-2**（纯配置 + 一条门禁，零算法风险，且直接决定 S11 回测的行情完整性），ING-3 并行（告警面收口是后续一切"loud"的前置）。

## 修复优先级裁定建议

| 序 | ID | 为什么先它 | 预计改动面 | 风险 |
|---|---|---|---|---|
| 1 | ING-1 | 唯一"现网每天在错"的项，改 `tasks.yaml` 即止血 | 1 文件 4 处 | 低 |
| 2 | ING-2 | 断更可见性是本节点命门；无档期=修了等于没修 | `tasks.yaml` +2 任务，`breadth_freshness_alerts.py` feed_task 校正 | 低-中（需确认 CH 表已建） |
| 3 | ING-3 | 不做这条，ING-2 即使触发也无人知 | `alerter.py` + `generate_resource_week_view.py` 默认值 + `services_registry.py` 文案 | 中（动告警主干，需回归） |
| 4 | ING-4/5 | 校验语义改造牵动写入主干 | `quality_gate.py` + 2 表 DDL + 消费侧 SQL | 中高，建议独立批次 |
| 5 | ING-6~9 | 契约/卫生类，可与治理战役合批 | 分散 | 低 |
