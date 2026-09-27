---
ttl: task_bound
completes_when: 六图（fig11-16）封矿并全部落地四件套后本件退役为归档参考
title: 全景图六图挖矿+施工战役·共识件（车道唯一必读）
owner: st-mapbuild-20260924（总包）
---

# 共识件——六图车道唯一必读

> 战役=图11~16 六张纵轴（流程）全景图从挖矿到施工端到端交付。
> 本件只写**协调契约**（写域/禁令/交付格式/施工配方），方法论真源不复制，只给指针：
> 裁定#409 一域一图四道门 · 系统宪章 §8 · `sop/mining_sop/skeleton_mining_policy.md`（骨架三律/四类批次/状态纪律/封矿四判据） ·
> `sop/trading_decision_map_sop/trading_decision_map_layering_policy.md`（防撞车/防越级/防枝末先行） ·
> `sop/governance_sop/alignment_checklist.md` §3（挂轴表）+ §4 原则6（新图必挂总线） ·
> `config/trading_decision_map.yaml` 文件头（INV-1 铁律+血肉填充约定） · `config/strategy_production_map.yaml`（图9 四件套先例）。

## 1. 写域（硬切分，越域=连坐事故）

| 图 | 车道文件夹（相对仓库根） |
|----|--------------------------|
| 图11 交付流水线 | `docs/_working/map_build/fig11_delivery/` |
| 图12 数据供给链 | `docs/_working/map_build/fig12_datachain/` |
| 图13 交易日循环 | `docs/_working/map_build/fig13_daycycle/` |
| 图14 AI 施工升级流 | `docs/_working/map_build/fig14_construction/` |
| 图15 策略卡生命周期 | `docs/_working/map_build/fig15_cardlife/` |
| 图16 治理立法流 | `docs/_working/map_build/fig16_ruling/` |

**车道只准写自己那个文件夹**（含其子层）。以下共享面一律**禁直写**，需要变更就在自己作业簿末尾开一节「总包收口请求」写清诉求，由总包统一落：

- `docs/01_policies_and_standards/_registry/catalogs/**`（裁定册 / capability 册 token / gate 册 / 翻译册）
- `docs/01_policies_and_standards/sop/governance_sop/alignment_checklist.md`（§3 挂轴）
- `config/**`（图本体；**挖矿期全域禁碰**）
- `src/zephyr/gov_enforcement/commit_gates/**`、`scripts/governance/**`（校验器/gate/生成器，施工期由总包排产）
- `scripts/git_commit.py` 提交、`git add` 一律由总包执行；车道**不提交**，只落盘。

## 2. 交付格式（挖矿期）

```
figNN_<slug>/
  00_skeleton.md        # 环节总骨架：域定义 + 四道门实证 + 环节全集 + 三态 + 真源映射 + 重叠判定 + 封顶声明
  01_<环节名>.md        # 每环节一本作业簿
  02_<环节名>.md
  ...
  9x_<专题>.md          # 溢出条目回写前的临时卷（须在同一批次里回写骨架）
```

- `00_skeleton.md` 是**该图唯一收敛基准**：环节编号一经定稿即为契约，作业簿标题必须引用环节编号。
- 状态标记按 `skeleton_mining_policy.md` §5：**✅ 必附实查路径**（哪张表/哪个文件/哪条命令/哪一行），凭印象标 ✅=审计事故。
- 停止判据三问（§3）决定"拆不拆下一层"：生产者变→拆；验证口径变→拆；只是标签/参数变→**不拆**。
- 挖矿文档一律 `ttl: task_bound` + `completes_when:` frontmatter（TTL-METADATA 硬 gate）；**不要**写 `doc_type`（EXEMPT-ZONE-FRONTMATTER 与 _working 冲突过）；**禁止 .json 落 docs/_working**（DCR-005/008 打死整批），机读件用 `.yaml`。
- 行首 `#` 不要写成 `[DOMAIN]` 形态注释（触 FK 假红）。

## 3. 作业簿交付判据「挖干」= 六向台账 + 自审三态

每本作业簿末尾 MUST 有「六向台账」小节，六向缺一即判欠：

| 向 | 内容 |
|----|------|
| 上 | 谁触发本环节、输入从哪来（真源路径+行号/命令） |
| 下 | 本环节输出给谁、消费方是谁 |
| 内 | 全部子模块/子流程清单（含自动化程度） |
| 旁 | 撞车面：与哪张现有图/哪份文档同职责，处置=吸收/融合/扩展/废弃/引用（五选一，见 layering policy Step 1） |
| 史 | 考古：旧实现/已退役件/被取代文档，及是否仍有活代码 |
| 新 | 最新算法与功能（含外部对标一句话结论） |

末尾再给「自审裁定」一行：`干` / `欠（缺哪向、补什么）` / `溢（发现骨架外新环节 → 已回写 00_skeleton.md 第 N 节）`。
**溢出条目必须先回写骨架再施工**；骨架回写权只在总包与本图骨架主，其他车道改骨架=违规。

封矿判据（§6 四问）：三扫收敛 + 相邻两批增量趋零 + 🌑 点名完毕 + 封顶声明落盘。

## 4. 重叠判定优先级（图13 最硬的一条）

图13 交易日循环图开工第一步 = **撞车实证**：`config/schedule.yaml` 一入口视图与 dloop 十环节（MOD-PLAN-033）现有哪些视图已在 TDM / battle_map / 排班表里画过？
判定结论必须三选一并给证据：①新图成立（列出与三者各自的连接点差异）②改挂 TDM/battle_map 扩节点（不另造，登记扩节点清单）③部分成立（只建缺的那段）。
**不得默认①**。图16 同理：先评并入 GOMAP 扩层，四道门过不了就登记「不建」并给理由——不建也是合格交付。

## 5. 施工期四件套配方（图9 先例逐件坐标）

封矿后由总包排产，车道可承接单图施工。每图同批五件：

| 件 | 图9 先例路径（照抄形态，勿造新概念） |
|----|----------------------------------------|
| ①生成器 | 机生图参照 `scripts/governance/generate_governance_map.py`（GOMAP：可执行真相源→YAML，禁手画） |
| ②图 YAML | `config/<map>.yaml`，字段集=TDM 节点规范 v1.5 七要素+五联锚（见 layering policy §2.2）+工厂四件；`laws`/`boundary`/`feedback_loops` 必填 |
| ③结构校验器 | `scripts/governance/d5_architecture/validators/validate_<map>.py`，形态照抄 `validate_strategy_production_map.py`（`validate_structure(data)->list[str]` 单一真源，gate 只封阻塞语义；`exit 1`=结构违规，`exit 2`=解析失败） |
| ④gate | **不建独立 gate**——st-gslim P4 已把六张图门并入聚合台：`src/zephyr/gov_enforcement/commit_gates/panorama_alignment_gate.py::make_map_alignment_gate()` 的 `subs` 清单加一行，新建 `<map>_gate.py` 只暴露 `_check(gateway, files, **kwargs)->(bool,str)`（触发式：图 YAML/校验器变更才跑；YAML 损坏 fail-closed）。gate 需 14 字段头标注 |
| ⑤挂轴 | `alignment_checklist.md` §3 加图行（对齐 key=module_id 总线，D38）+ `align_all.py` 新增一节（照抄第八节形态）+ §6 时机矩阵一行 |

对抗测试：`tests/governance/commit_gates/test_<map>_gate.py` 形态照抄 `test_strategy_factory_map_gate.py`，必须含**能红**用例（伪造节点/断链引用/越域挂载/反向边未声明/INV-1 复制侵权=把别的库条目内容抄进图节点）。
判据：自写校验脚本必须先证明自己能红，再声称绿。

## 6. 提交与并发纪律

- 挖矿期**不提交**；总包按波次统一：`token 先行独立批` → 内容批 → 挂轴/裁定批。
- token：新建 `.py/.yaml/.md/.sh/.ps1/.mmd/.json` 都吃 CREATE-GUARD（无 token 硬阻断）。总包用
  `python scripts/governance/d3_metadata/batch_creation_tokens.py --prefix docs/_working/map_build/figNN_xxx --created-by st-mapbuild-20260924 --capability map_build --merge-evaluation "<四判据一句话>"`。
- 提交只走 `scripts/git_commit.py --session st-mapbuild-20260924 --files ... --enqueue`（队列是正门；锁忙自动改道，勿直连混抢）。
- 裁定号：挖矿期禁造裁定。施工期需要裁定时**报总包取号**（HEAD 现 max=#410，取号前重测 max，防撞号——册撞号后队列合并器修不了自己）。
