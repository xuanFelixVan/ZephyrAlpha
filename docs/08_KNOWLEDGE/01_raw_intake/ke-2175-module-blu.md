---
module_id: KE-2083
status: active
title: 3.2 增强版五阶段检测流水线（含降级运行）
category: module_blueprint
---

# 3.2 增强版五阶段检测流水线（含降级运行）

3.2 增强版五阶段检测流水线（含降级运行）

```
Stage 0: 缓存预热 + 变更检测（毫秒级）
  → 加载 function-cache.json
    · 每个函数的签名指纹（参数类型+返回类型的 SHA256[:12]）
    · AST 子树归一化哈希
    · MinHash 签名
    · 文件路径 + 行号范围
    · last_modified 时间戳
    · intentional_duplicate 标记
    · known_shared_equivalent（已知共享等价函数）
  → 缓存完整性自检：
    · _integrity 字段：SHA256(cache_content) 跨磁盘写入校验
    · 加载时验证 hash → 不一致 → 自动 full rebuild → 记录 Session Log
    · 写入用原子操作：先写 .tmp → os.replace(.tmp, cache.json)
  → git diff 检测变更文件
  → 快速路径：只扫描变更/新增函数
  → 全量扫描路径：复用未变更函数的缓存

Stage 0.5: 签名指纹碰撞检测（毫秒级，新增！)
  → 对每个新增函数计算 signature_fingerprint（SHA256[:12]）
  → O(1) 精确匹配缓存中所有函数的 signature_fingerprint
  → 签名碰撞判定：
    · signature 完全相同 → "Signature Collision"（高置信度，直接标记）
    · signature 含相同参数类型但不同返回类型 → "Signature Near-Collision"（中置信度）
  → 为什么是 Stage 0.5 而非 Stage 3：
    · Vibe Coding AI 重新发明函数时通常保持相同签名（输入输出类型不变）
    · 不需要 MinHash、不需要 AST——纯缓存查询，零额外计算
    · 这是 Vibe Coding 语境下性价比最高的检测维度
  → 路径感知阈值同样适用：
    · shared/ 内签名碰撞 → CRITICAL（shared 里绝不允许签名冲突）
    · core/ 内签名碰撞 → HIGH
    · tests/ 内签名碰撞 → LOW（测试函数签名冲突容忍度高）

Stage 0.25: 行为采样快速验证（秒级，v0.6.0 新增！——低测试覆盖安全网）
  → 背景：Vibe Coding 项目中测试覆盖率通常极低（< 20%），verifier.py 依赖 pytest 不现实
  → 对每个签名碰撞候选对，进行轻量级行为采样验证：
    · 自动生成 N 组类型兼容的采样输入（基于类型注解推断——int→[0,1,-1,MAX]，str→["","test","中文"]，List→[[], [1], [1,2,3]]）
    · 分别对原始函数和候选重复函数执行采样输入
    · 比对输出：完全相同 → "behavioral_match" 标记 + 提升置信度
    · 输出部分不同 → "behavioral_divergence" 标记 + 降低置信度 → 降级为 needs_review
    · 函数有副作用（I/O/网络/数据库）→ 跳过行为采样 → 标记 "side_effect_skip"
  → 安全约束：
    · 仅对纯函数执行（无 I/O、无 global、无 random、无 time 调用——通过 AST 静态判定）
    · 永不执行 `eval()`/`exec()`/`__import__()`/`os.system()`/`subprocess` 相关代码
    · 执行超时 500ms/func——超时 → 跳过
    · 执行环境：subprocess 沙箱隔离（独立进程，内存限制 256MB）
  → 采样输入生成策略：
    · 基础类型映射：int→[0,1,-1,2,10,100], float→[0.0,1.0,-1.0], str→["","test","你好"], bool→[True,False]
    · 可选类型：Optional[X]→ +[None]
    · 集合类型：List[X]→ [[],[x1],[x1,x2,x3]], Dict[K,V]→ [{},{k1:v1}], Set[X]→ [set(),{x1}]
    · 自定义类 → 尝试无参构造 __init__()，失败则跳过
    · 最多生成 10 组采样输入（减少执行开销）

Stage 1: Token 级快速扫描（秒级）
  → 提取所有新增/变更函数的 token 序列
  → 归一化：统一变量名为 _VAR_、函数名为 _FUNC_
  → 剥离 docstring + 注释
  → 计算归一化 token 序列的 MinHash
  → LSH 近似去重：候选对集合
  → 路径感知阈值：
    · src/zephyr/shared/   → 0.3（shared 里重复是严重 bug）
    · src/zephyr/core/     → 0.6
    · src/zephyr/*/        → 0.7
    · tests/               → 0.9（测试允许更高的重复容忍度）
    · scripts/             → 0.7
  → **新增：代码块级去重**（非函数级别）
    · 对整个文件做 N 行窗口滑动（min_block_size=5，默认最少 5 行）
    · 计算每个窗口的 MinHash → 跨文件比对
    · 检测目标：import 块重复（20+ 文件中相同 import 段）、异常处理模板、配置读取+验证逻辑

Stage 2: AST 级精确比对（分钟级）
  → 对候选对进行 AST 子树哈希
  → 增强处理：
    · 剥离 docstring 后比对
    · 归一化变量名后比对
    · 装饰器剥离——@timer 和 @cache 不应阻止函数体比对
    · **Python 惯用法自动豁免**（新增）：
      - `__init__(self, ...): self._xxx = xxx` → 豁免
      - `__repr__/__str__` 返回 f-string 模式 → 豁免
      - `__enter__/__exit__` Context Manager 协议骨架 → 豁免
      - `@property` getter/setter 模式 → 豁免
      - ABC 抽象方法（`raise NotImplementedError`）→ 豁免
      - `@overload` 类型重载 → 豁免
    · **设计模式自动豁免**（v0.6.0 新增）：
   
