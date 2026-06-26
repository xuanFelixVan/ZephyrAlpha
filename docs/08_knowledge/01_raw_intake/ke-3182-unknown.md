---
module_id: KE-3076
status: active
title: 关键决策
category: session_log
ttl: permanent
doc_type: knowledge_entry
---

# 关键决策

关键决策

- SecurityGateway 接口签名比 codegen ABC 更丰富（带 metadata 参数和 ScanFinding 类型）——符合 OCP 扩展原则
- ArtifactScanner 自扫排除了自身文件（artifact_scanner.py），因其正则定义中包含 `.env` / `.aws/credentials` 等敏感文件模式导致假阳性
- AISGSandbox.scan_content() 返回 `list[str]`（描述文本），被映射为 AISG-DANGER-001 warning 级 finding
