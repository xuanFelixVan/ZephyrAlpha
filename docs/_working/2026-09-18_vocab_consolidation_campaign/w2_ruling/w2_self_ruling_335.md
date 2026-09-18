---
ttl: task_bound
completes_when: 战役 st-vocabconsol-20260918 W8 封账提交后转 archived
---
# 裁定#335 自裁定全文（分析过程 + 结论）

- 战役：st-vocabconsol-20260918
- 授权基础：Owner 通宵施工令（"中途不问问题、按第一性原理架构师范式自裁定；均无法裁定才登记+跳过"）
- 输入：w1_mining/w1a_consumers.md、w1b_generators.md、w1c_gates.md、w1d_layers.md

## 分析过程（第一性原理 × 长期战略 × 100% AI 开发约束）

1. **词表的本职=防第二真源，不是枚举洁癖**。W1a 实测：16 个"A 组新域"16/16 已在 depgraph DB
   `domains` 表——即**真实世界已发生、词表滞后**。长期看，只要"新增合法值"要走人工裁定，词表
   永远落后于注册表，100% AI 开发下每次落新域都会再积一笔债。故裁：收编的同时，**差集收敛脚本
   常驻化**（check_vocab_domain_convergence.py 进 validators 族），漂移=CI 可见红灯，而非季度考古。
   对标：OpenAPI/JSON Schema 社区的 controlled vocabulary 实践即"词表生成化+差集门禁化"两条腿。
2. **D_CONTRACTS 反转**：施工包原判"并入 D_SHARED"，W1a 取证 `07_fix_5_violations.sql` 显示它
   当年是**从 D_SHARED 拆出**的（有独立契约校验语义，DB 有 2 节点）。反合并=推翻已修复的裁定链，
   第一性原理上"拆出的理由没消失就不能合回去"。裁：升 A 组独立合法值（A 组 16→17，B 组 9→8）。
3. **别名可见性=迁移的隐形炸弹**。W1a：`_collect_vocab_values` 不读 aliases，折叠后 8 个源值从
   WARNING 直接坠 ERROR——词表自毁通道。裁：本战役必须同批扩展 `_collect_vocab_values` 读取
   aliases 段并映射到 canonical（含 validate_target_layer 与一切派生消费者），否则禁 B 组折叠。
4. **D_DATA_GOV 归组**。三值判据：①生产者=治理会话非数据管道；②验证口径=规则覆盖率非行情新鲜度；
   ③vision 判例"治理层=不犯错"——数据治理=对数据域的门禁与标准，属二线拦截职能。裁：**治理域**。
   （量化社区先例：数据治理归 governance/quality 家族而非 data engineering，如 DataHub vs Great
   Expectations 的分工。）
5. **B 组过渡期**。直接改挂会让历史 TaskCard/蓝图引用变未知值；`tasks.target_layer` 另有 146 行
   数字"1-7"历史值（2026-06-13 单批，与词表零交集）证明硬迁必留暗债。裁：**三段式过渡**——
   词表收 aliases（WARNING 级指向 canonical）→ 消费方只在新写入时用 canonical → 终局删除走
   退役审计（§4.2 触发率判据），**不留净删动作给本战役**（避开 Owner 门位"注册表净删"）。
   DB 侧仅 D_INFRASTRUCTURE(84)/D_RESEARCH(2) 有节点，走 `--merge-domain` 官方通道；
   D_GOV/D_INFRA/D_EXECUTION/D_PORTFOLIO/D_PLAN_ENGINE/D_SIGNAL DB 无行，merge 免做。
6. **层字段撞名**。W1b/W1d 双确认：`layer_vocabulary.yaml` v2.0.0（L0-L3，DB layer_id CHECK/trigger
   运行时真源）已占 `layer` 语义，与 vision 职责三分正交。强行复用=把职责分层和运行时栈焊死，
   长远必炸（AI 层横切一切的语义被 CHECK 约束否定）。裁：新字段定名 **responsibility_layer**，
   受控四值 governance/business/ai/infrastructure，真源=新 `domain_responsibility_layer_mapping.yaml`，
   生成器禁从 layer_id/目录名直推；叶级条目由域映射自动派生（§9.5 禁手工清单红线）。
7. **loader 吞条目定性修正**：W1b 证明 safe_load 层零字面重复，真实病灶=entries 段 30 组重复条目
   被 loader dict 折叠覆盖（声明 7090 vs 可见 7060）+ 写手 `add_module_translation.py` 裸
   `write_text`（违硬规则 13，疑即重复形成机制）且整块重写抹掉 module_id/build_status 扩展字段。
   裁：治本三件——写手改 safe_write_text CAS 通道、upsert 前全文件唯一键查重（复发型病灶必须
   查重自愈而非首块替换）、重写保留未知扩展字段（schema 演进兼容）。
8. **GATE-VOCAB 自我触发**：词表在 files_trigger 内，本战役提交必触发全集硬编码扫描，W1a 实测
   新增命中 +1（test_multi_contract_adapter.py:224）。裁：该处按基线棘轮走 gate-vocab noqa 登记，
   不豁免扫描本体。

## 裁定结论（可执行清单）

| # | 结论 | 执行件 |
|---|------|--------|
| 1 | 17 值入 values（D_DATA_GOV 归治理域注释；is_foundation 全 false） | 词表 YAML |
| 2 | 8 值入目标 canonical 的 aliases；D_CONTRACTS 升独立值不合并 | 词表 YAML |
| 3 | `_collect_vocab_values` 等全部派生消费者必读 aliases→canonical，否则禁折叠 | validate_target_layer.py + 派生件 |
| 4 | 终局删除不留本战役；过渡期=WARNING 指向 canonical；DB 仅 2 值走 --merge-domain | 施工 W3 |
| 5 | 新字段名 responsibility_layer + 映射 YAML 真源 + 生成器派生，禁直推 | 施工 W4 |
| 6 | 写手三件套治本（safe_write_text/全文件查重/保留扩展字段） | 施工 W4 |
| 7 | 差集收敛脚本常驻 validators 族并登记 gate/registry | 施工 W3c |
| 8 | tasks.target_layer 历史数字值"1-7"不入词表语义，不迁不动，仅文档留案 | 留案 |
| 9 | GATE-VOCAB 新增命中 +1 走基线棘轮 noqa | 施工 W3 |

## 遗留（不满足自裁定条件的项）

无。施工包 C 组两项（D_DATA_GOV 归组 / 别名过渡期）均已在本裁定内闭合。
