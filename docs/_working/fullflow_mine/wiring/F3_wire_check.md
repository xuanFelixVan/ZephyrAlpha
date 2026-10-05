---
ttl: task_bound
title: "水位聚合表接线查证报告"
owner: st-datasop-20260930
language: zh
status: active
version: "1.0.0"
date: 2026-10-05
---

# EXEC-F3 水位聚合表接线查证报告

判定：**无需接线，销账**。dashboard 无水位/房产展示面，两新表（alt_sz_reservoir_level_daily / alt_sz_house_listing_daily）零代码改动，服务对象=未来因子/研究查询（数据在库即可）。互斥清单、config/*map*.yaml、trading_decision_map.yaml 零触碰。

## 1. 查证过程与依据

### 1.1 dashboard 侧（步骤 1 grep 全量复核）

`grep -rn "reservoir\|水位\|house_listing\|挂牌" src/zephyr/frontend/dashboard/ --include="*.py" --include="*.js"` 全部命中均为异域同词，无一指向水库水位或房产挂牌：

| 命中 | 实义 | 判定 |
|------|------|------|
| services_registry.py L633/L994/L1009/L1222 | 磁盘水位/GPU 水位/内存水位条（系统监控） | 异域 |
| api_server.py L1281 | 服务总闸"整机水位"（CPU/内存） | 异域 |
| web/features/services/sv-page.js L44 | 总闸区"整机水位三杆"（前端渲染） | 异域 |
| chainmap-company-card.js L172-180（listing） | 股票上市地/上市日/上市状态 | 异域 |
| api_server.py L4490-4515（listing） | chainmap 公司卡 listing_venue/listing_date | 异域 |

扩展复核 `src/zephyr/frontend/` 全量（py/js/html/json）+ "水库/水情/alt_sz" 关键词：零命中。结论：**dashboard 无水位/房产数据展示面**，不存在"读原表待切新表"的接线对象。

### 1.2 两新表现存消费方（步骤 2/3 判定面）

- `alt_sz_reservoir_level_daily`：唯一业务消费方=data_supply_sentinel（`src/zephyr/data/config/data_supply_sentinel.yaml` L367-369，业务新鲜度腿已切日级降采样表，昨日完成）+ DDL 登记面（scripts/ch/apply_market_tables_ddl.py）。哨兵链路已闭环，无 dashboard 消费。
- `alt_sz_house_listing_daily`：仅 DDL 登记面（apply_market_tables_ddl.py L473-474/L617-618/L1211-1212），零运行时消费方，同判**无需接线**。
- 原表残留消费：akshare_alt_provider.py（采集写入方，非展示面）；factor/research 目录零消费（两新表预期服务对象=未来因子/研究查询）。

### 1.3 判定

命中任务书情形 **b)**：dashboard 无水位/房产展示面 → 登记"无需接线"销账。接一根无人消费的展示线反违全资产净零铁律（§4.1：新增须声明替代或合并旧条目）。house_listing_daily 同判。

## 2. 改动清单

- 代码：**零改动**（无接线即无代码/测试改动，无提交需求）。
- 本报告 + creation_token 登记（ledger 正道三步：api.register→publish_snapshot→render；2026-10-04 投影割接后 batch_creation_tokens 直写通道已失效，手改册=私改被投影门拦，故走 `register_tokens_ledger.py`，token 同批原子由总包注册册袋统一落地，本袋不携带注册册）。

## 3. lever 留痕

本次提交所用 lever（任务书指定）：`ZEPHYR_PRECOMMIT_DEBT_RATCHET=0`、`--allow-non-worktree --adopt-prior-work --skip-preflight --no-auto-enqueue`。用途：非 worktree 会话直连提交单一报告件，跳过 preflight 债务棘轮；提交后 `git log -1 --name-only` 核实归属。

## 4. 移交事项

无。若 ledger 登记被拒（DB 不可达/指纹冲突），本报告留盘移交 Owner/总包车道补登，token=`fullflow-mine-f3-wire-check-20261005`。
