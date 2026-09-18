---
ttl: task_bound
completes_when: 全流通战役收口报告归档
---

# 车道接力 · st-ff-sentinel-20260918（供数新鲜度致盲治理）

## 已达成
- T1 三条前提逐条复跑（结论见 `sentinel_premise_recheck.md` §1，含两处口径修正）
- T2 判据维度治本：`supply_sentinel.py` 扩 `row_filter / lag_basis / cadence /
  min_rows_in_window / column_fill_ratio / heartbeat_leg / leg_name`，
  并新增"仅心跳腿=盲点必出声"（`blind_spots`→WARN）与配置未知字段 fail-closed
- T3 z-datagap 片段合并 + 11 张无哨兵表补册（含逐张 20 行抽检）；实跑 checked 36→51、breached 1→8、blind→0
- T4 N-1 非零率判据落地并在跑（daily_valuation / index_valuation_daily 各一腿，均真红）
- T5 quality_sentinel 排班四要素落地（L13 托管形态，未建假任务条目；理由与实跑证据见 recheck §5/§6）
- T6 片段收口：`datagap_tasks_yaml_fragment.yaml` 8 条逐条处置（①④合并 / ②③处方 / ⑤待裁 / ⑥实测修正 / ⑦⑧无动作）；
  `altdataF_tasks_yaml_fragment.yaml` 核实 z-dag 的 disabled 理由**仍成立**（HEAD 里
  akshare_alt 无 cftc 能力、`scripts/ch/apply_cross_asset_ddl.py` 与两个品类 YAML 仍 untracked）→ 不翻转；
  提交前 20:3x 复测：HEAD 78976c56f5 已收编 `scripts/ch/apply_cross_asset_ddl.py`（DDL 已入库），
  但 `git show HEAD:src/zephyr/data/implementations/akshare_alt_provider.py | grep -c cftc_positioning`
  仍为 **0** -> 卡点（provider 能力不在 HEAD）依旧成立，两条 disabled 任务保持不翻转；
`instL_*` / `minelineI_*` 两片段实测**文件不存在**（与 z-dag 结论一致，未重做；
  minelineI 的 quality_sentinel 排班需求已由 T5 以托管形态闭环）
- 附带治了两条"假在岗"阈值行：`execution_report.date_col=trade_date`、`kline_5min.date_col=trade_date`
  （两表实测均无该列，旧代码把查询失败与真空表同写 `empty table` 而看不出破口）

## 未达成 / 缺口（如实）
1. **"与源对得上"只做实行级自洽 + 跨表互证，未做真回源 API 比对**（provider 面禁写 + 需外部通道）；
2. quality_sentinel 未建 tasks.yaml 条目 / 未开独立槽位（按实测选了托管形态）——待裁 req_sentinel_01；
3. intraday_sector 五任务停档期、`audit_opinion/rights_issue/dividend` 三个 disabled 任务的
   台账归因（是否退役）待裁 req_sentinel_02；
4. `edb_data`（0 行、iFind 退役、无任务）仍"故意无阈值行"；`sector_fund_flow` 在 tasks.yaml
   无条目（哨兵在册但采集侧归属未落账）——两条均只留注释与本报告，未动表未删条目；
5. 修复类（daily_valuation 写侧、议息换源、SHFE 备源、1970 残留 435 行清理）一律只出处方/移交，
   本车道禁 DELETE 生产数据、禁写 provider 面。
