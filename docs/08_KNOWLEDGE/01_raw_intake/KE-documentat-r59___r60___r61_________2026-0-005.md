---
module_id: KE-documentat-r59___r60___r61_________2026-0-005
title: ⚠️ 关于 R59 / R60 / R61 重号事故的说明（2026-04-19）
category: documentation
---

# ⚠️ 关于 R59 / R60 / R61 重号事故的说明（2026-04-19）

⚠️ 关于 R59 / R60 / R61 重号事故的说明（2026-04-19）

**事故事实**：批次 F（H6 Domain Event / H7 DDD Aggregate / H11 五张时序图，2026-04-19 午间由 Opus 会话完成）与批次 G（S2-S6 五视图 Architecture Runway 章节，2026-04-19 午后由 Sonnet 会话完成）在同一日**并发执行**时，任务书派发的 R 号区段重叠，导致 R59/R60/R61 三个编号在本日志下表中各被**双登记**（批次 F 一条 + 批次 G 一条）。

**根因**：两批次任务书起草时都独立向 R 号空间后续顺延取号，**未建立"取号前强制复查 rationale-log 最末 R 号"的派号台账机制**。批次 G handoff 日志（2026-04-19 条目）明确记录"与任务书指定一致，本批次据实执行"，说明占号冲突并非执行错误，而是**任务书源头的 R 号区段被重复派发**。

**治理决策**（遵循 ADR 编号不可变铁律 + 项目既有 R15-R22 superseded append-only 模式）：

1. **历史记录不改写**：下表原有两套 R59/R60/R61 条目**全部保留**，任何已落盘的引用均视为历史事实
2. **为区分两轨引用，批次 F 的三条 R 号统一追加后缀 "-F"**，即 **R59-F / R60-F / R61-F**（对应 H6 / H7 / H11）
3. **批次 G 的 R59-R63 保持原号**（先后仅差数小时，但 G 轨含 5 条连续号码更难拆分，按"先到先得 + 改动面最小"原则保留 G 轨原号）
4. **所有新引用**必须按"带后缀 = 批次 F / 原号 = 批次 G"解读，避免歧义
5. **本公告及下表中批次 F 的三条 "-F" 条目**作为治理案例永久留痕，不得删除
6. **防止复发机制**：本批次 H（R64）同步在 `taskbooks/serial-execution-plan.md` 顶部新增"R 号并发派号规约"，规定任何新批次任务书起草时必须先 `grep -E "^\| R[0-9]+ \|" rationale-log | tail -1` 核实当前最末 R 号

**本轮（批次 H，2026-04-19）实施的同步改动**（共 10 处引用同步打 "-F" 后缀）：

| 文件 | 改动位置 | 改动前 → 改动后 |
|------|----------|----------------|
| `rationale-log.md`（本文件） | 下表批次 F 三行首列 | R59 / R60 / R61 → **R59-F / R60-F / R61-F** |
| `catalogs/domain-event-catalog.md` | frontmatter `related_rationale` + §revision | R59 → **R59-F** |
| `catalogs/ddd-aggregates.md` | frontmatter `related_rationale` + §revision | R60 / R59 → **R60-F / R59-F** |
| `target-architecture/README.md` | frontmatter + §6 diagrams 表 × 5 + §revision | R61 → **R61-F**（批次 F 相关）/ R59/R60 在修订记录区指代批次 F 处一并改 **R59-F/R60-F** |
| `handoff-log.md` | S14-BatchF 条目（整段） | R59/R60/R61 → **R59-F/R60-F/R61-F** |
| `serial-execution-plan.md` | 批次 F 行 + 7.2/7.3/8.1 完成状态行 × 3 | R59/R60/R61 → **R59-F/R60-F/R61-F** |

**不改动的引用**（均指代批次 G 产出物，保留原号）：
- `01-BA.md` v1.2.0 frontmatter `related_rationale: R59` → 保持（= 批次 G S2）
- `target-architecture/README.md` frontmatter `R61` 出现两处：§6 表格内指代批次 F 的 5 行时序图改 `R61-F`，但 frontmatter 头部若已有的是批次 F 的 R61 则改 `R61-F`（本次已核实：README frontmatter 唯一的 R61 是批次 F 时序图索引的登记来源，统一改 -F）
- 批次 G 产出的 5 份视图（01-BA / 02-IA / 03-AA / 04-TA / 00-overview）其余章节 R59-R63 引用均保持原号

---
