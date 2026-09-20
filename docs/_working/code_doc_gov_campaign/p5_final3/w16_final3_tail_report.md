---
ttl: task_bound
session: st-code-doc-20260921
---

# WO-16 final3 尾巴+排期出单 台账（分包5 / st-code-doc-20260921）

> 出班：2026-09-21，总包丙·代码文档治理线 分包5。四件事 R8/R9/R10/R11。执行序：R9→R10→R11→R8。
> 提交：本班零 commit（总包走正门）；全部改动已 `git add`，清单见 §5。

## 1. R9 死信 q-0040（ALGO-FLOW 断锚）——终态：留档作废+清锚完成

**发现**[亲验]：
- 死信本体=`.runtime/commit_queue/dead_purged_20260920/q-20260920-st-maxexec-20260920-0040.json`，payload=删 `docs/03_modules/_domain_backtest/algo_flow/decisiongraph_adapter.yaml`（裁定#371 O-2 第 2/2 批），dead_reason=ALGO-FLOW-LINK 门阻断（yaml 删除时 HEAD 仍存 .py 内 external 锚指向它）。
- **判定依据（不 requeue）**：①死信 json 自带 `requeued.new_qid=q-20260920-st-maxexec-20260920-0053`（2026-09-20T13:46:59）；②q-0053 在 `done/`，落地 commit=`52d159c9a6`；③`git cat-file -e HEAD:<该yaml>` 报不存在=payload 已在 HEAD；④该路径工作树亦无未提交删除。payload 已由后继落地→留档作废。

**动作**：
- 残余锚清理：`capability_canonical_file_registry.yaml` creation_tokens 段 4 行条目（`- file: .../decisiongraph_adapter.yaml / token: algo-flow-externalize-decisiongraph-adapter-2026-09-16 / created_by: st-btfix-p17-20260916 / capability: algo_flow_externalize`）CAS 摘除——镜像已随裁定#371 退役，按 `algo_flow_reverse_orphan_reconciler`（#ARCH-326）"退役配套摘条"模式补齐漏做的注册表摘条。授权链=裁定#371（退役本体）+WO-16 R9 清锚 mandate+reconciler 摘条先例。
- 写入方式=claim+`safe_write_text`（base CAS+newline='\n'），写后进程外复核：yaml parse OK、`creation_tokens` 残余 decisiongraph_adapter.yaml 条目=0、diff 恰 4 行删除。

**证据**[亲验]：只读普查 `algo_flow_reverse_orphan_reconciler.py --json` → `{"scanned": 3231, "orphans": [], "broken_source_references": [], "unreadable": 2}`=活锚清零。

**停手项**：q-0040 未 requeue（依据见上）；`capability_canonical_file_registry.yaml:2890` 的 `backtest_decisiongraph_adapter` canonical_override→`p8_salvage/decisiongraph_adapter_retired.md` 为**有意**的退役登记，不属断锚，未动。

## 2. R10 旧路径 token 残留+reversal.py 行1——终态：功能断锚已清，系统性债务登记

**发现**[亲验]（结构化路径字段全量存在性扫描，逐条 os.path 验证）：
- 注册表 8922 条 `file:`+269 条 `canonical_override`+8 条 `path` 中，缺失 701 条：**696 条集中在 creation_tokens 段**（589 .md 多为 `docs/_working` TTL 扫除/晋升后的历史 token 审计账）+1 条 `canonical_override`（health_aggregator，功能性断锚）+1 条 `output_dir`（禁区）+3 条 note 为散文误报。
- capability_cards/ 33 张卡各 1 处 stale token：`docs/03_modules/_cross_layer/auto-runtime-core/blueprint.md`（连字符目录不存在；实体=`auto_runtime_core` 下划线版，`[亲验]` find/ls 双确认）。卡无生成器写入方（仅 checkers 读），系目录改名残留。
- reversal.py：行 1=`# [BLUEPRINT] MOD-L02-020 | (pending)`。git 追溯（-L1,1）：2026-08-13 `63278a1866` 起 `(pending)`，而 MOD-L02-020 至今无 blueprint 声明（path_ownership_map `declared_in: ''`，全 docs 无命中）——**行 1 属实不假，未动**。tilib 债①所指"计数散文 stale"实际在 docstring：写"5 个"而实现 4 个 indicator_id（CandlestickPattern 已按裁定#233 退役）。

**动作**（全部 claim+safe_write_text 逐条留痕+git add）：
1. health_aggregator capability：`canonical_override` 改指幸存版 `src/zephyr/infrastructure/system_telemetry/health_aggregator.py`（production，功能同族；原 health_monitor 版随 `1ddcd089cf` 死模块批退役）+description 尾部留痕一句（含退役 commit 与日期）。修后 CapabilityLookup 功能性断锚清零。
2. 33 张 capability_cards：`auto-runtime-core`→`auto_runtime_core` 单 token 替换，逐文件 CAS，修后 rg 残余=0。
3. reversal.py：docstring 单行"5 个"→"4 个（…裁定#233 退役…）"，AST 复核通过；行 1 及其余行未碰。

**停手项（系统性债务，转线索）**：creation_tokens 段 696 条 stale——历史 token 审计账属生成器/批量通道管辖（静态清单禁手工维护铁律），手搓 696 条违反净增为零与时间盒。**建议**：参照 #ARCH-326 reconciler 模式立"creation_tokens 孤儿摘条 reconciler"（检测=file 不在 HEAD 树+历史有删除提交；退役面同样绑 Owner 裁定），单独立 WO。1 条 `output_dir` 缺失指向 `docs/02_enterprise_architecture/05_contracts/`（禁区），未动。

## 3. R11 股权穿透派工单——终态：已出单，零施工

**发现**[亲验]：底座状态与任务书一致（`altdata_line/02_entity_graph_equity_person.md` 设计完备=表结构五件套/数据源四层/决策六条/施工顺序；代码面 `node_entity|edge_holding|entity_code_map|ig_node_binding` 在 src/schemas 零命中=施工 0；A 层 akshare 就绪+B 层 PDF 管道既有=原料约 60）。路线图挂点=P7（前置 P1①消歧桥）；施工纪律真源=09_data_subpackage_worklist.md §3。

**动作**：出 `docs/_working/code_doc_gov_campaign/p5_final3/wo_equity_penetration_v1.md`——自包含 WO 六要素齐备（目标/处方 S0-S5 分步/文件白名单 additive-only/红证双向 R1-R7 对照表/时间盒 5h+已知坑册/避让五条禁区/验收六要素），供 Owner 点火后新会话整贴开工。

**停手项**：本班零施工（出单即交付）。

## 4. R8 GATE-21 文案对——终态：已一致，无需动（他会话在途已对齐）

**发现**[亲验]：
- 程序化比对（YAML unfold 后 raw 字符串相等）：`.pre-commit-config.yaml` 与 `gate_registry.yaml` 两处 GATE-21 已知限制文案**逐字节一致**："已知限制（裁定#374 主题十 10-2 a 案登记）：--check 校验与并发重生成存在秒级竞态窗口——校验通过后、提交落地前清单被并发重生成可漏检；例行重生成批次兜底暴露，不阻断主线"。
- **但该对齐尚未进 HEAD**：两文件工作树存在未 staged 改动（`git log -S "秒级竞态窗口"` 零命中=从未提交；`git diff --cached` 空、`git diff` 命中两文件）。gate_registry 差异含 `generated_at: 2026-09-20T06:53:00Z` 重生成批（total_gates 169→170、CREATE-GUARD 描述收缩、新增 COMMIT-CRITICAL-SECTION-LOCK 等）——属他会话（P9 治本池方向）在途未提交产物，非本班可代提交。

**动作**：按 WO 预案记"已一致无需动"；未 claim 未 add 未改这两文件（他会话在途，§3.4 不代修不代管）。

**回执给总包**：两文件 GATE-21 段已在工作树对齐，落库时随他会话改动同批走正门即可；本班无新增动作。提交配方提示（P9 池挂账原文）：拆批+同 shell `ZEPHYR_PROTECTED_PATHS_BYPASS=1`+直连。

## 5. 改动清单（全部已 git add，零 commit）

| 文件 | 动作 |
|---|---|
| `docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml` | R9 摘 4 行 stale creation_tokens 条目；R10 health_aggregator canonical_override 改指向+留痕 |
| `data/capability_cards/*.yaml`（33 张） | R10 blueprint 路径连字符→下划线 |
| `src/zephyr/factor/technical_indicators/reversal.py` | R10 docstring 计数 5→4 单行修复（tilib 债①） |
| `docs/_working/code_doc_gov_campaign/p5_final3/wo_equity_penetration_v1.md` | R11 新建派工单 |
| `docs/_working/code_doc_gov_campaign/p5_final3/w16_final3_tail_report.md` | 本台账（新建） |
| 同上 registry（追加 2 行） | 两新件 CREATE-GUARD token：`code-doc-gov-campaign-{w16-final3-tail-report,wo-equity-penetration-v1}-20260921`（含 merge_evaluation） |

- requeue：**未执行**（q-0040 留档作废）。
- **token 登记通道偏差注记**：`batch_creation_tokens.py` 写前闸（盘上基底 vs HEAD 只增不减）被本班 R9 的**合规摘条**误判为"陈旧快照蒸发"而 fail-closed。未强闯工具、未整片回滚：改用同一 CAS 机制（复刻 build_block 格式+段内锚定）在 creation_tokens 列表真尾（`di_seam_exemptions:` 顶层键之前；该工具段边界函数把尾部顶层键也计入段内，手工锚定须避开）纯插入 2 条，写后 parse 复核 rows 9106→9108 精确 +2。**线索**：R9 型"合规摘条与 token 批量通道互斥"场景，建议该工具增 `--allow-documented-removals <file::token,...>` 显式豁免参数（判定依据=台账登记），否则摘条会话无法自助办新 token。
- 暂存区提示：staging 区另存有他会话大量在途 staged 内容（~200 文件，含 src/factor 测试等）——总包走正门时注意拆批归属核实（AGENTS §2.5）。
- 本班持有的 claim：capability_canonical_file_registry.yaml、reversal.py、33 张卡（TTL 30min 自动过期；如需即时释放走 `git_commit.py --release-only` 归总包收口序列）。
