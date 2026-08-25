---
blueprint_id: MOD-PF-011
module_name: exposure_manager
domain: D_PF_CORE
doc_type: blueprint
ttl: permanent
design_maturity: design
stability: evolving
safety_level: H
ai_autonomy: ai_modifiable
version: "0.1.0"
created: 2026-08-25
last_updated: 2026-08-25
owner: ZephyrAlpha-Owner
priority: P1
blueprint_level: module
domain_id: D_PF_CORE
path: src/zephyr/pf_core/core/exposure_manager.py
granularity: file
---

# MOD-PF-011 exposure_manager 蓝图（PC-07 Exposure Manager 敞口管理器）

> **module_id**: MOD-PF-011 | **域**: D_PF_CORE | **优先级**: P1
> **来源**: B3-05543（AUD-DRAFT-001-DIGEST P1 波 W-P1-21，CAND-PF004-004，D-PF-CORE §1.2）
> 代码：`src/zephyr/pf_core/core/exposure_manager.py`

## 0. 定位

组合域敞口管理器：申万 31 行业**主动敞口**（组合 − 基准）+ Barra 风格**主动
暴露** + 偏离阈值告警 + **行业轮动信号输出**（动量排名 × 当前主动敞口 →
增配/维持/减配建议）。

查重分工（W-P1-21 铁律④细读 TSV——**异，分工论证**）：

| 既有件 | module_id | 职责 | 与本模块边界 |
|---|---|---|---|
| factor_exposure_manager | MOD-RK-38 | 风险域：持仓×载荷→**绝对**敞口矩阵 vs 绝对 limits 超限预警（无基准、无轮动） | 监控面；本件=**基准相对主动敞口**+轮动配置信号（组合域决策面），口径不同 |
| concentration_monitor | MOD-RK-07 | 风险域：HHI/个股/行业集中度三级告警（无载荷、无基准、无轮动） | 集中度≠主动敞口 |
| constraint_solver | MOD-PF-006 | CTR-003 限额投影 | 求解器非敞口计量 |

TSV spec："申万31行业敞口+Barra风格因子暴露计算+集中度阈值告警+行业轮动信号
输出"——前三句风险域已有绝对口径件，"行业轮动信号输出"全仓无既有件；本件落
组合域相对口径+轮动信号，不重复绝对监控面。

## 1. 规则（确定性纯函数，数据全注入）

- **行业主动敞口**：industry_active[i] = Σ_{s∈i} w_p(s) − Σ_{s∈i} w_b(s)
  （基准行业权重可由基准持仓+行业映射合成或直接注入）。
- **风格主动暴露**：style_active[f] = Σ w_p×loading_p − Σ w_b×loading_b
  （缺载荷标的列 uncovered 按 0 计并披露）。
- **偏离告警**：|active| ≥ warn（默认行业 0.05/风格 0.15σ）→ WARNING；
  > breach（默认行业 0.10/风格 0.30σ）→ BREACH；按 |active/limit| 降序。
- **行业轮动信号**：行业动量横截面排名（注入 momentum），top_n（默认 5）且
  active < band → OVERWEIGHT 建议；bottom_n 且 active > −band → UNDERWEIGHT；
  其余 NEUTRAL。仅产信号，执行委托装配批。
- Fail-Closed：空持仓/负权重/非法阈值/空行业映射 → ExposureManagerError。

## 2. 接口

- `ExposureManagerConfig`（frozen）/ `ExposureDeviation` / `RotationSignal`（枚举）
  / `IndustryRotationAdvice` / `ActiveExposureReport`（frozen）
- `ExposureManager(config=None)`
  - `analyze(positions, industry_map, benchmark_weights=None,
    benchmark_industry_weights=None, style_loadings=None,
    benchmark_style_exposures=None, industry_momentum=None) -> ActiveExposureReport`

## 3. 不做什么

不做绝对敞口监控（MOD-RK-38）、不做 HHI 集中度（MOD-RK-07）、不做交易执行
（轮动信号仅建议）、不取数（基准/动量全注入）。
