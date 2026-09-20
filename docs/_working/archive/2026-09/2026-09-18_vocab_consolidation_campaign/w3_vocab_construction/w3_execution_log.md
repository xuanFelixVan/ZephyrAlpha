---
ttl: task_bound
completes_when: 战役 st-vocabconsol-20260918 W8 封账提交后转 archived
---

# W3 施工留痕——词表收编 v1.1.0 + 校验器治本 + 差集常驻件

- 执行时间：2026-09-18 05:40-06:10
- 依据：裁定#335 结论 1/2/3/7/8/9；输入=w1_mining 四文档

## 落地清单

| 件 | 改动 | 验收证据（命令→结果） |
|----|------|----------------------|
| `target_layer_vocabulary.yaml` | v1.1.0：A 组 17 值入 values（is_foundation 全 false）、B 组 8 值入 6 个 canonical 的 aliases、D_PLAN 携 alias、删 28/11 域散文计数、变更历史行 | `yaml.safe_load` 后 values=62 无重复、foundation 三项未动、aliases 10 个 |
| `validate_target_layer.py` | 正则归位 `(?:D[-_][A-Z_]+\|基础设施)`（采纳 W5 实测式，保连字符废弃值 WARNING 防再发）+ aliases→WARNING 分支 + total_values 启动自校 + docstring 同步 | 改前基线 13 errors → 改后 `exit=0`，"合法值 62/废弃 9/别名 10" |
| `src/zephyr/shared/io/yaml_utils.py` | `_collect_vocab_values` 并入 aliases（裁定#335 前置铁条件，SSoT 单点，全共享消费者受益） | `load_vocabulary_values` 实测 72（62+10），D_GOV/D_INFRASTRUCTURE 可见 |
| `check_vocab_domain_convergence.py`（新，scaffold 通道） | 三源差集常驻校验：known=values∪aliases∪deprecated；在用=FDR entries[].domain ∪ TR entries/algo_submodules domain_id（**字段位口径**，实测排除 D_XXX 模板/D_FBL_\* 通配/退役注释三类散文误捕）；DB 差集 --with-db 且永远 advisory | 实跑 exit=0（known=79/在用=72/差集=∅）；advisory 列出 DB 侧 *_SCRIPTS+D_TEST 共 10 域（留案，见下） |
| `tests/governance/d5_architecture/`（新） | 6 用例：收敛过/滞后红/散文不算/DB 不翻转/缺件 error/**真实三源差集=∅ 常驻验收** | 6 passed |
| depgraph | `--add-design-node ... planned`（node_id=14799407）+ scaffold 自动登记 script-manifest | 节点入图 |
| creation_token | scaffold `_register_creation_token` 自动落 capability registry（token=auto-scaffold-...-20260918） | scaffold 输出 REGISTERED |
| 翻译登记 | 走 **W4e 治本后写手** `add_module_translation.py --path ...`（顺带完成新写手首次实战冒烟）entries 7073 | 新增成功 + `--dedupe --dry-run` 报 0 组（幂等） |

## 设计决策（自裁定补充，均落裁定#335 框架内）

1. **字段位口径**：差集脚本只认 YAML 结构字段，不认散文——D_XXX（词表格式示例）、
   D_FBL_*（通配）、D_BEHAVIORAL_AUDIT（ARCH-169 退役留案注释）三例实测证明文本正则会
   制造永久性假红。判据：在用=被机器消费的字段位。
2. **DB advisory 不置非零**：depgraph domains 表含 10 个脚本治理命名空间域
   （D_ARCH_SCRIPTS 等+D_TEST，W1d 取证），它们不是 TaskCard target_layer 语义面；
   收编它们=污染 target_layer 值空间（违背 v1.0.0 统一裁定的收敛方向），DB 侧清理属
   另一链路（domain FK 治理），本件只负责可见性（advisory 常亮）。**不是待裁定项**：
   两个方向（扩词表/清 DB）各有连坐面，本战役封账判据（FDR∪TR 差集=∅）不含 DB，
   advisory 已把账目公开。
3. **GATE-VOCAB 连坐预检**：对 3 个改动 .py 实跑 `check_vocab_hardcode --ci` = OK；
   W1a 预告的 +1 命中（tests/ex_core/test_multi_contract_adapter.py:224 用 D_REPORTING
   字面量）只有该文件被其 owner 会话再 staged 时才触发——§3.4 owner 责任制，不代修；
   基线棘轮 registry 自动算，无需本战役动作。

## 遗留→转下环节

- B 组 DB `--merge-domain`（D_INFRASTRUCTURE 84 节点/D_RESEARCH 2 节点）：转 W4 迁移工位。
- W3 验收并入 W6 循环检查基线命令组。
