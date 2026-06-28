---
module_id: META-WRK-LOG-001
title: "任务：粒子级别全量分析项目 .md 文件，重新分类 ttl + doc_type"
doc_type: log
status: active
version: 1.0.0
date: 2026-06-27
owner: ZephyrAlpha-Owner
ttl: task_bound
completes_when: "5149 个 .md 文件 ttl+doc_type 重分类任务完成且结果落地"
---

# 任务：粒子级别全量分析项目 .md 文件，重新分类 ttl + doc\_type

## 任务目标

逐个分析 `d:\ZephyrAlpha\docs\` 下全部 5149 个 .md 文件的内容，基于内容（非路径）重新判定每个文件的：

1. **ttl**：permanent（永久保留）或 task\_bound（任务绑定，可清理）
2. **doc\_type**：27 种合法值之一（见词表）
3. **置信度**：high / medium / low
4. low 置信度的标记 `PENDING_REVIEW`，等待人工裁定

## 当前问题（已调查确认，无需重复诊断）

| 指标              | 当前值            | 问题                                                                     |
| --------------- | -------------- | ---------------------------------------------------------------------- |
| .md 总数          | 5149           | —                                                                      |
| 有 frontmatter   | 5123           | 26 个无 frontmatter（需单独标记）                                               |
| ttl=permanent   | 5091（99.7%）    | **严重失衡**——路径机械判定导致 changes/ 等过程文件被误标 permanent                         |
| ttl=task\_bound | 17（0.3%）       | 应该远多于此（changes/、reports/、\_working/ 等过程文件应是 task\_bound）               |
| 有 doc\_type     | 397/5149（7.7%） | **92% 缺失**                                                             |
| doc\_type 非法值   | 有              | domain\_architecture\_doc / domain\_architecture\_diagram 等不在 27 种合法值内 |

## 分类标准真源（必读）

### ttl 词表（2 值）

- **文件**：`d:\ZephyrAlpha\docs\01_policies_and_standards\_registry\vocabularies\ttl_vocabulary.yaml`
- **合法值**：permanent / task\_bound
- **判定原则**：基于内容判定，不是路径！
  - permanent = 核心治理文件（规则、标准、架构、蓝图、真源数据、词表）——不可删除
  - task\_bound = 过程性文档（变更记录、调研报告、施工方案、临时笔记、审计产出物）——任务完成后可清理
- **关键纠正**：当前路径判定把永久区路径下的 changes/ 变更记录都标为 permanent，这是错误的。changes/ 目录下的文件即使路径在 docs/03\_modules/ 下，内容是过程性的，应判 task\_bound
- **正交说明**：ttl（文件留多久）与 KE status（知识处于什么阶段）正交，不可互相替代

### doc\_type 词表（27 值）

- **文件**：`d:\ZephyrAlpha\docs\01_policies_and_standards\_registry\vocabularies\doc_type_vocabulary.yaml`
- **27 种合法值**：policy / standard / operational\_rule / register / index / protocol / template / terminology / reference / vocabulary / contract / schema / blueprint / construction\_plan / design / plan / roadmap / readme / log / knowledge\_entry / audit\_report / service\_spec / architecture\_view / declaration / gate / config / knowledge\_entry
- **废弃值**（不可用）：governance\_standard / ai\_governance / governance\_registry / registry / discussion\_draft / candidate\_pool / checklist
- **非法值**（当前存在但不在词表内）：domain\_architecture\_doc / domain\_architecture\_diagram / task\_card\_index / architecture\_construction\_plan / architecture\_discussion / architecture\_design / directory\_index / capacity\_report / constraint\_violations\_report / design\_vs\_production\_report / delivery\_record / cross\_domain\_matrix / runtime\_plane\_mapping / domain\_index / capability\_heatmap / governance\_report → 这些需映射到 27 种合法值之一或标记 PENDING\_REVIEW

### 永久区 4 路径（供参考，不是 ttl 判定依据）

- `docs/01_policies_and_standards/`
- `docs/02_enterprise_architecture/`
- `docs/03_modules/`
- `docs/08_knowledge/`

## 所有相关文件完整路径

| 用途               | 绝对路径                                                                                            |
| ---------------- | ----------------------------------------------------------------------------------------------- |
| 项目根              | `d:\ZephyrAlpha`                                                                                |
| ttl 词表           | `d:\ZephyrAlpha\docs\01_policies_and_standards\_registry\vocabularies\ttl_vocabulary.yaml`      |
| doc\_type 词表     | `d:\ZephyrAlpha\docs\01_policies_and_standards\_registry\vocabularies\doc_type_vocabulary.yaml` |
| GATE-15 校验器      | `d:\ZephyrAlpha\scripts\governance\d3_metadata\check_frontmatter_metadata.py`                   |
| ttl 回填脚本         | `d:\ZephyrAlpha\scripts\governance\d3_metadata\backfill_ttl_metadata.py`                        |
| frontmatter 解析器  | `d:\ZephyrAlpha\scripts\governance\_shared\frontmatter.py`                                      |
| 常量定义             | `d:\ZephyrAlpha\scripts\governance\_shared\constants.py`                                        |
| GitCommitGateway | `d:\ZephyrAlpha\src\zephyr\governance\git_commit_gateway.py`                                    |
| 全量 .md 文件        | `d:\ZephyrAlpha\docs\**\*.md`（5149 个）                                                           |

## 执行步骤

### 步骤 1：生成分片清单

5149 个文件按文件数量均匀切分为 40 片（每片 \~129 文件）。注意：`docs/08_knowledge/01_raw_intake/` 有 3242 文件（63%），`docs/08_knowledge/04_archived/` 有 1399 文件（27%），不能按目录分片，必须按文件数量均匀切分。

创建并运行以下脚本：

```python
# 文件：d:\ZephyrAlpha\docs\_working\generate_shards.py
from pathlib import Path
import json, csv

proj = Path(r"d:\ZephyrAlpha")
docs = proj / "docs"
output_dir = proj / "docs" / "_working" / "reclassification_shards"
output_dir.mkdir(parents=True, exist_ok=True)

# 收集全部 .md 文件（相对路径，正斜杠）
all_files = sorted(
    str(f.relative_to(proj)).replace("\\", "/")
    for f in docs.rglob("*.md")
)
print(f"Total .md files: {len(all_files)}")

# 均匀切分 40 片
NUM_SHARDS = 40
shard_size = len(all_files) // NUM_SHARDS
remainder = len(all_files) % NUM_SHARDS

shards = []
start = 0
for i in range(NUM_SHARDS):
    size = shard_size + (1 if i < remainder else 0)
    shard_files = all_files[start:start + size]
    shards.append({"shard_id": i, "files": shard_files, "count": len(shard_files)})
    start += size

# 写分片清单（每个分片一个 CSV）
for shard in shards:
    sid = shard["shard_id"]
    out = output_dir / f"shard_{sid:02d}_input.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["relative_path", "current_ttl", "current_doc_type"])
        for rel in shard["files"]:
            # 读 frontmatter 提取当前 ttl 和 doc_type
            fpath = proj / rel
            try:
                text = fpath.read_text(encoding="utf-8")
            except:
                w.writerow([rel, "READ_ERROR", ""])
                continue
            ttl_val = ""
            dt_val = ""
            if text.startswith("---"):
                import re
                m = re.match(r'^---\r?\n(.*?)\r?\n---', text, re.DOTALL)
                if m:
                    for line in m.group(1).split("\n"):
                        if line.startswith("ttl:"):
                            ttl_val = line.split(":", 1)[1].strip()
                        elif line.startswith("doc_type:"):
                            dt_val = line.split(":", 1)[1].strip()
            w.writerow([rel, ttl_val, dt_val])

# 写分片索引
index_path = output_dir / "shard_index.json"
index_path.write_text(json.dumps({
    "total_files": len(all_files),
    "num_shards": NUM_SHARDS,
    "shards": [{"shard_id": s["shard_id"], "count": s["count"]} for s in shards],
}, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"Shards written to: {output_dir}")
print(f"Shard index: {index_path}")
```

### 步骤 2：逐片分析

对每个分片 CSV（`shard_00_input.csv` \~ `shard_39_input.csv`），逐个文件分析内容：

1. 读取文件 frontmatter（前 20 行）+ 正文前 50 行（足够判断文档类型和生命周期）
2. 判定 ttl：基于内容——是核心治理文件（permanent）还是过程性文件（task\_bound）
3. 判定 doc\_type：从 27 种合法值中选择最匹配的
4. 标记置信度：high（内容明确）/ medium（有 ambiguity）/ low（无法确定）
5. low 置信度的标记 `PENDING_REVIEW`

### 步骤 3：输出 CSV

每个分片输出一个结果 CSV 到 `d:\ZephyrAlpha\docs\_working\reclassification_shards\`：

**输出文件名**：`shard_{NN}_output.csv`

**CSV 格式**（UTF-8，逗号分隔）：

| 列名                   | 说明                          | 示例值                                          |
| -------------------- | --------------------------- | -------------------------------------------- |
| relative\_path       | 相对项目根的路径（正斜杠）               | docs/03\_modules/\_cross\_layer/.../index.md |
| current\_ttl         | 当前 frontmatter 里的 ttl       | permanent                                    |
| current\_doc\_type   | 当前 frontmatter 里的 doc\_type | index                                        |
| suggested\_ttl       | 建议的 ttl                     | task\_bound                                  |
| suggested\_doc\_type | 建议的 doc\_type               | index                                        |
| confidence           | 置信度                         | high / medium / low                          |
| needs\_review        | 是否待裁定                       | YES / NO                                     |
| reason               | 判定理由（≤100 字）                | 变更记录，过程性文档                                   |
| content\_summary     | 内容摘要（≤50 字）                 | MOD-CONTEXT_ENGINE 的变更记录索引                          |

### 步骤 4：汇总

创建并运行以下汇总脚本：

```python
# 文件：d:\ZephyrAlpha\docs\_working\merge_shards.py
from pathlib import Path
import csv, json
from collections import Counter

proj = Path(r"d:\ZephyrAlpha")
shard_dir = proj / "docs" / "_working" / "reclassification_shards"
output_csv = shard_dir / "reclassification_full_report.csv"
pending_csv = shard_dir / "reclassification_pending_review.csv"

all_rows = []
for i in range(40):
    f = shard_dir / f"shard_{i:02d}_output.csv"
    if not f.exists():
        print(f"WARNING: {f.name} missing")
        continue
    with open(f, encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            all_rows.append(row)

# 写全量报告
fields = ["relative_path","current_ttl","current_doc_type","suggested_ttl",
          "suggested_doc_type","confidence","needs_review","reason","content_summary"]
with open(output_csv, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    w.writerows(all_rows)

# 写待裁定报告
pending = [r for r in all_rows if r.get("needs_review") == "YES"]
with open(pending_csv, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    w.writerows(pending)

# 统计
ttl_changes = Counter()
dt_changes = Counter()
conf_counts = Counter()
review_counts = Counter()
for r in all_rows:
    if r["current_ttl"] != r["suggested_ttl"]:
        ttl_changes[f'{r["current_ttl"]}→{r["suggested_ttl"]}'] += 1
    if r["current_doc_type"] != r["suggested_doc_type"]:
        dt_changes[f'{r["current_doc_type"]}→{r["suggested_doc_type"]}'] += 1
    conf_counts[r["confidence"]] += 1
    review_counts[r["needs_review"]] += 1

print(f"Total files analyzed: {len(all_rows)}")
print(f"Pending review: {len(pending)}")
print(f"\nttl changes (top 10):")
for k, c in ttl_changes.most_common(10):
    print(f"  {k:40s} {c:5d}")
print(f"\ndoc_type changes (top 10):")
for k, c in dt_changes.most_common(10):
    print(f"  {k:50s} {c:5d}")
print(f"\nConfidence: {dict(conf_counts)}")
print(f"Needs review: {dict(review_counts)}")
print(f"\nFull report: {output_csv}")
print(f"Pending review: {pending_csv}")
```

### 步骤 5：人工裁定

汇总后打开 `reclassification_pending_review.csv`，逐行裁定。裁定后由用户决定是否应用变更。

## 分析判定指南

### ttl 判定（基于内容，非路径）

**permanent 的特征**：

- 定义规则/标准/协议（"必须"/"禁止"/"推荐"）
- 架构设计文档、蓝图、不变量
- 词表、Schema、注册表
- 索引入口文件（index.md）——目录级导航，永久保留
- 模板文件——可复用骨架

**task\_bound 的特征**：

- 变更记录（changes/ 目录下的文件，即使路径在永久区）
- 调研报告、根因分析报告
- 施工方案、施工计划
- 审计产出物、测试报告
- 临时笔记、session log
- 候选池、讨论草稿

**灰色地带 → 标记 PENDING\_REVIEW**：

- 文件同时含规则和过程内容
- 文件类型不明确（如既像 blueprint 又像 construction\_plan）
- 归档文件（已归档的知识条目——文件保留但内容已过时）

### doc\_type 判定（27 种合法值）

参考 `doc_type_vocabulary.yaml` 的三问决策树：

- Q1: 定义"规则"还是"操作步骤"？→ 规则→Q2，步骤→operational\_rule
- Q2: "红线"还是"推荐"？→ 红线→policy，推荐→standard
- Q3: "导航入口"、"数据结构"、"交互约定"、"结构骨架"？→ index / register / protocol / template
- Q4: 不在 policies 目录？→ blueprint / construction\_plan / architecture\_view / knowledge\_entry / audit\_report / log 等

**非法值映射建议**：

- domain\_architecture\_doc → architecture\_view 或 blueprint
- domain\_architecture\_diagram → architecture\_view
- governance\_report → audit\_report
- construction\_plan → construction\_plan（合法）
- capacity\_report / constraint\_violations\_report / design\_vs\_production\_report → audit\_report
- delivery\_record → log 或 audit\_report
- cross\_domain\_matrix / runtime\_plane\_mapping / capability\_heatmap → reference
- directory\_index / domain\_index → index

## 项目约束

- **禁止直接修改 .md 文件**——本次只分析输出 CSV，不应用变更。变更应用是后续单独任务
- **禁止裸 git commit**——如需提交 CSV 报告，必须通过 GitCommitGateway
- **所有文件路径必须使用绝对路径**——禁止相对路径
- **CSV 输出目录**：`d:\ZephyrAlpha\docs\_working\reclassification_shards\`（task\_bound 临时区，可安全创建）
- **不涉及 depgraph.db 修改**——纯分析任务，不改数据库
- **并发安全**：每个分片 AI 只读 .md 文件，只写自己的 `shard_{NN}_output.csv`，无写冲突

## 验证

汇总完成后检查：

1. `reclassification_full_report.csv` 行数 = 5149
2. `reclassification_pending_review.csv` 的 `needs_review=YES` 行数合理（预期 100-500，不应为 0 也不应超过 1000）
3. ttl 变化统计合理：permanent→task\_bound 应有数百个（changes/ 等过程文件）
4. doc\_type 变化统计合理：大量空值→合法值的填充

```
' );

<function_results>File created successfully at: d:\ZephyrAlpha\docs\_working\ttl_doctype_reclassification_handoff.md
<system-reminder>
As you read or edit files, take care to be...</think>交接指令已写入文件。现在输出完整的一键复制指令：

---

## 一键复制指令（复制以下全部内容到新 AI 对话）

```

## 任务：粒子级别全量分析项目 .md 文件，重新分类 ttl + doc\_type

完整交接文档已存在于：d:\ZephyrAlpha\docs\_working\ttl\_doctype\_reclassification\_handoff.md

请先读取该文件获取完整执行方案，然后按以下步骤执行：

### 核心目标

逐个分析 d:\ZephyrAlpha\docs\ 下全部 5149 个 .md 文件的内容，基于内容（非路径）重新判定：

1. ttl：permanent / task\_bound（2 值，词表：d:\ZephyrAlpha\docs\01\_policies\_and\_standards\_registry\vocabularies\ttl\_vocabulary.yaml）
2. doc\_type：27 种合法值（词表：d:\ZephyrAlpha\docs\01\_policies\_and\_standards\_registry\vocabularies\doc\_type\_vocabulary.yaml）
3. 置信度 + 待裁定标记

### 当前问题（已调查确认）

- ttl 严重失衡：5091 permanent vs 17 task\_bound（路径机械判定导致 changes/ 等过程文件被误标 permanent）
- doc\_type 缺失：只有 397/5149 有值（7.7%），且有非法值（domain\_architecture\_doc 等不在 27 种合法值内）
- 26 个 .md 无 frontmatter

### 关键文件路径

- 项目根：d:\ZephyrAlpha
- ttl 词表：d:\ZephyrAlpha\docs\01\_policies\_and\_standards\_registry\vocabularies\ttl\_vocabulary.yaml
- doc\_type 词表：d:\ZephyrAlpha\docs\01\_policies\_and\_standards\_registry\vocabularies\doc\_type\_vocabulary.yaml
- GATE-15 校验器：d:\ZephyrAlpha\scripts\governance\d3\_metadata\check\_frontmatter\_metadata.py
- ttl 回填脚本：d:\ZephyrAlpha\scripts\governance\d3\_metadata\backfill\_ttl\_metadata.py
- frontmatter 解析器：d:\ZephyrAlpha\scripts\governance\_shared\frontmatter.py
- GitCommitGateway：d:\ZephyrAlpha\src\zephyr\governance\git\_commit\_gateway.py
- 全量 .md 文件：d:\ZephyrAlpha\docs\*\*\*.md（5149 个）
- 输出目录：d:\ZephyrAlpha\docs\_working\reclassification\_shards\\

### 执行步骤

1. 读取交接文档 d:\ZephyrAlpha\docs\_working\ttl\_doctype\_reclassification\_handoff.md 获取完整方案
2. 读取 ttl 词表和 doc\_type 词表，理解分类标准
3. 运行交接文档中的"步骤1：生成分片清单"脚本，生成 40 个分片 CSV
4. 逐片分析：每个文件读 frontmatter + 正文前 50 行，判定 ttl + doc\_type + 置信度
5. 输出每个分片的 shard\_{NN}\_output.csv（格式见交接文档）
6. 运行"步骤4：汇总"脚本，生成全量报告 + 待裁定报告
7. 人工审查待裁定项（reclassification\_pending\_review\.csv）

### 判定核心原则

ttl 判定基于内容而非路径：

- permanent = 核心治理文件（规则、标准、架构、蓝图、词表、索引、模板）
- task\_bound = 过程性文档（变更记录 changes/、调研报告、施工方案、审计产出物、临时笔记）
- 灰色地带标记 PENDING\_REVIEW

### CSV 输出格式

列：relative\_path, current\_ttl, current\_doc\_type, suggested\_ttl, suggested\_doc\_type, confidence, needs\_review, reason, content\_summary

### 项目约束

- 禁止直接修改 .md 文件——只分析输出 CSV
- 禁止裸 git commit——如需提交报告通过 GitCommitGateway
- 所有路径用绝对路径
- 并发安全：每个分片只读 .md，只写自己的 shard\_{NN}\_output.csv

```

---

指令已写入交接文档 [ttl_doctype_reclassification_handoff.md](file:///d:/ZephyrAlpha/docs/_working/ttl_doctype_reclassification_handoff.md)，并提供了上面的一键复制 prompt。

**交接要点总结**：
- **5149 个 .md 文件**，按文件数量均匀切 40 片（每片 ~129 文件）
- **分类两个维度**：ttl（2 值）+ doc_type（27 种合法值）
- **核心纠正**：ttl 从"路径机械判定"改为"内容判定"——changes/ 等过程文件应从 permanent 改为 task_bound
- **非法 doc_type 映射**：domain_architecture_doc 等 15 种非法值需映射到合法值
- **待裁定机制**：low 置信度标记 PENDING_REVIEW，汇总后人工审查
- **分片脚本 + 汇总脚本**：已嵌入交接文档，可直接运行
```

