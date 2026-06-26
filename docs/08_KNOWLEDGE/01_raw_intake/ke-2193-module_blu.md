---
module_id: KE-2100
title: 3.3 十八维检测矩阵
category: module_blueprint
ttl: permanent
---

# 3.3 十八维检测矩阵

3.3 十八维检测矩阵

| # | 检测维度 | 检测方法 | Type | 精确度 | 速度 | 备注 |
|:---:|---------|---------|:---:|:---:|:---:|------|
| 1 | **词法精确匹配** | 符号名 = 已知 SSoT 名 | Type-1 | ★★★★★ | ★★★★★ | Stage 0.5/1 |
| 2 | **签名+返回值匹配** | 参数类型 + 返回类型的并集指纹——SHA256[:12] O(1)精确匹配 | Type-2 | ★★★★ | ★★★★★ | **Stage 0.5——Vibe Coding 场景下性价比最高的防线**（AI 重实现时通常保持相同签名） |
| 3 | **Token 归一化匹配** | MinHash + LSH | Type-2 | ★★★★ | ★★★★ | Stage 1 |
| 4 | **代码块级重复** | 滑动窗口 MinHash（非函数级别，min_block_size≥5行） | Type-2/3 | ★★★★ | ★★ | Stage 1——import块/异常处理模板/配置逻辑 |
| 5 | **AST 结构匹配** | 归一化子树哈希 + 相似度 + Python惯用法豁免 | Type-3 | ★★★★★ | ★★★ | Stage 2 |
| 6 | **部分重复检测** | 滑动窗口 + LCS（最长公共子序列） | Type-3 | ★★★★ | ★★ | Stage 2 |
| 7 | **重排序语句容忍** | AST 子树集合比对而非序列比对 | Type-3 | ★★★★ | ★★★ | Stage 2 |
| 8 | **参数化模板识别** | 同名前缀 + 结构相似 > 0.7 → 聚类 | Type-3 | ★★★ | ★★★★ | Stage 2 |
| 9 | **常量/import/类/枚举重复** | Token 归一化（非函数结构也纳入） | Type-1/2 | ★★★★★ | ★★★★★ | Stage 1 + code block dedup |
| 10 | **Python 惯用法豁免** | AST 模式匹配自动跳过（`__init__`/`__repr__`/`@property`/`@overload`/ABC骨架） | — | — | ★★★★★ | Stage 2——减少误报 |
| 11 | **配置文件语义重复** | YAML/TOML AST 比对（Tree-sitter） | Type-2 | ★★★★ | ★★★★ | Wave 2 |
| 12 | **LLM 语义等价判断** | Prompt: "是否等价？给出置信度" | Type-4 | ★★★★ | ★ | Stage 3——可选 |
| 13 | **微型克隆检测** | n-gram 频率计数——逐行SHA256 + 归一化 + 2-3行滑动窗口 | Type-1/2/3 | ★★★★★ | ★★★★★ | **v0.9.0 / Stage 1——Vibe Coding 微克隆密度 3.8x（MSR 2024）——对标 Google Tricorder** |
| 14 | **提取后自动测试生成** | 类型驱动边界测试 + 执行轨迹金丝雀录制 + 调用方契约测试——生成pytest parametrize | — | ★★★★ | ★★★ | **v0.9.0 / auto_fixer 后触发——对标 Google Mozart/Test Certified——BRS 缓解** |
| 15 | **API契约一致性验证** | docstring参数校验+类型注解精确度+影子清单描述时效性+异常契约——三维信任模型 | — | ★★★★★ | ★★★★ | **v0.9.0 / Wave 2——对标 Google Tricorder/Meta Pyre——防止契约腐烂** |
| 16 | **跨边界克隆感知** | 四大边界差异化策略（SRC_TEST_BRIDGE/SRC_SCRIPTS_DIVERGENCE/CROSS_LAYER_REDUNDANCY/VENDORED） | Type-2/3 | ★★★★ | ★★★ | **v0.9.0 / Wave 2——对标 Google Blaze/JetBrains IntelliJ——最高价值去重** |
| 17 | **去重决策审计链** | DecisionFingerprint 不可变追加日志 + 证据包 + 可回滚——决策指纹永久可追溯 | — | ★★★★★ | ★★★★★ | **v0.10.0 / Wave 2——"我没看的时候引擎做了什么？"——对标 Google Tricorder/Meta Sapienz** |
| 18 | **共享函数主动发现** | 签名归一化匹配(Channel A) + TF-IDF语义匹配(Channel B)——主动通知AI已有实现 | Type-2/4 | ★★★★ | ★★★★★ | **v0.10.0 / Wave 2——从"被动拦截→主动赋能"——对标 Sourcegraph Cody/Google Code Search——<150行** |
