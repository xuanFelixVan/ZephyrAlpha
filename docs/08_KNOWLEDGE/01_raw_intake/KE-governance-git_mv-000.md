---
module_id: KE-governance-git_mv-000
title: 第一步：git mv 后立即搜索旧路径的所有引用
category: governance
---

# 第一步：git mv 后立即搜索旧路径的所有引用

第一步：git mv 后立即搜索旧路径的所有引用
git mv <旧路径> <新路径>
Select-String -Path "docs/**/*.md" -Pattern "旧文件名" -Recurse
