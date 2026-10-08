---
ttl: task_bound
completes_when: 季度三红首报落地并经 Owner 复核后本簿转归档参考；下季度清账以本簿判据为基线迭代
title: C2 季度账本口径簿（st-fig13-followup-20261006 线C 挖矿件）
owner: st-fig13-followup-20261006
---

# C2 季度账本口径簿（st-fig13-followup-20261006 · 线C挖矿件2）

> 状态：**封矿**（判据落笔，首报=C4）。输入=docs/_working/map_census/01_module_home_census_v1.csv（1618 行，Flash 9d246347f98）+02_quarterly_ledger_prep_v1.csv（四段备料，st-sentinel-census-20261005）；两输入只读零改写。
> 伴生件：`c2_unknown83_classification.csv`（unknown-83 逐行清洗，本簿 §2 口径机生）。

## 0. 恒等式与总账（02 备料头部，引用不抄写）

```
1618 = ①TEST 401（已裁定出宇宙） + ②unknown 83（本簿清洗→归类面收敛） + ③真无家 767 + ④有家 367（单家 310 + 复数家 57）
段行数：1_TEST=401 | 2_unknown=83 | 3a_domain_groups=292 | 3b_multihome=57 | 4a_dangling_py=28 | 4b_non_py=1 | 4d_tests_path=9 | 4c_supplement=6
分歧注记：任务包预期 unknown=74，严格口径=83（+9：MOD-AUTO 暂编号族 7 行语义近 autonomy_core + BT-CHTP/L02-FS/ML-DENSITY 等 token 在册可归——本簿 §2 全量逐行落分类，分歧消解）
```

## 1. 三红判据（季度账本口径，落笔）

### 红1 · 孤儿（在册模块该挂没挂）
- **判据**：census 中 home_count=0 且 **不属于** ①TEST（出宇宙裁定在案）与 §2 清洗出的 t/b/c 类的行，构成孤儿候选宇宙；逐族按"六图家族哪张图是该族本命图"判定该挂未挂。
- **宇宙修剪（本簿裁定，机械判据）**：
  - t 类（tests/ 路径或 id 含 TEST）= 测试件，同 TEST 族 401 出宇宙先例，不入孤儿宇宙；
  - b 类（docs/03_modules 蓝图树路径）= 蓝图文档件，归属蓝图族面（蓝图不是"该挂图的代码模块"，其挂图语义=蓝图所载模块的挂图，不重复记账）；
  - c 类（币圈）= Owner 2026-10-04 暂停令，冻结只读，不列施工项不判孤儿（恢复开发时一并清）；
  - f 类（正名家系归并建议）= 归入家系后按家系参加覆盖对账，家系已挂图者成员不判孤儿；
  - k 类（unknown-keep）= 猜不出，交 Owner。
- **本季红1 计数口径**：修剪后宇宙 = ③真无家 767 中剔除 t/b/c 误入面（若有）+ ②清洗后 f 类中"家系整体无图挂"的成员。真无家 767 的域分组面（3a_domain_groups=292 行带 unknown 旗标）按 autonomy/cross_layer 等域给计数，逐域处置建议进首报。

### 红2 · 抄写（复制非引用，INV-1）
- **判据**（图9 F4 先例同款）：①图 yaml 节点字段 >200 字符的散文与源文档逐字对碰；②跨节点同文指纹（同一段落在两节点出现=抄写嫌疑，指针化整改）；③casebooks/trigger_facts/consumers 三字段必须只指针/计数，禁内容复制（consumers 已由机生投影结构性免疫；casebooks 25 格=件2 采纳矩阵内联——**Owner 终批的合法内联例外**，登记豁免不判红）。
- **本季执行面**：对 config/trading_day_cycle_map.yaml（机生层）+fig13_followup 两簿自查；机械跑法进 C4 首报"内收四判据机械跑"段。

### 红3 · 未挂病历（casebooks 完备性）
- **判据**：病历册（12 本矩阵）中每本 ≥1 挂点，或显式登记"不挂理由"；图13 现状=25 格已挂（血肉批 864bfb1b99 件2 采纳矩阵，Owner 终批）为基线。
- **本季执行面**：机生校验——CASEBOOKS_ADOPTED 的册码逐一核在册实存；反向=12 本册逐一核是否有挂点/显式空挂注记。孤儿挂点（指向不存在册）=红3 正例。

## 2. unknown-83 逐行清洗（口径+结果）

清洗判据（优先级序，逐行机生落 `c2_unknown83_classification.csv`）：
1. **t** tests/ 或 scripts/tests/ 路径，或 id 含 TEST 段 → 测试件出宇宙（同 TEST 401 先例）；
2. **c** 路径/语义命中 okx|crypto → 币圈冻结件（Owner 2026-10-04 令，只读保留）；
3. **b** docs/03_modules/ 路径 → 蓝图文档件（归属蓝图族面，不计算码模块）；
4. **f** guess token 对碰在册家系（AUTO→autonomy、EXE→autonomy、SCRIPT→script 家系自证、SH-*→shared 工具族、DATA/DAT→data、INT→intelligence、NLP→nlp、REGIME→regime、RESCHED→resource_sched、GOV/INF/SEC/FE/ML/L02/BT/EX/RK/MKT→同名域家系）→ 家系归并建议；
5. **k** 以上皆不中 → unknown-keep 交 Owner。

结果：**f=55 / b=17 / t=6 / c=2 / k=3**（k 仅剩 D-DATA-CONCEPT-SYS、D-DATA-IO-ANCHOR、MOD-D-CONCEPT-SYS 三行，全在 scripts/industry_graph/ 同一目录=同一语义簇，交 Owner 一并定夺）。
- 分歧消解：严格 83 vs 任务包 74 的 +9 = AUTO 暂编号 7 行（f 类归 autonomy）+ 分类可归 2 行（BT/L02/ML token 命中）——与本簿口径一致，全量落 csv。
- MOD-MKT-DATA（okx_provider）与 MOD-SCRIPT-crypto_daily_review 命中 c 类=币圈冻结；MOD-SCRIPT-run_post_settlement 指向 installers/qmt_watchdog.ps1（历史条目，归属面已在 10-06 D13-07 批修正，此处 census 行为历史残影，f 类归 script 家系并注记）。

## 3. 处置四分与执行边界（并发纪律约束下的自裁）

| 处置 | 对象 | 本批动作 | 依据 |
|------|------|----------|------|
| **并**（家系归并建议） | f 类 55 行 | **只登记建议不执行**：目标册（module_id_registry/module_translation_registry/path_ownership）全是他会话在途修改面（git status MM/M 实证），本批不抢道 | 并发避让铁律 + RULE-WORKSPACE-WIP |
| **退**（退役/删除） | 暂无（币圈=冻结非退役；t 类=出宇宙非删除） | 无 | 删除/退役类唯一 Owner 门位（宪法 §5） |
| **留** | b 类 17（蓝图面合法存在）、c 类 2（Owner 令） | 登记+首报列明 | 判据在案 |
| **修** | unknown-keep 3 行、红2 整改面（若机械跑出） | 首报给处方，零撞册的小修可自裁执行；撞册一律登记 | 自裁协议 |

**待 Owner 裁定清单（C4 首报承装）**：①k 类 3 行归属；②f 类 55 行归并建议的批量准驳（涉及注册册批量写）；③真无家 767 中各域"整域退役/整域补挂"的定性；④复数家 57 行的本命家裁定。

## 4. 封矿自审闸

- 六向台账齐：真源（01/02 两 csv+恒等式）/判据（§1 三红）/清洗（§2 逐行）/处置（§3 四分）/执行边界（并发纪律）/旁证（c1 簿 trigger_facts 计数面）——齐。
- 增量趋零：02 备料四段全部有承接（1_TEST→出宇宙既裁；2_unknown→§2 清洗收敛；3a/3b/4a-d→§1 红1 判据与 §3 处置；无未决考古）——趋零成立。
- 三态裁定：**GO**（转 C4 首报+C3 施工并行）。
