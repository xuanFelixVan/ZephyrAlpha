---
module_id: KE-3557----head-000
title: 3. 若 HEAD 也已损坏，找干净版本
category: governance
---

# 3. 若 HEAD 也已损坏，找干净版本

3. 若 HEAD 也已损坏，找干净版本
git log --oneline -- <损坏文件路径>
git show <干净commit>:<损坏文件路径> > temp.md
