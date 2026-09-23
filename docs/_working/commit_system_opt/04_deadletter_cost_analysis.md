---
ttl: task_bound
title: "死信撞墙成本表（112 封实测）"
session: st-commitsys-20260924
---

# ④撞墙成本表（2026-09-22/23 死信战役）

口径：损失时长=created_at→dead_at（分钟，含排队等待）；样本=112 封（.runtime/commit_queue/dead/ 除去档）。
原始账：`.runtime/tmp/commitsys/dead_analysis_rows.json`。

## 总量

P50=10.8min/封，mean=32.9，P90=102.2，max=276.9。**一晚死信全成本≈61 小时会话时Lost**。

## 死因簇×成本矩阵（按 次数×P50 排序=优先级）

| 簇 | 封数 | P50 min | 面 | 指南章节 |
|---|---|---|---|---|
| GATE-PRECOMMIT-RUN(ruff/format) | 20 | 4.1 | 高频便宜 | FT-universal 步骤 7+ruff 预格式化 |
| CREATE-GUARD(token/basename) | 13 | 14.1 | 高频中价 | FT-new_src_py/new_script_py |
| TRANSLATION-COVERAGE | 9 | 7.5 | 高频便宜 | 同上 |
| landing 三向合并失败 | 8 | 15.2 | 基建 | FT-registry_yaml（解析护栏） |
| REGISTRY-MASS-DELETION | 8 | 3.6 | 高频便宜 | FT-registry_yaml |
| ORPHAN-MODULE | 5 | 36.8 | 低频高价 | FT-rename_move（三方原子） |
| PROTECTED-PATHS | 3 | 182.8 | 稀有天价 | FT-formal_md（ARCH-APPROVAL 前置） |
| R5-DIGIT-SUFFIX | 3 | 28.9 | 低频高价 | FT-working_md（语义名目录） |
| IMPORT-INTEGRITY | 2 | 148.4 | 稀有天价 | FT-rename_move |
| TTL-METADATA | 1 | 101.3 | 稀有天价 | FT-working_md |

## 按会话（谁的墙最多）

chainpile 19 / combine 18 / sweep-tail 14 / nightfix 10 / ulib3c 9 / e2e 6 / k4 6。
共性：**盲发循环**（同一死因连死 2-3 次不修根因）贡献约 30% 死信——指南+死因锚点递送直接打这一面。

## 优先级结论

1. 高频便宜档（precommit-run/token/translation/registry 四簇=50 封）→指南前置递送已覆盖（本包 ①②），预期死信 -40%。
2. 稀有天价档（PROTECTED-PATHS/IMPORT/TTL）→指南红字警示+锚点直达，单次避免即省 2-3h。
3. 盲发循环→死因锚点让属主第一次就拿到处方，配合"requeue 前核 HEAD 现状"纪律。
