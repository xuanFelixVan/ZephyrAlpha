---
ttl: task_bound
completes_when: 战役 st-vocabconsol-20260918 W8 封账提交后转 archived
---

# W7 红蓝极限对抗方案（先写判据后跑，防"看结果补判据"）

> 铁律（autoclaw 战役教训）：**判通过的脚本必须先证明能红**。每场景=注入一个真实故障→
> 期望变红+信息正确→撤销→回绿。撤销后必须与注入前基线逐项相等。

## 蓝军场景清单

| # | 注入 | 目标件 | 期望红判据 | 撤证 |
|---|------|--------|-----------|------|
| R1 | 词表漂移重现：临时删 target_layer_vocabulary.yaml 一个在用值（如 D_PLAN） | check_vocab_domain_convergence | exit 1 + 差集点名该域 | git checkout 还原→exit 0 |
| R2 | 别名折叠 ERROR：把某 alias 从 aliases 段移除（值仍在用） | validate_target_layer | 该 alias 赋值处 WARNING→ERROR 升红 | 还原→WARNING 归位 |
| R3 | 折叠自毁通道：_collect_vocab_values 临时不吃 aliases（改回旧逻辑） | yaml_utils 家族测试 | load_vocabulary_values 少 10 值→相关测试红 | 还原全绿 |
| R4 | 重复条目复发：向 TR 注入 1 组同 module_path 重复 | add_module_translation --dedupe --dry-run + loader | dry-run 报 1 组；loader WARNING 可见数<声明数 | 删除注入行→0 组 |
| R5 | 补标瞎填护栏：假 CSV 含非法域值+脏文件+.aidrafts 路径 | backfill_module_domain --apply（tmp 沙箱仓） | 非法→未决清单；脏文件跳过；审计 JSONL 行数吻合 | 沙箱自灭 |
| R6 | 预检 message 盲区回归：构造带标记净删批 + 不带标记净删批各一 | git_commit preflight（离线 harness，勿真入队） | 无标记=预检红+新提示含标记指引；有标记=放行 | 无 |
| R7 | 职责层直推诱惑：映射删一行后跑 --sync-layer | add_module_translation | 该域条目字段移除+统计正确；禁目录名兜底（不得出现推断值） | 还原行→幂等归位 |
| R8 | DB 幂等：对已合并域再 merge 一次 | apply_depgraph --merge-domain | RC=4 零写入 | 无 |
| R9 | total_values 自校：把 meta.total_values 改错 | validate_target_layer | selfcheck ERROR 非零 | 还原→0 |
| R10 | 豁免滥用：给新脚本塞无意义 m11-perm-manual-legitimate | MANUAL-ONLY-PERMANENT/NOQA gate | 预检/锁内红（reason<10字或无逃生正当性） | 删除→绿 |

## 红军加测（对抗 AI 自动化链路本体）

- A1：并发写热文件——两进程同时 safe_write_text 同一注册表，后者必须 StaleWriteRefused
  或基于新 base 成功，禁静默覆盖。
- A2：队列快照语义——入队后再改文件，落地内容必须=快照（衍生漂移容忍条款内）。
  （复用 0003 入队后的在途改动作自然实验证，不额外注入。）

## 通过判据

全部红→撤→绿闭环；任何"注入后仍绿"=检测失明，当场修复后重跑该场景；
修复记入 w7_fixes.md。连续两轮 W6 循环检查问题=0 才算封账前置。
