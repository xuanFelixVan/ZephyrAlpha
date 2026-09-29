---
ttl: task_bound
title: "终验循环检查两轮+红蓝对抗报告（对象=20260930 今晚施工面）"
session: st-finaldel-final2-20260930
---

# 终验循环检查两轮 + 红蓝对抗报告（st-finaldel-final2-20260930，2026-09-30）

> 对象：C115（ebbf8718）/C98 三批（4817b8c4f4、8a1ecdc69e、三批见 §2 判定）/昨夜批复面（3dda7e481a、bbcad37e、ac6bd10f、d27daa94、60d7bdda）。
> 纪律：只读为主；唯一修复=域册一行注记（红胜小缺陷，safe_write_text CAS+claim+正门提交）。

## 1. 循环检查两轮读数表（R1→R2 逐项对比）

| # | 检查项 | R1 读数 | R2 读数 | 对比判定 |
|---|--------|---------|---------|---------|
| 1 | 提交链面四套件 -q（integrity_head_baseline+commit_chain_campaign+lock_wait_ledger+ruff_preclean_enqueue） | **66 passed**（29.83s） | **66 passed**（28.77s） | 全等（仅耗时自然波动） |
| 2 | CR-008 域册门 `--check-domain-covers` | CR-008 FAIL 2=COVERS_UNFOUND（agent_communication / data_source_integrator，A 类既有=预期）；CR-007 FAIL 3 STALE | CR-008 FAIL 2（同上逐字节同）；CR-007 FAIL 4 STALE（**+REG-ARCH-ISSUE-001 811→812**） | CR-008 全等；CR-007 差异已归因（见下） |
| 3 | C98 台账复算抽 3 台 | STATE-VOCAB=3；MAP-ALIGNMENT=1438；RECONCILER-HEALTH=[] →无条件（当前 HEAD 全集 18,732） | 同左逐字节全等（HEAD total 同为 18,732） | 全等。复算公式对空触发面打印 0 系伪读数，`_files_trigger_hit` L282 `if not patterns: return True`=无条件实证；台账注记 18,720 系其时点快照（现 HEAD 18,732），语义一致 |
| 4 | 门禁三套（merge_domain_fk_scan_guard+heartbeat_queue_wait+c108）+ commit_queue `--co -q` | 19 passed（3+7+9）；112 collected 零 error | 19 passed（同构成）；112 collected 零 error | 全等 |
| 5 | crosscheck | — | — | **除 CR-007 一项并发漂移外全等** |

**CR-007 差异归因**：R1 后无新 commit（`git log --since 06:10` 空），但 architecture_issue_registry.yaml 与 ruling_registry.yaml 两热册盘面 mtime 晚于 R1 检查点、持有者=st-nightclean-20260929（lock_files 在案，7.3m 新锁）——他会话正在写入，新增 1 条 arch issue 致 REG-ARCH-ISSUE-001 计数漂移。活仓库并发写，非今晚施工面缺陷，不阻断。

## 2. C98 三批落地判定（q-0002 疑案）

- 队列四态目录（pending/processing/done/dead）**均无 q-…-finaldel-c98-…-0002**；q-0001=dead（BARE-SUBPROCESS，后由 4817b8c4f4 直提治愈）、q-0003=done（=4817b8c4f4 一批）。
- `git log -S "C98三批"` 唯一命中 **4817b8c4f4**：三批注册表内容（REF-INTEGRITY 六文本 fnmatch / DEPGRAPH 删 depgraph 裸子串 / RECONCILER-HEALTH 显式无条件 / RECONCILER-FILE-OPS 登记行注）已随一批提交整文件吸收落 HEAD。时序：二批 8a1ecdc69e → 台账注记 ad9b6538 → 一批 4817b8c4f4（吸收了工作树中已在的三批册面态）。
- **判定：三批内容已落 HEAD ✓**（落地载体=一批提交的文件吸收，台账所记"三批 q-…-0002"袋号与实际落地通道不符，属台账记载偏差，非内容缺失）。
- **风险观察（不碰，留档）**：当前暂存区持一份 in_process_gate_registry.yaml 旧快照，其 diff 会把三台回退到 st-gslim 条件态（REFERENCE-INTEGRITY→["docs/"] 等 3 行）；工作树又是三批态（净差对 HEAD=0，MM 态）。他会话在途暂态，归属其所有；若该快照随某袋落地将回退三批行——建议其 owner 落袋前 `git add` 刷新该文件。

## 3. 红蓝对抗逐场景判定表

| 场景 | 攻击面 | 判定 | 证据摘要 |
|------|--------|------|---------|
| C115-红A | 改指后"指到存在但语义错"新漂移（抽 3 条：escalation/persistence/mcp_servers） | **红胜×1（已修）**+登记观察×1+通过×1 | 见 §3.1/3.2/3.3 |
| C98-红a | 违规样例放非触发同语义文件（.pyx/x.py.md）验证收窄=漏检 | **蓝胜** | `_get_staged_py_files` 与 file_copy_gate 内部均 `endswith(".py")` 硬过滤——.pyx/x.py.md 改前也从未进内部扫描（触发只是空跑噪音）；收窄前后内部扫描面相同，零防护损失 |
| C98-红b | 外来 staged 场景 own/foreign 归因 | **蓝胜** | 实探针：own 违规→passed=False 阻断；同一违规文件转 foreign（files 不含它）→passed=True 放行+warn 审计（domain_fk_gate.py:277 `_split_own_foreign`）。套件 domain_fk 17+merge guard 3 绿 |
| C98-红c | STATE-VOCAB 收窄 3 路径后 vocab 目录外新增未登记词表类是否仍检出 | **红胜（登记不修，属 Owner 门位）** | 见 §3.4 |
| C355-红a | 队列有件时心跳豁免滥用边界 | **蓝胜** | `_session_has_pending_queue_items` **session 作用域**（L309 `item.get("session_id")==session_id`）：他会在队 2 项→本会话判活 False；自项在队→True；自项清空剩腐坏项→False（宁自退不扩权）；查询异常→保守 False。边界注记：挂死会话+自家在队项=判活延续，此即 C355 意图保护的落地等待语义，由队列项自身生命周期（drain/requeue/dead/cleanup）兜底，非豁免漏洞 |
| C355-红b / C108-红b | 判别器把 owner 误判 AI 侧的可能性 | **蓝胜** | `current_session_is_ai_side`（ai_secret_exposure.py:459）：误判需双条件（owner shell env 带在册 AI sid）；查询故障→保守非 AI；不在册→非 AI；永不抛异常；只影响读取面断言的 owner 豁免，S1 三族硬编码 deny 仍在兜底；现网 106 键 0 标注=插座态零拒绝 |
| 蓝验 | 相关测试套件全绿 | **绿** | 提交链面 66＋门禁三套 19＋domain_fk 17＋一批四台/own_scope/R5/词表 78 passed+1 skipped（skip=st-chiefzc-rescue-20260928 官方豁免标注，上游实现件未落，在案非本批）＋commit_queue 收集 112 零 error |

### 3.1 C115 红胜（已修）：escalation 条三实体误标"规划中未建"

- 原注（ebbf8718 条2）：`rule_canary_manager/rule_shadow_runner/rule_debt_auditor 规划中未建（承诺面收敛）`。
- 实测：三实体**在产**于 `src/zephyr/gov_enforcement/rule_enforcement/rule_engine/`（带测试 tests/rule/test_rule_*、ALGO_FLOW 出仓件、`__all__` 导出）；**rule_debt_auditor docstring 明写"分析 escalation_rules.yaml 维护债务指标"**——与 covers 声称（规则金丝雀/规则影子运行/规则债务审计）同名同义，非他域巧合同名。
- 修复：改跨子域注记（与同条 DelegationEngine/CircuitBreaker 先例同款），safe_write_text CAS 单 hunk，YAML 进程外复核 94 entries parse 过；CR-008 门复测仍恰 2 条 A 类既有、零新增红。

### 3.2 C115 登记观察（不修）：persistence 条 data_access_audit

- 条3 注记称 `data_access_audit` 等四项"规划中未建"；实测 `src/zephyr/data_security/data_access_auditor.py`（MOD-DATSEC-002，production，D_DATA_SEC 域，#ARCH-256 晋升）语义相近在产。
- 不修理由：persistence 声称的是持久化域内审计日志存储能力，与 data_security 的 UEBA 访问审计**能力同一性存在合理争议**（存 vs 察，层级不同）；force 改注记本身可能构成语义越权。建议域 owner 复核后择一：跨子域注记（指向 data_access_auditor）或维持"未建"并改名避撞。

### 3.3 C115 通过样本

- persistence 条 in-path：task_repo/database_manager/sqlite_schema 均在 `governance/persistence/` 实测存在；跨域注记 gate_repo@gov_enforcement/commit_gates/、olap_engine@frontend/dashboard/ 均实。
- mcp_servers 条：`integration/mcp/` 实测恰 10 server + gateway_server（blueprint_search/doc_guard/gate_engine/governance/rule_discovery/sandbox/sentinel/task_manager/telemetry/vector_memory）；KnowledgeBaseServer 全 src 零命中，VectorMemoryServer 承接注记成立。

### 3.4 C98 红胜（登记不修）：STATE-VOCAB 观测通道回归

- 端到端证据（`_files_trigger_hit` 真分派语义，CommitGateRegistry.check_all L452 未命中→trigger_skip）：
  - vocab 外新增词表类提交 `src/zephyr/trading/zz.py`：旧触发（['src/','.py']）命中=True → 被扫；新触发（vocab 前缀+册路径）命中=False → **门被跳过**。
  - `scripts/*.py` 同理 False；改 vocab 本体/改册两路 True（收窄后仅剩这两类提交触发）。
- 二批阴性验收"未登记词表类 tmp 样例仍检出"系**直调 gate.check()**（绕过 files_trigger 分派）——门函数被调时检出逻辑无恙，但 vocab 目录外**只有词表类、不碰词表源**的提交端到端不再触发门。台账建议依据"其余 src 变更与本门无关"与门自身 INVARIANTS（病根=状态词表散落各模块自造自用）相悖。
- 量级评估：warn-only 观察门（阻断面恒零），损失=词表制度 W3 的审计留痕面（未来升硬阻断的误报率数据源）；门被触发时仍扫全部 own staged .py（混合提交可检出）。
- 不修理由：恢复观测通道=files_trigger 注册表净改，且系 Owner 已批复批次的一部分（批复依据含上述错误断言）——属 Owner 复裁事项。**建议**：复裁恢复 own-diff 常跑（门内=own staged .py AST 扫描，单次成本∝commit 文件数，非 9,374 全量）或词汇类内容触发。

## 4. 修复与登记清单

| 类型 | 对象 | 处置 | 凭证 |
|------|------|------|------|
| 红胜小缺陷（已修） | functional_domain_registry.yaml escalation 条三实体误标 | 跨子域注记改写，CAS 单 hunk | 本袋 commit（含本报告） |
| 红胜（登记不修） | C98 二批 STATE-VOCAB 观测通道回归 | §3.4 建议 Owner 复裁 | 本报告 §3.4 |
| 观察（登记） | C115 persistence 条 data_access_audit 能力同一性 | 域 owner 复核 | 本报告 §3.2 |
| 观察（留档） | 暂存区 in_process_gate_registry.yaml 旧快照（会回退三批 3 行） | 不碰；提请其 owner 落袋前刷新 | 本报告 §2 |
| 台账记载偏差 | C98 台账"三批 q-…-0002"袋号与实际落地通道（一批提交吸收）不符 | 内容已落 HEAD 无缺失；记载随 task_bound 台账归档 | 本报告 §2 |

修复 diff 校验：`git show <本袋> -- docs/01_policies_and_standards/_registry/catalogs/functional_domain_registry.yaml` 恰 1 hunk（escalation 注记行）。

## 5. 总判定

**通过（附 2 项登记+1 项已修）**。两轮循环检查除 CR-007 一项已归因的并发计数漂移外全等；C115 改指 3 抽样中 2 条语义扎实、1 条暴露三实体误标（已当场修复复验）；C98 收窄面零阻断防护损失（own/foreign 归因、.py 语义面均实），唯 STATE-VOCAB 观测通道存在已批复但依据有误的覆盖回归，移交 Owner 复裁；C355/C108 判活与判别器边界经探针+实现双证无滥用面。
