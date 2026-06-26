---
module_id: KE-1136
status: active
title: 第一步：git mv 后立即搜索旧路径的所有引用
category: governance
ttl: permanent
---

# 第一步：git mv 后立即搜索旧路径的所有引用

第一步：git mv 后立即搜索旧路径的所有引用
git mv <旧路径> <新路径>
Select-String -Path "docs/**/*.md" -Pattern "旧文件名" -Recurse
