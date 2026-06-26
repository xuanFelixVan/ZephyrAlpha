---
module_id: KE-870
status: active
title: 3.5 "文件不存在"的三级判定
category: governance
ttl: permanent
---

# 3.5 "文件不存在"的三级判定

3.5 "文件不存在"的三级判定

```
级别 1：index.md 显式声明不存在
    ├── 判定：文件确实不存在
    └── 处理：停止搜索，记录"已确认不存在"

级别 2：index.md 中未注册 + 注册表中也未找到
    ├── 判定：大概率不存在
    └── 处理：执行路径 3（工具搜索确认），仍找不到 → 确认不存在

级别 3：Gre/Grep/SearchCodebase 均无结果
    ├── 判定：确认不存在
    └── 处理：在 Session Log 中记录"已确认文件 X 不存在，进行了三级判定"

反模式：grep 一次没找到就说"文件不存在" ❌
```

---
