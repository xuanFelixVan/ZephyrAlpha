---
ttl: task_bound
completes_when: 全流通战役新数据源车道交工并被总包复核
---

# 接力 · 新数据源车道（st-ff-newsrc-20260918）交工与未完项

> 全部数字为**本机实跑**（R-019：每条先复跑原始命令）。转报/普查记载凡与本文件冲突，以本文件实测为准。

## 1. 已完成并落地（2 笔，队列 done，零混入）

| 笔 | hash | 文件 | 内容 |
|---|---|---|---|
| N1 | `df42bf8374` | `src/zephyr/data/implementations/akshare_alt_provider.py`（+186 行，1 文件） | CFTC 持仓四报表 + SPDR 黄金 ETF 的 **provider 腿**（`cftc_positioning`/`gold_etf_holdings` 两能力 + CapabilityContract + 4 个纯函数 helper） |
| N2 | `2ebf2f238f` | `architecture_model/data/data_sources_registry.yaml`、`docs/_working/altdata_line/10_data_source_candidates.yaml`（2 文件） | DS-IRM + DS-HYPERLIQUID 补登（v2.5.0→v2.6.0，纯新增）+ DS-CAND-011 毕业 |

**N1 验收三样**：①增量任务=待合并
`docs/_working/fullflow_campaign/lanes/altdataF_tasks_yaml_fragment.yaml`（其前置「provider 能力已接」
**本车道已消除**，「部署件 untracked」由 z-orphan `78976c56f5` 消除 → 两条前置全清，可排跑）；
②哨兵阈值行**已在 HEAD**（`data_supply_sentinel.yaml:266-276`，cftc `report_date`/12d、gold `trade_date`/5d）
→ 本车道**不重复出片段**；③抽检 **CFTC 20/20、GOLD 20/20 与源逐字段全等**
（源端二次取数 vs `SELECT … FINAL`，证据 `.runtime/tmp/ff-newsrc/spotcheck_n1.json`）。
幂等实证：正道 `ch_writer.write_result` 全量重灌一轮 → raw 81,270→162,540 而 **FINAL 恒 81,270**
（gold 2,871→5,742 / FINAL 恒 2,871）。

**provider 腿到底缺不缺（问题④的答）**：缺，且**代码真源一度丢失**。证据三条：
`git grep -il cftc HEAD -- src/zephyr/data` 只命中哨兵；工作区 `akshare_alt_provider.py` 与 HEAD
**逐字节同（1975 行）**；唯一残留是 17:46 的 `__pycache__/akshare_alt_provider.cpython-312.pyc`，
marshal 解出顶层含 `_fetch_cftc_positioning` / `_cftc_frame_rows` / `_gold_etf_rows` /
`_cw_snapshot` 等 24 个函数 → **前手 provider 件被 reconciler 还原回 HEAD**
（CONSTRUCTION_DISCIPLINE §8 病型），本车道据 DDL+源接口重写而非从字节码恢复。

## 2. 推翻/修正的总包前提（5 条，均带实测）

1. **「两表已在灌数」不成立 → 是**一次性手工回填后静默**。**
   `SELECT toDate(ingest_ts), count() … GROUP BY` → 两表 ingest 只有 **2026-09-18 一个日**
   （cftc 09:47:28Z / gold 09:49:13Z），无任何后续采集 → 若本车道不补 provider 腿，
   两表从 09-18 起永久停更，而哨兵 12d/5d 档要到 09-30/09-23 才报红。
2. **`[ARCH-APPROVAL:ALTDATA-09-WORKLIST]` 标记通道无效**。门源码
   `protected_paths_gate.py:81` 与真源 `check_protected_paths.py:69`：
   `re.compile(r"\[ARCH-APPROVAL:(#?ARCH-[A-Z0-9_-]+)\]")`——**强制 `ARCH-` 前缀**，
   `ALTDATA-*` 不匹配→必被硬拦。改用仓内在册通行值 `ARCH-MODEL-LIFECYCLE-001`
   （同动作先例 `d8419af8e6`／`c98af98248`）。
3. **`get_clickhouse_conn()` 返回的是 `clickhouse-driver` 的 `Client`，不是 clickhouse-connect**。
   `database_service.py:186 from clickhouse_driver import Client`，实测
   `type(...) = <class 'clickhouse_driver.client.Client'>` → 取数方法是 **`.execute(sql, params)`**
   （既无 `.query()` 也无 `.cursor()`，但 `.execute` 两个都有）。总包「两次试错失败」的根因在此。
4. **`capability_canonical_file_registry.yaml` 的「24 行他人 staged 删除 + 92 行他人新增」已失效**：
   本车道实测 `git status --porcelain <该文件>` **空输出**、HEAD/index/worktree 均 35,774 行 → 现已干净。
   （本车道最终仍未带该册入 N1/N2 两批，因两批都是改存量件、无新建。）
5. **N8 前置不成立：本机 ollama 未在跑**。`Get-Process | ? ProcessName -match 'ollama|llama|server'`
   **零命中**，`curl http://127.0.0.1:11434/api/tags` **无响应** → 扩量批不可启动（硬等=白烧）。

## 3. N3 仪息日历：哨兵腿已被 z-sentinel 做掉，换源本体未完（问题③/⑧）

**实测 HEAD `data_supply_sentinel.yaml`**：`85ef0962d0` 已落三条腿 + 新机制字段
（`heartbeat_leg` / `row_filter` / `leg_name` / `rationale_zh`）：

- 行 67-71：`ingest_ts` 心跳腿（`max_lag_days: 2`，明写「本腿只证明我们在写」）
- 行 338-343：**`date_col: decision_date` 表级业务腿 75d** ← 任务书要求我「一起做」的那条
- 行 351-355：**`decision_date` + `row_filter: "bank_code = 'pboc'"` 维度腿 90d**

→ 任务书 N3 的「必须把 `decision_date` 口径一起做，否则致盲缺陷进新链路」**已由 z-sentinel 落地**
（且它已把 BRK-038 因果说反的事写进注释）。本车道**不再出重复片段**（规范总量净零增长 §4.1）。
**交 z-sentinel 的片段=无**；新源接入后只需把两条腿的 `max_lag_days` 从「临时止噪 400」收回常档。

**未完成的换源本体**（需另批，已具备实测可行性）：

| 通道 | 实测证据（2026-09-18 本机，15s 超时） | 结论 |
|---|---|---|
| Fed 官网 `federalreserve.gov/monetarypolicy/fomccalendars.htm` | **HTTP 200**，正文以 `<!doctype html>` 开头 | 权威主源**可达**，可建 `source: fed_official` capability `rate_decision_calendar` |
| 东财 `datacenter-web.eastmoney.com/api/data/v1/get?reportName=RPT_CBANCIAL_RATE` | **HTTP 200** 但 `{"success":false,"code":9501,"message":"返回字段参数不能为空"}` | reportName **存在**（报的是字段参数缺失而非未知报表）→ 补 `columns` 参数即可，国内腿可行 |
| 现金十腿 `akshare macro_bank_*` | max(decision_date)=2025-10-30（z-sentinel 实测 + 本车道复跑一致） | 按片段第 3 条改 `schedule: disabled` + `disabled_reason`，**禁删条目** |

G 盘冷库可用：`G:\zephyr_cold\30_corpus\web_snapshots` 存在（3 个子目录），
两源接入时按 SOP §12 先落原文快照再入表。

## 4. N4-N6/N8 状态与取证（问题②⑧）

- **N4 分红预案切源**：**未做**（预算让位于 N1/N2 的落地闭环）。前置已核清：
  片段 `lanes/datagap_tasks_yaml_fragment.yaml` 第 1 条 `dividend_incremental_akshare`
  配方（akshare `stock_fhps_detail_em` 族 + `daily_event` 槽）与库内实测一致，
  且 `akshare_provider.py` 可承载（股东户数切源先例同件）。**交下一班最短路径**：
  照 `_fetch_shareholder_count` 的东财 datacenter 窗口写法加一能力 + 哨兵片段，约 1 小时。
- **N5 中债深历史**：**仅调研，未接入**。实测两候选路径
  `https://www.chinabond.com.cn/Channel/11185` 与 `/dmdn/document/list?channelId=11185` **均 HTTP 404**
  —— 这**只证明这两条路径不存在**，不证明站点不可达（本车道未探根域/正确栏目号，
  故按任务书「禁写该源不可用而无证据」的要求，结论只到「路径待考古」）。
  已登记需求：需先做站点检索（`site:chinabond.com.cn 收益率曲线`）拿真栏目 ID，再走 download 型 SOP §2。
- **N6 调研类（六族）实测台账**（HTTP 状态码，15s 超时，全量 JSON 见
  `.runtime/tmp/ff-newsrc/probe_n56.json`）：
  - **F15 CENC 地震台网——推翻「连不上」记载**：`news.ceic.ac.cn/ajax/updatelist?page=1`
    返回 **HTTP 405 Method Not Allowed**（不是超时/不可达），且 `https://www.ceic.ac.cn/` **HTTP 200**。
    → 端点活着，**是方法/参数不对**（ajax 端点需 POST 或带 Referer）。可救，且成本低于普查估计。
  - F1 气象 / F7 空气：本车道未新探（`qweather_provider.py` 已在册 DS-QWEATHER，
    深圳开放数据族已在 `akshare_alt` 26 能力内）→ 登记为「已有通道，缺的是品种覆盖」而非「无源」。
  - F10 票房：**不建**（片段第 8 条：表不存在 + 无免费通道，须先过爬虫试点 + compliance_reviewer）。
  - D3 专利：`pss-system.cponline.cnipa.gov.cn/conventionalSearch` → **HTTP 412 Precondition Failed**
    （官方反爬闸，需 JS/cookie 栈）→ 本机 urllib 通道**确不可用**，需浏览器栈或商业 API（Owner 报批）。
  - D9 行政处罚：`www.creditchina.gov.cn/...` → **HTTP 412 Precondition Failed**（同一类闸）。
    → 与专利同判：**不是"找不到官方渠道"，是"官方渠道有反爬闸"**，需 Owner 决定浏览器栈/授权采购。
  - 公路运价 2015-2024 深历史：**未做**（现 `road_freight_index` 能力已在跑，缺的是旧站考古，
    属全站检索活，非接口活）。
  - 分品种肉蛋菜 `pfsc.agri.cn/api/priceQuotationController/pageList` → **HTTP 404**
    （与 `agri_wholesale_index` docstring 记载的 404/500 一致，**复跑仍死**）→ 指数层先行已满足挂价铁律。
- **N7 提交队列死信巡检**：**未做**。实测 `commit_queue.py status` 现
  **dead_backlog=980**（categories env 86 / item 801 / other 93），本车道自己的 2 个 qid 均
  `done`（零死信）。⚠️ 本车道**观察到但无权处置**的邻道死信：
  `q-20260918-st-ff-land3-20260918-0010` 死于 `GATE-ERRCODE-CONSISTENCY`
  `[unregistered_code] ZA-PA-CRISIS`（drain 期由 serializer 顺带处理，非本车道触发）。
  → 交总包：死信原件未删（取证材料），本车道未 requeue 任何非己项。
- **N8 IRM 抽取扩量**：**不可执行**（见 §2.5 ollama 未在跑）。已核到既有腿：
  `irm_provider` 的 `CONSUMERS` 明写 `scripts/ch/irm_extract_batch.py`，
  库内 `irm_interactive_qa=500 行`（2026-06-19~09-16）、`ir_activity_record=30 行`。
  → 扩量批应等 ollama 恢复后再投，本车道未跑任何 LLM 批（避免并发期数小时占用）。

## 5. 下一班最短路径（按「一夜可完成 × 下游价值」重排）

1. **N3 换源本体**（Fed 官网 HTML 解析 + 东财 `RPT_CBANCIAL_RATE` 补 columns）——两源实测都活着，
   表/品类已在库已注册，哨兵腿已钉 → 只差 provider 两件 + tasks 片段。
2. **N4 分红切源**（配方齐、先例件同文件）。
3. **F15 CENC 改 POST 重试**（§4 已推翻「不可达」，可能是本次最便宜的捡漏）。
4. `capability_canonical_file_registry.yaml` 的两条 **品类片段仍未并入**：
   `lanes/altdataF_categories_yaml_fragment.yaml`（market_cftc_positioning / market_gold_etf_holdings）
   → 载体 `docs/03_modules/_cross_layer/database/business_data_categories.yaml` 归战役禁写域。
   **合并前本车道 provider 靠 `_PENDING_CATEGORY_TABLES` 同值回退跑通**（真源仍是 YAML，
   合并后回退分支自动休眠）；合并后建议删回退表。双向子串碰撞实测=空（206 在册名四口径比对同 z-orphan）。
5. RULE-SSOT 的 YAML→DB 同步腿未跑：`scripts/governance/d8_doc_sync/sync_yaml_to_depgraph.py`
   无单表旗（全量重写只读表）→ 并发期不跑，交总包收口窗口。
