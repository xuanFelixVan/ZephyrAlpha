---
ttl: task_bound
completes_when: 战役 st-vocabconsol-20260918 W8 封账提交后转 archived
---
# target_layer 词表收编施工包（在用域差集归位 + 过时注释治本）

- 任务号：st-vocabconsol-20260918
- 起草日期：2026-09-18（05:35 由上下文再生——原版被并发清扫吞没，见 w2_ruling 留案）
- 类型：治理层 · 规则数据（YAML 真源）收编，无运行时代码改动（除别名消费方迁移）
- 关联宪法条款：RULE-SSOT（规则数据改 YAML）、§4 规范预算（计数用字段不写死散文）、RULE-DEPGRAPH
- 状态：已被 [[裁定#335]] 总裁定覆盖细化（17 值/8 别名/D_CONTRACTS 反转），执行以裁定为准

## 一、问题陈述（三源实测，2026-09-18）

| 真源 | 口径 | 实测数 |
|------|------|--------|
| `_registry/vocabularies/target_layer_vocabulary.yaml` | values 合法值 / deprecated | 45 / 9 |
| `_registry/catalogs/functional_domain_registry.yaml`（FDR） | 去重 domain_id | 68 |
| `_registry/catalogs/module_translation_registry.yaml`（TR） | 去重在用 domain_id | 66 |

**差集**：在用（TR∪FDR）但不在词表（values∪deprecated）的域 = **25 个**。
**反向**：词表 values 全部在两处之一在用，无词表孤儿。
**附带病灶**：词表注释散文写死"functional_domain_registry.yaml（28 域）和 cross_layer_contracts.yaml（11 域）"，FDR 实际 68 域，注释已漂移（违反 §4 文档纪律）。
**校验器基线**：`validate_target_layer.py` 当前 13 error 全在 `tests/knowledge/test_knowledge_artifact_store.py`——是知识库制品的 L1/L2/L3 层位字段被 `target_layer\s*=` 正则误捕，属校验器假红（根因=实现正则背离 docstring 承诺 `(D_[A-Z_]+|基础设施)`），非词表缺口。

## 二、差集清单与处置（25 项，按裁定#335 定稿）

- **A 组 17 值**入 values：D_FRONTEND, D_POSITION, D_PF_ALLOC, D_ORDER, D_SELL_DECISION, D_REGIME, D_ALT_DATA, D_DATA_ENG, D_DATA_SEC, D_REPORTING, D_PLAN, D_EXEC_SIM, D_DIGITAL_TWIN, D_CROSS_ASSET, D_EX_SOR, D_DATA_GOV（归治理域）, **D_CONTRACTS**（原 B 组反转独立——取证系从 D_SHARED 拆出，反合并=推翻已修复裁定链）。is_foundation 全 false。
- **B 组 8 值**入 canonical 的 aliases（三段式过渡，本战役零净删）：D_GOV→D_GOVERNANCE、D_INFRA→D_INFRA_OPS、D_INFRASTRUCTURE→D_INFRA_OPS、D_EXECUTION→D_EX_CORE、D_PORTFOLIO→D_PF_CORE、D_PLAN_ENGINE→D_PLAN、D_SIGNAL→D_SIGLEGACY、D_RESEARCH→D_INTELLIGENCE。
- **前置铁条件**：`_collect_vocab_values` 及全部派生消费者必读 aliases→canonical，否则禁折叠（防 8 值从 WARNING 坠 ERROR）。
- DB 侧仅 D_INFRASTRUCTURE(84)/D_RESEARCH(2) 有节点走 `apply_depgraph --merge-domain`；其余 6 值 DB 无行免迁。tasks.target_layer 历史数字值 1-7 不迁不动仅留案。
- 各值 definition/ai_keywords 落地时逐条补（格式同现有 values 条目）。

## 三、过时注释与散文字段治本

1. 词表"命名约定裁定依据"节：删去"（28 域）（11 域）"写死计数，改为"数量以 FDR/cross_layer_contracts 实时统计为准（RULE-REGISTRY）"。
2. `total_values: 45` 字段：落地后改为实际数，且 `validate_target_layer.py` 启动时读 values 段 len 与字段自校，不一致即 error。
3. 校验器假红治本：正则按 docstring 承诺收紧，13 error 清零；GATE-VOCAB 自触发新增命中 +1（test_multi_contract_adapter.py:224）走基线棘轮 noqa。

## 四、施工序（渐进披露，细节见 construction_sop；执行版=战役 00_skeleton.md W3-W8）

1. 冷启动六步 → 已完成（reaper 绿、能力反查留痕 sid=st-vocabconsol-20260918）。
2. 挖矿四路 → 已完成（w1_mining/ 四文档）。
3. 裁定 → 已完成（裁定#335 入 ruling_registry）。
4. 词表 YAML：A 组 17 值入 values、B 组 aliases 收录、注释治本、version 1.1.0 + 变更历史行。
5. 消费方迁移：FDR/TR 在用小值改挂；DB 2 值 --merge-domain（RULE-SSOT 方向核验）。
6. 校验器：正则收紧 + total_values 自校 + 豁免登记（noqa_exempt_registry，若用新标记）。
7. 差集脚本沉淀 `check_vocab_domain_convergence.py`（14 字段头 + creation_token + gate 登记）。
8. 验收：validate_target_layer exit 0；差集=∅；相关测试绿；git_commit.py --enqueue 落地，`git log -1 --name-only` 核实归属。

## 五、风险与回滚

- is_foundation 全 false ⇒ CT-PIPE 路由零变化；B 组过渡期不改历史数据 ⇒ 回滚=revert 词表单 commit。
- 词表/翻译注册表/FDR 均为 CAS 热文件：写必经 safe_write_text，改前 claim。
- 并发环境实测已吞本包原版一次——**每环节产出当轮即走网关提交，不过夜**。
