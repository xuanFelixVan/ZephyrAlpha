"""Vector Memory Service (VMS)
=====================================

Vibe Coding 2.0 基础设施 · L12 跨层支撑层 · 5 大核心服务之一

当前状态：skeleton（experimental 空壳）—— 实际能力暂由 src/zephyr/kb/ 提供。
beta 计划：kb/ 能力整合入 vector_memory/ 的 InProcessVectorMemory 实现。

规划架构（未实现）：
- 存储后端 : ChromaDB 0.6（2 进程内库，beta+ HTTP 服务）
- 嵌入模型 : BGE-M3 ONNX（本地推理，零外部依赖）
- 分块策略 : 递归字符分块（Recursive Character Chunking）
- 5 大 Collection : decisions / code_context / lessons / knowledge / runtime_logs

架构归属
--------
LPC 双轨架构 B 轨（Bounded Context · 无 l<NN>_ 前缀）
架构决策：ADR-0022 目录双轨治理 + ADR-0016 VMS
"""
