---
ttl: task_bound
completes_when: residual 独占期结束（tasks.yaml/apply_market_tables_ddl.py 解冻）且四登记 gate 化后由生成器/checklist gate 取代本手工清单
---

# 数据源上架四登记 checklist（从源卡片到正门班次出数）

> 工单 WO-③-03（四登记 checklist SOP 化，治"第 2 源易漏登记"）；真源=工段作业簿
> `docs/_working/automation/campaign/mining/03_自动上架/工段作业簿.md` §4/§7。
> 命令实抄自 `python scripts/data/onboard_source.py --help`（2026-09-18 实测）与真源文件；
> 锚点行号为 2026-09-18 工作区实读，漂移以 grep 关键字为准。
> 首源样例=ECB 汇率（fx_ecb），第 2 源起照抄本清单逐项打勾。

## 0. 术语对齐（防误改，记长尾的不对称命名）

一张卡片四个名字并存，各归各的消费方，**禁止"顺手统一"**：
`source_id=fx_rate_ecb`（卡片，实际不被路由消费）｜`source=alt_fx_ecb`（路由键，来自 tasks.yaml）｜
`task_name=ZephyrAlpha_AltFxECB`（Windows 旁路任务）｜`capability=fx_ecb_daily`（能力契约）。

## 1. 上架前一次性三件套（人工交付，卡片驱动的是编排不是采集代码）

- [ ] **provider**：`src/zephyr/data/implementations/<source>_provider.py`（四方法+fetch，先例 `fx_ecb_provider.py`）
- [ ] **DDL 模板**：`schemas/categories/market/market_<source>.py`（`*_DDL` 后缀常量+TABLE_NAME+INSERT_COLUMNS；
      库规四件套=DateTime64(3,'UTC') 系统列/ReplacingMergeTree/PARTITION toYYYYMM/ORDER BY 自然键，钉在 `tests/data/test_onboard_source.py::test_ddl_rules`）
- [ ] **测试**：provider 行形/游标/路由存在钉（先例 `tests/data/test_fx_ecb_provider.py` 11 项，全零网零 CH）

## 2. 编排器流水线（卡片→apply，一条命令三段）

### 步骤 1：源卡片（config/source_cards/*.yaml）

新源=新卡片，编排器零改动（MODIFY-GUARD）。必备 6 字段（`onboard_source.py REQUIRED_FIELDS`，
缺任一 load_card 即 KeyError+details 结构化）：`source_id / schema_module / table / ingest_script / task_name / schedule`；
schedule 三键 `type / days / time`；可选 `title / ingest_args / probe_days / backfill_days / compliance`。
批量无卡片可直接抄 `config/source_cards/fx_ecb.yaml`（顶层 11 字段全量样例）。

### 步骤 2：probe 沙箱试拉（零落库，研发站）

```bash
python scripts/data/onboard_source.py --card config/source_cards/fx_ecb.yaml --mode probe
```

验收：输出 `{"mode": "probe", " ingest_exit": 0}`——`ingest_exit=0` 才许进 apply；probe 只 run_ingest `--probe`，零写库。

### 步骤 3：apply（DDL 建表+首批回补+旁路任务登记，实盘生产站入口）

```bash
python scripts/data/onboard_source.py --card config/source_cards/fx_ecb.yaml --mode apply
```

验收（顺序判读 stdout 四段）：`ddl_ok=true` → `backfill_exit=0` → `task_registered=true` →
`{"mode": "apply", "rows": >0, "latest_date": 非空, "task_state": 就绪}`。
内建保护：backfill 失败不挂任务（exit 2，防"每晚注定失败"僵尸班次）；DDL IF NOT EXISTS+ReplacingMergeTree 重放=幂等可重跑。

> **residual 独占触点**：DDL 真源双消费方——单表上架走 deploy_schema（本步骤，自动）；
> 舰队建表走 `scripts/ch/apply_market_tables_ddl.py`（**residual 战役独占，本工段只读**）。
> 新源若需舰队口径建表，挂单至波次边界接线，勿在独占期直改。

## 3. 四登记（第 2 源最易漏的四件，同批原子落地，先例=commit 4058b7b1e0）

| # | 登记 | 文件与锚点（2026-09-18 实读） | 登记内容 |
|---|------|------------------------------|---------|
| 1 | provider 路由 | `src/zephyr/data/scheduler.py` create_provider `alt_fx_ecb` 分支（:1308-1312） | `elif source == "alt_fx_ecb": ... return FxEcbProvider()` |
| 2 | policies 限频 | `src/zephyr/data/config/policies.yaml` **HEAD :206-220** | `alt_fx_ecb: rpm 30 / concurrency 1 / 3 次指数退避 / retry_on 5xx / 代理探测同 fred 模式` |
| 3 | schedule 槽位 | `src/zephyr/data/config/schedule.yaml` daily_alt_fx（:187-191） | `cron: "35 23 * * 0-4" / executor: default / max_instances: 1` |
| 4 | tasks 任务 | `src/zephyr/data/config/tasks.yaml` alt_fx_ecb_daily_incremental（:3341-3352） | `source: alt_fx_ecb / capability: fx_ecb_daily / schedule: daily_alt_fx / 保守游标语义入 description` |

- [ ] 路由 | [ ] 策略 | [ ] 槽位 | [ ] 任务——**四件同批提交**，缺一即"登记了但不出数"或"出数但裸奔无限频"。
- **residual 独占警告**：`tasks.yaml` 在 residual 战役独占清单（`CAMPAIGN_LEDGER.md:110`）——
  新源任务登记触点**挂单至波次边界**，独占期内只读勿改；改排班真源前先读 `docs/registry_of_registries.yaml` 判真源方向。
- **活教材**（本 checklist 存在的理由）：2026-09-18 工作区实测 policies.yaml 的 alt_fx_ecb 块被未提交
  删除（HEAD :206 有、工作区缺，-12 行在飞，属 WO-③-00 处置中）——四件散落四处时单件删除静默，
  登记后必跑步骤 6 的 ConfigCheck 机械核对。

## 4. 激活窗（人工/值守，无自动化）

- [ ] 调度器**重启窗 04:00-05:00** 重启 DataScheduler（重启不热载配置，登记≠生效）；
- [ ] 晨间 08:05 `ZephyrAlpha_ConfigCheck` 机械核对"磁盘 vs 进程"键级 diff（快照缺失 fail-closed）——登记后不重启即报不一致；
- [ ] 连续 7 天正门打卡后，Windows 旁路任务退役提请 Owner（挂单 H-06，Owner 门）。

## 5. verify 对账（按次）与周期巡检（WO-③-04 已建）

一次性打卡：

```bash
python scripts/data/onboard_source.py --card config/source_cards/fx_ecb.yaml --mode verify
```

验收：`rows>0` 且 `latest_date` 推进且 `task_state` 就绪；载荷带 `error` 键=fail-visible（CH 故障不伪装空表）。

批量 verify（多卡一键过堂，单卡失败不炸批，末尾汇总表 card/mode/result/reason）：

```bash
python scripts/data/onboard_source.py --cards-dir config/source_cards --mode verify
```

周期巡检（全卡 verify→报告→告警，零网安全=只读对账）：

```bash
python scripts/data/source_health_patrol.py            # 报告落 data/source_health_patrol/<YYYYMMDD>.json
python scripts/data/source_health_patrol.py --no-alert # 只出报告
```

验收：`overall=pass`；卡级 FAIL→Alerter 正门 ERROR（写 `data/failures/`）；
CH 断连→全卡 degraded 单条 WARN、exit 0 不炸；报告含 per-card rows/latest_date/task_state。

## 6. 快速回查

| 症状 | 先看 |
|------|------|
| 登记了不出数 | 激活窗重启了吗（§4）→ConfigCheck 告警→tasks.yaml source 键 vs 路由分支键一致吗 |
| 出数但无限频裸奔 | policies.yaml 策略块在吗（§3-2，见活教材） |
| apply exit 2 | backfill_exit≠0（回补失败不挂任务=设计行为，查源可达性后重跑 apply） |
| 巡检全卡 degraded | CH 断连嫌疑，勿逐卡排查，查 ClickHouse |
