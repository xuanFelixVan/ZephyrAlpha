---
module_id: KE-845---head-000
title: 步骤 3：若 HEAD 也已损坏，找干净版本
category: governance
ttl: permanent
doc_type: knowledge_entry
---

# 步骤 3：若 HEAD 也已损坏，找干净版本

步骤 3：若 HEAD 也已损坏，找干净版本
git log --oneline -- <损坏文件路径>
git show <干净commit>:<损坏文件路径> > temp.md
