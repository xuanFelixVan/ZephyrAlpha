---

title: Reports Directory
description: 本地报告目录治理流水线与调试中间产物归档
blueprint_id: MOD-INF-005
ttl: task_bound
doc_type: index
---


scripts/reports — 本地报告目录说明
================================================================================

本目录下的 *.jsonl 多为治理流水线或调试产生的中间产物。.gitignore 已默认忽略新增的
scripts/reports/*.jsonl，避免无意将运行输出提交到版本库。若历史中仍有已被跟踪的
jsonl 文件，可选用：

  git rm --cached scripts/reports/<file>.jsonl

解除跟踪后再提交策略变更。

长期归档建议写入 .runtime/reports 或运维对象存储，并约定保留周期（TTL）。
