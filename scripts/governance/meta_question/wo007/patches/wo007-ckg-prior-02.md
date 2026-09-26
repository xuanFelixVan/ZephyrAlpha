# wo007-ckg-prior-02｜three_high_screen.py：咽喉度支柱降权 + source 过滤（含登记面）

- 目标文件：`scripts/backtest/three_high_screen.py`（他单文件）、`config/strategy_production_map.yaml`
- 用法性质：`hard_fact_consumer`（CKG 先验单独支撑排序，且直接产出策略进货候选 CSV）
- 在案证据：`PILLAR_WEIGHTS = {"growth":0.30,"margin":0.25,"barrier":0.25,"chokepoint":0.20}`；
  `SQL_CHOKEPOINT` 以 `ig_fact.supplies_to`（100% source='ckg_2021'）算下游广度与供给压力，
  合成 `total_z` 后按 `rank` 卸到 `data/strategy_intake/three_high_candidates.csv` 进 E1 编排；
  SQL 无 `source` 条件 → 与 `graph_enrich_staging` 的 LLM 候选混算（OB-4 违例）。

## 改动 1：先验档常量与权重（模块常量区）

```diff
-PILLAR_WEIGHTS = {"growth": 0.30, "margin": 0.25, "barrier": 0.25, "chokepoint": 0.20}
+# WO-007 件 3：CKG=结构先验（真源 data/registers/metaq_io_edge/ckg_structural_prior_tier.yaml）
+# TIERS['structural_prior'].weight_multiplier=0.45 → 名义 0.20×0.45=0.09，取 0.10（不失分辨率为下限）
+PILLAR_WEIGHTS = {"growth": 0.30, "margin": 0.25, "barrier": 0.25, "chokepoint": 0.10}
+PILLAR_WEIGHTS_NOMINAL = 0.20           # 降档前名义值（留审计对照）
+CHOKE_TIER_MULTIPLIER = 0.45
```

## 改动 2：SQL 按 source 分档（`SQL_CHOKEPOINT`）

```diff
 SQL_CHOKEPOINT = (
     "WITH prod AS (SELECT DISTINCT subject AS symbol, object AS product "
-    "  FROM ig_fact WHERE relation='produces'), "
+    "  FROM ig_fact WHERE relation='produces' AND source='ckg_2021'), "
     "down AS (SELECT f.subject AS product, count(DISTINCT f.object) AS breadth "
-    "  FROM ig_fact f WHERE f.relation='supplies_to' GROUP BY 1), "
+    "  FROM ig_fact f WHERE f.relation='supplies_to' AND f.source='ckg_2021' "
+    "    AND f.valid_to IS NULL GROUP BY 1), "
     "up AS (SELECT f.object AS product, count(DISTINCT f.subject) AS pressure "
-    "  FROM ig_fact f WHERE f.relation='supplies_to' GROUP BY 1) "
+    "  FROM ig_fact f WHERE f.relation='supplies_to' AND f.source='ckg_2021' "
+    "    AND f.valid_to IS NULL GROUP BY 1) "
     "SELECT p.symbol, avg(d.breadth) AS downstream_breadth, "
-    "       avg(u.pressure) AS supply_pressure "
+    "       avg(u.pressure) AS supply_pressure, "
+    "       count(*) FILTER (WHERE f.source <> 'ckg_2021') AS non_ckg_src_n "
     "FROM prod p JOIN down d ON d.product = p.product "
-    "JOIN up u ON u.product = p.product GROUP BY 1"
+    "JOIN up u ON u.product = p.product "
+    "JOIN ig_fact f ON f.relation='supplies_to' GROUP BY 1"
 )
```

> 注：上面这版 JOIN 会让 `non_ckg_src_n` 失真（笛卡尔放大）。落地批**采用更稳的等价写法**：
> 先按 source 分别聚合两个 CTE（`down_ckg`/`down_other`），再 `LEFT JOIN` 取
> `has_cross_source_evidence = (down_other.breadth > 0)`。目的不变：给每环节留一列
> 「咽喉度是否有异源侧证」。

## 改动 3：无侧证则整支柱置零（`score_three_high`，纯函数改造，禁改其余三支柱）

```diff
-    out["choke_z"] = winsor_z(stats["downstream_breadth"]) - winsor_z(stats["supply_pressure"])
+    choke_raw = winsor_z(stats["downstream_breadth"]) - winsor_z(stats["supply_pressure"])
+    # OB-1：structural_prior 不得单独支撑决策——无异源侧证时该支柱不计分（而非计低分）
+    out["choke_z"] = choke_raw.where(stats.get("has_cross_source_evidence", True), 0.0)
```

## 改动 4：出生证与登记面同步

- `BIRTH_SOURCE` 追加 `"[tier=structural_prior, cap=0.45, see ckg_structural_prior_tier.yaml]"`；
  候选 CSV 增列 `choke_tier`（值 `structural_prior` / `excluded_no_evidence`）。
- `config/strategy_production_map.yaml` FAC-E1D 车道文本
  「…×supplies_to 咽喉度四支柱 z 分合成」→ 补注 `（supplies_to=结构先验，权重 0.10，须异源侧证）`。

## 验收

1. `python scripts/backtest/three_high_screen.py screen --top 20 --dry-run` 跑通，
   输出 `choke_tier` 列且 `total_z` 排序与旧版差异可解释（仅咽喉贡献变化）；
2. 回归对照：同一入参下 growth/margin/barrier 三支柱 z 分**逐位不变**（防误伤）；
3. `build_ckg_prior_tier.py --self-check` → 本文件 `currently_prior_compliant=true`；
4. `tests/` 若已有三高相关断言，须同批更新（本战役窗不写 tests/，交落地批）。

## 回滚

revert 本笔；`PILLAR_WEIGHTS` 回 0.20 即恢复旧排序（无持久化状态）。
