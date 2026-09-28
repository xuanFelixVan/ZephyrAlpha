---
ttl: task_bound
volume: 91_machine_crosscheck_notes
session: st-ailayer-final-20260924
creation_token: fullflow-machine-crosscheck-gen-20260926
---

# 91 机生四向（实为五向）对账表 · 生成器施工记

> 本册＝生成器的施工案卷与复核面。**所有数字都在机生 YAML 的字段里，本册散文不复制数字**（引用一律写"见 YAML 的 `<字段路径>`"）。
> 机生产物=`docs/_working/fullflow_mining/00_skeleton/91_machine_crosscheck.yaml`（勿手改，改判据请改生成器）。
> 生成器=`scripts/governance/fullflow/generate_fullflow_crosscheck.py`。
> 需求出处=`91_chief_command_wave1.md` §二.2/§二.4（首波五册＝四 P0 漏项册＋机生对账表）＋`92_chief_command_wave2.md` §一（车道作业规范）。

## 一、这把尺量什么（口径）

| 向 | YAML 字段 | 实测口径（method 字段自带，可复算） |
|----|-----------|--------------------------------------|
| F 环节 | `counts.f_links.measured` | 总册表格行 `^\| F\d{2,3} \|` 去重；行数量 `counts.f_links.detail.row_count`，分段 `counts.f_links.per_segment` |
| TDM 节点 | `counts.tdm_nodes.measured` | `config/trading_decision_map.yaml` 的 `^\s*-\s*node_id:`；四流分布 `counts.tdm_nodes.detail.flow_distribution`（已把 YAML 实取值 `entry_flow` 归一为散文用词 `entry`） |
| 策略工厂节点 | `counts.factory_nodes.measured` | `config/strategy_production_map.yaml` 的 `node_id: FAC-` 去重；缺位面 `detail.module_ref_null_ids` |
| ROOR 册数 | `counts.roor_registries.measured` | `registry_id: REG-` 行计数；`summary.total_registries` 字段作为**声称面**入 `claims`，与实测面背离即入 `drift_flags` |
| 挖矿簿册 | `counts.mining_books.measured` | 盘面 `fullflow_mining/**/*.md` 计数；落地面 `detail.head_count`（`git ls-tree HEAD` 同面），差值 `detail.not_in_head_count`＋清单 `detail.not_in_head_sample`（＝P-0 敞口） |

附带观测面（非任务五向，但 wave1 §二.4 的四例里有它们）：
`counts.code_top_domains`（src/zephyr 一级包，排除 `.`/`_` 前缀与 `__pycache__`）、
`counts.functional_domain_registry_entries`（功能域注册表条目，**与"模块册 N 域"不同量纲，见该字段 `caliber_note`，不做直接比对**）。

## 二、逐段挖矿覆盖矩阵（缺口地图，本表价值最高项）

- 位置：`coverage_matrix`；定义面 `coverage_matrix.definition`。
- 判据：环节编号出现在任一**作业簿册**（正文 grep `F\d{2,3}` 大写，或文件名 `f\d{2,3}` 小写认领）＝`covered`；否则 `uncovered`。
- 排除面（`coverage_matrix.definition.non_workbook_excluded`）：总册（编号真源自指）、分工册、交叉验证册、指挥/裁定册、本对账表与本案卷。
  理由＝它们列 F 编号是"编排/指认缺口"，不是"已挖"；把它们算作覆盖会造出假全流通。
  **这是本尺的口径决定，若总筹判"分工册也算认领"，改 `NON_WORKBOOK_RELS` 一处常量即可，勿改判据阈值。**
- 消费方式：`coverage_matrix.uncovered_ids` 就是下一波开册的派单清单（按段聚合见 `coverage_matrix.segments.<段>.uncovered`）。
- 每环节的簿册清单在 `coverage_matrix.segments.<段>.rows[].workbooks`，可逐条反查是谁挖的。

## 三、漂移标志位（不静默）

- `claims[]`：每条＝一个散文/字段声称值 + 当前实测值 + 文件行号 + 原文摘录。
- `drift_flags[]`：`claims` 里 `claimed != measured` 者，或实测面取不到者（`kind: measured_unavailable`）。
- `drift_summary.red`：只要有漂移 / 有 unavailable / 有未覆盖环节 → true。**首轮实测即为 true**（见 YAML 的 `drift_summary`）。
- `unverified_prose_claims[]`：本尺**没有**对照实测面的散文声称（如"模块册 N 模块/M 域""业务资产库 N 表 vs declared N 轴""backlog N 对象"等），如实挂 `status: unverified`，不猜数、不判绿。

### wave1 §二.4"数值漂移四例"在本尺里的落位（复核用，读数见 YAML）

| 血案例 | 本尺落位 |
|--------|---------|
| TDM 过期节点声称 | `drift_flags` 里 `metric: tdm_nodes`，声称面来自 `91_chief_command_wave1.md`，实测来自 TDM YAML |
| F 册 entry 声称 vs 实扫 | 现为 `claims` 里 `metric: tdm_flow_entry` 的**声称==实测**一致项（即该例已归位，本尺现读不报红；若再漂移会自动报红） |
| ROOR 册数与 summary 字段背离 | `drift_flags` 里 `metric: roor_registries` 的整簇（总册两行散文＋ROOR 自身 summary 字段，条数见 YAML 的 `drift_summary.by_metric.roor_registries`） |
| 代码顶层域与册称背离 | `drift_flags` 里 `metric: code_top_domains`，声称面=总册七源行⑥，实测面=目录实扫 |

## 四、复核命令

```bash
# 1. 重跑（幂等自证：两次 sha256 必须相同）
python scripts/governance/fullflow/generate_fullflow_crosscheck.py --out .runtime/tmp/cc_a.yaml --quiet
python scripts/governance/fullflow/generate_fullflow_crosscheck.py --out .runtime/tmp/cc_b.yaml --quiet
certutil -hashfile .runtime/tmp/cc_a.yaml SHA256
certutil -hashfile .runtime/tmp/cc_b.yaml SHA256

# 2. 读数（勿抄进散文，直接看字段）
python - <<'PY'
import yaml
d=yaml.safe_load(open("docs/_working/fullflow_mining/00_skeleton/91_machine_crosscheck.yaml",encoding="utf-8"))
print({k:v["measured"] for k,v in d["counts"].items()})
print(d["drift_summary"])
print("uncovered:",d["coverage_matrix"]["uncovered_ids"])
PY

# 3. 尺的配对测试（含"能红"自证）
python -m pytest tests/governance/fullflow/test_fullflow_crosscheck_generator.py -q

# 4. 与 grep 口径对撞（生成器口径应与之同值）
grep -c -- "- node_id" config/trading_decision_map.yaml
grep -c "node_id: FAC-" config/strategy_production_map.yaml
grep -c "registry_id: REG-" docs/registry_of_registries.yaml
```

## 五、测试面（判通过的脚本须先证明能红）

`tests/governance/fullflow/test_fullflow_crosscheck_generator.py`，夹具=在 `tmp_path` 里造迷你仓库（只含对账所需真源），**不读不写生产文件、禁写 `data/`**：

- 幂等：`test_render_is_byte_identical_across_runs`（同输入两次字节相同）＋ `test_rendered_yaml_has_no_clock_fields`（正则扫 `generated_at|timestamp|created_at|updated_at`，即 RULE-SCHEMA-TZ 的生成器侧）。
- **能红自证（判别力）**：`test_caught_claimed_ne_measured_roor`（夹具造 summary≠条目数）、`test_caught_stale_tdm_node_claim`（夹具散文声称与实扫背离）、`test_duplicate_f_rows_are_flagged`（F 编号复用）、`test_coverage_goes_red_when_a_workbook_is_removed`（删一本簿 → 该环节立刻落 uncovered）。
- **反向自证（防恒红）**：`test_clean_fixture_reports_zero_drift`——全部对齐时必须 0 漂移，否则上面几条红测没有意义。
- **取不到数不填数**：`test_unavailable_metric_is_reported_not_guessed`——删掉 TDM 真源后 `status: unavailable` 且 `measured: null`，并计入 `drift_summary.unavailable_metrics`。
- 首轮实测：全套绿（项数只以 pytest 输出为准，不抄进散文）。且"能红"族不是摆设——写它们时先跑失败过一次：夹具里删掉 TDM 真源，生成器直接抛 `ReadFailure` 崩栈而非报 unavailable，已改为 `_safe_measure` 兜底（这条红测顺手抓出一个真缺陷，正是"恒绿无配对测试＝疑似判据失效"的反面教材）。

## 六、已知局限（勿当完工）

1. 覆盖判据是**编号被提到**＝"有簿认领"，不等于该环节已过全流通四要素（入口/出口/自动化/真源唯一）。翻绿还要作业簿逐环节过四要素，本尺只出缺口地图。
2. 簿册面在战役期间是**活数**：他道正在同工作树补 P0 册，盘面/HEAD 面每轮都变。任何引用前先重跑生成器，读数只认 YAML 字段。
3. `unverified_prose_claims` 里挂着的每一条都是"本尺暂无对照实测面"，不是"已对齐"（条数见 YAML 的 `drift_summary.unverified_prose_claims`）。要给它们配尺须另建实测口径（模块册行数、交叉轴代码常量等），属后续车道。
4. 本生成器只读真源＋只写自身 YAML，未接任何 reconciler/gate 触发面（待总筹决定是否入 `auto_sync_all_registries` 或做成周尺）。
