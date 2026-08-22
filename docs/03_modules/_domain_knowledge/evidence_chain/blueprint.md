---
blueprint_id: MOD-EVIDENCE_CHAIN
module_name: evidence_chain
domain: D_KNOWLEDGE
doc_type: blueprint
ttl: permanent
design_maturity: testing
stability: evolving
safety_level: L
ai_autonomy: ai_modifiable
version: "0.1.0"
created: 2026-08-22
last_updated: 2026-08-22
owner: ZephyrAlpha-Owner
---

# MOD-EVIDENCE_CHAIN evidence_chain 蓝图

> 紧凑版（SOP Step 4 补建，四件合一）。设计真源：11号文 §3.1 / §4.2 P0-1~P0-4 + 18号清单 §6 波4-11 + #ARCH-165。
> 代码：`src/zephyr/research/evidence/`（hypothesis_registry.py / evidence_chain.py / iteration_guide.py / batch_entry.py）

## 0. 定位

研究证据关联组件（AQuA"证据保留→迭代引导"机制落地）：治理"重复验证已否定的假设"和"忘记为什么放弃某条线"的研究迭代浪费——假设必须可机读、状态机驱动、证据可追溯。域归属：2026-08-22 统筹裁定 D_RESEARCH 不在 depgraph domains 表，归 D_KNOWLEDGE（假设/证据=知识资产）。落点 `data/research/evidence/`（参照 data/brain/passports/ 研究资产先例；.runtime 有 TTL 清理属易失区，严禁落永久资产）。日频/周频批量消费，不做盘中实时更新（11号文 §2.3/§5-3）。

## 1. 四件职责与接口

| 件 | 职责 | 关键接口 |
|---|---|---|
| hypothesis_registry（P0-1） | 假设结构化 CRUD + 五态生命周期状态机 + JSON 原子落盘 | `HypothesisRegistry.create/get/list_all/update/transition`；id=HYP-%04d 单调递增 |
| evidence_chain（P0-2） | 证据三态挂链 + 外键约束 + SHA-256 固化防篡改，append-only jsonl | `EvidenceChain.append/list_for/summary_for/verify_integrity`；id=EV-%04d |
| iteration_guide（P0-3） | 显式规则集从证据聚合出 continue/pivot/abandon 建议 | `IterationGuide.evaluate/evaluate_all`；`load_rules()` 默认 config/iteration_guide_rules.yaml |
| batch_entry（P0-4） | 日/周频全量（未归档）批量评估 CLI + 计划任务挂点 | `run_batch(frequency=daily/weekly, ...)`；`python -m zephyr.research.evidence.batch_entry` |

## 2. 输出契约

- `Hypothesis`（frozen）：hypothesis_id/statement/status/proposed_at/updated_at/tags/notes/status_history（每次迁移留痕 from/to/at/reason）；落盘 hypotheses.json（atomic_write tmp+os.replace），读损坏 fail-fast 不静默兜底。
- `EvidenceEntry`（frozen）：evidence_id/hypothesis_id/polarity/source/content/created_at/content_hash（六字段规范化 JSON 的 SHA-256）；落盘 evidence_chain.jsonl 单行追加（flush+fsync）。`EvidenceSummary` 聚合视图（三态计数+latest_support_at/latest_at）为迭代引导器输入契约。
- `Guidance`：hypothesis_id/recommendation/rule_id/rationale_zh/evidence_counts/generated_at——每条建议必带命中规则 id + 证据计数 + 中文理由（P0-3 可追溯）。
- 批量产出：`data/research/evidence/guidance/guidance_YYYYMMDD_HHMMSS_{frequency}.json`（原子写）+ `BatchReport`（evaluated_count/skipped_archived_count/output_path）；CLI 返回码 0 成功 / 3 盘中拒绝。

## 3. 不变量

- 状态机仅允许 proposed→testing→supported/refuted→archived（另含 proposed/testing→archived 中止边）；archived 终态不可迁出不可变更；proposed→supported/refuted 直飞被拒（须过 testing）
- 证据 append-only 只增不改不删；polarity ∈ {support, contradict, neutral} 词表外拒绝；hypothesis_id 外键必须已存在（拒挂孤儿证据）；verify_integrity 全量重算不一致即篡改检出 fail-fast；jsonl 任一行不可解析 fail-fast
- 规则按配置顺序首命中生效；recommendation 三态词表；未知条件键/重复 rule_id/词表外建议加载即拒；无命中规则显式报错（不静默给建议）；条件 AND 语义（support_gte/contradict_gte/no_support_within_weeks 等七键词表）
- 盘中零调用：工作日 09:30-15:00 CST（含午间休市从严，节假日按交易日从严）拒绝执行无例外无旁路；本模块不得被任何盘中/交易路径 import（静态约束）；仅评估未归档假设；批量前证据链完整性自检（防线前移）

## 4. 降级行为

- ERROR_CONTRACT 错误码：ZA-RE-0001（契约违反/落盘损坏）/0002（假设不存在）/0003（非法迁移）；ZA-RE-0010（链落盘损坏）/0011（外键）/0012（词表外极性）/0013（篡改检出）；ZA-RE-0020（无规则命中）/0021（规则配置非法）；ZA-RE-0030/0031（盘中执行尝试）
- frequency 词表外 → ValueError；全部 fail-fast，无静默兜底路径

## 5. 边界（不做）

- 不做盘中实时证据关联；不开 archived 翻案重开边（Phase 0）；不复用 governance EvidencePack 类（借鉴 hash 完整性模式，语义差异：审计包"打包封存" vs 本链"持续生长"，11号文 §2.1 划界）
- 不做学习模型置信度更新（假设量级不足，显式规则可审计可交叉验证）
- 计划任务注册由统筹裁定接线（本模块只提供 CLI 入口）；Phase 3 闭环回流接线由 11号文 §4.5 裁定

## 6. 测试

tests/research/test_evidence_phase0.py（56 用例，含盘中守卫 + 全 src grep 包外零 import 佐证）。
