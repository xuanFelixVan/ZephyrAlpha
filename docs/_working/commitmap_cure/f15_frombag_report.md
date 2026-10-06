---
ttl: task_bound
sid: st-f15-frombag-20261005
generated: 2026-10-06 05:48
task: F15 from-bag 批量重投（任务书五类，死信原快照重建，不依赖工作区）
---

> **固定尾句：判定权归总筹。**

## 1. 班前盘点（dead/ 面）

- dead/*.json 袋总数：**1055**
- 跳过（顶层 requeued=true，历史班次已投）：**562**
- 硬排除 893禁区/空提交 5 袋（F14 §3 圈定，零触碰）：**5**
- 基底冲突（死因以「冲突：/cascade_stale」开头，铁律不碰）：**139**
- 分类外零触碰（死因不含任务书五类任何关键词）：**122**
- **本班目标（五类命中）：227**

## 2. 目标五类构成（一袋可多标签，袋数去重）

| 类别 | 袋数 |
|---|---:|
| ①gate族 | 173 |
| ②GATE-PRECOMMIT | 50 |
| ③ghost/TAKEOVER | 10 |
| ④CLAIM_REQUIRED | 20 |
| ⑤RuntimeError/LandingEnv/OSError | 18 |
| **去重目标合计** | **227** |

关键词命中明细：ALGO-FLOW×54、GATE-PRECOMMIT×50、MODULE-ID×22、CREATE-GUARD×22、CLAIM_REQUIRED×20、TRANSLATION×19、RuntimeError×14、TTL×12、PERMANENT×12、ghost_session×9、COMPLEXITY×8、DIRECTORY×8、DOC-HEADER×7、DEPGRAPH×4、LandingEnv×2、OSError×2、DATETIME×2、TAKEOVER×1、FOLDER×1、R5×1、VOCAB×1

## 3. 执行结果

- 逐袋执行：`python scripts/commit_queue.py requeue <qid> --session st-f15-frombag-20261005 --force --from-bag`
- 重投成功：**218**（新 qid 排 FIFO 队尾，快照来源=死信原快照 blob sha256 自校验）
- 重投失败：**9**（按任务书「重投失败≠停」跳过登记，原袋原位保留）
  - 其他：6
  - TRANSLATION 入队轻检拒：3

## 3.5 重投袋排空侧去向（成稿时点观察，非本班操作）

- 本班新 qid（q-20261006-st-f15-frombag-*）经排空后再次死亡：**69** 袋（死因多为 cascade_stale 基底漂移——重投已复活入队，落地死亡属排空层门债/基底域，非重投失败；留总筹裁定）
  - q-20261006-st-f15-frombag-20261005-0002 :: 网关落盘失败（COMMIT_FAILED）: 门禁 FORGED-GW-MARKER 阻断: FORGED-GW-MARKER: commit message 含非本 session 的 [GW: 标
  - q-20261006-st-f15-frombag-20261005-0003 :: cascade_stale: 基底重校验不适用 ['src/zephyr/pf_alloc/allocation_inputs.py', 'src/zephyr/pf_alloc/allocation
  - q-20261006-st-f15-frombag-20261005-0004 :: cascade_stale: 基底重校验不适用 ['src/zephyr/pf_alloc/allocation_inputs.py', 'src/zephyr/pf_alloc/allocation
  - q-20261006-st-f15-frombag-20261005-0005 :: cascade_stale: 基底重校验不适用 ['docs/01_policies_and_standards/_registry/catalogs/capability_canonical_fil
  - q-20261006-st-f15-frombag-20261005-0006 :: 冲突：快照基底 166525c204c3（与 dev 的共同祖先 166525c204c3）之后 dev 已推进且触及同路径 ['src/zephyr/gov_enforcement/commit_g
  - q-20261006-st-f15-frombag-20261005-0007 :: cascade_stale: 基底重校验不适用 ['src/zephyr/gov_enforcement/commit_gates/__init__.py', 'tests/governance/co
  - q-20261006-st-f15-frombag-20261005-0008 :: cascade_stale: 基底重校验不适用 ['src/zephyr/gov_enforcement/commit_gates/__init__.py', 'tests/governance/co
  - q-20261006-st-f15-frombag-20261005-0009 :: cascade_stale: 基底重校验不适用 ['src/zephyr/gov_enforcement/commit_gates/registry_yaml_parse_gate.py', 'src
  - q-20261006-st-f15-frombag-20261005-0010 :: cascade_stale: 基底重校验不适用 ['scripts/ch/apply_market_tables_ddl.py', 'src/zephyr/data/implementations/a
  - q-20261006-st-f15-frombag-20261005-0011 :: 冲突：快照基底 f7d06a2a33e4（与 dev 的共同祖先 f7d06a2a33e4）之后 dev 已推进且触及同路径 ['config/ai_search_veins.yaml', 'conf
  - q-20261006-st-f15-frombag-20261005-0012 :: landing 异常: RuntimeError: [landing] 非 YAML 件双侧皆改真冲突（整文件三方，死信回退人工）: docs/_working/align_dirty/working
  - q-20261006-st-f15-frombag-20261005-0013 :: cascade_stale: 基底重校验不适用 ['scripts/governance/generate_governance_map.py', 'scripts/governance/genera
  - q-20261006-st-f15-frombag-20261005-0014 :: cascade_stale: 基底重校验不适用 ['tests/governance/test_audit_fix_lanes_rulers.py']（stale_by=q-20261006-st-f
  - q-20261006-st-f15-frombag-20261005-0015 :: cascade_stale: 基底重校验不适用 ['tests/governance/test_commit_queue_base_head.py', 'tests/governance/test_a
  - q-20261006-st-f15-frombag-20261005-0018 :: landing 异常: RuntimeError: [landing] 非 YAML 件双侧皆改真冲突（整文件三方，死信回退人工）: docs/_working/decision_map_campai
  - q-20261006-st-f15-frombag-20261005-0019 :: landing 异常: RuntimeError: [landing] 非 YAML 件双侧皆改真冲突（整文件三方，死信回退人工）: docs/_working/commit_speedup_camp
  - q-20261006-st-f15-frombag-20261005-0023 :: 冲突：快照基底 8f959906f81c（与 dev 的共同祖先 8f959906f81c）之后 dev 已推进且触及同路径 ['config/dev_delivery_map.yaml']——逐文件
  - q-20261006-st-f15-frombag-20261005-0025 :: 网关落盘失败（COMMIT_FAILED）: 门禁 GATE-PRECOMMIT-RUN 阻断: 落地前 pre-commit run 在 staged 面（own-scope 临时索引）发现本提交文
  - q-20261006-st-f15-frombag-20261005-0027 :: 冲突：快照基底 5bad54f31b35（与 dev 的共同祖先 5bad54f31b35）之后 dev 已推进且触及同路径 ['config/governance/noqa_exempt_regis
  - q-20261006-st-f15-frombag-20261005-0028 :: landing 异常: RuntimeError: [landing] 非 YAML 件双侧皆改真冲突（整文件三方，死信回退人工）: docs/_working/pipeline_final/pipe
  - q-20261006-st-f15-frombag-20261005-0029 :: cascade_stale: 基底重校验不适用 ['docs/01_policies_and_standards/_registry/catalogs/capability_canonical_fil
  - q-20261006-st-f15-frombag-20261005-0030 :: cascade_stale: 基底重校验不适用 ['docs/01_policies_and_standards/_registry/catalogs/module_translation_regis
  - q-20261006-st-f15-frombag-20261005-0031 :: landing 异常: RuntimeError: [landing] 非 YAML 件双侧皆改真冲突（整文件三方，死信回退人工）: docs/_working/decision_map_campai
  - q-20261006-st-f15-frombag-20261005-0032 :: 冲突：快照基底 5b8d7c04db83（与 dev 的共同祖先 5b8d7c04db83）之后 dev 已推进且触及同路径 ['scripts/backtest/calibrate_cost_tie
  - q-20261006-st-f15-frombag-20261005-0033 :: landing 异常: RuntimeError: [landing] 非 YAML 件双侧皆改真冲突（整文件三方，死信回退人工）: docs/_working/decision_map_campai
  - q-20261006-st-f15-frombag-20261005-0034 :: landing 异常: RuntimeError: [landing] 非 YAML 件双侧皆改真冲突（整文件三方，死信回退人工）: docs/_working/cmd_ledger/overnigh
  - q-20261006-st-f15-frombag-20261005-0035 :: landing 异常: RuntimeError: [landing] 非 YAML 件双侧皆改真冲突（整文件三方，死信回退人工）: docs/_working/decision_map_campai
  - q-20261006-st-f15-frombag-20261005-0036 :: 冲突：快照基底 613dcc4f9cf8（与 dev 的共同祖先 613dcc4f9cf8）之后 dev 已推进且触及同路径 ['data/strategy_intake/conditional_ta
  - q-20261006-st-f15-frombag-20261005-0037 :: landing 异常: RuntimeError: [landing] 非 YAML 件双侧皆改真冲突（整文件三方，死信回退人工）: docs/_working/decision_map_campai
  - q-20261006-st-f15-frombag-20261005-0038 :: landing 异常: RuntimeError: [landing] 非 YAML 件双侧皆改真冲突（整文件三方，死信回退人工）: docs/_working/decision_map_campai
  - q-20261006-st-f15-frombag-20261005-0039 :: landing 异常: RuntimeError: [landing] 非 YAML 件双侧皆改真冲突（整文件三方，死信回退人工）: docs/_working/decision_map_campai
  - q-20261006-st-f15-frombag-20261005-0040 :: cascade_stale: 基底重校验不适用 ['docs/_working/cmd_ledger/overnight_decisions_20260924.md']（stale_by=q-2026
  - q-20261006-st-f15-frombag-20261005-0041 :: landing 异常: RuntimeError: [landing] 非 YAML 件双侧皆改真冲突（整文件三方，死信回退人工）: docs/_working/decision_map_campai
  - q-20261006-st-f15-frombag-20261005-0042 :: cascade_stale: 基底重校验不适用 ['src/zephyr/gov_enforcement/rule_bridge/commit_belt_daemon.py', 'tests/gove
  - q-20261006-st-f15-frombag-20261005-0043 :: cascade_stale: 基底重校验不适用 ['docs/_working/total_command_closeout/93_owner_menu.md']（stale_by=q-2026100
  - q-20261006-st-f15-frombag-20261005-0044 :: cascade_stale: 基底重校验不适用 ['docs/_working/total_command_closeout/93_owner_menu.md']（stale_by=q-2026100
  - q-20261006-st-f15-frombag-20261005-0045 :: cascade_stale: 基底重校验不适用 ['docs/_working/total_command_closeout/93_owner_menu.md']（stale_by=q-2026100
  - q-20261006-st-f15-frombag-20261005-0046 :: cascade_stale: 基底重校验不适用 ['docs/_working/total_command_closeout/93_owner_menu.md']（stale_by=q-2026100
  - q-20261006-st-f15-frombag-20261005-0048 :: 网关落盘失败（COMMIT_FAILED）: 门禁 TRANSLATION-COVERAGE 阻断: TRANSLATION-COVERAGE: 2 个新建 .py 文件在翻译真源（module_tr
  - q-20261006-st-f15-frombag-20261005-0049 :: cascade_stale: 基底重校验不适用 ['src/zephyr/governance/audit/reconciliation_registry.py', 'src/zephyr/libra
  - q-20261006-st-f15-frombag-20261005-0050 :: 冲突：快照基底 ffc3ce5f4929（与 dev 的共同祖先 ffc3ce5f4929）之后 dev 已推进且触及同路径 ['src/zephyr/data/__init__.py', 'src/
  - q-20261006-st-f15-frombag-20261005-0053 :: 冲突：快照基底 268f2ff07ed6（与 dev 的共同祖先 268f2ff07ed6）之后 dev 已推进且触及同路径 ['config/flags.yaml', 'scripts/backup
  - q-20261006-st-f15-frombag-20261005-0054 :: 网关落盘失败（COMMIT_FAILED）: 门禁 GATE-PRECOMMIT-RUN 阻断: 落地前 pre-commit run 在 staged 面（own-scope 临时索引）发现本提交文
  - q-20261006-st-f15-frombag-20261005-0056 :: 冲突：快照基底 1dd6c70c74e9（与 dev 的共同祖先 1dd6c70c74e9）之后 dev 已推进且触及同路径 ['scripts/governance/data_supply/__in
  - q-20261006-st-f15-frombag-20261005-0059 :: cascade_stale: 基底重校验不适用 ['scripts/backtest/factory_grid_executor.py']（stale_by=q-20260929-st-secbatc
  - q-20261006-st-f15-frombag-20261005-0060 :: 网关落盘失败（COMMIT_FAILED）: 门禁 GATE-PRECOMMIT-RUN 阻断: 落地前 pre-commit run 在 staged 面（own-scope 临时索引）发现本提交文
  - q-20261006-st-f15-frombag-20261005-0062 :: 网关落盘失败（COMMIT_FAILED）: 门禁 TRANSLATION-COVERAGE 阻断: TRANSLATION-COVERAGE: 1 个新建 .py 文件在翻译真源（module_tr
  - q-20261006-st-f15-frombag-20261005-0063 :: 冲突：快照基底 1dd6c70c74e9（与 dev 的共同祖先 1dd6c70c74e9）之后 dev 已推进且触及同路径 ['scripts/governance/data_supply/ch_p
  - q-20261006-st-f15-frombag-20261005-0064 :: 冲突：快照基底 1dd6c70c74e9（与 dev 的共同祖先 1dd6c70c74e9）之后 dev 已推进且触及同路径 ['scripts/governance/wave1a/ch_read_s
  - q-20261006-st-f15-frombag-20261005-0066 :: 冲突：快照基底 1dd6c70c74e9（与 dev 的共同祖先 1dd6c70c74e9）之后 dev 已推进且触及同路径 ['scripts/governance/d6_security/dete

## 4. 班后盘点（成稿时点 dead/ 重扫）

- dead/*.json 袋总数：1186（班前 1055）
- requeued=true：783（班前 562，+221）
- 残余五类目标：74（含本班失败袋原位+执行窗内他会话新增死信，均零触碰）
- 基底冲突残余：190｜分类外残余：134｜893禁区：5（均零触碰）

## 5. 失败清单（死因原文全文）

### 失败 1/9：q-20260923-st-nightdata-20260923-0001（类别 ⑤RuntimeError/LandingEnv/OSError）

- 重投输出尾：`） | [TRANSLATION-COVERAGE] TRANSLATION-COVERAGE 预检（入队面等价判定，落地仿真态翻译册）：1 个新建 .py 文件在翻译真源（module_translation_registry.yaml）缺合格 plain_zh 大白话简介。修复：python scripts/governance/d3_metadata/add_module_translation.py --path <file_path> --domain <D_*> --name-zh <中文名> --plain-zh <大白话简介>。详情: 无 plain_zh 简介[scripts`
- 死因原文：
```
landing 异常: RuntimeError: prestage 拒绝：以下快照路径被 .gitignore 忽略（再生产物区，禁入 git）：
  - scripts/data/backfill_etf60min_depth.py
修复：①把文件移到非忽略目录（如 scripts/data/ 下代码应移 scripts/）后重新入队；②或确认该路径应入库，修 .gitignore 精确豁免（对齐 sz_open_data 先例）后重新入队
```
### 失败 2/9：q-20260924-st-pipeline-final-20260924-0022（类别 ①gate族）

- 重投输出尾：`d', 'data/strategy_intake/grid_gpu_sectorcond_20260924-0834/sector_index.json']. commit 新建 .md/.sh/.ps1/.mmd/.json 文件前 MUST 在 capability_canonical_file_registry.yaml 的 creation_tokens 字段登记 token（声明创建意图 + 关联 capability）。格式: - file: "<相对路径>"  token: "auto-xxx"  created_by: "session-xxx"  capability: "`
- 死因原文：
```
网关落盘失败（COMMIT_FAILED）: 门禁 DIRECTORY-CONTRACT 阻断: [GATE-DIRECTORY-CONTRACT] 9 个发现（9 errors, 0 warnings）:
  [error] DCR-005 docs/_working/sector_line/gpu_input_pack/build_gpu_input_pack.py
    扩展名 .py 不在 docs/_working/ 的 allowed 清单 ['.csv', '.html', '.md', '.yaml'] 内
  [error] DCR-006 docs/_working/sector_line/gpu_input_pack/build_gpu_input_pack.py
    扩展名 .py 在 docs/_working/ 的 forbidden 清单内
  [error] DCR-008 docs/_working/sector_line/gpu_input_pack/build_gpu_input_pack.py
    文件扩展名 .py 不匹配目录用途 task_document（purpose_allowed_extensions=['.md', '.csv', '.yaml', '.html']），目录 docs/_working/
  [error] DCR-005 docs/_working/sector_line/frontend_map_wip_20260924.patch
    扩展名 .patch 不在 docs/_working/ 的 allowed 清单 ['.csv', '.html', '.md', '.yaml'] 内
  [error] DCR-008 docs/_working/sector_line/frontend_map_wip_20260924.patch
    文件扩展名 .patch 不匹配目录用途 task_document（purpose_allowed_extensions=['.md', '.csv', '.yaml', '.html']），目录 docs/_working/
  [error] DCR-005 data/strategy_intake/grid_gpu_sectorcond_20260924-0834/is_holdout.npy
    扩展名 .npy 不在 data/ 的 allowed 清单 ['.bin', '.csv', '.db', '.duckdb', '.gitkeep', '.index', '.json', '.jsonl', '.log', '.md', '.mmd', '.ndjson', '.sql', '.sqlite3', '.tar.gz', '.wal', '.yaml'] 内
  [error] DCR-005 data/strategy_intake/grid_gpu_sectorcond_20260924-0834/momentum_pct.npy
    扩展名 .npy 不在 data/ 的 allowed 清单 ['.bin', '.csv', '.db', '.duckdb', '.gitkeep', '.index', '.json', '.jsonl', '.log', '.md', '.mmd', '.ndjson', '.sql', '.sqlite3', '.tar.gz', '.wal', '.yaml'] 内
  [error] DCR-005 data/strategy_intake/grid_gpu_sectorcond_20260924-0834/rrg_quadrant.npy
    扩展名 .npy 不在 data/ 的 allowed 清单 ['.bin', '.csv', '.db', '.duckdb', '.gitkeep', '.index', '.json', '.jsonl', '.log', '.md', '.mmd', '.ndjson', '.sql', '.sqlite3', '.tar.gz', '.wal', '.yaml'] 内
  [error] DCR-005 data/strategy_intake/grid_gpu_sectorcond_20260924-0834/watch_score.npy
    扩展名 .npy 不在 data/ 的 allowed 清单 ['.bin', '.csv', '.db', '.duckdb', '.gitkeep', '.index', '.json', '.jsonl', '.log', '.md', '.mmd', '
```
### 失败 3/9：q-20260924-st-pipeline-final-20260924-0029（类别 ①gate族）

- 重投输出尾：`_060 §2）: ['scripts/sector_line/build_gpu_input_pack.py', 'scripts/sector_line/freeze_baseline.py']. commit 新建 .py 文件前 MUST 在 capability_canonical_file_registry.yaml 的 creation_tokens 字段登记 token（声明创建意图 + 关联 capability）。格式: - file: "<相对路径>"  token: "auto-xxx"  created_by: "session-xxx"  capability: "`
- 死因原文：
```
网关落盘失败（COMMIT_FAILED）: 门禁 TRANSLATION-COVERAGE 阻断: TRANSLATION-COVERAGE: 2 个新建 .py 文件在翻译真源（module_translation_registry.yaml）缺合格 plain_zh 大白话简介。修复：python scripts/governance/d3_metadata/add_module_translation.py --path <file_path> --domain <D_*> --name-zh <中文名> --plain-zh <大白话简介>。详情: 无 plain_zh 简介[scripts/sector_line/build_gpu_input_pack.py, scripts/sector_line/freeze_baseline.py]
```
### 失败 4/9：q-20261005-st-f11-requeue-20261005-0080（类别 ③ghost/TAKEOVER）

- 重投输出尾：`translated/c4_370d098d7c54_vrev001_warm_oversold.py, scripts/backtest/translated/c4_cd3885d23838_vrev002_no_bottom_fish.py, scripts/backtest/translated/c4_6986c63122a5_momtrend002_ma_cross.py, scripts/backtest/translated/c4_7865eeda0157_momtrend019_first_breakout.py, scripts/backtest/translated/c4_6`
- 死因原文：
```
ghost_session: 属主会话 st-f11-requeue-20261005 已死（heartbeat=exited / 注册表无在册），自动重投被存活闸拒绝（裁定#459；CLI 手动 requeue 不受闸限，人工可强制）
```
### 失败 5/9：q-20261005-st-fg-srcline1-20261005-0001（类别 ①gate族、⑤RuntimeError/LandingEnv/OSError）

- 重投输出尾：`] TRANSLATION-COVERAGE 预检（入队面等价判定，落地仿真态翻译册）：1 个新建 .py 文件在翻译真源（module_translation_registry.yaml）缺合格 plain_zh 大白话简介。修复：python scripts/governance/d3_metadata/add_module_translation.py --path <file_path> --domain <D_*> --name-zh <中文名> --plain-zh <大白话简介>。详情: 无 plain_zh 简介[src/zephyr/signal_ashare/source_`
- 死因原文：
```
landing 异常: RuntimeError: [landing] 注册表三向合并失败（死信回退人工）: docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml: theirs(快照) 同侧身份键重复且内容冲突（同键异容，仓库态缺陷）: file=src/zephyr/gov_enforcement/commit_gates/map_family/data_supply_chain_map_gate.py|token=mapfamily-data_supply_chain_map_gate-20261001——死信回人工；处方: 跑 registry 去重对账器核对存量，勿手拼 YAML
--- 在册先条 (first) ---
file: src/zephyr/gov_enforcement/commit_gates/map_family/data_supply_chain_map_gate.py
token: mapfamily-data_supply_chain_map_gate-20261001
created_by: st-matrix-final-20260930
capability_id: map_family_data_supply_chain_map_gate
merge_evaluation: 跨域不同对象不并：map_family 三 gate=三图族提交面执法件，收纳子目录因 FOLDER-CAPACITY 120
  硬上限，非既有 gate 第二实现

--- 重复后条 (dup) ---
file: src/zephyr/gov_enforcement/commit_gates/map_family/data_supply_chain_map_gate.py
token: mapfamily-data_supply_chain_map_gate-20261001
created_by: st-matrix-final-20260930
capability_id: map_family_data_supply_chain_map_gate
no_mount_reason: 图族守门员执法件本身不入图节点（挂载语义=其守卫的图 YAML 输入面，见各文件 [CONSUMERS]/[DEPENDENCIES]
  声明面）；纯治理基建非业务资产
merge_evaluation: 跨域不同对象不并：map_family 三 gate=三图族提交面执法件，收纳子目录因 FOLDER-CAPACITY 120
  硬上限，非既有 gate 第二实现
```
### 失败 6/9：q-20261005-st-fg-srcline1-20261005-0002（类别 ①gate族）

- 重投输出尾：`NSLATION-COVERAGE 预检（入队面等价判定，落地仿真态翻译册）：1 个新建 .py 文件在翻译真源（module_translation_registry.yaml）缺合格 plain_zh 大白话简介。修复：python scripts/governance/d3_metadata/add_module_translation.py --path <file_path> --domain <D_*> --name-zh <中文名> --plain-zh <大白话简介>。详情: 无 plain_zh 简介[src/zephyr/signal_ashare/source_line/`
- 死因原文：
```
网关落盘失败（COMMIT_FAILED）: 门禁 CREATE-GUARD 阻断: 无 creation_token，禁止造第二真源（trae_060 §2）: ['src/zephyr/signal_ashare/source_line/tick_microstructure_criterion.py']. commit 新建 .py 文件前 MUST 在 capability_canonical_file_registry.yaml 的 creation_tokens 字段登记 token（声明创建意图 + 关联 capability）。格式: - file: "<相对路径>"  token: "auto-xxx"  created_by: "session-xxx"  capability: "xxx"
```
### 失败 7/9：q-20261005-st-fg-srcline1-20261005-0003（类别 ①gate族）

- 重投输出尾：` TRANSLATION-COVERAGE 预检（入队面等价判定，落地仿真态翻译册）：1 个新建 .py 文件在翻译真源（module_translation_registry.yaml）缺合格 plain_zh 大白话简介。修复：python scripts/governance/d3_metadata/add_module_translation.py --path <file_path> --domain <D_*> --name-zh <中文名> --plain-zh <大白话简介>。详情: 无 plain_zh 简介[src/zephyr/signal_ashare/source_l`
- 死因原文：
```
网关落盘失败（COMMIT_FAILED）: 门禁 CREATE-GUARD 阻断: 无 creation_token，禁止造第二真源（trae_060 §2）: ['src/zephyr/signal_ashare/source_line/sector_rotation_criterion.py']. commit 新建 .py 文件前 MUST 在 capability_canonical_file_registry.yaml 的 creation_tokens 字段登记 token（声明创建意图 + 关联 capability）。格式: - file: "<相对路径>"  token: "auto-xxx"  created_by: "session-xxx"  capability: "xxx"
```
### 失败 8/9：q-20261005-st-fg-srcline1-20261005-0004（类别 ⑤RuntimeError/LandingEnv/OSError）

- 重投输出尾：`TION-COVERAGE 预检（入队面等价判定，落地仿真态翻译册）：1 个新建 .py 文件在翻译真源（module_translation_registry.yaml）缺合格 plain_zh 大白话简介。修复：python scripts/governance/d3_metadata/add_module_translation.py --path <file_path> --domain <D_*> --name-zh <中文名> --plain-zh <大白话简介>。详情: 无 plain_zh 简介[src/zephyr/signal_ashare/source_line/fund`
- 死因原文：
```
landing 异常: RuntimeError: [landing] 注册表三向合并失败（死信回退人工）: docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml: 同键条目内容冲突: file=docs/_working/map_build/fig16_legislation/00_skeleton.md|token=fig16-00_skeleton-20261005（双侧各自新增且内容异）
--- ours (dev) ---
file: docs/_working/map_build/fig16_legislation/00_skeleton.md
token: fig16-00_skeleton-20261005
created_by: st-fig16-20261005
capability: governance_legislation_map
merge_evaluation: 裁定准入执行件：立法流状态机图，同真源(pg_ledger+裁定册)派生，无同域重复

--- theirs (快照) ---
file: docs/_working/map_build/fig16_legislation/00_skeleton.md
token: fig16-00_skeleton-20261005
capability_id: governance_legislation_map
merge_evaluation: 裁定准入执行件：立法流状态机图，同真源(pg_ledger+裁定册)派生，无同域重复
```
### 失败 9/9：q-20261005-st-tdm-mountgate-20261005-0015（类别 ①gate族）

- 重投输出尾：`等价判定，落地仿真态翻译册）：2 个新建 .py 文件在翻译真源（module_translation_registry.yaml）缺合格 plain_zh 大白话简介。修复：python scripts/governance/d3_metadata/add_module_translation.py --path <file_path> --domain <D_*> --name-zh <中文名> --plain-zh <大白话简介>。详情: 无 plain_zh 简介[scripts/governance/_shared/mount_obligation.py, scripts/gener`
- 死因原文：
```
网关落盘失败（COMMIT_FAILED）: 门禁 TRANSLATION-COVERAGE 阻断: TRANSLATION-COVERAGE: 2 个新建 .py 文件在翻译真源（module_translation_registry.yaml）缺合格 plain_zh 大白话简介。修复：python scripts/governance/d3_metadata/add_module_translation.py --path <file_path> --domain <D_*> --name-zh <中文名> --plain-zh <大白话简介>。详情: 无 plain_zh 简介[scripts/generate_mount_obligation_manifest.py, scripts/governance/_shared/mount_obligation.py]
```

## 6. 铁律遵守声明

- 基底冲突袋零 requeue（死因前缀机械判定，班前 139 袋原位）
- 空提交/893禁区 5 袋零触碰（F14 §3 圈定 qid 硬排除）
- 分类外 122 袋零 requeue/零改写；全程零归档、零判定（关键词机械匹配）
- 全程仅 requeue 任务书五类 227 袋，逐袋留痕（f15_results.jsonl，.runtime/tmp/st-f15-frombag-20261005/）

判定权归总筹。
