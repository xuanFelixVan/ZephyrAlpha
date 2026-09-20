---
ttl: task_bound
campaign_status: 已封账 archived（2026-09-21 封账批 st-taskcards-exec-20260921；ttl 词表无 archived 值故保持 task_bound，物理归档移交后续归置批）
completes_when: 战役 st-vocabconsol-20260918 W8 封账提交后转 archived（封账标记已落 campaign_status）
---
# 战役骨架——target_layer 词表收编 + 三层归属精确账（全链路环节挖矿图）

- 战役号：st-vocabconsol-20260918
- 方法论真源：`sop/mining_sop/skeleton_mining_policy.md`（骨架三律/停止判据三问/封矿四判据）+ `mining_sop_policy.md`（六向寻路/自审闸）
- 上位工单：`docs/_working/2026-09-18_vocab_consolidation_campaign/00_workorder_施工包.md`（差集 25 项，处置以 [[裁定#335]] 为准）
- 骨架职责：本文件=路由表+计分板+防腐对象。每格可实查，✅ 必须附实查路径。
- 留案：本骨架与施工包原版于 05:2x 被并发清扫吞没一次（stash 未含=直接消失），05:35 上下文再生；教训=当轮即提交。

## 批次志

| 批次 | 日期 | 主题 | 增量 |
|------|------|------|------|
| B0 | 2026-09-18 | 初版骨架：八环节+挖矿中类全集（静态盘点） | +8 中类 |
| B1 | 2026-09-18 | W1 四路挖矿回写：新增 W4e 写手治本/D_CONTRACTS 反转/responsibility_layer 定名 | +1 中类，0 新环节 |
| B2 | 2026-09-18 | W3 落地+W4e/W4d 落地+W5 普查：环节 0 新增（三扫收敛再证），差集脚本抓到 3 散文误捕→字段位口径自裁定 | +0 中类 |
| B3 | 2026-09-21 | W8 封账批（tc_05 卡步骤 3）：基线三连复跑全绿+10 域死结解除实测（单测 6 passed）+W4/W6/W7/W8 四格翻牌+frontmatter archived | 环节 0 新增；四格翻 ✅ |

## §1 大类（MECE，族级防漏）

- **F1 挖矿族**：环节/子环节全集挖掘（本图 ⬜ 项的挖掘义务）
- **F2 治理裁定族**：封矿判定、自裁定登记（RULE-RULING）
- **F3 施工族**：词表/校验器/生成器/补标四条产线
- **F4 验证族**：循环检查、红蓝对抗
- **F5 落地族**：网关提交、清理、汇报

## §2 中类全集（完整性检查单元 = 环节，每环节一个子文档目录）

| ID | 环节 | 子文档目录 | 状态 | 备注（实查证据） |
|----|------|-----------|------|------|
| W1 | 环节挖矿（四路） | `w1_mining/` | ✅ | 实查=w1a/b/c/d 四文档落盘+no_domain_list.csv 2115 行 |
| W2 | 封矿判定 + 裁定#335 登记 | `w2_ruling/` | ✅ | 实查=ruling_registry.yaml 末条 裁定#335（safe_write_text CAS，after_sha=4d74298caf）；封矿判据见 §4 |
| W3 | 词表收编 + validate_target_layer 治本 + 差集常驻脚本 | `w3_vocab_construction/` | ✅ | 实查=w3_execution_log.md 验收表（validate exit 0/差集 exit 0/6 用例绿/scaffold token 已登） |
| W4 | responsibility_layer 映射 YAML + 生成器 + 2115 无 domain 补标 + loader/写手治本 | `w4_layer_field/` | ✅ | W4a mapping yaml 84 域→4 层+W4-B组 merge-domain 两笔+W4d/W4e 88 用例绿+W4b 放量 4988 写入幂等收敛（w4_construction/w4_execution_log.md）；原 🔨 系回写遗漏，封账批 2026-09-21 翻 ✅ |
| W5 | 全仓 L1/L2/L3 同族假红普查 | `w5_exemption/` | ✅ | 实查=w5_survey.md：141 面分类 0 真违规；收紧差分 23→10 命中/新增红 0；noqa 标记判定=不需要（3 条硬否决）；W3 采纳其改良正则 D[-_] 保住废弃 WARNING |
| W6 | 循环检查两轮：全量相关测试+基线命令 diff 问题=0 | `w6_loop_check/` | ✅ | 轮2 全绿+09-21 复跑三连 RC=0/RC=0/存活+收敛单测 6 passed（w8_landing/landing_log.md 第 1 节；轮3 补记见 w6_round1_log） |
| W7 | 红蓝极限对抗（ARCH-310 范式 A-B 双基准）+修复 | `w7_redblue/` | ✅ | w7_redblue/w7_execution_log.md 场景表+w7_fixes.md 修复批在档（封账批 2026-09-21 翻 ✅） |
| W8 | GitCommitGateway 落地 + .runtime 清理 + 收尾序列 | `w8_landing/` | ✅ | w8_landing/landing_log.md+封账批（st-taskcards-exec-20260921，2026-09-21）；vocabconsol_* 六临时目录已被定向清除（tc_05 卡实测） |

**回写义务**：挖矿中发现骨架外新条目，先回写本表再施工（骨架 §2 操作律）。

## §3 环节内子类目（叶=生产者代表，非穷举；挖矿后定稿）

### W3（裁定#335 执行面）
- W3a 词表 YAML：17 值入 values（含 definition/ai_keywords）、8 值入 aliases、注释治本、version 1.1.0+变更历史、files_trigger 自触发 GATE-VOCAB→基线棘轮 noqa（test_multi_contract_adapter.py:224）
- W3b 校验器：`(D_[A-Z_]+|基础设施)` 正则归位+aliases 读取（_collect_vocab_values 扩展，前置铁条件）+total_values 自校
- W3c 差集脚本：`scripts/governance/d5_architecture/validators/check_vocab_domain_convergence.py`（三源 词表×FDR×TR×DB domains 表 差集=∅，scaffold 通道登记 creation_token+14 字段头+TRANSLATION-COVERAGE plain_zh）+ 是否入 gate_registry 判定（观测型=validator 族，非 commit gate）

### W4
- W4a `domain_responsibility_layer_mapping.yaml`（84+ 域→governance/business/ai/infrastructure，输入=w1d 草案 79 行+争点 10 条裁定化）
- W4b loader+生成器派生 layer→responsibility_layer（机生，§9.5 禁手工）
- W4c 2115 空 domain 补标（no_domain_list.csv 为输入；tests 1690 按 tests/ 豁免口径评估是否需补）
- W4d loader 折叠病灶：entries 30 组重复去重自愈
- W4e 写手治本：add_module_translation.py 改 safe_write_text+全文件查重+保留扩展字段（硬规则 13 违例清除）

### W6/W7/W8：判据型环节，子类目 W3-W5 施工后回写。

## §4 封顶声明（封矿时填写）

- [x] 三扫收敛：W1a/b/c/d 各一轮完毕，B1 回写仅增叶不增枝（新增 W4e 属 W4 中类下叶子级发现，过停止判据三问：同一生产者同一口径）
- [x] 相邻两批增量趋零：B1 环节增量=0（中类 8→8）
- [x] 🌑 清点：①tasks.target_layer 历史数字值 1-7 的清洗不做（裁定#335 结论 8 留案）；②D_CONTRACTS 反合并 D_SHARED 不做（推翻已修复裁定链风险）；③词表 8 值终局删除不做（Owner 门位，留退役审计）
- [ ] 封顶生效：此后增长仅叶→实现；增枝须过 §3 停止判据并留理由
- 封矿时间：2026-09-18 05:35（B1）；进入施工 SOP

## §5 状态标记纪律

✅ 必须附实查路径（命令/表/文件行）；🔨=有设计文档（本图）；⬜=候选入口。改标留批次号。
