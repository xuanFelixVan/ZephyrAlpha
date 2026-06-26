---
module_id: KE-1340
status: active
title: 10项盲点
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 10项盲点

10项盲点

- B601 路径处理——Pathlib统一正反斜杠
- B602 进程模型——Windows Process≠Linux Process
- B603 编码一致——Windows UTF-16→强制UTF-8
- B604 长路径——MAX_PATH=260→启用LongPaths
- B605 PowerShell兼容——不依赖Bash
- B606 换行符——CRLF vs LF→Git autocflf
- B607 防火墙/Defender——可能block API调用
- B608 Windows Service包装——nssm/win32serviceutil
- B609 注册表vs配置文件→统一配置文件
- B610 Windows Update重启→优雅handle
