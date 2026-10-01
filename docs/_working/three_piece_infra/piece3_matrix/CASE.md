---
ttl: task_bound
completes_when: 六类边全量 connection_matrix.csv 落本道工作树 + --check 退出码语义钉死 + 四类红证在册 + 仪表盘数据源面可读到矩阵
---

# 包 13.4（戊道）· 全连接矩阵 · 案卷

turn_budget: 150（子代理硬上限，实际用量见末尾）
verified:
  - "TDM 经 loader 实测：182 节点 / 254 边（feed 198 / sequence 38 / feedback 9 / broadcast 9）"
  - "TDM 消费字段实测：module_ref 非空 121（61 空）、data_refs 81 节点（31 distinct DS）、factor_refs 24 节点（32 distinct FCT）、strategy_mounts 19 节点 41 挂载、algo_refs 21 节点"
  - "声明侧空洞复核（第一号红线）：factor_registry.belongs_to_strategies 非空 0/175、inputs 非空 4/175（值是列名 close/limit_up_count…，不是表名）、strategy_registry.alpha_sources 非空 2/161（值确为 FCT-INTRADAY-029）"
  - "data_asset_registry 实测：sources 18（provides_datasets 非空 6 / code_path 非空 18）、datasets 294（produced_by_job 非空 243 / entity_name 非空 294）、jobs 122（source_code_ref 非空 122 / outputs 非空 122）"
  - "jobs[].source_code_ref 有 42 条在盘上不存在（含 37 条目录写法、2 条点分模块写法）——_file_ref 已认目录/点分/::symbol 三种写法，剩下的才是真悬空"
  - "ch_reader.query()（L95）与 ch_writer.query()（L426-433）均返回 TSV 字符串且失败返回空串 → 本尺读数一律走 ch_writer.get_client_strict() + client.execute()（会抛错、返回真行集），失败只记 unreachable 三态"
  - "本机 ClickHouse 本次运行不可达：243 张表 probe 全部 disposition=unreachable，全部降级到 §3.4 grep+tasks.yaml 通道，MISSING_WIRING 在 collection_leg__table 上恒为 0（没有一次把读不到当成表不存在）"
  - "depgraph PG 可达：121 条 module_ref 的 R9 通道全部返回 True（read_channel=filesystem+R9(depgraph)=True）"
  - "Python 3.12.8 在位（RULE-ENV）"
assumed:
  - "docs/_working/decision_map_campaign_20260924/ 是本矩阵唯一 CSV 落地面（目录已存在，只新增 connection_matrix.csv，不改别人任何册）"
  - "JSON 兄弟产物落 data/runtime/connection_matrix/connection_matrix.json：协调契约 §五.7 明文禁 .json 后缀进 docs/_working，故"同基名不同区"落运行区，仪表盘按 mtime 读它（CSV 仍是全量真物）"
  - "TDM 冻结面：本道零改动 config/trading_decision_map.yaml，需改的项列在 register_manifest.md 交总筹"
input_set_disjoint_with:
  - "丁道（st-p2-cens）消费面普查产物与 wiring_registry.yaml 生成器——本矩阵只读注册表/TDM/代码面，零写它的产物"
  - "乙道 create_guard.py、丙道 library/reconciler 面、己·庚道 mining 叶子簿"
  - "总筹独占的 docs/01_policies_and_standards/_registry/**（本道只读，未写一字节）"
evidence_ref.cmd: |
  cd D:\ZephyrAlpha\.worktrees\st-p3-matrix
  PYTHONPATH="src;." python scripts/governance/d5_architecture/generators/generate_connection_matrix.py --print-summary
  PYTHONPATH="src;." python scripts/governance/d5_architecture/generators/generate_connection_matrix.py --check   # 本次 rc=1（差集非空，见 §二）
  PYTHONPATH="src;." python -m pytest tests/governance/test_connection_matrix_rulers.py -q

## 一、判据定义（三态 + 第四态的边界）

| 状态 | 含义 | 判定要件 |
|---|---|---|
| WIRED | 声明且实测有真接线 | declared_by≠NONE 且 wired_by 指到盘上实存的 path:line / 实存表 / tasks.yaml 注册条目 |
| MISSING_WIRING | 指针存在但断了（悬空引用） | 声明在、目标不存在：文件不在（MW-E1）/ DS 经 R11 映射不到表（MW-E2）/ 表经 CH 强通道证伪（MW-E2）/ 策略在两侧名册都查无（MW-E4b、MW-E5） |
| SHOULD_NOT_WIRED_BUT_ISN'T | **该连未连**（头条差集） | 应连性由**独立在册声明**成立（同节点其他消费字段 / 另一本注册表），但接线证据为零 |
| NO_DECLARED_EDGE | 声明缺失（欠账，**永不入差集**） | 两侧都没有可依据的声明字段；[axis-mismatch] 标注"字段有、值域不是这条边" |

红线机械化：`_row()` 构造期硬拒"declared_by=NONE 却判差集"；`_assert_self_consistency()`
硬拒"有真声明源却躲进 NO_DECLARED_EDGE"+分母与行数不等+同行多态。

差集规则册（每条都有在册源，禁"我猜该连"）：
- SB-1 节点有 strategy_mounts/data_refs/factor_refs（消费声明在）但 module_ref 空 → 执行路径该连未连
- SB-2 节点同声明 data_refs×factor_refs，但因子实现面查不到该表引用 → 表→因子该连未连
- SB-3 节点同声明 factor_refs×strategy_mounts，但策略代码面查不到该 FCT- 引用 → 因子→策略该连未连
- SB-4 作业声明 outputs=DS（produced_by_job 在），但 §3.4 口径内查不到任何写表符号 → 采集腿→表该连未连
- SB-5 源声明 provides_datasets 但该 DS 无任何作业产出 → 数据源→采集腿该连未连
- SB-6 采集腿代码文件在、源也声明了它，但 tasks.yaml 无任何对应注册条目（四种对法全不中）→ 腿未挂上运行面
- SB-8 因子在册声明了 belongs_to_strategies 但策略代码面无引用（实测 0 条触发，通道已备好）

## 二、首次真跑实测（六类边 · 全量 1328 行）

**头条：该连未连 = 208 条**（MISSING_WIRING 42 · NO_DECLARED_EDGE 663 分列，三者互不折算）。

| 边类 | WIRED | 该连未连 | 指针悬空 | 声明缺失 | 合计 |
|---|---|---|---|---|---|
| 数据源→采集腿 | 33 | 45 (SB-6) | 40 (MW-E1) | 16 | 134 |
| 采集腿→表 | 201 | 42 (SB-4) | 0 | 51 | 294 |
| 表→因子 | 19 | 21 (SB-2) | 0 | 150 | 190 |
| 因子→策略 | 0 | 80 (SB-3) | 2 (MW-E4b) | 273 | 355 |
| 策略→TDM 节点 | 41 | 0 | 0 | 132 | 173 |
| 节点→执行路径 | 121 | 20 (SB-1) | 0 | 41 | 182 |
| **合计** | **415** | **208** | **42** | **663** | **1328** |

差集构成（按规则）：SB-3 因子→策略 80 · SB-6 腿未挂运行 45 · SB-4 表无写方 42 · SB-2 表→因子 21 · SB-1 无执行路径 20。
SB-1 的 20 个节点（全部有消费声明却无 module_ref）：TDM-E-L2、TDM-E-L2-05、TDM-E-L3、TDM-E-L3-03、
TDM-E-L3-11、TDM-E-L3-12、TDM-E-L4、TDM-E-L9-A01..A10、A12、A13、TDM-P-P2 —— L9 知识供给层 12 个是最大簇。
声明缺失构成：ND-E3 150 · ND-E4b 143 · ND-E5 132 · ND-E4 130 · ND-E2 51 · ND-E6 41 · ND-E1b 12 · ND-E1 4。

诚实边界（防读数被误用）：
1. 208 是**去重后的边条数**（同一条边被多节点声明会合并成一行，声明源全留痕在 declared_by），不等于"人眼数的 208 个缺口"。
2. 因子→策略 0 条 WIRED 是硬事实：`src/zephyr/pf_core/strategies/` 桶内 `FCT-` 出现次数实测为 0（`grep -rl "FCT-" src/zephyr/pf_core/strategies/ | wc -l` = 0），
   即策略侧根本不用因子 id 引用因子——这条轴的"已连"侧目前不存在，80 条 SB-3 全是代理声明推出来的最高信号缺口。
3. 采集腿→表 201 WIRED 的"已连"判据是 §3.4 口径内的符号命中（含 tasks.yaml 的 table 轴），**不等于**该表今天有数据（新鲜度属运行时 SLI，不进静态矩阵）。

## 三、声明侧欠账（矩阵要完整，先补这些——本道无权改，列给总筹）

| 待补字段 | 所在真源 | 卡住的边 | 现在只能记成 |
|---|---|---|---|
| 因子→表轴（把 inputs 升级成表限定，或新增 source_tables） | factor_registry.yaml | 表→因子 | NO_DECLARED_EDGE 150 |
| belongs_to_strategies 全量填写（现 0/175） | factor_registry.yaml | 因子→策略（因子侧） | NO_DECLARED_EDGE 143 |
| 策略→因子轴（alpha_sources 现 2/161 且只 1 个因子） | strategy_registry.yaml | 因子→策略（策略侧） | NO_DECLARED_EDGE 130 |
| 策略→TDM 节点轴（无此字段） | strategy_registry.yaml | 策略→节点（未挂载侧） | NO_DECLARED_EDGE 132 |
| sources[].provides_datasets（现 6/18） | data_asset_registry.yaml | 数据源→采集腿 | NO_DECLARED_EDGE 16 |
| datasets[].produced_by_job（现 243/294） | data_asset_registry.yaml | 采集腿→表 | NO_DECLARED_EDGE 51 |
| 61 个 module_ref=null 节点（20 有消费声明、41 无） | config/trading_decision_map.yaml | 节点→执行路径 | 差集 20 / 声明缺失 41 |
| jobs[].source_code_ref 40 条悬空（含已删模块） | data_asset_registry.yaml | 数据源→采集腿 | MISSING_WIRING 40（施工项，非声明项） |

TDM 侧本道**未提任何改动请求**（冻结面）：所有缺口都在两本业务注册表 + 61 个 module_ref 上。

## 四、读数通道披露（CH 陷阱处置）

- 通道：`zephyr.data.ch_writer.get_client_strict()` → `client.execute("SELECT count() FROM system.tables WHERE database={db:String} AND name={tbl:String}", params)`。
  会抛错、返回真行集；本次 probes=0 / unreachable=243（CH 未起）。
- 禁用的通道：`ch_reader.query()`、`ch_writer.query()`（返回 TSV 串、失败返空串，`r[0][0]` 取到首位数字、`count()` 失败取 0）——本尺一行都不用。
- 降级规则：disposition=unreachable 时**只**记进 read_channel 披露，状态由 §3.4 grep + tasks.yaml 通道判；
  只有 disposition=absent（CH 明确回答"没这张表"）才产 MISSING_WIRING（rule MW-E2）。
- 测试防线：`test_unreachable_clickhouse_is_never_read_as_absent_table` 用桩把 probe 钉成 unreachable，断言 collection_leg__table 的 MISSING_WIRING 恒 0。

## 五、红证（在册、可复跑）

`tests/governance/test_connection_matrix_rulers.py`（12 个用例，全部 tmp_path 沙盘，零写生产 data/）：
1. `test_blanked_module_ref_is_named` 抹掉 TDM-E-L0-04 的 module_ref → 必进差集（SB-1）且同节点基线态为 WIRED（证明红由"抹"造成）
2. `test_blanked_module_ref_without_consumption_is_declared_side_debt` 无消费声明的空 module_ref → 只能记 NO_DECLARED_EDGE，不得混进差集
3. `test_fake_data_ref_lands_missing_wiring_via_r11` 注入 `DS-NOPE-ZZZ999` → 必 MISSING_WIRING 且 read_channel 点名 R11 通道
4. `test_unreachable_clickhouse_is_never_read_as_absent_table` 用桩把 CH probe 钉成 unreachable → 不得产出 MISSING_WIRING（毒通道防线）
5. `test_factor_without_strategy_declaration_is_not_a_wiring_gap` 无声明链接的因子 → NO_DECLARED_EDGE 且该因子在 factor__strategy 上不得出现差集
6. `test_check_returns_nonzero_on_mutated_csv` 改一行 CSV → `--check` rc=1 且 artifact_stale=True（未改动时 stale=False，证口径稳）
7. `test_check_returns_tool_failure_when_artifact_missing` 产物不存在 → rc=2（工具故障与判据红分开）
8. `test_no_declared_edge_never_enters_difference_set` 真跑必须同时数出差集与声明缺失（任一为 0＝尺没接上）
9. `test_illegal_state_combination_raises` 无声明侧判差集 / 未知状态 → 构造期 ValueError
10. `test_probe_without_dot_never_claims_zero_rows` 坏 entity_name 只给"无法拆"归因，不写 0 行
11. `test_matrix_only_reads_declared_inputs` 沙盘不产 data/ 写入面
12. `test_ruler_imports_come_from_this_checkout` 尺与被测件同源（本道实测踩过 PYTHONPATH 冒号分隔在 Windows 失效→zephyr 静默落到主仓 checkout，故此条也是红证）

## 六、与既有尺的分工（不重画第二真源）

- TDM 解析：唯一入口 `zephyr.trading.decision_map.load_decision_map`（本道零自建 YAML 解析）。
- R9（module_ref→depgraph）与 R11（data_refs→DS→CH 表）与 R3（策略引用存在性）：直接 import
  `check_decision_map._module_exists_in_depgraph` / `_load_entity_map` / `collect_strategy_ids_via_ast`，未复制实现。
- §3.4 扫描口径：唯一定义处 `src/zephyr/governance/scan_scope_converged.py`（`SCAN_SCOPE_DIRS/SUFFIXES`
  + `iter_scope_files`），丁道普查引擎应 import 同一常量；本道不重述口径。
- 与 ORPHAN-MODULE 门不并：那门是创建期判据、只 `git grep src/**/*.py`；本口径是运行期消费者普查、
  src+scripts+config 的 .py/.yaml。对象不同→不并（§4 内收判据），分歧已在册。
- 净零：本道新增门禁台数 0（生成器+读侧面板+尺测试），未翻任何 enabled 旗，未新增 reconciler。

## 七、遗留与风险（如实报）

1. `--check` 当前 rc=1（差集 208 条非空），这是**设计上的常态红**，不是工具故障；要它转 0 得先清 §二/§三 的账。
2. CH 可达环境下采集腿→表的 MISSING_WIRING 会开始产数（本次 0 条是"没证伪"不是"全对"），首轮在有 CH 的机器上跑一遍再定基线。
3. 面板 `连接矩阵` Tab 需要一个可读产物才不显示"未生成"；合并后须由落地侧跑一次生成器（或挂事件触发，属总筹排产权）。
4. CSV 全量 1328 行 × 9 列实测 427 KB（JSON 兄弟 811 KB，含逐行 evidence_cmd 全文）——作为永久仪表盘数据源体积可接受，若后续要瘦身须先改契约再动列。
5. 本道跑完时主仓 `D:\ZephyrAlpha` 索引里有两条 staged `D`（`docs/_working/three_piece_infra/00_plan_and_ownership.md`、`LEDGER_three_piece.md`）——
   **非本道所为**（本道对主仓只跑过只读 git 命令），按"他会话在途内容不代修"原样上报，总筹自行判读。
