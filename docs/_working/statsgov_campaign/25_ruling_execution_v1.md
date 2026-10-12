---
ttl: task_bound
completes_when: 四件尾巴各有归属并被下一班/相应车道接走（规格件正式版／回补执行／款⑤ 原文／M6 待维护三班 C4）
---

# 统筹批复执行件（令⑥ 晚班·四裁逐条落点）

批复来源=统筹 2026-10-12 晚批复（非本班自拟）；本件只记"怎么落的、落在哪个字节、还差谁"。

## 一、PBO 撤统一门 ⇒ 已改规格件真源

- 落点：`trial_budget_registry_draft.yaml#caliber_declaration` →
  `pbo_gate_value: null` ＋ `pbo_role_after_revocation: in_family_diagnostic_only`（族内相对诊断，报告项非门）
  ＋ `promotion_gate_kept: DSR>=0.95 + 闭卷考试`；失效证据回指 `21_negative_results_family_v1.md` #2。
- 生成器侧同步：`cap_status` 与呈签片段 `04_numbers_table_for_signature.md` 重跑刷新（机生，未手填）。
- 未动项：`correlation_overfitting_audit.py:64` 的 `PBO_MAX=0.05` 常量**保留**（撤销的是"跨族统一门"地位，不是删数值）；
  该处是否加注释说明其新语义，归该件主人，本班不改他人文件。

## 二、数值表照签 ⇒ 六族帽已出正式版（C/D 的"帽待定"已被实测消解）

批复当时给的豁免是"C/D 判帽待定"。本班按"先修 row_rule 复跑"的正解当场修了计数口径，结果：

| 族 | 帽（=历史消耗×1） | 状态（机生） |
|---|---|---|
| A 信号/因子 | 1,733 | `owner_signed_20261012_measurement_incomplete`（12 支册里 1 支不可解析，见 `uncounted_files` ⇒ 该帽是**下界**） |
| B 策略配方 | 85,252 | `owner_signed_20261012` |
| C 组合/配置 | 9 | `owner_signed_20261012`（原报 5 且标待定，系 row_rule 猜错键名） |
| D 状态识别/环境 | 17 | `owner_signed_20261012`（**原报 0** ⇒ 若照签会误停 D 族；红旗解除方式＝修口径不是豁免） |
| E 工程件 | 194 | `owner_signed_20261012`（改用"一个 run 档案=一次可审计考"目录计数） |
| F 挖矿器元层 | 5,488 | `owner_signed_20261012` |

口径升级三条（都写进规格件，供复算）：①`row_rule` 由点名单键改为**候选键链**且逐件留 `key_used`；
②单体记录册（无容器键的 reexam/conditional 卡）按 `COUNTED_AS_SINGLE_RECORD=1` 计入，
**绝不返回 0**（0 会把真实试次读成零消耗——自家测试 `test_count_entries_distinguishes_absent_key_from_zero` 现钉死这两侧）；
③新增 `dir_glob` 面型。测试 10 passed；产物 `02_*.yaml`/`04_*.md` 已刷新。
- ⚑ 新暴露一条待统筹定归属的重计：A 族通配 `*exam*_v*.yaml` 与 B 族点名同时命中 `mom029_reexam_v2.yaml`（已写进 `overlap_notes`，建议归 A）。

## 三、更硬的阳性对照 ⇒ 出回补规格件（含本班自纠）

- 落点：`24_positive_control_backfill_spec_v1.md`。
- **本班自纠一条**：我 20:3x 口头说"只补 2019-2020 两年即可"，算错——所需 T≈1,651 交易日，
  两年只到 1,180（t≈2.62 仍不够）⇒ 批复三给的范围正确，我收回原建议并在该件 §0 留了认错记录。
- 关键实测（决定工量）：市值表全表起于 2021-01-04；价量表 2016=234／2017=240／2018=237 只票（stub，
  且 `kline_daily_hfq` 同形＝两表互证）；2019=3,771、2020=4,366 已完整。
  ⇒ 缺口是**两段**：段一只补 basic（2019-2020，≈198 万行）；段二须价量＋市值同补（2017-2018，各≈173 万行）。
- 派工前必核实项（已写明）：`scripts/data/backfill_stock_daily_basic.py` 默认 `--start 20210101`，
  但其 `fetch_symbol` 调的是 `ak.stock_zh_a_hist`（价量接口）而表名是 daily_basic——文件名与数据源不一致，
  须数据域确认它产哪套字段，避免跑错口写错列。
- 执行面归数据域，本班不跑取数；月频 t 口径留档不采。

## 四、款⑤ 原文 ⇒ 停在 Owner 手里，本班未代写

`22_f06_archive_ruling2_v1.md` §款⑤ 的粘贴位仍空（四节标题占位）。统筹亦不转抄以防漂移。
待 Owner 逐字贴来即入册（原文不改）。

## 五、其余验收项的落点确认

- 款② 不重写他人事实源：已守（本班 0 次写 `f06_survivors.csv`）；**BOM 观察已转挖矿班**（该件表头带 `ef bb bf`，实测记录在 22 号件）。
- 试次入账与追加更正行：2,412＋8 已入账（账面 38,310→40,730，治理分母 91,400→93,820）；
  冒烟批 48 次那条的 note 误写以正式批 note 说明，未 UPDATE/DELETE。
  ⚑ 一条如实提示：这三条新记录目前**只在主区盘面**，尚未进 dev（热册由账本/册主车道落，非本班袋内件）。
- 病根 4"尾部追加型外科写"正解：本班实测支撑（追加单条成功、整册重放被拒），已作为建议写入 `03_*.md` §5 与晨/晚间包。
- M6 留证法：跑批件三份源码全文在 `90_calibration_runners_source.md`（含 sha256 与行数，可粘回）；
  待维护三班 C4 落 PG 第三源或册主 render 后，`scripts/backtest/statsgov_deflation_and_budget.py` ＋
  `tests/backtest/test_statsgov_deflation_and_budget.py` 与两份校准跑批件一并入正式目录（token 已登记）。

## 四件尾巴与归属

| 尾巴 | 归属 | 本班留了什么 |
|---|---|---|
| 规格件进 `catalogs/` ＋ ROOR 登记 | 册主车道（本班不代打投影） | 规格件真源已成文＋机生两面 |
| 回补执行 | 数据域 | 段/行量/字段/验收/复考协议全在 24 号件 |
| 款⑤ 四节原文 | Owner | 占位与"禁代写"声明在 22 号件 |
| 两个 .py 入库 | 维护三班 C4（M6） | 源码留证＋token/translation 均已进 PG |
