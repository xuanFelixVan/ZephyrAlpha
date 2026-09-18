---
ttl: task_bound
completes_when: 全流通战役收官且验收仪交工
---

# 既有工具勘察结论（flowverifier 车道，2026-09-18）

> 目的：造"全流通验收仪"前先盘点既有轮子，明确每个工具覆盖六向的哪一向、
> 缺什么、验收仪如何**挂接而非重写**。

## 1. 逐工具勘察

| 既有工具 | 实测勘察结论（argparse/产物落点） | 覆盖六向 | 挂接方式 |
|---|---|---|---|
| `src/zephyr/data/ch_reader.py` | `query(sql)`/`count(table,where)`，对 ReplacingMergeTree 自动注入 FINAL，纯只读；底层经 DatabaseService 领 reader 连接 | ①③ 的查询引擎 | **直接复用**为①③的实测查询通道（不裸 duckdb/不裸 clickhouse_driver）；注意 `count()` 失败静默返 0（fail-open），验收仪改用 `query()` 判空串区分"0 行"与"查询失败" |
| `src/zephyr/data/quality_sentinel.py` + `config/quality_sentinel_tables.yaml` | `run_sentinel(specs, output=SentinelOutput(report_dir=None, notify=False))` 可无副作用在进程内实跑；`load_specs(config_path, tables=...)` 支持子集过滤；CLI 有 `--tables/--no-report/--no-alert` | ②（数据质量环节的可真跑转化入口）+ ⑤（阈值行真源之一） | ②=进程内实跑 `run_sentinel`（rc+耗时+findings_count）；⑤=读该 YAML 判产出表有无阈值行 |
| `src/zephyr/data/config/data_supply_sentinel.yaml` | 表级 `max_lag_days/date_col/past_only` 断供阈值真源 | ⑤ 第二阈值真源 | ⑤同时查两册，任一有行即算哨兵在岗（证据给路径+行内容） |
| `src/zephyr/data/config/tasks.yaml` + `schedule.yaml` | tasks 有 `task_id/table/source/schedule/dependencies/date_col/fallback_sources`；schedule 有 cron+executor+L0-L11 分层注释 | ①（新鲜度周期真源）+ ④（task DAG）+ 环节清单真源 D | 环节清单**从 tasks 按 schedule 分组自动推导**（禁写死）；cron→容忍滞后天数映射用于①新鲜度判定；dependencies 用于 --e2e 主链逐跳 |
| depgraph（PG `nodes/edges/domains` 表） | `generate_project_depgraph.py` 的 YAML 输出已 DEPRECATED，DB 是唯一 SSoT；`DatabaseService.get_depgraph_conn(read_only=True)` 可只读领连接；edges 列=`from_node_id/to_node_id/dep_type/...`，nodes 键=`node_id`+`path` | ④ 的唯一合法证据源（真实依赖边，不靠 grep 猜）+ 环节清单真源 F | ④=`JOIN nodes` 查 `to_node_id∈环节包` 的 from 侧消费者路径，按 `src/**` 与 `scripts/**` 分档（scripts-only→黄） |
| `scripts/governance/d5_architecture/generators/align_all.py` | 只读对齐（panorama+battle_map），产物=overview 报告；对齐键 module_id/step_id | 不直接覆盖六向（模块级对齐，非数据流通实测） | 不挂接；仅在报告中引用其存在，避免重复造对齐轮子 |
| `scripts/governance/generators/generate_skeleton_health.py` | argparse=`--tdm/--audit/--registry/--samples-dir/--decay/--out-dir/--dry-run`，从 TDM/审计/注册表出骨架健康度 | 接近④⑤的静态面，但不做①③实测数字 | 不重写；验收仪差异点=**每一向出实测数字**（行数/时间戳/rc/breach 数） |
| `scripts/governance/d8_doc_sync/algo_flow_reverse_orphan_reconciler.py` | 反向孤件普查（当前有他会话 +7 行 unstaged，只读不动） | ④ 的孤件子问题 | 不挂接（在飞文件禁改）；④直接用 depgraph 边自证 |
| `architecture_model/index.yaml` | `domains:` = 75 域索引（id/name/layer_id），由 depgraph domains 表派生 | 环节清单真源 A | --crosscheck 源 A |
| `docs/01.../catalogs/functional_domain_registry.yaml` | `entries[].domain`（D_* 63+ 域）+ ssot_path | 环节清单真源 B + 域级环节的 ssot_path 来源 | --crosscheck 源 B；域级环节卡片的 ssot_path（供④查询前缀） |
| `config/trading_decision_map.yaml` | `nodes[].flow/node_id/layer/market`，决策链视角 | 环节清单真源 C（词汇=flow，不可与 D_* 直接比） | --crosscheck 源 C，标"异词汇"单列 |
| `docs/03_modules/_domain_*/` | 45+ 个 `_domain_<x>` 目录 | 环节清单真源 E | 目录名→`D_<X>` 归一后进差集 |

## 2. 缺口结论（验收仪必须自造的部分）

1. **没有任何既有工具做"逐环节六向实测数字"**：ch_reader 只有查询原语、sentinel 只覆盖数据质量域、
   skeleton_health 是静态注册表视角 → 六向编排器缺位，即本件 `scripts/automation/flowthrough_verifier.py`。
2. **没有环节清单生成器**：mine-0 骨架未落盘（勘察时 `skeleton/` 为空目录）→ 验收仪从 6 真源自动推导环节清单，
   禁写死（宪法 §9.5）。
3. **没有"尺子自红"证明件**：既有测试体系有 mock 防线前科（#ARCH-327）→ `--prove-red` 为本件独有，
   断链注入走**内存/临时 spec 变异**（生产文件零触碰，附 tasks.yaml sha256 前后一致证据）。
4. **没有环节层面多真源差集对账**：align_all 是模块级 → `--crosscheck` 输出 6 真源两两差集到
   `skeleton/03_omission_crosscheck.md`。

## 3. 挂接原则（避免平行体系）

- 查询一律走 `ch_reader.query`（内含 FINAL 注入 + DatabaseService reader 连接）与
  `DatabaseService.get_depgraph_conn(read_only=True)`，验收仪自身**零新建数据库连接**。
- 哨兵不重造：⑤只读两册阈值真源 + 复用 `run_sentinel` 实跑。
- 环节清单不写死：全部 derive_* 函数从真源现算。
- 产物落点：Markdown→`docs/_working/fullflow_campaign/`（.md 合规格式）；机器可读 YAML→`.runtime/tmp/ff-flowverifier/`。
